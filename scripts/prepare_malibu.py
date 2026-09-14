from pathlib import Path
root=Path(__file__).resolve().parents[1]
base=(root/'scripts/build_bev_faucet.py').read_text(encoding='utf-8')
helpers=base[:base.index('\ntry:\n    app=')]
helpers=helpers.replace("'bev_faucet'","'malibu'").replace('Hansgrohe_Modern_Beverage_Faucet_04117340_Brushed_Black_Chrome_R2025.rfa','Icera_Malibu_II_RF_C-6360.01_R2025.rfa').replace('Beverage Faucet','Icera Malibu II RF')
helpers=helpers.replace("xyz(1.65,0,4.5)","xyz(0,12,14)").replace("xyz(-1,-1,.001)","xyz(-10,-1,.001)").replace("xyz(4.5,2.2,9.6)","xyz(10,26,30)")
helpers=helpers.replace("[('Metal Finish',(79,73,68),.65,.65),('Seam Finish',(18,18,18),.22,.03)]", "[('Ceramic Finish',(245,245,242),.88,.12),('Seat Finish',(245,245,242),.72,.08),('Lever Finish',(190,190,190),.95,.85)]")
body=r'''
def dloop(z,w,rear,front):
    a=w/2.; r=.65; shoulder=front-a
    pts=[(-a+r,rear),(a-r,rear),('arc',(a-r*.293,rear+r*.293),(a,rear+r)),(a,shoulder),('arc',(0,front),(-a,shoulder)),(-a,rear+r),('arc',(-a+r*.293,rear+r*.293),(-a+r,rear))]
    return profile_loop(xyz(0,0,z),DB.XYZ.BasisX,DB.XYZ.BasisY,pts)

def loft(doc,name,sections,param,cat,tank=False):
    loops=[]
    for z,w,rear,front in sections:
        loops.append(profile_loop(xyz(0,0,z),DB.XYZ.BasisX,DB.XYZ.BasisY,rounded_rect(-w/2.,rear,w/2.,front,1.1)) if tank else dloop(z,w,rear,front))
    s=DB.GeometryCreationUtilities.CreateLoftGeometry(List[DB.CurveLoop](loops),DB.SolidOptions(DB.ElementId.InvalidElementId,DB.ElementId.InvalidElementId))
    e=DB.FreeFormElement.Create(doc,s); e.Subcategory=cat
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    report.setdefault('parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

try:
    app=__revit__.Application; report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create family')
    doc=app.NewFamilyDocument(TEMPLATE); docs.append(doc)
    tx=DB.Transaction(doc,'Build Malibu II RF'); tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_PlumbingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('C-6360.01 - White - Chrome LH - Closed Seat')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False); fm.Set(p,mat.Id); params[name]=p
    for name,value in [('Overall Height',28.875),('Overall Width',15.875),('Overall Depth',24.625),('Bowl Rim Height',16.5),('Rough In',12),('Rear Wall Gap',.5)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Icera'),(DB.BuiltInParameter.ALL_MODEL_MODEL,'MALIBU II RF C-6360.01'),(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Independent visualization reconstruction; closed seat; white ceramic; chrome LH lever; no MEP connectors')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    cats={}
    for name in ['Ceramic','Seat','Lever','Bolt Covers']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    c=params['Ceramic Finish']; s=params['Seat Finish']; m=params['Lever Finish']
    loft(doc,'Skirted pedestal',[(0,10.875,3,22.25),(.15,10.875,3,22.25),(6,10.1,2.8,21.7),(9.5,9.8,1.5,21.4),(14.5,13.5,0,22.5)],c,cats['Ceramic'])
    loft(doc,'Rounded bowl exterior',[(8.7,9.4,11,20.8),(10,11.8,9.6,22.6),(13,14.5,7.8,24.2),(16.5,15.5,6.4,24.625)],c,cats['Ceramic'])
    loft(doc,'Integrated tank',[(14.5,15.5,.03,6.75),(27.65,15.7,.03,6.7)],c,cats['Ceramic'],True)
    loft(doc,'Tank lid',[(27.69,15.65,.08,6.67),(28.2825,15.875,0,6.75),(28.875,15.65,.08,6.67)],c,cats['Ceramic'],True)
    loft(doc,'Closed seat ring exterior',[(16.6,15.25,6.75,24.55),(16.92,15.45,6.75,24.625),(17.05,15.4,6.75,24.6)],s,cats['Seat'])
    loft(doc,'Closed seat lid',[(17.1,15.2,6.85,24.48),(17.475,15.5,6.75,24.625),(17.85,15.2,6.85,24.48)],s,cats['Seat'])
    form(doc,'Left hand tank lever',xyz(7.75,0,0),DB.XYZ.BasisY,DB.XYZ.BasisZ,DB.XYZ.BasisX,rounded_rect(1.65,25.15,3.4,25.9,.12),.6,m,cats['Lever'])
    for side in [-1,1]:
        form(doc,'Floor bolt cover',xyz(side*5.15,0,0),DB.XYZ.BasisY,DB.XYZ.BasisZ,DB.XYZ.BasisX.Multiply(side),rounded_rect(10.4,2.1,12.6,4.8,.15),.15,c,cats['Bolt Covers'])
    doc.Regenerate()
    views=[preview(doc,'Front',xyz(0,75,14)),preview(doc,'Oblique',xyz(48,70,46)),preview(doc,'Side',xyz(70,12,14)),preview(doc,'Top',xyz(0,12,90)),preview(doc,'Material Review',xyz(48,70,46),True)]
    tx.Commit(); tx=None
    o=DB.SaveAsOptions(); o.OverwriteExistingFile=True; o.MaximumBackups=1; o.PreviewViewId=views[1].Id
    doc.SaveAs(RFA,o); checkpoint('saved; export views'); export(doc,views)
    docs.remove(doc); doc.Close(False)
    doc=app.OpenDocumentFile(RFA); docs.append(doc)
    report['reopened']=doc.IsFamilyDocument; report['category']=doc.OwnerFamily.FamilyCategory.Name
    report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    report['bounds_inches']=bounds(forms)
    vertices=[v for e in forms for solid in solids(e.get_Geometry(DB.Options())) for face in solid.Faces for v in face.Triangulate().Vertices]
    report['tessellated_surface_bounds_inches']=[min(v.X for v in vertices)*12,min(v.Y for v in vertices)*12,min(v.Z for v in vertices)*12,max(v.X for v in vertices)*12,max(v.Y for v in vertices)*12,max(v.Z for v in vertices)*12]
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    checkpoint('test floor placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test floor placement and materials'); tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    ft=next(iter(DB.FilteredElementCollector(project).OfClass(DB.FloorType)))
    loop=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-36,-36),(36,-36),(36,48),(-36,48)])
    host=DB.Floor.Create(project,List[DB.CurveLoop]([loop]),ft.Id,level.Id)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetTopFaces(host)[0]; face=host.GetGeometryObjectFromReference(ref); point=face.Project(DB.XYZ.Zero).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol); project.Regenerate()
    report['loaded_and_face_placed']=inst.Host is not None and inst.Host.Id==host.Id
    report['mounting_normal_dot_host_normal']=inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)
    report['material_tests']={}
    for name in params:
        p=symbol.LookupParameter(name); original=p.AsElementId(); alternate=DB.Material.Create(project,'QA '+name); p.Set(alternate); project.Regenerate()
        report['material_tests'][name]=alternate in list(inst.GetMaterialIds(False))
        p.Set(original); project.Regenerate()
    tx.Commit(); tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    checkpoint('complete')
except Exception:
    report['error']=traceback.format_exc(); checkpoint('failed at '+report.get('stage','start'))
finally:
    if tx is not None:
        try: tx.RollBack()
        except Exception: pass
    for d in reversed(docs):
        try: d.Close(False)
        except Exception: pass
'''
(root/'scripts/build_malibu.py').write_text(helpers+body,encoding='utf-8')
