# -*- coding: utf-8 -*-
"""Build the Visual Comfort Nodes Angled Wall Sconce KW1041MBK (Midnight Black / Milk) as a Revit 2025
face-based Lighting Fixtures family. Runs in pyRevit IronPython 2.7 through the serialized runner.

Frame: X along the host face, Y up the host face, Z projecting out of the host face. Inches in this file,
feet only at the Revit API boundary. Constants live in common.py.
"""
import sys
import os
import json
import math
import traceback

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
if RUN + "/source" not in sys.path:
    sys.path.insert(0, RUN + "/source")
from common import *

RESULT = RUN + "/_work/build_result.json"
CAND = RUN + "/_work/candidates"

METAL_RGB = (32, 32, 35)
GLASS_RGB = (242, 240, 232)

report = {'stages': {}, 'constants': {
    'theta_deg': math.degrees(TH), 'disc_t_in': DISC_T, 'cf_in': list(CF), 'light_pos_in': list(LIGHT_POS), 'neck_axial_in': NECK_A,
    'axis_N': list(N), 'sphere_centre_in': list(SPHERE_C)}}
state = {}


def checkpoint(stage):
    report['stage'] = stage
    report['failures'] = FAILURES
    with open(safe(RESULT), 'w') as f:
        json.dump(report, f, indent=1, default=str)


def run_stage(name, fn, *args):
    checkpoint('start ' + name)
    try:
        out = fn(*args)
        report['stages'][name] = {'ok': True}
        checkpoint('done ' + name)
        return out
    except Exception:
        report['stages'][name] = {'ok': False, 'error': traceback.format_exc()}
        checkpoint('failed ' + name)
        return None


# ---- geometry helpers --------------------------------------------------------------------------------
def part_report(el):
    solids = list(iter_solids(el.get_Geometry(DB.Options())))
    pts = []
    vol = 0.0
    faces = 0
    for s in solids:
        pts.extend(solid_edge_points(s))
        pts.extend(mesh_points(s))
        vol += s.Volume * 1728.0
        faces += s.Faces.Size
    out = {'solids': len(solids), 'volume_in3': round(vol, 4), 'faces': faces}
    if pts:
        out['x'] = extent(pts, XV)
        out['y'] = extent(pts, YV)
        out['z'] = extent(pts, ZV)
        out['axis_rel_cf'] = extent([rel(p, CF) for p in pts], N)
    return out


def loop_circle(center, u, v, r):
    c = V(center)
    ux = DB.XYZ(u[0], u[1], u[2])
    vx = DB.XYZ(v[0], v[1], v[2])
    rr = r / 12.0
    loop = DB.CurveLoop()
    loop.Append(DB.Arc.Create(c, rr, 0.0, math.pi, ux, vx))
    loop.Append(DB.Arc.Create(c, rr, math.pi, 2.0 * math.pi, ux, vx))
    return loop


def loop_rect(center, u, v, half_u, half_v):
    def at(a, b):
        return V((center[0] + u[0] * a + v[0] * b, center[1] + u[1] * a + v[1] * b, center[2] + u[2] * a + v[2] * b))
    pts = [at(-half_u, -half_v), at(half_u, -half_v), at(half_u, half_v), at(-half_u, half_v)]
    loop = DB.CurveLoop()
    for i in range(4):
        loop.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
    return loop


def extrude(loops, direction, dist):
    return DB.GeometryCreationUtilities.CreateExtrusionGeometry(
        List[DB.CurveLoop](loops), DB.XYZ(direction[0], direction[1], direction[2]), dist / 12.0)


def axis_pt(r, a):
    """Point at radial r (along UPV) and axial a (along N) from the cut-face centre CF."""
    return V((CF[0] + UPV[0] * r + N[0] * a, CF[1] + UPV[1] * r + N[1] * a, CF[2] + UPV[2] * r + N[2] * a))


def revolve(loop):
    fx = DB.XYZ(UPV[0], UPV[1], UPV[2])
    fz = DB.XYZ(N[0], N[1], N[2])
    fy = fz.CrossProduct(fx)
    frame = DB.Frame(V(CF), fx, fy, fz)
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame, List[DB.CurveLoop]([loop]), 0.0, 2.0 * math.pi)


