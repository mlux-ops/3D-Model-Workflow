"""Preserve public manufacturer resources for the Wieland appliance families."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
ASSETS = [
    ('miele_h7280bp', 'manufacturer.zip', 'https://media.miele.com/downloads/1d/33/01_C7F12828C0C31FE182DC54A63F5A1D33.zip'),
    ('miele_h7270bm', 'manufacturer.zip', 'https://media.miele.com/downloads/8b/20/02_C7F138387FFA1FD189C793AEE9B58B20.zip'),
    ('miele_g5051scvi', 'manufacturer.zip', 'https://media.miele.com/downloads/a5/52/10_70A8A51285B71FE1ABFC9D443DCBA552.zip'),
    ('miele_h7280bp', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_11968200_USE_US-en-US.pdf'),
    ('lg_wm4000hba', 'product_sheet.pdf', 'https://media.us.lg.com/m/1c4e8c8e7a284ef2/original/WM4000H_A-LG-Builder-Spec-Sheet.pdf'),
]

def fetch(asset):
    slug, name, url = asset
    folder = ROOT / slug / 'source'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    result = dict(item=slug, url=url, path=str(path))
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
            result['content_type'] = response.headers.get('Content-Type')
        path.write_bytes(payload)
        result.update(size=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        if name.endswith('.zip'):
            with zipfile.ZipFile(path) as archive:
                result['entries'] = archive.namelist()
                for entry in archive.infolist():
                    dest = (folder / 'original' / entry.filename).resolve()
                    if not dest.is_relative_to((folder / 'original').resolve()):
                        raise ValueError('Archive entry escapes source folder')
                    if not entry.is_dir():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(archive.read(entry))
        elif name.endswith('.pdf') and not payload.startswith(b'%PDF'):
            raise ValueError('Response is not a PDF')
        result['ok'] = True
    except Exception as exc:
        result.update(ok=False, error=str(exc))
    return result

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, ASSETS))
    (ROOT / 'source_downloads.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    for result in results:
        print(json.dumps(result))
