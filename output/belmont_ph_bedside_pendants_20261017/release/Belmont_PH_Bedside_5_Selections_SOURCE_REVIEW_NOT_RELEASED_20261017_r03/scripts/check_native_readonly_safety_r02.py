"""Offline safety review of the native validator; does NOT emulate Revit QA."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / 'qa/native_readonly_oem_r02.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    forbidden = []
    transactions = []
    closes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        attr = node.func.attr
        if attr in ('Save', 'SaveAs', 'EditFamily', 'OpenAndActivateDocument', 'Terminate', 'Kill'):
            forbidden.append({'call': attr, 'line': node.lineno})
        if attr in ('Transaction', 'SubTransaction', 'TransactionGroup'):
            transactions.append({'line': node.lineno, 'document': ast.unparse(node.args[0])})
        if attr == 'Close':
            closes.append({'line': node.lineno, 'argument': ast.unparse(node.args[0])})
    assert not forbidden, forbidden
    assert transactions and all(row['document'] == 'project' for row in transactions)
    assert closes and all(row['argument'] == 'False' for row in closes)
    inventory = json.loads((ROOT / 'qa/OEM_BYTE_IDENTITY.json').read_text(encoding='utf-8'))
    originals = []
    for row in inventory['families']:
        current = hashlib.sha256(Path(row['file']).read_bytes()).hexdigest()
        assert current == row['original_rfa_sha256']
        originals.append({'file': row['file'], 'sha256': current, 'unchanged': True})
    report = {'status': 'OFFLINE_SAFETY_AND_COMPILE_PASS_NOT_NATIVE_EXECUTION',
              'script': str(path), 'script_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'forbidden_calls': forbidden, 'transactions': transactions, 'close_calls': closes,
              'originals': originals, 'native_api_behavior': 'UNTESTED',
              'scope_limit': 'AST review detects forbidden direct calls, not a sandbox/security proof or native gate.'}
    (ROOT / 'qa/NATIVE_READONLY_STATIC_CHECK_R02.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'originals_unchanged': len(originals),
                      'source_family_transactions': 0, 'save_calls': 0}, indent=2))


if __name__ == '__main__':
    main()
