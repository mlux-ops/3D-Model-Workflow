"""Gate the Gola wall unit build from validation.json. Exit 0 only when every gate passes.

Underside placement (rebuilt 2026-10-02): the channel is placed on the upper cabinet's underside along
its front edge. Underside frame in the tests: run (+X), back into the box from the front face (+Y),
up into the box from the underside (+Z).
"""
import json, os, sys
RUN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN)
import wall_unit_profile as W

r = json.load(open(os.path.join(RUN, 'validation.json')))
t = r.get('tests', {})
A = W.section_area_mm2()
TONGUE = -min(p[0] for p in W.OUTER if not isinstance(p[0], str))          # 6.9 above the web
UP = [0.0, W.PROFILE_H + TONGUE]                                            # curl on the underside, tongue tip 26.9 up
SB = r.get('setback_default_mm')                                            # 19.05 = 3/4 in
def BACK(sb): return [sb, sb + 20.0]                                        # profile front face sb behind the front edge, back 20 mm deeper
def FRONT(sb): return [-(sb + 20.0), -sb]                                   # the same, mirrored in front of the edge
sb = SB if SB is not None else 0
gates = {}


def gate(n, ok, d=''): gates[n] = (bool(ok), d)
def near(a, b, tol=0.01): return a is not None and b is not None and abs(a - b) <= tol
def span(x, want, tol=0.01): return x is not None and near(x[0], want[0], tol) and near(x[1], want[1], tol)
def axis(row, key, i): return (row.get(key) or [None, None, None])[i]


gate('run complete', r.get('stage') == 'complete' and 'error' not in r, r.get('stage'))
gate('reopened line based (two-click), one type', r.get('reopened', {}).get('placement_type') == 'CurveBased' and len(r.get('reopened', {}).get('types', [])) == 1, r.get('reopened'))
gate('default Wall Setback is 3/4 in', near(SB, 19.05, 1e-9), SB)
gate('Placement Plane (origin) at profile front + setback (y = -100 + 19.05)', near(r.get('placement_plane_y_mm'), -100 + sb), r.get('placement_plane_y_mm'))
gate('Setback Datum stayed fixed at y = -1000', near(r.get('datum_y_mm'), -1000), r.get('datum_y_mm'))
a = t.get('A_level', {})
e = a.get('extents_mm')
gate('two clicks: line starts and ends at the clicks', a.get('start_ok') and a.get('end_ok'))
gate('run equals clicked length (1500)', e and near(e[0], 0) and near(e[3], 1500), e)
gate('level placement: profile 3/4 in behind the line, hanging 26.9 below the clicked plane',
     e and span([e[1], e[4]], FRONT(sb)) and span([e[2], e[5]], [-UP[1], -UP[0]]), e)
gate('volume = section area x length (1500)', a and abs(a['volume_mm3'] - A * 1500) <= 2e-3 * A * 1500, (round(a.get('volume_mm3', 0), 1), round(A * 1500, 1)))
g = t.get('A_regrip', {})
gate('end grip re-drag to 2400 follows', g and near(g['extents_mm'][3], 2400) and abs(g['volume_mm3'] - A * 2400) <= 2e-3 * A * 2400, g.get('extents_mm'))
gate('stainless material on faces', 'Gola - Brushed Stainless Finish' in t.get('materials', []), t.get('materials'))
u = t.get('underside', {})
fr = t.get('underside_frame', {})
lr, rl = u.get('left_to_right', {}), u.get('right_to_left', {})
gate('underside frame: front face y 2000, underside z -700', near(fr.get('front_face_y_mm'), 2000) and near(fr.get('underside_z_mm'), -700), fr)
gate('underside: line on the front edge, click to click', lr.get('line_mm') and [round(v, 3) for v in lr['line_mm']] == [250, 2000, -700, 1750, 2000, -700]
     and [round(v, 3) for v in rl.get('line_mm', [])] == [1750, 2000, -700, 250, 2000, -700], (lr.get('line_mm'), rl.get('line_mm')))
