import os
import sys
import numpy as np
from PIL import Image

RUN = os.path.normpath("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/high").replace("\\", "/")
INPUTS = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/inputs"
RENDER = INPUTS + "/elm_formed_hex_sand_layout_render.webp"
LIFESTYLE = INPUTS + "/elm_formed_hex_sand_lifestyle_angled.webp"

PPI = 64
FLAT = 10.0
JOINT = 0.125
MOD = FLAT + JOINT              # 10.125 in across flats, module
COLS, ROWS = 8, 7
W, H = 4489, 4536


def guard(path):
    p = os.path.normpath(path).replace("\\", "/")
    root = RUN.rstrip("/") + "/"
    if not (p + "/").startswith(root) and not p.startswith(root):
        raise PermissionError("write outside run folder refused: " + p)
    d = os.path.dirname(p)
    os.makedirs(d, exist_ok=True)
    return p


def save_img(img, path, **kw):
    p = guard(path)
    for attempt in range(4):
        try:
            img.save(p, **kw)
            return
        except OSError as e:
            if attempt == 3:
                raise
            print("save retry", attempt, e)


def save_npy(arr, path):
    p = guard(path)
    np.save(p, arr)


def write_text(path, text):
    p = guard(path)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
