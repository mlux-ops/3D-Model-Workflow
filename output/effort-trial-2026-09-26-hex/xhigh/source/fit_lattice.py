"""Refit the render's hex lattice in 2D: x0, y0, column pitch and row half-pitch are free
(the render's hexagons are not assumed regular). Score = dark-line response on the predicted
joint centrelines minus the response 3-6 px away. Updates _work/render_lattice.json.
"""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize
from guard import inp, write_text, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
lum = R @ np.array([0.2126, 0.7152, 0.0722])
D = np.clip(ndi.gaussian_filter(lum, 2.5) - lum, 0, None)
LP = os.path.join(WORK_DIR, "render_lattice.json")
L = json.load(open(LP))
rng = np.random.default_rng(1)
idx = rng.choice(H * W, 400000, replace=False)
py, px = np.unravel_index(idx, (H, W))
py = py + 0.0
px = px + 0.0
Dv = D[py.astype(int), px.astype(int)]


def edge_dist(x0, y0, cp, hf, X, Y):
    """distance to the nearest Voronoi boundary of the lattice: columns at x0 + j*cp; column j
    has centres at y0 + k*hf for k with (k + j) odd."""
    jc = np.round((X - x0) / cp).astype(np.int64)
    best = np.full(X.shape, 1e18)
    cands = []
    for dj in (-1, 0, 1):
        j = jc + dj
        cx = x0 + j * cp
        par = (j + 1) % 2                         # k parity for this column
        kf = np.floor((Y - y0) / hf).astype(np.int64)
        for dk in (-2, -1, 0, 1, 2, 3):
            k = kf + dk
            ok = (k % 2) == par
            cy = y0 + k * hf
            d = np.where(ok, (X - cx) ** 2 + (Y - cy) ** 2, 1e18)
            cands.append((d, cx, cy))
    dstack = np.stack([c[0] for c in cands])
    k0 = np.argmin(dstack, 0)
    d0 = np.take_along_axis(dstack, k0[None], 0)[0]
    cxs = np.stack([np.broadcast_to(c[1], X.shape) for c in cands])
    cys = np.stack([np.broadcast_to(c[2], X.shape) for c in cands])
    c0x = np.take_along_axis(cxs, k0[None], 0)[0]
    c0y = np.take_along_axis(cys, k0[None], 0)[0]
    ed = np.full(X.shape, 1e9)
    for k in range(len(cands)):
        sep = np.hypot(cxs[k] - c0x, cys[k] - c0y)
        v = np.where((sep > 1) & (dstack[k] < 1e17), (dstack[k] - d0) / (2 * np.maximum(sep, 1)), 1e9)
        ed = np.minimum(ed, v)
    return ed


def score(p, band):
    ed = edge_dist(p[0], p[1], p[2], p[3], px, py)
    on = ed < band
    off = (ed > band + 2) & (ed < band + 6)
    return -(Dv[on].mean() - Dv[off].mean())


p0 = np.array([L["x0"], L["y0"], L["col_pitch"], L["half_f"]])
print("start", p0, "score(1.5)", -score(p0, 1.5))
# coarse grid over x0 and column pitch (the poorly constrained pair)
best = None
for dx in np.arange(-24, 24.1, 2.0):
    for dp in np.arange(-4, 4.01, 0.5):
        p = p0 + [dx, 0, dp, 0]
        s = score(p, 2.5)
        if best is None or s < best[0]:
            best = (s, p)
print("grid best", best[1], -best[0])
res = minimize(score, best[1], args=(1.5,), method="Nelder-Mead",
               options={"xatol": 0.05, "fatol": 1e-4, "initial_simplex": None, "maxiter": 400})
p1 = res.x
res2 = minimize(score, p1, args=(1.0,), method="Nelder-Mead", options={"xatol": 0.02, "fatol": 1e-5, "maxiter": 400})
p2 = res2.x
print("refined", np.round(p2, 3), "score(1.0)", -res2.fun, " old score(1.0)", -score(p0, 1.0))
x0, y0, cp, hf = p2
Rc_x = cp / 1.5                      # horizontal circumradius implied by the column pitch
F = 2 * hf
print("F (across flats module) %.3f px; point-to-point module %.3f px; regular would be %.3f; aspect ratio vs regular %.4f"
      % (F, 2 * Rc_x, F * 2 / np.sqrt(3), (2 * Rc_x) / (F * 2 / np.sqrt(3))))
# slanted-joint check per image third
ed = edge_dist(x0, y0, cp, hf, px, py)
for a, b in ((0, W / 3), (W / 3, 2 * W / 3), (2 * W / 3, W)):
    sel = (px >= a) & (px < b)
    on = sel & (ed < 1.0)
    off = sel & (ed > 3) & (ed < 7)
    print("  x %4d-%4d: on-joint dark %.2f  off %.2f" % (a, b, Dv[on].mean(), Dv[off].mean()))

# rebuild the cell list with the refined lattice
cells = []
for j in range(-2, int(W / cp) + 3):
    cx = x0 + j * cp
    par = (j + 1) % 2
    for kk in range(-3, 15):
        if kk % 2 != par:
            continue
        cy = y0 + kk * hf
        inside = (cx - Rc_x >= 0) and (cx + Rc_x <= W - 1) and (cy - hf >= 0) and (cy + hf <= H - 1)
        cells.append({"j": j, "k": kk, "cx": cx, "cy": cy, "full": bool(inside)})
L2 = {"y0": y0, "half_f": hf, "F": F, "Rc": Rc_x, "col_pitch": cp, "x0": x0,
      "px_per_in": F / 10.125, "px_per_in_x": 2 * Rc_x / (10.125 * 2 / np.sqrt(3)),
      "fit": {"score": float(-res2.fun), "method": "2D dark-line fit, non-regular allowed"},
      "cells": cells}
write_text(LP, json.dumps(L2, indent=1))
print("cells", len(cells), "px/in (from flats) %.3f, (from width) %.3f" % (L2["px_per_in"], L2["px_per_in_x"]))
