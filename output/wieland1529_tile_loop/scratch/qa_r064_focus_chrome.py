"""Short R064 regression: immersive viewport + two physical A/B room pairs only."""
from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/r064_focus';OUT.mkdir(exist_ok=True)
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
PICKS=ROOT/'deliverables/viewer3d/picks.json'
before=hashlib.sha256(PICKS.read_bytes()).hexdigest()
errors=[];checks=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
   args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1560,'height':960},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append('PAGE_ERROR:'+str(e)))
 page.goto(URL+'#PH-BATH3/307A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=30000)
 assert page.evaluate('window.__viewerDebug.getState().focusView') is False
 defaultBox=page.locator('#stage').bounding_box()
 page.screenshot(path=str(OUT/'PH-BATH3_307A_R063_DEFAULT.png'))
 page.locator('#viewer-focus-enter').click()
 assert page.evaluate('window.__viewerDebug.getState().focusView') is True
 assert page.locator('#viewer-v2-toolbar').is_hidden()
 assert page.locator('#viewer-focus-bar').is_visible()
 focusBox=page.locator('#stage').bounding_box()
 assert focusBox['x']==0 and focusBox['y']==0,focusBox
 assert focusBox['width']>=1559 and focusBox['height']>=959,focusBox
 # 1560px-wide standard 3-column UI gives the renderer ~940px. Immersive
 # stage gains ~1.8x canvas area on this viewport, not a universal 2x.
 assert focusBox['width']*focusBox['height']>1.6*defaultBox['width']*defaultBox['height']
 assert page.locator('#viewer-focus-title').inner_text()=='PH-BATH3 · 307A'
 page.screenshot(path=str(OUT/'PH-BATH3_307A_R064_FOCUS.png'))
 checks.append('full-viewport canvas >1.6x standard desktop area, source geometry unchanged')
 page.locator('#viewer-focus-ab').click()
 assert page.locator('#viewer-ab-drawer').is_visible()
 page.locator('#viewer-focus-ab').click()
 assert page.locator('#viewer-ab-drawer').is_hidden()
 page.locator('#viewer-focus-traces').click()
 assert page.evaluate('window.__viewerDebug.getState().sourceTraces') is True
 page.locator('#viewer-focus-traces').click()
 assert page.evaluate('window.__viewerDebug.getState().sourceTraces') is False
 checks.append('full-screen A/B and native source trace controls reversible')
 page.locator('#viewer-focus-instance').select_option('307B')
 page.wait_for_function('document.body.dataset.viewerMaterials==="READY"')
 assert page.evaluate('document.body.dataset.viewerInstance')=='307B'
 assert page.evaluate('window.__viewerDebug.getState().focusView') is True
 page.locator('#viewer-focus-room').select_option('TX-BATH2')
 page.wait_for_function('document.body.dataset.viewerMaterials==="READY"')
 page.locator('#viewer-focus-instance').select_option('205B')
 page.wait_for_function('document.body.dataset.viewerMaterials==="READY"')
 assert page.evaluate('document.body.dataset.viewerInstance')=='205B'
 assert page.evaluate('document.body.dataset.viewerRoom')=='TX-BATH2'
 page.locator('#viewer-focus-wet').click()
 assert page.evaluate('window.__viewerDebug.getCameraInfo().preset')=='wet'
 ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
 assert len([x for x in ev if x['category']=='FULL_ROOM_WET_WALL'])>=3
 page.screenshot(path=str(OUT/'TX-BATH2_205B_R064_FOCUS_WET.png'))
 checks.append('A/B change, deep link, room switch and existing wet finish in focus')
 page.locator('#viewer-focus-plan').click()
 assert page.evaluate('window.__viewerDebug.getCameraInfo().preset')=='top'
 page.locator('#viewer-focus-iso').click()
 assert page.evaluate('window.__viewerDebug.getCameraInfo().preset')=='isometric'
 page.keyboard.press('Escape')
 assert page.evaluate('window.__viewerDebug.getState().focusView') is False
 assert page.locator('#viewer-v2-toolbar').is_visible()
 assert page.locator('#viewer-focus-bar').is_hidden()
 page.locator('#viewer-focus-enter').click()
 page.locator('#viewer-focus-evidence').click()
 assert page.evaluate('window.__viewerDebug.getState().focusView') is False
 assert page.locator('#viewer-v2-evidence').evaluate('(el)=>el.open') is True
 checks.append('camera presets, Escape/Exit and source inspector restoration')
 assert not page.evaluate('window.__viewerDebug.errors')
 browser.close()
assert before==hashlib.sha256(PICKS.read_bytes()).hexdigest(),'Frozen picks changed'
assert not errors,errors
receipt={'status':'PASS','focus_physical_instances':['PH-BATH3/307A','PH-BATH3/307B',
 'TX-BATH2/205A','TX-BATH2/205B'],'checks':checks,'errors':errors,'frozen_picks_sha256':before}
(OUT/'R064_FOCUS_RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(receipt,indent=2))
