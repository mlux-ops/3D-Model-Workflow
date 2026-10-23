# -*- coding: utf-8 -*-
"""RANSAC ellipse fit of the disc outline in the oblique photo (uses mb_boundary.npy from analyze_mb.py)."""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from PIL import Image, ImageDraw

tag = sys.argv[1] if len(sys.argv) > 1 else "mb"
src = sys.argv[2] if len(sys.argv) > 2 else "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/833919_midnight_black.jpg"
pts = np.load("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/%s_boundary.npy" % tag)
img = Image.open(src).convert("RGB")
W, H = img.size
# drop points hugging the frame edge (clipped disc) and the far-left body region
m = (pts[:, 1] > 6) & (pts[:, 1] < H - 7) & (pts[:, 0] > 6) & (pts[:, 0] < W - 7)
pts = pts[m]
print("points", len(pts))


def conic_fit(p):
    mx, my = p[:, 0].mean(), p[:, 1].mean()
    x = p[:, 0] - mx
    y = p[:, 1] - my
    s = max(x.std(), y.std())
    x = x / s
    y = y / s
    D = np.c_[x * x, x * y, y * y, x, y, np.ones(len(x))]
    U, S, Vt = np.linalg.svd(D, full_matrices=False)
    coef = Vt[-1]
    return coef, mx, my, s


def conic_to_ellipse(coef, mx, my, s):
    a, b, c, d, e, f = coef
    if b * b - 4 * a * c >= 0:
        return None
    M = np.array([[a, b / 2], [b / 2, c]])
    ctr = np.linalg.solve(2 * M, -np.array([d, e]))
    M0 = np.array([[f, d / 2, e / 2], [d / 2, a, b / 2], [e / 2, b / 2, c]])
    val = np.linalg.det(M0) / np.linalg.det(M)
    ev, evec = np.linalg.eigh(M)
    q = -val / ev
    if np.any(q <= 0):
        return None
    axes = np.sqrt(q) * s
    return ctr[0] * s + mx, ctr[1] * s + my, axes, evec


def dist_to_ellipse(p, cx, cy, axes, evec):
    q = np.c_[p[:, 0] - cx, p[:, 1] - cy] @ evec
    # approximate geometric distance by algebraic radial scaling
    r = np.sqrt((q[:, 0] / axes[0]) ** 2 + (q[:, 1] / axes[1]) ** 2)
    return np.abs(r - 1.0) * np.sqrt(axes[0] * axes[1])


rng = np.random.default_rng(3)
best = None
for it in range(6000):
    idx = rng.choice(len(pts), 8, replace=False)
    coef, mx, my, s = conic_fit(pts[idx])
    el = conic_to_ellipse(coef, mx, my, s)
    if el is None:
        continue
    cx, cy, axes, evec = el
    A, B = max(axes), min(axes)
    if A > 1400 or B < 200 or A / B > 4:
        continue
    d = dist_to_ellipse(pts, cx, cy, axes, evec)
    inl = (d < 3.0).sum()
    if best is None or inl > best[0]:
        best = (inl, cx, cy, axes, evec)
inl, cx, cy, axes, evec = best
d = dist_to_ellipse(pts, cx, cy, axes, evec)
sel = pts[d < 3.0]
for _ in range(4):
    coef, mx, my, s = conic_fit(sel)
    el = conic_to_ellipse(coef, mx, my, s)
    cx, cy, axes, evec = el
    d = dist_to_ellipse(pts, cx, cy, axes, evec)
    sel = pts[d < 3.0]
print("inliers", len(sel), "of", len(pts))
ia = int(np.argmax(axes))
A, B = axes[ia], axes[1 - ia]
maj = evec[:, ia]
ang = np.degrees(np.arctan2(maj[1], maj[0]))
print("ellipse centre (%.1f, %.1f) semi-major %.1f semi-minor %.1f ratio %.4f" % (cx, cy, A, B, B / A))
print("major axis direction (x right, y down): (%.4f, %.4f)  angle from +x %.2f deg ; from vertical %.2f deg" % (maj[0], maj[1], ang, ang - 90 if ang > 0 else ang + 90))
print("residual rms of inliers %.2f px" % np.sqrt((d[d < 3.0] ** 2).mean()))

dr = ImageDraw.Draw(img)
t = np.linspace(0, 2 * np.pi, 720)
mn = evec[:, 1 - ia]
ex = cx + A * np.cos(t) * maj[0] + B * np.sin(t) * mn[0]
ey = cy + A * np.cos(t) * maj[1] + B * np.sin(t) * mn[1]
dr.line(list(zip(ex, ey)), fill=(255, 0, 0), width=4)
for x, y in sel[::4]:
    dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(0, 200, 255))
img.resize((800, int(800 * H / W))).save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/thumbs/%s_ellipse.png" % tag))
np.save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/%s_ellipse.npy" % tag), np.array([cx, cy, A, B, maj[0], maj[1]]))
