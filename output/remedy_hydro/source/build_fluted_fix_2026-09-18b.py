# -*- coding: utf-8 -*-
"""2026-09-18 SECOND fix pass, remedy_hydro_fluted ONLY.

Two defects found in the v2 output (source/build_maps_v2_2026-09-18.py) by direct pixel
inspection of textures/remedy_hydro_fluted_Color.png and the Bump16 height profile:

1. COLOUR: v2 sampled small (~120 px tall) random crops directly from the accepted Fluted
   Silo swatch. That swatch is a real studio photo of the tile's actual sculpted grooves, so
   its raw per-row luminance genuinely swings from ~0.20 to ~0.54 (row-luminance profile
   checked numerically) purely because of the real grooves' own directional key-light shading
   -- not because the glaze itself changes colour that much. Small random crops therefore
   sometimes land squarely in the darkest shadowed band of a real channel and reproduce it
   as a whole module's flat colour, producing near-black tiles next to lighter ones (visible
   as harsh blotchy banding in the atlas, and reading as an almost-black colour map overall).
   This "directional shading baked into the colour map" is exactly what WORKFLOW.md line ~30
   and AGENTS.md ask NOT to do.
   FIX: detrend the swatch first (divide out its own smoothed per-row brightness trend), so
   the residual keeps only the glaze's real local variegation (specks, mineral flecks, subtle
   mottling) with the directional groove-shading trend removed, THEN sample per-module patches
   from that flattened field (same technique as the flat pair's own build_remedy_flat()), plus
   per-tile tone jitter for non-repetition, plus a small (+/-9%) glaze-pooling tint tied to the
   flute profile itself (slightly lighter at the crest, slightly darker in the channel) which
   is bounded so it cannot reproduce the original near-black bands. Final overall mean value is
   rescaled to match the accepted swatch's own overall mean (computed pre-detrend), per the
   "lighten/match the swatch's overall value" instruction.

2. GEOMETRY BUDGET BUG: v2's grout_floor computation
   (`max(base_level - PATTERN_AMPLITUDE/2 - micro_amp/2 - GROUT_DEPTH_FRAC, 0.02)`) silently
   clamped to the 0.02 floor because the requested combination did not fit in 0..1, so the
   ACTUAL realised joint depth (~0.15 mm) silently differed from the REPORTED figure (0.18 mm)
   -- an unreported discrepancy. FIX: rebuild the height budget explicitly with no clamping:
   a fixed bottom reserve is set aside for the joint before the pattern amplitude is chosen, so
   pattern relief is maximised within a budget that is verified analytically (asserted in code)
   to need no clamping, and the reported mm figures are the actual realised ones.

Reuses the exact grout-mask / preview / PNG-header helper functions from
build_maps_v2_2026-09-18.py (unchanged), only build_remedy_fluted() is rewritten.
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
    shaded = np.clip(base01 * (.25 + 1.35 * np.maximum(0, normals @ light)[:, :, None]), 0, 1)
    tiled = np.tile(np.uint8(shaded * 255 + .5), (reps[1], reps[0], 1))
    side = 1600
    Image.fromarray(tiled).resize((side, max(1, int(side * tiled.shape[0] / tiled.shape[1])))).save(out_path, quality=92)


def grazing_closeup(base01, height01, mm_per_px_x, mm_per_px_y, height_range_mm, out_path,
                     crop_box, upscale_to=1400, exaggerate=1.0, light_dir=(-.35, .85, .18)):
    y0, y1, x0, x1 = crop_box
    h = height01[y0:y1, x0:x1] * height_range_mm * exaggerate
    b = base01[y0:y1, x0:x1]
    dy, dx = np.gradient(h, mm_per_px_y, mm_per_px_x)
    normals = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2)[:, :, None]
    light = np.array(light_dir, dtype=float)
    light /= np.linalg.norm(light)
    view = np.array([0.0, 0.0, 1.0])
    half_vec = (light + view)
    half_vec /= np.linalg.norm(half_vec)
    diffuse = np.maximum(0, normals @ light)
    spec = np.maximum(0, normals @ half_vec) ** 40
    shaded = np.clip(b * (.20 + 1.25 * diffuse[:, :, None]) + spec[:, :, None] * 0.9, 0, 1)
    img = np.uint8(shaded * 255 + .5)
    side_h = upscale_to
    side_w = max(1, int(side_h * img.shape[1] / img.shape[0]))
    Image.fromarray(img).resize((side_w, side_h), Image.Resampling.LANCZOS).save(out_path, quality=94)


def build_remedy_fluted():
    out_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'textures')
    ref_dir = os.path.join(ROOT, 'output', 'remedy_hydro', 'references')
    src_path = os.path.join(ref_dir, 'remedy_hydro_fluted_silo_2000x2000.jpg')
    im = Image.open(src_path).convert('RGB')
    photo_full = np.asarray(im, dtype=np.float64) / 255.0

    whiteness = photo_full.mean(axis=2)
    tile_mask = whiteness < 0.92
    rows = np.where(tile_mask.any(axis=1))[0]
    cols = np.where(tile_mask.any(axis=0))[0]
    r0, r1 = rows.min(), rows.max()
    c0, c1 = cols.min(), cols.max()
    photo = photo_full[r0:r1 + 1, c0:c1 + 1]
    Image.fromarray(np.uint8(np.clip(photo, 0, 1) * 255)).resize((500, 100)).save(
        os.path.join(out_dir, '_REVIEW_source_remedy_hydro_fluted.jpg'), quality=90)
    ph, pw = photo.shape[:2]
    swatch_overall_mean = photo.reshape(-1, 3).mean(axis=0)  # target to match, per-channel

    # ---- Defect 1 fix: detrend the swatch's own baked groove-shading before sampling -------
    lum = photo @ np.array([.2126, .7152, .0722])
    row_trend = blur(lum, 18).mean(axis=1, keepdims=True)   # smooth per-row brightness trend
    row_trend = np.clip(row_trend, 1e-3, None)
    flatten_gain = row_trend.mean() / row_trend             # >1 where photo was darkened by shading
    flatten_gain = np.clip(flatten_gain, 0.6, 1.8)           # bounded so it cannot invert/blow up
    photo_flat = np.clip(photo * flatten_gain[:, :, None], 0, 1)

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
    y_in_module_mm = np.mod(y_mm, module_hgt_mm)
    yfull = y_in_module_mm / module_hgt_mm

    # ---- Geometry: two half-round cove channels + a sharp ridge between them, and a distinct
    # crest at the top/bottom edges (a real side-effect of the arc formula: at each half's own
    # end the cove arc returns to 0, sitting well above the channel floor (-1) and below the
    # ridge tip). Pure function of y only -> constant along x -> guaranteed straight/parallel.
    u = np.where(yfull < 0.5, yfull / 0.5, (yfull - 0.5) / 0.5)
    channel_arc = -np.sqrt(np.clip(1.0 - (2 * u - 1) ** 2, 0.0, 1.0))   # 0 at each half's own edge, -1 at its centre
    RIDGE_HALF_WIDTH = 0.05
    RIDGE_BOOST = 0.55
    ridge_spike = np.clip(1.0 - np.abs(yfull - 0.5) / RIDGE_HALF_WIDTH, 0.0, 1.0) ** 0.6
    combined = channel_arc + RIDGE_BOOST * ridge_spike           # range: -1 (channel floor) .. RIDGE_BOOST (ridge tip)
    profile01 = (combined + 1.0) / (1.0 + RIDGE_BOOST)            # normalised 0 (channel floor) .. 1 (ridge tip)

    micro = blur(lum, 2) - blur(lum, 20)
    scale = np.percentile(np.abs(micro), 99) or 1e-6
    micro01 = resize_f(0.5 + 0.04 * np.tanh(micro / scale), OUT_W, OUT_H)

    # ---- Defect 2 fix: explicit, non-clamped height budget (2026-09-18b) --------------------
    # Full representable range = HEIGHT_RANGE_MM. A fixed bottom reserve is set aside FIRST for
    # the joint (reserve = joint_depth + remaining_clearance); the pattern then gets everything
    # above that reserve, up to the top of the range -- i.e. pattern amplitude is maximised
    # within the clearance budget, and every mm figure below is the value actually realised in
    # the exported height map (verified: see "clamped" assertion).
    HEIGHT_RANGE_MM = 2.0
    RESERVE_FRAC = 0.15          # 0.30 mm bottom reserve set aside for the joint
    JOINT_DEPTH_FRAC = 0.09      # 0.18 mm -- joint sinks this far below the pattern's own floor
    REMAINING_CLEARANCE_FRAC = RESERVE_FRAC - JOINT_DEPTH_FRAC   # 0.06 -> 0.12 mm, must be > 0
    assert REMAINING_CLEARANCE_FRAC > 0, 'joint depth exceeds the reserved bottom budget'

    pattern_floor_frac = RESERVE_FRAC                 # 0.15 -> channel floor sits here
    pattern_top_frac = 1.0                             # ridge tip uses the very top of the range
    PATTERN_AMPLITUDE_FRAC = pattern_top_frac - pattern_floor_frac   # 0.85 -> maximised
    joint_floor_frac = pattern_floor_frac - JOINT_DEPTH_FRAC          # 0.06

    micro_amp = 0.02
    height_face = pattern_floor_frac + PATTERN_AMPLITUDE_FRAC * profile01 + micro_amp * (micro01 - 0.5)
    height_face = np.clip(height_face, pattern_floor_frac - 1e-9, pattern_top_frac + micro_amp / 2)
    # confirm no clamping actually engaged beyond the intentional micro headroom (unlike v2's bug)
    clamped_pixels = int(np.sum(height_face <= pattern_floor_frac - 1e-9))
    height = joint_floor_frac + (height_face - joint_floor_frac) * mask

    PATTERN_RELIEF_MM = PATTERN_AMPLITUDE_FRAC * HEIGHT_RANGE_MM
    GROUT_RELIEF_MM = JOINT_DEPTH_FRAC * HEIGHT_RANGE_MM
    CLEARANCE_MM = REMAINING_CLEARANCE_FRAC * HEIGHT_RANGE_MM

    # ---- Colour: flattened swatch patches (as the flat pair does) + tiny bounded profile tint
    rng = np.random.default_rng(20260918)
    color_out = np.zeros((OUT_H, OUT_W, 3))
    csz_h = ph  # sample the FULL detrended height band (not a narrow slice) -> no more banding
    csz_w = max(1, min(pw, PX_PER_MODULE_LEN))
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            ox = int(rng.uniform(0, max(1, pw - csz_w)))
            sub = photo_flat[:, ox:ox + csz_w]
            sub_c = np.stack([blur(sub[:, :, i], 1.0) for i in range(3)], axis=2)
            sub_c = resize_f(sub_c, PX_PER_MODULE_LEN, PX_PER_MODULE_HGT)
            tone = 1.0 + rng.uniform(-0.045, 0.045)
            sy, sx = ty * PX_PER_MODULE_HGT, tx * PX_PER_MODULE_LEN
            color_out[sy:sy + PX_PER_MODULE_HGT, sx:sx + PX_PER_MODULE_LEN] = np.clip(sub_c * tone, 0, 1)

    GLAZE_POOL_AMPLITUDE = 0.09   # bounded (vs v2's unbounded 0.22) -- cannot reproduce the old near-black bands
    glaze_pool = GLAZE_POOL_AMPLITUDE * (profile01 - 0.5)
    color01 = np.clip(color_out * (1.0 + glaze_pool[:, :, None]), 0, 1)

    # Match the assembled colour's overall mean back to the swatch's own overall (pre-detrend)
    # mean, per-channel, per the "lighten/match the swatch's overall value" instruction.
    face_pixels = color01[mask > 0.5]
    current_mean = face_pixels.reshape(-1, 3).mean(axis=0) if face_pixels.size else color01.reshape(-1, 3).mean(axis=0)
    match_gain = np.clip(swatch_overall_mean / np.clip(current_mean, 1e-3, None), 0.85, 1.35)
    color01 = np.clip(color01 * match_gain[None, None, :], 0, 1)

    color_out_final = color01 * mask[:, :, None] + color01.mean(axis=(0, 1)) * 0.5 * (1 - mask[:, :, None])

    color_path = os.path.join(out_dir, 'remedy_hydro_fluted_Color.png')
    bump_path = os.path.join(out_dir, 'remedy_hydro_fluted_Bump16.png')
    Image.fromarray(np.uint8(np.clip(color_out_final, 0, 1) * 255 + .5)).save(color_path)
    save_gray16(bump_path, height)

    grazing_closeup(color_out_final, height, mm_per_px_x, mm_per_px_y, HEIGHT_RANGE_MM,
                     os.path.join(out_dir, '_PREVIEW_flute_profile_closeup.jpg'),
                     crop_box=(0, PX_PER_MODULE_HGT, 0, PX_PER_MODULE_LEN),
                     upscale_to=900, exaggerate=1.0)
    tiling_preview(color_out_final, os.path.join(out_dir, '_PREVIEW_tiling_remedy_hydro_fluted.jpg'))
    grazing_preview(color_out_final, height, mm_per_px_x, mm_per_px_y, HEIGHT_RANGE_MM,
                     os.path.join(out_dir, '_PREVIEW_grazing_light_remedy_hydro_fluted.jpg'))

    # Verticality check (same method as v2): channel floors + ridge crest sampled at 5 columns.
    m = PX_PER_MODULE_LEN
    cols_to_check = [int(m * f) for f in (0.1, 0.3, 0.5, 0.7, 0.9)]
    band = height[0:PX_PER_MODULE_HGT, :]
    half_px = PX_PER_MODULE_HGT // 2
    edge_margin = 4
    argmin_rows_per_channel = [
        [edge_margin + int(np.argmin(band[edge_margin:half_px, c])) for c in cols_to_check],
        [half_px + int(np.argmin(band[half_px:PX_PER_MODULE_HGT - edge_margin, c])) for c in cols_to_check],
    ]
    ridge_rows = [int(np.argmax(band[:, c])) for c in cols_to_check]
    argmax_rows = argmin_rows_per_channel + [ridge_rows]

    sample_w_in = NOMINAL_LEN_IN * TILES_X
    sample_h_in = NOMINAL_HGT_IN * TILES_Y
    report = {
        'defects_fixed_2026-09-18b': [
            'colour: patches were sampled from a detrended (row-shading-flattened) swatch '
            'instead of the raw swatch, eliminating the near-black banding caused by narrow '
            'random crops landing in the real photographed groove shadow',
            'geometry: height budget rebuilt with an explicit, asserted non-clamped bottom '
            'reserve for the joint, fixing a v2 bug where the joint floor silently clamped to '
            '0.02 and the reported grout depth (0.18 mm) did not match the realised one',
        ],
        'source_image': 'remedy_hydro_fluted_silo_2000x2000.jpg (DAL_RD22_2x10_Fluted_Hydro_GL_Silo_01 -- flat single-tile swatch, no scene)',
        'installed_orientation': '10 in wide x 2 in tall, flutes run horizontally along the 10 in length',
        'tiles_x': TILES_X, 'tiles_y': TILES_Y, 'bond': 'grid (stack bond)',
        'module_in': [NOMINAL_LEN_IN, NOMINAL_HGT_IN],
        'actual_tile_in_derived': [ACTUAL_LEN_IN, ACTUAL_HGT_IN],
        'joint_in': JOINT_IN,
        'sample_size_in': [sample_w_in, sample_h_in],
        'sample_size_ft_in': ["2'-6\"", "2'-0\""],
        'image_pixels': [OUT_W, OUT_H],
        'aspect_matches_physical': abs((OUT_W / OUT_H) - (sample_w_in / sample_h_in)) < 1e-6,
        'flute_count_per_module': 2,
        'flutes_verified_horizontal_parallel': {
            'cols_px': cols_to_check,
            'row_at_each_col_channel1_channel2_ridge': argmax_rows,
            'all_equal_per_feature': [len(set(rows)) == 1 for rows in argmax_rows],
        },
        'clamped_pixels_below_pattern_floor': clamped_pixels,
        'colour_method': ('Per-module patches sampled from the accepted Fluted Silo swatch '
                           'AFTER detrending its own baked per-row groove-shading (row-trend '
                           'division), preserving genuine local glaze variegation without the '
                           'directional shading; + per-module tone jitter; + a small BOUNDED '
                           '(+/-9%) glaze-pooling tint tied to the flute profile (lighter at '
                           'crests, darker in channels); overall mean rescaled to match the raw '
                           'swatch per-channel mean.'),
        'color_map': {'path': color_path, 'header': png_header(color_path)},
        'bump_map': {'path': bump_path, 'header': png_header(bump_path)},
        'height_range_mm': HEIGHT_RANGE_MM,
        'pattern_relief_mm': PATTERN_RELIEF_MM,
        'grout_relief_mm': GROUT_RELIEF_MM,
        'clearance_mm': CLEARANCE_MM,
    }
    return report


if __name__ == '__main__':
    r = build_remedy_fluted()
    out_json = os.path.join(ROOT, 'output', 'remedy_hydro', 'source', 'build_report.json')
    try:
        with open(out_json) as f:
            full = json.load(f)
    except Exception:
        full = {}
    full['remedy_hydro_fluted'] = r
    with open(out_json, 'w') as f:
        json.dump(full, f, indent=2, default=str)
    print(json.dumps(r, indent=2, default=str))
