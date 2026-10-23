# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from PIL import Image

src = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/KW1041_MWT_side_reference.jpg"
im = np.asarray(Image.open(src).convert("RGB")).astype(int)
H, W, _ = im.shape
lum = im.min(axis=2)
print("shape", im.shape, "bg corner", im[5, 5], im[H - 5, W - 5], "min lum", lum.min())
for thr in (254, 252, 250, 246, 240):
    mask = lum < thr
    ys, xs = np.nonzero(mask)
    print(thr, "count", mask.sum(), "x", xs.min(), xs.max(), "y", ys.min(), ys.max())

mask = lum < 250
# per-row extents (every 40 rows)
print("row extents (y: xmin..xmax)")
for y in range(0, H, 40):
    xs = np.nonzero(mask[y])[0]
    if len(xs):
        print(y, xs.min(), xs.max(), len(xs))
print("col extents (x: ymin..ymax)")
for x in range(0, W, 40):
    ys = np.nonzero(mask[:, x])[0]
    if len(ys):
        print(x, ys.min(), ys.max(), len(ys))
out = np.zeros((H, W, 3), dtype=np.uint8)
out[mask] = (255, 255, 255)
Image.fromarray(out).resize((800, 800), Image.LANCZOS).save(safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/thumbs/side_mask.png"))
