"""Offline self-test for clamp_spec.py and verify_clamp.py (CPython 3, standard library only).

No Revit. Builds the clamp analytically (plates as boxes, screw heads as Y-axis cylinders),
fires the same rays the builder fires, assembles a report shaped like the builder's
validation.json in a temporary run folder, and checks that:
  1. the spec self-check is clean and the catalog text is well formed,
  2. the verifier passes the analytic report,
  3. the verifier rejects each tampered copy (geometry, settings, flex, file, staleness).

Proves the gate arithmetic only. It says nothing about Revit API binding or behaviour.
Exit 0 when every expectation holds.
"""
import copy
import json
import math
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_spec as S  # noqa: E402
import verify_clamp as V  # noqa: E402


def analytic_parts(v):
    yb = S.y_bands(v)
    w, h = v['Clamp_Width'], v['Clamp_Height']
    boxes = {
        'plate_front': ((-w / 2, yb['plate_front'][0], -h / 2), (w / 2, yb['plate_front'][1], h / 2)),
        'plate_back': ((-w / 2, yb['plate_back'][0], -h / 2), (w / 2, yb['plate_back'][1], h / 2)),
    }
    caps = {}
    for key, sign in (('cap_left', -1.0), ('cap_right', 1.0)):
        caps[key] = {'cx': sign * v['Cap_Offset'], 'cz': 0.0, 'r': v['Cap_Diameter'] / 2,
                     'y': yb['cap']}
    return boxes, caps


def seg_box(box, p0, p1):
    lo, hi = box
    t0, t1 = 0.0, 1.0
    for a in range(3):
        d = p1[a] - p0[a]
        if abs(d) < 1e-15:
            if not lo[a] <= p0[a] <= hi[a]:
                return []
            continue
        ta, tb = sorted(((lo[a] - p0[a]) / d, (hi[a] - p0[a]) / d))
        t0, t1 = max(t0, ta), min(t1, tb)
    if t1 <= t0:
        return []
    point = lambda t: tuple(p0[i] + t * (p1[i] - p0[i]) for i in range(3))  # noqa: E731
    return [(point(t0), point(t1))]


def seg_cyl(cap, p0, p1):
    """Axis-aligned rays only (as the builder's)."""
    axis = [i for i in range(3) if abs(p1[i] - p0[i]) > 1e-12][0]
    y0, y1 = cap['y']
    if axis == 1:
        if math.hypot(p0[0] - cap['cx'], p0[2] - cap['cz']) > cap['r']:
            return []
        return [((p0[0], y0, p0[2]), (p0[0], y1, p0[2]))]
    if not y0 <= p0[1] <= y1:
        return []
    other = 2 if axis == 0 else 0
    centre_other = cap['cz'] if other == 2 else cap['cx']
    centre_axis = cap['cx'] if axis == 0 else cap['cz']
    off = p0[other] - centre_other
    if abs(off) > cap['r']:
        return []
    half = math.sqrt(cap['r'] ** 2 - off ** 2)
    a, b = list(p0), list(p0)
    a[axis], b[axis] = centre_axis - half, centre_axis + half
    return [(tuple(a), tuple(b))]


def fire(v, part, ray):
    boxes, caps = analytic_parts(v)
    if part in boxes:
        return seg_box(boxes[part], ray['p0'], ray['p1'])
    return seg_cyl(caps[part], ray['p0'], ray['p1'])


def part_rows(v):
    rows = []
    for ray in S.part_rays(v):
        segs = fire(v, ray['part'], ray)
        ok, got, want = S.compare(ray, segs)
        rows.append({'key': ray['key'], 'segments': segs, 'measured': got, 'expected': want, 'pass': ok})
    return rows


def project_rows(v):
    rows = []
    for ray in S.project_rays(v):
        segs = []
        for key, _, _ in S.PARTS:
            segs.extend(fire(v, key, ray))
        ok, got, want = S.compare(ray, segs)
        rows.append({'key': ray['key'], 'segments': segs, 'pass': ok})
    return rows


