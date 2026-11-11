"""Render each prepared tub option board in Chrome and make visual QA contact sheet."""
from pathlib import Path
import subprocess,time
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'r035-3-duravit-tub-comparison-PREPARED'
QA=ROOT/'scratch'/'r035_tub_board_qa'
QA.mkdir(parents=True,exist_ok=True)
CHROME=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
PROFILE=ROOT/'scratch'/'r031_single_chrome_print'
ids=('PH-BATH2','TX-BATH2','TX-BATH4')
for id in ids:
 html=OUT/(id+'_A_B_PREPARED.html')
 png=QA/(id+'.png')
 if png.is_file():png.unlink()
 argv=[str(CHROME),'--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--hide-scrollbars',
       '--window-size=1300,1000','--force-device-scale-factor=1','--user-data-dir='+str(PROFILE),
       '--screenshot='+str(png),html.as_uri()]
 p=subprocess.run(argv,capture_output=True,timeout=30)
 for _ in range(20):
  if png.is_file() and png.stat().st_size>8000:break
  time.sleep(.15)
 assert png.is_file() and png.stat().st_size>8000,(id,p.returncode,p.stderr[:200])
 print(id,png.stat().st_size,flush=True)
canvas=Image.new('RGB',(1200,1050*len(ids)),'#e8e8e8')
d=ImageDraw.Draw(canvas)
for i,id in enumerate(ids):
 with Image.open(QA/(id+'.png')) as im:
  im=im.convert('RGB')
  im.thumbnail((1170,1000),Image.Resampling.LANCZOS)
  canvas.paste(im,((1200-im.width)//2,i*1050+40))
 d.text((25,i*1050+10),id,fill='#222222')
dest=ROOT/'scratch'/'r035_tub_visual_comparison_contact_sheet.png'
canvas.save(dest,optimize=True)
print('PASS',dest)
