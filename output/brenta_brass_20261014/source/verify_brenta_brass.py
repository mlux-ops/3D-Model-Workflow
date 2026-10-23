# -*- coding: utf-8 -*-
"""Independent saved-file QA: geometry, finishes, and both wall orientations."""
import os, sys, json, hashlib, datetime, traceback, gzip
SOURCE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SOURCE)
sys.path.insert(0,SOURCE)
from native_fixture_support import NativeFixture, DB, xyz, all_solids, measured_geometry_bounds
from System.Collections.Generic import List

PATH = os.path.join(OUT,'AERIN_Brenta_ARN2473HAB-CG_Antique_Brass_R2025.rfa')
REPORT = os.path.join(OUT,'independent_validation.json')
app = __revit__.Application
row = {'rfa_path':PATH, 'started_utc':datetime.datetime.utcnow().isoformat()+'Z',
       'revit_version':app.VersionNumber, 'pass':False}
doc = project = tx = None

def material_data(document, mid):
    material = document.GetElement(mid)
    ae = document.GetElement(material.AppearanceAssetId)
    if ae is None:
        raise RuntimeError('Missing appearance asset')
    asset = ae.GetRenderingAsset()
    result = {'name':DB.Element.Name.GetValue(material),
              'rgb':[int(material.Color.Red),int(material.Color.Green),int(material.Color.Blue)]}
    for key in ('generic_is_metal','generic_glossiness','generic_transparency',
                'generic_self_illum_luminance','generic_self_illum_color_temperature'):
        p = asset.FindByName(key)
        result[key] = p.Value if p is not None else None
    diffuse = asset.FindByName('generic_diffuse')
    bitmap = diffuse.GetSingleConnectedAsset().FindByName('unifiedbitmap_Bitmap')
    result['bitmap'] = bitmap.Value
    result['bitmap_exists'] = os.path.isfile(bitmap.Value)
    result['bitmap_sha256'] = hashlib.sha256(open(bitmap.Value,'rb').read()).hexdigest()
    return result

def export_mesh(document, forms, sha256):
    data = {'source':{'rfa':PATH,'sha256':sha256},'units':'metres','materials':{},'parts':[]}
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    for element in forms:
        fallback = element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM).AsElementId()
        for si,solid in enumerate(all_solids(element.get_Geometry(options))):
            vertices, normals, triangles, ids = [], [], [], []
            for face in solid.Faces:
                mid = face.MaterialElementId
                if mid==DB.ElementId.InvalidElementId:mid=fallback
                key = str(mid.Value)
                if key not in data['materials']:
                    info = material_data(document,mid)
                    info['rgb'] = [v/255.0 for v in info['rgb']]
                    info['class'] = document.GetElement(mid).MaterialClass
                    info['generic_refraction_index'] = 1.52 if info['class']=='Glass' else 1.0
                    data['materials'][key] = info
                mesh = face.Triangulate(1.0)
                lookup = {}
                base = len(vertices)
                for vi in range(mesh.Vertices.Count):
                    v = mesh.Vertices[vi]
                    lookup[(round(v.X,9),round(v.Y,9),round(v.Z,9))] = base+vi
                    vertices.append([v.X*.3048,v.Y*.3048,v.Z*.3048])
                    projection = face.Project(v)
                    uv = projection.UVPoint if projection else (face.GetBoundingBox().Min+face.GetBoundingBox().Max)*.5
                    normal = face.ComputeNormal(uv)
                    normals.append([normal.X,normal.Y,normal.Z])
                for ti in range(mesh.NumTriangles):
                    triangle = mesh.get_Triangle(ti)
                    indices = []
                    for j in range(3):
                        v = triangle.get_Vertex(j)
                        indices.append(lookup[(round(v.X,9),round(v.Y,9),round(v.Z,9))])
                    triangles.append(indices)
                    ids.append(key)
            data['parts'].append({'element':int(element.Id.Value),'solid':si,'vertices':vertices,
                                 'normals':normals,'triangles':triangles,'material_ids':ids})
    target = os.path.join(OUT,'native_mesh.json.gz')
    with gzip.open(target,'wb') as stream:stream.write(json.dumps(data,separators=(',',':'),default=str).encode('utf8'))
    return {'file':target,'parts':len(data['parts']),'triangles':sum(len(p['triangles']) for p in data['parts'])}