def shade_dims():
    ro = SH_R
    ri = SH_R - SH_WALL
    ac = GLOBE_AX
    a_neck = ac - NECK_BELOW
    ro_n = math.sqrt(ro * ro - NECK_BELOW * NECK_BELOW)
    ri_n = math.sqrt(ri * ri - NECK_BELOW * NECK_BELOW)
    ph_o = math.atan2(-NECK_BELOW, ro_n)
    ph_i = math.atan2(-NECK_BELOW, ri_n)
    mid_o = 0.5 * (ph_o + math.pi / 2.0)
    mid_i = 0.5 * (ph_i + math.pi / 2.0)
    return ro, ri, ac, a_neck, ro_n, ri_n, mid_o, mid_i


def shade_direct():
    ro, ri, ac, a_neck, ro_n, ri_n, mid_o, mid_i = shade_dims()
    loop = DB.CurveLoop()
    loop.Append(DB.Arc.Create(axis_pt(ro_n, a_neck), axis_pt(0.0, ac + ro),
                              axis_pt(ro * math.cos(mid_o), ac + ro * math.sin(mid_o))))
    loop.Append(DB.Line.CreateBound(axis_pt(0.0, ac + ro), axis_pt(0.0, ac + ri)))
    loop.Append(DB.Arc.Create(axis_pt(0.0, ac + ri), axis_pt(ri_n, a_neck),
                              axis_pt(ri * math.cos(mid_i), ac + ri * math.sin(mid_i))))
    loop.Append(DB.Line.CreateBound(axis_pt(ri_n, a_neck), axis_pt(ro_n, a_neck)))
    return revolve(loop)


def shade_by_difference():
    ro, ri, ac, a_neck, ro_n, ri_n, mid_o, mid_i = shade_dims()
    outer = DB.CurveLoop()
    outer.Append(DB.Arc.Create(axis_pt(ro_n, a_neck), axis_pt(0.0, ac + ro),
                               axis_pt(ro * math.cos(mid_o), ac + ro * math.sin(mid_o))))
    outer.Append(DB.Line.CreateBound(axis_pt(0.0, ac + ro), axis_pt(0.0, a_neck)))
    outer.Append(DB.Line.CreateBound(axis_pt(0.0, a_neck), axis_pt(ro_n, a_neck)))
    below = a_neck - 0.10
    inner = DB.CurveLoop()
    inner.Append(DB.Line.CreateBound(axis_pt(ri_n, below), axis_pt(ri_n, a_neck)))
    inner.Append(DB.Arc.Create(axis_pt(ri_n, a_neck), axis_pt(0.0, ac + ri),
                               axis_pt(ri * math.cos(mid_i), ac + ri * math.sin(mid_i))))
    inner.Append(DB.Line.CreateBound(axis_pt(0.0, ac + ri), axis_pt(0.0, below)))
    inner.Append(DB.Line.CreateBound(axis_pt(0.0, below), axis_pt(ri_n, below)))
    return DB.BooleanOperationsUtils.ExecuteBooleanOperation(revolve(outer), revolve(inner),
                                                             DB.BooleanOperationsType.Difference)


def shade_solid():
    ro, ri, ac, a_neck, ro_n, ri_n, mid_o, mid_i = shade_dims()
    report['constants']['shade_profile'] = {'neck_outer_r': ro_n, 'neck_inner_r': ri_n, 'neck_axial': a_neck,
                                            'outer_pole_axial': ac + ro, 'inner_pole_axial': ac + ri}
    try:
        s = shade_direct()
        if s is not None and s.Volume > 1e-9 and s.Faces.Size >= 4:
            report['shade_method'] = 'direct hollow revolve'
            return s
        report['shade_direct_rejected'] = 'volume %s faces %s' % (s.Volume if s is not None else None,
                                                                   s.Faces.Size if s is not None else None)
    except Exception:
        report['shade_direct_error'] = traceback.format_exc()
    s = shade_by_difference()
    report['shade_method'] = 'outer revolve minus inner revolve'
    return s


