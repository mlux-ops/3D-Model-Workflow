"""Build the ELM ElmStone Jute Vein-Cut 24x48 (MILE stone EcoStone Vein-Cut Jute, SKU 1104304) colour (8-bit
sRGB) and bump (16-bit grey) maps, STACK BOND, long side horizontal, veins horizontal.

Facts and assumptions (README.md, SOURCE_SELECTION.md):
  * actual size not published by ELM or MILE stone (product pages, ElmStone catalog, EcoStone brochure, tech
    specs, 2026-09-26). MILE stone is Florim USA (metric production); used the 600 x 1200 mm rectified
    convention = 23.622 x 47.244 in, stated as an assumption.
  * joint 1/8 in: no manufacturer recommendation published; 1/8 in used as an assumption (the MILE panel
    mock-up draws ~1/16 in, which is a rendering, not installation guidance).
  * drawn tile 47.2083 x 23.625 in (-0.91 mm / +0.08 mm vs actual, both < 0.1 %) so that 3 x 6 tiles give a
    Sample Size of exactly 142.00 x 142.50 in (11'-10" x 11'-10 1/2"); Revit's Texture Editor rounds
    Sample Size to the project's 1/4 in.
  * colour: 100 % real photo pixels. Six distinct printed faces (A, B, W1..W4, a07_faces.py), each used in
    three different orientation-preserving transforms (r0 / flipH / flipV / r180, veins stay horizontal),
    plus per-tile tone jitter; no synthesised veins or mottle.

36 px/in: module 1704 x 855 px, image 5112 x 5130 px. Joint centrelines on x = k*1704 and y = k*855 px, so
a half joint lies on every image edge and both maps wrap exactly. Height (mm above the grout floor): face
FACE_MM, quarter-round eased edge EDGE_MM, photo-derived micro-relief (luminance DoG), bounded.
Usage:  python b01_build_24x48.py                 -> veincut_24x48/Color.png, Bump16.png, report.json
        python b01_build_24x48.py <suffix> R,G,B  -> veincut_24x48/Color_<suffix>.png only (same seed; raises
                                                     if the recomputed bump differs from Bump16.png)
Every write goes through guard.out_path.
"""
import itertools
import json
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

from common import MM, lin_to_srgb, lum, orient, srgb_to_lin, write_png16
from guard import out_path

Image.MAX_IMAGE_PIXELS = None
OUT = "veincut_24x48/"
SEED = 2026092621
PPI = 36
TILE_ACTUAL = (47.244, 23.622)
TILE_W, TILE_H, JOINT = 47.0 + 5.0 / 24.0, 23.625, 0.125
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT            # 47.3333 x 23.75 in
COLS, ROWS = 3, 6
MW, MH = int(round(MOD_W * PPI)), int(round(MOD_H * PPI))  # 1704 x 855 px (exact)
W_PX, H_PX = COLS * MW, ROWS * MH
assert abs(MW - MOD_W * PPI) < 1e-9 and abs(MH - MOD_H * PPI) < 1e-9

FACES = ["A", "B", "W1", "W2", "W3", "W4"]
TRANSFORMS = ["r0", "flipH", "flipV", "r180"]
TONE_SIGMA = 0.02        # per-tile log-luminance spread (MILE: shade variation V3 moderate)
HUE_SIGMA = 0.003
FACE_MM = 1.50           # tile face above the grout floor
EDGE_MM = 1.00           # eased-edge radius (rectified porcelain)
MICRO_SD_MM = 0.03       # photo-derived micro-relief, standard deviation before bounding
MICRO_MAX_MM = 0.10      # hard bound (tanh)
GROUT_SRGB = (208.0, 198.0, 180.0)   # warm light neutral, ~9 % darker (linear) than the face mean
REVIT_BUMP = 60          # editor value (100 x stored); 100 <-> 2.6 mm calibration, scaled to ~1.6 mm


