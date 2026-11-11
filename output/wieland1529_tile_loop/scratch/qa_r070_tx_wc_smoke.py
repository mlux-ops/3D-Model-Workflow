"""Two additional inherited TX-WC instance checks for shared R070 wall/light code.
Standalone local Chrome physical frames, no legacy/full suites.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
out=root/'scratch/r070_focus/after'
errors=[];photos=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1480,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((root/'deliverables/viewer3d/index.html').as_uri()+'#TX-WC/203A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=45000)
 page.locator('#viewer-focus-enter').click()
 for n in ['203A','203B']:
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#TX-WC/"+s)',n)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=23000)
  e=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  cats=[x['category'] for x in e]
  if not any(x=='ARCH_R070_PLASTER_FACE_STUDY' for x in cats):
   errors.append('TX WC source-native wall optical missing '+n)
  if any(x=='ARCH_R070_WOOD_FLOOR_MICRORELIEF' for x in cats):
   errors.append('WC inherited neutral floor mistakenly wood '+n)
  if any(x=='ARCH_REGISTERED_FLOOR' and y.get('r063_floor_material_selected') is True for x,y in [(o['category'],o) for o in e]):
   errors.append('WC got selected floor SKU '+n)
  if any(x=='ARCH_NATIVE_COUNTERTOP_VISUAL' for x in cats):
   errors.append('WC got unsupported countertop '+n)
  page.locator('#viewer-focus-iso').click()
  name='TX-WC_'+n+'_R070_SHARED_ISO.png'
  page.locator('#stage').screenshot(path=str(out/name));photos.append(name)
  page.evaluate('window.__viewerDebug.setCamera("r067-wc-survey")')
  name='TX-WC_'+n+'_R070_SHARED_DETAIL.png'
  page.locator('#stage').screenshot(path=str(out/name));photos.append(name)
 if page.evaluate('window.__viewerDebug.errors'):
  errors.append('runtime '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()
receipt={'status':'PASS' if not errors else 'FIX','changed_by_shared_code':'TX-WC 203A/203B source-native plaster and camera, inherited WC neutral floor retained',
 'cases':['TX-WC/203A','TX-WC/203B'],
 'actual_chrome_images':photos,'errors':errors,
 'no_full_26_or_78_suite':True}
(out/'TX_WC_R070_SHARED_RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(receipt,indent=2))
if errors:raise SystemExit(1)
