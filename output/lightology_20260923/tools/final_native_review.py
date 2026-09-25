# -*- coding: utf-8 -*-
"""Independent read-only review of final saved RFAs in fresh native host projects."""
import os,sys,json,math,hashlib,datetime,traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'tools'))
from native_fixture_support import NativeFixture,xyz,loop,all_solids,measured_geometry_bounds
EXPECTED={'f01':(None,3000),'f02':([7.9,8.5,11.],None),'f03':([3.5,18.5,3.75],2700),'f04':([9.84,9.84,37.82],2700),
'f05':([5.,5.,3.3],3000),'f06':([11.,11.,1.5],3000),'f07':([8.,7.63,5.5],None),'f08':([48.,13.375,15.875],None),
'f09':([4.,16.33,14.17],None),'f10':([18.25,18.25,2.75],2700),'f11':([8.66,8.3,19.7],3000),'f12':([5.,12.9,6.7],None)}
REVIEW_KEYS=globals().get('REVIEW_KEYS')
REPORT_STEM='native_final_review_patch' if REVIEW_KEYS else 'native_final_review'
COUNT=dict((k,2 if k in ['f05','f07'] else 1) for k in EXPECTED if not REVIEW_KEYS or k in REVIEW_KEYS)
index=json.load(open(os.path.join(ROOT,'native_mesh_index.json')))
summary={'started_utc':datetime.datetime.utcnow().isoformat()+'Z','revit_version':__revit__.Application.VersionNumber,'files':[],'all_pass':False}
app=__revit__.Application

