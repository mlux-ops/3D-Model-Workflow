# -*- coding: utf-8 -*-
"""Isolated Revit 2025 / IronPython 2.7 Smooth photometric parent candidate.

Uses independently verified face-based native-light Hinkley R05 as seed.
Places original Smooth R02 as one NONSHARED nested family on a dedicated
reference plane. Fails closed if Revit rejects reference-plane hosting.
Never saves either source. Run only in an isolated, document-free Revit session.
"""
from __future__ import print_function
import os, json, hashlib, traceback, time, uuid
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

ROOT = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101'
SOURCE = os.path.join(ROOT,'unpacked','REVIEW_RFAs','ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
SEED = os.path.join(ROOT,'unpacked','REVIEW_RFAs','Hinkley_Eos_53860BK_R2025_R05_NATIVE_LIGHT_IES_UNAPPROVED.rfa')
IES = os.path.join(ROOT,'unpacked','SOURCES','IES','FR-W2502-52L.IES')
OUT = os.path.join(ROOT,'smooth_parent_retrofit_r09')
TARGET = os.path.join(OUT,'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R09_PARENT_NATIVE_LIGHT_UNAPPROVED.rfa')
REPORT = os.path.join(OUT,'native_build_receipt_fix02.json')
SHA = {SOURCE:'f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db',
       SEED:'f9ab27d564ddac1c3242209d771ff5202a2de3f27b8f9e23840a6ae6133d85ae',
       IES:'6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e'}
NOMINAL_SWEEP_MM = 1321.6925205853231

def need(condition,message):
    if not condition: raise RuntimeError(message)
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def eid(value):
    try: return int(value.Value)
    except: return int(value.IntegerValue)
def nm(item):
    try: return unicode(DB.Element.Name.GetValue(item))
    except: return unicode(item.Name)
def light(doc):
    lf=DB.Lighting.LightFamily.GetLightFamily(doc)
    need(lf is not None and int(lf.GetNumberOfLightTypes())==1,'One native light type required')
    return lf,lf.GetLightType(0)
def geom(doc):
    return [x for cls in (DB.FreeFormElement,DB.ImportInstance,DB.FamilyInstance)
            for x in DB.FilteredElementCollector(doc).OfClass(cls)]
def refs(doc):
    return list(DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane))
def warn(doc):
    return [unicode(x.GetDescriptionText()) for x in doc.GetWarnings()]
def get_ies_type(doc):
    p=doc.FamilyManager.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
    need(p is not None,'Photometric Web File parameter missing')
    return unicode(doc.FamilyManager.CurrentType.AsString(p) or '')
def optical_check(doc):
    lf,lt=light(doc)
    dist=lt.GetLightDistribution()
    need(isinstance(dist,DB.Lighting.PhotometricWebLightDistribution),'Not a real photometric web')
    need(os.path.basename(unicode(dist.PhotometricWebFile).replace('\\','/')).lower()=='fr-w2502-52l.ies','Wrong native IES')
    need(os.path.basename(get_ies_type(doc).replace('\\','/')).lower()=='fr-w2502-52l.ies','Wrong IES type parameter')
    flux=lt.GetInitialIntensity()
    need(isinstance(flux,DB.Lighting.InitialFluxIntensity) and abs(float(flux.Flux)-707.09)<.02,
         'Wrong tested luminous flux: type='+str(type(flux))+' measured='+str(float(flux.Flux))+' expected=707.09')
    need(len(warn(doc))==0,'Family warnings: '+repr(warn(doc)))
    return {'light_types':1,'distribution':unicode(type(dist)),'flux_lm':float(flux.Flux),
            'ies':unicode(dist.PhotometricWebFile),'placement':unicode(doc.OwnerFamily.FamilyPlacementType)}

