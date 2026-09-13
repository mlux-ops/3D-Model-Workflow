import os,json,traceback,clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List
OUT=r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow\output\window_96x100'
RFA=os.path.join(OUT,'Window_Fixed_Over_Two_Awnings_96x100_R2025.rfa')
report={}; docs=[]; tx=None
def pt(x,y,z): return DB.XYZ(x/12.,y/12.,z/12.)
def save():
    with open(os.path.join(OUT,'validation.json'),'w') as f: json.dump(report,f,indent=2)
def box(name,x0,x1,y0,y1,z0,z1,mat,cat):
    z0+=sill_offset; z1+=sill_offset
    loop=DB.CurveLoop()
    points=[pt(x0,y0,z0),pt(x1,y0,z0),pt(x1,y1,z0),pt(x0,y1,z0)]
    for i in range(4): loop.Append(DB.Line.CreateBound(points[i],points[(i+1)%4]))
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),DB.XYZ.BasisZ,(z1-z0)/12.)
    e=DB.FreeFormElement.Create(doc,solid); e.Subcategory=cat
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),mat)
    return e
def ring(name,x0,x1,z0,z1,w,y0,y1,mat,cat):
    box(name,x0,x0+w,y0,y1,z0,z1,mat,cat); box(name,x1-w,x1,y0,y1,z0,z1,mat,cat)
    box(name,x0+w,x1-w,y0,y1,z0,z0+w,mat,cat); box(name,x0+w,x1-w,y0,y1,z1-w,z1,mat,cat)
