"""Reconcile durable test reports, installed/runtime DLL and immutable native exports."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
reports={
    'family_lifecycle':('evidence/native-attempt-02/family-native-report.json','passed'),
    'project_workflow':('evidence/workflow-attempt-02/native-workflow-report.json','technical_pass'),
    'hosting_and_response_recovery':('evidence/hosting-recovery-01/native-hosting-recovery.json','passed'),
    'annotations_mirror_dependency_fencing':('evidence/annotations-batch-02/native-hosting-recovery.json','passed'),
    'final_compiled_two_sheet_workflow':('evidence/compiled-sheets-final/native-hosting-recovery.json','passed'),
    'final_export_safety':('evidence/export-safety-final/native-hosting-recovery.json','passed'),
    'final_real_mcp_stdio':('evidence/native-mcp-stdio-export-safe.json','passed')}
summary={'schema_version':1,'package_identity':'codex-native-revit-2025','native_reports':{},'pass':True}
for label,(name,status) in reports.items():
    d=json.loads((root/name).read_text(encoding='utf-8'))
    if d['status']!=status:raise AssertionError(label+' incomplete')
    checks=d.get('checks',{})
    if any(not c['pass'] for c in checks.values()):raise AssertionError(label+' numerical check failed')
    summary['native_reports'][label]={'path':name,'status':d['status'],'checks':len(checks)}
export=json.loads((root/'evidence/export-safety-final/native-hosting-recovery.json').read_text())
for path,sha in export['original_export_hashes'].items():
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha:raise AssertionError('Immutable native export changed')
ann=json.loads((root/'evidence/annotations-batch-02/native-hosting-recovery.json').read_text())
mirror=ann['steps']['mirror']['result']['data']['after'][0]['location']
if sorted([mirror['start'][0],mirror['end'][0]])!=[-8,0]:raise AssertionError('Native mirror geometry incorrect')
compiled=json.loads((root/'evidence/compiled-sheets-final/native-hosting-recovery.json').read_text())
for key in ['capture-casework','capture-sheet_TEST_ID1_0','capture-sheet_TEST_ID1_1','capture-sheet2-coverage-safe']:
    files=compiled['steps'][key]['result']['files']
    if not files or any(not Path(p).is_file() or Path(p).stat().st_size==0 for p in files):raise AssertionError('Missing native capture')
hashes=json.loads((root/'evidence/final-release-assembly-hashes.json').read_text())
if len({r['Hash'] for r in hashes})!=1:raise AssertionError('Installed/build DLL differs')
assembly=root/'src/NativeRevit/bin/Release/net8.0-windows/CodexNativeRevit.dll'
if hashlib.sha256(assembly.read_bytes()).hexdigest().upper()!=hashes[0]['Hash']:raise AssertionError('Source-built DLL changed')
summary['assembly_sha256']=hashes[0]['Hash']
summary['current_mcp_target']={'port':49328,'native_process_id':48092,'scope':'disposable acceptance documents'}
summary['full_requested_scope_complete']=False
summary['limitations_file']='docs/CAPABILITY-MATRIX.md'
(root/'evidence/verified-delivery-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
