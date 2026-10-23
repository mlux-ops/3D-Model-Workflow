"""Package the verified RFA and explicit companions, then copy to Drive sync."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import zipfile

OUT = Path(__file__).resolve().parents[1]
NAME = 'AERIN_Brenta_ARN2473HAB-CG_Antique_Brass_R2025.rfa'
PACKAGE = 'AERIN_Brenta_Brass_R2025_20261014'
RELEASE = OUT / 'release' / PACKAGE
DRIVE = Path(r'F:\My Drive\3D Model Workflow\3D Models') / PACKAGE
MAPS = Path(r'F:\My Drive\Revit Material Maps - 25-012 651 Belmont')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy_identical_or_new(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha(source) != sha(target):
            raise RuntimeError('Different existing destination: ' + str(target))
    else:
        shutil.copy2(source, target)
    assert sha(source) == sha(target)

validation = json.loads((OUT / 'independent_validation.json').read_text())
visual = json.loads((OUT / 'visual_review.json').read_text())
assert validation['pass'] and all(validation['gates'].values())
assert all(item['pass'] for item in validation['view_exports'])
assert validation['horizontal_camera_front_of_wall']
assert visual['pass']
assert sha(OUT / NAME) == validation['sha256']

readme = f'''# AERIN Brenta wall sconce - Hand-Rubbed Antique Brass

Model: ARN 2473HAB-CG. Native Revit 2025 Lighting Fixtures family.

## Load and place

Open or load `{DRIVE / NAME}` in Revit 2025 or later. Use Place on Face on the intended wall. The default orientation is vertical; rotate the placed instance 90 degrees in the wall plane for horizontal installation. Both orientations were tested on an actual native wall face.

Local original: `{OUT / NAME}`.

## Dimensions and geometry

The fixed product geometry is 3.5 inches wide, 18.5 inches high and 3.75 inches from the mounting face to the outer glass. The centered backplate is 3.5 by 5.25 inches. Seven native smooth solids represent the backplate, support, central sleeve, two hollow flared glass shells and two rounded inner diffusers. There are no imported CAD instances. The dimension parameters report the product's fixed nominal size.

## Materials

Edit the type parameters Metal Finish, Glass Finish and Diffuser Finish to substitute materials. The saved defaults are Hand-Rubbed Antique Brass, clear glass and a warm white inner diffuser. All three appearances contain explicit diffuse bitmaps. The diffuser has a 2700 K appearance glow; this visualization family does not contain a photometric light source or an MEP connector.

The installed local RFA refers to `{OUT / 'textures'}`. All companion maps are also supplied at `{DRIVE / 'textures'}` and `{MAPS}`. On another computer, keep the package together and add its textures folder to Revit's Additional Render Appearance Paths, or browse to each supplied map in the material appearance editor. The uniform maps are intentionally free of invented grain or repeating marks.

## Accuracy and validation

Published overall and backplate dimensions are preserved. Internal proportions use the manufacturer reference model and product photographs. The 0.875-inch backplate projection, hidden support profile, 0.085-inch glass wall and small edge rounds remain source-informed approximations. The softened diffuser tips use an inferred 0.30-inch radius. Brass color and gloss are matched visually to product references rather than measured physical finish samples. This is a visualization model, not fabrication geometry.

Independent Revit 2025 verification passed all 14 gates: saved-file reopening, native geometry, exact nominal dimensions, category, face-based hosting, vertical and horizontal placement, all three material substitutions and restoration, appearance transfer, resolved bitmap paths, brass/clear-glass properties, 2700 K appearance and zero family/project warnings. Front, side, oblique, Realistic material and horizontal hosted images were visually reviewed. The exact receipt is `{DRIVE / 'independent_validation.json'}` and visual review is `{DRIVE / 'visual_review.json'}`.

RFA SHA-256: `{validation['sha256']}`.

## References

Exact selected product: https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241669

The selected brass photo and specification, dimensioned drawing, installation instructions and manufacturer component measurements are preserved in `{DRIVE / 'references'}`. The product requires the smaller 2 by 4 inch junction box indicated by the manufacturer. Appearance glow does not replace electrical or lighting design information.
'''
(OUT / 'README.md').write_text(readme, encoding='utf-8')

files = [Path(NAME), Path('README.md'), Path('independent_validation.json'), Path('visual_review.json')]
files += sorted(Path('textures').joinpath(p.name) for p in (OUT / 'textures').glob('*.png'))
files += sorted(Path('review').joinpath(p.name) for p in (OUT / 'review').glob('*.png'))
files += [Path('references') / n for n in (
    'lightology_brass_original.jpg', 'lightology_line_reference.jpg',
    'lightology_brass_spec.pdf', 'lightology_installation.pdf',
    'manufacturer_component_measurements.json', 'download_receipt.json')]
for rel in files:
    copy_identical_or_new(OUT / rel, RELEASE / rel)
manifest = [{'path':str(RELEASE / rel),'archive_member':rel.as_posix(),
             'bytes':(RELEASE / rel).stat().st_size,'sha256':sha(RELEASE / rel)} for rel in files]
(RELEASE / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
files.append(Path('manifest.json'))
archive = OUT / 'release' / (PACKAGE + '.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as package:
    for rel in files:
        package.write(RELEASE / rel, str(Path(PACKAGE) / rel))
with zipfile.ZipFile(archive) as package:
    assert package.testzip() is None
    assert hashlib.sha256(package.read(str(Path(PACKAGE) / NAME).replace('\\','/'))).hexdigest() == validation['sha256']
for rel in files:
    copy_identical_or_new(RELEASE / rel, DRIVE / rel)
copy_identical_or_new(archive, DRIVE / archive.name)
for source in (OUT / 'textures').glob('*.png'):
    copy_identical_or_new(source, MAPS / source.name)
receipt = {'created_utc':datetime.now(timezone.utc).isoformat(),'rfa':str(OUT / NAME),
           'rfa_sha256':validation['sha256'],'rfa_bytes':(OUT / NAME).stat().st_size,
           'package_file':str(archive),'package_sha256':sha(archive),'package_bytes':archive.stat().st_size,
           'release_folder':str(RELEASE),'drive_sync_folder':str(DRIVE),
           'drive_rfa':str(DRIVE / NAME),'drive_zip':str(DRIVE / archive.name),
           'file_count':len(files),'zip_integrity_pass':True,'copied_hashes_pass':True,
           'remote_metadata_verified':False}
(OUT / 'package_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