try:
    row['sha256'] = hashlib.sha256(open(PATH,'rb').read()).hexdigest()
    doc = app.OpenDocumentFile(PATH)
    row['reopened'] = doc.IsFamilyDocument
    row['category'] = doc.OwnerFamily.FamilyCategory.Name
    row['placement'] = str(doc.OwnerFamily.FamilyPlacementType)
    row['hosting_behavior'] = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR).AsInteger()
    row['family_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    forms = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    bounds = measured_geometry_bounds(forms)
    dims = [bounds[i+3]-bounds[i] for i in range(3)]
    row['dimensions_in'] = dims
    row['native_solid_count'] = len(forms)
    row['import_instance_count'] = len(list(DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance)))
    row['component_dimensions_in'] = []
    for form in forms:
        b = measured_geometry_bounds([form])
        row['component_dimensions_in'].append([b[i+3]-b[i] for i in range(3)])
    names = ('Metal Finish','Glass Finish','Diffuser Finish')
    fm = doc.FamilyManager
    materials = dict((name,material_data(doc,fm.CurrentType.AsElementId(fm.get_Parameter(name)))) for name in names)
    row['family_materials'] = materials
    row['native_mesh'] = export_mesh(doc,forms,row['sha256'])
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    family = doc.LoadFamily(project)
    symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])
    row['model'] = symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MODEL).AsString()
    row['type_name'] = DB.Element.Name.GetValue(symbol)
    tx = DB.Transaction(project,'Independent Brenta validation')
    tx.Start()
    level = DB.Level.Create(project,0)
    wt = next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind==DB.WallKind.Basic)
    host = DB.Wall.Create(project,DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),wt.Id,level.Id,10,0,False,False)
    project.Regenerate()
    reference = DB.HostObjectUtils.GetSideFaces(host,DB.ShellLayerType.Exterior)[0]
    face = host.GetGeometryObjectFromReference(reference)
    symbol.Activate()
    project.Regenerate()
    instances = []
    placements = {}
    for label, origin, direction, expected in [
            ('Vertical',DB.XYZ(-2,0,5),DB.XYZ.BasisX,[3.5,3.75,18.5]),
            ('Horizontal',DB.XYZ(2,0,5),DB.XYZ.BasisZ,[18.5,3.75,3.5])]:
        point = face.Project(origin).XYZPoint
        inst = project.Create.NewFamilyInstance(reference,point,direction,symbol)
        project.Regenerate()
        b = measured_geometry_bounds([inst])
        dimensions = [b[i+3]-b[i] for i in range(3)]
        normal = inst.GetTransform().BasisZ.DotProduct(face.FaceNormal)
        hosted = inst.Host is not None and inst.Host.Id==host.Id and inst.HostFace is not None
        placements[label] = {'dimensions_in':dimensions,'expected_in':expected,
            'hostface_verified':hosted,'normal_dot':normal,
            'pass':hosted and abs(normal-1)<1e-8 and all(abs(a-b)<.001 for a,b in zip(dimensions,expected))}
        instances.append(inst)
    row['placements'] = placements
    inst = instances[0]
    def face_ids():
        return [f.MaterialElementId for s in all_solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
    tests = {}
    for name in names:
        parameter = symbol.LookupParameter(name)
        original = parameter.AsElementId()
        loaded = material_data(project,original)
        before = sum(mid==original for mid in face_ids())
        alternate = DB.Material.Create(project,'Temporary QA '+name)
        parameter.Set(alternate)
        project.Regenerate()
        changed = sum(mid==alternate for mid in face_ids())
        parameter.Set(original)
        project.Regenerate()
        restored = sum(mid==original for mid in face_ids())
        tests[name] = {'assigned_faces':before,'changed_faces':changed,'restored_faces':restored,
                       'appearance_survives_load':loaded==materials[name],
                       'pass':before>0 and before==changed==restored and loaded==materials[name]}
    row['material_tests'] = tests
    proxy = object.__new__(NativeFixture)
    proxy.evidence = os.path.join(OUT,'review')
    if not os.path.isdir(proxy.evidence):os.makedirs(proxy.evidence)
    center = xyz(0,0,1.875)
    views = []
    transform = inst.GetTransform()
    for label, eye, realistic in [
            ('Front',xyz(0,0,50),False),('Side',xyz(50,0,1.875),False),
            ('Oblique',xyz(30,9,50),False),('Material',xyz(30,9,50),True)]:
        view = proxy._view(project,label,transform.OfPoint(eye),transform.OfPoint(center),
            transform.OfVector(DB.XYZ.BasisY),[inst],realistic)
        view.HideElements(List[DB.ElementId]([host.Id]))
        views.append(view)
    second = instances[1]
    b = second.get_BoundingBox(None)
    target = (b.Min+b.Max)*.5
    camera_eye = target+face.FaceNormal.Multiply(6)+DB.XYZ(2,0,1.4)
    row['horizontal_camera_front_of_wall'] = (camera_eye-target).DotProduct(face.FaceNormal)>0
    views.append(proxy._view(project,'Horizontal Wall Placement',camera_eye,target,
                             DB.XYZ.BasisZ,[second],False))
    tx.Commit()
    tx = None
    row['view_exports'] = []
    for view in views:
        record = {'view':view.Name,'style':str(view.DisplayStyle),'pass':False}
        try:
            proxy._export(project,[view],'Brenta Brass')
            record['pass'] = True
        except Exception as exc:
            record['error'] = str(exc)
        row['view_exports'].append(record)
    row['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    gates = {
        'reopened_2025':row['reopened'] and app.VersionNumber=='2025',
        'category':row['category']=='Lighting Fixtures',
        'native_face_based':row['hosting_behavior']==5 and row['placement']=='WorkPlaneBased',
        'nominal_dimensions':all(abs(a-b)<.001 for a,b in zip(dims,[3.5,18.5,3.75])),
        'native_geometry':len(forms)==7 and row['import_instance_count']==0,
        'both_orientations':all(p['pass'] for p in placements.values()),
        'material_parameters':all(t['pass'] for t in tests.values()),
        'brass_finish':materials['Metal Finish']['generic_is_metal']==True,
        'nonmetallic_glass':not materials['Glass Finish']['generic_is_metal'] and not materials['Diffuser Finish']['generic_is_metal'],
        'textures_resolved':all(m['bitmap_exists'] for m in materials.values()),
        'correct_model':row['model']=='ARN 2473HAB-CG',
        'cct':abs(materials['Diffuser Finish']['generic_self_illum_color_temperature']-2700)<.01,
        'geometry_views':row['horizontal_camera_front_of_wall'] and all(v['pass'] for v in row['view_exports'] if v['style']!='Realistic'),
        'warnings':not row['family_warnings'] and not row['project_warnings']}
    row['gates'] = gates
    row['pass'] = all(gates.values())
except Exception:
    row['error'] = traceback.format_exc()
finally:
    if tx is not None:tx.RollBack()
    if project is not None:project.Close(False)
    if doc is not None:doc.Close(False)
    row['finished_utc'] = datetime.datetime.utcnow().isoformat()+'Z'
    with open(REPORT,'w') as stream:json.dump(row,stream,indent=2,default=str)
if not row['pass']:
    raise RuntimeError('Independent Brenta validation failed; see '+REPORT)
print('BRENTA_BRASS_INDEPENDENT_PASS '+PATH)
