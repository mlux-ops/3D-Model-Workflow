import numpy as np, re,math,json,csv,collections
from pathlib import Path
from shapely.geometry import Point,Polygon,LineString
base=Path('output/trim_takeoffs_20261117')
r2=base/'wieland_r02'
src=Path.home()/'OneDrive/Documents/25-006 1527 N Wieland.ifc'
items={}
for ln in src.open(errors='replace'):
 m=re.match(r'#(\d+)=(\w+)\((.*)\);',ln)
 if not m: continue
 n=int(m[1])
 if n>3320:break
 items[n]=(m[2],m[3])
ref=lambda s:[int(x) for x in re.findall(r'#(\d+)',s)]
nums=lambda s:[float(x) for x in re.findall(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?',s)]
def xy(k): return np.array(nums(items[k][1])[:2])
def pos(a):
 typ,args=items[a];ks=ref(args)
 pt=xy(ks[0]); v=xy(ks[-1]) if len(ks)>=3 or (typ=='IFCAXIS2PLACEMENT2D' and len(ks)>=2) else np.array([1.,0.]);v=v/np.linalg.norm(v);return pt,np.array([[v[0],-v[1]],[v[1],v[0]]])
def footprint(idx):
 s=items[idx][1];rp=ref(s)[-1]; shp=items[ref(items[rp][1])[0]][1]; solid=items[ref(shp)[-1]]; assert solid[0]=='IFCEXTRUDEDAREASOLID'
 k=ref(solid[1]);e=p=items[k[0]];pt,rot=pos(k[1])
 if p[0]=='IFCRECTANGLEPROFILEDEF':
  h=ref(p[1])[0];c,pr=pos(h);w,t=map(float,p[1].split(',')[-2:]);v=np.array([[-w,-t],[w,-t],[w,t],[-w,t]])*.5;v=v@pr.T+c
 elif p[0] in ['IFCARBITRARYCLOSEDPROFILEDEF','IFCARBITRARYPROFILEDEFWITHVOIDS']:
  curve=items[ref(p[1])[0]];assert curve[0]=='IFCPOLYLINE';v=np.array([xy(x) for x in ref(curve[1])])
 else:raise ValueError(p[0])
 return Polygon(v@rot.T+pt)
rooms=list(csv.DictReader((r2/'current_room_boundary_inputs.csv').open(encoding='utf-8-sig')));byuid={r['unique_id']:r for r in rooms};idx=json.loads((r2/'ifc_room_index.json').read_text());doors=json.loads((r2/'current_doors.json').read_text())['result']['items']
def params(e):
 a=json.loads((r2/('door_'+str(e['id'])+'.json')).read_text())['result'];return {k:{p['name']:p for p in a[k]} for k in ['type','instance']}
def val(p,n,fmt=False):
 for k in ['instance','type']:
  x=p[k].get(n,{}).get('formatted' if fmt else 'value')
  if x is not None:return x
dc={e['id']:params(e) for e in doors}
# Repeated room tags exist within the same level. Separate by Revit element ID BEFORE any room grouping.
from collections import Counter
dups=Counter(r['number'] for r in rooms if r['area_sf'] and float(r['area_sf'])>0)
for r in rooms:
 if dups[r['number']]>1:r['number']=r['number']+' #'+r['element_id']
r3=base/'wieland_r03';ww=json.loads((r3/'windows.json').read_text())['result']['items']; walls={e['id']:e for e in json.loads((r3/'walls0.json').read_text())['result']['items']}; ceil=json.loads((r3/'ceilings.json').read_text())['result']['items']
def nearby(poly,e,limit=1.35):
 l=e.get('location') or {}
 return 'point' in l and poly.exterior.distance(Point(l['point'][:2]))<=limit
def axialdim(e,p):
 wall=walls.get(e['host_id']); loc=wall.get('location') if wall else None
 if not loc or 'start' not in loc:return None
 v=np.array(loc['end'][:2])-np.array(loc['start'][:2]);v/=np.linalg.norm(v)
 if min(abs(v))>1.e-4: return None
 axis=int(np.argmax(abs(v)));return e['bounds']['max'][axis]-e['bounds']['min'][axis]
sel=['306A','306B','308A','308B','309A','309B']
polys={z['oldnumber']:footprint(z['step']) for z in idx if z['oldnumber'] in sel}

from shapely.geometry import box
levs={e['name']:e['elevation'] for e in json.loads((base/'wieland_levels.json').read_text())['result']['items']}
def reconstruct(old,elev):
 ring=list(old.exterior.coords)[:-1];N=len(ring);edges=[];trace=[]
 for a,b in zip(ring,ring[1:]+ring[:1]):
  dx,dy=b[0]-a[0],b[1]-a[1]
  if min(abs(dx),abs(dy))>.003:raise ValueError('diagonal')
  t=0 if abs(dx)>abs(dy) else 1;n=1-t; lo,hi=sorted([a[t],b[t]]);v=a[n];candidates=[]
  for obj in walls.values():
   bd=obj['bounds'];loc=obj.get('location')or{}
   if not bd or 'start' not in loc or bd['max'][2]<elev+3.0 or bd['min'][2]>elev+2:continue
   st,en=loc['start'],loc['end']
   if abs(st[n]-en[n])>.001:continue
   # Prefer inner wall face closest to old finish plane, not axial line; constrain same side of wall axis.
   f=bd['max'][n] if v>st[n] else bd['min'][n]
   if abs(f-v)>.28:continue
   slo,shi=sorted([st[t],en[t]]);run=max(0,min(hi,shi)-max(lo,slo))
   if run<.08 or run/(hi-lo)<.13:continue
   candidates.append((f,run,obj['id']))
  groups={}
  for f,run,i in candidates:
   key=round(f,5); val_=groups.setdefault(key,[f,0,[]]);val_[1]+=run;val_[2].append(i)
  ranked=sorted(groups.values(),key=lambda z:(-min(z[1]/(hi-lo),1),abs(v-z[0])))
  if ranked: value,coverage,ids=ranked[0]
  else:value,coverage,ids=v,0,[]
  edges.append([n,value]);trace.append((n,v,value,ids,min(1,coverage/(hi-lo))))
 coords=[]
 for i in range(N):
  e1=edges[i-1];e2=edges[i]
  if e1[0]==e2[0] and abs(e1[1]-e2[1])>.015:raise ValueError('split wall shifts')
  pt=list(ring[i]);pt[e1[0]]=e1[1];pt[e2[0]]=e2[1];coords.append(pt)
 P=Polygon(coords)
 if not P.is_valid:raise ValueError('non-simple')
 return P,trace
currents={};recons={}
for z in idx:
 r=byuid.get(z['uid'])
 if not r or not r['area_sf'] or float(r['area_sf'])<.01:continue
 key=r['number'];S,per,elev=float(r['area_sf']),float(r['boundary_lf']),levs[r['level']]
 try:
  old=footprint(z['step']);p,trace=reconstruct(old,elev);da,dl=p.area-S,p.length-per
  if abs(da)<.00002 and abs(dl)<.00002:
   currents[key]=p
  recons[key]=(p,trace,da,dl)
 except Exception as ex:pass

from shapely.ops import unary_union,polygonize
sep=json.loads((r3/'room_separators.json').read_text())['result']['items']
import shapely
planes={}
for lev,z in levs.items():
 if lev not in [r['level']for r in rooms]:continue
 solids=[]
 for e in walls.values():
  b=e['bounds'];l=e.get('location') or {}
  if not b or 'start' not in l or b['min'][2]>z+2 or b['max'][2]<z+2:continue
  x0,y0=l['start'][:2];x1,y1=l['end'][:2]
  if min(abs(x1-x0),abs(y1-y0))<.01:
   solids.append(box(*b['min'][:2],*b['max'][:2]))
  else:
   ln=LineString([(x0,y0),(x1,y1)]);solids.append(ln.buffer(.2,cap_style=2))
 u=shapely.union_all(solids,grid_size=0.000001)
 bounds=u.bounds; outer=box(bounds[0]-3,bounds[1]-3,bounds[2]+3,bounds[3]+3)
 v=outer.difference(u);bounds=[v.boundary]
 for e in sep:
  l=e['location'];s,e_=np.array(l['start']),np.array(l['end'])
  if abs(s[2]-z)>.01:continue
  line=LineString([s[:2],e_[:2]]);bounds.append(line)
 net=shapely.union_all(bounds,grid_size=.00001)
 planes[lev]=[g for g in polygonize(net) if .1<g.area<4000 and v.covers(g.representative_point())]
print('floor rooms',[(l,len(g))for l,g in planes.items()])
extra={}
for z in idx:
 r=byuid.get(z['uid'])
 if not r or not r['area_sf'] or float(r['area_sf'])<.01 or r['number'] in currents:continue
 try:po=footprint(z['step']);pt=po.representative_point()
 except:continue
 g=next((g for g in planes[r['level']] if g.covers(pt)),None)
 if g is None:continue
 da=g.area-float(r['area_sf']);dl=g.length-float(r['boundary_lf'])
 if abs(da)<.001 and abs(dl)<.001:extra[r['number']]=g
 if r['name'] in ['LIVING & DINING','PRIMARY BED','BED 2','BED 3','BED 4','BED 5']:print(r['number'],'delta',round(da,3),round(dl,3),len(g.exterior.coords))
print('extra',extra.keys())

from shapely.geometry import box
def directtrace(P,z):
 c=list(P.exterior.coords);tr=[]
 for a,b in zip(c[:-1],c[1:]):
  t=0 if abs(a[0]-b[0])>abs(a[1]-b[1]) else 1;n=1-t;p=a[n];lo,hi=sorted([a[t],b[t]]);its=[];ids=[]
  for e in walls.values():
   bd=e['bounds'];l=e.get('location') or {}
   if not bd or 'start' not in l or bd['max'][2]<z+2.0 or bd['min'][2]>z+2:continue
   if min(abs(p-bd['min'][n]),abs(p-bd['max'][n]))>.0001:continue
   q1=max(lo,bd['min'][t]);q2=min(hi,bd['max'][t]);
   if q2>q1+.00001:its.append([q1,q2]);ids.append(e['id'])
  out=[]
  for a_,b_ in sorted(its):
   if out and a_<=out[-1][1]+.00001:out[-1][1]=max(out[-1][1],b_)
   else:out.append([a_,b_])
  tr.append((n,p,p,ids,min(1,sum(y-x for x,y in out)/max(.0000001,hi-lo))))
 return tr
for k,p in extra.items():
 r=next(r for r in rooms if r['number']==k);currents[k]=p;recons[k]=(p,directtrace(p,levs[r['level']]),p.area-float(r['area_sf']),p.length-float(r['boundary_lf']))
for k,p in currents.items():
 r=next(r for r in rooms if r['number']==k);recons[k]=(p,directtrace(p,levs[r['level']]),p.area-float(r['area_sf']),p.length-float(r['boundary_lf']))
case=json.loads((base/'wieland_casework.json').read_text())['result']['items']
def winp(e):
 f=r3/('win_'+str(e['id'])+'.json')
 if not f.exists():return {}
 v=json.loads(f.read_text())['result'];return {x['name']:x.get('value') for x in v['type']+v['instance']}
def merge(intervals):
 out=[]
 for lo,hi in sorted(intervals):
  if hi-lo<.00001: continue
  if out and lo<out[-1][1]+.00001:out[-1][1]=max(out[-1][1],hi)
  else:out.append([lo,hi])
 return out
def save(fn,rows):
 if not rows:return
 with (r3/(fn+'.csv')).open('w',newline='',encoding='utf-8-sig') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=[];segs=[];obs=[];roster=[];all_edges=[]
for row in rooms:
 if not row['area_sf'] or float(row['area_sf'])<.01:continue
 key=row['number'];S=float(row['area_sf']);per=float(row['boundary_lf']);lev=row['level'];z=levs[lev]
 good=key in currents
 state='area + perimeter reconcile; check wall/finish scope' if good else 'current quantities only; outline not reconciled'
 roster.append({'level':lev,'room':key,'room_name':row['name'],'gross_room_boundary_lf':per,'live_area_sf':S,'outline_QA':state,'base_finish_parameter':row['base_finish'],'room_uid':row['unique_id'],'Revit_receipt':row['receipt']})
 if not good:continue
 P=currents[key];trace=recons[key][1]
 elevs=[]
 for ce in ceil:
  b=ce['bounds']
  if not b or not z+6.5<b['min'][2]<z+12:continue
  bp=box(*b['min'][:2],*b['max'][:2])
  if bp.buffer(.02).covers(P.centroid) and P.intersection(bp).area/P.area>.96:elevs.append((bp.area,ce['id'],b['min'][2]))
 elevs.sort();ceid=elevs[0][1] if elevs else None;cebot=elevs[0][2] if elevs else None
 rr=[];opens=[];coords=list(P.exterior.coords)
 for j,(a,b) in enumerate(zip(coords[:-1],coords[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];t=0 if abs(dx)>abs(dy) else 1;n=1-t;pos=a[n];lo,hi=sorted([a[t],b[t]]);ll=hi-lo;ids=trace[j][3];cover=trace[j][4]
  wallok=cover>.965 and bool(ids) and all('curtain' not in walls[i]['name'].lower() for i in ids)
  if ll<.000001:continue
  record={'room':key,'edge':j+1,'wall_axis':'EW' if t==0 else 'NS','x_start_ft':a[0],'y_start_ft':a[1],'x_end_ft':b[0],'y_end_ft':b[1],'face_LF':ll,'wall_ids':'|'.join(map(str,ids)),'wall_projection_fraction':cover}
  all_edges.append(record)
  if False:continue
  door_int=[];win_b=[];door_c=[];win_c=[];case_b=[];case_c=[];unsupported_i=[]
  for kind,seq in [('Door',doors),('Window',ww)]:
   for e in seq:
    eb=e['bounds'];host=walls.get(e['host_id']);hl=host.get('location') if host else None
    if not eb or not hl or 'start' not in hl or abs(hl['start'][n]-hl['end'][n])>.001:continue
    if eb['max'][2]<=z+.03 or eb['min'][2]>=z+12:continue
    hbd=host['bounds'];surf=min(abs(pos-hbd[s][n]) for s in ['min','max'])
    if e['host_id'] not in ids and surf>.025:continue
    if not e.get('location') or 'point' not in e['location'] or abs(e['location']['point'][n]-pos)>1.3:continue
    rlo=max(lo,eb['min'][t]);rhi=min(hi,eb['max'][t]);span=rhi-rlo
    if span<=.02:continue
    h1=eb['min'][2]-z;h2=eb['max'][2]-z
    if kind=='Door':
     pp=dc[e['id']];mark=val(pp,'Mark');width=val(pp,'Width');trim=val(pp,'Trim Width');show=val(pp,'show trim');sill=head=None;wp={};rough=None
    else:
     wp=winp(e);mark=wp.get('Mark');width=wp.get('Width');trim=show=None;sill=wp.get('Sill Height');head=wp.get('Head Height');rough=wp.get('Rough Width')
    bas=eb['min'][2]<z+8/12 and eb['max'][2]>z+.001
    cr=cebot is not None and eb['max'][2]>cebot-3/12+.00001 and eb['min'][2]<cebot+.00001
    if bas:(door_int if kind=='Door' else win_b).append((rlo,rhi))
    if cr:(door_c if kind=='Door' else win_c).append((rlo,rhi))
    item={'room':key,'edge':j+1,'kind':kind,'instance_id':e['id'],'host_wall':e['host_id'],'mark':mark,'name':e['name'],'nominal_width_LF':width,'rough_width_LF':rough,'trim_each_side_LF':trim,'show_trim':show,'nominal_sill_above_floor_ft':sill,'nominal_head_above_floor_ft':head,'geometry_low_above_floor_ft':h1,'geometry_top_above_floor_ft':h2,'whole_family_axis_width_LF':eb['max'][t]-eb['min'][t],'clipped_face_overlap_LF':span,'axis_start_ft':rlo,'axis_end_ft':rhi,'base_vertical_conflict':bas,'crown_vertical_conflict':cr,'window_type_mark':wp.get('Type Mark'),'host_clearance_note':'Full family envelope; NOT automatically the interior trim stop.'}
    obs.append(item);opens.append(item)
  for e in case:
   eb=e.get('bounds')
   if not eb or eb['max'][2]<=z+.01 or eb['min'][2]>=z+12:continue
   bb=box(*eb['min'][:2],*eb['max'][:2])
   if bb.intersection(P).area<.05 or not eb['min'][n]-.085<=pos<=eb['max'][n]+.085:continue
   st,et=max(lo,eb['min'][t]),min(hi,eb['max'][t])
   if et-st<=.02:continue
   if eb['min'][2]<z+8/12:case_b.append((st,et))
   if cebot is not None and eb['max'][2]>cebot-3/12 and eb['min'][2]<cebot:case_c.append((st,et))
  length=lambda xs:sum(hi_-lo_ for lo_,hi_ in merge(xs))
  db=length(door_int);wb=length(win_b);dc_=length(door_c);wc=length(win_c)
  # Full envelope at each opening is conservative only for this model scenario, NOT an upper bound on unknown field casing.
  def clear(intervals):
   m=merge(intervals);start=lo;out=[]
   for l,h in m:
    if l-start>.00001:out.append((start,l))
    start=h
   if hi-start>.00001:out.append((start,hi))
   return out
  bs=clear(door_int+win_b+case_b);cs=clear(door_c+win_c+case_c)
  rec=dict(record,base_door_envelope_LF=db,base_window_envelope_LF=wb,base_cabinet_envelope_LF=length(case_b),crown_door_envelope_LF=dc_,crown_window_envelope_LF=wc,crown_cabinet_envelope_LF=length(case_c),wall_backed=wallok,
   clear_base_candidate_LF=length(bs) if wallok else None,clear_crown_candidate_LF=length(cs) if wallok and cebot is not None else None,
   openings='; '.join(str(o['mark'])+':'+str(o['instance_id']) for o in opens if o['edge']==j+1),ceiling_id=ceid,ceiling_below_z_LF=(cebot-z) if cebot else None,
   base_chain_LF=' + '.join(f'{h-l:.4f}' for l,h in bs) if wallok else '',crown_chain_LF=' + '.join(f'{h-l:.4f}' for l,h in cs)if wallok and cebot else '')
  segs.append(rec);rr.append(rec)
 if True:
  s=lambda f:sum(a[f] or 0 for a in rr)
  assert abs(s('face_LF')-per)<.002,(key,s('face_LF')-per)
  summary.append({'room':key,'name':row['name'],'level':lev,'gross_room_LF':per,'door_envelope_LF':s('base_door_envelope_LF'),'gross_less_door_envelopes_LF':per-s('base_door_envelope_LF'),'low_window_envelope_LF':s('base_window_envelope_LF'),'base_cabinet_envelopes_LF':s('base_cabinet_envelope_LF'),'wall_face_verification_hold_LF':sum(a['face_LF']for a in rr if not a['wall_backed']),'base_clear_face_candidate_LF':s('clear_base_candidate_LF'),'crown_clear_face_candidate_LF':s('clear_crown_candidate_LF') if cebot is not None else None,'crown_window_envelope_LF':s('crown_window_envelope_LF'),'ceiling_id':ceid,'indexed_room_id':row['element_id'],'order_QTY':'HOLD'})
save('01_room_scope_register',roster);save('02_room_takeoff',summary);save('03_wall_face_runs',segs);save('04_openings',obs);save('05_matched_wall_faces',all_edges)
print('TOTALS',len(roster),len(currents),len(summary),len(segs),len(obs));print('FOCUS')
for r in sorted(summary,key=lambda r:r['room']):
 if not ('BED' in r['name'] or 'LIVING' in r['name']):continue
 print(r['room'],*[(round(r[f],4) if r[f] is not None else 'HOLD') for f in ['gross_room_LF','door_envelope_LF','low_window_envelope_LF','wall_face_verification_hold_LF','base_clear_face_candidate_LF','crown_clear_face_candidate_LF']])

