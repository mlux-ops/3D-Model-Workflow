"""Print and physically validate the authentic R038 13-room PROVISIONAL owner set."""
from pathlib import Path
import subprocess, shutil, time
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / 'r038-13-owner-review-PROVISIONAL'
SRC = OUT / 'R038_13_ROOM_OWNER_REVIEW_PAGES.html'
FINAL = OUT / 'R038_13_ROOM_OWNER_REVIEW_PAGES.pdf'
TEMP = ROOT / 'scratch' / 'r038_owner_reprint.pdf'
CHROME = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
PROFILE = ROOT / 'scratch' / 'r031_single_chrome_print'
IDS = ('PH-PRIMARY','PH-BATH2','PH-BATH3','PH-BATH4','PH-POWDER','PH-WC',
       'TX-PRIMARY','TX-BATH2','TX-BATH3','TX-BATH4','TX-POWDER','TX-POWDER2','TX-WC')
assert SRC.is_file() and CHROME.is_file()
if TEMP.exists(): TEMP.unlink()  # scratch-only
args = [str(CHROME), '--headless=new', '--disable-gpu', '--no-first-run',
        '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars',
        '--user-data-dir='+str(PROFILE), '--print-to-pdf='+str(TEMP),
        '--no-pdf-header-footer', SRC.as_uri()]
job = subprocess.run(args, capture_output=True, timeout=100)
for _ in range(30):
    if TEMP.is_file() and TEMP.stat().st_size > 100000: break
    time.sleep(.2)
assert TEMP.is_file() and TEMP.stat().st_size > 100000, (job.returncode,job.stderr[-1200:])
reader = PdfReader(TEMP)
assert len(reader.pages) == 13, len(reader.pages)
for n,(room,page) in enumerate(zip(IDS,reader.pages),1):
    text = page.extract_text() or ''
    assert room in text and 'OWNER TILE REVIEW' in text, (room,'wrong header')
    assert 'UNRESOLVED OWNER' in text and 'MATERIAL-ONLY COST BASIS' in text, (room,'missing owner material/holds')
    assert 'not a final approved selection' in text.lower(), (room,'missing provisional disclaimer')
    assert int(float(page.mediabox.width))==612 and int(float(page.mediabox.height))==792, (room,'not Letter')
    assert len(text) >= 850, (room, 'empty/nonsearchable page')
    writer = PdfWriter(); writer.add_page(page)
    with (OUT/(room+'.pdf')).open('wb') as f: writer.write(f)
    assert len(PdfReader(OUT/(room+'.pdf')).pages)==1
    print(f'{n:02d} {room:14} US Letter, searchable text={len(text)}',flush=True)
shutil.copyfile(TEMP,FINAL)

# Physical visual QA without installing dependencies: the project's current
# Windows runtime has Chrome, Pillow and pypdf but not fitz/pdfium/poppler.
# Reuse the established single Chrome profile to raster each *same source*
# individual Letter-print HTML and inspect all pages on a contact sheet.
QA = ROOT / 'scratch' / 'r038_owner_visual_qa'
QA.mkdir(parents=True,exist_ok=True)
thumbs = []
for n,room in enumerate(IDS,1):
    pdf_page=reader.pages[n-1]
    assert len(pdf_page.images) >= 1, (room,'no embedded PDF image')
    src = OUT/(room+'.html')
    assert src.is_file(),(room,'missing room source HTML')
    dest = QA/(room+'.png')
    if dest.exists(): dest.unlink() # scratch-only prior screenshot
    argv=[str(CHROME),'--headless=new','--disable-gpu','--no-first-run',
          '--no-default-browser-check','--hide-scrollbars',
          '--window-size=1100,1400','--force-device-scale-factor=1',
          '--user-data-dir='+str(PROFILE),'--screenshot='+str(dest),src.as_uri()]
    done=subprocess.run(argv,capture_output=True,timeout=35)
    for _ in range(30):
        if dest.exists() and dest.stat().st_size>5000:break
        time.sleep(.15)
    assert dest.is_file() and dest.stat().st_size>5000,(room,'screenshot failed',done.stderr[-300:])
    with Image.open(dest) as pic:
        assert pic.width>=900 and pic.height>=1050,(room,pic.size)
        im=pic.convert('RGB').crop((125,12,975,1135))
        im.thumbnail((430,550),Image.Resampling.LANCZOS)
        thumbs.append((room,im.copy()))
    print('VISUAL',room,len(pdf_page.images),'embedded PDF images',dest.stat().st_size,'raster bytes',flush=True)
sheet=Image.new('RGB',(4*450,4*590),'#ededed')
dr=ImageDraw.Draw(sheet)
for i,(room,im) in enumerate(thumbs):
    x=(i%4)*450; y=(i//4)*590
    sheet.paste(im,(x+(450-im.width)//2,y+25))
    dr.text((x+10,y+5),room,fill='#111111')
contact=ROOT/'scratch'/'r038_owner_contact_sheet.png'
sheet.save(contact,optimize=True)
print('PASS: 13-page PDF, 13 searchable Letter single-page PDFs with embedded images, 13 owner-page Chrome rasters and visual contact sheet:',contact)
