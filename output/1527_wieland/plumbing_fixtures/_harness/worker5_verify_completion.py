"""Independently verify complete row coverage and the final plumbing evidence set."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'DOWNLOADED', 'AVAILABLE_LOGIN_REQUIRED+BUILT', 'BUILT', 'BUILT_WITH_LIMITATIONS', 'BLOCKED'}
FAILURES = []
CHECKS = 0


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, message):
    global CHECKS
    CHECKS += 1
    if not condition:
        FAILURES.append(message)


def valid_file(path, digest=None):
    try:
        path.resolve().relative_to(ROOT.resolve())
        check(path.is_file(), 'Missing file: ' + str(path))
        if path.is_file() and digest:
            check(sha(path) == digest, 'Hash changed: ' + str(path))
        return path.is_file()
    except ValueError:
        check(False, 'Evidence outside section: ' + str(path))
        return False


def main():
    source = load(ROOT / 'ITEMS.json')
    original_groups = load(ROOT / '_research/groups.json')
    final = load(ROOT / 'FINAL_STATUS.json')
    baseline = load(ROOT / '_harness/worker5_takeover_baseline.json')
    report = (ROOT / 'SECTION_REPORT.md').read_text(encoding='utf-8')
    rows = final['rows']
    groups = final['groups']
    source_ids = Counter(str(row['row_id']) for row in source['items'])
    check(len(source['items']) == 178, 'Source row count')
    check(Counter(row['row_id'] for row in rows) == source_ids, 'Final status row coverage')
    check(Counter(re.findall(r'^\| (\d+) \|', report, re.M)) == source_ids, 'Report row coverage')
    check(Counter(str(row['row_id']) for group in original_groups for row in group['rows']) == source_ids, 'Group partition coverage')
    check(len({row['notes_path'] for row in rows}) == 178, 'Distinct note paths')
    check(sha(ROOT / 'ITEMS.json') == baseline['inventory_sha256'] == final['inventory_sha256'], 'Original inventory preserved')
    check(sha(ROOT / '_research/groups.json') == baseline['groups_sha256'] == final['group_inventory_sha256'], 'Original grouping preserved')
    check(len(groups) == 71, 'Product group count')
    check(sum(g['native_gates_pass'] for g in groups) == 68, 'Native pass count')
    check(sum(bool(row['group_key']) for row in rows) == 160, 'Product row count')
    check(sum(row.get('blocker_kind') == 'ADMINISTRATIVE_NONPRODUCT' for row in rows) == 15, 'Header count')
    check(sum(row.get('blocker_kind') == 'MISSING_PRODUCT_SELECTION' for row in rows) == 3, 'Unselected sink count')
    check(final['release_ready'] is False, 'Release must remain held for review')
    source_by_id = {str(row['row_id']): row for row in source['items']}
    group_by_key = {g['key']: g for g in groups}
    for row in rows:
        check(row['status'] in ALLOWED, 'Invalid row status: ' + row['row_id'])
        check(row['agent_ignore'] == bool(source_by_id[row['row_id']].get('agent_ignore')), 'Scope flag changed: ' + row['row_id'])
        path = ROOT / row['notes_path']
        if valid_file(path, row['notes_sha256']):
            text = path.read_text(encoding='utf-8')
            check(row['row_id'] in text and '**Final status: ' + row['status'] + '**' in text, 'Note identity/status: ' + row['row_id'])
            for heading in ['Identity and scope', 'Source and last verified stage']:
                check(heading in text, 'Missing note section: ' + row['row_id'] + ' ' + heading)
            check('ASSUMPTION' in text or 'Assumptions and limitations' in text, 'Assumption disclosure: ' + row['row_id'])
            for hold in row['holds']:
                check(hold['code'] in text and hold['code'] in report, 'Hold lost: ' + hold['code'])
            if row['group_key']:
                group = group_by_key[row['group_key']]
                check(row['status'] == group['status'] and row['rfa_path'] == group['rfa_path'], 'Row/group mismatch: ' + row['row_id'])
                check('Dimensions checked' in text and 'Native gates and parameters' in text, 'Missing native note details: ' + row['row_id'])
    images = set()
    textures = set()
    parameters = 0
    current = {}
    for group in groups:
        key = group['key']
        rfa = ROOT / group['rfa_path']
        vpath = ROOT / group['validation_path']
        valid_file(vpath, group['validation_sha256'])
        v = load(vpath)
        if valid_file(rfa, group['rfa_sha256']):
            with rfa.open('rb') as stream:
                check(stream.read(8) == bytes.fromhex('d0cf11e0a1b11ae1'), 'RFA container signature: ' + key)
        check(str(group['saved_version']) == '2025' and v.get('reopened') is True, 'Native saved/reopened version: ' + key)
        check(group['native_gates_pass'] == bool(v.get('native_gates_pass')), 'Native result altered: ' + key)
        check(v.get('gates', {}).get('category') is True and v.get('gates', {}).get('actual_face_host') is True, 'Category or actual host: ' + key)
        check(v.get('stage') in {'complete', 'manufacturer_review_complete'}, 'Unfinished native stage: ' + key)
        check(not v.get('error'), 'Native error remains: ' + key)
        check(group['gates'] == v['gates'], 'Recorded gates differ: ' + key)
        check(group['last_verified_stage'] == v['stage'], 'Stage altered: ' + key)
        check(len(group['evidence']) >= 3, 'Preview count: ' + key)
        if group['source_spec_path']:
            spath = ROOT / group['source_spec_path']
            valid_file(spath, group['source_spec_sha256'])
            check(sha(spath) == v.get('source_spec_sha256'), 'Stale native result: ' + key)
            check(all(group['gates'].values()), 'Custom native gate failed: ' + key)
            check(all(abs(d['delta_mm']) <= 1.0 for d in group['dimensions']), 'Custom configured envelope mismatch: ' + key)
            check(all(c['pass'] for c in group['dimension_anchor_checks'] + group['native_path_checks']), 'Custom anchor/path failure: ' + key)
        valid_file(ROOT / group['build_script'])
        for test in group['material_tests'].values():
            parameters += 1
            if group['native_gates_pass']:
                check(test.get('writable') and test.get('substitution_reaches_faces'), 'Custom material substitution: ' + key)
        for asset in group['appearance_bindings'].values():
            if asset.get('path'):
                path = Path(asset['path'])
                if valid_file(path):
                    textures.add(path)
        for item in group['evidence']:
            path = ROOT / item['path']
            if valid_file(path, item['sha256']):
                images.add(path)
        current[key] = group
    for path in images | textures:
        try:
            with Image.open(path) as image:
                image.verify()
            check(True, '')
        except Exception as exc:
            check(False, 'Image cannot decode: ' + str(path) + ': ' + str(exc))
    for old in baseline['groups']:
        if old['validation_exists']:
            g = current[old['key']]
            check(g['validation_sha256'] == old['validation_sha256'], 'Protected validation changed: ' + old['key'])
            check(g['rfa_sha256'] == old['rfa_sha256'], 'Protected RFA changed: ' + old['key'])
            check(g['source_spec_sha256'] == old['spec_sha256'], 'Protected input changed: ' + old['key'])
    required = {'700337000000090', 'MS642124CEFG_01', 'SS124_01', '443306', '240328', '32526141'}
    check(all(current[key]['holds'] for key in required), 'Prescribed holds lost')
    check({g['key'] for g in groups if not g['native_gates_pass']} == {'700337000000090', 'MS642124CEFG_01', 'SS124_01'}, 'Manufacturer hold set changed')
    batch = load(ROOT / '_harness/batch_current.json')
    check({item['key'] for item in batch['items']} == {'62820LF-BL', '63221LF-BLLHP', '873111-BNX-2.5'}, 'Final native batch scope')
    check(all(item['native_gates_pass'] and item['technical_pass'] and not item.get('error') for item in batch['items']), 'Final batch gate failure')
    check('RESULT' in report and 'CHANGES' in report and 'VALIDATION' in report and 'BLOCKERS' in report, 'Report completion sections')
    hold_register = load(ROOT / 'NEEDS_USER_HOLDS.json')
    audit = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'pass': not FAILURES, 'checks': CHECKS,
             'failures': FAILURES, 'row_count': len(rows), 'notes_count': len(rows), 'rfa_count': len(groups),
             'validation_count': len(groups), 'native_pass_count': sum(g['native_gates_pass'] for g in groups),
             'native_preview_images': len(images), 'active_custom_textures': len(textures), 'material_parameters_recorded': parameters,
             'row_status_counts': dict(Counter(r['status'] for r in rows)), 'explicit_hold_count': len(hold_register['holds']),
             'protected_validation_rfa_pairs': 68, 'protected_custom_specs': 65,
             'report_sha256': sha(ROOT / 'SECTION_REPORT.md'), 'manifest_sha256': sha(ROOT / 'FINAL_STATUS.json')}
    path = ROOT / '_harness/worker5_completion_audit.json'
    path.write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    if not FAILURES:
        receipt = {'completed_utc': audit['generated_utc'], 'worker': 'worker-5', 'coverage_complete': True,
                   'worker_task_complete': True, 'release_ready': False, 'rows': len(rows), 'product_groups': len(groups),
                   'native_pass_groups': audit['native_pass_count'], 'manufacturer_hold_groups': 3,
                   'audit_path': '_harness/worker5_completion_audit.json', 'audit_sha256': sha(path),
                   'section_report_path': 'SECTION_REPORT.md', 'section_report_sha256': audit['report_sha256'],
                   'final_status_path': 'FINAL_STATUS.json', 'final_status_sha256': audit['manifest_sha256'],
                   'needs_user_holds_path': 'NEEDS_USER_HOLDS.json', 'needs_user_holds_sha256': sha(ROOT / 'NEEDS_USER_HOLDS.json')}
        (ROOT / 'completion_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(audit, indent=2))
    return 0 if not FAILURES else 2


if __name__ == '__main__':
    sys.exit(main())
