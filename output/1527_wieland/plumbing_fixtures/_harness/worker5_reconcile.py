"""Reconcile the preserved plumbing evidence and publish only missing final inputs."""
from pathlib import Path
from collections import Counter
import argparse
import contextlib
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / '_harness'
TARGETS = {'62820LF-BL', '63221LF-BLLHP', '873111-BNX-2.5'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding='utf-8')


def reconcile():
    inventory = load(ROOT / 'ITEMS.json')
    groups = load(ROOT / '_research/groups.json')
    rows = inventory['items']
    assert len(rows) == inventory['count'] == 178
    assert Counter(str(r['row_id']) for r in rows) == Counter(str(r['row_id']) for g in groups for r in g['rows'])
    current = []
    for group in groups:
        if not group['sku']:
            continue
        key = group['key']
        vpath = ROOT / key / 'validation.json'
        spath = ROOT / key / 'source/model_spec.json'
        data = load(vpath) if vpath.exists() else {}
        spec = load(spath) if spath.exists() else {}
        rfa = Path(data['rfa_path']) if data.get('rfa_path') else None
        entry = {
            'key': key, 'sku': group['sku'], 'row_ids': [str(r['row_id']) for r in group['rows']],
            'stage': data.get('stage'), 'native_pass': data.get('native_gates_pass', False),
            'technical_pass': data.get('technical_pass', False),
            'validation_exists': vpath.exists(), 'validation_sha256': digest(vpath) if vpath.exists() else None,
            'rfa_path': str(rfa) if rfa else None, 'rfa_exists': bool(rfa and rfa.is_file()),
            'rfa_sha256': digest(rfa) if rfa and rfa.is_file() else None,
            'spec_sha256': digest(spath) if spath.exists() else None,
            'spec_hash_matches': digest(spath) == data.get('source_spec_sha256') if spath.exists() else None,
            'actual_mm': data.get('actual_dimensions_after_reopen_mm'),
            'gates': data.get('gates'), 'error': data.get('error'),
            'authority_complete': data.get('all_overall_dimensions_authoritative'),
            'sources': data.get('source_references') or [data.get('source_url'), data.get('spec_url')],
            'limitations': data.get('limitations', []),
            'search': data.get('rfa_search') or spec.get('rfa_search'),
            'evidence_files': data.get('evidence_files', []),
        }
        current.append(entry)
    out = {
        'at_utc': datetime.now(timezone.utc).isoformat(),
        'inventory_sha256': digest(ROOT / 'ITEMS.json'),
        'groups_sha256': digest(ROOT / '_research/groups.json'),
        'row_count': len(rows), 'product_group_count': len(current),
        'product_row_count': sum(len(g['row_ids']) for g in current),
        'no_sku_rows': [r for g in groups if not g['sku'] for r in g['rows']],
        'native_pass_count': sum(g['native_pass'] for g in current),
        'missing_validations': [g['key'] for g in current if not g['validation_exists']],
        'failed_or_held': [g['key'] for g in current if g['validation_exists'] and not g['native_pass']],
        'stale_specs': [g['key'] for g in current if g['validation_exists'] and g['spec_hash_matches'] is False],
        'groups': current,
    }
    write(HARNESS / 'worker5_live_reconciliation.json', out)
    baseline = HARNESS / 'worker5_takeover_baseline.json'
    if not baseline.exists():
        write(baseline, out)
    print(json.dumps({k: out[k] for k in ['row_count', 'product_group_count', 'product_row_count', 'native_pass_count', 'missing_validations', 'failed_or_held', 'stale_specs']}))
    print('No-SKU rows: ' + json.dumps([{'row_id': str(r['row_id']), 'item_key': r['item_key'], 'description': r['description'], 'unit': r.get('unit_type'), 'room': r.get('room_type')} for r in out['no_sku_rows']]))
    return out


def prepare_missing():
    current = reconcile()
    missing = set(current['missing_validations'])
    assert missing <= TARGETS, 'Unexpected missing groups: ' + repr(missing - TARGETS)
    assert not current['stale_specs'], 'Existing source changes need separate review'
    if not missing:
        print('No missing validation inputs to publish.')
        return
    import prepare_products as products
    import prepare_completion_d
    previous = load(HARNESS / 'prepared_models.json')
    prepare_completion_d.prepare()
    products.MODELS[:] = [spec for spec in products.MODELS if spec['key'] in missing]
    assert {spec['key'] for spec in products.MODELS} == missing
    history = HARNESS / 'worker5_history'
    history.mkdir(exist_ok=True)
    for name in ['prepared_models.json', 'build_queue.json', 'batch_current.json', 'resume_inventory.json']:
        path = HARNESS / name
        if path.exists():
            (history / (path.stem + '_' + digest(path)[:16] + path.suffix)).write_bytes(path.read_bytes())
    with (HARNESS / 'worker5_preparation.log').open('w', encoding='utf-8') as log:
        with contextlib.redirect_stdout(log):
            products.publish()
    merged = {row['key']: row for row in previous}
    merged.update({row['key']: row for row in load(HARNESS / 'prepared_models.json')})
    write(HARNESS / 'prepared_models.json', list(merged.values()))
    write(HARNESS / 'build_queue.json', sorted(missing))
    write(HARNESS / 'worker5_preparation_receipt.json', {
        'at_utc': datetime.now(timezone.utc).isoformat(), 'queued': sorted(missing),
        'preserved_prepared_count': len(previous), 'merged_prepared_count': len(merged),
        'prepared_inputs': {key: digest(ROOT / key / 'source/model_spec.json') for key in sorted(missing)},
    })
    print(json.dumps({'queued': sorted(missing), 'prepared_total': len(merged)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['audit', 'prepare'])
    args = parser.parse_args()
    prepare_missing() if args.mode == 'prepare' else reconcile()
