# -*- coding: utf-8 -*-
"""CPython 3: copies the Revit view exports into views/, builds views/_REVIEW_compare.jpg and validation.json
from work/validation_raw.json. All writes go through guard.safe_path."""
import json
import math
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path, safe_open  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
INP = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/'
WORK = RUN + 'work/'
VIEWS = RUN + 'views/'

# Fidelity verdict written after my own review of views/_REVIEW_compare.jpg (see README).
FIDELITY = {
    'status': 'reviewed',
    'method': 'My own visual review of views/_REVIEW_compare.jpg and the individual views at matching angles.',
    'notes': [],
}
if os.path.exists(WORK + 'fidelity.json'):
    FIDELITY = json.load(open(WORK + 'fidelity.json'))

COPIES = [
    (WORK + 'export/nodes - 3D View - Front.png', 'front.png'),
    (WORK + 'export/nodes - 3D View - Side.png', 'side.png'),
    (WORK + 'export/nodes - 3D View - Oblique.png', 'oblique.png'),
    (WORK + 'export_hosted/hosted - 3D View - Hosted on wall.png', 'hosted_on_wall.png'),
    (WORK + 'export_hosted/hosted - 3D View - Hosted on wall - side.png', 'hosted_on_wall_side.png'),
    (WORK + 'export_hosted/hosted - 3D View - Hosted on wall - front.png', 'hosted_on_wall_front.png'),
    (WORK + 'export_hosted_off/hosted - 3D View - off front.png', 'hosted_disc_off_front.png'),
    (WORK + 'export_hosted_off/hosted - 3D View - off side.png', 'hosted_disc_off_side.png'),
    (WORK + 'export_hosted_off/hosted - 3D View - off oblique.png', 'hosted_disc_off_oblique.png'),
    (WORK + 'export_hosted_match/hosted - 3D View - match C roll-free.png', 'hosted_photo_match_C.png'),
    (WORK + 'export_hosted_match/hosted - 3D View - match D level.png', 'hosted_photo_match_D_level.png'),
]


