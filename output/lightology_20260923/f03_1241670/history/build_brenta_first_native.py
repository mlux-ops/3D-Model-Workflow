# -*- coding: utf-8 -*-
"""Build and validate the AERIN / Visual Comfort Brenta ARN 2473BZ-CG face-based Revit family."""
import os, json, math, traceback, datetime
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f03_1241670')
EVIDENCE = os.path.join(OUT, 'evidence')
SOURCE = os.path.join(OUT, 'source')
RFA = os.path.join(OUT, 'AERIN_Brenta_ARN2473BZ-CG_Bronze_R2025.rfa')
SOURCE_RFA = os.path.join(SOURCE, 'visualcomfort_arn2473_reference.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
REPORT_PATH = os.path.join(OUT, 'validation.json')
REPORT = {
    'fixture':'Brenta Single Wall Sconce',
    'manufacturer':'Visual Comfort Signature / AERIN',
    'requested_finish':'Bronze',
    'model':'ARN 2473BZ-CG',
    'lightology_spec':'VCG1241668',
    'lightology_assignment_url':'https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241669',
    'resolved_bronze_option_url':'https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241668',
    'nominal_dimensions_in':{'width':3.5,'height':18.5,'projection':3.75,'backplate_width':3.5,'backplate_height':5.25},
    'lamp':{'source':'Dedicated LED','cct_k':2700,'delivered_lumens':750},
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

def rounded_rect(x0,y0,x1,y1,r):
    k=1-math.sqrt(.5)
    return [(x0+r,y0),(x1-r,y0),('arc',(x1-r*k,y0+r*k),(x1,y0+r)),
            (x1,y1-r),('arc',(x1-r*k,y1-r*k),(x1-r,y1)),
            (x0+r,y1),('arc',(x0+r*k,y1-r*k),(x0,y1-r)),
            (x0,y0+r),('arc',(x0+r*k,y0+r*k),(x0+r,y0))]

def add_solid(doc,name,solid,param,subcategory):
    e=DB.FreeFormElement.Create(doc,solid); e.Subcategory=subcategory
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),param)
    REPORT.setdefault('generated_parts',[]).append({'name':name,'id':str(e.Id.Value)})
    return e

def extrude(doc,name,origin,u,v,normal,profile,length,param,subcategory):
    loop=profile_loop(origin,u,v,profile)
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),normal,length/12.0)
    return add_solid(doc,name,solid,param,subcategory)

def revolved(doc,name,origin,axis,points,param,subcategory):
    radial=DB.XYZ.BasisX if abs(axis.Z)>.99 else DB.XYZ.BasisZ
    radial=radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop=profile_loop(origin,radial,axis,points)
    frame=DB.Frame(origin,radial,axis.CrossProduct(radial),axis)
    solid=DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([loop]),0,2*math.pi)
    return add_solid(doc,name,solid,param,subcategory)

def cylinder(doc,name,origin,axis,r,start,end,param,subcategory,rounding=0):
    if rounding:
        q=rounding; k=1-math.sqrt(.5)
        pts=[(0,start),(r-q,start),('arc',(r-q*k,start+q*k),(r,start+q)),
             (r,end-q),('arc',(r-q*k,end-q*k),(r-q,end)),(0,end)]
    else: pts=[(0,start),(r,start),(r,end),(0,end)]
    return revolved(doc,name,origin,axis,pts,param,subcategory)

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
        ('Bronze Finish',(61,49,39),0,.42,.26,0),
        ('Clear Glass Finish',(236,239,235),82,.92,.07,0),
        ('2700K Diffuser Finish',(250,235,210),10,.35,.05,140)
    ]
    for pname,color,trans,gloss,refl,illum in specs:
        mat,appearance=clone_material(doc,'Brenta - '+pname,base,color,trans)
        scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
        set_color(a,'generic_diffuse',color); scalar(a,'generic_glossiness',gloss)
        scalar(a,'generic_transparency',trans/100.0); scalar(a,'generic_reflectivity_at_0deg',refl)
        scalar(a,'generic_reflectivity_at_90deg',.75 if 'Glass' in pname else .45)
        scalar(a,'generic_refraction_index',1.52 if 'Glass' in pname else 1.0)
        scalar(a,'generic_self_illum_luminance',illum)
        if illum:
            set_color(a,DB.Visual.Generic.GenericSelfIllumFilterMap,(255,236,210))
            scalar(a,DB.Visual.Generic.GenericSelfIllumColorTemperature,2700.0)
        scope.Commit(True); scope.Dispose()
        mat.MaterialClass='Metal' if 'Bronze' in pname else ('Glass' if 'Glass' in pname else 'Plastic')
        result[pname]=mat
    return result

