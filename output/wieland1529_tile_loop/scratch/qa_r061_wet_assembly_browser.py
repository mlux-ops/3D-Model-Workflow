"""Viewer-only R061 Chrome source/scene QA. Capture true offline file:// viewport.
R061 checks real native wall-supported W2/W3, original frozen programs,
26 cases, 78 modes, A/B focus screenshots, controls and source appearance.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUT=ROOT/'scratch/r061_wet_assembly_gallery';OUT.mkdir(exist_ok=True)
BEFORE=ROOT/'scratch/r061_before'
FOCUS=('PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3')
errors=[];cases=[];photos=[];wetReturnRows=[];modeProbes=0;viewChecks=0;compareChecks=0

def items(ev,c):return [x for x in ev if x['category']==c]
def err(label):errors.append(label)

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append('JS:'+str(e)))
 page.goto(URL+'#PH-BATH2/305A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for room in DATA['rooms']:
  for inst in room['physical_instances']:
   key=room['id']+'/'+inst['room_number'];a=inst.get('architecture') or {}
   page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   st=page.evaluate('window.__viewerDebug.getState()')
   if not inst.get('r061_visualization') or inst['r061_visualization']['physical_instance']!=inst['room_number']:
    err('R061 provenance:'+key)
   if st['mode']!='full' or st['sourceTraces'] or not st['interiorReveal']:
    err('default viewer controls:'+key)
   if not items(ev,'ARCH_REGISTERED_FLOOR'):err('native-registered room floor:'+key)
   if room['id']!='PH-BATH4' and any(x['native_host_face_id'] not in a.get('native_wall_ids',[]) or
      x['source_return_supported'] is not True or x['derived_return_not_partition'] is not True or
      not x['native_host_face_receipt'] for x in items(ev,'FULL_ROOM_WET_WALL')
      if x['wall'] in ('W2','W3')):
    err('unattributed 3D return not gated to actual source wall:'+key)
   if room['id'] in ('PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3'):
    returns=[x for x in items(ev,'FULL_ROOM_WET_WALL') if x['wall'] in ('W2','W3')]
    if room['id']=='TX-BATH2' and len(returns)!=2:
     err('TX2 native shortened host W1 centered incorrectly; actual two source side returns hidden:'+key)
    wetReturnRows.append({'type':room['id'],'physical':inst['room_number'],
      'source_wall_supported_return_ids':[x['native_host_face_id'] for x in returns],
      'visible_return_count':len(returns),
      'no_pan':room['program']['pan_selected'] is not True})
    if room['id']=='PH-BATH2':
     if not items(ev,'PLAN_SCHEMATIC_FIXTURE') or not any(x['fixture_model']=='700332000000090' for x in items(ev,'PLAN_SCHEMATIC_FIXTURE')):
      err('PH2 tub selected existing placement lost:'+key)
     w1=[x for x in items(ev,'FULL_ROOM_WET_WALL') if x['wall']=='W1']
     if len(w1)!=1 or abs(w1[0]['rendered_cutaway_height_ft']-.72)>.005:
      err('PH2 front W1 0.72ft reversible section lost:'+key)
     if any(abs(x['review_return_full_height_ft']-x['full_specification_height_ft'])>.005 for x in returns):
      err('PH2 sourced original returned full height lost:'+key)
     if not any(x['review_return_section_only'] for x in returns):
      err('PH2 camera-facing finished return floating beyond cut host:'+key)
    if room['program']['kind']=='TUB_OR_WALK_IN_UNSELECTED':
     if any(x['visible'] for x in items(ev,'ARCH_R061_UNSELECTED_PLAN_LABEL')):
      err('unselected reference black floor placard leaked into normal view:'+key)
     if any(x['fixture_visual_classification']=='NOMINAL_SELECTED_TUB_HOLLOW_GENERIC' for x in ev):
      err('conditional drawing reference turned into selected 3D tub:'+key)
    if items(ev,'FULL_ROOM_SELECTED_PAN_SCHEMATIC'):
     err('selected tub or conditional bathing scene invented extra PAN:'+key)
    photo=OUT/(room['id']+'_'+inst['room_number']+'_R061.png')
    page.screenshot(path=str(photo));photos.append(photo)
    page.locator('#viewer-camera-wet').click()
    if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='wet':
     err('wet camera:'+key)
    page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_WET.png')))
    viewChecks+=1
    if room['id']=='PH-BATH2':
     restored=items(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW')
     if len(restored)!=3 or not all(x['visible'] for x in restored):
      err('PH2 R059 full wet review counterparts lost:'+key)
    page.locator('#viewer-compare-ab').click()
    if page.locator('#viewer-ab-drawer').get_attribute('hidden') is not None:
     err('AB comparison not visible:'+key)
    page.locator('#viewer-compare-ab').click()
    compareChecks+=1
    page.locator('#viewer-reveal-interior').click()
    if any(x['review_cutaway_only'] for x in items(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_REGISTERED_WALL')):
     err('wall sectional cutaway did not fully restore:'+key)
    page.locator('#viewer-reveal-interior').click()
    page.locator('#viewer-ceiling-preview').click()
    if a.get('native_ceiling_evidence') and not any(x['visible'] for x in items(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_R059_DERIVED_GWB_CEILING_CANOPY')):
     err('source ceiling optional preview:'+key)
    page.locator('#viewer-ceiling-preview').click()
    page.locator('#viewer-toggle-source-traces').click()
    if room['program']['kind']=='TUB_OR_WALK_IN_UNSELECTED' and not all(x['visible'] for x in items(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_R061_UNSELECTED_PLAN_LABEL')):
     err('source-only plan placard toggle:'+key)
    page.locator('#viewer-toggle-source-traces').click()
    page.locator('#viewer-camera-iso').click()
   for mode in ('study','context'):
    page.evaluate('(v)=>window.__viewerDebug.setMode(v)',mode)
    if page.evaluate('window.__viewerDebug.getState().mode')!=mode:err('mode:'+key+'/'+mode)
    modeProbes+=1
   cases.append(key)
 # Explicit offline deep link and rapid cache/texture readiness.
 page.goto(URL+'#TX-BATH3/207B',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 if page.evaluate('window.__viewerDebug.getState().room')!='TX-BATH3' or page.evaluate('document.body.dataset.viewerInstance')!='207B':
  err('physical instance deep link')
 for n in ['PH-BATH2/305A','TX-BATH2/205B','PH-BATH3/307B','TX-BATH3/207A','PH-POWDER/405A','TX-POWDER2/010B']:
  page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',n)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
 if page.evaluate('window.__viewerDebug.errors.length'):
  err('runtime material/cache:'+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

if photos:
 sheet=Image.new('RGB',(4*600,2*435),(17,27,36));d=ImageDraw.Draw(sheet)
 for i,f in enumerate(photos):
  im=Image.open(f).convert('RGB'); im.thumbnail((590,400));x=(i%4)*600;y=(i//4)*435
  sheet.paste(im,(x,y+20));d.text((x+8,y+4),f.stem,fill='white')
  prev=BEFORE/(f.stem.replace('_R061','_R060')+'.png')
  if prev.exists():
   old=Image.open(prev).convert('RGB').resize(Image.open(f).size)
   delta=ImageChops.difference(old,Image.open(f).convert('RGB'))
   if max(ImageStat.Stat(delta).mean)<2:err('no visible R061 difference:'+f.stem)
 sheet.save(OUT/'R061_EIGHT_AB_AFTER_CONTACT.png')
receipt={'status':'PASS' if not errors else 'FIX','instances':len(cases),
 'mode_probes':len(cases)+modeProbes,'focus_captures':len(photos),
 'wet_camera_checks':viewChecks,'ab_checks':compareChecks,
 'returns':wetReturnRows,'errors':errors}
(ROOT/'scratch/r061_wet_assembly_browser_result.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in receipt.items() if k!='returns'},indent=2))
print('RETURN SOURCE STATUS:',json.dumps(wetReturnRows))
if errors or len(cases)!=26 or len(photos)!=8 or len(cases)+modeProbes!=78:raise SystemExit(1)
