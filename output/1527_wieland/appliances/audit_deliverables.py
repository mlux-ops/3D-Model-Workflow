"""Check row coverage, file hashes, native evidence and stated dimension gates."""
import datetime,hashlib,json,re
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'section_manifest.json').read_text())
items=json.loads((ROOT/'ITEMS.json').read_text())['items']
checks=[]
def check(name,passed,detail=''):
    checks.append({'check':name,'pass':bool(passed),'detail':detail})
check('All 27 inventory rows mapped once',len(manifest['rows'])==27 and {x['row_id'] for x in manifest['rows']}=={x['row_id'] for x in items})
report=(ROOT/'SECTION_REPORT.md').read_text(encoding='utf-8')
row_lines=re.findall(r'^\| (\d{10,}) \|',report,re.M)
check('Report has one table row per inventory item',len(row_lines)==27 and len(set(row_lines))==27)
check('No external release claimed',manifest['delivery_ready'] is False)
for row in manifest['rows']:
    check('Row notes '+str(row['row_id']),(ROOT/row['notes_path']).is_file())
    check('Final status '+str(row['row_id']),row['status'] in ('DOWNLOADED','BUILT_WITH_LIMITATIONS'))
for model in manifest['canonical_models']:
    slug=model['slug'];path=ROOT/model['rfa'];v=json.loads((ROOT/model['validation']).read_text())
    check('RFA hash '+slug,path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==model['rfa_sha256'])
    check('Native 2025 workflow '+slug,v.get('ok') and v.get('reopened') and v.get('saved_revit_format')=='2025' and v['placement']['placed'])
    check('Category '+slug,v.get('category')=='Specialty Equipment')
    check('Visual findings '+slug,bool(v.get('visual_review',{}).get('observation')))
    check('Canonical notes '+slug,(ROOT/slug/'NOTES.md').is_file())
    source=v.get('body_bounds') if v['dimension_gate_scope']=='body' else v.get('placed_bounds')
    delta=[source['xyz_size_mm'][i]-v['target_xyz_mm'][i] for i in range(3)]
    check('Dimension statement '+slug,v['dimension_gate']==all(abs(x)<=1 for x in delta))
    for image in model['previews']:
        p=ROOT/image
        with Image.open(p) as im:
            stat=ImageStat.Stat(im.convert('L'))
            check('Nonblank native view '+image,stat.stddev[0]>5 and min(im.size)>100)
    if model['status']=='BUILT_WITH_LIMITATIONS':
        check('Source build entry '+slug,(ROOT/slug/'source'/'build.py').is_file())
        check('Material flex '+slug,bool(v['parameter_flex']) and all(x['substitution_pass'] and x['restored'] for x in v['parameter_flex']))
        required={v['model']+' '+x['name'] for x in v['parameter_flex']}
        materials={x['name']:x for x in v['material_inventory']}
        valid=bool(required) and all(name in materials and materials[name]['bitmap_exists'] and Path(materials[name]['bitmap']).is_file() for name in required)
        check('Bitmap paths '+slug,valid,'Checks the geometry-bound appliance finish set; unused RFT defaults are not appliance texture dependencies.')
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':len(checks),
        'passed':sum(x['pass'] for x in checks),'failures':[x for x in checks if not x['pass']],
        'row_count':len(manifest['rows']),'canonical_rfa_count':len(manifest['canonical_models']),
        'all_artifact_checks_pass':all(x['pass'] for x in checks),'delivery_ready':False,
        'note':'Artifact completeness is independent of the explicitly retained dimensional, visual and identity holds.'}
(ROOT/'artifact_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['all_artifact_checks_pass'] else 1)
