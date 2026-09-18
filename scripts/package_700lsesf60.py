from pathlib import Path
import json, zipfile, hashlib, shutil
root=Path(__file__).resolve().parents[1]
out=root/'output'/'700lsesf60'
v=json.loads((out/'validation.json').read_text())
assert v['stage']=='complete' and v['reopened'] and v['loaded_and_face_placed']
assert not v['warnings'] and not v['project_warnings']
assert all(x['pass'] for x in v['flex_tests']) and all(v['material_tests'].values())
assert abs(v['body_bounds_inches'][3]-v['body_bounds_inches'][0]-60)<1e-6
assert abs(v['body_bounds_inches'][5]-v['body_bounds_inches'][2]-4.8)<1e-6
files=[out/'700LSESF60_Black_Adjustable_R2025.rfa',out/'700LSESF60_Body.rfa',out/'README.md',out/'REVIEW.md',out/'validation.json']
files+=list(out.glob('*.png'))+[out/'appearance_audit.json']
for path in files: assert path.is_file() and path.stat().st_size>0
archive=out/'700LSESF60_Black_Adjustable_R2025_Package.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,f.name)
    for f in (root/'references'/'700lsesf60').iterdir():z.write(f,'references/'+f.name)
    for name in ['build_700lsesf60.py','prepare_700lsesf60.py','package_700lsesf60.py','inspect_700lsesf60.py']:
        z.write(root/'scripts'/name,'source/'+name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    print('Verified archive entries:',len(z.namelist()))
print(json.dumps({'path':str(archive),'bytes':archive.stat().st_size,'md5':hashlib.md5(archive.read_bytes()).hexdigest()},indent=2))
