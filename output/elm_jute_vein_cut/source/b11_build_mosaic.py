"""Build the ELM ElmStone Jute Vein-Cut 1x3 mosaic (MILE stone EcoStone 1x3 Vein-Cut Jute, SKU 1104340, 12x12
sheet) colour (8-bit sRGB) and bump (16-bit grey) maps. Straight stack, long side horizontal, columns aligned,
veins horizontal (MILE sheet w07, MILE wall w10 and the user's u11 all show this layout).

Geometry (README.md): chip pitch 3 x 1 in (4 x 12 chips on the nominal 12 x 12 sheet; measured pitch ratio
2.99 on w07), joint 1/16 in (measured ~0.06 in on w07 and u11; not published), chip drawn 2.9375 x 0.9375 in.
The sheet joint is the same as the chip joint, so sheet boundaries do not show. Atlas 16 x 48 chips
(4 x 4 sheets) = 48.00 x 48.00 in (4'-0" x 4'-0"), 48 px/in, 2304 x 2304 px, module 144 x 48 px.
Colour: each chip is a distinct, non-overlapping 2.9375 x 0.9375 in crop of a real face (A = u09, B = old05
re-toned, W = the w14 48x110 slab minus its copy of A), in one of 4 orientation-preserving transforms, with
per-chip tone jitter calibrated to u11 (a06_mosaic_stats.py). No crop area is used twice (occupancy masks).
Height (mm above the grout floor): face FACE_MM, eased edge EDGE_MM, photo-derived micro-relief.
Usage:  python b11_build_mosaic.py                 -> mosaic_1x3/Color.png, Bump16.png, report.json
        python b11_build_mosaic.py <suffix> R,G,B  -> mosaic_1x3/Color_<suffix>.png only (bump must match)
"""
import json
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

from common import MM, lin_to_srgb, lum, orient, srgb_to_lin, write_png16
from guard import out_path

Image.MAX_IMAGE_PIXELS = None
OUT = "mosaic_1x3/"
SEED = 2026092631
PPI = 48
PITCH_W, PITCH_H, JOINT = 3.0, 1.0, 0.0625
CHIP_W, CHIP_H = PITCH_W - JOINT, PITCH_H - JOINT
COLS, ROWS = 16, 48
MW, MH = int(PITCH_W * PPI), int(PITCH_H * PPI)          # 144 x 48 px
W_PX, H_PX = COLS * MW, ROWS * MH
TRANSFORMS = ["r0", "flipH", "flipV", "r180"]
EDGE_MARGIN_IN = 0.2     # keep crops this far from the source image edges
FACE_MM = 1.20
EDGE_MM = 0.60
MICRO_SD_MM = 0.03
MICRO_MAX_MM = 0.10
HUE_SIGMA = 0.004
GROUT_SRGB = (208.0, 198.0, 180.0)
REVIT_BUMP = 50          # editor value; 100 <-> 2.6 mm calibration scaled to 1.3 mm full scale


def sources():
    fi = json.load(open(out_path("_work/faces.json")))
    mi = json.load(open(out_path("_work/mosaic_sources.json")))
    S = []
    for name, arr, ppi, excl in (
            ("A", np.load(out_path("_work/faces/A.npy")), fi["faces"]["A"]["ppi"], None),
            ("B", np.load(out_path("_work/faces/B.npy")), fi["faces"]["B"]["ppi"], None),
            ("W", np.load(out_path("_work/faces/W_full.npy")), mi["ppi"], np.load(out_path("_work/faces/W_full_exclude.npy")))):
        occ = np.zeros(arr.shape[:2], bool) if excl is None else excl.copy()
        m = int(round(EDGE_MARGIN_IN * ppi))
        occ[:m] = occ[-m:] = True
        occ[:, :m] = occ[:, -m:] = True
        S.append({"name": name, "img": arr, "ppi": ppi, "occ": occ, "free0": float((~occ).mean())})
    return S


def pick_crops(S, n, rng):
    """n non-overlapping crops (1 px guard band), sources chosen in proportion to their free area."""
    crops = []
    area = np.array([(~s["occ"]).sum() / s["ppi"] ** 2 for s in S])
    for i in range(n):
        for attempt in range(20000):
            si = int(rng.choice(len(S), p=area / area.sum()))
            s = S[si]
            w, h = CHIP_W * s["ppi"], CHIP_H * s["ppi"]
            H, W = s["occ"].shape
            x0 = rng.uniform(0, W - w - 2)
            y0 = rng.uniform(0, H - h - 2)
            xa, ya, xb, yb = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1, int(np.ceil(x0 + w)) + 1, int(np.ceil(y0 + h)) + 1
            xa, ya = max(xa, 0), max(ya, 0)
            if s["occ"][ya:yb, xa:xb].any():
                continue
            s["occ"][ya:yb, xa:xb] = True
            crops.append({"source": s["name"], "si": si, "x0": float(x0), "y0": float(y0), "w": float(w), "h": float(h),
                          "transform": TRANSFORMS[int(rng.integers(4))]})
            break
        else:
            raise RuntimeError("could not place chip %d without overlap" % i)
    return crops


