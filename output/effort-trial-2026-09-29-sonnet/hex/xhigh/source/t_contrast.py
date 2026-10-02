"""Compare luminance texture strength per face type: render faces vs the built atlas (multi-scale band-pass std, groove amplitude)."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import guard
import render_grid as rg

S = 64.0 / rg.PX_PER_IN
LW = np.array([0.299, 0.587, 0.114])
rend = rg.load_render() @ LW
H, W = rend.shape
feats = json.load(open(rg.WORK + "render_faces_raw.json"))
info = json.load(open(rg.WORK + "face_info.json"))
color = np.asarray(Image.open(guard.RUN + "/textures/Color.png").convert("RGB")).astype(np.float32)
La = color @ LW.astype(np.float32)
ids = np.asarray(Image.open(guard.RUN + "/textures/face_ids.png"))
gp = json.load(open(rg.WORK + "groove_profile.json"))


def ftype(f):
    if f["hf"] > 4.5:
        return "chiseled"
    if f["coh"] > 0.2:
        return "raw"
    return "matte"


scales = [1.0, 2.0, 4.0, 8.0, 16.0]
res = {}
for typ in ("matte", "raw", "chiseled"):
    r_rows = []
    for f in feats:
        if ftype(f) != typ or f["visfrac"] < 0.95:
            continue
        y0, x0 = int(f["cy"]) - 200, int(f["cx"]) - 200
        if y0 < 0 or x0 < 0 or y0 + 400 > H or x0 + 400 > W:
            continue
        blk = rend[y0:y0 + 400, x0:x0 + 400]
        yy, xx = np.mgrid[y0:y0 + 400, x0:x0 + 400]
        m = rg.hex_dist(xx, yy, f["cx"], f["cy"]) < 0.85
        row = []
        prev = blk
        for s in scales:
            g = ndi.gaussian_filter(blk, s)
            row.append(float((prev - g)[m].std()))
            prev = g
        row.append(float((ndi.gaussian_filter(blk, 32.0) - blk)[m].std()))
        r_rows.append(row)
    a_rows = []
    for fc in info["faces"]:
        if fc["type"] != typ:
            continue
        cy, cx = int(round(fc["cy"])), int(round(fc["cx"]))
        ys = np.arange(cy - 400, cy + 400) % La.shape[0]
        xs = np.arange(cx - 400, cx + 400) % La.shape[1]
        blk = La[np.ix_(ys, xs)]
        fid = ids[np.ix_(ys, xs)]
        m = fid == fc["index"]
        m = ndi.binary_erosion(m, iterations=int(0.15 * 320))
        row = []
        prev = blk
        for s in scales:
            g = ndi.gaussian_filter(blk, s * S)
            row.append(float((prev - g)[m].std()))
            prev = g
        row.append(float((ndi.gaussian_filter(blk, 32.0 * S) - blk)[m].std()))
        a_rows.append(row)
    r = np.mean(r_rows, axis=0)
    a = np.mean(a_rows, axis=0)
    print("%-9s render n=%2d  band std (DoG sigma 1,2,4,8,16 | resid to 32): %s" % (typ, len(r_rows), np.round(r, 2)))
    print("%-9s atlas  n=%2d                                              : %s   ratio atlas/render %s" % (typ, len(a_rows), np.round(a, 2), np.round(a / r, 2)))
