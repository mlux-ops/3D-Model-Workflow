# -*- coding: utf-8 -*-
import os,json,traceback,datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS=[('F03','f03_1241670','build_brenta.py'),('F06','f06_1418164','build_vantage.py'),('F02','f02_231180','build_ic_cw1.py'),('F07','f07_833919','build_nodes_payload_expanded.py')]
rows=[]
for key,folder,name in JOBS:
    path=os.path.join(ROOT,folder,name);row={'fixture':key,'started_utc':datetime.datetime.utcnow().isoformat()+'Z'}
    try:execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__});row['returned']=True
    except Exception:
        row['returned']=False;row['error']=traceback.format_exc()
        with open(os.path.join(os.path.dirname(os.path.dirname(ROOT)),'PROJECT_MEMORY.md'),'a') as f:f.write('\n- 2026-09-23 '+key+' proof batch failure: '+row['error'].replace('\n',' ')+'; review task report and correct cause.\n')
    rows.append(row)
    with open(os.path.join(ROOT,'native_proof_batch_v3.json'),'w') as f:json.dump(rows,f,indent=2)
path=os.path.join(ROOT,'tools','export_native_meshes.py')
execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__})