# -*- coding: utf-8 -*-
"""Independent Courcelette visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'courcelette')
RFA = os.path.join(OUT, 'DVI_Courcelette_873039_Graphite_Clear_Glow_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
DROP = 50.5
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
    source=next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance)
                if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    result={}
    for name,color,gloss,trans,graphic_trans,lum in [
        ('Graphite Finish',(48,49,51),.45,0.,0,0.),
        ('Clear Glass Finish',(246,249,250),.98,.96,80,0.),
        ('Bulb Finish',(255,245,220),.4,0.,0,650.)]:
        mat,appearance=clone_material(doc,'Courcelette - '+name,source,color,graphic_trans)
        mat.MaterialClass='Glass' if 'Glass' in name else 'Metal' if 'Graphite' in name else 'Light source appearance'
        scope=DB.Visual.AppearanceAssetEditScope(doc)
        a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color)
        scalar(a,'generic_glossiness',gloss)
        scalar(a,'generic_transparency',trans)
        scalar(a,'generic_refraction_index',1.52)
        scalar(a,'generic_reflectivity_at_0deg',.045 if trans else .1)
        scalar(a,'generic_reflectivity_at_90deg',.8 if trans else .4)
        scalar(a,'generic_self_illum_luminance',lum)
        if lum:
            set_color(a,DB.Visual.Generic.GenericSelfIllumFilterMap,(255,245,225))
            scalar(a,DB.Visual.Generic.GenericSelfIllumColorTemperature,2700.)
        scope.Commit(True); scope.Dispose()
        result[name]=mat
    return result

def preview(doc,name,eye,target,close=False,top=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name
    forward=target.Subtract(eye).Normalize()
    up=DB.XYZ.BasisY if top else DB.XYZ(0,0,-1)
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine; v.DisplayStyle=DB.DisplayStyle.Shading; v.Scale=1
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    if close:
        for cat in doc.OwnerFamily.FamilyCategory.SubCategories:
            if cat.Name=='Canopy and Suspension': v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-25,-12,DROP-14 if close else .001); box.Max=xyz(25,12,DROP+1)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(OUT,'Courcelette')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1800
    doc.ExportImage(o)

def analytic_globe_bounds(doc,globes):
    # Intersect the saved analytic shells along axes through each center.
    # Exterior extrema remain on the spheres; the inward mouth removes only a cap.
    lo=[1e10]*3; hi=[-1e10]*3
    for g in globes:
        solid=next(solids(doc.GetElement(DB.ElementId(int(g['id']))).get_Geometry(DB.Options())))
        center=g['center']
        for axis in range(3):
            start=center[:]; end=center[:]; start[axis]-=5; end[axis]+=5
            hits=solid.IntersectWithCurve(DB.Line.CreateBound(xyz(*start),xyz(*end)),DB.SolidCurveIntersectionOptions())
            for i in range(hits.SegmentCount):
                for j in [0,1]:
                    p=hits.GetCurveSegment(i).GetEndPoint(j)
                    value=[p.X,p.Y,p.Z][axis]*12
                    lo[axis]=min(lo[axis],value); hi[axis]=max(hi[axis],value)
    return lo+hi

try:
    app=__revit__.Application; report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create materials')
    doc=app.NewFamilyDocument(TEMPLATE); docs.append(doc)
    tx=DB.Transaction(doc,'Build Courcelette visualization family'); tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager; fm.NewType('46.6 in - Graphite Clear - 50.5 in Drop')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id); params[name]=p
    for name,value in [('Overall Length',46.6),('Overall Width',21.59),('Fixture Body Height',12.95),('Total Drop',DROP)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'DVI Lighting'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'Courcelette Linear Pendant / Lightology 873039'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Graphite and clear glass with warm bulb appearance; visualization only')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'Overall dimensions from supplied specs. Arm centers, globe diameter, canopy and internal lamp details inferred from drawing/photo. Fixed 50.5 inch drop; material glow only.')
    cats={}
    for name in ['Canopy and Suspension','Graphite Framework','Clear Globes','Visible Bulbs']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    metal=params['Graphite Finish']; glass=params['Clear Glass Finish']; bulb=params['Bulb Finish']
    canopy=cats['Canopy and Suspension']; framecat=cats['Graphite Framework']
    h=DROP-12.95
    checkpoint('build canopy and framework')
    cylinder(doc,'Round graphite canopy',DB.XYZ.Zero,DB.XYZ.BasisZ,2.5,0,.9,metal,canopy,.06)
    cylinder(doc,'Ceiling downrod socket',DB.XYZ.Zero,DB.XYZ.BasisZ,.27,.88,1.35,metal,canopy,.025)
    cylinder(doc,'Downrod',DB.XYZ.Zero,DB.XYZ.BasisZ,.18,1.30,h+.02,metal,canopy)
    for z in [13.0,25.0]:
        cylinder(doc,'Subtle downrod joint',DB.XYZ.Zero,DB.XYZ.BasisZ,.195,z,z+.12,metal,canopy)
    for x in [-1.5,1.5]:
        cylinder(doc,'Visible canopy fastener',xyz(x,0,0),DB.XYZ.BasisZ,.115,.88,1.12,metal,canopy,.025)
    cylinder(doc,'Top body connector',DB.XYZ.Zero,DB.XYZ.BasisZ,.35,h,h+.82,metal,framecat,.03)
    cylinder(doc,'Central vertical column',DB.XYZ.Zero,DB.XYZ.BasisZ,.8,h+.8,DROP-3.05,metal,framecat,.07)
    cylinder(doc,'Column bottom seam',DB.XYZ.Zero,DB.XYZ.BasisZ,.815,DROP-3.28,DROP-3.12,metal,framecat,.03)
    # Three crossed opposing pairs reconstructed from plan and front elevation.
    centers=[[-19.3,5.25,DROP-4],[19.3,-5.25,DROP-4],
             [-13.7,-3.85,DROP-5.4],[13.7,3.85,DROP-5.4],
             [0,-6.795,DROP-6.8],[0,6.795,DROP-6.8]]
    report['globes']=[]; radius=4.; wall=.06; mouth=1.15
    cut=-math.sqrt(radius*radius-mouth*mouth)
    inner=radius-wall; inner_mouth=math.sqrt(inner*inner-cut*cut)
    for i,center in enumerate(centers):
        c=xyz(*center); axis=DB.XYZ(center[0],center[1],0).Normalize()
        dist=math.sqrt(center[0]**2+center[1]**2)
        cylinder(doc,'Arm '+str(i+1),xyz(0,0,center[2]),axis,.18,0,dist+cut,metal,framecat)
        cylinder(doc,'Globe mounting cup '+str(i+1),c,axis,1.18,cut-.13,cut+.10,metal,framecat,.07)
        cylinder(doc,'Socket '+str(i+1),c,axis,.38,cut+.05,-1.35,metal,framecat,.04)
        cylinder(doc,'Warm lamp '+str(i+1),c,axis,.37,-1.4,.45,bulb,cats['Visible Bulbs'],.18)
        g=revolved(doc,'Clear glass globe '+str(i+1),c,axis,
            [(mouth,cut),('arc',(radius,0),(0,radius)),(0,inner),
             ('arc',(inner,0),(inner_mouth,cut))],glass,cats['Clear Globes'])
        report['globes'].append({'id':str(g.Id.Value),'center':center,'radius':radius})
    doc.Regenerate()
    target=xyz(0,0,DROP-6)
    views=[preview(doc,'Full Pendant',xyz(26,-85,13),xyz(0,0,DROP/2)),
           preview(doc,'Body Oblique',xyz(27,-75,DROP-28),target,True),
           preview(doc,'Front',xyz(0,-80,DROP-6),target,True),
           preview(doc,'Side',xyz(80,0,DROP-6),target,True),
           preview(doc,'Plan',xyz(0,0,DROP-70),target,True,True)]
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
    report['globe_count']=len([e for e in forms if e.Subcategory.Name=='Clear Globes'])
    report['bulb_count']=len([e for e in forms if e.Subcategory.Name=='Visible Bulbs'])
    b=bounds(forms); report['display_bounds_inches']=b
    gb=analytic_globe_bounds(doc,report['globes']); report['analytic_globe_bounds_inches']=gb
    report['overall_dimensions_inches']=[gb[3]-gb[0],gb[4]-gb[1],gb[5]-b[2]]
    body=bounds([e for e in forms if e.Subcategory.Name=='Graphite Framework'])
    report['fixture_body_height_inches']=gb[5]-body[2]
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    for name,key,prop in [('Clear Glass Finish','glass_transparency','generic_transparency'),('Bulb Finish','bulb_glow_luminance','generic_self_illum_luminance')]:
        m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='Courcelette - '+name)
        report[key]=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset().FindByName(prop).Value
    checkpoint('test overhead placement and finishes')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test overhead placement'); tx.Start()
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
    report['preview_files']=[n for n in os.listdir(OUT) if n.startswith('Courcelette -') and n.endswith('.png')]
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

