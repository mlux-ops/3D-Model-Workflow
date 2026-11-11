"""R062 source-constrained native primary architecture and physical offline Chrome QA.

This checks read-only source category AABBs and drawing-projected geometry, NOT
native Room membership, installed shower positions, finish approvals or family solids.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageChops, ImageDraw, ImageStat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUT=ROOT/'scratch/r062_primary_arch_gallery';OUT.mkdir(exist_ok=True)
BASE=ROOT/'scratch/r062_before'
FOCUS=('PH-PRIMARY','TX-PRIMARY','PH-BATH4','TX-BATH4')
errors=[];cases=[];photos=[];dataRows=[];modeProbes=0;cameraChecks=0
compareChecks=0;nativeRevealObjects=0

def objects(evidence,category):return [x for x in evidence if x['category']==category]
def issue(msg):errors.append(msg)
def moving(a,b):return sum(abs(x-y) for x,y in zip(a,b))

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
   args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
 page.on('pageerror',lambda e:issue('JS:'+str(e)))
 page.goto(URL+'#PH-PRIMARY/304A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for room in DATA['rooms']:
  for inst in room['physical_instances']:
   key=room['id']+'/'+inst['room_number'];a=inst.get('architecture') or {}
   page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   st=page.evaluate('window.__viewerDebug.getState()')
   if not inst.get('r062_visualization') or inst['r062_visualization']['physical_instance']!=inst['room_number']:
    issue('R062 generated per-instance provenance missing:'+key)
   if st['mode']!='full' or st['sourceTraces'] or not st['interiorReveal']:
    issue('default source-visibility state:'+key)
   if not objects(ev,'ARCH_REGISTERED_FLOOR'):
    issue('source-derived floor geometry missing:'+key)
   reveals=objects(ev,'ARCH_R062_NATIVE_HOST_REVEAL_VISUAL')
   nativeRevealObjects+=len(reveals)
   for v in reveals:
    if (not v['host_id'] in a.get('native_wall_ids',[]) and room['id']!='PH-BATH4') or not v['receipt_id'] or \
       v['not_swing_or_rough_opening'] is not True or v['source_bounded_display_only'] is not True or \
       not v['native_host_thickness_ft'] or not v['rendered_width_ft']:
     issue('native hosted wall thickness/receipt/reveal misattribution:'+key+':'+str(v))
   if any(x['category']=='ARCH_R062_NATIVE_HOST_REVEAL_VISUAL' and
      (not x['review_reveal_part'] in ('JAMB_STATION_A','JAMB_STATION_B','WALL_HEAD_UNDERSIDE','WALL_SILL_RETURN')) for x in ev):
    issue('unsupported source-opening family part:'+key)
   if room['id'] in FOCUS:
    file=OUT/(room['id']+'_'+inst['room_number']+'_R062.png')
    page.screenshot(path=str(file));photos.append(file)
    if room['id'] in ('PH-PRIMARY','TX-PRIMARY'):
     program=room['program']
     if program['kind']!='PRIMARY_WALK_IN_LINEAR' or program['pan_selected'] or '48-inch LINEAR' not in program['plumbing_truth']:
      issue('primary frozen walk-in or factory-solid 48in LINEAR program modified:'+key)
     if objects(ev,'FULL_ROOM_SELECTED_PAN_SCHEMATIC') or objects(ev,'ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY'):
      issue('fabricated primary pan or unsupported lavatory:'+key)
     if objects(ev,'FULL_ROOM_WET_WALL'):
      issue('unverified primary walk-in installed 3D wet planes still drawn:'+key)
     if len(objects(ev,'ARCH_NATIVE_COUNTERTOP_VISUAL'))!=1 or len(objects(ev,'ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL'))!=1 or \
       len(objects(ev,'ARCH_R062_NATIVE_BOUND_VANITY_END_STUDY'))!=2 or \
       len(objects(ev,'ARCH_R062_NATIVE_BOUND_VANITY_UNDERSIDE_STUDY'))!=1:
      issue('native bounded dimensional primary vanity is incomplete:'+key)
     counter=a['native_casework_proxies'][0]
     for v in objects(ev,'ARCH_R062_NATIVE_BOUND_VANITY_END_STUDY')+objects(ev,'ARCH_R062_NATIVE_BOUND_VANITY_UNDERSIDE_STUDY'):
      if v['contained_within_native_category_aabb_xyz'] is not True or v['revit_id']!=counter['id']:
       issue('native source AABB contained vanity metadata invalid:'+key)
      if v['source_bound_height_min_ft']<counter['min_height_ft']-.005 or \
        v['source_bound_height_max_ft']>counter['max_height_ft']+.005:
       issue('native bounding vertical envelope moved:'+key)
     traces=objects(ev,'ARCH_R062_PRIMARY_WET_UNLOCATED_PLAN_TRACE')
     if len(traces)!=1 or traces[0]['visible'] or traces[0]['not_installed_shower'] is not True or \
       traces[0]['selected_48in_drain_center'] is not None:
      issue('source-only primary wet spatial gate/marker incorrect:'+key)
     if not any(x['primary_source_only'] and not x['visible'] for x in objects(ev,'PLAN_SCHEMATIC_FIXTURE')):
      issue('generic primary shower physical floor symbol not suppressed:'+key)
     t=traces[0] if traces else {}
     if t.get('classification')!='PRIMARY_WET_3D_UNLOCATED_SOURCE_CONFLICT':
      issue('source-conflicting projected primary shower missing UNLOCATED classification:'+key+':'+str(t.get('classification')))
     if room['id']=='PH-PRIMARY' and not (t.get('counter_overlap_sf') or 0)>0.15:
      issue('source-native PH long vanity / wet footprint conflict missed:'+key)
     if room['id']=='TX-PRIMARY' and not t.get('hosted_entry_conflicts'):
      issue('source-native TX hosted entry / wet footprint conflict missed:'+key)
     if page.locator('#viewer-r062-primary-vanity').is_hidden() or page.locator('#viewer-r062-primary-shell').is_hidden():
      issue('primary source target cameras not accessible:'+key)
     page.locator('#viewer-r062-primary-vanity').click()
     if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='r062-primary-vanity':
      issue('native source primary vanity camera not selected:'+key)
     page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_VANITY.png')))
     page.locator('#viewer-r062-primary-shell').click()
     if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='r062-primary-shell':
      issue('source wall/step enclosure camera not selected:'+key)
     page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_SHELL.png')))
     cameraChecks+=2
     page.locator('#viewer-toggle-source-traces').click()
     traceNow=objects(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_R062_PRIMARY_WET_UNLOCATED_PLAN_TRACE')
     if not traceNow or not all(x['visible'] for x in traceNow):
      issue('2D primary source trace not restored by toggle:'+key)
     page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_TRACES.png')))
     page.locator('#viewer-toggle-source-traces').click()
     page.locator('#viewer-camera-iso').click()
     if page.locator('#viewer-v2-evidence').is_hidden():
      issue('source confidence inspector unavailable:'+key)
     page.locator('#viewer-v2-evidence summary').click()
     if 'R062 SELECTED PRIMARY WALK-IN' not in page.locator('#viewer-evidence-content').inner_text():
      issue('source conflict and fixture uncertainty absent from inspector:'+key)
     page.locator('#viewer-v2-evidence summary').click()
     page.locator('#viewer-ceiling-preview').click()
     nativeCeil=objects(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_R059_DERIVED_GWB_CEILING_CANOPY')
     if a.get('native_ceiling_evidence') and not any(x['visible'] for x in nativeCeil):
      issue('documented native underside preview not shown:'+key)
     if not a.get('native_ceiling_evidence') and any(x['visible'] for x in nativeCeil):
      issue('unsourced native ceiling was fabricated:'+key)
     page.locator('#viewer-ceiling-preview').click()
     page.locator('#viewer-reveal-interior').click()
     if any(x['review_cutaway_only'] for x in objects(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_REGISTERED_WALL')):
      issue('camera-facing visual wall section did not restore:'+key)
     page.locator('#viewer-reveal-interior').click()
     page.locator('#viewer-compare-ab').click()
     if page.locator('#viewer-ab-drawer').get_attribute('hidden') is not None:
      issue('native source A/B comparison unavailable:'+key)
     page.locator('#viewer-compare-ab').click()
     compareChecks+=1
    elif room['id']=='TX-BATH4':
     if not a.get('selected_tub_unlocated_reason') or \
        any(x['fixture_visual_classification']=='NOMINAL_SELECTED_TUB_HOLLOW_GENERIC' for x in ev):
      issue('TX4 protected selected Duravit 3D UNLOCATED gate regressed:'+key)
    elif room['id']=='PH-BATH4':
     if not any(x['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for x in ev):
      issue('PH4 original selected POINT PAN visual missing:'+key)
    dataRows.append({'type':room['id'],'physical':inst['room_number'],
      'primary_wet_status':objects(ev,'ARCH_R062_PRIMARY_WET_UNLOCATED_PLAN_TRACE')[0]['classification']
       if room['id'] in ('PH-PRIMARY','TX-PRIMARY') else None,
      'source_wall_reveals':len(reveals),
      'source_bound_countertops':len(objects(ev,'ARCH_NATIVE_COUNTERTOP_VISUAL')),
      'native_ceiling_matched':bool(a.get('native_ceiling_evidence'))})
   for mode in ('study','context'):
    page.evaluate('(v)=>window.__viewerDebug.setMode(v)',mode)
    if page.evaluate('window.__viewerDebug.getState().mode')!=mode:
     issue('room mode failed:'+key+'/'+mode)
    if mode=='context' and any(x['category']=='ARCH_R062_NATIVE_BOUND_VANITY_END_STUDY'
       for x in page.evaluate('window.__viewerDebug.getSceneEvidence()')):
     issue('Full-only illustrative casework leaked into native Revit context:'+key)
    modeProbes+=1
   cases.append(key)
 # Test actual browser mouse interaction on a primary exterior view, not a decorative toggle.
 page.goto(URL+'#PH-PRIMARY/304B',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
 initial=page.evaluate('window.__viewerDebug.getCameraInfo()')
 page.mouse.move(760,625);page.mouse.down();page.mouse.move(920,700,steps=8);page.mouse.up()
 page.wait_for_timeout(280)
 rotated=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if moving(initial['position'],rotated['position'])<.02:
  issue('physical mouse orbit did not change 3D camera')
 page.mouse.wheel(0,-350);page.wait_for_timeout(210)
 zoomed=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if moving(rotated['position'],zoomed['position'])<.02:
  issue('physical mouse zoom did not change camera')
 page.mouse.move(770,630);page.mouse.down(button='right');page.mouse.move(850,670,steps=6);page.mouse.up(button='right')
 page.wait_for_timeout(210)
 panned=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if moving(zoomed['target'],panned['target'])<.02:
  issue('physical mouse pan did not change target')
 page.locator('#reset').click()
 restored=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if moving(restored['position'],initial['position'])>.15:
  issue('reset view failed to restore source camera')
 # Deep links and rapid offline image readiness after mixed picked/no-pick switches.
 for key in ('TX-PRIMARY/202B','PH-PRIMARY/304A','PH-BATH4/311B',
  'TX-BATH4/007A','TX-BATH2/205B','TX-POWDER/102B','PH-POWDER/405A'):
  page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',key)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
  if page.evaluate('document.body.dataset.viewerInstance')!=key.split('/')[1]:
   issue('offline rapid physical instance switch failed:'+key)
 if page.evaluate('window.__viewerDebug.errors.length'):
  issue('Three.js/runtime errors:'+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

contact=Image.new('RGB',(4*620,2*460),(19,28,37));d=ImageDraw.Draw(contact)
for j,f in enumerate(photos):
 im=Image.open(f).convert('RGB');im.thumbnail((610,430));x=(j%4)*620;y=(j//4)*460
 contact.paste(im,(x,y+23));d.text((x+7,y+5),f.stem,fill='white')
 # Baseline is available at scratch/r062_before; tests use actual screenshot differences.
 previous=BASE/(f.stem.replace('_R062','_R061')+'.png')
 if previous.exists():
  old=Image.open(previous).convert('RGB').resize(Image.open(f).size)
  delta=ImageChops.difference(old,Image.open(f).convert('RGB'))
  if f.stem.startswith(('PH-PRIMARY','TX-PRIMARY')) and max(ImageStat.Stat(delta).mean)<1.5:
   issue('no perceptible R062 geometry or material change:'+f.stem)
contact.save(OUT/'R062_EIGHT_AB_AFTER_CONTACT.png')
receipt={'status':'PASS' if not errors else 'FIX','instances':len(cases),
 'mode_probes':len(cases)+modeProbes,'focus_physical_captures':len(photos),
 'source_anchored_primary_cameras':cameraChecks,'native_ab_checks':compareChecks,
 'native_reveal_visual_objects':nativeRevealObjects,'rows':dataRows,'errors':errors}
(ROOT/'scratch/r062_primary_arch_browser_result.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2))
if errors or len(cases)!=26 or len(cases)+modeProbes!=78 or len(photos)!=8:
 raise SystemExit(1)
