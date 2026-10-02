"""Classify each hexagon in the render; print features; save features json."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import guard
import render_grid as rg

im = rg.load_render()
H, W = im.shape[:2]
L = im @ np.array([0.299, 0.587, 0.114])
hp = L - ndi.gaussian_filter(L, 4.0)
hp = ndi.gaussian_filter(hp, 0.6)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
gy, gx = np.gradient(ndi.gaussian_filter(L, 1.0))
FULL_PX = 0.866025 * rg.F * rg.F * 0.81

feats = []
for (i, j, cx, cy) in rg.hex_list(W, H):
    y0, y1 = max(0, int(cy - 200)), min(H, int(cy + 200))
    x0, x1 = max(0, int(cx - 220)), min(W, int(cx + 220))
    if y1 <= y0 or x1 <= x0:
        continue
    d = rg.hex_dist(xx[y0:y1, x0:x1], yy[y0:y1, x0:x1], cx, cy)
    sub = d < 0.90
    if sub.sum() < 2000:
        continue
    hsub = hp[y0:y1, x0:x1][sub]
    gxm, gym = gx[y0:y1, x0:x1][sub], gy[y0:y1, x0:x1][sub]
    jxx, jyy, jxy = (gxm * gxm).mean(), (gym * gym).mean(), (gxm * gym).mean()
    coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-12)
    ang = 0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy))
    feats.append(dict(i=i, j=j, cx=cx, cy=cy, npx=int(sub.sum()), visfrac=float(sub.sum() / FULL_PX), hf=float(hsub.std()),
                      coh=float(coh), gang=float(ang), meanRGB=[float(v) for v in im[y0:y1, x0:x1][sub].mean(axis=0)]))
json.dump(feats, open(guard.safe(rg.WORK + "render_faces_raw.json"), "w"), indent=1)
print("n hexes", len(feats))
for f in feats:
    print("i%2d j%2d c(%5.0f,%5.0f) vis %.2f hf %.2f coh %.2f ang %6.1f rgb %s" % (f["i"], f["j"], f["cx"], f["cy"], f["visfrac"], f["hf"], f["coh"], f["gang"], [round(v) for v in f["meanRGB"]]))
