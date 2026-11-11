"""R070 second coordinated porcelain assembly pass.
Only four source-program types and their eight mirrored A/B instances:
PH/TX WC and PH/TX selected Bath2. Actual standalone Chrome captures.
No picks rewrites, 26x3, 78-combination or legacy suites.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops,ImageStat
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[1]
PHASE=sys.argv[1] if len(sys.argv)>1 else 'after'
assert PHASE in ('before','after')
DEST=ROOT/'scratch/r070_fixture_continuity'/PHASE
DEST.mkdir(parents=True,exist_ok=True)
CASES=[('PH-WC','314A'),('PH-WC','314B'),('TX-WC','203A'),('TX-WC','203B'),
 ('PH-BATH2','305A'),('PH-BATH2','305B'),('TX-BATH2','205A'),('TX-BATH2','205B')]
EXPECTED='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d'
PICKS=ROOT/'deliverables/viewer3d/picks.json'
rooms={r['id']:r for r in json.loads(PICKS.read_text(encoding='utf8'))['rooms']}
errors=[];pictures=[];measure=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1480,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append('pageerror '+str(e)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-WC/314A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=48000)
 page.locator('#viewer-focus-enter').click()
 def photo(key,suffix):
  p=DEST/(key+'_'+suffix+'.png')
  page.locator('#stage').screenshot(path=str(p))
  pictures.append(p)
 for kind,n in CASES:
  key=kind+'_'+n
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',kind+'/'+n)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
  page.locator('#viewer-focus-iso').click()
  evidence=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  arch=next(x['architecture'] for x in rooms[kind]['physical_instances'] if x['room_number']==n)
  if not any(x['category']=='ARCH_REGISTERED_WALL' for x in evidence):
   errors.append('native source shell lost '+key)
  if any(x['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for x in evidence):
   errors.append('duplicate PAN '+key)
  if kind.endswith('-WC'):
   if any(x['category']=='ARCH_R070_WOOD_FLOOR_MICRORELIEF' for x in evidence):
    errors.append('inherited WC floor became wood '+key)
   if any(x['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL' for x in evidence):
    errors.append('unsourced WC countertop '+key)
   if not any(x.get('r067_wc_visual_piece')=='R067_ABSTRACT_UNDERSHELL' for x in evidence) and PHASE=='before':
    errors.append('precondition generic WC undershell missing '+key)
  else:
   if not arch.get('selected_tub_proxy'):
    errors.append('frozen selected bathtub source registration lost '+key)
   if not any(x.get('kind')=='tub' for x in evidence):
    errors.append('selected tub source-gated generic vessel missing '+key)
   if any(x.get('kind')=='shower-reference' for x in evidence):
    errors.append('Bath2 invented independent shower '+key)
  if PHASE=='after':
   if kind.endswith('-WC'):
    shell=[x for x in evidence if x.get('r070_ceramic_continuous_bowl')]
    if len(shell)!=1:errors.append('source-gated continuous generic WC body missing '+key)
    else:
     if shell[0].get('fixture_coordinate_certified') is not False:
      errors.append('WC installed source coordinate falsely certified '+key)
    if any(x.get('r067_wc_visual_piece')=='R067_ABSTRACT_UNDERSHELL' for x in evidence):
     errors.append('outdated disconnected WC spherical underbody remains '+key)
   else:
    inner=[x for x in evidence if x.get('r070_illustrative_tub_inner')]
    if len(inner)!=1:errors.append('generic selected tub inner porcelain missing '+key)
    else:
     if inner[0].get('actual_manufacturer_solid') is True:
      errors.append('nominal tub visualization falsely certified '+key)
  photo(key,'ISO')
  page.evaluate('(x)=>window.__viewerDebug.setCamera(x)',
   'r067-wc-survey' if kind.endswith('-WC') else 'r063-bath-finish')
  photo(key,'DETAIL')
  if PHASE=='after' and n.endswith('A'):
   page.locator('#viewer-focus-traces').click()
   page.locator('#viewer-focus-traces').click()
   page.locator('#viewer-focus-cutaway').click()
   page.locator('#viewer-focus-cutaway').click()
   if not page.evaluate('window.__viewerDebug.getState().interiorReveal'):
    errors.append('reversible cutaway failed '+key)
  if kind=='PH-BATH2' and n.endswith('A'):
   page.evaluate('window.__viewerDebug.setMode("study")')
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=18000)
   page.evaluate('window.__viewerDebug.setCamera("isometric")')
   photo(key,'WET_STUDY')
   page.evaluate('window.__viewerDebug.setMode("full")')
  if kind=='TX-WC' and n.endswith('A'):
   page.evaluate('window.__viewerDebug.setMode("context")')
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=18000)
   photo(key,'REVIT_CONTEXT')
   page.evaluate('window.__viewerDebug.setMode("full")')
 if page.evaluate('window.__viewerDebug.errors'):
  errors.append('runtime debug '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()
if PHASE=='after':
 for p in pictures:
  a=Image.open(DEST.parent/'before'/p.name).convert('RGB')
  b=Image.open(p).convert('RGB')
  # The single source-gated WC porcelain occupies fewer than 2% of the
  # large 1480x900 room view. Compare the actual visible fixture region,
  # not a dark-stage average; no position change or camera pan is allowed.
  box=(625,430,835,630) if '-WC_' in p.name else (530,395,940,730)
  diff=ImageStat.Stat(ImageChops.difference(a.crop(box),b.crop(box))).mean
  value=round(sum(diff)/3,3)
  measure.append([p.name,value])
  if p.name.endswith(('ISO.png','DETAIL.png')) and value<(.20 if '-WC_' in p.name else .60):
   errors.append('no visible ceramic model improvement '+p.name)
if hashlib.sha256(PICKS.read_bytes()).hexdigest()!=EXPECTED:
 errors.append('frozen picks changed')
report={'status':'PASS' if not errors else 'FIX','phase':PHASE,
 'cases':[x+'/'+n for x,n in CASES],
 'actual_chrome_captures':len(pictures),'errors':errors,
 'scene_roi_deltas':measure,'source_html_sha256':hashlib.sha256(
  (ROOT/'deliverables/viewer3d/index.html').read_bytes()).hexdigest(),
 'picks_sha256':hashlib.sha256(PICKS.read_bytes()).hexdigest()}
(DEST/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
