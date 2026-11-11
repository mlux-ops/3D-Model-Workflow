"""Raster visual QA from original R036 HTML using the existing headless Chrome profile."""
from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'r036-3-wet-bath-comparison-UNSCORED'
QA=ROOT/'scratch'/'r036_three_wet_bath_visual_qa'
QA.mkdir(parents=True,exist_ok=True)
CHROME=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
PROFILE=ROOT/'scratch'/'r031_single_chrome_print'
ids=('PH-BATH4','PH-BATH3','TX-BATH3')
for rid in ids:
    source=OUT/(rid+'_A_B_UNSCORED.html')
    dest=QA/(rid+'.png')
    assert source.is_file()
    if dest.exists():
        dest.unlink()
    argv=[str(CHROME),'--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
          '--hide-scrollbars','--window-size=1500,1080','--force-device-scale-factor=1',
          '--user-data-dir='+str(PROFILE),'--screenshot='+str(dest),source.as_uri()]
    result=subprocess.run(argv,timeout=40,capture_output=True)
    for _ in range(30):
        if dest.exists() and dest.stat().st_size>10000:break
        time.sleep(.2)
    assert dest.is_file() and dest.stat().st_size>10000,(rid,result.stderr[-1000:])
    with Image.open(dest) as img:
        assert img.width>=1200 and img.height>=850
    print(rid,dest.stat().st_size,'bytes')
sheet=Image.new('RGB',(1320,3*700),'#e7e7e7')
draw=ImageDraw.Draw(sheet)
for i,rid in enumerate(ids):
    with Image.open(QA/(rid+'.png')) as img:
        image=img.convert('RGB')
        image.thumbnail((1280,655),Image.Resampling.LANCZOS)
        sheet.paste(image,((1320-image.width)//2,i*700+28))
    draw.text((14,i*700+8),rid,fill='#161616')
target=ROOT/'scratch'/'r036_three_wet_bath_visual_contact_sheet.png'
sheet.save(target,optimize=True)
print('PASS contact',target,sheet.size)
