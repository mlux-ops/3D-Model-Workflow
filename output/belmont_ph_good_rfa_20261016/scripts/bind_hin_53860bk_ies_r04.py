# -*- coding: utf-8 -*-
"""Bind exact Hinkley 53860BK official IES to NEW R04 candidate.

IronPython 2.7; isolated pyrevit run only. Refuses to counterfeit a native
LightFamily or save a photometric-web string without real Revit LightType.
Original R03 remains byte-identical; all changes happen in separate RFA,
then save/reopen/fingerprint QA. Never opens active RVT.
"""
from __future__ import print_function
import os,sys,json,hashlib,traceback,uuid
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE=os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R03_UNAPPROVED.rfa')
IES=os.path.join(BASE,'sources','photometry','HIN53860BK_53860_official.ies')
TARGET=os.path.join(BASE,'candidates','Hinkley_Eos_53860BK_R2025_R04_IES_UNAPPROVED.rfa')
REPORT=os.path.join(BASE,'qa','hin_r04_ies_native_qa.json')
SOURCE_SHA='f98a11733c8896549a8a16e956001379df3eb16f76f59acbc2e7197c9713ea70'
IES_SHA='b8f4e409bd01f235c2a6a17024825aca667dc187dd95ceb84a5adec90c50e8b9'
OFFICIAL_URL='https://hinkleymedia.s3.amazonaws.com/Products/files/ies/53860.ies'

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while True:
            b=f.read(1048576)
            if not b:break
            h.update(b)
    return h.hexdigest()

def check(b,reason):
    if not b:raise RuntimeError(reason)

def light_state(doc):
    check(doc.IsFamilyDocument,'Not a family document')
    check(str(doc.OwnerFamily.FamilyCategory.Name)=='Lighting Fixtures','Category mismatch')
    fm=doc.FamilyManager
    types=list(fm.Types)
    check(len(types)==1,'Require one known R03 family type')
    check(fm.CurrentType is not None,'CurrentType absent')
    family=DB.Lighting.LightFamily.GetLightFamily(doc)
    check(family is not None,'BLOCKED_NO_NATIVE_LIGHT_FAMILY: R03 face-based generic template has no physical Revit LightFamily. Need new emitter-equipped native family revision. No file was modified/saved.')
    check(int(family.GetNumberOfLightTypes())==1,'Need exactly one native emitter')
    lt=family.GetLightType(0)
    existing=lt.GetLightDistribution()
    check(isinstance(existing,DB.Lighting.PhotometricWebLightDistribution),
          'BLOCKED_NO_PHOTOMETRIC_WEB_DISTRIBUTION: real emitter must be configured to photometric web before binding')
    param=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    check(param is not None and str(param.StorageType)=='String','Native photometric family Type parameter absent')
    return fm,lt,existing,param

def readback(doc):
    fm,lt,dist,param=light_state(doc)
    return {'web_distribution_file':str(dist.PhotometricWebFile or ''),
            'family_type_file':str(fm.CurrentType.AsString(param) or ''),
            'family_type':str(fm.CurrentType.Name),
            'family_category':str(doc.OwnerFamily.FamilyCategory.Name),
            'warnings':[str(x.GetDescriptionText()) for x in doc.GetWarnings()]}

def main():
    check(sys.version_info[0]==2,'Requires IronPython 2.7')
    check(str(__revit__.Application.VersionNumber)=='2025','Requires Revit 2025')
    check(getattr(__revit__,'ActiveUIDocument',None) is None,'Requires isolated document-free pyrevit session')
    check(not os.path.lexists(TARGET) and not os.path.lexists(REPORT),'Refuse overwrite')
    check(os.path.isfile(SOURCE) and sha(SOURCE)==SOURCE_SHA,'R03 source SHA mismatch')
    check(os.path.isfile(IES) and sha(IES)==IES_SHA,'Official IES SHA mismatch')
    with open(IES,'rb') as f:head=f.read(600).decode('ascii')
    check('[LUMINAIRE] 53860BK' in head and '[MANUFAC] Hinkley' in head and
          'IESNA:LM-63-2002' in head,'IES source identity mismatch')
    app=__revit__.Application
    report={'source_rfa':SOURCE,'source_sha256':SOURCE_SHA,'ies':IES,
            'official_ies_url':OFFICIAL_URL,'ies_sha256':IES_SHA,
            'catalog':{'lamp_name':'5386XD','watts':19,'cct_k':3000,
                       'lumens':1000,'cri':93,'voltage_v':120},
            'ies_lab':{'watts':18.45,'lumens':1109,'date':'2024-08-15'},
            'candidate':TARGET,'status':'STARTED'}
    doc=None;reopened=None;tx=None;stage=None
    try:
        doc=app.OpenDocumentFile(SOURCE)
        fm,lt,dist,param=light_state(doc)
        prior=readback(doc)
        tx=DB.Transaction(doc,'Bind exact official Hinkley 53860BK IES')
        check(tx.Start()==DB.TransactionStatus.Started,'Transaction failed')
        dist.PhotometricWebFile=IES
        lt.SetLightDistribution(dist)
        fm.Set(param,IES)
        doc.Regenerate()
        check(os.path.basename(readback(doc)['web_distribution_file']).lower()==
              os.path.basename(IES).lower(),'LightType IES setter failed')
        check(os.path.basename(readback(doc)['family_type_file']).lower()==
              os.path.basename(IES).lower(),'Family Type IES setter failed')
        check(tx.Commit()==DB.TransactionStatus.Committed,'Commit failed')
        tx=None
        stage=os.path.join(BASE,'candidates','_stage_hin_ies_'+uuid.uuid4().hex+'.rfa')
        opts=DB.SaveAsOptions()
        opts.OverwriteExistingFile=False
        opts.MaximumBackups=1
        doc.SaveAs(stage,opts)
        doc.Close(False)
        doc=None
        reopened=app.OpenDocumentFile(stage)
        state=readback(reopened)
        check(os.path.basename(state['web_distribution_file']).lower()==
              os.path.basename(IES).lower(),'Saved LightType IES mismatch')
        check(os.path.basename(state['family_type_file']).lower()==
              os.path.basename(IES).lower(),'Saved Family Type IES mismatch')
        check(state['warnings']==prior['warnings'],'Additional warnings on reopen')
        reopened.Close(False)
        reopened=None
        check(sha(SOURCE)==SOURCE_SHA,'Source changed unexpectedly')
        check(not os.path.lexists(TARGET),'Candidate path appeared')
        os.rename(stage,TARGET)
        stage=None
        report['status']='NATIVE_IES_BIND_REOPEN_PASS_VISUAL_AND_PORTABILITY_HOLD'
        report['reopened_state']=state
        report['candidate_sha256']=sha(TARGET)
        report['physical_geometry_unchanged']='NOT_INDEPENDENTLY_REMEASURED'
        report['ies_cache_portability']='NOT_VERIFIED_COMPANION_IES_REQUIRED'
    except Exception:
        report['status']='BLOCKED_OR_ERROR'
        report['error']=traceback.format_exc()
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        for document in [reopened,doc]:
            if document is not None:
                try:document.Close(False)
                except Exception:pass
        report['source_hash_after']=sha(SOURCE)
        report['source_preserved']=report['source_hash_after']==SOURCE_SHA
        if not os.path.lexists(REPORT):
            with open(REPORT,'w') as f:json.dump(report,f,indent=2)
        print('HIN_53860_R04 '+report['status'])
        print('REPORT '+REPORT)
    check(report['status'].startswith('NATIVE_IES_BIND'),report.get('error','IES native hold'))

main()
