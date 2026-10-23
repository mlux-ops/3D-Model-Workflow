# -*- coding: utf-8 -*-
import os,json,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SCRIPT=os.path.join(BASE,'scripts','qa_quo_r02_native.py')
RFA=os.path.join(BASE,'candidates','Quorum_Veno_858-59_R2025_R02_UNAPPROVED.rfa')
OUTPUT=os.path.join(BASE,'runner','receipts','quo_r02_native_qa.json')
scope={'__revit__':__revit__,'APP':__revit__.Application,'DB':DB,
       'JOB':{'id':'quo_r02'},'TARGET_RFA':RFA,'SOURCE_RFA':RFA,
       'progress':lambda stage,detail=None:None,'result':{},'__file__':SCRIPT,'__name__':'__main__'}
receipt={}
try:
    execfile(SCRIPT,scope)
    receipt=scope['result']
except Exception:
    receipt={'status':'FAIL','error':traceback.format_exc(),'partial_result':scope['result']}
with open(OUTPUT,'w') as f:json.dump(receipt,f,indent=2,default=str)
print('QUO_R02_QA',receipt.get('native_qa_pass',False))
