r"""Independent gate verifier for the SHB_Glass Clamp 180 Square run.

`pyrevit run` exits 0 even when the hosted script raises (P01, 2026-09-18), so its
exit status is never the result. Run this afterwards and read ITS exit code:

    python verify_clamp.py          (any Python 3; run_clamp.ps1 finds one)

Standard library only. Targets come from clamp_spec.py, not from values the builder
recorded; every ray is re-compared from its raw segments, so a gate-logic bug in the
builder cannot hide a real failure.

Exit 0: complete run, every re-derived check true, RFA (< 500 KB), type catalog and
exports on disk, report newer than the runner's start stamp. Exit 1 otherwise.
A pass here is TECHNICAL only; the visual review is separate and no script awards it.
"""
import datetime
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_spec as S  # noqa: E402

RUN_DIR = os.path.normpath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN_DIR, 'validation.json')
RUN_START = os.path.join(RUN_DIR, 'logs', 'run-start.txt')
SEARCH_DEPTH = 6


def parse_utc(text):
    text = text.strip().rstrip('Z')
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('unparseable timestamp %r' % text)


def recheck_rays(label, rows, rays, add, merge=True):
    """Re-compare every recorded ray against rays computed here from clamp_spec."""
    by_key = dict((r.get('key'), r) for r in rows or [])
    for ray in rays:
        row = by_key.get(ray['key'])
        if row is None:
            add('%s: ray %s missing' % (label, ray['key']))
            continue
        if row.get('error'):
            add('%s: ray %s raised: %s' % (label, ray['key'], str(row['error']).strip().splitlines()[-1]))
            continue
        segments = [(tuple(a), tuple(b)) for a, b in row.get('segments', [])]
        ok, got, want = S.compare(ray, segments, merge=merge)
        if not ok:
            add('%s: ray %s measured %r, expected %r' % (label, ray['key'], got, want))


def elsewhere():
    """Reports or RFAs written by another copy of this kit under the user profile (bounded search)."""
    found = []
    base = os.environ.get('USERPROFILE') or os.path.expanduser('~')
    if not os.path.isdir(base):
        return found
    base_depth = base.rstrip('\\/').count(os.sep)
    for dirpath, dirs, files in os.walk(base):
        if dirpath.count(os.sep) - base_depth >= SEARCH_DEPTH:
            dirs[:] = []
        dirs[:] = [d for d in dirs if d not in ('AppData', '.git', 'node_modules')]
        if os.path.basename(dirpath) != 'glass_clamp_180' or os.path.normpath(dirpath) == RUN_DIR:
            continue
        for name in ('validation.json', S.RFA_NAME):
            if name in files:
                path = os.path.join(dirpath, name)
                found.append('%s (%d bytes)' % (path, os.path.getsize(path)))
    return found


