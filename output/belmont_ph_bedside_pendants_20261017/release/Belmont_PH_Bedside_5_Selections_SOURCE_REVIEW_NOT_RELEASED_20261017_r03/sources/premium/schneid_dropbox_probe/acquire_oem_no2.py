"""Acquire one factory ZIP with streaming I/O and extract only Lamp No.2."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[1]
SRC = next(x for x in json.loads((BASE / 'OEM_SOURCE_MANIFEST.json').read_text(encoding='utf-8-sig')) if x['id'] == 'schneid_stucco_dropbox_3d')
ARCHIVE = BASE / 'originals' / 'SCHNEID_Stucco_Share_3D.zip'
PART = ARCHIVE.with_suffix('.zip.part')
DEST = BASE / 'schneid_official_no2'

if not ARCHIVE.is_file():
    if PART.exists():
        raise RuntimeError(f'Partial download present, preserve it for inspection: {PART}')
    req = Request(SRC['url'], headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    with urlopen(req, timeout=45) as source:
        expected = int(source.headers['Content-Length'])
        if expected != 186260124:
            raise RuntimeError(f'Unexpected manufacturer archive size: {expected}')
        with PART.open('xb') as target:
            shutil.copyfileobj(source, target, length=1024 * 1024)
    if PART.stat().st_size != expected:
        raise RuntimeError(f'Incomplete transfer {PART.stat().st_size} / {expected}')
    PART.replace(ARCHIVE)

sha = hashlib.sha256()
with ARCHIVE.open('rb') as stream:
    for block in iter(lambda: stream.read(2 * 1024 * 1024), b''):
        sha.update(block)
receipt = {'archive_path': str(ARCHIVE), 'bytes': ARCHIVE.stat().st_size,
           'sha256': sha.hexdigest(), 'entries': [], 'no2': [], 'rfa_entries': []}
with zipfile.ZipFile(ARCHIVE) as z:
    for item in z.infolist():
        receipt['entries'].append({'name': item.filename, 'bytes': item.file_size})
        if item.filename.lower().endswith('.rfa'):
            receipt['rfa_entries'].append(item.filename)
        if item.filename.startswith('Stucco Lamp No.2/') and not item.is_dir():
            if item.file_size > 120 * 1024 * 1024:
                raise RuntimeError(f'No.2 member over extraction cap: {item.filename}')
            out = DEST / Path(item.filename).relative_to('Stucco Lamp No.2')
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as reader, out.open('xb') as writer:
                shutil.copyfileobj(reader, writer, length=1024 * 1024)
            digest = hashlib.sha256(out.read_bytes()).hexdigest()
            receipt['no2'].append({'name': item.filename, 'bytes': item.file_size, 'sha256': digest, 'local': str(out)})
    bad = z.testzip()
    receipt['zip_crc_error'] = bad
receipt_path = BASE / 'schneid_dropbox_probe' / 'SCHNEID_OEM_ARCHIVE_RECEIPT.json'
receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'archive_sha256': receipt['sha256'], 'bytes': receipt['bytes'], 'total_entries': len(receipt['entries']), 'no2': receipt['no2'], 'rfa_entries': receipt['rfa_entries'], 'zip_crc_error': receipt['zip_crc_error'], 'receipt': str(receipt_path)}, indent=2))
