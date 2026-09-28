"""Step 5: precise Chiseled groove geometry from the layout render.

For every chiseled face: search the groove-normal angle phi (image axes, y down) and the
period so that the luma projected onto the normal is sharpest; then fold the projection
at the period to get the mean cross-profile (luma vs position across one groove period).

Groove direction is reported y-up, counter-clockwise from +x, in [0, 180).
Writes _work/grooves.json and a profile plot _work/groove_profiles.png.
"""

import json
import sys

import numpy as np
from PIL import Image, ImageDraw

from common import load_lattice, render_rgb, luma, out_path, S3, hex_edge_distance_local
from guard import save_image

CHISELED = None  # filled from cells_raw.json using coherence


def face_pixels(lat, c, L, clean=6.0):
    rp = lat["rp"]
    R = rp / S3
    Hr, Wr = L.shape
    X0 = max(0, int(c["cx"] - R - 2)); X1 = min(Wr, int(c["cx"] + R + 2))
    Y0 = max(0, int(c["cy"] - rp / 2 - 2)); Y1 = min(Hr, int(c["cy"] + rp / 2 + 2))
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float64)
    dx = xs + 0.5 - c["cx"]; dy = ys + 0.5 - c["cy"]
    m = hex_edge_distance_local(dx, dy, rp * 0.5) >= clean
    return dx[m], dy[m], L[Y0:Y1, X0:X1][m]


def projection(dx, dy, v, phi_deg, binw=0.2):
    t = np.deg2rad(phi_deg)
    u = dx * np.cos(t) + dy * np.sin(t)
    u0 = u.min()
    idx = np.floor((u - u0) / binw).astype(np.int64)
    n = idx.max() + 1
    s = np.bincount(idx, weights=v, minlength=n)
    c = np.bincount(idx, minlength=n)
    ok = c > 20
    prof = np.where(ok, s / np.maximum(c, 1), np.nan)
    # fill gaps, detrend with a wide moving average
    x = np.arange(n)
    prof = np.interp(x, x[ok], prof[ok])
    k = int(round(30.0 / binw))
    ker = np.ones(k) / k
    trend = np.convolve(np.pad(prof, k, mode="edge"), ker, mode="same")[k:-k]
    return prof - trend, u0


def peak(prof, binw, pmin=5.5, pmax=7.0):
    n = len(prof)
    nf = 1 << int(np.ceil(np.log2(n * 8)))
    F = np.abs(np.fft.rfft(prof * np.hanning(n), nf)) ** 2
    f = np.fft.rfftfreq(nf, d=binw)
    band = (f > 1 / pmax) & (f < 1 / pmin)
    k = np.argmax(np.where(band, F, 0))
    # parabolic interpolation
    if 0 < k < len(F) - 1:
        a, b, c = np.log(F[k - 1] + 1e-12), np.log(F[k] + 1e-12), np.log(F[k + 1] + 1e-12)
        d = 0.5 * (a - c) / (a - 2 * b + c)
    else:
        d = 0.0
    fk = f[k] + d * (f[1] - f[0])
    return 1.0 / fk, float(F[k])


def main():
    lat = load_lattice()
    cells = json.load(open(out_path("_work", "cells_raw.json")))
    rgb = render_rgb()
    L = luma(rgb)
    res = []
    for c in cells:
        if c["coher"] < 0.6 or c["frac"] < 0.3:
            continue
        dx, dy, v = face_pixels(lat, c, L)
        # groove direction (y-up) -> normal angle in image axes (y down)
        line_up = c["fft_line_deg"]
        normal_up = (line_up + 90.0) % 180.0
        phi0 = (-normal_up) % 180.0
        best = None
        for phi in np.arange(phi0 - 4.0, phi0 + 4.001, 0.1):
            prof, _ = projection(dx, dy, v, phi)
            per, pw = peak(prof, 0.2)
            if best is None or pw > best[2]:
                best = (phi, per, pw)
        for phi in np.arange(best[0] - 0.15, best[0] + 0.151, 0.01):
            prof, _ = projection(dx, dy, v, phi)
            per, pw = peak(prof, 0.2)
            if pw > best[2]:
                best = (phi, per, pw)
        phi, per, pw = best
        # fold at the period into 24 bins; phase-align so the darkest bin is at 0
        t = np.deg2rad(phi)
        u = dx * np.cos(t) + dy * np.sin(t)
        ph = np.mod(u, per) / per
        nb = 24
        b = np.minimum((ph * nb).astype(int), nb - 1)
        fold = np.bincount(b, weights=v, minlength=nb) / np.bincount(b, minlength=nb)
        fold = fold - fold.mean()
        sh = int(np.argmin(fold))
        fold = np.roll(fold, -sh)
        normal_up_deg = (-phi) % 180.0
        groove_up = (normal_up_deg + 90.0) % 180.0
        res.append({"id": c["id"], "i": c["i"], "j": c["j"], "frac": c["frac"],
                    "normal_img_deg": phi, "groove_deg_yup": groove_up,
                    "period_px": per, "fold_profile": fold.tolist(),
                    "fold_pp": float(fold.max() - fold.min())})
        print("id %2d  groove %.2f deg (y-up)  period %.4f px  profile p-p %.2f"
              % (c["id"], groove_up, per, fold.max() - fold.min()))
    pers = np.array([r["period_px"] for r in res])
    print("period mean %.4f  sd %.4f px" % (pers.mean(), pers.std()))
    fams = {}
    for r in res:
        g = r["groove_deg_yup"]
        key = min((90, 150, 30), key=lambda a: min(abs(g - a), 180 - abs(g - a)))
        fams.setdefault(key, []).append(g)
    for k, v in fams.items():
        print("family %3d: n=%d mean %.2f  values %s" % (k, len(v), np.mean(v), np.round(v, 2)))
    json.dump({"faces": res, "period_px_mean": float(pers.mean()),
               "period_px_sd": float(pers.std()),
               "families": {str(k): v for k, v in fams.items()}},
              open(out_path("_work", "grooves.json"), "w"), indent=1)
    # plot folded profiles
    im = Image.new("RGB", (800, 400), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    cols = {90: (200, 0, 0), 150: (0, 120, 0), 30: (0, 0, 200)}
    for r in res:
        g = r["groove_deg_yup"]
        key = min((90, 150, 30), key=lambda a: min(abs(g - a), 180 - abs(g - a)))
        f = np.array(r["fold_profile"])
        f2 = np.concatenate([f, f])
        pts = [(20 + k * 760 / (len(f2) - 1), 200 - 12 * f2[k]) for k in range(len(f2))]
        dr.line(pts, fill=cols[key], width=2)
    dr.line([(20, 200), (780, 200)], fill=(128, 128, 128))
    save_image(im, "_work", "groove_profiles.png")


if __name__ == "__main__":
    sys.exit(main())
