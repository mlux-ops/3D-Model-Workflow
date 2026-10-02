"""Measure the chiseled groove geometry (period, orientation, profile, stroke continuity) on the render's complete chiseled faces."""
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
feats = json.load(open(rg.WORK + "render_faces_raw.json"))
chis = [f for f in feats if f["hf"] > 4.5 and f["visfrac"] > 0.9]
print("complete chiseled faces:", len(chis))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
N = 1024
out = []
for f in chis:
    cx, cy = f["cx"], f["cy"]
    y0, y1, x0, x1 = int(cy - 190), int(cy + 191), int(cx - 210), int(cx + 211)
    d = rg.hex_dist(xx[y0:y1, x0:x1], yy[y0:y1, x0:x1], cx, cy)
    sub = L[y0:y1, x0:x1]
    m = d < 0.85
    tap = np.clip((0.85 - d) / 0.10, 0, 1)
    w = (sub - ndi.gaussian_filter(sub, 5.0)) * tap
    pad = np.zeros((N, N))
    pad[:w.shape[0], :w.shape[1]] = w
    S = np.abs(np.fft.fftshift(np.fft.fft2(pad))) ** 2
    fy = np.fft.fftshift(np.fft.fftfreq(N))[:, None] * np.ones((1, N))
    fx = np.fft.fftshift(np.fft.fftfreq(N))[None, :] * np.ones((N, 1))
    fr = np.hypot(fx, fy)
    band = (fr > 1 / 14) & (fr < 1 / 3)
    Sb = np.where(band, S, 0)
    k = np.unravel_index(np.argmax(Sb), Sb.shape)
    fxp, fyp = fx[k], fy[k]
    per = 1 / np.hypot(fxp, fyp)
    ang = np.degrees(np.arctan2(fyp, fxp)) % 180   # wave-vector angle (normal to grooves), y down
    gdir = (ang + 90) % 180                          # groove direction
    # energy concentration: fraction of band energy in +-1.5 cycles-bin ring around the peak
    conc = Sb[(np.hypot(fx - fxp, fy - fyp) < 0.012) | (np.hypot(fx + fxp, fy + fyp) < 0.012)].sum() / Sb.sum()
    # cross profile: rotate so that grooves are vertical
    rot = ndi.rotate(sub, angle=(gdir - 90), reshape=False, order=3, mode="nearest") if False else None
    out.append(dict(i=f["i"], j=f["j"], period_px=float(per), period_in=float(per / rg.PX_PER_IN), wave_angle=float(ang), groove_dir=float(gdir), conc=float(conc)))
    print("i%d j%d period %.2f px = %.3f in (%.2f mm)  wave-angle %.1f  groove-dir %.1f  conc %.2f" % (f["i"], f["j"], per, per / rg.PX_PER_IN, per / rg.PX_PER_IN * 25.4, ang, gdir, conc))
json.dump(out, open(guard.safe(rg.WORK + "groove_measure.json"), "w"), indent=1)
p = np.array([o["period_px"] for o in out])
print("period px mean %.3f std %.3f ; in %.4f ; mm %.3f" % (p.mean(), p.std(), p.mean() / rg.PX_PER_IN, p.mean() / rg.PX_PER_IN * 25.4))
