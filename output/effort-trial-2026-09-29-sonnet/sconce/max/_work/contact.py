# -*- coding: utf-8 -*-
"""contact.py <out_name> <view1> [view2 ...] : 2 x N grid of views/<name>.png cells (400 px each, labelled), <= 800 px wide.
Writes _work/thumbs/<out_name>.png (through safe())."""
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
CELL = 400
LABEL = 22

out_name = sys.argv[1]
names = sys.argv[2:]
cols = 2
rows = (len(names) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CELL, rows * (CELL + LABEL)), (255, 255, 255))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
except Exception:
    font = ImageFont.load_default()
for i, n in enumerate(names):
    im = Image.open(RUN + "/views/" + n + ".png").convert("RGB")
    s = min(float(CELL) / im.width, float(CELL) / im.height)
    im2 = im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))), Image.LANCZOS)
    cx = (i % cols) * CELL
    cy = (i // cols) * (CELL + LABEL)
    sheet.paste(im2, (cx + (CELL - im2.width) // 2, cy + LABEL + (CELL - im2.height) // 2))
    d.rectangle((cx, cy, cx + CELL - 1, cy + LABEL - 1), fill=(235, 235, 235))
    d.text((cx + 6, cy + 3), "%s  (%dx%d)" % (n, im.width, im.height), fill=(0, 0, 0), font=font)
    d.rectangle((cx, cy, cx + CELL - 1, cy + CELL + LABEL - 1), outline=(200, 200, 200))
out = safe(RUN + "/_work/thumbs/" + out_name + ".png")
sheet.save(out)
print(out, sheet.size)
