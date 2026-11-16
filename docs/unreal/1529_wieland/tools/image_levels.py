"""Brightness of captures of the same view, by region, and a stacked picture for looking at.

Usage:
    python image_levels.py <a.png> <b.png> [<c.png> ...] [--rows N] [--cols N]
        [--crop x0,y0,x1,y1] [--stack-out <png>] [--stack-width W]

For each picture, prints the mean brightness (0 to 255, the plain average of
red, green and blue) of the whole frame and of each cell of a grid laid over
it (3 rows by 4 columns unless told otherwise), and the mean red, green and
blue of the frame; red minus blue says how warm or cool the frame reads.
Then, for every picture after the first, prints its difference from the
first, cell by cell.

--crop limits everything, the stacked picture included, to one box of each
picture, given in pixels.

Two captures of a moving scene differ pixel by pixel even when nothing was
changed (clouds, leaves, the upscaler settling), so a pixel comparison alone
overstates a change. A shift in the mean level of a whole region is a steadier
sign that the lighting itself changed. Compare a pair taken with nothing
changed first; its region differences are the noise floor.

--stack-out writes the pictures one above the other, each scaled to
--stack-width (1019 unless told otherwise), in the order given.

Needs Pillow and NumPy.
"""

import sys

import numpy as np
from PIL import Image


def option(argv, name, default):
    if name in argv:
        return argv[argv.index(name) + 1]
    return default


def open_picture(path, crop):
    picture = Image.open(path).convert("RGB")
    if crop:
        picture = picture.crop(crop)
    return picture


def grid_means(path, rows, cols, crop):
    colour = np.asarray(open_picture(path, crop), dtype=np.float64)
    pixels = colour.mean(axis=2)
    height, width = pixels.shape
    cells = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            cells[r, c] = pixels[r * height // rows:(r + 1) * height // rows, c * width // cols:(c + 1) * width // cols].mean()
    return float(pixels.mean()), cells, [float(colour[:, :, k].mean()) for k in range(3)]


def main(argv):
    value_options = ("--rows", "--cols", "--stack-out", "--stack-width", "--crop")
    paths = []
    skip = False
    for item in argv[1:]:
        if skip:
            skip = False
            continue
        if item in value_options:
            skip = True
            continue
        paths.append(item)
    if len(paths) < 2:
        print(__doc__)
        return 2
    rows = int(option(argv, "--rows", 3))
    cols = int(option(argv, "--cols", 4))
    crop_text = option(argv, "--crop", None)
    crop = tuple(int(v) for v in crop_text.split(",")) if crop_text else None
    results = [grid_means(path, rows, cols, crop) for path in paths]
    for path, (whole, cells, rgb) in zip(paths, results):
        print("%s\n  whole frame %.2f   red %.1f  green %.1f  blue %.1f   red minus blue %+.1f" % (
            path, whole, rgb[0], rgb[1], rgb[2], rgb[0] - rgb[2]))
        for r in range(rows):
            print("  row %d  " % (r + 1) + "  ".join("%7.2f" % cells[r, c] for c in range(cols)))
    base_whole, base_cells, _ = results[0]
    for path, (whole, cells, _) in zip(paths[1:], results[1:]):
        delta = cells - base_cells
        print("difference from the first: %s\n  whole frame %+.2f   largest cell %+.2f   mean of cell magnitudes %.2f" % (
            path, whole - base_whole, float(delta.flat[np.abs(delta).argmax()]), float(np.abs(delta).mean())))
        for r in range(rows):
            print("  row %d  " % (r + 1) + "  ".join("%+7.2f" % delta[r, c] for c in range(cols)))
    stack_out = option(argv, "--stack-out", None)
    if stack_out:
        width = int(option(argv, "--stack-width", 1019))
        scaled = []
        for path in paths:
            picture = open_picture(path, crop)
            scaled.append(picture.resize((width, round(picture.height * width / picture.width)), Image.LANCZOS))
        sheet = Image.new("RGB", (width, sum(p.height for p in scaled)))
        top = 0
        for picture in scaled:
            sheet.paste(picture, (0, top))
            top += picture.height
        sheet.save(stack_out)
        print("stacked picture written:", stack_out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
