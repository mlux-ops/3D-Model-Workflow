"""R058 integrated source-geometry/fixture/vanity/cutaway/browser review.
The browser loads ONLY the actual standalone offline deliverable. No Revit
calls, product decisions, or writes to any protected project record.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageStat

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/r058_tx_gallery'
OUT.mkdir(exist_ok=True)
BEFORE=ROOT/'scratch/r058_tx_before'
DATA=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf-8'))
ROOMS=DATA['rooms']
FOCUS=('TX-PRIMARY','TX-BATH2','TX-BATH3','TX-BATH4')
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
errors=[];checked=[];photos=[];foci=[];section_checks=0;compare_checks=0

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1600,'height':1000},device_scale_factor=1)
 page.on('pageerror',lambda exc:errors.append('runtime:'+str(exc)))
 page.goto(URL+'#TX-BATH2/205A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for room in ROOMS:
  for inst in room['physical_instances']:
   name=room['id']+'_'+inst['room_number']
   key=room['id']+'/'+inst['room_number']
   a=inst['architecture'];focus=room['id'] in FOCUS
   page.evaluate('(key)=>window.__viewerDebug.loadInstanceAddress("#"+key)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   st=page.evaluate('window.__viewerDebug.getState()')
   if st['mode']!='full' or st['sourceTraces'] or not st['interiorReveal']:
    errors.append('default-full-clean-controls:'+key)
   walls=[e for e in ev if e['category']=='ARCH_REGISTERED_WALL']
   # PH4 311 deliberately shows the separately registered 310 compartment
   # in the SAME scene. Its source native wall IDs are valid but not part of
   # the 311 wet-room-only ID list; accepting both is essential, not a leak.
   allowed=set(a['native_wall_ids'])
   allowed.update((a.get('adjacent_zone_geometry') or {}).get('native_wall_ids',[]))
   if not walls or not set(e['revit_id'] for e in walls).issubset(allowed):
    errors.append('source-wall-truth-no-longer-preserved:'+key)
   ghost=[e for e in ev if e['category']=='ARCH_VISUAL_CUTAWAY_UPPER_REMNANT' and e['visible']]
   if not ghost or any(e['visual_section_only'] is not True or
     e['rendered_start_y_ft']>=e['rendered_end_y_ft'] or
     e['revit_id'] not in a['native_wall_ids'] for e in ghost):
    errors.append('R058-source-wall-upper-remnant-not-provenanced:'+key)
   if (a.get('selected_tub_unlocated_reason') and
     any(e.get('fixture_visual_classification')=='NOMINAL_SELECTED_TUB_HOLLOW_GENERIC' for e in ev)):
    errors.append('R058-unlocated-TX4-tub-promoted-to-3D:'+key)
   if room['id']=='PH-POWDER':
    loc=[e for e in ev if e['category']=='ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR']
    if (len(loc)!=1 or loc[0]['not_exact_native_3d_insertion'] is not True or
      abs(loc[0]['visual_y_offset_from_source_ft']-.50615)>.005):
     errors.append('R058-R056-source-basin-protection-regressed:'+key)
   if focus:
    counter=a['native_casework_proxies']
    if len(counter)!=1:errors.append('R058-TX-source-counter-attribution:'+key)
    c=counter[0]
    front=[e for e in ev if e['category']=='ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL']
    should_front=c['min_height_ft']>.60
    if len(front)!=(1 if should_front else 0):
     errors.append('R058-TX-vanity-fascia-source-bounded:'+key)
    if front and (front[0]['revit_id']!=c['id'] or
       front[0]['cabinet_family_solid'] is not False or
       front[0]['installed_face_location_verified'] is not False or
       abs(front[0]['front_dimension_ft']-max(c['width_x_ft'],c['depth_z_ft']))>.003):
     errors.append('R058-vanity-fascia-fabricated-native-claim-or-width:'+key)
    missing=[e for e in ev if e['category']=='ARCH_NATIVE_CASEWORK_AABB_STUDY' and e['basin_spatial_status']]
    source_sink=c.get('closest_native_plumbing_insertion')
    should_missing=(not source_sink and room['program']['kind']!='TUB_OR_WALK_IN_UNSELECTED'
      and 'UNSELECTED' not in room['program'].get('plumbing_truth',''))
    # TX-PRIMARY 202A/B are the critical no-source-basins; 007B also has
    # no native sink relationship. Native casework is still shown.
    if room['id']=='TX-PRIMARY' or (room['id']=='TX-BATH4' and inst['room_number']=='007B'):
     if len(missing)!=1 or any(e['category'] in
       ('ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY','ARCH_ILLUSTRATIVE_BASIN_RIM') for e in ev):
      errors.append('R058-no-invented-3D-lavatory-without-native-point:'+key)
    if room['id']=='TX-BATH2':
     shells=[e for e in ev if e.get('generic_visual_profile') is True]
     if len(shells)!=1 or shells[0]['fixture_visual_classification']!='NOMINAL_SELECTED_TUB_HOLLOW_GENERIC':
      errors.append('R058-Duravit-hollow-shell-missing:'+key)
     else:
      actual=shells[0]['physical_study_bbox_ft']
      expected=[4.916667,1.34,2.458333]
      if not actual or any(abs(x-y)>.035 for x,y in zip(actual,expected)):
       errors.append('R058-Duravit-hollow-nominal-exterior-dimensions:'+key+':'+str(actual))
      if (not shells[0]['no_bathtub_drain_or_spout_location'] or
        shells[0]['actual_drain_location'] is not False):
       errors.append('R058-Duravit-invented-spout-or-drain:'+key)
    if room['id']=='TX-BATH3':
     uncertain=[e for e in ev if e['kind']=='tub-reference']
     if (len(uncertain)!=1 or
       uncertain[0]['fixture_visual_classification']!='UNSELECTED_BRANCH_2D_PLAN_ONLY' or
       abs(uncertain[0]['position'][1]-.05)>.015):
      errors.append('R058-TX3-conditional-tub-not-2D:'+key)
     if any(e['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for e in ev):
      errors.append('R058-TX3-optional-PAN-falsely-selected:'+key)
    if room['id']=='TX-BATH4':
     if not any(e['kind']=='tub (UNLOCATED 2D)' for e in ev) or a.get('selected_tub_proxy'):
      errors.append('R058-TX4-Duravit-unlocated-hold-lost:'+key)
    if room['id']=='TX-BATH2':
     if any(e['category'].startswith('ARCH_ILLUSTRATIVE_BASIN') for e in ev):
      errors.append('R058-TX2-unselected-basin-invented:'+key)
    screenshot=OUT/(name+'_after.png')
    page.screenshot(path=str(screenshot));photos.append(screenshot)
    # Verify the exterior source-based focus target, not a fabricated
    # standing position or location for any selected UNLOCATED tub.
    page.locator('#viewer-camera-fixture').click()
    camera=page.evaluate('window.__viewerDebug.getCameraInfo()')
    origin=a.get('selected_tub_proxy') or c
    center=origin.get('local_center_xz_ft')
    if camera['preset']!='fixture' or any(abs(camera['target'][q]-center[z])>.002
      for q,z in ((0,0),(2,1))):
     errors.append('R058-exterior-camera-target-not-native-or-selected-dim:'+key)
    focused=OUT/(name+'_focus.png')
    page.screenshot(path=str(focused));foci.append(focused)
    page.locator('#viewer-reveal-interior').click()
    no_reveal=page.evaluate('window.__viewerDebug.getSceneEvidence()')
    if any(e['visible'] for e in no_reveal if e['category']=='ARCH_VISUAL_CUTAWAY_UPPER_REMNANT'):
     errors.append('R058-cutaway-ghost-not-hidden-after-restore:'+key)
    page.locator('#viewer-reveal-interior').click()
    section_checks+=1
    page.locator('#viewer-compare-ab').click()
    panel=page.locator('#viewer-ab-drawer')
    if not panel.is_visible() or panel.locator('.viewer-ab-card').count()!=2:
     errors.append('R058-A-B-panel-or-instance-cards:'+key)
    if room['id']=='TX-BATH4' and 'UNLOCATED' not in panel.text_content():
     errors.append('R058-TX4-A-B-tub-spatial-hold-not-visible:'+key)
    page.locator('#viewer-compare-ab').click()
    compare_checks+=1
   checked.append({'key':key,'walls':len(walls),'visual_upper_remnants':len(ghost)})
  # End of room type iteration.
 page.evaluate('window.__viewerDebug.loadInstanceAddress("#TX-BATH2/205A")')
 page.locator('#viewer-camera-top').click()
 page.locator('#viewer-camera-front').click()
 page.locator('#viewer-camera-fixture').click()
 page.locator('#viewer-camera-iso').click()
 if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='isometric':
  errors.append('R058-plan-elevation-fixture-isometric-camera-cycle')
 for label in ('#viewer-toggle-source-traces','#toggle-walls'):
  page.locator(label).click()
  now=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  if label=='#toggle-walls':
   if any(e['visible'] for e in now if e['category'] in
     ('ARCH_REGISTERED_WALL','ARCH_VISUAL_CUTAWAY_UPPER_REMNANT')):
    errors.append('R058-walls-off-leaves-visible-ghosts')
  page.locator(label).click()
 if page.evaluate('window.__viewerDebug.errors.slice()'):
  errors.extend('viewer:'+str(x) for x in page.evaluate('window.__viewerDebug.errors.slice()'))
 browser.close()

def contact(paths,outname):
 tiles=Image.new('RGB',(4*540,2*358),(18,27,36));draw=ImageDraw.Draw(tiles)
 for i,path in enumerate(paths):
  im=Image.open(path).convert('RGB');im.thumbnail((526,326))
  if max(ImageStat.Stat(im).stddev)<9:errors.append('R058-black-capture:'+path.name)
  x=(i%4)*540+6;y=(i//4)*358+24
  tiles.paste(im,(x,y))
  draw.text((x,y-20),path.stem,fill=(233,221,199))
 tiles.save(OUT/outname)

contact(photos,'R058_TX_8_AB_AFTER.png')
contact(foci,'R058_TX_8_AB_FOCUS.png')
before_after=Image.new('RGB',(4*540,4*355),(18,27,36))
d=ImageDraw.Draw(before_after)
for i,after in enumerate(photos):
 prior=BEFORE/(after.name.replace('_after.png','.png'))
 for k,img_path in enumerate((prior,after)):
  if not img_path.exists():
   errors.append('R058-before-after-source-missing:'+str(img_path));continue
  im=Image.open(img_path).convert('RGB');im.thumbnail((530,327))
  cell=2*i+k;xx=(cell%4)*540+5;yy=(cell//4)*355+22
  before_after.paste(im,(xx,yy))
  d.text((xx,yy-18),img_path.stem,fill=(238,220,184))
before_after.save(OUT/'R058_TX_8_BEFORE_AFTER.png')

result={'status':'FIX' if errors else 'PASS','physical_instances_checked':len(checked),
 'tx_focus_screenshots':len(photos),'tx_focus_source_target_captures':len(foci),
 'tx_reversible_sections':section_checks,'tx_ab_plan_checks':compare_checks,
 'source_wall_remnants':sum(x['visual_upper_remnants'] for x in checked),
 'errors':errors,'cases':checked}
(ROOT/'scratch/r058_tx_browser_result.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
if errors:raise SystemExit(1)
