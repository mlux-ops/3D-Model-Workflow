"""Independent verifier for the ELM Jute Vein-Cut 24x48 and 1x3 mosaic maps and model patterns.

Re-reads Color.png, Bump16.png and the .pat from disk and re-derives every gate from the geometry stated
below (it does not import the builders). Writes <dir>/validation.json; exits 1 on any failure.
Usage: python b03_verify.py veincut_24x48 | mosaic_1x3

Gates
  ihdr          colour 8-bit RGB (type 2), bump 16-bit grey (type 0), identical W x H (IHDR bytes)
  aspect        W, H == modules x PPI exactly (integer px per inch); pixel aspect == physical aspect
  quarter_inch  both Sample Size numbers exact multiples of 0.25 in (self-tested: 142.107 / 142.482 must fail)
  joints        joint centres measured on the bump (sub-pixel, across every joint on sampled lines) vs
                k * module; effective joint width vs design; per-column/row widths equal (sheet joints of
                the mosaic are not wider)
  wrap          all four image edges lie inside half joints (grout on 100 % of edge pixels); left+right and
                top+bottom half-joint widths add up to one joint; colour and bump edge steps vs interior
  distinct      24x48: no two cells are the same face in the same orientation (NCC < 0.5, translation search);
                real-face clusters (orientation-searched NCC > 0.6) never touch each other (8-neighbourhood,
                wrapped). mosaic: no chip matches any other chip (NCC < 0.6, 4 orientations, +-1 px shifts);
                no two crop windows in report.json overlap in their source
  veins         structure-tensor vein direction per cell (24x48) / per 12 in block (mosaic) within 10 deg of
                horizontal
  clearance     tile face (outside the eased edge) above the grout floor; grout core == 0; full scale matches
  colour_bump   grout-core pixels carry the grout colour; face mean within 4 % (linear) of the Jute swatch u09
  model_pattern e01 analytic check of both .pat patterns (re-parsed from disk)
"""
import itertools
import json
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from common import LUMA, ftin, ihdr, ncc_map, srgb_to_lin
from guard import out_path

Image.MAX_IMAGE_PIXELS = None
MM = 25.4
GEOM = {  # restated independently of the builders
    "veincut_24x48": {"ppi": 36, "mod": (47.0 + 5.0 / 24.0 + 0.125, 23.625 + 0.125), "joint": 0.125,
                      "n": (3, 6), "edge_mm": 1.0, "face_mm": 1.5, "grout": (208, 198, 180)},
    "mosaic_1x3": {"ppi": 48, "mod": (3.0, 1.0), "joint": 0.0625, "n": (16, 48), "edge_mm": 0.6,
                   "face_mm": 1.2, "grout": (208, 198, 180)},
}
U09_MEAN_LIN = None


def is_quarter(x):
    return abs(x * 4 - round(x * 4)) < 1e-9


def vein_angle(L):
    """Dominant vein (iso-line) direction in degrees from the image x axis (0 = horizontal)."""
    gy, gx = np.gradient(gaussian_filter(L, 1.5))
    jxx, jyy, jxy = (gx * gx).mean(), (gy * gy).mean(), (gx * gy).mean()
    grad = 0.5 * np.degrees(np.arctan2(2 * jxy, jxx - jyy))
    a = (grad + 90.0) % 180.0
    return float(a if a <= 90 else a - 180), float(np.hypot(jxx - jyy, 2 * jxy) / (jxx + jyy))


