"""Compare two captures of the same view, pixel by pixel.

Usage:
    python compare_images.py <a.png> <b.png> [--diff-out <png>] [--crop-out <prefix>]

Prints how far the two images differ: the mean and root-mean-square
difference on a 0 to 255 scale, the share of pixels whose largest channel
difference exceeds 8 and 24 levels, and the box that holds the pixels over 24.

Two captures of an unchanged scene never match exactly, because the engine's
temporal upscaler and its lighting keep settling. Compare a pair taken with
nothing changed first; that is the noise floor for the view.

--diff-out writes the difference as a picture, brightened eight times.
--crop-out writes the changed box cut from each image as <prefix>_a.png and
<prefix>_b.png, for looking at side by side.

Needs Pillow and NumPy.
"""

import sys

import numpy as np
from PIL import Image


def load(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    a_path, b_path = argv[1], argv[2]
    a, b = load(a_path), load(b_path)
    if a.shape != b.shape:
        print("sizes differ: %s and %s" % (a.shape[:2], b.shape[:2]))
        return 1
    diff = np.abs(a - b)
    worst = diff.max(axis=2)
    total = worst.size
    over8 = int((worst > 8).sum())
    over24 = int((worst > 24).sum())
    print("size            %d x %d" % (a.shape[1], a.shape[0]))
    print("mean difference %.3f of 255" % float(diff.mean()))
    print("rms difference  %.3f of 255" % float(np.sqrt((diff.astype(np.float64) ** 2).mean())))
    print("pixels over 8   %.3f%% (%d)" % (100.0 * over8 / total, over8))
    print("pixels over 24  %.3f%% (%d)" % (100.0 * over24 / total, over24))
    box = None
    if over24:
        ys, xs = np.nonzero(worst > 24)
        box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        print("box over 24     x %d to %d, y %d to %d" % (box[0], box[2], box[1], box[3]))
        cols = (worst > 24).sum(axis=0)
        rows = (worst > 24).sum(axis=1)
        print("densest column  x = %d (%d pixels); densest row y = %d (%d pixels)" % (int(cols.argmax()), int(cols.max()), int(rows.argmax()), int(rows.max())))
    if "--diff-out" in argv:
        out = argv[argv.index("--diff-out") + 1]
        Image.fromarray(np.clip(diff * 8, 0, 255).astype(np.uint8)).save(out)
        print("difference picture written:", out)
    if "--crop-out" in argv and box:
        prefix = argv[argv.index("--crop-out") + 1]
        pad = 24
        crop = (max(0, box[0] - pad), max(0, box[1] - pad), min(a.shape[1], box[2] + pad), min(a.shape[0], box[3] + pad))
        Image.open(a_path).convert("RGB").crop(crop).save(prefix + "_a.png")
        Image.open(b_path).convert("RGB").crop(crop).save(prefix + "_b.png")
        print("crops written:", prefix + "_a.png", prefix + "_b.png", "box", crop)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