def good_report():
    v = S.resolve()
    types = {}
    for name, glass in S.TYPES:
        row = dict(S.resolve({'Glass_Thickness': glass}))
        row['Clamp_Material'] = S.MATERIAL['name']
        row['Model Accuracy Notes'] = S.ACCURACY_NOTE
        row.update(S.IDENTITY)
        types[name] = row
    params = dict((p[0], {'instance': False, 'formula': p[3], 'shared': False}) for p in S.PARAMETERS)
    parts = {}
    for key, sub, coarse in S.PARTS:
        parts[key] = {'found': True, 'subcategory': sub, 'material_parameter': 'Clamp_Material',
                      'depth_parameter': 'Plate_Thickness' if key.startswith('plate') else 'Cap_Height',
                      'solids': 1, 'face_materials': [S.MATERIAL['name']],
                      'visibility': {'coarse': coarse, 'medium': True, 'fine': True, 'front_back': True,
                                     'left_right': True, 'plan_rcp': True, 'top_bottom': True}}
    steps = [{'parameter': n, 'value_in': x, 'commit_status': 'Committed', 'failures': [],
              'rays': part_rows(S.resolve({n: x})), 'pass': True} for n, xs in S.FLEX for x in xs]
    box = S.overall_box(v)
    return {
        'stage': 'complete', 'revit_version': '2025', 'started_utc': '2099-01-01T00:00:00Z', 'spec_problems': [],
        'build': {'planes': {'dimensions_created': list(S.DIMENSION_KEYS), 'dimension_errors': []},
                  'parts': {
            'plate_front': {'side_locks': [{'locked': True}] * 4},
            'plate_back': {'side_locks': [{'locked': True}] * 4},
            'cap_left': {'side_locks': [{'locked': True}] * 4},
            'cap_right': {'side_locks': [{'locked': True}] * 4}},
            'purge': {'available': True, 'passes': [], 'remaining_unused': 0}},
        'family': {'reopened': True, 'category': 'Generic Models', 'always_vertical': 1, 'work_plane_based': 0,
                   'types': sorted(n for n, _ in S.TYPES), 'current_type': S.DEFAULT_TYPE,
                   'type_values': types, 'parameters': params,
                   'reference_planes': sorted(S.SPEC_PLANES + S.EXTRA_PLANES + S.SCREW_PLANES + ['Center (Front/Back)']),
                   'dimension_labels': dict(S.LABELLED_DIMENSIONS), 'equality_dimensions': S.EQ_DIMENSIONS,
                   'parts': parts, 'extrusion_count': 4, 'warnings': [],
                   'material': {'shading_color': list(S.MATERIAL['color']), 'surface_pattern_none': True,
                                'diffuse': list(S.MATERIAL['color'])},
                   'default_rays': part_rows(v)},
        'flex': {'steps': steps, 'after_restore_rays': part_rows(v), 'warnings_after_flex': []},
        'project': {'loaded_types': sorted(n for n, _ in S.TYPES), 'basis_z': [0, 0, 1],
                    'rays_default_type': project_rows(v),
                    'rays_3_8_type': project_rows(S.resolve({'Glass_Thickness': 0.375})),
                    'bbox_in': {'min': list(box['min']), 'max': list(box['max'])},
                    'solids_by_detail': {'coarse': 2, 'medium': 4, 'fine': 4},
                    'material_substitution': {'solids': 4, 'carrying_substitute': 4, 'restored': True},
                    'warnings': [], 'images': [{'file': 'Clamp_Project - Placed.png', 'bytes': 10}]},
        'family_images': [{'file': 'Clamp - %d.png' % i, 'bytes': 10} for i in range(S.MIN_FAMILY_IMAGES)],
        'captured_failures': [], 'failed_gates': [], 'technical_pass': True,
    }


def make_run_dir(rep):
    run = tempfile.mkdtemp(prefix='clamp_selftest_')
    os.makedirs(os.path.join(run, 'evidence'))
    with open(os.path.join(run, S.RFA_NAME), 'wb') as fh:
        fh.write(b'x' * 1000)
    with open(os.path.join(run, S.CATALOG_NAME), 'wb') as fh:
        fh.write(S.catalog_text().encode('ascii'))
    for image in rep['family_images'] + rep['project']['images']:
        with open(os.path.join(run, 'evidence', image['file']), 'wb') as fh:
            fh.write(b'png')
    return run


