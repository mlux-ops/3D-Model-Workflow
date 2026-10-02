"""Step 08c: which side is the light on?

The Raw shading fixes the light *axis* (about -33 deg) but not its sign. The Chiseled grooves
give a second, independent cue. A groove is a depression; a directional light makes the wall
that faces the light brighter than the opposite wall, on top of the symmetric cavity darkening.
For a groove-profile p(t) along the line normal u (t increasing along u) with its minimum at
t0, the asymmetry S = mean[p(t0+d) - p(t0-d)] is negative when the light has a positive
component along u (the wall on the -u side faces +u, toward the light) and positive when the
component is negative.  u is chosen by geometry alone (positive image-y, or +x for vertical
lines), so the sign of the prediction depends on the assumed light sign only through l.u.
"""

import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import RENDER_PATH, save_text, out_path  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s04_chisel_measure import CHISELED, face_window  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722])
NB = 48
LINE_DEG = {"vert": 90.0, "diagS": 30.0, "diagF": 150.0}


def main():
    grid = json.load(open(out_path("work", "render_grid.json")))
    meas = json.load(open(out_path("work", "chisel_measure.json")))
    psi = json.load(open(out_path("work", "light_axis.json")))["psi_deg"]
    l_up = np.array([np.cos(np.deg2rad(psi)), np.sin(np.deg2rad(psi))])      # (0.84, -0.55): toward upper right
    if l_up[0] < 0:
        l_up = -l_up
    lum = load_srgb(RENDER_PATH) @ LUMW
    rows = []
    for kind, faces in CHISELED.items():
        ang = np.deg2rad(LINE_DEG[kind])
        u = np.array([-np.sin(ang), np.cos(ang)])
        if kind == "vert" or u[1] < 0:
            u = np.array([1.0, 0.0]) if kind == "vert" else -u
        lu = float(l_up @ u)
        for (i, j) in faces:
            m = meas["%s_%d_%d" % (kind, i, j)]
            pitch = m["pitch_px"]
            sub, mk, cen = face_window(lum, grid, i, j)
            hp = sub - ndi.gaussian_filter(sub, 8.0)
            ys, xs = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
            t = ((xs - cen[0]) * u[0] + (ys - cen[1]) * u[1]) / pitch        # position in periods
            ph = np.mod(t, 1.0)
            idx = np.minimum((ph * NB).astype(int), NB - 1)
            w = mk > 0.99
            cnt = np.maximum(np.bincount(idx[w], minlength=NB), 1)
            prof = np.bincount(idx[w], weights=hp[w], minlength=NB) / cnt
            ps = ndi.uniform_filter1d(prof, 3, mode="wrap")
            k0 = int(np.argmin(ps))
            d = np.arange(2, int(0.42 * NB))
            S = float(np.mean([prof[(k0 + q) % NB] - prof[(k0 - q) % NB] for q in d]))
            rows.append((kind, i, j, lu, S, float(prof.max() - prof.min())))
            print("%-6s (%2d,%d)  l.u %+.2f   S %+6.2f   p2p %5.1f   predicted sign(S) for light from upper-right: %s"
                  % (kind, i, j, lu, S, prof.max() - prof.min(),
                     "-" if lu > 0.2 else ("+" if lu < -0.2 else "0")))
    agree = [np.sign(-r[3]) == np.sign(r[4]) for r in rows if abs(r[3]) > 0.2]
    print("faces agreeing with light-from-upper-right: %d of %d" % (sum(agree), len(agree)))
    for kind in CHISELED:
        v = [r[4] for r in rows if r[0] == kind]
        print("  %-6s mean S %+6.2f  (n=%d)" % (kind, np.mean(v), len(v)))
    score = float(sum(-r[3] * r[4] for r in rows))          # > 0: light toward upper right
    n_dir = len(agree)
    print("signed score %+.2f -> light toward %s" % (score, "upper-right" if score > 0 else "lower-left"))
    save_text(json.dumps(rows), "work", "light_sign_chisel.json")
    save_text(json.dumps({"toward_lower_left": bool(score < 0), "score": score,
                          "faces_agreeing_with_upper_right": int(sum(agree)), "directional_faces": n_dir,
                          "diagF_control_S": [r[4] for r in rows if r[0] == "diagF"]}),
              "work", "light_sign.json")


if __name__ == "__main__":
    main()
