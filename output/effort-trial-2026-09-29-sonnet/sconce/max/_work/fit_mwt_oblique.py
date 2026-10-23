# -*- coding: utf-8 -*-
"""Backplate outline ellipse in the matte-white oblique reference (white product on white ground, lum < 250 mask)."""
import numpy as np
from PIL import Image

SRC = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/KW1041_MWT_oblique_reference.jpg"
im = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
lum = im.min(axis=2)
mask = lum < 250
H, W = mask.shape

pts = []
for y in range(202, 1500, 6):
    xs = np.nonzero(mask[y])[0]
    if len(xs):
        pts.append((xs.min(), y))
        pts.append((xs.max(), y))
for x in range(260, 2140, 6):
    ys = np.nonzero(mask[:, x])[0]
    if len(ys):
        pts.append((x, ys.min()))
pts = np.unique(np.array(pts, dtype=float), axis=0)
print("boundary pts", len(pts))


def fit_ellipse(p):
    x = p[:, 0] - p[:, 0].mean()
    y = p[:, 1] - p[:, 1].mean()
    D = np.c_[x * x, x * y, y * y, x, y, np.ones_like(x)]
    S = D.T @ D
    C = np.zeros((6, 6))
    C[0, 2] = C[2, 0] = 2
    C[1, 1] = -1
    ev, evec = np.linalg.eig(np.linalg.inv(S) @ C)
    k = np.argmax(ev.real[np.isfinite(ev.real)] > 0)
    good = [i for i in range(6) if np.isfinite(ev[i]) and ev[i].real > 0]
    a = evec[:, good[0]].real
    A, B, Cc, Dd, E, F = a
    M0 = np.array([[A, B / 2], [B / 2, Cc]])
    c0 = np.linalg.solve(2 * M0, -np.array([Dd, E]))
    Fc = F + 0.5 * (Dd * c0[0] + E * c0[1])
    w, v = np.linalg.eigh(M0 / -Fc)
    ax = 1 / np.sqrt(w)
    cx = c0[0] + p[:, 0].mean()
    cy = c0[1] + p[:, 1].mean()
    return cx, cy, ax, v


cx, cy, ax, v = fit_ellipse(pts)
i_major = int(np.argmax(ax))
i_minor = 1 - i_major
maj = v[:, i_major]
mnr = v[:, i_minor]
ang = np.degrees(np.arctan2(maj[0], -maj[1]))
print("centre (%.1f, %.1f) semi-axes major %.1f minor %.1f ratio %.4f" % (cx, cy, ax[i_major], ax[i_minor], ax[i_minor] / ax[i_major]))
print("major axis direction (x,y) = (%.3f, %.3f), lean from vertical %.2f deg" % (maj[0], maj[1], ang))

xq = pts[:, 0] - cx
yq = pts[:, 1] - cy
u = xq * maj[0] + yq * maj[1]
w2 = xq * mnr[0] + yq * mnr[1]
rr = np.sqrt((u / ax[i_major]) ** 2 + (w2 / ax[i_minor]) ** 2)
print("fit residual (radial, relative): mean %.4f max %.4f" % (np.abs(rr - 1).mean(), np.abs(rr - 1).max()))

ys, xs = np.nonzero(mask)
print("mask bbox x %d..%d y %d..%d" % (xs.min(), xs.max(), ys.min(), ys.max()))
