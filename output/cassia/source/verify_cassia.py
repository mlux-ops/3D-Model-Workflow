r"""Independent gate verifier for the Cassia family run.

`pyrevit run` exits 0 even when the hosted script raises (P01, 2026-09-18), so its
exit status is never the result. Run this afterwards and read ITS exit code:

    "C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe" verify_cassia.py

Standard library only. Targets and tolerances come from cassia_geometry.py, not from
the values the builder recorded, and every pass is recomputed from the raw measurement,
so a gate-logic bug in the builder cannot hide a real failure.

Exit 0: complete run, every re-derived check true, RFA and exports on disk, report
newer than the runner's start stamp. Exit 1 otherwise. A pass here is a TECHNICAL pass;
the visual review is separate and no script awards it.
"""
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cassia_geometry as G  # noqa: E402

RUN_DIR = os.path.normpath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN_DIR, 'validation.json')
RUN_START = os.path.join(RUN_DIR, 'logs', 'run-start.txt')
KNOWN_ROOTS = [r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow',
               r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow']
RFA_NAME = 'Alora_Cassia_SF549315AGOP_Aged_Gold_Opal_R2025.rfa'
DIMENSIONS = {'Overall Diameter': G.OVERALL_DIAMETER, 'Overall Height': G.OVERALL_HEIGHT,
              'Canopy Diameter': G.CANOPY_DIAMETER, 'Canopy Height': G.CANOPY_HEIGHT,
              'Globe Diameter': G.GLOBE_DIAMETER}


def parse_utc(text):
    text = text.strip().rstrip('Z')
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('unparseable timestamp %r' % text)


def within(value, target, tol):
    return isinstance(value, (int, float)) and abs(value - target) <= tol


def elsewhere():
    """Reports or RFAs written to another known checkout (explains a 'missing' file)."""
    found = []
    for root in KNOWN_ROOTS:
        run = os.path.normpath(os.path.join(root, 'output', 'cassia'))
        if run == RUN_DIR:
            continue
        for name in ('validation.json', RFA_NAME):
            path = os.path.join(run, name)
            if os.path.isfile(path):
                stamp = datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat() + 'Z'
                found.append('%s (%d bytes, modified %s)' % (path, os.path.getsize(path), stamp))
    return found


def main():
    print('run folder: ' + RUN_DIR)
    if not os.path.isfile(REPORT):
        print('FAIL - no validation.json in this run folder: the builder never started inside Revit here.')
        other = elsewhere()
        if other:
            print('  but these were written in another checkout:')
            for item in other:
                print('    ' + item)
        else:
            print('  No Cassia report or RFA exists in the other known checkouts either.')
            print('  Most likely `pyrevit run` failed to start its own Revit (0xe06d7363 on 2026-09-23);')
            print('  use the in-Revit button instead - see README.md "If pyrevit run does not start".')
        return 1
    with open(REPORT) as handle:
        try:
            rep = json.load(handle)
        except ValueError as exc:
            print('FAIL - validation.json unparseable: %s' % exc)
            return 1
    problems = []
    add = problems.append

    if rep.get('stage') != 'complete':
        add('stage is %r, expected "complete"' % rep.get('stage'))
    if rep.get('error'):
        add('builder recorded an error:\n' + str(rep['error']).strip())
    if not str(rep.get('revit_version', '')).startswith('2025'):
        add('Revit version %r, expected 2025' % rep.get('revit_version'))
    if rep.get('profile_problems'):
        add('profile preflight problems: %r' % rep['profile_problems'])

    if os.path.isfile(RUN_START):
        with open(RUN_START) as handle:
            start = parse_utc(handle.read())
        started = parse_utc(rep.get('started_utc', '1970-01-01T00:00:00'))
        if started < start:
            add('STALE report: builder started %s, before this run began %s' % (started, start))

    fam = rep.get('family') or {}
    host = rep.get('hosted') or {}
    if not fam.get('reopened') or fam.get('category') != 'Lighting Fixtures':
        add('reopened=%r category=%r' % (fam.get('reopened'), fam.get('category')))

    parts = G.parts()
    bindings = dict((b.get('key'), b) for b in fam.get('part_bindings', []))
    for part in parts:
        b = bindings.get(part['key'])
        if not b:
            add('part %s missing from the reopened RFA' % part['key'])
            continue
        if not b.get('found') or b.get('subcategory') != part['subcategory'] \
                or b.get('material_parameter') != G.MATERIAL_PARAMETERS[part['material']]:
            add('part %s: found=%r subcategory=%r material parameter=%r' % (
                part['key'], b.get('found'), b.get('subcategory'), b.get('material_parameter')))

    rays = fam.get('rays') or {}
    for ray in G.measurement_rays():
        got = rays.get(ray['key'])
        if got is None:
            add('ray %s not recorded' % ray['key'])
        elif not within(got.get('measured'), ray['target'], ray['tol']):
            add('ray %s measured %r, target %.4f +/- %.3f%s' % (
                ray['key'], got.get('measured'), ray['target'], ray['tol'],
                ' ERROR ' + got['error'].strip().splitlines()[-1] if got.get('error') else ''))

    angles = fam.get('arm_angles_deg') or {}
    for i in range(len(G.ARM_AZIMUTHS_DEG)):
        a = angles.get('arm_%d' % i) or {}
        sections = a.get('sections')
        if not sections or len(sections) != 2:
            add('arm_%d: no section midpoints recorded' % i)
            continue
        ang = G.arm_angle_from_sections(sorted(tuple(s) for s in sections))
        if abs(ang - G.ARM_ANGLE_DEG) > G.ANGLE_TOL_DEG:
            add('arm_%d angle re-derived %.3f deg, target %.1f' % (i, ang, G.ARM_ANGLE_DEG))

    for i in range(len(G.ARM_AZIMUTHS_DEG)):
        flange = (rays.get('fitter_%d_flange_diameter' % i) or {}).get('measured')
        opening = (rays.get('globe_%d_opening_radius' % i) or {}).get('measured')
        if not isinstance(flange, (int, float)) or not isinstance(opening, (int, float)) \
                or flange / 2.0 - opening <= 0:
            add('arm_%d: fitter flange %r does not cover glass opening radius %r' % (i, flange, opening))

    clear = fam.get('internal_clearances') or []
    if len(clear) != len(G.clearance_rays()):
        add('internal clearances: %d rows, expected %d' % (len(clear), len(G.clearance_rays())))
    for row in clear:
        c = row.get('clearance_in')
        if not isinstance(c, (int, float)) or c < G.MIN_INTERNAL_CLEARANCE:
            add('clearance %s = %r (minimum %.2f)' % (row.get('key'), c, G.MIN_INTERNAL_CLEARANCE))

    saved = fam.get('saved_dimension_parameters_in') or {}
    for name, value in DIMENSIONS.items():
        if not within(saved.get(name), value, 1e-6):
            add('saved parameter %s = %r, expected %r' % (name, saved.get(name), value))

    if not host.get('hosted_on_floor'):
        add('instance is not hosted on the floor underside')
    basis = host.get('basis_z') or [0, 0, 0]
    if not within(basis[2], -1.0, 1e-6):
        add('hosted local Z = %r, expected (0, 0, -1): not hanging from the ceiling face' % (basis,))
    above = host.get('above_host_face_in')
    if not isinstance(above, (int, float)) or above > G.HOSTED_TOL:
        add('geometry extends %r in above the host face' % above)
    for i in range(len(G.ARM_AZIMUTHS_DEG)):
        drop = ((host.get('drop_in') or {}).get('globe_%d' % i) or {}).get('measured')
        if not within(drop, G.OVERALL_HEIGHT, G.HOSTED_TOL):
            add('hosted drop at globe %d = %r, expected %.3f' % (i, drop, G.OVERALL_HEIGHT))
        reach = ((host.get('spread_radius_in') or {}).get('globe_%d' % i) or {}).get('measured')
        if not within(reach, G.OVERALL_DIAMETER / 2.0, G.HOSTED_TOL):
            add('hosted spread radius at globe %d = %r, expected %.3f' % (i, reach, G.OVERALL_DIAMETER / 2.0))

    expected = G.expected_solids_per_material()
    subs = host.get('material_substitution') or {}
    for key, pname in G.MATERIAL_PARAMETERS.items():
        t = subs.get(pname)
        if not t:
            add('material substitution for %s not recorded' % pname)
            continue
        if t.get('solids_fully_carrying_substitute') != expected[key] or not t.get('restored'):
            add('%s: %r solids carried the substitute (expected %d), restored=%r' % (
                pname, t.get('solids_fully_carrying_substitute'), expected[key], t.get('restored')))

    for label, warnings in (('family', fam.get('warnings')), ('project', host.get('warnings'))):
        if warnings is None:
            add('%s warnings were never read' % label)
        elif warnings:
            add('%s warnings: %r' % (label, warnings))

    rfa = rep.get('rfa_path')
    if not rfa or not os.path.isfile(rfa):
        local = os.path.join(RUN_DIR, rep.get('rfa_name') or '')
        if not os.path.isfile(local):
            add('RFA missing on disk: %r' % rfa)
    evidence = os.path.join(RUN_DIR, 'evidence')
    fam_imgs = [i for i in rep.get('family_images', [])
                if os.path.isfile(os.path.join(evidence, i['file'])) and os.path.getsize(os.path.join(evidence, i['file']))]
    host_imgs = [i for i in host.get('images', [])
                 if os.path.isfile(os.path.join(evidence, i['file'])) and os.path.getsize(os.path.join(evidence, i['file']))]
    if len(fam_imgs) < 5:
        add('family exports on disk: %d, expected >= 5 (%r)' % (len(fam_imgs), rep.get('family_export_error')))
    if len(host_imgs) < 3:
        add('hosted exports on disk: %d, expected >= 3 (%r)' % (len(host_imgs), host.get('export_error')))

    gates = rep.get('gates') or {}
    disagree = [k for k, v in gates.items() if v is not True]
    if disagree and not problems:
        add('builder gate map reports failures the verifier did not reproduce: %r' % disagree)

    if problems:
        print('FAIL - %d problem(s):' % len(problems))
        for item in problems:
            print('  - ' + item.replace('\n', '\n    '))
        return 1
    print('TECHNICAL PASS - %d rays, %d arm angles, %d clearances, 3 hosted drops/spreads, '
          '%d material substitutions, 0 warnings.' % (len(G.measurement_rays()), len(angles), len(clear),
                                                       len(subs)))
    print('  RFA: %s (%s bytes)' % (rep.get('rfa_path'), fam.get('rfa_bytes')))
    print('  exports: %d family + %d hosted in evidence/' % (len(fam_imgs), len(host_imgs)))
    print('visual_verdict: %s' % rep.get('visual_verdict'))
    print('A technical pass is not a visual pass. Review evidence/ against references/cassia/.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
