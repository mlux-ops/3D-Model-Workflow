"""Step 8: tone measurements.

(a) render illumination field: a quadratic surface fitted to the per-face median linear
    luma of every face with a clean interior; residual per-face tone variation.
(b) joint colour: the darkest pixel of every joint cross-section in the render, plus a
    coverage correction from the integrated line darkness.
(c) groove phase relative to the tile centre for each chiseled face (is the pattern
    registered to the tile?).
(d) lifestyle tone: median colour of lit tile-face windows vs render face colour.
Writes _work/tone.json.
"""

import json
import sys

import numpy as np

from common import (load_lattice, render_rgb, lifestyle_rgb, srgb_to_lin, lin_to_srgb,
                    out_path, S3, hex_edge_distance_local)
from a03_fit_lattice import edge_distance


def main():
    lat = load_lattice()
    cells = json.load(open(out_path("_work", "cells_raw.json")))
    gr = json.load(open(out_path("_work", "grooves.json")))
    rgb = render_rgb()
    lin = srgb_to_lin(rgb)
    Y = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    Hr, Wr = Y.shape
    rp = lat["rp"]
    ys, xs = np.mgrid[0:Hr, 0:Wr].astype(np.float64)
    e, bi, bj = edge_distance(xs + 0.5, ys + 0.5, (lat["rp"], lat["aniso"], lat["theta_deg"],
                                                  lat["x0"], lat["y0"]))
    # (a) illumination field from per-face medians (all types; textured faces' medians
    # are close to their base tone)
    pts = []
    for c in cells:
        m = (bi == c["i"]) & (bj == c["j"]) & (e >= 6)
        if m.sum() < 3000:
            continue
        t = "chiseled" if c["coher"] > 0.6 else ("raw" if c["hp_std"] > 2.8 else "matte")
        med = np.median(lin[m], axis=0)
        pts.append((c["cx"], c["cy"], float(np.median(Y[m])), t, c["id"], med))
    X = np.array([[1, p[0] / Wr, p[1] / Hr, (p[0] / Wr) ** 2, (p[1] / Hr) ** 2,
                   p[0] * p[1] / (Wr * Hr)] for p in pts])
    yv = np.array([p[2] for p in pts])
    isM = np.array([p[3] == "matte" for p in pts])
    coef, *_ = np.linalg.lstsq(X[isM], yv[isM], rcond=None)
    fit = X @ coef
    resid = yv / fit
    print("illumination fit coef", np.round(coef, 5))
    print("fitted field range over faces: %.4f .. %.4f (ratio %.3f)" % (fit.min(), fit.max(), fit.max() / fit.min()))
    for t in ("matte", "raw", "chiseled"):
        r = resid[[p[3] == t for p in pts]]
        print("  %s: per-face tone after field removal: mean %.4f sd %.4f  (n=%d)" % (t, r.mean(), r.std(), len(r)))
    # corrected base colour of matte faces
    meds = np.array([p[5] for p in pts])
    corr = meds / (fit / fit.mean())[:, None]
    mm = corr[isM].mean(axis=0)
    print("matte base colour, field-normalised: linear", np.round(mm, 4), " sRGB", np.round(lin_to_srgb(mm), 1))
    # (b) joint colour
    core = (e < 0.5)
    face_ring = (e > 3.0) & (e < 6.0)
    jc = np.median(rgb[core], axis=0)
    fc = np.median(rgb[face_ring], axis=0)
    # min along each cross-section approximated by the 10th percentile of the core
    j10 = np.percentile(rgb[e < 0.7], 10, axis=0)
    # integrated darkness: sum over signed distance of (face - pixel) per unit length
    prof = []
    for k in np.arange(0, 4.01, 0.25):
        mk = (e >= k - 0.125) & (e < k + 0.125)
        prof.append(np.median(rgb[mk], axis=0))
    prof = np.array(prof)
    deficit = 2.0 * np.trapezoid(fc[None, :] - prof, dx=0.25, axis=0)   # both sides
    print("joint core median sRGB", np.round(jc, 1), " 10th pct", np.round(j10, 1),
          " face ring", np.round(fc, 1))
    print("integrated joint darkness per channel (level*px)", np.round(deficit, 1))
    for w in (1.0, 1.25, 1.5):
        print("  line width %.2f px -> implied joint colour sRGB %s" % (w, np.round(fc - deficit / w, 1)))
    # (c) groove phase relative to the tile centre
    per = gr["period_px_mean"]
    phases = []
    for g in gr["faces"]:
        c = [cc for cc in cells if cc["id"] == g["id"]][0]
        m = (bi == c["i"]) & (bj == c["j"]) & (e >= 6)
        dx = xs[m] + 0.5 - c["cx"]; dy = ys[m] + 0.5 - c["cy"]
        t = np.deg2rad(g["normal_img_deg"])
        u = (dx * np.cos(t) + dy * np.sin(t)) / per
        v = Y[m] - Y[m].mean()
        c1 = (v * np.exp(-2j * np.pi * u)).sum() / len(v)
        c2 = (v * np.exp(-4j * np.pi * u)).sum() / len(v)
        # position of the brightest point of the fundamental relative to centre, in periods
        crest = (np.angle(c1) / (2 * np.pi)) % 1.0
        phases.append({"id": g["id"], "family": round(g["groove_deg_yup"]), "crest_phase": crest,
                       "c1": abs(c1), "rel_c2": abs(c2) / abs(c1),
                       "relphase2_deg": float(np.degrees(np.angle(c2 * np.conj(c1) ** 2))),
                       "normal_img_deg": g["normal_img_deg"]})
        print("  chiseled id %2d family %3d: fundamental crest at %.3f period from centre, "
              "c2/c1 %.3f, rel phase %+.1f" % (g["id"], round(g["groove_deg_yup"]), crest,
                                               abs(c2) / abs(c1), phases[-1]["relphase2_deg"]))
    # (d) lifestyle tone
    L = lifestyle_rgb()
    wins = {"upper matte face": (457, 180, 100, 100), "mid matte face": (457, 590, 100, 100),
            "third matte window": (360, 700, 80, 80)}
    lres = {}
    for k, (x0, y0, w, h) in wins.items():
        a = L[y0:y0 + h, x0:x0 + w].reshape(-1, 3)
        med = np.median(a, axis=0)
        la = srgb_to_lin(med)
        lres[k] = {"srgb": med.tolist(), "chroma_r_over_g": float(la[0] / la[1]),
                   "chroma_b_over_g": float(la[2] / la[1])}
        print("lifestyle %s: median sRGB %s  lin R/G %.3f B/G %.3f" % (k, np.round(med, 1), la[0] / la[1], la[2] / la[1]))
    print("render matte: lin R/G %.3f B/G %.3f" % (mm[0] / mm[1], mm[2] / mm[1]))
    out = {"illum_coef": coef.tolist(), "illum_terms": "1, x/W, y/H, (x/W)^2, (y/H)^2, xy/(WH)",
           "illum_mean": float(fit.mean()),
           "matte_base_lin": mm.tolist(), "matte_base_srgb": lin_to_srgb(mm).tolist(),
           "per_face": [{"id": p[4], "type": p[3], "tone_resid": float(r)} for p, r in zip(pts, resid)],
           "joint_core_srgb": jc.tolist(), "joint_p10_srgb": j10.tolist(), "face_ring_srgb": fc.tolist(),
           "joint_deficit": deficit.tolist(), "groove_phase": phases, "lifestyle": lres}
    json.dump(out, open(out_path("_work", "tone.json"), "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
