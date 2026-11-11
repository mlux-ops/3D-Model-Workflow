"""R043 viewer-only native wall FACE registration, never a certified Revit Room.

Uses an EXISTING authorized read-only export. No Revit operations, source pick
changes or fabricated room solids. Wall-line closures under .003 ft are repaired
only for visualization; the actual native endpoints remain in source metadata.
"""
import json
import re
from pathlib import Path
from shapely.geometry import LineString, Point, box
from shapely.geometry import Polygon
from shapely.affinity import rotate as polygon_rotate
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'deliverables/viewer3d/picks.json'
data=json.loads(DEST.read_text(encoding='utf-8'))
native=json.loads((ROOT/'scratch/viewer3d_revit_sources.json').read_text(encoding='utf-8'))['categories']
WALL_RECEIPT=native['walls']['receipt_id']
DOOR_RECEIPT=native['doors']['receipt_id']
WIN_RECEIPT=native['windows']['receipt_id']
PLUMB_RECEIPT=native['plumbing']['receipt_id']
LEVELS={'LOWER LEVEL':-5.,'1ST FLOOR':6+2/3,'2ND FLOOR':17+1/3,'3RD FLOOR':28.,'4TH FLOOR':38+2/3}

# Drawing-label registration seeds, *not* native room-element IDs. Faces are
# accepted only if geometrically closed AND plausible against plan area.
# Other rooms intentionally retain the older dimensioned drawing schematic.
ANCHORS={
 'PH-PRIMARY':(-517.43,200.98),
 'PH-BATH4':(-514.6,237.3),
 'PH-BATH3':(-515.3,221.5),
 'PH-WC':(-521.0,206.4),
 'PH-POWDER':(-530.1,230.5),
 'TX-PRIMARY':(-516.49,205.24),
 'TX-BATH2':(-514.6,235.6),
 'TX-BATH3':(-514.8,243.4),
 'TX-BATH4':(-516.5,245.1),
 'TX-POWDER':(-515.4,199.94),
 'TX-WC':(-513.3,210.8),
 'TX-POWDER2':(-530.46,238.81),
}
PAIR_SHIFT=-35.84  # only seeds, not a transform; mirrors native extents
ROOM_B_SHIFTS={'PH-WC':-23.30,'PH-POWDER':-5.16,'TX-WC':-38.80,
               'TX-BATH4':-32.53,'TX-POWDER':-34.60,'TX-POWDER2':-4.48,
               'PH-PRIMARY':-30.54,'TX-PRIMARY':-32.42}
AREA_TOL={'PH-BATH4':.15,'PH-BATH3':.22,'PH-WC':.30,'PH-POWDER':.30,
          'TX-BATH2':.25,'TX-BATH3':.25,'TX-WC':.30,'TX-POWDER2':.40}
AREA_TOL.update({'TX-BATH4':.24,'TX-POWDER':.22,'TX-POWDER2':.22})
AREA_TOL.update({'PH-PRIMARY':.25,'TX-PRIMARY':.25})

def valid_location(x):
 loc=x.get('location') or {}
 a,b=loc.get('start'),loc.get('end')
 if not (isinstance(a,list) and isinstance(b,list) and len(a)==3 and len(b)==3):return None
 return a,b

def wall_records(z):
 out=[]
 for e in native['walls']['items']:
  endpoints=valid_location(e)
  bounds=e.get('bounds') or {}
  if not endpoints or not bounds.get('min') or not bounds.get('max'):continue
  lo,hi=bounds['min'],bounds['max']
  if not (lo[2]<=z+.5 and hi[2]>=z+.5):continue
  a,b=endpoints
  dx,dy=b[0]-a[0],b[1]-a[1]
  if (dx*dx+dy*dy)**.5<.25:continue
  thickness=(hi[1]-lo[1]) if abs(dx)>abs(dy) else (hi[0]-lo[0])
  if not .04<thickness<3.:continue
  line=LineString([(a[0],a[1]),(b[0],b[1])])
  out.append((e,line,thickness))
 return out

def face_candidates(walls):
 solids=unary_union([line.buffer(t/2,cap_style=2) for _,line,t in walls])
 # .003 ft (<1/16 in) heals numerical wall-line contacts without inserting
 # invented nominal architectural wall lengths.
 solids=solids.buffer(.003).buffer(-.003)
 open_area=box(-557.2,181.,-508.4,249.2).difference(solids)
 faces=list(open_area.geoms) if hasattr(open_area,'geoms') else [open_area]
 return [f for f in faces if f.area>4 and not f.interiors]

def matched_wall(edge,walls):
 best=None
 for e,line,t in walls:
  # Source wall location curve should lie approximately half a wall thickness
  # outside the inferred room face and be parallel to it.
  if edge.distance(line)>max(.18,t*.62):continue
  overlap=edge.buffer(.045).intersection(line.buffer(t/2+.06)).length
  if overlap<.45:continue
  if best is None or edge.distance(line)<best[0]:best=(edge.distance(line),e,line,t)
 return best

def records_for_polygon(poly,z,walls,origin,side_label):
 ox,oy=origin
 ext=list(poly.exterior.coords)
 segments=[];associated=[]
 for i,(p,q) in enumerate(zip(ext,ext[1:])):
  edge=LineString([p,q])
  if edge.length<.16:continue
  match=matched_wall(edge,walls)
  if not match:continue
  _,e,line,t=match
  associated.append(e['id'])
  segments.append({'id':e['id'],'host_id':e['id'],
    'start_local_ft':[round(p[0]-ox,5),round(oy-p[1],5)],
    'end_local_ft':[round(q[0]-ox,5),round(oy-q[1],5)],
    'native_location_start_ft':e['location']['start'],
    'native_location_end_ft':e['location']['end'],
    'thickness_ft':round(t,5),
    'height_ft':round(min(10.15,(e['bounds']['max'][2]-z)),4),
    'type_name':e.get('name'),'receipt_id':WALL_RECEIPT,
    'wall_face_source':'INFERRED INTERIOR FACE from exact Revit wall location line and bounding thickness'})
 openings=[]
 for typ,receipt in [('doors',DOOR_RECEIPT),('windows',WIN_RECEIPT)]:
  for e in native[typ]['items']:
   host=e.get('host_id')
   if host not in associated:continue
   point=(e.get('location') or {}).get('point')
   if not point or abs(point[2]-z)>1.7:continue
   ept=Point(point[:2])
   if poly.boundary.distance(ept)>.7:continue
   name=e.get('name') or ''
   import re
   if typ=='doors':
    nominal=re.search(r'(\d+(?:\.\d+)?)\s*"\s*x\s*(\d+(?:\.\d+)?)\s*"',name,re.I)
    if not nominal:
     nominal=re.search(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)',name,re.I)
    width=float(nominal.group(1))/12 if nominal else None
    height=float(nominal.group(2))/12 if nominal else None
   else:
    m=re.search(r"(\d+)'(\d+)?\"?\s*x\s*(\d+)'(\d+)?",name)
    width=(int(m.group(1))+int(m.group(2) or 0)/12) if m else None
    height=(int(m.group(3))+int(m.group(4) or 0)/12) if m else None
   if not width:continue
   item={'id':e['id'],'kind':'door' if typ=='doors' else 'window',
     'host_id':host,'location_local_ft':[round(point[0]-ox,5),round(oy-point[1],5)],
     'location_native_ft':point,'rotation_radians':e['location'].get('rotation_radians'),
     'nominal_width_ft':width,'nominal_height_ft':height,
     'rough_opening_width_ft':None,'swing_handing':None,
     'sill_height_ft':None if typ=='windows' else 0,
     'receipt_id':receipt,'type_name':name,
     'source':'READ_ONLY_REVIT_HOSTED_INSERTION; type NOMINAL dimension, rough opening and handing UNVERIFIED'}
   if typ=='windows':
    # Preserve actual READ-ONLY native window FAMILY CATEGORY AABB as an
    # independent spatial witness. Family type nominal 3x8-8 or 5x8-8 is
    # NOT equal to actual Revit element AABB (which may include symbolic
    # geometry); neither proves a native glazing/frame solid or clear hole.
    winbounds=e.get('bounds') or {}
    lower,upper=winbounds.get('min'),winbounds.get('max')
    if lower and upper and all(upper[k]>lower[k] for k in range(3)):
     item['native_window_family_aabb']={
      'bounds_native_ft':winbounds,
      'min_local_xyz_ft':[round(lower[0]-ox,5),round(lower[2]-z,5),round(oy-upper[1],5)],
      'max_local_xyz_ft':[round(upper[0]-ox,5),round(upper[2]-z,5),round(oy-lower[1],5)],
      'receipt_id':WIN_RECEIPT,'revit_id':e['id'],'host_id':host,
      'confidence':'ACTUAL read-only Revit WINDOW element AABB, not window/glazing/frame family SOLID; inferred room-face association by native hosted wall, may contain symbolic geometry or pass outside inferred room'}
   if typ=='doors':
    doorbounds=e.get('bounds') or {}
    lower,upper=doorbounds.get('min'),doorbounds.get('max')
    if lower and upper and all(upper[k]>lower[k] for k in range(3)):
     item['native_door_family_aabb']={
      'bounds_native_ft':doorbounds,
      'min_local_xyz_ft':[round(lower[0]-ox,5),round(lower[2]-z,5),round(oy-upper[1],5)],
      'max_local_xyz_ft':[round(upper[0]-ox,5),round(upper[2]-z,5),round(oy-lower[1],5)],
      'receipt_id':DOOR_RECEIPT,'revit_id':e['id'],'host_id':host,
      'confidence':'ACTUAL read-only Revit DOOR element category AABB, NOT native leaf solid, actual swing/hinge/rough opening or certified clear width; AABB may include symbolic swing and family offsets; 3D bounds may overlap other families without proving physical collision'}
   if typ=='doors':
    bb=e.get('bounds') or {}
    lo,hi=bb.get('min'),bb.get('max')
    host_record=next((rec for rec,_,_ in walls if rec['id']==host),None)
    if lo and hi and host_record:
     hloc=host_record.get('location') or {}
     pa,pb=hloc.get('start'),hloc.get('end')
     if pa and pb:
      # Family bbox may include a symbolic swing sector. Detect a *probable*
      # opening side from the one-sided bound extension; no hinge or swing arc
      # is certified by a native bounding box.
      wall_vertical=abs(pa[0]-pb[0])<abs(pa[1]-pb[1])
      axis=0 if wall_vertical else 1
      negative=point[axis]-lo[axis]
      positive=hi[axis]-point[axis]
      if max(negative,positive)>=1.6 and max(negative,positive)>min(negative,positive)*2:
       component_sign=-1 if negative>positive else 1
       local_vector=[component_sign,0] if axis==0 else [0,-component_sign]
       item['aabb_suggested_open_side']={
        'native_axis':'X' if axis==0 else 'Y',
        'inward_local_xz_direction':local_vector,
        'bbox_extent_negative_ft':round(negative,4),
        'bbox_extent_positive_ft':round(positive,4),
        'confidence':'INFERRED FROM ASYMMETRICAL NATIVE DOOR FAMILY AABB; hinge, exact swing arc, hardware, hand UNVERIFIED'}
   if typ=='windows':
    b=e.get('bounds') or {}
    if b.get('min'):item['sill_height_ft']=round(max(0,b['min'][2]-z),4)
   openings.append(item)
 return segments,openings,sorted(set(associated))

stats=[]
for room in data['rooms']:
 rid=room['id']
 for inst in room['physical_instances']:
  side=inst['room_number'][-1]
  inst['unit_side']['mapping']='LATEST 2026-11-07 A2.1/A2.2: A EAST model wing, B WEST; source drawing registration; native Room ID still unavailable'
  if rid not in ANCHORS:continue
  ix,iy=ANCHORS[rid]
  if side=='B':ix+=ROOM_B_SHIFTS.get(rid,PAIR_SHIFT)
  z=inst['level']['elevation_ft']
  walls=wall_records(z)
  anchor=Point(ix,iy)
  faces=[f for f in face_candidates(walls) if f.buffer(.02).covers(anchor)]
  if len(faces)!=1:continue
  face=faces[0]
  expected=room['full_room_plan']['display_area_ft2']
  if abs(face.area-expected)>max(2.5,expected*AREA_TOL[rid]):continue
  ox,oy=face.bounds[0]/2+face.bounds[2]/2,face.bounds[1]/2+face.bounds[3]/2
  segments,openings,ids=records_for_polygon(face,z,walls,(ox,oy),side)
  if len(segments)<3:continue
  polygon=[[round(x-ox,5),round(oy-y,5)] for x,y in list(face.exterior.coords)[:-1]]
  arch={'room_assignment':'DRAWING-LABEL REGISTERED / INFERRED, NO NATIVE Revit ROOM ELEMENT ID',
    'registration_method':'2026-11-07 A2.1/A2.2 drawing label plus source wall-face topology',
    'registration_seed_native_xy_ft':[ix,iy],
    'origin_native_xy_ft':[round(ox,6),round(oy,6)],
    'native_level_elevation_ft':z,
    'coordinate_transform':'localX=nativeX-originX; localZ=originY-nativeY; localY=nativeZ-levelElevation',
    'floor_polygon_local_xz_ft':polygon,
    'floor_polygon_area_ft2':round(face.area,4),
    'drawing_display_area_ft2':expected,
    'drawing_vs_wall_face_difference_ft2':round(face.area-expected,4),
    'drawing_vs_wall_face_difference_percent':round(100*(face.area-expected)/expected,2),
    'area_conflict_flag':abs(face.area-expected)>max(1.5,expected*.10),
    'wall_segments':segments,'openings':openings,'native_wall_ids':ids,
    'wall_receipt_id':WALL_RECEIPT,
    'face_confidence':'NATIVE WALL CURVES/THICKNESS; ROOM MEMBERSHIP DRAWING-INFERRED; topology closure tolerance 0.003 ft',
    'ceiling_polygon_same_plan_footprint':'ILLUSTRATIVE ONLY, no certified ceiling profile',
    'source_area_override_unchanged':room['full_room_plan']['source_floor_area_ft2']}
  inst['architecture']=arch
  inst['room_geometry_fidelity']='REGISTERED_NATIVE_WALL_FACE_POLYGON; ROOM_NAME_INFERRED'
  stats.append((rid,inst['room_number'],round(face.area,2),len(segments),len(openings)))

# R047: PH-BATH2 305A/B are spatially visible in the Nov-07 third-floor
# elevator-lobby plan but the native wall network contains short endpoint gaps:
# using the global face graph joins these ~5x7 ft baths to the corridor.
# Close ONLY the drawing-identified room faces between actual native wall faces.
# Four coordinate edges derive directly from wall element BOUNDING FACES, not
# historic area; the y=213.251 wall face is a 8-in CMU furring partition
# spanning BOTH 305 rooms (wall 10808894, from lower-level host record).
def native_wall(element_id):
 return next((x for x in native['walls']['items'] if x['id']==element_id),None)

