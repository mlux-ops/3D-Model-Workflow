"""Step 05: Raw-face analysis. Angular power spectrum vs the matte noise floor, and
pairwise cross-correlation of the eight complete Raw faces (duplicate check)."""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402
from s04_chisel_measure import face_window  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])
RAW = [(-1, 0), (0, 3), (1, 1), (1, 4), (2, 3), (4, 1), (4, 2), (5, 4)]
MATTE = [(-1, 1), (-1, 2), (-1, 4), (-1, 5), (0, 2), (0, 4), (1, 0), (1, 3), (1, 5), (2, 2), (2, 5),
         (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (4, 3), (4, 4), (5, 0), (5, 1), (5, 3), (5, 5)]
N = 512


def spectrum(lum, grid, faces):
    P = np.zeros((N, N))
    cnt = 0
    for (i, j) in faces:
        sub, m, c = face_window(lum, grid, i, j)
        hp = sub - ndi.gaussian_filter(sub, 12.0)
        w = hp * m
        w = w - (w.sum() / m.sum()) * m
        F2 = np.fft.fftshift(np.fft.fft2(w, s=(N, N)))
        P += (np.abs(F2) ** 2) / (m ** 2).sum()
        cnt += 1
    return P / cnt


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    Pr = spectrum(lum, grid, RAW)
    Pm = spectrum(lum, grid, MATTE)
    f = np.fft.fftshift(np.fft.fftfreq(N))
    FX, FY = np.meshgrid(f, f)
    FR = np.hypot(FX, FY)
    TH = np.degrees(np.arctan2(FY, FX)) % 180.0
    th_l = (-31.5) % 180.0
    dth = np.abs(((TH - th_l) + 90.0) % 180.0 - 90.0)      # angle from light axis, 0..90
    edges = [1 / 64., 1 / 32., 1 / 20., 1 / 14., 1 / 10., 1 / 7., 1 / 5., 1 / 3.5, 1 / 2.4]
    print("radial band (cyc/px)  wavelength px | RAW par  RAW perp | MATTE par MATTE perp | SNR(par) SNR(perp)")
    for a, b in zip(edges[:-1], edges[1:]):
        band = (FR >= a) & (FR < b)
        par = band & (dth < 25)
        perp = band & (dth > 65)
        rp, rq = Pr[par].mean(), Pr[perp].mean()
        mp, mq = Pm[par].mean(), Pm[perp].mean()
        print("%.4f-%.4f   %5.1f-%5.1f | %9.1f %9.1f | %9.1f %9.1f | %6.1f %6.1f"
              % (a, b, 1 / b, 1 / a, rp, rq, mp, mq, rp / mp, rq / mq))
    # ---- pairwise cross-correlation of raw faces (luminance, unrotated) ----
    subs = []
    for (i, j) in RAW:
        sub, m, c = face_window(lum, grid, i, j)
        hp = (sub - ndi.gaussian_filter(sub, 12.0)) * m
        subs.append((hp, m))
    print("pairwise max normalised cross-correlation (all shifts, unrotated):")
    K = len(RAW)
    best = np.zeros((K, K))
    for a in range(K):
        for b in range(a + 1, K):
            A = subs[a][0]
            B = subs[b][0]
            Fa = np.fft.rfft2(A, s=(2 * A.shape[0], 2 * A.shape[1]))
            Fb = np.fft.rfft2(B, s=(2 * A.shape[0], 2 * A.shape[1]))
            cc = np.fft.irfft2(Fa * np.conj(Fb))
            nrm = np.sqrt((A ** 2).sum() * (B ** 2).sum())
            best[a, b] = cc.max() / nrm
    np.set_printoptions(precision=2, suppress=True, linewidth=200)
    print(best)


if __name__ == "__main__":
    main()
