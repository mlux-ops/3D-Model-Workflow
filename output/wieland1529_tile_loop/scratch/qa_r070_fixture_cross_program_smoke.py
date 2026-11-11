"""Tiny cross-program shared ceramic renderer regression, three instances.
Not a full-room/26/78 suite; source no-pick and UNLOCATED hard gates prevail.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'scratch/r070_fixture_continuity/after'
PICKS=ROOT/'deliverables/viewer3d/picks.json'
ROOMS={r['id']:r for r in json.loads(PICKS.read_text(encoding='utf8'))['rooms']}
CASES=[('PH-PRIMARY','304A'),('PH-BATH3','307A'),('TX-BATH4','007A')]
errors=[];captured=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1480,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda err:errors.append('browser pageerror '+str(err)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-PRIMARY/304A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=48000)
 page.locator('#viewer-focus-enter').click()
 for kind,num in CASES:
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',kind+'/'+num)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=25000)
  e=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  toilets=[x for x in e if x.get('kind')=='toilet']
  if any(x.get('r067_wc_visual_piece')=='R067_ABSTRACT_UNDERSHELL' for x in toilets):
   errors.append('disconnected old generic porcelain underbody persisted '+kind)
  for x in toilets:
   if x.get('r067_wc_visual_piece')=='R070_CONTINUOUS_CERAMIC_SHELL' and not x.get('r070_ceramic_continuous_bowl'):
    errors.append('new continuous ceramic provenance absent '+kind)
  if any(x.get('actual_manufacturer_solid') is True for x in toilets):
   errors.append('generic porcelain mis-certified manufacturer solid '+kind)
  if kind=='PH-PRIMARY':
   if any(x.get('kind')=='shower-reference' for x in e):
    errors.append('primary installed unlocated shower fabricated')
  elif kind=='PH-BATH3':
   if any(x.get('kind')=='tub' for x in e):
    errors.append('Bath3 unselected installed tub fabricated')
  elif kind=='TX-BATH4':
   if any(x.get('kind')=='tub' for x in e):
    errors.append('TX4 3D UNLOCATED selected tub incorrectly installed')
  if any(x['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' and kind!='TX-BATH4' for x in e):
   errors.append('unsupported new selected PAN '+kind)
  page.locator('#viewer-focus-iso').click()
  name='R070_SHARED_CERAMIC_'+kind+'_'+num+'.png'
  page.locator('#stage').screenshot(path=str(DEST/name))
  captured.append(name)
 if page.evaluate('window.__viewerDebug.errors'):
  errors.append('viewer debug errors '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()
sha=hashlib.sha256(PICKS.read_bytes()).hexdigest()
if sha!='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d':
 errors.append('frozen picks SHA changed')
result={'status':'PASS' if not errors else 'FIX','cases':[x+'/'+n for x,n in CASES],
 'actual_chrome_photos':captured,'errors':errors,
 'picks_sha256':sha,'source_html_sha256':hashlib.sha256(
  (ROOT/'deliverables/viewer3d/index.html').read_bytes()).hexdigest()}
(DEST/'R070_CROSS_PROGRAM_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
if errors:raise SystemExit(1)
