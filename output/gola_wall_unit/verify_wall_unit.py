"""Gate the Gola wall unit build from validation.json. Exit 0 only when every gate passes."""
import json, os, sys
RUN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN)
import wall_unit_profile as W

r = json.load(open(os.path.join(RUN, 'validation.json')))
t = r.get('tests', {})
A = W.section_area_mm2()
TONGUE = -min(p[0] for p in W.OUTER if not isinstance(p[0], str))          # 6.9 above the line
HANG = [0.0, W.PROFILE_H + TONGUE]                                          # up-axis extent: sits above the line (leg foot on it), tongue to 26.9
OUT = [-W.DOOR_FACE_YD, 20.0 - W.DOOR_FACE_YD]                              # -19 behind the face .. +1 proud
gates = {}


def gate(n, ok, d=''): gates[n] = (bool(ok), d)
def near(a, b, tol=0.01): return a is not None and b is not None and abs(a - b) <= tol
def span(x, want, tol=0.01): return x is not None and near(x[0], want[0], tol) and near(x[1], want[1], tol)


gate('run complete', r.get('stage') == 'complete' and 'error' not in r, r.get('stage'))
gate('reopened line based (two-click), one type', r.get('reopened', {}).get('placement_type') == 'CurveBased' and len(r.get('reopened', {}).get('types', [])) == 1, r.get('reopened'))
gate('placement plane at 50 mm (door face on the clicked plane)', near(r.get('placement_plane_mm'), W.FACE_BASE_MM), r.get('placement_plane_mm'))
a = t.get('A_level', {})
gate('two clicks: line starts and ends at the clicks', a.get('start_ok') and a.get('end_ok'))
gate('run equals clicked length (1500)', a and near(a['extents_mm'][0], 0) and near(a['extents_mm'][3], 1500), a.get('extents_mm'))
gate('volume = section area x length (1500)', a and abs(a['volume_mm3'] - A * 1500) <= 2e-3 * A * 1500, (round(a.get('volume_mm3', 0), 1), round(A * 1500, 1)))
g = t.get('A_regrip', {})
gate('end grip re-drag to 2400 follows', g and near(g['extents_mm'][3], 2400) and abs(g['volume_mm3'] - A * 2400) <= 2e-3 * A * 2400, g.get('extents_mm'))
gate('stainless material on faces', 'Gola - Brushed Stainless Finish' in t.get('materials', []), t.get('materials'))
wf = t.get('wall_face', {})
lr, rl = wf.get('left_to_right', {}), wf.get('right_to_left', {})
gate('face, left->right: run = 1500', lr and span(lr['unflipped'][0], [0, 1500]), lr.get('unflipped'))
gate('face, left->right, default: sits in the 20 mm above the line (cabinet bottom), tongue up', lr and span(lr['unflipped'][1], HANG), lr.get('unflipped', [None, None])[1])
gate('face, left->right, default: 1 mm proud, 19 mm into the door', lr and span(lr['unflipped'][2], OUT), lr.get('unflipped', [None, None, None])[2])
gate('face, left->right, Flip Profile mirrors it below', lr and span(lr['flipped'][1], [-HANG[1], -HANG[0]]), lr.get('flipped', [None, None])[1])
gate('face, right->left + Flip Profile: back above the line', rl and span(rl['flipped'][1], HANG), rl.get('flipped', [None, None])[1])
gate('Door Face Offset 5 mm moves it 5 mm out', lr and span(lr['offset_5mm'][2], [OUT[0] + 5, OUT[1] + 5]), lr.get('offset_5mm', [None, None, None])[2])
gate('face placement hosted by the face element', t.get('wall_face_host') == 'Wall', t.get('wall_face_host'))
c = t.get('cuts', {})
L = c.get('length_mm', 0)
def cutgate(label, key, want):
    row = c.get(key, {})
    gate(label, row and abs(row['removed_mm3'] - want) <= 1e-5 * max(want, 1) + 1.0, row and (round(row['removed_mm3'], 1), round(want, 1)))
cutgate('cabinet box cut, Cut Depth 20: 20 x 20 mm recess', 'box_depth_20', 20 * 20 * L)
cutgate('cabinet box cut, Cut Depth 300: full band 20 x 300 mm', 'box_depth_300', 20 * 300 * L)
cutgate('flipped: cut moves with the profile (only the 1 mm overlap stays in the box)', 'box_depth_300_flipped', 1 * 300 * L)
cutgate('wall face cut: 21 x 20 mm (20 mm band + 1 mm below the line)', 'wall_face', 21 * 20 * L)
gate('void never cuts the profile itself', all(abs(c.get(k, {}).get('profile_mm3', -1) - A * L) <= 2e-3 * A * L
                                                for k in ('box_depth_20', 'box_depth_300', 'box_depth_300_flipped', 'wall_face')),
     [round(c.get(k, {}).get('profile_mm3', 0), 1) for k in ('box_depth_20', 'box_depth_300', 'box_depth_300_flipped', 'wall_face')])
bb = c.get('blocked_box', {})
# Measured 2026-09-28: a Casework box family with "Cut with Voids When Loaded" OFF is still cut by InstanceVoidCutUtils.
cutgate('cabinet family with "Cut with Voids When Loaded" off is cut too (setting not needed)', 'blocked_box', 20 * 20 * L)
gate('family allows cut with voids and voids stayed unattached', r.get('family_form_volumes_after_voids_mm3') == r.get('family_form_volumes_mm3'))
gate('preview written', r.get('preview') and any(f.startswith('wall_unit_section') for f in os.listdir(os.path.join(RUN, 'preview'))))
fails = 0
for n, (ok, d) in gates.items():
    print('%-4s %s  %s' % ('PASS' if ok else 'FAIL', n, d)); fails += not ok
print('NOTE right->left unflipped up-extent:', rl.get('unflipped', [None, None])[1])
print('\n%d gate(s) failed' % fails if fails else '\nALL GATES PASS')
sys.exit(1 if fails else 0)