def material_data(doc,mat):
    d={'name':mat.Name,'rgb':[int(mat.Color.Red),int(mat.Color.Green),int(mat.Color.Blue)],'textures':[]}
    ae=doc.GetElement(mat.AppearanceAssetId)
    if ae is None:raise RuntimeError('Material has no native appearance: '+mat.Name)
    asset=ae.GetRenderingAsset()
    for key in ['generic_diffuse','generic_transparency','generic_glossiness','generic_self_illum_color_temperature','generic_self_illum_luminance','generic_self_illum_filter_map']:
        p=asset.FindByName(key)
        if p is not None:
            try:value=p.Value
            except Exception:value=[float(v) for v in p.GetValueAsDoubles()]
            d[key]=value
            if p.NumberOfConnectedProperties:
                connected=p.GetSingleConnectedAsset();bitmap=connected.FindByName('unifiedbitmap_Bitmap')
                if bitmap is not None:
                    path=bitmap.Value;d['textures'].append({'path':path,'exists':os.path.isfile(path),'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest() if os.path.isfile(path) else None})
    return d

for source in index:
    if REVIEW_KEYS and source['folder'][:3] not in REVIEW_KEYS:continue
    row={'fixture':source['folder'][:3],'name':source['name'],'rfa':source['rfa'],'pass':False};doc=project=tx=None
    try:
        key=row['fixture'];expected,cct=EXPECTED[key]
        row['sha256']=hashlib.sha256(open(row['rfa'],'rb').read()).hexdigest()
        row['mesh_source_hash_matches']=row['sha256']==source['sha256']
        doc=app.OpenDocumentFile(row['rfa']);row['reopened']=doc.IsFamilyDocument
        row['category']=doc.OwnerFamily.FamilyCategory.Name;row['placement']=str(doc.OwnerFamily.FamilyPlacementType)
        row['family_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        row['type_names']=[t.Name for t in doc.FamilyManager.Types]
        host_behavior=doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR)
        row['hosting_behavior']=host_behavior.AsInteger() if host_behavior else None
        forms=list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
        bounds=measured_geometry_bounds(forms);dimensions=[bounds[i+3]-bounds[i] for i in range(3)]
        row['bounds_inches']=bounds;row['dimensions_inches']=dimensions;row['solid_count']=len(forms)
        if key=='f01':
            points=[p for form in forms for solid in all_solids(form.get_Geometry(DB.Options())) for face in solid.Faces for p in face.Triangulate(1.).Vertices]
            sweep=2*max(math.sqrt(p.X*p.X+p.Y*p.Y) for p in points)*12;row['fan_sweep_inches']=sweep
            dimensions_pass=abs(sweep-52)<.025 and abs(dimensions[2]-13.8)<.025
        else:dimensions_pass=all(abs(a-b)<.05 for a,b in zip(dimensions,expected))
        names={}
        for form in forms:
            p=form.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
            fp=doc.FamilyManager.GetAssociatedFamilyParameter(p) if p else None
            if fp is not None:names[fp.Definition.Name]=fp
        row['material_parameter_names']=sorted(names)
        family_materials={}
        for name,fp in names.items():
            mid=doc.FamilyManager.CurrentType.AsElementId(fp);family_materials[name]=material_data(doc,doc.GetElement(mid))
        project=app.NewProjectDocument(DB.UnitSystem.Imperial);family=doc.LoadFamily(project)
        symbol=project.GetElement(list(family.GetFamilySymbolIds())[0])
        tx=DB.Transaction(project,'Final face-host and editable-material review');tx.Start()
        level=DB.Level.Create(project,10 if source['host']=='ceiling' else 0)
        if source['host']=='wall':
            wt=next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
            host=DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,12,0,False,False)
            project.Regenerate();reference=DB.HostObjectUtils.GetSideFaces(host,DB.ShellLayerType.Exterior)[0]
            face=host.GetGeometryObjectFromReference(reference);point=face.Project(DB.XYZ(0,0,5)).XYZPoint
        else:
            ft=DB.Floor.GetDefaultFloorType(project,False)
            outline=loop(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,[(-120,-120),(120,-120),(120,120),(-120,120)])
            host=DB.Floor.Create(project,List[DB.CurveLoop]([outline]),ft,level.Id)
            project.Regenerate();reference=DB.HostObjectUtils.GetBottomFaces(host)[0]
            face=host.GetGeometryObjectFromReference(reference);point=face.Project(DB.XYZ(0,0,10)).XYZPoint
        symbol.Activate();project.Regenerate()
        instance=project.Create.NewFamilyInstance(reference,point,DB.XYZ.BasisX,symbol);project.Regenerate()
        transform=instance.GetTransform();normal=transform.BasisZ.DotProduct(face.FaceNormal)
        row['face_host']={'host_id':int(host.Id.Value),'instance_host_id':int(instance.Host.Id.Value) if instance.Host else None,'has_host_face':instance.HostFace is not None,'normal_dot':normal}
        row['material_tests']={};temps=[]
        def face_ids():return [f.MaterialElementId for solid in all_solids(instance.get_Geometry(DB.Options())) for f in solid.Faces]
        for name in sorted(names):
            parameter=symbol.LookupParameter(name) or instance.LookupParameter(name)
            original=parameter.AsElementId();before=face_ids();count=sum(i==original for i in before)
            loaded=material_data(project,project.GetElement(original));temps.append(loaded.get('generic_self_illum_color_temperature'))
            alternate=DB.Material.Create(project,'Final QA '+name);parameter.Set(alternate);project.Regenerate()
            substituted=sum(i==alternate for i in face_ids())
            parameter.Set(original);project.Regenerate();restored=sum(i==original for i in face_ids())
            row['material_tests'][name]={'before_faces':count,'substituted_faces':substituted,'restored_faces':restored,
                'all_assigned_faces_changed':count>0 and substituted==count and restored==count,'family_appearance':family_materials[name],
                'loaded_appearance':loaded,'appearance_survives_load':family_materials[name]==loaded}
        proxy=object.__new__(NativeFixture);proxy.evidence=os.path.join(ROOT,source['folder'],'final_evidence')
        if not os.path.isdir(proxy.evidence):os.makedirs(proxy.evidence)
        center=xyz((bounds[0]+bounds[3])/2,(bounds[1]+bounds[4])/2,(bounds[2]+bounds[5])/2);span=max(dimensions)*2+12
        up=DB.XYZ.BasisY if source['host']=='wall' else DB.XYZ(0,0,-1)
        front=center+xyz(0,0,span) if source['host']=='wall' else center+xyz(0,-span,0)
        eyes=[('Front',front),('Side',center+xyz(span,0,0)),('Oblique',center+xyz(span*.65,-span*.45,span*.65))]
        views=[]
        for name,eye in eyes:
            view=proxy._view(project,'Final '+name,transform.OfPoint(eye),transform.OfPoint(center),transform.OfVector(up),[instance])
            view.HideElements(List[DB.ElementId]([host.Id]));views.append(view)
        view=proxy._view(project,'Final Material',transform.OfPoint(eyes[-1][1]),transform.OfPoint(center),transform.OfVector(up),[instance],True)
        view.HideElements(List[DB.ElementId]([host.Id]));views.append(view)
        hosted=proxy._view(project,'Final Hosted',transform.OfPoint(eyes[-1][1]),transform.OfPoint(center),transform.OfVector(up),[instance]);views.append(hosted)
        tx.Commit();tx=None;proxy._export(project,views,row['name'])
        row['project_warnings']=[w.GetDescriptionText() for w in project.GetWarnings()]
        row['required_cct_k']=cct;row['appearance_cct_values']=temps
        gates={'reopened':row['reopened'],'lighting_category':row['category']=='Lighting Fixtures','placement':row['placement']=='WorkPlaneBased',
            'face_template_behavior':row['hosting_behavior']==5,'actual_face_host':instance.Host is not None and instance.Host.Id==host.Id and instance.HostFace is not None,
            'orientation':abs(normal-1)<1e-8,'dimensions':dimensions_pass,'mount_plane':-.01<=bounds[2]<=.02,
            'materials':bool(names) and all(m['all_assigned_faces_changed'] for m in row['material_tests'].values()),
            'appearance_load':all(m['appearance_survives_load'] for m in row['material_tests'].values()),
            'textures':all(t['exists'] for m in row['material_tests'].values() for t in m['loaded_appearance']['textures']),
            'cct':cct is None or any(t is not None and abs(t-cct)<.01 for t in temps),
            'warnings':not row['family_warnings'] and not row['project_warnings'],'source_hash':row['mesh_source_hash_matches']}
        row['gates']=gates;row['pass']=all(gates.values());row['review_directory']=proxy.evidence
    except Exception:
        row['error']=traceback.format_exc()
    finally:
        if tx is not None:
            try:tx.RollBack()
            except Exception:pass
        if project is not None:project.Close(False)
        if doc is not None:doc.Close(False)
    summary['files'].append(row)
    with open(os.path.join(ROOT,REPORT_STEM+'_progress.json'),'w') as f:json.dump(summary,f,indent=2,default=str)
actual=dict((k,sum(r['fixture']==k for r in summary['files'])) for k in COUNT)
summary['coverage']=actual;summary['coverage_pass']=actual==COUNT;summary['all_pass']=summary['coverage_pass'] and all(r['pass'] for r in summary['files'])
summary['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z'
with open(os.path.join(ROOT,REPORT_STEM+'.json'),'w') as f:json.dump(summary,f,indent=2,default=str)
if not summary['all_pass']:raise RuntimeError('Final review requires correction; inspect native_final_review.json')