def check(rep, run_dir=RUN_DIR, run_start=RUN_START):
    problems = []
    add = problems.append
    if rep.get('stage') != 'complete':
        add('stage is %r, expected "complete"' % rep.get('stage'))
    if rep.get('error'):
        add('builder recorded an error:\n' + str(rep['error']).strip())
    if not str(rep.get('revit_version', '')).startswith('2025'):
        add('Revit version %r, expected 2025' % rep.get('revit_version'))
    if rep.get('spec_problems') or S.check_spec():
        add('spec self-check problems: %r' % (rep.get('spec_problems') or S.check_spec()))
    if os.path.isfile(run_start):
        with open(run_start) as handle:
            start = parse_utc(handle.read())
        started = parse_utc(rep.get('started_utc', '1970-01-01T00:00:00'))
        if started < start:
            add('STALE report: builder started %s, before this run began %s' % (started, start))

    build = rep.get('build') or {}
    fam = rep.get('family') or {}
    proj = rep.get('project') or {}
    flex = rep.get('flex') or {}

    # family settings and types
    if not fam.get('reopened') or fam.get('category') != 'Generic Models':
        add('reopened=%r category=%r' % (fam.get('reopened'), fam.get('category')))
    if fam.get('always_vertical') != 1 or fam.get('work_plane_based') != 0:
        add('Always Vertical=%r Work Plane-Based=%r (want 1 / 0)' % (fam.get('always_vertical'),
                                                                   fam.get('work_plane_based')))
    if fam.get('types') != sorted(n for n, _ in S.TYPES) or fam.get('current_type') != S.DEFAULT_TYPE:
        add('types %r current %r' % (fam.get('types'), fam.get('current_type')))
    params = fam.get('parameters') or {}
    for name, kind, default, formula, source, note in S.PARAMETERS:
        row = params.get(name)
        if row is None:
            add('parameter %s missing' % name)
            continue
        if row.get('instance') is not False:
            add('parameter %s is not a type parameter' % name)
        got = (row.get('formula') or '').replace(' ', '')
        if formula and not got:
            add('parameter %s is not formula-locked (expected %r)' % (name, formula))
        elif not formula and got:
            add('parameter %s has an unexpected formula %r' % (name, row.get('formula')))
        elif formula and re.search(r'[A-Za-z_]', got.replace('"', '').replace("'", '')):
            # constants only: a parameter name here means a dependent formula, which evaluated wrongly natively
            add('parameter %s formula %r references another parameter; expected a constant' % (name, row.get('formula')))
        # constants only: the value check per type below proves the formula; Revit may reformat the text
    for type_name, glass in S.TYPES:
        values = (fam.get('type_values') or {}).get(type_name) or {}
        expected = S.resolve({'Glass_Thickness': glass})
        for name in S.LENGTH_DEFAULTS:
            got = values.get(name)
            if not isinstance(got, (int, float)) or abs(got - expected[name]) > 1e-6:
                add('type %s: %s = %r, expected %r' % (type_name, name, got, expected[name]))
        if values.get('Clamp_Material') != S.MATERIAL['name']:
            add('type %s: Clamp_Material %r' % (type_name, values.get('Clamp_Material')))
        for bip, text in S.IDENTITY.items():
            if values.get(bip) != text:
                add('type %s: %s = %r, expected %r' % (type_name, bip, values.get(bip), text))
        if values.get('Model Accuracy Notes') != S.ACCURACY_NOTE:
            add('type %s: Model Accuracy Notes differs' % type_name)

    # constraint structure
    for name in S.SPEC_PLANES + S.EXTRA_PLANES + S.SCREW_PLANES:
        if name not in (fam.get('reference_planes') or []):
            add('reference plane %r missing' % name)
    labels = fam.get('dimension_labels') or {}
    for label, count in S.LABELLED_DIMENSIONS.items():
        if labels.get(label, 0) < count:
            add('labelled dimension %s: %d found, %d expected' % (label, labels.get(label, 0), count))
    if (fam.get('equality_dimensions') or 0) < S.EQ_DIMENSIONS:
        add('EQ dimensions %r < %d' % (fam.get('equality_dimensions'), S.EQ_DIMENSIONS))
    planes_rec = build.get('planes') or {}
    expected_dims = S.DIMENSION_KEYS
    if sorted(planes_rec.get('dimensions_created') or []) != expected_dims:
        add('dimensions created %r, expected %r' % (sorted(planes_rec.get('dimensions_created') or []), expected_dims))
    for item in planes_rec.get('dimension_errors') or []:
        add('dimension problem: %s' % item)
    for item in rep.get('build_errors') or []:
        tail = str(item.get('error', '')).strip().splitlines()[-1:] 
        add('build step %r failed: %s' % (item.get('step'), ' '.join(tail)))
    parts_build = build.get('parts') or {}
    locked = sum(1 for k in ('plate_front', 'plate_back')
                 for r in (parts_build.get(k) or {}).get('side_locks', []) if r.get('locked') is True)
    if locked < S.MIN_LOCKED_ALIGNMENTS:
        add('plate side faces locked: %d of %d' % (locked, S.MIN_LOCKED_ALIGNMENTS))
    cap_locks = sum(1 for k in ('cap_left', 'cap_right')
                    for r in (parts_build.get(k) or {}).get('side_locks', []) if r.get('locked') is True)
    if cap_locks < S.MIN_CAP_LOCKS:
        add('screw-head flats locked: %d of %d' % (cap_locks, S.MIN_CAP_LOCKS))

    # parts
    parts = fam.get('parts') or {}
    for key, subcat, coarse in S.PARTS:
        row = parts.get(key) or {}
        vis = row.get('visibility') or {}
        bad = []
        if not row.get('found'):
            bad.append('not found')
        if row.get('subcategory') != subcat:
            bad.append('subcategory %r' % row.get('subcategory'))
        if row.get('material_parameter') != 'Clamp_Material':
            bad.append('material parameter %r' % row.get('material_parameter'))
        want_depth = 'Plate_Thickness' if key.startswith('plate') else 'Cap_Height'
        if row.get('depth_parameter') != want_depth:
            bad.append('depth parameter %r' % row.get('depth_parameter'))
        if row.get('solids') != 1:
            bad.append('solids %r' % row.get('solids'))
        if row.get('face_materials') != [S.MATERIAL['name']]:
            bad.append('face materials %r' % row.get('face_materials'))
        if vis.get('coarse') != coarse or not all(vis.get(x) for x in
                                                  ('medium', 'fine', 'front_back', 'left_right', 'plan_rcp',
                                                   'top_bottom')):
            bad.append('visibility %r' % vis)
        if bad:
            add('part %s: %s' % (key, '; '.join(bad)))
    if fam.get('extrusion_count') != len(S.PARTS):
        add('extrusions in family %r, expected %d (no stray solids)' % (fam.get('extrusion_count'), len(S.PARTS)))

    # measurements
    recheck_rays('default', fam.get('default_rays'), S.part_rays(S.resolve()), add)
    steps = flex.get('steps') or []
    expected_steps = [(n, x) for n, xs in S.FLEX for x in xs]
    if [(s.get('parameter'), s.get('value_in')) for s in steps] != expected_steps:
        add('flex steps %r, expected %r' % ([(s.get('parameter'), s.get('value_in')) for s in steps], expected_steps))
    for step in steps:
        label = 'flex %s=%s' % (step.get('parameter'), step.get('value_in'))
        if step.get('commit_status') != 'Committed':
            add('%s: commit %r' % (label, step.get('commit_status')))
        errors = [m for m in step.get('failures', []) if m.get('severity') != 'Warning']
        if errors:
            add('%s: errors %r' % (label, errors))
        recheck_rays(label, step.get('rays'), S.part_rays(S.resolve({step.get('parameter'): step.get('value_in')})),
                     add)
    recheck_rays('after restore', flex.get('after_restore_rays'), S.part_rays(S.resolve()), add)
    if flex.get('warnings_after_flex'):
        add('warnings after flex: %r' % flex['warnings_after_flex'])

    # material
    mat = fam.get('material') or {}
    if mat.get('shading_color') != list(S.MATERIAL['color']) or mat.get('surface_pattern_none') is not True:
        add('family material %r' % mat)
    if mat.get('diffuse') != list(S.MATERIAL['color']):
        add('appearance diffuse %r, expected %r' % (mat.get('diffuse'), list(S.MATERIAL['color'])))

    # project
    if proj.get('loaded_types') != sorted(n for n, _ in S.TYPES):
        add('project types %r' % proj.get('loaded_types'))
    basis = proj.get('basis_z') or [0, 0, 0]
    if abs(basis[2] - 1.0) > 1e-9:
        add('placed instance not vertical: basis_z %r' % basis)
    recheck_rays('project 1-2', proj.get('rays_default_type'), S.project_rays(S.resolve()), add)
    recheck_rays('project 3-8', proj.get('rays_3_8_type'), S.project_rays(S.resolve({'Glass_Thickness': 0.375})), add)
    box, want = proj.get('bbox_in') or {}, S.overall_box(S.resolve())
    for corner in ('min', 'max'):
        got = box.get(corner)
        if not got or any(abs(g - w) > 0.01 for g, w in zip(got, want[corner])):
            add('project bounding box %s %r, expected %r (+-0.01)' % (corner, got, want[corner]))
    if proj.get('solids_by_detail') != {'coarse': 2, 'medium': 4, 'fine': 4}:
        add('solids by detail level %r, expected coarse 2 / medium 4 / fine 4' % proj.get('solids_by_detail'))
    sub = proj.get('material_substitution') or {}
    if sub.get('solids') != 4 or sub.get('carrying_substitute') != 4 or sub.get('restored') is not True:
        add('material substitution %r' % sub)

    # warnings, purge, file
    if 'warnings' not in fam or 'warnings' not in proj or fam['warnings'] or proj['warnings']:
        add('warnings: family %r project %r' % (fam.get('warnings'), proj.get('warnings')))
    if rep.get('captured_failures'):
        add('failures captured during build/project: %r' % rep['captured_failures'])
    if (build.get('purge') or {}).get('available') is not True:
        add('purge unused did not run: %r' % build.get('purge'))
    rfa = os.path.join(run_dir, S.RFA_NAME)
    if not os.path.isfile(rfa):
        add('RFA missing: ' + rfa)
    elif os.path.getsize(rfa) >= S.MAX_RFA_BYTES:
        add('RFA %d bytes, limit %d' % (os.path.getsize(rfa), S.MAX_RFA_BYTES))
    catalog = os.path.join(run_dir, S.CATALOG_NAME)
    if not os.path.isfile(catalog):
        add('type catalog missing: ' + catalog)
    else:
        with open(catalog, 'rb') as handle:
            if handle.read() != S.catalog_text().encode('ascii'):
                add('type catalog content differs from clamp_spec.catalog_text()')
    evidence = os.path.join(run_dir, 'evidence')
    for label, images, minimum in (('family', rep.get('family_images'), S.MIN_FAMILY_IMAGES),
                                   ('project', proj.get('images'), 1)):
        present = [i for i in images or [] if os.path.isfile(os.path.join(evidence, i.get('file', '')))
                   and os.path.getsize(os.path.join(evidence, i['file'])) > 0]
        if len(present) < minimum:
            add('%s images on disk: %d, need %d' % (label, len(present), minimum))

    failed = rep.get('failed_gates')
    if failed:
        add('builder reported failed gates: %r' % failed)
    if rep.get('technical_pass') is not True:
        add('builder technical_pass is %r' % rep.get('technical_pass'))
    return problems


def main():
    print('run folder: ' + RUN_DIR)
    if not os.path.isfile(REPORT):
        print('FAIL - no validation.json in this run folder: the builder never started inside Revit here.')
        for item in elsewhere():
            print('  found in another checkout: ' + item)
        print('  If `pyrevit run` could not start Revit, use the in-Revit button (README.md).')
        return 1
    with open(REPORT) as handle:
        try:
            rep = json.load(handle)
        except ValueError as exc:
            print('FAIL - validation.json unparseable: %s' % exc)
            return 1
    problems = check(rep)
    if problems:
        print('TECHNICAL FAIL - %d problem(s):' % len(problems))
        for item in problems:
            print('  - ' + item)
        return 1
    print('TECHNICAL PASS - every gate re-derived from raw measurements.')
    print('Visual verdict: %s' % rep.get('visual_verdict'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
