# -*- coding: utf-8 -*-
import os,json,traceback,hashlib
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101'
SRC=os.path.join(ROOT,'unpacked','REVIEW_RFAs','Kuzco_Bolla_PD3106_BG_R2025_R05_REPAINT_OPTICAL_DIAGNOSTIC_UNAPPROVED.rfa')
OUT=os.path.join(ROOT,'bolla_load_probe_20261101.json')
result={'source':SRC,'status':'STARTED'}
doc=None
try:
    app=__revit__.Application
    doc=app.NewProjectDocument(DB.UnitSystem.Metric)
    result['project_created']=bool(doc)
    result['load_result']=bool(doc.LoadFamily(SRC))
    result['families']=[str(x.Name) for x in DB.FilteredElementCollector(doc).OfClass(DB.Family)]
    matches=[x for x in DB.FilteredElementCollector(doc).OfClass(DB.Family) if 'bolla' in str(x.Name).lower()]
    result['matched_family_count']=len(matches)
    result['load_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    result['status']='LOAD_PASS' if len(matches)==1 else 'LOAD_MISSING'
except Exception as e:
    result['status']='LOAD_FAILED'
    result['error']=str(e)
    result['traceback']=traceback.format_exc()[-3200:]
finally:
    if doc:
        try:doc.Close(False)
        except Exception as e:result['close_error']=str(e)
    with open(OUT,'w') as f:f.write(json.dumps(result,indent=2))
print('BOLLA_LOAD_PROBE',result['status'],result.get('error',''))