# ---- materials ---------------------------------------------------------------------------------------
def set_color(asset, key, color):
    prop = asset.FindByName(key)
    if prop is None:
        return False
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.SetValueAsColor(DB.Color(color[0], color[1], color[2]))
    return True


def set_scalar(asset, key, value):
    prop = asset.FindByName(key)
    if prop is None:
        return False
    if prop.NumberOfConnectedProperties:
        prop.RemoveConnectedAsset()
    prop.Value = value
    return True


def make_material(doc, app, name, color, scalars, shade_color, shade_transparency, material_class):
    assets = list(app.GetAssets(DB.Visual.AssetType.Appearance))
    source = None
    for a in assets:
        bs = a.FindByName('BaseSchema')
        if bs is not None and bs.Value == 'GenericSchema':
            source = a
            break
    if source is None:
        raise RuntimeError('no GenericSchema appearance asset found among %d assets' % len(assets))
    appearance = DB.AppearanceAssetElement.Create(doc, name, source)
    mat = doc.GetElement(DB.Material.Create(doc, name))
    mat.AppearanceAssetId = appearance.Id
    mat.Color = DB.Color(shade_color[0], shade_color[1], shade_color[2])
    mat.Transparency = shade_transparency
    try:
        mat.MaterialClass = material_class
    except Exception as ex:
        report.setdefault('material_class_errors', {})[name] = str(ex)
    scope = DB.Visual.AppearanceAssetEditScope(doc)
    asset = scope.Start(appearance.Id)
    applied = {}
    applied['generic_diffuse'] = set_color(asset, 'generic_diffuse', color)
    for k in sorted(scalars.keys()):
        try:
            applied[k] = set_scalar(asset, k, scalars[k])
        except Exception as ex:
            applied[k] = 'error: ' + str(ex)
    if 'asset_props' not in report:
        names = []
        try:
            for i in range(asset.Size):
                names.append(asset[i].Name)
        except Exception as ex:
            names.append('listing failed: ' + str(ex))
        report['asset_props'] = names
    scope.Commit(True)
    scope.Dispose()
    report.setdefault('materials', {})[name] = {'id': str(mat.Id.Value), 'applied': applied}
    return mat


def family_param_list(doc):
    out = []
    for p in doc.FamilyManager.Parameters:
        try:
            out.append({'name': p.Definition.Name, 'instance': p.IsInstance,
                        'group': str(p.Definition.GetGroupTypeId().TypeId), 'storage': str(p.StorageType),
                        'readonly': p.IsReadOnly})
        except Exception as ex:
            out.append({'err': str(ex)})
    return out


# ---- stages ------------------------------------------------------------------------------------------
def stage_family():
    app = __revit__.Application
    state['app'] = app
    report['revit'] = app.VersionNumber + ' ' + app.VersionBuild
    report['short_curve_tolerance_in'] = app.ShortCurveTolerance * 12.0
    doc = app.NewFamilyDocument(TEMPLATE)
    state['doc'] = doc
    fam = doc.OwnerFamily
    report['template'] = TEMPLATE
    report['category_in_template'] = fam.FamilyCategory.Name
    report['placement_type_in_template'] = str(fam.FamilyPlacementType)
    with Tx(doc, 'Set category'):
        fam.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
        doc.Regenerate()
    report['category'] = fam.FamilyCategory.Name
    report['placement_type'] = str(fam.FamilyPlacementType)

    # The 'Light Source' family parameter appears only once the category is Lighting Fixtures; Yes creates the source.
    light_param = None
    for p in fam.Parameters:
        if p.Definition.Name == 'Light Source':
            light_param = p
    report['light_source_parameter_found'] = light_param is not None
    if light_param is None:
        raise RuntimeError("family parameter 'Light Source' not present after the category change")
    with Tx(doc, 'Enable light source'):
        light_param.Set(1)
        doc.Regenerate()
    report['light_source_parameter_value'] = pval(light_param)
    for label, bip in [('host_behaviour', DB.BuiltInParameter.FAMILY_HOSTING_BEHAVIOR),
                       ('always_vertical', DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL),
                       ('work_plane_based', DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED)]:
        try:
            p = fam.get_Parameter(bip)
            report[label] = pval(p) if p is not None else None
        except Exception as ex:
            report[label] = 'error: ' + str(ex)
    census = {}
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        key = '%s | %s' % (e.GetType().Name, e.Category.Name if e.Category else None)
        census[key] = census.get(key, 0) + 1
    report['template_element_census'] = census
    tmpl_ext = []
    for e in DB.FilteredElementCollector(doc).OfClass(DB.Extrusion):
        item = {'id': str(e.Id.Value)}
        try:
            bb = e.get_BoundingBox(None)
            item['bbox_in'] = [round(v * 12.0, 3) for v in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)]
            item['category'] = e.Category.Name if e.Category is not None else None
            item['subcategory'] = e.Subcategory.Name if e.Subcategory is not None else None
            item['is_solid'] = e.IsSolid
            vis = e.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
            item['visible_param'] = pval(vis) if vis is not None else None
            item['is_reference_param'] = pval(e.get_Parameter(DB.BuiltInParameter.ELEMENT_IS_REFERENCE)) \
                if e.get_Parameter(DB.BuiltInParameter.ELEMENT_IS_REFERENCE) is not None else None
        except Exception as ex:
            item['error'] = str(ex)
        tmpl_ext.append(item)
    report['template_extrusions'] = tmpl_ext
    report['family_parameters_after_category'] = family_param_list(doc)


