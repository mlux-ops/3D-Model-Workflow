"""Probe strictly allow-listed Revit READ operations for parameter and geometry schemas."""
import json,sys,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
cases=[
  ('parameters.query',{'element_id':15926311}),
  ('parameters.query',{'id':15926311}),
  ('parameters.query',{'element_ids':[15926311],'parameter_names':['Number','Name','Room']}),
  ('elements.inspect',{'id':15926311}),
  ('elements.inspect',{'ids':[15926311]}),
  ('view.inspect',{'id':1084918}),
  ('api.lookup',{'name':'Autodesk.Revit.DB.Room'}),
]
for op,args in cases:
    file=P/'scratch/viewer3d_temp_read_args.json'
    file.write_text(json.dumps(args),encoding='utf-8')
    c=[sys.executable,'-B',str(P/'tools/revit_read.py'),op,'--title','25-006 1527 N Wieland','--args-file',str(file)]
    result=subprocess.run(c,capture_output=True,text=True,timeout=35)
    print(op,args,'EXIT',result.returncode,'OUTPUT',(result.stdout or result.stderr)[:360],flush=True)
