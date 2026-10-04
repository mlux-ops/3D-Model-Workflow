"""Preserve an explicitly identified browser download inside this section."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('key')
parser.add_argument('url')
args=parser.parse_args()
source=Path(args.input)
out=ROOT/args.key/'downloads';out.mkdir(parents=True,exist_ok=True)
target=out/source.name
if not target.exists():shutil.copy2(source,target)
record={'source_url':args.url,'source_path':str(source),'path':str(target),
        'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'access':'Public browser download; no sign-in, license acceptance or credentials supplied.'}
if zipfile.is_zipfile(target):
    with zipfile.ZipFile(target) as archive:
        record['archive_members']=archive.namelist();record['rfa_paths']=[]
        for entry in archive.infolist():
            name=Path(entry.filename).name
            if Path(name).suffix.lower() in ('.rfa','.pdf','.txt','.dwg','.dxf'):
                dest=out/(target.stem+'_files')/name;dest.parent.mkdir(exist_ok=True)
                if not dest.exists():dest.write_bytes(archive.read(entry))
                if dest.suffix.lower()=='.rfa':record['rfa_paths'].append(str(dest))
(target.with_name(target.name+'.browser_receipt.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
