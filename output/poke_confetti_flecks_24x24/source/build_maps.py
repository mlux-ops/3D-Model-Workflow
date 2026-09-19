# -*- coding: utf-8 -*-
"""Poke Confetti Flecks 24x24 + Remedy Hydro (fluted, handcrafted/flat) texture maps.

Adapted from output/model-transfer-tests/candidate-20260918-01/material/build_maps.py:
float luminance -> relief, edge mask for grout, 16-bit export, header-verified PNGs.

Scope: color (8-bit sRGB) + bump (16-bit gray) + Sample Size only. No ADSKLIB, no RVT,
no V-Ray, no ZIP, no Drive upload (out of scope per task).
"""
import json
import os
import struct
import zlib

import numpy as np
from PIL import Image

ROOT = 'C:/Users/mlux/Documents/GitHub/3D-Model-Workflow'
MM_PER_IN = 25.4


def png_header(path):
    with open(path, 'rb') as h:
        head = h.read(26)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('Not a PNG: ' + path)
    w, ht = struct.unpack('>II', head[16:24])
    return {'width': w, 'height': ht, 'bit_depth': head[24], 'colour_type': head[25]}


def save_gray16(path, a01):
    """Lossless 16-bit grayscale PNG (colour type 0), header-verifiable."""
    data = np.asarray(np.clip(a01, 0, 1) * 65535 + .5, dtype='>u2')
    h, w = data.shape

    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload
                + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))

    raw = b''.join(b'\x00' + row.tobytes() for row in data)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n'
                 + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 16, 0, 0, 0, 0))
                 + chunk(b'IDAT', zlib.compress(raw))
                 + chunk(b'IEND', b''))


def blur(a, s):
    p = int(s * 4) + 1
    b = np.pad(a, ((p, p), (p, p)), mode='reflect')
    fy = np.fft.fftfreq(b.shape[0])[:, None]
    fx = np.fft.rfftfreq(b.shape[1])[None, :]
    b = np.fft.irfft2(np.fft.rfft2(b) * np.exp(-2 * np.pi ** 2 * s * s * (fx * fx + fy * fy)),
                       s=b.shape)
    return b[p:-p, p:-p]


def resize_f(a, w, h):
    if a.ndim == 3:
        return np.stack([resize_f(a[:, :, i], w, h) for i in range(a.shape[2])], axis=2)
    return np.asarray(Image.fromarray(a.astype('float32')).resize((w, h), Image.Resampling.BICUBIC),
                       dtype=float)


def grout_mask(w, h, repeat_w_mm, repeat_h_mm, joint_mm, bevel_mm=1.0):
    """1.0 = tile face, 0.0 = grout core, smooth transition of width bevel_mm."""
    y, x = np.mgrid[:h, :w]
    edge = np.minimum.reduce([
        x * repeat_w_mm / w,
        (w - 1 - x) * repeat_w_mm / w,
        y * repeat_h_mm / h,
        (h - 1 - y) * repeat_h_mm / h,
    ])
    half_joint = joint_mm / 2.0
    t = np.clip((edge - half_joint) / bevel_mm, 0, 1)
    return t * t * (3 - 2 * t), edge


def grazing_preview(base01, height01, mm_per_px_x, mm_per_px_y, height_range_mm, out_path, reps=(2, 2)):
    dy, dx = np.gradient(height01 * height_range_mm, mm_per_px_y, mm_per_px_x)
    normals = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2)[:, :, None]
    light = np.array([-.85, .15, .25])
    light /= np.linalg.norm(light)
    shaded = np.clip(base01 * (.15 + .95 * np.maximum(0, normals @ light)[:, :, None]), 0, 1)
    tiled = np.tile(np.uint8(shaded * 255 + .5), (reps[1], reps[0], 1))
    Image.fromarray(tiled).resize((1600, 1600)).save(out_path, quality=92)


def tiling_preview(color01, out_path, reps=(2, 2)):
    tiled = np.tile(np.uint8(np.clip(color01, 0, 1) * 255 + .5), (reps[1], reps[0], 1))
    Image.fromarray(tiled).resize((1600, 1600)).save(out_path, quality=92)


REPORT = {}