def inspect_source(app):
    if not os.path.isfile(SOURCE_RFA):
        REPORT['source_rfa_inspection']={'exists':False}; return
    d=app.OpenDocumentFile(SOURCE_RFA); DOCS.append(d)
    rec={'exists':True,'title':d.Title,'is_family':d.IsFamilyDocument,'warnings':[w.GetDescriptionText() for w in d.GetWarnings()]}
    try:
        rec['placement']=str(d.OwnerFamily.FamilyPlacementType)
        rec['category']=d.OwnerFamily.FamilyCategory.Name
    except Exception: pass
    opt=DB.Options(); opt.IncludeNonVisibleObjects=True; opt.DetailLevel=DB.ViewDetailLevel.Fine
    rows=[]
    for e in DB.FilteredElementCollector(d).WhereElementIsNotElementType():
        try: g=e.get_Geometry(opt)
        except Exception: continue
        if g is None: continue
        for s in solids(g):
            b=s.GetBoundingBox()
            rows.append({'element_id':str(e.Id.Value),'name':DB.Element.Name.GetValue(e),
                         'category':e.Category.Name if e.Category else None,
                         'bbox_local_ft':[b.Min.X,b.Min.Y,b.Min.Z,b.Max.X,b.Max.Y,b.Max.Z],
                         'volume_ft3':s.Volume})
    rec['solid_count']=len(rows); rec['solid_samples']=rows[:80]
    REPORT['source_rfa_inspection']=rec
    DOCS.remove(d); d.Close(False)

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
    box=DB.BoundingBoxXYZ(); box.Min=xyz(-4,-11,-.1); box.Max=xyz(4,11,4.2); v.SetSectionBox(box); v.IsSectionBoxActive=True
    return v

def export_views(doc,views,prefix):
    o=DB.ImageExportOptions(); o.ExportRange=DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views])); o.FilePath=os.path.join(EVIDENCE,prefix)
    o.HLRandWFViewsFileType=DB.ImageFileType.PNG; o.ShadowViewsFileType=DB.ImageFileType.PNG
    o.ImageResolution=DB.ImageResolution.DPI_150; o.ZoomType=DB.ZoomFitType.FitToPage; o.PixelSize=1600
    doc.ExportImage(o)

def measure_instance(inst):
    b=inst.get_BoundingBox(None)
    return {'width':(b.Max.X-b.Min.X)*12,'height':(b.Max.Z-b.Min.Z)*12,'depth':(b.Max.Y-b.Min.Y)*12,
            'bbox_ft':[b.Min.X,b.Min.Y,b.Min.Z,b.Max.X,b.Max.Y,b.Max.Z]}

def hosted_view(project,inst):
    vt=next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
    v=DB.View3D.CreateIsometric(project,vt.Id); v.Name='Brenta Hosted Oblique'; v.DisplayStyle=DB.DisplayStyle.Realistic; v.DetailLevel=DB.ViewDetailLevel.Fine
    b=inst.get_BoundingBox(None); center=(b.Min+b.Max)*0.5
    eye=center.Add(DB.XYZ(7,-10,2)); f=center.Subtract(eye).Normalize(); up=DB.XYZ.BasisZ
    right=f.CrossProduct(up).Normalize(); trueup=right.CrossProduct(f).Normalize(); v.SetOrientation(DB.ViewOrientation3D(eye,trueup,f))
    sb=DB.BoundingBoxXYZ(); sb.Min=b.Min-DB.XYZ(2,2,2); sb.Max=b.Max+DB.XYZ(2,2,2); v.SetSectionBox(sb); v.IsSectionBoxActive=True
    return v

