"""Measure the chevron groove geometry of the ELM Fog Cross-Cut Chevron Deco swatch.

Read-only analysis. Writes a JSON report and diagnostic thumbnails into
../source/_analysis/. Nothing here writes a texture.

Source: ELM's flat straight-on swatch of the 48 x 110 in slab
(4460 x 1951 px). Pixel scale is taken from the slab's stated 110 in width.
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
os.makedirs(OUT, exist_ok=True)

SLAB_W_IN, SLAB_H_IN = 110.0, 48.0


def lum(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def thumb(a, name, lo=None, hi=None, maxw=800):
    a = np.asarray(a, dtype=np.float64)
    lo = np.percentile(a, 1) if lo is None else lo
    hi = np.percentile(a, 99) if hi is None else hi
    g = np.clip((a - lo) / max(hi - lo, 1e-9), 0, 1)
    im = Image.fromarray((g * 255).astype(np.uint8))
    if im.size[0] > maxw:
        im = im.resize((maxw, int(im.size[1] * maxw / im.size[0])), Image.LANCZOS)
    im.save(os.path.join(OUT, name), quality=90)


def main():
    rgb = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64)
    H, W = rgb.shape[:2]
    ppi_x, ppi_y = W / SLAB_W_IN, H / SLAB_H_IN
    L = lum(rgb)
    hp = L - ndi.gaussian_filter(L, 10)

    # global spectrum of the high-passed luminance
    win = np.outer(np.hanning(H), np.hanning(W))
    F = np.fft.fftshift(np.abs(np.fft.fft2(hp * win)))
    fy = np.fft.fftshift(np.fft.fftfreq(H))
    fx = np.fft.fftshift(np.fft.fftfreq(W))
    FX, FY = np.meshgrid(fx, fy)
    R = np.hypot(FX, FY)
    Fm = F.copy()
    Fm[R < 1 / 60.0] = 0  # ignore anything coarser than 60 px
    Fm[FY < 0] = 0        # half plane (spectrum is symmetric)
    peaks = []
    work = ndi.gaussian_filter(Fm, 1.0)
    for _ in range(8):
        iy, ix = np.unravel_index(np.argmax(work), work.shape)
        f = np.array([FX[iy, ix], FY[iy, ix]])
        pitch_px = 1.0 / np.hypot(*f)
        # stripe normal angle and stripe (line) direction angle, image coords (y down)
        normal_deg = np.degrees(np.arctan2(f[1], f[0]))
        peaks.append({
            "fx": float(f[0]), "fy": float(f[1]), "mag": float(work[iy, ix]),
            "pitch_px": float(pitch_px),
            "pitch_in": float(pitch_px / ((ppi_x + ppi_y) / 2)),
            "normal_deg": float(normal_deg),
            "line_deg": float((normal_deg + 90) % 180),
        })
        work[max(0, iy - 12):iy + 13, max(0, ix - 12):ix + 13] = 0

    # local orientation (structure tensor) of the groove field
    gy, gx = np.gradient(ndi.gaussian_filter(hp, 1.0))
    s = 8.0
    jxx = ndi.gaussian_filter(gx * gx, s)
    jyy = ndi.gaussian_filter(gy * gy, s)
    jxy = ndi.gaussian_filter(gx * gy, s)
    theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy)  # gradient direction
    line = (np.degrees(theta) + 90) % 180         # groove line direction
    coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-9)
    cls = np.where(line < 90, 1.0, -1.0)          # +1: line in (0,90), -1: (90,180)
    np.save(os.path.join(OUT, "line_angle_deg.npy"), line.astype(np.float32))
    np.save(os.path.join(OUT, "coherence.npy"), coh.astype(np.float32))
    thumb(hp, "hp_luminance.jpg")
    thumb(cls * np.clip(coh * 3, 0, 1), "orientation_class.jpg", -1, 1)
    thumb(coh, "coherence.jpg", 0, 0.6)

    # band structure: fraction of '+' class per row and per column (coherent px only)
    m = coh > 0.15
    rowfrac = (np.where(m, cls > 0, 0).sum(1) / np.maximum(m.sum(1), 1))
    colfrac = (np.where(m, cls > 0, 0).sum(0) / np.maximum(m.sum(0), 1))

    rep = {
        "source": os.path.relpath(SRC, PROD),
        "size_px": [W, H],
        "px_per_in": [ppi_x, ppi_y],
        "spectrum_peaks": peaks,
        "line_angle_hist_deg": np.histogram(line[m], bins=36, range=(0, 180))[0].tolist(),
        "coherent_fraction": float(m.mean()),
        "rowfrac_std": float(rowfrac.std()), "colfrac_std": float(colfrac.std()),
    }
    np.save(os.path.join(OUT, "rowfrac.npy"), rowfrac)
    np.save(os.path.join(OUT, "colfrac.npy"), colfrac)
    with open(os.path.join(OUT, "analysis.json"), "w") as fh:
        json.dump(rep, fh, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "line_angle_hist_deg"}, indent=1))
    print("hist", rep["line_angle_hist_deg"])


if __name__ == "__main__":
    main()
