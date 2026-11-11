# -*- coding: utf-8 -*-
import os,json,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101'
SRC=os.path.join(ROOT,'unpacked','REVIEW_RFAs','Kuzco_Bolla_PD3106_BG_R2025_R05_REPAINT_OPTICAL_DIAGNOSTIC_UNAPPROVED.rfa')
OUT=os.path.join(ROOT,'bolla_load_probe_alt_20261101.json')
app=__revit__.Application
report={}
project=None
family=None
try:
    project=app.NewProjectDocument(DB.UnitSystem.Metric)
    family=app.OpenDocumentFile(SRC)
    report['family_name']=str(family.OwnerFamily.Name)
    report['family_warnings']=[w.GetDescriptionText() for w in family.GetWarnings()]
    report['family_is_modifiable']=bool(family.IsModifiable)
    report['family_types']=[str(t.Name) for t in family.FamilyManager.Types]
    loaded=family.LoadFamily(project)
    report['load_return_type']=str(type(loaded))
    report['loaded_name']=str(loaded.Name) if loaded is not None else None
    report['status']='LOAD_PASS' if loaded is not None else 'LOAD_MISSING'
except Exception as e:
    report['status']='LOAD_EXCEPTION'
    report['error']=str(e)
    report['traceback']=traceback.format_exc()[-3800:]
finally:
    if family:family.Close(False)
    if project:project.Close(False)
    with open(OUT,'w') as f:f.write(json.dumps(report,indent=2))
print('BOLLA_ALTERNATIVE_LOAD',report['status'],report.get('error',''))
