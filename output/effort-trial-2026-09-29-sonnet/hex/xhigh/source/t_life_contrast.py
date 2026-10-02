"""Lifestyle-image texture strength (band-pass luminance std / local mean) for chiseled, raw and matte faces, vs the same measure on the grazing preview."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import guard
import render_grid as rg

LW = np.array([0.299, 0.587, 0.114])
life = np.asarray(Image.open(guard.inp("elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")).astype(float) @ LW
s = 1414 / 566.0
ppi_life = 165 * s / 10.0
print("lifestyle approx px/in across the flats: %.1f" % ppi_life)
boxes = {"chiseled": (262, 90, 350, 240), "raw": (150, 385, 250, 500), "raw2": (30, 130, 130, 260), "matte": (135, 20, 265, 120), "matte2": (145, 205, 260, 330)}
graze = np.asarray(Image.open(rg.WORK + "grazing_full.png").convert("RGB")).astype(np.float32) @ LW.astype(np.float32)
import json
info = json.load(open(rg.WORK + "face_info.json"))
from PIL import Image as I
ids = np.asarray(I.open(guard.RUN + "/textures/face_ids.png"))
k = 64.0 / ppi_life


def band(a, s0, s1):
    return ndi.gaussian_filter(a, s0) - ndi.gaussian_filter(a, s1)


for name, (x0, y0, x1, y1) in boxes.items():
    w = life[int(y0 * s):int(y1 * s), int(x0 * s):int(x1 * s)]
    mean = ndi.gaussian_filter(w, 30)
    out = []
    for (a, b) in ((1, 3), (3, 9), (9, 27)):
        out.append(float((band(w, a, b) / mean)[20:-20, 20:-20].std()))
    print("lifestyle %-9s band std/mean (sigma 1-3, 3-9, 9-27 life px): %s" % (name, np.round(out, 4)))
for typ in ("chiseled", "raw", "matte"):
    rows = []
    for fc in info["faces"]:
        if fc["type"] != typ:
            continue
        cy, cx = int(round(fc["cy"])), int(round(fc["cx"]))
        ys = np.arange(cy - 300, cy + 300) % graze.shape[0]
        xs = np.arange(cx - 300, cx + 300) % graze.shape[1]
        w = graze[np.ix_(ys, xs)]
        f = ids[np.ix_(ys, xs)] == fc["index"]
        f = ndi.binary_erosion(f, iterations=60)
        mean = ndi.gaussian_filter(w, 30 * k)
        row = [float((band(w, a * k, b * k) / mean)[f].std()) for (a, b) in ((1, 3), (3, 9), (9, 27))]
        rows.append(row)
    print("preview   %-9s band std/mean (same physical bands): %s" % (typ, np.round(np.mean(rows, axis=0), 4)))
