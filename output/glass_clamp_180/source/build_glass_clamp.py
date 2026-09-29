# -*- coding: utf-8 -*-
r"""SHB_Glass Clamp 180 Square - Revit 2025 family builder (pyRevit / IronPython 2.7).

Run inside Revit 2025 through the pyRevit CLI with an ABSOLUTE script path (a relative path
has returned exit 0 without running the script):

    "C:\Program Files\pyRevit-Master\bin\pyrevit.exe" run "<repo>\output\glass_clamp_180\source\build_glass_clamp.py" --revit=2025

or run output\glass_clamp_180\run_glass_clamp.ps1, which also runs the verifier.

What it does, in one Revit session, touching only new documents and output/glass_clamp_180:
  1. builds the family from Generic Model.rft per the task file (6 named reference planes plus
     helper planes, dimension-labelled parameters, 2 plates, 4 caps, subcategories, material
     bound to Clamp_Material, visibility by detail level)
  2. flexes Glass_Thickness and Clamp_Width (required) and four more parameters
     (informational), measuring the solids after every step, then rolls the flex back
  3. purges unused elements, saves with the compact option, closes and REOPENS the RFA
  4. writes the type catalog beside the RFA
  5. loads the family into a disposable project, places both types, measures the instances,
     counts material and detail-level behaviour, substitutes the material, exports views

validation.json is rewritten at every checkpoint (timestamped copy per attempt in logs/).
The script re-raises on failure because `pyrevit run` exits 0 even when a script crashes,
and it never awards itself a visual pass. The user's own Revit session and the Belmont
model are never opened.
"""
from __future__ import division

import os
import sys
import json
import math
import datetime
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List, HashSet

RUN_NAME = 'glass_clamp_180'
SCRIPT_VERSION = 'glass-clamp-builder-2026-09-29'
ENV_ROOT = 'GLASS_CLAMP_REPO_ROOT'
# Last-resort roots. The runner passes GLASS_CLAMP_REPO_ROOT and the script's own location
# is tried first, so the RFA lands in the checkout that was actually run. The 2026-09-25
# Ligne Noir check ran in the no-space OneDrive spelling.
REPO_ROOT_CANDIDATES = [
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3DModelWorkflow',
    r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow',
    r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow',
]
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return None


def repo_root():
    candidates = []
    env_root = os.environ.get(ENV_ROOT)
    if env_root:
        candidates.append((ENV_ROOT, os.path.normpath(env_root)))
    here = _script_dir()
    if here:
        candidates.append(('__file__', os.path.normpath(os.path.join(here, '..', '..', '..'))))
    candidates.extend(('fallback candidate', c) for c in REPO_ROOT_CANDIDATES)
    for source, candidate in candidates:
        if (os.path.isfile(os.path.join(candidate, 'AGENTS.md')) and
                os.path.isfile(os.path.join(candidate, 'output', RUN_NAME, 'source', 'clamp_geometry.py'))):
            return candidate, source
    raise RuntimeError('No repository root with AGENTS.md and output/%s/source/clamp_geometry.py among: %s'
                       % (RUN_NAME, ' | '.join(c for _, c in candidates)))


ROOT, ROOT_SOURCE = repo_root()
RUN_DIR = os.path.join(ROOT, 'output', RUN_NAME)
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)
sys.path.insert(0, os.path.join(RUN_DIR, 'source'))
import clamp_geometry as G  # noqa: E402  (shared with verify_glass_clamp.py and preview_geometry.py)

STARTED = datetime.datetime.utcnow()
STAMP = STARTED.strftime('%Y%m%dT%H%M%SZ')
DOCS = []
TX = [None]
REPORT = {
    'script': 'build_glass_clamp.py', 'script_version': SCRIPT_VERSION,
    'product': G.FAMILY_NAME, 'repo_root': ROOT, 'repo_root_source': ROOT_SOURCE, 'run_dir': RUN_DIR,
    'specification': 'Glass_Clamp_180_Family_Build.md (task file supplied 2026-09-29)',
    'started_utc': STARTED.isoformat(), 'stage': 'started',
    'source_status': {'verified': G.VERIFIED, 'assumed': G.ASSUMED,
                      'note': 'Values marked assumed are NOT manufacturer data.'},
    'transfer_project_standards_used': False,
    'visual_verdict': 'PENDING REVIEWER',
    'belmont_placement': ('NOT PERFORMED - the Belmont model is never opened by this script; '
                          'see README.md section "Place in the Belmont model".'),
    'gates': {},
}


# ---------------------------------------------------------------- plumbing
def out_path(*parts):
    """Every write goes through here: it raises outside output/glass_clamp_180."""
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if target != _RUN_DIR_NORM and not target.startswith(_RUN_DIR_NORM + os.sep):
        raise RuntimeError('Write path escapes the run directory: ' + target)
    parent = os.path.dirname(target)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    REPORT['updated_utc'] = datetime.datetime.utcnow().isoformat()
    payload = json.dumps(REPORT, indent=2, sort_keys=True, default=str)
    for path in (out_path('validation.json'), out_path('logs', 'validation-%s.json' % STAMP)):
        handle = open(path, 'w')
        try:
            handle.write(payload)
        finally:
            handle.close()


def gate(key, ok, detail=None, soft=False):
    REPORT['gates'][key] = {'pass': bool(ok), 'soft': bool(soft), 'detail': detail}
    return bool(ok)


def element_name(element):
    """Element.Name does not bind through a statically typed Element on the pyRevit .NET Core
    engine (MissingMemberException, P01); use the descriptor, then SYMBOL_NAME_PARAM."""
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        try:
            param = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
            return param.AsString() if param else None
        except Exception:
            return None


def ft(inches):
    return inches / 12.0


def inch(feet):
    return feet * 12.0


def pt(x, y, z):
    """Inches -> Revit feet."""
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def collect(doc, cls):
    return list(DB.FilteredElementCollector(doc).OfClass(cls))


def plain(value):
    """Floats rounded for the report; keeps JSON small and diffable."""
    return round(float(value), 6)


def attempt(label, function, *args):
    """Run one non-essential build step. A refusal is recorded in family.errors and the build
    continues, so a single rejected constraint yields an RFA plus a failed gate, not no RFA."""
    try:
        return function(*args)
    except Exception as exc:
        REPORT.setdefault('family', {}).setdefault('errors', []).append({'step': label, 'error': str(exc)})
        return None


# ---------------------------------------------------------------- API probe
def probe_api():
    """Facts about this Revit build that decide which strategy is used. Recorded, never assumed."""
    info = {}

    def methods(cls, name):
        try:
            return [str(m) for m in clr.GetClrType(cls).GetMethods() if m.Name == name]
        except Exception as exc:
            return ['probe error: %s' % exc]

    def props(cls):
        try:
            return sorted(p.Name for p in clr.GetClrType(cls).GetProperties())
        except Exception as exc:
            return ['probe error: %s' % exc]

    info['SketchPlane.Create overloads'] = methods(DB.SketchPlane, 'Create')
    info['FamilyElementVisibility properties'] = props(DB.FamilyElementVisibility)
    info['SaveAsOptions properties'] = props(DB.SaveAsOptions)
    info['Document.GetUnusedElements'] = methods(DB.Document, 'GetUnusedElements')
    info['Dimension properties'] = props(DB.Dimension)
    REPORT['api_probe'] = info
    return info


# ---------------------------------------------------------------- geometry helpers
def element_solids(element, detail=None, view=None):
    options = DB.Options()
    if detail is not None:
        options.DetailLevel = detail
    if view is not None:
        options.View = view
    found = []

    def walk(geometry):
        for item in geometry:
            if isinstance(item, DB.Solid):
                if item.Volume > 1e-12:
                    found.append(item)
            elif isinstance(item, DB.GeometryInstance):
                walk(item.GetInstanceGeometry())

    walk(element.get_Geometry(options))
    return found