def plan(rng):
    """Assign (face, transform) to the 3 x 6 cells.
    Rows 0/2/4 use one group of 3 faces, rows 1/3/5 the other, so with the wrap no face ever touches itself
    (8-neighbourhood); inside a group the columns form a Latin square; each face gets 3 different
    transforms. Among the random candidates, minimise (a) adjacent A/W pairs whose shared corner would show
    in the same orientation (t_W == t_A o flipH, see a07), then (b) same-transform neighbours."""
    comp = {("r0", "flipH"): "flipH", ("flipH", "flipH"): "r0", ("flipV", "flipH"): "r180", ("r180", "flipH"): "flipV"}
    best = None
    for _ in range(4000):
        f = list(rng.permutation(FACES))
        g1, g2 = f[:3], f[3:]
        cells = {}
        for grp, rows in ((g1, (0, 2, 4)), (g2, (1, 3, 5))):
            shifts = rng.permutation(3)
            for i, r in enumerate(rows):
                for c in range(3):
                    cells[(r, c)] = grp[(c + shifts[i]) % 3]
        tr = {}
        for face in FACES:
            ts = list(rng.permutation(TRANSFORMS))[:3]
            for (r, c), fc in sorted(cells.items()):
                if fc == face:
                    tr[(r, c)] = ts.pop()
        cost_a, cost_t = 0, 0
        for (r, c) in cells:
            for dr, dc in itertools.product((-1, 0, 1), repeat=2):
                if dr == dc == 0:
                    continue
                n = ((r + dr) % ROWS, (c + dc) % COLS)
                fa, fb = cells[(r, c)], cells[n]
                if fa == "A" and fb.startswith("W") and tr[n] == comp[(tr[(r, c)], "flipH")]:
                    cost_a += 1
                if tr[n] == tr[(r, c)]:
                    cost_t += 1
        key = (cost_a, cost_t)
        if best is None or key < best[0]:
            best = (key, cells, tr)
    (cost_a, cost_t), cells, tr = best
    return [[{"face": cells[(r, c)], "transform": tr[(r, c)]} for c in range(COLS)] for r in range(ROWS)], cost_a, cost_t


def load_faces():
    info = json.load(open(out_path("_work/faces.json")))
    return {k: np.load(out_path("_work/faces/%s.npy" % k)) for k in FACES}, info


def block_geometry():
    """Per pixel of one module block: face coords u, v (in, from the face's top-left corner) and signed
    distance d (in) to the face edge (< 0 in the joint)."""
    x_in = (np.arange(MW) + 0.5) / PPI
    y_in = (np.arange(MH) + 0.5) / PPI
    u = x_in - JOINT / 2
    v = y_in - JOINT / 2
    du = np.minimum(u, TILE_W - u)
    dv = np.minimum(v, TILE_H - v)
    d = np.minimum(du[None, :], dv[:, None])
    return u, v, d


def sample_face(src, u, v):
    """Resample a face (H x W x 3, covering the tile's actual size) at face coords u (W,), v (H,)."""
    sh, sw = src.shape[:2]
    fx = u * (sw / TILE_W) - 0.5
    fy = v * (sh / TILE_H) - 0.5
    gy, gx = np.meshgrid(fy, fx, indexing="ij")
    out = np.empty(gy.shape + (3,))
    for ch in range(3):
        out[..., ch] = map_coordinates(src[..., ch], [gy, gx], order=3, mode="nearest")
    return np.clip(out, 0, 1)


