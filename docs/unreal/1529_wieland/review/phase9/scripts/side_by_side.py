"""Phase 9: put the same crop of several pictures side by side, with a caption each, and print how they differ.

Usage:
    python -B side_by_side.py <output jpg> <left,top,right,bottom or "full"> <caption=picture> [<caption=picture> ...]

Prints, for every picture after the first, the mean brightness difference to the first over the crop (luminance
with the sRGB curve undone) and the share of 40 by 40 pixel blocks that differ by more than one stop.
"""

import sys

import numpy as np
from PIL import Image, ImageDraw


def luminance(image):
    c = np.asarray(image.convert("RGB")).astype(np.float32) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def blocks(lum, size=40):
    rows, cols = lum.shape[0] // size, lum.shape[1] // size
    return lum[:rows * size, :cols * size].reshape(rows, size, cols, size).mean(axis=(1, 3))


def main(argv):
    out, box = argv[1], argv[2]
    pairs = [item.split("=", 1) for item in argv[3:]]
    crops = []
    for caption, path in pairs:
        image = Image.open(path)
        if box != "full":
            image = image.crop(tuple(int(v) for v in box.split(",")))
        crops.append((caption, image))
    first = luminance(crops[0][1])
    for caption, image in crops[1:]:
        lum = luminance(image)
        a, b = blocks(first) + 0.003, blocks(lum) + 0.003
        off = np.abs(np.log2(b / a)) > 1.0
        print("%s against %s: mean %+.1f %%, blocks off by over one stop %.2f %%" % (
            caption, crops[0][0], (lum.mean() - first.mean()) / first.mean() * 100.0, off.mean() * 100.0))
    width = sum(image.width for _, image in crops)
    scale = min(1.0, 3600.0 / width)
    sheet = Image.new("RGB", (int(width * scale), int(crops[0][1].height * scale) + 28), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    x = 0
    for caption, image in crops:
        small = image.convert("RGB").resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
        sheet.paste(small, (x, 28))
        draw.text((x + 6, 8), caption, fill=(0, 0, 0))
        x += small.width
    sheet.save(out, quality=88)
    print("written", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
