"""Gate the GolaAutoCut native test from validation_autocut.json. Exit 0 only if all pass."""
import json, os, sys

r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validation_autocut.json')))
t = r.get('tests', {})
gates = {}


def gate(n, ok, d=''): gates[n] = (bool(ok), d)


def cut_ok(row, rel=1e-5):
    return row and abs(row['removed_mm3'] - row['expected_mm3']) <= rel * max(row['expected_mm3'], 1) + 1.0


gate('run complete', r.get('stage') == 'complete' and 'error' not in r, r.get('stage'))
gate('updater registered', r.get('registered'), r.get('addin_id'))
for key, label in [('T1_horizontal_face_1500', 'horizontal Place on Face cuts the recess automatically'),
                   ('T2_regrip_2400', 'stretching to 2400 mm grows the cut'),
                   ('T3_vertical_face_1500', 'vertical Place on Face cuts the recess automatically'),
                   ('T4_unhosted_level_1500', 'unhosted (work plane) channel cuts the wall it sits in'),
                   ('T5_moved_off_wall', 'moving the channel off the wall removes the cut'),
                   ('T6_button', 'Cut Gola Recesses button cuts when the updater is off')]:
    row = t.get(key)
    gate(label, cut_ok(row), row and (round(row['removed_mm3'], 1), round(row['expected_mm3'], 1)))
gate('face placements are hosted by the wall', t.get('T1_horizontal_face_1500', {}).get('host') == 'Wall' and t.get('T3_vertical_face_1500', {}).get('host') == 'Wall')
gate('work-plane placement is not wall hosted', t.get('T4_unhosted_level_1500', {}).get('host') in (None, 'Level'), t.get('T4_unhosted_level_1500', {}).get('host'))
gate('button test started uncut (updater really off)', t.get('T6_button', {}).get('removed_before_button_mm3', -1) == 0.0)
q = dict((n, ids) for n, ids in r.get('queued_after', []))
gate('updater queued the channel on every placement/change (T1-T5)', all(q.get(n) for n in ('T1', 'T2', 'T3', 'T4', 'T5')), dict((n, q.get(n)) for n in ('T1', 'T2', 'T3', 'T4', 'T5')))
gate('nothing queued while the updater was off (T6)', not q.get('T6 place'), q.get('T6 place'))
gate('no updater failures logged', not any('FAILED' in l for l in r.get('log', [])), len(r.get('log', [])))
fails = 0
for n, (ok, d) in gates.items():
    print('%-4s %s  %s' % ('PASS' if ok else 'FAIL', n, d)); fails += not ok
print('\n%d gate(s) failed' % fails if fails else '\nALL GATES PASS')
sys.exit(1 if fails else 0)
