# -*- coding: utf-8 -*-
"""Measure the side reference silhouette: backplate strip, body top/bottom, cut-face line, shade circle."""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from PIL import Image, ImageDraw

src = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/KW1041_MWT_side_reference.jpg"
img = Image.open(src).convert("RGB")
im = np.asarray(img).astype(int)
H, W, _ = im.shape
lum = im.min(axis=2)
mask = lum < 250
mask[:, :500] = False  # drop the stray streak at x~390-405

# outer boundary of the shade: rightmost mask pixel per row, for rows where the sphere dominates
pts = []
for y in range(880, 1740, 4):
    xs = np.nonzero(mask[y])[0]
    if len(xs):
        pts.append((xs.max(), y))
pts = np.array(pts, float)
sel = pts[pts[:, 0] > 1300]

def fit_circle(p):
    x, y = p[:, 0], p[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0], c[1]
    r = np.sqrt(c[2] + cx ** 2 + cy ** 2)
    res = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r
    return cx, cy, r, np.abs(res).max(), res.std()

cx, cy, r, rmax, rstd = fit_circle(sel)
print("shade circle: cx=%.1f cy=%.1f r=%.1f (dia %.1f) max resid %.1f std %.2f" % (cx, cy, r, 2 * r, rmax, rstd))

# also top/bottom of the shade at the sphere's widest column
col = mask[:, int(cx)]
ys = np.nonzero(col)[0]
print("column through sphere centre: y", ys.min(), ys.max())

# backplate strip: columns 560..700, vertical extent of the strip at its far-left column
for x in (570, 575, 580, 600, 620, 640, 650, 655):
    ys = np.nonzero(mask[:, x])[0]
    if len(ys):
        print("col", x, "y", ys.min(), ys.max(), "span", ys.max() - ys.min())

# strip thickness rows
for y in (580, 600, 620, 640, 660, 680, 700, 1000, 1203, 1500, 1700, 1750, 1780, 1800, 1820):
    xs = np.nonzero(mask[y])[0]
    if len(xs):
        # first contiguous run from the left
        run_end = xs[0]
        for v in xs[1:]:
            if v == run_end + 1:
                run_end = v
            else:
                break
        print("row", y, "leftmost", xs[0], "first run ends", run_end, "run len", run_end - xs[0] + 1)

# body top edge: the row where mask runs long to the right
top_rows = {}
for y in range(660, 740):
    xs = np.nonzero(mask[y])[0]
    if len(xs):
        top_rows[y] = (xs.min(), xs.max())
for y in (680, 684, 686, 688, 690, 694, 700, 710, 720, 740):
    print("top", y, top_rows.get(y))

# body bottom edge (rows near 1700-1730)
for y in range(1690, 1745, 5):
    xs = np.nonzero(mask[y])[0]
    if len(xs):
        print("bot", y, xs.min(), xs.max(), len(xs))

# slanted cut-face line from the upper part: max x per row 700..900
sl = []
for y in range(700, 900, 4):
    xs = np.nonzero(mask[y])[0]
    sl.append((xs.max(), y))
sl = np.array(sl, float)
A = np.c_[sl[:, 1], np.ones(len(sl))]
m, c = np.linalg.lstsq(A, sl[:, 0], rcond=None)[0]
print("upper slanted edge: x = %.4f*y + %.1f ; angle from vertical %.2f deg" % (m, c, np.degrees(np.arctan(-m))))
# the lower slanted edge: for rows 1560..1690 find where the body edge is: leftmost x of the sphere/body union isn't distinguishable;
# use the notch where the body meets the shade: examine per-row max x and look for the discontinuity
for y in range(1500, 1740, 20):
    xs = np.nonzero(mask[y])[0]
    # transitions
    gaps = np.nonzero(np.diff(xs) > 1)[0]
    print("row", y, "min", xs.min(), "max", xs.max(), "gaps", [(xs[g], xs[g + 1]) for g in gaps][:3])

d = ImageDraw.Draw(img)
d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 0, 0), width=4)
d.line((m * 700 + c, 700, m * 1720 + c, 1720), fill=(0, 0, 255), width=4)
img.crop((500, 500, 2100, 1900)).resize((800, 700)).save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/thumbs/side_fit.png"))
