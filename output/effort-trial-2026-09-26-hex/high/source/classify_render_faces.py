"""Step 2: extract every complete face in the layout render, measure its texture
statistics and classify it Matte / Raw / Chiseled.

Metrics (on luminance, face interior only, inset 0.3 in from the joint):
  hp_std     std of (L - gaussian(L, 3 px))   -> relief energy (Matte is lowest)
  coherence  structure-tensor coherence        -> Chiseled grooves are strongly oriented
  orient     dominant groove direction (deg, image axes, 0 = horizontal, CCW positive)
  period     groove spacing, px and inches, from the autocorrelation perpendicular to grooves

Classification uses the metrics, then is checked against a labelled contact sheet
(textures/_REVIEW_render_faces.jpg); the final labels are written to
source/data/render_faces.json.
"""

import json

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import render_geom as g
from common import RENDER_PATH, hexnorm, out_path

img = np.asarray(Image.open(RENDER_PATH).convert("RGB")).astype(np.float64) / 255.0
L = img @ np.array([0.2126, 0.7152, 0.0722])
Hs, Ws = L.shape
faces = g.render_faces((Ws, Hs))

hp = L - ndimage.gaussian_filter(L, 3.0)
gx = ndimage.sobel(ndimage.gaussian_filter(L, 0.7), axis=1)
gy = ndimage.sobel(ndimage.gaussian_filter(L, 0.7), axis=0)
Jxx = ndimage.gaussian_filter(gx * gx, 4)
Jyy = ndimage.gaussian_filter(gy * gy, 4)
Jxy = ndimage.gaussian_filter(gx * gy, 4)

Y, X = np.mgrid[0:Hs, 0:Ws].astype(np.float64)
inset = 0.3 * g.RPPI
rec = []
for i, (cx, cy) in enumerate(faces):
    m = hexnorm(X - cx, Y - cy) < 5.0 * g.RPPI - inset
    a, b, c = Jxx[m].sum(), Jyy[m].sum(), Jxy[m].sum()
    lam1 = 0.5 * (a + b + np.sqrt((a - b) ** 2 + 4 * c * c))
    lam2 = 0.5 * (a + b - np.sqrt((a - b) ** 2 + 4 * c * c))
    coh = (lam1 - lam2) / (lam1 + lam2)
    # gradient direction angle; grooves run perpendicular to it. image y is down,
    # so negate to report CCW-positive angles in the usual sense
    grad_ang = 0.5 * np.degrees(np.arctan2(2 * c, a - b))
    groove = (-(grad_ang + 90.0)) % 180.0
    # groove period: 1-D profile of hp along the gradient direction
    th = np.radians(grad_ang)
    ux, uy = np.cos(th), np.sin(th)
    t = (X[m] - cx) * ux + (Y[m] - cy) * uy
    bins = np.round(t * 4).astype(int)
    bins -= bins.min()
    prof = np.bincount(bins, weights=hp[m]) / np.maximum(np.bincount(bins), 1)
    prof = prof - ndimage.gaussian_filter1d(prof, 40)
    ac = np.correlate(prof, prof, "full")[len(prof) - 1:]
    ac /= ac[0]
    lo = 8  # quarter-pixel units: search periods 2..40 px
    pk = lo + np.argmax(ac[lo:160])
    period_px = pk / 4.0
    rec.append({
        "render_id": i,
        "centre_xy": [round(cx, 2), round(cy, 2)],
        "hp_std": float(hp[m].std()),
        "coherence": float(coh),
        "groove_orient_deg": float(groove),
        "period_px": period_px,
        "period_in": period_px / g.RPPI,
        "period_ac": float(ac[pk]),
        "mean_rgb": [float(v) for v in img[m].mean(axis=0) * 255],
    })

# contact sheet with ids and metrics (render resolution, face crops 180 px)
tile = 200
cols = 8
rows = int(np.ceil(len(faces) / cols))
sheet = Image.new("RGB", (cols * tile, rows * (tile + 30)), (40, 40, 40))
rimg = Image.open(RENDER_PATH).convert("RGB")
dr = ImageDraw.Draw(sheet)
half = int(round(5.8 * g.RPPI))
for k, r in enumerate(rec):
    cx, cy = r["centre_xy"]
    crop = rimg.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half)))
    # stretch contrast for the review only
    a = np.asarray(crop).astype(np.float64)
    a = (a - a.mean()) * 3.0 + 128
    crop = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((tile - 10, tile - 10))
    x, y = (k % cols) * tile, (k // cols) * (tile + 30)
    sheet.paste(crop, (x + 5, y + 5))
    dr.text((x + 5, y + tile - 2), "%d hp%.4f c%.2f o%.0f p%.1f" % (
        k, r["hp_std"], r["coherence"], r["groove_orient_deg"], r["period_px"]), fill=(255, 255, 0))
p = out_path("textures", "_REVIEW_render_faces.jpg")
sheet.save(p, quality=90)
json.dump(rec, open(out_path("source", "data", "render_face_metrics.json"), "w"), indent=1)
for r in rec:
    print(r["render_id"], r["centre_xy"], "hp %.4f coh %.3f orient %5.1f period %.2fpx %.3fin ac %.2f" % (
        r["hp_std"], r["coherence"], r["groove_orient_deg"], r["period_px"], r["period_in"], r["period_ac"]))
