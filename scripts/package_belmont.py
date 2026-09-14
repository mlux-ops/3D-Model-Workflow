from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,html
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'output/belmont_tiles'
spec=json.loads((p/'manifest.json').read_text())
assert len(spec)==8 and len(set(s['id'] for s in spec))==8
lib=p/'Belmont_New_Tiles_R2025.adsklib'
with zipfile.ZipFile(lib) as z:
    assert z.testzip() is None
    assert len(z.namelist())>37
rv=json.loads((p/'revit_validation.json').read_text());assert rv['success'] and rv['count']==8 and rv['warnings']==0
for m in rv['materials']:
    for path in m['maps'].values():assert Path(path).is_file()
checks=[]
for s in spec:
    d=p/s['id'];vr=E.parse(d/(s['id']+'.vrmat'))
    for parameter in vr.findall('.//parameter'):
        if parameter.get('name')=='file': assert (d/parameter.findtext('value')).is_file()
    for f in (d/'textures').glob('*.png'):
        with Image.open(f) as im: im.verify()
        with Image.open(f) as im: assert list(im.size)==s['pixels']
        if f.stem in ['Bump','Normal']:assert f.read_bytes()[24]==16
    checks.append({'id':s['id'],'images':'pass','height_and_normal_bits':16,'vrmat_xml_and_paths':'pass'})
log=(p/'vray_validation.log').read_text(encoding='utf-16') if (p/'vray_validation.log').read_bytes().startswith(b'\xff\xfe') else (p/'vray_validation.log').read_text()
assert 'Objects in scene: 80' in log and '0 warning(s)' in log
report={'new_materials':8,'existing_skipped':['Adella Viso White','Scandinavian Grey Decor'],'revit_native_reopen':'8 materials; zero warnings','adsklib':'exported by Revit 2025 Material Browser; all eight listed; library released; archive integrity pass','vray_scene_parse':'80 objects; zero warnings','vray_render':'blocked by license -98','vrmat_native_import':'unverified','checks':checks}
(p/'VALIDATION.json').write_text(json.dumps(report,indent=2))
existing=[('Adella Viso White','../adella_highres_review/MSI_Adella_HighRes_Review.zip'),('Scandinavian Grey Decor','../scandinavian/Scandinavian_Decor_Grey_6x7_Materials.zip')]
for _,rel in existing:assert (p/rel).is_file()
rows='\n'.join(f"| {s['name'].replace('Belmont - ','')} | {s['repeat_inches'][0]:.4f} x {s['repeat_inches'][1]:.4f} | {s['id']} |" for s in spec)
(p/'README.md').write_text('# Belmont bathroom materials — eight new tiles\n\nNative Revit 2025 library: Belmont_New_Tiles_R2025.adsklib. Open in Manage > Materials > Open Existing Library; add the desired Belmont materials to your project. Optional source RVT contains the same eight assets. Each material folder contains V-Ray VRMAT and material-only VRSCENE, four texture maps, a preview, and scale/source notes.\n\nRevit physical scales are set. In V-Ray, map UV channel 1 to the rectangular repeat below. Dimensions are nominal tile dimensions plus estimated 1/16-inch light grout. A mosaic texture repeat need not equal its commercial sheet size.\n\n| Material | Repeat, inches W x H | Folder |\n|---|---|---|\n'+rows+'\n\nKeep every texture subfolder intact. Revit references absolute paths in this workspace; if relocating, repath each material to its own folder. Do not flatten the folders: their Color.png/Bump.png names repeat. V-Ray texture references are relative to each VRMAT folder; use its texture directory if your host requires repathing.\n\nSource limits: real supplied photographs are retained. Several mosaic faces offer only 49–220 pixels across, and Soreno 24x48 faces about 490x240. Larger PNG exports do not add source detail. These are photo-based visualization materials, not measured PBR scans. Bump/normal maps contain smooth estimated grout and bevel relief only, avoiding photographic noise being interpreted as geometry. This intentionally omits unmeasured fine glaze/stone relief. Gloss/roughness and mixed-finish assignment are estimates. Plain Scandinavian retains edge lighting from its source photograph.\n\nRevit saved/reopened eight materials with zero warnings; all eight exported through Material Browser. V-Ray scene parsed 80 objects with zero warnings; render blocked by Chaos license -98. Native VRMAT import and final rendered appearance are unverified. Review.html provides flat previews, not renders.\n\nAlready created; not duplicated:\n'+''.join(f'- [{name}]({rel})\n' for name,rel in existing)+'\nExisting links work in this workspace; if moving this package, use your previously downloaded archives. No PR or push was created.\n')
cards=''.join(f'<article><img src="{s["id"]}/Preview.jpg"><h2>{html.escape(s["name"].replace("Belmont - ",""))}</h2><p>Repeat: {s["repeat_inches"][0]:.4f} × {s["repeat_inches"][1]:.4f} in</p><a href="{s["id"]}/{s["id"]}.vrmat">V-Ray material</a> · <a href="{s["id"]}/README.md">Notes</a></article>' for s in spec)
(p/'Review.html').write_text('<!doctype html><meta charset="utf-8"><title>Belmont tile materials</title><style>body{font:16px system-ui;background:#f5f4f1;color:#252523;margin:40px;max-width:1300px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px}article{background:white;padding:18px}img{width:100%;height:270px;object-fit:contain}h2{font-size:18px}a{color:#31564c}</style><h1>Belmont bathroom tiles</h1><p>Eight new materials. Flat photographic previews; source resolution and render limitations are in the notes.</p><p><a href="Belmont_New_Tiles_R2025.adsklib">Revit 2025 library</a> · <a href="README.md">Setup and dimensions</a></p><main>'+cards+'</main><h2>Existing materials — reused</h2>'+''.join(f'<p><a href="{r}">{n}</a></p>' for n,r in existing))
files=[p/n for n in ['Belmont_New_Tiles_R2025.adsklib','Belmont_New_Tiles_R2025.rvt','README.md','Review.html','manifest.json','VALIDATION.json','revit_validation.json']]
for s in spec:files.extend(f for f in (p/s['id']).rglob('*') if f.is_file())
archive=p/'Belmont_Eight_New_Materials_R2025_VRay.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,f.relative_to(p))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'files':len(files),'bytes':archive.stat().st_size,'new_materials':8,'checks':'passed; render/import limitations documented'},indent=2))
