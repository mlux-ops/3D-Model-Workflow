# -*- coding: utf-8 -*-
"""Build House of Troy USLEDZ15-76 as a Revit 2025 face-based lighting family."""
import os
import json
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
OUT = os.path.join(ROOT, 'output', 'house_of_troy_usledz15_76')
RFA = os.path.join(OUT, 'House_of_Troy_USLEDZ15-76_Weathered_Brass_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
report = {'rfa_path': RFA, 'source_sku': 'USLEDZ15-76'}
docs = []
tx = None

def checkpoint(stage):
    report['stage'] = stage
    with open(os.path.join(OUT, 'validation.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)

def xyz(x,y,z):
    return DB.XYZ(x/12.0,y/12.0,z/12.0)

def all_solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in all_solids(item.GetInstanceGeometry()):
                yield solid

def bounds(elements):
    boxes=[e.get_BoundingBox(None) for e in elements]
    return [round(v*12,4) for v in [min(b.Min.X for b in boxes),min(b.Min.Y for b in boxes),
            min(b.Min.Z for b in boxes),max(b.Max.X for b in boxes),
            max(b.Max.Y for b in boxes),max(b.Max.Z for b in boxes)]]

def profile_loop(origin,u,v,points):
    def at(pair):
        return origin.Add(u.Multiply(pair[0]/12.0)).Add(v.Multiply(pair[1]/12.0))
    loop=DB.CurveLoop()
    for i in range(len(points)):
        loop.Append(DB.Line.CreateBound(at(points[i]),at(points[(i+1)%len(points)])))
    return loop

def bind(doc,solid,name,param,category):
    element=DB.FreeFormElement.Create(doc,solid)
    element.Subcategory=category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    report.setdefault('parts',[]).append({'name':name,'id':str(element.Id.Value)})
    return element

def box(doc,name,x0,y0,z0,x1,y1,z1,param,category):
    loop=profile_loop(xyz(0,0,z0),DB.XYZ.BasisX,DB.XYZ.BasisY,
            [(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),DB.XYZ.BasisZ,(z1-z0)/12.)
    return bind(doc,solid,name,param,category)

def revolved(doc,name,origin,axis,points,param,category):
    radial=DB.XYZ.BasisZ if abs(axis.X)>.99 else DB.XYZ.BasisX
    radial=radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop=profile_loop(origin,radial,axis,points)
    frame=DB.Frame(origin,radial,axis.CrossProduct(radial),axis)
    solid=DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop]),0,2*math.pi)
    return bind(doc,solid,name,param,category)

def cylinder(doc,name,origin,axis,r,start,end,param,category):
    return revolved(doc,name,origin,axis,[(0,start),(r,start),(r,end),(0,end)],param,category)

def circular_profile(center,tangent,r):
    u=DB.XYZ.BasisX
    if abs(tangent.DotProduct(u))>.9: u=DB.XYZ.BasisZ
    u=u.Subtract(tangent.Multiply(u.DotProduct(tangent))).Normalize()
    v=tangent.CrossProduct(u).Normalize()
    loop=DB.CurveLoop()
    loop.Append(DB.Arc.Create(center,r/12.,0,math.pi,u,v))
    loop.Append(DB.Arc.Create(center,r/12.,math.pi,2*math.pi,u,v))
    return loop

def curved_arm(doc,x,param,category):
    # The circular centerline is photo-derived. Overall 5.5H x 8D stays within spec.
    start=xyz(x,1.72,.33)
    mid=xyz(x,4.812,2.20)
    end=xyz(x,3.55,7.58)
    arc=DB.Arc.Create(start,end,mid)
    tangent=arc.ComputeDerivatives(0,True).BasisX.Normalize()
    path=DB.CurveLoop();path.Append(arc)
    solid=DB.GeometryCreationUtilities.CreateSweptGeometry(path,0,0,
            List[DB.CurveLoop]([circular_profile(start,tangent,.11)]))
    return bind(doc,solid,'Swan neck '+str(x),param,category)

def set_color(asset,key,color):
    prop=asset.FindByName(key)
    if prop is None: raise RuntimeError('Appearance property missing: '+key)
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color))

def set_scalar(asset,key,value):
    prop=asset.FindByName(key)
    if prop is None: raise RuntimeError('Appearance property missing: '+key)
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.Value=value

def make_material(doc,app,name,color,gloss,refl,illum):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    appearance=DB.AppearanceAssetElement.Create(doc,name,source)
    mat=doc.GetElement(DB.Material.Create(doc,name));mat.AppearanceAssetId=appearance.Id
    mat.Color=DB.Color(*color)
    scope=DB.Visual.AppearanceAssetEditScope(doc);asset=scope.Start(appearance.Id)
    set_color(asset,'generic_diffuse',color)
    set_scalar(asset,'generic_glossiness',gloss)
    set_scalar(asset,'generic_reflectivity_at_0deg',refl)
    set_scalar(asset,'generic_reflectivity_at_90deg',.75)
    set_scalar(asset,'generic_self_illum_luminance',illum)
    scope.Commit(True);scope.Dispose()
    mat.MaterialClass='Metal' if not illum else 'Glass'
    return mat

def preview(doc,name,eye):
    vtype=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
            if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    view=DB.View3D.CreateIsometric(doc,vtype.Id);view.Name=name
    target=xyz(0,2.7,3.7)
    forward=target.Subtract(eye).Normalize()
    up=DB.XYZ.BasisY
    if abs(up.DotProduct(forward))>.98:up=DB.XYZ.BasisZ
    right=forward.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    view.DetailLevel=DB.ViewDetailLevel.Fine;view.DisplayStyle=DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(cat.Id):
            view.SetCategoryHidden(cat.Id,True)
    region=DB.BoundingBoxXYZ();region.Min=xyz(-8,-.2,.001);region.Max=xyz(8,5.8,8.1)
    view.SetSectionBox(region);view.IsSectionBoxActive=True
    return view

