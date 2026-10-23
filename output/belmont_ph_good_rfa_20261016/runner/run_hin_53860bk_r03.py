# -*- coding: utf-8 -*-
"""Isolated pyRevit 2025 entry; build once, never overwrite or touch open RVT."""
import os
import json
import traceback
import time
BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SCRIPT = os.path.join(BASE,'scripts','build_hin_53860bk_r03.py')
TARGET = os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R03_UNAPPROVED.rfa')
RECEIPT = os.path.join(BASE,'runner','receipts','hin_r03_build.json')
if os.path.lexists(TARGET) or os.path.lexists(RECEIPT):
    raise RuntimeError('R03 target or receipt exists; no overwrite')
if str(__revit__.Application.VersionNumber)!='2025':
    raise RuntimeError('Requires Revit 2025')
if getattr(__revit__,'ActiveUIDocument',None) is not None:
    raise RuntimeError('Use document-free isolated pyrevit run')
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
steps=[]
def progress(stage, detail=None):
    steps.append({'stage':stage,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    print('HINKLEY_R03 '+stage)
receipt={'target':TARGET,'source_builder':SCRIPT,'status':'STARTED'}
scope={'__name__':'__main__','__file__':SCRIPT,'__revit__':__revit__,
       'APP':__revit__.Application,'DB':DB,'JOB':{'id':'hin_r03'},
       'TARGET_RFA':TARGET,'SOURCE_RFA':None,'progress':progress,'result':{}}
try:
    execfile(SCRIPT,scope)
    receipt['builder_result']=scope['result']
    receipt['status']='SAVED_PENDING_INDEPENDENT_NATIVE_QA'
except Exception:
    receipt['status']='ERROR'
    receipt['error']=traceback.format_exc()
    raise
finally:
    receipt['progress']=steps
    if not os.path.lexists(RECEIPT):
        with open(RECEIPT,'wb') as f:
            f.write(json.dumps(receipt,indent=2,ensure_ascii=True,default=str).encode('ascii'))
