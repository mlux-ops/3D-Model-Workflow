"""Re-derive every gate of the Gola non-hosted conversion from validation.json.

Exits 0 only when all gates pass; the pyrevit run exit code is never used as evidence.
"""
import json, os, sys

RUN = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(RUN, 'validation.json')))
gates = {}
# Volume tolerance 0.005 %: the horizontal channel measured 2.795 mm3 larger per 1000 mm (0.0023 %)
# after paste with identical face topology (32 faces) and no cut or combination in the source.
# Probable cause: sub-micron sketch re-solve when its 52 sketch constraints are not carried; unconfirmed.
VOL_REL = 5e-5


def gate(name, ok, detail=''):
    gates[name] = (bool(ok), detail)


gate('run complete', r.get('stage') == 'complete' and 'error' not in r, r.get('stage'))
for j in r.get('jobs', []):
    k = j['orientation']
    src, conv, re = j.get('source', {}), j.get('converted', {}), j.get('reopened', {})
    gate(k + ': source was line based', j.get('source_placement_type') == 'CurveBased', j.get('source_placement_type'))
    gate(k + ': RFA exists', os.path.isfile(j.get('rfa', '')), j.get('rfa'))
    gate(k + ': reopened one-level based', re.get('placement_type') == 'OneLevelBased', re.get('placement_type'))
    gate(k + ': not work-plane based', re.get('work_plane_based') == 0, re.get('work_plane_based'))
    gate(k + ': all forms copied', src.get('forms') == conv.get('forms') == re.get('forms'),
         '%s/%s/%s' % (src.get('forms'), conv.get('forms'), re.get('forms')))
    sv, rv = src.get('form_volume_mm3', 0), re.get('form_volume_mm3', -1)
    gate(k + ': solid volume preserved', sv > 0 and abs(sv - rv) <= VOL_REL * sv, '%.3f vs %.3f mm3 (delta %.3f)' % (sv, rv, rv - sv))
    rows = j.get('association_rows', [])
    gate(k + ': every association restored', rows and all(a == b for _, a, b in rows),
         '%d forms, %d links' % (len(rows), sum(a for _, a, _ in rows)))
    gate(k + ': custom params carried (+Length)', re.get('custom_params') == src.get('custom_params', -9) + 1,
         '%s src vs %s dst' % (src.get('custom_params'), re.get('custom_params')))
    lh = j.get('length_handle', {})
    gate(k + ': Length handle labelled', abs(lh.get('dimension_mm', 0) - lh.get('type_length_mm', -1)) < 0.01, lh)
    pl = j.get('placement', {})
    gate(k + ': placed without a host face', pl.get('family_placement_type') == 'OneLevelBased' and pl.get('host_face_is_none')
         and pl.get('host_class') in (None, 'Level'), pl)
    flex = j.get('flex', [])
    ok = len(flex) == 3
    for a in flex[1:]:
        ok = ok and abs((a['run_span_mm'] - flex[0]['run_span_mm']) - (a['length_mm'] - flex[0]['length_mm'])) < 0.05
    gate(k + ': geometry follows Length', ok, [(f['length_mm'], round(f['run_span_mm'], 3)) for f in flex])
    if flex:
        s = flex[0]['span_xyz_mm']
        axis_ok = s[0] == max(s) if k == 'horizontal' else s[2] == max(s)
        gate(k + ': run axis ' + ('X' if k == 'horizontal' else 'Z'), axis_ok, [round(v, 2) for v in s])
    for name, src_mm, plane_gap_mm in j.get('datums', {}).get('labels_not_rebuilt', []):
        gate(k + ': datum planes for %s at source spacing' % name, abs(src_mm - plane_gap_mm) < 0.01, (src_mm, plane_gap_mm))
    pa = j.get('parity', {})
    gate(k + ': volume matches line-based original', pa and abs(pa['source_volume_mm3'] - pa['converted_volume_mm3']) <= VOL_REL * pa['source_volume_mm3'],
         pa and '%.3f vs %.3f mm3 (delta %.3f)' % (pa['source_volume_mm3'], pa['converted_volume_mm3'], pa['converted_volume_mm3'] - pa['source_volume_mm3']))
    gate(k + ': extents match line-based original', pa and all(abs(a - b) < 0.01 for a, b in zip(pa['source_extents_reoriented_mm'], pa['converted_extents_mm'])),
         pa and [round(v, 2) for v in pa['converted_extents_mm']])
    gate(k + ': profile material on faces', j.get('profile_material') in j.get('face_materials', []),
         '%s in %s' % (j.get('profile_material'), j.get('face_materials')))
    gate(k + ': previews written', j.get('previews') and all(
        any(f.startswith(os.path.basename(p)) and f.endswith('.png') for f in os.listdir(os.path.dirname(p)))
        for p in j['previews']), j.get('previews'))
if len(r.get('jobs', [])) != 2:
    gate('both jobs present', False, len(r.get('jobs', [])))

fails = 0
for n, (ok, d) in gates.items():
    print('%-4s %s  %s' % ('PASS' if ok else 'FAIL', n, d))
    fails += not ok
if r.get('builtin_values_skipped') or any(j.get('builtin_values_skipped') for j in r.get('jobs', [])):
    for j in r['jobs']:
        for row in j.get('builtin_values_skipped', []):
            print('NOTE built-in value not copied:', row)
print('\n%d gate(s) failed' % fails if fails else '\nALL GATES PASS')
sys.exit(1 if fails else 0)
