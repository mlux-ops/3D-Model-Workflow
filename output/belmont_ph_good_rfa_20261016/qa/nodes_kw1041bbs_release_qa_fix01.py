# -*- coding: utf-8 -*-
"""Independent Revit 2025 read-only release QA: Visual Comfort Nodes KW1041BBS.

Prime-only pyRevit invocation. Opens the ORIGINAL approved RFA; never saves an
RFA or project. Makes one disposable unsaved project and rolls back its edits.
Writes only a NEW JSON QA receipt. A valid visual proxy is not MEP approval.
"""
from __future__ import print_function
import os, json, hashlib, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(r'E:\Claude\3D-Model-Workflow\output\lightology_20260923',
                      'release','Lightology_14_Face_Based_RFAs_R2025_Rev1','RFAs',
                      'Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa')
RECEIPT = os.path.join(BASE, 'qa', 'nodes_kw1041bbs_release_native_qa_fix01.json')
EXPECTED_SHA = '446223760904a196d04c30cdd9f8676b0f67d46c0e91516080a160e8db91879f'
OEM = 'https://www.visualcomfort.com/media/docs/spec_sheet/k/w/ss_kw1041bbs.pdf'
LIGHTOLOGY = 'https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833918'
EXPECTED = (8.0, 7.63, 5.5)  # width, wall-plane height, projection, inches


def require(ok, reason):
    if not ok: raise RuntimeError(reason)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            block = stream.read(1024*1024)
            if not block: break
            h.update(block)
    return h.hexdigest()


def identifier(value):
    try: return int(value.Value)
    except Exception: return int(value.IntegerValue)


def typename(element):
    try: return str(DB.Element.Name.GetValue(element))
    except Exception: return str(element.Name)


def native_points(element):
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    def walk(geometry):
        if geometry is None: return
        for item in geometry:
            if isinstance(item, DB.GeometryInstance):
                for p in walk(item.GetInstanceGeometry()): yield p
            elif isinstance(item, DB.Solid) and item.Volume > 1e-12:
                for face in item.Faces:
                    for p in face.Triangulate(1.0).Vertices: yield p
                for edge in item.Edges:
                    cv = edge.AsCurve()
                    if cv is None: continue
                    n = 2 if isinstance(cv, DB.Line) else 129
                    for i in range(n): yield cv.Evaluate(float(i)/(n-1), True)
    return list(walk(element.get_Geometry(options)))


def bounds(elements):
    pts = []
    for element in elements: pts.extend(native_points(element))
    require(bool(pts), 'Missing positive-volume analytic native solid geometry')
    return [(max(getattr(p, axis) for p in pts)-min(getattr(p, axis) for p in pts))*12.0
            for axis in 'XYZ']


def source_type(family):
    fm = family.FamilyManager
    types = list(fm.Types)
    require(len(types) == 1, 'Unexpected Nodes family type count')
    t = types[0]
    def built_in(bip):
        p = fm.get_Parameter(bip)
        return t.AsString(p) if p is not None else None
    identity = {'name': str(t.Name),
                'manufacturer': built_in(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER),
                'model': built_in(DB.BuiltInParameter.ALL_MODEL_MODEL),
                'description': built_in(DB.BuiltInParameter.ALL_MODEL_DESCRIPTION)}
    return t, identity


def survey_lighting(family, t):
    fm = family.FamilyManager
    params = []
    for p in fm.Parameters:
        n = str(p.Definition.Name)
        if any(x in n.lower() for x in ('light', 'source', 'ies', 'watt', 'volt', 'lamp', 'power', 'photometric', 'flux', 'lumen', 'accuracy')):
            value = None
            try:
                if str(p.StorageType) == 'String': value = t.AsString(p)
                elif str(p.StorageType) == 'Double': value = t.AsDouble(p)
                elif str(p.StorageType) == 'Integer': value = t.AsInteger(p)
            except Exception: pass
            params.append({'name': n, 'value': value})
    connectors = list(DB.FilteredElementCollector(family).OfClass(DB.ConnectorElement))
    emission = list(DB.FilteredElementCollector(family).OfClass(DB.LightSource)) if hasattr(DB, 'LightSource') else []
    photofile = None
    try:
        p = fm.get_Parameter(DB.BuiltInParameter.FBX_LIGHT_PHOTOMETRIC_FILE)
        if p is not None: photofile = t.AsString(p)
    except Exception: pass
    light_api = {'available': False, 'distribution_style': None, 'error': None}
    try:
        light = DB.Lighting.LightFamily.GetLightFamily(family)
        light_api['available'] = True
        light_api['distribution_style'] = str(light.GetLightDistributionStyle())
    except Exception as exc:
        light_api['error'] = str(exc)
    return {'connectors_count': len(connectors), 'connector_ids': [identifier(x.Id) for x in connectors],
            'light_source_count': len(emission), 'photometric_file': photofile,
            'light_family': light_api, 'relevant_parameters': params,
            'source_url_embedded': any('visualcomfort.com' in str(x.get('value', '')).lower()
                                        for x in params)}


