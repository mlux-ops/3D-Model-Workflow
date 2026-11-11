"""Chrome prints current R035 HTML as actual paginated US Letter PDF."""
from pathlib import Path
import subprocess
import time
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'r035-13-owner-review-PROVISIONAL'
src=OUT/'R035_13_ROOM_OWNER_REVIEW_PAGES.html'
dst=ROOT/'scratch'/'r035_owner_reprint.pdf'
final=OUT/'R035_13_ROOM_OWNER_REVIEW_PAGES.pdf'
chrome=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
assert chrome.is_file() and src.is_file()
if dst.exists():
    dst.unlink()  # scratch-only temporary printer output
profile=ROOT/'scratch'/'r031_single_chrome_print'
cmd=[str(chrome),'--headless=new','--disable-gpu','--no-first-run',
     '--no-default-browser-check','--disable-extensions','--hide-scrollbars',
     '--user-data-dir='+str(profile),'--print-to-pdf='+str(dst),
     '--no-pdf-header-footer',src.as_uri()]
run=subprocess.run(cmd,capture_output=True,timeout=90)
for _ in range(40):
    if dst.exists() and dst.stat().st_size>150000:break
    time.sleep(.25)
assert dst.is_file() and dst.stat().st_size>150000,(run.returncode,run.stderr[-1200:])
shutil.copyfile(dst,final)
print('R035 printed and replaced provisional PDF',final, final.stat().st_size,'bytes', 'Chrome exit',run.returncode)