PH2_SOURCE={
 'A':{'left':12590818,'right':16428596,'front':16428780,'rear':10808894,
      'host':16428596,'door':16428635,'south_gap_wall':10937080},
 'B':{'left':12380128,'right':12590818,'front':15959004,'rear':10808894,
      'host':12380128,'door':12591854,'south_gap_wall':10937080}
}
for room in data['rooms']:
 if room['id']!='PH-BATH2':continue
 for inst in room['physical_instances']:
  side=inst['room_number'][-1]
  links=PH2_SOURCE[side]
  left=native_wall(links['left']);right=native_wall(links['right'])
  front=native_wall(links['front']);rear=native_wall(links['rear'])
  door=next((x for x in native['doors']['items'] if x['id']==links['door']),None)
  if not all([left,right,front,rear,door]):continue
  # Room boundaries: left/right are native wall interior faces. Source labels
  # distinguish each 305 from the central elevator lobby and adjacent rooms.
  x0=round(left['bounds']['max'][0],5)
  x1=round(right['bounds']['min'][0],5)
  y0=round(front['bounds']['max'][1],5)
  y1=round(rear['bounds']['min'][1],5)
  if not (4.5<x1-x0<5.7 and 6.8<y1-y0<7.5):continue
  z=inst['level']['elevation_ft']
  ox,oy=(x0+x1)/2,(y0+y1)/2
  # Local Z is negative toward north. Top floor-plan back is NATIVE y=max.
  coords=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
  polygon=[[round(x-ox,5),round(oy-y,5)] for x,y in coords]
  byside=[('front',(x0,y0),(x1,y0),front),('right',(x1,y0),(x1,y1),right),
          ('rear',(x1,y1),(x0,y1),rear),('left',(x0,y1),(x0,y0),left)]
  walls=[]
  for face,a,b,e in byside:
   bounds=e['bounds'];line=e['location']
   wall_thickness=(bounds['max'][0]-bounds['min'][0]) if face in ('left','right') else (bounds['max'][1]-bounds['min'][1])
   walls.append({'id':e['id'],'host_id':e['id'],'face':face,
    'start_local_ft':[round(a[0]-ox,5),round(oy-a[1],5)],
    'end_local_ft':[round(b[0]-ox,5),round(oy-b[1],5)],
    'native_location_start_ft':line['start'],'native_location_end_ft':line['end'],
    'thickness_ft':round(wall_thickness,5),'height_ft':round(min(10.15,bounds['max'][2]-z),4),
    'type_name':e.get('name'),'receipt_id':WALL_RECEIPT,
    'wall_face_source':'NATIVE WALL BOUNDING FACE plus DRAWING-inferred boundary closure for incomplete wall-line junction'})
  dp=door['location']['point']
  import re
  m=re.search(r'(\d+)\s*"\s*x\s*(\d+)\s*"',door['name'])
  openings=[{'id':door['id'],'kind':'door','host_id':links['host'],
    'location_local_ft':[round(dp[0]-ox,5),round(oy-dp[1],5)],
    'location_native_ft':dp,'rotation_radians':door['location'].get('rotation_radians'),
    'nominal_width_ft':int(m.group(1))/12 if m else None,
    'nominal_height_ft':int(m.group(2))/12 if m else None,
    'rough_opening_width_ft':None,'swing_handing':None,'sill_height_ft':0,
    'receipt_id':DOOR_RECEIPT,'type_name':door.get('name'),
    'source':'NATIVE HOSTED DOOR INSERTION, nominal type; opening and swing unverified'}]
  # 305 A/B door's family AABB includes an asymmetric symbolic extent. The
  # extent can suggest the open side, not native hinge/swing handing.
  door_bounds=door.get('bounds') or {}
  if door_bounds.get('min') and door_bounds.get('max'):
   lo,hi=door_bounds['min'],door_bounds['max']
   if all(hi[k]>lo[k] for k in range(3)):
    openings[0]['native_door_family_aabb']={
     'bounds_native_ft':door_bounds,
     'min_local_xyz_ft':[round(lo[0]-ox,5),round(lo[2]-z,5),round(oy-hi[1],5)],
     'max_local_xyz_ft':[round(hi[0]-ox,5),round(hi[2]-z,5),round(oy-lo[1],5)],
     'receipt_id':DOOR_RECEIPT,'revit_id':door['id'],'host_id':links['host'],
     'confidence':'ACTUAL read-only native Revit DOOR family category AABB; PH-BATH2 room corner closure DRAWING-CALIBRATED, not Revit Room solid; AABB may contain symbolic swing, not native door leaf or construction rough opening'}
   neg=dp[0]-lo[0];pos=hi[0]-dp[0]
   if max(neg,pos)>1.6 and max(neg,pos)>min(neg,pos)*2:
    openings[0]['aabb_suggested_open_side']={
     'native_axis':'X','inward_local_xz_direction':[-1 if neg>pos else 1,0],
     'bbox_extent_negative_ft':round(neg,4),'bbox_extent_positive_ft':round(pos,4),
     'confidence':'INFERRED from asymmetric Revit door AABB only; no certified hinge/swing arc or handedness'}
  area=(x1-x0)*(y1-y0)
  arch={'room_assignment':'DRAWING-REGISTERED + NATIVE WALL-FACE CALIBRATED CLOSURE; NOT NATIVE REVIT ROOM',
    'registration_method':'NOV-07 A2.2 305A/B + four actual native wall bounding faces, partial wall gaps bridged by drawing room identity',
    'registration_seed_native_xy_ft':[round(ox,5),round(oy,5)],
    'origin_native_xy_ft':[round(ox,6),round(oy,6)],
    'native_level_elevation_ft':z,
    'coordinate_transform':'localX=nativeX-originX; localZ=originY-nativeY; localY=nativeZ-levelElevation',
    'floor_polygon_local_xz_ft':polygon,'floor_polygon_area_ft2':round(area,4),
    'drawing_display_area_ft2':room['full_room_plan']['display_area_ft2'],
    'drawing_vs_wall_face_difference_ft2':round(area-room['full_room_plan']['display_area_ft2'],4),
    'drawing_vs_wall_face_difference_percent':round(100*(area-room['full_room_plan']['display_area_ft2'])/room['full_room_plan']['display_area_ft2'],2),
    'area_conflict_flag':abs(area-room['full_room_plan']['display_area_ft2'])>1.5,
    'wall_segments':walls,'openings':openings,'native_wall_ids':sorted({x['id'] for x in [left,right,front,rear]}),
    'wall_receipt_id':WALL_RECEIPT,'face_confidence':'FOUR SOURCE WALL FACES + 2026-11-07 DRAWING-REGISTERED ROOM CLOSURE; CORNER ENDPOINTS NOT NATIVE ROOM POLYGON',
    'ceiling_polygon_same_plan_footprint':'ILLUSTRATIVE ONLY; no certified ceiling profile',
    'source_area_override_unchanged':room['full_room_plan']['source_floor_area_ft2'],
    'unresolved':['4 original native wall line junctions have gaps; bounded face corners are calibrated closure, not exact intersecting BIM wall-face curves','Door 28x96 type is nominal; no rough opening/hinge/swing verified','Fixture symbol is not Revit family solid']}
  inst['architecture']=arch
  inst['room_geometry_fidelity']='NATIVE_WALL_FACES_WITH_DRAWING_CALIBRATED_CORNERS'
  stats.append((room['id'],inst['room_number'],round(area,2),len(walls),len(openings)))

# Reconcile WC plan-symbol toilet with source Revit plumbing insertion at the
# correct wall. A family insertion is NOT the center of a certified toilet
# solid: project a generic diagram 1.05 ft toward the polygon interior and
# retain both coordinates plus the explicit non-certified offset.
WC_PLUMB_ANCHORS={
 'PH-WC':{'A':16428736,'B':15957324},
 'TX-WC':{'A':16437697,'B':18055997}
}
plumb_by_id={x['id']:x for x in native['plumbing']['items']}
for room in data['rooms']:
 ids=WC_PLUMB_ANCHORS.get(room['id'])
 symbols=room.get('full_room_plan',{}).get('fixture_symbol_diagram') or {}
 if not ids and not any(x.get('kind')=='toilet' for x in symbols.get('items',[])):continue
 for inst in room['physical_instances']:
  arch=inst.get('architecture')
  if not arch:continue
  floor=Polygon(arch['floor_polygon_local_xz_ft'])
  ox,oy=arch['origin_native_xy_ft']
  if ids:element=plumb_by_id.get(ids[inst['room_number'][-1]])
  else:
   candidates=[]
   for e in native['plumbing']['items']:
    if e.get('name')!='270AA.101':continue
    p=(e.get('location') or {}).get('point')
    if not p or abs(p[2]-arch['native_level_elevation_ft'])>.6:continue
    local=Point(p[0]-ox,oy-p[1])
    nearest=floor.boundary.distance(local)
    if nearest<=.28 and floor.buffer(.3).covers(local):candidates.append((nearest,e))
   element=min(candidates,key=lambda x:x[0])[1] if candidates else None
  p=(element.get('location') or {}).get('point') if element else None
  if not p or abs(p[2]-arch['native_level_elevation_ft'])>1.:continue
  ax,az=p[0]-ox,oy-p[1]
  roomcenter=floor.centroid
  dx,dz=roomcenter.x-ax,roomcenter.y-az
  length=(dx*dx+dz*dz)**.5
  if length<.5:continue
  dx,dz=dx/length,dz/length
  # Place the generic WC *study proxy* at the smallest inward offset that
  # actually fits its source-unverified 1.4x2.05-ft diagram footprint.
  # This is a geometric visualization repair only: NEVER a toilet rough-in.
  from math import atan2,cos,sin
  turn=atan2(dx,dz)
  clear_floor=floor.buffer(-.012)
  chosen=None
  for tenth in range(21,35):
   offset=tenth*.05
   cx,cz=ax+dx*offset,az+dz*offset
   corners=[]
   for sx,sz in [(-1,-1),(-1,1),(1,-1),(1,1)]:
    ux=sx*1.4/2;uz=sz*2.05/2
    corners.append(Point(cx+ux*cos(turn)+uz*sin(turn),cz-ux*sin(turn)+uz*cos(turn)))
   if not all(clear_floor.covers(pt) for pt in corners):continue
   if any(((cx-o['location_local_ft'][0])**2+(cz-o['location_local_ft'][1])**2)**.5<
           o['nominal_width_ft']/2+1.25+.15 for o in arch['openings'] if o['kind']=='door'):continue
   chosen=(cx,cz,offset);break
  if chosen is None:
   cx,cz,offset=ax+dx*1.05,az+dz*1.05,1.05
   if not floor.buffer(-.1).covers(Point(cx,cz)):continue
  else:cx,cz,offset=chosen
  native_bounds=element.get('bounds') or {}
  lower,upper=native_bounds.get('min'),native_bounds.get('max')
  native_aabb=None
  if lower and upper and all(upper[k]>lower[k] for k in range(3)):
   native_aabb={
    'bounds_native_ft':native_bounds,
    'min_local_xyz_ft':[round(lower[0]-ox,5),round(lower[2]-arch['native_level_elevation_ft'],5),round(oy-upper[1],5)],
    'max_local_xyz_ft':[round(upper[0]-ox,5),round(upper[2]-arch['native_level_elevation_ft'],5),round(oy-lower[1],5)],
    'receipt_id':PLUMB_RECEIPT,'revit_id':element['id'],
    'confidence':'ACTUAL Revit plumbing-element category AABB, NOT family solid mesh; named-room attribution drawing-inferred; may extend through walls or contain family voids'}
  arch['toilet_proxy_anchor']={
   'native_plumbing_id':element['id'],'name':element.get('name'),
   'receipt_id':PLUMB_RECEIPT,'native_insertion_ft':p,
   'local_native_insertion_xz_ft':[round(ax,4),round(az,4)],
   'illustrative_proxy_center_xz_ft':[round(cx,4),round(cz,4)],
   'illustrative_front_vector_local_xz':[round(dx,4),round(dz,4)],
   'offset_from_native_insertion_ft':round(offset,3),
   'proxy_polygon_door_gate_passed':chosen is not None,
   'native_family_aabb':native_aabb,
   'confidence':'DRAWING TOILET PICTOGRAM + READ-ONLY 270AA PLUMBING INSERTION; ROOM MATCH INFERRED; smallest inward offset fitting a GENERIC 1.4x2.05ft footprint and avoiding nominal hosted door, NOT a plumbing rough-in or native family solid'
  }

# Revit casework bound/provenance is substantially stronger than generic
# drawing-relative 3D vanity cubes. Accept only a room-contained native
# countertop family with 70%+ actual AABB plan overlap; never treat its
# category-level AABB as an exact cabinet mesh. Preserve multiple distinct
# vanities, suppress overlapping source families so they do not double-render.
casework_receipt=native['casework']['receipt_id']
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture')
  if not arch or room['id']=='PH-BATH4':continue
  poly=Polygon(arch['floor_polygon_local_xz_ft'])
  ox,oy=arch['origin_native_xy_ft'];z=arch['native_level_elevation_ft']
  candidates=[]
  for e in native['casework']['items']:
   if e.get('name')!='Countertop':continue
   b=e.get('bounds') or {};lo,hi=b.get('min'),b.get('max')
   if not lo or not hi or abs(lo[2]-z)>3.6 or hi[2]-z>5:continue
   wide,deep=hi[0]-lo[0],hi[1]-lo[1]
   if not (.7<wide<12 and .7<deep<12):continue
   footprint=box(lo[0]-ox,oy-hi[1],hi[0]-ox,oy-lo[1])
   if footprint.area<.5 or poly.intersection(footprint).area/footprint.area<.70:continue
   candidates.append((footprint.area,e,footprint))
  selected=[]
  for _,e,fp in sorted(candidates,key=lambda t:t[0],reverse=True):
   if any(fp.intersection(prev).area/max(.01,min(fp.area,prev.area))>.5 for prev in [x[2] for x in selected]):continue
   selected.append((e['id'],e,fp))
  arch['native_casework_proxies']=[]
  for _,e,fp in selected[:3]:
   b=e['bounds'];lo,hi=b['min'],b['max']
   arch['native_casework_proxies'].append({
    'id':e['id'],'kind':'Countertop','receipt_id':casework_receipt,
    'native_bounds_ft':b,'local_center_xz_ft':[round((lo[0]+hi[0])/2-ox,5),round(oy-(lo[1]+hi[1])/2,5)],
    'width_x_ft':round(hi[0]-lo[0],4),'depth_z_ft':round(hi[1]-lo[1],4),
    'min_height_ft':round(lo[2]-z,4),'max_height_ft':round(hi[2]-z,4),
    'source_confidence':'EXACT NATIVE REVIT CATEGORY AABB; naming countertop; room spatial inclusion inferred, no solid geometry or selected basin'})
  for counter in arch['native_casework_proxies']:
   wx=counter['local_center_xz_ft'][0]+ox
   wy=oy-counter['local_center_xz_ft'][1]
   counter_top=z+counter['max_height_ft']
   insertions=[]
   for e in native['plumbing']['items']:
    pt=(e.get('location') or {}).get('point')
    if not pt or e.get('name')=='270AA.101':continue
    if abs(pt[0]-wx)>.8 or abs(pt[1]-wy)>.8 or abs(pt[2]-counter_top)>1.30:continue
    insertions.append((abs(pt[0]-wx)+abs(pt[1]-wy),e,pt))
   if insertions:
    _,e,pt=min(insertions,key=lambda v:v[0])
    counter['closest_native_plumbing_insertion']={
     'id':e['id'],'name':e.get('name'),'receipt_id':PLUMB_RECEIPT,
     'location_native_ft':pt,
     'location_local_xz_ft':[round(pt[0]-ox,5),round(oy-pt[1],5)],
     'confidence':'NATIVE PLUMBING LOCATION within 0.8ft of Revit countertop center; actual faucet/basin identity and countertop fixture opening UNVERIFIED'}

