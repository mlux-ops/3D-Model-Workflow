"""Review helper: write a <=800 px view of an image (optionally a crop, optionally scaled)
into _work/ so it can be opened safely. Usage:
  python a10_view.py <image path relative to run dir> <out name> [x0 y0 x1 y1] [scale]"""

import os
import sys

from PIL import Image

from guard import RUN_DIR, save_image

Image.MAX_IMAGE_PIXELS = None


def main():
    src = os.path.join(RUN_DIR, sys.argv[1])
    name = sys.argv[2]
    im = Image.open(src)
    if im.mode.startswith("I"):
        import numpy as np
        a = np.asarray(im).astype(np.float64)
        lo, hi = np.percentile(a, 0.5), np.percentile(a, 99.5)
        im = Image.fromarray(np.clip((a - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8))
    elif im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if len(sys.argv) >= 7:
        x0, y0, x1, y1 = map(int, sys.argv[3:7])
        im = im.crop((x0, y0, x1, y1))
    if len(sys.argv) >= 8:
        s = float(sys.argv[7])
        im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST if s > 1 else Image.LANCZOS)
    w, h = im.size
    k = min(1.0, 800.0 / max(w, h))
    if k < 1.0:
        im = im.resize((int(w * k), int(h * k)), Image.LANCZOS)
    save_image(im, "_work", name + ".png")
    print("view", name, im.size)


if __name__ == "__main__":
    sys.exit(main())
