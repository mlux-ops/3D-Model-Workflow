# -*- coding: utf-8 -*-
"""Independent Duo pendant visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'duo')
RFA = os.path.join(OUT, 'Astro_Duo_1561665_White_Opal_Glow_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
DROP = 1000.0
report = {'rfa_path': RFA, 'total_drop_mm': DROP}
docs = []
tx = None

def checkpoint(stage):
    report['stage'] = stage
    with open(os.path.join(OUT,'validation.json'), 'w') as f:
        json.dump(report,f,indent=2,default=str)

def xyz(x,y,z):
    return DB.XYZ(x/304.8,y/304.8,z/304.8)

def solids(geometry):
    for item in geometry:
        if isinstance(item,DB.Solid) and item.Volume>1e-12:
            yield item
        elif isinstance(item,DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid

def bounds(elements):
    bs = [e.get_BoundingBox(None) for e in elements]
    return [min(b.Min.X for b in bs)*304.8,min(b.Min.Y for b in bs)*304.8,min(b.Min.Z for b in bs)*304.8,
            max(b.Max.X for b in bs)*304.8,max(b.Max.Y for b in bs)*304.8,max(b.Max.Z for b in bs)*304.8]

def profile_loop(origin,u,v,points):
    def p(pair):
        return origin.Add(u.Multiply(pair[0]/304.8)).Add(v.Multiply(pair[1]/304.8))
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
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),normal,length/304.8)
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

def revolve(doc,name,points,param,category):
    loop=profile_loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisZ,points)
    frame=DB.Frame(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ)
    solid=DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop]),0,2*math.pi)
    e=DB.FreeFormElement.Create(doc,solid)
    e.Subcategory=category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    comment=e.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
    if comment is not None and not comment.IsReadOnly: comment.Set(name)
    report.setdefault('parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

def materials(doc,app):
    source=next(a for a in app.GetAssets(DB.Visual.AssetType.Appearance)
                if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    result={}
    for name,color,gloss,trans,lum in [
        ('Metal Finish',(238,238,235),.3,0.,0.),
        ('Opal Glass Finish',(250,247,237),.65,0.,300.),
        ('Cord Finish',(228,226,220),.12,0.,0.)]:
        mat,appearance=clone_material(doc,'Duo - '+name,source,color,0)
        mat.MaterialClass='Glass' if 'Glass' in name else 'Metal' if 'Metal' in name else 'Fabric'
        scope=DB.Visual.AppearanceAssetEditScope(doc)
        a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color)
        scalar(a,'generic_glossiness',gloss)
        scalar(a,'generic_transparency',trans)
        scalar(a,'generic_refraction_index',1.5)
        scalar(a,'generic_reflectivity_at_0deg',.05)
        scalar(a,'generic_reflectivity_at_90deg',.4)
        scalar(a,'generic_self_illum_luminance',lum)
        if lum:
            set_color(a,DB.Visual.Generic.GenericSelfIllumFilterMap,(255,245,225))
            scalar(a,DB.Visual.Generic.GenericSelfIllumColorTemperature,2700.)
        scope.Commit(True)
        scope.Dispose()
        result[name]=mat
    return result

def preview(doc,name,eye,target,close=False,realistic=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id)
    v.Name=name
    forward=target.Subtract(eye).Normalize()
    up=DB.XYZ(0,0,-1)
    if abs(forward.DotProduct(up))>.99: up=DB.XYZ.BasisY
    right=forward.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,right.CrossProduct(forward).Normalize(),forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    v.Scale=1
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    if close:
        for cat in doc.OwnerFamily.FamilyCategory.SubCategories:
            if cat.Name=='Suspension Cord': v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ()
    box.Min=xyz(-115,-115,DROP-285 if close else .001)
    box.Max=xyz(115,115,DROP+5)
    v.SetSectionBox(box)
    v.IsSectionBoxActive=True
    return v

def export(doc,views):
    o=DB.ImageExportOptions()
    o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    o.FilePath=os.path.join(OUT,'Duo')
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG
    o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150
    o.ZoomType=DB.ZoomFitType.FitToPage
    o.PixelSize=1800
    doc.ExportImage(o)

try:
    app=__revit__.Application
    report['revit_version']=app.VersionNumber
    assert app.VersionNumber=='2025'
    checkpoint('create family')
    doc=app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    tx=DB.Transaction(doc,'Create Duo pendant')
    tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm=doc.FamilyManager
    fm.NewType('210 mm - White Opal - Warm Glow')
    mats=materials(doc,app)
    params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id)
        params[name]=p
    for name,value in [('Shade Diameter',210),('Shade Height',210),('Total Drop',DROP)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
        fm.SetFormula(p,str(value)+' mm')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Astro Lighting'),
                      (DB.BuiltInParameter.ALL_MODEL_MODEL,'Duo Pendant / Lightology 1561665'),
                      (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Matte white metal and opal glass; warm appearance glow; visualization only')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    cats={}
    for name in ['Upper Shade','Lower Glass','Canopy and Stem','Suspension Cord']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
    metal=params['Metal Finish']; glass=params['Opal Glass Finish']; cord=params['Cord Finish']
    h=DROP-210
    checkpoint('build revolved shells')
    # The drawing is two 210 x 105 mm stadium sections. Revolve the half profiles.
    upper=revolve(doc,'Upper metal shell with open top',
        [(48,h),(52.5,h),('arc',(105,h+52.5),(52.5,h+105)),(0,h+105),
         (0,h+102),(52.5,h+102),('arc',(102,h+52.5),(52.5,h+3)),(48,h+3)],metal,cats['Upper Shade'])
    lower=revolve(doc,'Opal glass shell',
        [(0,h+105),(52.5,h+105),('arc',(105,h+157.5),(52.5,h+210)),(0,h+210),
         (0,h+207),(52.5,h+207),('arc',(102,h+157.5),(52.5,h+108)),(0,h+108)],glass,cats['Lower Glass'])
    # Photo-derived canopy diameter 95, depth 24; stem diameter16 and visible height65.
    revolve(doc,'Ceiling canopy',[(0,0),(46.5,0),('arc',(47.56,.44),(48,1.5)),
        (48,22.5),('arc',(47.56,23.56),(46.5,24)),(0,24)],metal,cats['Canopy and Stem'])
    revolve(doc,'Hollow stem with cable entry',[(6,h-65),(8,h-65),(8,h+90),(0,h+90),(0,h-61),(6,h-61)],metal,cats['Canopy and Stem'])
    revolve(doc,'White suspension cord',[(0,23),(2,23),(2,h-61),(0,h-61)],cord,cats['Suspension Cord'])
    doc.Regenerate()
    views=[preview(doc,'Full Pendant',xyz(350,-800,DROP*.4),xyz(0,0,DROP*.5)),
           preview(doc,'Shade Front',xyz(0,-700,DROP-105),xyz(0,0,DROP-105),True),
           preview(doc,'Shade Oblique',xyz(330,-550,DROP-400),xyz(0,0,DROP-105),True),
           preview(doc,'Warm Material Review',xyz(330,-550,DROP-400),xyz(0,0,DROP-105),True,True)]
    tx.Commit(); tx=None
    checkpoint('save and export')
    opts=DB.SaveAsOptions(); opts.OverwriteExistingFile=True; opts.MaximumBackups=1; opts.PreviewViewId=views[0].Id
    doc.SaveAs(RFA,opts)
    report['export_error']=None
    try: export(doc,views)
    except Exception: report['export_error']=traceback.format_exc()
    doc.Close(False); docs.remove(doc)
    doc=app.OpenDocumentFile(RFA); docs.append(doc)
    report['reopened']=doc.IsFamilyDocument
    report['category']=doc.OwnerFamily.FamilyCategory.Name
    report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    b=bounds(forms)
    report['dimensions_mm']=[b[3]-b[0],b[4]-b[1],b[5]-b[2]]
    b=bounds([e for e in forms if e.Subcategory.Name in ['Upper Shade','Lower Glass']])
    report['shade_dimensions_mm']=[b[3]-b[0],b[4]-b[1],b[5]-b[2]]
    # Element boxes can omit extrema of tessellated revolved faces. Measure the
    # saved analytic shell intersections at the equator in both radial directions.
    report['display_bounds_dimensions_mm']=report['dimensions_mm'][:]
    widths=[]
    upper=next(e for e in forms if e.Subcategory.Name=='Upper Shade')
    solid=next(solids(upper.get_Geometry(DB.Options())))
    for start,end,index in [((-200,0,h+52.5),(200,0,h+52.5),0),((0,-200,h+52.5),(0,200,h+52.5),1)]:
        hits=solid.IntersectWithCurve(DB.Line.CreateBound(xyz(*start),xyz(*end)),DB.SolidCurveIntersectionOptions())
        points=[hits.GetCurveSegment(i).GetEndPoint(j) for i in range(hits.SegmentCount) for j in [0,1]]
        values=[(p.X if index==0 else p.Y)*304.8 for p in points]
        widths.append(max(values)-min(values))
    report['analytic_equator_diameters_mm']=widths
    report['dimensions_mm'][:2]=widths
    report['shade_dimensions_mm'][:2]=widths
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    m=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='Duo - Opal Glass Finish')
    a=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    report['saved_glow_luminance']=a.FindByName('generic_self_illum_luminance').Value
    checkpoint('ceiling face placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); docs.append(project)
    family=doc.LoadFamily(project)
    symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Test Duo on native overhead face'); tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    ft=DB.Floor.GetDefaultFloorType(project,False)
    loop=profile_loop(xyz(0,0,3000),DB.XYZ.BasisX,DB.XYZ.BasisY,[(-1500,-1500),(1500,-1500),(1500,1500),(-1500,1500)])
    floor=DB.Floor.Create(project,List[DB.CurveLoop]([loop]),ft,level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(3000/304.8)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetBottomFaces(floor)[0]
    face=floor.GetGeometryObjectFromReference(ref)
    point=face.Project(xyz(0,0,3000)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol)
    project.Regenerate()
    report['loaded_and_face_placed']=inst.Host is not None and inst.Host.Id==floor.Id
    report['placed_axis_z']=inst.GetTransform().BasisZ.Z
    report['material_tests']={}
    for name in params:
        p=symbol.LookupParameter(name); orig=p.AsElementId()
        alt=DB.Material.Create(project,'QA '+name); p.Set(alt); project.Regenerate()
        ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        report['material_tests'][name]=alt in ids or alt in list(inst.GetMaterialIds(False))
        p.Set(orig); project.Regenerate()
    tx.Commit(); tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    report['preview_files']=[n for n in os.listdir(OUT) if n.startswith('Duo -') and n.endswith('.png')]
    checkpoint('complete')
except Exception:
    report['error']=traceback.format_exc()
    checkpoint('failed at '+report.get('stage','start'))
finally:
    if tx is not None:
        try: tx.RollBack()
        except Exception: pass
    for d in reversed(docs):
        try: d.Close(False)
        except Exception: pass

