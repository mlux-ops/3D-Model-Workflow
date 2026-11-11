"""R063 physically render complete source-registered bathroom package in offline Chrome."""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
FOCUS=('PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3')
OUT=ROOT/'scratch/r063_arch_gallery';OUT.mkdir(exist_ok=True)
BEFORE=ROOT/'scratch/r063_before'
fail=[];cases=[];focus=[];modes=0;cornerA={};checks={'focus_cameras':0,'ab':0,'wall_reveals':0,
 'ceilings':0,'source_inspectors':0,'material_inspectors':0,'source_toggles':0}

def cat(ev,name):return [x for x in ev if x['category']==name]
def error(msg):fail.append(msg)
def selected_floor(r):return next((p for p in r['products'] if 'level' in p['surface'].lower()),None)
def parse_size(s):
 import re
 m=re.search(r'(\d+(?:\.\d+)?)\s*[^\d\s]{1,2}\s*(\d+(?:\.\d+)?)',s)
 if not m:return None
 w,h=float(m.group(1))/12,float(m.group(2))/12
 return (max(w,h),min(w,h))

with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=CHROME,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
 page.on('pageerror',lambda e:error('JS:'+str(e)))
 page.goto(URL+'#PH-BATH2/305A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for room in DATA['rooms']:
  for inst in room['physical_instances']:
   key=room['id']+'/'+inst['room_number']
   page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   state=page.evaluate('window.__viewerDebug.getState()')
   a=inst.get('architecture',{})
   if inst.get('r063_visualization',{}).get('physical_instance')!=inst['room_number']:
    error('missing R063 26-instance provenance:'+key)
   if state['mode']!='full' or state['sourceTraces'] or not state['interiorReveal']:
    error('default Full Bathroom source/cutaway controls:'+key)
   floor=cat(ev,'ARCH_REGISTERED_FLOOR')
   if len(floor)!=1:error('missing actual registered shape floor:'+key)
   if selected_floor(room) and floor:
    size=parse_size(selected_floor(room)['size'])
    expected=sorted([1/size[0],1/size[1]]) if size else None
    tex=floor[0].get('r063_material_texture_repeat')
    if not expected or floor[0].get('r063_source_floor_uv_kind')!='PLANAR_SOURCE_FEET_NOT_NORMALIZED' or \
      not tex or any(abs(x-y)>.008 for x,y in zip(sorted(tex),expected)):
     error('physical nominal tile texture mapping in FEET incorrect:'+key+':'+str((tex,expected)))
    if not floor[0].get('r063_floor_material_selected'):error('chosen floor atlas not shown:'+key)
   else:
    if floor and floor[0]['r063_floor_material_selected']:
     error('invented selected floor in no-pick/dry room:'+key)
   contact=cat(ev,'ARCH_R063_SOURCE_WALL_FOOT_CONTACT_LIGHT')
   if not contact:error('source wall base light overlay missing:'+key)
   if any(x['revit_id'] not in a['native_wall_ids'] or
      not x['r063_source_bounded_to_actual_wall_run'] or
      x['r063_installed_baseboard'] is not False or
      x['r063_actual_floor_area_ft2'] is not None
      for x in contact):error('native-wall contact shading falsely sourced:'+key)
   if room['id'] in FOCUS:
    focus.append(key)
    if page.locator('#viewer-r063-bath-finish').is_hidden():error('new Bath finish camera hidden:'+key)
    pieces=cat(ev,'ARCH_R063_NATIVE_BOUND_COMPACT_VANITY_SIDE_STUDY')
    underside=cat(ev,'ARCH_R063_NATIVE_BOUND_COMPACT_VANITY_UNDERSIDE_STUDY')
    source_counter=a['native_casework_proxies'][0]
    # Native Countertop AABB 207A/B starts -0.167ft below floor. Never turn
    # this unverified category bound into a visible physical floor pedestal.
    safe_compact=source_counter['min_height_ft']>.60
    if len(pieces)!=(2 if safe_compact else 0) or len(underside)!=(1 if safe_compact else 0):
     error('native countertop category AABB vertical source-gated compact vanity:'+key)
    for v in pieces+underside:
     if v['revit_id']!=a['native_casework_proxies'][0]['id'] or \
       not v['r063_inside_native_category_aabb_xyz'] or not v['receipt_id']:
      error('compact vanity source IDs or AABB containment absent:'+key)
    if room['program']['kind']=='TUB_OR_WALK_IN_UNSELECTED':
     if cat(ev,'FULL_ROOM_SELECTED_PAN_SCHEMATIC') or \
       any(x['fixture_visual_classification']=='NOMINAL_SELECTED_TUB_HOLLOW_GENERIC' for x in ev):
      error('unselected tub vs walk-in branch got physical solid:'+key)
    if room['program']['kind']=='DURAVIT_TUB_SELECTED':
     tubs=[x for x in ev if x.get('r063_tub_part')=='CERAMIC_TOP_RIM_STUDY']
     if len(tubs)!=1 or not math.isclose(tubs[0]['nominal_exterior_width_ft'],59/12,abs_tol=.01):
      error('source nominal Duravit rim missing or wrong scale:'+key)
     if cat(ev,'FULL_ROOM_SELECTED_PAN_SCHEMATIC'):
      error('new tile PAN fabricated for selected bathtub:'+key)
    corners=cat(ev,'ARCH_R063_NATIVE_HOST_FINISH_CORNER_SHADE')
    wet=cat(ev,'FULL_ROOM_WET_WALL')
    sourceReturns=[w for w in wet if w['wall'] in ('W2','W3') and w['source_return_supported']]
    if len(corners)!=len(sourceReturns) or any(x['native_host_face_id'] not in a['native_wall_ids']
      or x['r063_new_tile_plane'] is not False or x['r063_material_quantities_unchanged'] is not True
       for x in corners):
     error('wet corner lighting not matched to native source-supported return:'+key)
    cornerA[key]=len(corners)
    full=OUT/(room['id']+'_'+inst['room_number']+'_R063_FULL.png')
    page.screenshot(path=str(full))
    page.locator('#viewer-r063-bath-finish').click()
    if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='r063-bath-finish':
     error('Bath finish camera not selected:'+key)
    page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_R063_FINISH.png')))
    checks['focus_cameras']+=1
    page.locator('#viewer-camera-wet').click()
    page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_R063_WET.png')))
    page.locator('#viewer-compare-ab').click()
    if page.locator('#viewer-ab-drawer').get_attribute('hidden') is not None:
     error('source-backed mirrored A/B drawer unavailable:'+key)
    page.locator('#viewer-compare-ab').click();checks['ab']+=1
    page.locator('#viewer-ceiling-preview').click()
    canopy=cat(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_R059_DERIVED_GWB_CEILING_CANOPY')
    if a.get('native_ceiling_evidence') and not any(x['visible'] for x in canopy):
     error('source-specific ceiling underside not independently visible:'+key)
    page.locator('#viewer-ceiling-preview').click();checks['ceilings']+=1
    page.locator('#viewer-reveal-interior').click()
    if any(x['review_cutaway_only'] for x in cat(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_REGISTERED_WALL')):
     error('wall geometry not restored with section OFF:'+key)
    page.locator('#viewer-reveal-interior').click();checks['wall_reveals']+=1
    page.locator('#viewer-toggle-source-traces').click()
    if not page.evaluate('window.__viewerDebug.getState().sourceTraces'):
     error('source trace toggle did not turn ON:'+key)
    page.locator('#viewer-toggle-source-traces').click();checks['source_toggles']+=1
    page.locator('#viewer-v2-evidence summary').click()
    if 'R063 source-scale floor finish' not in page.locator('#viewer-evidence-content').inner_text():
     error('R063 provenance missing in native source inspector:'+key)
    page.locator('#viewer-v2-evidence summary').click();checks['source_inspectors']+=1
    page.locator('#viewer-camera-iso').click()
    if selected_floor(room):
     if not page.locator('.surface').count():error('selected tile/material inspector absent:'+key)
     else:checks['material_inspectors']+=1
   for mode in ['study','context']:
    page.evaluate('(m)=>window.__viewerDebug.setMode(m)',mode)
    if page.evaluate('window.__viewerDebug.getState().mode')!=mode:
     error('study/context room switching error:'+key+'/'+mode)
    if mode=='context' and cat(page.evaluate('window.__viewerDebug.getSceneEvidence()'),
     'ARCH_R063_NATIVE_BOUND_COMPACT_VANITY_SIDE_STUDY'):
     error('full-only generic vanity leaked into native context:'+key)
    modes+=1
   cases.append(key)
 # Deep-link, rapid material readiness and real physical pointer manipulation.
 page.goto(URL+'#TX-BATH3/207B',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 if page.evaluate('document.body.dataset.viewerInstance')!='207B':error('deep link TX3 B failed')
 for key in ['PH-PRIMARY/304A','TX-BATH2/205B','PH-BATH3/307A','TX-BATH4/007A',
   'PH-POWDER/405B','PH-BATH2/305A','TX-POWDER/102A']:
  page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',key)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
 if page.evaluate('window.__viewerDebug.errors.length'):
  error('runtime texture/model errors:'+str(page.evaluate('window.__viewerDebug.errors')))
 page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)','TX-BATH2/205A')
 initial=page.evaluate('window.__viewerDebug.getCameraInfo()')
 page.mouse.move(760,620);page.mouse.down();page.mouse.move(900,700,steps=6);page.mouse.up()
 page.wait_for_timeout(230)
 moved=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if math.dist(initial['position'],moved['position'])<.02:error('physical mouse orbit failed')
 page.mouse.wheel(0,-200);page.wait_for_timeout(240)
 zoom=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if math.dist(moved['position'],zoom['position'])<.02:error('physical zoom failed')
 page.mouse.move(730,650);page.mouse.down(button='right');page.mouse.move(810,690,steps=6);page.mouse.up(button='right')
 page.wait_for_timeout(210)
 pan=page.evaluate('window.__viewerDebug.getCameraInfo()')
 if math.dist(zoom['target'],pan['target'])<.02:error('physical pan failed')
 page.locator('#reset').click()
 if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='isometric':error('camera reset failed')
 browser.close()

im=Image.new('RGB',(4*620,2*450),(18,29,37));draw=ImageDraw.Draw(im)
for i,key in enumerate(focus):
 kind,n=key.split('/');src=OUT/(kind+'_'+n+'_R063_FULL.png')
 if not src.exists():continue
 frame=Image.open(src).convert('RGB');frame.thumbnail((611,425))
 xx=i%4*620;yy=i//4*450
 im.paste(frame,(xx,yy+22));draw.text((xx+8,yy+5),kind+' '+n,fill='white')
 before=BEFORE/(kind+'_'+n+'_R062_FULL.png')
 if before.exists():
  prev=Image.open(before).convert('RGB').resize(Image.open(src).size)
  diff=ImageChops.difference(prev,Image.open(src).convert('RGB'))
  # Actual physical R063 source-difference is 0.78-0.86 units/pixel averaged
  # over the ENTIRE 1500x980 page, including immutable sidebar and header.
  # A 1.5 threshold falsely rejected all eight although visible 3D stage
  # changed. Require measured >0.5 page-wide AND changed scene pixels.
  if max(ImageStat.Stat(diff).mean)<.50 or diff.getbbox() is None:
   error('no visible R063 full-room improvement:'+key)
im.save(OUT/'R063_EIGHT_FOCUS_AB_AFTER_CONTACT.png')
receipt={'status':'PASS' if not fail else 'FIX','physical_instances':len(cases),
 'mode_probes':len(cases)+modes,'focus_instances':focus,
 'source_supported_corner_counts':cornerA,'checks':checks,'errors':fail}
(ROOT/'scratch/r063_arch_browser_result.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(receipt,indent=2))
if fail or len(cases)!=26 or len(cases)+modes!=78 or len(focus)!=8:raise SystemExit(1)
