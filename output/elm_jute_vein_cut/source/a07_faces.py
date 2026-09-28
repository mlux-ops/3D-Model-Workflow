"""Prepare the real vein-cut faces (linear light, float64, veins horizontal, Jute swatch colour).

Distinct printed content found by a03_dupes.py / a04_locate.py (see SOURCE_SELECTION.md):
  A  u09 (= ELM w01 = MILE w04 = old jute_original/PrimaryBath = w05 full tiles; w11 is a crop of it)
  B  old05 (= w05 half tiles, which are its left/right halves rotated 180 deg); old05 itself is paler
     (mean sRGB 239/233/219 vs the Jute swatch 218/207/188), so it is re-toned to the w05 half tiles'
     Jute colour by per-channel quantile mapping over the registered halves.
  W  w14 48x110 slab (rotated 90 deg, veins horizontal). It contains A (flipped, scale 0.96); the rest is new.
     Four tile-size windows at the slab's corners; each overlaps A's located box in one corner only.
     w14 is exposed darker (206/191/172); re-toned to u09 by quantile mapping over its A region.
Every face: planar (first-order) de-lighting only. Output _work/faces/<name>.npy (H x W x 3 linear) and
_work/faces.json (native px/in, crop, overlap with A, tone maps, planar trend removed)."""
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from common import lin_to_srgb, lum, srgb_to_lin
from guard import out_path, ref

Image.MAX_IMAGE_PIXELS = None
B = "E:/Claude/3D-Model-Workflow/"
TILE_ACT = (47.244, 23.622)        # 1200 x 600 mm (see README: actual size not published; assumption)
PPI_A = 1890 / TILE_ACT[0]         # 40.0 px/in: the swatch shows exactly one tile face


def load_lin(p, rot=0):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64)
    return srgb_to_lin(np.rot90(a, rot).copy())


def planar_delight(a):
    L = gaussian_filter(lum(a), 10)
    yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]
    xn, yn = xx / L.shape[1] - 0.5, yy / L.shape[0] - 0.5
    G = np.stack([np.ones_like(xn), xn, yn], -1).reshape(-1, 3)
    c, *_ = np.linalg.lstsq(G, L.ravel(), rcond=None)
    plane = (G @ c).reshape(L.shape) / c[0]
    return a / plane[..., None], float(plane.max() / plane.min() - 1), [float(v) for v in c[1:] / c[0]]


def quantile_map(src_vals, ref_vals, n=64):
    """Per-channel monotone map (piecewise linear through matched quantiles 1..99 %)."""
    q = np.linspace(1, 99, n)
    maps = []
    for ch in range(3):
        xs = np.percentile(src_vals[:, ch], q)
        ys = np.percentile(ref_vals[:, ch], q)
        maps.append((xs, ys))
    return maps


def apply_map(a, maps):
    out = np.empty_like(a)
    for ch, (xs, ys) in enumerate(maps):
        # linear extrapolation beyond the end quantiles (slope of the end segments)
        v = a[..., ch]
        o = np.interp(v, xs, ys)
        lo, hi = v < xs[0], v > xs[-1]
        sl = (ys[1] - ys[0]) / max(xs[1] - xs[0], 1e-9)
        sh = (ys[-1] - ys[-2]) / max(xs[-1] - xs[-2], 1e-9)
        o[lo] = ys[0] + (v[lo] - xs[0]) * sl
        o[hi] = ys[-1] + (v[hi] - xs[-1]) * sh
        out[..., ch] = o
    return np.clip(out, 0, 1)


def mean_srgb(a):
    return [float(v) for v in lin_to_srgb(a.reshape(-1, 3).mean(0))]


