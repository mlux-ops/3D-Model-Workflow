# -*- coding: utf-8 -*-
"""Least-squares circle fit to the shade silhouette in the white-finish side reference (image work, outside Revit)."""
import os
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import dump_json

IN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/KW1041_MWT_side_reference.jpg'
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/fit_sphere_side.json'

g = np.asarray(Image.open(IN).convert('L')).astype(float)
mask = g < 246
PLATE_BACK_X = 569.0
PLATE_CY = (569 + 1836) / 2.0
PX_PER_IN = (1836 - 569 + 1) / 5.25


def fit(pts):
    x = pts[:, 0]
    y = pts[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0], sol[1]
    r = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
    res = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r
    return cx, cy, r, float(np.abs(res).max()), float(res.std())


res = {}
for x0, x1 in ((1350, 1900), (1400, 1900), (1300, 1930)):
    pts = []
    for x in range(x0, x1 + 1, 4):
        col = np.nonzero(mask[:, x])[0]
        if len(col) > 50:
            pts.append((x, col.min()))
            pts.append((x, col.max()))
    pts = np.array(pts, float)
    cx, cy, r, mx, sd = fit(pts)
    res['%d-%d' % (x0, x1)] = {'cx_px': cx, 'cy_px': cy, 'r_px': r, 'max_res': mx, 'std': sd,
                               'r_in_at_plate_scale': r / PX_PER_IN,
                               'cx_from_plate_back_in': (cx - PLATE_BACK_X) / PX_PER_IN,
                               'cy_below_plate_center_in': (cy - PLATE_CY) / PX_PER_IN,
                               'apex_from_plate_back_in': (cx + r - PLATE_BACK_X) / PX_PER_IN}
res['px_per_in'] = PX_PER_IN
dump_json(res, OUT)
for k, v in res.items():
    print(k, v)
