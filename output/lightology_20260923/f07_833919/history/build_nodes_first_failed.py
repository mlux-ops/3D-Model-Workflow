# -*- coding: utf-8 -*-
"""Build and validate Visual Comfort Studio / Kelly Wearstler Nodes KW1041.

Creates two independent Revit 2025 face-based Lighting Fixtures families:
- KW1041BBS Burnished Brass / Milk
- KW1041MBK Midnight Black / Milk

Run with pyRevit CLI against Revit 2025 using this file's absolute path.
Only new documents and output/lightology_20260923/f07_833919 are modified,
plus one minimal append-only PROJECT_MEMORY.md error note when needed.
"""
import os
import json
import math
import traceback
import datetime
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f07_833919')
EVIDENCE = os.path.join(OUT, 'evidence')
SOURCES = os.path.join(OUT, 'sources')
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
PROJECT_MEMORY = os.path.join(ROOT, 'PROJECT_MEMORY.md')

# Published dimensions, inches.
OVERALL_W = 8.0
OVERALL_H = 7.63
OVERALL_D = 5.5
BACKPLATE_D = 5.25
BACKPLATE_DEPTH = 0.125
SHADE_D = 3.5
SHADE_AXIAL_H = 3.25
REFLECTOR_D = 8.0
REFLECTOR_T = 0.08
TILT_DEG = 18.0
TILT = math.radians(TILT_DEG)
AXIS = DB.XYZ(0.0, -math.sin(TILT), math.cos(TILT))
PIVOT_Z = 1.82
DISC_CENTER_T = 0.16
GLOBE_BACK_T = 0.62
HOUSING_BACK_R = 2.30
HOUSING_FRONT_R = 1.62
HOUSING_FRONT_Z = PIVOT_Z
SOCKET_R = 0.34
SOCKET_END_T = 0.68
CUT_R = math.sqrt((SHADE_D / 2.0) ** 2 - (1.5 ** 2))
DIM_TOL = 0.04
DEPTH_TOL = 0.05

CONFIGS = [
    {
        'key': 'brass',
        'finish': 'Burnished Brass',
        'sku': 'VCS833918',
        'model': 'KW1041BBS',
        'type_name': 'KW1041BBS - Burnished Brass / Milk',
        'rfa': 'Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa',
        'prefix': 'Nodes_KW1041BBS',
        'metal_rgb': (184, 132, 52),
        'metal_gloss': 0.43,
        'metal_refl': 0.48,
        'option_url': 'https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833918',
    },
    {
        'key': 'black',
        'finish': 'Midnight Black',
        'sku': 'VCS833919',
        'model': 'KW1041MBK',
        'type_name': 'KW1041MBK - Midnight Black / Milk',
        'rfa': 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa',
        'prefix': 'Nodes_KW1041MBK',
        'metal_rgb': (24, 24, 25),
        'metal_gloss': 0.22,
        'metal_refl': 0.18,
        'option_url': 'https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833919',
    },
]

RUN_STAMP = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
REPORT_PATH = os.path.join(OUT, 'validation_nodes_' + RUN_STAMP + '.json')
LATEST_PATH = os.path.join(OUT, 'validation_latest.json')
REPORT = {
    'fixture': 'Nodes Angled Wall Sconce',
    'designer': 'Kelly Wearstler',
    'manufacturer': 'Visual Comfort Studio',
    'product_family': 'KW1041',
    'assignment_url': 'https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833918',
    'run_stamp_utc': RUN_STAMP,
    'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'published_dimensions_in': {
        'overall_width': OVERALL_W,
        'overall_height': OVERALL_H,
        'overall_projection': OVERALL_D,
        'backplate_diameter': BACKPLATE_D,
        'backplate_depth': BACKPLATE_DEPTH,
        'shade_diameter': SHADE_D,
        'shade_axial_height': SHADE_AXIAL_H,
    },
    'geometry_inferences': {
        'reflector_disc_diameter': REFLECTOR_D,
        'reflector_disc_thickness': REFLECTOR_T,
        'reflector_tilt_degrees': TILT_DEG,
        'reason': '8-inch circular reflector tilted 18 degrees yields 7.633-inch projected height including 0.08-inch thickness, matching published 7.63-inch overall height. Installation sheet confirms the removable plate is normal to the angled socket axis.',
        'housing_back_diameter': HOUSING_BACK_R * 2.0,
        'housing_front_diameter': HOUSING_FRONT_R * 2.0,
        'housing_front_projection': HOUSING_FRONT_Z,
        'socket_radius': SOCKET_R,
        'globe_back_from_socket_pivot': GLOBE_BACK_T,
    },
    'configs': {},
}
DOCS = []
TX = None


