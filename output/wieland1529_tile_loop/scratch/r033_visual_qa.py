"""Produce an owner-page visual QA contact sheet from the current HTML print sources.

PDF pagination/text checks are separately performed by r033_verify_split_owner_pdf.py.
Chrome uses the already established local profile; no downloaded libraries or browser ports.
"""
from pathlib import Path
import subprocess
import time
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / 'r033-13-owner-review-PROVISIONAL'
QA = ROOT / 'scratch' / 'r033_visual_qa'
QA.mkdir(parents=True, exist_ok=True)
CHROME = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
PROFILE = ROOT / 'scratch' / 'r031_single_chrome_print'
IDS = ('PH-PRIMARY','PH-BATH2','PH-BATH3','PH-BATH4','PH-POWDER','PH-WC',
       'TX-PRIMARY','TX-BATH2','TX-BATH3','TX-BATH4','TX-POWDER','TX-POWDER2','TX-WC')
assert CHROME.is_file()
assert len(IDS) == 13

for id in IDS:
    html = OUT / (id + '.html')
    assert html.is_file()
    dest = QA / (id + '.png')
    if dest.exists():
        dest.unlink()
    argv = [str(CHROME), '--headless=new', '--disable-gpu', '--no-first-run',
            '--no-default-browser-check', '--hide-scrollbars',
            '--window-size=1100,1400', '--force-device-scale-factor=1',
            '--user-data-dir=' + str(PROFILE), '--screenshot=' + str(dest),
            html.as_uri()]
    done = subprocess.run(argv, capture_output=True, timeout=30)
    for _ in range(20):
        if dest.exists() and dest.stat().st_size > 6000:
            break
        time.sleep(.15)
    assert dest.is_file() and dest.stat().st_size > 6000, (id, done.returncode,done.stderr[:350])
    with Image.open(dest) as im:
        assert im.size[0] >= 900 and im.size[1] >= 1050, (id, im.size)
    print(id, dest.stat().st_size, 'bytes', flush=True)

cols, thumb_w, thumb_h = 4, 460, 610
rows = (len(IDS) + cols - 1) // cols
sheet = Image.new('RGB',(cols*thumb_w, rows*thumb_h), '#e8e8e8')
d = ImageDraw.Draw(sheet)
for i,id in enumerate(IDS):
    with Image.open(QA / (id + '.png')) as im:
        # Chrome full window contains centered white Letter paper.
        im = im.convert('RGB')
        crop = im.crop((125,12,975,1135))
        crop.thumbnail((thumb_w-22,thumb_h-42),Image.Resampling.LANCZOS)
        sheet.paste(crop,(i%cols*thumb_w+(thumb_w-crop.width)//2,
                          i//cols*thumb_h+30))
    d.text((i%cols*thumb_w+13,i//cols*thumb_h+8),id,fill='#111111')
dest = ROOT / 'scratch' / 'r033_owner_packet_contact_sheet.png'
sheet.save(dest,optimize=True)
print('PASS contact sheet',dest,sheet.size)
