"""Is the product photo itself built from a repeated texture? (Renders often reuse one veneer map.)

For every 6 x 3 in window (192 x 96 px) of every rectified crop, search every crop (other crops, and its own crop
away from itself) under the four grain-preserving transforms (r0, flipH, flipV, r180) with normalised
cross-correlation on a band-passed luminance with the along-grain mean removed.

Metric sanity test first (memory lesson 2026-09-26): a planted exact copy must score ~1, and a
phase-randomised surrogate gives the no-match baseline.  Writes _work/source_dupes.json."""
import json

import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

from common import lum
from guard import out_path

NAMES = ["drawer_L1", "drawer_L2", "drawer_L3", "drawer_R1", "drawer_R2", "drawer_R3", "door_L", "door_R", "apron",
         "bottom_rail"]
WW, WH = 192, 96          # 6 x 3 in at 32 px/in; apron/rail are only 70 px tall -> 64 px windows there
TR = {"r0": lambda a: a, "flipH": lambda a: a[:, ::-1], "flipV": lambda a: a[::-1], "r180": lambda a: a[::-1, ::-1]}


def feat(rgb):
    L = np.log(np.maximum(lum(rgb), 1e-4))
    L = ndi.gaussian_filter(L, 0.8) - ndi.gaussian_filter(L, 12)
    # remove along-grain mean (the pure stripe profile) with a 3 in running mean along x
    return L - ndi.uniform_filter1d(L, 96, axis=1, mode="reflect")


def ncc_valid(img, tpl):
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum())
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    o = np.ones_like(t)
    s1 = fftconvolve(img, o, mode="valid")
    s2 = fftconvolve(img * img, o, mode="valid")
    return num / (np.sqrt(np.maximum(s2 - s1 * s1 / t.size, 1e-12)) * tn)


def windows(F, wh):
    H, W = F.shape
    out = []
    for y in range(0, H - wh + 1, max(wh // 2, 1) if H > 2 * wh else max(H - wh, 1)):
        for x in range(0, W - WW + 1, WW // 2):
            out.append((y, x))
    return out


def main():
    F = {n: feat(np.load(out_path("_work/crops/%s.npy" % n))) for n in NAMES}
    # sanity test: planted copy + surrogate
    rng = np.random.default_rng(3)
    base = F["door_L"]
    tpl = base[100:196, 300:492]
    planted = F["door_R"].copy()
    planted[150:246, 500:692] = tpl
    s_copy = float(ncc_valid(planted, tpl).max())
    ph = np.fft.fft2(F["door_R"])
    sur = np.real(np.fft.ifft2(np.abs(ph) * np.exp(1j * rng.uniform(0, 2 * np.pi, ph.shape))))
    s_sur = float(ncc_valid(sur, tpl).max())
    s_other = float(ncc_valid(F["door_R"], tpl).max())
    print("sanity: planted copy %.3f  surrogate %.3f  real other door %.3f" % (s_copy, s_sur, s_other))

    results, worst = [], []
    for a in NAMES:
        wh = WH if F[a].shape[0] >= WH + 8 else 64
        for (y, x) in windows(F[a], wh):
            t = F[a][y:y + wh, x:x + WW]
            best = (-1, None)
            for b in NAMES:
                for tn, f in TR.items():
                    if F[b].shape[0] < wh:
                        continue
                    img = f(F[b])
                    m = ncc_valid(img, t)
                    if b == a and tn == "r0":
                        yy, xx = np.ogrid[:m.shape[0], :m.shape[1]]
                        m = np.where((np.abs(yy - y) < wh) & (np.abs(xx - x) < WW), -1, m)
                    v = float(m.max())
                    if v > best[0]:
                        best = (v, (b, tn))
            results.append({"crop": a, "y": y, "x": x, "best": round(best[0], 3), "match": best[1]})
    results.sort(key=lambda r: -r["best"])
    vals = np.array([r["best"] for r in results])
    out = {"sanity": {"planted_copy": round(s_copy, 3), "phase_randomised_surrogate": round(s_sur, 3),
                      "real_other_door": round(s_other, 3)},
           "windows": len(results), "max": float(vals.max()), "p95": float(np.percentile(vals, 95)),
           "median": float(np.median(vals)), "top10": results[:10]}
    json.dump(out, open(out_path("_work/source_dupes.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("windows", "max", "p95", "median")}))
    for r in results[:10]:
        print(r)


if __name__ == "__main__":
    main()