def stage_params():
    doc = state['doc']
    fm = doc.FamilyManager
    with Tx(doc, 'Family type and parameters'):
        fm.NewType(TYPE_NAME)
        fm.AddParameter('Metal Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
        fm.AddParameter('Glass Finish', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
        fm.AddParameter('Show Disc', DB.GroupTypeId.Visibility, DB.SpecTypeId.Boolean.YesNo, True)
        fm.Set(fm.get_Parameter('Show Disc'), 1)


def stage_materials():
    doc = state['doc']
    app = state['app']
    fm = doc.FamilyManager
    with Tx(doc, 'Materials'):
        metal = make_material(doc, app, 'Midnight Black', METAL_RGB,
                              {'generic_glossiness': 0.45, 'generic_reflectivity_at_0deg': 0.05,
                               'generic_reflectivity_at_90deg': 0.5}, (34, 34, 38), 0, 'Metal')
        glass = make_material(doc, app, 'Milk Glass', GLASS_RGB,
                              {'generic_glossiness': 0.9, 'generic_reflectivity_at_0deg': 0.05,
                               'generic_reflectivity_at_90deg': 0.7, 'generic_transparency': 0.35},
                              (240, 238, 230), 0, 'Glass')
        fm.Set(fm.get_Parameter('Metal Finish'), metal.Id)
        fm.Set(fm.get_Parameter('Glass Finish'), glass.Id)


def stage_identity():
    doc = state['doc']
    fm = doc.FamilyManager
    ident = {}
    with Tx(doc, 'Identity data'):
        for label, bip, value in [
                ('Manufacturer', DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, 'Visual Comfort Studio'),
                ('Model', DB.BuiltInParameter.ALL_MODEL_MODEL, 'KW1041MBK'),
                ('Description', DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,
                 'Nodes Angled Wall Sconce, Midnight Black / Milk. Kelly Wearstler for Visual Comfort Studio. '
                 '8 W x 7.63 H x 5.5 D in. 1x JCD/G9 3 W 120 V LED (bulb not included). Damp location.'),
                ('Type Comments', DB.BuiltInParameter.ALL_MODEL_TYPE_COMMENTS,
                 'Visualization family built from published dimensions and product photos; '
                 'see README for the basis of each dimension.')]:
            try:
                p = fm.get_Parameter(bip)
                if p is None:
                    ident[label] = 'family parameter not present'
                    continue
                fm.Set(p, value)
                ident[label] = 'set'
            except Exception as ex:
                ident[label] = 'error: ' + str(ex)
        for label, bip, setter in [
                ('Lamp', DB.BuiltInParameter.LIGHTING_FIXTURE_LAMP, None),
                ('Wattage', DB.BuiltInParameter.LIGHTING_FIXTURE_WATTAGE, None)]:
            try:
                p = fm.get_Parameter(bip)
                ident[label + '_present'] = p is not None
                if p is not None:
                    ident[label + '_storage'] = str(p.StorageType)
            except Exception as ex:
                ident[label + '_error'] = str(ex)
    report['identity'] = ident


def stage_subcategories():
    doc = state['doc']
    cats = doc.Settings.Categories
    parent = doc.OwnerFamily.FamilyCategory
    sub = {}
    with Tx(doc, 'Subcategories'):
        for nm in PART_NAMES:
            sub[nm] = cats.NewSubcategory(parent, nm)
    state['sub'] = sub
    state['parts'] = {}


def add_ff(name, solid, param_name):
    doc = state['doc']
    fm = doc.FamilyManager
    el = DB.FreeFormElement.Create(doc, solid)
    el.Subcategory = state['sub'][name]
    fm.AssociateElementParameterToFamilyParameter(el.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),
                                                  fm.get_Parameter(param_name))
    state['parts'][name] = el.Id
    return el


def stage_backplate():
    doc = state['doc']
    with Tx(doc, 'Backplate'):
        add_ff('Backplate', extrude([loop_circle((0.0, 0.0, 0.0), XV, YV, BP_R)], ZV, BP_T), 'Metal Finish')
        doc.Regenerate()


def stage_body():
    doc = state['doc']
    with Tx(doc, 'Body'):
        cyl = extrude([loop_circle((0.0, 0.0, BP_T), XV, YV, BODY_R)], ZV, 4.0)
        cutter = extrude([loop_rect(CF, XV, UPV, 6.0, 6.0)], N, 8.0)
        body = DB.BooleanOperationsUtils.ExecuteBooleanOperation(cyl, cutter, DB.BooleanOperationsType.Difference)
        report['body_cut_volume_in3'] = round(body.Volume * 1728.0, 4)
        add_ff('Body', body, 'Metal Finish')
        doc.Regenerate()


def stage_socket():
    doc = state['doc']
    with Tx(doc, 'Socket'):
        add_ff('Socket', extrude([loop_circle(CF, XV, UPV, COLLAR_R)], N, NECK_A), 'Metal Finish')
        doc.Regenerate()


def stage_shade():
    doc = state['doc']
    with Tx(doc, 'Shade'):
        add_ff('Shade', shade_solid(), 'Glass Finish')
        doc.Regenerate()


def circle_array(r):
    ca = DB.CurveArray()
    ux = DB.XYZ(XV[0], XV[1], XV[2])
    vx = DB.XYZ(UPV[0], UPV[1], UPV[2])
    ca.Append(DB.Arc.Create(V(CF), r / 12.0, 0.0, math.pi, ux, vx))
    ca.Append(DB.Arc.Create(V(CF), r / 12.0, math.pi, 2.0 * math.pi, ux, vx))
    return ca


def stage_disc():
    doc = state['doc']
    fm = doc.FamilyManager
    with Tx(doc, 'Disc'):
        plane = DB.Plane.CreateByNormalAndOrigin(DB.XYZ(N[0], N[1], N[2]), V(CF))
        sp = DB.SketchPlane.Create(doc, plane)
        arr = DB.CurveArrArray()
        arr.Append(circle_array(DISC_R))
        arr.Append(circle_array(COLLAR_R))
        disc = doc.FamilyCreate.NewExtrusion(True, arr, sp, DISC_T / 12.0)
        disc.Subcategory = state['sub']['Disc']
        fm.AssociateElementParameterToFamilyParameter(disc.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),
                                                      fm.get_Parameter('Metal Finish'))
        state['parts']['Disc'] = disc.Id
        vis = disc.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
        report['disc_visible_param_found'] = vis is not None
        if vis is None:
            vis = disc.LookupParameter('Visible')
            report['disc_visible_param_by_name'] = vis is not None
        fm.AssociateElementParameterToFamilyParameter(vis, fm.get_Parameter('Show Disc'))
        report['disc_visibility_linked'] = True
        doc.Regenerate()


