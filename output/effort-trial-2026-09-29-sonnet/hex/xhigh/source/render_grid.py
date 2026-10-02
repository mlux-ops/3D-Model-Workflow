"""Shared helpers: render lattice geometry, hex membership masks, and image loading."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import guard

WORK = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/xhigh/work/"
GRID = json.load(open(WORK + "render_grid.json"))
F, P, OX, OY = GRID["F"], GRID["P"], GRID["ox"], GRID["oy"]
PX_PER_IN = F / 10.125


def load_render():
    return np.asarray(Image.open(guard.inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)


def hex_list(w=2000, h=1888):
    out = []
    for i in range(-1, int(w / (0.75 * P)) + 2):
        cx = OX + i * 0.75 * P
        for j in range(-1, int(h / F) + 2):
            cy = OY + j * F + (i % 2) * F / 2
            out.append((i, j, cx, cy))
    return out


def hex_dist(xx, yy, cx, cy):
    """Normalised hex 'radius': <1 inside a flat-top hexagon with across-flats F (edges at 1.0)."""
    dx = np.abs(xx - cx)
    dy = np.abs(yy - cy)
    # flat-top: flats at |dy| = F/2 ; slanted edges: |dy|*cos30... distance to slanted edge
    d1 = dy / (F / 2)
    d2 = (dx * np.sqrt(3) / 2 + dy * 0.5) / (F / 2)
    return np.maximum(d1, d2)
