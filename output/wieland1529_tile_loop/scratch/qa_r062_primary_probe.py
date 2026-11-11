"""Read-only Chrome source/visual diagnostic of existing primary scenes before R062 changes."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
url=(root/'deliverables/viewer3d/index.html').as_uri()
chrome=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=chrome,
    args=['--enable-unsafe-swiftshader','--use-angle=swiftshader'])
 page=browser.new_page(viewport={'width':1500,'height':980})
 page.goto(url+'#PH-PRIMARY/304A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug')
 for k in ('PH-PRIMARY/304A','PH-PRIMARY/304B','TX-PRIMARY/202A','TX-PRIMARY/202B',
  'PH-BATH4/311A','TX-BATH4/007A'):
  page.evaluate('(v)=>window.__viewerDebug.loadInstanceAddress("#"+v)',k)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
  objs=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  print('\n'+k,'objects',len(objs))
  for x in objs:
   if x['category'] in ('FULL_ROOM_WET_WALL','FULL_ROOM_SELECTED_PAN_SCHEMATIC',
    'PLAN_SCHEMATIC_FIXTURE','ARCH_NATIVE_CASEWORK_AABB_STUDY',
    'ARCH_NATIVE_COUNTERTOP_VISUAL','ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL'):
    print(x['category'],'kind',x['kind'],'wall',x['wall'],
     'visible',x['visible'],'pos',[round(v,3) for v in x['position']],
     'host',x['native_host_face_id'],'supported',x['source_return_supported'],
     'source',x['source'][:100])
 browser.close()
