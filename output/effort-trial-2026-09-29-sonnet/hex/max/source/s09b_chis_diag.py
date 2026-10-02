"""Step 09b (diagnostic): what is left in a Chiseled face after the groove harmonics are notched?

Prints the residual band power in 15-degree sectors (angle measured from the groove normal u) for
each groove family, and writes a montage: source luminance, notched residual, residual spectrum."""

import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_image, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s04_chisel_measure import CHISELED  # noqa: E402
from s08_raw_height import padded_window, freq_grids, LUMW, NWIN  # noqa: E402
from s09_pools import notch  # noqa: E402


def stretch(a, valid, lo=1.0, hi=99.0):
    v = a[valid]
    l, h = np.percentile(v, lo), np.percentile(v, hi)
    return np.clip((a - l) / (h - l), 0, 1)


def tile(a01, size=256):
    im = Image.fromarray((a01 * 255).astype(np.uint8)).resize((size, size), Image.LANCZOS)
    return np.asarray(im)


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    meas = json.load(open(out_path("work", "chisel_measure.json")))
    psi = json.load(open(out_path("work", "light_axis.json")))["psi_deg"]
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    FX, FY, FR = freq_grids(NWIN)
    TH = np.arctan2(FY, FX)
    band = (FR > 0.04) & (FR < 0.22)
    rows = []
    for kind, lst in CHISELED.items():
        sect_acc = np.zeros(12)
        sect_raw = np.zeros(12)
        for (i, j) in lst:
            m = meas["%s_%d_%d" % (kind, i, j)]
            f0 = 1.0 / m["pitch_px"]
            ang = np.deg2rad(m["line_dir_deg_imgcoords"])
            u = np.array([-np.sin(ang), np.cos(ang)])
            win, tw, valid, cen = padded_window(lum, grid, i, j)
            w = (win - win[valid].mean()) * tw
            res = notch(w, f0, u)
            for arr, acc in ((res, sect_acc), (w, sect_raw)):
                P = np.abs(np.fft.fft2(arr)) ** 2
                rel = np.mod(np.degrees(TH - np.arctan2(u[1], u[0])), 180.0)
                for s in range(12):
                    sel = band & (rel >= s * 15) & (rel < (s + 1) * 15)
                    acc[s] += P[sel].mean()
            if (i, j) == lst[0]:
                Pr = np.fft.fftshift(np.log10(np.abs(np.fft.fft2(res)) ** 2 + 1e-3))
                c = NWIN // 2
                sp = Pr[c - 96:c + 96, c - 96:c + 96]
                sp = np.clip((sp - sp.min()) / (sp.max() - sp.min()), 0, 1)
                rows.append(np.hstack([tile(stretch(win, valid)), tile(stretch(res, valid)), tile(sp)]))
        axis_rel = np.mod(psi - np.degrees(np.arctan2(u[1], u[0])), 180.0)
        print("%-6s  light axis is %.0f deg from u.  sector power (from u, 15-deg bins) after notch, relative to mean:"
              % (kind, axis_rel))
        print("        ", np.round(sect_acc / sect_acc.mean(), 2))
        print("   before notch:", np.round(sect_raw / sect_raw.mean(), 2))
    img = np.vstack(rows)
    save_image(Image.fromarray(img), "work", "thumbs", "chis_resid_montage.png")
    print("montage", img.shape)


if __name__ == "__main__":
    main()
