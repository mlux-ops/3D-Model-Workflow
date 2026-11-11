"""R069 focused corrective Chrome pass, no full 26 / 78 / legacy reruns.
Correct only 8 Wet Zone Study source finish views and 311A/B Focus camera
that failed first-pass visual completeness; preserve independent receipts.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from playwright.sync_api import sync_playwright
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'scratch/r069_focus/after'
BASE=ROOT/'scratch/r069_focus/before'
PICKS=ROOT/'deliverables/viewer3d/picks.json'
ROOMS=[('PH-BATH3','307A'),('PH-BATH3','307B'),
 ('TX-BATH3','207A'),('TX-BATH3','207B'),
 ('PH-BATH4','311A'),('PH-BATH4','311B'),
 ('TX-BATH4','007A'),('TX-BATH4','007B')]
FROZEN='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d'
assert hashlib.sha256(PICKS.read_bytes()).hexdigest()==FROZEN
errors=[];fixes=[];deltas=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1480,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda err:errors.append('pageerror '+str(err)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-BATH3/307A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=45000)
 page.locator('#viewer-focus-enter').click()
 for room,num in ROOMS:
  name=f'{room}_{num}'
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',room+'/'+num)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=23000)
  page.evaluate('window.__viewerDebug.setMode("study")')
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=23000)
  page.evaluate('window.__viewerDebug.setCamera("isometric")')
  e=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  shown=[o for o in e if o['category']=='ARCH_R069_DRAWING_WET_STUDY_DEPTH']
  original=[o for o in e if o['category']=='sourceWall']
  if len(shown)!=len(original) or len(shown)<1:
   errors.append('study source material optical child missing '+name)
  path=DEST/(name+'_WET_STUDY.png')
  page.locator('#stage').screenshot(path=str(path))
  a=Image.open(BASE/path.name).convert('RGB');b=Image.open(path).convert('RGB')
  delta=round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
  deltas.append([path.name,delta])
  if delta<.25:errors.append('study appearance still visually unchanged '+name)
  fixes.append(name+' wet-study '+str(len(shown))+' source-plane children')
  if room=='PH-BATH4':
   page.evaluate('window.__viewerDebug.setMode("full")')
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=23000)
   page.evaluate('window.__viewerDebug.setCamera("ph4-311")')
   if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='ph4-311':
    errors.append('311 detail camera preset not retained '+name)
   path=DEST/(name+'_DETAIL.png')
   page.locator('#stage').screenshot(path=str(path))
   fixes.append(name+' source-wall 311 exterior Focus camera')
 if page.evaluate('window.__viewerDebug.errors'):
  errors.append('runtime errors '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

result=json.loads((DEST/'RESULT.json').read_text(encoding='utf8'))
# A targeted corrective regression supersedes only the 8 physically recaptured
# Wet study PNGs and 2 311 camera detail PNGs, not the earlier 8/26 test cases.
first_errors=result['errors']
assert all(x.startswith('no visual change ') for x in first_errors),first_errors
result['errors']=errors
result['status']='PASS' if not errors else 'FIX'
result['targeted_correction']={
 'purpose':'source-dimensioned wet material lighting and 311A/B upper wall framing',
 'retested_captures':len(fixes),'retested_study_cases':len(ROOMS),
 'wet_study_deltas':deltas,'error_before':first_errors,
 'source_tile_or_plumbing_selection_changed':False,
 'full_26_or_78_suite_run':False,'snapshot_type':'actual local Chrome screenshots'}
for f,d in deltas:
 for existing in result['visual_deltas']:
  if existing[0]==f:existing[1]=d
result['source_after_html_sha256']=hashlib.sha256(
 (ROOT/'deliverables/viewer3d/index.html').read_bytes()).hexdigest()
(DEST/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:result[k] for k in ('status','errors','targeted_correction','picks_sha256')},indent=2))
if errors:raise SystemExit(1)
