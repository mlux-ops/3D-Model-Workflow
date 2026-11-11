"""PH-BATH4-first dimensioned wet-zone and real level-specific Revit context.

Read-only source receipts; no new Revit calls, no tile decisions.
Run AFTER build_viewer3d_data.py and BEFORE build_viewer3d_index.py.
"""
from pathlib import Path
from collections import Counter
import json,datetime

P=Path(__file__).resolve().parents[1]
OUT=P/'deliverables/viewer3d'
data=json.loads((OUT/'picks.json').read_text(encoding='utf-8'))
revit=json.loads((P/'scratch/viewer3d_revit_sources.json').read_text(encoding='utf-8'))
level_receipt='9c9f23a7-8c76-4815-b5f4-b92320cb97a3'
level_raw=json.loads((P/'state/revit_receipts'/f'{level_receipt}.json').read_text(encoding='utf-8'))
assert level_raw['status']=='completed' and level_raw['request']['operation']=='elements.query'
levels={str(x['name']):x for x in level_raw['result']['items']}
level_spec={
 '0':('LOWER LEVEL',-5.0),
 '1':('1ST FLOOR',6.666666666666661),
 '2':('2ND FLOOR',17.333333333332995),
 '3':('3RD FLOOR',27.999999999999666),
 '4':('4TH FLOOR',38.66666666666632)}
for k,(name,z) in level_spec.items():
 assert abs(levels[name]['elevation']-z)<.001,(name,levels[name])

programs={
 'PH-BATH4':('WALK_IN_SELECTED','Brizo BT062415-BNX 4-inch SQUARE POINT, Brilliance Black Onyx','One combined original 40.2 gross SF LEVEL/POINT PAN; no separate second charge',False),
 'PH-BATH2':('DURAVIT_TUB_SELECTED','Duravit TUB with Hansgrohe Matte White','NO tiled shower PAN or POINT drain',False),
 'TX-BATH2':('DURAVIT_TUB_SELECTED','Duravit TUB with Hansgrohe Chrome; basin UNSELECTED','NO tiled shower PAN or POINT drain',False),
 'TX-BATH4':('DURAVIT_TUB_SELECTED','Duravit TUB with Hansgrohe Matte White','NO tiled shower PAN or POINT drain',False),
 'PH-BATH3':('TUB_OR_WALK_IN_UNSELECTED','Hansgrohe Chrome; conditional Delta DT062412 4-inch POINT only if WALK-IN; basin UNSELECTED','40.2 gross SF LEVEL only; additional optional PAN SF and cost NULL',False),
 'TX-BATH3':('TUB_OR_WALK_IN_UNSELECTED','Brizo BNX BT062415-BNX 4-inch POINT only if WALK-IN','42.5 gross SF LEVEL only; additional optional PAN SF and cost NULL',False),
 'PH-PRIMARY':('PRIMARY_WALK_IN_LINEAR','Brizo BNX 48-inch LINEAR factory-solid grate, NO niches','Wet shower CEILING tile permission + assembly BLOCKED',True),
 'TX-PRIMARY':('PRIMARY_WALK_IN_LINEAR','Brizo BNX 48-inch LINEAR factory-solid grate, NO niches','Wet shower CEILING tile permission + assembly BLOCKED',True),
 'PH-WC':('WC_PRIMARY_INHERITED','WC inherits Primary LEVEL tile; no independent duplicated floor purchase','BLOCKED with Primary; tile not selected',True),
 'TX-WC':('WC_PRIMARY_INHERITED','WC inherits Primary LEVEL tile; no independent duplicated floor purchase','BLOCKED with Primary; tile not selected',True),
 'PH-POWDER':('DRY_WOOD','Dry vanity WALL; retained wood flooring','No tiled LEVEL/PAN',False),
 'TX-POWDER':('DRY_WOOD','Dry vanity WALL; wall-mounted faucet finish UNCONFIRMED; retained wood flooring','No tile champion; NO PICK YET',True),
 'TX-POWDER2':('DRY_WOOD','Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK-mounted; basin UNSELECTED; retained wood floor','No tiled LEVEL/PAN',False)
}
def source_value(entry):
 if not isinstance(entry,dict):return None
 return {'value':entry.get('value'),'unit':entry.get('unit'),
         'classification':entry.get('classification'),
         'source':entry.get('source'),
         'live_revit_verified':bool(entry.get('live_revit_verified')),
         'revit_element_id':entry.get('revit_element_id'),
         'revit_receipt_id':entry.get('revit_receipt_id')}

