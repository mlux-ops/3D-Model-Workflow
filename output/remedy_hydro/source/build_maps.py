# -*- coding: utf-8 -*-
"""Remedy Hydro: fluted (dimensional, sculpted flute relief) + handcrafted (flat-role) maps.

Reuses helpers from output/poke_confetti_flecks_24x24/source/build_maps.py (same technique:
float64 luminance -> relief, edge mask for grout, 16-bit export, header-verified PNGs).

IMPORTANT LIMITATION recorded here and in README: the Remedy line as published by Daltile
offers only two Hydro styles, "Fluted" and "Handcrafted" (undulated) -- both are dimensional.
There is no literal flat/field SKU in this collection. Per task instruction, the Handcrafted
piece is used in the FLAT role (subtle relief + grout only, no sculpted flute geometry), and
this substitution is called out explicitly rather than fabricated as a true flat product.
"""
import json
import os
import struct
import zlib
from fractions import Fraction

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
    y, x = np.mgrid[:h, :w]
    edge = np.minimum.reduce([
        x * repeat_w_mm / w,
        (w - 1 - x) * repeat_w_mm / w,
        y * repeat_h_mm / h,
        (h - 1 - y) * repeat_h_mm / h,
    ])
    half_joint = joint_mm / 2.0
    t = np.clip((edge - half_joint) / bevel_mm, 0, 1)
    return t * t * (3 - 2 * t)


def tiling_preview(color01, out_path, reps=(2, 2)):
    tiled = np.tile(np.uint8(np.clip(color01, 0, 1) * 255 + .5), (reps[1], reps[0], 1))
    Image.fromarray(tiled).resize((1600, 1600)).save(out_path, quality=92)


def grazing_preview(base01, height01, mm_per_px_x, mm_per_px_y, height_range_mm, out_path, reps=(2, 2)):
    dy, dx = np.gradient(height01 * height_range_mm, mm_per_px_y, mm_per_px_x)
    normals = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2)[:, :, None]
    light = np.array([-.85, .15, .25])
    light /= np.linalg.norm(light)
    shaded = np.clip(base01 * (.15 + .95 * np.maximum(0, normals @ light)[:, :, None]), 0, 1)
    tiled = np.tile(np.uint8(shaded * 255 + .5), (reps[1], reps[0], 1))
    Image.fromarray(tiled).resize((1600, 1600)).save(out_path, quality=92)


def sample_size_str(sample_in):
    total_frac = Fraction(sample_in).limit_denominator(16)
    ft, rem_in = divmod(total_frac, 12)
    ft = int(ft)
    whole = int(rem_in)
    rem = rem_in - whole
    inch_str = f"{whole} {rem.numerator}/{rem.denominator}" if rem else f"{whole}"
    return f"{ft}'-{inch_str}\""


REPORT = {}
JOINT_IN = 1.0 / 8.0  # Daltile page: "Grout Joint Recommendation: 1/8 in" applies to all Remedy pieces
NOMINAL_W_IN, NOMINAL_L_IN = 2.0, 10.0
OUT_W, OUT_H = 2048, 2048 * 5  # keep 2x10 aspect ratio (1:5)


