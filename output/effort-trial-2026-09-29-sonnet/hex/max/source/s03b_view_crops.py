"""Step 03b: helper montages of native-resolution face crops for visual inspection."""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_image, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402


def crop_face(rgb, grid, i, j, half=200):
    F = grid["F_px"]
    cp = grid["col_pitch_px"]
    cx = grid["x0"] + i * cp
    cy = grid["y0"] + ((F / 2.0) if (i % 2) else 0.0) + j * F
    x0, y0 = int(round(cx)) - half, int(round(cy)) - half
    H, W = rgb.shape[:2]
    out = np.full((2 * half, 2 * half, 3), 255.0)
    xs0, ys0 = max(x0, 0), max(y0, 0)
    xs1, ys1 = min(x0 + 2 * half, W), min(y0 + 2 * half, H)
    out[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = rgb[ys0:ys1, xs0:xs1]
    return out


def montage(crops, labels, ncol, stretch=None, mag=1):
    tiles = []
    for c, lab in zip(crops, labels):
        if stretch is not None:
            m = c.reshape(-1, 3).mean(0)
            c = np.clip((c - m) * stretch + 128.0, 0, 255)
        im = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8))
        if mag != 1:
            im = im.resize((im.width * mag, im.height * mag), Image.BICUBIC)
        ImageDraw.Draw(im).text((4, 4), lab, fill=(255, 0, 0))
        tiles.append(im)
    w, h = tiles[0].size
    nrow = (len(tiles) + ncol - 1) // ncol
    M = Image.new("RGB", (w * ncol, h * nrow), (255, 255, 255))
    for k, t in enumerate(tiles):
        M.paste(t, ((k % ncol) * w, (k // ncol) * h))
    return M


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    sets = {
        "view_types_a": ([(1, 4), (2, 1), (3, 3), (1, 2)], ["raw 1,4", "chis-vert 2,1", "chis-diag\\ 3,3", "chis-diag/ 1,2"], None),
        "view_matte_stretch": ([(2, 2), (3, 2), (5, 1), (-1, 2)], ["matte 2,2", "matte 3,2", "matte 5,1", "matte -1,2"], 10.0),
        "view_raw_b": ([(0, 3), (2, 3), (4, 1), (5, 4)], ["raw 0,3", "raw 2,3", "raw 4,1", "raw 5,4"], None),
    }
    for name, (ij, labs, st) in sets.items():
        crops = [crop_face(rgb, grid, i, j, 200) for (i, j) in ij]
        M = montage(crops, labs, 2, stretch=st)
        save_image(M, "work", "thumbs", name + ".png")


if __name__ == "__main__":
    main()
