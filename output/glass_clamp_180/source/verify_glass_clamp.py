# -*- coding: utf-8 -*-
"""Independent verifier for the SHB_Glass Clamp 180 Square native build (CPython 3).

    python verify_glass_clamp.py              -> exit 0 only if every required check passes

Reads output/glass_clamp_180/validation.json plus the files on disk and RE-DERIVES every gate
from the raw measurements with clamp_geometry.py. It does not import the builder and it does
not trust the builder's own pass flags: a flag that disagrees with the verifier's result fails.
`pyrevit run` exits 0 on a crashed script, so this exit code is the result, not the runner's.

Prints the run folder first and, at the end, any clamp RFA found in the other known checkouts,
because the 2026-09-23 Cassia run left the file somewhere the user did not look.
Set GLASS_CLAMP_RUN_DIR to verify a different folder (the mock dry-run does).
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_geometry as G  # noqa: E402

RUN_DIR = os.path.normpath(os.environ.get('GLASS_CLAMP_RUN_DIR') or os.path.join(HERE, '..'))
OTHER_ROOTS = [r'C:\Users\found\OneDrive\Documents\ChatGPT\3DModelWorkflow',
               r'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow',
               r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow']
VOLUME_REL_TOL = 0.002
REQUIRED_KEYS = ['G%02d' % n for n in range(1, 30)]

results = []          # (status, name, detail)


def record(ok, name, detail='', soft=False):
    results.append(('PASS' if ok else ('WARN' if soft else 'FAIL'), name, detail))
    return ok


def compare(measured, st):
    """(worst position error in inches, worst relative volume error) vs the analytic model."""
    worst_pos, worst_vol = 0.0, 0.0
    for key, want in G.solids(st).items():
        got = measured.get(key)
        if not got or 'bounds_in' not in got:
            return 9.9, 9.9
        dev = max(abs(got['bounds_in']['y'][0] - want['y'][0]), abs(got['bounds_in']['y'][1] - want['y'][1]))
        if want['kind'] == 'plate':
            for axis in 'xz':
                dev = max(dev, abs(got['bounds_in'][axis][0] - want[axis][0]),
                          abs(got['bounds_in'][axis][1] - want[axis][1]))
        else:
            dev = max(dev, abs(got['centre_xz_in'][0] - want['cx']), abs(got['centre_xz_in'][1] - want['cz']),
                      abs(got['radius_xz_in'] - (want['x'][1] - want['x'][0]) / 2.0))
        worst_pos = max(worst_pos, dev)
        worst_vol = max(worst_vol, abs(got['volume_in3'] - want['volume']) / max(want['volume'], 1e-9))
    return worst_pos, worst_vol


def by_key(rows, forms):
    key_by_id = dict((f['id'], f['key']) for f in forms)
    return dict((key_by_id[r['id']], r['stats']) for r in rows if r['id'] in key_by_id)


def main():
    try:
        return run_checks()
    except Exception as exc:           # a malformed report is a failure, not a crash
        import traceback
        for status, name, det in results:
            print('%-4s  %s  %s' % (status, name, det if det not in ('', None) else ''))
        print('FAIL: verifier could not evaluate the report: %r' % (exc,))
        traceback.print_exc()
        return 1


def run_checks():
    print('Run folder: %s' % RUN_DIR)
    report_path = os.path.join(RUN_DIR, 'validation.json')
    if not os.path.isfile(report_path):
        print('FAIL: no validation.json - the builder did not reach its first checkpoint.')
        print('      If pyRevit printed nothing, the script did not run: use the absolute-path runner.')
        locate_elsewhere()
        return 1
    rep = json.load(open(report_path))
    print('Builder: %s  stage=%s  technical_pass=%s  revit=%s' % (
        rep.get('script_version'), rep.get('stage'), rep.get('technical_pass'), rep.get('revit_version')))
    if rep.get('error'):
        print('Builder error:\n' + rep['error'])
    record(rep.get('stage') == 'complete', 'stage complete', rep.get('stage'))
    fam = rep.get('family', {})
    record(not rep.get('stage_errors') and not rep.get('gate_error') and not rep.get('project_error'),
           'no swallowed stage errors', [e.get('stage') for e in rep.get('stage_errors', [])] +
           (['gate computation'] if rep.get('gate_error') else []) + (['project stage'] if rep.get('project_error') else []))
    record(not fam.get('errors'), 'no refused build steps (planes, dimensions, visibility)',
           [e.get('step') + ': ' + e.get('error', '')[:70] for e in fam.get('errors', [])], soft=True)
    st = G.state()
    started = rep.get('started_utc')

    # ---- files on disk
    rfa = rep.get('rfa_path')
    on_disk = bool(rfa) and os.path.isfile(rfa)
    record(on_disk, 'RFA exists on disk', rfa)
    if on_disk:
        size = os.path.getsize(rfa)
        record(size < G.FILE_SIZE_LIMIT_BYTES, 'RFA under 500 KB (measured from disk)', '%d bytes' % size)
        record(os.path.normpath(rfa).startswith(RUN_DIR), 'RFA inside the run folder', rfa)
        if started:
            fresh = datetime.datetime.utcfromtimestamp(os.path.getmtime(rfa)) >= (
                datetime.datetime.strptime(started[:19], '%Y-%m-%dT%H:%M:%S') - datetime.timedelta(seconds=5))
            record(fresh, 'RFA written during this run', started)
    cat = rep.get('catalog_path')
    record(bool(cat) and os.path.isfile(cat) and open(cat, 'rb').read().decode('ascii') == G.catalog_text(),
           'type catalog matches the specification', cat)

    fstate = fam.get('state_before_save') or {}
    reopened = rep.get('reopened') or {}
    forms = fam.get('forms', [])
    types = fstate.get('types', {})
    defaults = types.get(G.DEFAULT_TYPE, {})

    # ---- structure
    record(fstate.get('category') == 'Generic Models', 'category Generic Models', fstate.get('category'))
    record(fam.get('work_plane_based', {}).get('after') == 0, 'Work Plane-Based OFF', fam.get('work_plane_based'))
    record(fam.get('always_vertical', {}).get('after') == 1, 'Always vertical ON',
           fam.get('always_vertical'), soft=True)
    planes = fstate.get('reference_planes', {})
    want_planes = G.plane_positions(st)
    missing = [n for n in G.TASK_PLANES + G.EXTRA_PLANES if n not in planes]
    dev = max([abs(planes[n] - want_planes[n][1]) for n in want_planes if n in planes] or [9.9])
    record(not missing and dev <= G.DIM_TOL_IN, 'reference planes present and placed', {'missing': missing, 'dev_in': dev})
    bad = [n for n, k, d, f, s in G.PARAMETERS if d is not None and n != 'Glass_Thickness'
           and abs(defaults.get(n, -9) - d) > G.DIM_TOL_IN]
    record(not bad and abs(defaults.get('Glass_Thickness', -9) - 0.5) <= G.DIM_TOL_IN and
           abs(defaults.get('Cap_Spacing', -9) - 3.0) <= G.DIM_TOL_IN, 'parameter defaults and Cap_Spacing = 3 in', bad)
    record(sorted(types) == sorted(n for n, _g in G.TYPES) and all(
        abs(types[n].get('Glass_Thickness', -9) - g) <= G.DIM_TOL_IN for n, g in G.TYPES) and
        fstate.get('current_type') == G.DEFAULT_TYPE, 'types and default type', sorted(types))
    record(all(types[n].get(k) == v for n in types for k, v in (
        ('Manufacturer', G.MANUFACTURER), ('Model', G.MODEL), ('Description', G.DESCRIPTION),
        ('Type Comments', G.TYPE_COMMENTS))), 'identity data and Type Comments on every type')
    record(len(forms) == 6 and fstate.get('extrusions') == 2 and fstate.get('revolutions') == 4 and
           fstate.get('nested_family_instances') == 0 and fstate.get('import_instances') == 0,
           'six separate forms, no nested families, no imports')
    pos, vol = compare(by_key(fstate.get('forms', []), forms), st)
    record(pos <= G.GEOM_TOL_IN and vol <= VOLUME_REL_TOL, 'default solids match the analytic model',
           'dev %.5f in, volume err %.5f' % (pos, vol))
    frows = fstate.get('forms', [])
    record(sorted(str(r['subcategory']) for r in frows) == sorted([G.SUBCATEGORY_PLATE] * 2 + [G.SUBCATEGORY_CAP] * 4),
           'subcategories Clamp Plate x2, Clamp Cap x4')
    record(len(frows) == 6 and all(r['material_param'] == G.MATERIAL_PARAMETER for r in frows) and
           defaults.get(G.MATERIAL_PARAMETER) == G.MATERIAL_NAME, 'every form bound to Clamp_Material = Brushed Bronze')
    mat = fam.get('material_readback', {})
    record(mat.get('diffuse_rgb') == list(G.MATERIAL_RGB) and mat.get('graphics_rgb') == list(G.MATERIAL_RGB) and
           abs((mat.get('generic_glossiness') or -1) - G.MATERIAL_GLOSSINESS) < 1e-6 and
           mat.get('generic_is_metal') in (True, 1), 'material colour 110/86/62, glossiness 0.65, metal', mat)
    record(mat.get('surface_foreground_pattern_none') is True, 'material surface pattern none',
           mat.get('surface_foreground_pattern_none'), soft=True)
    kind = dict((f['id'], f['kind']) for f in forms)
    vis_bad = [r['id'] for r in frows if r['visibility'].get('IsShownInCoarse') != (kind.get(r['id']) == 'plate')
               or not r['visibility'].get('IsShownInMedium') or not r['visibility'].get('IsShownInFine')]
    record(not vis_bad and len(frows) == 6, 'Coarse: plates only; Medium/Fine: plates and caps', vis_bad)

    # ---- flex, re-derived row by row
    flex = rep.get('flex', {})

    def flex_check(bucket, name):
        rows = [r for r in flex.get(bucket, []) if r['parameter'] == name]
        problems = []
        for r in rows:
            if 'error' in r:
                problems.append((r['value_in'], r['error']))
                continue
            want = G.with_change(G.state(), name, r['value_in'])
            p, v = compare(r['solids'], want)
            pd = max(abs(r['planes_in'].get(n, 9e9) - q) for n, (axis, q) in G.plane_positions(want).items())
            sd = abs(r['cap_spacing_in'] - want['Cap_Spacing'])
            if p > G.GEOM_TOL_IN or v > VOLUME_REL_TOL or pd > G.DIM_TOL_IN or sd > G.DIM_TOL_IN:
                problems.append((r['value_in'], 'solids %.4f in, volume %.4f, planes %.4f in, spacing %.4f in' % (p, v, pd, sd)))
        return bool(rows) and not problems, '%d rows; %s' % (len(rows), problems or 'all within tolerance')

    for name, _v in G.REQUIRED_FLEX:
        ok, det = flex_check('required', name)
        record(ok, 'flex %s (required)' % name, det)
    for name, _v in G.INFO_FLEX:
        ok, det = flex_check('informational', name)
        record(ok, 'flex %s (informational)' % name, det, soft=True)
    record(fam.get('flex_rolled_back') is True and
           abs(fam.get('defaults_after_flex', {}).get('Glass_Thickness', -9) - 0.5) <= G.DIM_TOL_IN and
           abs(fam.get('defaults_after_flex', {}).get('Clamp_Width', -9) - 5.0) <= G.DIM_TOL_IN,
           'flex rolled back; defaults restored', fam.get('defaults_after_flex'))

    # ---- save / reopen
    record(not fstate.get('warnings') and not reopened.get('warnings'), 'no family warnings',
           {'before': fstate.get('warnings'), 'reopened': reopened.get('warnings')})
    rpos, rvol = compare(by_key(reopened.get('forms', []), forms), st) if len(reopened.get('forms', [])) == 6 else (9.9, 9.9)
    record(reopened.get('is_family_document') is True and reopened.get('category') == 'Generic Models' and
           sorted(reopened.get('types', {})) == sorted(n for n, _g in G.TYPES) and rpos <= G.GEOM_TOL_IN and
           rvol <= VOLUME_REL_TOL and all(f['material_param'] == G.MATERIAL_PARAMETER for f in reopened.get('forms', [])),
           'reopened from disk: same state, geometry and bindings', 'dev %.5f in' % rpos)
    purge = fam.get('purge', {})
    record('error' not in purge and purge.get('removed') is not None, 'purge unused ran', purge)

    # ---- disposable project
    proj = rep.get('project', {})
    placed_ok, detail = len(proj.get('placements', {})) == 2, {}
    for tname, placed in proj.get('placements', {}).items():
        p, v = compare(placed['solids'], placed['expected_state_in'])
        detail[tname] = '%.5f in' % p
        placed_ok = placed_ok and p <= G.GEOM_TOL_IN and v <= VOLUME_REL_TOL
    record(placed_ok, 'both types loaded, placed and measured in a project', detail)
    swap = proj.get('material_swap', {})
    record(len(swap.get('original_face_material_ids', [])) == 1 and
           swap.get('swapped_face_material_ids') == [swap.get('substitute_id')] and
           swap.get('restored_face_material_ids') == swap.get('original_face_material_ids'),
           'material substitution reaches every face, then restores', swap)
    dl = proj.get('detail_levels', {})
    every = sorted(G.solids(G.state()).keys())
    record(dl.get('Coarse') == ['plate_back', 'plate_front'] and dl.get('Medium') == every and dl.get('Fine') == every,
           'detail levels as instances see them (Coarse plates only)', dl, soft=True)
    record(not proj.get('warnings'), 'no project warnings', proj.get('warnings'))
    files = [f for e in proj.get('exports', []) for f in e.get('files', [])]
    record(len(files) >= 4 and all(os.path.isfile(os.path.join(RUN_DIR, 'exports', f['file'])) for f in files),
           'review views exported to disk', [f['file'] for f in files], soft=True)

    # ---- the builder's own flags must agree with this verifier
    gates = rep.get('gates', {})
    absent = [k for k in REQUIRED_KEYS if not any(g.startswith(k + '_') for g in gates)]
    record(not absent, 'builder reported all 29 gates', absent)
    hard = [g for g, v in gates.items() if not v['pass'] and not v['soft']]
    record(rep.get('technical_pass') is True and not hard, 'builder technical_pass agrees', hard)
    record(rep.get('visual_verdict') == 'PENDING REVIEWER', 'no self-awarded visual pass', rep.get('visual_verdict'))

    width = max(len(n) for _s, n, _d in results)
    for status, name, det in results:
        print('%-4s  %-*s  %s' % (status, width, name, det if det not in ('', None) else ''))
    failed = [n for s, n, _d in results if s == 'FAIL']
    warned = [n for s, n, _d in results if s == 'WARN']
    if failed:
        print('\nFAIL: %d required check(s): %s' % (len(failed), '; '.join(failed)))
        locate_elsewhere()
        return 1
    print('\nPASS: every required check%s. Visual review of exports/ is still PENDING.' %
          (' (%d warning(s): %s)' % (len(warned), '; '.join(warned)) if warned else ''))
    if rfa:
        print('RFA: %s' % rfa)
    return 0


def locate_elsewhere():
    found = []
    for root in OTHER_ROOTS:
        candidate = os.path.join(root, 'output', G.RUN_NAME, G.RFA_NAME)
        if os.path.normpath(os.path.join(root, 'output', G.RUN_NAME)) != RUN_DIR and os.path.isfile(candidate):
            found.append(candidate)
    if found:
        print('Clamp RFA found in another checkout:')
        for path in found:
            print('  ' + path)


if __name__ == '__main__':
    sys.exit(main())
