# -*- coding: utf-8 -*-
"""Independent Edge visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'edge_txw2a_22_down30')
RFA = os.path.join(OUT, 'Edge_TXW2A_22_Actual_Chrome_Down30_R2025.rfa')
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
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-12,-3,.001); box.Max=xyz(12,3,4.8)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'Edge')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    chrome_source=next(a for a in assets if 'Chrome - mirror' in asset_label(a))
    steel,_=clone_material(doc,'Edge - Polished Chrome',chrome_source,(190,195,200),0)
    steel.MaterialClass='Metal'; steel.Shininess=128; steel.Smoothness=100
    mat,appearance=clone_material(doc,'Edge - White Inner Diffuser',source,(252,247,235),0)
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
    tx=DB.Transaction(doc,'Build Edge visualization family'); tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('22 inch actual metal - Chrome - 30 degrees down')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id); params[name]=p
    for name,value in [('Overall Width',22.0),('Overall Height',4.62),('Projection',2.633871500692704)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Reference reconstruction'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'Edge TXW2A - 22 inch actual metal channel'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Visualization reconstruction; chrome linear housing and white front diffuser; no MEP or photometric source')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'22.0 inch actual metal length requested by user; 4.62 inch square plate, 0.37 inch plate depth, 0.9 inch bar height, 2 inch center clamp width from supplied drawing. Bar and center clamp tilted 30 degrees down around horizontal axis at 1.25 inch standoff. Original neutral projection 2.49 inches. Clamp height, bar depth and hidden pivot details inferred; fixed geometry; no photometric source.')
    cats={}
    for name in ['Housing','Diffusers','Mount']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    metal=params['Frame Finish']; glow=params['Diffuser Finish']
    def box(name,x0,y0,z0,x1,y1,z1,p,c):
        return form(doc,name,xyz(0,0,z0),DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z1-z0,p,c)
    # X horizontal, Y vertical, Z away from wall; inches.
    box('Square backplate',-2.31,-2.31,0,2.31,2.31,.37,metal,cats['Mount'])
    cylinder(doc,'Pivot connector',xyz(0,0,.37),DB.XYZ.BasisZ,.24,0,.88,metal,cats['Mount'])
    # Center clamp wraps the bar; 1.24 inch section depth from side diagram.
    box('Center clamp',-1,-.62,1.25,1,.62,2.49,metal,cats['Housing'])
    # The photograph shows a broad metal top, slim rims, inset luminous face.
    box('Channel rear',-11.0,-.45,1.34,11.0,.45,1.43,metal,cats['Housing'])
    box('Channel top',-11.0,.38,1.43,11.0,.45,2.40,metal,cats['Housing'])
    box('Channel bottom',-11.0,-.45,1.43,11.0,-.38,2.40,metal,cats['Housing'])
    for x0,x1 in [(-11.0,-10.88),(10.88,11.0)]:
        box('End cap',x0,-.45,1.43,x1,.45,2.40,metal,cats['Housing'])
    for x0,x1 in [(-10.88,-1),(1,10.88)]:
        box('Inset white lens',x0,-.38,2.34,x1,.38,2.395,glow,cats['Diffusers'])
    # Positive right-hand X rotation points the forward +Z normal down toward -Y.
    axis=DB.Line.CreateBound(xyz(-12,0,1.25),xyz(12,0,1.25))
    rotating=[e.Id for e in DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement)
              if e.Subcategory.Name in ['Housing','Diffusers']]
    DB.ElementTransformUtils.RotateElements(doc,List[DB.ElementId](rotating),axis,math.pi/6)
    report['bar_downward_tilt_degrees']=-30
    report['pivot_local_inches']=[0,0,1.25]
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
    expected=DB.XYZ(0,-.5,math.sqrt(3)/2)
    report['diffuser_normal_checks']=[]
    for e in ds:
        normals=[f.FaceNormal for solid in solids(e.get_Geometry(DB.Options())) for f in solid.Faces if isinstance(f,DB.PlanarFace)]
        report['diffuser_normal_checks'].append(any(n.DotProduct(expected)>.999999 for n in normals))
    assert all(report['diffuser_normal_checks'])

    report['diffuser_centers_y_inches']=[(e.get_BoundingBox(None).Min.Y+e.get_BoundingBox(None).Max.Y)*6 for e in ds]
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='Edge - White Inner Diffuser')
    a=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    report['diffuser_glow_luminance']=a.FindByName('generic_self_illum_luminance').Value
    checkpoint('test native wall placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test Edge wall placement'); tx.Start()
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
    report['preview_files']=[n for n in os.listdir(OUT) if n.startswith('Edge -') and n.endswith('.png')]
    assert report['reopened'] and report['loaded_and_face_placed']
    assert all(report['material_tests'].values())
    assert report['diffuser_count']==2
    assert all(abs(a-b)<.01 for a,b in zip(report['dimensions_inches'],[22.0,4.62,2.633871500692704]))
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

