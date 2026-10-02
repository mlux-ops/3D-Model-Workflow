"""Measure the joint (grout) colour and cross-profile in the render, and the joint appearance in the lifestyle image."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import guard
import render_grid as rg

im = rg.load_render()
H, W = im.shape[:2]
# horizontal joints: rows near oy + k*F/2 ; average profile of +-8 rows around each joint, over columns whose hexes are matte on both sides
feats = json.load(open(rg.WORK + "render_faces_raw.json"))
prof = []
for f in feats:
    if f["visfrac"] < 0.95 or f["hf"] > 1.6:
        continue
    # this hex's top edge: y = cy - F/2, x in [cx - P/4, cx + P/4]
    y = f["cy"] - rg.F / 2
    x0, x1 = int(f["cx"] - rg.P / 4 + 12), int(f["cx"] + rg.P / 4 - 12)
    if y < 12 or y > H - 12:
        continue
    ys = np.arange(-8, 9) + y
    cols = np.arange(x0, x1)
    samp = np.stack([ndi.map_coordinates(im[..., c], np.meshgrid(ys, cols, indexing="ij"), order=1) for c in range(3)], axis=-1)  # (17, ncols, 3)
    prof.append(samp.mean(axis=1))
prof = np.mean(prof, axis=0)
print("mean cross profile of horizontal joints, offsets -8..8 px (render, R G B):")
for o, p in zip(range(-8, 9), prof):
    print("%3d  %6.1f %6.1f %6.1f" % (o, *p))
bg = 0.5 * (prof[:3].mean(axis=0) + prof[-3:].mean(axis=0))
k = np.argmin(prof.sum(axis=1) * 0 + (prof[:, 0] - prof[:, 2]))  # lowest R-B = most neutral
print("background tone", np.round(bg, 1), " most neutral row offset", k - 8, "colour", np.round(prof[k], 1))
# per-edge centreline sample for joint colour statistics over the whole fitted lattice (all edge types)
cl = []
for (i, j, cx, cy) in rg.hex_list(W, H):
    vx = np.array([rg.P / 2, rg.P / 4, -rg.P / 4, -rg.P / 2, -rg.P / 4, rg.P / 4])
    vy = np.array([0, rg.F / 2, rg.F / 2, 0, -rg.F / 2, -rg.F / 2])
    for k2 in range(6):
        x0_, y0_ = cx + vx[k2], cy + vy[k2]
        x1_, y1_ = cx + vx[(k2 + 1) % 6], cy + vy[(k2 + 1) % 6]
        n = 60
        t = np.linspace(0.15, 0.85, n)
        px, py = x0_ + (x1_ - x0_) * t, y0_ + (y1_ - y0_) * t
        ok = (px > 6) & (px < W - 7) & (py > 6) & (py < H - 7)
        if ok.sum() < n:
            continue
        # search +-2 px perpendicular for the most neutral pixel (joint centre uncertainty)
        nx, ny = -(y1_ - y0_), (x1_ - x0_)
        nn = np.hypot(nx, ny)
        nx, ny = nx / nn, ny / nn
        best = None
        for off in np.arange(-2, 2.01, 0.5):
            v = np.stack([ndi.map_coordinates(im[..., c], [py + ny * off, px + nx * off], order=1) for c in range(3)], axis=-1)
            s = (v[:, 0] - v[:, 2]).mean()
            if best is None or s < best[0]:
                best = (s, v)
        cl.append(best[1])
cl = np.concatenate(cl)
print("centreline samples", len(cl))
print("centreline median", np.round(np.median(cl, axis=0), 1), " p10", np.round(np.percentile(cl, 10, axis=0), 1), " p90", np.round(np.percentile(cl, 90, axis=0), 1))
json.dump(dict(profile_offsets=list(range(-8, 9)), profile=prof.tolist(), background=bg.tolist(), centreline_median=np.median(cl, axis=0).tolist(),
               centreline_p10=np.percentile(cl, 10, axis=0).tolist(), centreline_p90=np.percentile(cl, 90, axis=0).tolist()), open(guard.safe(rg.WORK + "joint_measure.json"), "w"), indent=1)