ARR_SIGMA = (4.0, 1.5)    # chip-grid low-pass for the arrangement: 4 rows (4 in) x 1.5 columns (4.5 in)
ARR_TARGET = 0.5          # stop once the low-passed chip-luminance sd is half its random value


def lowpass(g):
    return gaussian_filter(g, ARR_SIGMA, mode="wrap")


def arrange(m, rng, iters=60000):
    """Permutation of the chips over the grid (row-major) minimising the variance of the low-passed
    chip-luminance field, by greedy random pair swaps. Returns order, sd before, sd after."""
    g = (m - m.mean()).reshape(ROWS, COLS).copy()
    idx = np.arange(len(m)).reshape(ROWS, COLS)
    cur = float((lowpass(g) ** 2).sum())
    before = float(np.sqrt(cur / g.size))
    for _ in range(iters):
        a = (int(rng.integers(ROWS)), int(rng.integers(COLS)))
        b = (int(rng.integers(ROWS)), int(rng.integers(COLS)))
        if a == b:
            continue
        g[a], g[b] = g[b], g[a]
        new = float((lowpass(g) ** 2).sum())
        if new < cur:
            cur = new
            idx[a], idx[b] = idx[b], idx[a]
            if np.sqrt(cur / g.size) <= ARR_TARGET * before:
                break                    # flat enough; do not drive it towards a regular (blue-noise) grid
        else:
            g[a], g[b] = g[b], g[a]
    return idx.ravel(), before, float(np.sqrt(cur / g.size))


