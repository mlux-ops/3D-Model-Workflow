# -*- coding: utf-8 -*-
"""M01 Adella photographic material: baseline (A) and 1/8 in grout variant (B).

Adapted from scripts/rebuild_adella_precision.py for docs/model-transfer-tests/MATERIAL.md.

Adaptation summary (see PATH_AUDIT.md):
  * the source script's two copy-backs are REMOVED, not redirected. It wrote
    generated PNGs into output/adella/textures and pulled the adsklib, vrmat and
    vrscene out of output/adella; both touched shipped deliverables.
  * every write goes through out_path(), which raises if a path leaves RUN_DIR.
  * the repository root is probed, not hard-coded.
  * both variants are produced from the same construction code in one run; the
    joint width is a parameter, not a second copied script.
  * grout core width is MEASURED from the rasterised edge field and gated,
    rather than assumed from the number substituted into the formula.
  * the script re-raises after writing its JSON, because a clean exit code is
    not evidence (ENVIRONMENT.md, and confirmed on P01 where pyrevit run
    returned 0 on two crashed runs).
"""
import json
import os
import struct
import traceback
import zlib

import numpy as np
from PIL import Image

RUN_ID = 'candidate-20260918-01'

REPO_ROOT_CANDIDATES = [
    'C:/Users/mlux/Documents/GitHub/3D-Model-Workflow',
    'C:/Users/found/OneDrive/Documents/ChatGPT/3D Model Workflow',
]

CROP = (12, 12, 2548, 1257)
OUT_W, OUT_H = 4096, 2048
MM_PER_IN = 25.4
NOMINAL_IN = (24.0, 12.0)
BEVEL_MM = 2.0            # transition outside the grout core; NOT grout
HEIGHT_RANGE_MM = 0.6     # inferred, not measured relief
GROUT_TOL_PX = 2.0        # MATERIAL.md allows 2 px for rasterisation

VARIANTS = [
    {'key': 'baseline', 'label': 'A - reproduction, 1/16 in grout',
     'joint_in': 1.0 / 16.0,
     'name': 'MSI Adella Viso White - 12x24 Satin - Stacked'},
    {'key': 'variant', 'label': 'B - controlled variation, 1/8 in grout',
     'joint_in': 1.0 / 8.0,
     'name': 'MSI Adella Viso White - 12x24 Satin - Stacked - 1-8 Grout'},
]


def repo_root():
    for candidate in REPO_ROOT_CANDIDATES:
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, 'AGENTS.md')):
            return candidate
    raise RuntimeError('No repository root found among: ' + ' | '.join(REPO_ROOT_CANDIDATES))


ROOT = repo_root()
RUN_DIR = os.path.join(ROOT, 'output', 'model-transfer-tests', RUN_ID, 'material')
_RUN_DIR_NORM = os.path.normpath(RUN_DIR)
SRC = os.path.join(ROOT, 'references', 'adella', 'crawl2.jpg')

REPORT = {
    'run_id': RUN_ID,
    'script': 'build_maps.py',
    'repo_root': ROOT,
    'run_dir': RUN_DIR,
    'specification': 'docs/model-transfer-tests/MATERIAL.md',
    'source_path': SRC,
    'source_url': ('https://www.stonelocator.com/wp-content/uploads/2017/11/'
                   'NADEVISWHI1224_a-scaled.jpg'),
    'source_is_scan': False,
    'crop': list(CROP),
    'output_pixels': [OUT_W, OUT_H],
    'height_full_range_mm': HEIGHT_RANGE_MM,
    'bevel_mm': BEVEL_MM,
    'method': ('floating point luminance filtering throughout, quantised only on export. '
               'Photo-derived relief estimate, not measured height. Photographed shading '
               'is attenuated, not calibrated albedo. Resampling to 4096 x 2048 does not '
               'create native 4K detail.'),
    'native_render': 'BLOCKED - V-Ray is not installed on this workstation',
    'revit_library': 'not attempted by this script; see the Revit stage',
    'variants': {},
    'stage': 'started',
}


def out_path(*parts):
    """Join under RUN_DIR and refuse any path that escapes it."""
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if target != _RUN_DIR_NORM and not target.startswith(_RUN_DIR_NORM + os.sep):
        raise RuntimeError('Write path escapes the run directory: ' + target)
    parent = os.path.dirname(target)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    payload = json.dumps(REPORT, indent=2, default=str, sort_keys=True)
    with open(out_path('validation.json'), 'w') as handle:
        handle.write(payload)


def blur(a, s):
    p = int(s * 4) + 1
    b = np.pad(a, ((p, p), (p, p)), mode='reflect')
    fy = np.fft.fftfreq(b.shape[0])[:, None]
    fx = np.fft.rfftfreq(b.shape[1])[None, :]
    b = np.fft.irfft2(
        np.fft.rfft2(b) * np.exp(-2 * np.pi ** 2 * s * s * (fx * fx + fy * fy)),
        s=b.shape)
    return b[p:-p, p:-p]


