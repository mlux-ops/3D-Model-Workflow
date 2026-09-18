# -*- coding: utf-8 -*-
"""Independent Mila visualization family. Run in Revit 2025 via pyRevit CLI.
Only new documents and this task's output folder are modified.
"""
import os
import json
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow'
OUT = os.path.join(ROOT, 'output', 'mila')
RFA = os.path.join(OUT, 'Matthew_McCormick_Mila_Dark_Adjustable_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
report = {'rfa_path': RFA}
docs = []
tx = None

def checkpoint(stage):
    report['stage'] = stage
    with open(os.path.join(OUT,'validation.json'), 'w') as f:
        json.dump(report,f,indent=2,default=str)

def xyz(x,y,z):
    return DB.XYZ(x/12.0,y/12.0,z/12.0)

def solids(geometry):
    for item in geometry:
        if isinstance(item,DB.Solid) and item.Volume>1e-12:
            yield item
        elif isinstance(item,DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid

def bounds(elements):
    bs = [e.get_BoundingBox(None) for e in elements]
    return [min(b.Min.X for b in bs)*12,min(b.Min.Y for b in bs)*12,min(b.Min.Z for b in bs)*12,
            max(b.Max.X for b in bs)*12,max(b.Max.Y for b in bs)*12,max(b.Max.Z for b in bs)*12]

def profile_loop(origin,u,v,points):
    def p(pair):
        return origin.Add(u.Multiply(pair[0]/12.0)).Add(v.Multiply(pair[1]/12.0))
    loop=DB.CurveLoop()
    current=points[0]
    for item in points[1:]:
        if len(item)==3 and item[0]=='arc':
            mid,end=item[1],item[2]
            loop.Append(DB.Arc.Create(p(current),p(end),p(mid)))
        else:
            end=item
            loop.Append(DB.Line.CreateBound(p(current),p(end)))
        current=end
    if current != points[0]:
        loop.Append(DB.Line.CreateBound(p(current),p(points[0])))
    return loop

def rounded_rect(x0,y0,x1,y1,r):
    k=1-math.sqrt(.5)
    return [(x0+r,y0),(x1-r,y0),('arc',(x1-r*k,y0+r*k),(x1,y0+r)),
            (x1,y1-r),('arc',(x1-r*k,y1-r*k),(x1-r,y1)),
            (x0+r,y1),('arc',(x0+r*k,y1-r*k),(x0,y1-r)),
            (x0,y0+r),('arc',(x0+r*k,y0+r*k),(x0+r,y0))]

def form(doc,name,origin,u,v,normal,profile,length,parameter,category):
    loop=profile_loop(origin,u,v,profile)
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),normal,length/12.0)
    e=DB.FreeFormElement.Create(doc,solid)
    e.Subcategory=category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),parameter)
    report.setdefault('parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

def asset_label(a):
    strings=[a.Name]
    for key in ['UIName','description','keyword']:
        p=a.FindByName(key)
        if p is not None:
            try: strings.append(str(p.Value))
            except Exception: pass
    return ' | '.join(strings)

def clone_material(doc,name,asset,color,transparency):
    existing=next((m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name==name),None)
    if existing: return existing,doc.GetElement(existing.AppearanceAssetId)
    appearance=DB.AppearanceAssetElement.Create(doc,name,asset)
    mat=doc.GetElement(DB.Material.Create(doc,name))
    mat.AppearanceAssetId=appearance.Id
    mat.Color=DB.Color(*color)
    mat.Transparency=transparency
    return mat,appearance

def set_color(asset,key,color):
    prop=asset.FindByName(key)
    if prop is None: raise RuntimeError('Missing appearance property: '+key)
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color))

def scalar(asset,key,value):
    prop=asset.FindByName(key)
    if prop is None: raise RuntimeError('Missing appearance property: '+key)
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.Value=value

