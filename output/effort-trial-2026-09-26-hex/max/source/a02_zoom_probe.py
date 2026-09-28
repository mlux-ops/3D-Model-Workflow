"""Step 2: magnified probes of the render (joint profile, groove detail) for inspection."""

import sys

import numpy as np
from PIL import Image

from guard import RENDER_PATH, LIFESTYLE_PATH, save_image


def zoom(a, x0, y0, w, h, k):
    c = a[y0:y0 + h, x0:x0 + w]
    return Image.fromarray(c).resize((w * k, h * k), Image.NEAREST)


def main():
    ra = np.asarray(Image.open(RENDER_PATH).convert("RGB"))
    la = np.asarray(Image.open(LIFESTYLE_PATH).convert("RGB"))
    args = sys.argv[1:]
    # usage: name src x0 y0 w h k
    for i in range(0, len(args), 7):
        name, src, x0, y0, w, h, k = args[i:i + 7]
        a = ra if src == "r" else la
        save_image(zoom(a, int(x0), int(y0), int(w), int(h), int(k)), "_work", name + ".png")
        print("wrote", name)


if __name__ == "__main__":
    main()
