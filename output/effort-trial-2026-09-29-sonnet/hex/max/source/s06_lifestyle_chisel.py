"""Step 06: groove pitch, orientation and cross-section profile of the Chiseled faces in the
lifestyle image (native resolution), as an independent check of the render measurement.

The lifestyle view is oblique, so only ratios and the profile *shape* are used from it, never
absolute pixel pitch as a physical scale (the horizontal and vertical scales differ)."""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import LIFESTYLE_PATH, save_text  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])

BOXES = {
    "vert_a": (735, 250, 150, 300),
    "vert_b": (735, 330, 150, 220),
    "diag_a": (700, 760, 170, 200),
    "diag_b": (700, 860, 170, 200),
}


def peak(sub, fmin=1 / 24.0, fmax=1 / 3.0, pad=1024):
    hp = sub - ndi.gaussian_filter(sub, 6.0)
    win = np.outer(np.hanning(sub.shape[0]), np.hanning(sub.shape[1]))
    w = hp * win
    F2 = np.fft.fftshift(np.fft.fft2(w, s=(pad, pad)))
    P = np.abs(F2) ** 2
    f = np.fft.fftshift(np.fft.fftfreq(pad))
    FX, FY = np.meshgrid(f, f)
    FR = np.hypot(FX, FY)
    Pb = np.where((FR > fmin) & (FR < fmax), P, 0.0)
    k = np.unravel_index(np.argmax(Pb), Pb.shape)
    r = 5
    sl = (slice(k[0] - r, k[0] + r + 1), slice(k[1] - r, k[1] + r + 1))
    ww = Pb[sl]
    return (FX[sl] * ww).sum() / ww.sum(), (FY[sl] * ww).sum() / ww.sum(), Pb[k]


def fold(sub, fx, fy, nb=48):
    f = np.hypot(fx, fy)
    sg = 1.0 if fx > 0 else -1.0
    ux, uy = sg * fx / f, sg * fy / f
    ys, xs = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    u = xs * ux + ys * uy
    ph = np.mod(u * f, 1.0)
    hp = sub - ndi.gaussian_filter(sub, 8.0)
    idx = np.minimum((ph * nb).astype(int), nb - 1).ravel()
    cnt = np.maximum(np.bincount(idx, minlength=nb), 1)
    prof = np.bincount(idx, weights=hp.ravel(), minlength=nb) / cnt
    return prof


def main():
    rgb = load_srgb(LIFESTYLE_PATH)
    lum = rgb @ LUMW
    out = {}
    for name, (x0, y0, w, h) in BOXES.items():
        sub = lum[y0:y0 + h, x0:x0 + w]
        fx, fy, pk = peak(sub)
        f = np.hypot(fx, fy)
        line_dir = (np.degrees(np.arctan2(fy, fx)) + 90.0) % 180.0
        prof = fold(sub, fx, fy)
        nb = len(prof)
        Fh = np.fft.rfft(prof) / nb * 2.0
        amps = [abs(Fh[n]) for n in range(1, 5)]
        phs = [np.degrees(np.angle(Fh[n])) for n in range(1, 5)]
        rel2 = (phs[1] - 2 * phs[0]) % 360
        # profile skew: fraction of the period spent below the mean
        below = float((prof < prof.mean()).mean())
        print("%-7s pitch %.3f px  lines at %.1f deg  A1 %.2f A2 %.2f A3 %.2f A4 %.2f  "
              "A2/A1 %.2f  rel2 %.0f  p2p %.1f  below-mean %.2f"
              % (name, 1 / f, line_dir, amps[0], amps[1], amps[2], amps[3], amps[1] / amps[0],
                 rel2, prof.max() - prof.min(), below))
        out[name] = {"pitch_px": 1 / f, "line_deg": line_dir, "amps": amps, "phs": phs,
                     "profile": [float(x) for x in prof]}
    save_text(json.dumps(out, indent=1), "work", "lifestyle_chisel.json")


if __name__ == "__main__":
    main()
