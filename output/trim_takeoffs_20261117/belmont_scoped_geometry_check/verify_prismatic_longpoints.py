
import json,csv,collections,math
from pathlib import Path
p=Path("output/trim_takeoffs_20261117/belmont_scoped_geometry_check"); groups=[];tol=2e-5
for k,h,t in [('base',8/12,5/8/12),('crown',3/12,.75/12)]:
 for a in json.loads((p/(k+'_volume_data.json')).read_text()):
  r=json.loads((p/(k+'_receipts')/(a['operation_id']+'.json')).read_text())['receipt']['result'];e=r['element'];bb=e['bounds'];g=r['geometry']
  sol=[v for v in g if v['kind']=='solid'and v['volume']>1e-10];fs=[v for v in g if v['kind']=='face']
  if len(sol)!=1 or sol[0]['faces']!=len(fs) or any(v['normal'] is None for v in fs) or not bb:continue
  span=[bb['max'][i]-bb['min'][i]for i in range(3)]
  if abs(span[2]-h)>tol:continue
  fits=[]
  for ax in [0,1]:
   c=1-ax
   if abs(span[c]-t)>tol:continue
   sides=[v for v in fs if abs(abs(v['normal'][c])-1)<1e-7];tb=[v for v in fs if abs(abs(v['normal'][2])-1)<1e-7];ends=[v for v in fs if v not in sides and v not in tb]
   if len(ends)<2 or len(ends)%2 or any(abs(v['normal'][2])>1e-7 or abs(v['normal'][ax])<.15 or abs(v['area']*abs(v['normal'][ax])-h*t)>tol for v in ends):continue
   count=len(ends)//2
   if sum(v['normal'][ax]>0 for v in ends)!=count:continue
   V=sol[0]['volume'];cen=V/h/t
   if any(abs(sum(v['area'] for v in tb if v['normal'][2]*s>0)-V/h)>tol for s in [-1,1]):continue
   avgside=sum(v['area']for v in sides)/2/h
   if abs(avgside-cen)>tol:continue
   # Signed end slope balances side-face material length difference independently.
   slopes=[abs(v['normal'][c]/v['normal'][ax]) for v in ends];angs=[math.degrees(math.atan(q)) for q in slopes]
   long=cen+t*sum(slopes)/2
   if count==1 and abs(long-span[ax])>tol:continue
   if count>1 and long>span[ax]+tol:continue
   fits.append((ax,count,cen,long,angs))
  if len(fits)!=1:continue
  ax,count,cen,long,angs=fits[0]
  groups.append({'profile':k,'element_id':e['id'],'unique_id':e['unique_id'],'group_piece_count':count,'modeled_longpoint_LF':long,'equivalent_center_LF':cen,'bbox_axial_LF':span[ax],'bbox_less_combined_cuts_LF':span[ax]-long,'axis':'XY'[ax],'end_angles_deg':' | '.join(str(round(x,4)) for x in angs),'base_z_ft':bb['min'][2],'x0':bb['min'][0],'y0':bb['min'][1],'x1':bb['max'][0],'y1':bb['max'][1],'scope_class':'Single piece - length independently matches bounds' if count==1 else 'Separated pieces - group sum only; individual split lengths held','face_count':len(fs),'receipt':a['operation_id']})
for k in ['base','crown']:
 rr=[x for x in groups if x['profile']==k];print(k,len(rr),sum(x['group_piece_count']for x in rr),sum(x['modeled_longpoint_LF']for x in rr),collections.Counter(x['group_piece_count']for x in rr))
buckets=collections.defaultdict(list)
for g in groups:
 sig=tuple([g['profile'],g['axis'],g['group_piece_count']]+[round(g[k],7)for k in ('x0','y0','x1','y1','base_z_ft','modeled_longpoint_LF')]);buckets[sig].append(g)
print('coincident',[[e['element_id']for e in v]for v in buckets.values()if len(v)>1])

out=p.parent/'belmont_revf';out.mkdir(exist_ok=True)
for g in groups:
 conflicts=[];ax=0 if g['axis']=='X' else 1;c=1-ax;keys=[['x0','x1'],['y0','y1']]
 for w in groups:
  if w is g or w['profile']!=g['profile'] or w['axis']!=g['axis'] or abs(w['base_z_ft']-g['base_z_ft'])>1e-5:continue
  if any(abs(w[x]-g[x])>1e-5 for x in keys[c]):continue
  a,b=keys[ax];run=min(w[b],g[b])-max(w[a],g[a])
  if run>0.001:conflicts.append(str(w['element_id'])+': '+str(round(run,4))+'ft')
 g['overlap_flags_among_qualified']='; '.join(conflicts)
with (out/'Belmont_model_longpoint_groups.csv').open('w',newline='',encoding='utf-8-sig')as fh:
 w=csv.DictWriter(fh,fieldnames=list(groups[0]));w.writeheader();w.writerows(groups)
print('flags',sum(bool(x['overlap_flags_among_qualified'])for x in groups))