def solid_stats(solid):
    """Bounds from tessellated edges, exact volume, and the radius of a cylinder about its axis."""
    points = []
    for edge in solid.Edges:
        for p in edge.Tessellate():
            points.append((inch(p.X), inch(p.Y), inch(p.Z)))
    xs, ys, zs = [p[0] for p in points], [p[1] for p in points], [p[2] for p in points]
    cx, cz = (min(xs) + max(xs)) / 2.0, (min(zs) + max(zs)) / 2.0
    radius = max(math.sqrt((p[0] - cx) ** 2 + (p[2] - cz) ** 2) for p in points)
    return {'bounds_in': {'x': [plain(min(xs)), plain(max(xs))], 'y': [plain(min(ys)), plain(max(ys))],
                          'z': [plain(min(zs)), plain(max(zs))]},
            'volume_in3': plain(solid.Volume * 1728.0),
            'centre_xz_in': [plain(cx), plain(cz)], 'radius_xz_in': plain(radius),
            'faces': int(solid.Faces.Size)}


def form_stats(form):
    solids = element_solids(form, DB.ViewDetailLevel.Fine)
    if len(solids) != 1:
        return {'error': '%d solids' % len(solids)}
    return solid_stats(solids[0])


# ---------------------------------------------------------------- material
def set_color(asset, key, color):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Appearance property missing: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(color[0], color[1], color[2]))


def set_scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        raise RuntimeError('Appearance property missing: ' + key)
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value


def make_bronze(doc, app, rec):
    """Look the material up first (task file: do not invent one); otherwise create it.
    A Generic appearance carries the task's numbers: base colour 110/86/62, roughness 0.35
    (Generic glossiness = 1 - roughness = 0.65), metallic 1.0 (generic_is_metal). No bitmap:
    the task defines a numeric appearance and the family ships no ADSKLIB."""
    for material in collect(doc, DB.Material):
        if element_name(material) == G.MATERIAL_NAME:
            rec['material'] = {'name': G.MATERIAL_NAME, 'created': False,
                               'note': 'material of this name already existed in the template'}
            return material
    source = None
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        schema = asset.FindByName('BaseSchema')
        if schema is not None and schema.Value == 'GenericSchema':
            source = asset
            break
    if source is None:
        raise RuntimeError('No GenericSchema appearance asset in the Revit appearance library')
    appearance = DB.AppearanceAssetElement.Create(doc, G.MATERIAL_NAME, source)
    material = doc.GetElement(DB.Material.Create(doc, G.MATERIAL_NAME))
    material.AppearanceAssetId = appearance.Id
    material.Color = DB.Color(G.MATERIAL_RGB[0], G.MATERIAL_RGB[1], G.MATERIAL_RGB[2])
    material.Transparency = 0
    material.MaterialClass = 'Metal'
    notes = {}
    for prop_name in ('SurfaceForegroundPatternId', 'SurfaceBackgroundPatternId'):
        try:
            setattr(material, prop_name, DB.ElementId.InvalidElementId)
            notes[prop_name] = 'none'
        except Exception as exc:
            notes[prop_name] = 'not set: %s' % exc
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    set_color(asset, 'generic_diffuse', G.MATERIAL_RGB)
    set_scalar(asset, 'generic_glossiness', G.MATERIAL_GLOSSINESS)
    set_scalar(asset, 'generic_reflectivity_at_0deg', G.MATERIAL_REFL_0)
    set_scalar(asset, 'generic_reflectivity_at_90deg', G.MATERIAL_REFL_90)
    set_scalar(asset, 'generic_self_illum_luminance', 0.0)
    metal_flag = asset.FindByName('generic_is_metal')
    if metal_flag is not None:
        metal_flag.Value = True
    notes['generic_is_metal_present'] = metal_flag is not None
    scope.Commit(True)
    scope.Dispose()
    rec['material'] = {'name': G.MATERIAL_NAME, 'created': True, 'pattern_notes': notes,
                       'appearance_schema': 'GenericSchema (library asset: %s)' % source.Name}
    return material


def read_material(doc, material):
    asset = doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
    out = {'name': element_name(material), 'material_class': material.MaterialClass,
           'graphics_rgb': [int(material.Color.Red), int(material.Color.Green), int(material.Color.Blue)],
           'graphics_transparency': int(material.Transparency)}
    colour = asset.FindByName('generic_diffuse')
    if colour is not None:
        c = colour.GetValueAsColor()
        out['diffuse_rgb'] = [int(c.Red), int(c.Green), int(c.Blue)]
        out['diffuse_connected_maps'] = int(colour.NumberOfConnectedProperties)
    for key in ('generic_glossiness', 'generic_reflectivity_at_0deg', 'generic_reflectivity_at_90deg',
                'generic_is_metal'):
        prop = asset.FindByName(key)
        out[key] = None if prop is None else prop.Value
    try:
        out['surface_foreground_pattern_none'] = (
            material.SurfaceForegroundPatternId == DB.ElementId.InvalidElementId)
    except Exception as exc:
        out['surface_foreground_pattern_none'] = 'unreadable: %s' % exc
    return out


# ---------------------------------------------------------------- reference planes / dimensions
class PlaneKit(object):
    """Creates the named reference planes, dimensions and labels."""

    def __init__(self, doc, fm, params):
        self.doc, self.fm, self.params = doc, fm, params
        self.planes = {}
        self.dim_log = []
        self.plan = None
        self.front = None
        self.side = None
        self.find_views()
        for plane in collect(doc, DB.ReferencePlane):
            self.planes[element_name(plane)] = plane

    def find_views(self):
        doc = self.doc
        views = collect(doc, DB.View)
        plans = [v for v in views if v.ViewType == DB.ViewType.FloorPlan and not v.IsTemplate]
        elevations = dict((element_name(v), v) for v in views
                          if v.ViewType == DB.ViewType.Elevation and not v.IsTemplate)
        if not plans or not elevations:
            raise RuntimeError('Template lacks a floor plan or elevations (plans %d, elevations %s)'
                               % (len(plans), sorted(elevations)))
        self.plan = plans[0]
        self.front = elevations.get('Front') or list(elevations.values())[0]
        self.side = elevations.get('Right') or elevations.get('Left') or list(elevations.values())[0]
        REPORT['family']['views_used'] = {'plan': element_name(self.plan), 'front': element_name(self.front),
                                          'side': element_name(self.side)}

    def make(self, name, axis, pos_in):
        half = 6.0
        if axis == 'x':          # normal X, drawn in plan
            a, b, cut, view = pt(pos_in, -half, 0), pt(pos_in, half, 0), DB.XYZ.BasisZ, self.plan
        elif axis == 'y':        # normal Y, drawn in plan
            a, b, cut, view = pt(-half, pos_in, 0), pt(half, pos_in, 0), DB.XYZ.BasisZ, self.plan
        else:                    # normal Z, drawn in the front elevation
            a, b, cut, view = pt(-half, 0, pos_in), pt(half, 0, pos_in), DB.XYZ.BasisY, self.front
        plane = self.doc.FamilyCreate.NewReferencePlane(a, b, cut, view)
        plane.Name = name
        self.planes[name] = plane
        return plane

    def rename_template_x(self, new_name):
        """Rename the template's X=0 plane to 'Joint CL' when Revit allows; else create one."""
        old = self.planes.get(G.TEMPLATE_X_PLANE)
        if old is not None:
            try:
                old.Name = new_name
                self.planes[new_name] = old
                del self.planes[G.TEMPLATE_X_PLANE]
                return 'renamed template plane'
            except Exception as exc:
                REPORT['family']['joint_cl_rename_error'] = str(exc)
        self.make(new_name, 'x', 0.0)
        return 'created new plane'

    def dimension(self, key, axis, names, label=None, eq=False, slot=0):
        """Linear dimension between named planes; optional parameter label; optional EQ."""
        refs = DB.ReferenceArray()
        for name in names:
            refs.Append(self.planes[name].GetReference())
        if axis == 'x':
            view, a, b = self.front, pt(-9, 0, 2.6 + 0.5 * slot), pt(9, 0, 2.6 + 0.5 * slot)
        elif axis == 'z':
            view, a, b = self.front, pt(-4.0 - 0.5 * slot, 0, -5), pt(-4.0 - 0.5 * slot, 0, 5)
        else:
            view, a, b = self.plan, pt(-4.0 - 0.5 * slot, -5, 0), pt(-4.0 - 0.5 * slot, 5, 0)
        dim = self.doc.FamilyCreate.NewLinearDimension(view, DB.Line.CreateBound(a, b), refs)
        entry = {'key': key, 'planes': list(names), 'label': label, 'eq_requested': eq}
        if label is not None:
            dim.FamilyLabel = self.params[label]
        if eq:
            try:
                dim.AreSegmentsEqual = True
                entry['eq_set'] = bool(dim.AreSegmentsEqual)
            except Exception as exc:
                entry['eq_set'] = False
                entry['eq_error'] = str(exc)
        self.dim_log.append(entry)
        return dim


