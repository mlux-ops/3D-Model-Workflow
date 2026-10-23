# -*- coding: utf-8 -*-
"""Builds views/_REVIEW_compare.jpg: product photos next to my Revit exports at matching angles (tight-cropped, same cell size)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe

ROOT = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce"
RUN = ROOT + "/max"
CELL = 640
PAD = 0.04
LABEL_H = 34
BG = (255, 255, 255)


def content_box(im, thresh=246):
    a = np.asarray(im.convert("RGB")).astype(int)
    mask = a.min(axis=2) < thresh
    ys, xs = np.nonzero(mask)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def fit_cell(path, crop=None):
    im = Image.open(path).convert("RGB")
    if crop is not None:
        im = im.crop(crop)
    x0, y0, x1, y1 = content_box(im)
    px = int((x1 - x0) * PAD)
    py = int((y1 - y0) * PAD)
    box = (max(0, x0 - px), max(0, y0 - py), min(im.width, x1 + px), min(im.height, y1 + py))
    im = im.crop(box)
    s = min(float(CELL) / im.width, float(CELL) / im.height)
    im = im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.LANCZOS)
    cell = Image.new("RGB", (CELL, CELL), BG)
    cell.paste(im, ((CELL - im.width) // 2, (CELL - im.height) // 2))
    return cell


ROWS = [
    ("FRONT (about 4 deg above axis) - matte-white product photo has no disc",
     [("PHOTO  KW1041_MWT_oblique_reference.jpg", ROOT + "/inputs/KW1041_MWT_oblique_reference.jpg", None),
      ("MINE  hosted, Show Disc = No", RUN + "/views/hosted_no_disc_front.png", None),
      ("MINE  family front, disc on (no photo of this view)", RUN + "/views/family_front.png", None)]),
    ("SIDE (looking along the wall) - matte-white product photo has no disc",
     [("PHOTO  KW1041_MWT_side_reference.jpg", ROOT + "/inputs/KW1041_MWT_side_reference.jpg", None),
      ("MINE  hosted, Show Disc = No", RUN + "/views/hosted_no_disc_side.png", None),
      ("MINE  family side, disc on (no photo of this view)", RUN + "/views/family_side.png", None)]),
    ("ANGLED - Midnight Black product photo (disc on)",
     [("PHOTO  833919_midnight_black.jpg", ROOT + "/inputs/833919_midnight_black.jpg", None),
      ("MINE  family oblique (yaw -54.5, pitch -10.5)", RUN + "/views/family_oblique.png", None),
      ("MINE  hosted on wall, same camera", RUN + "/views/hosted_on_wall_oblique.png", None)]),
]

try:
    FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    FONT_B = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
except Exception:
    FONT = ImageFont.load_default()
    FONT_B = FONT

W = CELL * 3
H = len(ROWS) * (CELL + LABEL_H * 2)
sheet = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sheet)
y = 0
for title, cells in ROWS:
    d.rectangle((0, y, W, y + LABEL_H), fill=(235, 235, 235))
    d.text((8, y + 6), title, fill=(0, 0, 0), font=FONT_B)
    y += LABEL_H
    for i, (cap, path, crop) in enumerate(cells):
        cell = fit_cell(path, crop)
        sheet.paste(cell, (i * CELL, y))
        d.rectangle((i * CELL, y, i * CELL + CELL - 1, y + CELL - 1), outline=(200, 200, 200))
    y += CELL
    for i, (cap, path, crop) in enumerate(cells):
        d.text((i * CELL + 8, y + 6), cap, fill=(160, 0, 0) if cap.startswith("PHOTO") else (0, 70, 140), font=FONT)
    y += LABEL_H
out = safe(RUN + "/views/_REVIEW_compare.jpg")
sheet.save(out, quality=90)
print(out, sheet.size)
