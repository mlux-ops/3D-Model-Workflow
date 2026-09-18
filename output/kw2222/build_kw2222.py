# -*- coding: utf-8 -*-
"""Independent KW2222 visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'kw2222')
RFA = os.path.join(OUT, 'KW2222_ABWG_28_R2025.rfa')
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

def capsule(r,reverse=False):
    c=3.38
    if reverse:
        return [(r,-c),('arc',(0,-c-r),(-r,-c)),(-r,c),('arc',(0,c+r),(r,c)),(r,-c)]
    return [(r,-c),(r,c),('arc',(0,c+r),(-r,c)),(-r,-c),('arc',(0,-c-r),(r,-c))]

def frame(doc,param,category):
    outer=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,capsule(2.62))
    inner=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,capsule(2.56,True))
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([outer,inner]),DB.XYZ.BasisZ,3./12)
    e=DB.FreeFormElement.Create(doc,solid); e.Subcategory=category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    return e

def lens(doc,param,category):
    # User-confirmed full-depth single diffuser; close-up shows a broad
    # cylindrical underside and nearly flat circular front with a soft edge.
    return cylinder(doc,'Full-depth continuous diffuser',xyz(0,3.38,0),
                    DB.XYZ.BasisZ,2.5,0,3,param,category,rounding=.04)

def preview(doc,name,eye,realistic=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name
    forward=xyz(0,0,1.5).Subtract(eye).Normalize()
    up=DB.XYZ.BasisY
    if abs(forward.DotProduct(up))>.99: up=DB.XYZ.BasisZ
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-3,-15,.001); box.Max=xyz(3,15,3)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'KW2222')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    chrome_source=next(a for a in assets if 'Chrome - mirror' in asset_label(a))
    steel,brassapp=clone_material(doc,'KW2222 - Antique Brass',source,(157,119,57),0)
    steel.MaterialClass='Metal'; steel.Shininess=45; steel.Smoothness=70
    scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(brassapp.Id)
    set_color(a,'generic_diffuse',(157,119,57))
    scalar(a,'generic_glossiness',.55); scalar(a,'generic_transparency',0.)
    scalar(a,'generic_reflectivity_at_0deg',.35); scalar(a,'generic_reflectivity_at_90deg',.6)
    scalar(a,'generic_self_illum_luminance',0.)
    scope.Commit(True); scope.Dispose()
    mat,appearance=clone_material(doc,'KW2222 - White Inner Diffuser',source,(252,247,235),0)
    mat.MaterialClass='Plastic'
    scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
    set_color(a,'generic_diffuse',(252,249,242))
    scalar(a,'generic_glossiness',.28); scalar(a,'generic_transparency',.03)
    scalar(a,'generic_refraction_index',1.49)
    scalar(a,'generic_reflectivity_at_0deg',.04); scalar(a,'generic_reflectivity_at_90deg',.4)
    scalar(a,'generic_self_illum_luminance',0.)
    set_color(a,DB.Visual.Generic.GenericSelfIllumFilterMap,(255,250,240))
    scalar(a,DB.Visual.Generic.GenericSelfIllumColorTemperature,3000.)
    scope.Commit(True); scope.Dispose()
    return {'Frame Finish':steel,'Diffuser Finish':mat}

try:
    app=__revit__.Application; report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create materials')
    doc=app.NewFamilyDocument(TEMPLATE); docs.append(doc)
    tx=DB.Transaction(doc,'Build KW2222 visualization family'); tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('28 inch - Antique Brass and White Glass')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id); params[name]=p
    for name,value in [('Overall Width',4.25),('Overall Height',28),('Projection',2.75)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Reference reconstruction'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'KW2222 ABWG reference reconstruction'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Visualization reconstruction; antique brass perforated rear sleeve and hollow white glass tube; no MEP or photometric source')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'28 inch height, 2 inch glass diameter, 2.75 inch projection and 4.25 inch square mounting plate from drawing. Sleeve length, thickness, perforations and hardware inferred from photos. Fixed visualization geometry; no photometric source.')
    cats={}
    for name in ['Housing','Diffusers','Mount']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    metal=params['Frame Finish']; glow=params['Diffuser Finish']
    def box(name,x0,y0,z0,x1,y1,z1,p,c):
        return form(doc,name,xyz(0,0,z0),DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z1-z0,p,c)
    # X horizontal, Y vertical, Z away from wall. Origin at mounting center.
    form(doc,'Rounded square backplate',DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,rounded_rect(-2.125,-2.125,2.125,2.125,.06),.16,metal,cats['Mount'])
    box('Central standoff',-.60,-.65,.16,.60,.65,.78,metal,cats['Mount'])
    for x in [-1.67,1.67]:
        cylinder(doc,'Mount screw',xyz(x,0,.16),DB.XYZ.BasisZ,.115,0,.075,metal,cats['Mount'])
    # Hollow glass tube; actual open ends as seen in the supplied photo.
    revolved(doc,'White glass tube',xyz(0,0,1.75),DB.XYZ.BasisY,
             [(.91,-14),(1,-14),(1,14),(.91,14)],glow,cats['Diffusers'])
    # Rear half-cylinder brass sleeve, with true radial perforations.
    origin=xyz(0,-9.3,1.75)
    loop=profile_loop(origin,DB.XYZ.BasisX,DB.XYZ.BasisZ,
        [(-1.065,0),('arc',(0,-1.065),(1.065,0)),(1.015,0),('arc',(0,-1.015),(-1.015,0))])
    sleeve=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),DB.XYZ.BasisY,18.6/12.)
    holes=0
    for row in range(49):
        y=-9.0+row*.375
        for col in range(9):
            theta=math.radians(12+col*19.5+(3 if row%2 else 0))
            radial=DB.XYZ(math.cos(theta),0,-math.sin(theta))
            center=xyz(0,y,1.75).Add(radial.Multiply(.95/12.))
            circle=DB.CurveLoop()
            u=DB.XYZ.BasisY; v=radial.CrossProduct(u)
            circle.Append(DB.Arc.Create(center,.0625/12.,0,math.pi,u,v))
            circle.Append(DB.Arc.Create(center,.0625/12.,math.pi,2*math.pi,u,v))
            cutter=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([circle]),radial,.2/12.)
            sleeve=DB.BooleanOperationsUtils.ExecuteBooleanOperation(sleeve,cutter,DB.BooleanOperationsType.Difference)
            holes+=1
    e=DB.FreeFormElement.Create(doc,sleeve); e.Subcategory=cats['Housing']
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),metal)
    report['real_perforations']=holes
    doc.Regenerate()
    views=[preview(doc,'Front',xyz(0,0,35)),preview(doc,'Oblique',xyz(18,-12,35)),
           preview(doc,'Side',xyz(35,0,1.5)),preview(doc,'Top',xyz(0,35,1.5)),
           preview(doc,'Material Review',xyz(18,-12,35),True)]
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
    ds=[e for e in forms if e.Subcategory.Name=='Diffusers']
    report['diffuser_count']=len(ds)
    report['diffuser_centers_y_inches']=[(e.get_BoundingBox(None).Min.Y+e.get_BoundingBox(None).Max.Y)*6 for e in ds]
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='KW2222 - White Inner Diffuser')
    a=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    report['diffuser_glow_luminance']=a.FindByName('generic_self_illum_luminance').Value
    checkpoint('test native wall placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test KW2222 wall placement'); tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    wall=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-5,0,0),DB.XYZ(5,0,0)),wt.Id,level.Id,9,0,False,False)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]
    face=wall.GetGeometryObjectFromReference(ref); point=face.Project(DB.XYZ(0,0,5)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol); project.Regenerate()
    report['loaded_and_face_placed']=inst.Host is not None and inst.Host.Id==wall.Id
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
    report['preview_files']=[n for n in os.listdir(OUT) if n.startswith('KW2222 -') and n.endswith('.png')]
    assert report['reopened'] and report['loaded_and_face_placed']
    assert all(report['material_tests'].values())
    assert report['diffuser_count']==1
    assert all(abs(a-b)<.01 for a,b in zip(report['dimensions_inches'],[4.25,28,2.75]))
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


