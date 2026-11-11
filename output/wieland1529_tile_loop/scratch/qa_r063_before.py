"""R063 physical Chrome BEFORE screenshots of final R062 standalone HTML (no source writes)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
OUT=ROOT/'scratch/r063_before'; OUT.mkdir(exist_ok=True)
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
ROOMS=[('PH-BATH2','305A','305B'),('PH-BATH3','307A','307B'),
       ('TX-BATH2','205A','205B'),('TX-BATH3','207A','207B')]
images=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=CHROME,
   args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
 page.goto(URL+'#PH-BATH2/305A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug',timeout=30000)
 for kind,aa,bb in ROOMS:
  for n in [aa,bb]:
   page.evaluate('(x)=>window.__viewerDebug.loadInstanceAddress("#"+x)',kind+'/'+n)
   page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=30000)
   f=OUT/(kind+'_'+n+'_R062_FULL.png')
   page.screenshot(path=str(f));images.append(f)
   if n==aa:
    page.evaluate('window.__viewerDebug.setMode("study")')
    page.screenshot(path=str(OUT/(kind+'_'+n+'_R062_WET.png')))
    page.evaluate('window.__viewerDebug.setMode("full")')
 browser.close()
sheet=Image.new('RGB',(4*620,2*445),(18,29,37));d=ImageDraw.Draw(sheet)
for i,f in enumerate(images):
 im=Image.open(f).convert('RGB'); im.thumbnail((614,414))
 x=i%4*620;y=i//4*445
 sheet.paste(im,(x,y+24));d.text((x+9,y+5),f.stem,fill='white')
sheet.save(OUT/'R063_FOCUS_EIGHT_R062_BASELINE.png')
print('R062 physical Chrome baseline',len(images),'FULL,',len(ROOMS),'WET; no geometry/model edited')
