# -*- coding: utf-8 -*-
"""Independent Trinity visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'trinity')
RFA = os.path.join(OUT, 'Kuzco_Trinity_Low_PD62014_BKSM_Glow_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
DROP = 48.0
report = {'rfa_path': RFA, 'total_drop_inches': DROP}
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

def make_materials(doc,app):
    import System
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    def schema(a):
        p=a.FindByName('BaseSchema')
        return p.Value if p is not None else ''
    source=next(a for a in assets if schema(a)=='GenericSchema')
    result={}
    for name,color,gloss,lum in [('Black Metal Finish',(28,29,31),.45,0.),('Diffuser Finish',(255,243,222),.35,450.)]:
        mat,appearance=clone_material(doc,'Trinity - '+name,source,color,0)
        scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color)
        scalar(a,'generic_glossiness',gloss); scalar(a,'generic_transparency',0.)
        scalar(a,'generic_reflectivity_at_0deg',.08); scalar(a,'generic_reflectivity_at_90deg',.4)
        scalar(a,'generic_self_illum_luminance',lum)
        if lum:
            set_color(a,DB.Visual.Generic.GenericSelfIllumFilterMap,(255,250,240))
            scalar(a,DB.Visual.Generic.GenericSelfIllumColorTemperature,3000.)
        scope.Commit(True); scope.Dispose(); result[name]=mat
    source=next(a for a in assets if schema(a)=='SolidGlassSchema')
    mat,appearance=clone_material(doc,'Trinity - Smoke Glass',source,(102,106,112),55)
    mat.MaterialClass='Glass'
    scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
    names=list(System.Enum.GetNames(DB.Visual.SolidglassTransmittanceType))
    report['glass_color_modes']=names
    mode=next(n for n in names if 'custom' in n.lower())
    scalar(a,DB.Visual.SolidGlass.SolidglassTransmittance,int(System.Enum.Parse(DB.Visual.SolidglassTransmittanceType,mode)))
    set_color(a,DB.Visual.SolidGlass.SolidglassTransmittanceCustomColor,(115,120,127))
    scalar(a,DB.Visual.SolidGlass.SolidglassColorByObject,False)
    scalar(a,DB.Visual.SolidGlass.SolidglassGlossiness,.98)
    scalar(a,DB.Visual.SolidGlass.SolidglassRefractionIor,1.52)
    scalar(a,DB.Visual.SolidGlass.CommonTintToggle,False)
    scalar(a,DB.Visual.SolidGlass.SolidglassBumpEnable,False)
    scope.Commit(True); scope.Dispose()
    result['Smoke Glass Finish']=mat
    return result

def shade(doc,h,param,category):
    # Two tangent ellipse quadrants describe the rounded shoulder and lower rim.
    # The outer and inner loops leave a real opening at the underside.
    loop=DB.CurveLoop()
    def line(a,b): loop.Append(DB.Line.CreateBound(xyz(a[0],0,h+a[1]),xyz(b[0],0,h+b[1])))
    def ellipse(center,rx,rz,start,end,reverse=False):
        c=DB.Ellipse.CreateCurve(xyz(center,0,h+3.0625),rx/12.,rz/12.,DB.XYZ.BasisX,DB.XYZ.BasisZ,start,end)
        loop.Append(c.CreateReversed() if reverse else c)
    line((3.1,0),(3.75,0))
    ellipse(3.75,3.375,3.0625,-math.pi/2,0)
    ellipse(4.875,2.25,3.0625,0,math.pi/2)
    line((4.875,6.125),(4.875,6.045))
    ellipse(4.875,2.17,2.9825,0,math.pi/2,True)
    ellipse(3.75,3.295,2.9825,-math.pi/2,0,True)
    line((3.75,.08),(3.1,.08)); line((3.1,.08),(3.1,0))
    frame=DB.Frame(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ)
    solid=DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop]),0,2*math.pi)
    e=DB.FreeFormElement.Create(doc,solid); e.Subcategory=category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    return e

def preview(doc,name,eye,target,close=False,bottom=False,realistic=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name
    forward=target.Subtract(eye).Normalize(); up=DB.XYZ.BasisY if bottom else DB.XYZ(0,0,-1)
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    if close:
        for cat in doc.OwnerFamily.FamilyCategory.SubCategories:
            if cat.Name=='Canopy and Suspension': v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-8,-8,DROP-6.5 if close else .001); box.Max=xyz(8,8,DROP+.5)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'Trinity')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

try:
    app=__revit__.Application; report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create materials')
    doc=app.NewFamilyDocument(TEMPLATE); docs.append(doc)
    tx=DB.Transaction(doc,'Build Trinity Low pendant'); tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('14.25 in - Black Smoke - 48 in Drop')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id); params[name]=p
    for name,value in [('Shade Diameter',14.25),('Shade Height',6.125),('Bottom Opening Diameter',9.75),('Canopy Diameter',4.75),('Total Drop',DROP)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Kuzco Lighting'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'Trinity Low / PD62014-BKSM / Lightology 1009570'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Black metal, smoke glass, warm recessed diffuser. Visualization only; no photometric source.')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    cats={}
    for name in ['Canopy and Suspension','Smoke Glass Shade','Recessed Housing','Warm Diffuser']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    metal=params['Black Metal Finish']; glass=params['Smoke Glass Finish']; diffuser=params['Diffuser Finish']
    h=DROP-6.125
    checkpoint('build hollow glass and recessed light')
    canopy=cylinder(doc,'Canopy',DB.XYZ.Zero,DB.XYZ.BasisZ,2.375,0,.25,metal,cats['Canopy and Suspension'],.035)
    cylinder(doc,'Downrod socket',DB.XYZ.Zero,DB.XYZ.BasisZ,.25,.23,.70,metal,cats['Canopy and Suspension'],.025)
    cylinder(doc,'Downrod',DB.XYZ.Zero,DB.XYZ.BasisZ,.1875,.65,h+.25,metal,cats['Canopy and Suspension'])
    for x in [-1.45,1.45]:
        cylinder(doc,'Canopy fixing',xyz(x,0,0),DB.XYZ.BasisZ,.095,.24,.55,metal,cats['Canopy and Suspension'],.02)
    g=shade(doc,h,glass,cats['Smoke Glass Shade'])
    q=.25; k=1-math.sqrt(.5)
    revolved(doc,'Recessed black lamp housing',DB.XYZ.Zero,DB.XYZ.BasisZ,
        [(0,h+.20),(3.05,h+.20),('arc',(3.3-q*k,h+.20+q*k),(3.3,h+.45)),
         (3.3,h+1.10),('arc',(3.3-q*k,h+1.35-q*k),(3.05,h+1.35)),
         (2.65,h+1.35),(2.65,h+1.24),(0,h+1.24)],metal,cats['Recessed Housing'])
    cylinder(doc,'Warm recessed diffuser',DB.XYZ.Zero,DB.XYZ.BasisZ,2.645,h+1.20,h+1.25,diffuser,cats['Warm Diffuser'])
    doc.Regenerate()
    target=xyz(0,0,h+3)
    views=[preview(doc,'Full Pendant',xyz(15,-65,18),xyz(0,0,DROP/2)),
           preview(doc,'Shade Front',xyz(0,-50,h+3),target,True),
           preview(doc,'Shade Oblique',xyz(20,-45,h+9),target,True),
           preview(doc,'Underside',xyz(0,0,DROP+40),target,True,True),
           preview(doc,'Material Review',xyz(20,-45,h+9),target,True,False,True)]
    tx.Commit(); tx=None
    checkpoint('save and export')
    o=DB.SaveAsOptions(); o.OverwriteExistingFile=True; o.MaximumBackups=1; o.PreviewViewId=views[0].Id
    doc.SaveAs(RFA,o); report['export_error']=None
    try: export(doc,views)
    except Exception: report['export_error']=traceback.format_exc()
    doc.Close(False); docs.remove(doc)
    doc=app.OpenDocumentFile(RFA); docs.append(doc)
    report['reopened']=doc.IsFamilyDocument; report['category']=doc.OwnerFamily.FamilyCategory.Name
    report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    g=next(e for e in forms if e.Subcategory.Name=='Smoke Glass Shade')
    solid=next(solids(g.get_Geometry(DB.Options())))
    b=bounds(forms); report['display_bounds_inches']=b
    widths=[]
    for axis in range(2):
        start=[0,0,h+3.0625]; end=start[:]; start[axis]=-10; end[axis]=10
        hits=solid.IntersectWithCurve(DB.Line.CreateBound(xyz(*start),xyz(*end)),DB.SolidCurveIntersectionOptions())
        coords=[]
        for i in range(hits.SegmentCount):
            for j in [0,1]:
                p=hits.GetCurveSegment(i).GetEndPoint(j); coords.append([p.X,p.Y][axis]*12)
        widths.append(max(coords)-min(coords))
    report['overall_dimensions_inches']=widths+[b[5]-b[2]]
    gb=bounds([g]); report['shade_height_inches']=gb[5]-gb[2]
    bottom_radii=[]
    for edge in solid.Edges:
        p=edge.AsCurve().GetEndPoint(0)
        if abs(p.Z*12-DROP)<1e-6: bottom_radii.append(math.sqrt(p.X*p.X+p.Y*p.Y)*12)
    report['bottom_opening_inches']=2*min(bottom_radii)
    ray=DB.Line.CreateBound(xyz(0,0,DROP-.1),xyz(0,0,DROP+.1))
    report['bottom_center_obstructed']=solid.IntersectWithCurve(ray,DB.SolidCurveIntersectionOptions()).SegmentCount>0
    canopy=next(e for e in forms if e.Subcategory.Name=='Canopy and Suspension' and abs(bounds([e])[2])<1e-6)
    cb=bounds([canopy]); report['canopy_display_diameter_inches']=cb[4]-cb[1]
    cs=next(solids(canopy.get_Geometry(DB.Options())))
    hit=cs.IntersectWithCurve(DB.Line.CreateBound(xyz(0,-4,.125),xyz(0,4,.125)),DB.SolidCurveIntersectionOptions())
    canopy_y=[hit.GetCurveSegment(i).GetEndPoint(j).Y*12 for i in range(hit.SegmentCount) for j in [0,1]]
    report['canopy_diameter_inches']=max(canopy_y)-min(canopy_y)
    # Along the open centerline, the first visible fixture surface from below
    # must be the diffuser rather than the housing or an accidental glass cap.
    ray=DB.Line.CreateBound(xyz(0,0,DROP-.1),xyz(0,0,h+.1))
    first_surfaces=[]
    for element in forms:
        for solid_part in solids(element.get_Geometry(DB.Options())):
            hits=solid_part.IntersectWithCurve(ray,DB.SolidCurveIntersectionOptions())
            for i in range(hits.SegmentCount):
                for j in [0,1]:
                    first_surfaces.append((hits.GetCurveSegment(i).GetEndPoint(j).Z,element.Subcategory.Name))
    report['underside_diffuser_exposed']=max(first_surfaces)[1]=='Warm Diffuser'
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    for name,key,prop in [('Diffuser Finish','diffuser_glow_luminance','generic_self_illum_luminance')]:
        m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='Trinity - '+name)
        report[key]=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset().FindByName(prop).Value
    m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='Trinity - Smoke Glass')
    smoke=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    report['smoke_asset_schema']=smoke.FindByName('BaseSchema').Value
    color=smoke.FindByName(DB.Visual.SolidGlass.SolidglassTransmittanceCustomColor).GetValueAsColor()
    report['smoke_transmission_rgb']=[int(color.Red),int(color.Green),int(color.Blue)]
    checkpoint('test native overhead placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test Trinity overhead placement'); tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    ft=DB.Floor.GetDefaultFloorType(project,False)
    loop=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-60,-60),(60,-60),(60,60),(-60,60)])
    floor=DB.Floor.Create(project,List[DB.CurveLoop]([loop]),ft,level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(10)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetBottomFaces(floor)[0]; face=floor.GetGeometryObjectFromReference(ref)
    point=face.Project(DB.XYZ(0,0,10)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol); project.Regenerate()
    report['loaded_and_face_placed']=inst.Host is not None and inst.Host.Id==floor.Id
    report['placed_axis_z']=inst.GetTransform().BasisZ.Z; report['material_tests']={}
    for name in params:
        p=symbol.LookupParameter(name); original=p.AsElementId()
        alternate=DB.Material.Create(project,'QA '+name); p.Set(alternate); project.Regenerate()
        ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        report['material_tests'][name]=alternate in ids or alternate in list(inst.GetMaterialIds(False))
        p.Set(original); project.Regenerate()
    tx.Commit(); tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    report['preview_files']=[n for n in os.listdir(OUT) if n.startswith('Trinity -') and n.endswith('.png')]
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

