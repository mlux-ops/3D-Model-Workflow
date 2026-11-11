"""Actual local-file Chrome rendering/navigation QA, no Revit or source writes.

All evidence written into scratch/, never into frozen decisions or owner packets.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'deliverables/viewer3d/index.html'
payload=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf-8'))
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL=HTML.as_uri()
out=ROOT/'scratch'
results=[]
errors=[]
shots={'PH-BATH4/311A','PH-BATH4/311B','PH-BATH3/307A','TX-BATH2/205A',
       'TX-BATH3/207A','PH-WC/314A','TX-POWDER2/010A','PH-PRIMARY/304A'}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1550,'height':1050},device_scale_factor=1)
 page.on('pageerror',lambda err:errors.append(str(err)))
 page.goto(URL+'#PH-BATH4/311A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMode==="full"',timeout=15000)
 for room in payload['rooms']:
  for inst in room['physical_instances']:
   key=room['id']+'/'+inst['room_number']
   ok=page.evaluate('hash=>window.__viewerDebug.loadInstanceAddress(hash)', '#'+key)
   observed=page.evaluate('''() => ({
      room:document.body.dataset.viewerRoom,
      instance:document.body.dataset.viewerInstance,
      mode:document.body.dataset.viewerMode,
      objects:window.__viewerDebug.getState().objectCount,
      errors:window.__viewerDebug.errors.slice()
    })''')
   if not ok or observed['room']!=room['id'] or observed['instance']!=inst['room_number'] or observed['mode']!='full':
    errors.append('BAD DIRECT LINK '+key+' '+str(observed))
   if observed['objects']<4:
    errors.append('INSUFFICIENT FULL ROOM OBJECTS '+key+' '+str(observed['objects']))
   results.append({'key':key,'objects':observed['objects'],'full_mode':observed['mode']})
   if key in shots:
    page.wait_for_timeout(370)
    page.screenshot(path=str(out/('r042_latest_'+key.replace('/','_')+'.png')))
 # Actual mode navigation, camera preset and pointer testing.
 page.evaluate('window.__viewerDebug.loadInstanceAddress("#PH-BATH4/311B")')
 page.locator('#viewer-mode-study').click()
 if page.evaluate('document.body.dataset.viewerMode')!='study':errors.append('WET ZONE MODE CLICK FAILED')
 page.locator('#viewer-mode-context').click()
 if page.evaluate('document.body.dataset.viewerMode')!='context':errors.append('CONTEXT MODE CLICK FAILED')
 page.locator('#viewer-mode-full').click()
 if page.evaluate('document.body.dataset.viewerMode')!='full':errors.append('FULL ROOM MODE CLICK FAILED')
 canvas=page.locator('canvas').first
 box=canvas.bounding_box()
 if box:
  x=box['x']+box['width']*.5;y=box['y']+box['height']*.5
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+87,y-36,steps=7);page.mouse.up()
  page.mouse.wheel(0,-220)
  page.wait_for_timeout(400)
  page.screenshot(path=str(out/'r042_latest_ph4_orbit_zoom.png'))
 else:errors.append('CANVAS NOT PRESENT')
 errors+=page.evaluate('window.__viewerDebug.errors.slice()')
 browser.close()
summary={'status':'PASS' if not errors else 'FIX','physical_instances':len(results),
 'full_room_entries':results,'saved_screenshots':sorted([str(x.name) for x in out.glob('r042_latest_*.png')]),'errors':errors}
(out/'r042_floorplan_browser_result.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='full_room_entries'},indent=2))
if errors:raise SystemExit(1)
