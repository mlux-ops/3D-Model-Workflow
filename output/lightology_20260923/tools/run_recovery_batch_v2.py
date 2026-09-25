# -*- coding: utf-8 -*-
"""Serialized native execution of prepared/stalled-worker deliverables."""
import os,json,datetime,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS=[('F12','f12_813073','build_f12_orbel.py'),('F01','f01_816712','build_f01_816712.py'),('F03','f03_1241670','build_brenta.py'),('F04','f04_1149899','build_forked.py'),('F05','f05_1441643','build_dimple.py'),('F06','f06_1418164','build_vantage.py'),('F08','f08_1104949','build_cassia.py'),('F10','f10_1242580','build_covet.py')]
result=[]
for label,folder,filename in JOBS:
    path=os.path.join(ROOT,folder,filename);row={'task':label,'script':path,'started_utc':datetime.datetime.utcnow().isoformat()+'Z','returned':False}
    try:
        execfile(path,{'__revit__':__revit__,'__file__':path,'__name__':'__main__'})
        row['returned']=True
    except Exception:
        row['error']=traceback.format_exc()
        with open(os.path.join(os.path.dirname(os.path.dirname(ROOT)),'PROJECT_MEMORY.md'),'a') as log:
            log.write('\n- '+datetime.datetime.utcnow().strftime('%Y-%m-%d')+' '+label+' recovery native batch failed: '+row['error'].replace('\n',' ')+'; cause and repair pending review of task validation.\n')
    row['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z';result.append(row)
    with open(os.path.join(ROOT,'native_recovery_batch_v2.json'),'w') as f:json.dump(result,f,indent=2)
mesh=os.path.join(ROOT,'tools','export_native_meshes.py')
try:execfile(mesh,{'__revit__':__revit__,'__file__':mesh,'__name__':'__main__'})
except Exception:
    with open(os.path.join(ROOT,'native_mesh_export_error.txt'),'w') as f:f.write(traceback.format_exc())