def build_planes_and_dimensions(doc, fm, params):
    kit = PlaneKit(doc, fm, params)
    rec = REPORT['family']
    st = G.state()
    positions = G.plane_positions(st)
    rec['joint_cl'] = attempt('Joint CL', kit.rename_template_x, 'Joint CL')
    for name in G.TASK_PLANES + G.EXTRA_PLANES:
        if name == 'Joint CL' or name in kit.planes:
            continue
        axis, pos = positions[name]
        plane = attempt('plane ' + name, kit.make, name, axis, pos)
        if plane is not None and name == 'Glass Mid':      # the template pins only its two centre planes
            try:
                plane.Pinned = True
                rec['glass_mid_pinned'] = bool(plane.Pinned)
            except Exception as exc:
                rec['glass_mid_pinned'] = 'not pinned: %s' % exc
    doc.Regenerate()                    # materialise plane references before dimensioning (gola)
    ycen = G.TEMPLATE_Y_PLANE
    if ycen not in kit.planes:
        raise RuntimeError('Template plane missing: ' + ycen)
    dimension_plan = [
        ('glass_eq', 'y', ['Glass Face Back', ycen, 'Glass Face Front'], None, True, 0),
        ('glass_thickness', 'y', ['Glass Face Back', 'Glass Face Front'], 'Glass_Thickness', False, 1),
        ('plate_front', 'y', ['Glass Face Front', 'Plate Outer Front'], 'Plate_Thickness', False, 2),
        ('plate_back', 'y', ['Plate Outer Back', 'Glass Face Back'], 'Plate_Thickness', False, 3),
        ('cap_front', 'y', ['Plate Outer Front', 'Cap Top Front'], 'Cap_Height', False, 4),
        ('cap_back', 'y', ['Cap Top Back', 'Plate Outer Back'], 'Cap_Height', False, 5),
        ('width_eq', 'x', ['Clamp Left', 'Joint CL', 'Clamp Right'], None, True, 0),
        ('clamp_width', 'x', ['Clamp Left', 'Clamp Right'], 'Clamp_Width', False, 1),
        ('spacing_eq', 'x', ['Cap Center Left', 'Joint CL', 'Cap Center Right'], None, True, 2),
        ('cap_spacing', 'x', ['Cap Center Left', 'Cap Center Right'], 'Cap_Spacing', False, 3),
        ('height_eq', 'z', ['Clamp Bottom', 'Glass Mid', 'Clamp Top'], None, True, 0),
        ('clamp_height', 'z', ['Clamp Bottom', 'Clamp Top'], 'Clamp_Height', False, 1),
        ('cap_radius', 'z', ['Glass Mid', 'Cap Radius Top'], 'Cap_Radius', False, 2),
    ]
    for key, axis, names, label, eq, slot in dimension_plan:
        attempt('dimension ' + key, kit.dimension, key, axis, names, label, eq, slot)
    doc.Regenerate()
    rec['dimensions'] = kit.dim_log
    return kit


# ---------------------------------------------------------------- forms
def loop_of(points_in):
    curves = DB.CurveArray()
    for i in range(len(points_in)):
        a, b = points_in[i], points_in[(i + 1) % len(points_in)]
        curves.Append(DB.Line.CreateBound(pt(*a), pt(*b)))
    loops = DB.CurveArrArray()
    loops.Append(curves)
    return loops


def associate(doc, form, bip, family_param):
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(form.get_Parameter(bip), family_param)


def align_profile(doc, view, form, picker, log, label):
    """Lock each profile line to the reference plane picker() names for it.
    Same call pattern that built and flexed scripts/add_gola_cutting.py natively:
    NewAlignment(view, plane.GetReference(), sketch_curve.Reference)."""
    ok, failed = 0, []
    try:
        loops = form.Sketch.Profile
    except Exception as exc:
        log.append({'form': label, 'error': 'no Sketch.Profile: %s' % exc})
        return
    for loop in loops:
        for curve in loop:
            try:
                plane = picker(curve)
                if plane is None:
                    continue
                doc.FamilyCreate.NewAlignment(view, plane.GetReference(), curve.Reference)
                ok += 1
            except Exception as exc:
                failed.append(str(exc))
    log.append({'form': label, 'aligned': ok, 'failed': failed})


def build_plate(doc, kit, params, side, sub, material_param, forms, align_log):
    st = G.state()
    w2, h2 = st['Clamp_Width'] / 2.0, st['Clamp_Height'] / 2.0
    g2, p = st['Glass_Thickness'] / 2.0, st['Plate_Thickness']
    if side == 'front':
        start_in, end_in, start_p, end_p = g2, g2 + p, 'Glass_Face_Front_Y', 'Plate_Outer_Front_Y'
    else:
        start_in, end_in, start_p, end_p = -(g2 + p), -g2, 'Plate_Outer_Back_Y', 'Glass_Face_Back_Y'
    sketch = DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisY, DB.XYZ.Zero))
    profile = loop_of([(-w2, 0, -h2), (w2, 0, -h2), (w2, 0, h2), (-w2, 0, h2)])
    form = doc.FamilyCreate.NewExtrusion(True, profile, sketch, ft(0.25))
    start_param = form.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM)
    end_param = form.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM)
    if start_in < 0:                    # keep start < end at every step
        start_param.Set(ft(start_in))
        end_param.Set(ft(end_in))
    else:
        end_param.Set(ft(end_in))
        start_param.Set(ft(start_in))
    associate(doc, form, DB.BuiltInParameter.EXTRUSION_START_PARAM, params[start_p])
    associate(doc, form, DB.BuiltInParameter.EXTRUSION_END_PARAM, params[end_p])
    doc.Regenerate()

    def pick(curve):
        d, mid = curve.Direction, curve.Evaluate(0.5, True)      # mid is in feet; only its sign matters here
        if abs(d.X) > 0.9:
            return kit.planes['Clamp Top'] if mid.Z > 0 else kit.planes['Clamp Bottom']
        return kit.planes['Clamp Right'] if mid.X > 0 else kit.planes['Clamp Left']

    align_profile(doc, kit.front, form, pick, align_log, 'plate_' + side)
    form.Subcategory = sub
    associate(doc, form, DB.BuiltInParameter.MATERIAL_ID_PARAM, material_param)
    forms.append(('plate_' + side, form, 'plate'))
    return form


def bound_sketch_plane(doc, plane, x_in):
    """Sketch plane bound to a reference plane, so the cap follows Cap_Spacing.
    SketchPlane.Create(Document, Reference) has no precedent in this repo: fall back to a
    fixed plane and say so (the cap-spacing flex gate then fails loudly)."""
    try:
        return DB.SketchPlane.Create(doc, plane.GetReference()), 'bound to reference plane'
    except Exception as exc:
        fixed = DB.SketchPlane.Create(doc, DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisX, pt(x_in, 0, 0)))
        return fixed, 'FIXED plane (bound sketch plane failed: %s)' % exc


def build_cap(doc, kit, params, side, hand, sub, material_param, forms, align_log, sketch_modes):
    """Cap = 360-degree revolve of a rectangle about the cap axis (a Y-parallel line through the
    cap centre). Same cylinder as an extruded circle, but every profile edge is a straight line
    that can be locked to a reference plane; an extruded circle's centre and diameter cannot be
    constrained through the API."""
    st = G.state()
    g2, p, ch = st['Glass_Thickness'] / 2.0, st['Plate_Thickness'], st['Cap_Height']
    r, s2 = st['Cap_Diameter'] / 2.0, st['Cap_Spacing'] / 2.0
    cx = -s2 if hand == 'left' else s2
    if side == 'front':
        y0, y1 = g2 + p, g2 + p + ch
    else:
        y0, y1 = -(g2 + p + ch), -(g2 + p)
    plane = kit.planes['Cap Center Left' if hand == 'left' else 'Cap Center Right']
    sketch, mode = bound_sketch_plane(doc, plane, cx)
    sketch_modes.append('cap_%s_%s: %s' % (side, hand, mode))
    profile = loop_of([(cx, y0, 0), (cx, y1, 0), (cx, y1, r), (cx, y0, r)])     # counter-clockwise
    axis = DB.Line.CreateBound(pt(cx, -3.0, 0), pt(cx, 3.0, 0))     # long: covers every flex state
    form = doc.FamilyCreate.NewRevolution(True, profile, sketch, axis, 0.0, 2.0 * math.pi)
    doc.Regenerate()
    y_mid = (y0 + y1) / 2.0

    def pick(curve):
        d, mid = curve.Direction, curve.Evaluate(0.5, True)
        mid_y, mid_z = inch(mid.Y), inch(mid.Z)                # feet -> inches, to match y_mid and r
        if abs(d.Y) > 0.9:                                   # runs along the axis
            return kit.planes['Cap Radius Top'] if mid_z > r / 2.0 else None
        if side == 'front':
            return kit.planes['Cap Top Front'] if mid_y > y_mid else kit.planes['Plate Outer Front']
        return kit.planes['Plate Outer Back'] if mid_y > y_mid else kit.planes['Cap Top Back']

    align_profile(doc, kit.side, form, pick, align_log, 'cap_%s_%s' % (side, hand))
    form.Subcategory = sub
    associate(doc, form, DB.BuiltInParameter.MATERIAL_ID_PARAM, material_param)
    forms.append(('cap_%s_%s' % (side, hand), form, 'cap'))
    return form


