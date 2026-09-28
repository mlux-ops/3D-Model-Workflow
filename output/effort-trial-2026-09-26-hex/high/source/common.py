"""Shared paths, write guard and fixed atlas geometry for the ELM Formed Hexagon (Sand) build."""

import os

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.abspath(os.path.join(RUN_DIR, "..", "inputs"))
RENDER_PATH = os.path.join(INPUT_DIR, "elm_formed_hex_sand_layout_render.webp")
LIFESTYLE_PATH = os.path.join(INPUT_DIR, "elm_formed_hex_sand_lifestyle_angled.webp")


def out_path(*parts):
    """Resolve a path inside the run folder; refuse anything outside it."""
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def save_png(img, *parts, **kw):
    """Save through the guard; retry once on the known errno 22 quirk."""
    p = out_path(*parts)
    try:
        img.save(p, **kw)
    except OSError as e:
        if getattr(e, "errno", None) != 22:
            raise
        img.save(p, **kw)
    return p


# --- fixed geometry (from the brief) ---------------------------------------
FLATS_IN = 10.0            # across the flats (assumption: nominal "10 x 10")
JOINT_IN = 0.125           # 1/8 in
MODULE_F_IN = FLATS_IN + JOINT_IN
PPI = 64.0
COLS, ROWS = 8, 7
W, H = 4489, 4536
SAMPLE_W_IN = 70.148
SAMPLE_H_IN = 70.875

ROW_PITCH = H / ROWS                 # 648 px  (= 10.125 in * 64)
COL_PITCH = W / COLS                 # 561.125 px (= 0.75 * point-to-point module)
FACE_APOTHEM = FLATS_IN * PPI / 2.0  # 320 px, half the across-flats face
JOINT_HALF = JOINT_IN * PPI / 2.0    # 4 px each side of the joint centreline
MM_PER_IN = 25.4


def hexnorm(dx, dy):
    """Flat-top hexagon 'apothem norm': equals the perpendicular distance to the
    nearest edge line of a hexagon centred at the origin (flat edges top/bottom)."""
    ax, ay = np.abs(dx), np.abs(dy)
    return np.maximum(ay, ax * (np.sqrt(3.0) / 2.0) + ay * 0.5)


def atlas_centres():
    """Face centres on the torus. Index = 1 + col*ROWS + row. Odd columns are
    offset half a row. Even-column centres sit at y = (row+0.5)*ROW_PITCH so the
    top and bottom image edges run along joint centrelines of the even columns."""
    out = []
    for c in range(COLS):
        for r in range(ROWS):
            cx = (c + 0.5) * COL_PITCH
            cy = (r + 0.5) * ROW_PITCH + (0.5 * ROW_PITCH if c % 2 else 0.0)
            out.append((1 + c * ROWS + r, c, r, cx, cy % H))
    return out
