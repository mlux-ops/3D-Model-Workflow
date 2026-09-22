"""Review images for the two non-repeating colour atlases, per the WORKFLOW.md
acceptance gate: wrap preview, correctly scaled surface, multiple atlas repeats so a
large atlas cannot merely hide periodicity in a small swatch.

For each finish, writes into its own textures/:
  _PREVIEW_atlas_full.jpg     the whole 3x3 atlas, so all 9 cells are visible at once
  _PREVIEW_wrap_2x2.jpg       2x2 repeat of the atlas (=> 6x6 = 36 virtual panels),
                              downsampled, to check for an obvious large-scale repeat
  _REVIEW_wrap_seam.jpg       the four-way corner of the atlas wrap, magnified
  _REVIEW_cell_grid.jpg       every cell at readable size with its (transform, roll)
                              label, to confirm no two adjacent cells are identical
"""

import json
import os

import numpy as np
from PIL import Image, ImageDraw

FLAT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BELMONT_DIR = os.path.dirname(FLAT_DIR)
CROSSCUT_DIR = os.path.join(BELMONT_DIR, "ElmStone_Jute_CrossCut_24x48")


def out_path(base_dir, *parts):
    p = os.path.abspath(os.path.join(base_dir, *parts))
    if os.path.commonpath([p, base_dir]) != base_dir:
        raise RuntimeError("refusing to write outside %s: %s" % (base_dir, p))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def process(base_dir, color_filename, report_filename, label):
    rep = json.load(open(os.path.join(base_dir, "textures", report_filename)))
    W, H = rep["pixels"]
    cols, rows = rep["atlas_cells"]
    cw, ch = W // cols, H // rows
    color = Image.open(os.path.join(base_dir, "textures", color_filename)).convert("RGB")
    print("%s: %s  %d x %d px  cell %d x %d" % (label, color_filename, W, H, cw, ch))

    # 1. whole atlas
    color.resize((1600, int(1600 * H / W)), Image.LANCZOS).save(
        out_path(base_dir, "textures", "_PREVIEW_atlas_full.jpg"), quality=90)

    # 2. 2x2 repeat of the whole atlas
    arr = np.asarray(color)
    two = np.tile(arr, (2, 2, 1))
    Image.fromarray(two).resize((1800, int(1800 * two.shape[0] / two.shape[1])),
                                Image.LANCZOS).save(
        out_path(base_dir, "textures", "_PREVIEW_wrap_2x2.jpg"), quality=90)

    # 3. four-way corner of the wrap, magnified
    k = 380
    def four_way(a):
        top = np.concatenate([a[-k:, -k:], a[-k:, :k]], axis=1)
        bot = np.concatenate([a[:k, -k:], a[:k, :k]], axis=1)
        return np.concatenate([top, bot], axis=0)
    Image.fromarray(four_way(arr)).save(
        out_path(base_dir, "textures", "_REVIEW_wrap_seam.jpg"), quality=92)

    # 4. every cell, labelled, at a size where composition is actually legible
    thumb_w = 380
    thumb_h = int(thumb_w * ch / cw)
    grid = Image.new("RGB", (thumb_w * cols + 8 * (cols - 1),
                             thumb_h * rows + 8 * (rows - 1)), (255, 255, 255))
    d = ImageDraw.Draw(grid)
    for j in range(rows):
        for i in range(cols):
            cell_img = color.crop((i * cw, j * ch, (i + 1) * cw, (j + 1) * ch)).resize(
                (thumb_w, thumb_h), Image.LANCZOS)
            x0, y0 = i * (thumb_w + 8), j * (thumb_h + 8)
            grid.paste(cell_img, (x0, y0))
            d.text((x0 + 4, y0 + 4), "cell (%d,%d)" % (i, j), fill=(255, 0, 0))
    grid.save(out_path(base_dir, "textures", "_REVIEW_cell_grid.jpg"), quality=90)
    print("  wrote 4 preview/review images")


def main():
    process(FLAT_DIR, "Color_NonRepeating.png", "nonrepeating_flat_report.json", "flat/vein-cut")
    process(CROSSCUT_DIR, "Color.png", "nonrepeating_crosscut_report.json", "fluted/cross-cut")


if __name__ == "__main__":
    main()