def summarise_parts():
    doc = state['doc']
    parts = {}
    for nm in PART_NAMES:
        if nm in state['parts']:
            parts[nm] = part_report(doc.GetElement(state['parts'][nm]))
            parts[nm]['element_id'] = str(state['parts'][nm].Value)
    allx = []
    ally = []
    allz = []
    for nm in parts:
        p = parts[nm]
        if 'x' in p:
            allx += p['x']
            ally += p['y']
            allz += p['z']
    env = None
    if allx:
        env = {'x': [min(allx), max(allx)], 'y': [min(ally), max(ally)], 'z': [min(allz), max(allz)],
               'W': round(max(allx) - min(allx), 4), 'H': round(max(ally) - min(ally), 4),
               'D': round(max(allz) - min(allz), 4)}
    return parts, env


def stage_summary():
    doc = state['doc']
    parts, env = summarise_parts()
    report['family_parts'] = parts
    report['family_envelope_in'] = env
    dax = parts.get('Disc', {}).get('axis_rel_cf')
    report['disc_axial_range_rel_cf'] = dax
    bax = parts.get('Body', {}).get('axis_rel_cf')
    report['body_axial_range_rel_cf'] = bax
    if dax and (dax[0] + dax[1]) * 0.5 < 0.0:
        with Tx(doc, 'Move disc onto the cut face'):
            DB.ElementTransformUtils.MoveElement(doc, state['parts']['Disc'],
                                                 V((N[0] * DISC_T, N[1] * DISC_T, N[2] * DISC_T)))
            doc.Regenerate()
        report['disc_moved_forward'] = True
        parts, env = summarise_parts()
        report['family_parts_after_disc_fix'] = parts
        report['family_envelope_after_disc_fix_in'] = env


