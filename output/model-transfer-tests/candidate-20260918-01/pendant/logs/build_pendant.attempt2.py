# -*- coding: utf-8 -*-
"""P01 model-transfer trial builder: baseline (A) and satin-brass 72 in variant (B).

Adapted from scripts/build_mila.py for docs/model-transfer-tests/PENDANT.md.
Run inside Revit 2025 through the pyRevit CLI. Ordinary CPython cannot execute
this file: it needs the Revit-hosted __revit__ handle and the .NET Revit API.

Adaptation summary (see PATH_AUDIT.md):
  * every write goes through out_path(), which refuses to leave RUN_DIR
  * source ROOT/OUT/RFA/TEMPLATE constants replaced; repo root is probed
  * nested body family and material element names are run-specific
  * both configurations are built from the same construction code in one run;
    no completed RFA is copied
  * gates are recorded explicitly and the script re-raises, because a clean
    pyRevit exit code alone is not evidence (ENVIRONMENT.md)
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

RUN_ID = 'candidate-20260918-01'

# PROMPT_PENDANT.md and ENVIRONMENT.md name the OneDrive checkout; the operator
# later reported a GitHub checkout. Probe both instead of hard-coding one.
REPO_ROOT_CANDIDATES = [
    r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow',
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow',
]
TEMPLATE_DIR = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial'
FACE_TEMPLATE = os.path.join(TEMPLATE_DIR, 'Generic Model face based.rft')
BODY_TEMPLATE = os.path.join(TEMPLATE_DIR, 'Generic Model.rft')

# Dimensions in inches. Sources: Lightology sheet MMK661292 for the loop, canopy
# and frame thickness; globe diameter and band depth are inferred (INFERENCES.md).
LOOP_W, LOOP_H, FRAME_T, BAND_D = 8.2, 29.1, 0.5, 0.5
CANOPY_D, CANOPY_H = 7.1, 1.1
GLOBE_D = 6.7
GLOBE_CENTRE_Z = 25.20          # body-local Z; local +Z runs downward once hosted
SOCKET_R, SOCKET_TOP, SOCKET_BOT = 0.23, -0.35, 0.1
SEAT_R, SEAT_TOP, SEAT_BOT = 0.35, 28.5, 28.65
DROP_CONSTANT = 30.55           # canopy 1.1 + socket 0.35 + loop 29.1
DIM_TOL = 0.01
DROP_TOL = 0.1

BASE_GLASS = {'color': (247, 244, 230), 'gloss': 0.65, 'refl0': 0.08,
              'refl90': 0.85, 'transparency': 0.08, 'self_illum': 100.0,
              'material_class': 'Glass'}

CONFIGS = [
    {
        'key': 'baseline',
        'label': 'A - reproduction',
        'rfa': 'Mila_Trial_Dark_Adjustable_R2025.rfa',
        'body_rfa': 'Mila_Trial_Body_Baseline.rfa',
        'type_name': 'Mila Black',
        'material_prefix': 'Mila Trial Baseline',
        'image_prefix': 'Baseline',
        'total_drop': 60.0,
        'flex': [8.0, 18.1496062992, 48.0, 118.0],
        'metal': {'color': (53, 50, 44), 'gloss': 0.42, 'refl0': 0.22,
                  'refl90': 0.85, 'transparency': 0.0, 'self_illum': 0.0,
                  'material_class': 'Metal'},
        'glass': BASE_GLASS,
        'appearance_note': 'Dark metal and dark canopy, warm opal glass; source-approved finish.',
    },
    {
        'key': 'variant',
        'label': 'B - controlled variation, satin brass, 72 in default',
        'rfa': 'Mila_Trial_SatinBrass_72in_R2025.rfa',
        'body_rfa': 'Mila_Trial_Body_SatinBrass.rfa',
        'type_name': 'Mila Satin Brass 72in',
        'material_prefix': 'Mila Trial SatinBrass',
        'image_prefix': 'Variant',
        'total_drop': 72.0,
        'flex': [12.0, 60.0],
        'metal': {'color': (186, 166, 112), 'gloss': 0.50, 'refl0': 0.28,
                  'refl90': 0.85, 'transparency': 0.0, 'self_illum': 0.0,
                  'material_class': 'Metal'},
        'glass': BASE_GLASS,
        'appearance_note': ('Satin brass requested by the user. Diffuse RGB 186,166,112 '
                            'chosen below the median of brass pixels sampled from '
                            'references/mila/product-sheet.png (median 194,175,122; '
                            'p10 178,158,106; p90 226,208,147) so rendered specular lift '
                            'does not double-count. Independent visual variant; no SKU asserted.'),
    },
]


def element_name(element):
    """Read Element.Name safely.

    Document.GetElement returns a statically typed Element, and the IronPython
    binder on the pyRevit .NET Core engine cannot resolve Element.Name through
    that reference (MissingMemberException: Name — attempt 1, 2026-09-18).
    Concrete types such as Material, Category and View bind normally. Go through
    the property descriptor, and fall back to the type-name parameter.
    """
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        param = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return param.AsString() if param else None


def repo_root():
    for candidate in REPO_ROOT_CANDIDATES:
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, 'AGENTS.md')):
            return candidate
    raise RuntimeError('No repository root found among: ' + ' | '.join(REPO_ROOT_CANDIDATES))


ROOT = repo_root()
RUN_DIR = os.path.join(ROOT, 'output', 'model-transfer-tests', RUN_ID, 'pendant')
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)

REPORT = {
    'run_id': RUN_ID,
    'script': 'build_pendant.py',
    'repo_root': ROOT,
    'run_dir': RUN_DIR,
    'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'specification': 'docs/model-transfer-tests/PENDANT.md',
    'dimension_tolerance_in': DIM_TOL,
    'drop_tolerance_in': DROP_TOL,
    'configs': {},
}
DOCS = []
TX = None


def out_path(*parts):
    """Join under RUN_DIR and refuse any path that escapes it."""
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if target != _RUN_DIR_NORM and not target.startswith(_RUN_DIR_NORM + os.sep):
        raise RuntimeError('Write path escapes the run directory: ' + target)
    parent = os.path.dirname(target)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    REPORT['checkpoint_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    payload = json.dumps(REPORT, indent=2, default=str, sort_keys=True)
    with open(out_path('validation.json'), 'w') as handle:
        handle.write(payload)
    # Attempt-retained copy: PENDANT.md requires evidence of every attempt.
    stamp = REPORT['started_utc'].replace(':', '').replace('-', '').replace('.', '')
    with open(out_path('logs', 'validation-%s.json' % stamp), 'w') as handle:
        handle.write(payload)


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid


def element_solids(element):
    return list(solids(element.get_Geometry(DB.Options())))


def bbox_inches(element):
    box = element.get_BoundingBox(None)
    return {'min': [box.Min.X * 12, box.Min.Y * 12, box.Min.Z * 12],
            'max': [box.Max.X * 12, box.Max.Y * 12, box.Max.Z * 12],
            'size': [(box.Max.X - box.Min.X) * 12,
                     (box.Max.Y - box.Min.Y) * 12,
                     (box.Max.Z - box.Min.Z) * 12]}


def ray_segments(element, start, end):
    """Measure the solid material a line crosses. Returns inch-space segments."""
    line = DB.Line.CreateBound(xyz(*start), xyz(*end))
    found = []
    for solid in element_solids(element):
        result = solid.IntersectWithCurve(line, DB.SolidCurveIntersectionOptions())
        for index in range(result.SegmentCount):
            segment = result.GetCurveSegment(index)
            p0, p1 = segment.GetEndPoint(0), segment.GetEndPoint(1)
            found.append({'length': segment.Length * 12,
                          'from': [p0.X * 12, p0.Y * 12, p0.Z * 12],
                          'to': [p1.X * 12, p1.Y * 12, p1.Z * 12]})
    found.sort(key=lambda s: (s['from'][0], s['from'][1], s['from'][2]))
    return found


def check(bucket, name, measured, target, tolerance, method):
    entry = {'measured_in': measured, 'target_in': target,
             'tolerance_in': tolerance, 'method': method}
    entry['pass'] = measured is not None and abs(measured - target) <= tolerance
    bucket[name] = entry
    return entry['pass']


def profile_loop(origin, u, v, points):
    def point(pair):
        return origin.Add(u.Multiply(pair[0] / 12.0)).Add(v.Multiply(pair[1] / 12.0))
    loop = DB.CurveLoop()
    current = points[0]
    for item in points[1:]:
        if len(item) == 3 and item[0] == 'arc':
            mid, end = item[1], item[2]
            loop.Append(DB.Arc.Create(point(current), point(end), point(mid)))
        else:
            end = item
            loop.Append(DB.Line.CreateBound(point(current), point(end)))
        current = end
    if current != points[0]:
        loop.Append(DB.Line.CreateBound(point(current), point(points[0])))
    return loop


def stadium(half_width, bottom_cap_z, top_cap_z, cap_radius):
    """Outer or inner boundary of the capsule loop, in profile inches."""
    return [(half_width, bottom_cap_z),
            (half_width, top_cap_z),
            ('arc', (0, top_cap_z + cap_radius), (-half_width, top_cap_z)),
            (-half_width, bottom_cap_z),
            ('arc', (0, bottom_cap_z - cap_radius), (half_width, bottom_cap_z))]


def revolved(doc, parts, name, origin, axis, points, param, category):
    radial = DB.XYZ.BasisX if abs(axis.Z) > 0.99 else DB.XYZ.BasisZ
    radial = radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop = profile_loop(origin, radial, axis, points)
    frame = DB.Frame(origin, radial, axis.CrossProduct(radial), axis)
    solid = DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, List[DB.CurveLoop]([loop]), 0, 2 * math.pi)
    element = DB.FreeFormElement.Create(doc, solid)
    element.Subcategory = category
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), param)
    parts.append({'name': name, 'id': str(element.Id.Value)})
    return element


def cylinder(doc, parts, name, origin, axis, radius, start, end, param, category):
    points = [(0, start), (radius, start), (radius, end), (0, end)]
    return revolved(doc, parts, name, origin, axis, points, param, category)


def clone_material(doc, name, asset, color, transparency):
    existing = next((m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)
                     if m.Name == name), None)
    if existing:
        return existing, doc.GetElement(existing.AppearanceAssetId)
    appearance = DB.AppearanceAssetElement.Create(doc, name, asset)
    material = doc.GetElement(DB.Material.Create(doc, name))
    material.AppearanceAssetId = appearance.Id
    material.Color = DB.Color(*color)
    material.Transparency = transparency
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


def make_materials(doc, app, cfg):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next(a for a in assets
                  if a.FindByName('BaseSchema') is not None
                  and a.FindByName('BaseSchema').Value == 'GenericSchema')
    result = {}
    for param_name, spec in [('Metal Finish', cfg['metal']), ('Glass Finish', cfg['glass'])]:
        name = '%s - %s' % (cfg['material_prefix'], param_name)
        material, appearance = clone_material(doc, name, source, spec['color'], 0)
        scope = DB.Visual.AppearanceAssetEditScope(doc)
        asset = scope.Start(appearance.Id)
        set_color(asset, 'generic_diffuse', spec['color'])
        scalar(asset, 'generic_glossiness', spec['gloss'])
        scalar(asset, 'generic_transparency', spec['transparency'])
        scalar(asset, 'generic_reflectivity_at_0deg', spec['refl0'])
        scalar(asset, 'generic_reflectivity_at_90deg', spec['refl90'])
        scalar(asset, 'generic_self_illum_luminance', spec['self_illum'])
        scope.Commit(True)
        scope.Dispose()
        material.Transparency = int(round(spec['transparency'] * 100))
        material.MaterialClass = spec['material_class']
        result[param_name] = material
    return result


def setup(doc, app, cfg):
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(
        doc, DB.BuiltInCategory.OST_LightingFixtures)
    always_vertical = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if always_vertical:
        always_vertical.Set(0)
    manager = doc.FamilyManager
    manager.NewType(cfg['type_name'])
    params = {}
    for name, material in make_materials(doc, app, cfg).items():
        param = manager.AddParameter(name, DB.GroupTypeId.Materials,
                                     DB.SpecTypeId.Reference.Material, False)
        manager.Set(param, material.Id)
        params[name] = param
    return manager, params


def family_view(doc, name, eye, top_z):
    view_type = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
                     if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, view_type.Id)
    view.Name = name
    forward = xyz(0, 0, top_z / 2.0).Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ.Negate()
    if abs(forward.DotProduct(up)) > 0.99:
        up = DB.XYZ.BasisY
    right = forward.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(forward).Normalize(), forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.Scale = 1
    view.DisplayStyle = DB.DisplayStyle.Shading
    for category in doc.Settings.Categories:
        if category.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(category.Id):
            view.SetCategoryHidden(category.Id, True)
    box = DB.BoundingBoxXYZ()
    box.Min = xyz(-6, -6, 0.001)
    box.Max = xyz(6, 6, top_z + 1)
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    return view


def hosted_view(doc, name, eye, target, box_min, box_max):
    view_type = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
                     if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, view_type.Id)
    view.Name = name
    forward = target.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ
    if abs(forward.DotProduct(up)) > 0.99:
        up = DB.XYZ.BasisY
    right = forward.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(forward).Normalize(), forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    box = DB.BoundingBoxXYZ()
    box.Min = box_min
    box.Max = box_max
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    return view


def export_images(doc, views, prefix):
    options = DB.ImageExportOptions()
    options.ExportRange = DB.ExportRange.SetOfViews
    options.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    options.FilePath = out_path('evidence', prefix)
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ShadowViewsFileType = DB.ImageFileType.PNG
    options.ImageResolution = DB.ImageResolution.DPI_150
    options.ZoomType = DB.ZoomFitType.FitToPage
    options.PixelSize = 1600
    doc.ExportImage(options)


def build_body(app, cfg, record):
    """Nested fixed body: capsule loop, opal globe, socket and globe seat."""
    global TX
    doc = app.NewFamilyDocument(BODY_TEMPLATE)
    DOCS.append(doc)
    TX = DB.Transaction(doc, 'Build pendant body')
    TX.Start()
    manager, params = setup(doc, app, cfg)
    frame_cat = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Mobile Frame')
    glass_cat = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, 'Luminous Acrylic')
    metal, glass = params['Metal Finish'], params['Glass Finish']
    parts = record.setdefault('body_parts', [])

    half = LOOP_W / 2.0
    cap = half
    bottom_cap_z, top_cap_z = cap, LOOP_H - cap
    inner_half = half - FRAME_T
    outer = profile_loop(xyz(0, -BAND_D / 2.0, 0), DB.XYZ.BasisX, DB.XYZ.BasisZ,
                         stadium(half, bottom_cap_z, top_cap_z, cap))
    inner = profile_loop(xyz(0, -BAND_D / 2.0, 0), DB.XYZ.BasisX, DB.XYZ.BasisZ,
                         stadium(inner_half, bottom_cap_z, top_cap_z, inner_half))
    solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(
        List[DB.CurveLoop]([outer, inner]), DB.XYZ.BasisY, BAND_D / 12.0)
    loop_element = DB.FreeFormElement.Create(doc, solid)
    loop_element.Subcategory = frame_cat
    manager.AssociateElementParameterToFamilyParameter(
        loop_element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), metal)
    parts.append({'name': 'Capsule loop', 'id': str(loop_element.Id.Value)})

    globe = revolved(doc, parts, 'Opal globe', xyz(0, 0, GLOBE_CENTRE_Z), DB.XYZ.BasisZ,
                     [(0, -GLOBE_D / 2.0), ('arc', (GLOBE_D / 2.0, 0), (0, GLOBE_D / 2.0))],
                     glass, glass_cat)
    socket = cylinder(doc, parts, 'Upper cable socket', DB.XYZ.Zero, DB.XYZ.BasisZ,
                      SOCKET_R, SOCKET_TOP, SOCKET_BOT, metal, frame_cat)
    seat = cylinder(doc, parts, 'Globe seat', DB.XYZ.Zero, DB.XYZ.BasisZ,
                    SEAT_R, SEAT_TOP, SEAT_BOT, metal, frame_cat)
    doc.Regenerate()   # omitting this previously produced None bounds

    every = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    boxes = [e.get_BoundingBox(None) for e in every]
    record['body_bounds_inches'] = [
        min(b.Min.X for b in boxes) * 12, min(b.Min.Y for b in boxes) * 12,
        min(b.Min.Z for b in boxes) * 12, max(b.Max.X for b in boxes) * 12,
        max(b.Max.Y for b in boxes) * 12, max(b.Max.Z for b in boxes) * 12]
    record['part_bounds_inches'] = {
        'capsule_loop': bbox_inches(loop_element), 'opal_globe': bbox_inches(globe),
        'upper_cable_socket': bbox_inches(socket), 'globe_seat': bbox_inches(seat)}

    mid_z = LOOP_H / 2.0
    dims = record.setdefault('dimensions', {})
    loop_box = record['part_bounds_inches']['capsule_loop']
    check(dims, 'loop_outer_width', loop_box['size'][0], LOOP_W, DIM_TOL,
          'Capsule loop element bounding box, X extent')
    check(dims, 'loop_outer_height', loop_box['size'][2], LOOP_H, DIM_TOL,
          'Capsule loop element bounding box, Z extent')
    check(dims, 'band_depth', loop_box['size'][1], BAND_D, DIM_TOL,
          'Capsule loop element bounding box, Y extent')

    across = ray_segments(loop_element, (-LOOP_W, 0, mid_z), (LOOP_W, 0, mid_z))
    record['loop_ray_segments'] = across
    if len(across) == 2:
        check(dims, 'frame_thickness_left', across[0]['length'], FRAME_T, DIM_TOL,
              'Solid.IntersectWithCurve along +X at Z=%.2f in, left strap' % mid_z)
        check(dims, 'frame_thickness_right', across[1]['length'], FRAME_T, DIM_TOL,
              'Solid.IntersectWithCurve along +X at Z=%.2f in, right strap' % mid_z)
        check(dims, 'loop_inner_width', across[1]['from'][0] - across[0]['to'][0],
              LOOP_W - 2 * FRAME_T, DIM_TOL,
              'Gap between the two strap ray segments at Z=%.2f in' % mid_z)
    else:
        dims['frame_thickness_left'] = {'pass': False, 'measured_in': None,
                                        'method': 'ray returned %d segments, expected 2' % len(across)}

    globe_ray = ray_segments(globe, (-LOOP_W, 0, GLOBE_CENTRE_Z), (LOOP_W, 0, GLOBE_CENTRE_Z))
    record['globe_ray_segments'] = globe_ray
    check(dims, 'globe_diameter', globe_ray[0]['length'] if globe_ray else None,
          GLOBE_D, DIM_TOL,
          'Solid.IntersectWithCurve through the globe solid at its centre Z')

    globe_box = record['part_bounds_inches']['opal_globe']
    record['globe_centre_above_loop_bottom_in'] = LOOP_H - GLOBE_CENTRE_Z
    record['globe_clear_of_inner_cap_in'] = (LOOP_H - FRAME_T) - globe_box['max'][2]
    record['socket_projection_above_loop_in'] = -record['part_bounds_inches']['upper_cable_socket']['min'][2]
    record['body_height_including_socket_in'] = (record['body_bounds_inches'][5]
                                                 - record['body_bounds_inches'][2])

    TX.Commit()
    TX = None
    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    body_path = out_path(cfg['body_rfa'])
    doc.SaveAs(body_path, save)
    record['body_rfa_path'] = body_path
    return doc


def build_parent(app, cfg, body_doc, record):
    """Face-based parent: canopy, cord and the nested body on an adjustable drop."""
    global TX
    doc = app.NewFamilyDocument(FACE_TEMPLATE)
    DOCS.append(doc)
    family = body_doc.LoadFamily(doc)
    TX = DB.Transaction(doc, 'Adjustable suspension')
    TX.Start()
    manager, params = setup(doc, app, cfg)
    default_cord = cfg['total_drop'] - DROP_CONSTANT

    cord = manager.AddParameter('Cord Length', DB.GroupTypeId.Geometry,
                                DB.SpecTypeId.Length, True)
    manager.Set(cord, default_cord / 12.0)
    offset = manager.AddParameter('Assembly Offset', DB.GroupTypeId.Geometry,
                                  DB.SpecTypeId.Length, True)
    manager.SetFormula(offset, 'Cord Length + %s in' % (CANOPY_H - SOCKET_TOP))
    total = manager.AddParameter('Total Drop', DB.GroupTypeId.Geometry,
                                 DB.SpecTypeId.Length, True)
    manager.SetFormula(total, 'Cord Length + %s in' % DROP_CONSTANT)
    record['requested_default_cord_in'] = default_cord
    record['requested_default_total_drop_in'] = cfg['total_drop']

    suspension = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,
                                                        'Canopy and Suspension')
    parts = record.setdefault('parent_parts', [])
    canopy = cylinder(doc, parts, 'Canopy', DB.XYZ.Zero, DB.XYZ.BasisZ,
                      CANOPY_D / 2.0, 0, CANOPY_H, params['Metal Finish'], suspension)

    symbol = doc.GetElement(list(family.GetFamilySymbolIds())[0])
    symbol.Activate()
    instance = doc.FamilyCreate.NewFamilyInstance(
        xyz(0, 0, cfg['total_drop'] - LOOP_H), symbol, DB.Structure.StructuralType.NonStructural)
    doc.Regenerate()
    record['nested_parameters'] = [(p.Definition.Name, str(p.Id.Value), p.IsReadOnly)
                                   for p in instance.Parameters]

    elevation = instance.get_Parameter(DB.BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM)
    if elevation is None:
        elevation = instance.get_Parameter(DB.BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM)
    if elevation is None:
        raise RuntimeError('Nested elevation parameter not found')
    manager.AssociateElementParameterToFamilyParameter(elevation, offset)
    for name, param in params.items():
        manager.AssociateElementParameterToFamilyParameter(symbol.LookupParameter(name), param)

    plane = DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ, DB.XYZ.Zero))
    curves = DB.CurveArray()
    for start, end in [(0, math.pi), (math.pi, 2 * math.pi)]:
        curves.Append(DB.Arc.Create(DB.XYZ.Zero, 0.06 / 12, start, end,
                                    DB.XYZ.BasisX, DB.XYZ.BasisY))
    array = DB.CurveArrArray()
    array.Append(curves)
    extrusion = doc.FamilyCreate.NewExtrusion(True, array, plane, 2)
    extrusion.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(CANOPY_H / 12.0)
    manager.AssociateElementParameterToFamilyParameter(
        extrusion.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), offset)
    manager.AssociateElementParameterToFamilyParameter(
        extrusion.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), params['Metal Finish'])
    doc.Regenerate()

    canopy_box = bbox_inches(canopy)
    record['canopy_bounds_inches'] = canopy_box
    dims = record.setdefault('dimensions', {})
    check(dims, 'canopy_diameter', canopy_box['size'][0], CANOPY_D, DIM_TOL,
          'Canopy element bounding box, X extent')
    check(dims, 'canopy_height', canopy_box['size'][2], CANOPY_H, DIM_TOL,
          'Canopy element bounding box, Z extent')
    canopy_ray = ray_segments(canopy, (-CANOPY_D, 0, CANOPY_H / 2.0), (CANOPY_D, 0, CANOPY_H / 2.0))
    check(dims, 'canopy_diameter_ray', canopy_ray[0]['length'] if canopy_ray else None,
          CANOPY_D, DIM_TOL, 'Solid.IntersectWithCurve through the canopy at mid height')

    views = [family_view(doc, 'Full Oblique', xyz(90, -130, 15), cfg['total_drop']),
             family_view(doc, 'Front', xyz(0, -160, 32), cfg['total_drop']),
             family_view(doc, 'Side', xyz(160, 0, 32), cfg['total_drop'])]
    TX.Commit()
    TX = None

    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    save.PreviewViewId = views[0].Id
    rfa_path = out_path(cfg['rfa'])
    doc.SaveAs(rfa_path, save)
    export_images(doc, views, cfg['image_prefix'])
    record['rfa_path'] = rfa_path
    record['family_images'] = sorted(name for name in os.listdir(out_path('evidence'))
                                     if name.startswith(cfg['image_prefix']))
    DOCS.remove(doc)
    doc.Close(False)
    return rfa_path


def validate(app, cfg, rfa_path, record):
    """Reopen, host on a native overhead face, flex, substitute materials, review."""
    global TX
    doc = app.OpenDocumentFile(rfa_path)
    DOCS.append(doc)
    record['reopened'] = doc.IsFamilyDocument
    record['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    record['category'] = doc.OwnerFamily.FamilyCategory.Name
    record['family_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    record['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(
        os.path.getmtime(rfa_path)).isoformat() + 'Z'
    record['rfa_bytes'] = os.path.getsize(rfa_path)

    manager = doc.FamilyManager
    saved = {}
    for param in manager.Parameters:
        name = param.Definition.Name
        if name in ('Cord Length', 'Total Drop', 'Assembly Offset'):
            value = manager.CurrentType.AsDouble(param)
            saved[name] = None if value is None else value * 12
    record['saved_type_values_in'] = saved
    dims = record.setdefault('dimensions', {})
    check(dims, 'saved_default_total_drop', saved.get('Total Drop'),
          cfg['total_drop'], DIM_TOL, 'FamilyManager.CurrentType value in the reopened RFA')

    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    family = doc.LoadFamily(project)
    symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])

    TX = DB.Transaction(project, 'Host on a native overhead face and flex')
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    floor_type = DB.Floor.GetDefaultFloorType(project, False)
    slab = profile_loop(DB.XYZ.Zero, DB.XYZ.BasisX, DB.XYZ.BasisY,
                        [(-100, -100), (100, -100), (100, 100), (-100, 100)])
    floor = DB.Floor.Create(project, List[DB.CurveLoop]([slab]), floor_type, level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(20)
    symbol.Activate()
    project.Regenerate()

    reference = DB.HostObjectUtils.GetBottomFaces(floor)[0]
    face = floor.GetGeometryObjectFromReference(reference)
    point = face.Project(DB.XYZ(0, 0, 20)).XYZPoint
    instance = project.Create.NewFamilyInstance(reference, point, DB.XYZ.BasisX, symbol)
    project.Regenerate()
    record['host_element_id'] = str(floor.Id.Value)
    record['host_type'] = element_name(project.GetElement(floor.GetTypeId()))
    record['host_face_z_ft'] = point.Z
    record['loaded_and_face_placed'] = instance.Host.Id == floor.Id

    box = instance.get_BoundingBox(None)
    record['orientation'] = {
        'host_face_z_in': point.Z * 12,
        'instance_min_z_in': box.Min.Z * 12,
        'instance_max_z_in': box.Max.Z * 12,
        'hangs_below_host': box.Max.Z <= point.Z + 1e-6,
    }

    drop_param = instance.LookupParameter('Total Drop')
    cord_param = instance.LookupParameter('Cord Length')
    record['total_drop_is_read_only'] = drop_param.IsReadOnly
    record['cord_length_is_read_only'] = cord_param.IsReadOnly
    check(dims, 'placed_default_total_drop', drop_param.AsDouble() * 12,
          cfg['total_drop'], DIM_TOL, 'Total Drop on the hosted instance before flexing')

    record['flex_tests'] = []
    for length in cfg['flex']:
        cord_param.Set(length / 12.0)
        project.Regenerate()
        flexed = instance.get_BoundingBox(None)
        actual = (point.Z - flexed.Min.Z) * 12
        formula = drop_param.AsDouble() * 12
        expected = length + DROP_CONSTANT
        record['flex_tests'].append({
            'cord_inches': length,
            'formula_total_drop_in': formula,
            'measured_drop_in': actual,
            'expected_drop_in': expected,
            'tolerance_in': DROP_TOL,
            'method': 'host face Z minus instance bounding box minimum Z',
            'formula_pass': abs(formula - expected) <= DIM_TOL,
            'measured_pass': abs(actual - expected) <= DROP_TOL,
            'body_height_in': (flexed.Max.Z - flexed.Min.Z) * 12,
        })
    cord_param.Set((cfg['total_drop'] - DROP_CONSTANT) / 12.0)
    project.Regenerate()
    record['cord_restored_in'] = cord_param.AsDouble() * 12

    # Body geometry must not change across flex states.
    heights = [t['body_height_in'] for t in record['flex_tests']]
    record['body_height_stable'] = bool(heights) and (max(heights) - min(heights)) <= DIM_TOL

    record['material_tests'] = {}
    for name in ('Metal Finish', 'Glass Finish'):
        type_param = symbol.LookupParameter(name)
        original = type_param.AsElementId()
        alternate = DB.Material.Create(project, 'QA %s %s' % (cfg['key'], name))
        type_param.Set(alternate)
        project.Regenerate()
        face_ids = [f.MaterialElementId
                    for solid in solids(instance.get_Geometry(DB.Options()))
                    for f in solid.Faces]
        record['material_tests'][name] = {
            'type_parameter_writable': not type_param.IsReadOnly,
            'substitute_material_id': str(alternate.Value),
            'faces_inspected': len(face_ids),
            'faces_carrying_substitute': sum(1 for i in face_ids if i == alternate),
            'distinct_material_ids': sorted(set(str(i.Value) for i in face_ids)),
            'reached_nested_geometry': alternate in face_ids,
        }
        type_param.Set(original)
        project.Regenerate()
        record['material_tests'][name]['restored_material_id'] = str(
            symbol.LookupParameter(name).AsElementId().Value)

    fixture = instance.get_BoundingBox(None)
    pad = 2.0
    view_min = DB.XYZ(fixture.Min.X - pad, fixture.Min.Y - pad, fixture.Min.Z - pad)
    view_max = DB.XYZ(fixture.Max.X + pad, fixture.Max.Y + pad, point.Z + 0.5)
    eye = DB.XYZ(fixture.Max.X + 12, fixture.Min.Y - 16, point.Z - 2)
    target = DB.XYZ(0, 0, (point.Z + fixture.Min.Z) / 2.0)
    hosted = hosted_view(project, 'Hosted Fixture', eye, target, view_min, view_max)
    TX.Commit()
    TX = None

    export_images(project, [hosted], cfg['image_prefix'] + '_Hosted')
    record['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    record['hosted_images'] = sorted(name for name in os.listdir(out_path('evidence'))
                                     if name.startswith(cfg['image_prefix'] + '_Hosted'))

    reopened = app.OpenDocumentFile(rfa_path)
    DOCS.append(reopened)
    final = {}
    for param in reopened.FamilyManager.Parameters:
        if param.Definition.Name == 'Total Drop':
            final['Total Drop'] = reopened.FamilyManager.CurrentType.AsDouble(param) * 12
    record['final_saved_total_drop_in'] = final.get('Total Drop')
    check(dims, 'default_preserved_after_flex', final.get('Total Drop'),
          cfg['total_drop'], DIM_TOL,
          'RFA reopened after the flex battery; flexing touched the project instance only')


def gate_summary(record):
    dims = record.get('dimensions', {})

    def dim(*names):
        return all(dims.get(n, {}).get('pass') is True for n in names)

    gates = {
        'fresh_rfa_reopen_category': bool(record.get('reopened'))
            and record.get('category') == 'Lighting Fixtures',
        'native_overhead_hosting_and_orientation': bool(record.get('loaded_and_face_placed'))
            and bool(record.get('orientation', {}).get('hangs_below_host')),
        'loop_and_canopy_dimensions': dim('loop_outer_width', 'loop_outer_height', 'band_depth',
                                          'frame_thickness_left', 'frame_thickness_right',
                                          'loop_inner_width', 'globe_diameter',
                                          'canopy_diameter', 'canopy_height'),
        'saved_default_total_drop': dim('saved_default_total_drop', 'placed_default_total_drop',
                                        'default_preserved_after_flex'),
        'measured_flex_tests': bool(record.get('flex_tests'))
            and all(t['formula_pass'] and t['measured_pass'] for t in record['flex_tests'])
            and bool(record.get('body_height_stable')),
        'materials_reach_nested_geometry': all(
            v.get('reached_nested_geometry') for v in record.get('material_tests', {}).values())
            and len(record.get('material_tests', {})) == 2,
        'zero_unexplained_warnings': not record.get('family_warnings')
            and not record.get('project_warnings'),
        'visual_exports_present': len(record.get('family_images', [])) >= 3
            and len(record.get('hosted_images', [])) >= 1,
    }
    record['gates'] = gates
    record['technical_pass'] = all(gates.values())
    record['visual_verdict'] = 'PENDING REVIEWER - exports produced, fidelity not self-assessed'
    return gates


try:
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    REPORT['templates'] = {'face_based': FACE_TEMPLATE, 'body': BODY_TEMPLATE,
                           'face_based_exists': os.path.isfile(FACE_TEMPLATE),
                           'body_exists': os.path.isfile(BODY_TEMPLATE)}
    if not (REPORT['templates']['face_based_exists'] and REPORT['templates']['body_exists']):
        raise RuntimeError('Revit 2025 English-Imperial family templates not found')
    if not app.VersionNumber.startswith('2025'):
        raise RuntimeError('Revit 2025 required; host reports ' + str(app.VersionNumber))

    for cfg in CONFIGS:
        record = {'label': cfg['label'], 'type_name': cfg['type_name'],
                  'appearance_note': cfg['appearance_note'],
                  'metal_appearance': cfg['metal'], 'glass_appearance': cfg['glass'],
                  'started_utc': datetime.datetime.utcnow().isoformat() + 'Z'}
        REPORT['configs'][cfg['key']] = record
        checkpoint('building:' + cfg['key'])
        body_doc = build_body(app, cfg, record)
        rfa_path = build_parent(app, cfg, body_doc, record)
        DOCS.remove(body_doc)
        body_doc.Close(False)
        validate(app, cfg, rfa_path, record)
        gate_summary(record)
        record['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
        checkpoint('validated:' + cfg['key'])

    REPORT['technical_pass'] = all(r.get('technical_pass') for r in REPORT['configs'].values())
    REPORT['failed_gates'] = {key: [g for g, ok in rec.get('gates', {}).items() if not ok]
                              for key, rec in REPORT['configs'].items()}
    checkpoint('complete' if REPORT['technical_pass'] else 'gates-failed')
    if not REPORT['technical_pass']:
        raise RuntimeError('Gate failures: ' + json.dumps(REPORT['failed_gates']))
except Exception:
    REPORT['error'] = traceback.format_exc()
    REPORT['technical_pass'] = False
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
    for document in reversed(DOCS):
        try:
            document.Close(False)
        except Exception:
            pass
