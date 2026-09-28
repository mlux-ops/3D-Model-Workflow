"""Step 3b: sub-pixel refinement of the render lattice (explicit simplex on all 5 terms).

The first fit's Nelder-Mead started y0 at exactly 0, where the default simplex step is
~0, so y0 was never explored. This pass re-optimises with a fixed-size initial simplex
and reports the joint-line profile on both sides of the centreline (signed distance),
which exposes any residual offset.
"""

import json
import sys

import numpy as np
from PIL import Image
from scipy import optimize

from guard import RENDER_PATH, out_path
from a03_fit_lattice import joint_score, edge_distance

S3 = np.sqrt(3.0)


def main():
    lat = json.load(open(out_path("_work", "lattice.json")))
    rgb = np.asarray(Image.open(RENDER_PATH).convert("RGB"))
    S, L = joint_score(rgb)
    thr = np.percentile(S, 97.0)
    yy, xx = np.nonzero(S > thr)
    ww = S[yy, xx]
    xs = xx + 0.5
    ys = yy + 0.5

    def score(p, sig=0.9):
        e, _, _ = edge_distance(xs, ys, p)
        return float((ww * np.exp(-0.5 * (e / sig) ** 2)).sum() / ww.sum())

    p0 = np.array([lat["rp"], lat["aniso"], lat["theta_deg"], lat["x0"], lat["y0"]])
    steps = np.array([0.3, 0.001, 0.02, 0.6, 0.6])
    simplex = [p0] + [p0 + np.eye(5)[k] * steps[k] for k in range(5)]
    best = None
    for start in (p0, p0 + np.array([0, 0, 0, 0, 0.5]), p0 + np.array([0, 0, 0, 0, -0.5])):
        sim = [start] + [start + np.eye(5)[k] * steps[k] for k in range(5)]
        r = optimize.minimize(lambda q: -score(q), start, method="Nelder-Mead",
                              options={"initial_simplex": np.array(sim), "xatol": 1e-4,
                                       "fatol": 1e-7, "maxiter": 3000})
        print("start y0 %.2f -> %s score %.5f" % (start[4], np.round(r.x, 4), -r.fun))
        if best is None or r.fun < best.fun:
            best = r
    rp, an, th, x0, y0 = best.x
    cp = rp * S3 / 2.0 * an
    print("refined: rp %.4f cp %.4f aniso %.5f theta %.4f x0 %.3f y0 %.3f"
          % (rp, cp, an, th, x0, y0))
    # signed profile across horizontal joints only (top/bottom flats): use dy sign
    H, W = S.shape
    ys2, xs2 = np.mgrid[0:H, 0:W].astype(np.float64)
    e, bi, bj = edge_distance(xs2 + 0.5, ys2 + 0.5, (rp, an, th, x0, y0))
    yoff = np.where(bi % 2 != 0, rp * 0.5, 0.0)
    cy = y0 + yoff + bj * rp
    dy = ys2 + 0.5 - cy
    horiz = np.abs(dy) > rp * 0.5 - 6            # near a top/bottom flat
    sgn = np.sign(dy)                            # + = bottom flat of this cell
    print("signed profile at bottom flats (distance inside cell above the joint):")
    for k in range(0, 8):
        m = horiz & (sgn > 0) & (np.abs(e - k * 0.5) < 0.25)
        print("  e %.1f luma %.2f   (n=%d)" % (k * 0.5, L[m].mean(), m.sum()))
    print("signed profile at top flats:")
    for k in range(0, 8):
        m = horiz & (sgn < 0) & (np.abs(e - k * 0.5) < 0.25)
        print("  e %.1f luma %.2f   (n=%d)" % (k * 0.5, L[m].mean(), m.sum()))
    lat.update({"rp": rp, "cp": cp, "aniso": an, "theta_deg": th, "x0": x0, "y0": y0,
                "refine_score": -best.fun})
    json.dump(lat, open(out_path("_work", "lattice.json"), "w"), indent=2)


if __name__ == "__main__":
    sys.exit(main())
