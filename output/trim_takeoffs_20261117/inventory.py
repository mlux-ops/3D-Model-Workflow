import sys,json,os
from pathlib import Path
sys.path.insert(0,'output/codex-native-revit-20261013/controller')
from native_revit import Client
out=Path('output/trim_takeoffs_20261117')
c=Client(base_url='http://127.0.0.1:49327',token_file=Path(os.environ['LOCALAPPDATA'])/'CodexNativeRevit/token',receipt_dir=out/'receipts')
docs=json.loads((out/'documents.json').read_text())['result']
def query(d,label,op,args):
 r=c.submit(op,{'session_id':d['session_id'],'path':d['path']},args,{'expected_title':d['title'],'is_family':False,'allow_existing_document':True})
 r=c.wait(r['operation_id'],30); (out/(label+'.json')).write_text(json.dumps(r,indent=2)); print(label,json.dumps(r),flush=True)
for i,d in enumerate(docs):
 prefix=['belmont','wieland'][i]
 query(d,prefix+'_context','context.query',{})
 query(d,prefix+'_sweeps','elements.query',{'class':'WallSweep','limit':500})
 query(d,prefix+'_trim','elements.query',{'name_contains':'trim','limit':500})
 query(d,prefix+'_casework','elements.query',{'category':'OST_Casework','limit':500})
query(docs[0],'plugin_check','compiled.query',{'assembly':'C:/ProgramData/CodexNativeRevit/plugins/belmont_window_trim/BelmontBedroomTrimInspect.dll','type':'BedroomTrimInspect','purpose':'Read-only access validation for trim takeoff','expected_changes':[],'arguments':{'elements':[]}})