# ---- light source ------------------------------------------------------------------------------------
def find_light_sources(doc):
    found = []
    seen = set()
    bic = getattr(DB.BuiltInCategory, 'OST_LightingFixtureSource', None)
    report['light_category_enum_present'] = bic is not None
    if bic is not None:
        for e in DB.FilteredElementCollector(doc).OfCategoryId(DB.ElementId(bic)).WhereElementIsNotElementType():
            if e.Id.Value not in seen:
                seen.add(e.Id.Value)
                found.append(e)
    if not found:
        for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            try:
                nm = e.Category.Name if e.Category is not None else ''
            except Exception:
                nm = ''
            if 'Source' in nm and e.Id.Value not in seen:
                seen.add(e.Id.Value)
                found.append(e)
    return found


def element_info(e):
    item = {'id': str(e.Id.Value), 'cls': e.GetType().Name, 'cat': e.Category.Name if e.Category else None}
    try:
        bb = e.get_BoundingBox(None)
        if bb is not None:
            item['bbox_in'] = [round(v * 12.0, 4) for v in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)]
    except Exception as ex:
        item['bbox_err'] = str(ex)
    try:
        loc = e.Location
        item['location_class'] = type(loc).__name__
        if hasattr(loc, 'Point') and loc.Point is not None:
            item['point_in'] = rnd(to_in(loc.Point))
    except Exception as ex:
        item['location_err'] = str(ex)
    try:
        ps = []
        for p in e.Parameters:
            ps.append({'name': p.Definition.Name, 'storage': str(p.StorageType), 'ro': p.IsReadOnly, 'value': pval(p)})
        item['params'] = ps
    except Exception as ex:
        item['params_err'] = str(ex)
    return item


def enum_pick(enum_type, wanted):
    for n in System.Enum.GetNames(enum_type):
        if n.lower() == wanted.lower():
            return getattr(enum_type, n)
    return None


