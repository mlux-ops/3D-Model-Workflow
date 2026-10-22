# -*- coding: utf-8 -*-
"""Miele KM 3054-1 gas cooktop - Revit 2025 face-based family builder.

Runs INSIDE Revit 2025 (IronPython 2.7, pyRevit). Ordinary CPython cannot run it.
    Route A: run_km3054.ps1  (pyrevit run "<absolute path to this file>" --revit=2025)
    Route B: pyRevit button  pyrevit/KM3054.extension/.../BuildKM3054.pushbutton

What it does (only ever creates, saves and closes its own new documents):
  1. new family from Generic Model face based.rft, category Specialty Equipment,
     FAMILY_ALWAYS_VERTICAL = 0; local +Z = host face normal (up from the countertop)
  2. geometry from km3054_geometry.py: one FreeFormElement per group, grates unioned
     per cast piece, one subcategory and one type material parameter per finish
  3. save, close, reopen; Solid.IntersectWithCurve rays against published values
  4. load into a fresh project, place on the TOP face of a countertop-height floor,
     re-measure hosted, substitute every material parameter and count faces
  5. export >= 5 family views (template host hidden, crop from fixture bounds) and a
     hosted view; write validation.json at every stage; raise after writing a failure
`visual_verdict` is hard-coded PENDING REVIEWER. No script awards a visual pass.
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

RUN_NAME = 'miele_km3054_1'
ENV_ROOT = 'KM3054_REPO_ROOT'
TEMPLATE = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
RFA_NAME = 'Miele_KM3054-1_Gas_Cooktop_R2025.rfa'
TYPE_NAME = 'KM 3054-1 - 37 1/8 in - Black Ceramic Glass'
FAMILY_PREFIX = 'KM3054'
HOSTED_PREFIX = 'KM3054_Hosted'
COUNTER_FT = 3.0          # disposable host: floor top face at 36 in (countertop height)


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return None


def repo_root():
    """Env var from the runner, then walk up from this file. Never a hard-coded user path."""
    candidates = []
    env = os.environ.get(ENV_ROOT)
    if env:
        candidates.append((ENV_ROOT, os.path.normpath(env)))
    here = _script_dir()
    if here:
        probe = here
        for _ in range(6):
            candidates.append(('__file__ walk-up', probe))
            parent = os.path.dirname(probe)
            if parent == probe:
                break
            probe = parent
    for source, cand in candidates:
        if os.path.isfile(os.path.join(cand, 'AGENTS.md')) and \
                os.path.isfile(os.path.join(cand, 'output', RUN_NAME, 'source', 'km3054_geometry.py')):
            return cand, source
    raise RuntimeError('No checkout with AGENTS.md and output/%s/source/km3054_geometry.py among: %s'
                       % (RUN_NAME, ' | '.join(c for _, c in candidates)))


ROOT, ROOT_SOURCE = repo_root()
RUN_DIR = os.path.join(ROOT, 'output', RUN_NAME)
_RUN_NORM = os.path.normpath(RUN_DIR)
sys.path.insert(0, os.path.join(RUN_DIR, 'source'))
import km3054_geometry as G  # noqa: E402

# Appearance values: colours sampled from 20000084693 (top view). Metals use a percentile
# below the pixel median so the renderer's specular lift is not double-counted.
MATERIALS = {
    'top': {'rgb': (0, 18, 28), 'gloss': 0.90, 'r0': 0.08, 'r90': 0.60, 'cls': 'Glass',
            'note': 'black ceramic glass, median of glass pixels (0,18,28)'},
    'frame': {'rgb': (120, 122, 125), 'gloss': 0.50, 'r0': 0.20, 'r90': 0.60, 'cls': 'Metal',
              'note': 'stainless frame band, p40 (median 122,122,129)'},
    'grate': {'rgb': (73, 72, 77), 'gloss': 0.25, 'r0': 0.05, 'r90': 0.20, 'cls': 'Metal',
              'note': 'matte black enamelled cast iron, p25 of bar pixels (median 90,90,100)'},
    'burner': {'rgb': (78, 74, 75), 'gloss': 0.30, 'r0': 0.06, 'r90': 0.25, 'cls': 'Metal',
               'note': 'enamelled burner caps and bowls, p40 of the power-burner cap (median 79,76,77)'},
    'ring': {'rgb': (183, 180, 188), 'gloss': 0.40, 'r0': 0.15, 'r90': 0.50, 'cls': 'Metal',
             'note': 'aluminium burner heads, p25 of the wok head (median 231,230,233)'},
    'knob': {'rgb': (184, 185, 187), 'gloss': 0.50, 'r0': 0.20, 'r90': 0.60, 'cls': 'Metal',
             'note': 'stainless knobs, p40 (median 192,192,193)'},
    'housing': {'rgb': (150, 152, 155), 'gloss': 0.30, 'r0': 0.10, 'r90': 0.30, 'cls': 'Metal',
                'note': 'below-counter casing, not visible in any source photo (INFERRED)'},
}

REPORT = {
    'product': 'Miele KM 3054-1 gas cooktop (material number 11766750)',
    'script': 'build_km3054.py',
    'repo_root': ROOT,
    'repo_root_source': ROOT_SOURCE,
    'run_dir': RUN_DIR,
    'rfa_name': RFA_NAME,
    'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'visual_verdict': 'PENDING REVIEWER',
    'technical_pass': False,
    'units': 'measurements in mm in the family frame; host face at z = 0',
}
DOCS = []
TX = None


def out_path(*parts):
    """Every write goes through here; refuses any path outside RUN_DIR."""
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if target != _RUN_NORM and not target.startswith(_RUN_NORM + os.sep):
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
    print('[km3054] checkpoint: ' + stage)


def element_name(element):
    try:
        return DB.Element.Name.GetValue(element)
    except Exception:
        p = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
        return p.AsString() if p else None


def ft(mm):
    return mm / 304.8


def xyz_mm(p):
    return DB.XYZ(ft(p[0]), ft(p[1]), ft(p[2]))


def loop(origin, u, v, points):
    """CurveLoop of straight segments; points in mm in the (u, v) plane at origin."""
    def at(q):
        return origin.Add(u.Multiply(ft(q[0]))).Add(v.Multiply(ft(q[1])))
    cl = DB.CurveLoop()
    for i in range(len(points)):
        a, b = points[i], points[(i + 1) % len(points)]
        cl.Append(DB.Line.CreateBound(at(a), at(b)))
    return cl


def prism_solid(part):
    origin = DB.XYZ(0, 0, ft(part['z0']))
    loops = List[DB.CurveLoop]([loop(origin, DB.XYZ.BasisX, DB.XYZ.BasisY, pts) for pts in part['loops']])
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(loops, DB.XYZ.BasisZ, ft(part['z1'] - part['z0']))


def revolve_solid(part):
    cx, cy = part['centre']
    origin = DB.XYZ(ft(cx), ft(cy), 0)
    frame = DB.Frame(origin, DB.XYZ.BasisX, DB.XYZ.BasisY, DB.XYZ.BasisZ)
    profile = loop(origin, DB.XYZ.BasisX, DB.XYZ.BasisZ, part['profile'])   # (r, z), CCW
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame, List[DB.CurveLoop]([profile]), 0, 2 * math.pi)


def part_solid(part):
    return prism_solid(part) if part['kind'] == 'prism' else revolve_solid(part)


def solids(geometry):
    if geometry is None:
        return
    for item in geometry:
        if isinstance(item, DB.Solid) and item.Volume > 1e-12:
            yield item
        elif isinstance(item, DB.GeometryInstance):
            for s in solids(item.GetInstanceGeometry()):
                yield s


def fine_options():
    o = DB.Options()
    o.DetailLevel = DB.ViewDetailLevel.Fine
    return o


def ray(solid_list, a_mm, b_mm, transform=None):
    """Raw Solid.IntersectWithCurve segments, returned in family-frame mm."""
    pa, pb = xyz_mm(a_mm), xyz_mm(b_mm)
    inv = None
    if transform is not None:
        pa, pb = transform.OfPoint(pa), transform.OfPoint(pb)
        inv = transform.Inverse
    line = DB.Line.CreateBound(pa, pb)
    segs = []
    for s in solid_list:
        res = s.IntersectWithCurve(line, DB.SolidCurveIntersectionOptions())
        for i in range(res.SegmentCount):
            c = res.GetCurveSegment(i)
            p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
            if inv is not None:
                p0, p1 = inv.OfPoint(p0), inv.OfPoint(p1)
            segs.append([[p0.X * 304.8, p0.Y * 304.8, p0.Z * 304.8], [p1.X * 304.8, p1.Y * 304.8, p1.Z * 304.8]])
    return segs


def run_rays(solid_list, transform=None, keys=None):
    out = {}
    for r in G.measurement_rays():
        if keys is not None and r['key'] not in keys:
            continue
        segs = ray(solid_list, r['a'], r['b'], transform)
        value = G.measure(r, segs)
        ok = value is not None and abs(value - r['target']) <= r['tol'] + 1e-9
        out[r['key']] = {'measured_mm': value, 'target_mm': r['target'], 'tol_mm': r['tol'],
                         'provenance': r['prov'], 'segments_mm': segs, 'pass': ok,
                         'method': 'Solid.IntersectWithCurve %s along %r -> %r' % (r['measure'], r['a'], r['b'])}
    return out


def measured_bounds(elements):
    pts = []
    for e in elements:
        for s in solids(e.get_Geometry(fine_options())):
            for f in s.Faces:
                pts.extend(list(f.Triangulate(1.0).Vertices))
            for ed in s.Edges:
                c = ed.AsCurve()
                n = 1 if isinstance(c, DB.Line) else 64
                pts.extend(c.Evaluate(float(i) / n, True) for i in range(n + 1))
    return [min(p.X for p in pts) * 304.8, min(p.Y for p in pts) * 304.8, min(p.Z for p in pts) * 304.8,
            max(p.X for p in pts) * 304.8, max(p.Y for p in pts) * 304.8, max(p.Z for p in pts) * 304.8]


# ------------------------------------------------------------------ materials
def make_materials(doc, app, fm):
    base = None
    for a in app.GetAssets(DB.Visual.AssetType.Appearance):
        bs = a.FindByName('BaseSchema')
        if bs is not None and bs.Value == 'GenericSchema':
            base = a
            break
    if base is None:
        raise RuntimeError('No GenericSchema appearance asset available')
    REPORT['appearance_source_asset'] = base.Name
    params, record = {}, {}
    for key, label in sorted(G.MATERIAL_PARAMETERS.items()):
        spec = MATERIALS[key]
        name = 'KM3054 ' + label
        appearance = DB.AppearanceAssetElement.Create(doc, name, base)
        mat = doc.GetElement(DB.Material.Create(doc, name))
        mat.AppearanceAssetId = appearance.Id
        mat.Color = DB.Color(*spec['rgb'])
        mat.MaterialClass = spec['cls']
        scope = DB.Visual.AppearanceAssetEditScope(doc)
        asset = scope.Start(appearance.Id)

        def prop(k, required=True):
            p = asset.FindByName(k)
            if p is None and required:
                raise RuntimeError('Appearance property missing: ' + k)
            if p is not None and p.NumberOfConnectedProperties:
                p.RemoveConnectedAsset()
            return p
        prop('generic_diffuse').SetValueAsColor(DB.Color(*spec['rgb']))
        prop('generic_glossiness').Value = spec['gloss']
        prop('generic_transparency').Value = 0.0
        prop('generic_reflectivity_at_0deg').Value = spec['r0']
        prop('generic_reflectivity_at_90deg').Value = spec['r90']
        lum = prop('generic_self_illum_luminance', False)
        if lum is not None:
            lum.Value = 0.0
        scope.Commit(True)
        scope.Dispose()
        fp = fm.AddParameter(label, DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
        fm.Set(fp, mat.Id)
        params[key] = fp
        record[label] = {'material': name, 'rgb': list(spec['rgb']), 'glossiness': spec['gloss'],
                         'reflectivity_0': spec['r0'], 'reflectivity_90': spec['r90'],
                         'self_illum_luminance': 0.0, 'bitmaps': 'none', 'source': spec['note']}
    REPORT['materials'] = record
    return params


# ------------------------------------------------------------------ views
def make_view(doc, name, eye, target, up, bounds_mm, realistic, hide_ids):
    vt = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
              if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    view = DB.View3D.CreateIsometric(doc, vt.Id)
    view.Name = name
    view.DetailLevel = DB.ViewDetailLevel.Fine
    forward = target.Subtract(eye).Normalize()
    if abs(forward.DotProduct(up)) > 0.98:
        up = DB.XYZ.BasisY
    right = forward.CrossProduct(up).Normalize()
    true_up = right.CrossProduct(forward).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, true_up, forward))
    view.DisplayStyle = DB.DisplayStyle.Realistic if realistic else DB.DisplayStyle.Shading
    white = DB.Color(255, 255, 255)
    view.SetBackground(DB.ViewDisplayBackground.CreateGradient(white, white, white))
    if hide_ids:
        try:
            view.HideElements(List[DB.ElementId](hide_ids))
            REPORT.setdefault('template_host_hidden', {})[name] = 'HideElements'
        except Exception as exc:
            view.HideElementsTemporary(List[DB.ElementId](hide_ids))
            REPORT.setdefault('template_host_hidden', {})[name] = 'HideElementsTemporary (%s)' % exc
    for cat in doc.Settings.Categories:
        if cat.CategoryType == DB.CategoryType.Annotation and view.CanCategoryBeHidden(cat.Id):
            view.SetCategoryHidden(cat.Id, True)
    doc.Regenerate()
    b = bounds_mm
    m = max(10.0, max(b[3] - b[0], b[4] - b[1], b[5] - b[2]) * 0.04)
    box = DB.BoundingBoxXYZ()
    box.Min = xyz_mm((b[0] - m, b[1] - m, b[2] - m))
    box.Max = xyz_mm((b[3] + m, b[4] + m, b[5] + m))
    view.SetSectionBox(box)
    view.IsSectionBoxActive = True
    doc.Regenerate()
    crop = view.CropBox
    inv = crop.Transform.Inverse
    pts = [inv.OfPoint(xyz_mm((x, y, z))) for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])]
    mf = ft(m)
    crop.Min = DB.XYZ(min(p.X for p in pts) - mf, min(p.Y for p in pts) - mf, crop.Min.Z)
    crop.Max = DB.XYZ(max(p.X for p in pts) + mf, max(p.Y for p in pts) + mf, crop.Max.Z)
    view.CropBox = crop
    view.CropBoxActive = True
    view.CropBoxVisible = False
    return view


def export(doc, views, prefix):
    o = DB.ImageExportOptions()
    o.ExportRange = DB.ExportRange.SetOfViews
    o.SetViewsAndSheets(List[DB.ElementId]([v.Id for v in views]))
    o.FilePath = out_path('evidence', prefix)
    o.HLRandWFViewsFileType = DB.ImageFileType.PNG
    o.ShadowViewsFileType = DB.ImageFileType.PNG
    o.ImageResolution = DB.ImageResolution.DPI_150
    o.ZoomType = DB.ZoomFitType.FitToPage
    o.PixelSize = 1800
    doc.ExportImage(o)


def view_set(bounds_mm, transform=None):
    b = bounds_mm
    c = ((b[0] + b[3]) / 2.0, (b[1] + b[4]) / 2.0, (b[2] + b[5]) / 2.0)
    d = 2500.0
    eyes = [('Top', (c[0], c[1], c[2] + d), (0, 1, 0), False),
            ('Front', (c[0], c[1] - d, c[2]), (0, 0, 1), False),
            ('Side', (c[0] + d, c[1], c[2]), (0, 0, 1), False),
            ('Oblique', (c[0] + d * 0.45, c[1] - d * 0.75, c[2] + d * 0.6), (0, 0, 1), False),
            ('Underside', (c[0] + d * 0.35, c[1] - d * 0.6, c[2] - d * 0.7), (0, 0, 1), False),
            ('Oblique Realistic', (c[0] + d * 0.45, c[1] - d * 0.75, c[2] + d * 0.6), (0, 0, 1), True)]
    out = []
    for name, eye, up, real in eyes:
        e, t, u = xyz_mm(eye), xyz_mm(c), DB.XYZ(*up)
        if transform is not None:
            e, t, u = transform.OfPoint(e), transform.OfPoint(t), transform.OfVector(u)
        out.append((name, e, t, u, real))
    return out


def evidence_files(prefix):
    folder = out_path('evidence')
    return sorted(n for n in os.listdir(folder) if n.startswith(prefix) and n.lower().endswith('.png'))


# ------------------------------------------------------------------ build
def build(app):
    global TX
    doc = app.NewFamilyDocument(TEMPLATE)
    DOCS.append(doc)
    template_forms = [e.Id for e in DB.FilteredElementCollector(doc).OfClass(DB.GenericForm)]
    REPORT['template_form_ids'] = [str(i.Value) for i in template_forms]
    TX = DB.Transaction(doc, 'Build Miele KM 3054-1')
    TX.Start()
    family = doc.OwnerFamily
    family.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_SpecialityEquipment)
    family.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm = doc.FamilyManager
    fm.NewType(TYPE_NAME)
    for bip, value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Miele'),
                       (DB.BuiltInParameter.ALL_MODEL_MODEL, 'KM 3054-1'),
                       (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
                        'Gas cooktop 37 1/8 in, 5 burners incl. dual wok, black ceramic glass, cast-iron grates'),
                       (DB.BuiltInParameter.ALL_MODEL_URL,
                        'https://www.mieleusa.com/product/11766750/gas-cooktop-km-3054-1')]:
        p = fm.get_Parameter(bip)
        if p is not None:
            fm.Set(p, value)
    text = fm.AddParameter('Miele Material Number', DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fm.Set(text, '11766750')
    note = fm.AddParameter('Model Accuracy Notes', DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fm.Set(note, 'Envelope, cut-out and built-in height published; burner, knob and grate layout from the '
                 'orthographic product photo; grate and knob heights inferred. See INFERENCES.md.')
    saved = {}
    for label, value in [('Overall Width', G.WIDTH), ('Overall Depth', G.DEPTH), ('Overall Height', G.OVERALL_HEIGHT),
                         ('Height Above Counter', G.ABOVE_COUNTER), ('Casing Depth', G.CASING_DEPTH),
                         ('Built-in Height', G.BUILT_IN_HEIGHT), ('Cutout Width', G.CUTOUT_W),
                         ('Cutout Depth', G.CUTOUT_D_MAX)]:
        p = fm.AddParameter(label, DB.GroupTypeId.Geometry, DB.SpecTypeId.Length, False)
        fm.SetFormula(p, '%.6f in' % G.inches(value))
        saved[label] = value
    REPORT['dimension_parameters_mm'] = saved
    params = make_materials(doc, app, fm)
    subcats = {}
    for key, name in sorted(G.SUBCATEGORIES.items()):
        subcats[key] = doc.Settings.Categories.NewSubcategory(family.FamilyCategory, name)
    try:
        REPORT['short_curve_tolerance_in'] = app.ShortCurveTolerance * 12.0
    except Exception:
        REPORT['short_curve_tolerance_in'] = None

    by_key = dict((p['key'], p) for p in G.parts())
    bindings, unions = [], {}
    for gkey, mat, keys in G.groups():
        REPORT['stage_detail'] = 'group ' + gkey
        made = [part_solid(by_key[k]) for k in keys]
        elements = []
        if len(made) == 1:
            solids_out = made
        else:
            try:
                merged = made[0]
                for s in made[1:]:
                    merged = DB.BooleanOperationsUtils.ExecuteBooleanOperation(merged, s, DB.BooleanOperationsType.Union)
                solids_out = [merged]
                unions[gkey] = 'unioned %d parts' % len(made)
            except Exception as exc:
                solids_out = made
                unions[gkey] = 'union failed (%s); %d separate elements' % (exc, len(made))
        for s in solids_out:
            form = DB.FreeFormElement.Create(doc, s)
            form.Subcategory = subcats[mat]
            fm.AssociateElementParameterToFamilyParameter(form.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),
                                                          params[mat])
            elements.append(str(form.Id.Value))
        bindings.append({'group': gkey, 'material_key': mat, 'parts': keys, 'element_ids': elements,
                         'expected_subcategory': G.SUBCATEGORIES[mat],
                         'expected_material_parameter': G.MATERIAL_PARAMETERS[mat]})
    REPORT['group_bindings'] = bindings
    REPORT['unions'] = unions
    doc.Regenerate()                       # bounds are None until regenerated
    forms = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    bounds = measured_bounds(forms)
    REPORT['build_bounds_mm'] = bounds
    views = [make_view(doc, n, e, t, u, bounds, real, template_forms) for n, e, t, u, real in view_set(bounds)]
    REPORT['family_views'] = [v.Name for v in views]
    TX.Commit()
    TX = None
    REPORT['family_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    checkpoint('built')
    so = DB.SaveAsOptions()
    so.OverwriteExistingFile = True
    so.MaximumBackups = 1
    so.PreviewViewId = views[3].Id
    rfa = out_path(RFA_NAME)
    doc.SaveAs(rfa, so)
    REPORT['rfa_path'] = rfa
    export(doc, views, FAMILY_PREFIX)
    REPORT['family_images'] = evidence_files(FAMILY_PREFIX + ' - ')
    DOCS.remove(doc)
    doc.Close(False)
    checkpoint('saved')
    return rfa


def validate_family(app, rfa):
    doc = app.OpenDocumentFile(rfa)
    DOCS.append(doc)
    fam = {'reopened': doc.IsFamilyDocument, 'category': doc.OwnerFamily.FamilyCategory.Name,
           'placement_type': str(doc.OwnerFamily.FamilyPlacementType),
           'always_vertical': doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).AsInteger(),
           'warnings': [w.GetDescriptionText() for w in doc.GetWarnings()],
           'rfa_bytes': os.path.getsize(rfa),
           'rfa_mtime_utc': datetime.datetime.utcfromtimestamp(os.path.getmtime(rfa)).isoformat() + 'Z'}
    REPORT['family'] = fam
    fm = doc.FamilyManager
    saved = {}
    for p in fm.Parameters:
        if p.Definition.Name in REPORT['dimension_parameters_mm']:
            v = fm.CurrentType.AsDouble(p)
            saved[p.Definition.Name] = None if v is None else v * 304.8
    fam['saved_dimension_parameters_mm'] = saved
    fam['type_name'] = fm.CurrentType.Name
    rows = []
    for b in REPORT['group_bindings']:
        for sid in b['element_ids']:
            e = doc.GetElement(DB.ElementId(long(sid)))
            row = {'group': b['group'], 'id': sid, 'found': e is not None}
            if e is not None:
                row['subcategory'] = e.Subcategory.Name if e.Subcategory is not None else None
                assoc = fm.GetAssociatedFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM))
                row['material_parameter'] = assoc.Definition.Name if assoc is not None else None
            rows.append(row)
    fam['part_bindings'] = rows
    forms = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
    fam['freeform_count'] = len(forms)
    sl = [s for f in forms for s in solids(f.get_Geometry(fine_options()))]
    fam['rays'] = run_rays(sl)
    fam['measured_bounds_mm'] = measured_bounds(forms)
    checkpoint('family_measured')
    DOCS.remove(doc)
    doc.Close(False)


def validate_hosted(app, rfa):
    global TX
    family_doc = app.OpenDocumentFile(rfa)
    DOCS.append(family_doc)
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    DOCS.append(project)
    family = family_doc.LoadFamily(project)
    DOCS.remove(family_doc)
    family_doc.Close(False)
    symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])
    host = {}
    REPORT['hosted'] = host
    TX = DB.Transaction(project, 'Place on a countertop-height floor top face')
    TX.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    floor_type = DB.Floor.GetDefaultFloorType(project, False)
    slab = loop(DB.XYZ.Zero, DB.XYZ.BasisX, DB.XYZ.BasisY, [(-1500, -1000), (1500, -1000), (1500, 1000), (-1500, 1000)])
    floor = DB.Floor.Create(project, List[DB.CurveLoop]([slab]), floor_type, level.Id)
    floor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(COUNTER_FT)
    symbol.Activate()
    project.Regenerate()
    ref = DB.HostObjectUtils.GetTopFaces(floor)[0]
    face = floor.GetGeometryObjectFromReference(ref)
    point = face.Project(DB.XYZ(0, 0, COUNTER_FT)).XYZPoint
    inst = project.Create.NewFamilyInstance(ref, point, DB.XYZ.BasisX, symbol)
    project.Regenerate()
    T = inst.GetTransform()
    host['host_kind'] = 'floor top face at %.1f in (disposable countertop stand-in)' % (COUNTER_FT * 12)
    host['host_type'] = element_name(project.GetElement(floor.GetTypeId()))
    host['host_id'] = str(floor.Id.Value)
    host['instance_host_id'] = str(inst.Host.Id.Value) if inst.Host is not None else None
    host['hostface_present'] = inst.HostFace is not None
    host['face_normal'] = [face.FaceNormal.X, face.FaceNormal.Y, face.FaceNormal.Z]
    host['basis_z'] = [T.BasisZ.X, T.BasisZ.Y, T.BasisZ.Z]
    host['normal_dot'] = T.BasisZ.DotProduct(face.FaceNormal)
    host['host_face_z_mm'] = point.Z * 304.8
    host['instance_origin_z_mm'] = T.Origin.Z * 304.8
    sl = list(solids(inst.get_Geometry(fine_options())))
    host['rays'] = run_rays(sl, T, keys=['overall_width', 'overall_depth', 'top_above_counter', 'overall_height',
                                         'casing_depth_below_counter', 'built_in_height_with_box', 'knob_count'])
    checkpoint('hosted_measured')
    subs = {}
    for key, label in sorted(G.MATERIAL_PARAMETERS.items()):
        p = symbol.LookupParameter(label)
        original = p.AsElementId()
        alt = DB.Material.Create(project, 'QA ' + label)
        p.Set(alt)
        project.Regenerate()
        geo = list(solids(inst.get_Geometry(fine_options())))
        faces = [f.MaterialElementId for s in geo for f in s.Faces]
        full = sum(1 for s in geo if all(f.MaterialElementId == alt for f in s.Faces))
        p.Set(original)
        project.Regenerate()
        subs[label] = {'writable': not p.IsReadOnly, 'faces_inspected': len(faces),
                       'faces_carrying_substitute': sum(1 for i in faces if i == alt),
                       'solids_fully_carrying_substitute': full,
                       'restored': symbol.LookupParameter(label).AsElementId() == original}
    host['material_substitution'] = subs
    checkpoint('materials_tested')
    bb = inst.get_BoundingBox(None)
    lo = [bb.Min.X * 304.8, bb.Min.Y * 304.8, bb.Min.Z * 304.8]
    hi = [bb.Max.X * 304.8, bb.Max.Y * 304.8, bb.Max.Z * 304.8]
    target = DB.XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, (bb.Min.Z + bb.Max.Z) / 2)
    eye = target.Add(DB.XYZ(ft(1400), ft(-2200), ft(1600)))
    hosted_view = make_view(project, 'Hosted On Counter', eye, target, DB.XYZ.BasisZ,
                            [lo[0] - 300, lo[1] - 300, lo[2], hi[0] + 300, hi[1] + 300, hi[2]], False, None)
    TX.Commit()
    TX = None
    export(project, [hosted_view], HOSTED_PREFIX)
    host['images'] = evidence_files(HOSTED_PREFIX)
    host['warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    checkpoint('hosted_exported')


def gates():
    fam, host = REPORT.get('family', {}), REPORT.get('hosted', {})
    rays = fam.get('rays', {})
    hrays = host.get('rays', {})
    saved = fam.get('saved_dimension_parameters_mm', {})
    bind = fam.get('part_bindings', [])
    want = dict((b['group'], b) for b in REPORT.get('group_bindings', []))
    g = {
        'reopened_category_workplane': bool(fam.get('reopened')) and fam.get('category') == 'Specialty Equipment'
            and fam.get('placement_type') == 'WorkPlaneBased' and fam.get('always_vertical') == 0,
        'parts_bound': bool(bind) and all(r.get('found') and r.get('subcategory') == want[r['group']]['expected_subcategory']
                                          and r.get('material_parameter') == want[r['group']]['expected_material_parameter']
                                          for r in bind),
        'family_rays': bool(rays) and all(v['pass'] for v in rays.values()),
        'saved_parameters': all(abs((saved.get(k) or -1e9) - v) < 0.01 for k, v in REPORT.get('dimension_parameters_mm', {}).items()),
        'actual_face_host': host.get('instance_host_id') == host.get('host_id') and bool(host.get('hostface_present')),
        'orientation_normal_dot_1': abs((host.get('normal_dot') or 0) - 1.0) < 1e-6,
        'hosted_rays': bool(hrays) and all(v['pass'] for v in hrays.values()),
        'materials_reach_faces': len(host.get('material_substitution', {})) == len(G.MATERIAL_PARAMETERS) and all(
            v['faces_carrying_substitute'] > 0 and v['restored'] for v in host.get('material_substitution', {}).values()),
        'zero_warnings': REPORT.get('family_warnings') == [] and fam.get('warnings') == [] and host.get('warnings') == [],
        'views_exported': len(REPORT.get('family_images', [])) >= 5 and len(host.get('images', [])) >= 1,
    }
    REPORT['gates'] = g
    REPORT['failed_gates'] = [k for k, v in g.items() if not v]
    REPORT['technical_pass'] = all(g.values())
    return g


def main():
    app = __revit__.Application  # noqa: F821  (provided by pyRevit)
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild
    REPORT['template'] = TEMPLATE
    checkpoint('started')
    if not str(app.VersionNumber).startswith('2025'):
        raise RuntimeError('Revit 2025 required; host reports %s' % app.VersionNumber)
    if not os.path.isfile(TEMPLATE):
        raise RuntimeError('Template not found: ' + TEMPLATE)
    problems = G.check_profiles()
    REPORT['profile_problems'] = problems
    if problems:
        raise RuntimeError('Profile preflight failed: %r' % problems)
    rfa = build(app)
    validate_family(app, rfa)
    validate_hosted(app, rfa)
    gates()
    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    checkpoint('complete' if REPORT['technical_pass'] else 'gates_failed')
    if not REPORT['technical_pass']:
        raise RuntimeError('Gate failures: %r' % REPORT['failed_gates'])
    print('[km3054] TECHNICAL PASS (builder). RFA: ' + rfa)


try:
    main()
except Exception:
    REPORT['error'] = traceback.format_exc()
    REPORT['technical_pass'] = False
    try:
        checkpoint('gates_failed' if REPORT.get('stage') == 'gates_failed' else 'failed')
    except Exception:
        pass
    print(REPORT['error'])
    raise
finally:
    if TX is not None:
        try:
            TX.RollBack()
        except Exception:
            pass
    for d in reversed(DOCS):
        try:
            d.Close(False)
        except Exception:
            pass
