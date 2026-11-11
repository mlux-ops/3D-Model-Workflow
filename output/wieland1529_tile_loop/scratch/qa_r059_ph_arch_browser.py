"""R059 physical Chrome fidelity tests, source-constrained and image-backed.

No source writes. The actual standalone file:// deliverable is tested. Prior
R056, R057 and R058 controls are tested alongside the new PH controls.
"""
from pathlib import Path
import json
from PIL import Image,ImageChops,ImageStat,ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/r059_ph_gallery'
OUT.mkdir(exist_ok=True)
DATA=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))
PH=('PH-PRIMARY','PH-BATH2','PH-BATH3','PH-BATH4')
errors=[];cases=[];photos=[];wetphotos=[];wall_restore=0;ceiling_cases=0;wc_cases=0
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def find(ev,cat):
 return [x for x in ev if x['category']==cat]

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1600,'height':1030},device_scale_factor=1)
 page.on('pageerror',lambda exc:errors.append('runtime:'+str(exc)))
 page.goto(URL+'#PH-PRIMARY/304A')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for room in DATA['rooms']:
  for inst in room['physical_instances']:
   a=inst['architecture'];nr=inst['room_number'];key=room['id']+'/'+nr
   page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   st=page.evaluate('window.__viewerDebug.getState()')
   if not inst.get('r059_visualization'):errors.append('r059-missing-instance-provenance:'+key)
   if st['mode']!='full' or not st['interiorReveal'] or st['sourceTraces'] or st['ceilingPreview']:
    errors.append('normal-scene-default-regression:'+key)
   originalWallIds=set(a['native_wall_ids'])
   if room['id']=='PH-BATH4':
    originalWallIds.update((a.get('adjacent_zone_geometry') or {}).get('native_wall_ids',[]))
   if not set(e['revit_id'] for e in find(ev,'ARCH_REGISTERED_WALL')).issubset(originalWallIds):
    errors.append('native-wall-IDs-modified:'+key)
   if any(x['visible'] for x in find(ev,'ARCH_R059_DERIVED_GWB_CEILING_CANOPY')):
    errors.append('opaque-ceiling-default:'+key)
   if a.get('native_ceiling_evidence'):
    canopy=find(ev,'ARCH_R059_DERIVED_GWB_CEILING_CANOPY')
    if not canopy or any(not e['derived_xy_only'] or
       not e['not_native_ceiling_solid'] or
       e['height_ft']!=a['native_ceiling_evidence']['underside_height_ft'] for e in canopy
       if e['parent_compartment']=='MAIN'):
     errors.append('native-GWB-underside-preview-source-mismatch:'+key)
   fascia=find(ev,'ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL')
   for f in fascia:
    c=next((c for c in a.get('native_casework_proxies',[]) if c['id']==f['revit_id']),None)
    if (not c or f['inside_native_aabb_y'] is not True or
      f['front_bottom_ft']<c['min_height_ft']-.005 or
      f['front_top_ft']>c['max_height_ft']+.005):
     errors.append('r059-floating-vanity-fascia-extrudes-outside-native-Z:'+key)
   sourceSinks=[x.get('closest_native_plumbing_insertion') for x in a.get('native_casework_proxies',[])]
   if room['id'] in ('PH-PRIMARY','TX-PRIMARY'):
    if any(x is not None for x in sourceSinks):
     errors.append('unexpected-primary-native-basin-insertion:'+key)
    if find(ev,'ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY'):
     errors.append('invented-primary-basin:'+key)
   if room['id']=='PH-POWDER':
    loc=find(ev,'ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR')
    if (len(loc)!=1 or loc[0]['not_exact_native_3d_insertion'] is not True or
      abs(loc[0]['visual_y_offset_from_source_ft']-.50615)>.005):
     errors.append('R056-native-basin-containment-regression:'+key)
   if room['id']=='TX-BATH4' and any(x['generic_visual_profile'] for x in ev):
    errors.append('TX4-3D-unlocated-tub-regression:'+key)
   if room['id']=='PH-BATH3' and any(x['fixture_visual_classification']=='NOMINAL_SELECTED_TUB_HOLLOW_GENERIC' for x in ev):
    errors.append('PH3-unselected-tub-represented-as-selected:'+key)
   if room['id']=='PH-BATH2':
    shells=[x for x in ev if x['generic_visual_profile']]
    if len(shells)!=1 or any(abs(a-b)>.035 for a,b in
      zip(shells[0]['physical_study_bbox_ft'],[4.916667,1.34,2.458333])):
     errors.append('PH2-nominal-source-fitted-selected-hollow-Duravit:'+key)
    rest=find(ev,'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW')
    if len(rest)!=3 or any(e['visible'] or e['no_additional_area'] is not True for e in rest):
     errors.append('PH2-default-low-wall-full-review-alternate:'+key)
   if room['id']=='PH-BATH4':
    rev=find(ev,'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW')
    if len(rev)!=1 or rev[0]['visible']:
     errors.append('PH4-default-full-height-W3-study-hidden:'+key)
    if nr=='311A':
     if any(e['room_number']=='310A' for e in ev if e['category']=='PLAN_SCHEMATIC_FIXTURE'):
      errors.append('PH4-310A-WIC4-false-installed-plumbing:'+key)
     near=find(ev,'ARCH_R059_310A_UNATTRIBUTED_CASEWORK_WITNESS')
     if len(near)!=1 or near[0]['visible']:
      errors.append('PH4-310A-nearby-counter-AABB-source-access:'+key)
    else:
     if not any(e['room_number']=='310B' and e['kind']=='toilet'
       for e in ev if e['category']=='PLAN_SCHEMATIC_FIXTURE'):
      errors.append('PH4-310B-separate-bath-fixture-context-missing:'+key)
   if a.get('toilet_proxy_anchor'):
    wc=[e for e in ev if e['wc_visual_piece']]
    # A wall/door-gated WC can legally become an unlocated 2D marker.
    if wc:
     if any(e['actual_wc_family_solid'] is not False for e in wc
      if e['actual_wc_family_solid'] is not None):
      errors.append('r059-WC-wrong-native-family-claim:'+key)
     wc_cases+=1
   cases.append(key)
   if room['id'] in PH:
    screenshot=OUT/(room['id']+'_'+nr+'_full.png')
    page.screenshot(path=str(screenshot));photos.append(screenshot)
    page.locator('#viewer-camera-wet').click()
    page.wait_for_timeout(160)
    if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='wet':
     errors.append('r059-wet-camera-inactive:'+key)
    after=page.evaluate('window.__viewerDebug.getSceneEvidence()')
    fullStudy=find(after,'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW')
    if room['id']=='PH-BATH2' and (len(fullStudy)!=3 or
      not all(e['visible'] for e in fullStudy)):
     errors.append('PH2-wet-camera-not-restoring-selected-original-heights:'+key)
    if room['id']=='PH-BATH4' and (len(fullStudy)!=1 or not fullStudy[0]['visible']):
     errors.append('PH4-wet-camera-not-restoring-311-W3-original-height:'+key)
    wet=OUT/(room['id']+'_'+nr+'_wet.png')
    page.screenshot(path=str(wet));wetphotos.append(wet)
    if room['id']=='PH-BATH4':
     for preset in ('ph4-311','ph4-310'):
      page.evaluate('(x)=>window.__viewerDebug.setCamera(x)',preset)
      if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!=preset:
       errors.append('PH4-exterior-separate-compartment-navigation:'+key+':'+preset)
      page.screenshot(path=str(OUT/(room['id']+'_'+nr+'_'+preset+'.png')))
    page.locator('#viewer-ceiling-preview').click()
    visible=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_R059_DERIVED_GWB_CEILING_CANOPY"&&x.visible)')
    # 310A has its OWN conservatively matched GWB AABB; 310B does not.
    # A 311 ceiling must NEVER be borrowed to fill the adjoining 310.
    adjacent_ceiling=(a.get('adjacent_zone_geometry') or {}).get('native_ceiling_evidence')
    expected=1+(1 if room['id']=='PH-BATH4' and adjacent_ceiling else 0)
    if len(visible)!=expected:errors.append('r059-compartment-independent-GWB-ON:'+key)
    else:ceiling_cases+=1
    page.locator('#viewer-ceiling-preview').click()
    if page.evaluate('document.body.dataset.viewerCeilingCanopies')!='0':
     errors.append('r059-ceiling-OFF-does-not-reveal-interior:'+key)
    page.locator('#viewer-reveal-interior').click()
    if page.evaluate('window.__viewerDebug.getState().interiorReveal'):
     errors.append('r059-reversible-wall-cutaway-wrong-state:'+key)
    page.locator('#viewer-reveal-interior').click();wall_restore+=1
    page.locator('#viewer-compare-ab').click()
    if (not page.locator('#viewer-ab-drawer').is_visible() or
      page.locator('#viewer-ab-drawer .viewer-ab-card').count()!=2):
     errors.append('r059-A-B-plan-comparison:'+key)
    page.locator('#viewer-compare-ab').click()
    if page.locator('#viewer-ceiling-preview').is_hidden():
     errors.append('r059-ceiling-control-disappeared:'+key)
   if page.evaluate('window.__viewerDebug.errors.length')>0:
    errors.append('runtime-recorded:'+key)
 page.evaluate('window.__viewerDebug.loadInstanceAddress("#PH-BATH4/311A")')
 page.locator('#viewer-toggle-source-traces').click()
 a=page.evaluate('window.__viewerDebug.getSceneEvidence()')
 if (len(find(a,'ARCH_R059_310A_UNATTRIBUTED_CASEWORK_WITNESS'))!=1 or
   not find(a,'ARCH_R059_310A_UNATTRIBUTED_CASEWORK_WITNESS')[0]['visible']):
  errors.append('r059-310A-nearby-native-source-hidden-when-traces-ON')
 page.locator('#viewer-toggle-source-traces').click()
 for button in ('#viewer-camera-iso','#viewer-camera-top','#viewer-camera-front',
   '#viewer-camera-fixture','#viewer-camera-inside','#viewer-camera-wet'):
  page.locator(button).click()
 if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='wet':
  errors.append('R059-camera-preset-cycle')
 page.locator('#toggle-walls').click()
 if any(e['visible'] for e in page.evaluate('window.__viewerDebug.getSceneEvidence()')
  if e['category'] in ('ARCH_REGISTERED_WALL','ARCH_R059_DERIVED_GWB_CEILING_CANOPY')):
  errors.append('r059-hide-walls-leaves-registered-walls')
 page.locator('#toggle-walls').click()
 errors.extend('viewer:'+str(e) for e in page.evaluate('window.__viewerDebug.errors.slice()'))
 browser.close()

def contact(images,outname):
 cols=4;rows=(len(images)+3)//4;w,h=530,350
 sheet=Image.new('RGB',(cols*w,rows*h),(17,26,37))
 painter=ImageDraw.Draw(sheet)
 for i,f in enumerate(images):
  pic=Image.open(f).convert('RGB')
  pic.thumbnail((w-12,h-32))
  x=(i%cols)*w+6;y=(i//cols)*h+25
  sheet.paste(pic,(x,y))
  painter.text((x,y-18),f.stem,fill=(235,225,205))
  if max(ImageStat.Stat(pic).stddev)<10:errors.append('black-scene-capture:'+str(f))
 sheet.save(OUT/outname)

contact(photos,'R059_PH_8_AB_FULL.png')
contact(wetphotos,'R059_PH_8_AB_WET.png')
report={'status':'FIX' if errors else 'PASS','physical_instances':len(cases),
 'ph_full_images':len(photos),'ph_wet_images':len(wetphotos),
 'source_specific_ceiling_preview_checks':ceiling_cases,
 'reversible_wall_cutaway_checks':wall_restore,
 'generic_wc_source_gated_cases':wc_cases,'errors':errors}
(ROOT/'scratch/r059_ph_browser_result.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
