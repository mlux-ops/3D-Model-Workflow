# -*- coding: utf-8 -*-
"""Read-only native QA of a produced RFA. Revit 2025 runner globals required.

No changes to the RFA or any user's project; disposable in-memory documents only.
Runner must set SOURCE_RFA to the RFA being inspected, or TARGET_RFA if doing
post-build QA. QA results are returned in `result`, never used to approve a file
whose visual/source-review gate is still pending.
"""
import os
import math
import hashlib

path=SOURCE_RFA or TARGET_RFA
if not path or not os.path.isfile(path):raise RuntimeError('QA family path missing: '+str(path))
if str(APP.VersionNumber)!='2025':raise RuntimeError('Revit 2025 required')
doc=None
project=None
tx=None
progress('native_qa_preflight',{'rfa':path})
try:
    doc=APP.OpenDocumentFile(path)
    model=doc.FamilyManager.CurrentType.Name.split(' - ')[0]
    if model=='53860BK':
        expected=(25.,5.5,3.)
        wanted_host='wall'
    elif model=='858-59':
        expected=(11.,11.,43.)
        wanted_host='ceiling'
    else:raise RuntimeError('Unrecognized native QA family type: '+model)
    checks={}
    checks['family_document']=doc.IsFamilyDocument
    checks['lighting_fixtures_category']=doc.OwnerFamily.FamilyCategory.Name=='Lighting Fixtures'
    checks['face_workplane_placement']='WorkPlaneBased' in str(doc.OwnerFamily.FamilyPlacementType)
    checks['no_imports']=DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).GetElementCount()==0
    checks['no_directshapes']=DB.FilteredElementCollector(doc).OfClass(DB.DirectShape).GetElementCount()==0
    checks['no_warnings']=len(doc.GetWarnings())==0
    elems=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    opts=DB.Options();opts.DetailLevel=DB.ViewDetailLevel.Fine
    vertices=[]
    for e in elems:
        for g in e.get_Geometry(opts):
            if isinstance(g,DB.Solid) and g.Volume>1e-12:
                for face in g.Faces:vertices.extend(face.Triangulate(1.0).Vertices)
                for edge in g.Edges:
                    cv=edge.AsCurve(); count=96 if not isinstance(cv,DB.Line) else 1
                    vertices.extend(cv.Evaluate(float(i)/count,True) for i in range(count+1))
    if not vertices:raise RuntimeError('No native FreeFormElement geometry in saved family')
    actual=[(max(getattr(v,c) for v in vertices)-min(getattr(v,c) for v in vertices))*12 for c in 'XYZ']
    # Quorum Z is full selected default drop, while published body is 19 inches.
    deviation_mm=[abs(a-b)*25.4 for a,b in zip(actual,expected)]
    checks['published_or_installed_envelope_mm_1']=max(deviation_mm)<=1.0
    project=APP.NewProjectDocument(DB.UnitSystem.Imperial)
    family=doc.LoadFamily(project)
    symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Temporary host and editable finish QA');tx.Start()
    level=DB.Level.Create(project,10.0 if wanted_host=='ceiling' else 0.0)
    if wanted_host=='wall':
        wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
        host=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,10,0,False,False)
        project.Regenerate()
        reference=DB.HostObjectUtils.GetSideFaces(host,DB.ShellLayerType.Exterior)[0]
        face=host.GetGeometryObjectFromReference(reference)
        point=face.Project(DB.XYZ(0,0,5)).XYZPoint
    else:
        perimeter=DB.CurveLoop()
        for a,b in [(DB.XYZ(-8,-8,10),DB.XYZ(8,-8,10)),(DB.XYZ(8,-8,10),DB.XYZ(8,8,10)),(DB.XYZ(8,8,10),DB.XYZ(-8,8,10)),(DB.XYZ(-8,8,10),DB.XYZ(-8,-8,10))]:perimeter.Append(DB.Line.CreateBound(a,b))
        floor_type=DB.Floor.GetDefaultFloorType(project,False)
        host=DB.Floor.Create(project,__import__('System').Collections.Generic.List[DB.CurveLoop]([perimeter]),floor_type,level.Id)
        project.Regenerate()
        reference=DB.HostObjectUtils.GetBottomFaces(host)[0]
        face=host.GetGeometryObjectFromReference(reference)
        point=face.Project(DB.XYZ(0,0,10)).XYZPoint
    symbol.Activate();project.Regenerate()
    inst=project.Create.NewFamilyInstance(reference,point,DB.XYZ.BasisX,symbol)
    project.Regenerate()
    checks['actual_face_host']=inst.Host is not None and inst.Host.Id==host.Id and inst.HostFace is not None
    material_names=[p.Definition.Name for p in doc.FamilyManager.Parameters if p.Definition.Name.endswith(' Material')]
    checks['editable_material_parameters']=len(material_names)>=2 and all(symbol.LookupParameter(name) is not None and not symbol.LookupParameter(name).IsReadOnly for name in material_names)
    checks['no_project_warnings']=len(project.GetWarnings())==0
    tx.RollBack();tx=None
    receipt={'rfa_path':path,'model':model,'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest(),
             'expected_dimensions_in':expected,'measured_dimensions_in':actual,
             'dimension_deviation_mm':deviation_mm,'freeform_element_count':len(elems),
             'tested_host':wanted_host,'checks':checks,'native_qa_pass':all(checks.values()),
             'visual_source_review':'PENDING','photometric_verification':'UNVERIFIED',
             'electrical_connector':'NOT PROVIDED'}
    result.update(receipt)
    progress('native_qa_complete',{'passed':receipt['native_qa_pass'],'checks':checks})
    if not receipt['native_qa_pass']:raise RuntimeError('Native QA checks failed: '+str([k for k,v in checks.items() if not v]))
finally:
    if tx is not None:
        try:tx.RollBack()
        except Exception:pass
    if project is not None:project.Close(False)
    if doc is not None:doc.Close(False)
