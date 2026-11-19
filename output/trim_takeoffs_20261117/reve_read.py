import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'output/codex-native-revit-20261013/controller'))
from native_revit import Client
out=Path(__file__).parent/'belmont_reve_sources';out.mkdir(exist_ok=True)
c=Client(receipt_dir=out/'receipts')
def call(op,doc,args,name,pre={}):
 r=c.submit(op,doc,args,pre);r=c.wait(r['operation_id'],30);(out/(name+'.json')).write_text(json.dumps(r,indent=2));return r
r=call('documents.list',{}, {},'documents');doc={'session_id':next(x['session_id'] for x in r['result'] if 'Belmont' in x['title'])};pre={'expected_title':'25-012 651 W. Belmont_Issue for Construction_','is_family':False,'allow_existing_document':True}
for name in ['2ND FLOOR','3RD FLOOR','ENTRY']:
 r=call('elements.query',doc,{'class':'View','name_contains':name,'limit':500},name.replace(' ','_'),pre);print([(x['id'],x['name'],x['unique_id']) for x in r.get('result',{}).get('items',[])])
for id,uid in [(7911391,'94c917a9-8b45-449d-a752-5283a706eaf8-0078b7df'),(4948502,'4dd28a71-15a6-464c-990d-001abe92aae4-004b8216'),(4961593,'6e48899a-0860-4e4b-baec-ed9b0c84af64-004bb539')]:
 r=call('capture.export',doc,{'view':uid,'pixels':4200,'path_prefix':str(out/('view_'+str(id)))},'export_'+str(id),pre);print(r.get('result'),r.get('error'))
print(call('elements.query',doc,{'class':'Wall','limit':500},'walls0',pre).get('status'))