def stage_light():
    doc = state['doc']
    r = report.setdefault('light', {})
    if LT is None:
        r['error'] = 'Autodesk.Revit.DB.Lighting is not available'
        return
    for nm in ('LightShapeStyle', 'LightDistributionStyle'):
        try:
            r[nm + '_names'] = list(System.Enum.GetNames(getattr(LT, nm)))
        except Exception as ex:
            r[nm + '_names_error'] = str(ex)
    r['before'] = read_light(doc)
    srcs = find_light_sources(doc)
    r['source_elements'] = [element_info(e) for e in srcs]

    lf = LT.LightFamily.GetLightFamily(doc)
    origin = lf.GetLightSourceTransform().Origin
    delta = V(LIGHT_POS).Subtract(origin)
    r['move_delta_in'] = rnd(to_in(delta))
    if not srcs:
        raise RuntimeError('no light source element found')
    with Tx(doc, 'Move light source into the shade'):
        srcs[0].Location.Move(delta)
        doc.Regenerate()
    r['move_method'] = 'Location.Move (ElementTransformUtils.MoveElement rolls the transaction back on a light source)'
    r['after_move'] = read_light(doc)

    try:
        with Tx(doc, 'Light shape and distribution'):
            lf = LT.LightFamily.GetLightFamily(doc)
            shp = enum_pick(LT.LightShapeStyle, 'Point')
            dst = enum_pick(LT.LightDistributionStyle, 'Spherical')
            r['style_pick'] = {'shape': str(shp), 'distribution': str(dst)}
            if shp is not None:
                lf.SetLightShapeStyle(shp)
            if dst is not None:
                lf.SetLightDistributionStyle(dst)
    except Exception:
        r['style_error'] = traceback.format_exc()

    try:
        with Tx(doc, 'Light photometrics'):
            lf = LT.LightFamily.GetLightFamily(doc)
            n = lf.GetNumberOfLightTypes()
            r['light_types_at_write'] = n
            for i in range(n):
                lt = lf.GetLightType(i)
                try:
                    lt.SetLightShape(LT.PointLightShape())
                    lt.SetLightDistribution(LT.SphericalLightDistribution())
                except Exception as ex:
                    r['shape_distribution_type_error'] = str(ex)
                ii = LT.InitialWattageIntensity(90.0, 3.0)
                try:
                    ii.Wattage = 3.0
                    ii.Efficacy = 90.0
                except Exception as ex:
                    r['intensity_setter_error'] = str(ex)
                lt.SetInitialIntensity(ii)
                lt.SetInitialColor(LT.CustomInitialColor(2700.0))
                lt.SetLossFactor(LT.BasicLossFactor())
    except Exception:
        r['photometrics_error'] = traceback.format_exc()

    r['after'] = read_light(doc)
    fm = doc.FamilyManager
    fbx = {}
    for nm in ('FBX_LIGHT_LIMUNOUS_FLUX', 'FBX_LIGHT_WATTAGE', 'FBX_LIGHT_EFFICACY',
               'FBX_LIGHT_INITIAL_COLOR_TEMPERATURE', 'FBX_LIGHT_LIMUNOUS_INTENSITY'):
        try:
            bip = getattr(DB.BuiltInParameter, nm)
            fp = fm.get_Parameter(bip)
            if fp is None:
                fbx[nm] = 'not a family parameter'
                continue
            ft = fm.CurrentType
            if fp.StorageType == DB.StorageType.Double:
                fbx[nm] = ft.AsDouble(fp)
            elif fp.StorageType == DB.StorageType.Integer:
                fbx[nm] = ft.AsInteger(fp)
            else:
                fbx[nm] = str(fp.StorageType)
        except Exception as ex:
            fbx[nm] = 'error: ' + str(ex)
    r['fbx_family_parameters'] = fbx
    r['source_elements_after'] = [element_info(e) for e in find_light_sources(doc)]
    report['family_parameters_final'] = family_param_list(doc)


# ---- views and save ----------------------------------------------------------------------------------
def make_view(doc, name, direction, dist=60.0):
    vtype = None
    for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType):
        if v.ViewFamily == DB.ViewFamily.ThreeDimensional:
            vtype = v
            break
    view = DB.View3D.CreateIsometric(doc, vtype.Id)
    view.Name = name
    target = (0.0, 0.0, 2.7)
    ln = math.sqrt(sum(c * c for c in direction))
    d = [c / ln for c in direction]
    eye = V((target[0] + d[0] * dist, target[1] + d[1] * dist, target[2] + d[2] * dist))
    fwd = V(target).Subtract(eye).Normalize()
    up = DB.XYZ.BasisY
    if abs(up.DotProduct(fwd)) > 0.98:
        up = DB.XYZ.BasisZ
    right = fwd.CrossProduct(up).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(fwd).Normalize(), fwd))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    keep = doc.OwnerFamily.FamilyCategory.Id
    for cat in doc.Settings.Categories:
        try:
            if cat.Id != keep and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        except Exception:
            pass
    bic = getattr(DB.BuiltInCategory, 'OST_LightingFixtureSource', None)
    if bic is not None:
        try:
            lsid = DB.ElementId(bic)
            if view.CanCategoryBeHidden(lsid):
                view.SetCategoryHidden(lsid, True)
        except Exception:
            pass
    region = DB.BoundingBoxXYZ()
    region.Min = V((-5.0, -4.6, 0.001))
    region.Max = V((5.0, 4.6, 5.95))
    view.SetSectionBox(region)
    view.IsSectionBoxActive = True
    return view


