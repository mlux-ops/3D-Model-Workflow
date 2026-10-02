"""Step 04b: chiseled cross-section profile in a canonical frame (grooves rotated to
vertical), per orientation class, harmonic decomposition, and RGB colour dependence."""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s03_faces import hex_dist_inside  # noqa: E402
from s04_chisel_measure import CHISELED, face_window, fft_peak  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])
PITCH = 6.185
NB = 48


def fold(chan, m, fxc, fyc, nb=NB):
    f = np.hypot(fxc, fyc)
    sgn = 1.0 if fxc > 0 else -1.0
    ux, uy = sgn * fxc / f, sgn * fyc / f
    pitch = 1.0 / f
    ys, xs = np.mgrid[0:chan.shape[0], 0:chan.shape[1]]
    u = xs * ux + ys * uy
    ph = np.mod(u / pitch, 1.0)
    hp = chan - ndi.gaussian_filter(chan, 8.0)
    sel = m > 0.999
    idx = np.minimum((ph[sel] * nb).astype(int), nb - 1)
    cnt = np.maximum(np.bincount(idx, minlength=nb), 1)
    prof = np.bincount(idx, weights=hp[sel], minlength=nb) / cnt
    # per-period jitter of profile: std of the profile over quarter-image subsets
    return prof, pitch


def harmonics(prof, nh=4):
    nb = len(prof)
    F = np.fft.rfft(prof) / nb * 2.0
    return [(abs(F[n]), np.degrees(np.angle(F[n]))) for n in range(1, nh + 1)]


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    rgb = load_srgb(RENDER_PATH)
    lum = rgb @ LUMW
    out = {}
    for kind, faces in CHISELED.items():
        for (i, j) in faces:
            sub, m, c = face_window(lum, grid, i, j)
            fxc, fyc, spread, pk = fft_peak(sub, m)
            prof, pitch = fold(sub, m, fxc, fyc)
            h = harmonics(prof)
            # phase of 2nd harmonic relative to twice the 1st: invariant to fold origin
            rel = (h[1][1] - 2 * h[0][1]) % 360.0
            rel3 = (h[2][1] - 3 * h[0][1]) % 360.0
            out["%s_%d_%d" % (kind, i, j)] = {"amp": [a for a, _ in h], "ph": [p for _, p in h],
                                              "rel2": rel, "rel3": rel3}
            print("%-5s (%2d,%d) f=(%+.4f,%+.4f) A1 %.2f A2 %.2f A3 %.2f A4 %.2f   rel2 %.0f  rel3 %.0f"
                  % (kind, i, j, fxc, fyc, h[0][0], h[1][0], h[2][0], h[3][0], rel, rel3))
    save_text(json.dumps(out, indent=1), "work", "chisel_harmonics.json")


if __name__ == "__main__":
    main()
