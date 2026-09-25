# -*- coding: utf-8 -*-
"""F01 - Visual Comfort Fan Maverick II 3MAVR52BKBKD.
Native Revit 2025 face-based Lighting Fixtures family.
"""
import os
import json
import math
import datetime
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f01_816712')
EVIDENCE = os.path.join(OUT, 'evidence')
RFA = os.path.join(OUT, 'Visual_Comfort_Maverick_II_3MAVR52BKBKD_R2025.rfa')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
SPAN = 52.0
HEIGHT = 19.8
PITCH = 13.0
TOL = 0.10
DOCS = []
TX = None
REPORT = {
    'fixture_id': 'f01_816712',
    'product': 'Maverick II Indoor / Outdoor Ceiling Fan with Light',
    'manufacturer': 'Visual Comfort Fan',
    'lightology_spec': 'MTC816709',
    'manufacturer_id': '3MAVR52BKBKD',
    'finish': 'Matte Black',
    'source_url': 'https://www.lightology.com/index.php?module=prod_detail&prod_id=816712&option_id=816709',
    'requested': {'span_in': SPAN, 'height_in': HEIGHT, 'pitch_deg': PITCH, 'cct_k': 3000},
}

def op(*parts):
    return os.path.join(OUT, *parts)

def checkpoint(stage):
    REPORT['stage'] = stage
    REPORT['checkpoint_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    with open(op('validation_latest.json'), 'w') as f:
        json.dump(REPORT, f, indent=2, default=str)

def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)

def profile_loop(origin, u, v, pts):
    loop = DB.CurveLoop()
    def p(q):
        return origin.Add(u.Multiply(q[0] / 12.0)).Add(v.Multiply(q[1] / 12.0))
    for i in range(len(pts)):
        loop.Append(DB.Line.CreateBound(p(pts[i]), p(pts[(i + 1) % len(pts)])))
    return loop

def revolve(doc, name, pts, mat_param, category):
    loop = profile_loop(DB.XYZ.Zero, DB.XYZ.BasisX, DB.XYZ.BasisZ, pts)
    frame = DB.Frame(DB.XYZ.Zero, DB.XYZ.BasisX, DB.XYZ.BasisY, DB.XYZ.BasisZ)
    solid = DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, List[DB.CurveLoop]([loop]), 0.0, 2.0 * math.pi)
    return freeform(doc, name, solid, mat_param, category)

def cylinder(doc, name, radius, z0, z1, mat_param, category):
    return revolve(doc, name, [(0,z0),(radius,z0),(radius,z1),(0,z1)], mat_param, category)

def freeform(doc, name, solid, mat_param, category):
    e = DB.FreeFormElement.Create(doc, solid)
    e.Subcategory = category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), mat_param)
    REPORT.setdefault('parts', []).append({'name': name, 'id': str(e.Id.Value)})
    return e

def generic_material(doc, app, name, color, gloss, transparency=0.0, self_illum=0.0):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    src = next(a for a in assets
               if a.FindByName('BaseSchema') is not None
               and a.FindByName('BaseSchema').Value == 'GenericSchema')
    appearance = DB.AppearanceAssetElement.Create(doc, name + ' Appearance', src)
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.AppearanceAssetId = appearance.Id
    mat.Color = DB.Color(*color)
    mat.Transparency = int(transparency * 100)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    def color_prop(key, rgb):
        p = asset.FindByName(key)
        if p is not None:
            if p.NumberOfConnectedProperties:
                p.RemoveConnectedAsset()
            p.SetValueAsColor(DB.Color(*rgb))
    def scalar(key, value):
        p = asset.FindByName(key)
        if p is not None:
            if p.NumberOfConnectedProperties:
                p.RemoveConnectedAsset()
            p.Value = value
    color_prop('generic_diffuse', color)
    scalar('generic_glossiness', gloss)
    scalar('generic_transparency', transparency)
    scalar('generic_reflectivity_at_0deg', 0.06)
    scalar('generic_reflectivity_at_90deg', 0.30)
    scalar('generic_self_illum_luminance', self_illum)
    if self_illum:
        color_prop(DB.Visual.Generic.GenericSelfIllumFilterMap, color)
        scalar(DB.Visual.Generic.GenericSelfIllumColorTemperature, 3000.0)
    scope.Commit(True)
    scope.Dispose()
    return mat

