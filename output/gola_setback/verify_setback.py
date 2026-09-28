"""Re-derive every gate of the Gola setback build from validation.json. Exit 0 only if all pass."""
import json, os, sys

RUN = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(RUN, 'validation.json')))
SB = r.get('setback_default_mm')
gates = {}


def gate(name, ok, detail=''):
    gates[name] = (bool(ok), detail)


def near(a, b, tol=0.01):
    return a is not None and b is not None and abs(a - b) <= tol


gate('run complete', r.get('stage') == 'complete' and 'error' not in r, r.get('stage'))
gate('default setback is 3/4 in', near(SB, 19.05, 1e-9), SB)
for j in r.get('jobs', []):
    k = j['orientation']
    depth = j.get('channel_local_z_mm', [0, 0])[1]
    re = j.get('reopened', {})
    gate(k + ': RFA exists', os.path.isfile(j.get('rfa', '')), j.get('rfa'))
    gate(k + ': still line based (two-click)', j.get('source_placement_type') == 'CurveBased' and re.get('placement_type') == 'CurveBased', re.get('placement_type'))
    gate(k + ': placement plane at depth + setback', near(re.get('origin_plane_z_mm'), depth + SB), (re.get('origin_plane_z_mm'), depth + SB))
    lv = j.get('level_two_click', {})
    gate(k + ': start and end are the clicked points', lv.get('start_matches_click') and lv.get('end_matches_click'), lv.get('clicked_length_mm'))
    L = lv.get('clicked_length_mm')
    rows = lv.get('setback_rows', [])
    ok = len(rows) == 3
    for row in rows:
        ok = ok and near(row['front_below_plane_mm'], row['setback_mm']) and near(row['back_below_plane_mm'], row['setback_mm'] + depth) \
            and near(row['run_mm'][0], 0) and near(row['run_mm'][1], L)
    gate(k + ': front face at setback (0, 3/4, 1 in) and run = clicked length', ok,
         [(row['setback_mm'], round(row['front_below_plane_mm'], 3), [round(v, 3) for v in row['run_mm']]) for row in rows])
    gate(k + ': endpoint re-grip follows', near(lv.get('regrip_run_mm', [9, 9])[0], 0) and near(lv.get('regrip_run_mm', [9, 9])[1], 2400), lv.get('regrip_run_mm'))
    gate(k + ': not hosted on a level', lv.get('host') in (None, 'Level'), lv.get('host'))
    wf = j.get('wall_face', {})
    gate(k + ': wall face - front 3/4 in inside the face', near(wf.get('front_inside_face_mm'), SB), wf.get('front_inside_face_mm'))
    gate(k + ': wall face - back at 3/4 in + depth', near(wf.get('back_inside_face_mm'), SB + depth), wf.get('back_inside_face_mm'))
    gate(k + ': wall face - run = clicked length', near(wf.get('run_mm', [9, 9])[0], 0) and near(wf.get('run_mm', [9, 9])[1], wf.get('clicked_length_mm')), wf.get('run_mm'))
    pa = j.get('parity', {})
    gate(k + ': same solid volume as source', pa and abs(pa['new_volume_mm3'] - pa['source_volume_mm3']) <= 1e-6 * pa['source_volume_mm3'],
         pa and (round(pa['new_volume_mm3'], 3), round(pa['source_volume_mm3'], 3)))
    if pa:
        exp = list(pa['source_extents_mm']); exp[2] += pa['expected_z_shift_mm']; exp[5] += pa['expected_z_shift_mm']
        gate(k + ': same solids as source, shifted only by the setback change', all(near(a, b) for a, b in zip(pa['new_extents_mm'], exp)),
             (pa['expected_z_shift_mm'], [round(v, 3) for v in pa['new_extents_mm']]))
    gate(k + ': preview written', j.get('previews') and all(os.path.isfile(p + '.png') or any(
        f.startswith(os.path.basename(p)) for f in os.listdir(os.path.dirname(p))) for p in j['previews']), j.get('previews'))
if len(r.get('jobs', [])) != 2: gate('both jobs present', False, len(r.get('jobs', [])))
fails = 0
for n, (ok, d) in gates.items():
    print('%-4s %s  %s' % ('PASS' if ok else 'FAIL', n, d)); fails += not ok
for j in r.get('jobs', []):
    print('NOTE', j['orientation'], 'wall volume cut by recess void (mm3):', j.get('wall_face', {}).get('wall_volume_removed_mm3'))
print('\n%d gate(s) failed' % fails if fails else '\nALL GATES PASS')
sys.exit(1 if fails else 0)
