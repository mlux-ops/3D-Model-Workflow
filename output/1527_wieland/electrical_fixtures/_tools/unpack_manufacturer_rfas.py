"""Inspect ZIP members and extract manufacturer RFA content under its source folder."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
records=[json.loads(p.read_text()) for p in ROOT.glob('*/source/*.zip.acquisition.json')]
manifest=[]
for record in records:
    if record.get('error'):continue
    archive=Path(record['path'])
    destination=archive.parent/(archive.stem+'_contents')
    destination.mkdir(exist_ok=True)
    with ZipFile(archive) as package:
        bad=package.testzip()
        if bad:raise RuntimeError('ZIP CRC failure: '+bad)
        for member in package.infolist():
            part=PurePosixPath(member.filename)
            if part.is_absolute() or '..' in part.parts:raise RuntimeError('Unexpected ZIP path')
            if member.is_dir() or part.suffix.lower() not in ('.rfa','.txt','.pdf'):continue
            if member.file_size>100*1024*1024:raise RuntimeError('Unexpected native resource size')
            target=destination/Path(*part.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            data=package.read(member)
            if not target.exists():target.write_bytes(data)
            manifest.append({'path':str(target),'source_archive':str(archive),'source_url':record['url'],
                             'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'extension':part.suffix.lower()})
            print(archive.name+' | '+member.filename+' | '+str(len(data)))
(ROOT/'OEM_EXTRACTED_FILES.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
