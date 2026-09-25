# -*- coding: utf-8 -*-
"""Build and validate the FLOS IC C/W1 Brass / Opal face-based Revit 2025 family."""
import os, json, math, traceback, datetime
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f02_231180')
EVIDENCE = os.path.join(OUT, 'evidence')
RFA = os.path.join(OUT, 'FLOS_IC_CW1_FU317859_Brass_Opal_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
REPORT_PATH = os.path.join(OUT, 'validation.json')
REPORT = {
    'fixture':'IC C/W1 Wall / Ceiling Light',
    'designer':'Michael Anastassiades',
    'manufacturer':'FLOS',
    'requested_finish':'Brass',
    'color':'Opal',
    'model':'FU317859',
    'lightology_spec':'FLO231180',
    'assignment_url':'https://www.lightology.com/index.php?module=prod_detail&prod_id=231180',
    'nominal_dimensions_in':{'width':7.9,'height':8.5,'projection':11.0},
    'lamp':{'source':'1 x JCD/G9','wattage_w':60,'voltage_v':120},
    'rfa_path':RFA,
    'started_utc':datetime.datetime.utcnow().isoformat()+'Z'
}
DOCS=[]
TX=None

def checkpoint(stage):
    REPORT['stage']=stage
    if not os.path.isdir(OUT): os.makedirs(OUT)
    if not os.path.isdir(EVIDENCE): os.makedirs(EVIDENCE)
    with open(REPORT_PATH,'w') as f: json.dump(REPORT,f,indent=2,default=str)

def xyz(x,y,z): return DB.XYZ(x/12.0,y/12.0,z/12.0)

def solids(geometry):
    for item in geometry:
        if isinstance(item,DB.Solid) and item.Volume>1e-12:
            yield item
        elif isinstance(item,DB.GeometryInstance):
            for s in solids(item.GetInstanceGeometry()): yield s

def elem_bounds(elements):
    boxes=[e.get_BoundingBox(None) for e in elements if e.get_BoundingBox(None)]
    return [min(b.Min.X for b in boxes)*12,min(b.Min.Y for b in boxes)*12,min(b.Min.Z for b in boxes)*12,
            max(b.Max.X for b in boxes)*12,max(b.Max.Y for b in boxes)*12,max(b.Max.Z for b in boxes)*12]

def profile_loop(origin,u,v,points):
    def p(pair): return origin.Add(u.Multiply(pair[0]/12.0)).Add(v.Multiply(pair[1]/12.0))
    loop=DB.CurveLoop(); cur=points[0]
    for item in points[1:]:
        if len(item)==3 and item[0]=='arc':
            mid,end=item[1],item[2]; loop.Append(DB.Arc.Create(p(cur),p(end),p(mid)))
        else:
            end=item; loop.Append(DB.Line.CreateBound(p(cur),p(end)))
        cur=end
    if cur!=points[0]: loop.Append(DB.Line.CreateBound(p(cur),p(points[0])))
    return loop

def add_solid(doc,name,solid,param,subcategory):
    e=DB.FreeFormElement.Create(doc,solid); e.Subcategory=subcategory
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    REPORT.setdefault('generated_parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

def revolved(doc,name,origin,axis,points,param,subcategory):
    radial=DB.XYZ.BasisX if abs(axis.Z)>.99 else DB.XYZ.BasisZ
    radial=radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop=profile_loop(origin,radial,axis,points)
    frame=DB.Frame(origin,radial,axis.CrossProduct(radial),axis)
    solid=DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame,List[DB.CurveLoop]([loop]),0,2*math.pi)
    return add_solid(doc,name,solid,param,subcategory)

def cylinder(doc,name,origin,axis,r,start,end,param,subcategory,rounding=0):
    if rounding:
        q=min(rounding,r*.7,(end-start)*.2); k=1-math.sqrt(.5)
        pts=[(0,start),(r-q,start),('arc',(r-q*k,start+q*k),(r,start+q)),
             (r,end-q),('arc',(r-q*k,end-q*k),(r-q,end)),(0,end)]
    else:
        pts=[(0,start),(r,start),(r,end),(0,end)]
    return revolved(doc,name,origin,axis,pts,param,subcategory)

def sphere(doc,name,center,r,param,subcategory):
    pts=[(0,-r),(0,r),('arc',(r,0),(0,-r))]
    return revolved(doc,name,center,DB.XYZ.BasisY,pts,param,subcategory)

def clone_material(doc,name,asset,color,transparency):
    appearance=DB.AppearanceAssetElement.Create(doc,name,asset)
    mat=doc.GetElement(DB.Material.Create(doc,name)); mat.AppearanceAssetId=appearance.Id
    mat.Color=DB.Color(*color); mat.Transparency=transparency
    return mat,appearance

def set_color(asset,key,color):
    prop=asset.FindByName(key)
    if prop is None: return False
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color)); return True

