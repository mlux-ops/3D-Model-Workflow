"""R043 combined in-app QA scene assertions and full 13/13 gallery DOM verification."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
U=(R/'deliverables/viewer3d/index.html').as_uri()
OUT=R/'scratch/r043_arch_gallery'
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
results={};errs=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=CHROME,headless=True,
    args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 pg=b.new_page(viewport={'width':1500,'height':980})
 pg.on('pageerror',lambda e:errs.append('JS:'+str(e)))
 pg.goto(U+'#PH-BATH4/311A',wait_until='load')
 pg.wait_for_function('!!window.__viewerDebug',timeout=25000)
 receipt=pg.evaluate('window.__viewerDebug.qa()')
 results['internal_qa']={'probes':len(receipt['passed']),'fail':receipt['fail']}
 pg.goto(U+'?gallery=1#PH-BATH4/311A',wait_until='load')
 pg.wait_for_function('document.getElementById("viewer-gallery")?.dataset.status === "COMPLETE" || document.getElementById("viewer-gallery")?.dataset.status === "FIX"',timeout=180000)
 results['gallery_status']=pg.get_attribute('#viewer-gallery','data-status')
 results['gallery_card_images']=pg.locator('#viewer-gallery img').count()
 results['gallery_data_status']=pg.evaluate('document.body.dataset.viewerGallery')
 results['gallery_errors']=pg.evaluate('window.__viewerDebug.errors.slice()')
 if results['gallery_status']=='COMPLETE':
  pg.screenshot(path=str(OUT/'R043_IN_APP_13_GALLERY_COMPLETE.png'))
 b.close()
results['errors']=errs
(R/'scratch/r043_inapp_qa_result.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2)[:22000])
if errs or results['internal_qa']['fail'] or results['gallery_status']!='COMPLETE' or results['gallery_card_images']!=13:
 raise SystemExit(1)
