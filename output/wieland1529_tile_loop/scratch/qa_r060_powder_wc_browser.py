"""R060 physical offline Chrome acceptance: 26 source records, dry floors,
program-held basins, counter bounds, targeted A/B captures and controls.
No Revit/source/selection writes; screenshots and JSON receipts in scratch.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import json, math

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
ROOMS=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))['rooms']
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUT=ROOT/'scratch/r060_powder_wc_gallery'
OUT.mkdir(exist_ok=True)
FOCUS={'PH-POWDER','PH-WC','TX-POWDER2','TX-WC'}
ERRORS=[];ROWS=[];FILES=[];CAMERAS=0;COMPARES=0;MODES=0

def cat(objects,c):return [o for o in objects if o['category']==c]

with sync_playwright() as p:
 b=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=b.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
 page.on('pageerror',lambda e:ERRORS.append('runtime:'+str(e)))
 page.goto(URL+'#PH-POWDER/405A')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for room in ROOMS:
  for inst in room['physical_instances']:
   key=room['id']+'/'+inst['room_number'];a=inst['architecture']
   page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',key)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
   state=page.evaluate('window.__viewerDebug.getState()')
   meta=inst.get('r060_visualization')
   if not meta or meta['physical_instance']!=inst['room_number']:
    ERRORS.append('r060 provenance:'+key)
   floor=cat(ev,'ARCH_REGISTERED_FLOOR')
   if len(floor)!=1:ERRORS.append('registered full floor:'+key)
   if room['program'].get('dry_floor_retained') and (not meta or not meta['dry_wood_visual_study']):
    ERRORS.append('inherited wood evidence:'+key)
   if room['id'] in ('TX-POWDER','TX-POWDER2'):
    if cat(ev,'ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY') or cat(ev,'ARCH_ILLUSTRATIVE_BASIN_RIM'):
     ERRORS.append('unselected or no pick physical basin:'+key)
    if not any(o['basin_program_status'] for o in cat(ev,'ARCH_NATIVE_CASEWORK_AABB_STUDY')):
     ERRORS.append('missing program basin hold:'+key)
    loc=cat(ev,'ARCH_NATIVE_UNSELECTED_PLUMBING_LOCATOR')
    for x in loc:
     if x['visible'] or not x['not_exact_native_3d_insertion'] or x['source_local_y_ft'] is None:
      ERRORS.append('source unselected locator default/source Y:'+key)
   if room['id']=='PH-POWDER':
    loc=cat(ev,'ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR')
    if len(loc)!=1 or abs(loc[0]['visual_y_offset_from_source_ft']-.50615)>.005:
     ERRORS.append('R056 original native elevation hold:'+key)
   for c in a.get('native_casework_proxies',[]):
    top=[x for x in cat(ev,'ARCH_NATIVE_COUNTERTOP_VISUAL') if x['revit_id']==c['id']]
    if len(top)!=1 or top[0]['contained_within_native_category_aabb_xyz'] is not True:
     ERRORS.append('strict native countertop top bounds:'+key)
   if a.get('toilet_proxy_anchor') and not cat(ev,'ARCH_NATIVE_TOILET_FAMILY_AABB_WITNESS'):
    ERRORS.append('native WC AABB source missing:'+key)
   if state['sourceTraces'] or not state['interiorReveal'] or state['ceilingPreview']:
    ERRORS.append('source/default controls:'+key)
   if room['id'] in FOCUS:
    f=OUT/(room['id']+'_'+inst['room_number']+'_r060_full.png')
    page.screenshot(path=str(f));FILES.append(f)
    if a.get('native_casework_proxies'):
     page.locator('#viewer-r060-counter-focus').click()
     if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='r060-counter':
      ERRORS.append('counter camera:'+key)
     page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_counter.png')))
     CAMERAS+=1
    if a.get('toilet_proxy_anchor'):
     page.locator('#viewer-r060-wc-focus').click()
     if page.evaluate('window.__viewerDebug.getCameraInfo().preset')!='r060-wc':
      ERRORS.append('WC camera:'+key)
     page.screenshot(path=str(OUT/(room['id']+'_'+inst['room_number']+'_wc.png')))
     CAMERAS+=1
    page.locator('#viewer-compare-ab').click()
    if page.locator('#viewer-ab-drawer').get_attribute('hidden') is not None:
     ERRORS.append('AB compare drawer:'+key)
    COMPARES+=1
    page.locator('#viewer-compare-ab').click()
    page.locator('#viewer-toggle-source-traces').click()
    for x in cat(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_NATIVE_UNSELECTED_PLUMBING_LOCATOR'):
     if not x['visible']:ERRORS.append('unselected source trace toggle:'+key)
    page.locator('#viewer-toggle-source-traces').click()
    page.locator('#viewer-reveal-interior').click()
    walls=cat(page.evaluate('window.__viewerDebug.getSceneEvidence()'),'ARCH_REGISTERED_WALL')
    if any(w['review_cutaway_only'] for w in walls):ERRORS.append('wall restore:'+key)
    page.locator('#viewer-reveal-interior').click()
   for mode in ('study','context'):
    page.evaluate('(m)=>window.__viewerDebug.setMode(m)',mode)
    if page.evaluate('window.__viewerDebug.getState().mode')!=mode:
     ERRORS.append('mode:'+mode+':'+key)
    MODES+=1
   ROWS.append({'type':room['id'],'physical':inst['room_number'],
    'wall_ids':a['native_wall_ids'],'area_sf':a['floor_polygon_area_ft2'],
    'basin_gate':meta['basin_selection_gate'] if meta else None})
 b.close()

if FILES:
 thumbs=[]
 for f in FILES:
  im=Image.open(f).convert('RGB');im.thumbnail((540,355))
  thumbs.append((f.name,im.copy()))
 canvas=Image.new('RGB',(540*4,385*math.ceil(len(thumbs)/4)),(18,28,38))
 draw=ImageDraw.Draw(canvas)
 for idx,(name,img) in enumerate(thumbs):
  x=(idx%4)*540;y=(idx//4)*385
  canvas.paste(img,(x,y+18));draw.text((x+10,y+2),name,fill='white')
 canvas.save(OUT/'R060_8_AB_FOCUS_CONTACT.png')
receipt={'status':'PASS' if not ERRORS else 'FIX','instances':len(ROWS),
 'mode_probes':MODES+len(ROWS),'focus_captures':len(FILES),
 'focus_cameras':CAMERAS,'ab_comparisons':COMPARES,'errors':ERRORS,'rows':ROWS}
(ROOT/'scratch/r060_powder_wc_browser_result.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2))
if ERRORS or len(ROWS)!=26 or len(FILES)!=8 or MODES+len(ROWS)!=78:raise SystemExit(1)
