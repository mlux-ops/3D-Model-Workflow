"""Check round-1 scope, complete native gates, selected paths and preservation."""
import datetime
import hashlib
import json
import re
from pathlib import Path
from PIL import Image,ImageStat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=load(HERE/'baseline.json')
manifest=load(ROOT/'section_manifest.json')
baseaudit=load(ROOT/'artifact_audit.json')
configs=load(HERE/'configs.json')
targets={c['slug'] for c in configs}
checks=[]

def check(name,passed,detail=None):
    checks.append({'check':name,'pass':bool(passed),'detail':detail})

check('Exactly nine assigned models',len(targets)==9 and targets==set(baseline['targets']))
check('Existing 27-row section artifact audit passes',baseaudit['all_artifact_checks_pass'] and baseaudit['row_count']==27)
check('All original inventory rows remain',len(manifest['rows'])==27 and {r['row_id'] for r in manifest['rows']}=={r['row_id'] for r in baseline['original_manifest']['rows']})
for path,digest in baseline['protected_files'].items():
    p=ROOT/path
    check('Preserved '+path,p.is_file() and sha(p)==digest)
for path,digest in baseline['mutable_before'].items():
    p=HERE/'history_before'/path
    check('Archived prior evidence '+path,p.is_file() and sha(p)==digest)
oldmodels={m['slug']:m for m in baseline['original_manifest']['canonical_models']}
models={m['slug']:m for m in manifest['canonical_models']}
oldrows={r['row_id']:r for r in baseline['original_manifest']['rows']}
oldvisuals={v['slug']:v for v in load(HERE/'history_before'/'visual_review.json')}
visuals={v['slug']:v for v in load(ROOT/'visual_review.json')}
for slug,m in oldmodels.items():
    if slug not in targets:
        check('Non-target model record unchanged '+slug,models[slug]==m)
        check('Non-target visual record unchanged '+slug,visuals[slug]==oldvisuals[slug])
affected=[]
for row in manifest['rows']:
    selected=set(row['model_slugs']) & targets
    if not selected:
        check('Non-target row unchanged '+str(row['row_id']),row==oldrows[row['row_id']])
        continue
    affected.append(row['row_id'])
    m=models[next(iter(selected))]
    notes=(ROOT/row['notes_path']).read_text(encoding='utf-8')
    check('Replacement selected '+str(row['row_id']),row['rfa_paths']==[m['rfa']] and row['status']=='BUILT_WITH_LIMITATIONS')
    check('Replacement row notes '+str(row['row_id']),m['rfa'] in notes and 'Round-1 native gates: **PASS**' in notes)
