# -*- coding: utf-8 -*-
r"""Alora Mood Cassia SF549315AGOP (Aged Gold / Opal Matte Glass) - Revit 2025 family builder.

Run inside Revit 2025 through the pyRevit CLI with an ABSOLUTE script path
(a relative path has returned exit 0 without running the script, E026):

    "C:\Program Files\pyRevit-Master\bin\pyrevit.exe" run "<repo>\output\cassia\source\build_cassia.py" --revit=2025

or simply run output\cassia\run_cassia.ps1, which also runs the verifier.

What it does, in one Revit session, touching only new documents and output/cassia:
  1. builds a face-based Lighting Fixtures family from cassia_geometry.py
     (19 revolved solids, 3 material parameters, 4 subcategories, fixed geometry)
  2. saves, closes and REOPENS the RFA; checks category, warnings, subcategories and
     every part's material binding
  3. fires the shared measurement rays (Solid.IntersectWithCurve) at the saved solids,
     and the internal-clearance rays at each globe
  4. loads the family into a disposable project, hosts it on the underside of a native
     floor, measures the hosted drop and spread through the instance geometry, and
     substitutes each material parameter, counting the solids that carry it
  5. exports family and hosted views for the visual review

validation.json is rewritten at every checkpoint, with a timestamped copy per attempt in
logs/. Gates are explicit. The script re-raises on failure because `pyrevit run` exits 0
even when a script crashes (P01, 2026-09-18). It never awards itself a visual pass.
"""
import os
import sys
import json
import math
import datetime
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN_NAME = 'cassia'
SCRIPT_VERSION = 'cassia-builder-2026-09-23'
REPO_ROOT_CANDIDATES = [
    r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow',
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow',
]
TEMPLATE_DIR = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial'
FACE_TEMPLATE = os.path.join(TEMPLATE_DIR, 'Generic Model face based.rft')
RFA_NAME = 'Alora_Cassia_SF549315AGOP_Aged_Gold_Opal_R2025.rfa'
TYPE_NAME = 'SF549315AGOP - Aged Gold - Opal Matte Glass'
IMAGE_PREFIX = 'Cassia'
HOSTED_PREFIX = 'Cassia_Hosted'
CEILING_FT = 10.0


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return None


def repo_root():
    candidates = []
    here = _script_dir()
    if here:
        candidates.append(os.path.normpath(os.path.join(here, '..', '..', '..')))
    candidates.extend(REPO_ROOT_CANDIDATES)
    for candidate in candidates:
        if (os.path.isfile(os.path.join(candidate, 'AGENTS.md')) and
                os.path.isfile(os.path.join(candidate, 'output', RUN_NAME, 'source', 'cassia_geometry.py'))):
            return candidate
    raise RuntimeError('No repository root with AGENTS.md and output/cassia/source/cassia_geometry.py '
                       'among: ' + ' | '.join(candidates))


ROOT = repo_root()
RUN_DIR = os.path.join(ROOT, 'output', RUN_NAME)
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)
sys.path.insert(0, os.path.join(RUN_DIR, 'source'))
import cassia_geometry as G  # noqa: E402  (shared with preview_geometry.py and verify_cassia.py)

# Appearance values. Aged gold diffuse is the 60th percentile of gold pixels in the supplied
# white render (median 135,99,54; p60 146,107,60; p90 232,185,119), kept below the lit
# highlights so the renderer's specular lift is not double-counted. Opal is the p10 of
# the lit globe pixels (242,236,231) lifted slightly; unlit and opaque, as in both renders.
# generic_is_metal is True for the brass so reflections take the metal's colour, as the
# render's tinted highlights do (same flag as build_kohler_titanium.py); flip it here if
# the Realistic review disagrees.
MATERIALS = {
    'metal': {'name': 'Cassia - Aged Gold', 'color': (146, 107, 60), 'gloss': 0.45,
              'refl0': 0.30, 'refl90': 0.80, 'transparency': 0.0, 'refraction': None,
              'is_metal': True, 'material_class': 'Metal', 'graphics_transparency': 0},
    'glass': {'name': 'Cassia - Opal Matte Glass', 'color': (244, 240, 234), 'gloss': 0.30,
              'refl0': 0.04, 'refl90': 0.35, 'transparency': 0.0, 'refraction': 1.52,
              'is_metal': False, 'material_class': 'Glass', 'graphics_transparency': 0},
    'lamp': {'name': 'Cassia - Candle Lamp', 'color': (250, 248, 240), 'gloss': 0.85,
             'refl0': 0.06, 'refl90': 0.60, 'transparency': 0.35, 'refraction': 1.50,
             'is_metal': False, 'material_class': 'Glass', 'graphics_transparency': 30},
}

