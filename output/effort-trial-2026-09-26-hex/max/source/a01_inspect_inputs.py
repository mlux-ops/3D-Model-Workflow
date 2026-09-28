"""Step 1: thumbnails and crops of the two inputs for visual inspection (<=800 px)."""

import sys

import numpy as np
from PIL import Image

from guard import RENDER_PATH, LIFESTYLE_PATH, save_image


def thumb(im, maxside=800):
    w, h = im.size
    s = min(1.0, maxside / float(max(w, h)))
    return im.resize((max(1, int(round(w * s))), max(1, int(round(h * s)))), Image.LANCZOS)


def main():
    r = Image.open(RENDER_PATH).convert("RGB")
    l = Image.open(LIFESTYLE_PATH).convert("RGB")
    print("render", r.size, Image.open(RENDER_PATH).mode)
    print("lifestyle", l.size, Image.open(LIFESTYLE_PATH).mode)
    save_image(thumb(r), "_work", "render_thumb.png")
    save_image(thumb(l), "_work", "lifestyle_thumb.png")
    # quadrant crops of the render at 1:1 (800 px windows)
    ra = np.asarray(r)
    H, W = ra.shape[:2]
    for name, (x0, y0) in {"r_tl": (0, 0), "r_tr": (W - 800, 0), "r_bl": (0, H - 800),
                           "r_br": (W - 800, H - 800), "r_c": (W // 2 - 400, H // 2 - 400)}.items():
        save_image(Image.fromarray(ra[y0:y0 + 800, x0:x0 + 800]), "_work", name + ".png")
    la = np.asarray(l)
    H, W = la.shape[:2]
    for name, (x0, y0) in {"l_top": (W // 2 - 400, 0), "l_mid": (W // 2 - 400, H // 2 - 400),
                           "l_left": (0, H // 2 - 400), "l_bot": (W // 2 - 400, H - 800)}.items():
        save_image(Image.fromarray(la[y0:y0 + 800, x0:x0 + 800]), "_work", name + ".png")
    # basic stats
    for nm, a in (("render", ra), ("lifestyle", la)):
        f = a.astype(np.float64)
        print(nm, "mean RGB", f.reshape(-1, 3).mean(0).round(1), "min", f.min(), "max", f.max())


if __name__ == "__main__":
    sys.exit(main())
