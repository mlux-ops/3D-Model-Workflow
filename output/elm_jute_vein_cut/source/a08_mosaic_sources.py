"""Chip source pool for the 1x3 mosaic: the full w14 48x110 slab (re-toned to the Jute swatch, as in a07),
de-lit with a smooth quadratic log-luminance surface (the slab photo has a ~10-20 % lighting gradient;
variegation at scales below ~20 in is kept). A (u09) and B (old05 re-toned) come from a07 (planar de-lit).
The region of w14 that duplicates A is excluded from chip sampling (mask), so no printed area is used twice.
Writes _work/faces/W_full.npy, _work/faces/W_full_exclude.npy and _work/mosaic_sources.json."""
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from a07_faces import apply_map, load_lin, quantile_map
from common import lin_to_srgb, lum
from guard import out_path, ref
from scipy.ndimage import zoom


def quad_delight(a):
    L = np.log(gaussian_filter(lum(a), 20) + 1e-4)
    s = 8
    Ls = L[::s, ::s]
    yy, xx = np.mgrid[0:Ls.shape[0], 0:Ls.shape[1]]
    xn, yn = xx / Ls.shape[1] - 0.5, yy / Ls.shape[0] - 0.5
    G = np.stack([np.ones_like(xn), xn, yn, xn * xn, yn * yn, xn * yn], -1).reshape(-1, 6)
    c, *_ = np.linalg.lstsq(G, Ls.ravel(), rcond=None)
    yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]
    xn, yn = xx / L.shape[1] - 0.5, yy / L.shape[0] - 0.5
    surf = c[1] * xn + c[2] * yn + c[3] * (xn * xn - 1 / 12) + c[4] * (yn * yn - 1 / 12) + c[5] * xn * yn
    g = np.exp(surf)
    return a / g[..., None], float(g.max() / g.min() - 1), [float(v) for v in c]


def main():
    finfo = json.load(open(out_path("_work/faces.json")))
    ax0, ay0, ax1, ay1 = finfo["tone_maps"]["W_from_w14_to_u09"]["A_box_in_w14_px"]
    A = np.load(out_path("_work/faces/A.npy"))
    w14 = load_lin(ref("web/w14_ms_jute_veincut_48x110_04.jpg"), 1)
    regA = w14[ay0 + 10:ay1 - 10, ax0 + 10:ax1 - 10]
    Asc = zoom(A, ((ay1 - ay0 - 20) / A.shape[0], (ax1 - ax0 - 20) / A.shape[1], 1), order=1)
    W = apply_map(w14, quantile_map(regA.reshape(-1, 3), Asc.reshape(-1, 3)))
    Wd, trend, coef = quad_delight(W)
    excl = np.zeros(W.shape[:2], bool)
    m = 12                                   # a04 box accuracy (~5 px) plus margin
    excl[max(ay0 - m, 0):ay1 + m, max(ax0 - m, 0):ax1 + m] = True
    np.save(out_path("_work/faces/W_full.npy"), Wd)
    np.save(out_path("_work/faces/W_full_exclude.npy"), excl)
    v = np.clip(np.round(lin_to_srgb(Wd)), 0, 255).astype(np.uint8)
    im = Image.fromarray(v)
    im.thumbnail((800, 800))
    im.save(out_path("_work/faces/_VIEW_W_full.jpg"), quality=90)
    info = {"W_full_px": [int(Wd.shape[1]), int(Wd.shape[0])], "ppi": finfo["tone_maps"]["W_from_w14_to_u09"]["ppi_w14_on_swatch_scale"],
            "quadratic_trend_removed_rel": trend, "quadratic_coef_log": coef,
            "excluded_A_box_px": [int(max(ax0 - m, 0)), int(max(ay0 - m, 0)), int(ax1 + m), int(ay1 + m)],
            "excluded_share": float(excl.mean()),
            "mean_srgb": [float(x) for x in lin_to_srgb(Wd.reshape(-1, 3).mean(0))]}
    json.dump(info, open(out_path("_work/mosaic_sources.json"), "w"), indent=1)
    print(info)


if __name__ == "__main__":
    main()