def scalar(asset,key,value):
    prop=asset.FindByName(key)
    if prop is None: return False
    if prop.NumberOfConnectedProperties: prop.RemoveConnectedAsset()
    prop.Value=value; return True

def make_materials(doc,app):
    assets=list(app.GetAssets(DB.Visual.AssetType.Appearance))
    base=next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value=='GenericSchema')
    result={}
    specs=[
        ('Brass Finish',(171,132,63),0,.55,.38,0),
        ('Opal Glass Finish',(247,244,235),16,.38,.08,25)
    ]
    for pname,color,trans,gloss,refl,illum in specs:
        mat,appearance=clone_material(doc,'FLOS IC - '+pname,base,color,trans)
        scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color); scalar(a,'generic_glossiness',gloss)
        scalar(a,'generic_transparency',trans/100.0); scalar(a,'generic_reflectivity_at_0deg',refl)
        scalar(a,'generic_reflectivity_at_90deg',.55 if 'Brass' in pname else .35)
        scalar(a,'generic_refraction_index',1.48 if 'Opal' in pname else 1.0)
        scalar(a,'generic_self_illum_luminance',illum)
        if illum:
            set_color(a,DB.Visual.Generic.GenericSelfIllumFilterMap,(255,247,230))
            scalar(a,DB.Visual.Generic.GenericSelfIllumColorTemperature,3000.0)
        scope.Commit(True); scope.Dispose()
        mat.MaterialClass='Metal' if 'Brass' in pname else 'Glass'
        result[pname]=mat
    return result

def preview(doc,name,eye,target,realistic=False):
    vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(doc,vt.Id); v.Name=name
    forward=target.Subtract(eye).Normalize(); up=DB.XYZ.BasisY
    if abs(forward.DotProduct(up))>.99: up=DB.XYZ.BasisZ
    right=forward.CrossProduct(up).Normalize(); trueup=right.CrossProduct(forward).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,trueup,forward)); v.DetailLevel=DB.ViewDetailLevel.Fine; v.Scale=1
    v.DisplayStyle=DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id!=doc.OwnerFamily.FamilyCategory.Id and v.CanCategoryBeHidden(cat.Id): v.SetCategoryHidden(cat.Id,True)
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-5,-1,-.2); box.Max=xyz(5,9.2,11.5)
    v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export_views(doc,views,prefix):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(EVIDENCE,prefix)
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def hosted_view(project,inst):
    vt=next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(project,vt.Id); v.Name='FLOS IC Hosted Oblique'
    v.DisplayStyle=DB.DisplayStyle.Realistic; v.DetailLevel=DB.ViewDetailLevel.Fine
    b=inst.get_BoundingBox(None); center=(b.Min+b.Max)*0.5
    eye=center.Add(DB.XYZ(8,-10,5)); f=center.Subtract(eye).Normalize(); up=DB.XYZ.BasisZ
    right=f.CrossProduct(up).Normalize(); trueup=right.CrossProduct(f).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(eye,trueup,f))
    sb=DB.BoundingBoxXYZ(); sb.Min=b.Min-DB.XYZ(2,2,2); sb.Max=b.Max+DB.XYZ(2,2,2)
    v.SetSectionBox(sb); v.IsSectionBoxActive=True
    return v

