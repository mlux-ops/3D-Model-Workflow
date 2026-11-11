"""R070 standalone visual source review; no 26x3, 78 or legacy suites.
Usage: python -B scratch/qa_r070_dry_baths_browser.py before|after
Four compact dry-room types, actual A/B; Focus Full ISO and detail, source Wet Study,
and two A-instance Revit Context checks with physical PNG contact sheet.
"""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageChops,ImageStat,ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PHASE=sys.argv[1] if len(sys.argv)>1 else 'after'
assert PHASE in ('before','after')
DEST=ROOT/'scratch/r070_focus'/PHASE
DEST.mkdir(parents=True,exist_ok=True)
CASES=[('PH-POWDER','405A'),('PH-POWDER','405B'),
 ('TX-POWDER','102A'),('TX-POWDER','102B'),
 ('TX-POWDER2','010A'),('TX-POWDER2','010B'),
 ('PH-WC','314A'),('PH-WC','314B')]
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
  if kind!='PH-WC' and len([o for o in evidence if o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL'])!=1:
   errors.append('native Countertop missing '+key)
  if kind=='PH-WC' and any(o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL' for o in evidence):
   errors.append('fabricated WC Countertop '+key)
  if kind in ('PH-POWDER','TX-POWDER','TX-POWDER2') and not any(o['category']=='ARCH_REGISTERED_FLOOR' for o in evidence):
   errors.append('retained wood floor source footprint missing '+key)
  if kind=='PH-WC' and any(o['category']=='ARCH_NATIVE_UNSELECTED_PLUMBING_LOCATOR' for o in evidence):
   errors.append('WC fictitious sink source '+key)
  if PHASE=='after':
   if not any(o['category']=='ARCH_R070_PLASTER_FACE_STUDY' for o in evidence):
    errors.append('R070 native plaster wall optical depth missing '+key)
   if kind!='PH-WC' and not any(o['category']=='ARCH_R070_WOOD_FLOOR_MICRORELIEF' for o in evidence):
    errors.append('R070 retained wood floor relief missing '+key)
   if kind!='PH-WC':
    for o in evidence:
     if o['category']=='ARCH_R070_NATIVE_COUNTER_SURFACE_STUDY' and not o.get('r070_native_counter_contained'):
      errors.append('R070 countertop not contained '+key)
   if not any(o['category']=='ARCH_R070_CORNER_DEPTH_STUDY' for o in evidence):
    errors.append('R070 source wall return depth missing '+key)
  page.locator('#viewer-focus-iso').click()
  shot(key,'ISO')
  preset='r067-wc-survey' if kind=='PH-WC' else 'r067-powder-survey'
  if PHASE=='after':
   page.evaluate('(x)=>window.__viewerDebug.setCamera(x)',preset)
  else:
   page.evaluate('(x)=>window.__viewerDebug.setCamera(x)',preset)
  if PHASE=='after' and page.evaluate('window.__viewerDebug.getCameraInfo().preset')!=preset:
   errors.append('wrong detail preset '+key)
  shot(key,'DETAIL')
  page.evaluate('window.__viewerDebug.setMode("study")')
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
  page.evaluate('window.__viewerDebug.setCamera("isometric")')
  shot(key,'WET_STUDY')
  if PHASE=='after' and kind!='PH-WC' and not any(o['category']=='sourceWall' for o in page.evaluate('window.__viewerDebug.getSceneEvidence()')):
   errors.append('Wet mode source wall lost '+key)
  if n.endswith('A') and kind in ('PH-POWDER','TX-POWDER2'):
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
   'modes':['full','study']+(['context'] if n.endswith('A') and kind in ('PH-POWDER','TX-POWDER2') else [])}
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
contact.save(DEST/'R070_WET_BATHS_CONTACT_SHEET.png')
deltas=[]
if PHASE=='after':
 for k,n in CASES:
  for suffix in ('ISO','DETAIL','WET_STUDY'):
   f=k+'_'+n+'_'+suffix+'.png'
   a=Image.open(DEST.parent/'before'/f).convert('RGB')
   b=Image.open(DEST/f).convert('RGB')
   delta=round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
   deltas.append((f,delta))
   # Source-protected no-pick: PH-WC has no W1 (0 modeled wet walls), and
   # TX-POWDER has a neutral/no-selected-tile wall. Visual invariance here
   # is a correctness criterion, not an unmet requirement to fabricate tile.
   if delta<.25 and not (suffix=='WET_STUDY' and k in ('PH-WC','TX-POWDER')):
    errors.append('no visual change '+f)
if hashlib.sha256(PICKS.read_bytes()).hexdigest()!=EXPECTED_SHA:errors.append('frozen picks changed')
result={'status':'PASS' if not errors else 'FIX','phase':PHASE,
 'focus_cases':[k+'/'+n for k,n in CASES],'errors':errors,'interactions':interaction,
 'picks_sha256':hashlib.sha256(PICKS.read_bytes()).hexdigest(),
 'source_receipts':record,'visual_deltas':deltas,
 'physical_capture_count':len(shots)}
(DEST/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='source_receipts'},indent=2))
if errors:raise SystemExit(1)