# Selected Duravit tubs MUST remain visually recognizable. The R042 fractional
# pictogram was suppressed when 3D generic corners crossed native L-shaped
# wall faces. Instead locate the actual manufacturer 59x29.5-inch nominal
# footprint inside the read-only wall-face polygon as close as defensible to
# the Nov 07 plan symbol. This is a CALIBRATED DRAWING POSITION, not a Revit
# native tub insertion, rough-in, tolerance or installation dimension.
TUB_NOMINAL=(59/12,29.5/12)
for room in data['rooms']:
 if not room.get('program',{}).get('tub_selected'):continue
 fixture_specs=json.loads((ROOT/'rooms'/room['id']/'plumbing.json').read_text(encoding='utf-8'))
 tub_record=next((x for x in fixture_specs.get('fixtures',[]) if x.get('model_or_sku')=='700332000000090'),None)
 if not tub_record:continue
 plan=room.get('full_room_plan',{}).get('fixture_symbol_diagram') or {}
 tub_symbol=next((x for x in plan.get('items',[]) if x.get('kind')=='tub'),None)
 if not tub_symbol:continue
 for inst in room['physical_instances']:
  arch=inst.get('architecture')
  if not arch:continue
  poly=Polygon(arch['floor_polygon_local_xz_ft'])
  if not poly.is_valid or poly.area<10:continue
  xmin,zmin,xmax,zmax=poly.bounds
  xfrac=1-tub_symbol['x_fraction'] if inst.get('plan_is_mirrored_B') else tub_symbol['x_fraction']
  target=((xmax-xmin)*xfrac+xmin,(zmax-zmin)*tub_symbol['z_fraction']+zmin)
  # Actual native casework bounds and separately native-anchored WC insertion
  # provide a stricter conflict gate than polygon containment alone. Do not
  # treat an arbitrary drawing tub symbol as license to overlap source
  # countertop or a generic but explicitly source-hosted toilet proxy.
  protected=[]
  for c in arch.get('native_casework_proxies',[]):
   xx,zz=c['local_center_xz_ft'];ww=c['width_x_ft'];dd=c['depth_z_ft']
   protected.append(('NATIVE_COUNTERTOP_AABB_'+str(c['id']),box(xx-ww/2,zz-dd/2,xx+ww/2,zz+dd/2)))
  toilet=arch.get('toilet_proxy_anchor')
  if toilet:
   xx,zz=toilet['illustrative_proxy_center_xz_ft']
   dx,dz=toilet['illustrative_front_vector_local_xz']
   from math import atan2,degrees
   theta=degrees(atan2(dx,dz))
   proxy=polygon_rotate(box(xx-.70,zz-1.025,xx+.70,zz+1.025),-theta,origin=(xx,zz))
   protected.append(('NATIVE_ANCHORED_GENERIC_TOILET_'+str(toilet['native_plumbing_id']),proxy))
   # A native point PLUS an invented-offset generic envelope is NOT the same
   # as the actual read-only Revit toilet family's measured BOUNDING BOX.
   # Protect the source AABB separately: R051's 007B nominal tub passed the
   # generic proxy test yet overlapped native toilet 16297835 by ~0.47 SF.
   # AABB may include family voids and is NOT a certified solid, but an
   # intersection cannot be passed off as demonstrated noncolliding geometry.
   native_toilet=next((e for e in native['plumbing']['items']
                      if e.get('id')==toilet['native_plumbing_id']),None)
   b=(native_toilet or {}).get('bounds') or {}
   lo,hi=b.get('min'),b.get('max')
   if lo and hi:
    ox,oy=arch['origin_native_xy_ft']
    native_box=box(lo[0]-ox,oy-hi[1],hi[0]-ox,oy-lo[1])
    if native_box.is_valid and native_box.area>.05:
     protected.append(('NATIVE_TOILET_AABB_'+str(toilet['native_plumbing_id']),native_box))
  # Native wall-face bounds are geometrical, not construction clearances. Use
  # only 0.008 ft visual face margin to avoid crossing a wall: not a clearance
  # recommendation or an assertion of installation feasibility.
  interior=poly.buffer(-.008)
  from math import hypot
  candidates=[]
  tub_fit_audit={'evaluated':0,'outside_wall_face':0,'native_counter_or_wc_intersection':0,
                 'native_hosted_door_gate':0,'source_compatible_candidate_count':0,
                 'nominal_size_ft':[round(x,6) for x in TUB_NOMINAL],
                 'drawing_pictogram_target_local_xz_ft':[round(v,5) for v in target],
                 'protected_source_ids':[name for name,_ in protected],
                 'confidence':'VIEWER GEOMETRY GATES, NOT REVIT FAMILY SOLID / CODE CLEARANCE'}
  for rotation,ww,dd in [(0,TUB_NOMINAL[0],TUB_NOMINAL[1]),(90,TUB_NOMINAL[1],TUB_NOMINAL[0])]:
   if ww>xmax-xmin or dd>zmax-zmin:continue
   xlo,xhi=xmin+ww/2,xmax-ww/2
   zlo,zhi=zmin+dd/2,zmax-dd/2
   if xlo>xhi or zlo>zhi:continue
   xstep=.07;zstep=.07
   nx=int((xhi-xlo)/xstep)+1
   nz=int((zhi-zlo)/zstep)+1
   # Native face segment midpoints are better than a 0.07ft grid near a
   # nominal 59in tub inside a ~4.93ft alcove: the permissible center
   # interval can be just .004ft, smaller than the coarse grid resolution.
   xs={xlo,xhi,(xlo+xhi)/2}
   zs={zlo,zhi,(zlo+zhi)/2}
   for wseg in arch['wall_segments']:
    a,b=wseg['start_local_ft'],wseg['end_local_ft']
    if abs(a[1]-b[1])<.035 and abs(a[0]-b[0])>=ww-.15:
     xs.add((a[0]+b[0])/2)
     for offset in [.02,.045]:
      zs.add(min(zhi,max(zlo,a[1]+(dd/2+offset))))
      zs.add(min(zhi,max(zlo,a[1]-(dd/2+offset))))
    if abs(a[0]-b[0])<.035 and abs(a[1]-b[1])>=dd-.15:
     zs.add((a[1]+b[1])/2)
     for offset in [.02,.045]:
      xs.add(min(xhi,max(xlo,a[0]+(ww/2+offset))))
      xs.add(min(xhi,max(xlo,a[0]-(ww/2+offset))))
   for ix in range(nx+2):xs.add(min(xhi,xlo+ix*xstep))
   for iz in range(nz+2):zs.add(min(zhi,zlo+iz*zstep))
   for cx in sorted(xs):
    if not xlo<=cx<=xhi:continue
    for cz in sorted(zs):
     if not zlo<=cz<=zhi:continue
     tub_fit_audit['evaluated']+=1
     tub_foot=box(cx-ww/2,cz-dd/2,cx+ww/2,cz+dd/2)
     if not interior.covers(tub_foot):
      tub_fit_audit['outside_wall_face']+=1;continue
     if any(tub_foot.intersection(occupied).area>.016 for _,occupied in protected):
      tub_fit_audit['native_counter_or_wc_intersection']+=1;continue
     # A nominal door leaf box is not a verified swing. Gate only the
     # depiction overlap with a known hosted opening center.
     # Match the existing viewer's conservative nominal hosted door gate
     # exactly; the previous generator checked only 1.47ft while browser
     # rejected at ~2.56ft, falsely labeling 305A/B as valid 3D placements.
     if any(hypot(cx-o['location_local_ft'][0],cz-o['location_local_ft'][1])<
            o['nominal_width_ft']/2+min(1.25,hypot(ww,dd)/2)+.15
            for o in arch['openings'] if o['kind']=='door'):
      tub_fit_audit['native_hosted_door_gate']+=1;continue
     err=hypot(cx-target[0],cz-target[1]) + (1.4 if rotation==90 else 0)
     candidates.append((err,cx,cz,rotation,ww,dd))
  tub_fit_audit['source_compatible_candidate_count']=len(candidates)
  arch['selected_tub_fit_audit']=tub_fit_audit
  if not candidates:
   arch['selected_tub_unlocated_reason']='Selected Duravit 59x29.5in nominal 3D tub has NO sampled nonconflicting position inside source wall-face enclosure once native countertop AABBs, the actual Revit toilet family AABB, illustrative toilet envelope and hosted doors are protected. Selected but 3D UNLOCATED, not a deleted fixture or proven construction impossibility.'
   arch['selected_tub_conflicting_native_objects']=[name for name,_ in protected]
   continue
  err,cx,cz,rotation,ww,dd=min(candidates,key=lambda c:c[0])
  displacement=hypot(cx-target[0],cz-target[1])
  tub_fit_audit['best_candidate_displacement_ft']=round(displacement,4)
  tub_fit_audit['best_candidate_orientation_degrees']=rotation
  if displacement>1.65:
   arch['selected_tub_unlocated_reason']='Any nominal Duravit 59x29.5in model fit avoiding native casework and source-anchored WC would require '+str(round(displacement,3))+'ft displacement from Nov-07 drawing pictogram (>1.65ft source-confidence gate). Render 2D UNLOCATED marker, not falsely located 3D tub.'
   arch['selected_tub_conflicting_native_objects']=[name for name,_ in protected]
   continue
  arch['selected_tub_proxy']={
   'model_or_sku':tub_record['model_or_sku'],
   'source_row_id':tub_record['source_row_id'],'source_description':tub_record['description'],
   'nominal_width_ft':round(TUB_NOMINAL[0],6),'nominal_depth_ft':round(TUB_NOMINAL[1],6),
   'local_center_xz_ft':[round(cx,5),round(cz,5)],
   'rotation_degrees':rotation,
   'render_width_x_ft':round(ww,6),'render_depth_z_ft':round(dd,6),
   'drawing_pictogram_target_xz_ft':[round(target[0],5),round(target[1],5)],
   'calibrated_symbol_displacement_ft':round(displacement,4),
   'confidence':'NOMINAL DURAVIT 59x29.5 SIZE from FROZEN plumbing record; drawing symbol translated to source-face polygon to eliminate collision; no native family insertion, shower PAN, fixture rough-in, working clearance or construction fit certification'
  }

# Native Revit OST_Ceilings GWB read-only AABBs can establish the underside
# elevation even if exact ceiling trim/profile is unavailable. Never infer a
# room-specific ceiling from a building-wide slab: require a tight XY footprint
# (<=1.75x room area) and >=88% coverage of the room face.
ceiling_receipt=native['ceilings']['receipt_id']
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture')
  if not arch:continue
  floor=Polygon(arch['floor_polygon_local_xz_ft'])
  ox,oy=arch['origin_native_xy_ft'];z=arch['native_level_elevation_ft']
  cands=[]
  for e in native['ceilings']['items']:
   if e.get('name')!='GWB':continue
   bounds=e.get('bounds') or {};lo,hi=bounds.get('min'),bounds.get('max')
   if not lo or not (z+7<lo[2]<z+12):continue
   footprint=box(lo[0]-ox,oy-hi[1],hi[0]-ox,oy-lo[1])
   if footprint.area>floor.area*1.75:continue
   overlap=floor.intersection(footprint).area/floor.area
   if overlap<.88:continue
   cands.append((footprint.area,1-overlap,e))
  if not cands:continue
  _,_,e=min(cands,key=lambda c:(c[0],c[1]))
  lo,hi=e['bounds']['min'],e['bounds']['max']
  arch['native_ceiling_evidence']={
   'id':e['id'],'name':e['name'],'receipt_id':ceiling_receipt,
   'underside_height_ft':round(lo[2]-z,5),'top_height_ft':round(hi[2]-z,5),
   'native_bounds_ft':e['bounds'],'drawing_datum_ft':9.25,
   'confidence':'READ_ONLY GWB CEILING AABB underside elevation; extent intersection with DRAWING-INFERRED room floor face; no exact ceiling cut profile',
   'height_conflict_with_drawing_ft':round(lo[2]-z-9.25,5)}

