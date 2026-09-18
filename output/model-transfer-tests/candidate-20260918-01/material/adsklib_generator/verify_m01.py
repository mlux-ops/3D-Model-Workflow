# -*- coding: utf-8 -*-
"""Post-write assertions for the two generated M01 .adsklib libraries, plus
size/SHA-256 reporting."""
import hashlib
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adsklib_gen as G

MATERIAL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

TARGETS = [
    ('baseline', os.path.join(MATERIAL_ROOT, 'baseline', 'MSI_Adella_Viso_White_1-16_Grout_R2025.adsklib'),
     'MSI Adella Viso White - 12x24 Satin - Stacked', (24.0625, 12.0625),
     os.path.join(MATERIAL_ROOT, 'baseline', 'textures', 'Adella_BaseColor.png'),
     os.path.join(MATERIAL_ROOT, 'baseline', 'textures', 'Adella_Bump.png')),
    ('variant', os.path.join(MATERIAL_ROOT, 'variant', 'MSI_Adella_Viso_White_1-8_Grout_R2025.adsklib'),
     'MSI Adella Viso White - 12x24 Satin - Stacked - 1-8 Grout', (24.125, 12.125),
     os.path.join(MATERIAL_ROOT, 'variant', 'textures', 'Adella_BaseColor.png'),
     os.path.join(MATERIAL_ROOT, 'variant', 'textures', 'Adella_Bump.png')),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run():
    all_ok = True
    for label, path, expect_name, expect_scale, expect_diffuse, expect_bump in TARGETS:
        print('===', label, '===')
        print(' path:', path)
        print(' size:', os.path.getsize(path), 'bytes')
        print(' sha256:', sha256(path))

        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
        ok = bad is None
        print(' testzip() is None:', ok)
        all_ok &= ok

        params = G.extract_params(path)
        ok = params['diffuse_path'] == expect_diffuse
        print(' diffuse_path decodes correctly:', ok, '->', params['diffuse_path'])
        all_ok &= ok
        ok = params['bump_path'] == expect_bump
        print(' bump_path decodes correctly:', ok, '->', params['bump_path'])
        all_ok &= ok
        ok = params['material_name'] == expect_name
        print(' material_name decodes correctly:', ok, '->', params['material_name'])
        all_ok &= ok
        got_scale = params['real_world_scale_in']
        ok = abs(got_scale[0] - expect_scale[0]) < 1e-6 and abs(got_scale[1] - expect_scale[1]) < 1e-6
        print(' real_world_scale_in decodes correctly:', ok, '->', got_scale, 'expected', expect_scale)
        all_ok &= ok
        print()
    print('ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED')
    return all_ok


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
