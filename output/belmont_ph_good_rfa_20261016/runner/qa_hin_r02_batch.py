# -*- coding: utf-8 -*-
import os,json,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SCRIPT=os.path.join(BASE,'scripts','qa_hin_r02_native.py')
RFA=os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R02_UNAPPROVED.rfa')
OUTPUT=os.path.join(BASE,'runner','receipts','hin_r02_native_qa.json')
scope={'__revit__':__revit__,'APP':__revit__.Application,'DB':DB,
       'JOB':{'id':'hin_r02'},'TARGET_RFA':RFA,'SOURCE_RFA':RFA,
       'progress':lambda stage,detail=None:None,'result':{},'__file__':SCRIPT,'__name__':'__main__'}
receipt={}
try:
    execfile(SCRIPT,scope)
    receipt=scope['result']
except Exception:
    receipt={'status':'FAIL','error':traceback.format_exc(),'partial_result':scope['result']}
receipt['published_oem_envelope_in']=[25.0,5.5,3.0]
receipt['modeled_height_shortfall_in']=0.75
receipt['release_status']='HOLD_UNTIL_HEIGHT_AND_SILHOUETTE_CONFIRMED'
with open(OUTPUT,'w') as f:json.dump(receipt,f,indent=2,default=str)
print('HIN_R02_QA',receipt.get('native_qa_pass',False),'OEM_DIM_HOLD',receipt['modeled_height_shortfall_in'])