def instance_context(z,side):
 # All values are actual native element BOUNDING BOXES, not room attribution.
 # 2026-11-07 A2.1/A2.2 proves A is EAST and B is WEST in drawing registration.
 xmid=-533.5
 xbounds=(-533.5,-507.0) if side=='A' else (-559.0,-533.5)
 ybounds=(175.0,267.0)
 out={}
 for key in ('walls','doors','windows','plumbing','casework','floors','ceilings'):
  source=revit['categories'][key]
  vals=[]
  for elem in source['items']:
   bounds=elem.get('bounds')
   if not bounds:continue
   lo=bounds.get('min');hi=bounds.get('max')
   if not lo or not hi:continue
   if lo[2]>z+11.3 or hi[2]<z+.10:continue
   if hi[0]<xbounds[0] or lo[0]>xbounds[1]:continue
   if hi[1]<ybounds[0] or lo[1]>ybounds[1]:continue
   # Do not assign shared large slabs to either specific bathroom.
   if key in ('floors','ceilings') and ((hi[0]-lo[0]>65) or (hi[1]-lo[1]>100)):continue
   vals.append({'id':elem['id'],'name':elem.get('name'),'category':key,
                'bounds':bounds,'host_id':elem.get('host_id'),
                'location':elem.get('location'),
                'receipt_id':source['receipt_id'],
                'representation':'READ_ONLY_REVIT_BOUNDS',
                'room_association':'UNVERIFIED'})
  out[key]=vals
 return out

for room in data['rooms']:
 rid=room['id']
 source=P/'rooms'/rid/'geometry.json'
 geom=json.loads(source.read_text(encoding='utf-8'))
 wall_data=[]
 for w in geom.get('tiled_walls') or []:
  wall_data.append({'id':w.get('id'),'description':w.get('description'),
                    'length':source_value(w.get('length')),
                    'height':source_value(w.get('height')),
                    'tiled_height':source_value(w.get('tiled_height')),
                    'openings':w.get('openings'),
                    'revit_element_id':w.get('revit_element_id')})
 fp=geom.get('shower_or_tub_footprint') or {}
 kind,fixture,scope,blocked=programs[rid]
 room['program']={'kind':kind,'plumbing_truth':fixture,'scope_truth':scope,
                  'technical_hold':blocked,'tub_selected':kind=='DURAVIT_TUB_SELECTED',
                  'walk_in_selected':kind in ('WALK_IN_SELECTED','PRIMARY_WALK_IN_LINEAR'),
                  'pan_selected':kind=='WALK_IN_SELECTED',
                  'dry_floor_retained':kind=='DRY_WOOD',
                  'owner_approved':False}
 room['wet_zone_schematic']={'wall_segments':wall_data,
        'width':source_value(fp.get('width')),
        'depth':source_value(fp.get('depth')),
        'reported_kind':fp.get('kind'),
        'ceiling':source_value(geom.get('ceiling_height')),
        'floor_area':source_value(geom.get('floor_area')),
        'room_exact_solid_geometry':None,
        'orientation':'UNVERIFIED; schematic normal axes only',
        'openings':'NOT_EXTRACTED',
        'niche_location':'NOT_EXTRACTED',
        'drain_location':'NOT_EXTRACTED',
        'draw_only_source_dimensions':True}
 room['physical_instances']=[]
 for n in room['numbers']:
  first=str(n)[0]
  if first not in level_spec:continue
  name,z=level_spec[first]
  side='B' if str(n).upper().endswith('B') else 'A'
  ctx=instance_context(z,side)
  room['physical_instances'].append({
   'room_number':n,
   'revit_room_element_id':None,
   'room_number_source':'state/ROOMS.json room schedule handoff; NOT yet native spatial-ID verified',
   'level':{'name':name,'elevation_ft':z,'element_id':levels[name]['id'],
            'receipt_id':level_receipt,
            'mapping':'INFERRED from first digit of room number; source model level elevation VERIFIED'},
   'unit_side':{'value':side,'mapping':'DRAWING-REGISTERED A-east/B-west; native room-tag ID unavailable'},
   'unit_context':ctx,'room_boundary':None,
   'room_geometry_fidelity':'SOURCE_MEASURED_MODEL_BOUNDS_AT_LEVEL, ROOM_ASSOCIATION_UNVERIFIED',
   'missing':[
    'Room element id and spatial boundary/host-wall assignment',
    'Actual named-room slab and ceiling polygons',
    'Door/window host geometry and opening profile for room',
    'Fixtures placed/rotated in named room, family solids and drains',
    'Niche spatial location, cutout and tile return profiles']})
 assert len(room['physical_instances'])==2,(rid,room['physical_instances'])
 room['geometry_confidence']='Two distinct floor-matched Revit contexts (real bounds; room not mapped), with drawing-derived wet-zone scale where available'
 # Legacy single-context anchor falsely implied common center/z; replace with a null sentinel.
 room['model_context']=None