def revolved(doc,name,origin,axis,points,param,category):
    radial=DB.XYZ.BasisX if abs(axis.Z)>.99 else DB.XYZ.BasisZ
    radial=radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop=profile_loop(origin,radial,axis,points)
    frame=DB.Frame(origin,radial,axis.CrossProduct(radial),axis)
    solid=DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop]),0,2*math.pi)
    e=DB.FreeFormElement.Create(doc,solid)
    e.Subcategory=category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    report.setdefault('parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

def cylinder(doc,name,origin,axis,r,start,end,param,category,rounding=0):
    if rounding:
        q=rounding; k=1-math.sqrt(.5)
        points=[(0,start),(r-q,start),('arc',(r-q*k,start+q*k),(r,start+q)),
                (r,end-q),('arc',(r-q*k,end-q*k),(r-q,end)),(0,end)]
    else: points=[(0,start),(r,start),(r,end),(0,end)]
    return revolved(doc,name,origin,axis,points,param,category)

def preview(doc,name,eye,realistic=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name
    forward=xyz(0,0,32).Subtract(eye).Normalize()
    up=DB.XYZ.BasisZ.Negate()
    if abs(forward.DotProduct(up))>.99: up=DB.XYZ.BasisY
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-6,-6,.001); box.Max=xyz(6,6,61)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'Mila')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    result={}
    for name,color,gloss,refl in [('Metal Finish',(53,50,44),.42,.22),('Glass Finish',(247,244,230),.65,.08)]:
        mat,appearance=clone_material(doc,'Mila - '+name,source,color,0)
        scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color)
        scalar(a,'generic_glossiness',gloss); scalar(a,'generic_transparency',.08 if name=='Glass Finish' else 0.)
        scalar(a,'generic_reflectivity_at_0deg',refl); scalar(a,'generic_reflectivity_at_90deg',.85)
        scalar(a,'generic_self_illum_luminance',100. if name=='Glass Finish' else 0.)
        scope.Commit(True); scope.Dispose()
        mat.Transparency=8 if name=='Glass Finish' else 0
        mat.MaterialClass='Metal' if name=='Metal Finish' else 'Glass'
        result[name]=mat
    return result


def setup(doc,app):
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    p=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if p: p.Set(0)
    fm=doc.FamilyManager; fm.NewType('Mila Black')
    params={}
    for name,mat in make_materials(doc,app).items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id);params[name]=p
    return fm,params

def rod(doc,name,a,b,r,p,c):
    a=xyz(*a);b=xyz(*b);axis=b.Subtract(a)
    return cylinder(doc,name,a,axis.Normalize(),r,0,axis.GetLength()*12,p,c)

