r"""Independent gate verifier for the Miele KM 3054-1 family run (CPython 3, stdlib only).

    "C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe" verify_km3054.py

pyrevit run has exited 0 on crashed scripts, so its exit status is never the result.
Targets and tolerances come from km3054_geometry.py, not from what the builder recorded,
and every ray value is re-derived from the raw Solid.IntersectWithCurve segments.

Exit 0  technical pass (re-derived), RFA and exports on disk, report not stale.
Exit 1  technical fail.
Exit 2  BLOCKED: no validation.json (the builder never ran here) or the RFA is missing
        because nothing ran. A blocked run is not a failed model.
A pass is TECHNICAL only. The visual verdict belongs to the reviewer (REVIEW.md).
"""
import datetime
import json
import os
import struct
import sys
import zlib

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import km3054_geometry as G  # noqa: E402

RUN_DIR = os.path.normpath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN_DIR, 'validation.json')
RUN_START = os.path.join(RUN_DIR, 'logs', 'run-start.txt')
RFA_NAME = 'Miele_KM3054-1_Gas_Cooktop_R2025.rfa'
HOSTED_KEYS = ['overall_width', 'overall_depth', 'top_above_counter', 'overall_height',
               'casing_depth_below_counter', 'built_in_height_with_box', 'knob_count']


def parse_utc(text):
    text = text.strip().rstrip('Z')
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('unparseable timestamp %r' % text)


def mtime_utc(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc).replace(tzinfo=None)


