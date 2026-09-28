"""Render lattice helpers: fitted hex centres and a joint-distance map for the layout render."""

import json
import os

import numpy as np

from common import RUN_DIR, hexnorm

LAT = json.load(open(os.path.join(RUN_DIR, "source", "data", "render_lattice.json")))
F = LAT["module_across_flats_px"]
X0, Y0 = LAT["centre0_xy"]
COLP = F * np.sqrt(3) / 2.0
RPPI = F / 10.125           # render pixels per inch


def nearest_centre(X, Y):
    """Return (hexnorm distance, cx, cy) of the nearest render lattice centre."""
    best = np.full(np.shape(X), 1e9)
    bcx = np.zeros(np.shape(X))
    bcy = np.zeros(np.shape(X))
    for par in (0, 1):
        cx0, cy0 = X0 + par * COLP, Y0 + par * F / 2.0
        c = np.round((X - cx0) / (2 * COLP))
        r = np.round((Y - cy0) / F)
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                cx = cx0 + (c + dc) * 2 * COLP
                cy = cy0 + (r + dr) * F
                d = hexnorm(X - cx, Y - cy)
                m = d < best
                best[m] = d[m]
                bcx[m] = cx[m]
                bcy[m] = cy[m]
    return best, bcx, bcy


def render_faces(size, margin_in=0.0):
    """All lattice centres whose whole face (plus margin) lies inside the render."""
    Ws, Hs = size
    half_pp = (10.0 / np.sqrt(3)) * RPPI     # half point-to-point of the face
    half_ff = 5.0 * RPPI
    out = []
    for par in (0, 1):
        for c in range(-6, 12):
            for r in range(-6, 12):
                cx = X0 + par * COLP + c * 2 * COLP
                cy = Y0 + par * F / 2.0 + r * F
                m = margin_in * RPPI
                if cx - half_pp - m >= 0 and cx + half_pp + m <= Ws - 1 and cy - half_ff - m >= 0 and cy + half_ff + m <= Hs - 1:
                    out.append((cx, cy))
    out.sort(key=lambda p: (round(p[1] / (F / 2)), p[0]))
    return out