def emit_fixture(run):
    """Write a passing analytic run (report, RFA stand-in, evidence) into `run`. Used only to test
    run_clamp.ps1 against a stub pyRevit in a temporary copy of the kit; never run against the real folder."""
    rep = good_report()
    os.makedirs(os.path.join(run, 'evidence'), exist_ok=True)
    with open(os.path.join(run, 'validation.json'), 'w') as fh:
        json.dump(rep, fh)
    with open(os.path.join(run, S.RFA_NAME), 'wb') as fh:
        fh.write(b'x' * 1000)
    for image in rep['family_images'] + rep['project']['images']:
        with open(os.path.join(run, 'evidence', image['file']), 'wb') as fh:
            fh.write(b'png')


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--emit-fixture':
        emit_fixture(sys.argv[2])
        return 0
    failures = []
    problems = S.check_spec()
    if problems:
        failures.append('spec self-check: %r' % problems)
    text = S.catalog_text()
    if not text.startswith(',Glass_Thickness##length##inches\r\n') or '3-8 Glass,0.375\r\n' not in text \
            or '1-2 Glass,0.5\r\n' not in text:
        failures.append('catalog text %r' % text)
    v = S.resolve()
    if abs(v['Cap_Spacing'] - 3.25) > 1e-12 or abs(v['Cap_Offset'] - 1.625) > 1e-12:
        failures.append('derived screw spacing %r' % v['Cap_Spacing'])

    rep = good_report()
    run = make_run_dir(rep)
    start = os.path.join(run, 'run-start.txt')
    with open(start, 'w') as fh:
        fh.write('2026-09-30T00:00:00')
    try:
        base = V.check(rep, run, start)
        if base:
            failures.append('verifier rejected the analytic report: %r' % base)

        def tampered(label, mutate, files=None):
            bad = copy.deepcopy(rep)
            mutate(bad)
            if files:
                files()
            found = V.check(bad, run, start)
            if not found:
                failures.append('tamper not caught: ' + label)
            return found

        def shift_segment(r):
            row = r['family']['default_rays'][0]
            (a, b) = row['segments'][0]
            row['segments'][0] = (a, (b[0], b[1] + 0.01, b[2]))
        tampered('plate 0.01 in thick', shift_segment)

        def cap_spacing_task_sheet(r):
            # screws at the task sheet's Clamp_Width - 2 in = 3 in centres
            wrong = S.resolve()
            wrong['Cap_Offset'] = 1.5
            rows = []
            for ray in S.part_rays(S.resolve()):
                wrong_ray = [x for x in S.part_rays(wrong) if x['key'] == ray['key']][0]
                segs = fire(wrong, ray['part'], wrong_ray)
                rows.append({'key': ray['key'], 'segments': segs})
            r['family']['default_rays'] = rows
        tampered('screws at 3 in centres', cap_spacing_task_sheet)
        tampered('always vertical off', lambda r: r['family'].__setitem__('always_vertical', 0))
        tampered('work plane based on', lambda r: r['family'].__setitem__('work_plane_based', 1))
        tampered('flex step missing', lambda r: r['flex']['steps'].pop())
        tampered('flex error', lambda r: r['flex']['steps'][1]['failures'].append(
            {'severity': 'Error', 'text': 'Constraints are not satisfied'}))
        tampered('coarse shows screw heads', lambda r: r['family']['parts']['cap_left']['visibility'].__setitem__(
            'coarse', True))
        tampered('screw head drifted with the plate end (the 2026-10-02 native flex failure)', lambda r: [
            row.__setitem__('segments', [((p[0] + 0.5, p[1], p[2]), (q[0] + 0.5, q[1], q[2])) for p, q in row['segments']])
            for st in r['flex']['steps'] if st['parameter'] == 'Clamp_Width'
            for row in st['rays'] if row['key'] == 'cap_left_x'])
        tampered('a screw flat not locked', lambda r: r['build']['parts']['cap_right'].__setitem__(
            'side_locks', [{'locked': True}] * 3 + [{'locked': False}]))
        tampered('Cap_Spacing value from the bad dependent formula', lambda r: [
            r['family']['type_values'][t].__setitem__('Cap_Spacing', 0.0625) for t in r['family']['type_values']])
        tampered('Cap_Diameter not formula-locked', lambda r: r['family']['parameters']['Cap_Diameter'].__setitem__(
            'formula', None))
        tampered('3/8 type wrong', lambda r: r['family']['type_values']['3-8 Glass'].__setitem__(
            'Glass_Thickness', 0.5))
        tampered('formula changed', lambda r: r['family']['parameters']['Cap_Spacing'].__setitem__(
            'formula', 'Clamp_Width - 2"'))
        tampered('project coarse 4 solids', lambda r: r['project']['solids_by_detail'].__setitem__('coarse', 4))
        tampered('warning present', lambda r: r['family']['warnings'].append('Line is slightly off axis'))
        tampered('a dimension failed (the 2026-10-02 native failure)', lambda r: (
            r['build']['planes'].__setitem__('dimensions_created', ['glass_eq'][:0]),
            r['build']['planes'].__setitem__('dimension_errors', ['glass_eq: NewDimension failed twice'])))
        tampered('build step error', lambda r: r.__setitem__(
            'build_errors', [{'step': 'create plate_front', 'error': 'Traceback\nException: boom'}]))
        tampered('stale report', lambda r: r.__setitem__('started_utc', '2020-01-01T00:00:00Z'))
        tampered('stage failed', lambda r: r.__setitem__('stage', 'failed'))

        def big_rfa():
            with open(os.path.join(run, S.RFA_NAME), 'wb') as fh:
                fh.write(b'x' * S.MAX_RFA_BYTES)
        tampered('RFA over 500 KB', lambda r: None, big_rfa)
        with open(os.path.join(run, S.RFA_NAME), 'wb') as fh:
            fh.write(b'x' * 1000)

        def bad_catalog():
            with open(os.path.join(run, S.CATALOG_NAME), 'wb') as fh:
                fh.write(b',Glass_Thickness##length##inches\n3-8 Glass,0.375\n')
        tampered('catalog LF / missing row', lambda r: None, bad_catalog)
    finally:
        shutil.rmtree(run)

    summary = {'analytic_rays_default': len(rep['family']['default_rays']),
               'flex_steps': len(rep['flex']['steps']), 'failures': failures}
    print(json.dumps(summary, indent=2))
    print('SELFTEST PASS' if not failures else 'SELFTEST FAIL')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
