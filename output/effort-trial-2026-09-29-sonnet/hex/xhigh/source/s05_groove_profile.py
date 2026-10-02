"""Measure chiseled groove profile, wobble and stroke-continuity statistics on the vertical-groove faces (i3 j0, i3 j3)."""
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
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
gm = json.load(open(rg.WORK + "groove_measure.json"))
per = float(np.mean([g["period_px"] for g in gm if g["period_px"] > 5]))
f0 = 1 / per
print("mean period px", per, "in", per / rg.PX_PER_IN)
res = {"period_px": per, "period_in": per / rg.PX_PER_IN}
prof_all = []
amp_corr = []
wob = []
amps = []
for (i, j) in ((3, 0), (3, 3)):
    cx = rg.OX + i * 0.75 * rg.P
    cy = rg.OY + j * rg.F + (i % 2) * rg.F / 2
    y0, y1, x0, x1 = int(cy - 190), int(cy + 191), int(cx - 210), int(cx + 211)
    d = rg.hex_dist(xx[y0:y1, x0:x1], yy[y0:y1, x0:x1], cx, cy)
    sub = L[y0:y1, x0:x1]
    hp = sub - ndi.gaussian_filter(sub, 6.0)
    m = d < 0.80
    # quadrature demodulation along x
    X = xx[y0:y1, x0:x1]
    z = hp * np.exp(-2j * np.pi * f0 * X)
    zr = ndi.gaussian_filter(z.real, [0.0001 + 2.0, per * 0.9]) if False else ndi.gaussian_filter(z.real, 1.2)
    zi = ndi.gaussian_filter(z.imag, 1.2)
    # low-pass along x only at ~ one period, keep y detail
    zr = ndi.gaussian_filter1d(z.real, per * 0.8, axis=1)
    zi = ndi.gaussian_filter1d(z.imag, per * 0.8, axis=1)
    zc = zr + 1j * zi
    a = np.abs(zc) * 2
    ph = np.angle(zc)
    amps.append(a[m].mean())
    # phase-fold profile using the demodulated (locally unwrapped) phase: use global f0 grid, then align phase per pixel
    # cross profile: fold hp by local phase
    phase_of_pixel = (2 * np.pi * f0 * X + ph)
    bins = 16
    idx = np.floor(((phase_of_pixel % (2 * np.pi)) / (2 * np.pi)) * bins).astype(int)
    prof = np.array([hp[m & (idx == b)].mean() for b in range(bins)])
    prof_all.append(prof)
    # stroke continuity: autocorrelation of amplitude along y (groove direction) inside the mask
    ac = []
    ax = a - a[m].mean()
    for lag in range(0, 120, 4):
        A = ax[: ax.shape[0] - lag] * ax[lag:]
        M = m[: m.shape[0] - lag] & m[lag:]
        ac.append((A[M].mean()) / (ax[m] ** 2).mean())
    amp_corr.append(ac)
    # wobble: structure function of the demodulated phase (in fractions of period) along y
    phs = np.unwrap(ph, axis=0)
    sf = []
    for lag in (2, 5, 10, 20, 40, 80):
        dd = (phs[lag:] - phs[:-lag])
        M = m[lag:] & m[:-lag]
        sf.append(float(np.std((dd[M] / (2 * np.pi)))))
    wob.append(sf)
    print("face i%d j%d amp %.2f levels; amp-CV %.2f; phase-wobble std (periods) at lags 2,5,10,20,40,80 px: %s" % (i, j, a[m].mean(), a[m].std() / a[m].mean(), np.round(sf, 3)))
prof = np.mean(prof_all, axis=0)
prof = prof - prof.mean()
print("fold profile (16 bins over one period, levels):", np.round(prof, 2))
ac = np.mean(amp_corr, axis=0)
print("amplitude autocorr along groove at lags 0,4,8..:", np.round(ac[:16], 2))
# groove dash length: lag where amplitude autocorr falls to 0.5 / 1/e
lags = np.arange(0, 120, 4)
half = lags[np.argmax(ac < 0.5)] if (ac < 0.5).any() else None
print("amplitude corr length (0.5 crossing, px):", half, " = in:", None if half is None else half / rg.PX_PER_IN)
res.update(profile16=[float(v) for v in prof], amp_mean=float(np.mean(amps)), amp_corr_lags=[int(v) for v in lags], amp_corr=[float(v) for v in ac], wobble_lags=[2, 5, 10, 20, 40, 80], wobble_std_periods=[float(v) for v in np.mean(wob, axis=0)])
json.dump(res, open(guard.safe(rg.WORK + "groove_profile.json"), "w"), indent=1)