def main(grout_srgb=GROUT_SRGB, suffix=""):
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    cells, cost_a, cost_t = plan(rng)
    n = COLS * ROWS
    tone = np.exp(TONE_SIGMA * rng.standard_normal(n))
    hue = HUE_SIGMA * rng.standard_normal((n, 3))
    hue -= hue.mean(1, keepdims=True)
    gnoise_white = rng.standard_normal((H_PX, W_PX))
    faces, finfo = load_faces()

    u, v, d = block_geometry()
    alpha = np.clip(d * PPI + 0.5, 0, 1)
    d_mm = d * MM
    q = np.clip(d_mm / EDGE_MM, 0, 1)
    drop = EDGE_MM * (1 - np.sqrt(1 - (1 - q) ** 2))              # quarter-circle roundover
    gl = srgb_to_lin(np.array(grout_srgb))
    gnoise = gaussian_filter(gnoise_white, 1.0, mode="wrap") * 0.015

    srgb = np.zeros((H_PX, W_PX, 3), np.uint8)
    height = np.zeros((H_PX, W_PX))
    tile_id = np.zeros((H_PX, W_PX), np.uint8)
    face_means, micro_all = [], []
    for r in range(ROWS):
        for c in range(COLS):
            k = r * COLS + c
            cell = cells[r][c]
            src = orient(faces[cell["face"]], cell["transform"])
            lin = sample_face(src, u, v) * (tone[k] * np.exp(hue[k]))[None, None, :]
            lin = np.clip(lin, 0, 1)
            ys, xs = slice(r * MH, (r + 1) * MH), slice(c * MW, (c + 1) * MW)
            grout = gl[None, None, :] * (1 + gnoise[ys, xs][..., None])
            col = alpha[..., None] * lin + (1 - alpha[..., None]) * grout
            srgb[ys, xs] = np.clip(np.round(lin_to_srgb(col)), 0, 255).astype(np.uint8)
            inner = d_mm >= EDGE_MM
            face_means.append([float(x) for x in lin[inner].mean(0)])
            # photo-derived micro-relief: luminance band-pass of this cell's own face pixels
            L = np.log(lum(lin) + 1e-4)
            band = gaussian_filter(L, 0.7, mode="nearest") - gaussian_filter(L, 3.0, mode="nearest")
            micro_all.append(band)
            tile_id[ys, xs] = k
    sd = float(np.std(np.concatenate([m[d_mm >= EDGE_MM] for m in micro_all])))
    for r in range(ROWS):
        for c in range(COLS):
            k = r * COLS + c
            micro = micro_all[k] / sd * MICRO_SD_MM
            micro = MICRO_MAX_MM * np.tanh(micro / MICRO_MAX_MM)
            ys, xs = slice(r * MH, (r + 1) * MH), slice(c * MW, (c + 1) * MW)
            height[ys, xs] = alpha * np.maximum(FACE_MM + micro - drop, 0.0)
    full_mm = FACE_MM + MICRO_MAX_MM          # fixed full scale, independent of the data
    assert height.max() <= full_mm + 1e-9
    h16 = np.clip(np.round(height / full_mm * 65535), 0, 65535).astype(np.uint16)

    cname = OUT + "Color%s.png" % ("_" + suffix if suffix else "")
    Image.fromarray(srgb, "RGB").save(out_path(cname), optimize=True)
    if suffix:
        delivered = np.asarray(Image.open(out_path(OUT + "Bump16.png"))).astype(np.uint16)
        if not np.array_equal(delivered, h16):
            raise RuntimeError("variant bump differs from delivered Bump16.png: geometry or seed changed")
        print("bump identical to delivered Bump16.png")
    else:
        write_png16(out_path(OUT + "Bump16.png"), h16)
        np.save(out_path("_work/tile_id_24x48.npy"), tile_id)

    face_px = np.tile(d_mm >= EDGE_MM, (ROWS, COLS))
    report = {
        "product": "ELM Surfaces ElmStone Jute Vein-Cut 24x48 matte porcelain (= MILE stone EcoStone Vein-Cut Jute, SKU 1104304), 8 mm",
        "seed": SEED, "ppi": PPI, "pixels": [W_PX, H_PX],
        "tile_actual_in": list(TILE_ACTUAL), "tile_actual_basis": "600 x 1200 mm rectified metric convention (actual size not published)",
        "tile_drawn_in": [TILE_W, TILE_H],
        "drawn_minus_actual_mm": [(TILE_W - TILE_ACTUAL[0]) * MM, (TILE_H - TILE_ACTUAL[1]) * MM],
        "drawn_minus_actual_pct": [100 * (TILE_W / TILE_ACTUAL[0] - 1), 100 * (TILE_H / TILE_ACTUAL[1] - 1)],
        "joint_in": JOINT, "joint_basis": "1/8 in assumption (no manufacturer recommendation published)",
        "module_in": [MOD_W, MOD_H], "module_px": [MW, MH],
        "layout": "stack bond (straight stack), long side horizontal, veins horizontal",
        "atlas_tiles": [COLS, ROWS], "sample_size_in": [W_PX / PPI, H_PX / PPI],
        "first_tile_face_offset_from_origin_in": [JOINT / 2, JOINT / 2],
        "cells": cells, "plan_cost_A_W_same_orientation_adjacent": cost_a, "plan_cost_same_transform_adjacent": cost_t,
        "relief_mm": {"full_scale": full_mm, "grout_floor": 0.0, "face_design": FACE_MM, "joint_depth": FACE_MM,
                      "edge_radius": EDGE_MM, "micro_sd_design": MICRO_SD_MM, "micro_bound": MICRO_MAX_MM,
                      "face_min": float(height[face_px].min()), "face_max": float(height[face_px].max()),
                      "face_relief_p1_p99": [float(v) for v in np.percentile(height[face_px], [1, 99])],
                      "height_at_tile_edge_design": FACE_MM - EDGE_MM, "mm_per_count": full_mm / 65535},
        "revit_bump_amount_editor": REVIT_BUMP,
        "colour": {"grout_srgb": list(grout_srgb), "tone_sigma_log": TONE_SIGMA, "hue_sigma": HUE_SIGMA,
                   "tile_tone_factors": [float(x) for x in tone],
                   "face_mean_srgb_per_tile": [[float(x) for x in lin_to_srgb(np.array(m))] for m in face_means],
                   "face_mean_srgb": [float(x) for x in lin_to_srgb(np.mean(face_means, 0))]},
        "faces": finfo["faces"], "build_seconds": time.time() - t0,
    }
    json.dump(report, open(out_path(OUT + "report%s.json" % ("_" + suffix if suffix else "")), "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("pixels", "sample_size_in", "cells", "relief_mm", "build_seconds")}, indent=None))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        rgb = tuple(float(x) for x in sys.argv[2].split(","))
        main(rgb, sys.argv[1])
    else:
        main()
