"""R057 whole-viewer camera-facing sectional reveal and source A/B comparison.
Actual offline Chrome/Playwright, never a generated or schematic-only preview.
The R043 and in-app suites remain the source-specific regression authorities.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageOps, ImageDraw, ImageStat

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/r057_interior_gallery'
OUT.mkdir(exist_ok=True)
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
ROOMS=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))['rooms']
FOCUS={'PH-BATH2','PH-BATH3','PH-BATH4','PH-POWDER'}
errors=[];focus_files=[];rows=[];compare_checks=0;restores=0

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1600,'height':1000},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append('runtime:'+str(e)))
 page.goto(URL+'#PH-BATH4/311A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=25000)
 for room in ROOMS:
  for inst in room['physical_instances']:
   key=room['id']+'/'+inst['room_number']
   page.evaluate('(key)=>window.__viewerDebug.loadInstanceAddress("#"+key)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=25000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   walls=[o for o in ev if o['category']=='ARCH_REGISTERED_WALL']
   cuts=[o for o in walls if o.get('review_cutaway_only')]
   if not walls:errors.append('R057-no-source-wall-faces:'+key)
   if not cuts:errors.append('R057-no-camera-facing-section:'+key)
   if any(o['review_rendered_top_ft']>o['review_original_top_ft']+.001 or
     o['review_rendered_top_ft']<o['review_original_bottom_ft']-.001 for o in walls):
    errors.append('R057-wall-visual-section-increases-or-crosses-source-height:'+key)
   if any(o.get('review_source_native_geometry_unchanged') is not True or
     not o.get('receipt_id') for o in walls):
    errors.append('R057-wall-section-missing-source-disclosure:'+key)
   st=page.evaluate('window.__viewerDebug.getState()')
   if st['sourceTraces'] is not False or st['interiorReveal'] is not True:
    errors.append('R057-default-presentation-mode:'+key)
   camera=page.evaluate('window.__viewerDebug.getCameraInfo()')
   azimuth=camera['position'][0]-camera['target'][0]
   expected_left=(inst.get('plan_entry_side')=='left' if room['id']=='PH-BATH4'
    else inst.get('plan_is_mirrored_B') is True)
   if not ((azimuth < -1 if expected_left else azimuth > 1)):
    errors.append('R057-A-B-source-mirrored-camera-azimuth:'+key+':'+str(round(azimuth,3)))
   if room['id'] in FOCUS:
    f=OUT/(room['id']+'_'+inst['room_number']+'_reveal.png')
    page.screenshot(path=str(f));focus_files.append(f)
    # Restore full visualization WITHOUT regenerating or erasing the source
    # hosted-opening evidence; then reapply the source-faithful review section.
    page.locator('#viewer-reveal-interior').click()
    normal=page.evaluate('window.__viewerDebug.getSceneEvidence()')
    restored=[o for o in normal if o['category']=='ARCH_REGISTERED_WALL']
    if any(o['review_cutaway_only'] is True or
       abs(o['review_rendered_top_ft']-o['review_original_top_ft'])>.001 for o in restored):
     errors.append('R057-section-not-reversible:'+key)
    if len(restored)!=len(walls):
     errors.append('R057-wall-count-changed-on-visual-toggle:'+key)
    n0={(o['revit_id'],o['receipt_id'],o['review_original_top_ft'])
       for o in restored}
    n1={(o['revit_id'],o['receipt_id'],o['review_original_top_ft'])
       for o in walls}
    if n0!=n1:errors.append('R057-native-wall-provenance-mutated:'+key)
    if room['id']=='PH-BATH4' and not any(o.get('review_compartment')=='ADJACENT' for o in restored):
     errors.append('R057-PH4-310-311-combined-or-lost:'+key)
    restores+=1
    if inst['room_number'].endswith('A'):
     f=OUT/(room['id']+'_'+inst['room_number']+'_envelope.png')
     page.screenshot(path=str(f))
    page.locator('#viewer-reveal-interior').click()
    next_ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
    if not any(o['category']=='ARCH_REGISTERED_WALL' and o.get('review_cutaway_only') for o in next_ev):
     errors.append('R057-section-reenable-failed:'+key)
    # Physical mirror comparison uses only source-registered wall-face and
    # native-hosted insertion evidence; no false certified OST_Room or solids.
    page.locator('#viewer-compare-ab').click()
    if not page.locator('#viewer-ab-drawer').is_visible():
     errors.append('R057-A-B-source-plan-not-open:'+key)
    cards=page.locator('#viewer-ab-drawer .viewer-ab-card')
    if cards.count()!=2:errors.append('R057-A-B-card-count:'+key)
    elif not all(i['room_number'] in page.locator('#viewer-ab-drawer').text_content()
        for i in room['physical_instances']):
     errors.append('R057-A-B-physical-identity-mismatch:'+key)
    shapes=page.locator('#viewer-ab-drawer svg polygon').count()
    expected=2+(2 if room['id']=='PH-BATH4' else 0)
    if shapes!=expected:errors.append('R057-A-B-floor-face-count:'+key+':'+str(shapes))
    if room['id']=='PH-BATH4':
     if 'separate adjacent compartment' not in page.locator('#viewer-ab-drawer').text_content():
      errors.append('R057-PH4-310-source-ownership-undisclosed:'+key)
    compare_checks+=1
    page.locator('#viewer-compare-ab').click()
    if page.locator('#viewer-ab-drawer').is_visible():
     errors.append('R057-comparison-panel-not-reversible:'+key)
   rows.append({'instance':key,'walls':len(walls),'source_cut_sections':len(cuts),
    'door_witnesses':sum(o['category']=='ARCH_NATIVE_DOOR_FAMILY_AABB_WITNESS' for o in ev),
    'wet_w1_hidden':sum(bool(o['category']=='FULL_ROOM_WET_WALL' and o.get('review_visual_hidden_only')) for o in ev)})
 # Verify genuine A/B navigation from the comparison panel and native source
 # source properties, rather than a mere duplicated screenshot.
 page.evaluate('window.__viewerDebug.loadInstanceAddress("#PH-BATH3/307A")')
 page.locator('#viewer-compare-ab').click()
 page.locator('#viewer-ab-drawer .viewer-ab-open').nth(1).click()
 if page.evaluate('document.body.dataset.viewerInstance')!='307B':
  errors.append('R057-A-B-plan-navigation-to-physical-B-failed')
 page.locator('#viewer-compare-ab').click()
 page.locator('#viewer-camera-front').click()
 page.locator('#viewer-camera-top').click()
 page.locator('#viewer-camera-iso').click()
 if page.evaluate('window.__viewerDebug.getState().preset')!='isometric':
  errors.append('R057-camera-preset-cycle-failed')
 initial_camera=page.evaluate('window.__viewerDebug.getCameraInfo()')
 rect=page.locator('#render').bounding_box()
 if not rect:errors.append('R057-orbit-canvas-missing')
 else:
  cx=rect['x']+rect['width']*.54;cy=rect['y']+rect['height']*.56
  page.mouse.move(cx,cy)
  page.mouse.down(button='right')
  page.mouse.move(cx+95,cy+46,steps=8)
  page.mouse.up(button='right')
  page.wait_for_timeout(300)
  panned=page.evaluate('window.__viewerDebug.getCameraInfo()')
  if sum((a-b)**2 for a,b in zip(initial_camera['target'],panned['target']))<.0005:
   errors.append('R057-right-mouse-pan-not-working')
  page.mouse.wheel(0,-285)
  page.wait_for_timeout(280)
  zoomed=page.evaluate('window.__viewerDebug.getCameraInfo()')
  dist=lambda c:sum((a-b)**2 for a,b in zip(c['position'],c['target']))**.5
  if abs(dist(zoomed)-dist(panned))<.02:
   errors.append('R057-mouse-wheel-zoom-not-working')
  page.locator('#reset').click()
  if page.evaluate('window.__viewerDebug.getState().preset')!='isometric':
   errors.append('R057-camera-reset-after-pan-zoom-failed')
 page.locator('#viewer-reveal-interior').click()
 if page.evaluate('window.__viewerDebug.getState().interiorReveal') is not False:
  errors.append('R057-visual-section-persistence-failed')
 page.locator('#viewer-reveal-interior').click()
 page.locator('#viewer-toggle-source-traces').click()
 if page.evaluate('window.__viewerDebug.getState().sourceTraces') is not True:
  errors.append('R057-source-witness-restore-failed')
 page.locator('#viewer-toggle-source-traces').click()
 browser.close()

# Contact sheet is a physical browser capture gallery, not fabricated artwork.
sheet=Image.new('RGB',(650*4,460*2),(18,28,36))
for j,f in enumerate(focus_files):
 im=Image.open(f).convert('RGB')
 if max(ImageStat.Stat(im).stddev)<10:errors.append('R057-blank-physical-screenshot:'+f.name)
 im.thumbnail((636,424))
 x=(j%4)*650+7;y=(j//4)*460+25
 sheet.paste(im,(x,y))
 ImageDraw.Draw(sheet).text((x,y-20),f.stem,fill=(236,218,188))
sheet.save(OUT/'R057_PH_FOCUS_8_AB.png')
receipt={'status':'PASS' if not errors else 'FIX','instances':len(rows),
 'source_wall_cutaway_instances':sum(x['source_cut_sections']>0 for x in rows),
 'focus_physical_screenshots':len(focus_files),'reversible_checks':restores,
 'ab_source_plan_checks':compare_checks,'rows':rows,'errors':errors}
(ROOT/'scratch/r057_interior_qa_result.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2))
if errors:raise SystemExit(1)
