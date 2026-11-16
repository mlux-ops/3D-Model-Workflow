"""Copy the existing building trim and size only the new instance."""
import json
from pathlib import Path
import native_query as native

def run(label, operation, arguments, document=None, preconditions=None):
    destination = native.TASK / (label + '.json')
    if destination.exists():
        raise RuntimeError('Existing receipt: reconcile before running again: ' + str(destination))
    if preconditions is None:
        preconditions = dict(native.PRECONDITIONS, allow_existing_document=True)
    receipt = native.client.submit(operation, native.DOCUMENT if document is None else document, arguments, preconditions)
    destination.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'label':label,'operation_id':receipt['operation_id']}), flush=True)
    receipt = native.client.wait(receipt['operation_id'], timeout_seconds=25)
    destination.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'label':label,'status':receipt['status'],'error':receipt.get('error')}), flush=True)
    if receipt['status'] != 'completed':
        raise RuntimeError('Reconcile original operation ' + receipt['operation_id'])
    return receipt['result']

if __name__ == '__main__':
    source = '79604fd5-7f98-4516-a061-568bee79594d-00cd6422'
    source_point = [74.45456524299492, -56.69033126641836, 37.666666666666664]
    target_point = [37.33999190966225, -55.69033126642166, 37.666666666666664]
    copied = run('casing_copy', 'element.copy', {'element':source,'vector':[b-a for a,b in zip(source_point,target_point)]})
    (native.TASK / 'casing_copy_result.json').write_text(json.dumps(copied, indent=2), encoding='utf-8')
    print(json.dumps({'transaction_status':copied['transaction_status'],'created':copied['data']['after']}), flush=True)