# Independently register the physically adjoining 310 zones without borrowing
# any of their geometry/fixtures/material quantities for PH4 311.
for room in data['rooms']:
 if room['id']!='PH-BATH4':continue
 for inst in room['physical_instances']:
  side=inst['room_number'][-1]
  x=-514.8 if side=='A' else -550.6
  z=inst['level']['elevation_ft'];walls=wall_records(z)
  fs=[f for f in face_candidates(walls) if f.buffer(.02).covers(Point(x,243.65))]
  if not fs or 'architecture' not in inst:continue
  f=fs[0];origin=inst['architecture']['origin_native_xy_ft']
  seg,opens,ids=records_for_polygon(f,z,walls,origin,side)
  # Adjacent 310A/B toilet and lavatory evidence is spatially independent of
  # the 311 wet room. Native fixture LOCATIONS are exact, but type-to-room
  # membership is drawing-registered; family outlines remain illustrative.
  adjacent_fixture_ids={'A':(16428804,16428825,16438318),
                        'B':(16377760,16428332,16438253)}
  selected=adjacent_fixture_ids[side]
  fixture_evidence=[]
  for kind,cat,eid in [('toilet','plumbing',selected[0]),
                       ('lavatory_reference','plumbing',selected[1]),
                       ('countertop','casework',selected[2])]:
   e=next((v for v in native[cat]['items'] if v['id']==eid),None)
   if not e:continue
   raw_point=(e.get('location') or {}).get('point')
   bounds=e.get('bounds') or {}
   lo,hi=bounds.get('min'),bounds.get('max')
   bounds_center=[(a+b)/2 for a,b in zip(lo,hi)] if lo and hi else None
   # Some read-only casework records report the placeholder point [0,0,0]
   # although their actual Revit category AABB is centered in 310. Never
   # classify the AABB center as a native insertion point. Prefer source
   # location only when finite, geographically near its own AABB, and
   # legitimately within the source-derived compartment. Other category
   # records can use an explicitly typed bounds-center fallback.
   source_point_valid=bool(raw_point and len(raw_point)>=3 and
    all(isinstance(v,(int,float)) and abs(v)<1e7 for v in raw_point) and
    (not bounds_center or all(lo[k]-.5<=raw_point[k]<=hi[k]+.5 for k in range(3))) and
    f.buffer(.7).covers(Point(raw_point[:2])))
   native_pt=raw_point if source_point_valid else bounds_center
   if not native_pt or not f.buffer(.7).covers(Point(native_pt[:2])):continue
   source_kind='NATIVE_INSERTION' if source_point_valid else 'NATIVE_BOUNDS_CENTER'
   fixture_evidence.append({'kind':kind,'id':eid,'name':e.get('name'),
     'native_insertion_ft':raw_point if source_point_valid else None,
     'native_bounds_center_ft':bounds_center,
     'coordinate_reference_kind':source_kind,
     'location_local_xz_ft':[round(native_pt[0]-origin[0],5),round(origin[1]-native_pt[1],5)],
     'bounds_native_ft':bounds,
     'receipt_id':native[cat]['receipt_id'],
     'classification':source_kind+' from READ-ONLY Revit element; 310 room membership DRAWING-INFERRED; family SOLID NOT EXTRACTED'})
  inst['architecture']['adjacent_zone_geometry']={
    'number':'310'+side,'label':inst['adjacent_zone']['label'],
    'floor_polygon_local_xz_ft':[[round(a-origin[0],5),round(origin[1]-b,5)] for a,b in list(f.exterior.coords)[:-1]],
    'area_display_ft2':round(f.area,3),'wall_segments':seg,'openings':opens,
    'native_wall_ids':ids,'tile_scope':'SEPARATE COMPARTMENT, excluded from 311 original 40.2 SF pool',
    'native_fixture_evidence':fixture_evidence}
  # Never transfer the 311 room's GWB evidence into its separate 310 zone.
  # Apply the same conservative 88%-coverage / 1.75x-footprint conditions to
  # the independent 310 face, and leave the source absent if no match exists.
  adjacent_gwb=[]
  for e in native['ceilings']['items']:
   if e.get('name')!='GWB':continue
   b=e.get('bounds') or {};lo,hi=b.get('min'),b.get('max')
   if not lo or not hi or not (z+7<lo[2]<z+12):continue
   fp=box(lo[0],lo[1],hi[0],hi[1])
   if fp.area>f.area*1.75 or f.area<.01:continue
   coverage=f.intersection(fp).area/f.area
   if coverage<.88:continue
   adjacent_gwb.append((fp.area,-coverage,e,lo,hi))
  if adjacent_gwb:
   _,_,e,lo,hi=min(adjacent_gwb,key=lambda t:(t[0],t[1]))
   inst['architecture']['adjacent_zone_geometry']['native_ceiling_evidence']={
    'id':e['id'],'receipt_id':ceiling_receipt,
    'underside_height_ft':round(lo[2]-z,5),
    'top_height_ft':round(hi[2]-z,5),
    'native_bounds_ft':e['bounds'],
    'confidence':'INDEPENDENT 310 GWB AABB footprint overlap >=88%, area <=1.75x; 310 named-room attribution remains drawing-inferred, no true ceiling trim profile'}

for room in data['rooms']:
 for inst in room['physical_instances']:
  # Context is a level inventory, never assigned to a named room.
  inst['unit_side']['value']=inst['room_number'][-1]
  # Refilter native level inventory by the now-confirmed drawing wing.
  xlo,xhi=(-533.5,-507) if inst['unit_side']['value']=='A' else (-559,-533.5)
  for key,records in inst['unit_context'].items():
   inst['unit_context'][key]=[x for x in records if x['bounds']['max'][0]>=xlo and x['bounds']['min'][0]<=xhi] if records else []

# R058 is a VIEWER interpretation manifest, not an authoritative source
# mutation. Keep the native category bounds/receipt IDs separately available
# and expose when a full 3D model is WITHHELD or only a generic silhouette.
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture') or {}
  program=room.get('program') or {}
  planItems=(room.get('full_room_plan') or {}).get('fixture_symbol_diagram') or {}
  fixtureKinds=[f.get('kind') for f in planItems.get('items',[])]
  unselectedSink=bool(re.search('basin UNSELECTED|sink UNSELECTED',
   program.get('plumbing_truth',''),re.I))
  counters=[]
  for item in arch.get('native_casework_proxies',[]):
   w,d=item['width_x_ft'],item['depth_z_ft']
   sink=item.get('closest_native_plumbing_insertion')
   if unselectedSink:
    basin='UNSELECTED_BASIN__NO_GENERIC_SOLID'
   elif not sink:
    basin='3D_UNLOCATED__NO_ATTRIBUTABLE_NATIVE_PLUMBING'
   else:
    x,z=item['local_center_xz_ft']
    sx,sz=sink['location_local_xz_ft']
    basin=('SOURCE_XZ__GENERIC_ILLUSTRATIVE_BASIN_FITS_AABB'
      if abs(sx-x)+min(.52,w*.31)<=w/2+.00001 and
         abs(sz-z)+min(.38,d*.30)<=d/2+.00001
      else '3D_UNLOCATED__NATIVE_PLAN_XY_RAISED_LOCATOR_ONLY')
   counters.append({
    'native_casework_id':item['id'],'native_receipt_id':item['receipt_id'],
    'native_element_aabb_ft':item.get('native_bounds_ft'),
    'actual_category_aabb_plan_ft':[w,d],
    'long_axis':'Z' if d>w else 'X',
    'long_axis_ft':max(w,d),
    'native_plumbing_id':sink.get('id') if sink else None,
    'native_plumbing_receipt_id':sink.get('receipt_id') if sink else None,
    'illustrative_front':('DRAWING_ASSOCIATED_TRANSPARENT_NON_NATIVECABINET'
      if item['min_height_ft']>.60 and
        ('vanity' in fixtureKinds or 'lavatory' in fixtureKinds) else 'NONE'),
    'basin_visual_gate':basin,
    'not_real_countertop_profile_or_joinery':True
   })
  tub=arch.get('selected_tub_proxy')
  if arch.get('selected_tub_unlocated_reason'):
   tubVisual='SELECTED_DURAVIT_700332000000090__2D_UNLOCATED'
  elif tub:
   tubVisual='SELECTED_NOMINAL_59x29.5_DURAVIT__HOLLOW_GENERIC_SHELL'
  elif program.get('kind')=='TUB_OR_WALK_IN_UNSELECTED':
   tubVisual='TUB_PICTOGRAM__2D_UNSELECTED_PROGRAM_ONLY'
  else:
   tubVisual='NONE__NO_TUB_FABRICATED'
  inst['r058_visualization']={
   'scope':'VIEWER_ONLY__NOT_A_CHANGE_TO_SOURCE_OR_OWNER_SELECTION',
   'source_plan':'Nov 7 2026 A2.1/A2.2',
   'native_room_boundary_certified':False,'native_family_mesh_extracted':False,
   'native_casework_bound_studies':counters,
   'tub_visual_classification':tubVisual,
   'selected_Duravit_nominal_size_ft':[4.916667,2.458333] if (tub or arch.get('selected_tub_unlocated_reason')) else None,
   'default_interior_reveal':{'presentation_only':True,
     'view_facing_lower_wall_height_ft':2.35,'upper_wall_ghost_is_NOT_glazing':True},
   'source_fitted_fixture_camera':('NATIVE_CASEWORK_AABB_CENTER'
      if counters and not tub else 'DRAWING_CALIBRATED_SELECTED_NOMINAL_TUB'
      if tub else 'ILLUSTRATIVE_TOILET_OR_ROOM_CENTER'),
   'frozen_program_kind':program.get('kind'),
   'all_owner_picks_and_quantities_unchanged':True
  }

# R059: explicit presentation-only provenance per all 26 physical instances.
# This does not move, select or modify any source-native element or decision.
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture') or {}
  c=arch.get('native_ceiling_evidence')
  adj=arch.get('adjacent_zone_geometry') or {}
  c310=adj.get('native_ceiling_evidence')
  sourceIds=[x['id'] for x in arch.get('native_casework_proxies',[])]
  nativeSinkIds=[x.get('closest_native_plumbing_insertion',{}).get('id')
   for x in arch.get('native_casework_proxies',[])
   if x.get('closest_native_plumbing_insertion')]
  roomPlan=(room.get('full_room_plan') or {}).get('fixture_symbol_diagram') or {}
  symbols=[x.get('kind') for x in roomPlan.get('items',[])]
  inst['r059_visualization']={
   'round':'VIEWER_ONLY_R059',
   'source_plan':'25-006 1527 N Wieland fp.pdf, Nov-07 2026 A2.1/A2.2',
   'original_native_wall_ids':arch.get('native_wall_ids',[]),
   'native_boundary_certified':False,'native_family_solids_extracted':False,
   'real_native_ceiling_aabb_id':c.get('id') if c else None,
   'real_native_ceiling_aabb_receipt_id':c.get('receipt_id') if c else None,
   'actual_gwb_underside_ft':c.get('underside_height_ft') if c else None,
   'ceiling_canopy_preview':'OFF_BY_DEFAULT__DRAWING_INFERRED_XY' if c else 'NO_GWB_CANOPY_NO_MATCH',
   'nominal_gwb_profile_certified':False,
   'native_countertop_aabb_ids':sourceIds,
   'native_plumbing_attributed_sink_ids':nativeSinkIds,
   'illustrative_vanity_face_vertical':'STRICTLY_WITHIN_NATIVE_COUNTERTOP_CATEGORY_AABB' if
    sourceIds and any(x in symbols for x in ['vanity','lavatory']) else 'NOT_DRAWN',
   'wc_silhouette':'GENERIC_PORCELAIN_INSIDE_PRE_EXISTING_CONTAINMENT_GATE' if
    arch.get('toilet_proxy_anchor') else 'NO_NATIVE_ROOM_WC_ANCHOR',
   'wc_family_mesh_certified':False,
   'wet_review_full_height':'VISUAL_ONLY_NO_PURCHASE_CHANGE' if
    room['id'] in ('PH-BATH2','PH-BATH4') else 'NO_EXTRA_VISUAL_DUPLICATE',
   'ph4_310_compartment':('310'+inst['room_number'][-1]) if adj else None,
   'ph4_310_classification':('WIC4__NATIVE_NEARBY_PLUMBING_UNATTRIBUTED__NO_3D_FIXTURE' if
    room['id']=='PH-BATH4' and inst['room_number'].endswith('A') else
    'BATH4__ILLUSTRATIVE_PLUMBING__SEPARATE_FROM_311' if
    room['id']=='PH-BATH4' else None),
   'ph4_310_native_wall_ids':adj.get('native_wall_ids',[]),
   'ph4_310_native_ceiling_id':c310.get('id') if c310 else None,
   'ph4_310_native_ceiling_receipt':c310.get('receipt_id') if c310 else None,
   'exterior_wet_review_camera':'DRAWING_HAND_ORIENTATION__NOT_DOORWAY',
   'owner_approved':False,'materials_quantity_cost_program_unchanged':True
  }

# R060: scene provenance is analytical and viewer-only. Actual source
# positions and immutable material/plumbing/approval program remain as read.
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture') or {}
  program=room.get('program') or {}
  counters=arch.get('native_casework_proxies') or []
  held=room['id']=='TX-POWDER' or 'basin UNSELECTED' in program.get('plumbing_truth','') or 'sink UNSELECTED' in program.get('plumbing_truth','')
  toilet=arch.get('toilet_proxy_anchor') or {}
  inst['r060_visualization']={
   'round':'VIEWER_ONLY_R060',
   'physical_instance':inst['room_number'],
   'focus_type':room['id'] in ('PH-POWDER','PH-WC','TX-POWDER2','TX-WC'),
   'cross_room_basin_fix':room['id']=='TX-POWDER',
   'native_wall_ids':arch.get('native_wall_ids',[]),
   'inferred_wall_face_area_ft2':arch.get('floor_polygon_area_ft2'),
   'native_ost_rooms_certified':False,
   'native_family_mesh_extracted':False,
   'dry_wood_visual_study':bool(program.get('dry_floor_retained')),
   'wood_material_source':'UNSELECTED_NEUTRAL_PROCEDURAL_VISUAL_ONLY' if program.get('dry_floor_retained') else None,
   'source_countertop_aabb_ids':[c.get('id') for c in counters],
   'countertop_top_volumes_contained_in_native_aabb_xyz':bool(counters),
   'native_plumbing_vicinity_ids':[c.get('closest_native_plumbing_insertion',{}).get('id')
      for c in counters if c.get('closest_native_plumbing_insertion')],
   'basin_selection_gate':'NO_PICK_OR_BASIN_UNSELECTED__NO_3D' if held else
      'R056_NATIVE_INSERTION_AND_FOOTPRINT_CONTAINMENT_GATES_RETAINED',
   'physical_sink_selection_inferred_from_native_plumbing':False,
   'source_wc_native_id':toilet.get('native_plumbing_id'),
   'wc_visual':'GENERIC_PORCELAIN__ORIGINAL_WALL_DOOR_COUNTER_GATES',
   'wc_native_family_solid':False,
   'wc_camera':'SOURCE_ANCHOR_PROXY_EXTERIOR__NOT_INTERIOR_STANDING_POSITION' if toilet else None,
   'countertop_camera':'SOURCE_AABB_EXTERIOR__NOT_CERTIFIED_INSTALLATION' if counters else None,
   'room_walls':'NATIVE_WALL_RUNS_WITH_REVERSIBLE_CAMERA_FACING_SECTION',
   'native_ceiling_id':(arch.get('native_ceiling_evidence') or {}).get('id'),
   'owner_approved':False,
   'selection_scores_prices_material_program_unchanged':True,
  }

