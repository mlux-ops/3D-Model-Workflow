# -*- coding: utf-8 -*-
"""Independent Icera Malibu II RF visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'malibu')
RFA = os.path.join(OUT, 'Icera_Malibu_II_RF_C-6360.01_R2025.rfa')
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
    forward=xyz(0,12,14).Subtract(eye).Normalize()
    up=DB.XYZ.BasisZ
    if abs(forward.DotProduct(up))>.99: up=DB.XYZ.BasisY
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-10,-1,.001); box.Max=xyz(10,26,30)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'Icera Malibu II RF')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    result={}
    for name,color,gloss,refl in [('Ceramic Finish',(245,245,242),.88,.12),('Seat Finish',(245,245,242),.72,.08),('Lever Finish',(190,190,190),.95,.85)]:
        mat,appearance=clone_material(doc,'Icera Malibu II RF - '+name,source,color,0)
        scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color)
        scalar(a,'generic_glossiness',gloss); scalar(a,'generic_transparency',0.)
        scalar(a,'generic_reflectivity_at_0deg',refl); scalar(a,'generic_reflectivity_at_90deg',.85)
        scalar(a,'generic_self_illum_luminance',0.)
        scope.Commit(True); scope.Dispose()
        mat.MaterialClass='Metal' if name=='Metal Finish' else 'Plastic'
        result[name]=mat
    return result


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
