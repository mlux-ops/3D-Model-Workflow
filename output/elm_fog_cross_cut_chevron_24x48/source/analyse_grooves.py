"""Per-band groove measurement for the ELM Fog Cross-Cut Chevron Deco swatch.

For each horizontal band (spines found by analyse_chevron.py) this measures the
groove line angle, pitch, phase and the mean cross-groove luminance profile, by
projecting the high-passed luminance onto the groove normal and folding it at
the refined pitch. Read-only; writes _analysis/grooves.json and thumbnails.
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.dirname(HERE)
SRC = os.path.join(PROD, "references", "candidates",
                   "6508c8490fee3dfe7508423d_ElmStone_Fog_Cross-Cut_Chevron-Deco_48x110_01.jpg")
OUT = os.path.join(HERE, "_analysis")
SPINES = [0, 309, 645, 974, 1264, 1625, 1951]   # measured, rows (0 and H are slab edges)
MARGIN = 24


def lum(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def fold_contrast(u, v, pitch, nb=64):
    ph = np.mod(u / pitch, 1.0)
    idx = np.minimum((ph * nb).astype(int), nb - 1)
    s = np.bincount(idx, v, nb)
    c = np.bincount(idx, None, nb)
    prof = s / np.maximum(c, 1)
    return prof.std(), prof


def main():
    rgb = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64)
    H, W = rgb.shape[:2]
    L = lum(rgb)
    hp = L - ndi.gaussian_filter(L, 10)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    bands = []
    for k in range(len(SPINES) - 1):
        y0, y1 = SPINES[k] + MARGIN, SPINES[k + 1] - MARGIN
        sub = hp[y0:y1]
        # coarse angle from the band spectrum
        win = np.outer(np.hanning(sub.shape[0]), np.hanning(W))
        F = np.abs(np.fft.fft2(sub * win))
        fy = np.fft.fftfreq(sub.shape[0])
        fx = np.fft.fftfreq(W)
        FX, FY = np.meshgrid(fx, fy)
        R = np.hypot(FX, FY)
        F[(R < 1 / 12.0) | (R > 1 / 5.0)] = 0
        iy, ix = np.unravel_index(np.argmax(F), F.shape)
        f = np.array([FX[iy, ix], FY[iy, ix]])
        if f[1] < 0:
            f = -f
        normal = np.arctan2(f[1], f[0])
        pitch0 = 1.0 / np.hypot(*f)
        # refine angle + pitch by maximising folded-profile contrast
        X, Y = xx[y0:y1].ravel(), yy[y0:y1].ravel()
        V = sub.ravel()
        sel = np.random.default_rng(1).choice(V.size, min(V.size, 400000), replace=False)
        best = (-1, None, None)
        for da in np.linspace(-1.5, 1.5, 31):
            a = normal + np.radians(da)
            u = X[sel] * np.cos(a) + Y[sel] * np.sin(a)
            for p in np.linspace(pitch0 * 0.96, pitch0 * 1.04, 41):
                c, _ = fold_contrast(u, V[sel], p)
                if c > best[0]:
                    best = (c, a, p)
        c, a, p = best
        u = X * np.cos(a) + Y * np.sin(a)
        _, prof = fold_contrast(u, V, p, nb=96)
        # phase: u of the darkest profile bin, measured at the band's top spine
        dark = int(np.argmin(np.convolve(np.r_[prof[-3:], prof, prof[:3]], np.ones(7) / 7, "valid")))
        line_deg = (np.degrees(a) + 90) % 180
        # three-groove super-period check: fold at 3p and look for unequal minima
        _, prof3 = fold_contrast(u, V, 3 * p, nb=288)
        bands.append({
            "band": k, "rows": [SPINES[k], SPINES[k + 1]],
            "height_px": SPINES[k + 1] - SPINES[k],
            "line_deg_image": float(line_deg),
            "angle_from_horizontal_deg": float(min(line_deg, 180 - line_deg)),
            "pitch_px": float(p), "fold_contrast": float(c),
            "dark_phase_bin_of_96": dark,
            "profile96": [round(float(v), 3) for v in prof],
            "profile288_over_3_pitches": [round(float(v), 3) for v in prof3],
        })
        print(k, SPINES[k], SPINES[k + 1], "line %.2f deg  pitch %.3f px  contrast %.3f" % (line_deg, p, c))
    with open(os.path.join(OUT, "grooves.json"), "w") as fh:
        json.dump({"source": os.path.relpath(SRC, PROD), "size_px": [W, H], "bands": bands}, fh, indent=1)


if __name__ == "__main__":
    main()
