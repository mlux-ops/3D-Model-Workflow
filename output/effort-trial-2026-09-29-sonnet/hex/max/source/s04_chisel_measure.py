"""Step 04: measure the Chiseled groove pattern in the render (pitch, orientation,
profile) face by face, by FFT peak and by fold-averaged cross-section."""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])
PX_PER_IN = 31.0916
MM_PER_PX = 25.4 / PX_PER_IN

CHISELED = {"vert": [(-1, 3), (2, 1), (2, 4)],
            "diagS": [(0, 1), (0, 5), (3, 3), (5, 2)],      # "\" lines
            "diagF": [(1, 2), (4, 5)]}                      # "/" lines


def crop_padded(a, x0, y0, w, h):
    """Crop with edge replication where the window leaves the image (the hexagon mask
    keeps padded pixels out of every measurement)."""
    H, W = a.shape[:2]
    xs = np.clip(np.arange(x0, x0 + w), 0, W - 1)
    ys = np.clip(np.arange(y0, y0 + h), 0, H - 1)
    return a[np.ix_(ys, xs)].copy()


def face_window(lum, grid, i, j, inset=14, half=176):
    F = grid["F_px"]
    cp = grid["col_pitch_px"]
    cx = grid["x0"] + i * cp
    cy = grid["y0"] + ((F / 2.0) if (i % 2) else 0.0) + j * F
    x0, y0 = int(round(cx)) - half, int(round(cy)) - half
    sub = crop_padded(lum, x0, y0, 2 * half, 2 * half)
    ys, xs = np.mgrid[0:2 * half, 0:2 * half]
    d = hex_dist_inside(xs + x0 - cx, ys + y0 - cy, F)
    m = np.clip((d - inset) / 6.0, 0.0, 1.0)          # soft edge
    return sub, m, (cx - x0, cy - y0)


def fft_peak(sub, m, fmin=1 / 24.0, fmax=1 / 2.6, pad=1024):
    hp = sub - ndi.gaussian_filter(sub, 6.0)
    w = hp * m
    w = w - (w.sum() / m.sum()) * m
    F2 = np.fft.fftshift(np.fft.fft2(w, s=(pad, pad)))
    P = np.abs(F2) ** 2
    fy = np.fft.fftshift(np.fft.fftfreq(pad))
    fx = np.fft.fftshift(np.fft.fftfreq(pad))
    FX, FY = np.meshgrid(fx, fy)
    FR = np.hypot(FX, FY)
    band = (FR > fmin) & (FR < fmax)
    Pb = np.where(band, P, 0.0)
    k = np.unravel_index(np.argmax(Pb), Pb.shape)
    f = (FX[k], FY[k])
    # centroid refinement around the peak
    r = 6
    sl = (slice(k[0] - r, k[0] + r + 1), slice(k[1] - r, k[1] + r + 1))
    ww = Pb[sl]
    fxc = (FX[sl] * ww).sum() / ww.sum()
    fyc = (FY[sl] * ww).sum() / ww.sum()
    # peak width: radial second moment of the peak neighbourhood
    r2 = 14
    sl2 = (slice(k[0] - r2, k[0] + r2 + 1), slice(k[1] - r2, k[1] + r2 + 1))
    ww2 = P[sl2] * band[sl2]
    dfx = FX[sl2] - fxc
    dfy = FY[sl2] - fyc
    spread = np.sqrt((ww2 * (dfx ** 2 + dfy ** 2)).sum() / ww2.sum())
    return fxc, fyc, spread, Pb[k]


def profile_fold(sub, m, fxc, fyc, nb=32):
    """Average cross-section, folded at the measured pitch. Coordinate u runs along the
    frequency vector (across the grooves)."""
    f = np.hypot(fxc, fyc)
    pitch = 1.0 / f
    ux, uy = fxc / f, fyc / f
    ys, xs = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    u = xs * ux + ys * uy
    ph = np.mod(u / pitch, 1.0)
    hp = sub - ndi.gaussian_filter(sub, 8.0)
    sel = m > 0.999
    idx = np.minimum((ph[sel] * nb).astype(int), nb - 1)
    prof = np.bincount(idx, weights=hp[sel], minlength=nb) / np.maximum(np.bincount(idx, minlength=nb), 1)
    return pitch, prof


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    res = {}
    for kind, faces in CHISELED.items():
        for (i, j) in faces:
            sub, m, c = face_window(lum, grid, i, j)
            fxc, fyc, spread, pk = fft_peak(sub, m)
            f = np.hypot(fxc, fyc)
            pitch_px = 1.0 / f
            line_dir = (np.degrees(np.arctan2(fyc, fxc)) + 90.0) % 180.0   # image coords, y down
            pitch, prof = profile_fold(sub, m, fxc, fyc)
            res["%s_%d_%d" % (kind, i, j)] = {
                "kind": kind, "i": i, "j": j, "pitch_px": pitch_px,
                "pitch_mm": pitch_px * MM_PER_PX, "line_dir_deg_imgcoords": line_dir,
                "peak_spread_cyc_px": spread, "profile_p2p": float(prof.max() - prof.min()),
                "profile": [float(x) for x in prof]}
            print("%-5s (%2d,%d) pitch %.3f px = %.2f mm  lines at %.1f deg (y-down)  spread %.4f  prof p2p %.2f"
                  % (kind, i, j, pitch_px, pitch_px * MM_PER_PX, line_dir, spread, prof.max() - prof.min()))
    save_text(json.dumps(res, indent=1), "work", "chisel_measure.json")


if __name__ == "__main__":
    main()
