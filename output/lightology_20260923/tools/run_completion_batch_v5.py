# -*- coding: utf-8 -*-
import os,json,datetime,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS=[('F01','f01_816712','build_f01_816712.py'),('F07','f07_833919','build_nodes_payload_expanded.py'),('F09','f09_1254269','build_madame.py'),('F11','f11_1476233','build_mizu.py')]
rows=[]
for key,folder,filename in JOBS:
    path=os.path.join(ROOT,folder,filename);row={'fixture':key,'started_utc':datetime.datetime.utcnow().isoformat()+'Z'}
    try:execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__});row['returned']=True
    except Exception:
        row['returned']=False;row['error']=traceback.format_exc()
        with open(os.path.join(os.path.dirname(os.path.dirname(ROOT)),'PROJECT_MEMORY.md'),'a') as f:f.write('\n- 2026-09-23 final build pass '+key+' failed: '+row['error'].replace('\n',' ')+'; see task report, unresolved pending correction.\n')
    rows.append(row)
    with open(os.path.join(ROOT,'native_completion_batch_v5.json'),'w') as f:json.dump(rows,f,indent=2)
path=os.path.join(ROOT,'tools','export_native_meshes.py')
execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__})