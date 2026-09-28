"""Measure the facts the build depends on, from the reference images, and write _work/measure.json.

1. Full-tile retailer swatch (landoftile_vivant_184826.webp): tile bbox, aspect, flute period and count.
2. ELM page swatch (elm_page_main-image_template.jpg): trimmed face area, flute period (epoch folding
   around the FFT peak), the mean shading profile over one flute period, lit-rib colour.
3. ELM installed wall (elm_ligne-noir_3.jpg): column/row joint pitch, joint width, module aspect,
   flute period in the wall, grout colour, and the folded rib/channel luminance profile.
"""
import json

import numpy as np
from PIL import Image

from guard import out_path, ref


def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def load(name):
    return np.asarray(Image.open(ref(name)).convert("RGB")).astype(np.float64)


def fold_period(profile, lo, hi, steps=4000):
    """Epoch folding: the period in [lo, hi] px that maximises the variance of the folded mean."""
    x = np.arange(len(profile))
    best = (0, None)
    for p in np.linspace(lo, hi, steps):
        ph = (x / p) % 1.0
        b = np.minimum((ph * 32).astype(int), 31)
        m = np.bincount(b, profile, 32) / np.maximum(np.bincount(b, None, 32), 1)
        v = m.var()
        if v > best[0]:
            best = (v, p)
    return best[1]


def folded(profile, period, bins=32, offset=0.0):
    x = np.arange(len(profile))
    ph = ((x - offset) / period) % 1.0
    b = np.minimum((ph * bins).astype(int), bins - 1)
    return np.bincount(b, profile, bins) / np.maximum(np.bincount(b, None, bins), 1)


def main():
    out = {}

    # 1. full-tile retailer swatch; flutes run along the image x axis (tile lying horizontal)
    a = load("landoftile_vivant_184826.webp")
    L = a.mean(2)
    ys, xs = np.where(L < 200)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    face = L[y0 + 6:y1 - 6, x0 + 20:x1 - 20]
    prof = face.mean(1)  # across the flutes
    p = fold_period(prof - prof.mean(), 20.0, 40.0)
    out["retailer_swatch"] = {
        "bbox_xyxy": [int(x0), int(y0), int(x1), int(y1)],
        "w_px": int(x1 - x0), "h_px": int(y1 - y0),
        "aspect": (x1 - x0) / (y1 - y0),
        "flute_period_px": p,
        "flutes_across_tile": (y1 - y0) / p,
    }

    # 2. ELM page swatch
    s = load("elm_page_main-image_template.jpg")
    Ls = s.mean(2)
    core = Ls[8:-8, 20:-20]
    prof = core.mean(1)
    p2 = fold_period(prof - prof.mean(), 25.0, 45.0)
    fp = folded(prof, p2)
    lin = srgb_to_lin(s[8:-8, 20:-20])
    # lit rib tops: rows whose folded luminance is in the top half of the profile
    rows = np.arange(core.shape[0])
    ph = (rows / p2) % 1.0
    b = np.minimum((ph * 32).astype(int), 31)
    lit = fp[b] >= np.median(fp)
    out["elm_swatch"] = {
        "size": [s.shape[1], s.shape[0]],
        "flute_period_px": p2,
        "flutes_in_height": s.shape[0] / p2,
        "folded_profile_srgb_lum": [round(v, 2) for v in fp],
        "mean_srgb": [round(v, 2) for v in lin_to_srgb(lin.reshape(-1, 3).mean(0))],
        "lit_rows_mean_srgb": [round(v, 2) for v in lin_to_srgb(lin[lit].reshape(-1, 3).mean(0))],
        "length_px_if_full_tile": s.shape[1],
    }

    # 3. installed wall: tiles vertical, stack bond; grout is the bright thin lines
    w = load("elm_ligne-noir_3.jpg")
    Lw = w.mean(2)
    upper = Lw[:1600, :900]  # left of the fruit stand and table
    colp = np.percentile(upper, 90, axis=0)  # grout columns are bright over their whole height
    rowp = np.percentile(Lw[:1700, :700], 90, axis=1)
    pc = fold_period(colp - colp.mean(), 150.0, 220.0)
    pr = fold_period(rowp - rowp.mean(), 550.0, 750.0)
    fc = folded(colp, pc, bins=int(round(pc)))
    fr = folded(rowp, pr, bins=int(round(pr)))
    thr_c = fc.min() + 0.5 * (fc.max() - fc.min())
    thr_r = fr.min() + 0.5 * (fr.max() - fr.min())
    joint_c_px = float((fc > thr_c).sum()) * pc / len(fc)
    joint_r_px = float((fr > thr_r).sum()) * pr / len(fr)
    # flute period inside tiles: row-mean over a lit band, excluding joints
    band = Lw[200:560, 60:880].mean(0)
    pf = fold_period(band - band.mean(), 12.0, 24.0)
    # grout colour: brightest core of vertical joints in the upper wall
    jc = int(np.argmax(fc))
    gx = [int(round(jc + k * pc)) for k in range(0, 5)]
    g = np.concatenate([w[100:1500, x - 1:x + 2].reshape(-1, 3) for x in gx if x + 2 < 900])
    gl = srgb_to_lin(g)
    keep = gl.mean(1) >= np.percentile(gl.mean(1), 60)
    out["installed_wall"] = {
        "column_pitch_px": pc, "row_pitch_px": pr,
        "module_aspect": pr / pc,
        "joint_width_col_px": joint_c_px, "joint_width_row_px": joint_r_px,
        "flute_period_px": pf, "flutes_per_module": pc / pf,
        "grout_srgb_as_photographed": [round(v, 1) for v in lin_to_srgb(gl[keep].mean(0))],
    }
    # joint width implied by the actual size 2.75 x 9.66 and the photographed module aspect
    A = pr / pc
    out["installed_wall"]["joint_in_implied_by_aspect"] = (9.66 - 2.75 * A) / (A - 1)
    out["installed_wall"]["joint_in_from_width_px"] = joint_c_px / pc * (2.75 + 0.1875)

    json.dump(out, open(out_path("_work/measure.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