def main(grout_srgb=GROUT_SRGB, suffix=""):
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    S = sources()
    n = COLS * ROWS
    crops = pick_crops(S, n, rng)
    stats = json.load(open(out_path("_work/mosaic_stats.json")))
    sd_nat = stats["face_crops"]["sd_logmean"]
    sd_tgt = stats["u11_local_sd_logmean"]
    extra = float(np.sqrt(max(0.0, sd_tgt ** 2 - sd_nat ** 2)))
    tone = np.exp(extra * rng.standard_normal(n))
    hue = HUE_SIGMA * rng.standard_normal((n, 3))
    hue -= hue.mean(1, keepdims=True)
    gnoise = gaussian_filter(rng.standard_normal((H_PX, W_PX)), 1.0, mode="wrap") * 0.015

    x_in = (np.arange(MW) + 0.5) / PPI
    y_in = (np.arange(MH) + 0.5) / PPI
    u, v = x_in - JOINT / 2, y_in - JOINT / 2
    d = np.minimum(np.minimum(u, CHIP_W - u)[None, :], np.minimum(v, CHIP_H - v)[:, None])
    alpha = np.clip(d * PPI + 0.5, 0, 1)
    d_mm = d * MM
    q = np.clip(d_mm / EDGE_MM, 0, 1)
    drop = EDGE_MM * (1 - np.sqrt(1 - (1 - q) ** 2))
    gl = srgb_to_lin(np.array(grout_srgb))
    inner = d_mm >= EDGE_MM

    # 1) sample every chip (linear light, with its tone), 2) arrange chips on the grid so the
    #    low-frequency chip-luminance field is as flat as possible (no large light/dark clusters that would
    #    become a visible landmark when the atlas repeats), 3) compose.
    blocks = []
    for k, cr in enumerate(crops):
        s = S[cr["si"]]
        # source sample coords: chip face coords (u, v) map linearly onto the crop window
        fu = np.clip(u, 0, CHIP_W) / CHIP_W
        fv = np.clip(v, 0, CHIP_H) / CHIP_H
        if cr["transform"] in ("flipH", "r180"):
            fu = 1 - fu
        if cr["transform"] in ("flipV", "r180"):
            fv = 1 - fv
        sx = cr["x0"] + fu * cr["w"] - 0.5
        sy = cr["y0"] + fv * cr["h"] - 0.5
        gy, gx = np.meshgrid(sy, sx, indexing="ij")
        lin = np.empty((MH, MW, 3))
        for ch in range(3):
            lin[..., ch] = map_coordinates(s["img"][..., ch], [gy, gx], order=3, mode="nearest")
        lin = np.clip(lin * (tone[k] * np.exp(hue[k]))[None, None, :], 0, 1)
        blocks.append(lin)
        cr["tone"] = float(tone[k])
    order, flat_before, flat_after = arrange(np.array([np.log(lum(b[inner].mean(0))) for b in blocks]), rng)
    blocks = [blocks[i] for i in order]
    crops = [crops[i] for i in order]
    srgb = np.zeros((H_PX, W_PX, 3), np.uint8)
    bands, means = [], []
    for k, (cr, lin) in enumerate(zip(crops, blocks)):
        r, c = divmod(k, COLS)
        ys, xs = slice(r * MH, (r + 1) * MH), slice(c * MW, (c + 1) * MW)
        grout = gl[None, None, :] * (1 + gnoise[ys, xs][..., None])
        col = alpha[..., None] * lin + (1 - alpha[..., None]) * grout
        srgb[ys, xs] = np.clip(np.round(lin_to_srgb(col)), 0, 255).astype(np.uint8)
        L = np.log(lum(lin) + 1e-4)
        bands.append(gaussian_filter(L, 0.7, mode="nearest") - gaussian_filter(L, 3.0, mode="nearest"))
        means.append(lin[inner].mean(0))
        cr["row"], cr["col"] = r, c
    sd = float(np.std(np.concatenate([b[inner] for b in bands])))
    height = np.zeros((H_PX, W_PX))
    for k in range(n):
        r, c = divmod(k, COLS)
        micro = MICRO_MAX_MM * np.tanh(bands[k] / sd * MICRO_SD_MM / MICRO_MAX_MM)
        height[r * MH:(r + 1) * MH, c * MW:(c + 1) * MW] = alpha * np.maximum(FACE_MM + micro - drop, 0.0)
    full_mm = FACE_MM + MICRO_MAX_MM
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
    facepx = np.tile(inner, (ROWS, COLS))
    for cr in crops:
        cr.pop("si")
    per_src = {s["name"]: sum(1 for cr in crops if cr["source"] == s["name"]) for s in S}
    report = {
        "product": "ELM Surfaces ElmStone Jute Vein-Cut 1x3 mosaic on 12x12 sheet (= MILE stone EcoStone 1x3 Vein-Cut Jute, SKU 1104340), 8 mm",
        "seed": SEED, "ppi": PPI, "pixels": [W_PX, H_PX],
        "chip_pitch_in": [PITCH_W, PITCH_H], "chip_drawn_in": [CHIP_W, CHIP_H], "joint_in": JOINT,
        "chip_basis": "nominal 1x3 on a 12x12 sheet, 4 x 12 chips; pitch ratio 2.99 and joint ~0.06 in measured on MILE sheet w07; actual chip size not published",
        "module_px": [MW, MH], "layout": "straight stack, long side horizontal, columns aligned, veins horizontal",
        "atlas_chips": [COLS, ROWS], "atlas_sheets": [COLS // 4, ROWS // 12], "sample_size_in": [W_PX / PPI, H_PX / PPI],
        "first_chip_face_offset_from_origin_in": [JOINT / 2, JOINT / 2],
        "relief_mm": {"full_scale": full_mm, "grout_floor": 0.0, "face_design": FACE_MM, "joint_depth": FACE_MM,
                      "edge_radius": EDGE_MM, "micro_sd_design": MICRO_SD_MM, "micro_bound": MICRO_MAX_MM,
                      "face_min": float(height[facepx].min()), "face_max": float(height[facepx].max()),
                      "face_relief_p1_p99": [float(x) for x in np.percentile(height[facepx], [1, 99])],
                      "height_at_tile_edge_design": FACE_MM - EDGE_MM, "mm_per_count": full_mm / 65535},
        "revit_bump_amount_editor": REVIT_BUMP,
        "colour": {"grout_srgb": list(grout_srgb), "chip_tone_extra_sigma_log": extra,
                   "tone_basis": "u11 local chip sd %.4f vs natural crop sd %.4f (a06)" % (sd_tgt, sd_nat),
                   "hue_sigma": HUE_SIGMA, "chip_mean_sd_log_measured": float(np.std(np.log(lum(np.array(means))))),
                   "face_mean_srgb": [float(x) for x in lin_to_srgb(np.mean(means, 0))]},
        "chips_per_source": per_src,
        "arrangement": {"lowpass_sigma_rows_cols": list(ARR_SIGMA), "lowpass_sd_log_before": flat_before,
                        "lowpass_sd_log_after": flat_after,
                        "note": "chips re-ordered on the grid (pair swaps) to avoid large light/dark clusters"},
        "source_free_share_before": {s["name"]: s["free0"] for s in S},
        "source_share_used": {s["name"]: float(sum(cr["w"] * cr["h"] for cr in crops if cr["source"] == s["name"]) / (~np.zeros(s["occ"].shape, bool)).sum()) for s in S},
        "chips": crops, "build_seconds": time.time() - t0,
    }
    json.dump(report, open(out_path(OUT + "report%s.json" % ("_" + suffix if suffix else "")), "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("pixels", "sample_size_in", "relief_mm", "colour", "chips_per_source", "build_seconds")}, indent=None))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(tuple(float(x) for x in sys.argv[2].split(",")), sys.argv[1])
    else:
        main()