try:
    app=__revit__.Application; REPORT['revit_version']=app.VersionNumber; REPORT['revit_build']=app.VersionBuild
    checkpoint('inspect-source')
    if not app.VersionNumber.startswith('2025'): raise RuntimeError('Revit 2025 required')
    if not os.path.isfile(TEMPLATE): raise RuntimeError('Face-based template missing: '+TEMPLATE)
    inspect_source(app)

    checkpoint('build-family')
    doc=app.NewFamilyDocument(TEMPLATE); DOCS.append(doc)
    TX=DB.Transaction(doc,'Build Brenta ARN 2473BZ-CG'); TX.Start()
    doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_LightingFixtures)
    av=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if av: av.Set(0)
    fm=doc.FamilyManager; fm.NewType('Bronze - White Glass - 2700K')
    mats=make_materials(doc,app); params={}
    for name,mat in mats.items():
        p=fm.AddParameter(name,DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False); fm.Set(p,mat.Id); params[name]=p
    for name,val in [('Overall Width',3.5),('Overall Height',18.5),('Projection',3.75),('Backplate Width',3.5),('Backplate Height',5.25)]:
        p=fm.AddParameter(name,DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,False); fm.SetFormula(p,str(val)+' in')
    for bip,val in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,'Visual Comfort Signature / AERIN'),
                    (DB.BuiltInParameter.ALL_MODEL_MODEL,'ARN 2473BZ-CG'),
                    (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,'Brenta Single Wall Sconce; Bronze with white glass; 2700K dedicated LED; face-based visualization family')]:
        p=fm.get_Parameter(bip)
        if p is not None: fm.Set(p,val)
    note=fm.AddParameter('Model Accuracy Notes',DB.GroupTypeId.IdentityData,DB.SpecTypeId.String.Text,False)
    fm.Set(note,'Nominal 3.5 W x 18.5 H x 3.75 projection; 3.5 x 5.25 rectangular backplate from Visual Comfort. Glass tube diameter, sleeve diameter, backplate thickness and standoff are photo-derived/inferred; modeled for faithful visualization. Mountable vertically or horizontally by rotating the placed instance. No MEP connector or photometric data.')
    cats={n:doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,n) for n in ['Backplate','Bronze Housing','Clear Glass','Warm Diffuser']}
    bronze=params['Bronze Finish']; glass=params['Clear Glass Finish']; diffuser=params['2700K Diffuser Finish']

    # Wall plane is XY at Z=0; local X = width, Y = fixture vertical, Z = projection away from host.
    extrude(doc,'3.5 x 5.25 rectangular backplate',DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,
            rounded_rect(-1.75,-2.625,1.75,2.625,.05),.18,bronze,cats['Backplate'])
    extrude(doc,'Central standoff',xyz(0,0,.18),DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,
            rounded_rect(-.62,-1.70,.62,1.70,.04),1.58,bronze,cats['Bronze Housing'])
    # Sleeve front reaches exactly 3.75 in projection: center Z 2.75 + radius 1.00.
    cylinder(doc,'Central bronze sleeve',xyz(0,0,2.75),DB.XYZ.BasisY,1.00,-1.75,1.75,bronze,cats['Bronze Housing'],.06)
    # Two elongated clear glass cylinders, with warm-white internal diffusers.
    for tag,a,b in [('Upper',1.62,9.25),('Lower',-9.25,-1.62)]:
        cylinder(doc,tag+' clear glass tube',xyz(0,0,2.75),DB.XYZ.BasisY,.875,a,b,glass,cats['Clear Glass'],.08)
        ia=a+.12 if a>0 else a+.12; ib=b-.12 if b>0 else b-.12
        cylinder(doc,tag+' 2700K diffuser',xyz(0,0,2.75),DB.XYZ.BasisY,.68,ia,ib,diffuser,cats['Warm Diffuser'],.06)
    doc.Regenerate()
    elems=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement)); REPORT['family_bounds_in']=elem_bounds(elems)
    views=[preview(doc,'Brenta Front',xyz(0,0,36),xyz(0,0,2.2),False),
           preview(doc,'Brenta Side',xyz(22,0,2.0),xyz(0,0,2.0),False),
           preview(doc,'Brenta Oblique',xyz(14,5,28),xyz(0,0,2.0),False),
           preview(doc,'Brenta Material',xyz(12,4,25),xyz(0,0,2.2),True)]
    TX.Commit(); TX=None
    so=DB.SaveAsOptions(); so.OverwriteExistingFile=True; so.MaximumBackups=1; so.PreviewViewId=views[2].Id
    doc.SaveAs(RFA,so); export_views(doc,views,'Brenta')
    REPORT['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    DOCS.remove(doc); doc.Close(False)

    checkpoint('reopen-validate')
    reopened=app.OpenDocumentFile(RFA); DOCS.append(reopened)
    REPORT['reopened']=reopened.IsFamilyDocument; REPORT['category']=reopened.OwnerFamily.FamilyCategory.Name
    REPORT['placement']=str(reopened.OwnerFamily.FamilyPlacementType)
    REPORT['reopened_warnings']=[w.GetDescriptionText() for w in reopened.GetWarnings()]
    project=app.NewProjectDocument(DB.UnitSystem.Imperial); DOCS.append(project)
    family=reopened.LoadFamily(project); symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
    TX=DB.Transaction(project,'Host Brenta on wall face'); TX.Start()
    level=next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)),None)
    if level is None: level=DB.Level.Create(project,0)
    wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    wall=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,10,0,False,False)
    symbol.Activate(); project.Regenerate()
    ref=DB.HostObjectUtils.GetSideFaces(wall,DB.ShellLayerType.Exterior)[0]; face=wall.GetGeometryObjectFromReference(ref)
    point=face.Project(DB.XYZ(0,0,5)).XYZPoint
    inst=project.Create.NewFamilyInstance(ref,point,DB.XYZ.BasisX,symbol); project.Regenerate()
    REPORT['host_validation']={'host_id':str(inst.Host.Id.Value) if inst.Host else None,
                               'wall_id':str(wall.Id.Value),'hostface_present':inst.HostFace is not None,
                               'face_based_host':bool(inst.Host is not None and inst.Host.Id==wall.Id and inst.HostFace is not None),
                               'transform_basis_z_dot_face_normal':inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)}
    b=inst.get_BoundingBox(None)
    dims=sorted([(b.Max.X-b.Min.X)*12,(b.Max.Y-b.Min.Y)*12,(b.Max.Z-b.Min.Z)*12])
    REPORT['placed_bbox_dimensions_sorted_in']=dims
    REPORT['dimension_checks']={'height_18_5':abs(max(dims)-18.5)<.03,
                                'width_3_5':any(abs(x-3.5)<.03 for x in dims),
                                'projection_3_75':any(abs(x-3.75)<.03 for x in dims)}
    REPORT['material_tests']={}
    for pname in ['Bronze Finish','Clear Glass Finish','2700K Diffuser Finish']:
        p=symbol.LookupParameter(pname); old=p.AsElementId(); alt=DB.Material.Create(project,'QA '+pname); p.Set(alt); project.Regenerate()
        ids=[f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        REPORT['material_tests'][pname]={'writable':not p.IsReadOnly,'faces':len(ids),'substitute_reached_geometry':alt in ids}
        p.Set(old); project.Regenerate()
    hv=hosted_view(project,inst)
    TX.Commit(); TX=None
    export_views(project,[hv],'Brenta_Hosted')
    REPORT['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
    REPORT['evidence_files']=sorted(os.listdir(EVIDENCE))
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
    REPORT['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z'; checkpoint('complete' if REPORT['technical_pass'] else 'gates-failed')
    if not REPORT['technical_pass']: raise RuntimeError('Gate failures: '+json.dumps([k for k,v in gates.items() if not v]))
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
