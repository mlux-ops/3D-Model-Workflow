import json
import native_query as native
from apply_casing import run

symbol=json.loads((native.TASK/'adaptation_loaded_type.json').read_text())['result']['items'][0]
arguments={'type':symbol['unique_id'],'point':[37.33999190966225,-55.69033126642166,37.666666666666664]}
(native.TASK/'apply_cut_arguments.json').write_text(json.dumps(arguments,indent=2))
result=run('cut_native_preview','compiled.query',{'assembly':'C:/ProgramData/CodexNativeRevit/plugins/belmont_window_trim/BelmontWindowTrimCutV2.dll','type':'PreviewWindowTrimCut','purpose':'Validate native window trim cuts, protected wall and all three existing dimensions, then roll back completely','expected_changes':[],'arguments':arguments})
print(json.dumps(result))