# R061: per-instance architectural MATERIAL-VIEW evidence, not a room or
# manufacturer-model certification. The Three.js return host fit is checked
# against these original wall segments at rendering and in physical Chrome.
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture') or {}
  spec=(room.get('full_room_plan') or {}).get('fixture_symbol_diagram') or {}
  refs=[x for x in spec.get('items',[]) if x.get('kind') in
   ('tub','tub-reference','shower-reference')]
  inst['r061_visualization']={
   'round':'VIEWER_ONLY_R061',
   'physical_instance':inst['room_number'],
   'coordinated_focus':room['id'] in ('PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3'),
   'original_wall_ids':arch.get('native_wall_ids',[]),
   'original_wall_segment_count':len(arch.get('wall_segments',[])),
   'source_wall_face_area_ft2':arch.get('floor_polygon_area_ft2'),
   'native_ost_room_polygon_certified':False,
   'native_family_mesh_extracted':False,
   'wet_reference_pictogram_kinds':[x.get('kind') for x in refs],
   'wet_return_visual_source_gate':('ACTUAL_NATIVE_WALL_FACE_SEGMENT_RUNTIME_ASSERTION'
      if refs else 'NO_NAMED_WET_BATHING_PICTOGRAM'),
   'selected_wet_return_wall_finish':'NATIVE_WALL_SUPPORTED_ONLY__NO_PARTITION' if refs else None,
   'ph_bath2_front_w1_study':'LOW_0_72FT_NORMAL__FULL_HEIGHT_WET_CAMERA'
      if room['id']=='PH-BATH2' else None,
   'ph_bath2_return_view':'FULL_HEIGHT_NORMAL_WHEN_NATIVE_HOSTED'
      if room['id']=='PH-BATH2' else None,
   'conditional_tub_label':'SOURCE_TRACES_ONLY__NOT_PHYSICAL_STEP_OR_TUB'
      if room['program'].get('kind')=='TUB_OR_WALK_IN_UNSELECTED' else None,
   'source_floor_kind':'DRY_RETAINED_WOOD_NEUTRAL' if room['program'].get('dry_floor_retained')
      else 'FROZEN_LEVEL_OR_UNSELECTED_AS_PREVIOUS',
   'wall_finish_preview':'OPAQUE_APPEARING_PBR_SOURCE_DERIVED_WALL_WITH_REVERSIBLE_CUTAWAY',
   'grout_preview':'PROCEDURAL_UNSELECTED_HALF_JOINT_PER_TILE_1_16IN_TOTAL',
   'fixture_contact_shadow':'SELECTED_SOURCE_FITTED_NOMINAL_TUB_STUDIO_ONLY__WC_CAST_DISABLED_NO_NATIVE_HEIGHT_PROOF',
   'native_ceiling_id':(arch.get('native_ceiling_evidence') or {}).get('id'),
   'source_opening_ids':[x.get('id') for x in arch.get('openings',[])],
   'source_tub_fit':('DRAWING_CALIBRATED_GENERIC_NOMINAL' if arch.get('selected_tub_proxy')
      else 'SELECTED_UNLOCATED_2D' if arch.get('selected_tub_unlocated_reason')
      else 'CONDITIONAL_2D_ONLY' if room['program'].get('kind')=='TUB_OR_WALK_IN_UNSELECTED'
      else 'NO_SELECTED_TUB_SOLID'),
   'owner_approved':False,'original_program_scores_skus_prices_quantities_unchanged':True,
  }

# R062: all 26 record their original read-only registrations and the
# LIVE visual source tests performed in browser. Do not turn a category AABB
# into a cabinet family or the drawing into an installed shower location.
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture') or {}
  program=room.get('program') or {}
  primary=program.get('kind')=='PRIMARY_WALK_IN_LINEAR'
  counters=arch.get('native_casework_proxies') or []
  openings=arch.get('openings') or []
  inst['r062_visualization']={
   'round':'VIEWER_ONLY_R062',
   'physical_instance':inst['room_number'],
   'primary_coordinated_focus':primary,
   'ph4_independent_adjoining_context':room['id']=='PH-BATH4',
   'tx4_selected_tub_2d_hold':room['id']=='TX-BATH4',
   'native_wall_ids':arch.get('native_wall_ids',[]),
   'inferred_room_wall_face_area_sf':arch.get('floor_polygon_area_ft2'),
   'native_opening_ids':[x.get('id') for x in openings],
   'native_opening_hosts':[x.get('host_id') for x in openings],
   'native_opening_classification':'NOMINAL_HOSTED_STATION_WITH_NATIVE_WALL_THICKNESS_NOT_A_JAMB_OR_ROUGH_OPENING',
   'source_host_reveal_visual_only':bool(openings),
   'native_casework_category_box_ids':[c.get('id') for c in counters],
   'native_casework_local_vertical_bounds_ft':[
    [c.get('min_height_ft'),c.get('max_height_ft')] for c in counters],
   'native_casework_lengths_ft':[max(c.get('width_x_ft',0),c.get('depth_z_ft',0)) for c in counters],
   'native_lavatory_insertions_attributable_to_primary':[
    c.get('closest_native_plumbing_insertion',{}).get('id')
    for c in counters if c.get('closest_native_plumbing_insertion')],
   'primary_3d_shower_spatial_status':'SOURCE_NATIVE_WALL_COUNTER_DOOR_RUNTIME_TEST; NO CERTIFIED INSTALLATION'
    if primary else 'NOT_PRIMARY_WALK_IN',
   'primary_shower_reference_3d_rendering':'UNLOCATED_2D_SOURCE_TRACES_ONLY'
    if primary else None,
   'selected_factory_solid_linear_drain_48in':primary,
   'primary_drain_center_or_slope_modelled':False,
   'primary_sink_count_or_3d_basin_fabricated':False,
   'primary_vanity_mass_study':'NATIVE_CATEGORY_AABB_CONTAINED_NEUTRAL_FACE_ENDS_AND_UNDERSIDE_ONLY'
     if primary and counters else None,
   'native_gwb_underside_id':(arch.get('native_ceiling_evidence') or {}).get('id'),
   'native_room_certified':False,
   'manufacturer_family_mesh_extracted':False,
   'owner_approved':False,
   'program_skus_costs_quantities_status_unchanged':True,
  }

# R063: whole-viewer geometric/material provenance bound to the existing
# read-only native wall/fixture receipts. Do NOT relabel drawing-registered
# room faces as certified OST_Rooms or a product source photo as a sample.
for room in data['rooms']:
 for inst in room['physical_instances']:
  arch=inst.get('architecture') or {}
  program=room.get('program') or {}
  focus=room['id'] in ('PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3')
  floor=next((p for p in room.get('products',[]) if
     ('level' in p.get('surface','').lower() or 'bath floor' in p.get('surface','').lower())),None)
  counters=arch.get('native_casework_proxies') or []
  tub=arch.get('selected_tub_proxy')
  inst['r063_visualization']={
   'round':'VIEWER_ONLY_R063',
   'physical_instance':inst['room_number'],
   'coordinated_focus':focus,
   'source_geometry_basis':'NATIVE_WALL_CENTERLINES_THICKNESS_WALL_FACES_PLUS_DRAWING_INFERRED_ROOM',
   'inferred_wall_face_area_ft2':arch.get('floor_polygon_area_ft2'),
   'native_wall_ids':arch.get('native_wall_ids',[]),
   'native_wall_receipt':arch.get('wall_receipt_id'),
   'native_hosted_opening_ids':[o.get('id') for o in arch.get('openings',[])],
   'selected_level_material':floor.get('name') if floor else None,
   'selected_level_nominal_size':floor.get('size') if floor else None,
   'floor_uv_system':'NATIVE_FACE_POLYGON_UNNORMALIZED_PLANAR_FEET__REPEAT_INVERSE_NOMINAL_TILE_FEET'
      if floor and not program.get('dry_floor_retained') else 'UNSELECTED_NEUTRAL_OR_RETAINED_FLOOR',
   'floor_uv_origin_source_native':'NATIVE_WALL_FACE_DERIVED_ROOM_LOCAL_FT',
   'tile_layout_or_grout_owner_approved':False,
   'native_wall_base_view_lighting':'NATIVE_WALL_BOX_ONLY_SHADOW_GRADIENT_NO_BASEBOARD',
   'native_countertop_aabb_ids':[c['id'] for c in counters],
   'compact_counter_study_source_gate':(
      'WITHIN_NATIVE_COUNTERTOP_CATEGORY_AABB_NO_FLOOR_PEDESTAL_OR_CABINET_SOLID'
      if focus and counters and all(c.get('min_height_ft',-1)>.60 for c in counters)
      else 'WITHHELD_AABB_EXTENDS_BELOW_LEVEL_NOT_CERTIFIED_CABINET' if focus and counters
      else None),
   'compact_counter_original_vertical_local_ft':[
       [c.get('min_height_ft'),c.get('max_height_ft')] for c in counters] if focus else [],
   'wet_finish_corner_light_source_gate':'NATIVE_WALL_FACE_MATCHED_RETURNS_ONLY'
       if focus else 'PREEXISTING_R061_WET_RETURN_GATE',
   'source_tub_nominal_model':tub.get('model_or_sku') if tub else None,
   'source_tub_nominal_footprint_ft':[
       tub.get('nominal_width_ft'),tub.get('nominal_depth_ft')] if tub else None,
   'tub_study_fidelity':'GENERIC_ROUNDED_VESSEL_WITH_REFLECTIVE_RIM_NOT_MANUFACTURER_SOLID'
      if focus and tub else 'NO_NEW_BATHTUB_FAMILY_OR_BRANCH',
   'conditional_tub_or_walk_in_3d_unlocated':program.get('kind')=='TUB_OR_WALK_IN_UNSELECTED',
   'installed_niche_or_glass_or_faucet_location_fabricated':False,
   'source_tub_rotation_revised':False,
   'source_drain_or_roughin_revised':False,
   'wall_face_natively_certified_room_polygon':False,
   'native_family_mesh_extracted':False,
   'selected_material_program_changed':False,
   'owner_approved':False,
  }

data['phase']='v4_native_wall_face_architecture_r043'
data['architecture_summary']={'registered_instances':len(stats),'native_receipts':{'walls':WALL_RECEIPT,'doors':DOOR_RECEIPT,'windows':WIN_RECEIPT},
 'registration':'drawing-inferred per instance, NOT native Revit room boundary',
 'native_wall_network_closed_instances':sum(1 for r in data['rooms'] for i in r['physical_instances'] if i.get('room_geometry_fidelity','').startswith('REGISTERED_NATIVE')),
 'native_wall_faces_with_calibrated_corner_closure':sum(1 for r in data['rooms'] for i in r['physical_instances'] if i.get('room_geometry_fidelity','').startswith('NATIVE_WALL_FACES_WITH')),
 'toilet_native_insertion_anchors':sum(1 for r in data['rooms'] for i in r['physical_instances'] if i.get('architecture',{}).get('toilet_proxy_anchor')),
 'native_hosted_window_family_AABB_witnesses':sum(
  1 for r in data['rooms'] for i in r['physical_instances']
  for zone in (i.get('architecture',{}),i.get('architecture',{}).get('adjacent_zone_geometry') or {})
  for opening in zone.get('openings',[]) if opening.get('kind')=='window' and opening.get('native_window_family_aabb')),
 'native_hosted_door_family_AABB_witnesses':sum(
  1 for r in data['rooms'] for i in r['physical_instances']
  for zone in (i.get('architecture',{}),i.get('architecture',{}).get('adjacent_zone_geometry') or {})
  for opening in zone.get('openings',[]) if opening.get('kind')=='door' and opening.get('native_door_family_aabb')),
 'selected_Duravit_tub_source_fitted_instances':sum(1 for r in data['rooms'] for i in r['physical_instances'] if i.get('architecture',{}).get('selected_tub_proxy')),
 'native_casework_proxy_records':sum(len(i.get('architecture',{}).get('native_casework_proxies',[])) for r in data['rooms'] for i in r['physical_instances'])}
data['architecture_summary']['selected_Duravit_tub_unlocated_due_source_collision']=sum(
 1 for r in data['rooms'] for i in r['physical_instances'] if i.get('architecture',{}).get('selected_tub_unlocated_reason'))
