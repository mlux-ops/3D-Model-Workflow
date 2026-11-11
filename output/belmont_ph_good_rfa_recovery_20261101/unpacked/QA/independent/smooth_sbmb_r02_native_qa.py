# -*- coding: utf-8 -*-
"""Independent, non-overwriting Smooth R02 finish and 52-in radial sweep QA.

Run only by prime under an isolated Revit 2025 process. No RFA or RVT saved.
"""
from __future__ import print_function
import os, json, hashlib, math, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
RFA=os.path.join(BASE,'candidates','ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa')
BUILD=os.path.join(BASE,'qa','smooth_sbmb_r02_build.json')
OUTPUT=os.path.join(BASE,'qa','smooth_sbmb_r02_native_qa.json')
SOURCE=os.path.join(BASE,'families','ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa')
OEM=os.path.join(BASE,'sources','oem','extracted','MFR1415595_FR-W2502_Smooth_Revit','FR-W2502-52L.rfa')
PROBE=os.path.join(BASE,'qa','inspect_oem_material_parts.json')
SHA={'source':'45c76b46fba9daebcf5d0ebbedb7b5592d4eaa50cbbd4b5b59fe44321b7b8e18',
     'oem':'5275e71a2d6cfd033b4cb6d6fa1351d0e78c953586bdbcafe2b905893286d617',
     'probe':'2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3'}
BLADES=(2997,2998,2999)
HOUSING=(3038,3039,3040,3041,3042)
IMPORTS=(2977,2980,2982,2985,2986,2987,2988,2989,2990,2991,2992,2993,2994)
EXPECTED_FACES={2997:140,2998:140,2999:140,3038:52,3039:20,3040:22,3041:29,3042:103,3000:97}
BLACK='PH GOOD Smooth MB ABS Blades R02 Provisional'
BRASS='PH GOOD Smooth SB Housing R02 Provisional'

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            b=f.read(1048576)
            if not b:break
            h.update(b)
    return h.hexdigest()

def ide(v):
    try:return int(v.Value)
    except Exception:return int(v.IntegerValue)

def name(e):
    try:return unicode(DB.Element.Name.GetValue(e))
    except Exception:return unicode(e.Name)

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def material_faces(element):
    counts={}
    options=DB.Options();options.DetailLevel=DB.ViewDetailLevel.Fine
    options.IncludeNonVisibleObjects=False
    def walk(g):
        for item in g:
            if isinstance(item,DB.GeometryInstance):walk(item.GetInstanceGeometry())
            elif isinstance(item,DB.Solid) and item.Volume>1e-12:
                for face in item.Faces:
                    key=str(ide(face.MaterialElementId))
                    counts[key]=counts.get(key,0)+1
    walk(element.get_Geometry(options))
    return counts

def family_finish(family_doc):
    mats={name(m):m for m in DB.FilteredElementCollector(family_doc).OfClass(DB.Material)}
    require(BLACK in mats and BRASS in mats,'Candidate finish materials missing')
    expected={BLACK:mats[BLACK],BRASS:mats[BRASS]}
    for mat_name,mat in expected.items():
        require(mat.Transparency==0 and
                isinstance(family_doc.GetElement(mat.AppearanceAssetId),DB.AppearanceAssetElement),
                'Candidate material lacks native opaque appearance: '+mat_name)
    faces={}
    for idnum in BLADES+HOUSING+(3000,):
        element=family_doc.GetElement(DB.ElementId(idnum))
        require(isinstance(element,DB.FreeFormElement),'Unexpected element '+str(idnum))
        observed=material_faces(element)
        selected=('-1' if idnum==3000 else
                  str(ide(mats[BLACK].Id if idnum in BLADES else mats[BRASS].Id)))
        require(observed=={selected:EXPECTED_FACES[idnum]},
                'Wrong source/finish face mapping %d: %s' %(idnum,observed))
        faces[str(idnum)]=observed
    imported=sorted(ide(e.Id) for e in DB.FilteredElementCollector(family_doc).OfClass(DB.ImportInstance))
    require(imported==list(IMPORTS),'CAD imports changed')
    for idnum in IMPORTS:
        observed=material_faces(family_doc.GetElement(DB.ElementId(idnum)))
        require(list(observed.keys())==['-1'],
                'An imported CAD surface was recolored: '+str(idnum))
    return {'finish_face_mapping':faces,'imports_untouched':list(IMPORTS),
            'matte_black_id':ide(mats[BLACK].Id),'soft_brass_id':ide(mats[BRASS].Id)}

def radial_placed(instance):
    center=instance.GetTransform().Origin
    alignment=abs(instance.GetTransform().BasisZ.DotProduct(DB.XYZ.BasisZ))
    opts=DB.Options();opts.DetailLevel=DB.ViewDetailLevel.Fine
    opts.IncludeNonVisibleObjects=False
    result={'solid_count':0,'samples':0,'max_radius_ft':-1.}
    def sample(p):
        r=math.sqrt((p.X-center.X)**2+(p.Y-center.Y)**2)
        result['max_radius_ft']=max(result['max_radius_ft'],r)
        result['samples']+=1
    def walk(geometry):
        for item in geometry:
            if isinstance(item,DB.GeometryInstance):walk(item.GetInstanceGeometry())
            elif isinstance(item,DB.Solid) and item.Volume>1e-12:
                result['solid_count']+=1
                for face in item.Faces:
                    for v in face.Triangulate().Vertices:sample(v)
                for edge in item.Edges:
                    curve=edge.AsCurve()
                    if curve is None:continue
                    n=2 if isinstance(curve,DB.Line) else 9
                    for i in range(n):sample(curve.Evaluate(float(i)/(n-1),True))
    walk(instance.get_Geometry(opts))
    actual=2.*result['max_radius_ft']*304.8
    result.update({'radial_sweep_mm':actual,'expected_mm':1320.8,
                   'absolute_delta_mm':abs(actual-1320.8),
                   'axial_alignment':alignment,
                   'passed':result['samples']>0 and alignment>=.98 and
                            abs(actual-1320.8)<=1.0})
    return result

