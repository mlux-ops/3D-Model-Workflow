"""Step 09c (diagnostic): remove the groove signal with an angular wedge around +-u instead of
point notches, and see how much luminance variance survives as organic residual.

Control: Matte luminance std over the same interior mask (the organic level a groove-free land
should have) and the same wedge removal applied to Matte faces (fraction of variance a wedge takes
from an isotropic field)."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402
from s04_chisel_measure import CHISELED  # noqa: E402
from s08_raw_height import padded_window, freq_grids, LUMW, NWIN  # noqa: E402
from s09_pools import notch, classify  # noqa: E402


def wedge_remove(w, u, half_deg, f_lo=0.06, f_hi=0.66, ramp_deg=3.0):
    n = w.shape[0]
    FX, FY, FR = freq_grids(n)
    th = np.arctan2(FY, FX)
    du = np.abs(np.degrees(np.angle(np.exp(2j * (th - np.arctan2(u[1], u[0])))) / 2.0))
    keep_ang = np.clip((du - half_deg) / ramp_deg, 0.0, 1.0)
    keep_ang = 0.5 - 0.5 * np.cos(np.pi * keep_ang)
    rad = np.clip((FR - f_lo) / 0.02, 0, 1) * np.clip((f_hi - FR) / 0.05, 0, 1)
    rad = 0.5 - 0.5 * np.cos(np.pi * rad)
    keep = 1.0 - rad * (1.0 - keep_ang)
    return np.real(np.fft.ifft2(np.fft.fft2(w) * keep))


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    F = grid["F_px"]
    meas = json.load(open(out_path("work", "chisel_measure.json")))
    faces = json.load(open(out_path("work", "render_faces_raw.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    ys, xs = np.mgrid[0:NWIN, 0:NWIN]
    matte = [(f["i"], f["j"]) for f in faces if f["frac_visible"] >= 0.995 and classify(f) == "matte"]
    widths = [0, 4, 8, 12, 16]
    print("wedge half-angle (deg):", widths)
    for kind, lst in CHISELED.items():
        rows = []
        for (i, j) in lst:
            m = meas["%s_%d_%d" % (kind, i, j)]
            f0 = 1.0 / m["pitch_px"]
            ang = np.deg2rad(m["line_dir_deg_imgcoords"])
            u = np.array([-np.sin(ang), np.cos(ang)])
            win, tw, valid, cen = padded_window(lum, grid, i, j)
            vin = hex_dist_inside(xs - cen[0], ys - cen[1], F) > 14
            w = (win - win[valid].mean()) * tw
            r = [float(w[vin].std())]
            r += [float(wedge_remove(w, u, W)[vin].std()) for W in widths[1:]]
            r.append(float(notch(w, f0, u)[vin].std()))
            rows.append(r)
        rows = np.array(rows).mean(0)
        print("%-6s std: none %.2f | wedge %s | point notch %.2f" % (kind, rows[0], np.round(rows[1:-1], 2), rows[-1]))
    # Matte control: raw std and std after removing a wedge in three arbitrary directions
    stds, after = [], []
    for (i, j) in matte:
        win, tw, valid, cen = padded_window(lum, grid, i, j)
        vin = hex_dist_inside(xs - cen[0], ys - cen[1], F) > 14
        w = (win - win[valid].mean()) * tw
        stds.append(w[vin].std())
        after.append([wedge_remove(w, np.array([1.0, 0.0]), W)[vin].std() for W in widths[1:]])
    print("Matte control: std %.2f  after wedge %s" % (np.mean(stds), np.round(np.mean(after, 0), 2)))


if __name__ == "__main__":
    main()