def blade_section(radius, sweep, width, thickness, zc, twist_deg):
    # Rounded-octagonal airfoil section in a plane normal to the radial X axis.
    # Tangential width dominates; the section twists progressively root-to-tip.
    c = math.cos(math.radians(twist_deg))
    s = math.sin(math.radians(twist_deg))
    hw = width / 2.0
    ht = thickness / 2.0
    raw = [
        (-hw * 0.82, -ht), (-hw, -ht * 0.30), (-hw, ht * 0.30),
        (-hw * 0.82, ht), (hw * 0.82, ht), (hw, ht * 0.30),
        (hw, -ht * 0.30), (hw * 0.82, -ht)
    ]
    pts = []
    for y0, z0 in raw:
        y = sweep + y0 * c - z0 * s
        z = zc + y0 * s + z0 * c
        pts.append(xyz(radius, y, z))
    loop = DB.CurveLoop()
    for i in range(len(pts)):
        loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % len(pts)]))
    return loop

def blade_solid():
    # Product-photo-derived sculpted wood blade:
    # narrow root -> broad paddle -> rounded tapering tip; increasing aft sweep;
    # strong root pitch relaxing toward the tip. Nominal page pitch is 13 deg.
    stations = [
        (3.45,  0.00, 2.00, 0.62, 13.75, 20.0),
        (5.50, -0.18, 2.70, 0.58, 13.78, 18.0),
        (8.50, -0.48, 3.55, 0.53, 13.83, 16.0),
        (12.5, -0.92, 4.45, 0.48, 13.90, 14.0),
        (17.0, -1.42, 5.20, 0.43, 13.98, 12.0),
        (21.0, -1.83, 5.70, 0.38, 14.07, 10.0),
        (24.2, -2.08, 5.35, 0.32, 14.15,  8.5),
        (25.6, -2.17, 3.80, 0.26, 14.20,  7.5),
        (26.0, -2.20, 0.80, 0.18, 14.22,  7.0),
    ]
    loops = List[DB.CurveLoop]()
    for st in stations:
        loops.Add(blade_section(*st))
    opts = DB.SolidOptions(DB.ElementId.InvalidElementId, DB.ElementId.InvalidElementId)
    return DB.GeometryCreationUtilities.CreateLoftGeometry(loops, opts)

def rotate_about_z(solid, degrees):
    tr = DB.Transform.CreateRotationAtPoint(
        DB.XYZ.BasisZ, math.radians(degrees), DB.XYZ.Zero)
    return DB.SolidUtils.CreateTransformed(solid, tr)

def geometry_points(element):
    opts = DB.Options()
    geom = element.get_Geometry(opts)
    pts = []
    def visit(obj):
        if isinstance(obj, DB.Solid) and obj.Volume > 1e-12:
            for edge in obj.Edges:
                for p in edge.Tessellate():
                    pts.append(p)
        elif isinstance(obj, DB.GeometryInstance):
            for sub in obj.GetInstanceGeometry():
                visit(sub)
    if geom:
        for obj in geom:
            visit(obj)
    return pts

def measured_extents(elements):
    pts = []
    for e in elements:
        pts.extend(geometry_points(e))
    r = max(math.sqrt(p.X*p.X + p.Y*p.Y) for p in pts) * 12.0
    z0 = min(p.Z for p in pts) * 12.0
    z1 = max(p.Z for p in pts) * 12.0
    return {'max_radius_in': r, 'sweep_diameter_in': 2*r,
            'zmin_in': z0, 'zmax_in': z1, 'height_in': z1-z0}

def view3d(doc, name, eye, target, realistic=False):
    vft = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
               if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    v = DB.View3D.CreateIsometric(doc, vft.Id)
    v.Name = name
    ep = xyz(*eye)
    tp = xyz(*target)
    fwd = tp.Subtract(ep).Normalize()
    up = DB.XYZ.BasisZ
    if abs(fwd.DotProduct(up)) > 0.99:
        up = DB.XYZ.BasisY
    right = fwd.CrossProduct(up).Normalize()
    v.SetOrientation(DB.ViewOrientation3D(ep, right.CrossProduct(fwd).Normalize(), fwd))
    v.DetailLevel = DB.ViewDetailLevel.Fine
    v.DisplayStyle = DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    box = DB.BoundingBoxXYZ()
    box.Min = xyz(-33,-33,-1)
    box.Max = xyz(33,33,22)
    v.SetSectionBox(box)
    v.IsSectionBoxActive = True
    return v