IDENTITY = [
    (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Alora Mood (Kuzco Lighting)'),
    (DB.BuiltInParameter.ALL_MODEL_MODEL, 'Cassia SF549315AGOP'),
    (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
     'Cassia 3-light semi-flush, Aged Gold / Opal Matte Glass, D17-3/4 x H7-5/8 in. '
     'Visualization family: fixed geometry, no light source, no MEP connectors.'),
    (DB.BuiltInParameter.ALL_MODEL_URL, 'https://s3-us-west-2.amazonaws.com/catsy.870/SF549315_Spec_Sheet.pdf'),
]
ACCURACY_NOTE = ('Published: D17-3/4, H7-5/8, canopy D4-3/4 x 7/8, globes D6 (Alora Mood SF549315 spec sheet). '
                 'Drawing-measured: 30 deg arms through globe centres, hub, arm, stepped fitter. '
                 'Inferred: glass wall 0.10, socket sleeve and candle lamp (hidden by opal), screw domes, '
                 'edge rounds. See output/cassia/INFERENCES.md.')
DIMENSION_PARAMETERS = [('Overall Diameter', G.OVERALL_DIAMETER), ('Overall Height', G.OVERALL_HEIGHT),
                        ('Canopy Diameter', G.CANOPY_DIAMETER), ('Canopy Height', G.CANOPY_HEIGHT),
                        ('Globe Diameter', G.GLOBE_DIAMETER)]

REPORT = {
    'script': 'output/cassia/source/build_cassia.py',
    'script_version': SCRIPT_VERSION,
    'repo_root': ROOT,
    'run_dir': RUN_DIR,
    'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'rfa_name': RFA_NAME,
    'type_name': TYPE_NAME,
    'geometry': G.summary(),
    'materials_requested': MATERIALS,
    'tolerances_in': {'dimension': G.DIM_TOL, 'angle_deg': G.ANGLE_TOL_DEG, 'hosted': G.HOSTED_TOL,
                      'min_internal_clearance': G.MIN_INTERNAL_CLEARANCE},
    'visual_verdict': 'PENDING REVIEWER - exports produced, fidelity not self-assessed',
}
DOCS = []
TX = None


# ------------------------------------------------------------------ plumbing
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
    stamp = REPORT['started_utc'].replace(':', '').replace('-', '').replace('.', '')
    with open(out_path('logs', 'validation-%s.json' % stamp), 'w') as handle:
        handle.write(payload)


def element_name(element):
    """Element.Name through the property descriptor (MissingMemberException, P01 attempt 1)."""
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        param = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return param.AsString() if param else None


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def inches(point):
    return (point.X * 12.0, point.Y * 12.0, point.Z * 12.0)


def solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid


def element_solids(element):
    options = DB.Options()
    options.ComputeReferences = False
    return list(solids(element.get_Geometry(options)))


def solid_segments(solid_list, p0_in, p1_in):
    """Portions of the line p0-p1 (inches) inside the given solids, as inch tuples."""
    line = DB.Line.CreateBound(xyz(*p0_in), xyz(*p1_in))
    found = []
    for solid in solid_list:
        result = solid.IntersectWithCurve(line, DB.SolidCurveIntersectionOptions())
        for index in range(result.SegmentCount):
            segment = result.GetCurveSegment(index)
            found.append((inches(segment.GetEndPoint(0)), inches(segment.GetEndPoint(1))))
    return found


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


def revolve_part(doc, part, params, subcategories):
    origin = xyz(*part['origin'])
    axis = DB.XYZ(part['axis'][0], part['axis'][1], part['axis'][2]).Normalize()
    ref = DB.XYZ.BasisX if abs(axis.Z) > 0.99 else DB.XYZ.BasisZ
    radial = ref.Subtract(axis.Multiply(ref.DotProduct(axis))).Normalize()
    loop = profile_loop(origin, radial, axis, part['profile'])
    frame = DB.Frame(origin, radial, axis.CrossProduct(radial), axis)
    solid = DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, List[DB.CurveLoop]([loop]), 0, 2 * math.pi)
    element = DB.FreeFormElement.Create(doc, solid)
    element.Subcategory = subcategories[part['subcategory']]
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), params[part['material']])
    return element


