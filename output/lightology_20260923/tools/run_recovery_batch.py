# -*- coding: utf-8 -*-
"""Serialize only prime-owned native operations; record each result independently."""
import os,json,datetime,traceback
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jobs=[os.path.join(root,'f08_1104949','build_cassia.py'),os.path.join(root,'f05_1441643','build_dimple.py'),os.path.join(root,'tools','audit_brenta_source.py')]
report=[]
for path in jobs:
    row={'script':path,'started_utc':datetime.datetime.utcnow().isoformat()+'Z'}
    try:
        execfile(path,{'__revit__':__revit__,'__file__':path,'__name__':'__main__'})
        row['script_returned']=True
    except Exception:row['error']=traceback.format_exc();row['script_returned']=False
    report.append(row)
    with open(os.path.join(root,'native_batch_recovery.json'),'w') as stream:json.dump(report,stream,indent=2)