def main(prod):
    G = GEOM[prod]
    D = prod + "/"
    gates = {}
    rep = json.load(open(out_path(D + "report.json")))
    cpath, bpath = out_path(D + "Color.png"), out_path(D + "Bump16.png")
    ci, bi = ihdr(cpath), ihdr(bpath)
    gates["ihdr"] = {"colour": ci, "bump": bi,
                     "pass": bool(ci["bit_depth"] == 8 and ci["colour_type"] == 2 and bi["bit_depth"] == 16
                                  and bi["colour_type"] == 0 and (ci["w"], ci["h"]) == (bi["w"], bi["h"]))}
    W, H = ci["w"], ci["h"]
    ppi = G["ppi"]
    (mw_in, mh_in), (nc, nr) = G["mod"], G["n"]
    exp_w, exp_h = nc * mw_in, nr * mh_in
    w_in, h_in = W / ppi, H / ppi
    gates["aspect"] = {"pixels": [W, H], "ppi": ppi, "sample_size_in": [w_in, h_in], "expected_in": [exp_w, exp_h],
                       "report_sample_size_in": rep["sample_size_in"], "pixel_aspect": W / H, "physical_aspect": exp_w / exp_h,
                       "pass": bool(abs(w_in - exp_w) < 1e-9 and abs(h_in - exp_h) < 1e-9 and rep["ppi"] == ppi
                                    and abs(W / H - exp_w / exp_h) < 1e-12
                                    and abs(rep["sample_size_in"][0] - w_in) < 1e-9 and abs(rep["sample_size_in"][1] - h_in) < 1e-9)}
    selftest = (not is_quarter(142.107)) and (not is_quarter(142.482)) and is_quarter(142.5) and is_quarter(48.0)
    gates["quarter_inch"] = {"sample_size_in": [w_in, h_in], "feet_inches": [ftin(w_in), ftin(h_in)],
                             "selftest_non_quarter_rejected": bool(selftest),
                             "pass": bool(is_quarter(w_in) and is_quarter(h_in) and selftest)}

    c = np.asarray(Image.open(cpath).convert("RGB")).astype(np.float64)
    b = np.asarray(Image.open(bpath)).astype(np.float64)
    full = rep["relief_mm"]["full_scale"]
    h = b / 65535.0 * full
    h_edge = G["face_mm"] - G["edge_mm"]
    g = 1 - np.clip(h / h_edge, 0, 1)             # joint coverage (1 = grout)
    mw, mh, jpx = mw_in * ppi, mh_in * ppi, G["joint"] * ppi

    # joints. Centres: from the bump's joint coverage g (symmetric, so sub-pixel exact). Widths: from the
    # colour map, because an eased-edge pixel that is partly joint has a bump height that mixes coverage and
    # edge drop; the colour is a plain alpha blend of face and grout. For every joint segment (one tile
    # edge) the luminance profile across the joint is averaged along it (texture averages out), then
    # coverage = (face level - P) / (face level - grout level), width = sum of coverage.
    L = (srgb_to_lin(c) @ LUMA)
    gl = float(srgb_to_lin(np.array(G["grout"], float)) @ LUMA)
    half = int(np.ceil(jpx / 2)) + 6

    def joint_profile(img, centre, lo, hi, axis):
        n = img.shape[1] if axis == 0 else img.shape[0]
        idx = (np.floor(centre) + np.arange(-half, half + 1)).astype(int)
        if axis == 0:
            P = img[lo:hi][:, idx % n].mean(0)
        else:
            P = img[idx % n][:, lo:hi].mean(1)
        return idx, P

    def width_centre(idx, P, gcov):
        # face level taken separately on each side (neighbouring tiles differ in tone)
        m = len(P) // 2
        fl = np.where(np.arange(len(P)) < m, P[:3].mean(), P[-3:].mean())
        cov = np.clip((fl - P) / (fl - gl), 0, 1)
        wd = float(cov[2:-2].sum())
        cen = float((gcov * (idx + 0.5)).sum() / gcov.sum())
        return wd, cen
    def fit_width(hprof, idx, centre):
        """Least-squares joint width (px) of an along-line mean bump profile, using the restated eased-edge
        section: h = alpha * max(FACE - drop(d), 0), alpha = clip(d + 0.5, 0, 1) (px), quarter-round drop."""
        t = (idx + 0.5) - centre
        best = (np.inf, None)
        for j in np.arange(0.5 * jpx, 1.5 * jpx + 1e-9, 0.01):
            dpx = np.abs(t) - j / 2
            al = np.clip(dpx + 0.5, 0, 1)
            q = np.clip(dpx / ppi * MM / G["edge_mm"], 0, 1)
            drop = G["edge_mm"] * (1 - np.sqrt(1 - (1 - q) ** 2))
            mdl = al * np.maximum(G["face_mm"] - drop, 0)
            e = float(((mdl - hprof) ** 2).sum())
            if e < best[0]:
                best = (e, float(j))
        return best[1]

    # one width per joint LINE (all its segments averaged: single chips/tiles differ in tone), one centre
    # error per segment
    ev, eh, colw, roww, colb, rowb = [], [], [], [], [], []
    for k in range(nc):
        xc = k * mw
        Ps, Gs, Hs = [], [], []
        for r in range(nr):
            lo, hi = int(r * mh + half + 2), int((r + 1) * mh - half - 2)
            idx, P = joint_profile(L, xc, lo, hi, 0)
            _, gp = joint_profile(g, xc, lo, hi, 0)
            Hs.append(joint_profile(h, xc, lo, hi, 0)[1])
            Ps.append(P)
            Gs.append(gp)
            ev.append(((width_centre(idx, P, gp)[1] - xc + W / 2) % W) - W / 2)
        colw.append(width_centre(idx, np.mean(Ps, 0), np.mean(Gs, 0))[0])
        colb.append(fit_width(np.mean(Hs, 0), idx, xc - np.floor(xc) + np.floor(xc)))
    for k in range(nr):
        yc = k * mh
        Ps, Gs, Hs = [], [], []
        for cc in range(nc):
            lo, hi = int(cc * mw + half + 2), int((cc + 1) * mw - half - 2)
            idx, P = joint_profile(L, yc, lo, hi, 1)
            _, gp = joint_profile(g, yc, lo, hi, 1)
            Hs.append(joint_profile(h, yc, lo, hi, 1)[1])
            Ps.append(P)
            Gs.append(gp)
            eh.append(((width_centre(idx, P, gp)[1] - yc + H / 2) % H) - H / 2)
        roww.append(width_centre(idx, np.mean(Ps, 0), np.mean(Gs, 0))[0])
        rowb.append(fit_width(np.mean(Hs, 0), idx, yc))
    ev, eh, colw, roww, colb, rowb = map(np.array, (ev, eh, colw, roww, colb, rowb))
    wv_all, wh_all = colw, roww
    tol_c = 0.25 * jpx                     # colour-profile width: sanity check only (low-contrast grout)
    gates["joints"] = {"expected_width_px": jpx,
                       "method": "centre from bump coverage; width by least-squares fit of the restated eased-edge section to each joint line's mean bump profile; colour-profile width as a sanity check",
                       "max_centre_err_px": [float(np.abs(ev).max()), float(np.abs(eh).max())],
                       "bump_fit_width_px_vertical_lines": [float(x) for x in colb],
                       "bump_fit_width_px_horizontal_lines_min_max": [float(rowb.min()), float(rowb.max())],
                       "colour_width_px_vertical_mean_sd": [float(colw.mean()), float(colw.std())],
                       "colour_width_px_horizontal_mean_sd": [float(roww.mean()), float(roww.std())],
                       "pass": bool(np.abs(ev).max() <= 0.5 and np.abs(eh).max() <= 0.5
                                    and np.abs(colb - jpx).max() <= 0.1 and np.abs(rowb - jpx).max() <= 0.1
                                    and abs(colw.mean() - jpx) < tol_c and abs(roww.mean() - jpx) < tol_c)}

    # wrap: the k = 0 joints above were measured ACROSS the image edges (indices modulo W / H), so their
    # widths are the left+right and top+bottom half joints added together.
    edge = {"left": g[:, 0], "right": g[:, -1], "top": g[0], "bottom": g[-1]}
    share = {k: float((v > 0.9).mean()) for k, v in edge.items()}
    half_lr, half_tb = float(colb[0]), float(rowb[0])
    ix = [int(k * mw) for k in range(1, nc)]
    step_edge = float(np.abs(L[:, 0] - L[:, -1]).mean())
    step_int = float(np.mean([np.abs(L[:, x] - L[:, x - 1]).mean() for x in ix]))
    stepb_edge = float(np.abs(h[:, 0] - h[:, -1]).mean())
    stepb_int = float(np.mean([np.abs(h[:, x] - h[:, x - 1]).mean() for x in ix]))
    interior_w = float(np.mean(np.r_[colb[1:], rowb[1:]]))
    gates["wrap"] = {"edge_grout_share": share, "left_plus_right_half_joints_px": half_lr,
                     "top_plus_bottom_half_joints_px": half_tb, "interior_joint_width_px": interior_w,
                     "colour_lum_step_wrap_vs_interior_joint": [step_edge, step_int],
                     "bump_mm_step_wrap_vs_interior_joint": [stepb_edge, stepb_int],
                     "pass": bool(min(share.values()) == 1.0 and abs(half_lr - interior_w) <= 0.1 and abs(half_tb - interior_w) <= 0.1
                                  and step_edge <= 1.5 * step_int + 1e-4 and stepb_edge <= 1.5 * stepb_int + 1e-6)}

    # face extraction helper
    def face(r, cc, inset_px):
        x0 = int(np.ceil(cc * mw + jpx / 2)) + inset_px
        y0 = int(np.ceil(r * mh + jpx / 2)) + inset_px
        x1 = int(np.floor((cc + 1) * mw - jpx / 2)) - inset_px
        y1 = int(np.floor((r + 1) * mh - jpx / 2)) - inset_px
        return L[y0:y1, x0:x1], (x0, y0, x1, y1)

    # distinct
    if prod == "veincut_24x48":
        F = []
        for r in range(nr):
            for cc in range(nc):
                f, _ = face(r, cc, 6)
                f = zoom(f, 0.25, order=1)
                F.append(gaussian_filter(f, 0.8) - gaussian_filter(f, 4.0))
        n = len(F)
        same = np.zeros((n, n))
        anyo = np.zeros((n, n))
        for i in range(n):
            hh, ww = F[i].shape
            t = F[i][int(hh * .2):int(hh * .8), int(ww * .2):int(ww * .8)]
            for j in range(n):
                if i == j:
                    continue
                same[i, j] = ncc_map(F[j], t).max()
                anyo[i, j] = max(ncc_map(F[j], tt).max() for tt in (t, t[::-1, ::-1], t[:, ::-1], t[::-1]))
        # clusters of the same real face
        lab = list(range(n))
        for i in range(n):
            for j in range(n):
                if max(anyo[i, j], anyo[j, i]) > 0.6:
                    a, bb = lab[i], lab[j]
                    lab = [a if x == bb else x for x in lab]
        clusters = sorted(set(lab))
        touching = []
        for i in range(n):
            r, cc = divmod(i, nc)
            for dr, dc in itertools.product((-1, 0, 1), repeat=2):
                if dr == dc == 0:
                    continue
                j = ((r + dr) % nr) * nc + (cc + dc) % nc
                if lab[i] == lab[j]:
                    touching.append((i, j))
        # cross-check against the build plan (not trusted, compared)
        plan = [cell["face"] for row in rep["cells"] for cell in row]
        plan_consistent = all((plan[i] == plan[j]) == (lab[i] == lab[j]) for i in range(n) for j in range(n))
        # A / W shared-corner disclosure: best NCC between different-face cells
        diff = [max(anyo[i, j], anyo[j, i]) for i in range(n) for j in range(n) if i < j and lab[i] != lab[j]]
        gates["distinct"] = {"cells": n, "max_same_orientation_ncc": float(same.max()),
                             "real_face_clusters": len(clusters), "cells_per_cluster": sorted([lab.count(k) for k in clusters]),
                             "same_face_touching_pairs": touching, "plan_matches_measured_clusters": bool(plan_consistent),
                             "max_ncc_between_different_faces": float(max(diff)),
                             "note": "each real face appears 3 times in different flips; see README limitation",
                             "pass": bool(same.max() < 0.5 and len(clusters) == 6 and not touching and plan_consistent)}
    else:
        s = 16.0 / ppi
        chips = []
        for r in range(nr):
            for cc in range(nc):
                f, _ = face(r, cc, 2)
                f = zoom(f, s, order=1)
                chips.append(gaussian_filter(f, 0.6) - gaussian_filter(f, 2.5))
        A = np.stack(chips)                               # n x h x w
        n, hh, ww = A.shape
        tin = A[:, 1:hh - 1, 1:ww - 1]

        def norm(M):
            M = M.reshape(len(M), -1)
            M = M - M.mean(1, keepdims=True)
            return M / np.linalg.norm(M, axis=1, keepdims=True)
        best = np.full((n, n), -1.0)
        for o in range(4):
            T = [tin, tin[:, ::-1, ::-1], tin[:, :, ::-1], tin[:, ::-1, :]][o]
            Tn = norm(np.ascontiguousarray(T))
            for dy in (0, 1, 2):
                for dx in (0, 1, 2):
                    C = norm(np.ascontiguousarray(A[:, dy:dy + hh - 2, dx:dx + ww - 2]))
                    best = np.maximum(best, Tn @ C.T)
        np.fill_diagonal(best, -1)
        # crop-window overlap (from report.json)
        ov = 0
        cr = rep["chips"]
        for i in range(len(cr)):
            for j in range(i + 1, len(cr)):
                a, bb = cr[i], cr[j]
                if a["source"] != bb["source"]:
                    continue
                if (a["x0"] < bb["x0"] + bb["w"] and bb["x0"] < a["x0"] + a["w"]
                        and a["y0"] < bb["y0"] + bb["h"] and bb["y0"] < a["y0"] + a["h"]):
                    ov += 1
        pos = {(x["row"], x["col"]) for x in cr}
        gates["distinct"] = {"chips": n, "max_pair_ncc": float(best.max()), "p99_pair_ncc": float(np.percentile(best[best > -1], 99)),
                             "median_pair_ncc": float(np.median(best[best > -1])), "report_window_overlaps": ov,
                             "report_chips_cover_grid": bool(len(pos) == n),
                             "chips_per_source": rep["chips_per_source"],
                             "pass": bool(best.max() < 0.6 and ov == 0 and len(pos) == n)}

    # veins
    angs = []
    if prod == "veincut_24x48":
        for r in range(nr):
            for cc in range(nc):
                f, _ = face(r, cc, 20)
                angs.append(vein_angle(zoom(f, 0.25, order=1)))
    else:
        blk = int(12 * ppi)
        for y0 in range(0, H, blk):
            for x0 in range(0, W, blk):
                sub = L[y0:y0 + blk, x0:x0 + blk].copy()
                gm = g[y0:y0 + blk, x0:x0 + blk] > 0.05
                sub[gm] = np.median(sub[~gm])            # neutralise joints (they would dominate)
                angs.append(vein_angle(sub))
    a = np.array([x[0] for x in angs])
    gates["veins"] = {"angles_deg": [round(float(x), 2) for x in a], "coherence": [round(x[1], 3) for x in angs],
                      "max_abs_deg": float(np.abs(a).max()), "pass": bool(np.abs(a).max() < 10)}

    # clearance
    yy = np.arange(H) + 0.5
    xx = np.arange(W) + 0.5
    dv = np.abs(((yy + mh / 2) % mh) - mh / 2)[:, None]
    du = np.abs(((xx + mw / 2) % mw) - mw / 2)[None, :]
    dist_px = np.minimum(du, dv) - jpx / 2
    face_px = dist_px >= (G["edge_mm"] / MM * ppi + 1)
    core = dist_px <= -0.75
    fmin = float(h[face_px].min())
    gates["clearance"] = {"face_min_mm": fmin, "face_max_mm": float(h[face_px].max()), "face_median_mm": float(np.median(h[face_px])),
                          "face_relief_sd_mm": float(h[face_px].std()), "grout_core_max_mm": float(h[core].max()),
                          "joint_depth_mm": G["face_mm"], "full_scale_mm": full, "clearance_face_above_grout_mm": fmin,
                          "pass": bool(fmin > 0.5 * G["face_mm"] and h[core].max() == 0.0 and h.max() <= full + 1e-9)}
    gs = np.array(G["grout"], float)
    dcol = np.sqrt(((c[core] - gs) ** 2).sum(1))
    u09 = np.asarray(Image.open(out_path("references/user_supplied/u09_flat_veincut_swatch.webp")).convert("RGB")).astype(np.float64)
    m_ref = srgb_to_lin(u09).reshape(-1, 3).mean(0)
    m_face = srgb_to_lin(c[face_px]).mean(0)
    rel = m_face / m_ref - 1
    gates["colour_bump"] = {"grout_core_px": int(core.sum()), "share_within_12_of_grout": float((dcol < 12).mean()),
                            "face_mean_lin_vs_u09_rel": [float(x) for x in rel],
                            "face_mean_srgb": [float(x) for x in c[face_px].mean(0)],
                            "pass": bool((dcol < 12).mean() > 0.99 and np.abs(rel).max() < 0.04)}

    import e01_model_pattern as e01
    mp = e01.check(prod)
    mpj = json.load(open(out_path(D + "model_pattern_check.json")))
    gates["model_pattern"] = {"file": mpj["file"], "horizontal": mpj["horizontal"], "vertical": mpj["vertical"],
                              "header_ok": mpj["header_ok"], "pass": bool(mp)}

    allpass = all(v["pass"] for v in gates.values())
    out = {"product": prod, "all_pass": allpass, "gates": gates,
           "revit_sample_size": {"width_in": w_in, "height_in": h_in, "width": ftin(w_in), "height": ftin(h_in)},
           "revit_bump_amount_editor": rep["revit_bump_amount_editor"]}
    json.dump(out, open(out_path(D + "validation.json"), "w"), indent=1)
    for k, v in gates.items():
        print("%-14s %s" % (k, "PASS" if v["pass"] else "FAIL"))
    print("ALL PASS" if allpass else "FAILED")
    sys.exit(0 if allpass else 1)


if __name__ == "__main__":
    main(sys.argv[1])
