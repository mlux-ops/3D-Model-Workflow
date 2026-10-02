"""Fit the flat-top hexagon lattice to the manufacturer layout render. Writes work/render_grid.json."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize
import guard

W = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/xhigh/work/"
im = np.asarray(Image.open(guard.inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, Wd = im.shape[:2]
R, G, B = im[..., 0], im[..., 1], im[..., 2]
sat = R - B
med = ndi.median_filter(sat, size=11)
J = np.clip(med - sat, 0, None)
Jb = ndi.gaussian_filter(J, 1.2)
print("J stats", J.mean(), J.max(), np.percentile(J, [50, 90, 99]))

# initial estimate of F from row profile
row = Jb.sum(axis=1)
row = row - ndi.uniform_filter1d(row, 60)
ac = np.correlate(row, row, mode="full")[len(row) - 1:]
lo, hi = 100, 220
half = lo + int(np.argmax(ac[lo:hi]))
print("half-F autocorr peak", half)


def edge_points(F, ox, oy, step=2.0):
    P = F * 2 / np.sqrt(3)
    pts = []
    for i in range(-2, int(Wd / (0.75 * P)) + 3):
        cx = ox + i * 0.75 * P
        for j in range(-2, int(H / F) + 3):
            cy = oy + j * F + (i % 2) * F / 2
            vx = np.array([P / 2, P / 4, -P / 4, -P / 2, -P / 4, P / 4])
            vy = np.array([0, F / 2, F / 2, 0, -F / 2, -F / 2])
            for k in range(6):
                x0, y0 = cx + vx[k], cy + vy[k]
                x1, y1 = cx + vx[(k + 1) % 6], cy + vy[(k + 1) % 6]
                n = max(2, int(np.hypot(x1 - x0, y1 - y0) / step))
                t = np.linspace(0, 1, n, endpoint=False)
                pts.append(np.stack([y0 + (y1 - y0) * t, x0 + (x1 - x0) * t]))
    return np.concatenate(pts, axis=1)


def score(p):
    F, ox, oy = p
    pts = edge_points(F, ox, oy, 3.0)
    ok = (pts[0] > 3) & (pts[0] < H - 4) & (pts[1] > 3) & (pts[1] < Wd - 4)
    v = ndi.map_coordinates(Jb, pts[:, ok], order=1)
    return -v.mean()


F0 = 2 * half
best = None
for F in np.arange(F0 - 6, F0 + 6.1, 1.0):
    P = F * 2 / np.sqrt(3)
    for ox in np.arange(0, 1.5 * P, 6.0):
        for oy in np.arange(0, F, 6.0):
            s = score((F, ox, oy))
            if best is None or s < best[0]:
                best = (s, F, ox, oy)
print("coarse", best)
res = minimize(score, [best[1], best[2], best[3]], method="Nelder-Mead", options={"xatol": 0.02, "fatol": 1e-5, "initial_simplex": [[best[1], best[2], best[3]], [best[1] + 1, best[2], best[3]], [best[1], best[2] + 3, best[3]], [best[1], best[2], best[3] + 3]]})
F, ox, oy = res.x
print("fit", res.x, res.fun)
json.dump({"F": F, "P": F * 2 / np.sqrt(3), "ox": ox, "oy": oy, "score": -res.fun}, open(guard.safe(W + "render_grid.json"), "w"), indent=1)

# overlay for verification
pts = edge_points(F, ox, oy, 1.0)
ov = im.copy().astype(np.uint8)
yy = np.round(pts[0]).astype(int)
xx = np.round(pts[1]).astype(int)
ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < Wd)
ov[yy[ok], xx[ok]] = (255, 0, 0)
o = Image.fromarray(ov)
o.thumbnail((800, 800), Image.LANCZOS)
guard.save_image(o, W + "thumbs/render_grid_overlay.png")
