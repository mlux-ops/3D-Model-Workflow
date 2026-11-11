"""R068 standalone visual source review; no 26x3, 78 or legacy suites.
Usage: python -B scratch/qa_r068_wet_baths_browser.py before|after
Four wet-bath types, actual A/B; Focus Full ISO and detail, source Wet Study,
and two A-instance Revit Context checks with physical PNG contact sheet.
"""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageChops,ImageStat,ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PHASE=sys.argv[1] if len(sys.argv)>1 else 'after'
assert PHASE in ('before','after')
DEST=ROOT/'scratch/r068_focus'/PHASE
DEST.mkdir(parents=True,exist_ok=True)
CASES=[('PH-PRIMARY','304A'),('PH-PRIMARY','304B'),
 ('TX-PRIMARY','202A'),('TX-PRIMARY','202B'),
 ('PH-BATH2','305A'),('PH-BATH2','305B'),
 ('TX-BATH2','205A'),('TX-BATH2','205B')]
PICKS=ROOT/'deliverables/viewer3d/picks.json'
EXPECTED_SHA='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d'
rooms={r['id']:r for r in json.loads(PICKS.read_text(encoding='utf8'))['rooms']}
errors=[];shots=[];record={};interaction=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1480,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda err:errors.append('pageerror:'+str(err)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-PRIMARY/304A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=48000)
 page.locator('#viewer-focus-enter').click()
 def shot(key,suffix):
  path=DEST/(key+'_'+suffix+'.png')
  page.locator('#stage').screenshot(path=str(path))
  shots.append(path)
 for kind,n in CASES:
  key=kind+'_'+n
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',kind+'/'+n)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=25000)
  page.wait_for_timeout(90)
  if page.evaluate('document.body.dataset.viewerInstance')!=n:errors.append('wrong instance '+key)
  if not page.evaluate('window.__viewerDebug.getState().focusView'):errors.append('Focus exited '+key)
  arch=next(x for x in rooms[kind]['physical_instances'] if x['room_number']==n)['architecture']
  evidence=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  cats=[o.get('category') for o in evidence]
  expectedWalls=len(arch['wall_segments'])
  wallObjects=[o for o in evidence if o['category']=='ARCH_REGISTERED_WALL']
  if len(wallObjects)<4:errors.append('missing native walls '+key)
  if len([o for o in evidence if o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL'])!=1:
   errors.append('counter category AABB missing '+key)
  if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
   errors.append('PAN in selected tub/unknown primary room '+key)
  if kind.endswith('PRIMARY') and any(o['category']=='ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY' for o in evidence):
   errors.append('fabricated primary basin '+key)
  if kind.endswith('BATH2'):
   # The real registered generic shell has kind=tub, not the obsolete
   # r063_tub_part BODY/SHELL key; top ceramic rim has a distinct part name.
   if not any(o.get('kind')=='tub' and o['category']=='PLAN_SCHEMATIC_FIXTURE' for o in evidence):
    errors.append('selected nominal Duravit tub shell missing '+key)
   if not any(o['category']=='FULL_ROOM_WET_WALL' for o in evidence):
    errors.append('selected wet-wall study absent '+key)
  if PHASE=='after':
   # R068 geometry assertions filled against actual source metadata; never
   # imply new manufacturer solids, fixtures, selected tile or room members.
   if not any(o['category']=='ARCH_R068_SOURCE_COUNTER_LIGHT_REVEAL' for o in evidence):
    errors.append('R068 bounded counter detail absent '+key)
   if not any(o['category']=='ARCH_R068_NATIVE_WALL_DEPTH_LIGHT' for o in evidence):
    errors.append('R068 native wall photographic depth missing '+key)
   if kind.endswith('PRIMARY'):
    schedule=page.evaluate('window.__viewerDebug.getR068PrimarySheetBath()')
    required='700337000000090' if kind=='PH-PRIMARY' else 'TER-N-SW-OF'
    if not schedule or schedule.get('model_or_sku')!=required or not schedule.get('not_installed_fixture'):
     errors.append('separate primary sheet-listed tub source HOLD missing '+key)
    if not any(o.get('primary_no_physical_shower_model') for o in evidence):
     errors.append('primary source-only walk-in annotation missing '+key)
   if kind.endswith('BATH2') and not any(o['category']=='ARCH_R068_SOURCE_WET_CONTACT_LIGHT' for o in evidence):
    errors.append('R068 native wet finish contact treatment missing '+key)
   if kind.endswith('BATH2') and not any(o.get('r068_selected_bath2_glazed_optical_relief') for o in evidence):
    errors.append('selected nominal ceramic relief missing '+key)
   for o in evidence:
    if o['category']=='ARCH_R068_SOURCE_COUNTER_LIGHT_REVEAL':
     if not o.get('r068_inside_native_countertop_xyz'):errors.append('counter visual not source bounded '+key)
     c=arch['native_casework_proxies'][0];xx,zz=c['local_center_xz_ft']
     limits=[[xx-c['width_x_ft']/2,c['min_height_ft'],zz-c['depth_z_ft']/2],
      [xx+c['width_x_ft']/2,c['max_height_ft'],zz+c['depth_z_ft']/2]]
     bb=o.get('r068_world_mesh_aabb')
     if not bb or any(bb[0][a]<limits[0][a]-.005 or bb[1][a]>limits[1][a]+.005 for a in range(3)):
      errors.append('counter actual mesh outside category XYZ '+key)
  page.locator('#viewer-focus-iso').click()
  shot(key,'ISO')
  preset='r062-primary-vanity' if kind.endswith('PRIMARY') else 'r063-bath-finish'
  if PHASE=='after':
   page.locator('#viewer-focus-architectural' if kind.endswith('PRIMARY') else '#viewer-focus-finish').click()
  else:
   page.evaluate('(x)=>window.__viewerDebug.setCamera(x)',preset)
  if PHASE=='after' and page.evaluate('window.__viewerDebug.getCameraInfo().preset')!=preset:
   errors.append('wrong detail preset '+key)
  shot(key,'DETAIL')
  page.evaluate('window.__viewerDebug.setMode("study")')
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
  page.evaluate('window.__viewerDebug.setCamera("isometric")')
  shot(key,'WET_STUDY')
  if PHASE=='after' and not any(o['category']=='sourceWall' for o in page.evaluate('window.__viewerDebug.getSceneEvidence()')):
   errors.append('Wet mode source wall lost '+key)
  if n.endswith('A') and kind in ('PH-PRIMARY','TX-BATH2'):
   page.evaluate('window.__viewerDebug.setMode("context")')
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
   shot(key,'REVIT_CONTEXT')
   if PHASE=='after' and not page.evaluate('window.__viewerDebug.getState().mode==="context"'):
    errors.append('Revit context inaccessible '+key)
  page.evaluate('window.__viewerDebug.setMode("full")')
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
  if PHASE=='after' and n.endswith('A'):
   if arch.get('native_ceiling_evidence',{} ) and not page.locator('#viewer-focus-gwb').is_hidden():
    page.locator('#viewer-focus-gwb').click()
    page.locator('#viewer-focus-gwb').click()
   page.locator('#viewer-focus-ab').click()
   if not page.locator('#viewer-ab-drawer').is_visible():errors.append('A/B plan compare '+key)
   page.locator('#viewer-focus-ab').click()
   page.locator('#viewer-focus-traces').click()
   page.locator('#viewer-focus-traces').click()
   page.locator('#viewer-focus-cutaway').click()
   page.locator('#viewer-focus-cutaway').click()
   if not page.evaluate('window.__viewerDebug.getState().interiorReveal'):
    errors.append('reversible cutaway not restored '+key)
   interaction.append(key)
  record[key]={'source_wall_segments':expectedWalls,'rendered_wall_pieces':len(wallObjects),
   'native_casework_ids':[x['id'] for x in arch['native_casework_proxies']],
   'native_door_ids':[x['id'] for x in arch.get('openings',[]) if x['kind']=='door'],
   'native_ceiling_source':bool(arch.get('native_ceiling_evidence')),
   'selected_3d_tub':bool(arch.get('selected_tub_proxy')),
   'modes':['full','study']+(['context'] if n.endswith('A') and kind in ('PH-PRIMARY','TX-BATH2') else [])}
 if PHASE=='after' and page.evaluate('window.__viewerDebug.errors'):
  errors.append('runtime '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

# Visual survey contact sheet, not an assertion substitute.
cw,ch=475,322
contact=Image.new('RGB',(cw*4,ch*((len(shots)+3)//4)),(27,35,43))
draw=ImageDraw.Draw(contact)
for i,path in enumerate(shots):
 im=Image.open(path).convert('RGB');im.thumbnail((cw-8,ch-28))
 x=(i%4)*cw;y=(i//4)*ch
 contact.paste(im,(x,y+25));draw.text((x+6,y+5),path.stem,fill='#ffffff')
contact.save(DEST/'R068_WET_BATHS_CONTACT_SHEET.png')
deltas=[]
if PHASE=='after':
 for k,n in CASES:
  for suffix in ('ISO','DETAIL','WET_STUDY'):
   f=k+'_'+n+'_'+suffix+'.png'
   a=Image.open(DEST.parent/'before'/f).convert('RGB')
   b=Image.open(DEST/f).convert('RGB')
   delta=round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
   deltas.append((f,delta))
   if delta<.25:errors.append('no visual change '+f)
if hashlib.sha256(PICKS.read_bytes()).hexdigest()!=EXPECTED_SHA:errors.append('frozen picks changed')
result={'status':'PASS' if not errors else 'FIX','phase':PHASE,
 'focus_cases':[k+'/'+n for k,n in CASES],'errors':errors,'interactions':interaction,
 'picks_sha256':hashlib.sha256(PICKS.read_bytes()).hexdigest(),
 'source_receipts':record,'visual_deltas':deltas,
 'physical_capture_count':len(shots)}
(DEST/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='source_receipts'},indent=2))
if errors:raise SystemExit(1)