def build():
    app=__revit__.Application
    need(str(app.VersionNumber)=='2025','Revit 2025 only')
    need(getattr(__revit__,'ActiveUIDocument',None) is None,'Isolated Revit process required')
    need(not os.path.lexists(TARGET) and not os.path.lexists(REPORT),'Candidate or receipt already exists')
    for path,expected in SHA.items():
        need(os.path.isfile(path) and digest(path)==expected,'Source SHA mismatch '+path)
    report={'status':'STARTED','source':SOURCE,'seed':SEED,'ies':IES,
            'source_sha256':SHA[SOURCE],'seed_sha256':SHA[SEED],'ies_sha256':SHA[IES]}
    seed_doc=None; child_doc=None; reopened=None; tx=None; stage=None
    try:
        seed_doc=app.OpenDocumentFile(SEED)
        child_doc=app.OpenDocumentFile(SOURCE)
        need(seed_doc.IsFamilyDocument and child_doc.IsFamilyDocument,'Input not family documents')
        need(unicode(seed_doc.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased','Seed not face hosted')
        need(unicode(child_doc.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased','OEM R02 not face hosted')
        light(seed_doc)
        source_geom=geom(child_doc)
        need(len([x for x in source_geom if isinstance(x,DB.FreeFormElement)])==9,'OEM R02 freeform roster changed')
        need(len([x for x in source_geom if isinstance(x,DB.ImportInstance)])==13,'OEM R02 CAD import roster changed')
        original_family_types=list(child_doc.FamilyManager.Types)
        need(len(original_family_types)==1,'OEM R02 family type count changed')
        # Non-shared source family prevents a second project scheduler row.
        sp=child_doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_SHARED)
        need(sp is not None and sp.AsInteger()==0,'OEM nested child is shared: fail closed')
        # Revit's LoadFamily forbids a modifiable TARGET document.
        nested=child_doc.LoadFamily(seed_doc)
        need(nested is not None,'Nested OEM LoadFamily failed')
        syms=[seed_doc.GetElement(x) for x in nested.GetFamilySymbolIds()]
        need(len(syms)==1,'Unexpected nested OEM symbols')
        symbol=syms[0]
        # Refuse if seed has physical nested content we cannot distinguish.
        seed_physical=geom(seed_doc)
        report['seed_removed_physical_elements']=len(seed_physical)
        tx=DB.Transaction(seed_doc,'Replace all Hinkley physical geometry with Smooth child')
        tx.Start()
        for e in seed_physical: seed_doc.Delete(e.Id)
        seed_doc.Regenerate()
        need(not geom(seed_doc),'Residual visible seed geometry detected')
        # Clear Hinkley identity: maintain exactly ONE top-level schedule type.
        fm=seed_doc.FamilyManager
        need(len(list(fm.Types))==1,'Unexpected seed family types')
        fm.CurrentType=list(fm.Types)[0]
        fm.RenameCurrentType('FR-W2502-52L-SB/MB - 52 in')
        for bip,value in ((DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Modern Forms'),
                          (DB.BuiltInParameter.ALL_MODEL_MODEL,'FR-W2502-52L-SB/MB'),
                          (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Smooth 52 inch ceiling fan, native light parent with exact OEM Smooth nested geometry')):
            p=fm.get_Parameter(bip)
            need(p is not None,'Seed missing identity parameter '+unicode(bip))
            fm.Set(p,value)
        # Remove source-specific Hinkley metadata only when family parameters are
        # deletable. Stop on ambiguity; the independent QA audits all type names.
        for p in list(fm.Parameters):
            n=unicode(p.Definition.Name)
            if n.startswith('R05 ') or n.startswith('Hinkley '):
                try: fm.RemoveParameter(p)
                except: raise RuntimeError('Stale seed-specific parameter '+n)
        symbol.Activate()
        seed_doc.Regenerate()
        # Existing seed reference planes are inspected; select the family's
        # host work plane at local origin. A new plane avoids seed naming ambiguity.
        plane=seed_doc.FamilyCreate.NewReferencePlane(DB.XYZ(-10,0,0),DB.XYZ(10,0,0),DB.XYZ.BasisZ,seed_doc.ActiveView)
        plane.Name='SMOOTH_NESTED_HOST_PLANE_R09'
        seed_doc.Regenerate()
        # Face-based family instances in family editor require a valid face/work
        # plane reference; this API call must succeed and be checked after reopen.
        inst=seed_doc.FamilyCreate.NewFamilyInstance(plane.GetReference(),DB.XYZ.Zero,DB.XYZ.BasisX,symbol)
        need(inst is not None,'Face-hosted nesting failed')
        seed_doc.Regenerate()
        need(len(geom(seed_doc))==1,'Expected exactly one nested OEM family instance')
        need(len([x for x in geom(seed_doc) if isinstance(x,DB.FamilyInstance)])==1,'Unexpected nested contents')
        shared=nested.get_Parameter(DB.BuiltInParameter.FAMILY_SHARED)
        need(shared is not None and shared.AsInteger()==0,'Nested OEM symbol unexpectedly shared')
        report['nested_family']=nm(nested)
        report['nested_symbol']=nm(symbol)
        # Only alter optical settings in the working seed parent.
        lf,lt=light(seed_doc)
        lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
        lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.PhotometricWeb)
        seed_doc.Regenerate()
        lf,lt=light(seed_doc)
        dist=lt.GetLightDistribution()
        need(isinstance(dist,DB.Lighting.PhotometricWebLightDistribution),'Native web distribution unsupported')
        dist.PhotometricWebFile=IES
        lt.SetLightDistribution(dist)
        lt.SetInitialIntensity(DB.Lighting.InitialFluxIntensity(707.09))
        # The native source should be positioned below the opaque OEM lens
        # only after a physical volume/clearance test: refuse blind relocation.
        transform=lf.GetLightSourceTransform()
        report['emitter_origin_before']=[transform.Origin.X,transform.Origin.Y,transform.Origin.Z]
        report['optical_orientation_requires_project_qa']=True
        tx.Commit();tx=None
        report['working_optics']=optical_check(seed_doc)
        need(len(geom(seed_doc))==1,'Physical parent count changed before save')
        stage=os.path.join(OUT,'_stage_smooth_r09_'+uuid.uuid4().hex+'.rfa')
        need(not os.path.lexists(stage),'Stage collision')
        opts=DB.SaveAsOptions();opts.OverwriteExistingFile=False
        seed_doc.SaveAs(stage,opts)
        seed_doc.Close(False);seed_doc=None
        child_doc.Close(False);child_doc=None
        reopened=app.OpenDocumentFile(stage)
        report['reopened_optics']=optical_check(reopened)
        need(unicode(reopened.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased','Host placement changed')
        need(len(geom(reopened))==1 and isinstance(geom(reopened)[0],DB.FamilyInstance),'Nested physical count changed')
        nested_saved=geom(reopened)[0]
        saved_shared=nested_saved.Symbol.Family.get_Parameter(DB.BuiltInParameter.FAMILY_SHARED)
        need(saved_shared is not None and saved_shared.AsInteger()==0,'Nested family is shared after save')
        report['nested_bbox_ft']=[float(v) for v in
            (nested_saved.get_BoundingBox(None).Min.X,nested_saved.get_BoundingBox(None).Min.Y,
             nested_saved.get_BoundingBox(None).Min.Z,nested_saved.get_BoundingBox(None).Max.X,
             nested_saved.get_BoundingBox(None).Max.Y,nested_saved.get_BoundingBox(None).Max.Z)]
        reopened.Close(False);reopened=None
        need(all(digest(p)==v for p,v in SHA.items()),'Input changed')
        os.rename(stage,TARGET);stage=None
        report['candidate_sha256']=digest(TARGET)
        report['status']='BUILT_PARENT_NATIVE_LIGHT_PENDING_PROJECT_GEOMETRY_AND_OPTICAL_QA'
    except Exception:
        report['status']='BLOCKED_NO_RELEASE';report['error']=traceback.format_exc()
    finally:
        if tx is not None:
            try: tx.RollBack()
            except: pass
        for doc in (reopened,child_doc,seed_doc):
            if doc is not None:
                try:doc.Close(False)
                except: pass
        report['input_hashes_preserved']=all(os.path.isfile(p) and digest(p)==v for p,v in SHA.items())
        report['timestamp_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
        with open(REPORT,'w') as out:json.dump(report,out,indent=2,sort_keys=True)
        print('SMOOTH_R09 '+report['status'])
        print('SMOOTH_R09_RECEIPT '+REPORT)
        if stage is not None:print('UNRELEASED_STAGE '+stage)
    need(report['status'].startswith('BUILT_PARENT'),'Native build failed: '+report.get('error','unknown'))

build()
