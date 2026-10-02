# -*- coding: utf-8 -*-
r"""SHB_Glass Clamp 180 Square (CRL SGC180BBRZ stand-in) - Revit 2025 family builder.

Run inside Revit 2025 through the pyRevit CLI with an ABSOLUTE script path
(a relative path has returned exit 0 without running the script, E026):

    pyrevit run "<repo>\output\glass_clamp_180\source\build_clamp.py" --revit=2025

or run output\glass_clamp_180\run_clamp.ps1, which also runs the verifier.

One Revit session, touching only new documents and output/glass_clamp_180:
  1. Generic Model.rft (non-hosted): Always Vertical on, Work Plane-Based off, types
     '3-8 Glass' and '1-2 Glass', parameters from clamp_spec.py
  2. named reference planes driven by labelled dimensions (no formulas on planes)
  3. plates: extrusions sketched on the glass-face planes, depth = Plate_Thickness,
     four side faces aligned and locked to the clamp-edge planes
  4. screw heads (rear plate, CRL rear view): extrusions sketched on Plate Outer Back,
     depth = Cap_Height; centre and diameter constrained inside the sketch
     (SketchEditScope) to Cap_Offset, Cap_Elevation and Cap_Diameter
  5. subcategories, Clamp_Material binding, coarse visibility off for screw heads
  6. purge unused, compact save, close, REOPEN; measure every part by ray
  7. load into a disposable project, place, switch type, substitute the material
  8. flex Glass_Thickness / Clamp_Width / Cap_Diameter / Plate_Thickness in the reopened
     family with a failure capture, re-measure every step, restore, close unsaved
  9. export review images

validation.json is rewritten at every checkpoint (timestamped copy per attempt in logs/).
The script re-raises on failure because `pyrevit run` exits 0 even when a script
crashes (P01, 2026-09-18). It never awards itself a visual pass.
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
from Autodesk.Revit.DB.Structure import StructuralType
from System.Collections.Generic import List, HashSet

RUN_NAME = 'glass_clamp_180'
SCRIPT_VERSION = 'clamp-builder-2026-09-30'
TEMPLATE_NAME = 'Generic Model.rft'
TEMPLATE = None     # resolved at run time by find_template(); never a fixed install path
IMAGE_PREFIX = 'Clamp'
PROJECT_PREFIX = 'Clamp_Project'


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return None


def _walk_up(start):
    path = os.path.abspath(start)
    while True:
        yield path
        parent = os.path.dirname(path)
        if parent == path:
            return
        path = parent


def repo_root():
    """The checkout this script lives in: CLAMP_REPO_ROOT, else walk up from this file, else from
    the working directory. No user name, drive or folder name is assumed."""
    candidates = []
    env_root = os.environ.get('CLAMP_REPO_ROOT')
    if env_root:
        candidates.append(('CLAMP_REPO_ROOT', os.path.normpath(env_root)))
    here = _script_dir()
    if here:
        candidates.extend(('walk up from __file__', p) for p in _walk_up(here))
    try:
        candidates.extend(('walk up from working directory', p) for p in _walk_up(os.getcwd()))
    except Exception:
        pass
    for source, candidate in candidates:
        if (os.path.isfile(os.path.join(candidate, 'AGENTS.md')) and
                os.path.isfile(os.path.join(candidate, 'output', RUN_NAME, 'source', 'clamp_spec.py'))):
            return candidate, source
    raise RuntimeError('No repository root (AGENTS.md + output/%s/source/clamp_spec.py) found; first tried: %s'
                       % (RUN_NAME, ' | '.join('%s: %s' % c for c in candidates[:6])))


def _startup_failure(text):
    """The run folder is unknown here, so no validation.json can be written; leave a note in TEMP."""
    try:
        import tempfile
        with open(os.path.join(tempfile.gettempdir(), 'clamp_builder_startup_error.txt'), 'w') as handle:
            handle.write(text)
    except Exception:
        pass


try:
    ROOT, ROOT_SOURCE = repo_root()
except Exception:
    _startup_failure(traceback.format_exc())
    raise
RUN_DIR = os.path.join(ROOT, 'output', RUN_NAME)
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)
sys.path.insert(0, os.path.join(RUN_DIR, 'source'))
import clamp_spec as S  # noqa: E402

REPORT = {
    'script': 'output/%s/source/build_clamp.py' % RUN_NAME,
    'script_version': SCRIPT_VERSION,
    'repo_root': ROOT,
    'repo_root_source': ROOT_SOURCE,
    'run_dir': RUN_DIR,
    'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'rfa_name': S.RFA_NAME,
    'spec_values_in': S.resolve(),
    'visual_verdict': 'PENDING REVIEWER - exports produced, fidelity not self-assessed',
}
DOCS = []
TX = None
CAPTURED = []   # failures from build / purge / project transactions (flex keeps its own)


# ------------------------------------------------------------------ template
def find_template(app):
    """Generic Model.rft for this Revit, wherever it is installed. Order: CLAMP_TEMPLATE, the
    folder Revit reports (FamilyTemplatePath) and its parent, %ProgramData%\\Autodesk\\RVT 2025.
    English-Imperial is preferred; any other copy is used only if no Imperial one exists."""
    roots = []
    try:
        reported = app.FamilyTemplatePath
    except Exception:
        reported = None
    if reported:
        roots.extend([reported, os.path.dirname(reported.rstrip('\\/'))])
    program_data = os.environ.get('ProgramData')
    if program_data:
        roots.append(os.path.join(program_data, 'Autodesk', 'RVT 2025', 'Family Templates'))
    seen, ordered = set(), []
    for root in roots:
        key = os.path.normcase(os.path.normpath(root))
        if key not in seen and os.path.isdir(root):
            seen.add(key)
            ordered.append(root)
    info = {'roots_searched': ordered, 'family_template_path_reported': reported}
    env = os.environ.get('CLAMP_TEMPLATE')
    if env and os.path.isfile(env):
        info.update({'path': env, 'source': 'CLAMP_TEMPLATE'})
        return info
    hits = []
    for root in ordered:
        for dirpath, dirs, files in os.walk(root):
            if TEMPLATE_NAME in files:
                hits.append(os.path.join(dirpath, TEMPLATE_NAME))
            dirs[:] = [d for d in dirs if dirpath.count(os.sep) - root.count(os.sep) < 2]
    hits.sort(key=lambda path: ('Imperial' not in path, path))
    info['candidates'] = hits
    if hits:
        info.update({'path': hits[0], 'source': 'search', 'imperial': 'Imperial' in hits[0]})
    else:
        info.update({'path': None, 'source': None})
    return info


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


def ft(inches_value):
    return inches_value / 12.0


def xyz(x, y, z):
    return DB.XYZ(x / 12.0, y / 12.0, z / 12.0)


def inches(point):
    return (point.X * 12.0, point.Y * 12.0, point.Z * 12.0)


def vec(p):
    return [round(p.X, 9), round(p.Y, 9), round(p.Z, 9)]


def solids(geometry):
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for solid in solids(item.GetInstanceGeometry()):
                yield solid


def element_solids(element, detail=None, references=False):
    options = DB.Options()
    options.ComputeReferences = references
    if detail is not None:
        options.DetailLevel = detail
    geometry = element.get_Geometry(options)
    return list(solids(geometry)) if geometry is not None else []


def solid_segments(solid_list, p0_in, p1_in, transform=None):
    """Portions of the line p0-p1 (inches) inside the solids, as inch tuples in the same frame."""
    a, b = xyz(*p0_in), xyz(*p1_in)
    if transform is not None:
        a, b = transform.OfPoint(a), transform.OfPoint(b)
    line = DB.Line.CreateBound(a, b)
    inverse = transform.Inverse if transform is not None else None
    found = []
    for solid in solid_list:
        result = solid.IntersectWithCurve(line, DB.SolidCurveIntersectionOptions())
        for index in range(result.SegmentCount):
            segment = result.GetCurveSegment(index)
            e0, e1 = segment.GetEndPoint(0), segment.GetEndPoint(1)
            if inverse is not None:
                e0, e1 = inverse.OfPoint(e0), inverse.OfPoint(e1)
            found.append((inches(e0), inches(e1)))
    return found


def ray_row(ray, segments, merge=True):
    ok, got, want = S.compare(ray, segments, merge=merge)
    return {'key': ray['key'], 'axis': ray['axis'], 'p0': ray['p0'], 'p1': ray['p1'],
            'segments': segments, 'measured': got, 'expected': want, 'pass': ok}


class FailureCapture(DB.IFailuresPreprocessor):
    """Records every failure; deletes warnings, rolls back on any error (no UI dialogs)."""

    def __init__(self, name='', collect=True):
        self.name = name
        self.collect = collect
        self.messages = []

    def PreprocessFailures(self, accessor):
        has_error = False
        for failure in accessor.GetFailureMessages():
            severity = failure.GetSeverity()
            row = {'transaction': self.name, 'severity': str(severity), 'text': failure.GetDescriptionText()}
            self.messages.append(row)
            if self.collect:
                CAPTURED.append(row)
            if severity == DB.FailureSeverity.Warning:
                accessor.DeleteWarning(failure)
            else:
                has_error = True
        if has_error:
            return DB.FailureProcessingResult.ProceedWithRollBack
        return DB.FailureProcessingResult.Continue


def captured_transaction(doc, name, collect=True):
    tx = DB.Transaction(doc, name)
    capture = FailureCapture(name, collect)
    options = tx.GetFailureHandlingOptions()
    options.SetFailuresPreprocessor(capture)
    options.SetClearAfterRollback(True)
    tx.SetFailureHandlingOptions(options)
    return tx, capture


# --------------------------------------------------------------- lookups
def find_view(doc, view_type, name):
    for view in DB.FilteredElementCollector(doc).OfClass(DB.View):
        if not view.IsTemplate and view.ViewType == view_type and view.Name == name:
            return view
    raise RuntimeError('Template view not found: %s %s' % (view_type, name))


def find_plane(doc, name):
    for plane in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane):
        if plane.Name == name:
            return plane
    return None


def family_param(doc, name):
    param = doc.FamilyManager.get_Parameter(name)
    if param is None:
        raise RuntimeError('Family parameter missing: ' + name)
    return param


# ------------------------------------------------------------ materials
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


def make_material(doc, app, record):
    """Family default for Clamp_Material. A project material of the same name wins on load."""
    spec = S.MATERIAL
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = next((a for a in assets if a.FindByName('BaseSchema') is not None
                   and a.FindByName('BaseSchema').Value == 'GenericSchema'), None)
    if source is None:
        raise RuntimeError('No GenericSchema appearance asset in the Revit appearance library')
    record['appearance_source_asset'] = source.Name
    appearance = DB.AppearanceAssetElement.Create(doc, spec['name'], source)
    material = doc.GetElement(DB.Material.Create(doc, spec['name']))
    material.AppearanceAssetId = appearance.Id
    material.Color = DB.Color(spec['color'][0], spec['color'][1], spec['color'][2])   # shading colour
    material.MaterialClass = spec['material_class']
    material.SurfaceForegroundPatternId = DB.ElementId.InvalidElementId
    material.SurfaceBackgroundPatternId = DB.ElementId.InvalidElementId
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    removed = []
    for index in range(asset.Size):          # same idiom as build_cassia.py
        prop = asset[index]
        try:
            if prop.NumberOfConnectedProperties:
                prop.RemoveConnectedAsset()
                removed.append(prop.Name)
        except Exception:
            pass
    set_color(asset, 'generic_diffuse', spec['color'])
    scalar(asset, 'generic_glossiness', spec['glossiness'])
    scalar(asset, 'generic_reflectivity_at_0deg', spec['refl0'])
    scalar(asset, 'generic_reflectivity_at_90deg', spec['refl90'])
    scalar(asset, 'generic_transparency', 0.0)
    metal = asset.FindByName('generic_is_metal')
    if metal is not None:
        metal.Value = spec['is_metal']
    scope.Commit(True)
    scope.Dispose()
    record['material'] = {'name': spec['name'], 'removed_connected_maps': removed,
                          'is_metal_set': metal is not None}
    return material


def read_material(doc, name):
    material = next((m for m in DB.FilteredElementCollector(doc).OfClass(DB.Material) if m.Name == name), None)
    if material is None:
        return None
    out = {'name': material.Name, 'id': str(material.Id.Value), 'material_class': material.MaterialClass,
           'shading_color': [int(material.Color.Red), int(material.Color.Green), int(material.Color.Blue)],
           'surface_pattern_none': material.SurfaceForegroundPatternId == DB.ElementId.InvalidElementId}
    try:
        asset = doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
        diffuse = asset.FindByName('generic_diffuse').GetValueAsColor()
        out['diffuse'] = [int(diffuse.Red), int(diffuse.Green), int(diffuse.Blue)]
        out['glossiness'] = float(asset.FindByName('generic_glossiness').Value)
        metal = asset.FindByName('generic_is_metal')
        out['is_metal'] = bool(metal.Value) if metal is not None else None
    except Exception:
        out['appearance_error'] = traceback.format_exc()
    return out


# ------------------------------------------------------ planes and dimensions
def new_plane(doc, view, name, bubble, free, cut, want_normal, record):
    plane = doc.FamilyCreate.NewReferencePlane(xyz(*bubble), xyz(*free), cut, view)
    plane.Name = name
    flipped = False
    if want_normal is not None and plane.Normal.DotProduct(want_normal) < 0:
        plane.Flip()
        flipped = True
    if want_normal is not None and plane.Normal.DotProduct(want_normal) < 0.999:
        raise RuntimeError('Reference plane %s normal %r, wanted %r' % (name, vec(plane.Normal), vec(want_normal)))
    record[name] = {'id': str(plane.Id.Value), 'normal': vec(plane.Normal), 'flipped': flipped}
    return plane


def dimension(doc, view, p0, p1, refs, label=None, equal=False):
    array = DB.ReferenceArray()
    for ref in refs:
        array.Append(ref)
    dim = doc.FamilyCreate.NewDimension(view, DB.Line.CreateBound(xyz(*p0), xyz(*p1)), array)
    if equal:
        dim.AreSegmentsEqual = True
    if label is not None:
        dim.FamilyLabel = label
    return dim


def reference_planes(doc, plan, front, v, record):
    """Six task-sheet planes plus four clamp-edge planes, all driven by labelled dimensions."""
    planes = {}
    joint = find_plane(doc, 'Center (Left/Right)')
    centre_y = find_plane(doc, 'Center (Front/Back)')
    if joint is None or centre_y is None:
        raise RuntimeError('Template centre planes not found')
    joint.Name = 'Joint CL'
    planes['Joint CL'] = joint
    planes['Center (Front/Back)'] = centre_y
    record['Joint CL'] = {'id': str(joint.Id.Value), 'normal': vec(joint.Normal),
                          'note': "template 'Center (Left/Right)' renamed; defines origin"}
    g, p, w, h = v['Glass_Thickness'], v['Plate_Thickness'], v['Clamp_Width'], v['Clamp_Height']
    Y, Z = DB.XYZ.BasisY, DB.XYZ.BasisZ
    # vertical planes, normal Y, drawn in plan (cut vector Z); normals point away from the glass
    for name, y, sign in (('Glass Face Front', g / 2.0, 1), ('Glass Face Back', -g / 2.0, -1),
                          ('Plate Outer Front', g / 2.0 + p, 1), ('Plate Outer Back', -g / 2.0 - p, -1)):
        planes[name] = new_plane(doc, plan, name, (-4, y, 0), (4, y, 0), Z, Y.Multiply(sign), record)
    # vertical planes, normal X, drawn in plan
    for name, x in (('Clamp Left', -w / 2.0), ('Clamp Right', w / 2.0)):
        planes[name] = new_plane(doc, plan, name, (x, -3, 0), (x, 3, 0), Z, None, record)
    # horizontal planes, normal Z, drawn in the Front elevation (cut vector Y)
    for name, z in (('Glass Mid', 0.0), ('Clamp Top', h / 2.0), ('Clamp Bottom', -h / 2.0)):
        planes[name] = new_plane(doc, front, name, (-4, 0, z), (4, 0, z), Y, None, record)

    # Glass Mid sits on the template origin level; lock it there, pin as fallback.
    level = next(iter(DB.FilteredElementCollector(doc).OfClass(DB.Level)), None)
    try:
        lock = doc.FamilyCreate.NewAlignment(front, level.GetPlaneReference(), planes['Glass Mid'].GetReference())
        lock.IsLocked = True
        record['Glass Mid']['locked_to'] = element_name(level)
    except Exception:
        planes['Glass Mid'].Pinned = True
        record['Glass Mid']['locked_to'] = 'pinned (alignment failed): ' + traceback.format_exc().splitlines()[-1]

    fm = doc.FamilyManager
    ref = dict((k, pl.GetReference()) for k, pl in planes.items())
    dims = {}
    # plan: glass faces symmetric about Y=0, overall = Glass_Thickness; plates = Plate_Thickness
    dims['glass_eq'] = dimension(doc, plan, (3.5, -2, 0), (3.5, 2, 0),
                                 [ref['Glass Face Back'], ref['Center (Front/Back)'], ref['Glass Face Front']],
                                 equal=True)
    dims['glass'] = dimension(doc, plan, (4.2, -2, 0), (4.2, 2, 0),
                              [ref['Glass Face Back'], ref['Glass Face Front']], fm.get_Parameter('Glass_Thickness'))
    dims['plate_front'] = dimension(doc, plan, (-3.5, 0, 0), (-3.5, 2, 0),
                                    [ref['Glass Face Front'], ref['Plate Outer Front']],
                                    fm.get_Parameter('Plate_Thickness'))
    dims['plate_back'] = dimension(doc, plan, (-3.5, -2, 0), (-3.5, 0, 0),
                                   [ref['Plate Outer Back'], ref['Glass Face Back']],
                                   fm.get_Parameter('Plate_Thickness'))
    # front elevation: clamp sides about Joint CL = Clamp_Width; top/bottom about Glass Mid = Clamp_Height
    dims['width_eq'] = dimension(doc, front, (-3, 0, 1.6), (3, 0, 1.6),
                                 [ref['Clamp Left'], ref['Joint CL'], ref['Clamp Right']], equal=True)
    dims['width'] = dimension(doc, front, (-3, 0, 2.2), (3, 0, 2.2),
                              [ref['Clamp Left'], ref['Clamp Right']], fm.get_Parameter('Clamp_Width'))
    dims['height_eq'] = dimension(doc, front, (3.2, 0, -1.5), (3.2, 0, 1.5),
                                  [ref['Clamp Bottom'], ref['Glass Mid'], ref['Clamp Top']], equal=True)
    dims['height'] = dimension(doc, front, (3.8, 0, -1.5), (3.8, 0, 1.5),
                               [ref['Clamp Bottom'], ref['Clamp Top']], fm.get_Parameter('Clamp_Height'))
    record['dimensions_created'] = sorted(dims.keys())
    return planes


# ----------------------------------------------------------------- geometry
def rectangle(y, w, h):
    corners = [xyz(-w / 2.0, y, -h / 2.0), xyz(w / 2.0, y, -h / 2.0),
               xyz(w / 2.0, y, h / 2.0), xyz(-w / 2.0, y, h / 2.0)]
    loop = DB.CurveArray()
    for i in range(4):
        loop.Append(DB.Line.CreateBound(corners[i], corners[(i + 1) % 4]))
    profile = DB.CurveArrArray()
    profile.Append(loop)
    return profile


def circle(centre, radius, normal, halves):
    """Full circle, or two semicircles (the P01 native precedent) when halves is True."""
    x_axis = DB.XYZ.BasisX
    y_axis = normal.CrossProduct(x_axis).Normalize()
    loop = DB.CurveArray()
    spans = ((0.0, math.pi), (math.pi, 2 * math.pi)) if halves else ((0.0, 2 * math.pi),)
    for start, end in spans:
        loop.Append(DB.Arc.Create(centre, ft(radius), start, end, x_axis, y_axis))
    profile = DB.CurveArrArray()
    profile.Append(loop)
    return profile


def bind_common(doc, element, subcategory, material_param, coarse):
    fm = doc.FamilyManager
    element.Subcategory = subcategory
    fm.AssociateElementParameterToFamilyParameter(
        element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), material_param)
    vis = DB.FamilyElementVisibility(DB.FamilyElementVisibilityType.Model)
    vis.IsShownInCoarse = coarse
    vis.IsShownInMedium = True
    vis.IsShownInFine = True
    vis.IsShownInFrontBack = True
    vis.IsShownInLeftRight = True
    vis.IsShownInPlanRCPCut = True
    vis.IsShownInTopBottom = True
    element.SetVisibility(vis)


def planar_faces(element):
    faces = []
    for solid in element_solids(element, references=True):
        for face in solid.Faces:
            if isinstance(face, DB.PlanarFace) and face.Reference is not None:
                faces.append(face)
    return faces


def lock_plate_sides(doc, extrusion, views, planes, record):
    """Align and lock the four side faces of a plate to the clamp-edge planes.
    views: elevation that sees this plate first, the opposite elevation as fallback."""
    locks = []
    for face in planar_faces(extrusion):
        n, o = face.FaceNormal, face.Origin
        if abs(n.X) > 0.99:
            target = 'Clamp Right' if n.X > 0 else 'Clamp Left'
        elif abs(n.Z) > 0.99:
            target = 'Clamp Top' if n.Z > 0 else 'Clamp Bottom'
        else:
            continue
        row = {'face_normal': vec(n), 'face_origin_in': inches(o), 'plane': target}
        row['locked'] = False
        for view in views:
            try:
                align = doc.FamilyCreate.NewAlignment(view, planes[target].GetReference(), face.Reference)
                align.IsLocked = True
                row['locked'] = bool(align.IsLocked)
                row['view'] = view.Name
                break
            except Exception:
                row.setdefault('errors', []).append(view.Name + ': ' + traceback.format_exc().splitlines()[-1])
        locks.append(row)
    record['side_locks'] = locks
    return locks


def make_plate(doc, key, face_plane, v, views, planes, params, subcats, record):
    rec = record.setdefault(key, {})
    sketch = DB.SketchPlane.Create(doc, face_plane.Id)
    rec['sketch_plane'] = face_plane.Name
    rec['sketch_normal'] = vec(sketch.GetPlane().Normal)
    y = face_plane.GetPlane().Origin.Y * 12.0
    extrusion = doc.FamilyCreate.NewExtrusion(True, rectangle(y, v['Clamp_Width'], v['Clamp_Height']),
                                              sketch, ft(v['Plate_Thickness']))
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        extrusion.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), params['Plate_Thickness'])
    bind_common(doc, extrusion, subcats['Clamp Plate'], params['Clamp_Material'], True)
    doc.Regenerate()
    lock_plate_sides(doc, extrusion, views, planes, rec)
    rec['id'] = str(extrusion.Id.Value)
    return extrusion


def make_cap(doc, key, sign, outer_plane, v, params, subcats, record):
    rec = record.setdefault(key, {})
    sketch = DB.SketchPlane.Create(doc, outer_plane.Id)
    normal = sketch.GetPlane().Normal
    rec['sketch_plane'] = outer_plane.Name
    rec['sketch_normal'] = vec(normal)
    y = outer_plane.GetPlane().Origin.Y * 12.0
    centre = xyz(sign * v['Cap_Offset'], y, 0.0)
    extrusion = None
    for label, halves in (('full circle', False), ('two semicircles', True)):
        try:
            profile = circle(centre, v['Cap_Diameter'] / 2.0, normal, halves)
            extrusion = doc.FamilyCreate.NewExtrusion(True, profile, sketch, ft(v['Cap_Height']))
            rec['profile'] = label
            break
        except Exception:
            rec.setdefault('profile_errors', []).append(label + ': ' + traceback.format_exc().splitlines()[-1])
    if extrusion is None:
        raise RuntimeError('Screw head extrusion failed for ' + key)
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(
        extrusion.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM), params['Cap_Height'])
    bind_common(doc, extrusion, subcats['Clamp Cap'], params['Clamp_Material'], False)
    rec['id'] = str(extrusion.Id.Value)
    return extrusion


def constrain_cap(doc, key, extrusion, view, planes, v, sign, record):
    """Inside the cap's sketch: centre to Joint CL = Cap_Offset, to Clamp Bottom = Cap_Elevation,
    diameter = Cap_Diameter. SketchEditScope must run outside any open transaction."""
    rec = record.setdefault(key, {})
    fm = doc.FamilyManager
    scope = DB.SketchEditScope(doc, 'Constrain ' + key)
    scope.Start(extrusion.SketchId)
    tx = DB.Transaction(doc, 'Dimension ' + key)
    tx.Start()
    made = []
    try:
        sketch = doc.GetElement(extrusion.SketchId)
        arcs = []
        for element_id in sketch.GetAllElements():
            element = doc.GetElement(element_id)
            if isinstance(element, DB.CurveElement) and isinstance(element.GeometryCurve, DB.Arc):
                arcs.append(element)
        rec['sketch_arcs'] = len(arcs)
        cx = sign * v['Cap_Offset']
        yplane = planes['Plate Outer Back'].GetPlane().Origin.Y * 12.0
        for index, arc in enumerate(arcs):
            try:
                arc.CenterMarkVisible = True
            except Exception:
                pass
            centre_ref = arc.CenterPointReference
            if centre_ref is None:
                raise RuntimeError('CenterPointReference is None for %s arc %d' % (key, index))
            dimension(doc, view, (0, yplane, -1.4 - 0.2 * index), (cx, yplane, -1.4 - 0.2 * index),
                      [planes['Joint CL'].GetReference(), centre_ref], fm.get_Parameter('Cap_Offset'))
            made.append('Cap_Offset')
            dimension(doc, view, (cx + 0.6 + 0.2 * index, yplane, -v['Clamp_Height'] / 2.0),
                      (cx + 0.6 + 0.2 * index, yplane, 0.0),
                      [planes['Clamp Bottom'].GetReference(), centre_ref], fm.get_Parameter('Cap_Elevation'))
            made.append('Cap_Elevation')
            curve_ref = arc.GeometryCurve.Reference
            if curve_ref is None:
                curve_ref = DB.Reference(arc)
            diameter = doc.FamilyCreate.NewDiameterDimension(view, curve_ref, xyz(cx, yplane, v['Cap_Diameter']))
            diameter.FamilyLabel = fm.get_Parameter('Cap_Diameter')
            made.append('Cap_Diameter')
            if len(arcs) == 1:
                break
        tx.Commit()
        capture = FailureCapture('Sketch ' + key)
        scope.Commit(capture)
        rec['sketch_constraints'] = made
        rec['sketch_commit_messages'] = capture.messages
        rec['sketch_constrained'] = True
    except Exception:
        rec['sketch_constrained'] = False
        rec['sketch_error'] = traceback.format_exc()
        if tx.HasStarted() and not tx.HasEnded():
            tx.RollBack()
        try:
            scope.Cancel()
        except Exception:
            pass


# --------------------------------------------------------------------- views
def view_type_3d(doc):
    return next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
                if v.ViewFamily == DB.ViewFamily.ThreeDimensional)


def orient(view, eye, forward, up_hint):
    forward = forward.Normalize()
    right = forward.CrossProduct(up_hint).Normalize()
    up = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, up, forward))


def iso_view(doc, name, toward_eye, target, style, detail, box=None, hide_others=True):
    view = DB.View3D.CreateIsometric(doc, view_type_3d(doc).Id)
    view.Name = name
    d = DB.XYZ(toward_eye[0], toward_eye[1], toward_eye[2]).Normalize()
    eye = target.Add(d.Multiply(3.0))
    orient(view, eye, target.Subtract(eye), DB.XYZ.BasisZ)
    view.DetailLevel = detail
    view.DisplayStyle = style
    if hide_others and doc.IsFamilyDocument:
        for category in doc.Settings.Categories:
            if category.Id != doc.OwnerFamily.FamilyCategory.Id and view.CanCategoryBeHidden(category.Id):
                view.SetCategoryHidden(category.Id, True)
    if box is not None:
        view.SetSectionBox(box)
        view.IsSectionBoxActive = True
    return view


def family_views(doc):
    target = DB.XYZ.Zero
    fine, coarse = DB.ViewDetailLevel.Fine, DB.ViewDetailLevel.Coarse
    shade, real = DB.DisplayStyle.Shading, DB.DisplayStyle.Realistic
    front_dir, back_dir = (-0.55, 1.0, 0.45), (0.55, -1.0, 0.45)
    return [
        iso_view(doc, 'Clamp Front Oblique', front_dir, target, shade, fine),
        iso_view(doc, 'Clamp Back Oblique', back_dir, target, shade, fine),
        iso_view(doc, 'Clamp Back Oblique Realistic', back_dir, target, real, fine),
        iso_view(doc, 'Clamp Back Oblique Coarse', back_dir, target, shade, coarse),
        iso_view(doc, 'Clamp Top', (0.0, -0.02, 1.0), target, shade, fine),
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
    options.PixelSize = 1400
    doc.ExportImage(options)


def list_images(prefix):
    folder = out_path('evidence')
    return sorted([{'file': n, 'bytes': os.path.getsize(os.path.join(folder, n))}
                   for n in os.listdir(folder)
                   if n.startswith(prefix + ' - ') and n.lower().endswith('.png')],
                  key=lambda item: item['file'])


# ---------------------------------------------------------------- purge
def purge_unused(doc, record):
    """Manage > Purge Unused equivalent (Document.GetUnusedElements, Revit 2024+), up to 3 passes."""
    passes = []
    if not hasattr(doc, 'GetUnusedElements'):
        record['purge'] = {'available': False}
        return
    for _ in range(3):
        ids = list(doc.GetUnusedElements(HashSet[DB.ElementId]()))
        if not ids:
            break
        deleted, failed = 0, []
        tx, capture = captured_transaction(doc, 'Purge unused')
        tx.Start()
        for element_id in ids:
            try:
                doc.Delete(element_id)
                deleted += 1
            except Exception:
                failed.append(str(element_id.Value))
        status = tx.Commit()
        passes.append({'candidates': len(ids), 'deleted': deleted, 'failed': failed,
                       'status': str(status), 'messages': capture.messages})
        if deleted == 0:
            break
    remaining = len(list(doc.GetUnusedElements(HashSet[DB.ElementId]())))
    record['purge'] = {'available': True, 'passes': passes, 'remaining_unused': remaining}


# --------------------------------------------------------------------- build
def build(app):
    global TX
    doc = app.NewFamilyDocument(REPORT['template']['path'])
    DOCS.append(doc)
    rec = REPORT.setdefault('build', {})
    v = S.resolve()
    plan = find_view(doc, DB.ViewType.FloorPlan, 'Ref. Level')
    front = find_view(doc, DB.ViewType.Elevation, 'Front')
    back = find_view(doc, DB.ViewType.Elevation, 'Back')

    TX, _ = captured_transaction(doc, 'Build SHB_Glass Clamp 180 Square')
    TX.Start()
    family = doc.OwnerFamily
    family.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_GenericModel)
    settings = {}
    for label, bip, value in (('always_vertical', DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL, 1),
                              ('work_plane_based', DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED, 0)):
        param = family.get_Parameter(bip)
        if param is not None and not param.IsReadOnly:
            param.Set(value)
        settings[label] = None if param is None else param.AsInteger()
    rec['family_settings_set'] = settings

    fm = doc.FamilyManager
    material = make_material(doc, app, rec)
    params = {}
    for name, kind, default, formula, source, note in S.PARAMETERS:
        if kind == 'length':
            spec = DB.SpecTypeId.Length
            group = DB.GroupTypeId.Geometry
        elif kind == 'material':
            spec, group = DB.SpecTypeId.Reference.Material, DB.GroupTypeId.Materials
        else:
            spec, group = DB.SpecTypeId.String.Text, DB.GroupTypeId.IdentityData
        params[name] = fm.AddParameter(name, group, spec, False)
    rec['template_types'] = [t.Name for t in fm.Types]
    for index, (type_name, glass) in enumerate(S.TYPES):
        if index == 0 and fm.CurrentType is not None and fm.Types.Size == 1:
            fm.RenameCurrentType(type_name)
        else:
            fm.CurrentType = fm.NewType(type_name)
        for name, kind, default, formula, source, note in S.PARAMETERS:
            if kind == 'length' and not formula:
                fm.Set(params[name], ft(glass if name == 'Glass_Thickness' else default))
        fm.Set(params['Clamp_Material'], material.Id)
        fm.Set(params['Model Accuracy Notes'], S.ACCURACY_NOTE)
        for bip_name, value in S.IDENTITY.items():
            param = fm.get_Parameter(getattr(DB.BuiltInParameter, bip_name))
            if param is not None:
                fm.Set(param, value)
    for name, formula in S.FORMULAS.items():
        fm.SetFormula(params[name], formula)
    fm.CurrentType = next(t for t in fm.Types if t.Name == S.DEFAULT_TYPE)

    subcats = {}
    for name in S.SUBCATEGORIES:
        subcats[name] = doc.Settings.Categories.NewSubcategory(family.FamilyCategory, name)

    plane_rec = rec.setdefault('planes', {})
    planes = reference_planes(doc, plan, front, v, plane_rec)
    doc.Regenerate()

    part_rec = rec.setdefault('parts', {})
    elements = {
        'plate_front': make_plate(doc, 'plate_front', planes['Glass Face Front'], v, [back, front], planes,
                                  params, subcats, part_rec),
        'plate_back': make_plate(doc, 'plate_back', planes['Glass Face Back'], v, [front, back], planes,
                                 params, subcats, part_rec),
        'cap_left': make_cap(doc, 'cap_left', -1.0, planes['Plate Outer Back'], v, params, subcats, part_rec),
        'cap_right': make_cap(doc, 'cap_right', 1.0, planes['Plate Outer Back'], v, params, subcats, part_rec),
    }
    doc.Regenerate()
    status = TX.Commit()
    TX = None
    rec['main_commit_status'] = str(status)
    REPORT['parts'] = dict((k, str(e.Id.Value)) for k, e in elements.items())
    checkpoint('plates and screw heads created')

    # Revit's Front elevation looks toward +Y from the -Y (screw) side, so the heads face it.
    for key, sign in (('cap_left', -1.0), ('cap_right', 1.0)):
        constrain_cap(doc, key, elements[key], front, planes, v, sign, part_rec)
        checkpoint('constrained ' + key)

    TX, _ = captured_transaction(doc, 'Review views')
    TX.Start()
    views = family_views(doc)
    TX.Commit()
    TX = None
    purge_unused(doc, rec)
    checkpoint('built, saving')

    save = DB.SaveAsOptions()
    save.OverwriteExistingFile = True
    save.MaximumBackups = 1
    save.Compact = True
    save.PreviewViewId = views[1].Id
    rfa_path = out_path(S.RFA_NAME)
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
def measure_parts(doc, v):
    """Ray every part at the current values; returns (rows, all_pass)."""
    rows = []
    for ray in S.part_rays(v):
        element = doc.GetElement(DB.ElementId(int(REPORT['parts'][ray['part']])))
        try:
            rows.append(ray_row(ray, solid_segments(element_solids(element), ray['p0'], ray['p1'])))
        except Exception:
            rows.append({'key': ray['key'], 'pass': False, 'error': traceback.format_exc()})
    return rows, all(r['pass'] for r in rows)


def labelled_dimensions(doc):
    labels, equal, locked = {}, 0, 0
    for dim in DB.FilteredElementCollector(doc).OfClass(DB.Dimension):
        label = None
        try:
            label = dim.FamilyLabel.Definition.Name if dim.FamilyLabel is not None else None
        except Exception:
            label = None
        if label:
            labels[label] = labels.get(label, 0) + 1
        try:
            if dim.AreSegmentsEqual:
                equal += 1
        except Exception:
            pass
        try:
            if dim.IsLocked:
                locked += 1
        except Exception:
            pass
    return labels, equal, locked


def measure_family(app, rfa_path):
    doc = app.OpenDocumentFile(rfa_path)
    DOCS.append(doc)
    rec = REPORT.setdefault('family', {})
    fam = doc.OwnerFamily
    rec['reopened'] = doc.IsFamilyDocument
    rec['category'] = fam.FamilyCategory.Name
    rec['placement_type'] = str(fam.FamilyPlacementType)
    for label, bip in (('always_vertical', DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL),
                       ('work_plane_based', DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED),
                       ('shared', DB.BuiltInParameter.FAMILY_SHARED)):
        param = fam.get_Parameter(bip)
        rec[label] = None if param is None else param.AsInteger()
    rec['warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    rec['rfa_bytes'] = os.path.getsize(rfa_path)
    rec['rfa_mtime_utc'] = datetime.datetime.utcfromtimestamp(os.path.getmtime(rfa_path)).isoformat() + 'Z'
    if hasattr(doc, 'GetUnusedElements'):
        rec['unused_after_reopen'] = len(list(doc.GetUnusedElements(HashSet[DB.ElementId]())))

    fm = doc.FamilyManager
    rec['types'] = sorted(t.Name for t in fm.Types)
    rec['current_type'] = fm.CurrentType.Name if fm.CurrentType is not None else None
    values = {}
    for t in fm.Types:
        row = {}
        for name, kind, default, formula, source, note in S.PARAMETERS:
            param = fm.get_Parameter(name)
            if param is None:
                row[name] = 'MISSING'
            elif kind == 'length':
                raw = t.AsDouble(param)
                row[name] = None if raw is None else raw * 12.0
            elif kind == 'material':
                mid = t.AsElementId(param)
                row[name] = doc.GetElement(mid).Name if mid is not None and mid != DB.ElementId.InvalidElementId else None
            else:
                row[name] = t.AsString(param)
        for bip_name in S.IDENTITY:
            param = fm.get_Parameter(getattr(DB.BuiltInParameter, bip_name))
            row[bip_name] = t.AsString(param) if param is not None else 'MISSING'
        values[t.Name] = row
    rec['type_values'] = values
    params = {}
    for param in fm.Parameters:
        params[param.Definition.Name] = {'instance': param.IsInstance, 'formula': param.Formula,
                                         'shared': param.IsShared}
    rec['parameters'] = params

    rec['reference_planes'] = sorted(p.Name for p in DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane)
                                     if p.Name)
    labels, equal, locked = labelled_dimensions(doc)
    rec['dimension_labels'] = labels
    rec['equality_dimensions'] = equal
    rec['locked_alignments'] = locked

    parts = {}
    for key, subcat, coarse in S.PARTS:
        element = doc.GetElement(DB.ElementId(int(REPORT['parts'][key])))
        row = {'found': isinstance(element, DB.Extrusion)}
        if row['found']:
            row['subcategory'] = element.Subcategory.Name if element.Subcategory is not None else None
            assoc = fm.GetAssociatedFamilyParameter(element.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM))
            row['material_parameter'] = assoc.Definition.Name if assoc is not None else None
            end = fm.GetAssociatedFamilyParameter(element.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM))
            row['depth_parameter'] = end.Definition.Name if end is not None else None
            vis = element.GetVisibility()
            row['visibility'] = {'coarse': vis.IsShownInCoarse, 'medium': vis.IsShownInMedium,
                                 'fine': vis.IsShownInFine, 'front_back': vis.IsShownInFrontBack,
                                 'left_right': vis.IsShownInLeftRight, 'plan_rcp': vis.IsShownInPlanRCPCut,
                                 'top_bottom': vis.IsShownInTopBottom}
            fine = element_solids(element)
            row['solids'] = len(fine)
            row['faces'] = sum(s.Faces.Size for s in fine)
            material_ids = set()
            for solid in fine:
                for face in solid.Faces:
                    material_ids.add(face.MaterialElementId)
            names = []
            for mid in material_ids:
                m = doc.GetElement(mid)
                names.append(m.Name if m is not None else 'None')
            row['face_materials'] = sorted(names)
        parts[key] = row
    rec['parts'] = parts
    rec['extrusion_count'] = len(list(DB.FilteredElementCollector(doc).OfClass(DB.Extrusion)))
    rec['material'] = read_material(doc, S.MATERIAL['name'])
    rows, ok = measure_parts(doc, S.resolve())
    rec['default_rays'] = rows
    return doc


# ------------------------------------------------------------- project tests
def project_tests(app, family_doc):
    global TX
    rec = REPORT.setdefault('project', {})
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    family = family_doc.LoadFamily(project)
    symbols = dict((element_name(project.GetElement(i)), project.GetElement(i)) for i in family.GetFamilySymbolIds())
    rec['loaded_types'] = sorted(symbols.keys())
    rec['material_in_project'] = read_material(project, S.MATERIAL['name'])

    TX, capture = captured_transaction(project, 'Place clamp')
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)), None)
    if level is None:
        level = DB.Level.Create(project, 0)
    symbol = symbols[S.DEFAULT_TYPE]
    symbol.Activate()
    project.Regenerate()
    instance = project.Create.NewFamilyInstance(DB.XYZ(0, 0, 4.0), symbol, level, StructuralType.NonStructural)
    project.Regenerate()
    transform = instance.GetTransform()
    rec['placed_origin_in'] = inches(transform.Origin)
    rec['basis_z'] = vec(transform.BasisZ)

    def through(values, label):
        rows = []
        world = element_solids(instance, DB.ViewDetailLevel.Fine)
        for ray in S.project_rays(values):
            rows.append(ray_row(ray, solid_segments(world, ray['p0'], ray['p1'], transform)))
        rec[label] = rows
        return all(r['pass'] for r in rows)

    v = S.resolve()
    through(v, 'rays_default_type')
    box = instance.get_BoundingBox(None)
    rec['bbox_in'] = {'min': inches(transform.Inverse.OfPoint(box.Min)), 'max': inches(transform.Inverse.OfPoint(box.Max))}
    rec['expected_bbox_in'] = S.overall_box(v)
    rec['solids_by_detail'] = {}
    for label, level in (('coarse', DB.ViewDetailLevel.Coarse), ('medium', DB.ViewDetailLevel.Medium),
                         ('fine', DB.ViewDetailLevel.Fine)):
        rec['solids_by_detail'][label] = len(element_solids(instance, level))

    # material substitution through the type parameter
    type_param = symbol.LookupParameter('Clamp_Material')
    original = type_param.AsElementId()
    alternate = DB.Material.Create(project, 'QA substitute Clamp_Material')
    type_param.Set(alternate)
    project.Regenerate()
    carrying, total = 0, 0
    for solid in element_solids(instance):
        total += 1
        ids = [f.MaterialElementId for f in solid.Faces]
        if ids and all(i == alternate for i in ids):
            carrying += 1
    type_param.Set(original)
    project.Regenerate()
    rec['material_substitution'] = {'solids': total, 'carrying_substitute': carrying,
                                    'restored': symbol.LookupParameter('Clamp_Material').AsElementId() == original}

    # type switch to 3/8 glass
    other = symbols.get('3-8 Glass')
    if other is not None:
        other.Activate()
        instance.ChangeTypeId(other.Id)
        project.Regenerate()
        through(S.resolve({'Glass_Thickness': 0.375}), 'rays_3_8_type')
        instance.ChangeTypeId(symbol.Id)
        project.Regenerate()

    target = transform.Origin
    pad = 1.0 / 12.0
    section = DB.BoundingBoxXYZ()
    section.Min = DB.XYZ(box.Min.X - pad, box.Min.Y - pad, box.Min.Z - pad)
    section.Max = DB.XYZ(box.Max.X + pad, box.Max.Y + pad, box.Max.Z + pad)
    views = [iso_view(project, 'Placed Back Oblique', (0.55, -1.0, 0.45), target, DB.DisplayStyle.Realistic,
                      DB.ViewDetailLevel.Fine, section, hide_others=False)]
    status = TX.Commit()
    TX = None
    rec['commit_status'] = str(status)
    rec['commit_messages'] = capture.messages
    try:
        export_images(project, views, PROJECT_PREFIX)
        rec['export_error'] = None
    except Exception:
        rec['export_error'] = traceback.format_exc()
    rec['images'] = list_images(PROJECT_PREFIX)
    rec['warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]


# ------------------------------------------------------------------ flexing
def flex_family(doc):
    rec = REPORT.setdefault('flex', {})
    fm = doc.FamilyManager
    steps = []
    for name, values in S.FLEX:
        param = fm.get_Parameter(name)
        for value in values:
            tx, capture = captured_transaction(doc, 'Flex %s %s' % (name, value), collect=False)
            tx.Start()
            fm.Set(param, ft(value))
            status = tx.Commit()
            current = S.resolve({name: value})
            rows, ok = measure_parts(doc, current)
            steps.append({'parameter': name, 'value_in': value, 'commit_status': str(status),
                          'failures': capture.messages, 'rays': rows, 'pass':
                          ok and str(status) == 'Committed'
                          and not [m for m in capture.messages if m['severity'] != 'Warning']})
        # restore this parameter before the next one
        tx, capture = captured_transaction(doc, 'Restore ' + name, collect=False)
        tx.Start()
        fm.Set(param, ft(S.LENGTH_DEFAULTS[name]))
        rec.setdefault('restores', []).append({'parameter': name, 'status': str(tx.Commit()),
                                               'failures': capture.messages})
    rec['steps'] = steps
    rows, ok = measure_parts(doc, S.resolve())
    rec['after_restore_rays'] = rows
    rec['after_restore_pass'] = ok
    rec['warnings_after_flex'] = [w.GetDescriptionText() for w in doc.GetWarnings()]


# -------------------------------------------------------------------- gates
def gates():
    REPORT['captured_failures'] = list(CAPTURED)
    fam = REPORT.get('family', {})
    proj = REPORT.get('project', {})
    flex = REPORT.get('flex', {})
    build_rec = REPORT.get('build', {})
    v = S.resolve()

    def rays_ok(rows):
        return bool(rows) and all(r.get('pass') is True for r in rows)
    parts = fam.get('parts', {})
    types = fam.get('type_values', {})
    params = fam.get('parameters', {})
    labels = fam.get('dimension_labels', {})
    caps_constrained = all(build_rec.get('parts', {}).get(k, {}).get('sketch_constrained') for k in ('cap_left', 'cap_right'))
    result = {
        'revit_2025_host': str(REPORT.get('revit_version', '')).startswith('2025'),
        'spec_self_check': not REPORT.get('spec_problems'),
        'fresh_rfa_reopen_category': bool(fam.get('reopened')) and fam.get('category') == 'Generic Models',
        'always_vertical_on_work_plane_off': fam.get('always_vertical') == 1 and fam.get('work_plane_based') == 0,
        'types_present': sorted(n for n, _ in S.TYPES) == fam.get('types')
            and fam.get('current_type') == S.DEFAULT_TYPE,
        'type_parameters': all(params.get(p[0], {}).get('instance') is False for p in S.PARAMETERS)
            and all(params.get(n, {}).get('formula') == f for n, f in S.FORMULAS.items())
            and all(abs((types.get(t, {}).get('Glass_Thickness') or -1) - g) < 1e-6 for t, g in S.TYPES)
            and all(types.get(t, {}).get('Clamp_Material') == S.MATERIAL['name'] for t, _ in S.TYPES)
            and all(types.get(t, {}).get(b) == val for t, _ in S.TYPES for b, val in S.IDENTITY.items()),
        'reference_planes_named': all(n in fam.get('reference_planes', []) for n in S.SPEC_PLANES + S.EXTRA_PLANES),
        'labelled_dimensions': all(labels.get(k, 0) >= c for k, c in S.LABELLED_DIMENSIONS.items())
            and fam.get('equality_dimensions', 0) >= S.EQ_DIMENSIONS,
        'plate_sides_locked': sum(1 for k in ('plate_front', 'plate_back')
                                  for r in build_rec.get('parts', {}).get(k, {}).get('side_locks', [])
                                  if r.get('locked')) >= S.MIN_LOCKED_ALIGNMENTS,
        'screw_heads_sketch_constrained': caps_constrained,
        'parts_separate_bound': len(parts) == len(S.PARTS) and all(
            parts[k].get('found') and parts[k].get('subcategory') == sub
            and parts[k].get('material_parameter') == 'Clamp_Material' and parts[k].get('solids') == 1
            and parts[k].get('face_materials') == [S.MATERIAL['name']]
            and parts[k].get('visibility', {}).get('coarse') == coarse
            and all(parts[k].get('visibility', {}).get(x) for x in
                    ('medium', 'fine', 'front_back', 'left_right', 'plan_rcp', 'top_bottom'))
            for k, sub, coarse in S.PARTS),
        'default_geometry_measured': rays_ok(fam.get('default_rays')),
        'flex_all_steps': bool(flex.get('steps')) and all(s.get('pass') for s in flex.get('steps', []))
            and len(flex.get('steps', [])) == sum(len(x) for _, x in S.FLEX),
        'flex_default_restored': flex.get('after_restore_pass') is True and not flex.get('warnings_after_flex'),
        'material_defined': bool(fam.get('material')) and fam['material'].get('shading_color') == list(S.MATERIAL['color'])
            and fam['material'].get('surface_pattern_none') is True,
        'project_load_place': sorted(n for n, _ in S.TYPES) == proj.get('loaded_types')
            and rays_ok(proj.get('rays_default_type')) and rays_ok(proj.get('rays_3_8_type'))
            and abs(proj.get('basis_z', [0, 0, 0])[2] - 1.0) < 1e-9,
        'project_detail_levels': proj.get('solids_by_detail') == {'coarse': 2, 'medium': 4, 'fine': 4},
        'project_material_substitution': proj.get('material_substitution', {}).get('carrying_substitute') == 4
            and proj.get('material_substitution', {}).get('solids') == 4
            and proj.get('material_substitution', {}).get('restored') is True,
        'zero_warnings': 'warnings' in fam and 'warnings' in proj and not fam['warnings'] and not proj['warnings']
            and not REPORT.get('captured_failures'),
        'purged_compact_under_500kb': build_rec.get('purge', {}).get('available') is True
            and (fam.get('rfa_bytes') or S.MAX_RFA_BYTES) < S.MAX_RFA_BYTES,
        'visual_exports_present': len([i for i in REPORT.get('family_images', []) if i['bytes'] > 0])
            >= S.MIN_FAMILY_IMAGES and len([i for i in proj.get('images', []) if i['bytes'] > 0]) >= 1,
    }
    REPORT['gates'] = result
    REPORT['failed_gates'] = sorted(k for k, ok in result.items() if not ok)
    REPORT['technical_pass'] = all(result.values())
    return result


# --------------------------------------------------------------------- main
try:
    app = __revit__.Application  # noqa: F821 (pyRevit global)
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    REPORT['template'] = find_template(app)
    REPORT['template']['exists'] = bool(REPORT['template'].get('path'))
    REPORT['spec_problems'] = S.check_spec()
    checkpoint('preflight')
    if not str(app.VersionNumber).startswith('2025'):
        raise RuntimeError('Revit 2025 required; host reports ' + str(app.VersionNumber))
    if not REPORT['template']['exists']:
        raise RuntimeError('%s not found; searched %r' % (TEMPLATE_NAME, REPORT['template'].get('roots_searched')))
    if REPORT['spec_problems']:
        raise RuntimeError('Spec self-check failed: ' + '; '.join(REPORT['spec_problems']))

    checkpoint('building')
    rfa = build(app)
    checkpoint('reopening and measuring')
    family_doc = measure_family(app, rfa)
    checkpoint('project tests')
    project_tests(app, family_doc)
    checkpoint('flexing')
    flex_family(family_doc)
    gates()
    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    checkpoint('complete' if REPORT['technical_pass'] else 'gates-failed')
    if not REPORT['technical_pass']:
        raise RuntimeError('Gate failures: ' + ', '.join(REPORT['failed_gates']))
except Exception:
    REPORT['error'] = traceback.format_exc()
    REPORT['technical_pass'] = False
    REPORT['captured_failures'] = list(CAPTURED)
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
            document.Close(False)     # the flexed family is never saved; the RFA on disk is the built one
        except Exception:
            pass
