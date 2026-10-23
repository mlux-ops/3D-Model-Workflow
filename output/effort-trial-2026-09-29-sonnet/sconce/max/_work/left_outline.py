# -*- coding: utf-8 -*-
"""Left outline of the fixture (backplate/body) in the oblique photo, and an ellipse fit to it."""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

src = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/833919_midnight_black.jpg"
img = Image.open(src).convert("RGB")
im = np.asarray(img).astype(int)
H, W, _ = im.shape
mn = im.min(axis=2)
sil = mn < 246
sil = ndimage.binary_opening(sil, iterations=1)
lab, n = ndimage.label(sil)
sizes = ndimage.sum(sil, lab, range(1, n + 1))
sil = lab == (1 + int(np.argmax(sizes)))
sil = ndimage.binary_fill_holes(sil)

# leftmost silhouette pixel per row
rows = np.arange(0, H, 6)
left = []
for y in rows:
    xs = np.nonzero(sil[y])[0]
    if len(xs):
        left.append((xs.min(), y))
left = np.array(left, float)
print("leftmost rows:", len(left))
for y in range(0, H, 60):
    xs = np.nonzero(sil[y])[0]
    if len(xs):
        print(y, xs.min(), end=" | ")
print()

# split: the disc's own left outline takes over near the top and bottom; print the curvature change by looking at dx/dy
dx = np.gradient(left[:, 0], left[:, 1])
for i in range(0, len(left), 8):
    print("y=%4d x=%6.1f dx/dy=%7.3f" % (left[i, 1], left[i, 0], dx[i]))

np.save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/mb_left.npy"), left)
