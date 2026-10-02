"""Step 10b0: angular gain of the shading inversion. The Wiener height h' from s08 is fed by
shading that only sees the slope along the light, so its power should fall off for wave vectors
perpendicular to the light axis. This script measures that fall-off (pooled over the 8 Raw faces,
three radial bands) so step 10b can weight the two partner sources of a Raw face by measured gain
instead of by an assumed |cos|."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import save_text, out_path  # noqa: E402
from s08_raw_height import freq_grids  # noqa: E402

BANDS = [(0.03, 0.08), (0.08, 0.16), (0.16, 0.30)]      # cycles per source pixel
EDGES = np.arange(0.0, 91.0, 10.0)


def main():
    h = np.load(out_path("work", "pool_raw_h.npy"))
    psi = json.load(open(out_path("work", "pool_raw_info.json")))["psi_axis_deg"]
    n = h.shape[1]
    FX, FY, FR = freq_grids(n)
    th = np.degrees(np.arctan2(FY, FX))
    delta = np.abs(((th - psi + 90.0) % 180.0) - 90.0)      # 0 = along the light axis, 90 = perpendicular
    ys, xs = np.mgrid[0:n, 0:n]
    r = np.hypot(xs - n / 2.0, ys - n / 2.0)
    win = np.clip((165.0 - r) / 20.0, 0.0, 1.0)
    win = 0.5 - 0.5 * np.cos(np.pi * win)
    P = np.zeros((n, n))
    for k in range(h.shape[0]):
        w = h[k] * win
        w = w - w[win > 0.99].mean() * win
        P += np.abs(np.fft.fft2(w)) ** 2
    P /= h.shape[0]
    table = {}
    for lo, hi in BANDS:
        sel = (FR >= lo) & (FR < hi)
        row = []
        for a, b in zip(EDGES[:-1], EDGES[1:]):
            m = sel & (delta >= a) & (delta < b)
            row.append(float(P[m].mean()))
        row = np.array(row)
        table["%.2f-%.2f" % (lo, hi)] = (row / row[0]).tolist()
        print("band %.2f-%.2f  power vs angle from light axis (rel. to 0-10 deg):" % (lo, hi),
              np.round(row / row[0], 3), " cos^2 at bin centre:",
              np.round(np.cos(np.radians(EDGES[:-1] + 5.0)) ** 2, 3))
    save_text(json.dumps({"delta_edges_deg": EDGES.tolist(), "bands": table}, indent=1), "work", "angular_gain.json")


if __name__ == "__main__":
    main()
