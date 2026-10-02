"""Review helper: python s12b_thumbs.py <file in textures/> [x0 y0 w h] -> work/thumbs/view_<name>.png
(<= 800 px wide; an optional crop box in original pixels is taken first, magnified by nearest
neighbour when the crop is narrower than 400 px so single pixels stay visible)."""

import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import save_image, out_path  # noqa: E402


def main():
    name = sys.argv[1]
    im = Image.open(out_path("textures", name))
    if im.mode.startswith("I"):
        a = np.asarray(im).astype(np.float64)
        lo, hi = np.percentile(a, [0.5, 99.5])
        im = Image.fromarray(np.clip((a - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8))
    im = im.convert("RGB")
    if len(sys.argv) >= 6:
        x0, y0, w, h = [int(v) for v in sys.argv[2:6]]
        im = im.crop((x0, y0, x0 + w, y0 + h))
    if im.width < 400:
        f = max(1, 800 // im.width)
        im = im.resize((im.width * f, im.height * f), Image.NEAREST)
    elif im.width > 800:
        im = im.resize((800, int(round(im.height * 800.0 / im.width))), Image.LANCZOS)
    tag = "_".join(sys.argv[2:6]) if len(sys.argv) >= 6 else "full"
    out = "view_%s_%s.png" % (os.path.splitext(name)[0], tag)
    save_image(im, "work", "thumbs", out)
    print(out, im.size)


if __name__ == "__main__":
    main()
