"""Step 1: measure the hexagon lattice in the manufacturer layout render.

Joints in the render are thin grey lines. A joint-line response (luminance and
saturation below their local mean) is matched against an analytic flat-top hex joint mask over a grid
of pitch / offset values. Writes textures/../source_data/render_lattice.json.
"""

import json

import numpy as np
from PIL import Image
from scipy import ndimage

from common import RENDER_PATH, hexnorm, out_path

img = np.asarray(Image.open(RENDER_PATH).convert("RGB")).astype(np.float64) / 255.0
L = img.mean(axis=2)
Hs, Ws = L.shape
# joints are thin GREY lines (darker and less saturated than the cream face)
sat = img.max(axis=2) - img.min(axis=2)
resp = (ndimage.gaussian_filter(L, 4.0) - L) + (ndimage.gaussian_filter(sat, 4.0) - sat)
resp = np.clip(resp, 0, None)

# horizontal joints: row profile has peaks every F/2 (both column parities)
prof = resp.mean(axis=1)
prof = prof - ndimage.gaussian_filter1d(prof, 40)
spec = np.abs(np.fft.rfft(prof * np.hanning(len(prof))))
freqs = np.fft.rfftfreq(len(prof))
band = (freqs > 1 / 250) & (freqs < 1 / 120)   # fundamental; harmonics sit at F/4, F/6 ...
f0 = freqs[band][np.argmax(spec[band])]
print("row-profile period (F/2) ~", 1 / f0)

from scipy.signal import fftconvolve

F_est = 2.0 / f0
print("F estimate", F_est, flush=True)


def joint_template(F, h, w, width=1.5):
    """Joint-centreline mask of a hex lattice with a centre at (0,0), size h x w."""
    colp = F * np.sqrt(3) / 2.0
    Y, X = np.mgrid[0:h, 0:w].astype(np.float64)
    best = np.full(X.shape, 1e9)
    for par in (0, 1):
        cx0, cy0 = par * colp, par * F / 2.0
        c = np.round((X - cx0) / (2 * colp))
        r = np.round((Y - cy0) / F)
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                best = np.minimum(best, hexnorm(X - (cx0 + (c + dc) * 2 * colp), Y - (cy0 + (r + dr) * F)))
    m = (np.abs(best - F / 2.0) < width).astype(np.float64)
    return m - m.mean()


def search(F):
    colp = F * np.sqrt(3) / 2.0
    ph, pw = int(np.ceil(F)) + 2, int(np.ceil(2 * colp)) + 2
    T = joint_template(F, Hs + ph, Ws + pw)
    # correlation: out[dy,dx] = sum resp * T[dy:dy+Hs, dx:dx+Ws]
    out = fftconvolve(T, resp[::-1, ::-1], mode="valid")
    k = np.unravel_index(np.argmax(out), out.shape)
    # template shifted by (dy,dx) means lattice centre at (-dx,-dy) mod period
    return out[k] / resp.size, (-k[1]) % (2 * colp), (-k[0]) % F


best = (-1e9, None, None, None)
for F in np.arange(F_est - 3, F_est + 3.001, 0.25):
    s, x0, y0 = search(F)
    if s > best[0]:
        best = (s, F, x0, y0)
print("coarse", best, flush=True)
F0 = best[1]
for F in np.arange(F0 - 0.25, F0 + 0.2501, 0.05):
    s, x0, y0 = search(F)
    if s > best[0]:
        best = (s, F, x0, y0)
print("fine", best, flush=True)

s, F, x0, y0 = best
data = {
    "render_size": [Ws, Hs],
    "module_across_flats_px": F,
    "px_per_in": F / 10.125,
    "centre0_xy": [x0, y0],
    "column_pitch_px": F * np.sqrt(3) / 2,
    "score": s,
    "note": "module = face 10 in + joint 1/8 in across the flats (assumed geometry)",
}
json.dump(data, open(out_path("source", "data", "render_lattice.json"), "w"), indent=2)
print(json.dumps(data, indent=2))
