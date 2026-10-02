# -*- coding: utf-8 -*-
"""Native validation of the KW1041MBK family in Revit 2025 (pyRevit IronPython 2.7).

run_all(app) reopens the saved RFA, places it on the exterior face of a wall in a disposable project, measures the
placed geometry, toggles Show Disc, swaps the finish materials, checks the light source and exports the hosted views.
validation.json is rewritten after every stage. The disposable project is never saved.
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

OUT = RUN + "/validation.json"
TOL = 0.02
result = {'gates': {}, 'stages': {}, 'expected': {
    'envelope_in': {'W': 8.00, 'H': 7.63, 'D': 5.50}, 'envelope_disc_off_in': {'W': 5.25, 'H': 5.25, 'D': 5.50},
    'backplate_in': {'diameter': 5.25, 'thickness': 0.125}, 'shade_in': {'max_diameter': 3.50, 'axial_height': 3.25},
    'tolerance_in': TOL}}
S_ = {}


def dump():
    result['failures'] = FAILURES
    with open(safe(OUT), 'w') as f:
        json.dump(result, f, indent=1, default=str)


def stage(name, fn, *args):
    try:
        out = fn(*args)
        result['stages'][name] = {'ok': True}
        dump()
        return out
    except Exception:
        result['stages'][name] = {'ok': False, 'error': traceback.format_exc()}
        dump()
        return None


def gate(key, passed, **details):
    d = {'pass': passed}
    d.update(details)
    result['gates'][key] = d
    dump()


def tup(v):
    return (v.X, v.Y, v.Z)


def unit(v):
    ln = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / ln, v[1] / ln, v[2] / ln)


def within(value, target, tol=TOL):
    return abs(value - target) <= tol


def radial_about_axis(p):
    q = rel(p, CF)
    a = dot(q, N)
    return math.sqrt(max(dot(q, q) - a * a, 0.0))


# ---- Gate 1: reopen the saved family ---------------------------------------------------------------
def family_part_volumes(fdoc):
    out = {}
    for cls in (DB.FreeFormElement, DB.Extrusion):
        for el in DB.FilteredElementCollector(fdoc).OfClass(cls):
            sub = None
            try:
                sub = el.Subcategory.Name if el.Subcategory is not None else None
            except Exception:
                pass
            vol = 0.0
            for s in iter_solids(el.get_Geometry(DB.Options())):
                vol += s.Volume * 1728.0
            out[sub or ('element_%s' % el.Id.Value)] = {'class': cls.__name__, 'volume_in3': round(vol, 4),
                                                        'id': str(el.Id.Value)}
    return out


def stage_reopen(app):
    fdoc = app.OpenDocumentFile(os.path.normpath(RFA))
    S_['fdoc'] = fdoc
    g = {'file': RFA, 'file_bytes': os.path.getsize(RFA), 'is_family_document': fdoc.IsFamilyDocument}
    fam = fdoc.OwnerFamily
    g['category'] = fam.FamilyCategory.Name
    g['placement_type'] = str(fam.FamilyPlacementType)
    warns = list(fdoc.GetWarnings())
    g['warning_count'] = len(warns)
    g['warnings'] = [w.GetDescriptionText() for w in warns]
    fm = fdoc.FamilyManager
    g['type_names'] = [t.Name for t in fm.Types]
    ft = fm.CurrentType
    g['current_type'] = ft.Name if ft is not None else None
    params = {}
    for fp in fm.Parameters:
        nm = fp.Definition.Name
        item = {'instance': fp.IsInstance, 'storage': str(fp.StorageType)}
        if ft is not None:
            try:
                if nm in ('Metal Finish', 'Glass Finish'):
                    m = fdoc.GetElement(ft.AsElementId(fp))
                    item['material'] = m.Name if m is not None else None
                elif nm == 'Show Disc':
                    item['default'] = ft.AsInteger(fp)
            except Exception as ex:
                item['read_error'] = str(ex)
        params[nm] = item
    g['parameters'] = params
    ident = {}
    for label, bip in (('Manufacturer', DB.BuiltInParameter.ALL_MODEL_MANUFACTURER),
                       ('Model', DB.BuiltInParameter.ALL_MODEL_MODEL),
                       ('Description', DB.BuiltInParameter.ALL_MODEL_DESCRIPTION)):
        try:
            fp = fm.get_Parameter(bip)
            ident[label] = ft.AsString(fp) if (fp is not None and ft is not None) else None
        except Exception as ex:
            ident[label] = 'error: ' + str(ex)
    g['identity'] = ident
    vols = family_part_volumes(fdoc)
    g['parts'] = vols
    S_['family_volumes'] = vols
    try:
        ext = None
        for el in DB.FilteredElementCollector(fdoc).OfClass(DB.Extrusion):
            if el.Subcategory is not None and el.Subcategory.Name == 'Disc':
                ext = el
        vis = ext.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
        assoc = fm.GetAssociatedFamilyParameter(vis)
        g['disc_visibility_linked_to'] = assoc.Definition.Name if assoc is not None else None
    except Exception as ex:
        g['disc_visibility_link_error'] = str(ex)
    ok = (g['is_family_document'] and g['category'] == 'Lighting Fixtures' and g['placement_type'] == 'WorkPlaneBased'
          and g['warning_count'] == 0 and TYPE_NAME in g['type_names'])
    result['reopen'] = g
    gate('G1_native', ok, category=g['category'], placement_type=g['placement_type'],
         warning_count=g['warning_count'], reopened=True, type_name=g['current_type'])


# ---- project, wall and placement (Gates 2 and 3) ---------------------------------------------------
def template_candidates(app):
    out = []
    try:
        d = app.DefaultProjectTemplate
        if d and os.path.isfile(d):
            out.append(d.replace('\\', '/'))
    except Exception:
        pass
    root = 'C:/ProgramData/Autodesk/RVT 2025/Templates'
    found = []
    if os.path.isdir(root):
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if f.lower().endswith('.rte'):
                    found.append(dp.replace('\\', '/') + '/' + f)

    def score(p):
        low = p.lower()
        s = 0
        if 'imperial' in low:
            s -= 3
        if 'default' in low:
            s -= 2
        if 'architectural' in low:
            s -= 2
        if 'construction' in low:
            s -= 1
        for bad in ('structural', 'mechanical', 'electrical', 'plumbing'):
            if bad in low:
                s += 2
        return (s, p)

    found.sort(key=score)
    S_['templates_found'] = found
    for p in found:
        if p not in out:
            out.append(p)
    return out


def stage_project(app):
    tried = []
    for path in template_candidates(app)[:6]:
        item = {'template': path}
        try:
            proj = app.NewProjectDocument(path)
        except Exception as ex:
            item['error'] = str(ex)
            tried.append(item)
            continue
        wtypes = [w for w in DB.FilteredElementCollector(proj).OfClass(DB.WallType) if w.Kind == DB.WallKind.Basic]
        item['basic_wall_types'] = len(wtypes)
        tried.append(item)
        if wtypes:
            S_['proj'] = proj
            S_['template'] = path
            S_['wtypes'] = wtypes
            break
        proj.Close(False)
    result['project_templates_tried'] = tried
    proj = S_.get('proj')
    if proj is None:
        raise RuntimeError('no project template with a basic wall type could be opened')
    wtypes = S_['wtypes']
    wtypes.sort(key=lambda w: (0 if (ename(w) or '').lower().startswith('generic') else 1, w.Width))
    wt = wtypes[0]
    with Tx(proj, 'Level and wall'):
        levels = list(DB.FilteredElementCollector(proj).OfClass(DB.Level))
        if levels:
            level = sorted(levels, key=lambda l: l.Elevation)[0]
        else:
            level = DB.Level.Create(proj, 0.0)
        line = DB.Line.CreateBound(DB.XYZ(-10.0, 0.0, 0.0), DB.XYZ(10.0, 0.0, 0.0))
        wall = DB.Wall.Create(proj, line, wt.Id, level.Id, 12.0, 0.0, False, False)
        proj.Regenerate()
    refs = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)
    fref = refs[0]
    face = wall.GetGeometryObjectFromReference(fref)
    S_['wall'] = wall
    S_['fref'] = fref
    S_['face'] = face
    d = wall.Location.Curve
    along = unit(tup(d.GetEndPoint(1).Subtract(d.GetEndPoint(0))))
    S_['axes'] = {'along': along, 'vertical': (0.0, 0.0, 1.0), 'normal': unit(tup(wall.Orientation))}
    S_['face_origin_in'] = to_in(face.Origin)
    result['wall'] = {'type': ename(wt), 'width_in': round(wt.Width * 12.0, 4), 'orientation': rnd(tup(wall.Orientation)),
                      'face_normal': rnd(tup(face.FaceNormal)), 'face_origin_in': rnd(S_['face_origin_in']),
                      'level': ename(level), 'template': path}


def try_place(proj, symbol, fref, pt, wn, refdir):
    tx = Tx(proj, 'Place fixture')
    t = tx.__enter__()
    info = {'ref_direction': list(refdir)}
    inst = None
    try:
        inst = proj.Create.NewFamilyInstance(fref, pt, DB.XYZ(refdir[0], refdir[1], refdir[2]), symbol)
        proj.Regenerate()
        T = inst.GetTransform()
        info['basis_x'] = rnd(tup(T.BasisX))
        info['basis_y'] = rnd(tup(T.BasisY))
        info['basis_z'] = rnd(tup(T.BasisZ))
        info['origin_in'] = rnd(to_in(T.Origin))
        ok = T.BasisY.Z > 0.99 and abs(T.BasisZ.DotProduct(wn) - 1.0) < 1e-6
        info['upright'] = ok
    except Exception:
        info['error'] = traceback.format_exc()
        ok = False
    if ok:
        st = t.Commit()
        info['commit'] = str(st)
        return True, info, inst.Id
    t.RollBack()
    return False, info, None


def stage_place():
    proj = S_['proj']
    fdoc = S_['fdoc']
    fam = fdoc.LoadFamily(proj)
    if fam is None:
        raise RuntimeError('LoadFamily returned None')
    symbol = None
    for sid in fam.GetFamilySymbolIds():
        symbol = proj.GetElement(sid)
        break
    result['loaded_symbol'] = ename(symbol)
    with Tx(proj, 'Activate symbol'):
        if not symbol.IsActive:
            symbol.Activate()
        proj.Regenerate()
    S_['symbol'] = symbol
    wall = S_['wall']
    wn = wall.Orientation
    pt = S_['face'].Project(DB.XYZ(0.0, 0.0, 5.0)).XYZPoint
    attempts = []
    inst_id = None
    for refdir in ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)):
        ok, info, iid = try_place(proj, symbol, S_['fref'], pt, wn, refdir)
        attempts.append(info)
        if ok:
            inst_id = iid
            break
    result['placement_attempts'] = attempts
    if inst_id is None:
        raise RuntimeError('no reference direction gave an upright instance with the wall normal as its Z axis')
    inst = proj.GetElement(inst_id)
    S_['inst'] = inst
    S_['T'] = inst.GetTransform()
    p = {'host_id': str(inst.Host.Id.Value) if inst.Host is not None else None, 'wall_id': str(wall.Id.Value),
         'hosted_on_wall': inst.Host is not None and inst.Host.Id.Value == wall.Id.Value,
         'symbol': ename(symbol), 'family': ename(fam)}
    try:
        p['host_face_reference_valid'] = inst.HostFace is not None
    except Exception as ex:
        p['host_face_error'] = str(ex)
    try:
        tt = inst.GetTotalTransform()
        p['total_transform_matches'] = (tt.Origin.DistanceTo(S_['T'].Origin) < 1e-9 and
                                        tt.BasisX.DistanceTo(S_['T'].BasisX) < 1e-9 and
                                        tt.BasisY.DistanceTo(S_['T'].BasisY) < 1e-9)
    except Exception as ex:
        p['total_transform_error'] = str(ex)
    result['placement'] = p


# ---- measurement helpers ---------------------------------------------------------------------------
def solids_by_part(proj, inst):
    opts = DB.Options()
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    named = {}
    unlabeled = []
    unmatched = []
    for s in iter_solids(inst.get_Geometry(opts)):
        nm = None
        try:
            gs = proj.GetElement(s.GraphicsStyleId)
            if gs is not None and gs.GraphicsStyleCategory is not None:
                nm = gs.GraphicsStyleCategory.Name
        except Exception:
            nm = None
        if nm in PART_NAMES:
            named.setdefault(nm, []).append(s)
        else:
            unlabeled.append(s)
    labelled_by = 'graphics style'
    if unlabeled:
        vols = S_.get('family_volumes', {})
        for s in unlabeled:
            v = s.Volume * 1728.0
            best = None
            for nm in PART_NAMES:
                if nm in vols and vols[nm]['volume_in3'] > 0:
                    err = abs(v - vols[nm]['volume_in3']) / vols[nm]['volume_in3']
                    if best is None or err < best[0]:
                        best = (err, nm)
            if best is not None and best[0] < 0.05:
                named.setdefault(best[1], []).append(s)
            else:
                unmatched.append(s)
        labelled_by = 'graphics style, then volume match for %d solid(s)' % len(unlabeled)
    S_['unmatched'] = unmatched
    return named, labelled_by


def collect_points(solids):
    ep = []
    mp = []
    for s in solids:
        ep.extend(solid_edge_points(s))
        mp.extend(mesh_points(s))
    return ep, mp


def axis_extents(points):
    out = {}
    for key, v in S_['axes'].items():
        lo, hi = extent(points, v)
        out[key] = [lo, hi, round(hi - lo, 4)]
    return out


def style_names(proj, s):
    out = {'graphics_style_id': str(s.GraphicsStyleId.Value)}
    try:
        gs = proj.GetElement(s.GraphicsStyleId)
        if gs is not None:
            out['graphics_style_name'] = ename(gs)
            c = gs.GraphicsStyleCategory
            if c is not None:
                out['category'] = c.Name
                if c.Parent is not None:
                    out['parent_category'] = c.Parent.Name
    except Exception:
        out['style_error'] = traceback.format_exc()
    return out


def measure_state(label):
    proj = S_['proj']
    inst = S_['inst']
    named, how = solids_by_part(proj, inst)
    per = {}
    allp = []
    for nm in PART_NAMES:
        if nm in named:
            ep, mp = collect_points(named[nm])
            per[nm] = ep + mp
            allp.extend(per[nm])
    env = axis_extents(allp) if allp else None
    parts = {}
    for nm in per:
        parts[nm] = axis_extents(per[nm])
        parts[nm]['solids'] = len(named[nm])
        parts[nm]['faces'] = sum([s.Faces.Size for s in named[nm]])
        parts[nm]['volume_in3'] = round(sum([s.Volume for s in named[nm]]) * 1728.0, 4)
    S_.setdefault('points', {})[label] = per
    extra = []
    raw_pts = list(allp)
    for s in S_.get('unmatched', []):
        ep, mp = collect_points([s])
        raw_pts.extend(ep + mp)
        item = {'volume_in3': round(s.Volume * 1728.0, 4), 'faces': s.Faces.Size,
                'extent_along_wall': extent(ep + mp, S_['axes']['along']),
                'extent_vertical': extent(ep + mp, S_['axes']['vertical']),
                'extent_normal': extent(ep + mp, S_['axes']['normal'])}
        item.update(style_names(proj, s))
        extra.append(item)
    return {'labelled_by': how, 'envelope': env, 'parts': parts, 'parts_present': sorted(per.keys()),
            'solids_not_matched_to_a_part': extra,
            'raw_envelope_all_solids_incl_unmatched': axis_extents(raw_pts) if raw_pts else None}


def fresh_named():
    named, how = solids_by_part(S_['proj'], S_['inst'])
    return named


def set_show_disc(value):
    proj = S_['proj']
    with Tx(proj, 'Show Disc %s' % value):
        p = S_['inst'].LookupParameter('Show Disc')
        if p is None:
            raise RuntimeError('instance parameter Show Disc not found')
        p.Set(1 if value else 0)
        proj.Regenerate()


def stage_envelope():
    proj = S_['proj']
    T = S_['T']
    wall_face = dot(S_['face_origin_in'], S_['axes']['normal'])
    on = measure_state('disc_on')
    result['disc_on'] = on
    env = on['envelope']
    W, H, D = env['along'][2], env['vertical'][2], env['normal'][2]
    bp = S_['points']['disc_on'].get('Backplate')
    bp_min = min([dot(p, S_['axes']['normal']) for p in bp]) if bp else None
    bp_gap = round(bp_min - wall_face, 4) if bp_min is not None else None
    fixture_max = max([dot(p, S_['axes']['normal']) for p in S_['points']['disc_on']['Shade']])
    on_face = bp_gap is not None and abs(bp_gap) <= 0.005
    projects_out = (fixture_max - wall_face) > 5.0
    p = result['placement']
    g2 = bool(p.get('hosted_on_wall')) and on_face and projects_out
    gate('G2_hosting', g2, hosted_on_wall=p.get('hosted_on_wall'), backplate_back_face_offset_from_wall_face_in=bp_gap,
         fixture_projection_from_wall_face_in=round(fixture_max - wall_face, 4), wall_orientation=result['wall']['orientation'],
         instance_z_axis=result['placement_attempts'][-1].get('basis_z'), instance_y_axis=result['placement_attempts'][-1].get('basis_y'))

    set_show_disc(False)
    off = measure_state('disc_off')
    result['disc_off'] = off
    set_show_disc(True)
    eo = off['envelope']
    Wo, Ho, Do = eo['along'][2], eo['vertical'][2], eo['normal'][2]
    unchanged = {}
    for nm in ('Backplate', 'Body', 'Socket', 'Shade'):
        a = on['parts'].get(nm)
        b = off['parts'].get(nm)
        if a is None or b is None:
            unchanged[nm] = False
            continue
        unchanged[nm] = all([abs(a[k][i] - b[k][i]) < 1e-4 for k in ('along', 'vertical', 'normal') for i in range(3)])
    disc_gone = 'Disc' not in off['parts_present']
    g3 = (within(W, 8.00) and within(H, 7.63) and within(D, 5.50) and within(Wo, 5.25) and within(Ho, 5.25)
          and within(Do, 5.50) and disc_gone and all(unchanged.values()))
    gate('G3_envelope', g3, disc_on_in={'W_along_wall': W, 'H_vertical': H, 'D_wall_normal': D},
         disc_off_in={'W_along_wall': Wo, 'H_vertical': Ho, 'D_wall_normal': Do}, disc_absent_when_off=disc_gone,
         other_parts_unchanged_when_off=unchanged, tolerance_in=TOL,
         measured_from='instance solid edges plus tessellation vertices, projected on the wall axes',
         solids_excluded_from_envelope=on['solids_not_matched_to_a_part'],
         raw_envelope_all_solids_disc_on=on['raw_envelope_all_solids_incl_unmatched'],
         raw_envelope_note=('get_Geometry of this placed instance also returns the light-source symbol as a '
                            'solid (a 24 in sphere centred on the light, subcategory Light Source, read-only Light Source '
                            'Symbol Size = 2 ft). It is not fixture hardware and is hidden in the exported views, so the '
                            'envelope is taken from the five named parts; the raw all-solids envelope is listed for transparency. '
                            'Default Options(), DetailLevel Fine, IncludeNonVisibleObjects, a view-bound Options and '
                            'get_BoundingBox(null) all include this symbol (see geometry_option_probe), so an unfiltered '
                            'envelope of this instance reads 24 in wide. Other families were not tested.'))


def stage_parts():
    T = S_['T']
    Ti = T.Inverse
    named = fresh_named()
    out = {}
    for nm in PART_NAMES:
        ss = named.get(nm)
        if not ss:
            continue
        ep, mp = collect_points(ss)
        fe = [to_in(Ti.OfPoint(V(p))) for p in ep]
        fmesh = [to_in(Ti.OfPoint(V(p))) for p in mp]
        allp = fe + fmesh
        rec = {'x': extent(allp, XV), 'y': extent(allp, YV), 'z': extent(allp, ZV)}
        rec['size_x'] = round(rec['x'][1] - rec['x'][0], 4)
        rec['size_y'] = round(rec['y'][1] - rec['y'][0], 4)
        rec['size_z'] = round(rec['z'][1] - rec['z'][0], 4)
        rec['axial_rel_cf'] = extent([rel(p, CF) for p in allp], N)
        rec['axial_length'] = round(rec['axial_rel_cf'][1] - rec['axial_rel_cf'][0], 4)
        rec['max_radius_about_axis'] = round(max([radial_about_axis(p) for p in allp]), 4)
        rec['max_diameter_about_axis'] = round(2.0 * rec['max_radius_about_axis'], 4)
        rec['edge_only_x'] = extent(fe, XV)
        rec['edge_only_max_radius_about_axis'] = round(max([radial_about_axis(p) for p in fe]), 4)
        biggest = None
        for s in ss:
            for f in s.Faces:
                if isinstance(f, DB.PlanarFace) and (biggest is None or f.Area > biggest.Area):
                    biggest = f
        if biggest is not None:
            nf = Ti.OfVector(biggest.FaceNormal)
            ang = math.degrees(math.acos(max(-1.0, min(1.0, abs(nf.Z)))))
            rec['largest_planar_face_normal_family'] = rnd(tup(nf))
            rec['largest_planar_face_tilt_from_wall_deg'] = round(ang, 3)
            rec['largest_planar_face_area_in2'] = round(biggest.Area * 144.0, 4)
        rec['solids'] = len(ss)
        rec['faces'] = sum([s.Faces.Size for s in ss])
        rec['volume_in3'] = round(sum([s.Volume for s in ss]) * 1728.0, 4)
        out[nm] = rec
    result['parts_measured_family_frame'] = out
    bp = out['Backplate']
    sh = out['Shade']
    checks = {
        'backplate_diameter_x': [bp['size_x'], 5.25, within(bp['size_x'], 5.25)],
        'backplate_diameter_y': [bp['size_y'], 5.25, within(bp['size_y'], 5.25)],
        'backplate_thickness': [bp['size_z'], 0.125, within(bp['size_z'], 0.125)],
        'shade_max_diameter': [sh['max_diameter_about_axis'], 3.50, within(sh['max_diameter_about_axis'], 3.50)],
        'shade_axial_height': [sh['axial_length'], 3.25, within(sh['axial_length'], 3.25)]}
    gate('G4_parts', all([c[2] for c in checks.values()]), checks={k: {'measured_in': v[0], 'expected_in': v[1], 'pass': v[2]}
                                                                    for k, v in checks.items()},
         note='measured in the family frame through the inverse instance transform; part sizes are also listed in parts_measured_family_frame')


# ---- Gate 5: materials -----------------------------------------------------------------------------
def face_materials(named):
    proj = S_['proj']
    out = {}
    for nm in PART_NAMES:
        ss = named.get(nm)
        if not ss:
            continue
        cnt = {}
        for s in ss:
            for f in s.Faces:
                key = 'none'
                try:
                    mid = f.MaterialElementId
                    if mid.Value != -1:
                        m = proj.GetElement(mid)
                        key = ename(m) if m is not None else 'id %s' % mid.Value
                except Exception:
                    key = 'error'
                cnt[key] = cnt.get(key, 0) + 1
        out[nm] = cnt
    return out


def stage_materials():
    proj = S_['proj']
    symbol = S_['symbol']
    before = face_materials(fresh_named())
    orig_metal = symbol.LookupParameter('Metal Finish').AsElementId()
    orig_glass = symbol.LookupParameter('Glass Finish').AsElementId()
    with Tx(proj, 'Test materials'):
        m1 = proj.GetElement(DB.Material.Create(proj, 'ZZ_TEST_METAL_RED'))
        m1.Color = DB.Color(200, 20, 20)
        m2 = proj.GetElement(DB.Material.Create(proj, 'ZZ_TEST_GLASS_BLUE'))
        m2.Color = DB.Color(20, 60, 220)
        pm = symbol.LookupParameter('Metal Finish')
        pg = symbol.LookupParameter('Glass Finish')
        pm.Set(m1.Id)
        pg.Set(m2.Id)
        proj.Regenerate()
    after = face_materials(fresh_named())
    with Tx(proj, 'Restore default materials'):
        symbol.LookupParameter('Metal Finish').Set(orig_metal)
        symbol.LookupParameter('Glass Finish').Set(orig_glass)
        proj.Regenerate()
    restored = face_materials(fresh_named())
    metal_ok = all([set(after.get(nm, {}).keys()) == set(['ZZ_TEST_METAL_RED']) for nm in ('Backplate', 'Body', 'Socket', 'Disc')])
    glass_ok = set(after.get('Shade', {}).keys()) == set(['ZZ_TEST_GLASS_BLUE'])
    default_metal_ok = all([set(before.get(nm, {}).keys()) == set(['Midnight Black']) for nm in ('Backplate', 'Body', 'Socket', 'Disc')])
    default_glass_ok = set(before.get('Shade', {}).keys()) == set(['Milk Glass'])
    gate('G5_materials', metal_ok and glass_ok and default_metal_ok and default_glass_ok,
         faces_by_material_default=before, faces_by_material_after_swap=after, faces_by_material_restored=restored,
         swapped_to={'Metal Finish': 'ZZ_TEST_METAL_RED', 'Glass Finish': 'ZZ_TEST_GLASS_BLUE'},
         metal_parts_follow_metal_finish=metal_ok, shade_follows_glass_finish=glass_ok,
         defaults_are_midnight_black_and_milk_glass=default_metal_ok and default_glass_ok)


# ---- Gate 6: light ---------------------------------------------------------------------------------
def stage_light_gate():
    fdoc = S_['fdoc']
    T = S_['T']
    g = {}
    info = read_light(fdoc)
    g['family_light'] = info
    origin_in = None
    try:
        origin_in = info['source_transform']['origin_in']
    except Exception:
        pass
    g['expected_position_in'] = rnd(LIGHT_POS)
    if origin_in is not None:
        g['measured_position_in'] = origin_in
        g['position_error_in'] = round(math.sqrt(sum([(origin_in[i] - LIGHT_POS[i]) ** 2 for i in range(3)])), 5)
    axial = dot(rel(LIGHT_POS, CF), N)
    radial = radial_about_axis(LIGHT_POS)
    inner_r = SH_R - SH_WALL
    cavity_r = math.sqrt(max(inner_r * inner_r - (axial - GLOBE_AX) ** 2, 0.0))
    g['analytic'] = {'axial_from_cut_face_in': round(axial, 4), 'radial_from_axis_in': round(radial, 4),
                     'shade_cavity_axial_range_in': [round(NECK_A, 4), round(GLOBE_AX + inner_r, 4)],
                     'cavity_radius_at_light_in': round(cavity_r, 4),
                     'inside_cavity': (NECK_A < axial < GLOBE_AX + inner_r) and radial < cavity_r}
    named = fresh_named()
    P = T.OfPoint(V(LIGHT_POS))
    if origin_in is not None:
        P = T.OfPoint(V(origin_in))
    dirs = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for k in (-1, 0, 1):
                if (i, j, k) != (0, 0, 0):
                    dirs.append(unit((i * XV[0] + j * UPV[0] + k * N[0], i * XV[1] + j * UPV[1] + k * N[1],
                                      i * XV[2] + j * UPV[2] + k * N[2])))
    opts = DB.SolidCurveIntersectionOptions()
    length = 6.0 / 12.0
    rays = []
    enclosed = True
    inside_material = False
    for d in dirs:
        dw = T.OfVector(DB.XYZ(d[0], d[1], d[2])).Normalize()
        line = DB.Line.CreateBound(P, P.Add(dw.Multiply(length)))
        best = None
        for nm in PART_NAMES:
            for s in named.get(nm, []):
                res = s.IntersectWithCurve(line, opts)
                if res is None or res.SegmentCount == 0:
                    continue
                for si in range(res.SegmentCount):
                    seg = res.GetCurveSegment(si)
                    dist = min(seg.GetEndPoint(0).DistanceTo(P), seg.GetEndPoint(1).DistanceTo(P)) * 12.0
                    if best is None or dist < best[0]:
                        best = (dist, nm)
        first = best[1] if best is not None else None
        if best is not None and best[0] < 1e-6:
            inside_material = True
        if first not in ('Shade', 'Socket'):
            enclosed = False
        rays.append({'dir_shade_frame_index': len(rays), 'first_hit': first, 'distance_in': round(best[0], 4) if best else None})
    g['rays_26'] = rays
    g['enclosed_by_shade_and_socket'] = enclosed
    g['light_start_inside_solid_material'] = inside_material
    nearest = min([r['distance_in'] for r in rays if r['distance_in'] is not None]) if rays else None
    g['nearest_wall_distance_in'] = nearest
    lt = info.get('types', [{}])
    flux = None
    try:
        ii = LT.LightFamily.GetLightFamily(fdoc).GetLightType(0).GetInitialIntensity()
        flux = {'class': ii.GetType().Name, 'wattage_W': ii.Wattage, 'efficacy_lm_per_W': ii.Efficacy}
    except Exception as ex:
        flux = {'error': str(ex)}
    g['photometrics'] = flux
    lp = []
    try:
        for p in S_['inst'].Parameters:
            n = p.Definition.Name
            if any([w in n for w in ('Light', 'Lumin', 'Wattage', 'Color', 'Efficacy', 'Flux', 'Lamp')]):
                lp.append({'name': n, 'value': pval(p)})
    except Exception as ex:
        lp.append({'error': str(ex)})
    g['placed_instance_light_parameters'] = lp
    src = []
    bic = getattr(DB.BuiltInCategory, 'OST_LightingFixtureSource', None)
    if bic is not None:
        for e in DB.FilteredElementCollector(fdoc).OfCategoryId(DB.ElementId(bic)).WhereElementIsNotElementType():
            src.append({'id': str(e.Id.Value), 'class': e.GetType().Name})
    g['light_source_elements_in_reopened_family'] = src
    on = False
    try:
        on = (flux is not None and flux.get('wattage_W', 0) > 0 and flux.get('efficacy_lm_per_W', 0) > 0)
    except Exception:
        on = False
    inside = g['analytic']['inside_cavity'] and enclosed and not inside_material and \
        (origin_in is not None and g.get('position_error_in', 1.0) < 0.02)
    g['light_on_basis'] = 'a light source element exists in the family and its initial intensity is nonzero'
    result['light_gate'] = g
    gate('G6_light', bool(on and inside and len(src) > 0),
         light_source_elements=len(src), position_in=origin_in, expected_position_in=rnd(LIGHT_POS),
         position_error_in=g.get('position_error_in'), inside_shade=inside, enclosed_all_26_rays=enclosed,
         nearest_shade_or_socket_wall_in=nearest, intensity_nonzero=on, photometrics=flux)


# ---- hosted views ----------------------------------------------------------------------------------
def make_project_view(name, dir_f, target_f, box_f, dist=60.0, keep_wall=True):
    proj = S_['proj']
    T = S_['T']
    vtype = None
    for v in DB.FilteredElementCollector(proj).OfClass(DB.ViewFamilyType):
        if v.ViewFamily == DB.ViewFamily.ThreeDimensional:
            vtype = v
            break
    view = DB.View3D.CreateIsometric(proj, vtype.Id)
    view.Name = name
    tgt = T.OfPoint(V(target_f))
    d = T.OfVector(DB.XYZ(dir_f[0], dir_f[1], dir_f[2])).Normalize()
    eye = tgt.Add(d.Multiply(dist))
    fwd = tgt.Subtract(eye).Normalize()
    right = fwd.CrossProduct(DB.XYZ.BasisZ).Normalize()
    up = right.CrossProduct(fwd).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(eye, up, fwd))
    view.DetailLevel = DB.ViewDetailLevel.Fine
    view.DisplayStyle = DB.DisplayStyle.Shading
    keep = [DB.ElementId(DB.BuiltInCategory.OST_LightingFixtures)]
    if keep_wall:
        keep.append(DB.ElementId(DB.BuiltInCategory.OST_Walls))
    for cat in proj.Settings.Categories:
        try:
            if cat.Id not in keep and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        except Exception:
            pass
    xs = []
    ys = []
    zs = []
    for x in (box_f[0], box_f[3]):
        for y in (box_f[1], box_f[4]):
            for z in (box_f[2], box_f[5]):
                c = T.OfPoint(V((x, y, z)))
                xs.append(c.X)
                ys.append(c.Y)
                zs.append(c.Z)
    region = DB.BoundingBoxXYZ()
    region.Min = DB.XYZ(min(xs), min(ys), min(zs))
    region.Max = DB.XYZ(max(xs), max(ys), max(zs))
    view.SetSectionBox(region)
    view.IsSectionBoxActive = True
    return view


HOSTED = [
    ('hosted_on_wall_front', (0.0, 0.0, 1.0), (-6.0, -5.5, -3.0, 6.0, 5.5, 6.2)),
    ('hosted_on_wall_side', (-1.0, 0.0, 0.0), (-6.0, -5.5, -3.0, 6.0, 5.5, 6.2)),
    ('hosted_on_wall_oblique', (-0.8005, -0.1822, 0.5710), (-6.0, -5.5, -3.0, 6.0, 5.5, 6.2)),
]


def stage_hosted_views():
    proj = S_['proj']
    views = {}
    with Tx(proj, 'Hosted preview views'):
        for tag, dir_f, box in HOSTED:
            views[tag] = make_project_view('Hosted ' + tag, dir_f, (0.0, 0.0, 2.7), box)
        proj.Regenerate()
    exports = {}
    for tag, dir_f, box in HOSTED:
        try:
            made = export_view(proj, views[tag], VIEWS, tag)
            exports[tag] = {'files': made, 'saved': os.path.exists(VIEWS + '/' + tag + '.png')}
        except Exception:
            exports[tag] = {'error': traceback.format_exc()}
    result['hosted_view_exports'] = exports


NODISC = [
    ('hosted_no_disc_front', (0.0, 0.0698, 0.9976), (-6.0, -5.5, -0.5, 6.0, 5.5, 6.2)),
    ('hosted_no_disc_side', (-1.0, 0.0, 0.0), (-6.0, -5.5, -0.5, 6.0, 5.5, 6.2)),
    ('hosted_no_disc_oblique', (-0.8005, -0.1822, 0.5710), (-6.0, -5.5, -0.5, 6.0, 5.5, 6.2)),
]


def stage_no_disc_views():
    # Show Disc = No on the placed instance; the wall is hidden so the views compare with the matte-white photos.
    proj = S_['proj']
    inst = S_['inst']
    nod = {}
    try:
        set_show_disc(False)
        result['no_disc_state_show_disc_value'] = inst.LookupParameter('Show Disc').AsInteger()
        nviews = {}
        with Tx(proj, 'No-disc preview views'):
            for tag, dir_f, box in NODISC:
                nviews[tag] = make_project_view('Hosted ' + tag, dir_f, (0.0, 0.0, 2.7), box, keep_wall=False)
            proj.Regenerate()
        for tag, dir_f, box in NODISC:
            try:
                made = export_view(proj, nviews[tag], VIEWS, tag)
                nod[tag] = {'files': made, 'saved': os.path.exists(VIEWS + '/' + tag + '.png')}
            except Exception:
                nod[tag] = {'error': traceback.format_exc()}
    finally:
        set_show_disc(True)
        result['show_disc_value_after_restore'] = inst.LookupParameter('Show Disc').AsInteger()
    result['no_disc_view_exports'] = nod


def stage_geometry_option_probe():
    # How an independent measurement would see the placed instance under different API options (transparency for G3).
    proj = S_['proj']
    inst = S_['inst']
    out = {}

    def raw_env(opts):
        solids = list(iter_solids(inst.get_Geometry(opts)))
        pts = []
        for s in solids:
            ep, mp = collect_points([s])
            pts.extend(ep + mp)
        return {'solid_count': len(solids), 'volumes_in3': [round(s.Volume * 1728.0, 3) for s in solids],
                'envelope_in': axis_extents(pts) if pts else None}

    def box_env(bb):
        corners = []
        for x in (bb.Min.X, bb.Max.X):
            for y in (bb.Min.Y, bb.Max.Y):
                for z in (bb.Min.Z, bb.Max.Z):
                    corners.append(to_in(bb.Transform.OfPoint(DB.XYZ(x, y, z))))
        return {'envelope_in': axis_extents(corners)}

    o = DB.Options()
    out['Options() defaults'] = raw_env(o)
    o = DB.Options()
    o.DetailLevel = DB.ViewDetailLevel.Fine
    out['Options DetailLevel=Fine'] = raw_env(o)
    o = DB.Options()
    o.DetailLevel = DB.ViewDetailLevel.Fine
    o.IncludeNonVisibleObjects = True
    out['Options Fine + IncludeNonVisibleObjects'] = raw_env(o)
    view = None
    for v in DB.FilteredElementCollector(proj).OfClass(DB.View3D):
        if ename(v) == 'Hosted hosted_on_wall_front':
            view = v
    if view is not None:
        o = DB.Options()
        o.View = view
        out['Options View = hosted 3D view (Light Source category hidden)'] = raw_env(o)
    bb = inst.get_BoundingBox(None)
    if bb is not None:
        out['instance.get_BoundingBox(null)'] = box_env(bb)
    if view is not None:
        bbv = inst.get_BoundingBox(view)
        if bbv is not None:
            out['instance.get_BoundingBox(hosted 3D view)'] = box_env(bbv)
    result['geometry_option_probe'] = out


def run_all(app):
    result['revit'] = app.VersionNumber + ' ' + app.VersionBuild
    result['rfa_exists'] = os.path.exists(RFA)
    dump()
    try:
        stage('reopen', stage_reopen, app)
        if S_.get('fdoc') is not None:
            stage('project', stage_project, app)
            if S_.get('proj') is not None:
                stage('place', stage_place)
                if S_.get('inst') is not None:
                    stage('envelope', stage_envelope)
                    stage('parts', stage_parts)
                    stage('materials', stage_materials)
                    stage('light', stage_light_gate)
                    stage('hosted_views', stage_hosted_views)
                    stage('no_disc_views', stage_no_disc_views)
                    stage('geometry_option_probe', stage_geometry_option_probe)
    finally:
        for key in ('proj', 'fdoc'):
            if S_.get(key) is not None:
                close_doc(S_[key], result.setdefault('doc_closes', []), key)
        result['gates'].setdefault('G7_fidelity', {
            'pass': None, 'note': 'visual gate, not measurable natively: judged from views/_REVIEW_compare.jpg, see README'})
        result['gates'].setdefault('G8_honesty', {
            'pass': None, 'note': 'documentation gate: every dimension is labelled published, measured or inferred in README'})
        result['all_native_gates_pass'] = all([result['gates'].get(k, {}).get('pass') is True for k in
                                               ('G1_native', 'G2_hosting', 'G3_envelope', 'G4_parts', 'G5_materials', 'G6_light')])
        dump()
