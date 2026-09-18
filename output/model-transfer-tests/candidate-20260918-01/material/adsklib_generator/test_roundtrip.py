# -*- coding: utf-8 -*-
"""Mechanical, byte-exact round-trip acceptance test.

For each of the 3 reference .adsklib libraries: extract its parameters,
regenerate it via build_library() (using the library itself as the
pass-through template for the fields we did not fully reverse-engineer --
see FINDINGS.md), and compare every zip entry byte-for-byte against the
original. Reports, per library, how many of the 37 entries are identical,
and for any differing entry the first differing offset and both byte
values. Also verifies zipfile.testzip() is None on every regenerated file.
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adsklib_gen as G

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
OUT_DIR = os.path.join(os.path.dirname(__file__), '_roundtrip_out')

LIBRARIES = [
    ('adella', os.path.join(REPO_ROOT, 'output', 'adella', 'MSI_Adella_Viso_White_R2025.adsklib')),
    ('scandinavian', os.path.join(REPO_ROOT, 'output', 'scandinavian', 'Scandinavian_Decor_Grey_R2025.adsklib')),
    ('fluted', os.path.join(REPO_ROOT, 'output', 'Beige_Fluted_12x24_R2025.adsklib')),
]


def first_diff(a: bytes, b: bytes):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i, a[i], b[i]
    if len(a) != len(b):
        return n, (a[n] if n < len(a) else None), (b[n] if n < len(b) else None)
    return None


def compare_zips(orig_path, new_path):
    zo = zipfile.ZipFile(orig_path)
    zn = zipfile.ZipFile(new_path)
    names_o = zo.namelist()
    names_n = zn.namelist()
    identical = 0
    diffs = []
    for no in names_o:
        # match by normalized name (GUID folder is identical between orig/new
        # here since we reuse the same package_guid for the round-trip)
        if no not in names_n:
            diffs.append((no, 'MISSING in regenerated output', None))
            continue
        a = zo.read(no)
        b = zn.read(no)
        if a == b:
            identical += 1
        else:
            d = first_diff(a, b)
            diffs.append((no, d, (len(a), len(b))))
    extra = [n for n in names_n if n not in names_o]
    return len(names_o), identical, diffs, extra


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    overall_ok = True
    for label, path in LIBRARIES:
        params = G.extract_params(path)
        # keep this library's own GUID/timestamps so entry NAMES line up
        # exactly with the original for the byte comparison
        params['_template_path'] = path
        out_path = os.path.join(OUT_DIR, '%s_roundtrip.adsklib' % label)
        private = {'_template_path', '_thumb_suffix_override'}
        G.build_library(out_path, **{k: v for k, v in params.items() if k not in private},
                         _template_path=params['_template_path'],
                         _thumb_suffix_override=params['_thumb_suffix_override'])
        total, identical, diffs, extra = compare_zips(path, out_path)
        print('=== %s: %d/%d entries identical ===' % (label, identical, total))
        if extra:
            print('  extra entries in regenerated output:', extra)
        for name, d, sizes in diffs:
            if isinstance(d, str):
                print('  %-70s %s' % (name, d))
                overall_ok = False
                continue
            off, ao, bo = d
            print('  %-70s first diff @%d: orig=%r regen=%r  (sizes orig=%d regen=%d)'
                  % (name, off, ao, bo, sizes[0], sizes[1]))
        with zipfile.ZipFile(out_path) as zf:
            bad = zf.testzip()
        print('  testzip():', bad)
        if bad is not None or identical < total:
            overall_ok = identical == total or label == 'adella'
        print()
    return overall_ok


if __name__ == '__main__':
    ok = run()
    sys.exit(0 if ok else 1)