def check(bucket, key, measured, target, tolerance, method, source):
    entry = {'measured': measured, 'target': target, 'tolerance': tolerance,
             'method': method, 'source': source}
    entry['pass'] = measured is not None and abs(measured - target) <= tolerance
    bucket[key] = entry
    return entry['pass']


# ----------------------------------------------------------------- materials
def set_color(asset, key, color):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Missing appearance property: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(color[0], color[1], color[2]))


def scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Missing appearance property: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value


def strip_connected_maps(asset):
    """Remove every bitmap/procedural map inherited from the library source asset."""
    removed = []
    for index in range(asset.Size):          # same idiom as build_kohler_titanium.py
        prop = asset[index]
        try:
            connected = prop.NumberOfConnectedProperties
        except Exception:
            continue
        if connected:
            prop.RemoveConnectedAsset()
            removed.append(prop.Name)
    return removed


def make_materials(doc, app, record):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next((a for a in assets if a.FindByName('BaseSchema') is not None
                   and a.FindByName('BaseSchema').Value == 'GenericSchema'), None)
    if source is None:
        raise RuntimeError('No GenericSchema appearance asset in the Revit appearance library')
    record['appearance_source_asset'] = source.Name
    created = {}
    applied = {}
    for key in ('metal', 'glass', 'lamp'):
        spec = MATERIALS[key]
        appearance = DB.AppearanceAssetElement.Create(doc, spec['name'], source)
        material = doc.GetElement(DB.Material.Create(doc, spec['name']))
        material.AppearanceAssetId = appearance.Id
        material.Color = DB.Color(spec['color'][0], spec['color'][1], spec['color'][2])
        material.Transparency = spec['graphics_transparency']
        material.MaterialClass = spec['material_class']
        scope = DB.Visual.AppearanceAssetEditScope(doc)
        asset = scope.Start(appearance.Id)
        info = {'removed_connected_maps': strip_connected_maps(asset)}
        set_color(asset, 'generic_diffuse', spec['color'])
        scalar(asset, 'generic_glossiness', spec['gloss'])
        scalar(asset, 'generic_transparency', spec['transparency'])
        scalar(asset, 'generic_reflectivity_at_0deg', spec['refl0'])
        scalar(asset, 'generic_reflectivity_at_90deg', spec['refl90'])
        scalar(asset, 'generic_self_illum_luminance', 0.0)
        if spec['refraction'] is not None:
            scalar(asset, 'generic_refraction_index', spec['refraction'])
        metal_flag = asset.FindByName('generic_is_metal')
        if metal_flag is not None:
            metal_flag.Value = spec['is_metal']
        info['is_metal_set'] = metal_flag is not None
        scope.Commit(True)
        scope.Dispose()
        created[key] = material
        applied[key] = info
    record['material_setup'] = applied
    return created


def read_appearance(doc, material):
    asset = doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
    out = {'material': material.Name, 'material_class': material.MaterialClass,
           'graphics_color': [int(material.Color.Red), int(material.Color.Green), int(material.Color.Blue)],
           'graphics_transparency': int(material.Transparency), 'connected_maps': []}
    diffuse = asset.FindByName('generic_diffuse')
    if diffuse is not None:
        c = diffuse.GetValueAsColor()
        out['diffuse'] = [int(c.Red), int(c.Green), int(c.Blue)]
    for key in ('generic_glossiness', 'generic_transparency', 'generic_reflectivity_at_0deg',
                'generic_reflectivity_at_90deg', 'generic_self_illum_luminance', 'generic_refraction_index'):
        prop = asset.FindByName(key)
        if prop is not None:
            out[key] = float(prop.Value)
    for index in range(asset.Size):
        prop = asset[index]
        try:
            if prop.NumberOfConnectedProperties:
                out['connected_maps'].append(prop.Name)
        except Exception:
            pass
    return out