def project_test(app,source_doc):
    project=None;tx=None
    try:
        project=app.NewProjectDocument(DB.UnitSystem.Imperial)
        family=source_doc.LoadFamily(project)
        require(isinstance(family,DB.Family),'FamilyDoc.LoadFamily failed')
        symbols=[project.GetElement(i) for i in family.GetFamilySymbolIds()]
        require(len(symbols)==1,'Expected one Smooth family type')
        symbol=symbols[0]
        tx=DB.Transaction(project,'Disposable Smooth R02 radial QA');tx.Start()
        level=DB.Level.Create(project,0.)
        loop=DB.CurveLoop()
        points=[DB.XYZ(-7,-7,0),DB.XYZ(7,-7,0),DB.XYZ(7,7,0),DB.XYZ(-7,7,0)]
        for i in range(4):loop.Append(DB.Line.CreateBound(points[i],points[(i+1)%4]))
        from System.Collections.Generic import List
        floortype=DB.Floor.GetDefaultFloorType(project,False)
        floor=DB.Floor.Create(project,List[DB.CurveLoop]([loop]),floortype,level.Id)
        project.Regenerate()
        ref=list(DB.HostObjectUtils.GetBottomFaces(floor))[0]
        symbol.Activate();project.Regenerate()
        instance=project.Create.NewFamilyInstance(ref,DB.XYZ(0,0,0),DB.XYZ.BasisX,symbol)
        project.Regenerate()
        hosting=(instance.Host is not None and instance.Host.Id.Equals(floor.Id))
        sweep=radial_placed(instance)
        result={'placement_hosted':hosting,'radial':sweep,
                'warnings':[unicode(w.GetDescriptionText()) for w in project.GetWarnings()],
                'project_saved':False}
        require(hosting and sweep['passed'] and not result['warnings'],
                'Placed sweep, host, or warnings failed')
        return result
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        if project is not None:project.Close(False)

def main():
    require(not os.path.lexists(OUTPUT) and not os.path.lexists(OUTPUT+'.tmp'),
            'Receipt exists; choose a new QA revision')
    app=__revit__.Application
    require(str(app.VersionNumber)=='2025' and
            getattr(__revit__,'ActiveUIDocument',None) is None,
            'Requires isolated Revit 2025 without active user document')
    protected=[RFA,SOURCE,OEM,PROBE,BUILD]
    before={p:digest(p) for p in protected}
    require(before[SOURCE]==SHA['source'] and before[OEM]==SHA['oem'] and
            before[PROBE]==SHA['probe'],'Source/probe checksum mismatch')
    with open(BUILD,'rb') as f:build=json.load(f)
    require(build['target_sha256']==before[RFA] and
            build['status']=='PARTIAL_FINISH_SAVED_NATIVE_FACE_BINDINGS_VERIFIED_VISUAL_HOLD',
            'Candidate builder receipt is mismatched or not accepted')
    report={'status':'ERROR','candidate':RFA,'input_shas':before,
            'finish_release_status':'PARTIAL_FINISH_ONLY_CAD_IMPORTS_UNVERIFIED',
            'visual_review':'PENDING'}
    doc=None
    try:
        doc=app.OpenDocumentFile(RFA)
        require(doc.IsFamilyDocument,'Expected saved native RFA')
        require(name(doc.OwnerFamily.FamilyCategory)=='Lighting Fixtures',
                'Family category changed')
        require(str(doc.OwnerFamily.FamilyPlacementType)=='WorkPlaneBased',
                'Hosting changed')
        report['material']=family_finish(doc)
        report['family_warnings']=[unicode(w.GetDescriptionText()) for w in doc.GetWarnings()]
        require(not report['family_warnings'],'Family warnings')
        report['placed']=project_test(app,doc)
        report['status']='NATIVE_MATERIAL_AND_SWEEP_PASS_VISUAL_HOLD'
    except Exception:
        report['error']=traceback.format_exc()
    finally:
        if doc is not None:doc.Close(False)
        report['input_shas_after']={p:digest(p) for p in protected}
        report['originals_unchanged']=report['input_shas']==report['input_shas_after']
        if not report['originals_unchanged']:
            report['status']='FAIL_SOURCE_BYTES_CHANGED'
        encoded=json.dumps(report,ensure_ascii=True,indent=2,sort_keys=True)
        with open(OUTPUT+'.tmp','wb') as f:f.write(encoded.encode('ascii'))
        require(not os.path.lexists(OUTPUT),'QA receipt appeared during run')
        os.rename(OUTPUT+'.tmp',OUTPUT)
    print('SMOOTH_R02_NATIVE_QA '+report['status'])
    if report['status']!='NATIVE_MATERIAL_AND_SWEEP_PASS_VISUAL_HOLD':
        raise RuntimeError('Smooth R02 QA held; read separate JSON receipt')

main()
