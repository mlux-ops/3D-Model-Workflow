"""Measure the non-groove roughness of the render's Chiseled faces.

For each fully visible Chiseled face: 2D spectrum of the band-passed luminance, notch out the
groove fundamental and its 2nd/3rd harmonics (narrow Gaussian notches at +-k, +-2k, +-3k), and
compare the residual's std with the same band on Matte faces. Also measures along-groove
amplitude modulation of the fundamental (complex demodulation) and its correlation length.
Writes _work/chiseled_rough.json (used by build_maps.py).
"""
import os
import json
import numpy as np
from scipy import ndimage as ndi
from guard import WORK_DIR, write_text

P = np.load(os.path.join(WORK_DIR, "pools.npz"))
INFO = json.load(open(os.path.join(WORK_DIR, "pools.json")))
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
cells = {"%d,%d" % (c["j"], c["k"]): c for c in L["cells"]}
Yres = (P["resid"] @ np.array([0.2126, 0.7152, 0.0722], np.float32)).astype(np.float64)
band = ndi.gaussian_filter(Yres, 0.7) - ndi.gaussian_filter(Yres, 10.0)
r = 100
win = np.outer(np.hanning(2 * r), np.hanning(2 * r))
fy, fx = np.meshgrid(np.fft.fftfreq(2 * r), np.fft.fftfreq(2 * r), indexing="ij")
out = {"chiseled": {}, "matte": {}}
for k, m in INFO["chiseled_measure"].items():
    c = cells[k]
    cx, cy = int(round(c["cx"])), int(round(c["cy"]))
    p = band[cy - r:cy + r, cx - r:cx + r]
    nrm = np.radians(m["groove_deg_img"] - 90.0)
    k0 = np.array([np.cos(nrm), np.sin(nrm)]) / m["period_px"]
    F = np.fft.fft2(p - p.mean())
    notch = np.ones_like(fx)
    for h in (1, 2, 3):
        for s in (1, -1):
            d2 = (fx - s * h * k0[0]) ** 2 + (fy - s * h * k0[1]) ** 2
            notch *= 1 - np.exp(-d2 / (2 * (0.012) ** 2))
    resid = np.real(np.fft.ifft2(F * notch))
    inner = resid[20:-20, 20:-20]
    # along-groove amplitude modulation of the fundamental
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]
    u = (xx - r) * k0[0] + (yy - r) * k0[1]
    z = p * np.exp(-2j * np.pi * u)
    zs = ndi.gaussian_filter(z.real, 3.0) + 1j * ndi.gaussian_filter(z.imag, 3.0)
    amp = np.abs(zs)[20:-20, 20:-20]
    # correlation length of the amplitude along the groove direction
    a = amp - amp.mean()
    gdir = np.array([-k0[1], k0[0]]) / np.hypot(*k0)
    ac = []
    for t in range(0, 40, 2):
        sh = ndi.shift(a, (t * gdir[1], t * gdir[0]), order=1, mode="nearest")
        ac.append(float((a * sh).mean() / (a * a).mean()))
    corr_len = next((t * 2 for t, v in enumerate(ac) if v < 0.5), 40)
    out["chiseled"][k] = {"residual_std": float(inner.std()), "band_std": float(p[20:-20, 20:-20].std()),
                          "amp_cv": float(amp.std() / amp.mean()), "amp_corr_len_px_half": corr_len}
    print("%s residual std %.2f (band %.2f), amp cv %.2f, amp corr length (to 0.5) %d render px" % (
        k, inner.std(), p[20:-20, 20:-20].std(), amp.std() / amp.mean(), corr_len))
for k, t in INFO["types"].items():
    if t != "matte" or k not in cells:
        continue
    c = cells[k]
    cx, cy = int(round(c["cx"])), int(round(c["cy"]))
    if cx - r < 0 or cy - r < 0 or cx + r > band.shape[1] or cy + r > band.shape[0]:
        continue
    out["matte"][k] = float(band[cy - r + 20:cy + r - 20, cx - r + 20:cx + r - 20].std())
ch = np.median([v["residual_std"] for v in out["chiseled"].values()])
mt = np.median(list(out["matte"].values()))
out["summary"] = {"chiseled_residual_std_median": float(ch), "matte_band_std_median": float(mt),
                  "ratio": float(ch / mt),
                  "amp_cv_median": float(np.median([v["amp_cv"] for v in out["chiseled"].values()])),
                  "amp_corr_len_median_render_px": float(np.median([v["amp_corr_len_px_half"] for v in out["chiseled"].values()]))}
print("summary", out["summary"])
write_text(os.path.join(WORK_DIR, "chiseled_rough.json"), json.dumps(out, indent=1))