DEST.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
acc=ROOT/'deliverables/viewer3d/ACCURACY.md'
with acc.open('a',encoding='utf-8') as f:
 f.write('\n## R043 read-only native wall-face architectural registration\n')
 f.write('- November 7 latest A2.1/A2.2: unit A is east, B west (correcting R042 global context wing; local wet handedness preserved). Native wall curve receipt '+WALL_RECEIPT+'; hosted door receipt '+DOOR_RECEIPT+'; windows '+WIN_RECEIPT+'. All element coordinates are actual read-only Revit feet; attributed ROOM NAME remains drawing-inferred.\n')
 f.write('- Source inner faces are derived from original wall location lines and exact native AABB THICKNESSES. Polygon topology repairs sub-0.003-ft gaps and is NOT a certified Room boundary. Wall heights use model bounds; type names are source-native. Hosted doors represent nominal leaf widths and insertion coordinates, NOT approved rough openings, swing handing or fabrication.\n')
 f.write('- Registered rooms: native-derived polygons where closed; 305A/B use explicitly labeled four native wall faces with Nov-07 drawing-calibrated corner closures. No instance is a certified native Revit Room spatial object:\n')
 for rid,n,area,segments,openings in stats:
  f.write(f'  - {rid} {n}: {area:.2f} SF face-derived; {segments} source wall-face segments; {openings} hosted opening(s); named-room attribution DRAWING-INFERRED.\n')
 f.write('- PH4 311A/B nominal source faces approximately 26.98 SF each, separate 310A/B faces 35.10 SF; original 27.08 drawing vs owner 35 SF remains unresolved. 40.2 SF single gross LEVEL/POINT PAN material pool NOT remeasured, duplicated or amended. Northern 310 windows are not transferred into southern 311.\n')
 f.write('- PH-BATH2 305A/B: R047 resolves historic drawing-only fallback into 35.10 SF native WALL-FACE + DRAWING CALIBRATED enclosure: source wall IDs A 12590818/16428596/16428780/10808894, B 12380128/12590818/15959004/10808894, hosted nominal 28x96 doors 16428635/12591854, with endpoint gaps expressly unverified. No native Room ID or certified floor polygon and NO extra Duravit PAN.\n')
 f.write('- Latest Nov-07 A2.2 high-resolution plan inspection corrects previous generated 305A/B tub marker NORTH to SOUTH/lobby-side and lavatory NORTH/elevator-side, with actual native sink countertop/wall-hung WC corroboration. Both frozen Duravit 59x29.5 tubs now have 3D NONCOLLIDING nominal drawing-calibrated positions (each ~0.034ft from corrected source symbol), with hosted doors at north/elevator-side. This correction changes viewer schematic only, not frozen plumbing/tile, and is NOT a Revit-native tub family location.\n')
 f.write('- Latest Nov-07 A2.1 lower-level plan inspection corrects former 007A/B fixture handedness: A east-side tub compartment/right, west-side sink/left; B mirrors. Native countertop, toilet insertion and ACTUAL native toilet FAMILY BOUNDING BOX evidence reinforce sink/WC zone. R051 tighter source gate supersedes the former 007B 1.2212ft shifted generic 3D study: that 007B tub overlapped source toilet AABB 16297835 by about 0.47 SF. 007A overlaps its own protected geometry. BOTH frozen selected Duravit TUBS now render 2D UNLOCATED until physical source-compatible geometry is found; no SKU deletion, no replacement WALK-IN or extra tiled PAN. AABB is a conservative extent not a family mesh or construction clearance.\n')
 f.write('- PH4 adjacent 310 native plumbing/countertop proxies: toilet 16428804/16377760, lavatory reference 16428825/16428332 and countertop 16438318/16438253. Source-native insertion/bounds, drawing-inferred 310 membership; these fixtures remain OUTSIDE 311 original purchased area.\n')
 f.write('- R051 reviewer96 FIX corrected PH4 310 native countertop omission: casework 16438318 (310A), 16438253 (310B) reported source location.point=[0,0,0] placeholder, not true physical position. Use ACTUAL READ-ONLY Revit countertop AABB bounds-center for 310 relationship (not a native insertion), with coordinate_reference_kind NATIVE_BOUNDS_CENTER and raw native insertion NULL; the original AABB supplies its source-dimensioned neutral proxy. Plumbing insertions remain independently sourced; 311 source material and original 40.2 SF pool unchanged.\n')
 f.write('- R050 ceiling review: adjoining 310 ceiling line is NEVER attributed to 311 native GWB. Each 310 zone has a separate conservative GWB footprint search (at least 88% covered, at most 1.75x area); unmatched 310 retains a clearly marked DRAWING 9.25ft non-solid datum with NO native ceiling receipt. This is not a native ceiling profile. Full Bathroom PH4 front W3 lowers to 2.8ft solely to expose 311 pan/310 adjacency; Wet Zone Study and frozen material heights remain full.\n')
 for ph4 in (r for r in data['rooms'] if r['id']=='PH-BATH4'):
  for inst in ph4['physical_instances']:
   adj=inst['architecture'].get('adjacent_zone_geometry') or {}
   c=adj.get('native_ceiling_evidence')
   label=adj.get('number', '310?')
   f.write('- '+label+' ceiling datum independently sourced: '+
    (('native GWB id '+str(c['id'])+' receipt '+str(c['receipt_id'])+' underside '+str(c['underside_height_ft'])+'ft; footprint overlap is evidence, named-room membership still drawing-inferred') if c else
     'DRAWING 9.25ft only; native GWB for this separate 310 compartment NOT MATCHED')+'; no inherited 311 receipt.\n')
 f.write('- Material drawing-vs-wall-face conflicts remain unclosed: PH-PRIMARY wall-face 122.06 SF vs drawing display 103.09 (+18.4%); TX-PRIMARY 104.46 vs 87.02 (+20.0%); TX-BATH4 native 32.26/35.83 vs drawing 38.89 SF. Display source differences as registration uncertainty, not corrections to owner source, quantities or historical prices.\n')
 f.write('- Hosted door insertions identify nominal 28in x 96in elements in the 311 inner partitions; exact swing/hinges, rough opening, actual shower drain location and glass/niche remain UNVERIFIED. Selected wet program and all frozen selections are untouched.\n')
 f.write('- R053 source-hosted opening DEPTH wire is a thin line connecting the host wall faces at native bounded thickness and hosted insertion with separately recorded NOMINAL family dimensions. Reviewer96 R053 FIX corrected VISUALLY_CLIPPED witnesses: actual rendered width/height, geometry-vertex-measured extents, visual-height-cutaway flag and inferred-room-face clipping flag are distinct from full nominal width/height. A source wall face may terminate before nominal family width (TX4 007A); missing type span is UNRESOLVED, never extended to fabricate an opening. Likewise shortened front/310 context walls may limit visible head height, not the nominal family height. These are not actual Revit opening profiles, verified rough openings, door leaf/jamb/frame/glazing assemblies, hinges, swings or construction clearances. Native host IDs, receipts and dimensions remain inspectable; material/purchase quantities unchanged.\n')
 f.write('- R054 after independent Reviewer96 R053 CONTINUE: six individually source-hosted native WINDOW element AABBs (two TX-PRIMARY, two TX-BATH3, and independently two PH4 adjoining 310A/B windows, ZERO transferred into 311 wet-room scope) are transformed exactly from native XYZ bounds into room-local drawing-registered coordinates and shown as separate sparse dashed 3D witnesses. Actual native AABB is NOT the nominal type size and NOT the window glazing/frame solid; symbolic family extents may exceed nominal glass. Host IDs, opening insertion/nominal dimension and real source AABB remain independent; no invented frame, rough opening, jamb, glazing mullion, hand, clearance, quantification or room membership. Browser physically checks source equality and owner-visible 310A/B compartment labels.\n')
 f.write('- R055 source-native hosted DOOR element AABBs are registered for all 30 door appearances (including 311/310 separate connections) with original read-only Revit category XYZ bounds, host ID, source receipt and precisely transformed local feet. These are NOT native door leaf solids; a family AABB can include symbolic swing geometry and may exceed nominal type width. It is NOT a verified clear rough opening, installed door arc, hinge or fabrication clearance. User can toggle source-bounds witness wires without changing genuine wall solids, separate generic leaf depiction, frozen selections or the evidence matrix. 310/311 attributions remain explicitly drawing-inferred.\n')
 f.write('- WC toilet proxies 314A/B and 203A/B have read-only plumbing insertion IDs 16428736/15957324/16437697/18055997; other bathroom toilets use nearby native 270AA.101 insertions when drawing registration supports it. An INFERRED 1.05–1.7ft interior visualization offset is selected by generic 1.4×2.05ft footprint containment plus nominal hosted-entry gate, not a native toilet center or plumbing rough-in. Native plumbing receipt '+PLUMB_RECEIPT+'. Infeasible pictograms remain 2D UNLOCATED markers.\n')
 f.write('- Additional 270AA.101 toilet insertion candidates and contained Countertop AABB records are reconciled individually against inferred room floor face, retained with element and source receipt IDs, and displayed only as deliberately generic offset/neutral source-bounded proxies. Some room-symbol positions are suppressed rather than inventing geometry. 310A/B native toilet/countertop evidence stays separately contextual.\n')
 f.write('- Native GWB ceiling AABB underside data are accepted only when the footprint covers at least 88% of a named room and is no more than 1.75x its floor area; source receipt '+ceiling_receipt+'. The outline remains drawing-registered, no slab/profile mesh is claimed, and 9.25ft legacy drawn datum is retained as a separate conflicting source where different.\n')
 f.write('- R051 architectural fidelity: the viewer now distinguishes a DOTTED original native GWB AABB XY witness rectangle (read-only category bounds, source elevation/ID/receipt) from the room-shaped ceiling datum derived from inferred native wall faces. No fabricated ceiling slab or soffit profile; unmatched rooms show drawing 9.25ft datum ONLY. Actual 270AA native toilet insertion points render as cyan floor witnesses joined by dashed lines to their generically offset toilet proxies (including the separate 310A/B context); the line shows illustrative displacement, NOT a relocated rough-in, code clearance or physical pipe.\n')
 f.write('- R052 after reviewer96 CONTINUE: 20/26 actual attributable native toilet insertion records now also retain the original READ-ONLY Revit 270AA toilet family bounding MIN/MAX in native XYZ and transformed local model feet; rendered as sparse cyan dashed 3D bounding-edge witness. Includes separate native 310A/B toilet element AABBs, independent of 311 shower. Source AABB is NOT a physical mesh, clearances, rough-in or proof of room membership; may contain voids and cross wall faces. Generic porcelain proxy and insertion offset remain DISTINCT and inspectable. This prevents interpreting the previously overlapping 007A/B tub (both SELECTED / 2D UNLOCATED) as source-verified 3D.\n')
 f.write('- Additional source-plumbing insertion-to-countertop spatial reconciliations only when source family point is <=0.8ft from matching native Countertop AABB center and elevation within 1.30ft of countertop top. A rendered generic basin may use this XY locator, but the family name does NOT prove an actual basin, faucet, cutout or rough-in. Rooms with owner basin UNSELECTED do not acquire a selected basin by visualization.\n')
 f.write('- Frozen selected PH-BATH2 / TX-BATH2 / TX-BATH4 TUB program uses Duravit Starck 59×29.5in model 700332000000090 (source rows per plumbing.json). A generic 3D vessel is shown ONLY when its nominal footprint fits source wall-face room bounds AND does not overlap native countertop AABBs, the actual associated Revit toilet family AABB, the separately source-anchored illustrative WC envelope or hosted doors within 1.65ft of the drawing symbol. A conflicting room renders a 2D UNLOCATED marker instead: NOT cancelled or unselected, merely no defensible precise position. Exact family solids and real installation clearances are NOT certified. NO tiled PAN, drain coordinate, fabricator clearance or purchasing calculation.\n')
 for room in data['rooms']:
  if room['id']!='TX-BATH4':continue
  for inst in room['physical_instances']:
   a=inst.get('architecture',{});t=a.get('selected_tub_fit_audit',{})
   f.write('- R051 '+inst['room_number']+' 59x29.5in selected tub visual fit audit INCLUDING ACTUAL NATIVE TOILET FAMILY AABB: '+str(t.get('evaluated'))+' sampled candidate centers; '+str(t.get('outside_wall_face'))+' outside native wall faces, '+str(t.get('native_counter_or_wc_intersection'))+' intersect source countertop/native toilet bounds or illustrative WC proxy, '+str(t.get('native_hosted_door_gate'))+' rejected by nominal hosted-door gate; '+str(t.get('source_compatible_candidate_count'))+' source-compatible. '+('Selected tub kept 2D UNLOCATED.' if a.get('selected_tub_unlocated_reason') else 'Closest defensible 3D proxy '+str(t.get('best_candidate_displacement_ft'))+'ft from pictogram, DRAWING-CALIBRATED, NOT native insertion.')+' Candidate grid is a visual overlap filter, not continuous/exhaustive proof or approved clearance.\n')
 f.write('- Full Bathroom tiles: 2026-11-07 reviewer96 PBR FIX repaired by packaging the exact existing viewer product JPG asset as an inline DATA URI in single offline HTML (original picks.json paths unchanged), then source-image color/variation + illustrative grout normal/roughness encoded as scene-owned RGBA DataTextures. This avoids file:// canvas cross-origin taint and near-black stale CanvasTexture GPU maps on rapid navigation. Maker JPG installation/lighting/photo is visual reference, NOT an exact color or grout submittal.\n')
 f.write('\n### Instance-specific R047 wall, opening, plumbing and casework evidence matrix\n')
 f.write('| Physical room | Registration confidence | Wall-face SF (NOT purchase) | Native wall IDs | Native hosted opening IDs | Native DOOR element AABB IDs | Native window AABB IDs (310 separate) | Native toilet insertion/illustrative offset | Native casework IDs | Native plumbing near counter | R056 generic basin footprint gate | Selected tub SKU / calibrated delta (ft) | GWB ceiling underside ID / ft | Explicit unresolved dependency |\n')
 f.write('|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|\n')
 for r in data['rooms']:
  for i in r['physical_instances']:
   a=i.get('architecture')
   if not a:continue
   reg=('WALL FACES + DRAWING-CALIBRATED corner closure' if i['room_geometry_fidelity'].startswith('NATIVE_WALL_FACES_WITH') else 'NATIVE WALL-LINE POLYGON, DRAWING-INFERRED room ID')
   opening=', '.join(str(x['id'])+' ('+x['kind']+')' for x in a['openings']) or 'no hosted opening'
   doors=', '.join(str(x['id'])+' ('+i['room_number']+')' for x in a.get('openings',[]) if x.get('native_door_family_aabb'))
   doors+=(', ' if doors else '')+', '.join(str(x['id'])+' ('+(a.get('adjacent_zone_geometry') or {}).get('number','310?')+')' for x in (a.get('adjacent_zone_geometry') or {}).get('openings',[]) if x.get('native_door_family_aabb'))
   doors=doors or 'none'
   windows=', '.join(str(x['id'])+' ('+i['room_number']+')' for x in a.get('openings',[]) if x.get('native_window_family_aabb'))
   windows+=(', ' if windows else '')+', '.join(str(x['id'])+' (310'+i['room_number'][-1]+')' for x in (a.get('adjacent_zone_geometry') or {}).get('openings',[]) if x.get('native_window_family_aabb'))
   windows=windows or 'none'
   casework=', '.join(str(x['id']) for x in a.get('native_casework_proxies',[])) or 'none'
   counter_insertions=', '.join(str(x['closest_native_plumbing_insertion']['id']) for x in a.get('native_casework_proxies',[]) if x.get('closest_native_plumbing_insertion')) or 'unverified'
   basin_gates=[]
   for counter in a.get('native_casework_proxies',[]):
    sink=counter.get('closest_native_plumbing_insertion')
    if not sink:continue
    w,d=counter['width_x_ft'],counter['depth_z_ft']
    center=counter['local_center_xz_ft'];point=sink['location_local_xz_ft']
    inside=(abs(center[0]-point[0])+min(.52,w*.31)<=w/2+.00001 and
            abs(center[1]-point[1])+min(.38,d*.30)<=d/2+.00001)
    basin_gates.append(str(counter['id'])+': '+('ILLUSTRATIVE FIT' if inside else '3D UNLOCATED / native-point locator'))
   basin_gate=', '.join(basin_gates) or 'native basin point unverified'
   ta=a.get('toilet_proxy_anchor')
   toilet=(str(ta['native_plumbing_id'])+' / '+str(ta['offset_from_native_insertion_ft'])+' ft ILLUSTRATIVE' if ta else 'unverified')
   tub=a.get('selected_tub_proxy')
   tubtext=(str(tub['model_or_sku'])+' / '+str(tub['calibrated_symbol_displacement_ft'])+' ft DRAWING-CALIBRATED' if tub else
    ('SELECTED Duravit 700332000000090 / 3D UNLOCATED due native toilet AABB/counter/wall/door gates' if a.get('selected_tub_unlocated_reason') else 'not selected'))
   ceil=a.get('native_ceiling_evidence')
   ceiling=(str(ceil['id'])+' / '+str(ceil['underside_height_ft']) if ceil else 'DRAWING 9.25 only; native room ceiling not matched')
   unresolved=('wall gap closure/door swing/family solids' if i['room_geometry_fidelity'].startswith('NATIVE_WALL_FACES_WITH') else
     'room membership/door swing/family solids'+('/area delta '+str(a['drawing_vs_wall_face_difference_percent'])+'%' if a['area_conflict_flag'] else ''))
   f.write('| '+i['room_number']+' | '+reg+' | '+str(a['floor_polygon_area_ft2'])+' | '+
    ', '.join(map(str,a['native_wall_ids']))+' | '+opening+' | '+doors+' | '+windows+' | '+toilet+' | '+casework+' | '+counter_insertions+' | '+basin_gate+' | '+tubtext+' | '+ceiling+' | '+unresolved+' |\n')
 f.write('\nR056 source countertop/basin rule: a generic basin envelope is shown atop a source category AABB only if its entire illustrative footprint fits the bounded counter at the nearest native plumbing insertion. If it exceeds those bounds, retain a visually raised PLAN-XY locator (NOT a true Revit 3D insertion witness) and label the native plumbing XYZ, source relative Y, rendered Y and exact visual Y offset. PH-POWDER 405A/B plan-XY rings are raised about 0.50615 ft above native insertion for visibility only. 3D basin remains UNLOCATED. This is NOT a cutout, true basin family solid, installation clearance, rough-in location or counter fabrication geometry.\n')
 f.write('\n## R057 integrated architectural cutaway, interior visibility and A/B registration\n')
 f.write('- The default Full Bathroom scene is a **reversible VISUAL section**, not a modified Revit wall. Camera-facing parts of the source-derived wall geometry display only up to 2.35 ft above the visual floor while their source-derived wall locations/thicknesses, original height and native host IDs are preserved. A facing tall W1 wet tile preview may be hidden for visibility; its full nominal specification and tile quantities stay unchanged. Use the Interior reveal OFF control to restore the original presentation wall geometry (including its inherited earlier 305/311 fixed cutaways). Wet Zone Study remains unchanged. The source-traces switch defaults OFF for legibility but can restore all analytical witnesses.\n')
 f.write('- Camera azimuth is mirrored for 12 drawing-mirrored A/B pairs; PH4 uses its independent 311 entrance side. The new A/B viewer comparison draws the ACTUAL registered A/B source-wall-derived planar polygons, Revit hosted opening insertion points, native countertop CATEGORY bounds, and native toilet insertion when attributable. Secondary PH4 310A/B faces are drawn as explicitly separate dashed compartments. Source geometry is not certified OST_Rooms or exact family solids; the viewer does not manufacture missing openings or fixture placements.\n')
 f.write('| Instance | Original native wall IDs | Drawing-inferred source wall-face SF (not purchase) | Default exterior review azimuth | Separate native adjacent zone | Material/geometry holds unchanged |\n')
 f.write('|---|---|---:|---|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   a=inst.get('architecture',{})
   hand=('LEFT' if inst.get('plan_entry_side')=='left' else 'RIGHT') if r['id']=='PH-BATH4' else ('LEFT' if inst.get('plan_is_mirrored_B') else 'RIGHT')
   f.write('| '+inst['room_number']+' | '+', '.join(str(x) for x in a.get('native_wall_ids',[]))+' | '+
    str(a.get('floor_polygon_area_ft2','unknown'))+' | '+hand+' (EXTERIOR visual, not standing position) | '+
    ('310'+inst['room_number'][-1]+' separately documented' if a.get('adjacent_zone_geometry') else 'No')+' | '+
    ('Selected tub remains 2D UNLOCATED' if a.get('selected_tub_unlocated_reason') else
     'Source-bounded basin 3D UNLOCATED' if r['id']=='PH-POWDER' else
     'Unselected program/geometry preserved' if not r.get('has_pick') else 'Frozen selections retained')+' |\n')
 f.write('\n## R058 coordinated full-bath interior interpretation: 26 physical source records\n')
 f.write('- TX-PRIMARY 202A/B selected WALK-IN with 48-inch factory-solid LINEAR and NO new niche or approved overhead tile; although the Nov 7 A2.1 plan includes a tub-shaped symbol, DO NOT convert the frozen program to a tub. Its 9.5625-ft LONG source-native Countertop CATEGORY AABB has NO matching native lavatory insertion: no centered 3D sink or fabricated double-sink count. A neutral lower vanity fascia is drawn only where the drawing records vanity scope; exact source countertop AABB and receipt remain independently traceable.\n')
 f.write('- TX-BATH2 205A/B selected Duravit 700332000000090: use precisely the 59 × 29.5-inch nominal footprint ONLY at pre-R058 native-source-bounded, drawing-calibrated centers, with a hollow rounded GENERIC shell. No bathtub-family solid, verified installed vertical height, drain, spout, faucet rough-in, flange, or PAN is asserted. TX-BATH3 207A/B frozen TUB/WALK-IN UNSELECTED: conditional tub pictogram is ONLY a translucent 2D outline, not installed or selected; optional PAN remains NULL. TX-BATH4 007A/B frozen SELECTED Duravit but 3D UNLOCATED from source-toilet-wall/counter/door guards.\n')
 f.write('- The R058 reversible visual section adds extremely faint non-material UPPER REMNANTS aligned with retained source walls above the 2.35-ft camera-facing cutaway. They are NOT physical translucent walls, glass, certification of OST_Rooms, or demolition. The Source traces ON/OFF switch remains independent; only analytical wires reveal native AABBs. Full Bathroom, Wet Zone Study, Revit Context, A/B source plan comparison and all frozen materials/areas are unchanged. Exterior Fixture focus camera uses only selected nominal source-fitted tub center OR native category countertop AABB center, never a derived standing point or TX4 bathtub.\n')
 f.write('| Physical instance | Native countertop AABB / receipt / long-axis | Native plumbing attribution / 3D basin visual gate | Frozen tub program / R058 visual classification | Native wall-face/camera interpretation |\n')
 f.write('|---|---|---|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   e=inst['r058_visualization']
   cs=e['native_casework_bound_studies']
   counter=('; '.join(str(c['native_casework_id'])+' / '+str(c['native_receipt_id'])+
    ' / '+c['long_axis']+' '+str(round(c['long_axis_ft'],3))+'ft '+c['illustrative_front'] for c in cs)
    or 'No attributable source counter')
   basins=('; '.join(str(c['native_plumbing_id'] or 'NO NATIVE BASIN POINT')+
    ' / '+c['basin_visual_gate'] for c in cs) or 'NO SOURCE BASIN CLAIM')
   place=e['tub_visual_classification']
   a=inst.get('architecture') or {}
   wall=('native IDs '+','.join(map(str,a.get('native_wall_ids',[])))+
    '; source-derived wall-face '+str(a.get('floor_polygon_area_ft2'))+' SF; '+
    e['source_fitted_fixture_camera']+' exterior, no native room boundary')
   f.write('| '+inst['room_number']+' | '+counter+' | '+basins+' | '+place+' | '+wall+' |\n')
 f.write('\nR058 provenance and frozen decisions: native source document owner confirms same 1527/1529 building but no fresh 3D family-solid read or native Room IDs; read-only receipt IDs remain in picks.json. A visual AABB is not a fabricated furniture profile; a translucent vanity face is not selected cabinetry. PH4 311/310 compartments, GWB identities, area 26.9792 vs drawing 27.08 vs frozen owner 35 SF, original combined 40.2 SF LEVEL/POINT pool, 5 no-pick, 0 approvals and all selected/historical costs unchanged.\n')
 f.write('\n## R059 PH coordinated architectural legibility and material presentation — 26 instance truth table\n')
 f.write('- The Nov-07 A2.2 3RD-floor drawing registers PH-PRIMARY 304A/B, PH-BATH2 305A/B, PH-BATH3 307A/B, and PH4 311A/B with adjoining 310A **WIC4** and 310B **BATH4**. The earlier 310A generic toilet and vanity were NOT certified closet contents: R059 suppresses their visual solids, while preserving nearby original native plumbing AABB and countertop AABB as optional independent source traces. 310B Bath4 still has a conservative porcelain WC pictogram/neutral countertop study, NOT native family solids. The 311 shower is never a 310 room; original combined 40.2 SF LEVEL/POINT PAN pool remains unchanged, PH4 26.9792/27.08/35 SF unresolved.\n')
 f.write('- PH-PRIMARY 304A/B has a 9.177ft-long native Countertop-category box but no attributable source lavatory insertion. NO basin count, sink centers or double lavatory fabricated. PH-BATH2 305A/B source-confirmed 59×29.5in selected Duravit nominal placement remains drawing-calibrated, now shown with R058 hollow generic vessel. In Full Bathroom normal view the front wet-wall overlay is sectioned for tub visibility; **Wet wall** exterior camera shows reversible **full-height** original selected tile W1/W2/W3 as presentation-only counterpart with NO second tile takeoff, material order, or revised construction wall. PH-BATH3 307A/B TUB/WALK-IN remains unselected, 2D only.\n')
 f.write('- Native GWB ceiling receipt '+ceiling_receipt+' provides real underside elevation where conservatively matched; R059 **Ceiling OFF/ON** shows at most one low-opacity non-solid canopy for each separately matched compartment. Its XZ edges are the DRAWING-INFERRED source wall-face polygon and NOT actual native ceiling trim, soffit, roof/slab solid, lighting or room certified boundary. 310A/310B independently matched GWB cannot be merged with 311. Default canopy OFF for interior visibility.\n')
 f.write('- R059 generic porcelain toilet bowl/rim replaces box/cistern silhouette only after existing native plumbing insertion/drawing pictogram footprint, casework collision, wall polygon and native hosted door guards pass. Approximate 1.4×2.05ft plan footprint and selected SOURCE GATES unchanged; no native family mesh, manufacturer height/identity, rough-in, tank, carrier, trap, drain or clearance is certified. Generic color fascia now remains strictly WITHIN actual native countertop CATEGORY AABB height: the former R058 floor-reaching fascia erroneously suggested unsupported floor-to-vanity cabinetry. No joinery, mounting hardware, true countertop shape or selected cabinetry finish.\n')
 f.write('- Lighting uses restrained studio-neutral directional/hemisphere/soft point contributions to reduce overexposure of matte versus glossy tile; existing pixel-sourced manufacturer blend, nominal-tile atlas, manufacturer-image caveat and PBR roughness/normal maps remain. New orientation-aware Wet wall, 311 shower, 310 context EXTERIOR review cameras do NOT suggest a measured physical standing or doorway location. Source traces, wall/edge visibility, R057 section and R058 focus remain independently reversible.\n')
 f.write('| Physical instance | Native matched GWB ID / underside ft | Native countertop AABB IDs (not cabinet profiles) | Illustrative basin/WC branch | Ceiling and PH4 adjoining 310 provenance |\n')
 f.write('|---|---|---|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   a=inst.get('architecture') or {}
   v=inst['r059_visualization']
   ceil=(str(v['real_native_ceiling_aabb_id'])+' / '+str(v['actual_gwb_underside_ft'])+
    ' ft' if v['real_native_ceiling_aabb_id'] else 'NO MATCH — DRAWING DATUM ONLY')
   cases=','.join(map(str,v['native_countertop_aabb_ids'])) or 'NONE'
   wc=v['wc_silhouette']+'; basin source IDs '+(
    ','.join(map(str,v['native_plumbing_attributed_sink_ids'])) or 'UNATTRIBUTED/UNSELECTED')
   adj=(str(v['ph4_310_compartment'])+': '+str(v['ph4_310_classification'])+
    ' / independently matched GWB '+str(v['ph4_310_native_ceiling_id'])
    if v['ph4_310_compartment'] else 'No adjoining 310 source claimed')
   f.write('| '+inst['room_number']+' | '+ceil+' | '+cases+' | '+wc+
    ' | '+v['ceiling_canopy_preview']+'; '+adj+' |\n')
 f.write('\nR059 every instance remains DRAWING-REGISTERED native wall-face geometry, NOT OST_Rooms or extracted Revit family solids. PH2 full-height finish duplicates are DISPLAY-ALTERNATES, not an additional physical wet-wall plane or purchase quantity; PH4 311/310 areas stay distinct. Five unpicked bathrooms, ZERO owner approvals, frozen linear/point drains, historical prices, plumbing products, technical holds and 43 protected originals remain unchanged.\n')
 f.write('\n## R060 viewer-only powder and WC architecture, selection-grounded material presentation — 26 physical instances\n')
 f.write('- Physically inspected 26-image room×A/B baseline, and read all A/B powder/WC focus screenshots. R060 visually distinguishes retained DRY WOOD floors with deterministic, neutral plank/grain study; plank layout, finish, board width and texture are NOT sourced existing wood flooring, selected SKU or new tile coverage. Powder/WC native wall-face runs remain wall-thickness/hosted-door source-derived, with a restrained warmer plaster-like material and reversible camera-facing section. No Revit Room boundary, actual ceiling solid, floor slab, door leaf/swing, glass or manufactured fixture family solid inferred.\n')
 f.write('- R060 neutral countertop visualization now stays **strictly inside** native Revit Countertop category AABB X/Y/Z (including its visually rendered thickness), while the native AABB volume remains a translucent study only; neither is a fabricated stone profile, cabinetry build, sink cutout, selected cabinet finish or verified mounting. Distinct EXTERIOR Countertop and WC focus cameras point to real read-only native counter bounds and native toilet evidence, respectively. They do NOT represent an interior person/doorway, construction clearance or exact selected fixture location.\n')
 f.write('- **TX-POWDER 102A/B NO PICK YET:** 102B had nearby native plumbing, which previous generic visuals could wrongly turn into an apparently selected 3D basin. R060 suppresses both 102A/B physical basins independent of source presence, while retaining a read-only raised PLAN-XY plumbing vicinity locator under optional Source traces. **TX-POWDER2 010A/B BASIN UNSELECTED** similarly remains physically without a 3D basin, although its Hansgrohe Tecturis E 73072341 deck-mounted faucet remains an unchanged frozen program fact. No faucet location or selected basin shape is invented. PH-POWDER 405A/B keeps R056 exact native insertion Z and +0.50615ft raised locator disclosure, with 3D basin UNLOCATED due to counter containment; 314A/B and 203A/B WC proxy offset stays illustrative and the primary LEVEL floor is inherited with no extra purchase.\n')
 f.write('| Room type | Physical | Native WC ID (source, not solid) | Native countertop AABBs | R060 floor/fixture interpretation |\n')
 f.write('|---|---|---|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   v=inst['r060_visualization']
   floor='DRY WOOD neutral visual, no tile' if v['dry_wood_visual_study'] else 'Existing frozen LEVEL/other selection untouched'
   f.write('| '+r['id']+' | '+str(inst['room_number'])+' | '+str(v['source_wc_native_id'] or 'NONE')+
    ' | '+(', '.join(map(str,v['source_countertop_aabb_ids'])) or 'NONE')+
    ' | '+floor+'; '+v['basin_selection_gate']+' |\n')
 f.write('\nR060 provenance: every instance retains original source receipt IDs in picks.json. OWNER prior confirmation identifies 1527 and 1529 as the same building, but native room membership, session identity, ceiling trimmed geometry, and actual fixture family solids remain uncertified. Five original no-pick rooms, zero approvals, 43 frozen originals, PH4 311/310 source distinction and disputed 26.9792/27.08/35 SF, selected tub/walk-in and LINEAR/POINT drain rules, R056 basin elevation holds and material pools all remain unchanged.\n')
 f.write('\n## R061 integrated bathroom 2/3 wet-zone architectural finish fidelity — 26 instance register\n')
 f.write('- R060 independently reconciled: live viewer source contains its asserted neutral retained wood, native category AABB-bound countertop tops, no-pick TX-POWDER basin gate and 26 R060 source records; one nine-line R060 ledger, one R060 ACCURACY section, six physical Chrome receipts (R060 plus R043/R057/R058/R059 and gallery) all present. Their PASS does not certify the architectural completeness of 13 room types. R061 upstream changes focus **PH-BATH2 305A/B, PH-BATH3 307A/B, TX-BATH2 205A/B, TX-BATH3 207A/B** based on source-wall, November 7 drawing-derived fixture diagrams and actual A/B R060 screenshots; other rooms receive reusable neutral wall/grout/shadow/annotation improvements without modifying picks. The source November 7 PDF itself is not resident as a copy within this approved working folder; registered plan-symbol and native read-only receipt evidence, not the older local October 28 PDF, is the source used here.\n')
 f.write('- Wet finish THREE-DIMENSIONAL W2/W3 returns now require actual registered native wall-face geometry on the same axis and at both ends within tightly constrained visual-projection residuals. When the actual available wall segment does not corroborate a drawing return, suppress its room-volume finish plane while retaining the frozen named W2/W3 dimensions/selected materials in Wet Zone Study and inspector; do not invent a new partition. **TX-BATH2 205A/B:** original wet W1 length 5.207ft exceeds the documented stepped native rear-host span 4.932/5.036ft. The earlier placement-center clamp incorrectly used original wet length rather than the shorter native visual run, leaving both 205A returns missing despite actual native side-wall support; R061 source-centers the shorter visual W1 in real read-only host extents and reveals TWO native corroborated side returns in each A/B. Source wet W1 length, purchase quantities and selected material remain frozen. This is **visual source association**, NOT a native Revit material parameter, certified OST_Rooms boundary, tile layout instruction or field tolerance.\n')
 f.write('- The PH-BATH2 source-calibrated Duravit tub appears behind the selected south/front W1. Ordinary Full Bathroom now keeps the W1 0.72ft visualization section but displays full-height W2/W3 blue tile ONLY when their original source wall faces support those returns. Reversible Wet wall camera shows full original W1/W2/W3 counterparts; no additional tile planes or quantities. PH-BATH3/TX-BATH3 retain 2D drawing tub references, NULL optional pan amounts and NO chosen tub/walk-in, removing only the giant solid-black plan text placard from default view; Source traces ON restores its 2D annotation. TX-BATH2 source-bound selected tub, no PAN, no invented spout/drain and its revised mirror-compatible wet returns stay intact.\n')
 f.write('- Wider viewer: formerly doubled 1/16in *per-edge* grout appearance corrected to a 1/16in nominal TOTAL illustrative seam, PBR source-maker color with subtle generic ceramic arris normal and adjusted matte/gloss response, warmer more solid-looking source walls with reversible camera-facing cutaways, real-time studio shadows limited to source-fitted GENERIC selected tub shell; unverified wall-hung WC shadow explicitly disabled after a detached false ground-shadow counterexample in Chrome. Source-backed W2/W3 finish planes now follow the SAME camera-facing reversible 2.35ft section as their supporting native wall, rather than appearing as floating freestanding full-height sheets; Wet wall review restores the original source height without adding a second purchase. All are **presentation-only**: no exact manufacturer solid, native slab, existing grout choice, finish assembly, installation height, tile shop drawing, recess, glazing, niche, drain position, clearances or bought area.\n')
 f.write('| Room type | Physical A/B | Source wall-face SF (not purchase) | Original wall IDs | Wet/fixture source fidelity |\n|---|---|---:|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   v=inst['r061_visualization']
   f.write('| '+r['id']+' | '+inst['room_number']+' | '+str(v['source_wall_face_area_ft2'] or 'unknown')+
    ' | '+(','.join(map(str,v['original_wall_ids'])) or 'NO NATIVE WALL ID')+
    ' | '+v['wet_return_visual_source_gate']+'; '+v['source_tub_fit']+' |\n')
 f.write('\nR061 frozen controls: same-building 1527/1529 owner confirmation is not equivalent to native OST_Rooms/session-certified geometry; PH4 311 wet/310A WIC4/310B Bath4 identities remain distinct, 26.9792/27.08/35 SF unresolved, original combined 40.2 SF LEVEL/POINT PAN pool and Brizo point selection unchanged. 405A/B basin remains 3D UNLOCATED with its native insertion vertical offset disclosed; TX-PRIMARY no fabricated basin; TX4 selected Duravit 700332000000090 remains 2D UNLOCATED in both instances. Both primaries 48in factory-solid linear drains, WC inherited floors, dry wood powders, five no-picks, zero owner approvals, scores, product models, prices, technical holds and 43 source originals unchanged.\n')
 f.write('\n## R062 viewer-only primary source-bounded architectural enclosures and vanity legibility — 26 physical instances\n')
 f.write('- R061 reconciled before work against actual source JS, architecture generator, standalone HTML, registered per-instance R061 pick records, one 10-line-max ledger and six Chrome-native/fixture/room screenshots and QA receipts; R061 physical 26 instances × 3 modes (78 probes) rerun PASS; this is an implementation regression, NOT whole bathroom/native family acceptance. The latest November 7 plan is present as registered drawing-relative fixture/source metadata and native wall/opening receipts; original November 7 plan PDF itself is not resident in the authorized folder (the on-disk PDF is the older Oct 28 set), so no certification of direct full Nov 7 PDF review is claimed. Full 26 screenshots inspected, with 304A/B and 202A/B source wall, countertop, door and window evidence individually audited.\n')
 f.write('- **PH-PRIMARY 304A/B:** native wall-face polygon 122.0562 SF vs registered drawing 103.09 SF remains an unresolved +18.4% association difference; native long Countertop-category AABB `16428733` A: 2.0×9.177ft, 1.5581–2.8333ft above level, and `15957321` B: 1.658×9.177ft, 1.0027–3.012ft above level, no attributable source lavatory insertion. Original no-pick LEVEL/walls remain neutral. Former neutral vertical shower W1/W2 was shown at drawing-inferred reference against the actual countertop and stepped partition; R062 primary wet-envelope source gate rejects conflicting 3D projections, retains optional source-traces-only 2D diagram and standalone Wet Zone nominal study without moving or installing a shower. Selected factory-solid Brizo BNX 48in LINEAR drain remains a program fact, **not placed as a fixture**.\n')
 f.write('- **TX-PRIMARY 202A/B:** source wall-face polygon 104.4577 SF vs drawing 87.02 SF +20% unresolved, native Countertop category `16437668` A/`18055995` B 1.913×9.562ft 1.9306–3.0ft above level and no attributable sink insertion; native left/right stepped partition and hosted doors 16437700/18056000 and window 16414455/11188884 remain individually source-linked. A November 7 second-floor drawing tub-like pictogram NEVER supersedes frozen WALK-IN+48in factory-solid LINEAR; no invented bathtub, sink count, shower slope, niche, pan, glass or linear drain center. 3D wet-wall location is source-gated separately from selected wet-wall specifications; optional outline classified drawing-relative UNLOCATED.\n')
 f.write('- R062 3D architectural improvements: every source-hosted nominal door/window station gains two neutral source-depth vertical wall-facing reveal studies; only an actual wall segment above the nominal opening receives a thin overhead underside; only a source window with actual sill receives sill return. Geometry uses the original Revit host bounded thickness and existing clipped nominal insertion spans, **NOT actual door leaf/jamb/frame/clear rough opening, swing/hinge or glazed family mesh**; source-only categories remain separately inspectable and reversible with camera-facing wall sections. Native Revit door/window AABB witnesses/receipts and original wall/ceiling geometry are preserved. Both primary long counter 3D studies add a neutral contained front, two end faces and underside **strictly inside existing native category AABB X/Y/Z**; not fabricated wood/stone, sink cutout, toe-kick, joinery, mounting brackets, selected doors, height or sink count. EXTERIOR Primary vanity and Primary enclosure cameras focus source AABB and L-plan native wall faces, not actual standing or installed fixture locations. Generic no-pick floor/wall neutral mineral shade brightened; never a selected tile, marble or new procurement item.\n')
 f.write('| Room type | Physical instance | Source-derived wall-face SF (NOT purchase) | Native countertop category IDs/height (not cabinet) | R062 source truth and limits |\n|---|---|---:|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   v=inst['r062_visualization']
   cs='; '.join(str(cid)+' y '+str(y[0])+'–'+str(y[1])+'ft' for cid,y in zip(
    v['native_casework_category_box_ids'],v['native_casework_local_vertical_bounds_ft'])) or 'NONE'
   status=(v['primary_shower_reference_3d_rendering']+
    '; 48in LINEAR selected, drain location UNKNOWN; NO native lav insertion'
    if v['primary_coordinated_focus'] else
    'Frozen '+str(r['program'].get('kind'))+'; separate native opening/fixture witnesses')
   f.write('| '+r['id']+' | '+inst['room_number']+' | '+
    str(v['inferred_room_wall_face_area_sf'] or 'UNMATCHED')+' | '+cs+' | '+status+' |\n')
 f.write('\nR062 invariants: owner explicitly confirms 1527/1529 are one building, but independent OST_Rooms membership, native solids, field conditions and session certification still absent; PH4 311 wet / 310A WIC4 / 310B Bath4 distinct; 26.9792/27.08/35SF PH4 discrepancy and original 40.2SF combined LEVEL/POINT PAN pool unmodified. PH-POWDER 405A/B native source basin offsets and 3D UNLOCATED; TX-PRIMARY no basin; TX-BATH4 007A/B selected Duravit 700332000000090 2D UNLOCATED; PH-BATH3/TX-BATH3 unselected tub/walk-in optional PAN null, no fabricated primary niche/glass/slopes/rough-ins/door swing. Five no-pick states, zero owner approvals, all factory-solid linear/point drain choices, dry wood floors, WC inherited floors, material prices and quantities remain frozen. All native wall/door/window/casework/ceiling identifiers and original read-only receipts remain available in picks.json.\n')
 f.write('\n**Native receipts:** wall '+WALL_RECEIPT+', hosted door '+DOOR_RECEIPT+', window '+WIN_RECEIPT+', plumbing '+PLUMB_RECEIPT+', casework '+casework_receipt+', ceiling '+ceiling_receipt+'. Every table ID and raw coordinate is in generated picks.json; drawing orientation and room names are not verified native Revit Room IDs.\n')
 f.write('\n## R063 viewer-only bathroom 2/3 interior-fidelity and actual nominal floor-scale correction — 26 physical instances\n')
 f.write('- R062 factual reconciliation first: original rendered standalone index, upstream generator and renderer, one unique 9-line R062 ledger, one R062 ACCURACY section and 26 R062 instance records are present; the physical R062 26×3, R043 26+13 gallery, R057–R061 and 13 type gallery 78 internal probes all show last-run PASS with zero error fields. Physical R062 eight bath2/bath3 A/B baseline frames were recaptured before R063 changes. Reviewer96 only is finished and nonrevivable; none of this is an independent acceptance. The Nov-07 plan PDF itself is not resident within this approved folder: latest November 7 A2.1/A2.2 drawing-derived relative diagrams plus source-native read-only Revit receipts are the evidence, NOT substituted older October drawings.\n')
 f.write('- **R063 source floor/finish fix across eligible rooms:** native-registered floor polygons are THREE ShapeGeometry with UNNORMALIZED planar XY coordinates in FEET. Earlier tileMaterial(room_width,room_depth) multiplied nominal tile repeat by room span *again*, making 24×24in LEVEL tile visually many times too small. Now ShapeGeometry gets one material cycle per physical nominal product tile width/depth in FEET, directly preserving selected vendor-product image and R061 total illustrative 1/16in grout. For rectangular PlaneGeometry wet-zone materials, the original normalized-UV formula is retained; no alternate products, quantities, grout approval, installation layout/shop drawing, slab or field measurements are implied. All dry powders retain existing neutral WOOD and inherited WC remains neutral; no tile applied to no-pick rooms.\n')
 f.write('- **PH-BATH2 305A/B & TX-BATH2 205A/B:** retain native wall/hosted door footprints; original chosen Duravit `700332000000090` nominal 59×29.5in source-fitted ONLY under original drawing-calibrated wall/toilet/door/counter gates. Rounded hollow generic porcelain studio vessel now includes a bounded reflective top lip and a softly colored inner well; not manufacturer mesh or verified installation elevation, faucet, tub rough-in, new slope, drain, niche or PAN. SOURCE-native wall-facing tile returns remain gated as in R061 and retain their actual frozen selected Blue/Sapphire finish; native-wall-supported corner gradients simulate contact shadows without new tile planes or purchased area. PH2 front W1 stays 0.72ft NORMAL section; Wet wall camera still displays full specification. TX2 original shortened stepped W1 4.932/5.036ft and both actual native host returns remain untouched.\n')
 f.write('- **PH-BATH3 307A/B & TX-BATH3 207A/B:** source-selected Pienza Terra / La Belle Antique Blue wet finishes and actual native-supported W2/W3 only (TX 207B retains ONE corroborated return); 24×24in selected LEVEL texture now correctly scaled. FROZEN TUB/WALK-IN remains UNSELECTED, original drawing tub-reference stays 2D/UNLOCATED and optional POINT PAN remains NULL and uncharged. No bathtub, shower pan, fixture, niche box, point-drain center or glass fabricated. Room-specific Bath finish EXTERIOR camera uses source-derived wall-face extents and ORIGINAL drawing wet-side; never a doorway/standing point. A/B physically mirrored, source identities and geometry unchanged.\n')
 f.write('- **Compact vanity/source ambient modeling:** PH-BATH2/3 and TX-BATH2 A/B use ORIGINAL native countertop CATEGORY AABB measured plan and vertical limits for bounded neutral front, two end planes and underside, NOT actual cabinet joinery, sink cutout, faucet, panel finish, mounting or installed elevation. **TX-BATH3 207A/B native Countertop category AABB begins -0.167ft BELOW room level:** no native evidence certifies its bounding box as a floor-piercing installed cabinet, therefore R063 WITHHOLDS every additional compact cabinet front/end/underside there, retains read-only category AABB witness and the original source fixture gates. Existing attributable read-only plumbing insertion and R056 containment logic are unchanged, source counter and actual native markers inspectable. All source wall-bottom contact gradients are restricted to physical native wall-box portions rather than hosted gaps; shadow geometry is VIEW LIGHTING ONLY, not a new baseboard/material. R063 corner shadows restricted to native-backed W2/W3 finishes and follow the reversible section.\n')
 f.write('| Room type | Physical | Drawing-inferred native wall-face SF (not bought) | Native Countertop AABB IDs | R063 original selected LEVEL source | Tub spatial/branch fidelity |\n|---|---|---:|---|---|---|\n')
 for r in data['rooms']:
  for inst in r['physical_instances']:
   v=inst['r063_visualization']
   f.write('| '+r['id']+' | '+inst['room_number']+' | '+
    str(v['inferred_wall_face_area_ft2'] if v['inferred_wall_face_area_ft2'] is not None else 'unverified')+
    ' | '+(','.join(map(str,v['native_countertop_aabb_ids'])) or 'NONE')+
    ' | '+(v['selected_level_material'] or 'UNSELECTED / retained')+
    ' | '+('source-calibrated selected nominal Duravit, no native family' if v['source_tub_nominal_model'] else
      'UNSELECTED 2D-only branch' if v['conditional_tub_or_walk_in_3d_unlocated'] else
      'frozen prior selected or no-pick, no added fixture')+' |\n')
 f.write('\nR063 invariants: ONLY viewer changed; 43 protected originals unchanged at rebuild. Independent native OST_Rooms membership and family solids NOT established; owner confirmation that 1527=1529 is preserved separately from native source confidence. Frozen PH4 311A/B wet vs adjoining 310A WIC4/310B Bath4; disputed PH4 26.9792/27.08/35SF and original single 40.2SF combined LEVEL/POINT PAN; selected point and factory-solid 48in linear drains unchanged, no guessed slopes/rough-ins/glass/niches. PH-POWDER 405A/B basin 3D UNLOCATED, TX-PRIMARY no 3D basin, TX-BATH4 007A/B Duravit selected 2D UNLOCATED, PH3/TX3 tub/walk-in UNSELECTED, five no-pick, zero owner approvals, historical prices/scores/SKUs/quantities/technical holds all unchanged. Color, polish, AO and minor bath-fixture silhouettes are ILLUSTRATIVE and not installed manufacturer solids.\n')
print('R043 registered',len(stats),'instances:',stats)
print('PASS PH4',[(i['room_number'],i.get('architecture',{}).get('floor_polygon_area_ft2')) for r in data['rooms'] if r['id']=='PH-BATH4' for i in r['physical_instances']])
