"""Review helper: crop a box from a source image, optionally magnify / contrast-stretch,
and write it (<=800 px wide) to work/thumbs/ so it can be opened.

usage: python view_crop.py <render|lifestyle> x0 y0 w h mag stretch outname
"""

import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, LIFESTYLE_PATH, save_image  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402


def main():
    which, x0, y0, w, h, mag, stretch, name = sys.argv[1:9]
    x0, y0, w, h = int(x0), int(y0), int(w), int(h)
    mag, stretch = float(mag), float(stretch)
    path = RENDER_PATH if which == "render" else LIFESTYLE_PATH
    rgb = load_srgb(path)
    c = rgb[y0:y0 + h, x0:x0 + w]
    if stretch != 1.0:
        m = c.reshape(-1, 3).mean(0)
        c = (c - m) * stretch + 128.0
    im = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8))
    if mag != 1.0:
        im = im.resize((int(round(im.width * mag)), int(round(im.height * mag))), Image.LANCZOS)
    assert im.width <= 800, "crop wider than 800 px"
    save_image(im, "work", "thumbs", name + ".png")
    print("saved", name, im.size)


if __name__ == "__main__":
    main()
