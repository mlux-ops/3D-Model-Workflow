# -*- coding: utf-8 -*-
"""Build Hinkley source-informed R02 as an independent unapproved candidate."""
import os,json,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SCRIPT=os.path.join(BASE,'scripts','build_hin_53860bk_r02.py')
TARGET=os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R02_UNAPPROVED.rfa')
OUT=os.path.join(BASE,'runner','receipts','hin_r02_build.json')
if os.path.exists(TARGET):raise RuntimeError('Hinkley R02 target already exists')
if not os.path.isdir(os.path.dirname(TARGET)):os.makedirs(os.path.dirname(TARGET))
scope={'__name__':'__main__','__file__':SCRIPT,'__revit__':__revit__,
       'APP':__revit__.Application,'DB':DB,'JOB':{'id':'hin990485_r02'},
       'TARGET_RFA':TARGET,'SOURCE_RFA':None,
       'progress':lambda stage,detail=None:None,'result':{}}
receipt={'target':TARGET,'source_builder':SCRIPT,'status':'STARTED'}
try:
    execfile(SCRIPT,scope)
    receipt['builder_result']=scope['result']
    doc=__revit__.Application.OpenDocumentFile(TARGET)
    try:
        receipt['family_category']=doc.OwnerFamily.FamilyCategory.Name
        receipt['warnings']=[x.GetDescriptionText() for x in doc.GetWarnings()]
        receipt['status']='TECHNICAL_REOPEN_PASS' if doc.IsFamilyDocument and receipt['family_category']=='Lighting Fixtures' and not receipt['warnings'] else 'HOLD'
    finally:doc.Close(False)
except Exception:
    receipt['status']='FAIL'
    receipt['error']=traceback.format_exc()
with open(OUT,'w') as f:json.dump(receipt,f,indent=2,default=str)
print('HIN_R02',receipt['status'])
