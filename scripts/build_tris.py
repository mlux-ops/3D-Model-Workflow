# -*- coding: utf-8 -*-
"""Independent Tris visualization family. Run in Revit 2025 via pyRevit CLI.
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
OUT = os.path.join(ROOT, 'output', 'tris')
RFA = os.path.join(OUT, 'Tris_3_Light_700BCTRS_Chrome_Unlit_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
TEXTURE = os.path.join(OUT, 'textures', 'Tris_Microdots_Color.png')
TRANSMISSION = os.path.join(OUT, 'textures', 'Tris_Microdots_Transmission.png')
report = {'rfa_path': RFA, 'texture_path': TEXTURE, 'transmission_path': TRANSMISSION}
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

def bitmap(asset,key,path):
    prop=asset.FindByName(key)
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.AddConnectedAsset('UnifiedBitmap')
    texture=prop.GetSingleConnectedAsset()
    texture.FindByName('unifiedbitmap_Bitmap').Value=path
    for axis in ['texture_RealWorldScaleX','texture_RealWorldScaleY']:
        size=texture.FindByName(axis)
        size.Value=DB.UnitUtils.ConvertFromInternalUnits(.4/12.0,size.GetUnitTypeId())
    for axis in ['texture_URepeat','texture_VRepeat']:
        repeat=texture.FindByName(axis)
        if repeat is not None: repeat.Value=True

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    chrome_source=next(a for a in assets if 'Chrome - mirror' in asset_label(a))
    generic_source=next(a for a in assets if a.FindByName('BaseSchema') is not None
                        and a.FindByName('BaseSchema').Value=='GenericSchema')
    chrome,_=clone_material(doc,'Tris - Polished Chrome',chrome_source,(190,195,200),0)
    chrome.MaterialClass='Metal'
    chrome.Shininess=128
    chrome.Smoothness=100
    result={'Metal Finish':chrome}
    for name,face,trans in [('Acrylic Edge Finish',False,.7),('Diffuser Finish',True,.5)]:
        mat,appearance=clone_material(doc,'Tris - '+('Etched Acrylic Unlit' if face else 'Clear Acrylic Edge'),generic_source,(239,242,235),25 if face else 55)
        mat.MaterialClass='Plastic'
        scope=DB.Visual.AppearanceAssetEditScope(doc)
        editable=scope.Start(appearance.Id)
        set_color(editable,'generic_diffuse',(240,243,236))
        scalar(editable,'generic_transparency',trans)
        scalar(editable,'generic_glossiness',.55 if face else .9)
        scalar(editable,'generic_refraction_index',1.49)
        scalar(editable,'generic_reflectivity_at_0deg',.08)
        scalar(editable,'generic_reflectivity_at_90deg',.5)
        scalar(editable,'generic_self_illum_luminance',0.0)
        if face:
            bitmap(editable,'generic_diffuse',TEXTURE)
            bitmap(editable,'generic_transparency',TRANSMISSION)
            scalar(editable,'generic_diffuse_image_fade',1.0)
            scalar(editable,'generic_transparency_image_fade',1.0)
        scope.Commit(True)
        scope.Dispose()
        result[name]=mat
    report['chrome_asset']=asset_label(chrome_source)
    report['unlit_luminance']=0
    return result

def preview(doc,name,eye,up,realistic=False):
    viewtype=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,viewtype.Id)
    v.Name=name
    target=xyz(0,0,1.5)
    forward=target.Subtract(eye).Normalize()
    right=forward.CrossProduct(up).Normalize()
    actualup=right.CrossProduct(forward).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,actualup,forward))
    v.DetailLevel=DB.ViewDetailLevel.Fine
    v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id):
            v.SetCategoryHidden(cat.Id,True)
    section=DB.BoundingBoxXYZ()
    section.Min=xyz(-14,-3,0.001)
    section.Max=xyz(14,3,4)
    v.SetSectionBox(section)
    v.IsSectionBoxActive=True
    return v

def export(doc,views):
    opts=DB.ImageExportOptions()
    opts.ExportRange=DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    opts.FilePath=os.path.join(OUT,'Tris')
    opts.HLRandWFViewsFileType=DB.ImageFileType.PNG
    opts.ShadowViewsFileType=DB.ImageFileType.PNG
    opts.ImageResolution=DB.ImageResolution.DPI_150
    opts.ZoomType=DB.ZoomFitType.FitToPage
    opts.PixelSize=2200
    doc.ExportImage(opts)

try:
    app=__revit__.Application
    report['revit_version']=app.VersionNumber
    report['revit_build']=app.VersionBuild
    assert app.VersionNumber=='2025'
    checkpoint('create materials')
    doc=app.NewFamilyDocument(TEMPLATE)
    docs.append(doc)
    tx=DB.Transaction(doc,'Build Tris visualization family')
    tx.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    vertical=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if vertical is not None and not vertical.IsReadOnly: vertical.Set(0)
    fm=doc.FamilyManager
    fm.NewType('25.6 in - Chrome - Unlit Acrylic')
    materials=make_materials(doc,app)
    parameters={}
    for name,material in materials.items():
        parameters[name]=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(parameters[name],material.Id)
    for name,value in [('Overall Width',25.6),('Projection',3.4),('Backplate Width',5.0),('Overall Height',4.5)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
        fm.SetFormula(p,str(value)+'"')
    for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Tech Lighting / Visual Comfort'),
                      (DB.BuiltInParameter.ALL_MODEL_MODEL,'Tris 3-Light / 700BCTRS'),
                      (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Visualization family; chrome and unlit acrylic; no MEP connectors or light source')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,value)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'Overall dimensions from supplied diagram. Panel thickness/spacing, channel profile, edge radii and microdots inferred from supplied photos. Unlit appearance approximation.')
    cats={}
    for name in ['Backplate','Chrome Rail','Acrylic Panels']:
        cats[name]=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,name)
        cats[name].Material=materials['Acrylic Edge Finish' if name=='Acrylic Panels' else 'Metal Finish']
    checkpoint('build geometry')
    metal=parameters['Metal Finish']
    edge=parameters['Acrylic Edge Finish']
    allforms=[]
    plate=form(doc,'Backplate',DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,
               rounded_rect(-2.5,-2.25,2.5,2.25,.1),.45,metal,cats['Backplate'])
    allforms.append(plate)
    # Two shallow longitudinal channels; no invented screws or internal LED parts.
    # The coordinates are depth Z and elevation Y in inches.
    railprofile=[(.45,-.38),(1.5,-.38),(1.5,-.10),(1.17,-.10),(1.17,.38),
                 (1.04,.38),(1.04,.22),(.86,.22),(.86,.38),(.70,.38),
                 (.70,.22),(.58,.22),(.58,.38),(.45,.38)]
    allforms.append(form(doc,'Continuous channel rail',xyz(-12.74,0,0),DB.XYZ.BasisZ,DB.XYZ.BasisY,DB.XYZ.BasisX,
                         railprofile,25.48,metal,cats['Chrome Rail']))
    for start in [-12.8,12.74]:
        allforms.append(form(doc,'Simple terminal cap',xyz(start,0,0),DB.XYZ.BasisZ,DB.XYZ.BasisY,DB.XYZ.BasisX,
                             rounded_rect(.45,-.38,1.5,.38,.05),.06,metal,cats['Chrome Rail']))
    panels=[]
    for center in [-9.7,0,9.7]:
        panel=form(doc,'Acrylic panel',xyz(0,-.09,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,DB.XYZ.BasisY,
                   rounded_rect(center-3.1,1.17,center+3.1,3.4,.055),.18,edge,cats['Acrylic Panels'])
        panels.append(panel)
        allforms.append(panel)
    doc.Regenerate()
    painted=0
    for panel in panels:
        for solid in solids(panel.get_Geometry(DB.Options())):
            for face in solid.Faces:
                if isinstance(face,DB.PlanarFace) and abs(face.FaceNormal.Y)>.99:
                    doc.Paint(panel.Id,face,parameters['Diffuser Finish'])
                    painted+=1
    report['texture_connected_faces']=painted
    views=[preview(doc,'Three Quarter',xyz(24,15,35),DB.XYZ.BasisY),
           preview(doc,'Front',xyz(0,0,35),DB.XYZ.BasisY),
           preview(doc,'Side',xyz(35,0,1.5),DB.XYZ.BasisY),
           preview(doc,'Top',xyz(0,35,1.5),DB.XYZ.BasisZ),
           preview(doc,'Material Review',xyz(16,19,35),DB.XYZ.BasisY,True)]
    tx.Commit()
    tx=None
    checkpoint('save and export')
    options=DB.SaveAsOptions()
    options.OverwriteExistingFile=True
    options.MaximumBackups=1
    options.PreviewViewId=views[0].Id
    doc.SaveAs(RFA,options)
    report['export_error']=None
    try: export(doc,views)
    except Exception: report['export_error']=traceback.format_exc()
    doc.Close(False)
    docs.remove(doc)
    checkpoint('reopen and verify geometry')
    doc=app.OpenDocumentFile(RFA)
    docs.append(doc)
    report['reopened']=doc.IsFamilyDocument
    report['category']=doc.OwnerFamily.FamilyCategory.Name
    report['placement']=str(doc.OwnerFamily.FamilyPlacementType)
    elements=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    b=bounds(elements)
    report['bounds_inches']=b
    report['dimensions_inches']=[b[3]-b[0],b[4]-b[1],b[5]-b[2]]
    panels=[e for e in elements if e.Subcategory.Name=='Acrylic Panels']
    report['panel_count']=len(panels)
    report['panel_bounds_inches']=[bounds([e]) for e in panels]
    report['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    report['solid_count']=len(elements)
    diffuser=next(m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name=='Tris - Etched Acrylic Unlit')
    da=doc.GetElement(diffuser.AppearanceAssetId).GetRenderingAsset()
    report['saved_unlit_luminance']=da.FindByName('generic_self_illum_luminance').Value
    report['saved_diffuse_texture']=da.FindByName('generic_diffuse').GetSingleConnectedAsset().FindByName('unifiedbitmap_Bitmap').Value
    checkpoint('verify native face placement')
    project=app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(project)
    family=doc.LoadFamily(project)
    symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    tx=DB.Transaction(project,'Tris placement and material acceptance')
    tx.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    walltype=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    wall=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-5,0,0),DB.XYZ(5,0,0)),walltype.Id,level.Id,8,0,False,False)
    symbol.Activate()
    project.Regenerate()
    ref=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]
    face=wall.GetGeometryObjectFromReference(ref)
    point=face.Project(DB.XYZ(0,0,4)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol)
    project.Regenerate()
    report['loaded_and_face_placed']=inst.Host is not None and inst.Host.Id==wall.Id
    report['mounting_normal_dot_host_normal']=inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)
    b=bounds([inst])
    report['placed_dimensions_inches']=[b[3]-b[0],b[4]-b[1],b[5]-b[2]]
    for name,key,painted in [('Metal Finish','metal_material_test',False),('Diffuser Finish','diffuser_material_test',True)]:
        param=symbol.LookupParameter(name)
        original=param.AsElementId()
        alternate=DB.Material.Create(project,'QA '+name)
        param.Set(alternate)
        project.Regenerate()
        # Paint inside a family can be reported as a native instance material,
        # unlike project-level paint. Inspect the actual geometry as well.
        native_ids=list(inst.GetMaterialIds(False))
        painted_ids=list(inst.GetMaterialIds(True))
        geometry_ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        report[key+'_diagnostics']={'alternate':str(alternate.Value),
            'native_ids':[str(i.Value) for i in native_ids],
            'painted_ids':[str(i.Value) for i in painted_ids],
            'geometry_ids':sorted(set(str(i.Value) for i in geometry_ids))}
        report[key]=alternate in native_ids or alternate in painted_ids or alternate in geometry_ids
        param.Set(original)
        project.Regenerate()
    tx.Commit()
    tx=None
    report['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    report['preview_files']=[os.path.join(OUT,n) for n in os.listdir(OUT) if n.startswith('Tris -') and n.endswith('.png')]
    checkpoint('complete')
except Exception:
    report['error']=traceback.format_exc()
    checkpoint('failed at '+report.get('stage','startup'))
finally:
    if tx is not None:
        try: tx.RollBack()
        except Exception: pass
    for doc in reversed(docs):
        try: doc.Close(False)
        except Exception: pass