try:
    app=__revit__.Application; REPORT['revit_version']=app.VersionNumber; REPORT['revit_build']=app.VersionBuild
    checkpoint('build-family')
    if not app.VersionNumber.startswith('2025'): raise RuntimeError('Revit 2025 required')
    if not os.path.isfile(TEMPLATE): raise RuntimeError('Face-based template missing: '+TEMPLATE)

    doc=app.NewFamilyDocument(TEMPLATE); DOCS.append(doc)
    TX=DB.Transaction(doc,'Build FLOS IC C/W1 FU317859'); TX.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    av=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if av: av.Set(0)
    fm=doc.FamilyManager; fm.NewType('Brass - Opal')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        fm.Set(p,mat.Id); params[name]=p
    for name,val in [('Overall Width',7.9),('Overall Height',8.5),('Projection',11.0),('Globe Diameter',7.9)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False)
        fm.SetFormula(p,str(val)+' in')
    for bip,val in [
        (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'FLOS'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL,'FU317859 / IC C-W1'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'IC C/W1 Wall / Ceiling Light by Michael Anastassiades; Brass / Opal; face-based visualization family')
    ]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,val)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'Lightology drawing dimensions are authoritative: 7.9 in globe diameter, 8.5 in overall height, 11 in projection and 4.3 in wall-plate diameter. Brass tube radius, bell-plate depth/profile, globe depth center, elbow radius and small top contact cap are image-derived/inferred to match the preserved 231180 side reference. Fixed visualization geometry; no MEP connector or photometric source.')

    cats={n:doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,n) for n in ['Brass Frame','Backplate','Opal Globe']}
    brass=params['Brass Finish']; opal=params['Opal Glass Finish']

    sphere(doc,'7.9 inch opal globe',xyz(0,3.95,6.95),3.95,opal,cats['Opal Globe'])

    plate_profile=[(0,0),(2.15,0),('arc',(2.15,.13),(2.02,.30)),
                   (1.50,.68),('arc',(.92,.98),(.42,1.05)),(0,1.05)]
    revolved(doc,'Brass bell backplate',xyz(0,4.25,0),DB.XYZ.BasisZ,plate_profile,brass,cats['Backplate'])

    tube_r=.28
    cylinder(doc,'Vertical brass riser',xyz(0,0,1.05),DB.XYZ.BasisY,tube_r,.28,8.22,brass,cats['Brass Frame'],.06)
    sphere(doc,'Rounded brass elbow',xyz(0,8.22,1.05),tube_r,brass,cats['Brass Frame'])
    cylinder(doc,'Horizontal brass rail',xyz(0,8.22,0),DB.XYZ.BasisZ,tube_r,1.05,11.0,brass,cats['Brass Frame'],.06)
    cylinder(doc,'Globe contact cap',xyz(0,0,6.95),DB.XYZ.BasisY,.44,7.86,7.98,brass,cats['Brass Frame'],.03)

    doc.Regenerate()
    elems=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    REPORT['family_bounds_in']=elem_bounds(elems)
    views=[
        preview(doc,'FLOS IC Front',xyz(0,4,28),xyz(0,4,6),False),
        preview(doc,'FLOS IC Side',xyz(24,4,6),xyz(0,4,6),False),
        preview(doc,'FLOS IC Oblique',xyz(15,-5,22),xyz(0,4,6),False),
        preview(doc,'FLOS IC Material',xyz(14,-4,20),xyz(0,4,6),True)
    ]
    TX.Commit(); TX=None
    so=DB.SaveAsOptions(); so.OverwriteExistingFile=True; so.MaximumBackups=1; so.PreviewViewId=views[2].Id
    doc.SaveAs(RFA,so); export_views(doc,views,'FLOS_IC')
    REPORT['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    DOCS.remove(doc); doc.Close(False)

    checkpoint('reopen-validate')
    reopened=app.OpenDocumentFile(RFA); DOCS.append(reopened)
    REPORT['reopened']=reopened.IsFamilyDocument
    REPORT['category']=reopened.OwnerFamily.FamilyCategory.Name
    REPORT['placement']=str(reopened.OwnerFamily.FamilyPlacementType)
    REPORT['reopened_warnings']=[w.GetDescriptionText() for w in reopened.GetWarnings()]

    project=app.NewProjectDocument(DB.UnitSystem.Imperial); DOCS.append(project)
    family=reopened.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    TX=DB.Transaction(project,'Host FLOS IC on wall face'); TX.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    wall=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,12,0,False,False)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]
    face=wall.GetGeometryObjectFromReference(ref); point=face.Project(DB.XYZ(0,0,5)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol); project.Regenerate()
    REPORT['host_validation']={
        'host_id':str(inst.Host.Id.Value) if inst.Host else None,
        'wall_id':str(wall.Id.Value),
        'hostface_present':inst.HostFace is not None,
        'face_based_host':bool(inst.Host is not None and inst.Host.Id==wall.Id and inst.HostFace is not None),
        'transform_basis_z_dot_face_normal':inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)
    }
    b=inst.get_BoundingBox(None)
    dims=sorted([(b.Max.X-b.Min.X)*12,(b.Max.Y-b.Min.Y)*12,(b.Max.Z-b.Min.Z)*12])
    REPORT['placed_bbox_dimensions_sorted_in']=dims
    REPORT['dimension_checks']={
        'width_7_9':any(abs(x-7.9)<.04 for x in dims),
        'height_8_5':any(abs(x-8.5)<.04 for x in dims),
        'projection_11':any(abs(x-11.0)<.04 for x in dims)
    }
    REPORT['material_tests']={}
    for pname in ['Brass Finish','Opal Glass Finish']:
        p=symbol.LookupParameter(pname); old=p.AsElementId()
        alt=DB.Material.Create(project,'QA '+pname); p.Set(alt); project.Regenerate()
        ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        REPORT['material_tests'][pname]={
            'writable':not p.IsReadOnly,
            'faces':len(ids),
            'substitute_reached_geometry':alt in ids
        }
        p.Set(old); project.Regenerate()
    hv=hosted_view(project,inst)
    TX.Commit(); TX=None
    export_views(project,[hv],'FLOS_IC_Hosted')
    REPORT['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    REPORT['evidence_files']=sorted(os.listdir(EVIDENCE))
    REPORT['rfa_bytes']=os.path.getsize(RFA)
    REPORT['rfa_mtime_utc']=datetime.datetime.utcfromtimestamp(os.path.getmtime(RFA)).isoformat()+'Z'
    gates={
        'reopen':REPORT['reopened'],
        'lighting_fixture_category':REPORT['category']=='Lighting Fixtures',
        'face_based_placement':'WorkPlaneBased' in REPORT['placement'] or 'Face' in REPORT['placement'],
        'actual_host_face':REPORT['host_validation']['face_based_host'],
        'nominal_dimensions':all(REPORT['dimension_checks'].values()),
        'material_substitution_reaches_geometry':all(v['substitute_reached_geometry'] for v in REPORT['material_tests'].values()),
        'zero_warnings':not REPORT['family_warnings'] and not REPORT['reopened_warnings'] and not REPORT['project_warnings'],
        'visual_exports':len(REPORT['evidence_files'])>=5
    }
    REPORT['gates']=gates; REPORT['technical_pass']=all(gates.values())
    REPORT['visual_verdict']='PENDING SELF REVIEW AND PRIME REVIEW'
    REPORT['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z'
    checkpoint('complete' if REPORT['technical_pass'] else 'gates-failed')
    if not REPORT['technical_pass']:
        raise RuntimeError('Gate failures: '+json.dumps([k for k,v in gates.items() if not v]))
except Exception:
    REPORT['error']=traceback.format_exc(); REPORT['technical_pass']=False
    try: checkpoint('failed')
    except Exception: pass
    raise
finally:
    if TX:
        try: TX.RollBack()
        except Exception: pass
    for d in reversed(DOCS):
        try: d.Close(False)
        except Exception: pass
