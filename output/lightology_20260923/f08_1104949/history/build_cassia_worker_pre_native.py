# -*- coding: utf-8 -*-
"""Build and validate Alora Mood Cassia LP549448AGOP in Revit 2025.

Run through pyRevit with an absolute script path. All generated artifacts stay
inside output/lightology_20260923/f08_1104949.
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
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f08_1104949')
TEMPLATE_DIR = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial'
FACE_TEMPLATE = os.path.join(TEMPLATE_DIR, 'Generic Model face based.rft')
RFA_NAME = 'Alora_Cassia_LP549448AGOP_R2025.rfa'
RFA_PATH = os.path.join(OUT, RFA_NAME)

# Manufacturer dimensions, inches.
OVERALL_L = 48.0
OVERALL_W = 13.375
GLOBE_D = 6.0
GLOBE_R = 3.0
CANOPY_L = 11.125
CANOPY_W = 4.375
CANOPY_H = 0.875
SUSPENSION = 46.0
BAR_Z = CANOPY_H + SUSPENSION
TOTAL_DROP = BAR_Z + GLOBE_R
DOWNROD_SPACING = 9.75

# Photo-derived / drawing-interpreted details, inches.
ROD_R = 0.14
COLLAR_R = 0.55
COLLAR_DEPTH = 0.28
DOWNROD_R = 0.14
DOWNROD_COLLAR_R = 0.23
DOWNROD_COLLAR_H = 0.28
CENTER_GLOBE_Y = OVERALL_W / 2.0 - GLOBE_R
END_GLOBE_X = OVERALL_L / 2.0 - GLOBE_R
DOWNROD_X = DOWNROD_SPACING / 2.0
DIM_TOL = 0.03

METAL_SPEC = {
    'color': (183, 137, 63), 'gloss': 0.58, 'refl0': 0.34,
    'refl90': 0.86, 'transparency': 0.0, 'self_illum': 0.0,
    'material_class': 'Metal'
}
GLASS_SPEC = {
    'color': (242, 238, 224), 'gloss': 0.28, 'refl0': 0.08,
    'refl90': 0.52, 'transparency': 0.12, 'self_illum': 0.0,
    'material_class': 'Glass'
}

REPORT = {
    'task': 'f08_1104949',
    'product': 'Alora Mood Cassia Linear Pendant',
    'manufacturer_model': 'LP549448AGOP',
    'lightology_spec': 'ALR1104949',
    'requested_variant': {'finish': 'Aged Gold', 'color': 'Opal Matte'},
    'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'script': os.path.basename(__file__),
    'output_dir': OUT,
    'dimensions_source': 'Lightology page plus manufacturer LP549448 dimension graphic',
    'cct_note': 'No integrated CCT: four E12 lamps are not included; lamp choice determines CCT.',
}
DOCS = []
TX = None


def out_path(*parts):
    target = os.path.normpath(os.path.join(OUT, *parts))
    root = os.path.normpath(OUT)
    if target != root and not target.startswith(root + os.sep):
        raise RuntimeError('Write path escapes task directory: ' + target)
    parent = os.path.dirname(target)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    REPORT['checkpoint_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    payload = json.dumps(REPORT, indent=2, sort_keys=True, default=str)
    with open(out_path('validation.json'), 'w') as f:
        f.write(payload)
    stamp = REPORT['started_utc'].replace(':', '').replace('-', '').replace('.', '')
    with open(out_path('logs', 'validation-%s.json' % stamp), 'w') as f:
        f.write(payload)


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def element_name(element):
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        p = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return p.AsString() if p else None


def solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid


def profile_loop(origin, u, v, points):
    def pt(pair):
        return origin.Add(u.Multiply(pair[0] / 12.0)).Add(v.Multiply(pair[1] / 12.0))
    loop = DB.CurveLoop()
    current = points[0]
    for item in points[1:]:
        if len(item) == 3 and item[0] == 'arc':
            mid, end = item[1], item[2]
            loop.Append(DB.Arc.Create(pt(current), pt(end), pt(mid)))
        else:
            end = item
            loop.Append(DB.Line.CreateBound(pt(current), pt(end)))
        current = end
    if current != points[0]:
        loop.Append(DB.Line.CreateBound(pt(current), pt(points[0])))
    return loop


def add_freeform(doc, solid, subcat, param, name, bucket):
    el = DB.FreeFormElement.Create(doc, solid)
    el.Subcategory = subcat
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        el.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), param)
    bucket.append({'name': name, 'id': int(el.Id.Value)})
    return el


def revolved(doc, origin, axis, points, subcat, param, name, bucket):
    axis = axis.Normalize()
    radial = DB.XYZ.BasisX if abs(axis.Z) > 0.99 else DB.XYZ.BasisZ
    radial = radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop = profile_loop(origin, radial, axis, points)
    frame = DB.Frame(origin, radial, axis.CrossProduct(radial), axis)
    solid = DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, List[DB.CurveLoop]([loop]), 0, 2 * math.pi)
    return add_freeform(doc, solid, subcat, param, name, bucket)


def sphere(doc, center, radius, subcat, param, name, bucket):
    pts = [(0, -radius), ('arc', (radius, 0), (0, radius)), (0, -radius)]
    return revolved(doc, center, DB.XYZ.BasisZ, pts, subcat, param, name, bucket)


def cylinder(doc, origin, axis, radius, length, subcat, param, name, bucket):
    pts = [(0, 0), (radius, 0), (radius, length), (0, length)]
    return revolved(doc, origin, axis, pts, subcat, param, name, bucket)


def box(doc, x0, y0, z0, x1, y1, z1, subcat, param, name, bucket):
    p0, p1, p2, p3 = xyz(x0, y0, z0), xyz(x1, y0, z0), xyz(x1, y1, z0), xyz(x0, y1, z0)
    loop = DB.CurveLoop()
    loop.Append(DB.Line.CreateBound(p0, p1))
    loop.Append(DB.Line.CreateBound(p1, p2))
    loop.Append(DB.Line.CreateBound(p2, p3))
    loop.Append(DB.Line.CreateBound(p3, p0))
    solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(
        List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, (z1 - z0) / 12.0)
    return add_freeform(doc, solid, subcat, param, name, bucket)


def clone_material(doc, name, asset, color, transparency):
    appearance = DB.AppearanceAssetElement.Create(doc, name, asset)
    material = doc.GetElement(DB.Material.Create(doc, name))
    material.AppearanceAssetId = appearance.Id
    material.Color = DB.Color(*color)
    material.Transparency = int(round(transparency * 100))
    return material, appearance


def set_color(asset, key, color):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Missing appearance property: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color))


def scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Missing appearance property: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value


def make_material(doc, app, name, spec):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next(a for a in assets if a.FindByName('BaseSchema') is not None
                  and a.FindByName('BaseSchema').Value == 'GenericSchema')
    material, appearance = clone_material(doc, name, source, spec['color'], spec['transparency'])
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    edit = scope.Start(appearance.Id)
    set_color(edit, 'generic_diffuse', spec['color'])
    scalar(edit, 'generic_glossiness', spec['gloss'])
    scalar(edit, 'generic_transparency', spec['transparency'])
    scalar(edit, 'generic_reflectivity_at_0deg', spec['refl0'])
    scalar(edit, 'generic_reflectivity_at_90deg', spec['refl90'])
    scalar(edit, 'generic_self_illum_luminance', spec['self_illum'])
    scope.Commit(True)
    scope.Dispose()
    material.MaterialClass = spec['material_class']
    return material


def setup(doc, app):
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    av = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if av:
        av.Set(0)
    mgr = doc.FamilyManager
    mgr.NewType('LP549448AGOP - Aged Gold / Opal Matte')
    metal = make_material(doc, app, 'Cassia Aged Gold', METAL_SPEC)
    glass = make_material(doc, app, 'Cassia Opal Matte', GLASS_SPEC)
    p_metal = mgr.AddParameter('Metal Finish', DB.GroupTypeId.Materials,
                               DB.SpecTypeId.Reference.Material, False)
    p_glass = mgr.AddParameter('Glass Finish', DB.GroupTypeId.Materials,
                               DB.SpecTypeId.Reference.Material, False)
    mgr.Set(p_metal, metal.Id)
    mgr.Set(p_glass, glass.Id)
    for name, value in [
        ('Manufacturer', 'Alora Mood'),
        ('Model', 'LP549448AGOP'),
        ('Lightology Spec', 'ALR1104949'),
        ('Finish', 'Aged Gold'),
        ('Shade Color', 'Opal Matte'),
        ('CCT', 'Lamp dependent - 4 x E12 lamps not included'),
    ]:
        p = mgr.AddParameter(name, DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
        mgr.Set(p, value)
    return mgr, p_metal, p_glass


def bounds_for_ids(doc, ids):
    boxes = []
    for value in ids:
        el = doc.GetElement(DB.ElementId(value))
        if el is not None:
            b = el.get_BoundingBox(None)
            if b:
                boxes.append(b)
    if not boxes:
        return None
    mn = [min(getattr(b.Min, c) for b in boxes) * 12 for c in ('X','Y','Z')]
    mx = [max(getattr(b.Max, c) for b in boxes) * 12 for c in ('X','Y','Z')]
    return {'min': mn, 'max': mx, 'size': [mx[i] - mn[i] for i in range(3)]}


def check(bucket, name, measured, target, tol, method):
    ok = measured is not None and abs(measured - target) <= tol
    bucket[name] = {'measured_in': measured, 'target_in': target,
                    'tolerance_in': tol, 'method': method, 'pass': ok}
    return ok


def family_view(doc, name, eye, target, box_min, box_max, realistic=False):
    vt = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
              if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vt.Id)
    view.Name = name
    forward = target.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ.Negate()
    if abs(forward.DotProduct(up)) > 0.99:
        up = DB.XYZ.BasisY
    right = forward.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(
        eye, right.CrossProduct(forward).Normalize(), forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    boxv = DB.BoundingBoxXYZ()
    boxv.Min = box_min
    boxv.Max = box_max
    view.SetSectionBox(boxv)
    view.IsSectionBoxActive = True
    return view


def export_images(doc, views, prefix):
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    opts.FilePath = out_path('evidence', prefix)
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 1800
    doc.ExportImage(opts)


def build_family(app):
    global TX
    doc = app.NewFamilyDocument(FACE_TEMPLATE)
    DOCS.append(doc)
    TX = DB.Transaction(doc, 'Build Cassia LP549448AGOP')
    TX.Start()
    mgr, metal, glass = setup(doc, app)
    body_cat = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Cassia Body Metal')
    glass_cat = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Cassia Opal Globes')
    susp_cat = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Cassia Canopy and Suspension')
    body = []
    suspension = []

    # Canopy.
    box(doc, -CANOPY_L/2, -CANOPY_W/2, 0, CANOPY_L/2, CANOPY_W/2, CANOPY_H,
        susp_cat, metal, 'Canopy', suspension)

    # Two suspension rods and short connector collars.
    for x in (-DOWNROD_X, DOWNROD_X):
        cylinder(doc, xyz(x, 0, CANOPY_H), DB.XYZ.BasisZ, DOWNROD_R, SUSPENSION,
                 susp_cat, metal, 'Downrod %.3f' % x, suspension)
        cylinder(doc, xyz(x, 0, BAR_Z - DOWNROD_COLLAR_H/2), DB.XYZ.BasisZ,
                 DOWNROD_COLLAR_R, DOWNROD_COLLAR_H,
                 susp_cat, metal, 'Downrod lower collar %.3f' % x, suspension)

    # Longitudinal rail from globe seat to globe seat.
    cylinder(doc, xyz(-END_GLOBE_X + GLOBE_R, 0, BAR_Z), DB.XYZ.BasisX,
             ROD_R, 2*(END_GLOBE_X - GLOBE_R),
             body_cat, metal, 'Main rail', body)

    # End globes and collars.
    sphere(doc, xyz(-END_GLOBE_X, 0, BAR_Z), GLOBE_R,
           glass_cat, glass, 'Left opal globe', body)
    sphere(doc, xyz( END_GLOBE_X, 0, BAR_Z), GLOBE_R,
           glass_cat, glass, 'Right opal globe', body)
    cylinder(doc, xyz(-END_GLOBE_X + GLOBE_R, 0, BAR_Z), DB.XYZ.BasisX.Negate(),
             COLLAR_R, COLLAR_DEPTH, body_cat, metal, 'Left globe collar', body)
    cylinder(doc, xyz( END_GLOBE_X - GLOBE_R, 0, BAR_Z), DB.XYZ.BasisX,
             COLLAR_R, COLLAR_DEPTH, body_cat, metal, 'Right globe collar', body)

    # Opposed central globes perpendicular to main rail.
    sphere(doc, xyz(0, -CENTER_GLOBE_Y, BAR_Z), GLOBE_R,
           glass_cat, glass, 'Rear opal globe', body)
    sphere(doc, xyz(0,  CENTER_GLOBE_Y, BAR_Z), GLOBE_R,
           glass_cat, glass, 'Front opal globe', body)
    inner = CENTER_GLOBE_Y - GLOBE_R
    cylinder(doc, xyz(0, -inner, BAR_Z), DB.XYZ.BasisY, ROD_R, 2*inner,
             body_cat, metal, 'Cross rail', body)
    cylinder(doc, xyz(0, -inner, BAR_Z), DB.XYZ.BasisY,
             COLLAR_R, COLLAR_DEPTH, body_cat, metal, 'Rear globe collar', body)
    cylinder(doc, xyz(0, inner, BAR_Z), DB.XYZ.BasisY.Negate(),
             COLLAR_R, COLLAR_DEPTH, body_cat, metal, 'Front globe collar', body)

    doc.Regenerate()
    REPORT['body_element_ids'] = [p['id'] for p in body]
    REPORT['suspension_element_ids'] = [p['id'] for p in suspension]
    REPORT['parts'] = {'body': body, 'suspension': suspension}
    body_bounds = bounds_for_ids(doc, REPORT['body_element_ids'])
    canopy_id = next(p['id'] for p in suspension if p['name'] == 'Canopy')
    canopy_bounds = bounds_for_ids(doc, [canopy_id])
    REPORT['build_body_bounds_in'] = body_bounds
    REPORT['build_canopy_bounds_in'] = canopy_bounds
    dims = REPORT.setdefault('dimensions', {})
    check(dims, 'body_length', body_bounds['size'][0], OVERALL_L, DIM_TOL,
          'union bounding box of Cassia body geometry')
    check(dims, 'body_width', body_bounds['size'][1], OVERALL_W, DIM_TOL,
          'union bounding box of Cassia body geometry')
    check(dims, 'globe_body_height', body_bounds['size'][2], GLOBE_D, DIM_TOL,
          'union body Z extent; globe diameter controls height')
    check(dims, 'canopy_length', canopy_bounds['size'][0], CANOPY_L, DIM_TOL,
          'canopy solid X extent')
    check(dims, 'canopy_width', canopy_bounds['size'][1], CANOPY_W, DIM_TOL,
          'canopy solid Y extent')
    check(dims, 'canopy_height', canopy_bounds['size'][2], CANOPY_H, DIM_TOL,
          'canopy solid Z extent')

    target = xyz(0, 0, BAR_Z/2)
    bmin, bmax = xyz(-27, -10, -1), xyz(27, 10, TOTAL_DROP + 2)
    views = [
        family_view(doc, 'Cassia Front', xyz(0, -115, BAR_Z/2), target, bmin, bmax),
        family_view(doc, 'Cassia Side', xyz(115, 0, BAR_Z/2), target, bmin, bmax),
        family_view(doc, 'Cassia Oblique', xyz(80, -100, BAR_Z/2 - 8), target, bmin, bmax),
        family_view(doc, 'Cassia Material', xyz(64, -72, BAR_Z - 2), xyz(0,0,BAR_Z),
                    xyz(-27,-10,BAR_Z-8), xyz(27,10,BAR_Z+8), realistic=True),
    ]
    TX.Commit()
    TX = None

    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    save.PreviewViewId = views[2].Id
    doc.SaveAs(RFA_PATH, save)
    export_images(doc, views, 'Cassia')
    REPORT['family_exports'] = sorted(
        n for n in os.listdir(out_path('evidence')) if n.startswith('Cassia'))
    DOCS.remove(doc)
    doc.Close(False)
    return RFA_PATH


def validate(app, rfa_path):
    global TX
    doc = app.OpenDocumentFile(rfa_path)
    DOCS.append(doc)
    REPORT['reopened'] = bool(doc.IsFamilyDocument)
    REPORT['category'] = doc.OwnerFamily.FamilyCategory.Name
    REPORT['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    REPORT['family_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    REPORT['rfa_bytes'] = os.path.getsize(rfa_path)
    REPORT['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(
        os.path.getmtime(rfa_path)).isoformat() + 'Z'

    body_bounds = bounds_for_ids(doc, REPORT['body_element_ids'])
    canopy_id = next(p['id'] for p in REPORT['parts']['suspension'] if p['name'] == 'Canopy')
    canopy_bounds = bounds_for_ids(doc, [canopy_id])
    REPORT['reopened_body_bounds_in'] = body_bounds
    REPORT['reopened_canopy_bounds_in'] = canopy_bounds
    dims = REPORT.setdefault('dimensions', {})
    check(dims, 'reopened_body_length', body_bounds['size'][0], OVERALL_L, DIM_TOL,
          'saved/reopened RFA union body bounding box')
    check(dims, 'reopened_body_width', body_bounds['size'][1], OVERALL_W, DIM_TOL,
          'saved/reopened RFA union body bounding box')
    check(dims, 'reopened_globe_body_height', body_bounds['size'][2], GLOBE_D, DIM_TOL,
          'saved/reopened RFA union body Z extent')
    check(dims, 'reopened_canopy_length', canopy_bounds['size'][0], CANOPY_L, DIM_TOL,
          'saved/reopened canopy X extent')
    check(dims, 'reopened_canopy_width', canopy_bounds['size'][1], CANOPY_W, DIM_TOL,
          'saved/reopened canopy Y extent')
    check(dims, 'reopened_canopy_height', canopy_bounds['size'][2], CANOPY_H, DIM_TOL,
          'saved/reopened canopy Z extent')

    # Confirm the requested type metadata/material parameters persisted.
    mgr = doc.FamilyManager
    REPORT['family_type'] = mgr.CurrentType.Name
    REPORT['saved_identity'] = {}
    for p in mgr.Parameters:
        nm = p.Definition.Name
        if nm in ('Manufacturer','Model','Lightology Spec','Finish','Shade Color','CCT'):
            REPORT['saved_identity'][nm] = mgr.CurrentType.AsString(p)
    REPORT['saved_material_ids'] = {}
    for nm in ('Metal Finish','Glass Finish'):
        p = next((x for x in mgr.Parameters if x.Definition.Name == nm), None)
        REPORT['saved_material_ids'][nm] = int(mgr.CurrentType.AsElementId(p).Value) if p else None

    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    fam = doc.LoadFamily(project)
    symbol = project.GetElement(list(fam.GetFamilySymbolIds())[0])

    TX = DB.Transaction(project, 'Cassia native host/material QA')
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    floor_type = DB.Floor.GetDefaultFloorType(project, False)
    slab = DB.CurveLoop()
    pts = [xyz(-80,-80,0), xyz(80,-80,0), xyz(80,80,0), xyz(-80,80,0)]
    for i in range(4):
        slab.Append(DB.Line.CreateBound(pts[i], pts[(i+1)%4]))
    floor = DB.Floor.Create(project, List[DB.CurveLoop]([slab]), floor_type, level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(20)
    symbol.Activate()
    project.Regenerate()
    reference = DB.HostObjectUtils.GetBottomFaces(floor)[0]
    face = floor.GetGeometryObjectFromReference(reference)
    point = face.Project(DB.XYZ(0,0,20)).XYZPoint
    inst = project.Create.NewFamilyInstance(reference, point, DB.XYZ.BasisX, symbol)
    project.Regenerate()

    host_face = inst.HostFace
    REPORT['host'] = {
        'host_element_id': int(floor.Id.Value),
        'host_type': element_name(project.GetElement(floor.GetTypeId())),
        'instance_host_id': int(inst.Host.Id.Value) if inst.Host else None,
        'instance_host_matches': bool(inst.Host and inst.Host.Id == floor.Id),
        'source_reference_element_id': int(reference.ElementId.Value),
        'host_face_reference_element_id': int(host_face.ElementId.Value) if host_face else None,
        'host_face_matches': bool(host_face and host_face.ElementId == floor.Id),
        'host_reference_stable': host_face.ConvertToStableRepresentation(project) if host_face else None,
        'host_face_z_in': point.Z * 12,
    }
    ib = inst.get_BoundingBox(None)
    REPORT['orientation'] = {
        'instance_min_z_in': ib.Min.Z * 12,
        'instance_max_z_in': ib.Max.Z * 12,
        'hangs_below_host': ib.Max.Z <= point.Z + 1e-5,
        'measured_drop_in': (point.Z - ib.Min.Z) * 12,
        'expected_drop_in': TOTAL_DROP,
        'drop_pass': abs((point.Z - ib.Min.Z)*12 - TOTAL_DROP) <= 0.08,
    }

    REPORT['material_tests'] = {}
    for nm in ('Metal Finish','Glass Finish'):
        p = symbol.LookupParameter(nm)
        original = p.AsElementId()
        alt = DB.Material.Create(project, 'Cassia QA Substitute ' + nm)
        p.Set(alt)
        project.Regenerate()
        face_ids = [f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        REPORT['material_tests'][nm] = {
            'parameter_writable': not p.IsReadOnly,
            'faces_inspected': len(face_ids),
            'faces_carrying_substitute': sum(1 for x in face_ids if x == alt),
            'reached_geometry': alt in face_ids,
            'substitute_material_id': int(alt.Value),
        }
        p.Set(original)
        project.Regenerate()
        REPORT['material_tests'][nm]['restored_material_id'] = int(p.AsElementId().Value)

    # Hosted evidence view.
    ib = inst.get_BoundingBox(None)
    eye = DB.XYZ(7, -9, point.Z - 1.5)
    target = DB.XYZ(0, 0, (point.Z + ib.Min.Z)/2.0)
    hview = family_view(project, 'Cassia Hosted', eye, target,
                        DB.XYZ(ib.Min.X-1, ib.Min.Y-1, ib.Min.Z-1),
                        DB.XYZ(ib.Max.X+1, ib.Max.Y+1, point.Z+0.5), realistic=False)
    TX.Commit()
    TX = None
    export_images(project, [hview], 'Cassia_Hosted')
    REPORT['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    REPORT['hosted_exports'] = sorted(
        n for n in os.listdir(out_path('evidence')) if n.startswith('Cassia_Hosted'))

    gates = {
        'revit_2025': str(REPORT.get('revit_version','')).startswith('2025'),
        'fresh_rfa_reopen': REPORT['reopened'],
        'lighting_fixtures_category': REPORT['category'] == 'Lighting Fixtures',
        'face_based_placement': 'FaceBased' in REPORT['placement_type'],
        'saved_dimensions': all(dims[k]['pass'] for k in (
            'reopened_body_length','reopened_body_width','reopened_globe_body_height',
            'reopened_canopy_length','reopened_canopy_width','reopened_canopy_height')),
        'requested_variant_persisted': (
            REPORT['family_type'] == 'LP549448AGOP - Aged Gold / Opal Matte'
            and REPORT['saved_identity'].get('Finish') == 'Aged Gold'
            and REPORT['saved_identity'].get('Shade Color') == 'Opal Matte'
            and REPORT['saved_identity'].get('Model') == 'LP549448AGOP'),
        'native_host_reference': REPORT['host']['instance_host_matches']
            and REPORT['host']['host_face_matches'],
        'correct_overhead_orientation': REPORT['orientation']['hangs_below_host']
            and REPORT['orientation']['drop_pass'],
        'material_substitution_reaches_geometry': all(
            x['parameter_writable'] and x['reached_geometry']
            for x in REPORT['material_tests'].values()),
        'zero_warnings': not REPORT['family_warnings'] and not REPORT['project_warnings'],
        'visual_exports_present': len(REPORT.get('family_exports',[])) >= 4
            and len(REPORT.get('hosted_exports',[])) >= 1,
    }
    REPORT['gates'] = gates
    REPORT['technical_pass'] = all(gates.values())
    REPORT['visual_verdict'] = 'PENDING SELF REVIEW'
    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    checkpoint('complete' if REPORT['technical_pass'] else 'gates-failed')
    if not REPORT['technical_pass']:
        raise RuntimeError('Cassia gate failures: ' + json.dumps(
            [k for k,v in gates.items() if not v]))


try:
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    REPORT['templates'] = {
        'face_based': FACE_TEMPLATE,
        'face_based_exists': os.path.isfile(FACE_TEMPLATE),
    }
    if not REPORT['templates']['face_based_exists']:
        raise RuntimeError('Revit 2025 face-based template not found: ' + FACE_TEMPLATE)
    if not str(app.VersionNumber).startswith('2025'):
        raise RuntimeError('Revit 2025 required, got ' + str(app.VersionNumber))
    checkpoint('building')
    path = build_family(app)
    checkpoint('validating')
    validate(app, path)
except Exception:
    REPORT['technical_pass'] = False
    REPORT['error'] = traceback.format_exc()
    try:
        checkpoint('failed')
    except Exception:
        pass
    raise
finally:
    if TX:
        try:
            TX.RollBack()
        except Exception:
            pass
    for d in reversed(DOCS):
        try:
            d.Close(False)
        except Exception:
            pass