def export(doc,views):
    opts=DB.ImageExportOptions();opts.ExportRange=DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    opts.FilePath=os.path.join(OUT,'USLEDZ15-76')
    opts.HLRandWFViewsFileType=DB.ImageFileType.PNG
    opts.ShadowViewsFileType=DB.ImageFileType.PNG
    opts.ImageResolution=DB.ImageResolution.DPI_150
    opts.ZoomType=DB.ZoomFitType.FitToPage;opts.PixelSize=1600
    doc.ExportImage(opts)

try:
    app=__revit__.Application
    report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create family')
    doc=app.NewFamilyDocument(TEMPLATE);docs.append(doc)
    tx=DB.Transaction(doc,'Build USLEDZ15-76');tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager;fm.NewType('15 in - Weathered Brass')
    metal=make_material(doc,app,'USLEDZ15 - Weathered Brass',(135,106,68),.46,.36,0.)
    lens=make_material(doc,app,'USLEDZ15 - Warm Opal Diffuser',(246,231,197),.23,.08,65.)
    mp=fm.AddParameter('Metal Finish',DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
    lp=fm.AddParameter('LED Diffuser Finish',DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
    fm.Set(mp,metal.Id);fm.Set(lp,lens.Id)
    for label,value in [('Overall Width',15.),('Overall Height',5.5),('Overall Projection',8.),('Shade Diameter',.75)]:
        p=fm.AddParameter(label,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
        fm.SetFormula(p,str(value)+' in')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'House of Troy'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'USLEDZ15-76'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
        'Ultra Slim-Line 15 in LED picture light, Weathered Brass. Visualization family; 4.5W, 2700K, 360 lm per source.')]:
        p=fm.get_Parameter(bip)
        if p is not None:fm.Set(p,value)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'15 W x 5.5 H x 8 D from House of Troy. Shade diameter 0.75 in from reseller listing. Arm curves, spacing, mounts, lens and end-cap details inferred from one product view. No photometric output.')
    mount=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,'Wall Mounts')
    arms=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,'Swan Neck Arms')
    head=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,'LED Tube')
    diffuser=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,'Diffuser')
    checkpoint('build geometry')
    for x in [-5.3,5.3]:
        box(doc,'Vertical mounting clip '+str(x),x-.30,0,0,x+.30,1.80,.16,mp,mount)
        cylinder(doc,'Arm ferrule '+str(x),xyz(x,0,.27),DB.XYZ.BasisY,.18,1.47,1.9,mp,mount)
        curved_arm(doc,x,mp,arms)
        cylinder(doc,'Head arm socket '+str(x),xyz(x,3.55,7.58),DB.XYZ.BasisZ,.16,-.23,.08,mp,head)
    # 15 in full end-to-end slim cylinder; caps are concentric details within the envelope.
    cylinder(doc,'Tubular LED shade',xyz(0,3.55,7.625),DB.XYZ.BasisX,.375,-7.5,7.5,mp,head)
    for x0,x1 in [(-7.5,-7.39),(7.39,7.5)]:
        cylinder(doc,'End cap',xyz(0,3.55,7.625),DB.XYZ.BasisX,.375,x0,x1,mp,head)
    box(doc,'Underside opal LED lens',-7.10,3.135,7.43,7.10,3.195,7.82,lp,diffuser)
    doc.Regenerate()
    elements=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    report['geometry_bounds_inches']=bounds(elements)
    report['geometry_parts']=len(elements)
    views=[preview(doc,'Front Oblique',xyz(20,12,20)),preview(doc,'Front',xyz(0,3,28)),
           preview(doc,'Side',xyz(21,2.7,3.7))]
    tx.Commit();tx=None
    checkpoint('save and export')
    opts=DB.SaveAsOptions();opts.OverwriteExistingFile=True;opts.PreviewViewId=views[0].Id
    doc.SaveAs(RFA,opts);export(doc,views)
    docs.remove(doc);doc.Close(False)
    doc=app.OpenDocumentFile(RFA);docs.append(doc)
    report['reopened']=doc.IsFamilyDocument
    report['family_placement_type']=str(doc.OwnerFamily.FamilyPlacementType)
    report['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    project=app.NewProjectDocument(DB.UnitSystem.Imperial);docs.append(project)
    family=doc.LoadFamily(project)
    symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Validate wall placement and materials');tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    wall=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,10,0,False,False)
    symbol.Activate();project.Regenerate()
    ref=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]
    face=wall.GetGeometryObjectFromReference(ref)
    point=face.Project(DB.XYZ(0,0,5)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol)
    project.Regenerate()
    report['wall_face_placed']=inst.Host is not None and inst.Host.Id==wall.Id
    report['placed_bounds_inches']=bounds([inst])
    report['material_swap_tests']={}
    for label in ['Metal Finish','LED Diffuser Finish']:
        p=symbol.LookupParameter(label);old=p.AsElementId()
        alt=DB.Material.Create(project,'QA '+label)
        p.Set(alt);project.Regenerate()
        face_ids=[f.MaterialElementId for s in all_solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        report['material_swap_tests'][label]=alt in face_ids
        p.Set(old)
    tx.Commit();tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    assert report['reopened'] and report['wall_face_placed']
    assert all(report['material_swap_tests'].values())
    assert len(report['family_warnings'])==0 and len(report['project_warnings'])==0
    checkpoint('complete')
except Exception:
    report['error']=traceback.format_exc();checkpoint('failed')
finally:
    if tx:
        try:tx.RollBack()
        except:pass
    for d in reversed(docs):
        try:d.Close(False)
        except:pass
