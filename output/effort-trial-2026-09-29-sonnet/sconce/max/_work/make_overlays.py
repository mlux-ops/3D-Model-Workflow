# -*- coding: utf-8 -*-
"""Registers my Revit exports onto the product photos and draws my render's edges in red over the photo.
front: registered on the backplate circle; side: on the backplate plate (height + back face); angled: on the dark silhouette bbox.
Writes _work/overlays/overlay_<name>.png (photo-sized crop, <=800 px) and prints the registration numbers."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe

ROOT = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce"
RUN = ROOT + "/max"
OUT = RUN + "/_work/overlays/"


def load(p):
    return Image.open(p).convert("RGB")


def lum(im):
    return np.asarray(im).astype(float).min(axis=2)


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return xs.min(), ys.min(), xs.max(), ys.max()


def edges_of(im, thr=18.0):
    g = np.asarray(im.convert("L")).astype(float)
    gx = ndimage.sobel(g, axis=1)
    gy = ndimage.sobel(g, axis=0)
    mag = np.hypot(gx, gy) / 4.0
    e = mag > thr
    return ndimage.binary_dilation(e, iterations=1)


def transform_mine(im_m, s, dx, dy, size):
    w, h = im_m.size
    im2 = im_m.resize((max(1, int(round(w * s))), max(1, int(round(h * s)))), Image.LANCZOS)
    canvas = Image.new("RGB", size, (255, 255, 255))
    canvas.paste(im2, (int(round(dx)), int(round(dy))))
    return canvas


def overlay(photo, mine_reg, name, crop):
    e = edges_of(mine_reg)
    arr = np.asarray(photo).copy()
    arr[e] = (230, 20, 20)
    out = Image.fromarray(arr).crop(crop)
    s = min(1.0, 800.0 / max(out.size))
    out = out.resize((int(round(out.width * s)), int(round(out.height * s))), Image.LANCZOS)
    out.save(safe(OUT + "overlay_" + name + ".png"))
    print(name, "overlay", out.size)


# ---- side: photo (white on white) vs my hosted no-disc side view --------------------------------------
ph = load(ROOT + "/inputs/KW1041_MWT_side_reference.jpg")
mi = load(RUN + "/views/hosted_no_disc_side.png")
mp = lum(ph) < 250
mm = lum(mi) < 250
px0, py0, px1, py1 = bbox(mp)
mx0, my0, mx1, my1 = bbox(mm)


def plate_extent(mask):
    cnt = mask.sum(axis=0)
    first = int(np.nonzero(cnt >= 0.75 * cnt.max())[0].min())
    top, bot = None, None
    for x in range(first, first + 80):
        col = np.nonzero(mask[:, x])[0]
        if len(col):
            top = col.min() if top is None else min(top, col.min())
            bot = col.max() if bot is None else max(bot, col.max())
    return first, top, bot


x0p, tp, bp_ = plate_extent(mp)
x0m, tm, bm = plate_extent(mm)
hp = bp_ - tp + 1
hm = bm - tm + 1
s = hp / float(hm)
ycp = (tp + bp_) / 2.0
ycm = (tm + bm) / 2.0
print("side: photo plate x0=%d h=%d yc=%.1f | mine x0=%d h=%d yc=%.1f | scale %.4f (photo px/in %.1f)" % (
    x0p, hp, ycp, x0m, hm, ycm, s, hp / 5.25))
reg = transform_mine(mi, s, x0p - x0m * s, ycp - ycm * s, ph.size)
overlay(ph, reg, "side", (max(0, px0 - 40), max(0, py0 - 40), min(ph.width, px1 + 60), min(ph.height, py1 + 40)))

# ---- front: photo (white on white) vs my hosted no-disc front view, registered on the backplate circle ---
ph = load(ROOT + "/inputs/KW1041_MWT_oblique_reference.jpg")
mi = load(RUN + "/views/hosted_no_disc_front.png")
mm = lum(mi) < 250
mx0, my0, mx1, my1 = bbox(mm)
r_m = (mx1 - mx0 + 1) / 2.0
cxm = (mx0 + mx1) / 2.0
cym = (my0 + my1) / 2.0
cxp, cyp, r_p = 1200.0, 1157.5, 955.7
s = r_p / r_m
print("front: mine circle centre (%.1f, %.1f) r %.1f | photo centre (%.1f, %.1f) r %.1f | scale %.4f" % (cxm, cym, r_m, cxp, cyp, r_p, s))
reg = transform_mine(mi, s, cxp - cxm * s, cyp - cym * s, ph.size)
overlay(ph, reg, "front", (int(cxp - r_p - 60), int(cyp - r_p - 60), int(cxp + r_p + 60), int(cyp + r_p + 100)))

# ---- angled: photo hero vs my family oblique (no wall), registered on the dark silhouette bbox ---------
ph = load(ROOT + "/inputs/833919_midnight_black.jpg")
mi = load(RUN + "/views/family_oblique.png")
mp = lum(ph) < 235
# the globe is near white; keep only the dark structure for registration
dark_p = lum(ph) < 150
dark_m = lum(mi) < 150
px0, py0, px1, py1 = bbox(dark_p)
mx0, my0, mx1, my1 = bbox(dark_m)
s = (py1 - py0 + 1) / float(my1 - my0 + 1)
print("angled: photo dark bbox x %d..%d y %d..%d | mine x %d..%d y %d..%d | scale %.4f" % (px0, px1, py0, py1, mx0, mx1, my0, my1, s))
sx = (px1 - px0 + 1) / float(mx1 - mx0 + 1)
print("  width scale would be %.4f (height scale %.4f)" % (sx, s))
dx = (px0 + px1) / 2.0 - (mx0 + mx1) / 2.0 * s
dy = (py0 + py1) / 2.0 - (my0 + my1) / 2.0 * s
reg = transform_mine(mi, s, dx, dy, ph.size)
overlay(ph, reg, "angled", (0, 0, ph.width, ph.height))
