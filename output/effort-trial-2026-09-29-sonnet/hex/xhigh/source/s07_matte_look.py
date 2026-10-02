"""Contrast-stretched look at matte faces of the render (residual after subtracting the face mean)."""
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
imp = np.pad(im, ((220, 220), (220, 220), (0, 0)), mode="edge")
yy, xx = np.mgrid[0:H + 440, 0:W + 440].astype(np.float64)
yy -= 220
xx -= 220
feats = json.load(open(rg.WORK + "render_faces_raw.json"))
mat = [f for f in feats if f["hf"] < 1.6 and f["visfrac"] > 0.95 and f["coh"] < 0.1]
print("complete matte faces", len(mat))
tiles = []
for f in mat[:6]:
    cx, cy = f["cx"], f["cy"]
    y0, y1, x0, x1 = int(cy - 190) + 220, int(cy + 191) + 220, int(cx - 210) + 220, int(cx + 211) + 220
    sub = imp[y0:y1, x0:x1]
    d = rg.hex_dist(xx[y0:y1, x0:x1], yy[y0:y1, x0:x1], cx, cy)
    m = d < 0.9
    mean = sub[m].mean(axis=0)
    res = sub - mean
    Lr = res @ np.array([0.299, 0.587, 0.114])
    print("i%d j%d mean %s  L-resid std %.2f  lowfreq(s=8) std %.2f  chroma R-B resid std %.2f" % (f["i"], f["j"], np.round(mean, 1), Lr[m].std(), ndi.gaussian_filter(Lr, 8)[m].std(), (res[..., 0] - res[..., 2])[m].std()))
    v = np.clip(0.5 + Lr / 16.0, 0, 1) * m
    tiles.append(Image.fromarray((v * 255).astype(np.uint8)))
mont = Image.new("L", (3 * 260, 2 * 230))
for n, t in enumerate(tiles):
    mont.paste(t.resize((260, 230), Image.LANCZOS), ((n % 3) * 260, (n // 3) * 230))
guard.save_image(mont, rg.WORK + "thumbs/matte_resid_montage.png")
