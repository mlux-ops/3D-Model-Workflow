# -*- coding: utf-8 -*-
"""Independent Air Switch visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'air_switch')
RFA = os.path.join(OUT, 'Hansgrohe_Air_Switch_04032340_Brushed_Black_Chrome_R2025.rfa')
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
    forward=xyz(0,0,.45).Subtract(eye).Normalize()
    up=DB.XYZ.BasisZ
    if abs(forward.DotProduct(up))>.99: up=DB.XYZ.BasisY
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-1.1,-1.1,.001); box.Max=xyz(1.1,1.1,1.1)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'Air Switch')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    result={}
    for name,color,gloss,refl in [('Metal Finish',(79,73,68),.65,.65),('Seam Finish',(18,18,18),.22,.03)]:
        mat,appearance=clone_material(doc,'Air Switch - '+name,source,color,0)
        scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color)
        scalar(a,'generic_glossiness',gloss); scalar(a,'generic_transparency',0.)
        scalar(a,'generic_reflectivity_at_0deg',refl); scalar(a,'generic_reflectivity_at_90deg',.85)
        scalar(a,'generic_self_illum_luminance',0.)
        scope.Commit(True); scope.Dispose()
        mat.MaterialClass='Metal' if name=='Metal Finish' else 'Plastic'
        result[name]=mat
    return result


try:
    app=__revit__.Application; report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create materials')
    doc=app.NewFamilyDocument(TEMPLATE); docs.append(doc)
    tx=DB.Transaction(doc,'Build Air Switch visualization family'); tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_PlumbingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('04032340 - Brushed Black Chrome')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id); params[name]=p
    for name,value in [('Visible Height',.9375),('Base Diameter',1.875),('Button Diameter',.9375)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'hansgrohe'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'Air Switch 04032340'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Visualization reconstruction; brushed black chrome; no MEP connectors')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'Official Hansgrohe 2026 catalog page 46: base diameter 1.875 inch and visible height 0.9375 inch. Button diameter, base thickness, fillets and seam estimated from catalog photograph. Above-counter visualization only.')
    cats={}
    for name in ['Base','Button','Seam']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    metal=params['Metal Finish']; dark=params['Seam Finish']
    cylinder(doc,'Circular escutcheon',DB.XYZ.Zero,DB.XYZ.BasisZ,.9375,0,.375,metal,cats['Base'],.04)
    cylinder(doc,'Button lower sleeve',DB.XYZ.Zero,DB.XYZ.BasisZ,.46875,.35,.51,metal,cats['Button'])
    cylinder(doc,'Inset button seam',DB.XYZ.Zero,DB.XYZ.BasisZ,.45,.48,.56,dark,cats['Seam'])
    cylinder(doc,'Raised push button',DB.XYZ.Zero,DB.XYZ.BasisZ,.46875,.52,.9375,metal,cats['Button'],.035)
    doc.Regenerate()
    views=[preview(doc,'Front',xyz(0,-8,.45)),preview(doc,'Oblique',xyz(5,-7,5)),preview(doc,'Side',xyz(8,0,.45)),preview(doc,'Top',xyz(0,0,8)),preview(doc,'Material Review',xyz(5,-7,5),True)]
    tx.Commit(); tx=None
    checkpoint('save and export')
    o=DB.SaveAsOptions(); o.OverwriteExistingFile=True; o.MaximumBackups=1; o.PreviewViewId=views[1].Id
    doc.SaveAs(RFA,o); report['export_error']=None
    try: export(doc,views)
    except Exception: report['export_error']=traceback.format_exc()
    doc.Close(False); docs.remove(doc)
    doc=app.OpenDocumentFile(RFA); docs.append(doc)
    report['reopened']=doc.IsFamilyDocument; report['category']=doc.OwnerFamily.FamilyCategory.Name
    report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    b=bounds(forms); report['bounds_inches']=b
    report['dimensions_inches']=[b[3]-b[0],b[4]-b[1],b[5]-b[2]]
    base=[e for e in forms if e.Subcategory.Name=='Base']; bb=bounds(base)
    report['base_diameter_inches']=bb[3]-bb[0]
    bs=next(solids(base[0].get_Geometry(DB.Options())))
    diameters=[]
    for axis in [DB.XYZ.BasisX,DB.XYZ.BasisY]:
        center=xyz(0,0,.18)
        hit=bs.IntersectWithCurve(DB.Line.CreateBound(center.Subtract(axis),center.Add(axis)),DB.SolidCurveIntersectionOptions())
        diameters.append(hit.GetCurveSegment(0).Length*12)
    report['exact_base_diameters_inches']=diameters
    report['dimensions_inches']=[diameters[0],diameters[1],b[5]-b[2]]
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    report['source_url']='https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf'
    report['source_printed_page']=46
    checkpoint('test native wall placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test Air Switch wall placement'); tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    ft=next(iter(DB.FilteredElementCollector(project).OfClass(DB.FloorType)))
    loop=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-24,-24),(24,-24),(24,24),(-24,24)])
    host=DB.Floor.Create(project,List[DB.CurveLoop]([loop]),ft.Id,level.Id)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetTopFaces(host)[0]
    face=host.GetGeometryObjectFromReference(ref); point=face.Project(DB.XYZ.Zero).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol); project.Regenerate()
    report['loaded_and_face_placed']=inst.Host is not None and inst.Host.Id==host.Id
    report['mounting_normal_dot_host_normal']=inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)
    report['material_tests']={}
    for name in params:
        p=symbol.LookupParameter(name); original=p.AsElementId()
        alternate=DB.Material.Create(project,'QA '+name); p.Set(alternate); project.Regenerate()
        ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        report['material_tests'][name]=alternate in ids or alternate in list(inst.GetMaterialIds(False))
        p.Set(original); project.Regenerate()
    tx.Commit(); tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    report['preview_files']=[n for n in os.listdir(OUT) if n.startswith('Air Switch -') and n.endswith('.png')]
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

