# -*- coding: utf-8 -*-
"""Ellipse fit to the left arc (backplate) of the oblique photo silhouette."""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

src = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/833919_midnight_black.jpg"
img = Image.open(src).convert("RGB")
im = np.asarray(img).astype(int)
H, W, _ = im.shape
mn = im.min(axis=2)
sil = mn < 246
sil = ndimage.binary_opening(sil, iterations=1)
lab, n = ndimage.label(sil)
sizes = ndimage.sum(sil, lab, range(1, n + 1))
sil = lab == (1 + int(np.argmax(sizes)))
sil = ndimage.binary_fill_holes(sil)

y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 440
y1 = int(sys.argv[2]) if len(sys.argv) > 2 else 1400
pts = []
for y in range(y0, y1, 3):
    xs = np.nonzero(sil[y])[0]
    pts.append((xs.min(), y))
pts = np.array(pts, float)


def conic_fit(p):
    mx, my = p[:, 0].mean(), p[:, 1].mean()
    x = p[:, 0] - mx
    y = p[:, 1] - my
    s = max(x.std(), y.std())
    x = x / s
    y = y / s
    D = np.c_[x * x, x * y, y * y, x, y, np.ones(len(x))]
    U, S, Vt = np.linalg.svd(D, full_matrices=False)
    return Vt[-1], mx, my, s


def to_ellipse(coef, mx, my, s):
    a, b, c, d, e, f = coef
    M = np.array([[a, b / 2], [b / 2, c]])
    ctr = np.linalg.solve(2 * M, -np.array([d, e]))
    M0 = np.array([[f, d / 2, e / 2], [d / 2, a, b / 2], [e / 2, b / 2, c]])
    val = np.linalg.det(M0) / np.linalg.det(M)
    ev, evec = np.linalg.eigh(M)
    q = -val / ev
    axes = np.sqrt(np.abs(q)) * s
    return ctr[0] * s + mx, ctr[1] * s + my, axes, evec


coef, mx, my, s = conic_fit(pts)
cx, cy, axes, evec = to_ellipse(coef, mx, my, s)
ia = int(np.argmax(axes))
A, B = axes[ia], axes[1 - ia]
maj = evec[:, ia]
if maj[1] > 0:
    maj = -maj
print("left arc ellipse: centre (%.1f, %.1f) semi-major %.1f semi-minor %.1f ratio %.4f" % (cx, cy, A, B, B / A))
print("major axis (x right, y down): (%.4f, %.4f) -> angle from vertical %.2f deg (positive = top leans right)" % (maj[0], maj[1], np.degrees(np.arctan2(maj[0], -maj[1]))))
t = np.linspace(0, 2 * np.pi, 720)
mnv = evec[:, 1 - ia]
ex = cx + A * np.cos(t) * maj[0] + B * np.sin(t) * mnv[0]
ey = cy + A * np.cos(t) * maj[1] + B * np.sin(t) * mnv[1]
# residual of arc points to the fitted ellipse
q = np.c_[pts[:, 0] - cx, pts[:, 1] - cy] @ np.c_[maj, mnv]
r = np.sqrt((q[:, 0] / A) ** 2 + (q[:, 1] / B) ** 2)
print("rms radial residual (px): %.2f" % (np.sqrt(np.mean(((r - 1) * np.sqrt(A * B)) ** 2))))
np.save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/mb_leftarc_ellipse.npy"), np.array([cx, cy, A, B, maj[0], maj[1]]))

dr = ImageDraw.Draw(img)
dr.line(list(zip(ex, ey)), fill=(255, 0, 0), width=4)
for x, y in pts[::5]:
    dr.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(0, 200, 255))
img.resize((800, int(800 * H / W))).save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/thumbs/mb_leftarc.png"))
