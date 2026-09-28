"""Edge-continuity search over all 8 faces, all 8 dihedral orientations of the neighbour, for the right-hand and
the lower neighbour, at full resolution (1417 px). Also: face-identity test (IMGCOM vs faces), per-face
lighting/vignetting fit, and colour statistics in sRGB (sources are tagged Adobe RGB (1998)).

Edge score: 1-D luminance profile of the 3 px strip along A's edge vs the 3 px strip along B's facing edge,
band-passed along the edge (Gaussian 1.2 - 25 px), NCC at along-edge shift s in [-12, 12] and at normal gap
g in [0, 12] px (g > 0: B's first g px treated as missing / trimmed). Baseline: the same statistic between two
3 px strips 3 px apart inside every face (interior continuity), and between random non-adjacent strips.
Writes _work/edges.json and prints the ranked table.  Usage: python a01_edges.py"""
import itertools
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, zoom

from colour_io import load_face_lin, lum
from guard import out_path, ref

K = 3
SH = 12


def D4(a, t):
    k, f = divmod(t, 2)
    r = np.rot90(a, k)
    return r[:, ::-1] if f else r


TNAME = ["r0", "r0+flipH", "r90", "r90+flipH", "r180", "r180+flipH", "r270", "r270+flipH"]


def bp(p):
    return gaussian_filter1d(p, 1.2) - gaussian_filter1d(p, 25)


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-18))


def best_shift(pa, pb):
    best = (-2, 0)
    n = len(pa)
    for s in range(-SH, SH + 1):
        if s >= 0:
            v = ncc(pa[s:], pb[:n - s])
        else:
            v = ncc(pa[:n + s], pb[-s:])
        if v > best[0]:
            best = (v, s)
    return best


def main():
    L = [lum(load_face_lin(i)) for i in range(1, 9)]
    n = len(L[0])
    # interior baseline
    base = []
    for Li in L:
        for x in range(100, n - 100, 60):
            base.append(ncc(bp(Li[:, x - K:x].mean(1)), bp(Li[:, x + K:x + 2 * K].mean(1))))
    rnd = []
    rng = np.random.default_rng(1)
    for _ in range(400):
        i, j = rng.integers(0, 8, 2)
        x, y = rng.integers(10, n - 10, 2)
        rnd.append(ncc(bp(L[i][:, x:x + K].mean(1)), bp(L[j][:, y:y + K].mean(1))))
    rows = []
    for i, j in itertools.product(range(8), range(8)):
        if i == j:
            continue
        A = L[i]
        for t in range(8):
            B = D4(L[j], t)
            for rel in ("right", "below", "left", "above"):
                if rel == "right":
                    pa = bp(A[:, -K:].mean(1))
                    prof = [bp(B[:, g:g + K].mean(1)) for g in range(13)]
                elif rel == "left":
                    pa = bp(A[:, :K].mean(1))
                    prof = [bp(B[:, n - K - g:n - g].mean(1)) for g in range(13)]
                elif rel == "below":
                    pa = bp(A[-K:, :].mean(0))
                    prof = [bp(B[g:g + K, :].mean(0)) for g in range(13)]
                else:
                    pa = bp(A[:K, :].mean(0))
                    prof = [bp(B[n - K - g:n - g, :].mean(0)) for g in range(13)]
                s0 = ncc(pa, prof[0])
                bs = best_shift(pa, prof[0])
                gbest = max((ncc(pa, prof[g]), g) for g in range(13))
                rows.append({"a": i + 1, "b": j + 1, "orient_b": TNAME[t], "rel": rel, "ncc0": s0,
                             "best_shift": bs[1], "ncc_best_shift": bs[0], "best_gap": gbest[1], "ncc_best_gap": gbest[0]})
    rows.sort(key=lambda r: -r["ncc0"])
    # identity test: IMGCOM vs every face (downscaled 2x), all orientations
    im = lum(load_face_lin("IMGCOM_940"))
    ident = []
    for j in range(8):
        f = zoom(L[j], im.shape[0] / n, order=1)[:im.shape[0], :im.shape[1]]
        ident.append({"face": j + 1, "ncc_best_orient": max(ncc(im, D4(f, t)) for t in range(8))})
    # lighting: fit a quadratic surface to heavily blurred log-luminance of each face
    light = []
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1) - 0.5
    Aq = np.stack([np.ones(n * n), xx.ravel(), yy.ravel(), (xx * xx).ravel(), (yy * yy).ravel(), (xx * yy).ravel()], 1)
    for i, Li in enumerate(L):
        lg = np.log(Li + 1e-4).ravel()
        c, *_ = np.linalg.lstsq(Aq, lg, rcond=None)
        fit = (Aq @ c).reshape(n, n)
        light.append({"face": i + 1, "coef": [float(v) for v in c], "fit_range_pct": float(100 * (np.exp(fit.max() - fit.min()) - 1)),
                      "corner_vs_centre_pct": float(100 * (np.exp(np.mean([fit[0, 0], fit[0, -1], fit[-1, 0], fit[-1, -1]]) - fit[n // 2, n // 2]) - 1)),
                      "edge_means_lum": {"left": float(Li[:, :20].mean()), "right": float(Li[:, -20:].mean()),
                                         "top": float(Li[:20].mean()), "bottom": float(Li[-20:].mean()), "all": float(Li.mean())}})
    out = {"baseline_interior_3px": [float(np.mean(base)), float(np.percentile(base, 10)), float(np.percentile(base, 90))],
           "baseline_random": [float(np.mean(rnd)), float(np.percentile(rnd, 1)), float(np.percentile(rnd, 99))],
           "top40": rows[:40], "imgcom_identity": ident, "lighting": light}
    json.dump({**out, "all": rows}, open(out_path("_work/edges.json"), "w"), indent=1)
    print("interior baseline mean/p10/p90 %.3f %.3f %.3f" % tuple(out["baseline_interior_3px"]))
    print("random   baseline mean/p1/p99  %.3f %.3f %.3f" % tuple(out["baseline_random"]))
    for r in [r for r in rows if r["rel"] in ("right", "left")][:24]:
        print("%d -> %d %-11s %-5s ncc0 %.3f  shift %+d (%.3f)  gap %d (%.3f)" % (
            r["a"], r["b"], r["orient_b"], r["rel"], r["ncc0"], r["best_shift"], r["ncc_best_shift"], r["best_gap"], r["ncc_best_gap"]))
    print("best vertical (below/above) rows:")
    for r in [r for r in rows if r["rel"] in ("below", "above")][:14]:
        print("%d v %d %-11s %s ncc0 %.3f shift %+d (%.3f) gap %d (%.3f)" % (
            r["a"], r["b"], r["orient_b"], r["rel"], r["ncc0"], r["best_shift"], r["ncc_best_shift"], r["best_gap"], r["ncc_best_gap"]))
    print(json.dumps(ident))
    for l in light:
        print(l["face"], "range %.1f%%  corner-centre %.1f%%" % (l["fit_range_pct"], l["corner_vs_centre_pct"]),
              {k: round(v, 4) for k, v in l["edge_means_lum"].items()})


if __name__ == "__main__":
    main()