gate('underside placement hosted by the cabinet', lr.get('host_is_box') and rl.get('host_is_box'))
gate('underside, left->right: run = 1500', span(axis(lr, 'unflipped', 0), [0, 1500]), axis(lr, 'unflipped', 0))
gate('underside, left->right, default: front face 3/4 in behind the front edge, inside the box', span(axis(lr, 'unflipped', 1), BACK(sb)), axis(lr, 'unflipped', 1))
gate('underside, left->right, default: curl on the underside, web 20 up, tongue to 26.9', span(axis(lr, 'unflipped', 2), UP), axis(lr, 'unflipped', 2))
gate('underside, left->right, Flip Profile mirrors it in front of the edge', span(axis(lr, 'flipped', 1), FRONT(sb)) and span(axis(lr, 'flipped', 2), UP), lr.get('flipped'))
gate('underside, right->left + Flip Profile: back inside the box', span(axis(rl, 'flipped', 1), BACK(sb)) and span(axis(rl, 'flipped', 2), UP), rl.get('flipped'))
gate('underside, right->left unflipped lands in front (why Flip exists)', span(axis(rl, 'unflipped', 1), FRONT(sb)), axis(rl, 'unflipped', 1))
gate('Wall Setback 0: front face on the front edge', span(axis(lr, 'setback_0', 1), BACK(0)), axis(lr, 'setback_0', 1))
gate('Wall Setback 1 in: front face 25.4 mm behind', span(axis(lr, 'setback_1in', 1), BACK(25.4)), axis(lr, 'setback_1in', 1))
gate('Flip + Wall Setback 1 in: mirrored 25.4 mm', span(axis(lr, 'flipped_setback_1in', 1), FRONT(25.4)), axis(lr, 'flipped_setback_1in', 1))
c = t.get('cuts', {})
L = c.get('length_mm', 0)
def cutgate(label, key, want):
    row = c.get(key, {})
    gate(label, row and abs(row['removed_mm3'] - want) <= 1e-5 * max(want, 1) + 1.0 and not row.get('refused'),
         row and (round(row['removed_mm3'], 1), round(want, 1), row.get('refused')))
cutgate('underside-hosted cut, Cut Depth 20: 20 mm high, front face to 20 mm behind the set-back profile', 'box_depth_20', 20 * (sb + 20) * L)
cutgate('Cut Depth 300: full band', 'box_depth_300', 20 * (sb + 300) * L)
cutgate('flipped: cut moves with the profile (only the 3 mm lead-in stays in the box)', 'box_depth_300_flipped', 20 * 3 * L)
cutgate('reset to unflipped, Cut Depth 20: same cut again', 'box_depth_20_reset', 20 * (sb + 20) * L)
# Measured 2026-09-28: a Casework box family with "Cut with Voids When Loaded" OFF is still cut by InstanceVoidCutUtils.
cutgate('cabinet family with "Cut with Voids When Loaded" off is cut too (setting not needed)', 'blocked_box', 20 * (sb + 20) * L)
keys = ('box_depth_20', 'box_depth_300', 'box_depth_300_flipped', 'box_depth_20_reset')
gate('channel stays hosted on the cabinet it cuts (no circular chain)', all(c.get(k, {}).get('still_hosted_on_box') for k in keys))
gate('void never cuts the profile itself', all(abs(c.get(k, {}).get('profile_mm3', -1) - A * L) <= 2e-3 * A * L for k in keys),
     [round(c.get(k, {}).get('profile_mm3', 0), 1) for k in keys])
au, auf = t.get('A_level_up', {}).get('extents_mm'), t.get('A_level_up_flipped', {}).get('extents_mm')
gate('Plane Faces Up on a level: profile rises 0..26.9 above the plane', au and span([au[2], au[5]], UP) and span([au[1], au[4]], FRONT(sb)), au)
gate('Plane Faces Up + Flip on a level: mirrored across the line', auf and span([auf[2], auf[5]], UP) and span([auf[1], auf[4]], BACK(sb)), auf)
for key in ('detach_left_to_right', 'detach_right_to_left_flipped'):
    d = t.get(key, {})
    gate('%s: channel on the element it cuts is replaced by an unhosted copy on the level' % key,
         d.get('old_deleted') and d.get('new_host') == 'Level' and not d.get('refused'), (d.get('new_host'), d.get('note')))
    gate('%s: copy is identical (visible solid within 0.01 mm)' % key, d.get('box_shift_mm') is not None and d['box_shift_mm'] <= 0.01, d.get('box_shift_mm'))
    gate('%s: settings and comments carried over' % key, near(d.get('cut_depth_mm'), 30) and d.get('comments') == 'detach test', (d.get('cut_depth_mm'), d.get('comments')))
    gate('%s: then cuts exactly (Cut Depth 30)' % key, d.get('removed_mm3') is not None and abs(d['removed_mm3'] - 20 * (sb + 30) * L) <= 1.0,
         (round(d.get('removed_mm3', 0), 1), round(20 * (sb + 30) * L, 1)))
gate('family allows cut with voids and voids stayed unattached', r.get('family_form_volumes_after_voids_mm3') == r.get('family_form_volumes_mm3'))
gate('no Revit failures recorded', not r.get('revit_failures'), r.get('revit_failures'))
gate('preview written', r.get('preview') and any(f.startswith('wall_unit_section') for f in os.listdir(os.path.join(RUN, 'preview'))))
fails = 0
for n, (ok, d) in gates.items():
    print('%-4s %s  %s' % ('PASS' if ok else 'FAIL', n, d)); fails += not ok
print('\n%d gate(s) failed' % fails if fails else '\nALL %d GATES PASS' % len(gates))
sys.exit(1 if fails else 0)
