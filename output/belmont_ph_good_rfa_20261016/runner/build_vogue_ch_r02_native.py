# -*- coding: utf-8 -*-
"""Create source-guarded Vogue Chrome candidate in isolated pyRevit 2025."""
import os,json,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SCRIPT=os.path.join(BASE,'scripts','revise_oem_vogue_ch_r01.py')
SOURCE=os.path.join(BASE,'families','ModernForms_Vogue_WS-3127_CH_R2025.rfa')
TARGET=os.path.join(BASE,'candidates','ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa')
OUT=os.path.join(BASE,'runner','receipts','vogue_ch_r02_build.json')
if os.path.exists(TARGET):raise RuntimeError('Candidate already exists')
scope={'__name__':'__main__','__file__':SCRIPT,'__revit__':__revit__,
       'APP':__revit__.Application,'DB':DB,'JOB':{'id':'mfr201959_r02'},
       'TARGET_RFA':TARGET,'SOURCE_RFA':SOURCE,
       'progress':lambda stage,detail=None:None,'result':{}}
receipt={'target':TARGET,'source':SOURCE,'status':'STARTED'}
try:
    execfile(SCRIPT,scope)
    receipt['builder_result']=scope['result']
    if os.path.isfile(TARGET):
        receipt['status']='SAVED_AND_REOPENED_REVIEW_CANDIDATE'
    else:raise RuntimeError('Builder did not save candidate')
except Exception:
    receipt['status']='FAIL'
    receipt['error']=traceback.format_exc()
with open(OUT,'w') as f:json.dump(receipt,f,indent=2,default=str)
print('VOGUE_CH_R02',receipt['status'])