def export_images(doc, views, prefix):
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    opts.FilePath = os.path.join(EVIDENCE, prefix)
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 1800
    doc.ExportImage(opts)

def build(app):
    global TX
    doc = app.NewFamilyDocument(TEMPLATE)
    DOCS.append(doc)
    TX = DB.Transaction(doc, 'Build Maverick II 52 inch')
    TX.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(
        doc, DB.BuiltInCategory.OST_LightingFixtures)
    try:
        doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    except Exception:
        pass
    fm = doc.FamilyManager
    fm.NewType('52 inch - Matte Black - 3000K')
    metal = generic_material(doc, app, 'Maverick II - Matte Black Metal', (24,24,24), 0.22)
    wood = generic_material(doc, app, 'Maverick II - Black Wood Blades', (20,20,20), 0.18)
    glow = generic_material(doc, app, 'Maverick II - Opal 3000K', (250,245,233), 0.25, 0.06, 650.0)
    qa = generic_material(doc, app, 'Maverick II - QA Orange', (190,115,35), 0.50)

    p_metal = fm.AddParameter('Metal Finish', DB.GroupTypeId.Materials,
                              DB.SpecTypeId.Reference.Material, False)
    p_blade = fm.AddParameter('Blade Finish', DB.GroupTypeId.Materials,
                              DB.SpecTypeId.Reference.Material, False)
    p_glow = fm.AddParameter('Diffuser Finish', DB.GroupTypeId.Materials,
                             DB.SpecTypeId.Reference.Material, False)
    fm.Set(p_metal, metal.Id)
    fm.Set(p_blade, wood.Id)
    fm.Set(p_glow, glow.Id)
    for name, value in [('Blade Span', SPAN), ('Overall Height', HEIGHT)]:
        p = fm.AddParameter(name, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
        fm.SetFormula(p, str(value) + '"')
    p = fm.AddParameter('Blade Pitch', DB.GroupTypeId.Geometry, DB.SpecTypeId.Angle, False)
    fm.SetFormula(p, str(PITCH) + ' deg')
    p = fm.AddParameter('CCT', DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fm.Set(p, '3000 K')
    p = fm.AddParameter('Model Accuracy Notes', DB.GroupTypeId.IdentityData,
                        DB.SpecTypeId.String.Text, False)
    fm.Set(p, '52 in sweep, 19.8 in overall height, 13 deg nominal pitch, 6 in downrod and three blades from Lightology. Blade width/sweep/twist profile, canopy and motor diameters are reconstructed from preserved product/application images.')
    for bip, value in [
        (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Visual Comfort Fan'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL, 'Maverick II 3MAVR52BKBKD'),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
         'Maverick II 52 inch face-based visualization family, Matte Black, integrated 3000K LED')]:
        fp = fm.get_Parameter(bip)
        if fp is not None:
            fm.Set(fp, value)

    body_cat = doc.Settings.Categories.NewSubcategory(
        doc.OwnerFamily.FamilyCategory, 'Body')
    blade_cat = doc.Settings.Categories.NewSubcategory(
        doc.OwnerFamily.FamilyCategory, 'Sculpted Wood Blades')
    diff_cat = doc.Settings.Categories.NewSubcategory(
        doc.OwnerFamily.FamilyCategory, 'Diffuser')

    elems = []
    # Photo-matched tapered canopy and compact central motor/light housing.
    elems.append(revolve(doc, 'Canopy', [
        (0,0.0),(2.55,0.0),(2.65,0.30),(2.50,0.75),(2.08,1.28),
        (1.48,1.62),(0.95,1.82),(0,1.82)], p_metal, body_cat))
    elems.append(cylinder(doc, 'Downrod', 0.34, 1.70, 7.72, p_metal, body_cat))
    elems.append(revolve(doc, 'Upper motor neck', [
        (0,7.55),(0.88,7.55),(1.10,8.15),(1.55,8.70),(2.35,9.10),(0,9.10)
    ], p_metal, body_cat))
    elems.append(revolve(doc, 'Motor shell', [
        (0,9.05),(2.35,9.05),(3.18,9.65),(3.70,10.65),(3.85,12.10),
        (3.65,13.20),(3.10,14.15),(2.45,14.65),(0,14.65)
    ], p_metal, body_cat))
    elems.append(revolve(doc, 'Light bezel', [
        (0,14.28),(2.65,14.28),(3.22,14.58),(3.45,15.00),(3.32,15.42),(0,15.42)
    ], p_metal, body_cat))
    elems.append(revolve(doc, 'Opal light bowl', [
        (0,15.22),(3.05,15.22),(3.25,15.72),(3.18,16.65),
        (2.78,17.75),(2.05,18.75),(1.00,19.55),(0,19.80)
    ], p_glow, diff_cat))

    base_blade = blade_solid()
    for i, a in enumerate((0.0, 120.0, 240.0)):
        elems.append(freeform(doc, 'Sculpted blade %d' % (i+1),
                              rotate_about_z(base_blade, a), p_blade, blade_cat))
    doc.Regenerate()
    REPORT['measured_geometry'] = measured_extents(elems)
    mg = REPORT['measured_geometry']
    REPORT['dimension_checks'] = {
        'sweep_52_in': abs(mg['sweep_diameter_in'] - SPAN) <= TOL,
        'height_19_8_in': abs(mg['height_in'] - HEIGHT) <= TOL,
        'zmin_zero': abs(mg['zmin_in']) <= TOL,
    }
    REPORT['blade_model'] = {
        'construction': 'CreateLoftGeometry through nine rounded 3D cross-sections',
        'root_twist_deg': 20.0,
        'nominal_pitch_deg': PITCH,
        'tip_twist_deg': 7.0,
        'aft_sweep_at_tip_in': 2.20,
        'max_chord_in': 5.70,
        'root_thickness_in': 0.62,
        'tip_thickness_in': 0.18,
        'source_basis': 'preserved Lightology product and application images'
    }

    views = [
        view3d(doc, 'Front', (0,-88,14), (0,0,11), False),
        view3d(doc, 'Side', (88,0,14), (0,0,11), False),
        view3d(doc, 'Oblique', (58,-58,34), (0,0,11), True),
    ]
    TX.Commit()
    TX = None

    TX = DB.Transaction(doc, 'Material QA')
    TX.Start()
    fm.Set(p_blade, qa.Id)
    fm.Set(p_metal, qa.Id)
    doc.Regenerate()
    qa_view = view3d(doc, 'Material QA', (58,-58,30), (0,0,11), True)
    TX.Commit()
    TX = None
    export_images(doc, [qa_view], 'F01_MaterialQA')

    TX = DB.Transaction(doc, 'Restore Matte Black')
    TX.Start()
    fm.Set(p_blade, wood.Id)
    fm.Set(p_metal, metal.Id)
    doc.Regenerate()
    TX.Commit()
    TX = None

    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    save.PreviewViewId = views[2].Id
    doc.SaveAs(RFA, save)
    export_images(doc, views, 'F01_Family')
    REPORT['family_warnings_before_close'] = [
        w.GetDescriptionText() for w in doc.GetWarnings()]
    REPORT['rfa_path'] = RFA
    DOCS.remove(doc)
    doc.Close(False)
    checkpoint('family saved')

def validate(app):
    global TX
    doc = app.OpenDocumentFile(RFA)
    DOCS.append(doc)
    REPORT['reopened'] = bool(doc.IsFamilyDocument)
    REPORT['category'] = doc.OwnerFamily.FamilyCategory.Name
    REPORT['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    REPORT['family_warnings_reopen'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    REPORT['rfa_bytes'] = os.path.getsize(RFA)
    REPORT['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(
        os.path.getmtime(RFA)).isoformat() + 'Z'

    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    family = doc.LoadFamily(project)
    symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])
    TX = DB.Transaction(project, 'Host and validate Maverick II')
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    floor_type = DB.Floor.GetDefaultFloorType(project, False)
    cl = DB.CurveLoop()
    corners = [xyz(-60,-60,0), xyz(60,-60,0), xyz(60,60,0), xyz(-60,60,0)]
    for i in range(4):
        cl.Append(DB.Line.CreateBound(corners[i], corners[(i+1) % 4]))
    floor = DB.Floor.Create(project, List[DB.CurveLoop]([cl]), floor_type, level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(12.0)
    symbol.Activate()
    project.Regenerate()
    reference = DB.HostObjectUtils.GetBottomFaces(floor)[0]
    face = floor.GetGeometryObjectFromReference(reference)
    point = face.Project(DB.XYZ(0,0,12)).XYZPoint
    inst = project.Create.NewFamilyInstance(reference, point, DB.XYZ.BasisX, symbol)
    project.Regenerate()
    box = inst.get_BoundingBox(None)
    REPORT['host_validation'] = {
        'host_element_id': str(floor.Id.Value),
        'host_face_reference': reference.ConvertToStableRepresentation(project),
        'instance_host_id': str(inst.Host.Id.Value) if inst.Host is not None else None,
        'face_placed': bool(inst.Host is not None and inst.Host.Id == floor.Id),
        'host_face_z_in': point.Z * 12.0,
        'instance_bounds_in': [box.Min.X*12, box.Min.Y*12, box.Min.Z*12,
                               box.Max.X*12, box.Max.Y*12, box.Max.Z*12],
        'hangs_below_host': box.Max.Z <= point.Z + 1e-6
    }

    qa_id = DB.Material.Create(project, 'Maverick II QA Substitute')
    qa = project.GetElement(qa_id)
    qa.Color = DB.Color(220,120,30)
    blade_p = symbol.LookupParameter('Blade Finish')
    old = blade_p.AsElementId()
    blade_p.Set(qa_id)
    project.Regenerate()
    mids = set()
    geom = inst.get_Geometry(DB.Options())
    def scan(obj):
        if isinstance(obj, DB.Solid) and obj.Volume > 1e-12:
            for face0 in obj.Faces:
                mid = face0.MaterialElementId
                if mid is not None and mid != DB.ElementId.InvalidElementId:
                    mids.add(mid.Value)
        elif isinstance(obj, DB.GeometryInstance):
            for sub in obj.GetInstanceGeometry():
                scan(sub)
    if geom:
        for g in geom:
            scan(g)
    REPORT['material_substitution'] = {
        'blade_parameter_found': blade_p is not None,
        'qa_material_id': str(qa_id.Value),
        'resolved_face_material_ids': [str(x) for x in sorted(mids)],
        'qa_material_reached_geometry': qa_id.Value in mids,
    }
    blade_p.Set(old)
    project.Regenerate()
    hosted = view3d(project, 'Hosted Review', (55,-55,145), (0,0,132), False)
    REPORT['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    TX.Commit()
    TX = None
    export_images(project, [hosted], 'F01_Hosted')
    DOCS.remove(project)
    project.Close(False)
    DOCS.remove(doc)
    doc.Close(False)

def finish_report():
    REPORT['evidence_files'] = sorted(os.listdir(EVIDENCE))
    REPORT['warning_count'] = (
        len(REPORT.get('family_warnings_reopen', [])) +
        len(REPORT.get('project_warnings', [])))
    REPORT['native_gate'] = bool(
        REPORT.get('reopened') and
        REPORT.get('category') == 'Lighting Fixtures' and
        REPORT.get('host_validation', {}).get('face_placed') and
        REPORT.get('host_validation', {}).get('hangs_below_host') and
        REPORT.get('dimension_checks', {}).get('sweep_52_in') and
        REPORT.get('dimension_checks', {}).get('height_19_8_in') and
        REPORT.get('material_substitution', {}).get('qa_material_reached_geometry') and
        REPORT.get('warning_count') == 0)
    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    path = op('validation-' + stamp + '.json')
    with open(path, 'w') as f:
        json.dump(REPORT, f, indent=2, default=str)
    with open(op('validation_latest.json'), 'w') as f:
        json.dump(REPORT, f, indent=2, default=str)
    REPORT['timestamped_validation_path'] = path

try:
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    if app.VersionNumber != '2025':
        raise RuntimeError('Revit 2025 required, got ' + app.VersionNumber)
    if not os.path.isdir(EVIDENCE):
        os.makedirs(EVIDENCE)
    checkpoint('starting')
    build(app)
    validate(app)
    finish_report()
except Exception as ex:
    REPORT['error'] = str(ex)
    REPORT['traceback'] = traceback.format_exc()
    checkpoint('FAILED')
finally:
    try:
        if TX is not None and TX.GetStatus() == DB.TransactionStatus.Started:
            TX.RollBack()
    except Exception:
        pass
    for d in list(DOCS):
        try:
            d.Close(False)
        except Exception:
            pass


