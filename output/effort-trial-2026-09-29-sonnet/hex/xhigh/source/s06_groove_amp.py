"""Groove amplitude maps of the render's chiseled faces (demodulated at the measured pitch/orientation)."""
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
L = im @ np.array([0.299, 0.587, 0.114])
Lp = np.pad(L, 220, mode="edge")
yy, xx = np.mgrid[0:H + 440, 0:W + 440].astype(np.float64)
yy -= 220
xx -= 220
gm = json.load(open(rg.WORK + "groove_measure.json"))
per = 6.185
feats = json.load(open(rg.WORK + "render_faces_raw.json"))
chis = [f for f in feats if f["hf"] > 4.5 and f["visfrac"] > 0.9]
tiles = []
stats = []
for f in chis:
    cx, cy = f["cx"], f["cy"]
    ang = {-1: None}.get(0)
    # groove orientation from structure tensor rounded to the 30/90/150 set
    g = f["gang"] % 180
    wave = min([90 + 30 * 0, 0, 60, 120], key=lambda a: min(abs(g - a), 180 - abs(g - a)))
    wave = min([0.0, 60.0, 120.0], key=lambda a: min(abs((g - a) % 180), 180 - abs((g - a) % 180)))
    k = np.array([np.cos(np.radians(wave)), np.sin(np.radians(wave))]) / per
    y0, y1, x0, x1 = int(cy - 190) + 220, int(cy + 191) + 220, int(cx - 210) + 220, int(cx + 211) + 220
    sub = Lp[y0:y1, x0:x1]
    X = xx[y0:y1, x0:x1]
    Y = yy[y0:y1, x0:x1]
    d = rg.hex_dist(X, Y, cx, cy)
    hp = sub - ndi.gaussian_filter(sub, 6.0)
    z = hp * np.exp(-2j * np.pi * (k[0] * X + k[1] * Y))
    zs = ndi.gaussian_filter(z.real, 5.0) + 1j * ndi.gaussian_filter(z.imag, 5.0)
    a = 2 * np.abs(zs)
    m = d < 0.86
    am = a[m]
    stats.append((f["i"], f["j"], wave, am.mean(), am.std() / am.mean(), np.percentile(am, 5), np.percentile(am, 95)))
    print("i%d j%d wave %.0f  amp mean %.2f  CV %.2f  p5 %.2f p95 %.2f" % stats[-1])
    v = np.clip(a / 8.0, 0, 1) * (d < 0.98)
    tiles.append(Image.fromarray((v * 255).astype(np.uint8)))
mont = Image.new("L", (3 * 220, 3 * 190))
for n, t in enumerate(tiles[:9]):
    t2 = t.resize((220, 190), Image.LANCZOS)
    mont.paste(t2, ((n % 3) * 220, (n // 3) * 190))
guard.save_image(mont, rg.WORK + "thumbs/groove_amp_montage.png")