try:
    app=__revit__.Application;report['revit_version']=app.VersionNumber
    child=app.NewFamilyDocument(TEMPLATE.replace('Generic Model face based.rft','Generic Model.rft'));docs.append(child)
    tx=DB.Transaction(child,'Build fixed mobile');tx.Start()
    fm,params=setup(child,app)
    cat=child.Settings.Categories.NewSubcategory(child.OwnerFamily.FamilyCategory,'Mobile Frame')
    disc=child.Settings.Categories.NewSubcategory(child.OwnerFamily.FamilyCategory,'Luminous Acrylic')
    m=params['Metal Finish'];g=params['Glass Finish']
    # Inches from supplied PDF. Loop thickness .5; globe diameter 6.7 inferred from photo.
    unit=1/25.4
    outer=profile_loop(xyz(0,-.25,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,
        [(4.1,4.1),(4.1,25.),('arc',(0,29.1),(-4.1,25.)),(-4.1,4.1),('arc',(0,0),(4.1,4.1))])
    inner=profile_loop(xyz(0,-.25,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,
        [(3.6,4.1),(3.6,25.),('arc',(0,28.6),(-3.6,25.)),(-3.6,4.1),('arc',(0,.5),(3.6,4.1))])
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([outer,inner]),DB.XYZ.BasisY,.5/12.)
    e=DB.FreeFormElement.Create(child,solid);e.Subcategory=cat
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),m)
    revolved(child,'Opal globe',xyz(0,0,25.20),DB.XYZ.BasisZ,
        [(0,-3.35),('arc',(3.35,0),(0,3.35))],g,disc)
    cylinder(child,'Upper cable socket',DB.XYZ.Zero,DB.XYZ.BasisZ,.23,-.35,.1,m,cat)
    cylinder(child,'Globe seat',DB.XYZ.Zero,DB.XYZ.BasisZ,.35,28.5,28.65,m,cat)
    child.Regenerate()
    report['body_bounds_inches']=bounds(list(DB.FilteredElementCollector(child).OfClass(DB.FreeFormElement)))
    tx.Commit();tx=None
    co=DB.SaveAsOptions();co.OverwriteExistingFile=True
    child.SaveAs(os.path.join(OUT,'Mila_Body.rfa'),co)
    doc=app.NewFamilyDocument(TEMPLATE);docs.append(doc)
    family=child.LoadFamily(doc)
    tx=DB.Transaction(doc,'Adjustable suspension');tx.Start()
    fm,params=setup(doc,app)
    cord=fm.AddParameter('Cord Length',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,True)
    fm.Set(cord,(60-30.55)/12)
    offset=fm.AddParameter('Assembly Offset',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,True)
    fm.SetFormula(offset,'Cord Length + 1.45 in')
    total=fm.AddParameter('Total Drop',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,True)
    fm.SetFormula(total,'Cord Length + 30.55 in')
    cat=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,'Canopy and Suspension')
    cylinder(doc,'Canopy',DB.XYZ.Zero,DB.XYZ.BasisZ,3.55,0,1.1,params['Metal Finish'],cat)
    symbol=doc.GetElement(list(family.GetFamilySymbolIds())[0]);symbol.Activate()
    inst=doc.FamilyCreate.NewFamilyInstance(xyz(0,0,60-29.1),symbol,DB.Structure.StructuralType.NonStructural)
    doc.Regenerate()
    report['nested_parameters']=[(p.Definition.Name,str(p.Id.Value),p.IsReadOnly) for p in inst.Parameters]
    p=inst.get_Parameter(DB.BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM)
    if p is None: p=inst.get_Parameter(DB.BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM)
    if p is None: raise Exception('Nested elevation parameter not found')
    fm.AssociateElementParameterToFamilyParameter(p,offset)
    for name,param in params.items():fm.AssociateElementParameterToFamilyParameter(symbol.LookupParameter(name),param)
    plane=DB.SketchPlane.Create(doc,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ,DB.XYZ.Zero))
    ca=DB.CurveArray()
    for a,b in [(0,math.pi),(math.pi,2*math.pi)]:ca.Append(DB.Arc.Create(DB.XYZ.Zero,.06/12,a,b,DB.XYZ.BasisX,DB.XYZ.BasisY))
    arr=DB.CurveArrArray();arr.Append(ca)
    e=doc.FamilyCreate.NewExtrusion(True,arr,plane,2)
    e.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(1.1/12.)
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM),offset)
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),params['Metal Finish'])
    doc.Regenerate()
    views=[preview(doc,'Full Oblique',xyz(90,-130,15)),preview(doc,'Front',xyz(0,-160,32)),preview(doc,'Side',xyz(160,0,32))]
    tx.Commit();tx=None
    o=DB.SaveAsOptions();o.OverwriteExistingFile=True;o.PreviewViewId=views[0].Id
    doc.SaveAs(RFA,o);export(doc,views)
    docs.remove(doc);doc.Close(False)
    doc=app.OpenDocumentFile(RFA);docs.append(doc)
    report['reopened']=doc.IsFamilyDocument;report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    project=app.NewProjectDocument(DB.UnitSystem.Imperial);docs.append(project)
    family=doc.LoadFamily(project);symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Flex cord on native ceiling face');tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    ft=DB.Floor.GetDefaultFloorType(project,False)
    loop=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-100,-100),(100,-100),(100,100),(-100,100)])
    floor=DB.Floor.Create(project,List[DB.CurveLoop]([loop]),ft,level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(20)
    symbol.Activate();project.Regenerate()
    ref=DB.HostObjectUtils.GetBottomFaces(floor)[0];face=floor.GetGeometryObjectFromReference(ref)
    point=face.Project(DB.XYZ(0,0,20)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol);project.Regenerate()
    report['loaded_and_face_placed']=inst.Host.Id==floor.Id
    report['flex_tests']=[]
    for length in [8.,18.1496062992,48.,118.]:
        inst.LookupParameter('Cord Length').Set(length/12);project.Regenerate()
        b=inst.get_BoundingBox(None)
        actual=(point.Z-b.Min.Z)*12
        expected=length+30.55
        report['flex_tests'].append({'cord_inches':length,'actual_drop':actual,'expected_drop':expected,'pass':abs(actual-expected)<.1})
    report['material_tests']={}
    for name in params:
        p=symbol.LookupParameter(name);old=p.AsElementId();alt=DB.Material.Create(project,'QA '+name);p.Set(alt);project.Regenerate()
        ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        report['material_tests'][name]=alt in ids
        p.Set(old)
    tx.Commit();tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    assert report['reopened'] and report['loaded_and_face_placed']
    assert all(t['pass'] for t in report['flex_tests'])
    assert all(report['material_tests'].values())
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