def ensure_dirs():
    for p in (OUT, EVIDENCE, SOURCES):
        if not os.path.isdir(p):
            os.makedirs(p)


def append_memory_once():
    marker = '## Lightology f07_833919 worker - 2026-09-23'
    try:
        existing = ''
        if os.path.isfile(PROJECT_MEMORY):
            with open(PROJECT_MEMORY, 'r') as f:
                existing = f.read()
        if marker not in existing:
            entry = (
                '\n' + marker + '\n'
                '- Preparation tool errors: initial Core calls used the misspelled normalized namespace `Chat_On_Sterioids_Core` and therefore resolved undefined; browser unsafe code also reported `ReferenceError: require is not defined` and dynamic import reported `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`. Cause: Core namespace mismatch plus the browser VM correctly lacking Node/CommonJS filesystem APIs. Solution: rediscovered the callable tools, switched to `Chat_On_Steroids_Core`, preserved source evidence, and verified the native builder on the Windows project root. Status: preparation errors resolved; native validation remains serialized by the Revit slot.\n'
            )
            with open(PROJECT_MEMORY, 'a') as f:
                f.write(entry)
    except Exception:
        REPORT.setdefault('memory_append_errors', []).append(traceback.format_exc())


def checkpoint(stage):
    ensure_dirs()
    REPORT['stage'] = stage
    REPORT['updated_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    for path in (REPORT_PATH, LATEST_PATH):
        with open(path, 'w') as f:
            json.dump(REPORT, f, indent=2, default=str)


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def move_in(origin, vector, inches):
    return origin.Add(vector.Multiply(inches / 12.0))


def solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid


def elem_bounds(elements):
    boxes = [e.get_BoundingBox(None) for e in elements if e.get_BoundingBox(None)]
    return [
        min(b.Min.X for b in boxes) * 12,
        min(b.Min.Y for b in boxes) * 12,
        min(b.Min.Z for b in boxes) * 12,
        max(b.Max.X for b in boxes) * 12,
        max(b.Max.Y for b in boxes) * 12,
        max(b.Max.Z for b in boxes) * 12,
    ]


def bbox_inches(element):
    b = element.get_BoundingBox(None)
    return {
        'min': [b.Min.X * 12, b.Min.Y * 12, b.Min.Z * 12],
        'max': [b.Max.X * 12, b.Max.Y * 12, b.Max.Z * 12],
        'size': [(b.Max.X - b.Min.X) * 12, (b.Max.Y - b.Min.Y) * 12, (b.Max.Z - b.Min.Z) * 12],
    }


def profile_loop(origin, u, v, points):
    def p(pair):
        return origin.Add(u.Multiply(pair[0] / 12.0)).Add(v.Multiply(pair[1] / 12.0))
    loop = DB.CurveLoop()
    cur = points[0]
    for item in points[1:]:
        if len(item) == 3 and item[0] == 'arc':
            mid, end = item[1], item[2]
            loop.Append(DB.Arc.Create(p(cur), p(end), p(mid)))
        else:
            end = item
            loop.Append(DB.Line.CreateBound(p(cur), p(end)))
        cur = end
    if cur != points[0]:
        loop.Append(DB.Line.CreateBound(p(cur), p(points[0])))
    return loop


def add_solid(doc, name, solid, param, subcategory, record):
    element = DB.FreeFormElement.Create(doc, solid)
    element.Subcategory = subcategory
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), param)
    record.setdefault('generated_parts', []).append({'name': name, 'id': str(element.Id.Value)})
    return element


