# -*- coding: utf-8 -*-
"""2026-09-18 fix pass v2, all three Daltile map pairs (Poke, Remedy fluted, Remedy flat).

Supersedes build_all.py. Two additional defects found by visual review of v1 output and
fixed here, on top of the flute-geometry and Sample-Size-double-counting fixes:

3. Source-image defect: the ORIGINAL references used for all three pairs were scene/room
   renders (Poke: full bathroom with fixtures/shadows/reflections; Remedy Fluted: a multi-row
   wall panel in perspective, ~3 columns x 20 rows of tiles with a dark frame baked around it,
   mislabelled as a single tile). Fix: switched to Daltile's plain flat "Silo" swatch images
   for all three pieces (single-tile, straight-on, no room, no perspective, no baked lighting):
     - Poke:        DAL_PK23_24x24_ConfettiFlecks_MT_Silo_01
     - Fluted:      DAL_RD22_2x10_Fluted_Hydro_GL_Silo_01
     - Handcrafted: DAL_RD22_2x10_Handcrafted_Hydro_GL_Silo_01
   `_REVIEW_source_<pair>.jpg` is saved per pair showing exactly the swatch used.

4. Flute-count correction from real imagery: the Fluted Silo swatch (a single 2x10 tile,
   installed-orientation: 10 in wide x 2 in tall) clearly shows TWO rounded flute ridges
   stacked across the 2 in tall dimension, running the full 10 in length -- not the earlier
   single-flute guess and not the original discredited 4-flute autocorrelation estimate. This
   is now a sourced-from-a-straight-on-photo fact, not an assumption.

5. Installed orientation + atlas: Remedy 2x10 installs HORIZONTALLY (10 in wide x 2 in tall),
   flutes running along the 10 in length. Atlas built in that orientation, stack bond
   (simplest full-bleed grid; not a running/staggered bond -- stated explicitly, since no
   bond pattern is specified by Daltile), 3 tiles wide x 12 rows tall = 30 x 24 in total,
   matching the coordinator's own worked example. Poke atlas stays 3x3 of the 24x24 in module.
   Every image's pixel aspect ratio is set equal to its total physical (Sample Size) aspect.
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


def grout_mask_atlas(w, h, module_w_mm, module_h_mm, joint_mm, mm_per_px_x, mm_per_px_y, bevel_mm=0.8):
    """1.0 = tile face, 0.0 = grout core. Modulo construction repeats a half-joint-per-edge
    band at every internal module join AND at the outer atlas edges, so tiling the whole
    atlas is seamless (two opposing half joints from a wrap sum to one full joint, same as
    two adjacent interior modules)."""
    y, x = np.mgrid[:h, :w]
    x_mm = x * mm_per_px_x
    y_mm = y * mm_per_px_y
    x_in = np.mod(x_mm, module_w_mm)
    y_in = np.mod(y_mm, module_h_mm)
    edge = np.minimum(np.minimum(x_in, module_w_mm - x_in), np.minimum(y_in, module_h_mm - y_in))
    half_joint = joint_mm / 2.0
    t = np.clip((edge - half_joint) / bevel_mm, 0, 1)
    return t * t * (3 - 2 * t), x_mm, y_mm


def tiling_preview(color01, out_path, reps=(2, 2)):
    tiled = np.tile(np.uint8(np.clip(color01, 0, 1) * 255 + .5), (reps[1], reps[0], 1))
    side = 1600
    Image.fromarray(tiled).resize((side, max(1, int(side * tiled.shape[0] / tiled.shape[1])))).save(out_path, quality=92)


def grazing_preview(base01, height01, mm_per_px_x, mm_per_px_y, height_range_mm, out_path, reps=(2, 2)):
    dy, dx = np.gradient(height01 * height_range_mm, mm_per_px_y, mm_per_px_x)
    normals = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2)[:, :, None]
    light = np.array([-.55, .65, .3])
    light /= np.linalg.norm(light)
    shaded = np.clip(base01 * (.15 + .95 * np.maximum(0, normals @ light)[:, :, None]), 0, 1)
    tiled = np.tile(np.uint8(shaded * 255 + .5), (reps[1], reps[0], 1))
    side = 1600
    Image.fromarray(tiled).resize((side, max(1, int(side * tiled.shape[0] / tiled.shape[1])))).save(out_path, quality=92)


def sample_size_str(sample_in):
    total_frac = Fraction(sample_in).limit_denominator(16)
    ft, rem_in = divmod(total_frac, 12)
    ft = int(ft)
    whole = int(rem_in)
    rem = rem_in - whole
    inch_str = f"{whole} {rem.numerator}/{rem.denominator}" if rem else f"{whole}"
    return f"{ft}'-{inch_str}\""


REPORT = {}

# =============================================================================
# 1) POKE Confetti Flecks 24x24 -- flat Silo swatch, 3x3 atlas of the 24x24 in module
# =============================================================================
def build_poke():
    out_dir = os.path.join(ROOT, 'output', 'poke_confetti_flecks_24x24', 'textures')
    ref_dir = os.path.join(ROOT, 'output', 'poke_confetti_flecks_24x24', 'references')
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(ref_dir, 'poke_confetti_flecks_24x24_silo_3000x3000.jpg')
    im = Image.open(src).convert('RGB')
    photo = np.asarray(im, dtype=np.float64) / 255.0
    ph, pw = photo.shape[:2]
    im.resize((500, 500)).save(os.path.join(out_dir, '_REVIEW_source_poke.jpg'), quality=90)

    NOMINAL_IN = 24.0
    ACTUAL_IN = 23.81
    JOINT_IN = NOMINAL_IN - ACTUAL_IN
    TILES_X, TILES_Y = 3, 3

    module_mm = NOMINAL_IN * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    PX_PER_MODULE = 700
    OUT_W = PX_PER_MODULE * TILES_X
    OUT_H = PX_PER_MODULE * TILES_Y
    mm_per_px = module_mm / PX_PER_MODULE

    mask, x_mm, y_mm = grout_mask_atlas(OUT_W, OUT_H, module_mm, module_mm, joint_mm,
                                         mm_per_px, mm_per_px, bevel_mm=1.2)

    rng = np.random.default_rng(20260918)
    color_out = np.zeros((OUT_H, OUT_W, 3))
    micro_out = np.zeros((OUT_H, OUT_W))
    csz = int(min(ph, pw) * 0.55)
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            oy = int(rng.uniform(0, ph - csz))
            ox = int(rng.uniform(0, pw - csz))
            sub = photo[oy:oy + csz, ox:ox + csz]
            sub_c = np.stack([blur(sub[:, :, i], 1.5) for i in range(3)], axis=2)
            sub_c = resize_f(sub_c, PX_PER_MODULE, PX_PER_MODULE)
            lum = sub @ np.array([.2126, .7152, .0722])
            smooth = blur(lum, 2)
            micro = smooth - blur(smooth, 60)
            scale = np.percentile(np.abs(micro), 99) or 1e-6
            micro01 = resize_f(0.5 + 0.06 * np.tanh(micro / scale), PX_PER_MODULE, PX_PER_MODULE)
            tone = 1.0 + rng.uniform(-0.04, 0.04)
            sy, sx = ty * PX_PER_MODULE, tx * PX_PER_MODULE
            color_out[sy:sy + PX_PER_MODULE, sx:sx + PX_PER_MODULE] = np.clip(sub_c * tone, 0, 1)
            micro_out[sy:sy + PX_PER_MODULE, sx:sx + PX_PER_MODULE] = micro01

    HEIGHT_RANGE_MM = 0.35
    GROUT_FLOOR = 0.10
    height = np.where(mask < 1.0, GROUT_FLOOR + (micro_out - GROUT_FLOOR) * mask, micro_out)
    color_final = color_out * mask[:, :, None] + color_out.mean(axis=(0, 1)) * 0.55 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'poke_confetti_flecks_24x24_Color.png')
    bump_path = os.path.join(out_dir, 'poke_confetti_flecks_24x24_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_final, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)
    tiling_preview(color_final, os.path.join(out_dir, '_PREVIEW_tiling_poke.jpg'))
    grazing_preview(color_final, height, mm_per_px, mm_per_px, HEIGHT_RANGE_MM,
                     os.path.join(out_dir, '_PREVIEW_grazing_light_poke.jpg'))

    sample_w_in = NOMINAL_IN * TILES_X
    sample_h_in = NOMINAL_IN * TILES_Y
    return {
        'source_image': 'poke_confetti_flecks_24x24_silo_3000x3000.jpg (DAL_PK23_24x24_ConfettiFlecks_MT_Silo_01 -- flat swatch, no scene)',
        'tiles_x': TILES_X, 'tiles_y': TILES_Y, 'bond': 'grid (stack bond)',
        'module_in': [NOMINAL_IN, NOMINAL_IN],
        'actual_tile_in': [ACTUAL_IN, ACTUAL_IN],
        'joint_in': JOINT_IN,
        'sample_size_in': [sample_w_in, sample_h_in],
        'sample_size_ft_in': [sample_size_str(sample_w_in), sample_size_str(sample_h_in)],
        'image_pixels': [OUT_W, OUT_H],
        'aspect_matches_physical': abs((OUT_W / OUT_H) - (sample_w_in / sample_h_in)) < 1e-9,
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'height_range_mm': HEIGHT_RANGE_MM,
        'grout_depth_mm': (1 - GROUT_FLOOR) * HEIGHT_RANGE_MM,
    }


# =============================================================================
# 2) REMEDY HYDRO FLUTED -- flat Silo swatch, installed horizontally (10in wide x 2in tall),
#    2 flutes across the 2in height (sourced from the swatch), 3x12 atlas = 30x24 in
# =============================================================================
def build_remedy_fluted():
    out_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'textures')
    ref_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'references')
    src_path = os.path.join(ref_dir, 'remedy_hydro_fluted_silo_2000x2000.jpg')
    im = Image.open(src_path).convert('RGB')
    photo_full = np.asarray(im, dtype=np.float64) / 255.0

    # Crop the silo image down to just the tile face (the source is a 2000x2000 canvas with
    # a large white margin around a centered horizontal tile). Find the tile's bounding box
    # via a saturation/luminance-difference-from-white mask.
    whiteness = photo_full.mean(axis=2)
    tile_mask = whiteness < 0.92
    rows = np.where(tile_mask.any(axis=1))[0]
    cols = np.where(tile_mask.any(axis=0))[0]
    r0, r1 = rows.min(), rows.max()
    c0, c1 = cols.min(), cols.max()
    photo = photo_full[r0:r1 + 1, c0:c1 + 1]
    Image.fromarray(np.uint8(np.clip(photo, 0, 1) * 255)).resize((500, 100)).save(
        os.path.join(out_dir, '_REVIEW_source_remedy_hydro_fluted.jpg'), quality=90)

    NOMINAL_LEN_IN, NOMINAL_HGT_IN = 10.0, 2.0   # installed orientation: 10 in wide x 2 in tall
    JOINT_IN = 1.0 / 8.0
    ACTUAL_LEN_IN = NOMINAL_LEN_IN - JOINT_IN
    ACTUAL_HGT_IN = NOMINAL_HGT_IN - JOINT_IN
    TILES_X, TILES_Y = 3, 12   # 3 wide x 12 rows -> 30 x 24 in total

    module_len_mm = NOMINAL_LEN_IN * MM_PER_IN
    module_hgt_mm = NOMINAL_HGT_IN * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    PX_PER_MODULE_LEN = 600
    PX_PER_MODULE_HGT = int(round(PX_PER_MODULE_LEN * NOMINAL_HGT_IN / NOMINAL_LEN_IN))
    OUT_W = PX_PER_MODULE_LEN * TILES_X
    OUT_H = PX_PER_MODULE_HGT * TILES_Y
    mm_per_px_x = module_len_mm / PX_PER_MODULE_LEN
    mm_per_px_y = module_hgt_mm / PX_PER_MODULE_HGT

    mask, x_mm, y_mm = grout_mask_atlas(OUT_W, OUT_H, module_len_mm, module_hgt_mm, joint_mm,
                                         mm_per_px_x, mm_per_px_y, bevel_mm=0.6)
    y_in_module_mm = np.mod(y_mm, module_hgt_mm)

    # 2 half-round flutes stacked across the 2 in tall dimension, sourced directly from the
    # flat Silo swatch (see module docstring). Function of y (height) only -> constant along
    # x (the 10 in length) -> geometrically vertical/parallel ridges when the tile is read
    # in its installed horizontal orientation (ridges run horizontally the full length,
    # perfectly parallel to each other and to the tile edges).
    N_FLUTES = 2
    flute_pitch_mm = module_hgt_mm / N_FLUTES
    yfrac_in_flute = np.mod(y_in_module_mm, flute_pitch_mm) / flute_pitch_mm
    d = (yfrac_in_flute - 0.5) * 2.0
    radial = np.sqrt(np.clip(1.0 - d * d, 0.0, 1.0))

    lum = photo @ np.array([.2126, .7152, .0722])
    micro = blur(lum, 2) - blur(lum, 20)
    scale = np.percentile(np.abs(micro), 99) or 1e-6
    micro01 = resize_f(0.5 + 0.04 * np.tanh(micro / scale), OUT_W, OUT_H)

    HEIGHT_RANGE_MM = 1.0
    PATTERN_AMPLITUDE = 0.55
    GROUT_DEPTH_FRAC = 0.18
    micro_amp = 0.06
    pattern_component = PATTERN_AMPLITUDE * (radial - 0.5) + micro_amp * (micro01 - 0.5)
    base_level = 0.5
    height_face = np.clip(base_level + pattern_component,
                           base_level - PATTERN_AMPLITUDE / 2 - micro_amp / 2,
                           base_level + PATTERN_AMPLITUDE / 2 + micro_amp / 2)
    grout_floor = max(base_level - PATTERN_AMPLITUDE / 2 - micro_amp / 2 - GROUT_DEPTH_FRAC, 0.02)
    height = grout_floor + (height_face - grout_floor) * mask

    base_rgb = np.median(photo.reshape(-1, 3), axis=0)
    lowfreq = blur(lum, 60)
    lowfreq -= lowfreq.mean()
    lf_scale = np.percentile(np.abs(lowfreq), 99) or 1.0
    lowfreq_rs = resize_f(np.clip(lowfreq / lf_scale, -1, 1), OUT_W, OUT_H)

    rng = np.random.default_rng(20260918)
    speckle = rng.normal(0, 1, size=(max(1, OUT_H // 4), max(1, OUT_W // 4)))
    speckle = resize_f(speckle, OUT_W, OUT_H)
    speckle = (speckle - speckle.mean()) / (speckle.std() + 1e-6)

    tile_ix = np.floor(x_mm / module_len_mm).astype(int)
    tile_iy = np.floor(y_mm / module_hgt_mm).astype(int)
    per_tile_jitter = rng.uniform(-0.045, 0.045, size=(TILES_Y, TILES_X))
    tile_tone = per_tile_jitter[np.clip(tile_iy, 0, TILES_Y - 1), np.clip(tile_ix, 0, TILES_X - 1)]

    tone = 1.0 + 0.05 * lowfreq_rs + 0.012 * speckle + tile_tone
    color01 = np.clip(base_rgb[None, None, :] * tone[:, :, None], 0, 1)
    color_out = color01 * mask[:, :, None] + color01.mean(axis=(0, 1)) * 0.5 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'remedy_hydro_fluted_Color.png')
    bump_path = os.path.join(out_dir, 'remedy_hydro_fluted_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_out, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)
    tiling_preview(color_out, os.path.join(out_dir, '_PREVIEW_tiling_remedy_hydro_fluted.jpg'))
    grazing_preview(color_out, height, mm_per_px_x, mm_per_px_y, HEIGHT_RANGE_MM,
                     os.path.join(out_dir, '_PREVIEW_grazing_light_remedy_hydro_fluted.jpg'))

    # Sample columns inside the tile FACE only (avoid the joint band at the module edges,
    # which is grout, not flute, and would falsely look like a verticality mismatch).
    m = PX_PER_MODULE_LEN
    cols_to_check = [int(m * f) for f in (0.1, 0.3, 0.5, 0.7, 0.9)]
    band = height[0:PX_PER_MODULE_HGT, :]  # first module row only, verticality within one tile
    pitch_px = PX_PER_MODULE_HGT / N_FLUTES
    # Check each flute ridge independently (its local argmax within its own sub-band), since
    # the two flutes' peak heights can differ by the small micro-texture term and a global
    # argmax across both would jump between them and falsely read as "not parallel".
    argmax_rows_per_flute = []
    for k in range(N_FLUTES):
        r0 = int(round(k * pitch_px))
        r1 = int(round((k + 1) * pitch_px))
        sub_band = band[r0:r1, :]
        argmax_rows_per_flute.append([r0 + int(np.argmax(sub_band[:, c])) for c in cols_to_check])
    argmax_rows = argmax_rows_per_flute

    sample_w_in = NOMINAL_LEN_IN * TILES_X
    sample_h_in = NOMINAL_HGT_IN * TILES_Y
    return {
        'source_image': 'remedy_hydro_fluted_silo_2000x2000.jpg (DAL_RD22_2x10_Fluted_Hydro_GL_Silo_01 -- flat single-tile swatch, no scene)',
        'installed_orientation': '10 in wide x 2 in tall, flutes run horizontally along the 10 in length',
        'tiles_x': TILES_X, 'tiles_y': TILES_Y, 'bond': 'grid (stack bond) -- no Daltile-specified bond pattern found, so the simplest full-bleed grid was used',
        'module_in': [NOMINAL_LEN_IN, NOMINAL_HGT_IN],
        'actual_tile_in_derived': [ACTUAL_LEN_IN, ACTUAL_HGT_IN],
        'joint_in': JOINT_IN,
        'sample_size_in': [sample_w_in, sample_h_in],
        'sample_size_ft_in': [sample_size_str(sample_w_in), sample_size_str(sample_h_in)],
        'image_pixels': [OUT_W, OUT_H],
        'aspect_matches_physical': abs((OUT_W / OUT_H) - (sample_w_in / sample_h_in)) < 1e-6,
        'flute_count_per_module': N_FLUTES,
        'flute_profile': 'half-round (semicircular cross-section)',
        'flute_count_source': (
            'Directly visible in the flat, straight-on Silo swatch (single tile, no '
            'perspective): two rounded ridges stacked across the 2 in tall dimension. This '
            'replaces both the original angled-photo autocorrelation estimate (4 flutes) and '
            'the interim single-flute guess made before the flat swatch was located.'),
        'flutes_verified_horizontal_parallel': {
            'method': 'argmax row of bump-map ridge centre sampled at 5 columns across one module (top module row)',
            'cols_px': cols_to_check, 'ridge_row_at_each_col_per_flute': argmax_rows,
            'all_equal_per_flute': [len(set(rows)) == 1 for rows in argmax_rows],
        },
        'colour_method': ('Robust median base colour from the flat Fluted Silo swatch itself '
                           '(cropped to the tile face, white margin removed) + large-scale '
                           'non-directional mottling + per-module tone jitter; no directional shading baked in.'),
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'height_range_mm': HEIGHT_RANGE_MM,
        'pattern_relief_mm': PATTERN_AMPLITUDE * HEIGHT_RANGE_MM,
        'grout_relief_mm': GROUT_DEPTH_FRAC * HEIGHT_RANGE_MM,
        'clearance_mm': (PATTERN_AMPLITUDE - GROUT_DEPTH_FRAC) * HEIGHT_RANGE_MM,
    }


# =============================================================================
# 3) REMEDY HYDRO FLAT (Handcrafted, flat role) -- flat Silo swatch, same 3x12 atlas/module
# =============================================================================
def build_remedy_flat():
    out_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'textures')
    ref_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'references')
    src_path = os.path.join(ref_dir, 'remedy_hydro_handcrafted_silo_2000x2000.jpg')
    im = Image.open(src_path).convert('RGB')
    photo_full = np.asarray(im, dtype=np.float64) / 255.0

    whiteness = photo_full.mean(axis=2)
    tile_mask = whiteness < 0.92
    rows = np.where(tile_mask.any(axis=1))[0]
    cols = np.where(tile_mask.any(axis=0))[0]
    r0, r1 = rows.min(), rows.max()
    c0, c1 = cols.min(), cols.max()
    photo = photo_full[r0:r1 + 1, c0:c1 + 1]
    ph, pw = photo.shape[:2]
    Image.fromarray(np.uint8(np.clip(photo, 0, 1) * 255)).resize((500, 100)).save(
        os.path.join(out_dir, '_REVIEW_source_remedy_hydro_flat.jpg'), quality=90)

    NOMINAL_LEN_IN, NOMINAL_HGT_IN = 10.0, 2.0
    JOINT_IN = 1.0 / 8.0
    ACTUAL_LEN_IN = NOMINAL_LEN_IN - JOINT_IN
    ACTUAL_HGT_IN = NOMINAL_HGT_IN - JOINT_IN
    TILES_X, TILES_Y = 3, 12

    module_len_mm = NOMINAL_LEN_IN * MM_PER_IN
    module_hgt_mm = NOMINAL_HGT_IN * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    PX_PER_MODULE_LEN = 600
    PX_PER_MODULE_HGT = int(round(PX_PER_MODULE_LEN * NOMINAL_HGT_IN / NOMINAL_LEN_IN))
    OUT_W = PX_PER_MODULE_LEN * TILES_X
    OUT_H = PX_PER_MODULE_HGT * TILES_Y
    mm_per_px_x = module_len_mm / PX_PER_MODULE_LEN
    mm_per_px_y = module_hgt_mm / PX_PER_MODULE_HGT

    mask, x_mm, y_mm = grout_mask_atlas(OUT_W, OUT_H, module_len_mm, module_hgt_mm, joint_mm,
                                         mm_per_px_x, mm_per_px_y, bevel_mm=0.6)

    rng = np.random.default_rng(20260918 + 1)
    color_out = np.zeros((OUT_H, OUT_W, 3))
    micro_out = np.zeros((OUT_H, OUT_W))
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            oy = int(rng.uniform(0, max(1, ph - PX_PER_MODULE_HGT)))
            ox = int(rng.uniform(0, max(1, pw - PX_PER_MODULE_LEN // 2)))
            sub = photo[oy:oy + min(PX_PER_MODULE_HGT, ph), ox:ox + min(PX_PER_MODULE_LEN, pw - ox)]
            sub_c = np.stack([blur(sub[:, :, i], 1.2) for i in range(min(3, sub.shape[2]))], axis=2)
            sub_c = resize_f(sub_c, PX_PER_MODULE_LEN, PX_PER_MODULE_HGT)
            lum = sub @ np.array([.2126, .7152, .0722])
            smooth = blur(lum, 2)
            micro = smooth - blur(smooth, 40)
            scale = np.percentile(np.abs(micro), 99) or 1e-6
            micro01 = resize_f(0.5 + 0.07 * np.tanh(micro / scale), PX_PER_MODULE_LEN, PX_PER_MODULE_HGT)
            tone = 1.0 + rng.uniform(-0.04, 0.04)
            sy, sx = ty * PX_PER_MODULE_HGT, tx * PX_PER_MODULE_LEN
            color_out[sy:sy + PX_PER_MODULE_HGT, sx:sx + PX_PER_MODULE_LEN] = np.clip(sub_c * tone, 0, 1)
            micro_out[sy:sy + PX_PER_MODULE_HGT, sx:sx + PX_PER_MODULE_LEN] = micro01

    HEIGHT_RANGE_MM = 0.35
    GROUT_FLOOR = 0.10
    height = np.where(mask < 1.0, GROUT_FLOOR + (micro_out - GROUT_FLOOR) * mask, micro_out)
    color_final = color_out * mask[:, :, None] + color_out.mean(axis=(0, 1)) * 0.55 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'remedy_hydro_flat_Color.png')
    bump_path = os.path.join(out_dir, 'remedy_hydro_flat_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_final, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)
    tiling_preview(color_final, os.path.join(out_dir, '_PREVIEW_tiling_remedy_hydro_flat.jpg'))

    sample_w_in = NOMINAL_LEN_IN * TILES_X
    sample_h_in = NOMINAL_HGT_IN * TILES_Y
    return {
        'source_image': 'remedy_hydro_handcrafted_silo_2000x2000.jpg (DAL_RD22_2x10_Handcrafted_Hydro_GL_Silo_01 -- flat single-tile swatch, no scene)',
        'installed_orientation': '10 in wide x 2 in tall',
        'tiles_x': TILES_X, 'tiles_y': TILES_Y, 'bond': 'grid (stack bond)',
        'module_in': [NOMINAL_LEN_IN, NOMINAL_HGT_IN],
        'actual_tile_in_derived': [ACTUAL_LEN_IN, ACTUAL_HGT_IN],
        'joint_in': JOINT_IN,
        'sample_size_in': [sample_w_in, sample_h_in],
        'sample_size_ft_in': [sample_size_str(sample_w_in), sample_size_str(sample_h_in)],
        'image_pixels': [OUT_W, OUT_H],
        'aspect_matches_physical': abs((OUT_W / OUT_H) - (sample_w_in / sample_h_in)) < 1e-6,
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'height_range_mm': HEIGHT_RANGE_MM,
        'grout_depth_mm': (1 - GROUT_FLOOR) * HEIGHT_RANGE_MM,
    }


REPORT['poke_confetti_flecks_24x24'] = build_poke()
REPORT['remedy_hydro_fluted'] = build_remedy_fluted()
REPORT['remedy_hydro_flat'] = build_remedy_flat()

poke_report_path = os.path.join(ROOT, 'output', 'poke_confetti_flecks_24x24', 'source', 'build_report.json')
with open(poke_report_path, 'w') as f:
    json.dump(REPORT['poke_confetti_flecks_24x24'], f, indent=2, default=str)

remedy_report_path = os.path.join(ROOT, 'output', 'remedy_hydro', 'source', 'build_report.json')
with open(remedy_report_path, 'w') as f:
    json.dump({'remedy_hydro_fluted': REPORT['remedy_hydro_fluted'],
               'remedy_hydro_flat': REPORT['remedy_hydro_flat']}, f, indent=2, default=str)

print(json.dumps(REPORT, indent=2, default=str))
