"""Print and physically verify three R036 neutral new-wet-bath design option sheets."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageDraw
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'r036-3-wet-bath-comparison-UNSCORED'
HTML=OUT/'R036_THREE_WET_BATHS_SIDE_BY_SIDE_UNSCORED.html'
PDF=OUT/'R036_THREE_WET_BATHS_SIDE_BY_SIDE_UNSCORED.pdf'
CHROME=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
PROFILE=ROOT/'scratch'/'r031_single_chrome_print'
assert HTML.is_file() and CHROME.is_file()
if not PDF.exists():
    argv=[str(CHROME),'--headless=new','--disable-gpu','--no-first-run',
          '--no-default-browser-check','--disable-extensions',
          '--user-data-dir='+str(PROFILE),'--no-pdf-header-footer',
          '--print-to-pdf='+str(PDF),HTML.as_uri()]
    result=subprocess.run(argv,timeout=90,capture_output=True)
    for _ in range(40):
        if PDF.is_file() and PDF.stat().st_size>100000:break
        time.sleep(.25)
    assert PDF.is_file() and PDF.stat().st_size>100000,(result.returncode,result.stderr[-1000:])
r=PdfReader(PDF)
ids=('PH-BATH4','PH-BATH3','TX-BATH3')
assert len(r.pages)==3,len(r.pages)
QA=ROOT/'scratch'/'r036_three_wet_bath_visual_qa'
QA.mkdir(parents=True,exist_ok=True)
for idx,(room,page) in enumerate(zip(ids,r.pages),1):
    text=page.extract_text() or ''
    assert room in text and 'Neutral candidate A' in text and 'Neutral candidate B' in text,(idx,room)
    assert 'UNSCORED' in text and '15% waste ONCE' in text,(idx,room)
    assert 790 <=float(page.mediabox.width)<=795 and 610<=float(page.mediabox.height)<=614,(idx,room,page.mediabox)
    assert len(page.images)>=4,(room,len(page.images))
    w=PdfWriter();w.add_page(page)
    dst=OUT/(room+'_A_B_UNSCORED.pdf')
    with dst.open('wb') as handle:w.write(handle)
    assert len(PdfReader(dst).pages)==1
    print(idx,room,'1 landscape US Letter, text',len(text),'images',len(page.images))
print('PASS R036 three original manufacturer-image neutral comparison PDFs, no owner approval or reviewed scores')
