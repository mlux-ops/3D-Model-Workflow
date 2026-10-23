# -*- coding: utf-8 -*-
from __future__ import print_function
import os,json,traceback,time
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SCRIPT=os.path.join(BASE,'scripts','qa_hin_quo_native.py')
OUT=os.path.join(BASE,'runner','receipts','custom_qa.json')
families=[('hin990485','Hinkley_Eos_53860BK_R2025.rfa'),('quo1249827','Quorum_Veno_858-59_R2025.rfa')]
results=[]
for sku,name in families:
    path=os.path.join(BASE,'families',name)
    env={'__revit__':__revit__,'APP':__revit__.Application,'DB':DB,'JOB':{'id':sku},'TARGET_RFA':path,'SOURCE_RFA':path,'result':{},'progress':lambda stage,detail=None:None,'__file__':SCRIPT,'__name__':'__main__'}
    try:
        execfile(SCRIPT,env)
        results.append({'id':sku,'status':'PASS' if env['result'].get('native_qa_pass') else 'HOLD','detail':env['result']})
    except Exception:
        results.append({'id':sku,'status':'FAIL','error':traceback.format_exc(),'detail':env.get('result')})
with open(OUT,'w') as f:json.dump({'timestamp':time.time(),'results':results},f,indent=2,default=str)
print('CUSTOM_QA',[(x['id'],x['status']) for x in results])
