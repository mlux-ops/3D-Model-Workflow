"""Reproducible viewer-only build; freeze guards for source selections and owner packets.

Usage: python -B scratch/rebuild_viewer3d_v2.py
No Revit model writes, Git, tile scoring, procurement, or owner packet regeneration.
"""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
source_files=[ROOT/'state/ROOMS.json',ROOT/'state/OWNER_FEEDBACK.md']
source_files.extend(sorted((ROOT/'rooms').glob('*/champion.md')))
source_files.extend(sorted((ROOT/'deliverables/r039-13-owner-review-PROVISIONAL').glob('*.html')))
source_files.extend(sorted((ROOT/'deliverables/r039-13-owner-review-PROVISIONAL').glob('*.pdf')))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(ROOT)):digest(p) for p in source_files}
for script in ('build_viewer3d_data.py','viewer3d_enrich_v2.py','viewer3d_plan_enrich.py','viewer3d_architecture_r043.py','build_viewer3d_index.py'):
    p=ROOT/'scratch'/script
    result=subprocess.run([sys.executable,'-B',str(p)],cwd=ROOT,
                          capture_output=True,text=True,timeout=80)
    print(result.stdout.rstrip(),flush=True)
    if result.returncode:
        print(result.stderr,file=sys.stderr)
        raise SystemExit(f'BUILD FAILED {script}: {result.returncode}')
after={str(p.relative_to(ROOT)):digest(p) for p in source_files}
assert before==after,('FROZEN_SOURCE_MUTATION',[(k,before[k],after[k]) for k in before if before[k]!=after[k]])
payload=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf-8'))
assert len(payload['rooms'])==13
assert sum(len(x.get('physical_instances',[])) for x in payload['rooms'])==26
assert payload['phase']=='v4_native_wall_face_architecture_r043'
assert payload['architecture_summary']['registered_instances']>=10
assert all(x.get('full_room_plan',{}).get('width_ft',0)>0 and x.get('full_room_plan',{}).get('depth_ft',0)>0 for x in payload['rooms'])
assert all(x['program']['owner_approved'] is False for x in payload['rooms'])
assert len([x for x in payload['rooms'] if not x['has_pick']])==5
assert next(x for x in payload['rooms'] if x['id']=='PH-BATH4')['champion_id']=='round-036-B'
assert next(x for x in payload['rooms'] if x['id']=='PH-BATH4')['program']['scope_truth'].startswith('One combined original 40.2')
assert next(x for x in payload['rooms'] if x['id']=='TX-POWDER')['has_pick'] is False
assert all((x['program']['tub_selected'] is False or x['program']['pan_selected'] is False) for x in payload['rooms'])
print('PASS freeze hashes: '+str(len(before))+' original decision/owner files UNCHANGED; 13 room types, 26 physical instances, 5 no-pick, zero approvals.')