# ---------------------------------------------------------------------------
# Fluted piece: dimensional, pronounced sinusoidal flute relief + separate grout
# ---------------------------------------------------------------------------
def build_fluted():
    out_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'textures')
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(ROOT, 'output', 'remedy_hydro', 'references',
                        'remedy_hydro_fluted_2000x2000.jpg')
    im = Image.open(src).convert('RGB')
    photo = np.asarray(im, dtype=np.float64) / 255.0

    repeat_w_mm = (NOMINAL_W_IN + JOINT_IN) * MM_PER_IN
    repeat_l_mm = (NOMINAL_L_IN + JOINT_IN) * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    # Flute geometry estimate: photo autocorrelation of the fluted panel photo indicated a
    # dominant period corresponding to roughly 4 flutes across the 2 in tile width (flute
    # pitch approx 0.5 in / 12.7 mm), running the length of the strip. This is an ESTIMATE
    # from marketing imagery + the 2x10 nominal size, NOT an orthographic/measured scan.
    N_FLUTES = 4
    flute_pitch_mm = repeat_w_mm / N_FLUTES

    color_src = resize_f(np.stack([blur(photo[:, :, i], 1.2) for i in range(3)], axis=2),
                          OUT_W, OUT_H)
    color01 = np.clip(color_src, 0, 1)

    y, x = np.mgrid[:OUT_H, :OUT_W]
    x_mm = x * repeat_w_mm / OUT_W
    flute_phase = 2 * np.pi * x_mm / flute_pitch_mm
    flute_sine = 0.5 + 0.5 * np.sin(flute_phase)  # 0..1 sinusoidal ridge/valley, runs along length (y)

    lum = photo @ np.array([.2126, .7152, .0722])
    micro = blur(lum, 2) - blur(lum, 40)
    scale = np.percentile(np.abs(micro), 99)
    micro01 = resize_f(0.5 + 0.04 * np.tanh(micro / max(scale, 1e-6)), OUT_W, OUT_H)

    mask = grout_mask(OUT_W, OUT_H, repeat_w_mm, repeat_l_mm, joint_mm, bevel_mm=0.8)

    # Two SEPARATE depth components, kept distinguishable per 2026-09-18 rule:
    #   pattern (flute) component: pronounced, amplitude below is large relative to grout
    #   grout component: shallow, only active in the mask border band
    HEIGHT_RANGE_MM = 1.0
    PATTERN_AMPLITUDE = 0.55        # fraction of HEIGHT_RANGE_MM devoted to flute peak-valley swing
    GROUT_DEPTH_FRAC = 0.18         # shallower than pattern -> stays a joint, not a puncture
    micro_amp = 0.06

    pattern_component = PATTERN_AMPLITUDE * (flute_sine - 0.5) + micro_amp * (micro01 - 0.5)
    base_level = 0.5
    height_face = base_level + pattern_component
    height_face = np.clip(height_face, base_level - PATTERN_AMPLITUDE / 2 - micro_amp / 2,
                           base_level + PATTERN_AMPLITUDE / 2 + micro_amp / 2)

    grout_floor = base_level - PATTERN_AMPLITUDE / 2 - micro_amp / 2 - GROUT_DEPTH_FRAC
    grout_floor = max(grout_floor, 0.02)  # keep inside 0..1 with margin
    height = grout_floor + (height_face - grout_floor) * mask

    pattern_relief_mm = PATTERN_AMPLITUDE * HEIGHT_RANGE_MM
    grout_relief_mm = GROUT_DEPTH_FRAC * HEIGHT_RANGE_MM
    clearance_mm = pattern_relief_mm - grout_relief_mm  # must stay > 0 per hard ceiling rule

    color_out = color01 * mask[:, :, None] + color01.mean(axis=(0, 1)) * 0.5 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'remedy_hydro_fluted_Color.png')
    bump_path = os.path.join(out_dir, 'remedy_hydro_fluted_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_out, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)

    tiling_preview(color_out, os.path.join(out_dir, '_PREVIEW_tiling_remedy_hydro_fluted.jpg'), reps=(2, 2))
    grazing_preview(color_out, height, repeat_w_mm / OUT_W, repeat_l_mm / OUT_H, HEIGHT_RANGE_MM,
                     os.path.join(out_dir, '_PREVIEW_grazing_light_remedy_hydro_fluted.jpg'), reps=(2, 2))

    sample_in_w = NOMINAL_W_IN + JOINT_IN
    sample_in_l = NOMINAL_L_IN + JOINT_IN
    return {
        'style': 'fluted (dimensional)',
        'source_url': ('https://s7d9.scene7.com/is/image/daltile/'
                        'DAL_RD22_2x10_Fluted_Hydro_GL_LivePanel_Angle_01?wid=2000&hei=2000'),
        'source_pixels': list(im.size),
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'joint_in': JOINT_IN,
        'joint_source': "Daltile Remedy-Hydro page: 'Grout Joint Recommendation: 1/8 in' (applies to all Remedy pieces)",
        'nominal_in': [NOMINAL_W_IN, NOMINAL_L_IN],
        'sample_size_in': [sample_in_w, sample_in_l],
        'sample_size_ft_in': [sample_size_str(sample_in_w), sample_size_str(sample_in_l)],
        'flute_count_estimate': N_FLUTES,
        'flute_pitch_mm_estimate': flute_pitch_mm,
        'flute_estimate_basis': ('autocorrelation of the fluted product photo suggested a ~4x '
                                  'repeat across the 2 in width; not an orthographic measurement'),
        'height_range_mm': HEIGHT_RANGE_MM,
        'pattern_relief_mm': pattern_relief_mm,
        'grout_relief_mm': grout_relief_mm,
        'clearance_mm': clearance_mm,
        'previews': ['_PREVIEW_tiling_remedy_hydro_fluted.jpg',
                     '_PREVIEW_grazing_light_remedy_hydro_fluted.jpg'],
    }


# ---------------------------------------------------------------------------
# Handcrafted piece, used in the FLAT role: subtle relief + grout joint only
# ---------------------------------------------------------------------------
def build_flat():
    out_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'textures')
    src = os.path.join(ROOT, 'output', 'remedy_hydro', 'references',
                        'remedy_hydro_handcrafted_2000x2000.jpg')
    im = Image.open(src).convert('RGB')
    photo = np.asarray(im, dtype=np.float64) / 255.0

    repeat_w_mm = (NOMINAL_W_IN + JOINT_IN) * MM_PER_IN
    repeat_l_mm = (NOMINAL_L_IN + JOINT_IN) * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    color_src = resize_f(np.stack([blur(photo[:, :, i], 1.2) for i in range(3)], axis=2),
                          OUT_W, OUT_H)
    color01 = np.clip(color_src, 0, 1)

    lum = photo @ np.array([.2126, .7152, .0722])
    smooth = blur(lum, 2)
    micro = smooth - blur(smooth, 60)
    scale = np.percentile(np.abs(micro), 99)
    micro01 = resize_f(0.5 + 0.07 * np.tanh(micro / max(scale, 1e-6)), OUT_W, OUT_H)

    mask = grout_mask(OUT_W, OUT_H, repeat_w_mm, repeat_l_mm, joint_mm, bevel_mm=0.8)

    HEIGHT_RANGE_MM = 0.35
    GROUT_FLOOR = 0.10
    height = np.where(mask < 1.0, GROUT_FLOOR + (micro01 - GROUT_FLOOR) * mask, micro01)

    color_out = color01 * mask[:, :, None] + color01.mean(axis=(0, 1)) * 0.55 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'remedy_hydro_flat_Color.png')
    bump_path = os.path.join(out_dir, 'remedy_hydro_flat_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_out, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)

    tiling_preview(color_out, os.path.join(out_dir, '_PREVIEW_tiling_remedy_hydro_flat.jpg'), reps=(2, 2))

    sample_in_w = NOMINAL_W_IN + JOINT_IN
    sample_in_l = NOMINAL_L_IN + JOINT_IN
    return {
        'style': ('handcrafted / undulated -- used in the FLAT role per task instruction; '
                  'Daltile Remedy does not publish a literal flat/field SKU in Hydro'),
        'source_url': ('https://s7d9.scene7.com/is/image/daltile/'
                        'DAL_RD22_2x10_Handcrafted_Hydro_GL_LivePanel_01?wid=2000&hei=2000'),
        'source_pixels': list(im.size),
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'joint_in': JOINT_IN,
        'joint_source': "Daltile Remedy-Hydro page: 'Grout Joint Recommendation: 1/8 in' (applies to all Remedy pieces)",
        'nominal_in': [NOMINAL_W_IN, NOMINAL_L_IN],
        'sample_size_in': [sample_in_w, sample_in_l],
        'sample_size_ft_in': [sample_size_str(sample_in_w), sample_size_str(sample_in_l)],
        'height_range_mm': HEIGHT_RANGE_MM,
        'grout_depth_mm': (1 - GROUT_FLOOR) * HEIGHT_RANGE_MM,
        'previews': ['_PREVIEW_tiling_remedy_hydro_flat.jpg'],
    }


REPORT['remedy_hydro_fluted'] = build_fluted()
REPORT['remedy_hydro_flat'] = build_flat()

with open(os.path.join(ROOT, 'output', 'remedy_hydro', 'source', 'build_report.json'), 'w') as f:
    json.dump(REPORT, f, indent=2, default=str)

print(json.dumps(REPORT, indent=2, default=str))
