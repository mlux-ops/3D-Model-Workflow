from pathlib import Path
import json, hashlib, zipfile, re
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'output/belmont_preferred_bath2_bath3_r2'
native=json.loads((folder/'revit_validation.json').read_text())
assert native['success'] and native['count']==6 and native['warnings']==0
assert (folder/'native_complete.txt').is_file()
checks=json.loads((folder/'map_validation.json').read_text(encoding='utf-8-sig'))
assert len(checks)==6 and all(not r['failures'] for r in checks)
files=[p for p in sorted(folder.rglob('*')) if p.is_file() and not re.search(r'\.\d{4}\.rvt$',p.name) and p.name not in ['error.txt','package_inventory.json']]
inventory=[]
for p in files:
    inventory.append({'file':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
(folder/'package_inventory.json').write_text(json.dumps(inventory,indent=2))
files.append(folder/'package_inventory.json')
archive=ROOT/'output/651_Belmont_Preferred_Tiles_R2025_R2_Corrected_Review.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
    for p in files:z.write(p,folder.name+'/'+p.relative_to(folder).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.rvt')])==1
    assert len([n for n in z.namelist() if '/textures/' in n])==18
report={'file':str(archive),'bytes':archive.stat().st_size,'entries':len(files),
        'sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),
        'md5':hashlib.file_digest(archive.open('rb'),'md5').hexdigest(),'zip_integrity':'pass'}
(ROOT/'output/belmont_preferred_r2_package_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