def set_visibility(form, coarse):
    """Coarse: plates only. Medium/Fine: plates and caps. Plan/RCP, Front/Back, Left/Right on."""
    vis = DB.FamilyElementVisibility(DB.FamilyElementVisibilityType.Model)
    applied, missing = {}, []
    wanted = [('IsShownInFrontBack', True), ('IsShownInLeftRight', True), ('IsShownInPlanRCPCut', True),
              ('IsShownInTopBottom', True), ('IsShownInCoarse', coarse), ('IsShownInMedium', True),
              ('IsShownInFine', True)]
    for name, value in wanted:
        if hasattr(vis, name):
            setattr(vis, name, value)
            applied[name] = value
        else:
            missing.append(name)
    form.SetVisibility(vis)
    return {'applied': applied, 'missing_properties': missing}


def read_visibility(form):
    try:
        vis = form.GetVisibility()
    except Exception as exc:
        return {'error': 'GetVisibility failed: %s' % exc}
    out = {}
    for name in ('IsShownInFrontBack', 'IsShownInLeftRight', 'IsShownInPlanRCPCut', 'IsShownInTopBottom',
                 'IsShownInCoarse', 'IsShownInMedium', 'IsShownInFine'):
        if hasattr(vis, name):
            out[name] = bool(getattr(vis, name))
    return out


# ---------------------------------------------------------------- family build
def set_flag(param, wanted):
    if param is None:
        return {'present': False}
    entry = {'present': True, 'read_only': bool(param.IsReadOnly), 'before': param.AsInteger()}
    if not param.IsReadOnly:
        try:
            param.Set(wanted)
        except Exception as exc:
            entry['error'] = str(exc)
    entry['after'] = param.AsInteger()
    entry['wanted'] = wanted
    return entry


def apply_identity(fm, rec):
    applied = {}
    for label, bip, value in [('Manufacturer', DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, G.MANUFACTURER),
                              ('Model', DB.BuiltInParameter.ALL_MODEL_MODEL, G.MODEL),
                              ('Description', DB.BuiltInParameter.ALL_MODEL_DESCRIPTION, G.DESCRIPTION),
                              ('Type Comments', DB.BuiltInParameter.ALL_MODEL_TYPE_COMMENTS, G.TYPE_COMMENTS)]:
        param = fm.get_Parameter(bip)
        if param is None:
            applied[label] = 'built-in parameter not exposed by FamilyManager'
            continue
        fm.Set(param, value)
        applied[label] = value
    rec['identity'] = applied


def apply_length_defaults(fm, params, glass_in):
    for name, kind, default_in, formula, status in G.PARAMETERS:
        if default_in is not None:
            value = glass_in if name == 'Glass_Thickness' else default_in
            fm.Set(params[name], ft(value))


