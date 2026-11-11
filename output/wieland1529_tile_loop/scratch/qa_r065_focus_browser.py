"""Fast Chrome SOURCE-VIEW QA for R065; eight targeted A/B Bath2/3 instances only.

Run twice: --phase before before editing; --phase after after rebuilding.
No new room/fixture evidence assumed; preserves and verifies picks hash.
"""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image, ImageDraw, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

P=argparse.ArgumentParser();P.add_argument('--phase',choices=['before','after'],required=True)
args=P.parse_args()
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/r065_focus' / args.phase;OUT.mkdir(parents=True,exist_ok=True)
PICKS=ROOT/'deliverables/viewer3d/picks.json'
HASH=hashlib.sha256(PICKS.read_bytes()).hexdigest()
DATA=json.loads(PICKS.read_text(encoding='utf8'))
ROOMS={r['id']:r for r in DATA['rooms']}
CASES=[('PH-BATH2','305A'),('PH-BATH2','305B'),
       ('PH-BATH3','307A'),('PH-BATH3','307B'),
       ('TX-BATH2','205A'),('TX-BATH2','205B'),
       ('TX-BATH3','207A'),('TX-BATH3','207B')]
errors=[];checks=[];pictures=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1550,'height':960},device_scale_factor=1)
 page.on('pageerror',lambda err:errors.append(str(err)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-BATH2/305A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=30000)
 page.locator('#viewer-focus-enter').click()
 for kind,n in CASES:
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',kind+'/'+n)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
  page.wait_for_timeout(75)
  if page.evaluate('document.body.dataset.viewerInstance')!=n:
   errors.append('deep link wrong: '+kind+'/'+n)
  if not page.evaluate('window.__viewerDebug.getState().focusView'):
   errors.append('Focus dropped: '+kind+'/'+n)
  ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  wall=[x for x in ev if x['category']=='ARCH_REGISTERED_WALL']
  wet=[x for x in ev if x['category']=='FULL_ROOM_WET_WALL']
  if len(wall)<2 or not wet:errors.append('lost source enclosure/tile: '+kind+'/'+n)
  if args.phase=='after':
   for x in wall:
    if not x.get('r065_neutral_plaster_display_only') or not x.get('r065_plaster_microtexture'):
     errors.append('uncertified or absent native-wall PBR: '+kind+'/'+n)
   for name in ('ARCH_FLOOR_FACE_OUTLINE','ARCH_CEILING_EXTENT_DATUM','ARCH_INFERRED_ROOM_VERTICAL_WIRES'):
    if any(x['visible'] for x in ev if x['category']==name):
     errors.append('analytical wire obscures Focus: '+kind+'/'+n+':'+name)
   if not any(x.get('r065_wet_host_photo_reveal') for x in wall):
    errors.append('source-registered selected wet host not optically revealed: '+kind+'/'+n)
   if page.locator('#viewer-focus-finish').is_hidden():
    errors.append('source finish camera inaccessible: '+kind+'/'+n)
   if page.locator('#viewer-focus-cutaway').is_hidden():
    errors.append('reversible native wall section button missing: '+kind+'/'+n)
  page.locator('#viewer-focus-iso').click()
  base=OUT/(kind+'_'+n+'_ISO.png');page.locator('#stage').screenshot(path=str(base))
  pictures.append(base)
  if args.phase=='after':page.locator('#viewer-focus-finish').click()
  else:page.evaluate('window.__viewerDebug.setCamera("r063-bath-finish")')
  photo=OUT/(kind+'_'+n+'_FINISH.png');page.locator('#stage').screenshot(path=str(photo))
  if args.phase=='after':
   if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='r063-bath-finish':
    errors.append('finish camera wrong: '+kind+'/'+n)
   if n.endswith('A'):
    # Selected source tile remains.  Toggle study/compare and return; no new
    # physical fixtures/pans allowed in original unresolved choices.
    if kind in ('PH-BATH3','TX-BATH3') and any(x['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for x in ev):
     errors.append('conditional selected PAN fabricated: '+kind+'/'+n)
    page.locator('#viewer-focus-traces').click()
    trace=page.evaluate('window.__viewerDebug.getSceneEvidence()')
    if not any(x['category']=='ARCH_FLOOR_FACE_OUTLINE' and x['visible'] for x in trace):
     errors.append('source evidence not restored in Focus: '+kind+'/'+n)
    if any(x.get('r065_wet_host_photo_reveal') for x in trace if x['category']=='ARCH_REGISTERED_WALL'):
     errors.append('native wet hosts not restored to original source opacity: '+kind+'/'+n)
    page.locator('#viewer-focus-traces').click()
    page.locator('#viewer-focus-cutaway').click()
    if page.evaluate('window.__viewerDebug.getState().interiorReveal'):
     errors.append('section off toggle failed:'+kind+'/'+n)
    page.locator('#viewer-focus-cutaway').click()
    if not page.evaluate('window.__viewerDebug.getState().interiorReveal'):
     errors.append('section restoration failed:'+kind+'/'+n)
    page.locator('#viewer-focus-ab').click()
    if not page.locator('#viewer-ab-drawer').is_visible():
     errors.append('source A/B compare drawer not visible:'+kind+'/'+n)
    page.locator('#viewer-focus-ab').click()
    checks.append(kind+'/'+n+' finish/source/section/A-B controls')
 if args.phase=='after':
  page.locator('#viewer-focus-evidence').click()
  if page.evaluate('window.__viewerDebug.getState().focusView'):
   errors.append('evidence exit did not restore full inspector')
  if not page.locator('#viewer-v2-evidence').evaluate('(el)=>el.open'):
   errors.append('evidence inspector still closed')
  if page.evaluate('window.__viewerDebug.errors'):
   errors.append('browser runtime: '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

sheet=Image.new('RGB',(4*620,2*415),(20,29,38));draw=ImageDraw.Draw(sheet)
for i,f in enumerate(pictures):
 im=Image.open(f).convert('RGB'); im.thumbnail((610,385));x=(i%4)*620;y=(i//4)*415
 sheet.paste(im,(x,y+24));draw.text((x+8,y+5),f.stem,fill='white')
sheet.save(OUT/'R065_EIGHT_AB_FOCUS_CONTACT.png')
if args.phase=='after':
 prior=OUT.parent/'before';deltas=[]
 for key,n in CASES:
  new=Image.open(OUT/(key+'_'+n+'_FINISH.png')).convert('RGB')
  old=Image.open(prior/(key+'_'+n+'_FINISH.png')).convert('RGB')
  delta=ImageStat.Stat(ImageChops.difference(old,new)).mean
  deltas.append({'key':key+'/'+n,'average_delta':round(sum(delta)/3,3)})
  if sum(delta)/3<.6:errors.append('no actual visible improvement: '+key+'/'+n)
else:deltas=[]
if HASH!=hashlib.sha256(PICKS.read_bytes()).hexdigest():errors.append('frozen picks bytes changed during QA')
receipt={'status':'PASS' if not errors else 'FIX','phase':args.phase,
 'physical_instances':[x+'/'+n for x,n in CASES],
 'focus_captures':len(pictures),'picks_sha256':HASH,
 'delta_vs_before':deltas,'checks':checks,'errors':errors}
(OUT/'RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(receipt,indent=2))
if errors:raise SystemExit(1)