check('Thirteen affected rows',len(affected)==13)
peak=0
total_materials=0
total_views=0
native_parts=0
for c in configs:
    slug=c['slug'];m=models[slug]
    v=load(ROOT/m['validation'])
    nv=load(ROOT/slug/'source'/'rework_r1'/'validation.json')
    build=load(ROOT/slug/'source'/'rework_r1'/'build_result.json')
    sm=load(ROOT/slug/'source_manifest.json')
    check('Native gate evidence '+slug,nv.get('native_gates_pass') and v.get('requested_round1_gates_pass') and not nv.get('error'))
    check('New custom RFA '+slug,m['rfa'].endswith('_Custom_R1_R2025.rfa') and m['rfa']!=oldmodels[slug]['rfa'] and sha(ROOT/m['rfa'])==m['rfa_sha256'])
    check('RFA source manifests agree '+slug,sm==m and sha(ROOT/m['validation'])==m['validation_sha256'])
    check('Native custom geometry '+slug,nv['native_freeform_count']>10 and nv['import_instance_count']==0 and nv['nested_instance_count']==0)
    check('Complete measurement scope '+slug,v['dimension_gate_scope']=='overall' and v['target_xyz_mm']==c['target_xyz_mm'])
    for group in ['family_bounds','placed_bounds']:
        errors=[nv[group]['xyz_size_mm'][i]-c['target_xyz_mm'][i] for i in range(3)]
        peak=max(peak,max(abs(x) for x in errors))
        check('Measured <=1 mm '+group+' '+slug,all(abs(x)<=1 for x in errors),errors)
    check('Source identity/category/placement '+slug,nv['identity_gate'] and nv['category_gate'] and nv['placement']['placed'] and nv['saved_revit_format']=='2025')
    check('Native family and placed material flex '+slug,all(t['substitution_pass'] and t['restored'] for t in nv['parameter_flex']+nv['placed_material_flex']) and len(nv['parameter_flex'])>0)
    check('All companion bitmaps resolve '+slug,nv['bitmap_gate'] and all(Path(x['bitmap']).is_file() for x in nv['material_inventory']))
    check('Warnings '+slug,not nv['warnings'] and not nv['placed_warnings'])
    check('Native validation follows build '+slug,nv['started_utc']>=build['finished_utc'])
    check('Retained source dimensions '+slug,sha(Path(c['source_pdf']))==c['source_pdf_sha256'])
    check('Original OEM records preserved '+slug,m['original_rfas']==oldmodels[slug]['original_rfas'])
    check('Visual inspection recorded '+slug,bool(visuals[slug]['observation']) and visuals[slug]['revision']=='Custom_R1')
    for item in visuals[slug]['images']:
        path=ROOT/item['path']
        with Image.open(path) as im:
            check('Fresh nonblank preview '+item['path'],sha(path)==item['sha256'] and ImageStat.Stat(im.convert('L')).stddev[0]>5 and min(im.size)>100)
    total_materials+=len(nv['parameter_flex'])+len(nv['placed_material_flex'])
    total_views+=len(nv['previews'])
    native_parts+=nv['native_freeform_count']
report=(ROOT/'SECTION_REPORT.md').read_text(encoding='utf-8')
tableids=re.findall(r'^\| (\d{10,}) \|',report,re.M)
check('Report covers every row exactly once',len(tableids)==27 and len(set(tableids))==27)
check('No external release claimed',manifest['delivery_ready'] is False)
passed=all(x['pass'] for x in checks)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_checks_pass':passed,
        'checks':len(checks),'passed':sum(x['pass'] for x in checks),'failures':[x for x in checks if not x['pass']],
        'base_section_audit_checks':baseaudit['checks'],'protected_files_verified':len(baseline['protected_files']),
        'prior_metadata_verified':len(baseline['mutable_before']),'models':9,'affected_rows':len(affected),
        'material_substitution_checks':total_materials,'native_previews':total_views,'native_freeform_elements':native_parts,
        'max_dimension_error_mm':peak,'delivery_ready':False}
(HERE/'round1_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(HERE/'round1_audit_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
if passed:
    receipt=load(HERE/'completion_receipt.json')
    receipt.update(artifact_audit_pending=False,artifact_audit_pass=True,round1_audit_checks=len(checks),
                   section_artifact_audit_checks=baseaudit['checks'],section_report_sha256=sha(ROOT/'SECTION_REPORT.md'),
                   section_manifest_sha256=sha(ROOT/'section_manifest.json'),native_freeform_elements=native_parts)
    (HERE/'completion_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    baseaudit['round1_audit']={k:v for k,v in result.items() if k!='failures'}
    (ROOT/'artifact_audit.json').write_text(json.dumps(baseaudit,indent=2),encoding='utf-8')
    (HERE/'ACTIVE_TASK.md').write_text('# Appliances round 1\n\nCOMPLETE. Nine custom working replacements, 13 affected rows, complete overall dimension gates passed. Native validations, 27 previews, original-file protection and report reconciliation verified.\n\nSee completion_receipt.json, round1_audit.json, RESULT.md and ../SECTION_REPORT.md. The five named user-decision holds are unchanged. Final release belongs to the orchestrator.\n',encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(0 if passed else 1)
