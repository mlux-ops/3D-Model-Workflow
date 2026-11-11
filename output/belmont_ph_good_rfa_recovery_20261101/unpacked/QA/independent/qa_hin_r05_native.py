# -*- coding: utf-8 -*-
"""R03 independent read-only native inspection, isolated pyrevit run."""
import os
import sys
import json
import hashlib
import traceback
BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
RFA=os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R05_NATIVE_LIGHT_IES_UNAPPROVED.rfa')
PRIOR=os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R03_UNAPPROVED.rfa')
SCRIPT=os.path.join(BASE,'qa','qa_hin_r03_core.py')
REPORT=os.path.join(BASE,'qa','hin_r05_independent_native_qa.json')
if os.path.lexists(REPORT):
    raise RuntimeError('R05 QA receipt already exists')
if not os.path.isfile(RFA):
    raise RuntimeError('R05 RFA not yet built')
if getattr(__revit__,'ActiveUIDocument',None) is not None:
    raise RuntimeError('Requires document-free isolated Revit process')
if str(__revit__.Application.VersionNumber)!='2025':
    raise RuntimeError('Requires Revit 2025')
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while True:
            b=f.read(1024*1024)
            if not b:break
            h.update(b)
    return h.hexdigest()
before={p:sha(p) for p in [RFA,PRIOR]}
scope={'__name__':'__main__','__file__':SCRIPT,'__revit__':__revit__,
       'APP':__revit__.Application,'DB':DB,'SOURCE_RFA':RFA,'TARGET_RFA':None,
       'progress':lambda *args:None,'result':{}}
report={'target':RFA,'status':'STARTED','protected_before':before}
try:
    execfile(SCRIPT,scope)
    result=scope['result']
    report['original_native_checks']=result
    actual=result.get('measured_dimensions_in')
    assert actual is not None and len(actual)==3
    expected=[25.0,5.5,3.0]
    delta=[float(actual[i])-expected[i] for i in range(3)]
    report['published_xyz_in']=expected
    report['measured_xyz_in']=actual
    report['difference_in']=delta
    report['dimension_within_1mm']=all(abs(d)<=1./25.4 for d in delta)
    report['native_qa_pass']=bool(result.get('native_qa_pass') and report['dimension_within_1mm'])
    doc=__revit__.Application.OpenDocumentFile(RFA)
    try:
        lf=DB.Lighting.LightFamily.GetLightFamily(doc)
        light=lf.GetLightType(0)
        distribution=light.GetLightDistribution()
        report['native_light_family']=bool(lf is not None)
        report['light_type_class']=str(distribution.GetType().Name)
        report['ies_path']=str(distribution.PhotometricWebFile)
        report['native_ies_exact']=os.path.basename(report['ies_path']).lower()=='hin53860bk_53860_official.ies'
        report['native_kelvin']=float(light.GetInitialColor().Temperature)
        report['native_flux_lm']=float(light.GetInitialIntensity().Flux)
        report['native_emitter_position_ft']=[float(lf.GetLightSourceTransform().Origin.X),float(lf.GetLightSourceTransform().Origin.Y),float(lf.GetLightSourceTransform().Origin.Z)]
        report['emitter_outside_depth']=report['native_emitter_position_ft'][2]>3.0/12.0
        report['native_qa_pass']=bool(report['native_qa_pass'] and report['native_ies_exact'] and abs(report['native_kelvin']-3000.)<1 and abs(report['native_flux_lm']-1109.)<1 and report['emitter_outside_depth'])
    finally:
        doc.Close(False)
    report['status']='TECHNICAL_PASS_VISUAL_HOLD' if report['native_qa_pass'] else 'HOLD'
    report['visual_comparison']='PENDING_OFFICIAL_FRONT_AND_OBLIQUE_REVIEW'
    report['oem_part_identity']='PHOTO_INFERRED_FACE_COVER_AND_DIFFUSER'
    report['photometric_ies']='UNVERIFIED'
except Exception:
    report['status']='ERROR'
    report['error']=traceback.format_exc()
finally:
    report['protected_after']={p:sha(p) for p in before}
    report['protected_unchanged']=(report['protected_before']==report['protected_after'])
    if not report['protected_unchanged']:report['status']='HASH_CHANGE_HOLD'
    with open(REPORT,'wb') as f:
        f.write(json.dumps(report,indent=2,ensure_ascii=True,default=str).encode('ascii'))