def png_rows(path):
    """Minimal PNG decoder (8-bit grey/RGB/RGBA, non-interlaced). Returns (w, h, rows of RGB tuples)."""
    with open(path, 'rb') as fh:
        data = fh.read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    pos, idat, ihdr = 8, b'', None
    while pos < len(data):
        n, kind = struct.unpack('>I4s', data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + n]
        if kind == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', chunk)
        elif kind == b'IDAT':
            idat += chunk
        pos += 12 + n
    w, h, depth, ctype, _, _, interlace = ihdr
    if depth != 8 or interlace or ctype not in (0, 2, 6):
        raise ValueError('unsupported PNG %r' % (ihdr,))
    bpp = {0: 1, 2: 3, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride = w * bpp
    prev = bytearray(stride)
    rows, i = [], 0
    for _ in range(h):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        prev = line
        if bpp == 1:
            rows.append([(v, v, v) for v in line])
        else:
            rows.append([tuple(line[k:k + 3]) for k in range(0, stride, bpp)])
    return w, h, rows


def border_white_fraction(path, band=6):
    """Share of near-white pixels in the outer band: the host must not reach the crop edge."""
    w, h, rows = png_rows(path)
    px = []
    for y in list(range(band)) + list(range(h - band, h)):
        px.extend(rows[y])
    for y in range(band, h - band):
        px.extend(rows[y][:band] + rows[y][w - band:])
    white = sum(1 for p in px if min(p) >= 235)
    return white / float(len(px))


def main():
    print('run folder: ' + RUN_DIR)
    if not os.path.isfile(REPORT):
        print('BLOCKED - no validation.json: the builder never started inside Revit for this folder.')
        print('  Check the newest Revit journal for 0xe06d7363 or a licence dialog; see README.md.')
        return 2
    try:
        with open(REPORT) as fh:
            rep = json.load(fh)
    except ValueError as exc:
        print('FAIL - validation.json unparseable: %s' % exc)
        return 1
    problems = []
    add = problems.append
    start = None
    if os.path.isfile(RUN_START):
        with open(RUN_START) as fh:
            start = parse_utc(fh.read())
        if parse_utc(rep.get('started_utc', '1970-01-01T00:00:00')) < start:
            print('STALE report: builder started %s, before this run began %s' % (rep.get('started_utc'), start))
            print('BLOCKED - this run produced no new report.')
            return 2
    if rep.get('stage') != 'complete':
        add('stage is %r, expected "complete"' % rep.get('stage'))
    if rep.get('error'):
        add('builder error:\n' + str(rep['error']).strip())
    if not str(rep.get('revit_version', '')).startswith('2025'):
        add('Revit version %r' % rep.get('revit_version'))
    if G.check_profiles():
        add('profile sanity problems: %r' % G.check_profiles())
    if rep.get('visual_verdict') != 'PENDING REVIEWER':
        add('validation.json carries a visual verdict %r; verdicts belong in REVIEW.md' % rep.get('visual_verdict'))

    fam = rep.get('family') or {}
    host = rep.get('hosted') or {}
    if not fam.get('reopened') or fam.get('category') != 'Specialty Equipment':
        add('reopened=%r category=%r' % (fam.get('reopened'), fam.get('category')))
    if fam.get('placement_type') != 'WorkPlaneBased' or fam.get('always_vertical') != 0:
        add('placement %r always_vertical %r' % (fam.get('placement_type'), fam.get('always_vertical')))

    # parts: every group present with its subcategory and material parameter
    rows = fam.get('part_bindings') or []
    seen = {}
    for r in rows:
        seen.setdefault(r.get('group'), []).append(r)
    for gkey, mat, _ in G.groups():
        got = seen.get(gkey)
        if not got:
            add('group %s missing from the reopened RFA' % gkey)
            continue
        for r in got:
            if not r.get('found') or r.get('subcategory') != G.SUBCATEGORIES[mat] \
                    or r.get('material_parameter') != G.MATERIAL_PARAMETERS[mat]:
                add('group %s element %s: found=%r subcategory=%r parameter=%r' % (
                    gkey, r.get('id'), r.get('found'), r.get('subcategory'), r.get('material_parameter')))

    def check_rays(label, recorded, keys):
        for ray in G.measurement_rays():
            if ray['key'] not in keys:
                continue
            got = (recorded or {}).get(ray['key'])
            if got is None:
                add('%s ray %s not recorded' % (label, ray['key']))
                continue
            value = G.measure(ray, [tuple(s) for s in got.get('segments_mm', [])])
            if value is None or abs(value - ray['target']) > ray['tol'] + 1e-9:
                add('%s ray %s re-derived %r mm, target %.3f +/- %.3f mm (builder said %r)' % (
                    label, ray['key'], value, ray['target'], ray['tol'], got.get('measured_mm')))
    check_rays('family', fam.get('rays'), [r['key'] for r in G.measurement_rays()])
    check_rays('hosted', host.get('rays'), HOSTED_KEYS)

    saved = fam.get('saved_dimension_parameters_mm') or {}
    for name, value in (rep.get('dimension_parameters_mm') or {}).items():
        if not isinstance(saved.get(name), (int, float)) or abs(saved[name] - value) > 0.01:
            add('saved parameter %s = %r mm, expected %r' % (name, saved.get(name), value))
    for name, value in (('Overall Width', G.WIDTH), ('Overall Depth', G.DEPTH), ('Overall Height', G.OVERALL_HEIGHT),
                        ('Built-in Height', G.BUILT_IN_HEIGHT)):
        if not isinstance(saved.get(name), (int, float)) or abs(saved[name] - value) > 0.01:
            add('published parameter %s = %r, expected %r' % (name, saved.get(name), value))

    if not host.get('host_id') or host.get('instance_host_id') != host.get('host_id') or not host.get('hostface_present'):
        add('not hosted on the floor face: host %r instance host %r hostface %r' % (
            host.get('host_id'), host.get('instance_host_id'), host.get('hostface_present')))
    nd = host.get('normal_dot')
    if not isinstance(nd, (int, float)) or abs(nd - 1.0) > 1e-6:
        add('normal dot %r, expected 1' % nd)
    bz, fn = host.get('basis_z') or [0, 0, 0], host.get('face_normal') or [0, 0, 0]
    if abs(bz[2] - 1.0) > 1e-6 or abs(fn[2] - 1.0) > 1e-6:
        add('host face normal %r / local Z %r: expected world +Z (horizontal top face)' % (fn, bz))
    if abs((host.get('host_face_z_mm') or 0) - (host.get('instance_origin_z_mm') or 1e9)) > 0.01:
        add('instance origin %r not on the host face %r' % (host.get('instance_origin_z_mm'), host.get('host_face_z_mm')))

    expected = G.expected_groups_per_material()
    subs = host.get('material_substitution') or {}
    for key, label in G.MATERIAL_PARAMETERS.items():
        t = subs.get(label)
        if not t:
            add('material substitution for %s not recorded' % label)
            continue
        if not t.get('faces_carrying_substitute') or t.get('solids_fully_carrying_substitute', 0) < expected[key] \
                or not t.get('restored'):
            add('%s: %r faces / %r solids carried the substitute (expected >= %d solids), restored=%r' % (
                label, t.get('faces_carrying_substitute'), t.get('solids_fully_carrying_substitute'), expected[key],
                t.get('restored')))

    for label, w in (('build', rep.get('family_warnings')), ('reopened family', fam.get('warnings')),
                     ('project', host.get('warnings'))):
        if w is None:
            add('%s warnings never read' % label)
        elif w:
            add('%s warnings: %r' % (label, w))

    rfa = os.path.join(RUN_DIR, RFA_NAME)
    if not os.path.isfile(rfa):
        add('RFA missing on disk: %s' % rfa)
    elif start and mtime_utc(rfa) < start:
        add('RFA on disk is older than this run (stale)')
    ev = os.path.join(RUN_DIR, 'evidence')

    def fresh(names):
        ok = []
        for n in names or []:
            p = os.path.join(ev, n)
            if os.path.isfile(p) and os.path.getsize(p) > 0 and \
                    (start is None or mtime_utc(p) >= start):
                ok.append(n)
        return ok
    fam_imgs, host_imgs = fresh(host.get('isolated_images')), fresh(host.get('images'))
    if len(fam_imgs) < 5:
        add('fresh isolated exports on disk: %d, expected >= 5' % len(fam_imgs))
    if len(host_imgs) < 1:
        add('fresh hosted exports on disk: %d, expected >= 1' % len(host_imgs))
    hidden = rep.get('isolated_host_hidden') or {}
    if len(hidden) < 5 or not all(v.get('hidden') for v in hidden.values()):
        add('disposable host not hidden in every isolated view: %r' % hidden)
    for n in fam_imgs:
        try:
            frac = border_white_fraction(os.path.join(ev, n))
        except Exception as exc:
            add('could not read %s: %s' % (n, exc))
            continue
        if frac < 0.97:
            add('%s: only %.1f%% of the crop border is background; host or geometry reaches the crop edge'
                % (n, frac * 100))

    disagree = [k for k, v in (rep.get('gates') or {}).items() if v is not True]
    if disagree and not problems:
        add('builder gate map reports failures the verifier did not reproduce: %r' % disagree)

    if problems:
        print('FAIL - %d problem(s):' % len(problems))
        for p in problems:
            print('  - ' + p.replace('\n', '\n    '))
        return 1
    print('TECHNICAL PASS - %d family rays, %d hosted rays, %d material substitutions, 0 warnings, normal dot %.6f'
          % (len(fam.get('rays', {})), len(host.get('rays', {})), len(subs), nd))
    print('  RFA: %s (%d bytes)' % (rfa, os.path.getsize(rfa)))
    print('  exports: %d isolated (host hidden, border check) + %d hosted in evidence/' % (len(fam_imgs), len(host_imgs)))
    print('visual_verdict: %s' % rep.get('visual_verdict'))
    print('A technical pass is not a visual pass. Review the comparison sheets in evidence/.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