def check_materials(doc, symbol, project, instance):
    mats = {str(m.Name): m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)}
    expected = ('Nodes - Burnished Brass', 'Nodes - Milk Glass')
    require(all(n in mats for n in expected), 'Original approved finish materials absent')
    actual = {}
    for n in expected:
        m = mats[n]
        actual[n] = {'rgb': [int(m.Color.Red), int(m.Color.Green), int(m.Color.Blue)],
                     'transparency': int(m.Transparency),
                     'appearance_asset_valid': isinstance(doc.GetElement(m.AppearanceAssetId), DB.AppearanceAssetElement)}
    require(actual[expected[0]]['rgb'] == [184,132,52], 'Burnished Brass base color changed')
    require(actual[expected[1]]['rgb'] == [246,243,235], 'Milk Glass base color changed')
    require(all(actual[n]['appearance_asset_valid'] for n in expected), 'Missing native appearance asset')
    substitutes = {}
    for pname in ('Metal Finish','Glass Finish'):
        p = symbol.LookupParameter(pname)
        require(p is not None and not p.IsReadOnly, 'Material type parameter unavailable '+pname)
        original = p.AsElementId()
        substitute = DB.Material.Create(project, 'Disposable Nodes QA '+pname)
        p.Set(substitute)
        project.Regenerate()
        # Verify the substitution actually reaches physical faces of this fixture.
        opts=DB.Options();opts.DetailLevel=DB.ViewDetailLevel.Fine
        face_ids=[]
        def collect(geometry):
            for item in geometry:
                if isinstance(item,DB.GeometryInstance):collect(item.GetInstanceGeometry())
                elif isinstance(item,DB.Solid) and item.Volume>1e-12:
                    for face in item.Faces:face_ids.append(identifier(face.MaterialElementId))
        collect(instance.get_Geometry(opts))
        affected=sum(1 for n in face_ids if n==identifier(substitute))
        require(affected>0,'Material substitution did not reach geometry '+pname)
        substitutes[pname] = {'substitute_id': identifier(substitute),
                              'original_id':identifier(original),'affected_faces':affected}
        p.Set(original)
        project.Regenerate()
    return {'materials': actual, 'editable_type_parameters': substitutes}


def placement(app, family):
    project = None
    tx = None
    try:
        project = app.NewProjectDocument(DB.UnitSystem.Imperial)
        loaded = family.LoadFamily(project)
        require(isinstance(loaded, DB.Family), 'Could not load accepted RFA in disposable project')
        ids = list(loaded.GetFamilySymbolIds())
        require(len(ids)==1, 'Disposable project family symbol count differs')
        symbol = project.GetElement(ids[0])
        tx = DB.Transaction(project, 'Nodes KW1041BBS temporary wall placement')
        tx.Start()
        level = DB.Level.Create(project, 0.0)
        walltype = next((w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType)
                         if w.Kind == DB.WallKind.Basic), None)
        require(walltype is not None, 'Disposable project lacks basic wall type')
        wall = DB.Wall.Create(project, DB.Line.CreateBound(DB.XYZ(-8,0,0),DB.XYZ(8,0,0)),
                              walltype.Id, level.Id, 10.0, 0.0, False, False)
        project.Regenerate()
        reference = list(DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior))[0]
        face = wall.GetGeometryObjectFromReference(reference)
        point = face.Project(DB.XYZ(0,0,5)).XYZPoint
        symbol.Activate(); project.Regenerate()
        instance = project.Create.NewFamilyInstance(reference,point,DB.XYZ.BasisX,symbol)
        project.Regenerate()
        hosted = instance.Host is not None and instance.Host.Id == wall.Id and instance.HostFace is not None
        require(hosted, 'Accepted Nodes RFA did not host to true wall face')
        dims = sorted(bounds([instance]))
        deviations = [abs(x-y) for x,y in zip(dims, sorted(EXPECTED))]
        require(max(deviations) <= 0.05, 'Placed dimensions differ from OEM limits by more than 0.05in')
        finish = check_materials(family,symbol,project,instance)
        warn = [str(w.GetDescriptionText()) for w in project.GetWarnings()]
        require(not warn,'Disposable host warnings: '+str(warn))
        return {'hosted_on_actual_wall_face': hosted, 'wall_id': identifier(wall.Id),
                'instance_id':identifier(instance.Id), 'world_dims_in_sorted':dims,
                'deviation_in_sorted':deviations,'finish':finish,
                'warnings':warn,'saved':False}
    finally:
        if tx is not None:
            try: tx.RollBack()
            except Exception: pass
        if project is not None: project.Close(False)


