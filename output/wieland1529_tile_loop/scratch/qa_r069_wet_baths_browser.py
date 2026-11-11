"""R069 standalone visual source review; no 26x3, 78 or legacy suites.
Usage: python -B scratch/qa_r069_wet_baths_browser.py before|after
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
DEST=ROOT/'scratch/r069_focus'/PHASE
DEST.mkdir(parents=True,exist_ok=True)
CASES=[('PH-BATH3','307A'),('PH-BATH3','307B'),
 ('TX-BATH3','207A'),('TX-BATH3','207B'),
 ('PH-BATH4','311A'),('PH-BATH4','311B'),
 ('TX-BATH4','007A'),('TX-BATH4','007B')]
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
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-BATH3/307A',wait_until='load')
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
  if kind!='PH-BATH4' and len([o for o in evidence if o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL'])!=1:
   errors.append('native countertop source not retained '+key)
  if kind=='PH-BATH4' and any(o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL' for o in evidence):
   errors.append('311 incorrectly inherited separate 310 counter '+key)
  if kind in ('PH-BATH3','TX-BATH3'):
   if any(o.get('kind')=='tub' for o in evidence):errors.append('unselected Bath3 tub became 3D '+key)
   if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
    errors.append('unselected Bath3 PAN fabricated '+key)
  if kind=='TX-BATH4':
   if any(o.get('kind')=='tub' for o in evidence):
    errors.append('TX4 selected-but-UNLOCATED tub became 3D '+key)
   if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
    errors.append('TX4 imaginary PAN fabricated '+key)
  if kind=='PH-BATH4' and any(o.get('kind')=='tub' for o in evidence):
   errors.append('311 shower got invented tub '+key)
  if PHASE=='after':
   # R069 specific source-containment/provenance gates; note no fixture additions.
   if not any(o['category']=='ARCH_R069_SOURCE_NATIVE_LIGHT' for o in evidence):
    errors.append('R069 source-native wall visual treatment missing '+key)
   if kind!='PH-BATH4' and not any(o['category']=='ARCH_R069_BOUNDED_CASEWORK_LIGHT' for o in evidence):
    errors.append('R069 source-bounded countertop optical assembly missing '+key)
   for o in evidence:
    if o['category']=='ARCH_R069_BOUNDED_CASEWORK_LIGHT':
     if not o.get('r069_within_native_aabb'):errors.append('uncontained native-counter optical part '+key)
     c=arch['native_casework_proxies'][0];xx,zz=c['local_center_xz_ft']
     limit=[[xx-c['width_x_ft']/2,c['min_height_ft'],zz-c['depth_z_ft']/2],
      [xx+c['width_x_ft']/2,c['max_height_ft'],zz+c['depth_z_ft']/2]]
     bb=o.get('r069_world_mesh_aabb')
     if not bb or any(bb[0][ax]<limit[0][ax]-.006 or bb[1][ax]>limit[1][ax]+.006 for ax in range(3)):
      errors.append('native countertop optical mesh outside source XYZ '+key)
   if kind in ('PH-BATH3','TX-BATH3') and not any(o.get('r069_selected_ceramic_relief') for o in evidence):
    errors.append('R069 frozen Bath3 selected tile relief missing '+key)
  page.locator('#viewer-focus-iso').click()
  shot(key,'ISO')
  preset='ph4-311' if kind=='PH-BATH4' else 'r066-tx4-counter' if kind=='TX-BATH4' else 'r063-bath-finish'
  if PHASE=='after':
   page.locator('#viewer-focus-architectural' if kind in ('PH-BATH4','TX-BATH4') else '#viewer-focus-finish').click()
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
  if n.endswith('A') and kind in ('PH-BATH3','PH-BATH4'):
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
   'native_casework_ids':[x['id'] for x in arch.get('native_casework_proxies',[])],
   'native_door_ids':[x['id'] for x in arch.get('openings',[]) if x['kind']=='door'],
   'native_ceiling_source':bool(arch.get('native_ceiling_evidence')),
   'selected_3d_tub':bool(arch.get('selected_tub_proxy')),
   'modes':['full','study']+(['context'] if n.endswith('A') and kind in ('PH-BATH3','PH-BATH4') else [])}
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
contact.save(DEST/'R069_WET_BATHS_CONTACT_SHEET.png')
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
