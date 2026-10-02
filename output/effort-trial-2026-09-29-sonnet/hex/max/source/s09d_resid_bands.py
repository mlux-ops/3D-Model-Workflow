"""Step 09d (diagnostic): where in frequency does the Chiseled variance live once the groove
harmonics are notched? Radial bands x (near-u wedge / elsewhere), against the Matte control."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s04_chisel_measure import CHISELED  # noqa: E402
from s08_raw_height import padded_window, freq_grids, LUMW, NWIN  # noqa: E402
from s09_pools import notch, classify  # noqa: E402

EDGES = [0.0, 0.01, 0.02, 0.04, 0.08, 0.16, 0.24, 0.32, 0.42, 0.55, 0.75]


def band_table(w, u, FR, TH):
    P = np.abs(np.fft.fft2(w)) ** 2 / w.size ** 2
    du = np.abs(np.degrees(np.angle(np.exp(2j * (TH - np.arctan2(u[1], u[0])))) / 2.0))
    near = du < 16.0
    out = []
    for a, b in zip(EDGES[:-1], EDGES[1:]):
        sel = (FR >= a) & (FR < b)
        out.append((float(P[sel & near].sum()), float(P[sel & ~near].sum())))
    return np.array(out)


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    meas = json.load(open(out_path("work", "chisel_measure.json")))
    faces = json.load(open(out_path("work", "render_faces_raw.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    FX, FY, FR = freq_grids(NWIN)
    TH = np.arctan2(FY, FX)
    print("radial bands (cyc/px):", EDGES)
    acc = None
    for kind, lst in CHISELED.items():
        for (i, j) in lst:
            m = meas["%s_%d_%d" % (kind, i, j)]
            f0 = 1.0 / m["pitch_px"]
            ang = np.deg2rad(m["line_dir_deg_imgcoords"])
            u = np.array([-np.sin(ang), np.cos(ang)])
            win, tw, valid, cen = padded_window(lum, grid, i, j)
            w = notch((win - win[valid].mean()) * tw, f0, u)
            t = band_table(w, u, FR, TH)
            acc = t if acc is None else acc + t
    acc /= 9.0
    matte = [(f["i"], f["j"]) for f in faces if f["frac_visible"] >= 0.995 and classify(f) == "matte"]
    accm = None
    u = np.array([1.0, 0.0])
    for (i, j) in matte:
        win, tw, valid, cen = padded_window(lum, grid, i, j)
        t = band_table((win - win[valid].mean()) * tw, u, FR, TH)
        accm = t if accm is None else accm + t
    accm /= len(matte)
    print("variance per band  [near-u wedge | elsewhere]   Chiseled after point notch  vs  Matte")
    for k, (a, b) in enumerate(zip(EDGES[:-1], EDGES[1:])):
        print("  %.2f-%.2f   chis [%7.2f | %7.2f]   matte [%7.2f | %7.2f]" % (a, b, acc[k, 0], acc[k, 1], accm[k, 0], accm[k, 1]))
    print("totals: chis near %.1f elsewhere %.1f   matte near %.1f elsewhere %.1f"
          % (acc[:, 0].sum(), acc[:, 1].sum(), accm[:, 0].sum(), accm[:, 1].sum()))


if __name__ == "__main__":
    main()
