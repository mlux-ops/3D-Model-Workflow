"""Step 4: measure and classify every face of the layout render (matte / raw / chiseled).

Per cell, on the clean interior (>= 5 px from the joint centreline), inside the image:
  hp_std   std of luma minus a 4 px Gaussian (fine relief energy)
  coher    structure-tensor coherence of the luma gradient (0 isotropic .. 1 one direction)
  line_deg direction of the grooves (perpendicular to the dominant gradient), degrees
           counter-clockwise from +x with y up, in [0, 180)
  fft_per  period (px) of the strongest spectral peak in the 3-14 px band, and its
           share of band energy
Writes _work/cells.json and a labelled overlay _work/cells_overlay.png (800 px).
"""

import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import (load_lattice, render_rgb, luma, gaussian, render_cells,
                    hex_edge_distance_local, out_path, S3)
from guard import save_image

CLEAN_PX = 5.0


def font(sz):
    for p in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def cell_region(lat, c, rgb, clean=CLEAN_PX):
    rp = lat["rp"]
    R = rp / S3
    Hr, Wr = rgb.shape[:2]
    x0 = int(np.floor(c["cx"] - R - 2)); x1 = int(np.ceil(c["cx"] + R + 2))
    y0 = int(np.floor(c["cy"] - rp / 2 - 2)); y1 = int(np.ceil(c["cy"] + rp / 2 + 2))
    X0, X1, Y0, Y1 = max(0, x0), min(Wr, x1), max(0, y0), min(Hr, y1)
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float64)
    e = hex_edge_distance_local(xs + 0.5 - c["cx"], ys + 0.5 - c["cy"], rp * 0.5)
    m = e >= clean
    return (X0, Y0, X1, Y1), m, e


def features(L, m):
    hp = L - gaussian(L, 4.0)
    lf = gaussian(L, 4.0)
    gx = gaussian(L, 1.0)
    Iy, Ix = np.gradient(gx)
    Jxx = (Ix * Ix)[m].sum(); Jyy = (Iy * Iy)[m].sum(); Jxy = (Ix * Iy)[m].sum()
    coher = float(np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2) / (Jxx + Jyy + 1e-12))
    phi = 0.5 * np.degrees(np.arctan2(2 * Jxy, Jxx - Jyy))   # gradient dir, image axes (y down)
    # convert to y-up convention; grooves run perpendicular to the dominant gradient
    grad_deg_up = (-phi) % 180.0
    line_deg = (grad_deg_up + 90.0) % 180.0
    # windowed FFT of the high-pass
    win = gaussian(m.astype(np.float64), 3.0) * m
    a = (hp - hp[m].mean()) * win
    F = np.abs(np.fft.fftshift(np.fft.fft2(a))) ** 2
    h, w = a.shape
    fy = np.fft.fftshift(np.fft.fftfreq(h))[:, None]
    fx = np.fft.fftshift(np.fft.fftfreq(w))[None, :]
    fr = np.sqrt(fx ** 2 + fy ** 2)
    band = (fr > 1 / 14.0) & (fr < 1 / 3.0)
    Fb = np.where(band, gaussian(F, 1.0), 0)
    k = np.unravel_index(np.argmax(Fb), Fb.shape)
    per = float(1.0 / fr[k]) if fr[k] > 0 else 0.0
    share = float(Fb[k] / (F[band].sum() + 1e-12))
    # frequency-peak direction -> groove direction (y-up)
    kdeg = np.degrees(np.arctan2(-fy[k[0], 0], fx[0, k[1]])) % 180.0
    fft_line_deg = (kdeg + 90.0) % 180.0
    return {
        "hp_std": float(hp[m].std()), "lf_std": float(lf[m].std()),
        "mean_luma": float(L[m].mean()), "coher": coher, "line_deg": float(line_deg),
        "fft_per_px": per, "fft_share": share, "fft_line_deg": float(fft_line_deg),
    }


def main():
    lat = load_lattice()
    rgb = render_rgb()
    Lall = luma(rgb)
    cells = render_cells(lat, margin_px=CLEAN_PX)
    out = []
    for c in cells:
        if c["frac"] < 0.12:
            continue
        (X0, Y0, X1, Y1), m, e = cell_region(lat, c, rgb)
        if m.sum() < 800:
            continue
        L = Lall[Y0:Y1, X0:X1]
        f = features(L, m)
        f.update(c)
        f["mean_rgb"] = [float(v) for v in rgb[Y0:Y1, X0:X1][m].mean(axis=0)]
        f["npx"] = int(m.sum())
        out.append(f)
    out.sort(key=lambda d: (d["j"], d["i"]))
    for k, d in enumerate(out):
        d["id"] = k
    print(" id  i  j  frac  hp_std lf_std coher line  fftper share fftline  meanL")
    for d in out:
        print("%3d %2d %2d  %.2f  %5.2f  %5.2f  %.3f %5.1f  %5.2f  %.3f  %5.1f  %6.1f"
              % (d["id"], d["i"], d["j"], d["frac"], d["hp_std"], d["lf_std"], d["coher"],
                 d["line_deg"], d["fft_per_px"], d["fft_share"], d["fft_line_deg"], d["mean_luma"]))
    json.dump(out, open(out_path("_work", "cells_raw.json"), "w"), indent=1)
    # overlay with ids
    Hr, Wr = rgb.shape[:2]
    s = 800.0 / Wr
    im = Image.fromarray(rgb.astype(np.uint8)).resize((800, int(round(Hr * s))), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    fn = font(13)
    for d in out:
        x, y = d["cx"] * s, d["cy"] * s
        t = "%d\n%.1f %.2f" % (d["id"], d["hp_std"], d["coher"])
        dr.multiline_text((x - 18, y - 14), t, fill=(200, 0, 0), font=fn, align="center")
    save_image(im, "_work", "cells_overlay.png")


if __name__ == "__main__":
    sys.exit(main())
