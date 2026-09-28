"""Measure joint positions / widths / pitch in the manufacturer layout images (panel mock-ups, mosaic sheet,
installed mosaic) from column and row luminance profiles. Writes _work/measure.json.

A joint shows as a narrow luminance dip (grout darker than the face) in the mean column (or row) profile of the
region between joints. Pitch = mean distance between dips; joint width = FWHM of the dip below the local face
level (sub-pixel via linear interpolation)."""
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, median_filter

from guard import out_path, ref


def lum(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64)
    return a @ np.array([0.2126, 0.7152, 0.0722]), a


def dips(profile, min_sep, k=4.0):
    base = median_filter(profile, size=max(9, int(min_sep) | 1), mode="wrap")
    d = base - profile
    thr = k * np.median(np.abs(d - np.median(d))) + 1e-9
    cand = np.flatnonzero((d > thr) & (d >= np.roll(d, 1)) & (d >= np.roll(d, -1)))
    keep = []
    for c in cand[np.argsort(-d[cand])]:
        if all(abs(c - q) >= min_sep for q in keep):
            keep.append(int(c))
    keep = sorted(keep)
    out = []
    for c in keep:
        half = d[c] / 2
        lo = c
        while lo > 0 and d[lo] > half:
            lo -= 1
        hi = c
        while hi < len(d) - 1 and d[hi] > half:
            hi += 1
        # sub-pixel crossing
        l = lo + (half - d[lo]) / (d[lo + 1] - d[lo] + 1e-12)
        h = hi - 1 + (d[hi - 1] - half) / (d[hi - 1] - d[hi] + 1e-12)
        w = d[max(lo, 0):hi + 1]
        xs = np.arange(max(lo, 0), hi + 1)
        cen = float((w.clip(0) * xs).sum() / w.clip(0).sum())
        out.append({"centre": cen, "fwhm": float(h - l), "depth": float(d[c]), "base": float(base[c])})
    return out


def analyse(name, path, min_sep_x, min_sep_y, crop=None):
    L, a = lum(path)
    if crop:
        x0, y0, x1, y1 = crop
        L, a = L[y0:y1, x0:x1], a[y0:y1, x0:x1]
    colp = gaussian_filter1d(L.mean(0), 0.5)
    rowp = gaussian_filter1d(L.mean(1), 0.5)
    vx = dips(colp, min_sep_x)
    hy = dips(rowp, min_sep_y)
    res = {"name": name, "px": [int(L.shape[1]), int(L.shape[0])], "crop": crop,
           "vertical_joints": vx, "horizontal_joints": hy}
    for key, js in (("x", vx), ("y", hy)):
        c = np.array([j["centre"] for j in js])
        if len(c) > 1:
            res["pitch_" + key] = float(np.median(np.diff(c)))
            res["fwhm_median_" + key] = float(np.median([j["fwhm"] for j in js]))
    return res, L, a


def grout_colour(a, L, js_x, js_y):
    m = np.zeros(L.shape, bool)
    for j in js_x:
        c = int(round(j["centre"]))
        m[:, max(c - 1, 0):c + 2] = True
    for j in js_y:
        c = int(round(j["centre"]))
        m[max(c - 1, 0):c + 2, :] = True
    return [float(v) for v in np.median(a[m], 0)], [float(v) for v in np.median(a[~m], 0)]


def main():
    out = {}
    # manufacturer 24x48 panel (half-offset mock-up, 4 tile positions)
    r, L, a = analyse("w05_panel_24x48", ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), 400, 400)
    out["w05"] = r
    # per row: vertical joint in each band separately (the panel is half-offset)
    H = L.shape[0]
    hy = [j["centre"] for j in r["horizontal_joints"]]
    bands = []
    edges = [0] + [int(round(y)) for y in hy] + [H]
    for i in range(len(edges) - 1):
        y0, y1 = edges[i] + 15, edges[i + 1] - 15
        if y1 - y0 < 100:
            continue
        rr, _, _ = analyse("w05_band%d" % i, ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), 400, 400,
                           crop=(0, y0, L.shape[1], y1))
        bands.append({"y": [y0, y1], "vertical_joints": rr["vertical_joints"]})
    out["w05"]["bands"] = bands
    r, L, a = analyse("w12_panel_12x24", ref("web/w12_ms_jute_veincut_panel_12x24.jpg"), 200, 200)
    out["w12"] = r
    r, L, a = analyse("w07_mosaic_sheet", ref("web/w07_ms_jute_veincut_1x3mosaic_01.jpg"), 60, 20)
    out["w07"] = r
    out["w07"]["grout_srgb_median"], out["w07"]["face_srgb_median"] = grout_colour(a, L, r["vertical_joints"],
                                                                                   r["horizontal_joints"])
    r, L, a = analyse("u11_installed_mosaic", ref("user_supplied/u11_mosaic_1x3_installed.png"), 25, 8)
    out["u11"] = r
    out["u11"]["grout_srgb_median"], out["u11"]["face_srgb_median"] = grout_colour(a, L, r["vertical_joints"],
                                                                                   r["horizontal_joints"])
    json.dump(out, open(out_path("_work/measure.json"), "w"), indent=1)
    for k, v in out.items():
        print(k, v["px"], "pitch", v.get("pitch_x"), v.get("pitch_y"), "fwhm", v.get("fwhm_median_x"),
              v.get("fwhm_median_y"), "nV", len(v["vertical_joints"]), "nH", len(v["horizontal_joints"]))
        print("   V:", [round(j["centre"], 1) for j in v["vertical_joints"]])
        print("   H:", [round(j["centre"], 1) for j in v["horizontal_joints"]])
        if "bands" in v:
            for b in v["bands"]:
                print("   band", b["y"], [(round(j["centre"], 1), round(j["fwhm"], 2)) for j in b["vertical_joints"]])
        if "grout_srgb_median" in v:
            print("   grout", [round(x) for x in v["grout_srgb_median"]], "face", [round(x) for x in v["face_srgb_median"]])


if __name__ == "__main__":
    main()