# --------------------------------------------------------------------- views
def view_type_3d(doc):
    return next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
                if v.ViewFamily == DB.ViewFamily.ThreeDimensional)


def orient(view, eye, forward, up_hint):
    forward = forward.Normalize()
    right = forward.CrossProduct(up_hint).Normalize()
    up = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, up, forward))


def family_view(doc, name, direction_in, up_hint, style):
    """Isometric family view; direction_in points from the fixture toward the eye."""
    view = DB.View3D.CreateIsometric(doc, view_type_3d(doc).Id)
    view.Name = name
    target = xyz(0, 0, G.OVERALL_HEIGHT / 2.0)
    d = DB.XYZ(direction_in[0], direction_in[1], direction_in[2]).Normalize()
    eye = target.Add(d.Multiply(90.0 / 12.0))
    orient(view, eye, target.Subtract(eye), up_hint)
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = style
    for category in doc.Settings.Categories:
        if category.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(category.Id):
            view.SetCategoryHidden(category.Id, True)
    box = DB.BoundingBoxXYZ()
    box.Min = xyz(-10.5, -10.5, 0.001)          # template host lies at z <= 0
    box.Max = xyz(10.5, 10.5, G.OVERALL_HEIGHT + 1.0)
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    return view


def family_views(doc):
    down = DB.XYZ(0, 0, -1)     # local +Z hangs downward once hosted, so screen-up is -Z
    beta = math.radians(8.5)
    az = math.radians(300.0)    # render camera, world azimuth; world Y = -local Y when hosted
    oblique = (math.cos(az) * math.cos(beta), -math.sin(az) * math.cos(beta), math.sin(beta))
    return [
        family_view(doc, 'Cassia Oblique', oblique, down, DB.DisplayStyle.Shading),
        family_view(doc, 'Cassia Oblique Realistic', oblique, down, DB.DisplayStyle.Realistic),
        family_view(doc, 'Cassia Front Elevation', (0, 1, 0), down, DB.DisplayStyle.Shading),
        family_view(doc, 'Cassia Side Along Arm', (-1, 0, 0), down, DB.DisplayStyle.Shading),
        family_view(doc, 'Cassia Plan From Below', (0, 0, 1), DB.XYZ(0, 1, 0), DB.DisplayStyle.Shading),
    ]


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


def list_images(prefix):
    folder = out_path('evidence')
    return sorted([{'file': n, 'bytes': os.path.getsize(os.path.join(folder, n))}
                   for n in os.listdir(folder)
                   if n.startswith(prefix + ' - ') and n.lower().endswith('.png')],
                  key=lambda item: item['file'])


