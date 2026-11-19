import sys,json,os
from pathlib import Path
sys.path.insert(0,'output/codex-native-revit-20261013/controller')
from native_revit import Client
out=Path('output/trim_takeoffs_20261117')
c=Client(base_url='http://127.0.0.1:49327',token_file=Path(os.environ['LOCALAPPDATA'])/'CodexNativeRevit/token',receipt_dir=out/'receipts')
r=c.submit('documents.list',{},{}); r=c.wait(r['operation_id'],30)
(out/'documents.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
