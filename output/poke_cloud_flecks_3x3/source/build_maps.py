# -*- coding: utf-8 -*-
"""Poke Cloud Flecks, Straight Joint 3x3 Matte -- color + bump map pair.

Follows the proven procedure from output/poke_confetti_flecks_24x24 (same product line):
build ONLY from the flat, straight-on Silo swatch; never a room render, angled photo, or
installed panel (WORKFLOW.md line 30 + visual acceptance gate).

2026-09-19 correction: the first pass cropped random square regions from anywhere in the
Silo swatch, so many atlas chips accidentally straddled the SOURCE sheet's own 4x4 grid and
showed fragments of its joint lines inside a constructed chip face. Fix: detect the source
sheet's 4x4 chip grid precisely (its light-grey joint bands are trivial to find from a
per-row/per-column MEDIAN luminance profile -- median is robust to individual dark/light
flecks, unlike a mean), extract each of the 16 chip INTERIORS with a safety margin inside
the joint, and build the 8x8 delivered atlas only from random-choice/rotated/flipped copies
of those 16 interiors. No delivered crop can cross a source joint. The 1/8 in delivered
joint is drawn procedurally, as before -- never copied from the source photo.

Product facts sourced from the Daltile product page (2026-09-19):
  - Nominal chip size: 3 x 3 in
  - Grout Joint Recommendation: 1/8 in -> actual chip = 3 - 0.125 = 2.875 x 2.875 in
  - Nominal Mounted Sheet Size: 12x12 in (a 4x4 grid of 3 in chips per sheet -- visible
    directly in the accepted Silo swatch, which shows a 4x4 chip grid)
  - Mount Method: Dot Mount; straight joint, matte white terrazzo-look porcelain mosaic

Sample Size rule (mandatory, user's): Sample Size = real-world extent of every chip shown
in the image. An 8x8 chip atlas at the 3 in nominal module = 24 x 24 in = 2'-0" x 2'-0".
8x8 chosen as the minimum non-repeating atlas size per the brief. Image pixel aspect (1:1)
matches the physical aspect (24:24 = 1:1) exactly.
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
OUT_DIR = os.path.join(ROOT, 'output', 'poke_cloud_flecks_3x3', 'textures')
REF_DIR = os.path.join(ROOT, 'output', 'poke_cloud_flecks_3x3', 'references')
SRC_DIR = os.path.join(ROOT, 'output', 'poke_cloud_flecks_3x3', 'source')
os.makedirs(OUT_DIR, exist_ok=True)


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


def grout_mask_atlas(w, h, module_w_mm, module_h_mm, joint_mm, mm_per_px_x, mm_per_px_y, bevel_mm=1.0):
    """1.0 = tile face, 0.0 = grout core. Half-joint band at every internal join AND at the
    outer atlas edges, so tiling the whole atlas is seamless (two opposing half joints from
    a wrap sum to one full joint, same as two adjacent interior modules)."""
    y, x = np.mgrid[:h, :w]
    x_mm = x * mm_per_px_x
    y_mm = y * mm_per_px_y
    x_in = np.mod(x_mm, module_w_mm)
    y_in = np.mod(y_mm, module_h_mm)
    edge = np.minimum(np.minimum(x_in, module_w_mm - x_in), np.minimum(y_in, module_h_mm - y_in))
    half_joint = joint_mm / 2.0
    t = np.clip((edge - half_joint) / bevel_mm, 0, 1)
    return t * t * (3 - 2 * t), x_mm, y_mm


def tiling_preview(color01, out_path, reps=(2, 2), side=1600):
    tiled = np.tile(np.uint8(np.clip(color01, 0, 1) * 255 + .5), (reps[1], reps[0], 1))
    Image.fromarray(tiled).resize((side, max(1, int(side * tiled.shape[0] / tiled.shape[1])))).save(out_path, quality=90)


def grazing_preview(base01, height01, mm_per_px_x, mm_per_px_y, height_range_mm, out_path, reps=(2, 2), side=1600):
    dy, dx = np.gradient(height01 * height_range_mm, mm_per_px_y, mm_per_px_x)
    normals = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2)[:, :, None]
    light = np.array([-.55, .65, .3])
    light /= np.linalg.norm(light)
    shaded = np.clip(base01 * (.15 + .95 * np.maximum(0, normals @ light)[:, :, None]), 0, 1)
    tiled = np.tile(np.uint8(shaded * 255 + .5), (reps[1], reps[0], 1))
    Image.fromarray(tiled).resize((side, max(1, int(side * tiled.shape[0] / tiled.shape[1])))).save(out_path, quality=90)


def sample_size_str(sample_in):
    total_frac = Fraction(sample_in).limit_denominator(16)
    ft, rem_in = divmod(total_frac, 12)
    ft = int(ft)
    whole = int(rem_in)
    rem = rem_in - whole
    inch_str = f"{whole} {rem.numerator}/{rem.denominator}" if rem else f"{whole}"
    return f"{ft}'-{inch_str}\""


def find_joint_bands(profile_med, thresh):
    """Group consecutive indices below `thresh` (the source joint's grey plateau) into
    (start, end) bands. profile_med is a per-row or per-column MEDIAN luminance profile,
    which is robust to individual dark/light flecks (median of a mostly-tile row/column is
    the tile level; only a true joint band pulls the median down to the joint's grey level)."""
    is_joint = profile_med < thresh
    bands = []
    i, n = 0, len(profile_med)
    while i < n:
        if is_joint[i]:
            j = i
            while j < n and is_joint[j]:
                j += 1
            bands.append((i, j))
            i = j
        else:
            i += 1
    return bands


def segments_between_bands(total_len, bands, margin):
    """Interior segments strictly between/around joint bands, each shrunk by `margin` px on
    both sides for a safety buffer inside the joint (never crosses it)."""
    starts = [0] + [b[1] for b in bands]
    ends = [b[0] for b in bands] + [total_len]
    return [(s + margin, e - margin) for s, e in zip(starts, ends)]


def build():
    src_path = os.path.join(REF_DIR, 'poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01.jpg')
    im = Image.open(src_path).convert('RGB')
    photo_full = np.asarray(im, dtype=np.float64) / 255.0

    # 1) Crop to the tile-face bounding box (removes the white photography margin around the
    #    4x4 chip grid).
    whiteness = photo_full.mean(axis=2)
    tile_mask = whiteness < 0.90
    rows = np.where(tile_mask.any(axis=1))[0]
    cols = np.where(tile_mask.any(axis=0))[0]
    r0, r1 = rows.min(), rows.max()
    c0, c1 = cols.min(), cols.max()
    photo = photo_full[r0:r1, c0:c1]
    ph, pw = photo.shape[:2]
    gray = photo.mean(axis=2)

    review = Image.open(src_path).convert('RGB')
    review.thumbnail((900, 900))
    review.save(os.path.join(OUT_DIR, '_REVIEW_source_poke_cloud.jpg'), quality=88)

    # 2) Detect the source sheet's internal 4x4 grid joints from median luminance profiles.
    row_med = np.median(gray, axis=1)
    col_med = np.median(gray, axis=0)
    # Per-axis threshold roughly halfway between the typical (median) row/column level and
    # the joint's own plateau level (its minimum): robust because the joint plateau is flat
    # and constant, while the tile plateau, though speckled, has a per-row/column MEDIAN well
    # above the joint (a majority of any row/column crossing a chip is background tile, not
    # a fleck).
    row_thresh = (np.median(row_med) + row_med.min()) / 2.0
    col_thresh = (np.median(col_med) + col_med.min()) / 2.0
    tile_level, joint_level = np.median(row_med), row_med.min()
    row_bands = find_joint_bands(row_med, row_thresh)
    col_bands = find_joint_bands(col_med, col_thresh)
    if len(row_bands) != 3 or len(col_bands) != 3:
        raise RuntimeError(f'Expected 3 internal joint bands each way for a 4x4 grid, '
                            f'got {len(row_bands)} row bands and {len(col_bands)} col bands: '
                            f'{row_bands} / {col_bands}')

    MARGIN_PX = 12  # safety buffer inside each source joint, in addition to the band itself
    rsegs = segments_between_bands(ph, row_bands, MARGIN_PX)
    csegs = segments_between_bands(pw, col_bands, MARGIN_PX)

    # 3) Extract the 16 chip interiors (guaranteed joint-free) and a contact sheet for review.
    chip_interiors = []
    for (rs, re_) in rsegs:
        for (cs, ce) in csegs:
            chip_interiors.append(photo[rs:re_, cs:ce])
    contact_cell = 220
    contact = np.ones((contact_cell * 4, contact_cell * 4, 3))
    for idx, chip in enumerate(chip_interiors):
        ci = Image.fromarray(np.uint8(np.clip(chip, 0, 1) * 255)).resize((contact_cell, contact_cell))
        r, c = divmod(idx, 4)
        contact[r * contact_cell:(r + 1) * contact_cell, c * contact_cell:(c + 1) * contact_cell] = np.asarray(ci) / 255.0
    Image.fromarray(np.uint8(np.clip(contact, 0, 1) * 255)).save(
        os.path.join(OUT_DIR, '_REVIEW_chip_interiors.jpg'), quality=92)

    NOMINAL_IN = 3.0
    JOINT_IN = 1.0 / 8.0
    ACTUAL_IN = NOMINAL_IN - JOINT_IN
    TILES_X, TILES_Y = 8, 8   # minimum non-repeating atlas per brief

    module_mm = NOMINAL_IN * MM_PER_IN
    joint_mm = JOINT_IN * MM_PER_IN

    PX_PER_MODULE = 250
    OUT_W = PX_PER_MODULE * TILES_X
    OUT_H = PX_PER_MODULE * TILES_Y
    mm_per_px = module_mm / PX_PER_MODULE

    mask, x_mm, y_mm = grout_mask_atlas(OUT_W, OUT_H, module_mm, module_mm, joint_mm,
                                         mm_per_px, mm_per_px, bevel_mm=0.6)

    rng = np.random.default_rng(20260919)
    color_out = np.zeros((OUT_H, OUT_W, 3))
    micro_out = np.zeros((OUT_H, OUT_W))
    n_interiors = len(chip_interiors)
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            src_chip = chip_interiors[rng.integers(0, n_interiors)]
            k = rng.integers(0, 4)          # random 90-degree rotation
            flip = rng.integers(0, 2)       # random horizontal flip
            variant = np.rot90(src_chip, k=k, axes=(0, 1))
            if flip:
                variant = variant[:, ::-1, :]
            sub_c = np.stack([blur(variant[:, :, i], 1.0) for i in range(3)], axis=2)
            sub_c = resize_f(sub_c, PX_PER_MODULE, PX_PER_MODULE)
            lum = variant @ np.array([.2126, .7152, .0722])
            smooth = blur(lum, 1.5)
            micro = smooth - blur(smooth, 40)
            scale = np.percentile(np.abs(micro), 99) or 1e-6
            micro01 = resize_f(0.5 + 0.06 * np.tanh(micro / scale), PX_PER_MODULE, PX_PER_MODULE)
            tone = 1.0 + rng.uniform(-0.04, 0.04)
            sy, sx = ty * PX_PER_MODULE, tx * PX_PER_MODULE
            color_out[sy:sy + PX_PER_MODULE, sx:sx + PX_PER_MODULE] = np.clip(sub_c * tone, 0, 1)
            micro_out[sy:sy + PX_PER_MODULE, sx:sx + PX_PER_MODULE] = micro01

    HEIGHT_RANGE_MM = 0.35   # flat matte tile: subtle surface micro-relief + grout recess only
    GROUT_FLOOR = 0.10
    height = np.where(mask < 1.0, GROUT_FLOOR + (micro_out - GROUT_FLOOR) * mask, micro_out)
    color_final = color_out * mask[:, :, None] + color_out.mean(axis=(0, 1)) * 0.55 * (1 - mask[:, :, None])

    color_path = os.path.join(OUT_DIR, 'poke_cloud_flecks_3x3_Color.png')
    bump_path = os.path.join(OUT_DIR, 'poke_cloud_flecks_3x3_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_final, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)
    tiling_preview(color_final, os.path.join(OUT_DIR, '_PREVIEW_tiling_poke_cloud.jpg'))
    grazing_preview(color_final, height, mm_per_px, mm_per_px, HEIGHT_RANGE_MM,
                     os.path.join(OUT_DIR, '_PREVIEW_grazing_light_poke_cloud.jpg'))

    sample_w_in = NOMINAL_IN * TILES_X
    sample_h_in = NOMINAL_IN * TILES_Y
    report = {
        'source_image': ('poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01.jpg '
                          '(DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01 -- flat swatch, no scene), '
                          f'{im.size[0]}x{im.size[1]} px'),
        'grid_detection': {
            'method': 'median row/column luminance profile of the tile-face-cropped swatch; '
                      'joint bands are the plateaus below a per-axis threshold '
                      f'(row thresh {round(row_thresh, 4)}, col thresh {round(col_thresh, 4)}; '
                      f'typical tile-row/col level {round(tile_level, 4)}, '
                      f'joint plateau level {round(joint_level, 4)})',
            'row_bands_px': row_bands, 'col_bands_px': col_bands,
            'safety_margin_px': MARGIN_PX,
            'chip_interior_count': n_interiors,
            'chip_interior_sizes_px': [(re_ - rs, ce - cs) for (rs, re_) in rsegs for (cs, ce) in csegs],
        },
        'atlas_method': ('8x8 delivered atlas built only from random-choice, random 90-degree '
                          'rotation/flip, mild-tone-jitter copies of the 16 joint-free chip '
                          'interiors; no delivered crop crosses a source joint. The 1/8 in '
                          'delivered joint is drawn procedurally, not copied from the photo.'),
        'tiles_x': TILES_X, 'tiles_y': TILES_Y, 'bond': 'grid (stack bond, straight joint)',
        'module_in': [NOMINAL_IN, NOMINAL_IN],
        'actual_chip_in': [ACTUAL_IN, ACTUAL_IN],
        'joint_in': JOINT_IN,
        'sheet_nominal_in': [12.0, 12.0],
        'chips_per_sheet': [4, 4],
        'sample_size_in': [sample_w_in, sample_h_in],
        'sample_size_ft_in': [sample_size_str(sample_w_in), sample_size_str(sample_h_in)],
        'image_pixels': [OUT_W, OUT_H],
        'aspect_matches_physical': abs((OUT_W / OUT_H) - (sample_w_in / sample_h_in)) < 1e-9,
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'height_range_mm': HEIGHT_RANGE_MM,
        'grout_depth_mm': (1 - GROUT_FLOOR) * HEIGHT_RANGE_MM,
    }
    with open(os.path.join(SRC_DIR, 'build_report.json'), 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(json.dumps(report, indent=2, default=str))


if __name__ == '__main__':
    build()
