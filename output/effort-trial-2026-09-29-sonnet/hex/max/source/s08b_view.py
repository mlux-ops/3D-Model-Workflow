"""Review helper for step 08: source luminance, recovered height and albedo residual for a few
Raw faces, side by side (3 columns x N rows, 256 px tiles, 768 px wide)."""

import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_image, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s08_raw_height import padded_window, LUMW, NWIN  # noqa: E402
import json

FACES = [(0, 3), (1, 4), (4, 6)]


def stretch(a, valid, lo=1.0, hi=99.0):
    v = a[valid]
    l, h = np.percentile(v, lo), np.percentile(v, hi)
    return np.clip((a - l) / (h - l), 0, 1)


def tile(a01):
    im = Image.fromarray((a01 * 255).astype(np.uint8)).resize((256, 256), Image.LANCZOS)
    return np.asarray(im)


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    rows = []
    for (i, j) in FACES:
        win, tw, valid, _ = padded_window(lum, grid, i, j)
        h = np.load(out_path("work", "raw_h_%d_%d.npy" % (i, j)))
        alb = np.load(out_path("work", "raw_alb_%d_%d.npy" % (i, j)))
        al = alb @ LUMW
        rows.append(np.hstack([tile(stretch(win, valid)), tile(stretch(h, valid)), tile(stretch(al, valid))]))
    img = np.vstack(rows)
    save_image(Image.fromarray(img), "work", "thumbs", "raw_height_montage.png")
    print("saved", img.shape)


if __name__ == "__main__":
    main()
