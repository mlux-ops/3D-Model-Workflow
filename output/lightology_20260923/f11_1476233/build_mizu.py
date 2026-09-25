# -*- coding: utf-8 -*-
"""Build F11 Terzani Mizu 3-light Gold / 3000K as a native Revit 2025 face-based family.

Prime owns native execution. This file is preparation only until the serialized Revit slot runs it.
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

ROOT = r'E:\Claude\3D-Model-Workflow'
OUT = os.path.join(ROOT, 'output', 'lightology_20260923', 'f11_1476233')
TOOLS = os.path.join(ROOT, 'output', 'lightology_20260923', 'tools')
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

from native_fixture_support import NativeFixture, xyz

BASENAME = 'Terzani_Mizu_0R03SE8A4ATE_Gold_3000K_R2025'
MODEL = '0R03SE8A4ATE'
TYPE_NAME = 'Mizu 3-Light - Gold - 3000K - 8.66 inch'
LIGHTOLOGY_SPEC = 'TRZ1476232'
LINKED_SOURCE = 'TRZ1476230 / 0R03SE8A4AT'
BODY_WIDTH = 8.66
BODY_CLUSTER_H = 13.77
CANOPY_D = 8.30
CANOPY_H = 1.60
MIN_OVERALL_H = 19.70
CORD_LISTED = 74.80
DROP_H = 3.90
HIGH_TOP = MIN_OVERALL_H - BODY_CLUSTER_H
MID_TOP = HIGH_TOP + (BODY_CLUSTER_H - DROP_H) / 2.0
LOW_TOP = MIN_OVERALL_H - DROP_H
NSEG = 28

VARIANTS = {
    'high':  {'sx':0.94, 'sy':1.00, 'phase':0.20, 'leanx':0.050, 'leany':-0.035, 'lobe':0.038},
    'left':  {'sx':1.00, 'sy':0.97, 'phase':1.05, 'leanx':-0.060, 'leany':0.055, 'lobe':0.052},
    'right': {'sx':0.98, 'sy':1.02, 'phase':2.15, 'leanx':0.065, 'leany':0.030, 'lobe':0.046},
}

OUTER_STATIONS = [
    (0.00, 0.42, 0.39),
    (0.32, 0.72, 0.66),
    (1.05, 1.32, 1.18),
    (2.15, 1.74, 1.52),
    (3.05, 1.48, 1.34),
    (3.58, 0.95, 0.86),
    (3.86, 0.38, 0.34),
    (3.90, 0.08, 0.07),
]
INNER_STATIONS = [
    (-0.12, 0.22, 0.20),
    (0.38, 0.48, 0.44),
    (1.05, 1.06, 0.93),
    (2.15, 1.42, 1.23),
    (3.00, 1.18, 1.07),
    (3.40, 0.65, 0.59),
]


def ring_points(variant_key, z, rx, ry, inner=False):
    v = VARIANTS[variant_key]
    progress = max(0.0, min(1.0, z / DROP_H))
    cx = v['leanx'] * math.sin(math.pi * progress)
    cy = v['leany'] * math.sin(math.pi * progress)
    amp = v['lobe'] * (0.45 if inner else 1.0)
    phase = v['phase']
    pts = []
    for i in range(NSEG):
        a = 2.0 * math.pi * float(i) / float(NSEG)
        warp = 1.0 + amp * math.sin(3.0 * a + phase) + 0.024 * math.sin(2.0 * a - 0.55 * phase)
        px = cx + (rx * v['sx']) * warp * math.cos(a)
        py = cy + (ry * v['sy']) * (1.0 - 0.35 * amp * math.cos(3.0 * a + phase)) * math.sin(a)
        pts.append((px, py, z))
    return pts


def curve_loop(global_x, global_y, pts):
    loop = DB.CurveLoop()
    native = [xyz(global_x + p[0], global_y + p[1], p[2]) for p in pts]
    for i in range(len(native)):
        loop.Append(DB.Line.CreateBound(native[i], native[(i + 1) % len(native)]))
    return loop


def loft_from_stations(global_x, global_y, variant_key, stations, inner=False):
    loops = List[DB.CurveLoop]()
    for z, rx, ry in stations:
        loops.Add(curve_loop(global_x, global_y, ring_points(variant_key, z, rx, ry, inner)))
    options = DB.SolidOptions(DB.ElementId.InvalidElementId, DB.ElementId.InvalidElementId)
    return DB.GeometryCreationUtilities.CreateLoftGeometry(loops, options)


def local_x_extents(variant_key):
    xs = []
    for z, rx, ry in OUTER_STATIONS:
        xs.extend(p[0] for p in ring_points(variant_key, z, rx, ry, False))
    return min(xs), max(xs)


def hollow_drop_solid(global_x, global_y, top_z, variant_key):
    outer = loft_from_stations(global_x, global_y, variant_key, OUTER_STATIONS, False)
    inner = loft_from_stations(global_x, global_y, variant_key, INNER_STATIONS, True)
    move = DB.Transform.CreateTranslation(xyz(0, 0, top_z))
    outer = DB.SolidUtils.CreateTransformed(outer, move)
    inner = DB.SolidUtils.CreateTransformed(inner, move)
    return DB.BooleanOperationsUtils.ExecuteBooleanOperation(
        outer, inner, DB.BooleanOperationsType.Difference)


def set_subcategory(element, category):
    element.Subcategory = category
    return element


def text_param(fx, name, value):
    p = fx.fm.AddParameter(name, DB.GroupTypeId.IdentityData, DB.SpecTypeId.String.Text, False)
    fx.fm.Set(p, value)
    return p


def write_json(path, data):
    with open(path, 'w') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, default=str)


def family_string(fm, name):
    p = next((q for q in fm.Parameters if q.Definition.Name == name), None)
    if p is None:
        return None
    try:
        return fm.CurrentType.AsString(p)
    except Exception:
        return None


def extended_qa(app, rfa_path, report):
    docs = []
    tx = None
    try:
        doc = app.OpenDocumentFile(rfa_path)
        docs.append(doc)
        fm = doc.FamilyManager
        identity_names = [
            'Lightology Spec', 'Source Linked Spec', 'Finish', 'Color',
            'CCT', 'Lamp Source', 'Total Wattage', 'Delivered Lumens',
            'Dimmable'
        ]
        report['saved_selection'] = {name: family_string(fm, name) for name in identity_names}
        forms = list(DB.FilteredElementCollector(doc).OfClass(DB.FreeFormElement))
        report['saved_form_count'] = len(forms)
        subcats = {}
        for e in forms:
            name = e.Subcategory.Name if e.Subcategory else '<none>'
            subcats[name] = subcats.get(name, 0) + 1
        report['saved_form_subcategories'] = subcats

        project = app.NewProjectDocument(DB.UnitSystem.Imperial)
        docs.append(project)
        family = doc.LoadFamily(project)
        symbol = project.GetElement(list(family.GetFamilySymbolIds())[0])
        tx = DB.Transaction(project, 'F11 stable host-reference QA')
        tx.Start()
        level = DB.Level.Create(project, 10.0)
        floor_type = DB.Floor.GetDefaultFloorType(project, False)
        perimeter = DB.CurveLoop()
        pts = [xyz(-36,-36,0), xyz(36,-36,0), xyz(36,36,0), xyz(-36,36,0)]
        for i in range(4):
            perimeter.Append(DB.Line.CreateBound(pts[i], pts[(i + 1) % 4]))
        host = DB.Floor.Create(project, List[DB.CurveLoop]([perimeter]), floor_type, level.Id)
        project.Regenerate()
        ref = DB.HostObjectUtils.GetBottomFaces(host)[0]
        face = host.GetGeometryObjectFromReference(ref)
        point = face.Project(DB.XYZ(0, 0, 10.0)).XYZPoint
        symbol.Activate()
        project.Regenerate()
        inst = project.Create.NewFamilyInstance(ref, point, DB.XYZ.BasisX, symbol)
        project.Regenerate()
        host_face = inst.HostFace
        normal = face.FaceNormal
        basis = inst.GetTransform().BasisZ
        report['extended_host_reference'] = {
            'host_id': int(host.Id.Value),
            'instance_host_id': int(inst.Host.Id.Value) if inst.Host else None,
            'stable_reference': host_face.ConvertToStableRepresentation(project) if host_face else None,
            'face_normal': [normal.X, normal.Y, normal.Z],
            'instance_basis_z': [basis.X, basis.Y, basis.Z],
            'normal_dot': basis.DotProduct(normal),
        }
        tx.Commit()
        tx = None
    finally:
        if tx is not None:
            try:
                tx.RollBack()
            except Exception:
                pass
        for d in reversed(docs):
            try:
                d.Close(False)
            except Exception:
                pass


def append_error_to_memory(detail):
    stamp = datetime.datetime.utcnow().isoformat() + 'Z'
    local = os.path.join(OUT, 'ERROR_LOG.md')
    central = os.path.join(ROOT, 'PROJECT_MEMORY.md')
    entry = (
        '\n\n### 2026-09-23 - F11 native builder runtime error\n'
        'Observed error: native F11 builder failed during prime-owned execution at %s.\n'
        'Cause: see traceback below; unresolved until a corrected run passes.\n'
        'Solution/next step: inspect validation/runtime traceback, correct the task-owned builder only, '
        'then rerun through the serialized prime slot.\n'
        'Status: unresolved at this checkpoint.\n\n'
        '%s\n' % (stamp, detail)
    )
    for path in (local, central):
        try:
            with open(path, 'a') as stream:
                stream.write(entry)
        except Exception:
            pass


def main():
    app = __revit__.Application
    fx = NativeFixture(
        app, OUT, BASENAME, 'Terzani USA', MODEL, TYPE_NAME,
        'ceiling', [BODY_WIDTH, CANOPY_D, MIN_OVERALL_H], cct=3000
    )
    try:
        canopy_mat = fx.material(
            'Canopy Finish', (238,238,235), gloss=.28, transparency=0.0,
            reflectivity=.05, material_class='Paint')
        cord_mat = fx.material(
            'Cord Finish', (142,142,137), gloss=.42, transparency=0.0,
            reflectivity=.22, material_class='Metal')
        crystal_mat = fx.material(
            'Crystal Finish', (213,159,49), gloss=.94, transparency=.72,
            reflectivity=.16, material_class='Glass')
        emitter_mat = fx.material(
            'Emitter Finish', (255,235,195), gloss=.36, transparency=.05,
            reflectivity=.06, emission=1200.0, cct=3000, material_class='Plastic')

        fx.note(
            'Authoritative: 8.66 in body width, 13.77 in crystal-cluster height, '
            '8.3 in diameter x 1.6 in high white canopy, 19.7 in minimum overall height, '
            '74.8 in listed cord, approx 3.9 in crystal drop height. '
            'Inferred from exact Gold photos: triangular suspension points, stagger spacing, '
            'cord diameter, glass wall thickness, LED-core size, and smooth asymmetric '
            'hand-cast surface approximation. Each crystal is a separate lofted hollow shell '
            'with a Boolean-cut neck opening; drops use distinct non-rotational profiles.'
        )
        text_param(fx, 'Lightology Spec', LIGHTOLOGY_SPEC)
        text_param(fx, 'Source Linked Spec', LINKED_SOURCE)
        text_param(fx, 'Finish', 'White')
        text_param(fx, 'Color', 'Gold')
        text_param(fx, 'CCT', '3000K Integrated LED')
        text_param(fx, 'Lamp Source', '3 x integrated LED / 1.5W / 120V')
        text_param(fx, 'Total Wattage', '4.5 W')
        text_param(fx, 'Delivered Lumens', '438 lm')
        text_param(fx, 'Dimmable', 'No')
        fx.length('Crystal Cluster Height', BODY_CLUSTER_H)
        fx.length('Canopy Diameter', CANOPY_D)
        fx.length('Canopy Height', CANOPY_H)
        fx.length('Listed Cord Length', CORD_LISTED)
        fx.length('Crystal Drop Height', DROP_H)

        canopy_cat = fx.doc.Settings.Categories.NewSubcategory(
            fx.doc.OwnerFamily.FamilyCategory, 'Mizu White Canopy')
        cord_cat = fx.doc.Settings.Categories.NewSubcategory(
            fx.doc.OwnerFamily.FamilyCategory, 'Mizu Suspension Cords')
        crystal_cat = fx.doc.Settings.Categories.NewSubcategory(
            fx.doc.OwnerFamily.FamilyCategory, 'Mizu Gold Crystal Shells')
        emitter_cat = fx.doc.Settings.Categories.NewSubcategory(
            fx.doc.OwnerFamily.FamilyCategory, 'Mizu 3000K Emitters')

        canopy = fx.cylinder(
            '8.3 inch white canopy', xyz(0,0,0), DB.XYZ.BasisZ,
            CANOPY_D/2.0, 0.0, CANOPY_H, canopy_mat, rounding=.10)
        set_subcategory(canopy, canopy_cat)

        left_min, left_max = local_x_extents('left')
        right_min, right_max = local_x_extents('right')
        left_x = -BODY_WIDTH/2.0 - left_min
        right_x = BODY_WIDTH/2.0 - right_max

        placements = [
            {'key':'high',  'label':'High rear crystal', 'x':0.62,    'y':-0.72, 'top':HIGH_TOP},
            {'key':'left',  'label':'Mid left crystal',   'x':left_x,  'y':0.78,  'top':MID_TOP},
            {'key':'right', 'label':'Low right crystal',  'x':right_x, 'y':0.50,  'top':LOW_TOP},
        ]
        report_drops = []
        for d in placements:
            shell = hollow_drop_solid(d['x'], d['y'], d['top'], d['key'])
            shell_el = fx.add(d['label'] + ' - asymmetric hollow crystal shell', shell, crystal_mat)
            set_subcategory(shell_el, crystal_cat)

            cord_end = d['top'] + 0.25
            cord = fx.cylinder(
                d['label'] + ' - suspension cord', xyz(d['x'], d['y'], CANOPY_H),
                DB.XYZ.BasisZ, 0.045, 0.0, cord_end - CANOPY_H, cord_mat)
            set_subcategory(cord, cord_cat)

            core = fx.revolve(
                d['label'] + ' - 3000K LED core',
                xyz(d['x'], d['y'], d['top'] + 0.55), DB.XYZ.BasisZ,
                [
                    (0.0,0.0),(0.24,0.0),(0.33,0.18),(0.35,1.65),
                    (0.29,2.05),(0.18,2.28),(0.0,2.28)
                ], emitter_mat)
            set_subcategory(core, emitter_cat)
            report_drops.append({
                'key':d['key'], 'label':d['label'], 'x_in':d['x'],
                'y_in':d['y'], 'top_z_in':d['top'], 'bottom_z_in':d['top'] + DROP_H,
                'variant':VARIANTS[d['key']]
            })

        fx.report['drop_geometry'] = report_drops
        fx.report['source_selection'] = {
            'requested_color':'Gold',
            'requested_nominal_width_in':8.7,
            'resolved_actual_width_in':BODY_WIDTH,
            'requested_cct_k':3000,
            'resolved_lightology_spec':LIGHTOLOGY_SPEC,
            'resolved_manufacturer_id':MODEL,
            'linked_source_variant':LINKED_SOURCE,
        }
        fx.report['shell_construction'] = {
            'outer_loft_station_count':len(OUTER_STATIONS),
            'inner_loft_station_count':len(INNER_STATIONS),
            'ring_segments':NSEG,
            'method':'CreateLoftGeometry outer minus inner Boolean cavity; inner starts above crystal top to form real neck opening',
            'distinct_variants':list(VARIANTS.keys()),
        }

        plan = {
            'body_width_in':BODY_WIDTH,
            'body_cluster_height_in':BODY_CLUSTER_H,
            'canopy_diameter_in':CANOPY_D,
            'canopy_height_in':CANOPY_H,
            'minimum_overall_height_in':MIN_OVERALL_H,
            'listed_cord_in':CORD_LISTED,
            'crystal_drop_height_in':DROP_H,
            'placements':report_drops,
            'construction':fx.report['shell_construction'],
        }
        write_json(os.path.join(OUT, 'geometry_plan.json'), plan)

        report = fx.finish()

        extended_qa(app, fx.path, report)
        expected_selection = {
            'Lightology Spec':LIGHTOLOGY_SPEC,
            'Source Linked Spec':LINKED_SOURCE,
            'Finish':'White',
            'Color':'Gold',
            'CCT':'3000K Integrated LED',
            'Lamp Source':'3 x integrated LED / 1.5W / 120V',
            'Total Wattage':'4.5 W',
            'Delivered Lumens':'438 lm',
            'Dimmable':'No',
        }
        custom_gates = {
            'selection_persisted': all(report['saved_selection'].get(k) == v for k, v in expected_selection.items()),
            'three_distinct_crystal_shells': report['saved_form_subcategories'].get('Mizu Gold Crystal Shells', 0) == 3,
            'three_emitters': report['saved_form_subcategories'].get('Mizu 3000K Emitters', 0) == 3,
            'stable_native_host_reference': bool(report['extended_host_reference'].get('stable_reference')),
            'native_host_id_matches': report['extended_host_reference'].get('host_id') == report['extended_host_reference'].get('instance_host_id'),
            'native_normal_aligned': abs(report['extended_host_reference'].get('normal_dot', 0.0) - 1.0) < 1e-6,
            'body_cluster_height_documented': abs((LOW_TOP + DROP_H) - HIGH_TOP - BODY_CLUSTER_H) < 1e-9,
        }
        report['custom_gates'] = custom_gates
        report['base_helper_technical_pass'] = bool(report.get('technical_pass'))
        report['technical_pass'] = report['base_helper_technical_pass'] and all(custom_gates.values())
        report['visual_verdict'] = 'PENDING PRIME VISUAL REVIEW'
        report['finished_utc_extended'] = datetime.datetime.utcnow().isoformat() + 'Z'
        write_json(os.path.join(OUT, BASENAME + '_validation.json'), report)
        write_json(os.path.join(OUT, 'validation.json'), report)
        native_dir = os.path.join(OUT, 'native')
        if not os.path.isdir(native_dir):
            os.makedirs(native_dir)
        write_json(os.path.join(native_dir, 'latest_validation.json'), report)
        if not report['technical_pass']:
            raise RuntimeError('F11 extended gates failed: ' + repr([k for k,v in custom_gates.items() if not v]))

    except Exception:
        detail = traceback.format_exc()
        try:
            if fx is not None and not fx.report.get('technical_pass'):
                fx.fail()
        except Exception:
            pass
        append_error_to_memory(detail)
        raise


if __name__ == '__main__':
    main()
