from pathlib import Path
import json,zipfile,hashlib,shutil
from PIL import Image
root=Path(__file__).resolve().parents[1]
out=root/'output/beige_fluted_12x24'
source=out/'source';source.mkdir(exist_ok=True)
for name in ['prepare_beige_fluted.py','build_beige_fluted_revit.py','package_beige_fluted.py']:
    shutil.copy2(root/'scripts'/name,source/name)
validation=json.loads((out/'revit_validation.json').read_text())
assert validation['success'] and validation['warnings']==0
with zipfile.ZipFile(out/'Beige_Fluted_12x24_R2025.adsklib') as z:
    assert z.testzip() is None
    assert any('Beige%20Fluted' in x for x in z.namelist())
for p in (out/'textures').iterdir():
    with Image.open(p) as im:
        assert im.size==(1200,2400)
        im.verify()
assert (out/'textures/Beige_Fluted_Color.jpeg').read_bytes()==Path('C:/Users/found/OneDrive/Desktop/IMG_0786.jpeg').read_bytes()
assert (out/'textures/Beige_Fluted_Bump16.png').read_bytes()[24]==16
report={'revit_2025_save_reopen':'passed','revit_warnings':0,'native_library':'Created/populated/released in Revit Material Browser; stored row verified','library_integrity':'passed','color_texture':'byte-identical to original user photograph, 1200 x 2400','bump_bit_depth':16,'ui_color_scale_inches':[12,24],'native_material_preview':'Inspected; photo and fluting load correctly. Not a calibrated or full-scene render.','relief_and_sheen':'estimated'}
(out/'PACKAGE_VALIDATION.json').write_text(json.dumps(report,indent=2))
files=[p for p in out.rglob('*') if p.is_file() and p.suffix not in ['.zip','.lck'] and '.0001.' not in p.name]
package=out/'Beige_Fluted_12x24_R2025_Package.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(out))
with zipfile.ZipFile(package) as z:assert z.testzip() is None
print(json.dumps({'package':str(package),'bytes':package.stat().st_size,'files':len(files),'sha256':hashlib.sha256(package.read_bytes()).hexdigest()},indent=2))