def revolved(doc, name, origin, axis, points, param, subcategory, record):
    radial = DB.XYZ.BasisX if abs(axis.Z) > .99 else DB.XYZ.BasisZ
    radial = radial.Subtract(axis.Multiply(radial.DotProduct(axis))).Normalize()
    loop = profile_loop(origin, radial, axis, points)
    frame = DB.Frame(origin, radial, axis.CrossProduct(radial), axis)
    solid = DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, List[DB.CurveLoop]([loop]), 0, 2 * math.pi)
    return add_solid(doc, name, solid, param, subcategory, record)


def cylinder(doc, name, origin, axis, radius, start, end, param, subcategory, record, rounding=0):
    if rounding:
        q = rounding
        k = 1 - math.sqrt(.5)
        points = [
            (0, start), (radius - q, start),
            ('arc', (radius - q * k, start + q * k), (radius, start + q)),
            (radius, end - q),
            ('arc', (radius - q * k, end - q * k), (radius - q, end)),
            (0, end),
        ]
    else:
        points = [(0, start), (radius, start), (radius, end), (0, end)]
    return revolved(doc, name, origin, axis, points, param, subcategory, record)


def clone_material(doc, name, asset, color, transparency):
    appearance = DB.AppearanceAssetElement.Create(doc, name, asset)
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.AppearanceAssetId = appearance.Id
    mat.Color = DB.Color(*color)
    mat.Transparency = transparency
    return mat, appearance


def set_color(asset, key, color):
    prop = asset.FindByName(key)
    if prop is None:
        return False
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(*color))
    return True


def scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        return False
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value
    return True


def make_materials(doc, app, cfg):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    base = next(a for a in assets if a.FindByName('BaseSchema') is not None and a.FindByName('BaseSchema').Value == 'GenericSchema')
    result = {}
    metal, appearance = clone_material(doc, 'Nodes - ' + cfg['finish'], base, cfg['metal_rgb'], 0)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    a = scope.Start(appearance.Id)
    set_color(a, 'generic_diffuse', cfg['metal_rgb'])
    scalar(a, 'generic_glossiness', cfg['metal_gloss'])
    scalar(a, 'generic_transparency', 0.0)
    scalar(a, 'generic_reflectivity_at_0deg', cfg['metal_refl'])
    scalar(a, 'generic_reflectivity_at_90deg', .72 if cfg['key'] == 'brass' else .42)
    scalar(a, 'generic_self_illum_luminance', 0.0)
    scope.Commit(True)
    scope.Dispose()
    metal.MaterialClass = 'Metal'
    result['Metal Finish'] = metal

    milk_rgb = (246, 243, 235)
    glass, appearance = clone_material(doc, 'Nodes - Milk Glass', base, milk_rgb, 12)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    a = scope.Start(appearance.Id)
    set_color(a, 'generic_diffuse', milk_rgb)
    scalar(a, 'generic_glossiness', .42)
    scalar(a, 'generic_transparency', .12)
    scalar(a, 'generic_refraction_index', 1.49)
    scalar(a, 'generic_reflectivity_at_0deg', .05)
    scalar(a, 'generic_reflectivity_at_90deg', .58)
    scalar(a, 'generic_self_illum_luminance', 0.0)
    scope.Commit(True)
    scope.Dispose()
    glass.MaterialClass = 'Glass'
    result['Glass Finish'] = glass
    return result


def check_dim(rec, name, measured, target, tol, method):
    rec[name] = {
        'measured_in': measured,
        'target_in': target,
        'tolerance_in': tol,
        'pass': measured is not None and abs(measured - target) <= tol,
        'method': method,
    }


def ray_segments(element, start_xyz, end_xyz):
    line = DB.Line.CreateBound(start_xyz, end_xyz)
    result = []
    opt = DB.SolidCurveIntersectionOptions()
    geom = element.get_Geometry(DB.Options())
    for solid in solids(geom):
        sci = solid.IntersectWithCurve(line, opt)
        for i in range(sci.SegmentCount):
            seg = sci.GetCurveSegment(i)
            result.append({
                'from': [seg.GetEndPoint(0).X * 12, seg.GetEndPoint(0).Y * 12, seg.GetEndPoint(0).Z * 12],
                'to': [seg.GetEndPoint(1).X * 12, seg.GetEndPoint(1).Y * 12, seg.GetEndPoint(1).Z * 12],
                'length': seg.Length * 12,
            })
    return result


