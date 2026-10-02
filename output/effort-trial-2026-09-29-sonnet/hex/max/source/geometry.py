"""Atlas geometry shared by the build, verify and preview scripts.

Flat-top hexagons on a torus, 8 columns x 7 rows = 56 faces at 64 px/in.
Module across flats 648 px (10.125 in) = 10.000 in face + 1/8 in joint; the joint is drawn as
4 px inside every face edge so the image wraps on both axes."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path  # noqa: E402

PPI = 64.0
MM_PER_PX = 25.4 / PPI
NCOL, NROW = 8, 7
MODULE = 648.0
INSET = 4.0
FACE_FLATS = MODULE - 2 * INSET                 # 640 px = 10.000 in
COL_PITCH = 4489 / 8.0
W, H = 4489, 4536
N_FACES = NCOL * NROW
COS30, SIN30 = np.cos(np.deg2rad(30.0)), np.sin(np.deg2rad(30.0))


def source_to_atlas_scale():
    grid = json.load(open(out_path("work", "render_grid.json")))
    return PPI / grid["px_per_in_if_10in_flats"]


def face_index(i, j):
    return i * NROW + j + 1


def face_centres():
    """list of dicts: index, i (column), j (row within column), cx, cy (cy wrapped into [0,H))."""
    out = []
    for i in range(NCOL):
        for j in range(NROW):
            cx = COL_PITCH / 2.0 + i * COL_PITCH
            cy = (MODULE / 2.0 if i % 2 == 0 else MODULE) + j * MODULE
            out.append({"index": face_index(i, j), "i": i, "j": j, "cx": cx, "cy": cy % H})
    return out


def hex_inside(dx, dy):
    """Signed distance (px) inside the flat-top module hexagon (positive inside)."""
    m = np.maximum(np.abs(dy), np.maximum(np.abs(dx * COS30 + dy * SIN30), np.abs(dx * COS30 - dy * SIN30)))
    return MODULE / 2.0 - m


def torus_delta(a, b, period):
    return (b - a + period / 2.0) % period - period / 2.0


def neighbour_lists(faces):
    """rings of 6 faces each per face (0-based lists): ~648 px, ~1122 px and ~1296 px away."""
    n = len(faces)
    rings = ([[] for _ in range(n)], [[] for _ in range(n)], [[] for _ in range(n)])
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            dx = torus_delta(faces[a]["cx"], faces[b]["cx"], W)
            dy = torus_delta(faces[a]["cy"], faces[b]["cy"], H)
            d = float(np.hypot(dx, dy))
            if d < 700:
                rings[0][a].append(b)
            elif 1000 < d < 1200:
                rings[1][a].append(b)
            elif 1200 <= d < 1400:
                rings[2][a].append(b)
    for r in rings:
        assert all(len(x) == 6 for x in r), [len(x) for x in r]
    return rings


def window_indices(cx, cy, half):
    x0 = int(round(cx)) - half
    y0 = int(round(cy)) - half
    xi = (x0 + np.arange(2 * half)) % W
    yi = (y0 + np.arange(2 * half)) % H
    return x0, y0, xi, yi


def window_offsets(cx, cy, half):
    """dx, dy of pixel centres of the (2*half)^2 window relative to the true face centre."""
    x0 = int(round(cx)) - half
    y0 = int(round(cy)) - half
    xs = x0 + np.arange(2 * half) + 0.5 - cx
    ys = y0 + np.arange(2 * half) + 0.5 - cy
    return np.meshgrid(xs, ys)
