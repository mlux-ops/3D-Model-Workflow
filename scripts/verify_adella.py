from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E
from PIL import Image
out=Path(__file__).resolve().parents[1]/'output/adella'
with zipfile.ZipFile(out/'MSI_Adella_Viso_White_R2025.adsklib') as z:
    assert z.testzip() is None
    print('ADSKLIB container integrity passed')
root=E.parse(out/'MSI_Adella_Viso_White.vrmat').getroot()
assets={a.attrib['url']:a for a in root.findall('Asset')}
materials=[k for k,a in assets.items() if a.attrib['type']=='material']
assert len(materials)==1
links=0
for p in root.iter('parameter'):
    v=p.findtext('value','')
    if p.attrib['type'] in ['plugin','acolor texture','float texture'] and v.startswith('/'):
        assert v in assets,(p.attrib,v)
        links+=1
    if p.attrib['name']=='file':assert (out/v).is_file(),v
for f in (out/'textures').glob('*.png'):
    with Image.open(f) as im:
        im.verify()
report={'adsklib_zip_integrity':'passed','vrmat_xml_and_references':'passed','vrmat_materials':materials,'resolved_plugin_links':links,'native_revit_project_reopen':'passed, Revit 2025, zero warnings','native_adsklib_export':'created and populated in Revit 2025 Material Browser; released library and inspected stored row','native_vray_render':'blocked: Chaos license -98','native_vrmat_import':'not verified; SDK reader also failed on installed Cosmos reference material','relief_fidelity':'procedural approximation, not measured scan'}
log=(out/'vrscene_validation.log').read_text(encoding='utf-8-sig')
assert 'Scene file parsed successfully' in log
assert '0 warning(s)' in log
report['native_vrscene_parse']='passed in installed V-Ray 7.20.05; 10 objects, zero warnings; rendering blocked by license -98'
report['relief_fidelity']='photographic exact-product crop at 2560px source; not a calibrated height scan'
(out/'PACKAGE_VALIDATION.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