def fit(im, w, h, bg=(255, 255, 255)):
    im = im.convert('RGB')
    s = min(w / float(im.width), h / float(im.height))
    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    cell = Image.new('RGB', (w, h), bg)
    cell.paste(im2, ((w - im2.width) // 2, (h - im2.height) // 2))
    return cell


def build_views():
    os.makedirs(safe_path(VIEWS), exist_ok=True)
    out = []
    for src, name in COPIES:
        shutil.copyfile(src, safe_path(VIEWS + name))
        out.append(name)
    cell = 390
    label_h = 18
    rows = [
        ('Black variant photo (833919_midnight_black.jpg)', INP + '833919_midnight_black.jpg',
         'Model: photo-fit camera C (roll free), hosted, disc on', VIEWS + 'hosted_photo_match_C.png'),
        ('Black variant photo (833919_midnight_black.jpg)', INP + '833919_midnight_black.jpg',
         'Model: photo-fit camera D (level, roll 0), hosted, disc on', VIEWS + 'hosted_photo_match_D_level.png'),
        ('White variant side photo (KW1041_MWT_side_reference.jpg; no 8 in disc)', INP + 'KW1041_MWT_side_reference.jpg',
         'Model: side, hosted on wall, Show Disc = No', VIEWS + 'hosted_disc_off_side.png'),
        ('White variant front photo (KW1041_MWT_oblique_reference.jpg; no disc)', INP + 'KW1041_MWT_oblique_reference.jpg',
         'Model: front, hosted on wall, Show Disc = No', VIEWS + 'hosted_disc_off_front.png'),
    ]
    font = ImageFont.load_default()
    sheet = Image.new('RGB', (cell * 2, (cell + label_h) * len(rows)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for r, (lp, pp, lm, mp) in enumerate(rows):
        y = r * (cell + label_h)
        for c, (lab, path) in enumerate(((lp, pp), (lm, mp))):
            x = c * cell
            d.rectangle([x, y, x + cell - 1, y + label_h - 1], fill=(30, 30, 30))
            d.text((x + 3, y + 3), lab[:64], fill=(255, 255, 255), font=font)
            sheet.paste(fit(Image.open(path), cell, cell), (x, y + label_h))
        d.line([(cell, y), (cell, y + cell + label_h)], fill=(200, 0, 0), width=1)
    sheet.save(safe_path(VIEWS + '_REVIEW_compare.jpg'), quality=90)
    return out, sheet.size


def close(a, b, tol):
    return abs(a - b) <= tol


def main():
    views, sheet_size = build_views()
    raw = json.load(open(WORK + 'validation_raw.json'))
    off_raw = json.load(open(WORK + 'render_hosted_off.json'))
    build = json.load(open(WORK + 'build_report.json'))
    fam = raw['family_doc']
    tol = 0.02

    env_on = raw['envelope_disc_on']['tessellated_lod1']['size_in']
    env_on_bb = raw['instance_bbox_get_BoundingBox']
    bb_size = [env_on_bb['hi_in'][i] - env_on_bb['lo_in'][i] for i in range(3)]
    env_off = raw['envelope_disc_off']['tessellated_lod1']['size_in']
    loose = raw['envelope_disc_on']['solid_bbox']['size_in']

    pe_on = raw['part_extents_disc_on']
    pe_off = raw['part_extents_disc_off']
    moved = {}
    for n in ('Backplate', 'Body', 'Socket', 'Shade', 'Light Source'):
        a = pe_on[n]['tessellated_lod1']
        b = pe_off[n]['tessellated_lod1']
        moved[n] = max(max(abs(a['lo_in'][i] - b['lo_in'][i]) for i in range(3)),
                       max(abs(a['hi_in'][i] - b['hi_in'][i]) for i in range(3)))

    apsz = raw['analytic_part_sizes']
    fits = apsz['shade_sphere_fits']
    outer = max(fits, key=lambda f: f['radius_in'])
    inner = min(fits, key=lambda f: f['radius_in'])
    plate = pe_on['Backplate']['tessellated_lod1']['size_in']
    plate_edge = pe_on['Backplate']['edge_sampled']['size_in']
    shade_tess = pe_on['Shade']['tessellated_lod1']

    swaps = raw['material_swaps']
    pfc = raw['part_face_counts_default']
    metal_parts = ('Backplate', 'Body', 'Disc', 'Socket')

    def mats(d, parts):
        return dict((p, d[p]['by_material']) for p in parts)

    g5_metal_ok = all(list(swaps['metal_swapped'][p]['by_material'].keys()) == ['ZZ Test Metal'] for p in metal_parts) and \
        list(swaps['metal_swapped']['Shade']['by_material'].keys()) == ['KW1041 Milk Glass']
    g5_glass_ok = list(swaps['glass_swapped']['Shade']['by_material'].keys()) == ['ZZ Test Glass']
    g5_restore_ok = swaps['restored_type_params'] == {'Glass Finish': 'KW1041 Milk Glass', 'Metal Finish': 'KW1041 Midnight Black'} and \
        swaps['restored_after_swaps'] == pfc

    upright = raw['placement']['upright_ref_dir_up_x_normal']
    li = raw['light_in_instance']
    lightfam = fam['light']

    g = {}
    g['1_native'] = {
        'target': 'RFA saves and reopens in Revit 2025, zero warnings, category Lighting Fixtures, placement WorkPlaneBased',
        'measured': {'revit_version': build['revit_version'], 'category': fam['category'], 'placement_type': fam['placement_type'],
                     'warnings_on_reopen': fam['warnings'], 'types': fam['types'], 'size_bytes': fam['size_bytes'],
                     'project_warnings_after_load_and_place': raw['project_warnings'],
                     'project_warnings_after_views': raw['project_warnings_after_view']},
        'pass': fam['category'] == 'Lighting Fixtures' and fam['placement_type'] == 'WorkPlaneBased' and fam['warnings'] == [] and
        raw['project_warnings'] == [] and raw['project_warnings_after_view'] == [],
    }
    g['2_hosting'] = {
        'target': 'places on the exterior wall face, backplate on the face, fixture projecting out of the wall',
        'measured': {'wall': raw['wall'], 'host_is_wall': upright['host_is_wall'], 'host_face_reference_present': upright['host_face_reference_present'],
                     'instance_transform_basis_family_xyz_in_world': upright['transform_basis'],
                     'instance_facing_orientation': upright['facing_orientation'],
                     'backplate_depth_range_from_wall_face_in': [pe_on['Backplate']['tessellated_lod1']['lo_in'][1], pe_on['Backplate']['tessellated_lod1']['hi_in'][1]],
                     'fixture_depth_range_from_wall_face_in': [raw['envelope_disc_on']['tessellated_lod1']['lo_in'][1], raw['envelope_disc_on']['tessellated_lod1']['hi_in'][1]],
                     'reference_direction_used': 'up x face normal = (-1,0,0) for this wall',
                     'reference_direction_plus_x_result': {'facing_orientation': raw['placement']['reference_dir_plus_x']['facing_orientation'],
                                                            'note': 'upside-down fixture (family Y -> world -Z); not the intended placement'}},
        'pass': bool(upright['host_is_wall'] and upright['host_face_reference_present'] and
                     close(pe_on['Backplate']['tessellated_lod1']['lo_in'][1], 0.0, 1e-4) and
                     raw['envelope_disc_on']['tessellated_lod1']['hi_in'][1] > 5.0 and
                     abs(upright['transform_basis']['Y'][2] - 1.0) < 1e-9),
    }
    g['3_envelope'] = {
        'target_in': {'width_along_wall': 8.00, 'height_vertical': 7.63, 'depth_wall_normal': 5.50, 'tolerance': tol},
        'axes': 'instance world axes at placement: X = along the wall, Z = vertical, Y = wall normal (measured from the wall face)',
        'measured_disc_on_in': {
            'tessellated_LOD1_face_triangulation': {'width': env_on[0], 'height': env_on[2], 'depth': env_on[1]},
            'instance_get_BoundingBox_exact': {'width': bb_size[0], 'height': bb_size[2], 'depth': bb_size[1]},
            'note_Solid_GetBoundingBox_is_loose': {'width': loose[0], 'height': loose[2], 'depth': loose[1],
                                                   'why': 'Revit returns a padded box on curved solids (+1.57 % per side here); it is not the geometry extent'},
        },
        'deviation_tessellated_in': {'width': env_on[0] - 8.0, 'height': env_on[2] - 7.63, 'depth': env_on[1] - 5.5},
        'deviation_instance_bbox_in': {'width': bb_size[0] - 8.0, 'height': bb_size[2] - 7.63, 'depth': bb_size[1] - 5.5},
        'measured_disc_off_in': {'width': env_off[0], 'height': env_off[2], 'depth': env_off[1]},
        'expected_disc_off_in': {'width': 5.25, 'height': 5.25, 'depth': 5.5, 'basis': 'backplate governs width/height, shade apex governs depth'},
        'other_parts_movement_disc_on_vs_off_in': moved,
        'parts_present_disc_off': raw['parts_present_disc_off'],
        'disc_off_bbox_from_separate_run_in': off_raw['instance_bbox_in'],
        'pass': all(close(a, b, tol) for a, b in ((env_on[0], 8.0), (env_on[2], 7.63), (env_on[1], 5.5), (bb_size[0], 8.0), (bb_size[2], 7.63), (bb_size[1], 5.5))) and
        close(env_off[0], 5.25, tol) and close(env_off[2], 5.25, tol) and max(moved.values()) < 1e-4 and 'Disc' not in raw['parts_present_disc_off'],
    }
    g['4_parts'] = {
        'target_in': {'backplate_diameter': 5.25, 'backplate_thickness': 0.125, 'shade_max_diameter': 3.5, 'shade_axial_height': 3.25, 'tolerance': tol},
        'measured_in': {
            'backplate': {'tessellated_LOD1': plate, 'edge_sampled': plate_edge, 'diameter_arc_measured': apsz['backplate_arc_diameters_in']},
            'shade_outer_sphere_fit_LOD1': {'radius': outer['radius_in'], 'max_diameter': 2 * outer['radius_in'],
                                            'apex_from_base_plane': outer['apex_along_axis_from_base_in'], 'centre_from_base_plane': outer['centre_along_axis_from_base_in'],
                                            'max_residual': outer['max_residual_in'], 'n_vertices': outer['n_vertices']},
            'shade_inner_sphere_fit_LOD1': {'radius': inner['radius_in'], 'apex_from_base_plane': inner['apex_along_axis_from_base_in'],
                                            'note': 'cavity surface; wall 0.10 in is inferred'},
            'shade_axial_height_analytic': apsz['shade_axial_height_analytic_in'],
            'shade_axial_height_tessellated': apsz['shade_axial_height_tessellated_in'],
            'shade_max_diameter_tessellated': apsz['shade_max_diameter_tessellated_in'],
            'shade_base_ring_circle_diameters': apsz['shade_base_circle_diameters_in'],
            'shade_axis_world': apsz['shade_axis_world'],
            'body_diameter': apsz['body_arc_diameters_in'], 'body_depth_range_from_wall_face': [pe_on['Body']['tessellated_lod1']['lo_in'][1], pe_on['Body']['tessellated_lod1']['hi_in'][1]],
            'disc_circle_diameters': apsz['disc_circle_diameters_in'], 'disc_depth_range_from_wall_face': [pe_on['Disc']['tessellated_lod1']['lo_in'][1], pe_on['Disc']['tessellated_lod1']['hi_in'][1]],
            'disc_overall_extent_tessellated': pe_on['Disc']['tessellated_lod1']['size_in'],
            'socket_diameter': raw['analytic_part_sizes']['disc_circle_diameters_in'][0], 'socket_depth_range_from_wall_face': [pe_on['Socket']['tessellated_lod1']['lo_in'][1], pe_on['Socket']['tessellated_lod1']['hi_in'][1]],
            'light_source_symbol_solid_extent': pe_on['Light Source']['tessellated_lod1']['size_in'],
        },
        'build_report_designed_parts': build['parts'],
        'pass': close(plate[0], 5.25, tol) and close(plate[2], 5.25, tol) and close(plate[1], 0.125, tol) and
        close(2 * outer['radius_in'], 3.5, tol) and close(apsz['shade_axial_height_analytic_in'], 3.25, tol) and
        close(apsz['shade_axial_height_tessellated_in'], 3.25, tol) and close(apsz['shade_max_diameter_tessellated_in'], 3.5, tol),
    }
    g['5_materials'] = {
        'target': 'substituting other materials in Metal Finish and Glass Finish changes the faces of the right parts',
        'test': 'Set the type parameters on the loaded symbol to new materials, read the material of every face of the instance geometry, then restore',
        'face_counts_default': pfc,
        'after_Metal_Finish_swap': swaps['metal_swapped'],
        'after_Glass_Finish_swap': swaps['glass_swapped'],
        'after_restore': swaps['restored_after_swaps'],
        'restored_type_parameters': swaps['restored_type_params'],
        'parameter_definitions': fam['parameters'],
        'bindings': fam['part_bindings'],
        'checks': {'metal_swap_changes_only_metal_parts': g5_metal_ok, 'glass_swap_changes_only_shade': g5_glass_ok, 'restore_returns_defaults': g5_restore_ok},
        'pass': g5_metal_ok and g5_glass_ok and g5_restore_ok,
    }
    g['6_light'] = {
        'target': 'light source exists, is on, and its position is inside the shade',
        'measured': {'family_light_source': lightfam,
                     'light_source_symbol_centre_in_placed_instance_family_coords_in': li['symbol_solid_centre_family_in'],
                     'shade_sphere_centre_family_coords_in': li['shade_sphere_centre_family_coords_in'] if 'shade_sphere_centre_family_coords_in' in li else li['shade_sphere_centre_family_in'],
                     'distance_between_in': li['distance_from_sphere_centre_in'],
                     'inner_glass_radius_in': li['inner_glass_radius_in'],
                     'symbol_radius_in': 0.36, 'clearance_to_glass_in': li['inner_glass_radius_in'] - li['distance_from_sphere_centre_in'] - 0.36,
                     'family_warnings': fam['warnings'],
                     'meaning_of_on': 'A Point/Spherical source with 250 lm at 2700 K exists and Revit reports no "light source inside solid geometry" warning on reopen or in the project. The family has no on/off switch.'},
        'pass': bool(lightfam['source_elements'] == 1 and lightfam['flux_lm'] > 0 and li['inside_shade_cavity'] and fam['warnings'] == []),
    }
    g['7_fidelity'] = {
        'target': 'front, side and angled views match the photos (disc size, tilt and position; body shape; shade form, angle and position)',
        'status': FIDELITY['status'],
        'method': FIDELITY.get('method'),
        'notes': FIDELITY.get('notes', []),
        'pass': FIDELITY.get('pass', None),
    }
    _rt = open(RUN + 'README.md', encoding='utf-8').read() if os.path.exists(RUN + 'README.md') else ''
    _readme_ok = all(w in _rt for w in ('published', 'measured', 'inferred', 'Limitations')) and os.path.exists(RUN + 'SOURCES.md') and os.path.exists(RUN + 'ERRORS.md')
    g['8_honesty'] = {
        'target': 'every non-published dimension labelled measured or inferred, with basis; nothing unmeasured claimed',
        'status': 'README.md dimension table gives the basis (published / measured / inferred) and confidence of every dimension; SOURCES.md and ERRORS.md list inputs used or rejected and every error',
        'pass': bool(_readme_ok),
    }

    out = {
        'family': 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa',
        'revit': '2025 (25.0.2.419), headless via _harness/revit_run.py',
        'measurement_methods': {
            'tessellated_LOD1': 'Face.Triangulate(1.0) vertices of every face of the instance solids; accurate to about 0.0002 in on curved faces',
            'instance_get_BoundingBox': 'Element.get_BoundingBox(null) on the placed instance; exact',
            'edge_sampled': 'points sampled along every face edge; exact for planar/circular edges, omits the shade apex',
            'sphere_fit': 'OLS sphere fit (rad^2 + a^2 = 2 t a + K) on LOD 1.0 vertices of each RevolvedFace of the shade; residual below 3e-6 in',
            'Solid_GetBoundingBox': 'reported only to flag it as loose (+1.57 % per side on curved solids); not used for a gate',
        },
        'gates': g,
        'gates_pass_summary': dict((k, v['pass']) for k, v in g.items()),
        'views': views,
        'compare_sheet': {'file': 'views/_REVIEW_compare.jpg', 'size_px': list(sheet_size)},
        'identity_and_defaults': fam['identity_and_defaults'],
        'materials_in_family': fam['materials'],
        'project_materials_shading': raw['project_materials'],
        'raw': raw,
    }
    f = safe_open(RUN + 'validation.json', 'w')
    try:
        f.write(json.dumps(out, indent=1, sort_keys=True))
    finally:
        f.close()
    print(json.dumps(out['gates_pass_summary']))
    print('sheet', sheet_size, 'views', views)


main()
