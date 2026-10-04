"""Queue only new, changed, or failed native products after explicit source preparation."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
prepared=json.loads((ROOT/'_harness/prepared_models.json').read_text(encoding='utf-8'))
queue=[]
for product in prepared:
    key=product['key'];spec=ROOT/key/'source/model_spec.json';validation=ROOT/key/'validation.json'
    data=json.loads(validation.read_text(encoding='utf-8')) if validation.exists() else {}
    digest=hashlib.sha256(spec.read_bytes()).hexdigest()
    if not data.get('native_gates_pass') or data.get('source_spec_sha256')!=digest:
        if validation.exists():
            history=ROOT/key/'_history';history.mkdir(exist_ok=True)
            previous=validation.read_bytes();history_name='validation_'+hashlib.sha256(previous).hexdigest()[:16]+'.json'
            (history/history_name).write_bytes(previous)
        queue.append(key)
(ROOT/'_harness/build_queue.json').write_text(json.dumps(queue,indent=2),encoding='utf-8')
print(json.dumps({'queue_count':len(queue),'keys':queue}))
