"""Shared geometry and helpers for the ELM Formed Hexagon (Sand) build."""

import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

from guard import RUN_DIR, RENDER_PATH, LIFESTYLE_PATH, out_path

S3 = np.sqrt(3.0)

# ---- fixed atlas geometry (brief) -------------------------------------------------
FLATS_IN = 10.0                      # tile across the flats (assumption of "10 x 10 hexagon")
JOINT_IN = 0.125                     # 1/8 in joint
MODULE_F_IN = FLATS_IN + JOINT_IN    # 10.125 in across the flats, module
MODULE_R_IN = MODULE_F_IN / S3       # module circumradius (centre to corner), 5.8457 in
COL_PITCH_IN = 1.5 * MODULE_R_IN     # 8.7685 in
ROW_PITCH_IN = MODULE_F_IN
COLS, ROWS = 8, 7
PPI = 64.0
W = int(np.floor(COLS * COL_PITCH_IN * PPI))   # 4489
H = int(round(ROWS * ROW_PITCH_IN * PPI))      # 4536
SAMPLE_W_IN = COLS * COL_PITCH_IN               # 70.148 in
SAMPLE_H_IN = ROWS * ROW_PITCH_IN               # 70.875 in
PX_PER_IN_X = W / SAMPLE_W_IN                   # 63.9927 (exact wrap on the torus)
PX_PER_IN_Y = H / SAMPLE_H_IN                   # 64.0
HALF_JOINT_IN = JOINT_IN / 2.0

WORK = os.path.join(RUN_DIR, "_work")


def load_lattice():
    with open(os.path.join(WORK, "lattice.json")) as f:
        return json.load(f)


def render_rgb():
    return np.asarray(Image.open(RENDER_PATH).convert("RGB")).astype(np.float64)


def lifestyle_rgb():
    return np.asarray(Image.open(LIFESTYLE_PATH).convert("RGB")).astype(np.float64)


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(np.asarray(c, dtype=np.float64), 0.0, 1.0)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def luma(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def hex_edge_distance_local(dx, dy, apothem):
    """Flat-top regular hexagon centred at 0: signed distance to the edge (+ inside)."""
    return apothem - np.maximum(np.abs(dy), np.abs(dx) * S3 / 2.0 + np.abs(dy) * 0.5)


def render_cells(lat, margin_px=0.0):
    """Every lattice cell whose centre lies within one module of the render, with its
    centre and the fraction of its (margin-shrunk) face that is inside the image."""
    rp, cp, x0, y0 = lat["rp"], lat["cp"], lat["x0"], lat["y0"]
    Wr, Hr = lat["image_wh"]
    cells = []
    imin = int(np.floor((0 - x0) / cp)) - 1
    imax = int(np.ceil((Wr - x0) / cp)) + 1
    for i in range(imin, imax + 1):
        yoff = rp * 0.5 if (i % 2 != 0) else 0.0
        jmin = int(np.floor((0 - y0 - yoff) / rp)) - 1
        jmax = int(np.ceil((Hr - y0 - yoff) / rp)) + 1
        for j in range(jmin, jmax + 1):
            cx = x0 + i * cp
            cy = y0 + yoff + j * rp
            R = rp / S3
            # sample the hexagon on a fine grid to get the inside fraction
            g = np.linspace(-R, R, 81)
            gx, gy = np.meshgrid(g, g)
            inside = hex_edge_distance_local(gx, gy, rp * 0.5 - margin_px) > 0
            px = cx + gx[inside]
            py = cy + gy[inside]
            frac = float(((px >= 0) & (px < Wr) & (py >= 0) & (py < Hr)).mean())
            if frac > 0:
                cells.append({"i": i, "j": j, "cx": cx, "cy": cy, "frac": frac})
    return cells


def gaussian(a, s):
    return ndimage.gaussian_filter(a, s, mode="nearest")


def thumb(im, maxside=800):
    w, h = im.size
    s = min(1.0, maxside / float(max(w, h)))
    return im.resize((max(1, int(round(w * s))), max(1, int(round(h * s)))), Image.LANCZOS)