# --------------------------------------------------------------------- build
def build(app):
    global TX
    doc = app.NewFamilyDocument(FACE_TEMPLATE)
    DOCS.append(doc)
    build_rec = REPORT.setdefault('build', {})
    TX = DB.Transaction(doc, 'Build Cassia SF549315 visualization family')
    TX.Start()
    family = doc.OwnerFamily
    family.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    always_vertical = family.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
    if always_vertical is not None and not always_vertical.IsReadOnly:
        always_vertical.Set(0)
    manager = doc.FamilyManager
    manager.NewType(TYPE_NAME)

    materials = make_materials(doc, app, build_rec)
    params = {}
    for key, material in materials.items():
        param = manager.AddParameter(G.MATERIAL_PARAMETERS[key], DB.GroupTypeId.Materials,
                                     DB.SpecTypeId.Reference.Material, False)
        manager.Set(param, material.Id)
        params[key] = param
    for name, value in DIMENSION_PARAMETERS:
        param = manager.AddParameter(name, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
        manager.SetFormula(param, '%g"' % value)
    for bip, value in IDENTITY:
        param = manager.get_Parameter(bip)
        if param is not None:
            manager.Set(param, value)
    note = manager.AddParameter('Model Accuracy Notes', DB.GroupTypeId.IdentityData,
                                DB.SpecTypeId.String.Text, False)
    manager.Set(note, ACCURACY_NOTE)

    subcategories = {}
    for name in G.SUBCATEGORIES:
        subcategories[name] = doc.Settings.Categories.NewSubcategory(family.FamilyCategory, name)

    try:
        build_rec['short_curve_tolerance_in'] = app.ShortCurveTolerance * 12.0
    except Exception:
        build_rec['short_curve_tolerance_in'] = None
    parts = []
    for part in G.parts():
        element = revolve_part(doc, part, params, subcategories)
        parts.append({'key': part['key'], 'name': part['name'], 'id': str(element.Id.Value),
                      'material': part['material'], 'subcategory': part['subcategory']})
        REPORT['stage_detail'] = 'created ' + part['key']
    REPORT['parts'] = parts
    doc.Regenerate()          # bounds and geometry are None without this (Mila, 700LSESF60)
    views = family_views(doc)
    TX.Commit()
    TX = None
    checkpoint('built, saving')

    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    save.MaximumBackups = 1
    save.PreviewViewId = views[0].Id
    rfa_path = out_path(RFA_NAME)
    doc.SaveAs(rfa_path, save)
    REPORT['rfa_path'] = rfa_path
    try:
        export_images(doc, views, IMAGE_PREFIX)
        REPORT['family_export_error'] = None
    except Exception:
        REPORT['family_export_error'] = traceback.format_exc()
    REPORT['family_images'] = list_images(IMAGE_PREFIX)
    DOCS.remove(doc)
    doc.Close(False)
    return rfa_path


# ------------------------------------------------------------ reopen + measure
def measure_family(app, rfa_path):
    doc = app.OpenDocumentFile(rfa_path)
    DOCS.append(doc)
    rec = REPORT.setdefault('family', {})
    rec['reopened'] = doc.IsFamilyDocument
    rec['category'] = doc.OwnerFamily.FamilyCategory.Name
    rec['placement_type'] = str(doc.OwnerFamily.FamilyPlacementType)
    rec['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    rec['rfa_bytes'] = os.path.getsize(rfa_path)
    rec['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(os.path.getmtime(rfa_path)).isoformat() + 'Z'
    manager = doc.FamilyManager

    # saved type values
    saved = {}
    for param in manager.Parameters:
        name = param.Definition.Name
        if name in [n for n, _ in DIMENSION_PARAMETERS]:
            value = manager.CurrentType.AsDouble(param)
            saved[name] = None if value is None else value * 12.0
    rec['saved_dimension_parameters_in'] = saved
    rec['type_names'] = [t.Name for t in manager.Types]

    # every part resolves, keeps its subcategory and its material binding
    elements = {}
    bindings = []
    for part in REPORT['parts']:
        element = doc.GetElement(DB.ElementId(int(part['id'])))
        ok = isinstance(element, DB.FreeFormElement)
        sub = element.Subcategory.Name if ok and element.Subcategory is not None else None
        bound, bind_error = None, None
        if ok:
            try:
                assoc = manager.GetAssociatedFamilyParameter(
                    element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM))
                bound = assoc.Definition.Name if assoc is not None else None
            except Exception:
                bind_error = traceback.format_exc()
        row = {'key': part['key'], 'found': ok, 'subcategory': sub, 'material_parameter': bound,
               'pass': ok and sub == part['subcategory']
               and bound == G.MATERIAL_PARAMETERS[part['material']]}
        if bind_error:
            row['error'] = bind_error
        bindings.append(row)
        if ok:
            elements[part['key']] = element
    rec['part_bindings'] = bindings
    rec['freeform_count'] = len(list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement)))

    # shared measurement rays
    rays = {}
    sections = {}
    for ray in G.measurement_rays():
        element = elements.get(ray['part'])
        try:
            segs = solid_segments(element_solids(element), ray['p0'], ray['p1']) if element else []
            value = G.reduce_segments(ray, segs)
            error = None
        except Exception:
            segs, value, error = [], None, traceback.format_exc()
        check(rays, ray['key'], value, ray['target'], ray['tol'],
              'Solid.IntersectWithCurve on %s, reduce=%s' % (ray['part'], ray['reduce']), ray['source'])
        rays[ray['key']]['segments'] = len(segs)
        if error:
            rays[ray['key']]['error'] = error
        if 'radius' in ray and value is not None:
            sections.setdefault(ray['part'], []).append((ray['radius'], value))
    rec['rays'] = rays
    angles = {}
    for part_key, values in sorted(sections.items()):
        if len(values) == 2:
            check(angles, part_key, G.arm_angle_from_sections(sorted(values)), G.ARM_ANGLE_DEG,
                  G.ANGLE_TOL_DEG, 'slope between two vertical section midpoints (degrees)', 'DRAWING')
            angles[part_key]['sections'] = sorted(values)
    rec['arm_angles_deg'] = angles

    # fitter must cover the glass opening (measured, not assumed)
    cover = {}
    for i in range(len(G.ARM_AZIMUTHS_DEG)):
        flange = rays.get('fitter_%d_flange_diameter' % i, {}).get('measured')
        opening = rays.get('globe_%d_opening_radius' % i, {}).get('measured')
        margin = None if flange is None or opening is None else flange / 2.0 - opening
        cover['arm_%d' % i] = {'flange_radius_in': None if flange is None else flange / 2.0,
                               'glass_opening_radius_in': opening, 'margin_in': margin,
                               'pass': margin is not None and margin > 0.0}
    rec['fitter_covers_opening'] = cover

    # internal clearances
    clear = []
    for cray in G.clearance_rays():
        try:
            glass = solid_segments(element_solids(elements[cray['glass']]), cray['p0'], cray['p1'])
            inside = []
            for key in cray['inside']:
                inside.extend(solid_segments(element_solids(elements[key]), cray['p0'], cray['p1']))
            value, glass_inner, part_outer = G.clearance_from_segments(cray['p0'], glass, inside)
            error = None
        except Exception:
            value, glass_inner, part_outer, error = None, None, None, traceback.format_exc()
        row = {'key': cray['key'], 'station_in': cray['station_in'], 'clearance_in': value,
               'glass_inner_radius_in': glass_inner, 'inside_outer_radius_in': part_outer,
               'pass': value is not None and value >= G.MIN_INTERNAL_CLEARANCE}
        if error:
            row['error'] = error
        clear.append(row)
    rec['internal_clearances'] = clear

    # appearance read-back
    rec['appearances'] = {}
    for key, spec in MATERIALS.items():
        material = next((m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material)
                         if m.Name == spec['name']), None)
        rec['appearances'][key] = read_appearance(doc, material) if material else None
    return doc


