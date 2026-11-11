"""Frozen-tile interactive viewer data from current project state and read-only Revit receipts."""
from pathlib import Path
import json,re,math,html,datetime
P=Path(__file__).resolve().parents[1]
OUT=P/'deliverables/viewer3d'
OUT.mkdir(parents=True,exist_ok=True)
STATE=json.loads((P/'state/ROOMS.json').read_text(encoding='utf-8'))
REV=json.loads((P/'scratch/viewer3d_revit_sources.json').read_text(encoding='utf-8'))
rooms=STATE['rooms']
images_dir=P/'deliverables/assets/tile_thumbs'
texture_dest=OUT/'assets';texture_dest.mkdir(exist_ok=True)
import shutil
for src in images_dir.glob('*.jpg'):
 shutil.copyfile(src,texture_dest/src.name)

def products_for(room):
 rid=room['id']
 if room.get('status')=='blocked' or not room.get('champion_id'):
  return []
 # Frozen HTML owner source is generated directly from genuine current champion snapshots.
 src=P/'deliverables/r039-13-owner-review-PROVISIONAL'/(rid+'.html')
 if not src.exists():return []
 t=src.read_text(encoding='utf-8')
 m=re.search(r'<h2>Proposed tile by actual surface</h2><table>.*?<tbody>(.*?)</tbody>',t,re.S|re.I)
 if not m:return []
 rows=[]
 urlkey={
  'pienza-terra':'pienza','sandstone-tones':'sandstone','sapphire-tones':'sapphire',
  'indigo-edge':'indigo','earth-lines':'earth','haze-camel':'haze','luxe-sand':'luxe',
  'de-rossi-ivory':'derossi',
  'la-belle-purity':'purity','la-belle-antique':'antique','cortar-clay':'clay',
  'cortar-bone':'bone','cortar-charcoal':'charcoal','riviera-oat':'riviera','perimeter-gray':'perimeter',
 }
 for row in re.findall(r'<tr>(.*?)</tr>',m.group(1),re.S):
  cells=re.findall(r'<td>(.*?)</td>',row,re.S)
  if len(cells)!=3:continue
  def strip(x):return html.unescape(re.sub('<[^>]+>',' ',x)).strip()
  link=re.search(r'href="([^"]+)"[^>]*>(.*?)</a>',cells[1],re.S)
  if not link:continue
  url=html.unescape(link.group(1));name=strip(link.group(2))
  key=next((v for k,v in urlkey.items() if k in url.lower()),None)
  if key and not (texture_dest/(key+'.jpg')).is_file():key=None
  sz=strip(cells[1]).replace(name,'',1).strip()
  rows.append({'surface':strip(cells[0]),'name':name,'size':sz,'price':strip(cells[2]),
               'url':url,'image':('assets/'+key+'.jpg') if key else None,
               'source':'Frozen existing R039 owner review, based on current champion; verify physical sample'})
 return rows