def preview(doc, name, eye, target, realistic=False):
    vt = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vt.Id)
    view.Name = name
    forward = target.Subtract(eye).Normalize()
    up = DB.XYZ.BasisY
    if abs(forward.DotProduct(up)) > .99:
        up = DB.XYZ.BasisZ
    right = forward.CrossProduct(up).Normalize()
    trueup = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, trueup, forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.Scale = 1
    view.DisplayStyle = DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    for cat in doc.Settings.Categories:
        if cat.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(cat.Id):
            view.SetCategoryHidden(cat.Id, True)
    box = DB.BoundingBoxXYZ()
    box.Min = xyz(-5.2, -5.2, -.2)
    box.Max = xyz(5.2, 5.2, 6.1)
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    return view


def export_views(doc, views, prefix):
    options = DB.ImageExportOptions()
    options.ExportRange = DB.ExportRange.SetOfViews
    options.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    options.FilePath = os.path.join(EVIDENCE, prefix)
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ShadowViewsFileType = DB.ImageFileType.PNG
    options.ImageResolution = DB.ImageResolution.DPI_150
    options.ZoomType = DB.ZoomFitType.FitToPage
    options.PixelSize = 1600
    doc.ExportImage(options)


def hosted_view(project, inst, cfg):
    vt = next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(project, vt.Id)
    view.Name = cfg['prefix'] + ' Hosted Oblique'
    view.DisplayStyle = DB.DisplayStyle.Realistic
    view.DetailLevel = DB.ViewDetailLevel.Fine
    box = inst.get_BoundingBox(None)
    center = (box.Min + box.Max) * .5
    eye = center.Add(DB.XYZ(8, -11, 3))
    forward = center.Subtract(eye).Normalize()
    up = DB.XYZ.BasisZ
    right = forward.CrossProduct(up).Normalize()
    trueup = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, trueup, forward))
    sb = DB.BoundingBoxXYZ()
    sb.Min = box.Min - DB.XYZ(2, 2, 2)
    sb.Max = box.Max + DB.XYZ(2, 2, 2)
    view.SetSectionBox(sb)
    view.IsSectionBoxActive = True
    return view