assert len(data['rooms'])==13 and sum(len(x['physical_instances']) for x in data['rooms'])==26
assert next(x for x in data['rooms'] if x['id']=='PH-BATH4')['physical_instances'][0]['level']['elevation_ft']==28-3.34e-13
assert next(x for x in data['rooms'] if x['id']=='TX-POWDER')['has_pick'] is False
data['room_geometry_verified']=False
data['geometry_strategy']='DUAL MODE: real Revit level/instance context bounds + source-dimensioned wet-zone schematic; no exact room-face map'
data['phase']='v2_room_level_context_and_dimensioned_schematic'
(OUT/'picks.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

matrix=['# 1529 Wieland — VIEWER ACCURACY v2 (frozen selections)', '',
 '## Evidence class and truthful fidelity',
 '- **Native Revit read-only element bounds and insertion transforms:** direct bridge query receipts for walls, doors, windows, floors, ceilings, casework and plumbing; all model coordinates are feet. Level-context casework/plumbing insertion symbols use actual native `location.point` and `rotation_radians` only when the point falls within/near its source element bounds. Symbols are NOT fixture solids and are NOT assigned to the named bathroom.',
 f'- **Native floor elevations:** OST_Levels receipt `{level_receipt}`; lower -5, first 6.667, second 17.333, third 28, fourth 38.667 feet.',
 '- **Room number → level:** digit-of-number inference against native level schedule, NOT a native Revit room spatial match. **A EAST / B WEST** is the latest November 7, 2026 A2.1/A2.2 drawing-registered wing orientation; Revit Room IDs remain unavailable.',
 '- **Dimensioned wet-zone drawing study:** wall runs/footprint/ceiling from existing room `geometry.json`, with original classifications and sources preserved; physical location and orientation unverified.',
 '- **Viewer reconstruction is not certified BIM or construction-ready:** downstream R043 architecture enrichment uses actual native wall location-line endpoints and bounding thickness to reconstruct wall-face polygons for all 26 physical instances; 305A/B require explicitly drawing-calibrated corner closures. Read-only hosted doors/windows are mapped to native wall hosts, but each host-wall-to-NAMED-ROOM assignment remains drawing-inferred, never an `OST_Rooms` spatial boundary. Generic fixture and selected-tub visual proxies are independently source-gated, not native family solids. No verified niche, pan slope, rough-in or drain point. Revit Context separately displays original native AABBs/insertions; Wet Zone Study retains source-specified material-height diagrams.',
 '- No specific room membership is certified for native elements. Viewer-only visual geometry may be calibrated from November 7 plans while original source quantities, prices, frozen selections and technical holds remain unchanged. PH-BATH2 305A/B south wet W1/returns use a 0.72-ft VISUAL CUTAWAY in Full Bathroom to reveal the selected tub, with full-height wet specification retained in Wet Zone Study. Zero owner approvals.',
 '', '## Room-by-room fidelity matrix',
 '| Room · physical instances | Revit level evidence / model context | Drawing-derived geometry used | Actual room assignment and unresolved elements |',
 '|---|---|---|---|']
for room in data['rooms']:
 rid=room['id'];ws=room['wet_zone_schematic']['wall_segments']
 lc=room['physical_instances'][0]['level']
 nums='/'.join(room['numbers'])
 wstr=', '.join(f"{w['id']} {w['length']['value']} {w['length']['unit']}" for w in ws if w.get('length') and w['length']['value'] is not None) or 'No verified wall runs'
 cv=room['wet_zone_schematic']['ceiling']
 h=('; height '+str(cv['value'])+' '+str(cv['unit'])+' (drawing-derived)') if cv and cv.get('value') is not None else ''
 matrix.append(f"| {rid} ({nums}) | {lc['name']} {lc['elevation_ft']:.3f} ft, ID {lc['element_id']}, receipt {level_receipt} — room-to-level inferred; true native bounding boxes by unit side | {wstr}{h} | Spatial room ID/true wall boundaries, slab footprint, hosted openings, family solids, niche/drain positions NOT verified. {room['program']['scope_truth']} |")
matrix += ['', '## Selected program invariants and material provenance',
 '- PH-BATH4: owner WALK-IN, Brizo BNX BT062415-BNX square POINT; source wet-zone 5.0 × 2.54 ft approximate and 9.25-ft ceiling drawing-derived. Original 40.2 gross SF single LEVEL/POINT PAN pool, never duplicate. F&D Pienza Terra on specified wet wall and selected bath LEVEL/PAN; Elm Sandstone NICHE specification only until niche location read.',
 '- PH-BATH2, TX-BATH2, TX-BATH4: actual selected Duravit TUB; NO tiled shower PAN, no point-drain object created.',
 '- PH-BATH3, TX-BATH3: TUB/WALK-IN UNSELECTED, conditional point drain only in WALK-IN; optional PAN area/cost NULL, not zero; no simulated approved tub or walk-in.',
 '- PH-PRIMARY/TX-PRIMARY: original 48-inch Brizo BNX LINEAR factory-solid grates; no niches and wet-overhead maker/assembly blocker. WC tile follows Primary LEVEL; both blocked. No selected material painted on these surfaces.',
 '- All dry powder rooms: original wood floor retained; no new tiled floor, wet pan or niche. TX-POWDER has no tile pick.',
 '- Manufacturer thumbnails (not samples) are supplied from existing project thumbnails. Sandstone installation photo is MIXED Sandstone/Copper, not exact Sandstone-only proof.',
 '- Tile nominal-size representation and 1/16-in illustrative grout are a study default if used; manufacturer geometry/cuts and layout orientation require verification.',
 '- A clickable native-element inspector in Revit context exposes the original element ID, receipt, bounds, insertion point/rotation and host ID (when returned); these are evidence, not certified bathroom attribution. The image gallery is a render diagnostic and not independent spatial BIM certification.',
 '', '## Evidence needed to graduate to exact geometry',
 '1. Read-only native room schedule or room-tag-to-room mapping with room element IDs for every 311A/B et al.; current `OST_Rooms` serializes with unsupported LocationPoint rotation and `parameters.query`/`elements.inspect` produce KeyNotFoundException.',
 '2. Wall lines/thickness and hosted nominal insertions are already available; still needed: true named-room spatial boundary and floor/ceiling profiles, exact rough-opening/hinge/swing details, and native family solids/mesh for drain, fixtures, shower screens, tub and niche.',
 '3. Field reconciliation owner 35 SF versus drawing 27 SF PH-BATH4 floor discrepancy; source gross 40.2 SF already includes original 15% waste ONCE.',
 '', 'No Revit write, Git, Smartsheet write, procurement, scoring or owner-packet revision performed.']
(OUT/'ACCURACY.md').write_text('\n'.join(matrix)+'\n',encoding='utf-8')
print('PASS',len(data['rooms']),'room types',sum(len(x['physical_instances']) for x in data['rooms']),'physical instances; PH-BATH4 both at Revit 3rd-floor z28 and no fabrications')
