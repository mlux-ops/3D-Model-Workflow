"""Build a local source/binary/evidence archive; never includes state tokens or Autodesk DLLs."""
import hashlib
import json
import argparse
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parent
delivery=root/'delivery';delivery.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--name',default='CodexNativeRevit2025-20261014.zip');options=parser.parse_args()
if Path(options.name).name!=options.name or not options.name.endswith('.zip'):raise RuntimeError('Archive name must be a plain .zip filename')
archive=delivery/options.name
if archive.exists():raise RuntimeError('Archive exists; use a new filename rather than replacing a delivered artifact.')
excluded={'obj','__pycache__','delivery','.git','Debug'}
files=[p for p in root.rglob('*') if p.is_file() and not excluded.intersection(p.relative_to(root).parts)
       and p.suffix.lower() not in {'.pyc','.tmp','.zip'} and p.name not in {'verification-index.json'}]
if any(p.name.lower() in {'revitapi.dll','revitapiui.dll','token','auth.json','.env'} for p in files):
    raise RuntimeError('Private credential or Autodesk runtime file detected in package')
index={'package_identity':'codex-native-revit-2025','schema_version':1,
    'completion_status':'tested development implementation; limitations in capability matrix',
    'files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]}
manifest=root/'verification-index.json';manifest.write_text(json.dumps(index,indent=2),encoding='utf-8');files.append(manifest)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('Archive CRC verification failed')
    for row in index['files']:
        if hashlib.sha256(z.read(row['path'])).hexdigest()!=row['sha256']:raise RuntimeError('Archive payload hash mismatch')
receipt={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
    'payload_files':len(files),'archive_crc_and_payload_hashes_verified':True}
(delivery/'archive-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
