# -*- coding: utf-8 -*-
"""Silhouette measurements from the white-finish side reference (pixels in the 2400x2400 original)."""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_open
import numpy as np
from PIL import Image

IN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/'
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/'

g = np.asarray(Image.open(IN + 'KW1041_MWT_side_reference.jpg').convert('L')).astype(float)
print('bg corner values', g[5, 5], g[2390, 2390], g[5, 2390])
for thr in (250, 246, 240):
    mask = g < thr
    ys, xs = np.nonzero(mask)
    print('thr', thr, 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())

mask = g < 246
ys, xs = np.nonzero(mask)
x_min, x_max, y_min, y_max = xs.min(), xs.max(), ys.min(), ys.max()

# per-column extent
print('column extents (x: ytop..ybot)')
for x in list(range(x_min, x_min + 140, 10)) + list(range(700, x_max + 1, 50)):
    col = np.nonzero(mask[:, x])[0]
    if len(col):
        print(x, col.min(), col.max(), 'height', col.max() - col.min() + 1)

# per-row extent
print('row extents (y: xleft..xright)')
for y in range(y_min, y_max + 1, 50):
    row = np.nonzero(mask[y, :])[0]
    if len(row):
        print(y, row.min(), row.max())
