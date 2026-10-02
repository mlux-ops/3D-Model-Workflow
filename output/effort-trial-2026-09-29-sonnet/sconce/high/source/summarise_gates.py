# -*- coding: utf-8 -*-
"""Plain Python 3 (not Revit): reads validation.json, evaluates each acceptance gate against its tolerance and writes the result
back into validation.json under 'gates'. Usage: python summarise_gates.py"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.normpath(os.path.join(HERE, '..', 'validation.json'))
TOL = 0.02

with open(PATH) as f:
    v = json.load(f)


def within(measured, target, tol=TOL):
    return abs(measured - target) <= tol


on = v['measure_disc_on']
off = v['measure_disc_off']
parts = on['parts']
size = on['envelope']['size_in']
gates = {}

fam = v['family']
gates['1_native'] = {
    'pass': bool(v.get('ok')) and fam['warning_count'] == 0 and fam['category'] == 'Lighting Fixtures' and fam['placement_type'] == 'WorkPlaneBased',
    'reopen_warnings': fam['warning_count'], 'project_warnings': len(v['project_warnings']), 'category': fam['category'],
    'placement_type': fam['placement_type'], 'type_name': fam['current_type']}

h = v['hosting']
gates['2_hosting'] = {
    'pass': bool(h['host_is_wall'] and h['backplate_on_face'] and h['all_solids_on_exterior_side_of_face']),
    'host_is_wall': h['host_is_wall'], 'backplate_w_range_in': h['backplate_w_range_in'], 'fixture_w_range_in': h['fixture_w_range_in'],
    'note': 'w is measured along the wall exterior face normal from the host face; 0 is the wall face'}

env_ok = within(size['W'], 8.00) and within(size['H'], 7.63) and within(size['D'], 5.50)
off_size = off['envelope']['size_in']
shift = max(v['disc_off_max_shift_of_other_parts_in'].values())
gates['3_envelope'] = {
    'pass': bool(env_ok and shift < 0.001 and off_size['W'] < size['W'] and off_size['H'] < size['H']),
    'disc_on_in': size, 'targets_in': {'W': 8.00, 'H': 7.63, 'D': 5.50}, 'tolerance_in': TOL,
    'disc_off_in': off_size, 'disc_off_max_shift_of_other_parts_in': shift,
    'note': 'Envelope excludes the Light Source proxy solid (a fixed 24 in symbol that Revit adds to instance geometry); instance get_BoundingBox includes it and reads 24 x 24 x 24 in.'}

bp = parts['Backplate']
sh = parts['Shade']
bp_d = bp['u'][1] - bp['u'][0]
bp_t = bp['w'][1] - bp['w'][0]
sh_d = sh['u'][1] - sh['u'][0]
sh_ax = sh['axis'][1] - sh['axis'][0]
gates['4_parts'] = {
    'pass': bool(within(bp_d, 5.25) and within(bp_t, 0.125) and within(sh_d, 3.50) and within(sh_ax, 3.25)),
    'backplate_diameter_in': round(bp_d, 4), 'backplate_depth_in': round(bp_t, 4), 'shade_max_diameter_in': round(sh_d, 4),
    'shade_axial_length_in': round(sh_ax, 4), 'tolerance_in': TOL,
    'all_parts': dict((k, {'u': p['u'], 'v': p['v'], 'w': p['w'], 'axis': p['axis'], 'volume_in3': p['volume_in3']}) for k, p in parts.items())}

ms = v['material_swap']
metal = ('Backplate', 'Body', 'Socket', 'Disc')


def all_in(table, names, mat):
    return all(list(table[n].keys()) == [mat] for n in names)


swap_ok = (all_in(ms['metal_finish_to_TEST_RED'], metal, 'TEST_RED') and all_in(ms['metal_finish_to_TEST_RED'], ['Shade'], 'KW1041MBK - Milk Glass')
           and all_in(ms['glass_finish_also_to_TEST_GREEN'], ['Shade'], 'TEST_GREEN') and all_in(ms['default'], metal, 'KW1041MBK - Midnight Black Metal'))
gates['5_materials'] = {
    'pass': bool(swap_ok),
    'face_counts_by_part': dict((k, p['face_count']) for k, p in parts.items()),
    'metal_finish_faces': sum(parts[n]['face_count'] for n in metal), 'glass_finish_faces': parts['Shade']['face_count'],
    'metal_finish_to_TEST_RED_changed_parts': list(metal), 'glass_finish_to_TEST_GREEN_changed_parts': ['Shade'],
    'tables': ms}

lt = fam['light']
gates['6_light'] = {
    'pass': bool(fam['light_source_param'] == 1 and lt['inside_shade_cavity'] and lt['intensity_Wattage'] == 3.0 and v['project_light']['wattage'] == 3.0),
    'family_light_source_enabled': fam['light_source_param'] == 1, 'origin_in_family_frame': lt['origin_in'], 'shade_centre_in_family_frame': lt['shade_centre_in'],
    'distance_to_shade_centre_in': lt['distance_to_shade_centre_in'], 'axial_position_from_face_in': lt['axial_position_from_face_in'],
    'inside_shade_cavity': lt['inside_shade_cavity'], 'shape': lt['shape'], 'distribution': lt['distribution'], 'wattage': lt['intensity_Wattage'],
    'efficacy_lm_per_w': lt['intensity_Efficacy'], 'colour_temperature_K': lt['color_temperature_K'], 'loss_factor': lt['loss_factor_value'],
    'project_instance_reads_wattage': v['project_light']['wattage']}

gates['7_fidelity'] = {'pass': None, 'note': 'Visual gate, reviewed by the author from views/_REVIEW_compare.jpg; result recorded in README.md (Fidelity review).'}
gates['8_honesty'] = {'pass': None, 'note': 'Every dimension is labelled published, measured or inferred in README.md (Dimension table).'}
v['gates'] = gates
v['gates_all_measured_pass'] = all(g['pass'] for k, g in gates.items() if g['pass'] is not None)
with open(PATH, 'w') as f:
    json.dump(v, f, indent=1, sort_keys=True)
print(json.dumps(dict((k, g['pass']) for k, g in gates.items())), v['gates_all_measured_pass'])