# ---------------------------------------------------------------------------
# PRODUCT 1: Poke, Confetti Flecks, 24x24 matte, terrazzo-look (FLAT tile)
# ---------------------------------------------------------------------------
def build_poke():
    out_dir = os.path.join(ROOT, 'output', 'poke_confetti_flecks_24x24', 'textures')
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(ROOT, 'output', 'poke_confetti_flecks_24x24', 'references',
                        'poke_confetti_flecks_24x24_3000x3000.jpg')
    im = Image.open(src).convert('RGB')
    rec = {'source_url': ('https://s7d9.scene7.com/is/image/daltile/'
                          'DAL_Poke_PK23_24x24_RES_03?wid=3000&hei=3000'),
           'source_pixels': list(im.size)}

    photo = np.asarray(im, dtype=np.float64) / 255.0
    OUT = 2048
    NOMINAL_IN = 24.0  # nominal size per product page; actual measured dimension is 23.81 in
    JOINT_IN = 3.0 / 16.0  # page-stated "Grout Joint Recommendation: 3/16 in"
    repeat_in = NOMINAL_IN + JOINT_IN
    repeat_mm = repeat_in * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    color = resize_f(np.stack([blur(photo[:, :, i], 1.5) for i in range(3)], axis=2), OUT, OUT)

    mask, edge = grout_mask(OUT, OUT, repeat_mm, repeat_mm, joint_mm, bevel_mm=1.2)
    lum = photo @ np.array([.2126, .7152, .0722])
    smooth = blur(lum, 2)
    micro = smooth - blur(smooth, 60)  # subtle surface variation only, no sculpted pattern
    scale = np.percentile(np.abs(micro), 99)
    micro01 = 0.5 + 0.06 * np.tanh(micro / max(scale, 1e-6))  # SUBTLE: +/-0.06 only
    micro01 = resize_f(micro01, OUT, OUT)

    HEIGHT_RANGE_MM = 0.35  # flat matte tile: subtle micro relief; grout is the dominant feature
    GROUT_FLOOR = 0.10
    height = GROUT_FLOOR + (micro01 - GROUT_FLOOR) * mask
    # blend grout floor into tile face at boundary via mask already; grout itself:
    height = np.where(mask < 1.0, GROUT_FLOOR + (micro01 - GROUT_FLOOR) * mask, micro01)

    color_out = np.clip(color, 0, 1) * mask[:, :, None] + np.clip(color, 0, 1).mean(axis=(0, 1)) * 0.55 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'poke_confetti_flecks_24x24_Color.png')
    bump_path = os.path.join(out_dir, 'poke_confetti_flecks_24x24_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_out, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)

    tiling_preview(color_out, os.path.join(out_dir, '_PREVIEW_tiling_poke.jpg'))

    color_hdr = png_header(color_path)
    bump_hdr = png_header(bump_path)
    sample_in = repeat_in
    from fractions import Fraction
    total_frac = Fraction(sample_in).limit_denominator(16)
    ft, rem_in = divmod(total_frac, 12)
    ft = int(ft)
    whole = int(rem_in)
    rem = rem_in - whole
    inch_str = f"{whole} {rem.numerator}/{rem.denominator}" if rem else f"{whole}"
    rec.update({
        'color_map': {'path': color_path, 'header': color_hdr},
        'bump_map': {'path': bump_path, 'header': bump_hdr},
        'joint_in': JOINT_IN, 'joint_source': "Daltile product page: 'Grout Joint Recommendation: 3/16 in'",
        'nominal_in': NOMINAL_IN,
        'sample_size_in': sample_in,
        'sample_size_ft_in': f"{ft}'-{inch_str}\"",
        'height_range_mm': HEIGHT_RANGE_MM,
        'grout_floor_frac': GROUT_FLOOR,
        'grout_depth_mm': (1 - GROUT_FLOOR) * HEIGHT_RANGE_MM,
    })
    return rec


REPORT['poke_confetti_flecks_24x24'] = build_poke()

with open(os.path.join(ROOT, 'output', 'poke_confetti_flecks_24x24', 'source', 'build_report.json'), 'w') as f:
    json.dump(REPORT, f, indent=2, default=str)

print(json.dumps(REPORT, indent=2, default=str))
