# -*- coding: utf-8 -*-
"""Segment the Midnight Black photo: fixture silhouette, globe circle, disc ellipse."""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

src = sys.argv[1] if len(sys.argv) > 1 else "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/833919_midnight_black.jpg"
tag = sys.argv[2] if len(sys.argv) > 2 else "mb"
img = Image.open(src).convert("RGB")
im = np.asarray(img).astype(int)
H, W, _ = im.shape
lum = im.mean(axis=2)
mn = im.min(axis=2)
print("shape", im.shape, "corner", im[3, 3])

sil = mn < 246
sil = ndimage.binary_opening(sil, iterations=1)
lab, n = ndimage.label(sil)
sizes = ndimage.sum(sil, lab, range(1, n + 1))
keep = 1 + int(np.argmax(sizes))
sil = lab == keep
sil = ndimage.binary_fill_holes(sil)
ys, xs = np.nonzero(sil)
print("silhouette bbox x %d..%d y %d..%d  area %d" % (xs.min(), xs.max(), ys.min(), ys.max(), sil.sum()))

metal = sil & (lum < 150)
glass = sil & (lum >= 150)
glass = ndimage.binary_opening(glass, iterations=3)
lab, n = ndimage.label(glass)
sizes = ndimage.sum(glass, lab, range(1, n + 1))
glass = lab == (1 + int(np.argmax(sizes)))
glass = ndimage.binary_fill_holes(glass)
gy, gx = np.nonzero(glass)
print("glass bbox x %d..%d y %d..%d area %d" % (gx.min(), gx.max(), gy.min(), gy.max(), glass.sum()))


def boundary(mask):
    er = ndimage.binary_erosion(mask)
    return mask & ~er


def fit_ellipse(pts):
    """Direct algebraic conic fit, returns (cx, cy, a, b, angle_deg)."""
    x = pts[:, 0] - pts[:, 0].mean()
    y = pts[:, 1] - pts[:, 1].mean()
    mx, my = pts[:, 0].mean(), pts[:, 1].mean()
    D = np.c_[x * x, x * y, y * y, x, y, np.ones(len(x))]
    S = D.T @ D
    C = np.zeros((6, 6))
    C[0, 2] = C[2, 0] = 2
    C[1, 1] = -1
    w, v = np.linalg.eig(np.linalg.inv(S) @ C)
    w = np.real(w)
    v = np.real(v)
    idx = np.argmax(w[np.isfinite(w)])
    a_, b_, c_, d_, e_, f_ = v[:, idx]
    M0 = np.array([[f_, d_ / 2, e_ / 2], [d_ / 2, a_, b_ / 2], [e_ / 2, b_ / 2, c_]])
    M = np.array([[a_, b_ / 2], [b_ / 2, c_]])
    ev, evec = np.linalg.eig(M)
    center = np.linalg.solve(2 * M, -np.array([d_, e_]))
    val = np.linalg.det(M0) / np.linalg.det(M)
    axes = np.sqrt(np.abs(-val / ev))
    ang = np.degrees(np.arctan2(evec[1, 0], evec[0, 0]))
    return center[0] + mx, center[1] + my, axes[0], axes[1], ang, evec


# globe: fit a circle to the boundary points of the glass region that lie on the silhouette outline
gb = boundary(glass)
gyb, gxb = np.nonzero(gb)
gpts = np.c_[gxb, gyb].astype(float)
A = np.c_[2 * gpts[:, 0], 2 * gpts[:, 1], np.ones(len(gpts))]
bb = gpts[:, 0] ** 2 + gpts[:, 1] ** 2
c, *_ = np.linalg.lstsq(A, bb, rcond=None)
gcx, gcy = c[0], c[1]
gr = np.sqrt(c[2] + gcx ** 2 + gcy ** 2)
res = np.sqrt((gpts[:, 0] - gcx) ** 2 + (gpts[:, 1] - gcy) ** 2) - gr
print("globe circle fit: c=(%.1f, %.1f) r=%.1f resid std %.2f max %.1f" % (gcx, gcy, gr, res.std(), np.abs(res).max()))
# robust: use only points within 3 px of fit and refit
for it in range(3):
    keepm = np.abs(res) < 4
    p2 = gpts[keepm]
    A = np.c_[2 * p2[:, 0], 2 * p2[:, 1], np.ones(len(p2))]
    bb = p2[:, 0] ** 2 + p2[:, 1] ** 2
    c, *_ = np.linalg.lstsq(A, bb, rcond=None)
    gcx, gcy = c[0], c[1]
    gr = np.sqrt(c[2] + gcx ** 2 + gcy ** 2)
    res = np.sqrt((gpts[:, 0] - gcx) ** 2 + (gpts[:, 1] - gcy) ** 2) - gr
    print(" refit: c=(%.1f, %.1f) r=%.1f, n=%d" % (gcx, gcy, gr, keepm.sum()))

img2 = img.copy()
d = ImageDraw.Draw(img2)
d.ellipse((gcx - gr, gcy - gr, gcx + gr, gcy + gr), outline=(255, 0, 0), width=3)

# disc outline: silhouette boundary points that are not glass-adjacent (dilate glass to exclude), and drop the left body region
sb = boundary(sil)
near_glass = ndimage.binary_dilation(glass, iterations=12)
sby, sbx = np.nonzero(sb & ~near_glass)
pts = np.c_[sbx, sby].astype(float)
np.save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/%s_boundary.npy" % tag), pts)
print("silhouette boundary pts (non-glass):", len(pts))
# draw the boundary in green for review
for x, y in pts[::3]:
    d.point((x, y), fill=(0, 255, 0))
img2.resize((800, 800)).save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/thumbs/%s_fit.png" % tag))
