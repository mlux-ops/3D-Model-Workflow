"""Measure the floor photo's depth scale (alpha) from texture isotropy.

Across-scale is fixed by the joints. Depth-scale is the one free parameter.
Cross-cut stone has no directional veining, and the swatch confirms it
(band-passed gradient energy ratio gy^2/gx^2 close to 1). alpha is chosen so
the rectified floor texture has the same ratio, measured in the same
physical band, over several independent regions. Writes floor_calibration.json.
"""
import json

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import brentq

from floor_geom import CALIB, FLOOR, SWATCH, FloorGeom, load_gray

R = 8.0                                   # px/in for the measurement
BANDS = [(0.35, 0.9), (0.5, 1.5)]         # DoG sigmas in inches
SWATCH_PPI = 2000 / 48.0


def ratio(img, mask, band, r):
    d = ndi.gaussian_filter(img, band[0] * r) - ndi.gaussian_filter(img, band[1] * r)
    gy, gx = np.gradient(d)
    return float((gy[mask] ** 2).mean() / (gx[mask] ** 2).mean())


def swatch_ratio(band, r=R):
    sw = load_gray(SWATCH)
    w, h = int(round(sw.shape[1] / SWATCH_PPI * r)), int(round(sw.shape[0] / SWATCH_PPI * r))
    s = np.asarray(Image.fromarray(sw).resize((w, h), Image.LANCZOS)).astype(float)
    m = np.zeros(s.shape, bool)
    b = int(3 * band[1] * r)
    m[b:-b, b:-b] = True
    return ratio(s, m, band, r)


def main():
    geo = FloorGeom(alpha=1.0)
    fl = load_gray(FLOOR)
    Xj = geo.joint_X
    subsets = {
        "far_row": lambda X, Z: Z > 0, "near_row": lambda X, Z: Z < 0,
        "col1": lambda X, Z: (X > Xj[0]) & (X < Xj[1]), "col2": lambda X, Z: (X > Xj[1]) & (X < Xj[2]),
        "col3": lambda X, Z: (X > Xj[2]) & (X < Xj[3]), "col4": lambda X, Z: (X > Xj[3]) & (X < Xj[4]),
    }

    def floor_ratio(alpha, band, sel):
        ztop = alpha * (1 / (8 - geo.y_vp) - 1 / geo.u_j)
        zbot = alpha * (1 / (346 - geo.y_vp) - 1 / geo.u_j)
        out, XX, ZZ, x, y = geo.rectify(fl, R, Xj[0] - 24, Xj[-1] + 6, zbot, ztop, alpha)
        ok = geo.valid_mask(XX, ZZ, x, y, joint_clear=1.0) & np.isfinite(out)
        o = np.where(np.isfinite(out), out, np.nanmean(out))
        ok = ndi.binary_erosion(ok, iterations=int(1.2 * R))
        return ratio(o, ok & sel(XX, ZZ), band, R)

    results = []
    for band in BANDS:
        target = swatch_ratio(band)
        for name, sel in subsets.items():
            for tgt_name, tgt in [("swatch", target), ("unity", 1.0)]:
                a = brentq(lambda al: floor_ratio(al, band, sel) - tgt, 1.0e5, 2.6e5, xtol=200)
                results.append({"band_in": band, "subset": name, "target": tgt_name,
                                "target_ratio": round(tgt, 4), "alpha": round(a, 0)})
                print(results[-1], flush=True)
    al = np.array([r["alpha"] for r in results])
    alpha = float(np.median(al))
    geo.alpha = alpha
    info = {
        "alpha": alpha,
        "alpha_spread": {"min": float(al.min()), "max": float(al.max()), "std": float(al.std()),
                         "n": int(len(al))},
        "K_in": geo.K, "vp_px": [geo.x_vp, geo.y_vp], "cross_joint_row_px": 260.5,
        "joint_X_in": [float(v) for v in Xj], "joint_fit_rms_px": geo.joint_rms,
        "visible_depth_in": {"far_row": alpha * (1 / (0 - geo.y_vp) - 1 / geo.u_j),
                             "near_row": alpha * (1 / (348 - geo.y_vp) - 1 / geo.u_j)},
        "source_res_ppi": {"top_row_across_depth": list(geo.local_res(0)),
                           "bottom_row_across_depth": list(geo.local_res(348))},
        "measurements": results,
    }
    with open(CALIB, "w") as f:
        json.dump(info, f, indent=2)
    print("alpha = %.0f (min %.0f, max %.0f)" % (alpha, al.min(), al.max()))
    print("far-row depth visible %.1f in, near-row %.1f in" % tuple(info["visible_depth_in"].values()))
    print("source res top (across, depth) %.1f, %.1f px/in; bottom %.1f, %.1f px/in"
          % (*geo.local_res(0), *geo.local_res(348)))


if __name__ == "__main__":
    main()