FAMILY_VIEWS = [
    ('front', (0.0, 0.0, 1.0), VIEWS),
    ('side', (-1.0, 0.0, 0.0), VIEWS),
    ('oblique', (-0.8005, -0.1822, 0.5710), VIEWS),
    ('cand_below_left', (-0.8005, -0.1822, 0.5710), CAND),
    ('cand_above_left', (-0.8005, 0.1822, 0.5710), CAND),
    ('cand_below_right', (0.8005, -0.1822, 0.5710), CAND),
    ('cand_above_right', (0.8005, 0.1822, 0.5710), CAND),
]


def stage_views_and_save():
    doc = state['doc']
    fm = doc.FamilyManager
    views = {}
    all_views = FAMILY_VIEWS
    with Tx(doc, 'Preview views'):
        for tag, direction, folder in all_views:
            views[tag] = make_view(doc, 'Preview ' + tag, direction)
        doc.Regenerate()
    report['exports'] = {}
    for tag, direction, folder in FAMILY_VIEWS:
        try:
            report['exports'][tag] = export_view(doc, views[tag], folder, 'family_' + tag)
        except Exception:
            report['exports'][tag] = 'error: ' + traceback.format_exc()
    report['show_disc_value_before_save'] = fm.CurrentType.AsInteger(fm.get_Parameter('Show Disc'))
    keep = views['oblique']
    try:
        with Tx(doc, 'Remove extra preview views'):
            for tag, direction, folder in all_views:
                if tag != 'oblique':
                    doc.Delete(views[tag].Id)
    except Exception:
        report['view_cleanup_error'] = traceback.format_exc()
    report['warnings_before_save'] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    opts = DB.SaveAsOptions()
    opts.OverwriteExistingFile = True
    try:
        opts.PreviewViewId = keep.Id
    except Exception as ex:
        report['preview_view_error'] = str(ex)
    if os.path.exists(RFA):
        os.remove(safe(RFA))
    doc.SaveAs(os.path.normpath(safe(RFA)), opts)
    report['saved'] = os.path.exists(RFA)
    for fn in os.listdir(RUN):
        if fn.lower().endswith('.rfa') and RUN + '/' + fn != RFA and fn.startswith('Visual_Comfort_Nodes_KW1041MBK'):
            os.remove(safe(RUN + '/' + fn))
            report.setdefault('backups_removed', []).append(fn)


def stage_validation():
    import validate_sconce
    validate_sconce.run_all(state['app'])


def main():
    checkpoint('begin')
    run_stage('family', stage_family)
    if state.get('doc') is None:
        return
    try:
        run_stage('params', stage_params)
        run_stage('materials', stage_materials)
        run_stage('identity', stage_identity)
        run_stage('subcategories', stage_subcategories)
        if report['stages'].get('subcategories', {}).get('ok') and report['stages'].get('params', {}).get('ok'):
            run_stage('backplate', stage_backplate)
            run_stage('body', stage_body)
            run_stage('socket', stage_socket)
            run_stage('shade', stage_shade)
            run_stage('disc', stage_disc)
            run_stage('summary', stage_summary)
            run_stage('light', stage_light)
            run_stage('views_and_save', stage_views_and_save)
    finally:
        close_doc(state['doc'], report.setdefault('doc_closes', []), 'family build doc')
        checkpoint('family doc closed')
    if report['stages'].get('views_and_save', {}).get('ok'):
        run_stage('validation', stage_validation)
    report['all_ok'] = all(v.get('ok') for v in report['stages'].values())
    checkpoint('complete')


main()