def resize(a):
    return np.asarray(
        Image.fromarray(a.astype('float32')).resize((OUT_W, OUT_H), Image.Resampling.BICUBIC),
        dtype=float)


def png16(path, a):
    """Write a lossless RGB16 PNG.

    Pillow exposes RGB16 as an 8-bit view, so the near-flat normals would be
    re-quantised if this went through Image.save.
    """
    data = np.asarray(np.clip(a, 0, 1) * 65535 + .5, dtype='>u2')
    h, w, _ = data.shape

    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload
                + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))

    raw = b''.join(b'\x00' + row.tobytes() for row in data)
    with open(path, 'wb') as handle:
        handle.write(b'\x89PNG\r\n\x1a\n'
                     + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 16, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(raw))
                     + chunk(b'IEND', b''))


def png_header(path):
    """Read dimensions, bit depth and colour type from the PNG header itself.

    MATERIAL.md requires verifying depth from the header because some image
    libraries report an 8-bit view of an RGB16 file.
    """
    with open(path, 'rb') as handle:
        head = handle.read(26)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('Not a PNG: ' + path)
    width, height = struct.unpack('>II', head[16:24])
    return {'width': width, 'height': height,
            'bit_depth': head[24], 'colour_type': head[25]}


def build(cfg, photo):
    record = {'label': cfg['label'], 'material_name': cfg['name']}

    joint_mm = cfg['joint_in'] * MM_PER_IN
    repeat_in = (NOMINAL_IN[0] + cfg['joint_in'], NOMINAL_IN[1] + cfg['joint_in'])
    repeat_mm = (repeat_in[0] * MM_PER_IN, repeat_in[1] * MM_PER_IN)
    half_joint_mm = joint_mm / 2.0

    record['joint_inches'] = cfg['joint_in']
    record['joint_mm'] = joint_mm
    record['repeat_inches'] = list(repeat_in)
    record['repeat_mm'] = list(repeat_mm)
    record['half_joint_mm'] = half_joint_mm
    record['mm_per_pixel'] = [repeat_mm[0] / OUT_W, repeat_mm[1] / OUT_H]

    # Distance to the nearest repeat boundary, in millimetres.
    y, x = np.mgrid[:OUT_H, :OUT_W]
    edge = np.minimum.reduce([
        x * repeat_mm[0] / OUT_W,
        (OUT_W - 1 - x) * repeat_mm[0] / OUT_W,
        y * repeat_mm[1] / OUT_H,
        (OUT_H - 1 - y) * repeat_mm[1] / OUT_H,
    ])
    t = np.clip((edge - half_joint_mm) / BEVEL_MM, 0, 1)
    mask = t * t * (3 - 2 * t)

    # Measure the grout core rather than trusting the substituted number. A
    # repeat with a centred boundary joint carries half the joint on each of two
    # opposing edges, so a centre scanline crosses the full joint width.
    core = edge < half_joint_mm
    h_px = int(core[OUT_H // 2, :].sum())
    v_px = int(core[:, OUT_W // 2].sum())
    ideal_h = joint_mm / (repeat_mm[0] / OUT_W)
    ideal_v = joint_mm / (repeat_mm[1] / OUT_H)
    record['grout_core'] = {
        'method': ('count of pixels whose edge distance is below the half joint, along the '
                   'centre row and the centre column. Pixel centres are used, so each '
                   'half-joint rounds outward by up to one pixel. The bevel is excluded and '
                   'is not counted as grout.'),
        'measured_px': [h_px, v_px],
        'ideal_px': [ideal_h, ideal_v],
        'tolerance_px': GROUT_TOL_PX,
        'pass': bool(abs(h_px - ideal_h) <= GROUT_TOL_PX
                     and abs(v_px - ideal_v) <= GROUT_TOL_PX),
    }

    lum = photo @ np.array([.2126, .7152, .0722])
    smooth = blur(lum, 3)
    signal = smooth - blur(smooth, 100)
    scale = np.percentile(np.abs(signal), 99)
    height = resize(.5 + .20 * np.tanh(signal / max(scale, 1e-6)))
    height = .15 + (.5 + (height - .5) * mask - .15) * mask

    base = np.stack([resize(blur(photo[:, :, i], 2)) for i in range(3)], axis=2)
    base = .85 * np.median(photo, axis=(0, 1)) + .15 * base
    base = base * mask[:, :, None] + .86 * (1 - mask[:, :, None])

    record['precision'] = {
        'height_finite': bool(np.isfinite(height).all()),
        'base_finite': bool(np.isfinite(base).all()),
        'height_min': float(height.min()),
        'height_max': float(height.max()),
        'working_dtype': str(height.dtype),
    }

    tex = cfg['key'] + '/textures'
    q = np.uint16(np.clip(height, 0, 1) * 65535 + .5)
    unique = int(len(np.unique(q)))
    record['height_unique_values'] = unique
    record['height_unique_smoke_check'] = bool(unique > 1000)

    Image.fromarray(np.uint8(np.clip(base, 0, 1) * 255 + .5)).save(
        out_path(tex, 'Adella_BaseColor.png'))
    Image.fromarray(q).save(out_path(tex, 'Adella_Bump.png'))
    Image.fromarray(q).save(out_path(tex, 'Adella_Height16.png'))

    dy, dx = np.gradient(height * HEIGHT_RANGE_MM,
                         repeat_mm[1] / OUT_H, repeat_mm[0] / OUT_W)
    normals = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2)[:, :, None]
    png16(out_path(tex, 'Adella_Normal_OpenGL.png'), normals * .5 + .5)

    rough = .42 * mask + .78 * (1 - mask)
    Image.fromarray(np.uint8(rough * 255 + .5)).save(out_path(tex, 'Adella_Roughness.png'))
    record['roughness_response'] = {
        'tile': 0.42,
        'grout': 0.78,
        'note': ('the satin ceramic face is smoother than the light grout. Linear data map, '
                 'consumed as roughness with option_use_roughness in the V-Ray material.'),
    }

    record['maps'] = {}
    for name in sorted(os.listdir(out_path(tex))):
        path = out_path(tex, name)
        record['maps'][name] = png_header(path)
        record['maps'][name]['bytes'] = os.path.getsize(path)

    # Illustrative shaded preview over 2 x 2 repeats. NOT a native render.
    light = np.array([-.8, .2, .5])
    light /= np.linalg.norm(light)
    shaded = np.clip(base * (.35 + .75 * np.maximum(0, normals @ light)[:, :, None]), 0, 1)
    two_by_two = np.tile(np.uint8(shaded * 255 + .5), (2, 2, 1))
    preview_name = cfg['key'] + '/Preview_2x2_ILLUSTRATIVE_NOT_A_RENDER.jpg'
    Image.fromarray(two_by_two).resize((1600, 800)).save(out_path(preview_name), quality=92)
    record['preview'] = {
        'file': preview_name,
        'covers_repeats': [2, 2],
        'label': 'ILLUSTRATIVE shaded map preview, not a native Revit or V-Ray render',
    }

    normal_hdr = record['maps']['Adella_Normal_OpenGL.png']
    record['gates'] = {
        'output_dimensions': all(m['width'] == OUT_W and m['height'] == OUT_H
                                 for m in record['maps'].values()),
        'normal_is_rgb16': normal_hdr['bit_depth'] == 16 and normal_hdr['colour_type'] == 2,
        'height_is_16bit': record['maps']['Adella_Bump.png']['bit_depth'] == 16,
        'float_precision_retained': (record['precision']['height_finite']
                                     and record['precision']['base_finite']
                                     and record['precision']['working_dtype'] == 'float64'),
        'height_quantisation_smoke_check': record['height_unique_smoke_check'],
        'grout_core_measured': record['grout_core']['pass'],
        'five_maps_present': len(record['maps']) == 5,
        'preview_2x2_present': os.path.isfile(out_path(preview_name)),
    }
    record['maps_pass'] = all(record['gates'].values())
    record['visual_verdict'] = ('PENDING REVIEWER - previews are illustrative, '
                                'fidelity not self-assessed')
    return record


def main():
    image = Image.open(SRC)
    REPORT['source_pixels'] = list(image.size)
    crop = image.convert('RGB').crop(CROP)
    REPORT['cropped_pixels'] = list(crop.size)
    photo = np.asarray(crop, dtype=np.float64) / 255
    checkpoint('source-read')

    for cfg in VARIANTS:
        REPORT['variants'][cfg['key']] = build(cfg, photo)
        checkpoint('built-' + cfg['key'])

    failed = dict((key, sorted(name for name, ok in record['gates'].items() if not ok))
                  for key, record in REPORT['variants'].items())
    REPORT['failed_gates'] = failed
    REPORT['maps_pass'] = all(v['maps_pass'] for v in REPORT['variants'].values())
    checkpoint('complete')

    if any(failed.values()):
        raise RuntimeError('Gate failures: ' + json.dumps(failed))

    print(json.dumps({
        'maps_pass': REPORT['maps_pass'],
        'grout_core_px': dict((k, v['grout_core']['measured_px'])
                              for k, v in REPORT['variants'].items()),
        'height_unique': dict((k, v['height_unique_values'])
                              for k, v in REPORT['variants'].items()),
    }, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        REPORT['error'] = traceback.format_exc()
        try:
            checkpoint('failed')
        finally:
            raise