def main():
    require(str(__revit__.Application.VersionNumber)=='2025','Revit 2025 required')
    require(getattr(__revit__,'ActiveUIDocument',None) is None,'Requires isolated document-free Revit')
    require(not os.path.lexists(RECEIPT) and not os.path.lexists(RECEIPT+'.tmp'),
            'Receipt already exists; select revisioned path instead')
    require(os.path.isfile(SOURCE),'Approved Nodes RFA missing')
    original=sha(SOURCE)
    require(original==EXPECTED_SHA,'Approved RFA fingerprint mismatch')
    report={'source_rfa':SOURCE,'sha256':original,'status':'ERROR',
            'manufacturer_product':'KW1041BBS Burnished Brass / Milk',
            'manufacturer_spec_url':OEM,'retailer_exact_option_url':LIGHTOLOGY,
            'prior_appearance_approved':True,'original_rfa_modified':False,
            'photometric_distribution_approved':False,'electrical_release_approved':False}
    doc=None
    try:
        doc=__revit__.Application.OpenDocumentFile(SOURCE)
        require(doc.IsFamilyDocument,'Source is not family document')
        require(str(doc.OwnerFamily.FamilyCategory.Name)=='Lighting Fixtures','Wrong family category')
        require('WorkPlaneBased' in str(doc.OwnerFamily.FamilyPlacementType),'Wrong placement type')
        t, identity=source_type(doc)
        report['identity']=identity
        require(identity['name']=='KW1041BBS - Burnished Brass / Milk','Exact type mismatch')
        require(identity['model']=='KW1041BBS','Exact manufacturer model mismatch')
        require('Visual Comfort' in str(identity['manufacturer']),'Manufacturer metadata mismatch')
        report['source_geometry_in'] = bounds(list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement)))
        expected=[8.0,7.63,5.5]
        require(all(abs(x-y)<=0.05 for x,y in zip(report['source_geometry_in'],expected)),
                'Analytic source geometry differs from published envelope')
        require(len(list(DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance)))==0,
                'Unexpected CAD import found')
        require(len(list(DB.FilteredElementCollector(doc).OfClass(DB.DirectShape)))==0,
                'Unexpected DirectShape found')
        report['lighting']=survey_lighting(doc,t)
        report['family_warnings']=[str(w.GetDescriptionText()) for w in doc.GetWarnings()]
        require(not report['family_warnings'],'Warnings found in accepted family')
        report['disposable_placement']=placement(__revit__.Application,doc)
        # Original was explicitly an architectural visualization family.
        # A photometric/connector absence stays a disclosure, not invented pass.
        report['status']='ARCHITECTURAL_NATIVE_PASS_MEP_HOLD'
    except Exception:
        report['error']=traceback.format_exc()
    finally:
        if doc is not None: doc.Close(False)
        after=sha(SOURCE)
        report['sha256_after']=after
        report['original_rfa_modified']=after!=original
        if after!=original: report['status']='FAIL_SOURCE_MUTATED'
        data=json.dumps(report,indent=2,sort_keys=True,ensure_ascii=True)
        with open(RECEIPT+'.tmp','wb') as out:out.write(data.encode('ascii'))
        require(not os.path.lexists(RECEIPT),'Receipt appeared mid-run')
        os.rename(RECEIPT+'.tmp',RECEIPT)
    print('NODES_KW1041BBS_QA '+report['status'])
    require(report['status']=='ARCHITECTURAL_NATIVE_PASS_MEP_HOLD','Nodes QA failed; inspect receipt')


if __name__=='__main__': main()
