import importlib.util
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
TASK = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'native-revit.json').read_text())
spec = importlib.util.spec_from_file_location('controller', ROOT / manifest['controller'])
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)
settings = tomllib.loads((Path.home() / '.codex/config.toml').read_text(encoding='utf-8-sig'))['mcp_servers'][manifest['integration']]['env']
client = controller.Client(base_url=settings['CODEX_NATIVE_REVIT_URL'], token_file=settings['CODEX_NATIVE_REVIT_TOKEN_FILE'])
client.token = None
DOCUMENT = {'session_id': 'd9136c2f-5567-4bc5-9bc4-e8bd4b966f6c', 'path': 'Autodesk Docs://25 012 - 651 W. Belmont/25-012 651 W. Belmont_Issue for Construction_.rvt'}
PRECONDITIONS = {'expected_title': '25-012 651 W. Belmont_Issue for Construction_', 'is_family': False}

def query(label, operation, arguments):
    if operation not in {'context.query', 'elements.query', 'elements.inspect', 'parameters.query', 'api.lookup', 'view.inspect', 'warnings.query', 'capture.export', 'compiled.query'}:
        raise ValueError('Read-only helper refuses this operation')
    preconditions = dict(PRECONDITIONS)
    if operation == 'capture.export':
        preconditions['allow_existing_document'] = True
    receipt = client.submit(operation, DOCUMENT, arguments, preconditions)
    operation_id = receipt['operation_id']
    print(json.dumps({'label': label, 'operation_id': operation_id}), flush=True)
    receipt = client.wait(operation_id, timeout_seconds=25)
    (TASK / (label + '.json')).write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'label': label, 'status': receipt['status'], 'saved_to': str(TASK / (label + '.json')), 'error': receipt.get('error')}), flush=True)
    if receipt['status'] != 'completed':
        raise RuntimeError('Reconcile original job ' + operation_id)
    return receipt['result']

if __name__ == '__main__':
    query(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]))