def build_family(app):
    doc = app.NewFamilyDocument(TEMPLATE)
    DOCS.append(doc)
    rec = REPORT.setdefault('family', {})
    rec['template'] = TEMPLATE
    TX[0] = DB.Transaction(doc, 'Build ' + G.FAMILY_NAME)
    TX[0].Start()
    family = doc.OwnerFamily
    family.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_GenericModel)
    rec['category'] = family.FamilyCategory.Name
    rec['always_vertical'] = set_flag(family.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL), 1)
    rec['work_plane_based'] = set_flag(family.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED), 0)

    fm = doc.FamilyManager
    default_type = fm.NewType(G.TYPES[0][0])
    params = {}
    for name, kind, default_in, formula, status in G.PARAMETERS:
        params[name] = fm.AddParameter(name, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
    for name, formula in G.HELPERS:
        params[name] = fm.AddParameter(name, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
    apply_length_defaults(fm, params, G.TYPES[0][1])
    formulas = {}
    for name, kind, default_in, formula, status in G.PARAMETERS:
        if formula:
            formulas[name] = formula
    formulas.update(dict(G.HELPERS))
    tried = {}
    for name in [n for n, _f in G.HELPERS] + ['Cap_Spacing']:
        candidates = [formulas[name]]
        if name == 'Cap_Spacing':
            candidates.append('Clamp_Width - 2"')       # inch-mark spelling, in case ' in' is refused
        for text in candidates:
            try:
                fm.SetFormula(params[name], text)
                tried[name] = text
                break
            except Exception as exc:
                tried[name] = 'FAILED %r: %s' % (text, exc)
    rec['formulas_applied'] = tried

    material = make_bronze(doc, app, rec)
    material_param = fm.AddParameter(G.MATERIAL_PARAMETER, DB.GroupTypeId.Materials,
                                     DB.SpecTypeId.Reference.Material, False)
    fm.Set(material_param, material.Id)
    params[G.MATERIAL_PARAMETER] = material_param
    apply_identity(fm, rec)

    categories = doc.Settings.Categories
    sub_plate = categories.NewSubcategory(family.FamilyCategory, G.SUBCATEGORY_PLATE)
    sub_cap = categories.NewSubcategory(family.FamilyCategory, G.SUBCATEGORY_CAP)

    checkpoint('planes and dimensions')
    kit = build_planes_and_dimensions(doc, fm, params)

    checkpoint('forms')
    forms, align_log, sketch_modes = [], [], []
    build_plate(doc, kit, params, 'front', sub_plate, material_param, forms, align_log)
    build_plate(doc, kit, params, 'back', sub_plate, material_param, forms, align_log)
    for side in ('front', 'back'):
        for hand in ('left', 'right'):
            build_cap(doc, kit, params, side, hand, sub_cap, material_param, forms, align_log, sketch_modes)
    doc.Regenerate()
    visibility = {}
    for key, form, kind in forms:
        visibility[key] = attempt('visibility ' + key, set_visibility, form, kind == 'plate') or {
            'applied': {}, 'missing_properties': ['SetVisibility failed, see family.errors']}
    doc.Regenerate()
    rec['alignments'] = align_log
    rec['sketch_plane_modes'] = sketch_modes
    rec['visibility_applied'] = visibility
    rec['forms'] = [{'key': key, 'id': str(form.Id.Value), 'kind': kind,
                     'class': form.GetType().Name} for key, form, kind in forms]
    rec['fillet'] = 'not modelled (optional and cosmetic per the task file)'

    # second type last, so every constraint was created in the default state
    second = fm.NewType(G.TYPES[1][0])
    apply_length_defaults(fm, params, G.TYPES[1][1])
    fm.Set(params[G.MATERIAL_PARAMETER], material.Id)
    apply_identity(fm, rec)
    removed_types = []
    for extra in [t for t in fm.Types if t.Name not in [n for n, _g in G.TYPES]]:
        try:
            fm.CurrentType = extra
            fm.DeleteCurrentType()
            removed_types.append(extra.Name)
        except Exception as exc:
            rec.setdefault('errors', []).append({'step': 'delete template type %r' % extra.Name, 'error': str(exc)})
    fm.CurrentType = default_type
    doc.Regenerate()
    TX[0].Commit()
    TX[0] = None
    rec['removed_template_types'] = removed_types
    rec['types'] = [t.Name for t in fm.Types]
    return doc, fm, params, forms, material


def read_family_state(doc):
    """Everything that can be read back from a family document (used before save and after reopen)."""
    fm = doc.FamilyManager
    out = {'category': doc.OwnerFamily.FamilyCategory.Name, 'is_family_document': bool(doc.IsFamilyDocument)}
    out['always_vertical'] = _int_or_none(doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL))
    out['work_plane_based'] = _int_or_none(doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED))
    types = {}
    current = fm.CurrentType
    for t in fm.Types:
        row = {}
        for p in fm.Parameters:
            name = p.Definition.Name
            try:
                if name in [n for n, _k, _d, _f, _s in G.PARAMETERS] + [n for n, _f in G.HELPERS]:
                    row[name] = plain(inch(t.AsDouble(p)))
                elif name in (G.MATERIAL_PARAMETER,):
                    row[name] = element_name(doc.GetElement(t.AsElementId(p)))
            except Exception as exc:
                row[name] = 'unreadable: %s' % exc
        for label, bip in [('Manufacturer', DB.BuiltInParameter.ALL_MODEL_MANUFACTURER),
                           ('Model', DB.BuiltInParameter.ALL_MODEL_MODEL),
                           ('Description', DB.BuiltInParameter.ALL_MODEL_DESCRIPTION),
                           ('Type Comments', DB.BuiltInParameter.ALL_MODEL_TYPE_COMMENTS)]:
            p = fm.get_Parameter(bip)
            try:
                row[label] = t.AsString(p) if p is not None else None
            except Exception as exc:
                row[label] = 'unreadable: %s' % exc
        types[t.Name] = row
    out['types'] = types
    out['current_type'] = current.Name if current is not None else None
    out['parameters'] = []
    for p in fm.Parameters:
        name = p.Definition.Name
        if name in [n for n, _k, _d, _f, _s in G.PARAMETERS] + [n for n, _f in G.HELPERS] + [G.MATERIAL_PARAMETER]:
            try:
                formula = p.Formula
            except Exception:
                formula = None
            try:
                spec = str(p.Definition.GetDataType().TypeId)
            except Exception as exc:
                spec = 'unreadable: %s' % exc
            out['parameters'].append({'name': name, 'formula': formula, 'is_instance': bool(p.IsInstance),
                                      'spec': spec})
    out['reference_planes'] = plane_positions_in(doc)
    extrusions, revolutions = collect(doc, DB.Extrusion), collect(doc, DB.Revolution)
    out['extrusions'], out['revolutions'] = len(extrusions), len(revolutions)
    out['nested_family_instances'] = len(collect(doc, DB.FamilyInstance))
    out['import_instances'] = len(collect(doc, DB.ImportInstance))
    forms = []
    for form in extrusions + revolutions:
        assoc_error = None
        try:
            assoc = fm.GetAssociatedFamilyParameter(form.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM))
        except Exception as exc:
            assoc, assoc_error = None, str(exc)
        sub = form.Subcategory
        forms.append({'id': str(form.Id.Value), 'class': form.GetType().Name, 'assoc_error': assoc_error,
                      'subcategory': sub.Name if sub is not None else None,     # Category is not an Element
                      'material_param': assoc.Definition.Name if assoc is not None else None,
                      'visibility': read_visibility(form), 'stats': form_stats(form)})
    out['forms'] = forms
    out['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    return out


def _int_or_none(param):
    return None if param is None else param.AsInteger()


def plane_positions_in(doc):
    """Reference-plane position along its own axis, inches, read from the live document.
    Origin of ReferencePlane.GetPlane() when available, else BubbleEnd (both lie on the plane)."""
    axes = dict((name, axis) for name, (axis, _p) in G.plane_positions(G.state()).items())
    axes[G.TEMPLATE_Y_PLANE] = 'y'
    result = {}
    for rp in collect(doc, DB.ReferencePlane):
        name = element_name(rp)
        axis = axes.get(name)
        if axis is None:
            continue
        try:
            p = rp.GetPlane().Origin
        except Exception:
            p = rp.BubbleEnd
        result[name] = plain(inch({'x': p.X, 'y': p.Y, 'z': p.Z}[axis]))
    return result


# ---------------------------------------------------------------- flex
def flex_family(doc, fm, params, forms):
    """Set each parameter through its values, measuring solids and planes after every step,
    inside one TransactionGroup that is rolled back so the saved defaults are untouched."""
    fam = REPORT.setdefault('family', {})
    flex = {'required': [], 'informational': []}
    group = DB.TransactionGroup(doc, 'flex ' + G.FAMILY_NAME)
    group.Start()
    try:
        for bucket, plan in (('required', G.REQUIRED_FLEX), ('informational', G.INFO_FLEX)):
            for name, values in plan:
                for value in values:
                    row = {'parameter': name, 'value_in': value}
                    tx = DB.Transaction(doc, 'flex %s %s' % (name, value))
                    tx.Start()
                    try:
                        fm.Set(params[name], ft(value))
                        doc.Regenerate()
                        status = tx.Commit()
                        row['transaction'] = str(status)
                    except Exception as exc:
                        row['error'] = str(exc)
                        try:
                            tx.RollBack()
                        except Exception:
                            pass
                    st = G.with_change(G.state(), name, value)
                    row['expected_state_in'] = st
                    try:
                        row['planes_in'] = plane_positions_in(doc)
                        row['solids'] = dict((key, form_stats(form)) for key, form, kind in forms)
                        row['cap_spacing_in'] = plain(inch(fm.CurrentType.AsDouble(params['Cap_Spacing'])))
                    except Exception as exc:
                        row['error'] = row.get('error') or ('measurement failed: %s' % exc)
                        row.setdefault('planes_in', {})
                        row.setdefault('solids', {})
                        row.setdefault('cap_spacing_in', -1.0)
                    flex[bucket].append(row)
                # return this parameter to its default before the next parameter
                default = dict((n, d) for n, _k, d, _f, _s in G.PARAMETERS)[name]
                tx = DB.Transaction(doc, 'restore %s' % name)
                tx.Start()
                fm.Set(params[name], ft(default))
                doc.Regenerate()
                tx.Commit()
    finally:
        group.RollBack()
    fam['flex_rolled_back'] = True
    REPORT['flex'] = flex
    return flex


def purge_unused(doc, keep_ids):
    tx = DB.Transaction(doc, 'Purge unused')
    tx.Start()
    record = {'method': 'Document.GetUnusedElements + Delete, keeping the bronze material and its appearance asset'}
    removed, skipped = [], []
    try:
        unused = doc.GetUnusedElements(HashSet[DB.ElementId]())
        record['unused_reported'] = len(list(unused))
        for element_id in list(unused):
            if element_id in keep_ids:
                skipped.append(str(element_id.Value))
                continue
            try:
                doc.Delete(element_id)
                removed.append(str(element_id.Value))
            except Exception:
                pass                     # already removed by a cascade, or not deletable
    except Exception as exc:
        record['error'] = str(exc)
    tx.Commit()
    record['removed'] = len(removed)
    record['kept_on_purpose'] = skipped
    return record


# ---------------------------------------------------------------- family save / reopen
def save_family(doc, path, rec):
    options = DB.SaveAsOptions()
    options.OverwriteExistingFile = True
    options.MaximumBackups = 1
    try:
        options.Compact = True
        rec['compact_option'] = 'set'
    except Exception as exc:
        rec['compact_option'] = 'unavailable: %s' % exc
    try:
        doc.SaveAs(path, options)
        rec['rfa_path'] = path
        rec['save_fallback'] = None
    except Exception as exc:
        alt = out_path('%s (build %s).rfa' % (G.FAMILY_NAME, STAMP))
        rec['save_first_error'] = str(exc)
        doc.SaveAs(alt, options)
        rec['rfa_path'] = alt
        rec['save_fallback'] = 'main file locked or refused; saved under a distinct name'
    rec['rfa_bytes'] = os.path.getsize(rec['rfa_path'])
    rec['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(os.path.getmtime(rec['rfa_path'])).isoformat()
    return rec['rfa_path']


def write_catalog():
    path = out_path(G.CATALOG_NAME)
    handle = open(path, 'wb')
    try:
        handle.write(G.catalog_text().encode('ascii'))
    finally:
        handle.close()
    return path


# ---------------------------------------------------------------- project tests
def solids_by_key(instance, detail=None, view=None, state=None, x_offset_in=0.0, z_offset_in=0.0):
    """Instance solids classified by centroid against the analytic model at `state` (default:
    the default state). The placement offsets (X: spacing between the two placed types, Z: the
    level elevation) are removed from centroids and bounds so the stats compare directly with
    the family-space expectation. Returns key -> stats."""
    found = {}
    for solid in element_solids(instance, detail, view):
        c = solid.ComputeCentroid()
        cx, cz = inch(c.X) - x_offset_in, inch(c.Z) - z_offset_in
        key = G.classify(cx, inch(c.Y), cz, state)
        stats = solid_stats(solid)
        bounds = stats['bounds_in']
        bounds['x'] = [plain(bounds['x'][0] - x_offset_in), plain(bounds['x'][1] - x_offset_in)]
        bounds['z'] = [plain(bounds['z'][0] - z_offset_in), plain(bounds['z'][1] - z_offset_in)]
        stats['centre_xz_in'][0] = plain(stats['centre_xz_in'][0] - x_offset_in)
        stats['centre_xz_in'][1] = plain(stats['centre_xz_in'][1] - z_offset_in)
        stats['centroid_in'] = [plain(cx), plain(inch(c.Y)), plain(cz)]
        stats['material_ids'] = sorted(set(str(f.MaterialElementId.Value) for f in solid.Faces))
        found[key or 'unclassified_%d' % len(found)] = stats
    return found


def make_view3d(doc, name, eye_in, forward, up, half_x, half_z, cx=0.0, cz=0.0):
    vft = next(v for v in collect(doc, DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vft.Id)
    try:
        DB.Element.Name.SetValue(view, name)
    except Exception:
        view.get_Parameter(DB.BuiltInParameter.VIEW_NAME).Set(name)
    box = DB.BoundingBoxXYZ()
    box.Min = pt(cx - half_x, -half_x, cz - half_z)
    box.Max = pt(cx + half_x, half_x, cz + half_z)
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    view.SetOrientation(DB.ViewOrientation3D(pt(cx + eye_in[0], eye_in[1], cz + eye_in[2]), up, forward))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.ShadingWithEdges
    for param in view.Parameters:
        if param.Definition.Name == 'Sun Path' and not param.IsReadOnly:
            param.Set(0)
    return view


def export_view(doc, view, prefix):
    folder = out_path('exports')
    if not os.path.isdir(folder):
        os.makedirs(folder)
    before = set(os.listdir(folder))
    options = DB.ImageExportOptions()
    options.ZoomType = DB.ZoomFitType.FitToPage
    options.PixelSize = 1600
    options.FitDirection = DB.FitDirectionType.Horizontal
    options.HLRandWFViewsFileType = DB.ImageFileType.PNG
    options.ShadowViewsFileType = DB.ImageFileType.PNG
    options.ImageResolution = DB.ImageResolution.DPI_150
    options.ExportRange = DB.ExportRange.SetOfViews
    ids = List[DB.ElementId]()
    ids.Add(view.Id)
    options.SetViewsAndSheets(ids)
    options.FilePath = os.path.join(folder, prefix)
    entry = {'view': element_name(view)}
    try:
        doc.ExportImage(options)
        entry['files'] = [{'file': n, 'bytes': os.path.getsize(os.path.join(folder, n))}
                          for n in sorted(set(os.listdir(folder)) - before)]
    except Exception as exc:
        entry['error'] = str(exc)
        entry['files'] = []
    return entry


def project_tests(app, family_doc):
    rec = REPORT.setdefault('project', {})
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    family = family_doc.LoadFamily(project)
    symbols = {}
    for symbol_id in family.GetFamilySymbolIds():
        symbol = project.GetElement(symbol_id)
        symbols[element_name(symbol)] = symbol
    rec['symbols'] = sorted(symbols)
    level = sorted(collect(project, DB.Level), key=lambda l: l.Elevation)[0]      # lowest level, normally 0 ft
    level_z_in = inch(level.Elevation)
    rec['level_used'] = {'elevation_in': plain(level_z_in)}
    tx = DB.Transaction(project, 'Place and test ' + G.FAMILY_NAME)
    tx.Start()
    placements, instances = {}, {}
    for index, (type_name, glass) in enumerate(G.TYPES):
        symbol = symbols[type_name]
        symbol.Activate()
        project.Regenerate()
        origin = DB.XYZ(4.0 * index, 0.0, level.Elevation)     # 4 ft apart, on the level, feet
        instance = project.Create.NewFamilyInstance(origin, symbol, level, DB.Structure.StructuralType.NonStructural)
        project.Regenerate()
        instances[type_name] = instance
        expected = G.state(glass=glass)
        placements[type_name] = {
            'glass_in': glass, 'placed_at_x_in': 48.0 * index, 'expected_state_in': expected,
            'solids': solids_by_key(instance, DB.ViewDetailLevel.Fine, None, expected, 48.0 * index, level_z_in)}
    rec['placements'] = placements

    # detail level: Coarse plates only, Medium/Fine plates and caps (geometry read through the view)
    probe = instances[G.DEFAULT_TYPE]
    levels = {}
    view = make_view3d(project, 'Detail probe', (0, -60, 0), DB.XYZ(0, 1, 0), DB.XYZ(0, 0, 1), 4.0, 2.5, 0.0, level_z_in)
    for label, detail in (('Coarse', DB.ViewDetailLevel.Coarse), ('Medium', DB.ViewDetailLevel.Medium),
                          ('Fine', DB.ViewDetailLevel.Fine)):
        view.DetailLevel = detail
        project.Regenerate()
        found = solids_by_key(probe, None, view, None, 0.0, level_z_in)
        levels[label] = sorted(found)
    rec['detail_levels'] = levels
    view.DetailLevel = DB.ViewDetailLevel.Fine

    # material substitution: all faces carry the bronze; the substitute reaches every face; restore
    symbol = symbols[G.DEFAULT_TYPE]
    param = symbol.LookupParameter(G.MATERIAL_PARAMETER)
    original = param.AsElementId()
    swap = {'original_material': element_name(project.GetElement(original))}
    faces_before = solids_by_key(probe, DB.ViewDetailLevel.Fine, None, None, 0.0, level_z_in)
    swap['original_face_material_ids'] = sorted(set(i for s in faces_before.values() for i in s['material_ids']))
    substitute = project.GetElement(DB.Material.Create(project, 'QA substitute material'))
    param.Set(substitute.Id)
    project.Regenerate()
    faces_swapped = solids_by_key(probe, DB.ViewDetailLevel.Fine, None, None, 0.0, level_z_in)
    swap['substitute_id'] = str(substitute.Id.Value)
    swap['swapped_face_material_ids'] = sorted(set(i for s in faces_swapped.values() for i in s['material_ids']))
    param.Set(original)
    project.Regenerate()
    faces_restored = solids_by_key(probe, DB.ViewDetailLevel.Fine, None, None, 0.0, level_z_in)
    swap['restored_face_material_ids'] = sorted(set(i for s in faces_restored.values() for i in s['material_ids']))
    swap['original_id'] = str(original.Value)
    rec['material_swap'] = swap
    tx.Commit()

    # exports: front (toward the room, +Y looking -Y), plan, side, iso; the 1/2 in type only
    tx = DB.Transaction(project, 'Review views')
    tx.Start()
    forward = DB.XYZ(-30.0, -40.0, -25.0).Normalize()
    right = forward.CrossProduct(DB.XYZ.BasisZ).Normalize()
    iso_up = right.CrossProduct(forward).Normalize()          # perpendicular to forward, as Revit requires
    views = [make_view3d(project, 'Clamp Front', (0, 60, 0), DB.XYZ(0, -1, 0), DB.XYZ(0, 0, 1), 4.0, 2.5, 0.0, level_z_in),
             make_view3d(project, 'Clamp Plan', (0, 0, 60), DB.XYZ(0, 0, -1), DB.XYZ(0, 1, 0), 4.0, 2.5, 0.0, level_z_in),
             make_view3d(project, 'Clamp Side', (60, 0, 0), DB.XYZ(-1, 0, 0), DB.XYZ(0, 0, 1), 4.0, 2.5, 0.0, level_z_in),
             make_view3d(project, 'Clamp Iso', (30, 40, 25), forward, iso_up, 4.0, 2.5, 0.0, level_z_in)]
    tx.Commit()
    rec['exports'] = [export_view(project, v, 'glass_clamp') for v in views]
    rec['warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    return rec


def complete_project(found):
    """Defaults for whatever the project stage did not reach, so every gate can still be computed
    (and fail honestly) when that stage stopped early."""
    swap = {'original_face_material_ids': [], 'swapped_face_material_ids': [],
            'restored_face_material_ids': [], 'substitute_id': None}
    swap.update(found.get('material_swap', {}))
    out = {'placements': {}, 'detail_levels': {'Coarse': [], 'Medium': [], 'Fine': []}, 'exports': [],
           'warnings': ['project stage did not complete: see project_error']}
    out.update(found)
    out['material_swap'] = swap
    if 'project_error' not in REPORT:
        out['warnings'] = found.get('warnings', [])
    REPORT['project'] = out
    return out


# ---------------------------------------------------------------- gates
VOLUME_REL_TOL = 0.002


def compare_solids(measured, st):
    """(worst position error in inches, worst relative volume error, per-solid detail) between
    measured solid stats keyed by solid name and the analytic expectation at parameter state st."""
    expected = G.solids(st)
    worst_pos, worst_vol, detail = 0.0, 0.0, {}
    for key, want in expected.items():
        got = measured.get(key)
        if not got or 'bounds_in' not in got:
            detail[key] = 'missing'
            worst_pos = max(worst_pos, 9.9)
            continue
        dev = max(abs(got['bounds_in']['y'][0] - want['y'][0]), abs(got['bounds_in']['y'][1] - want['y'][1]))
        if want['kind'] == 'plate':
            for axis in 'xz':
                dev = max(dev, abs(got['bounds_in'][axis][0] - want[axis][0]),
                          abs(got['bounds_in'][axis][1] - want[axis][1]))
        else:
            dev = max(dev, abs(got['centre_xz_in'][0] - want['cx']), abs(got['centre_xz_in'][1] - want['cz']),
                      abs(got['radius_xz_in'] - (want['x'][1] - want['x'][0]) / 2.0))
        vol = abs(got['volume_in3'] - want['volume']) / max(want['volume'], 1e-9)
        detail[key] = {'max_dev_in': plain(dev), 'volume_rel_err': plain(vol)}
        worst_pos, worst_vol = max(worst_pos, dev), max(worst_vol, vol)
    return worst_pos, worst_vol, detail


def stats_by_key(form_rows, form_records):
    """Map read_family_state()['forms'] rows to solid names through the element ids recorded at build."""
    key_by_id = dict((f['id'], f['key']) for f in form_records)
    return dict((key_by_id[row['id']], row['stats']) for row in form_rows if row['id'] in key_by_id)


def flex_problems(flex, bucket, param):
    rows = [r for r in flex[bucket] if r['parameter'] == param]
    problems = []
    for r in rows:
        if 'error' in r:
            problems.append({'value': r['value_in'], 'error': r['error']})
            continue
        want = G.with_change(G.state(), param, r['value_in'])
        pos, vol, _ = compare_solids(r['solids'], want)
        plane_dev = max(abs(r['planes_in'].get(n, 9e9) - p) for n, (axis, p) in G.plane_positions(want).items())
        spacing_dev = abs(r['cap_spacing_in'] - want['Cap_Spacing'])
        if pos > G.GEOM_TOL_IN or vol > VOLUME_REL_TOL or plane_dev > G.DIM_TOL_IN or spacing_dev > G.DIM_TOL_IN:
            problems.append({'value': r['value_in'], 'solid_dev_in': plain(pos), 'volume_rel_err': plain(vol),
                             'plane_dev_in': plain(plane_dev), 'spacing_dev_in': plain(spacing_dev)})
    return (bool(rows) and not problems), {'rows': len(rows), 'problems': problems}


def compute_gates(before_save, reopened, flex, project, catalog_path, rfa_path, purge_rec):
    rec = REPORT['family']
    st = G.state()
    form_records = rec.get('forms', [])
    forms_ok = (len(form_records) == 6 and before_save['extrusions'] == 2 and before_save['revolutions'] == 4)
    gate('G01_family_category_generic_models', before_save['category'] == 'Generic Models', before_save['category'])
    av = rec.get('always_vertical', {})
    gate('G02_always_vertical_on', av.get('after') == 1, av, soft=True)
    wp = rec.get('work_plane_based', {})
    gate('G03_work_plane_based_off', wp.get('after') == 0, wp)
    want_planes = G.plane_positions(st)
    plane_dev, plane_missing = 0.0, []
    for name in G.TASK_PLANES + G.EXTRA_PLANES:
        got = before_save['reference_planes'].get(name)
        if got is None:
            plane_missing.append(name)
            continue
        plane_dev = max(plane_dev, abs(got - want_planes[name][1]))
    gate('G04_reference_planes_named_and_placed', not plane_missing and plane_dev <= G.DIM_TOL_IN,
         {'missing': plane_missing, 'max_dev_in': plane_dev})
    types = before_save['types']
    defaults = types.get(G.DEFAULT_TYPE, {})
    param_bad = [n for n, k, d, f, s in G.PARAMETERS
                 if d is not None and n != 'Glass_Thickness' and abs(defaults.get(n, -9) - d) > G.DIM_TOL_IN]
    gate('G05_parameters_and_defaults',
         not param_bad and abs(defaults.get('Glass_Thickness', -9) - 0.5) <= G.DIM_TOL_IN
         and len(before_save['parameters']) >= len(G.PARAMETERS) + len(G.HELPERS) + 1,
         {'bad': param_bad, 'defaults': defaults})
    gate('G06_cap_spacing_formula', abs(defaults.get('Cap_Spacing', -9) - 3.0) <= G.DIM_TOL_IN,
         {'value_in': defaults.get('Cap_Spacing'), 'formula_applied': rec.get('formulas_applied', {}).get('Cap_Spacing')})
    gate('G07_types', sorted(types) == sorted(n for n, _g in G.TYPES)
         and all(abs(types[n].get('Glass_Thickness', -9) - g) <= G.DIM_TOL_IN for n, g in G.TYPES)
         and before_save['current_type'] == G.DEFAULT_TYPE, {'types': sorted(types), 'current': before_save['current_type']})
    gate('G08_identity_and_type_comments',
         all(types[n].get('Manufacturer') == G.MANUFACTURER and types[n].get('Model') == G.MODEL
             and types[n].get('Description') == G.DESCRIPTION and types[n].get('Type Comments') == G.TYPE_COMMENTS
             for n in types), dict((n, dict((k, types[n].get(k)) for k in ('Manufacturer', 'Model', 'Description', 'Type Comments')))
                                   for n in types))
    gate('G09_six_separate_forms_no_nested_no_imports',
         forms_ok and before_save['nested_family_instances'] == 0 and before_save['import_instances'] == 0,
         {'extrusions': before_save['extrusions'], 'revolutions': before_save['revolutions'],
          'nested': before_save['nested_family_instances'], 'imports': before_save['import_instances']})
    measured = stats_by_key(before_save['forms'], form_records)
    pos, vol, detail = compare_solids(measured, st)
    gate('G10_default_geometry_matches_analytic_model', pos <= G.GEOM_TOL_IN and vol <= VOLUME_REL_TOL,
         {'worst_dev_in': plain(pos), 'worst_volume_rel_err': plain(vol), 'per_solid': detail})
    subs = [f['subcategory'] for f in before_save['forms']]
    gate('G11_subcategories', sorted(subs) == sorted([G.SUBCATEGORY_PLATE] * 2 + [G.SUBCATEGORY_CAP] * 4), subs)
    bound = [f['material_param'] for f in before_save['forms']]
    gate('G12_material_bound_to_clamp_material',
         len(bound) == 6 and all(b == G.MATERIAL_PARAMETER for b in bound)
         and defaults.get(G.MATERIAL_PARAMETER) == G.MATERIAL_NAME,
         {'bound': bound, 'default': defaults.get(G.MATERIAL_PARAMETER)})
    mat = rec.get('material_readback', {})
    gate('G13_material_appearance',
         mat.get('diffuse_rgb') == list(G.MATERIAL_RGB) and mat.get('graphics_rgb') == list(G.MATERIAL_RGB)
         and abs((mat.get('generic_glossiness') or -1) - G.MATERIAL_GLOSSINESS) < 1e-6
         and mat.get('generic_is_metal') in (True, 1), mat)
    kind_by_id = dict((f['id'], f['kind']) for f in form_records)
    vis_bad = []
    for row in before_save['forms']:
        v = row['visibility']
        want_coarse = kind_by_id.get(row['id']) == 'plate'
        if v.get('IsShownInCoarse') != want_coarse or not v.get('IsShownInMedium') or not v.get('IsShownInFine'):
            vis_bad.append(row['id'])
    gate('G14_visibility_by_detail_level', not vis_bad and len(before_save['forms']) == 6,
         {'bad': vis_bad, 'missing_properties': sorted(set(m for v in rec.get('visibility_applied', {}).values()
                                                            for m in v['missing_properties']))})
    ok, det = flex_problems(flex, 'required', 'Glass_Thickness')
    gate('G15_flex_glass_thickness_plates_move_outward', ok, det)
    ok, det = flex_problems(flex, 'required', 'Clamp_Width')
    gate('G16_flex_clamp_width_caps_centred_per_formula', ok, det)
    info_problems = {}
    for name, _values in G.INFO_FLEX:
        ok, det = flex_problems(flex, 'informational', name)
        if not ok:
            info_problems[name] = det
    gate('G17_flex_informational_height_diameter_capheight_plate', not info_problems, info_problems, soft=True)
    gate('G18_no_family_warnings', not before_save['warnings'] and not reopened['warnings'],
         {'before_save': before_save['warnings'], 'reopened': reopened['warnings']})
    gate('G19_purge_unused_ran_and_kept_material',
         'error' not in purge_rec and purge_rec.get('removed') is not None and len(reopened['forms']) == 6
         and all(f['material_param'] == G.MATERIAL_PARAMETER for f in reopened['forms']), purge_rec)
    size = rec.get('rfa_bytes')
    gate('G20_saved_compact_under_500kb', size is not None and size < G.FILE_SIZE_LIMIT_BYTES,
         {'bytes': size, 'limit': G.FILE_SIZE_LIMIT_BYTES, 'path': rfa_path, 'compact_option': rec.get('compact_option')})
    cat_ok = os.path.isfile(catalog_path) and open(catalog_path, 'rb').read().decode('ascii') == G.catalog_text()
    gate('G21_type_catalog_written', cat_ok, catalog_path)
    r_meas = stats_by_key(reopened['forms'], form_records)
    rpos, rvol, _ = compare_solids(r_meas, st)
    gate('G22_reopened_from_disk_same_state',
         reopened['is_family_document'] and reopened['category'] == 'Generic Models'
         and reopened['extrusions'] == 2 and reopened['revolutions'] == 4
         and sorted(reopened['types']) == sorted(n for n, _g in G.TYPES)
         and rpos <= G.GEOM_TOL_IN and rvol <= VOLUME_REL_TOL, {'worst_dev_in': plain(rpos)})
    worst_place, place_detail = 0.0, {}
    for type_name, placed in project['placements'].items():
        d, v, _ = compare_solids(placed['solids'], placed['expected_state_in'])
        place_detail[type_name] = {'dev_in': plain(d), 'volume_rel_err': plain(v)}
        worst_place = max(worst_place, d, 0.0 if v <= VOLUME_REL_TOL else 9.9)
    gate('G23_project_load_and_place_both_types', worst_place <= G.GEOM_TOL_IN and len(project['placements']) == 2,
         place_detail)
    swap = project['material_swap']
    orig, sub, back = swap['original_face_material_ids'], swap['swapped_face_material_ids'], swap['restored_face_material_ids']
    gate('G24_material_substitution_reaches_every_face',
         len(orig) == 1 and sub == [swap['substitute_id']] and back == orig, swap)
    dl = project['detail_levels']
    everything = sorted(G.solids(G.state()).keys())
    gate('G25_detail_levels_coarse_plates_only',
         dl['Coarse'] == ['plate_back', 'plate_front'] and dl['Medium'] == everything and dl['Fine'] == everything,
         dl, soft=True)
    gate('G26_no_project_warnings', not project['warnings'], project['warnings'])
    names_ok = all(ch.isalnum() or ch in ' -_' for ch in G.MATERIAL_NAME)
    gate('G27_fbx_clean_structure',
         names_ok and forms_ok and before_save['nested_family_instances'] == 0
         and before_save['import_instances'] == 0 and len(set(bound)) == 1,
         {'material_name_safe': names_ok, 'material_slot_sources': sorted(set(bound))})
    exported = [f for e in project['exports'] for f in e.get('files', [])]
    gate('G28_review_views_exported', len(exported) >= 4, {'files': [f['file'] for f in exported]}, soft=True)
    gate('G29_material_surface_pattern_none', mat.get('surface_foreground_pattern_none') is True,
         {'readback': mat.get('surface_foreground_pattern_none'), 'notes': rec.get('material', {}).get('pattern_notes')},
         soft=True)
    failed = sorted(k for k, v in REPORT['gates'].items() if not v['pass'] and not v['soft'])
    REPORT['failed_gates'] = failed
    REPORT['soft_failed_gates'] = sorted(k for k, v in REPORT['gates'].items() if not v['pass'] and v['soft'])
    REPORT['technical_pass'] = not failed
    return failed


# ---------------------------------------------------------------- main
def main():
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['family'] = {}
    checkpoint('probe')
    probe_api()
    if not os.path.isfile(TEMPLATE):
        raise RuntimeError('Template missing: ' + TEMPLATE)
    checkpoint('build family')
    doc, fm, params, forms, material = build_family(app)
    rec = REPORT['family']
    stage_errors = REPORT.setdefault('stage_errors', [])

    def guarded(label, function, *args):
        try:
            return function(*args)
        except Exception:
            stage_errors.append({'stage': label, 'error': traceback.format_exc()})
            return None

    rec['material_readback'] = guarded('material readback', read_material, doc, material) or {}
    before_save = guarded('state before save', read_family_state, doc) or {}
    rec['state_before_save'] = before_save
    checkpoint('flex')
    flex = guarded('flex', flex_family, doc, fm, params, forms) or REPORT.get('flex') or {'required': [], 'informational': []}
    REPORT['flex'] = flex

    def restore_default_type():
        tx = DB.Transaction(doc, 'Restore default type')
        tx.Start()
        try:
            fm.CurrentType = [t for t in fm.Types if t.Name == G.DEFAULT_TYPE][0]
            doc.Regenerate()
        finally:
            tx.Commit()
    guarded('restore default type', restore_default_type)
    rec['defaults_after_flex'] = (guarded('defaults after flex', read_family_state, doc) or {}).get(
        'types', {}).get(G.DEFAULT_TYPE, {})
    checkpoint('purge and save')
    keep = set([material.Id, material.AppearanceAssetId])
    purge_rec = guarded('purge', purge_unused, doc, keep) or {'error': 'purge stage failed, see stage_errors'}
    rec['purge'] = purge_rec
    rfa_path = save_family(doc, out_path(G.RFA_NAME), rec)
    catalog_path = write_catalog()
    rec['catalog_path'] = catalog_path
    DOCS.remove(doc)
    doc.Close(False)
    checkpoint('reopen')
    reopened_doc = app.OpenDocumentFile(rfa_path)
    DOCS.append(reopened_doc)
    reopened = read_family_state(reopened_doc)
    REPORT['reopened'] = reopened
    checkpoint('project tests')
    try:
        project_tests(app, reopened_doc)
    except Exception:
        REPORT['project_error'] = traceback.format_exc()
    project = complete_project(REPORT.get('project', {}))
    checkpoint('gates')
    try:
        failed = compute_gates(before_save, reopened, flex, project, catalog_path, rfa_path, purge_rec)
    except Exception:
        REPORT['gate_error'] = traceback.format_exc()
        REPORT['technical_pass'] = False
        REPORT['failed_gates'] = ['gates could not be computed: see gate_error and stage_errors']
        failed = REPORT['failed_gates']
    if stage_errors:
        REPORT['technical_pass'] = False
    REPORT['rfa_path'] = rfa_path
    REPORT['catalog_path'] = catalog_path
    REPORT['export_folder'] = out_path('exports')
    checkpoint('complete')
    return failed


def run():
    try:
        main()
    except Exception:
        REPORT['error'] = traceback.format_exc()
        checkpoint('failed at ' + str(REPORT.get('stage')))
        raise
    finally:
        if TX[0] is not None:
            try:
                TX[0].RollBack()
            except Exception:
                pass
        for d in reversed(DOCS):
            try:
                d.Close(False)
            except Exception:
                pass


run()