# ------------------------------------------------------------- hosted tests
def hosted_tests(app, family_doc):
    global TX
    rec = REPORT.setdefault('hosted', {})
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    loaded = family_doc.LoadFamily(project)
    symbol = project.GetElement(list(loaded.GetFamilySymbolIds())[0])

    TX = DB.Transaction(project, 'Host Cassia on a native ceiling face')
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)), None)
    if level is None:
        level = DB.Level.Create(project, 0)
    floor_type = DB.Floor.GetDefaultFloorType(project, False)
    slab = profile_loop(DB.XYZ.Zero, DB.XYZ.BasisX, DB.XYZ.BasisY,
                        [(-60, -60), (60, -60), (60, 60), (-60, 60)])
    floor = DB.Floor.Create(project, List[DB.CurveLoop]([slab]), floor_type, level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(CEILING_FT)
    symbol.Activate()
    project.Regenerate()
    reference = DB.HostObjectUtils.GetBottomFaces(floor)[0]
    face = floor.GetGeometryObjectFromReference(reference)
    point = face.Project(DB.XYZ(0, 0, CEILING_FT)).XYZPoint
    instance = project.Create.NewFamilyInstance(reference, point, DB.XYZ.BasisX, symbol)
    project.Regenerate()

    rec['host_type'] = element_name(project.GetElement(floor.GetTypeId()))
    rec['host_face_z_in'] = point.Z * 12.0
    rec['hosted_on_floor'] = instance.Host is not None and instance.Host.Id == floor.Id
    transform = instance.GetTransform()
    rec['basis_z'] = [transform.BasisZ.X, transform.BasisZ.Y, transform.BasisZ.Z]
    box = instance.get_BoundingBox(None)
    rec['instance_bbox_in'] = {'min': inches(box.Min), 'max': inches(box.Max)}
    rec['above_host_face_in'] = box.Max.Z * 12.0 - point.Z * 12.0

    world = list(solids(instance.get_Geometry(DB.Options())))
    rec['instance_solids'] = len(world)
    face_z = point.Z * 12.0
    origin = inches(transform.Origin)
    drops = {}
    spreads = {}
    for i, phi in enumerate(G.ARM_AZIMUTHS_DEG):
        centre = inches(transform.OfPoint(xyz(*G.arm_frame(phi)[0])))
        segs = solid_segments(world, (centre[0], centre[1], face_z + 1.0), (centre[0], centre[1], face_z - 12.0))
        low = min(p[2] for s in segs for p in s) if segs else None
        check(drops, 'globe_%d' % i, None if low is None else face_z - low, G.OVERALL_HEIGHT, G.HOSTED_TOL,
              'vertical ray through the hosted globe centre, host face Z minus lowest solid point', 'PUBLISHED')
        dx, dy = centre[0] - origin[0], centre[1] - origin[1]
        n = math.hypot(dx, dy)
        far = (origin[0] + dx / n * 12.0, origin[1] + dy / n * 12.0, centre[2])
        segs = solid_segments(world, (origin[0], origin[1], centre[2]), far)
        reach = max(math.hypot(p[0] - origin[0], p[1] - origin[1]) for s in segs for p in s) if segs else None
        check(spreads, 'globe_%d' % i, reach, G.OVERALL_DIAMETER / 2.0, G.HOSTED_TOL,
              'horizontal ray from the instance axis through the hosted globe centre', 'PUBLISHED')
    rec['drop_in'] = drops
    rec['spread_radius_in'] = spreads

    expected = G.expected_solids_per_material()
    tests = {}
    for key, pname in G.MATERIAL_PARAMETERS.items():
        type_param = symbol.LookupParameter(pname)
        original = type_param.AsElementId()
        alternate = DB.Material.Create(project, 'QA substitute ' + pname)
        type_param.Set(alternate)
        project.Regenerate()
        carrying = 0
        faces = 0
        for solid in solids(instance.get_Geometry(DB.Options())):
            ids = [f.MaterialElementId for f in solid.Faces]
            faces += len(ids)
            if ids and all(i == alternate for i in ids):
                carrying += 1
        tests[pname] = {'type_parameter_writable': not type_param.IsReadOnly,
                        'solids_fully_carrying_substitute': carrying,
                        'expected_solids': expected.get(key), 'faces_inspected': faces,
                        'pass': carrying == expected.get(key)}
        type_param.Set(original)
        project.Regenerate()
        tests[pname]['restored'] = symbol.LookupParameter(pname).AsElementId() == original
        tests[pname]['pass'] = tests[pname]['pass'] and tests[pname]['restored']
    rec['material_substitution'] = tests

    pad = 3.0 / 12.0
    beta = math.radians(8.5)
    az = math.radians(300.0)
    target = DB.XYZ(point.X, point.Y, point.Z - G.OVERALL_HEIGHT / 24.0)
    views = []
    for name, direction, style in [
            ('Hosted Oblique', DB.XYZ(math.cos(az) * math.cos(beta), math.sin(az) * math.cos(beta), -math.sin(beta)),
             DB.DisplayStyle.Shading),
            ('Hosted Oblique Realistic', DB.XYZ(math.cos(az) * math.cos(beta), math.sin(az) * math.cos(beta),
                                                -math.sin(beta)), DB.DisplayStyle.Realistic),
            ('Hosted Below', DB.XYZ(0.35, -0.55, -0.76), DB.DisplayStyle.Shading)]:
        view = DB.View3D.CreateIsometric(project, view_type_3d(project).Id)
        view.Name = name
        eye = target.Add(direction.Normalize().Multiply(8.0))
        orient(view, eye, target.Subtract(eye), DB.XYZ.BasisZ)
        view.DetailLevel = DB.ViewDetailLevel.Fine
        view.DisplayStyle = style
        section = DB.BoundingBoxXYZ()
        section.Min = DB.XYZ(box.Min.X - pad, box.Min.Y - pad, box.Min.Z - pad)
        section.Max = DB.XYZ(box.Max.X + pad, box.Max.Y + pad, point.Z + 1.0 / 12.0)
        view.SetSectionBox(section)
        view.IsSectionBoxActive = True
        views.append(view)
    TX.Commit()
    TX = None
    try:
        export_images(project, views, HOSTED_PREFIX)
        rec['export_error'] = None
    except Exception:
        rec['export_error'] = traceback.format_exc()
    rec['images'] = list_images(HOSTED_PREFIX)
    rec['warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]


# -------------------------------------------------------------------- gates
def gates():
    fam = REPORT.get('family', {})
    host = REPORT.get('hosted', {})

    def all_pass(mapping):
        return bool(mapping) and all(v.get('pass') is True for v in mapping.values())
    saved = fam.get('saved_dimension_parameters_in', {})
    result = {
        'revit_2025_host': str(REPORT.get('revit_version', '')).startswith('2025'),
        'profile_preflight_clean': not REPORT.get('profile_problems'),
        'fresh_rfa_reopen_category': bool(fam.get('reopened')) and fam.get('category') == 'Lighting Fixtures',
        'all_parts_bound': len(fam.get('part_bindings', [])) == len(G.parts())
            and all(b['pass'] for b in fam.get('part_bindings', [])),
        'measured_dimensions': all_pass(fam.get('rays', {})),
        'measured_arm_angles': len(fam.get('arm_angles_deg', {})) == len(G.ARM_AZIMUTHS_DEG)
            and all_pass(fam.get('arm_angles_deg', {})),
        'fitter_covers_glass_opening': all_pass(fam.get('fitter_covers_opening', {})),
        'internal_clearances': bool(fam.get('internal_clearances'))
            and all(c['pass'] for c in fam['internal_clearances']),
        'saved_dimension_parameters': len(saved) == len(DIMENSION_PARAMETERS) and all(
            saved.get(n) is not None and abs(saved[n] - v) <= 1e-6 for n, v in DIMENSION_PARAMETERS),
        'native_ceiling_hosting': bool(host.get('hosted_on_floor'))
            and abs(host.get('basis_z', [0, 0, 0])[2] + 1.0) <= 1e-6
            and host.get('above_host_face_in', 1.0) <= G.HOSTED_TOL,
        'hosted_drop_and_spread': all_pass(host.get('drop_in', {})) and all_pass(host.get('spread_radius_in', {})),
        'material_substitution': len(host.get('material_substitution', {})) == len(G.MATERIAL_PARAMETERS)
            and all_pass(host.get('material_substitution', {})),
        'zero_warnings': not fam.get('warnings') and not host.get('warnings')
            and 'warnings' in fam and 'warnings' in host,
        'visual_exports_present': len([i for i in REPORT.get('family_images', []) if i['bytes'] > 0]) >= 5
            and len([i for i in host.get('images', []) if i['bytes'] > 0]) >= 3,
    }
    REPORT['gates'] = result
    REPORT['failed_gates'] = sorted(k for k, v in result.items() if not v)
    REPORT['technical_pass'] = all(result.values())
    return result


# --------------------------------------------------------------------- main
try:
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    REPORT['template'] = {'path': FACE_TEMPLATE, 'exists': os.path.isfile(FACE_TEMPLATE)}
    REPORT['profile_problems'] = G.check_profiles()
    checkpoint('preflight')
    if not str(app.VersionNumber).startswith('2025'):
        raise RuntimeError('Revit 2025 required; host reports ' + str(app.VersionNumber))
    if not REPORT['template']['exists']:
        raise RuntimeError('Family template not found: ' + FACE_TEMPLATE)
    if REPORT['profile_problems']:
        raise RuntimeError('Profile preflight failed: ' + '; '.join(REPORT['profile_problems']))

    checkpoint('building')
    rfa = build(app)
    checkpoint('reopening and measuring')
    family_doc = measure_family(app, rfa)
    checkpoint('hosted tests')
    hosted_tests(app, family_doc)
    gates()
    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    checkpoint('complete' if REPORT['technical_pass'] else 'gates-failed')
    if not REPORT['technical_pass']:
        raise RuntimeError('Gate failures: ' + ', '.join(REPORT['failed_gates']))
except Exception:
    REPORT['error'] = traceback.format_exc()
    REPORT['technical_pass'] = False
    try:
        checkpoint('failed' if REPORT.get('stage') != 'gates-failed' else 'gates-failed')
    except Exception:
        pass
    raise
finally:
    if TX is not None:
        try:
            TX.RollBack()
        except Exception:
            pass
    for document in reversed(DOCS):
        try:
            document.Close(False)
        except Exception:
            pass
