"""Step 01: header facts and <=800 px thumbnails / quadrant crops of both sources."""

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, LIFESTYLE_PATH, save_image  # noqa: E402


def main():
    for name, p in (("render", RENDER_PATH), ("lifestyle", LIFESTYLE_PATH)):
        im = Image.open(p)
        print(name, im.size, im.mode, im.format, im.info.keys())
        rgb = im.convert("RGB")
        s = 800.0 / max(rgb.size)
        t = rgb.resize((int(round(rgb.width * s)), int(round(rgb.height * s))), Image.LANCZOS)
        save_image(t, "work", "thumbs", name + "_full_800.png")

    r = Image.open(RENDER_PATH).convert("RGB")
    W, H = r.size
    # 2x2 quadrants of the render, each <= 800 px (crop 1000 x 944 -> 800 x 755)
    for qi, (x0, y0) in enumerate(((0, 0), (W // 2, 0), (0, H // 2), (W // 2, H // 2))):
        c = r.crop((x0, y0, x0 + W // 2, y0 + H // 2))
        c = c.resize((800, int(round(800.0 * c.height / c.width))), Image.LANCZOS)
        save_image(c, "work", "thumbs", "render_q%d.png" % qi)


if __name__ == "__main__":
    main()
