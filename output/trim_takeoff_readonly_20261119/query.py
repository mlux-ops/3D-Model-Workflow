import importlib.util,json,tomllib
from pathlib import Path
root=Path.cwd();task=root/'output/trim_takeoff_readonly_20261119'
spec=importlib.util.spec_from_file_location('native',root/'output/codex-native-revit-20261013/controller/native_revit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
e=tomllib.loads((Path.home()/'.codex/config.toml').read_text(encoding='utf-8-sig'))['mcp_servers']['codex-native-revit-2025']['env'];client=m.Client(base_url=e['CODEX_NATIVE_REVIT_URL'],token_file=e['CODEX_NATIVE_REVIT_TOKEN_FILE'],receipt_dir=task/'receipts');client.token=None
doc={'session_id':'757b186f-3d69-41f0-8a59-587e86130d17','path':'Autodesk Docs://25 012 - 651 W. Belmont/25-012 651 W. Belmont_Issue for Construction_.rvt'};pre={'expected_title':'25-012 651 W. Belmont_Issue for Construction_','is_family':False}
def query(name,op,args):
 assert op in ['context.query','elements.query','elements.inspect','compiled.query','parameters.query','documents.list']
 r=client.submit(op,doc,args,pre);oid=r['operation_id'];print('SUBMITTED',name,oid,flush=True);r=client.wait(oid,timeout_seconds=25);(task/(name+'.json')).write_text(json.dumps(r,indent=2));print('STATUS',r['status'],r.get('error'),flush=True)
 if r['status']!='completed':raise RuntimeError(oid)
 return r['result']
if __name__=='__main__':
 r=query('casework_current','elements.query',{'category':'OST_Casework','limit':500})
 print(json.dumps({'next_offset':r.get('next_offset'),'items':[v for v in r['items'] if 'rim' in v['name'] or '45' in v['name'] or v['id']==13688525]}))