def main():
    info = {"tile_actual_in": TILE_ACT, "faces": {}}
    loc = {(r["query"], r["target"]): r for r in json.load(open(out_path("_work/locate.json")))}

    # --- A
    A = load_lin(ref("user_supplied/u09_flat_veincut_swatch.webp"))
    # --- B: old05 re-toned to the w05 half tiles (Jute colour)
    old = load_lin(B + "output/belmont_tiles/ElmStone_Jute_24x48/references/05_new_flat_veincut.jpg")
    pan = load_lin(ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"))
    h1 = pan[1203:2396, 4:1195]          # r1half = old05 x 0..24 in, rotated 180
    h0 = pan[4:1194, 2402:3596]          # r0half = old05 x 24.3..47.7 in, rotated 180
    ppi_old = 1890 / 48.0                # a04 box units (48 in nominal width)
    b1 = loc[("w05_r1half", "old05")]["query_box_in_target_in"]
    b0 = loc[("w05_r0half", "old05")]["query_box_in_target_in"]
    reg_old = []
    for b in (b1, b0):
        x0, y0, x1, y1 = [int(round(v * ppi_old)) for v in b]
        reg_old.append(old[max(y0, 0):y1, max(x0, 0):x1].reshape(-1, 3))
    maps_B = quantile_map(np.concatenate(reg_old), np.concatenate([h1.reshape(-1, 3), h0.reshape(-1, 3)]))
    Bf = apply_map(old, maps_B)
    # --- W: w14 rotated 90 deg (CCW, as in a03/a04), re-toned to u09 over its A region
    w14 = load_lin(ref("web/w14_ms_jute_veincut_48x110_04.jpg"), 1)
    bA = loc[("u09", "w14_48x110")]["query_box_in_target_in"]
    ppi14_nom = 2039 / 48.0
    ax0, ay0, ax1, ay1 = [int(round(v * ppi14_nom)) for v in bA]
    regA = w14[ay0 + 10:ay1 - 10, ax0 + 10:ax1 - 10]
    Asc = zoom(A, ((ay1 - ay0 - 20) / A.shape[0], (ax1 - ax0 - 20) / A.shape[1], 1), order=1)
    maps_W = quantile_map(regA.reshape(-1, 3), Asc.reshape(-1, 3))
    W = apply_map(w14, maps_W)
    # w14's effective px/in on the swatch scale: A (one 47.244 in face) spans ax1-ax0 px
    ppi_w = (ax1 - ax0) / TILE_ACT[0]
    fw, fh = int(round(TILE_ACT[0] * ppi_w)), int(round(TILE_ACT[1] * ppi_w))
    Hh, Ww = W.shape[:2]
    wins = {"W1": (0, 0), "W2": (0, Hh - fh), "W3": (Ww - fw, 0), "W4": (Ww - fw, Hh - fh)}
    faces = {"A": (A, PPI_A, "u09 full swatch"), "B": (Bf, 1890 / TILE_ACT[0], "old05 re-toned to w05 halves")}
    for k, (x0, y0) in wins.items():
        ox = max(0, min(x0 + fw, ax1) - max(x0, ax0))
        oy = max(0, min(y0 + fh, ay1) - max(y0, ay0))
        faces[k] = (W[y0:y0 + fh, x0:x0 + fw], ppi_w, "w14 window x%d y%d" % (x0, y0))
        info["faces"][k] = {"window_px_in_w14_rot": [x0, y0, x0 + fw, y0 + fh],
                            "overlap_with_A_box_px": [int(ox), int(oy)],
                            "overlap_with_A_share_of_face": float(ox * oy / (fw * fh))}
    for k, (a, ppi, desc) in faces.items():
        d, trend, grad = planar_delight(a)
        np.save(out_path("_work/faces/%s.npy" % k), d)
        Image.fromarray(np.clip(np.round(lin_to_srgb(d)), 0, 255).astype(np.uint8)).resize(
            (800, int(800 * d.shape[0] / d.shape[1]))).save(out_path("_work/faces/_VIEW_%s.jpg" % k), quality=90)
        info["faces"].setdefault(k, {}).update({
            "desc": desc, "px": [int(d.shape[1]), int(d.shape[0])], "ppi": float(ppi),
            "planar_trend_removed_rel": trend, "planar_gradient_rel_x_y": grad,
            "mean_srgb_before_delight": mean_srgb(a), "mean_srgb": mean_srgb(d)})
    info["tone_maps"] = {"B_from_old05_to_w05_halves": {"mean_srgb_old05": mean_srgb(old), "mean_srgb_after": mean_srgb(Bf),
                                                        "mean_srgb_w05_halves": mean_srgb(np.concatenate([h1.reshape(-1, 3), h0.reshape(-1, 3)]))},
                         "W_from_w14_to_u09": {"mean_srgb_w14": mean_srgb(w14), "mean_srgb_after": mean_srgb(W),
                                               "A_box_in_w14_px": [ax0, ay0, ax1, ay1], "ppi_w14_on_swatch_scale": ppi_w}}
    json.dump(info, open(out_path("_work/faces.json"), "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