def build_family(app, cfg, rec):
    global TX
    doc = app.NewFamilyDocument(TEMPLATE)
    DOCS.append(doc)
    TX = DB.Transaction(doc, 'Build Nodes ' + cfg['model'])
    TX.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    av = doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if av:
        av.Set(0)
    fm = doc.FamilyManager
    fm.NewType(cfg['type_name'])
    mats = make_materials(doc, app, cfg)
    params = {}
    for name, mat in mats.items():
        p = fm.AddParameter(name, DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
        fm.Set(p, mat.Id)
        params[name] = p

    for name, value in [
        ('Overall Width', OVERALL_W),
        ('Overall Height', OVERALL_H),
        ('Projection', OVERALL_D),
        ('Backplate Diameter', BACKPLATE_D),
        ('Backplate Depth', BACKPLATE_DEPTH),
        ('Shade Diameter', SHADE_D),
        ('Shade Height', SHADE_AXIAL_H),
    ]:
        p = fm.AddParameter(name, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
        fm.SetFormula(p, str(value) + ' in')

    for bip, value in [
        (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Visual Comfort Studio / Kelly Wearstler'),
        (DB.BuiltInParameter.ALL_MODEL_MODEL, cfg['model']),
        (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, 'Nodes Angled Wall Sconce; ' + cfg['finish'] + ' / Milk; face-based visualization family'),
    ]:
        p = fm.get_Parameter(bip)
        if p is not None:
            fm.Set(p, value)
    note = fm.AddParameter('Model Accuracy Notes', DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fm.Set(note, 'Published 8 W x 7.63 H x 5.5 D; 5.25 dia x 0.125 backplate; 3.5 dia x 3.25 milk shade. Installation sheet confirms tapered wall housing, removable reflector plate, angled socket, screw-on shade. Reflector modeled as 8 dia x 0.08 plate tilted 18 deg because that reproduces 7.63 projected height; housing taper, plate thickness, socket size and spacing are photo/drawing-derived inferences. No MEP connector or photometric source.')

    cats = {}
    for name in ['Backplate', 'Housing', 'Reflector', 'Socket', 'Milk Glass']:
        cats[name] = doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory, name)
    metal = params['Metal Finish']
    glass = params['Glass Finish']

    backplate = cylinder(doc, 'Round backplate', DB.XYZ.Zero, DB.XYZ.BasisZ,
                         BACKPLATE_D / 2.0, 0, BACKPLATE_DEPTH, metal, cats['Backplate'], rec, .035)

    housing_points = [
        (0, BACKPLATE_DEPTH),
        (HOUSING_BACK_R, BACKPLATE_DEPTH),
        (HOUSING_FRONT_R, HOUSING_FRONT_Z),
        (0, HOUSING_FRONT_Z),
    ]
    housing = revolved(doc, 'Tapered wall housing', DB.XYZ.Zero, DB.XYZ.BasisZ,
                       housing_points, metal, cats['Housing'], rec)

    pivot = xyz(0, 0, PIVOT_Z)
    reflector = cylinder(doc, 'Angled 8 inch reflector disc', pivot, AXIS,
                         REFLECTOR_D / 2.0,
                         DISC_CENTER_T - REFLECTOR_T / 2.0,
                         DISC_CENTER_T + REFLECTOR_T / 2.0,
                         metal, cats['Reflector'], rec, .025)
    socket = cylinder(doc, 'Angled socket collar', pivot, AXIS, SOCKET_R,
                      0, SOCKET_END_T, metal, cats['Socket'], rec, .035)

    globe_origin = move_in(pivot, AXIS, GLOBE_BACK_T)
    globe_profile = [
        (0, 0),
        (CUT_R, 0),
        ('arc', (SHADE_D / 2.0, 1.5), (0, SHADE_AXIAL_H)),
    ]
    globe = revolved(doc, 'Milk glass globe shade', globe_origin, AXIS,
                     globe_profile, glass, cats['Milk Glass'], rec)

    doc.Regenerate()
    elems = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    bounds = elem_bounds(elems)
    rec['family_bounds_in'] = bounds
    rec['overall_from_family_bounds_in'] = {
        'width': bounds[3] - bounds[0],
        'height': bounds[4] - bounds[1],
        'projection': bounds[5] - bounds[2],
    }
    rec['part_bounds_in'] = {
        'backplate': bbox_inches(backplate),
        'housing': bbox_inches(housing),
        'reflector': bbox_inches(reflector),
        'socket': bbox_inches(socket),
        'globe': bbox_inches(globe),
    }

    dims = rec.setdefault('dimension_checks', {})
    check_dim(dims, 'overall_width', rec['overall_from_family_bounds_in']['width'], OVERALL_W, DIM_TOL, 'All generated FreeFormElement bounding boxes, X extent')
    check_dim(dims, 'overall_height', rec['overall_from_family_bounds_in']['height'], OVERALL_H, DIM_TOL, 'All generated FreeFormElement bounding boxes, Y extent')
    check_dim(dims, 'overall_projection', rec['overall_from_family_bounds_in']['projection'], OVERALL_D, DEPTH_TOL, 'All generated FreeFormElement bounding boxes, Z extent')
    check_dim(dims, 'backplate_diameter_x', rec['part_bounds_in']['backplate']['size'][0], BACKPLATE_D, DIM_TOL, 'Backplate element X bounding extent')
    check_dim(dims, 'backplate_diameter_y', rec['part_bounds_in']['backplate']['size'][1], BACKPLATE_D, DIM_TOL, 'Backplate element Y bounding extent')
    check_dim(dims, 'backplate_depth', rec['part_bounds_in']['backplate']['size'][2], BACKPLATE_DEPTH, DIM_TOL, 'Backplate element Z bounding extent')
    check_dim(dims, 'reflector_width', rec['part_bounds_in']['reflector']['size'][0], REFLECTOR_D, DIM_TOL, 'Tilted reflector element X bounding extent')
    check_dim(dims, 'reflector_projected_height', rec['part_bounds_in']['reflector']['size'][1], OVERALL_H, DIM_TOL, 'Tilted 8-inch circular reflector projected to wall-plane Y')

    globe_center = move_in(globe_origin, AXIS, 1.5)
    side_a = move_in(globe_center, DB.XYZ.BasisX, -3.0)
    side_b = move_in(globe_center, DB.XYZ.BasisX, 3.0)
    globe_cross = ray_segments(globe, side_a, side_b)
    rec['globe_cross_segments'] = globe_cross
    check_dim(dims, 'shade_diameter_ray', globe_cross[0]['length'] if globe_cross else None,
              SHADE_D, DIM_TOL, 'Solid.IntersectWithCurve through maximum globe section, perpendicular to socket axis')
    axial_a = move_in(globe_origin, AXIS, -0.5)
    axial_b = move_in(globe_origin, AXIS, 4.0)
    globe_axis = ray_segments(globe, axial_a, axial_b)
    rec['globe_axial_segments'] = globe_axis
    check_dim(dims, 'shade_axial_height_ray', globe_axis[0]['length'] if globe_axis else None,
              SHADE_AXIAL_H, DIM_TOL, 'Solid.IntersectWithCurve along socket/globe axis from clipped back to front')

    target = xyz(0, -.15, 2.6)
    views = [
        preview(doc, cfg['prefix'] + ' Front', xyz(0, 0, 30), target, False),
        preview(doc, cfg['prefix'] + ' Side', xyz(18, 0, 2.6), target, False),
        preview(doc, cfg['prefix'] + ' Oblique', xyz(12, -10, 18), target, False),
        preview(doc, cfg['prefix'] + ' Material', xyz(11, -9, 16), target, True),
    ]
    TX.Commit()
    TX = None

    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    save.MaximumBackups = 1
    save.PreviewViewId = views[2].Id
    rfa_path = os.path.join(OUT, cfg['rfa'])
    doc.SaveAs(rfa_path, save)
    export_views(doc, views, cfg['prefix'])
    rec['rfa_path'] = rfa_path
    rec['family_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    DOCS.remove(doc)
    doc.Close(False)
    return rfa_path


def validate_family(app, cfg, rfa_path, rec):
    global TX
    reopened = app.OpenDocumentFile(rfa_path)
    DOCS.append(reopened)
    rec['reopened'] = reopened.IsFamilyDocument
    rec['category'] = reopened.OwnerFamily.FamilyCategory.Name
    rec['placement'] = str(reopened.OwnerFamily.FamilyPlacementType)
    rec['reopened_warnings'] = [w.GetDescriptionText() for w in reopened.GetWarnings()]
    rec['rfa_bytes'] = os.path.getsize(rfa_path)
    rec['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(os.path.getmtime(rfa_path)).isoformat() + 'Z'

    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    family = reopened.LoadFamily(project)
    symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])
    TX = DB.Transaction(project, 'Host and material-test Nodes ' + cfg['model'])
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)), None)
    if level is None:
        level = DB.Level.Create(project, 0)
    wall_type = next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(project,
                          DB.Line.CreateBound(DB.XYZ(-8, 0, 0), DB.XYZ(8, 0, 0)),
                          wall_type.Id, level.Id, 10, 0, False, False)
    symbol.Activate()
    project.Regenerate()
    reference = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(reference)
    point = face.Project(DB.XYZ(0, 0, 5)).XYZPoint
    inst = project.Create.NewFamilyInstance(reference, point, DB.XYZ.BasisX, symbol)
    project.Regenerate()

    rec['host_validation'] = {
        'host_id': str(inst.Host.Id.Value) if inst.Host else None,
        'wall_id': str(wall.Id.Value),
        'hostface_present': inst.HostFace is not None,
        'face_based_host': bool(inst.Host is not None and inst.Host.Id == wall.Id and inst.HostFace is not None),
        'transform_basis_z_dot_face_normal': inst.GetTransform().BasisZ.DotProduct(face.FaceNormal),
    }
    box = inst.get_BoundingBox(None)
    world_dims = [(box.Max.X - box.Min.X) * 12, (box.Max.Y - box.Min.Y) * 12, (box.Max.Z - box.Min.Z) * 12]
    rec['placed_bbox_dimensions_in'] = world_dims
    rec['placed_bbox_dimensions_sorted_in'] = sorted(world_dims)
    rec['placed_dimension_checks'] = {
        'contains_5_5_projection': any(abs(x - OVERALL_D) <= DEPTH_TOL for x in world_dims),
        'contains_7_63_height': any(abs(x - OVERALL_H) <= DIM_TOL for x in world_dims),
        'contains_8_0_width': any(abs(x - OVERALL_W) <= DIM_TOL for x in world_dims),
    }

    rec['material_tests'] = {}
    for pname in ['Metal Finish', 'Glass Finish']:
        param = symbol.LookupParameter(pname)
        original = param.AsElementId()
        alternate = DB.Material.Create(project, 'QA ' + cfg['model'] + ' ' + pname)
        param.Set(alternate)
        project.Regenerate()
        ids = [f.MaterialElementId for s in solids(inst.get_Geometry(DB.Options())) for f in s.Faces]
        rec['material_tests'][pname] = {
            'writable': not param.IsReadOnly,
            'faces_inspected': len(ids),
            'substitute_material_id': str(alternate.Value),
            'faces_carrying_substitute': sum(1 for i in ids if i == alternate),
            'substitute_reached_geometry': alternate in ids,
        }
        param.Set(original)
        project.Regenerate()
        rec['material_tests'][pname]['restored_material_id'] = str(param.AsElementId().Value)

    hosted = hosted_view(project, inst, cfg)
    TX.Commit()
    TX = None
    export_views(project, [hosted], cfg['prefix'] + '_Hosted')
    rec['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    rec['evidence_files'] = sorted(n for n in os.listdir(EVIDENCE) if n.startswith(cfg['prefix']))

    dims_pass = all(v.get('pass') is True for v in rec.get('dimension_checks', {}).values())
    placed_pass = all(rec['placed_dimension_checks'].values())
    material_pass = len(rec['material_tests']) == 2 and all(v.get('substitute_reached_geometry') for v in rec['material_tests'].values())
    gates = {
        'fresh_rfa_reopen': bool(rec.get('reopened')),
        'lighting_fixture_category': rec.get('category') == 'Lighting Fixtures',
        'face_based_placement': 'WorkPlaneBased' in rec.get('placement', '') or 'Face' in rec.get('placement', ''),
        'actual_native_wall_face_host': rec['host_validation']['face_based_host'],
        'published_and_inferred_geometry_measures': dims_pass,
        'placed_envelope_measures': placed_pass,
        'material_substitution_reaches_geometry': material_pass,
        'zero_warnings': not rec.get('family_warnings') and not rec.get('reopened_warnings') and not rec.get('project_warnings'),
        'front_side_oblique_material_hosted_exports': len(rec.get('evidence_files', [])) >= 5,
    }
    rec['gates'] = gates
    rec['technical_pass'] = all(gates.values())
    rec['visual_verdict'] = 'PENDING SELF/PRIME REVIEW - native exports produced; source comparison remains a separate gate'
    DOCS.remove(project)
    project.Close(False)
    DOCS.remove(reopened)
    reopened.Close(False)
    return rec['technical_pass']


try:
    ensure_dirs()
    append_memory_once()
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    REPORT['template'] = TEMPLATE
    REPORT['template_exists'] = os.path.isfile(TEMPLATE)
    checkpoint('preflight')
    if not app.VersionNumber.startswith('2025'):
        raise RuntimeError('Revit 2025 required; host reports ' + str(app.VersionNumber))
    if not os.path.isfile(TEMPLATE):
        raise RuntimeError('Face-based template missing: ' + TEMPLATE)

    for cfg in CONFIGS:
        rec = {
            'finish': cfg['finish'],
            'sku': cfg['sku'],
            'model': cfg['model'],
            'type_name': cfg['type_name'],
            'option_url': cfg['option_url'],
            'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
        }
        REPORT['configs'][cfg['key']] = rec
        checkpoint('build-' + cfg['key'])
        rfa = build_family(app, cfg, rec)
        checkpoint('validate-' + cfg['key'])
        validate_family(app, cfg, rfa, rec)
        rec['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
        checkpoint('validated-' + cfg['key'])

    REPORT['technical_pass'] = all(r.get('technical_pass') for r in REPORT['configs'].values())
    REPORT['failed_gates'] = {
        key: [name for name, ok in rec.get('gates', {}).items() if not ok]
        for key, rec in REPORT['configs'].items()
    }
    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
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
