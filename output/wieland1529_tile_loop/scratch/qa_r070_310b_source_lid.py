"""One physically scoped Chrome check for Reviewer97 inherited 310B R069 FIX.
Not a repetition of R069 eight-room or 26-instance testing.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib
root=Path(__file__).resolve().parents[1]
rooms=json.loads((root/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))['rooms']
room=next(r for r in rooms if r['id']=='PH-BATH4')
arch=next(i['architecture'] for i in room['physical_instances'] if i['room_number']=='311B')
source=next(x for x in arch['adjacent_zone_geometry']['native_fixture_evidence']
 if x['kind']=='countertop' and x['id']==16438253)
b=source['bounds_native_ft'];ox,oy=arch['origin_native_xy_ft']
limit=[[b['min'][0]-ox,b['min'][2]-arch['native_level_elevation_ft'],oy-b['max'][1]],
       [b['max'][0]-ox,b['max'][2]-arch['native_level_elevation_ft'],oy-b['min'][1]]]
errors=[]
dest=root/'scratch/r070_focus/after'
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1480,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append('runtime '+str(e)))
 page.goto((root/'deliverables/viewer3d/index.html').as_uri()+'#PH-BATH4/311B',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=48000)
 page.locator('#viewer-focus-enter').click()
 page.evaluate('window.__viewerDebug.setCamera("ph4-310")')
 page.locator('#stage').screenshot(path=str(dest/'PH-BATH4_311B_310B_LID_R070.png'))
 e=page.evaluate('window.__viewerDebug.getSceneEvidence()')
 lids=[x for x in e if x['category']=='ARCH_R070_310B_NATIVE_BOUNDED_LID']
 if len(lids)!=1:errors.append('native 310B lid missing or duplicated '+str(len(lids)))
 if lids:
  actual=lids[0].get('r070_native_lid_world_aabb')
  if actual is None:errors.append('lid mesh physical extent not exposed')
  else:
   for axis in range(3):
    if actual[0][axis]<limit[0][axis]-.005 or actual[1][axis]>limit[1][axis]+.005:
     errors.append('lid overhang source AABB axis '+str(axis)+' '+str(actual))
  if not lids[0].get('category')=='ARCH_R070_310B_NATIVE_BOUNDED_LID':
   errors.append('missing source-specific lid category')
 if any(x['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for x in e):
  errors.append('311 got an invented second selected pan')
 if not any(x['category']=='ARCH_R066_SHARED_LEVEL_POINT_SOURCE_EDGE' for x in e):
  errors.append('PH4 original 40.2 SF combined pool evidence not retained')
 if page.evaluate('window.__viewerDebug.errors'):
  errors.append('browser runtime errors '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()
result={'status':'PASS' if not errors else 'FIX','reviewer97_r069_genuine_fix':'inherited PH4 310B native countertop lid',
 'case':'PH-BATH4/311B', 'countertop_id':16438253,
 'category_AABB_local_ft':limit,'corrected_lid_AABB_local_ft':actual if lids else None,
 'over_native_category_y_ft':round(max(0,actual[1][1]-limit[1][1]),5) if lids and actual else None,
 'errors':errors,'actual_chrome_capture':'PH-BATH4_311B_310B_LID_R070.png',
 'viewer_sha256':hashlib.sha256((root/'deliverables/viewer3d/index.html').read_bytes()).hexdigest()}
(dest/'REVIEWER97_310B_FIX.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
if errors:raise SystemExit(1)
