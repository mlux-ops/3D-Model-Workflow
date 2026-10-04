"""Retain failed candidate evidence before a geometry correction."""
from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[1]
groups={g['key']:g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
for key in ['BOM1273301','VIS1256139']:
    folder=ROOT/groups[key]['canonical_item']
    validation=json.loads((folder/'validation.json').read_text())
    dest=folder/'history'/'failed_curved_profile_r01'
    if dest.exists():continue
    if validation.get('technical_pass'):raise RuntimeError('Refusing to archive accepted candidate as failed')
    dest.mkdir(parents=True)
    for name in ['validation.json',Path(validation['rfa_path']).name]:shutil.copy2(folder/name,dest/name)
    shutil.copytree(folder/'evidence',dest/'evidence')
    shutil.copy2(ROOT/'_tools'/'build_completion.py',dest/'build_completion.py')
    print('Archived',key,validation['actual_dimensions_in'])
history=ROOT/'_review'/'history';history.mkdir(exist_ok=True)
target=history/'completion_batch_r01.json'
if not target.exists():shutil.copy2(ROOT/'COMPLETION_BATCH_RESULT.json',target)
(ROOT/'COMPLETION_RUN_KEYS.json').write_text(json.dumps(['BOM1273301','VIS1256139']))