def alternate_for(rid):
 if rid!='PH-BATH4':return None
 # Verified archived R036 challenger A. Preview only; NOT an approved current pick.
 return {'provenance':'Historical R036 alternative A, unselected',
         'products':[
          {'surface':'Wet WALL','name':'F&D Perimeter Gray Matte Porcelain 101239218',
           'size':'24x48','price':'$3.99/SF historic non-Chicago public retail',
           'url':'https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html','image':'assets/perimeter.jpg'},
          {'surface':'Niche all faces','name':'F&D La Belle Purity High Gloss Ceramic 100507722',
           'size':'3x12','price':'$5.56/SF historic non-Chicago public retail',
           'url':'https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html','image':'assets/purity.jpg'},
          {'surface':'Shared LEVEL + POINT PAN','name':'F&D Luxe Sand Matte Porcelain 101317949',
           'size':'24x24','price':'$3.49/SF historic non-Chicago public retail',
           'url':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html','image':'assets/luxe.jpg'}]}

def level_hint(rid):
 if rid.startswith('PH-'):
  return 42.0 if rid!='PH-POWDER' else 51.0
 if rid in ('TX-BATH4','TX-POWDER2'):return -5.0
 if rid in ('TX-PRIMARY','TX-BATH2','TX-BATH3','TX-WC'):return 28.0
 return 8.0

def candidate_context(rid):
 # Room dimensions are never invented: this is a model-wide context proxy,
 # not a proven room-specific wall selection. Elements retain exact Revit bounds.
 z=level_hint(rid)
 rev=REV['categories']
 walls=rev['walls']['items']; fixtures=rev['plumbing']['items']
 # Two nearly symmetric units; use one side as a context viewport only.
 # The center is a visual browsing point, NOT a verified room centroid.
 center=[-535.5,228.0,z]
 # Select representative elements near a visualization anchor, always source-qualified.
 def near(item):
  b=item.get('bounds')
  if not b:return False
  lo,hi=b['min'],b['max']
  mx=(lo[0]+hi[0])/2;my=(lo[1]+hi[1])/2
  return abs(mx-center[0])<=20 and abs(my-center[1])<=22 and lo[2] < z+10 and hi[2]>z-2
 def emit(key,items,n):
  return [{'id':x['id'],'name':x.get('name'),'bounds':x['bounds'],'host_id':x.get('host_id'),
           'location':x.get('location'),'receipt_id':rev[key]['receipt_id'],'category':key,
           'representation':'Revit axis-aligned bounding box; mesh/profile not exposed'}
          for x in items if near(x)][:n]
 return {'anchor_ft':center,'anchor_status':'visual browsing anchor, room placement UNVERIFIED',
         'walls':emit('walls',walls,35),'fixtures':emit('plumbing',fixtures,20),
         'doors':emit('doors',rev['doors']['items'],15),
         'windows':emit('windows',rev['windows']['items'],10),
         'casework':emit('casework',rev['casework']['items'],20),
         'floors':emit('floors',rev['floors']['items'],8)}

records=[]
for r in rooms:
 rid=r['id'];prod=products_for(r);context=candidate_context(rid)
 # Truly blocked Primaries/WCs/powder show no selected tile per newest owner instruction.
 rec={'id':rid,'title':r.get('room_name',rid),'unit_type':r.get('unit_type',''),
      'numbers':r.get('revit_room_numbers',[]),'status':r.get('status'),
      'champion_id':r.get('champion_id'),'champion_score':r.get('champion_score'),
      'has_pick':bool(prod),'products':prod,'alternative':alternate_for(rid),'model_context':context,
      'geometry_confidence':'MODEL-DERIVED CONTEXT ONLY: room-specific assignment unverified',
      'revit_receipts':{k:v.get('receipt_id') for k,v in REV['categories'].items()},
      'fixture_shapes':'axis-aligned Revit bounding boxes only; not family solids',
      'alternative_status':'Historic alternatives are not active tile picks and are not applied to geometry'}
 records.append(rec)
payload={'model':'25-006 1527 N Wieland','owner_confirmed_same_building':True,
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'read_only_revit':True,'unit':'feet','room_geometry_verified':False,
 'rooms':records,'revit_query_errors':REV.get('errors',[]),
 'warning':'Illustrative model-derived context, NOT surveyed room-specific geometry, construction layout or owner approval. No guesswork is marked as measured.'}
(OUT/'picks.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'ACCURACY.md').write_text("""# 1529 Wieland — 3D viewer geometry accuracy and limitation register

## Verified provenance

- Source: live open Revit model **25-006 1527 N Wieland** (same 1529 building per owner confirmation); accessed through the project-approved **read-only** `tools/revit_read.py`.
- Native Revit `elements.query` returned **axis-aligned bounding boxes and insertion locations** for walls, plumbing fixtures, doors, windows, floors, ceilings and casework. Receipts and every rendered object's Revit element ID are recorded in `picks.json`, and original receipt files remain under `state/revit_receipts/`.
- Geometry uses feet as exported by the bridge. The viewer transforms world horizontal XY and vertical Z consistently, keeping exact bounding-box dimensions for the selected context objects.
- Current tile choices are frozen and sourced from `state/ROOMS.json` and current owner room review, not re-scored. PH-BATH4 uses Pienza Terra for wet wall and one floor/pan pool, Elm Sandstone for the niche accent. Manufacturer thumbnail is a visual proxy, **not an exact physical sample**.

## NOT established — do not treat as exact

- **Room-specific placement is NOT verified**: the bridge's `OST_Rooms` query fails due an unsupported rotation property; `parameters.query` and `elements.inspect` return KeyNotFoundException in this runtime. Room tag placement does not supply a reliable wall/fixture-to-room map.
- Consequently, the 3D viewer shows a **real Revit-derived neighborhood context** at an explicitly approximate browsing anchor, **not a claim that all displayed walls, fixtures or openings belong to the selected named bathroom**.
- Wall centerlines, compound layers, face/solid mesh, exact floor boundary, door/window cut-out profiles, shower curbs, point-drain position, niche location/dimensions and selected tub/vanity/toilet type-to-room associations **could not be read**. Each drawn element is a labeled Revit bounding box, not an exact shaped fixture; no invented niche or drain geometry is installed.
- Real nominal tile dimensions and grout reveal appear in the selected surface information; visible procedurally repeated tile graphics are **illustrative** and not a measured setter's layout. Walls and slab texture assignments are **visual overlays on context**, not a confirmed per-face BIM material assignment.
- No exact photorealistic claim is possible from bounds-only geometry. The WebGL renderer supplies PBR lighting, high-quality materials, exposure and interactive orbit/pan/zoom as available, but visual appearance and room attribution must be validated against actual Revit solids/mesh or a room geometry export.
- Tile selection itself remains **PROVISIONAL**, with owner approvals zero; blocked rooms deliberately show `NO PICK YET`.

## Missing source / recommended release evidence

A room boundary-to-element export from Revit (room number, wall curve endpoints, thickness, Z, floor outline, openings hosted wall ID+width+height+offset, fixture family type/location/rotation/bounds and niches) would permit a source-faithful bath reconstruction. Until then the viewer must visibly disclose the context-only mode. No Revit or Smartsheet edits were made.
""",encoding='utf-8')
print('PASS',len(records),'rooms frozen','with_tiles',sum(r['has_pick'] for r in records),'PH4_surfaces',len(next(r for r in records if r['id']=='PH-BATH4')['products']),'output',OUT)