try:
    app=__revit__.Application
    doc=app.NewFamilyDocument(r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Window.rft'); docs.append(doc)
    tx=DB.Transaction(doc,'Build combined window'); tx.Start()
    fm=doc.FamilyManager; fm.NewType('96 x 100 - Fixed over paired awnings')
    for bip,value in [(DB.BuiltInParameter.WINDOW_WIDTH,96),(DB.BuiltInParameter.WINDOW_HEIGHT,100)]:
        p=fm.get_Parameter(bip); fm.SetFormula(p,str(value)+'"')
    for name,value in [('Rough Opening Width',96),('Rough Opening Height',100),('Transom Center Above RO Sill',36)]:
        p=fm.get_Parameter(name)
        if p is None: p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
        fm.SetFormula(p,str(value)+'"')
    doc.Regenerate()
    opening=next(iter(DB.FilteredElementCollector(doc).OfClass(DB.Opening)))
    sill_offset=opening.get_BoundingBox(None).Min.Z*12
    mats={}
    for name,color,tr in [('Frame Finish',(75,78,80),0),('Glass',(165,204,215),70),('Gasket',(28,28,28),0)]:
        m=doc.GetElement(DB.Material.Create(doc,"Combined Window - "+name)); m.Color=DB.Color(*color); m.Transparency=tr
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False); fm.Set(p,m.Id); mats[name]=p
    cats={n:doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,n) for n in ['Frame','Awning Sash','Fixed Glazing','Awning Glazing','Seals','Hardware']}
    metal=mats['Frame Finish']; glass=mats['Glass']; gasket=mats['Gasket']
    # Nominal RO 96 x 100; 1/4 inch installation clearance on all sides.
    ring('Perimeter frame',-47.75,47.75,.25,99.75,2,-2.25,2.25,metal,cats['Frame'])
    box('Horizontal transom',-45.75,45.75,-2.25,2.25,35,37,metal,cats['Frame'])
    box('Lower center mullion',-1,1,-2.25,2.25,2.25,35,metal,cats['Frame'])
    ring('Fixed glazing stop',-45.75,45.75,37,97.75,.625,-.65,.65,metal,cats['Frame'])
    box('Upper fixed pane',-45.125,45.125,-.5,.5,37.625,97.125,glass,cats['Fixed Glazing'])
    for x0,x1 in [(-45.75,-1),(1,45.75)]:
        ring('Awning seal',x0,x1,2.25,35,.25,-1.5,1.5,gasket,cats['Seals'])
        ring('Awning sash',x0+.125,x1-.125,2.375,34.875,1.75,-1.625,1.625,metal,cats['Awning Sash'])
        ring('Awning glazing bead',x0+1.875,x1-1.875,4.125,33.125,.375,-.65,.65,metal,cats['Awning Sash'])
        box('Awning pane',x0+2.25,x1-2.25,-.5,.5,4.5,32.75,glass,cats['Awning Glazing'])
        mid=(x0+x1)/2
        box('Interior latch',mid-2,mid+2,1.625,2.125,2.8,3.3,metal,cats['Hardware'])
        for hx in [x0+7,x1-7]: box('Top hinge',hx-1.5,hx+1.5,-1.9,-1.625,34,34.75,metal,cats['Hardware'])
    doc.Regenerate()
    report['opening_bounds']=[str(e.get_BoundingBox(None).Min) for e in DB.FilteredElementCollector(doc).OfClass(DB.Opening)]
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    views=[]
    for name,eye in [('Front',pt(0,-200,50+sill_offset)),('Oblique',pt(150,-220,140+sill_offset))]:
        v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name
        fw=pt(0,0,50+sill_offset).Subtract(eye).Normalize(); right=fw.CrossProduct(DB.XYZ.BasisZ).Normalize()
        v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(fw),fw)); v.DisplayStyle=DB.DisplayStyle.Shading; v.DetailLevel=DB.ViewDetailLevel.Fine
        hide=[e.Id for e in DB.FilteredElementCollector(doc).OfClass(DB.Wall) if e.CanBeHidden(v)]
        hide.extend(e.Id for e in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm) if not isinstance(e,DB.FreeFormElement) and e.CanBeHidden(v))
        if hide: v.HideElements(List[DB.ElementId](hide))
        views.append(v)
    tx.Commit(); tx=None
    opt=DB.SaveAsOptions(); opt.OverwriteExistingFile=True; opt.PreviewViewId=views[1].Id; doc.SaveAs(RFA,opt)
    im=DB.ImageExportOptions(); im.ExportRange=DB.ExportRange.SetOfViews; im.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); im.FilePath=os.path.join(OUT,'Window'); im.HLRandWFViewsFileType=DB.ImageFileType.PNG; im.ShadowViewsFileType=DB.ImageFileType.PNG; im.ZoomType=DB.ZoomFitType.FitToPage; im.PixelSize=1400
    doc.ExportImage(im)
    doc.Close(False); docs.remove(doc); doc=app.OpenDocumentFile(RFA); docs.append(doc)
    report['reopened']=doc.IsFamilyDocument; report['category']=doc.OwnerFamily.FamilyCategory.Name; report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Verify window placement'); tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    wall=DB.Wall.Create(project,DB.Line.CreateBound(pt(-100,0,0),pt(100,0,0)),level.Id,False)
    wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(12)
    symbol.Activate(); project.Regenerate()
    before=wall.get_Parameter(DB.BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble()
    inst=project.Create.NewFamilyInstance(pt(0,0,12),symbol,wall,level,DB.Structure.StructuralType.NonStructural); project.Regenerate()
    after=wall.get_Parameter(DB.BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble()
    report['hosted']=inst.Host.Id==wall.Id; report['removed_wall_volume_ft3']=before-after
    report['expected_removed_volume_ft3']=8*(100/12.)*wall.Width
    report['width_inches']=symbol.get_Parameter(DB.BuiltInParameter.WINDOW_WIDTH).AsDouble()*12
    report['height_inches']=symbol.get_Parameter(DB.BuiltInParameter.WINDOW_HEIGHT).AsDouble()*12
    report['family_frame_z_bounds_inches']=[sill_offset+.25,sill_offset+99.75]
    report['family_opening_z_bounds_inches']=[sill_offset,sill_offset+100]
    report['material_tests']={}
    for name in mats:
        p=symbol.LookupParameter(name); original=p.AsElementId(); alt=DB.Material.Create(project,'QA '+name); p.Set(alt); project.Regenerate()
        report['material_tests'][name]=alt in list(inst.GetMaterialIds(False))
        p.Set(original)
    tx.Commit(); tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]; report['status']='complete'; save()
except Exception:
    report['error']=traceback.format_exc(); save()
finally:
    if tx:
        try: tx.RollBack()
        except: pass
    for d in reversed(docs):
        try: d.Close(False)
        except: pass

