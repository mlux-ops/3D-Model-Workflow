"""Detect the drawn joint grid of each straight-on 24x48 swatch and list every tile face (full or partial).

Joints in these MSI digital swatches are light lines with a thin darker shadow. For each image:
  * horizontal joints: rows whose mean high-passed luminance departs strongly from the field
  * vertical joints: the same per row band
Writes _work/grid.json: per image the joint rows, per band the joint columns, and each face box with
its completeness (fraction of a 2:1 tile visible). Prints a summary.
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, uniform_filter1d

from guard import out_path, ref

CANDS = [
    "msi_porcelainceramic__soreno-ivory-porcelain-24x48.jpg",
    "msi_porcelainceramic__soreno-ivory-paver-24x48.jpg",
    "repo_belmont_PrimaryBath_Floor_MSI_Soreno_Ivory_24x48_NSORIVO2448.jpg",
    "aaaplus_soreno-ivory-porcelain-24x48.jpg",
    "gohardwood_soreno-ivory-porcelain-24x48.jpg",
    "mosaicmosaic_soreno-ivory-porcelain-24x48_1280.jpg",
    "pdf_images/msi_pdf_soreno-porcelain-flyer_03_439x439.png",
]


def lum(path):
    a = np.asarray(Image.open(ref(path)).convert("RGB")).astype(np.float64)
    return a, a @ np.array([0.2126, 0.7152, 0.0722])


def peaks(profile, min_gap, thresh):
    """Local extrema of |profile| above thresh (robust z), separated by min_gap."""
    z = (profile - np.median(profile)) / (1.4826 * np.median(np.abs(profile - np.median(profile))) + 1e-9)
    az = np.abs(z)
    idx = []
    order = np.argsort(-az)
    for i in order:
        if az[i] < thresh:
            break
        if all(abs(i - j) >= min_gap for j in idx):
            idx.append(int(i))
    return sorted(idx), z


def joint_centre(profile, i, half=4):
    """Refine a joint centre: centroid of the positive (light) excursion around i."""
    lo, hi = max(0, i - half), min(len(profile), i + half + 1)
    seg = profile[lo:hi] - np.median(profile)
    w = np.clip(seg, 0, None)
    if w.sum() <= 0:
        return float(i)
    return float(lo + (w * np.arange(len(seg))).sum() / w.sum())


def analyse(name):
    rgb, L = lum(name)
    H, W = L.shape
    hp = L - gaussian_filter1d(gaussian_filter1d(L, 6, 0), 6, 1)
    rowp = hp.mean(1)
    rows, zr = peaks(rowp, max(20, H // 8), 6.0)
    rows_c = [joint_centre(rowp, r) for r in rows]
    bands = [0.0] + rows_c + [float(H)]
    faces, vj = [], []
    for b in range(len(bands) - 1):
        y0, y1 = bands[b], bands[b + 1]
        a, c = int(y0) + 4, int(y1) - 4
        if c - a < 20:
            continue
        colp = hp[a:c].mean(0)
        cols, zc = peaks(colp, max(20, W // 6), 6.0)
        cols_c = [joint_centre(colp, x) for x in cols]
        vj.append({"band": [y0, y1], "cols": cols_c, "z": [float(zc[x]) for x in cols]})
        edges = [0.0] + cols_c + [float(W)]
        for k in range(len(edges) - 1):
            faces.append({"box": [edges[k], y0, edges[k + 1], y1]})
    # tile pitch from full-width bands / full faces
    hts = np.diff(rows_c) if len(rows_c) > 1 else []
    return {"image": name, "px": [W, H], "joint_rows": rows_c, "row_z": [float(zr[r]) for r in rows],
            "row_pitch": [float(v) for v in hts], "bands": vj, "faces": faces}


def main():
    out = []
    for n in CANDS:
        r = analyse(n)
        pitch_y = np.median(r["row_pitch"]) if r["row_pitch"] else float("nan")
        pitch_x = []
        for b in r["bands"]:
            if len(b["cols"]) > 1:
                pitch_x += list(np.diff(b["cols"]))
        px = float(np.median(pitch_x)) if pitch_x else 2 * pitch_y
        r["pitch_px"] = [px, float(pitch_y)]
        for f in r["faces"]:
            x0, y0, x1, y1 = f["box"]
            f["frac_w"] = (x1 - x0) / px
            f["frac_h"] = (y1 - y0) / pitch_y
        out.append(r)
        print(n, r["px"], "rows", [round(v, 1) for v in r["joint_rows"]], "pitch", [round(v, 1) for v in r["pitch_px"]])
        for b in r["bands"]:
            print("   band", [round(v, 1) for v in b["band"]], "cols", [round(v, 1) for v in b["cols"]])
    json.dump(out, open(out_path("_work/grid.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
