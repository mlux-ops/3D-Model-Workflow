import json
import native_query as native
from apply_casing import run

preview=json.loads((native.TASK/'cut_preview_verified.json').read_text())
assert preview['status']=='completed' and preview['result']['transaction_status']=='rolled_back'
assert preview['result']['data']['wall_unchanged']
arguments=json.loads((native.TASK/'apply_cut_arguments.json').read_text())
result=run('cut_native_commit','compiled.modify',{
    'assembly':'C:/ProgramData/CodexNativeRevit/plugins/belmont_window_trim/BelmontWindowTrimCutV4.dll',
    'type':'ApplyWindowTrimCut',
    'purpose':'Apply matching editable panel-border geometry and native void cuts to existing bedroom panel trim, crown and baseboard around the new window',
    'expected_changes':['Create one native editable adaptation family instance','Cut only panel 13138641, crown 13685582 and baseboard 13285841','Preserve exterior wall 13836440 and dimensions 13960635, 13960707, 13962280','No element deletion, save or synchronization'],
    'arguments':arguments})
print(json.dumps({'transaction_status':result['transaction_status'],'result':result['data']}))
