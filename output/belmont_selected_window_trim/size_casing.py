import json
import native_query as native
from apply_casing import run

copied = json.loads((native.TASK/'casing_copy_result.json').read_text())
element = copied['data']['after'][0]['unique_id']
steps = [{'operation':'parameter.set','arguments':{'element':element,'name':name,'value':value}} for name,value in [
    ('Window_Width',3.0),('Sill_Height',2/3),('Head_Height',28/3),('Comments','SHB trim for fourth-floor primary bedroom window group 14122480')]]
result = run('casing_size','batch.atomic',{'steps':steps})
print(json.dumps({'element':element,'transaction_status':result['transaction_status'],'bounds':[e['bounds'] for e in result['actual_elements'] if e['unique_id']==element]}))
