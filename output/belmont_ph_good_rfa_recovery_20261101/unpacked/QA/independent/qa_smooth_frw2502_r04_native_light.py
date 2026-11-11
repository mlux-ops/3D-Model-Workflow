# -*- coding: utf-8 -*-
"""Independent read-only Revit 2025 QA for Smooth SB/MB R04 native light."""
from __future__ import print_function
import os, json, hashlib, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
R02=os.path.join(BASE,'candidates',
 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
R04=os.path.join(BASE,'candidates',
 'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R04_NATIVE_LIGHT_IES_UNAPPROVED.rfa')
IES=os.path.join(BASE,'sources','photometry','FR-W2502-52L.IES')
OUT=os.path.join(BASE,'qa','smooth_sbmb_r04_independent_light_qa.json')
R02_SHA='f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db'
IES_SHA='6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e'

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        while True:
            b=stream.read(1048576)
            if not b:return h.hexdigest()
            h.update(b)

def eid(x):
    try:return int(x.Value)
    except:return int(x.IntegerValue)

def snap(doc):
    assert doc.IsFamilyDocument
    assert doc.OwnerFamily.FamilyCategory.Name=='Lighting Fixtures'
    assert str(doc.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased'
    lf=DB.Lighting.LightFamily.GetLightFamily(doc)
    fm=doc.FamilyManager
    types=list(fm.Types)
    assert len(types)==1
    count=int(lf.GetNumberOfLightTypes())
    flag=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE)
    data={'type':str(types[0].Name),'light_type_count':count,
          'light_source_flag':flag.AsInteger() if flag else None,
          'source_ids':[eid(e.Id) for e in
             DB.FilteredElementCollector(doc).OfCategory(
               DB.BuiltInCategory.OST_LightingFixtureSource)],
          'warnings':[str(w.GetDescriptionText()) for w in doc.GetWarnings()]}
    if count==1:
        lt=lf.GetLightType(0)
        dist=lt.GetLightDistribution()
        inten=lt.GetInitialIntensity()
        color=lt.GetInitialColor()
        web=fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
        t=lf.GetLightSourceTransform()
        data.update({'distribution':str(dist.GetType().Name),
                     'style':str(lf.GetLightDistributionStyle()),
                     'shape':str(lf.GetLightShapeStyle()),
                     'ies_distribution':str(dist.PhotometricWebFile) if isinstance(
                         dist,DB.Lighting.PhotometricWebLightDistribution) else None,
                     'ies_type':str(fm.CurrentType.AsString(web)) if web else None,
                     'flux':float(inten.Flux) if isinstance(inten,
                           DB.Lighting.InitialFluxIntensity) else None,
                     'kelvin':float(color.Temperature) if isinstance(color,
                           DB.Lighting.CustomInitialColor) else None,
                     'emitter_mm':[float(t.Origin.X)*304.8,
                                   float(t.Origin.Y)*304.8,
                                   float(t.Origin.Z)*304.8],
                     'basis_z':[float(t.BasisZ.X),
                                float(t.BasisZ.Y),float(t.BasisZ.Z)]})
    forms={}
    for e in DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement):
        if eid(e.Id) not in (2997,2998,2999,3000,3038,3039,3040,3041,3042):continue
        b=e.get_BoundingBox(None)
        forms[str(eid(e.Id))]={'bbox':[round(float(v),8) for v in
                       (b.Min.X,b.Min.Y,b.Min.Z,b.Max.X,b.Max.Y,b.Max.Z)],
                       'materials':sorted(eid(v) for v in e.GetMaterialIds(False))}
    data['forms']=forms
    data['imports']=sorted(eid(e.Id) for e in
                         DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance))
    data['material_records']={}
    for m in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if m.Name in ('PH GOOD Smooth MB ABS Blades R02 Provisional',
                      'PH GOOD Smooth SB Housing R02 Provisional'):
            data['material_records'][str(m.Name)]={
              'id':eid(m.Id),'appearance':eid(m.AppearanceAssetId),
              'rgb':[int(m.Color.Red),int(m.Color.Green),int(m.Color.Blue)],
              'transparency':int(m.Transparency)}
    return data

def main():
    assert str(__revit__.Application.VersionNumber)=='2025'
    assert os.path.isfile(R02) and sha(R02)==R02_SHA
    assert os.path.isfile(IES) and sha(IES)==IES_SHA
    assert os.path.isfile(R04),'R04 candidate has not been built'
    assert not os.path.lexists(OUT),'Independent receipt exists; no overwrite'
    states=[]
    for path in (R02,R04):
        doc=__revit__.Application.OpenDocumentFile(path)
        try:
            record=snap(doc)
            record['path']=path
            record['sha256']=sha(path)
            states.append(record)
        finally:doc.Close(False)
    a,b=states
    checks={
      'real_native_light':b['light_type_count']==1 and b['light_source_flag']==1
                         and len(b['source_ids'])==1,
      'exact_distribution':b.get('distribution')=='PhotometricWebLightDistribution'
                           and os.path.basename((b.get('ies_distribution') or '').replace('\\','/')).lower()=='fr-w2502-52l.ies'
                           and os.path.basename((b.get('ies_type') or '').replace('\\','/')).lower()=='fr-w2502-52l.ies',
      'photometric_flux_and_CCT':b.get('flux') is not None and
                  abs(b['flux']-707.09)<.02 and abs(b['kelvin']-3000)<.05,
      'physical_geometry':a['forms']==b['forms'] and a['imports']==b['imports'],
      'SBMB_materials':a['material_records']==b['material_records'],
      'warnings':not b['warnings'],
      'position':b.get('emitter_mm') is not None and
                 365.8 < b['emitter_mm'][2] < 373.0 and
                 abs(b['emitter_mm'][0])<10.0 and abs(b['emitter_mm'][1])<10.0,
      'orientation':b.get('basis_z') is not None and b['basis_z'][2]>.9,
      'source_preserved':sha(R02)==R02_SHA and sha(IES)==IES_SHA}
    passed=all(checks.values())
    report={'status':'PASS_TECHNICAL_NATIVE_LIGHT_VISUAL_HOLD' if passed else 'FAIL',
            'checks':checks,'R02':a,'R04':b,
            'release_limitations':['visual IES orientation pending',
                 'companion IES required','unverified MEP connector',
                 'finish/CCT-specific IES not established',
                 'imported CAD finish still partial']}
    fd=os.open(OUT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o666)
    with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2,sort_keys=True)
    print(report['status'])
    if not passed:raise RuntimeError('R04 QA failed')

if __name__=='__main__':
    try:main()
    except Exception:
        print(traceback.format_exc())
        raise
