"""Measure groove pitch and orientation of every chiseled face in the finished Color.png and compare with the assigned wave angle and the measured source pitch.
Wave-vector angle is in image coordinates (x right, y down); 0 = vertical grooves. Writes work/groove_check.json."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
info = json.load(open(rg.WORK + "face_info.json"))
P = info["params"]
gp = json.load(open(rg.WORK + "groove_profile.json"))
color = np.asarray(Image.open(TEX + "Color.png").convert("RGB")).astype(np.float32)
lum = color @ np.array([0.299, 0.587, 0.114], np.float32)
H, W = lum.shape
N = 384
win = np.hanning(N)[:, None] * np.hanning(N)[None, :]
fy = np.fft.fftshift(np.fft.fftfreq(N))[:, None]
fx = np.fft.fftshift(np.fft.fftfreq(N))[None, :]
fr = np.hypot(fx, fy)
band = (fr > 1.0 / 22.0) & (fr < 1.0 / 8.0)
rows = []
for fc in info["faces"]:
    if fc["type"] != "chiseled":
        continue
    cy, cx = int(round(fc["cy"])), int(round(fc["cx"]))
    ys = np.arange(cy - N // 2, cy + N // 2) % H
    xs = np.arange(cx - N // 2, cx + N // 2) % W
    a = lum[np.ix_(ys, xs)]
    a = (a - a.mean()) * win
    S = np.abs(np.fft.fftshift(np.fft.fft2(a))) ** 2
    Sb = np.where(band, S, 0)
    # sub-bin peak by power-weighted centroid of the 5x5 neighbourhood of the maximum
    k = int(np.argmax(Sb))
    py, px = divmod(k, N)
    ys5, xs5 = np.mgrid[py - 2:py + 3, px - 2:px + 3]
    w = Sb[ys5, xs5]
    fyp = (fy[:, 0][ys5] * w).sum() / w.sum()
    fxp = (fx[0, :][xs5] * w).sum() / w.sum()
    ang = np.degrees(np.arctan2(fyp, fxp)) % 180.0
    ang = (ang + 0.0) % 180.0
    rows.append(dict(index=fc["index"], assigned_wave_deg=fc["rotation_deg"], measured_wave_deg=float(ang), measured_pitch_px=float(1.0 / np.hypot(fxp, fyp)),
                     measured_pitch_in=float(1.0 / np.hypot(fxp, fyp) / P["PPI"]), peak_share_of_band_power=float(Sb[ys5, xs5].sum() / Sb.sum())))
    print(rows[-1])
d_ang = [min(abs(r["measured_wave_deg"] - r["assigned_wave_deg"]) % 180, 180 - abs(r["measured_wave_deg"] - r["assigned_wave_deg"]) % 180) for r in rows]
pit = np.array([r["measured_pitch_in"] for r in rows])
out = dict(faces=rows, source_pitch_in=gp["period_in"], design_pitch_in=P["pitch_px"] / P["PPI"], pitch_in_mean=float(pit.mean()), pitch_in_min=float(pit.min()), pitch_in_max=float(pit.max()),
           max_angle_error_deg=float(max(d_ang)), mean_angle_error_deg=float(np.mean(d_ang)))
print({k: v for k, v in out.items() if k != "faces"})
json.dump(out, open(guard.safe(rg.WORK + "groove_check.json"), "w"), indent=1)
