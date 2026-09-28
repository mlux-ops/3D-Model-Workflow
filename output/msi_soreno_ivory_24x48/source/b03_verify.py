"""Independent verifier for the MSI Soreno Ivory 24x48 maps and model pattern.

Re-reads textures/Color.png, textures/Bump16.png and the .pat from disk and re-derives every gate from
the geometry (it does not import the builder). Writes textures/validation.json; exits 1 on any failure.

Gates
  ihdr            colour 8-bit RGB (type 2), bump 16-bit grey (type 0), same W x H (IHDR bytes, not a library)
  aspect          W/H in pixels == Sample Size W/H exactly; W, H == atlas modules x PPI
  quarter_inch    both Sample Size numbers exact multiples of 0.25 in
  joint_width     effective joint width sum(1 - alpha) on scan lines across every joint, alpha = h / h_edge
  offset_1_3      measured vertical-joint centres per row vs r * module / 3 (and 3 joints per row)
  wrap            edge step / interior step for colour luminance and bump, both axes
  distinct_faces  max NCC between the 18 built tile faces (band-passed, translation search, 4 orientations)
  clearance       tile face (outside the eased edge) stays above the grout floor; grout floor is 0
  colour_bump     grout-core pixels (h == 0) carry the grout colour
  model_pattern   e01 analytic check of both .pat patterns (re-parsed from disk)
"""
import json
import math
import struct
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
from scipy.signal import fftconvolve

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
MM = 25.4
# geometry restated independently (must agree with report.json; checked below)
PPI = 24
TILE_W, TILE_H, JOINT = 47.0 + 5.0 / 24.0, 23.625, 0.125
COLS, ROWS = 3, 6
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT
OFF = MOD_W / 3


def ihdr(path):
    b = open(path, "rb").read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR", path
    w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", b[16:29])
    return {"w": w, "h": h, "bit_depth": depth, "colour_type": ctype, "interlace": inter}


def ncc_max(img, tpl):
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum())
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    o = np.ones_like(t)
    s1 = fftconvolve(img, o, mode="valid")
    s2 = fftconvolve(img * img, o, mode="valid")
    return float((num / (np.sqrt(np.maximum(s2 - s1 * s1 / t.size, 1e-9)) * tn)).max())


def main():
    gates = {}
    rep = json.load(open(out_path("textures/report.json")))
    cpath, bpath = out_path("textures/Color.png"), out_path("textures/Bump16.png")
    ci, bi = ihdr(cpath), ihdr(bpath)
    gates["ihdr"] = {"colour": ci, "bump": bi,
                     "pass": ci["bit_depth"] == 8 and ci["colour_type"] == 2 and bi["bit_depth"] == 16
                     and bi["colour_type"] == 0 and (ci["w"], ci["h"]) == (bi["w"], bi["h"])}
    W, H = ci["w"], ci["h"]
    w_in, h_in = W / PPI, H / PPI
    gates["aspect"] = {"pixels": [W, H], "sample_size_in": [w_in, h_in],
                       "expected_in": [COLS * MOD_W, ROWS * MOD_H], "report_sample_size_in": rep["sample_size_in"],
                       "pixel_aspect": W / H, "physical_aspect": (COLS * MOD_W) / (ROWS * MOD_H),
                       "pass": (abs(w_in - COLS * MOD_W) < 1e-9 and abs(h_in - ROWS * MOD_H) < 1e-9
                                and abs(W / H - (COLS * MOD_W) / (ROWS * MOD_H)) < 1e-12)}
    gates["aspect"]["pass"] = bool(gates["aspect"]["pass"] and abs(rep["sample_size_in"][0] - w_in) < 1e-9
                                   and abs(rep["sample_size_in"][1] - h_in) < 1e-9)

    def q(x):
        return abs(x * 4 - round(x * 4)) < 1e-9

    def ftin(x):
        return "%d'-%.3fin" % (int(x // 12), x - 12 * int(x // 12))
    gates["quarter_inch"] = {"sample_size_in": [w_in, h_in], "feet_inches": [ftin(w_in), ftin(h_in)],
                             "pass": bool(q(w_in) and q(h_in))}

    c = np.asarray(Image.open(cpath).convert("RGB")).astype(np.float64)
    b = np.asarray(Image.open(bpath)).astype(np.float64)
    full = rep["relief_mm"]["full_scale"]
    h = b / 65535.0 * full
    h_edge = rep["relief_mm"]["height_at_tile_edge_design"]
    ratio = np.clip(h / h_edge, 0, 1)             # = alpha (tile coverage) in and next to the joint
    g = 1 - ratio

    mw, mh, off = MOD_W * PPI, MOD_H * PPI, OFF * PPI
    jpx = JOINT * PPI
    # horizontal joints: centres at y = k * mh (k = 0 .. ROWS-1, k = 0 is the wrapped top/bottom edge)
    widths_h, widths_v, cen_err, per_row = [], [], [], []
    xs = np.linspace(5, W - 6, 240).astype(int)
    for k in range(ROWS):
        yc = k * mh
        rows_idx = (np.floor(yc) + np.arange(-6, 7)).astype(int) % H
        for x in xs:
            # skip columns within 10 px of a vertical joint in the rows above/below
            near = False
            for r in ((k - 1) % ROWS, k % ROWS):
                xv = (r * off) % mw
                dx = ((x + 0.5 - xv + mw / 2) % mw) - mw / 2
                if abs(dx) < 10:
                    near = True
            if near:
                continue
            widths_h.append(g[rows_idx, x].sum())
    for r in range(ROWS):
        ys = np.linspace(r * mh + 12, (r + 1) * mh - 12, 30).astype(int)
        for y in ys:
            gl = g[y]
            e = np.flatnonzero(np.diff((gl > 0.5).astype(np.int8)))
            runs = int(((gl > 0.5).astype(np.int8)[e + 1] == 1).sum()) + (1 if gl[0] > 0.5 and gl[-1] <= 0.5 else 0)
            per_row.append((r, runs))
            for kk in range(COLS):
                xc = (r * off + kk * mw) % W
                idx = (np.floor(xc) + np.arange(-6, 7)).astype(int)
                wv = g[y, idx % W]
                widths_v.append(wv.sum())
                cen = (wv * (idx + 0.5)).sum() / wv.sum()
                d = ((cen - xc + W / 2) % W) - W / 2
                cen_err.append(d)
    widths_h, widths_v, cen_err = np.array(widths_h), np.array(widths_v), np.array(cen_err)
    run_counts = sorted(set(n for _, n in per_row))
    gates["joint_width"] = {
        "expected_px": jpx, "expected_in": JOINT,
        "horizontal": {"n": int(len(widths_h)), "mean_px": float(widths_h.mean()), "min_px": float(widths_h.min()),
                       "max_px": float(widths_h.max())},
        "vertical": {"n": int(len(widths_v)), "mean_px": float(widths_v.mean()), "min_px": float(widths_v.min()),
                     "max_px": float(widths_v.max())},
        "pass": bool(abs(widths_h.mean() - jpx) < 0.15 and abs(widths_v.mean() - jpx) < 0.15
                     and np.abs(widths_h - jpx).max() < 0.4 and np.abs(widths_v - jpx).max() < 0.4)}
    # 1/3 offset: per-row mean measured centre relative to row 0
    rowc = cen_err.reshape(ROWS, 30, COLS)
    meas_off = []
    for r in range(ROWS):
        meas_off.append(float(r * off + rowc[r].mean()))
    gates["offset_1_3"] = {"expected_row_offsets_px": [float(r * off % mw) for r in range(ROWS)],
                           "measured_row_offsets_px": [float(v % mw) for v in meas_off],
                           "max_abs_centre_error_px": float(np.abs(cen_err).max()),
                           "grout_runs_per_scan_row": run_counts,
                           "pass": bool(np.abs(cen_err).max() <= 0.5 and run_counts == [COLS])}

    L = c @ np.array([0.2126, 0.7152, 0.0722])
    wrap = {}
    ok = True
    # x wrap: only rows whose left/right image edge falls inside a tile face (rows 1, 2, 4, 5), and only
    # interior columns that are not near a joint, so the edge step is compared like with like.
    yy_all = np.arange(H) + 0.5
    rr = np.minimum((yy_all // mh).astype(int), ROWS - 1)
    dv_all = np.abs(((yy_all + mh / 2) % mh) - mh / 2)
    rows_x = np.flatnonzero((rr % 3 != 0) & (dv_all > 8))
    xx_all = np.arange(W - 1) + 1.0                      # step between column x-1 and x sits at x
    for name, A in (("colour_lum", L), ("bump_mm", h)):
        ex = np.abs(A[rows_x, 0] - A[rows_x, -1]).mean()
        steps = []
        for r in (1, 2, 4, 5):
            sel = rows_x[rr[rows_x] == r]
            dxj = np.abs(((xx_all - r * off + mw / 2) % mw) - mw / 2)
            cols = np.flatnonzero(dxj > 8) + 1
            steps.append(np.abs(A[np.ix_(sel, cols)] - A[np.ix_(sel, cols - 1)]).mean())
        ix = float(np.mean(steps))
        ey = np.abs(A[0] - A[-1]).mean()
        wrap[name] = {"edge_step_x_face_rows": float(ex), "interior_step_x_face_rows": ix, "ratio_x": float(ex / ix),
                      "edge_step_y": float(ey),
                      "note_y": "top and bottom image rows are both inside the half-joints (structural check below)"}
        ok = ok and ex / ix < 1.3
    # the joint structure itself must continue across the wrap: row-0 rows are grout at x = 0 and x = W-1
    rows0 = np.arange(12, int(mh) - 12)
    wrap["row0_edge_columns_grout_share"] = float(((g[rows0, 0] > 0.9) & (g[rows0, -1] > 0.9)).mean())
    wrap["top_bottom_rows_grout_share"] = float(((g[0] > 0.9) & (g[-1] > 0.9)).mean())
    ok = ok and wrap["row0_edge_columns_grout_share"] == 1.0 and wrap["top_bottom_rows_grout_share"] > 0.99
    wrap["pass"] = bool(ok)
    gates["wrap"] = wrap

    # distinct faces
    faces = []
    inset = 8
    fw, fh = int(TILE_W * PPI) - 2 * inset, int(TILE_H * PPI) - 2 * inset
    for r in range(ROWS):
        for k in range(COLS):
            x0 = int(round(r * off + k * mw + jpx / 2)) + inset
            y0 = int(round(r * mh + jpx / 2)) + inset
            xi = (x0 + np.arange(fw)) % W
            yi = y0 + np.arange(fh)
            f = L[np.ix_(yi, xi)]
            f = zoom(f, 0.5, order=1)
            faces.append(gaussian_filter(f, 1.0) - gaussian_filter(f, 6.0))
    worst = (-1, None)
    pairs = []
    for i in range(len(faces)):
        hh, ww = faces[i].shape
        t = faces[i][int(hh * .2):int(hh * .8), int(ww * .2):int(ww * .8)]
        for j in range(len(faces)):
            if j == i:
                continue
            v = max(ncc_max(faces[j], tt) for tt in (t, t[::-1, ::-1], t[:, ::-1], t[::-1]))
            pairs.append(v)
            if v > worst[0]:
                worst = (v, (i, j))
    # the two source faces at the same 12 px/in scale, as a reference (not gated)
    src = []
    mppi = rep["sources"]["master_ppi"]
    for k in ("A", "B"):
        m = np.load(out_path("_work/master_%s.npy" % k)) @ np.array([0.2126, 0.7152, 0.0722])
        m = zoom(m, 12.0 / mppi, order=1)
        src.append(gaussian_filter(m, 1.0) - gaussian_filter(m, 6.0))
    vs_src = []
    for i, f in enumerate(faces):
        hh, ww = f.shape
        t = f[int(hh * .2):int(hh * .8), int(ww * .2):int(ww * .8)]
        best = 0
        for S in src:
            for tt in (t, t[::-1, ::-1], t[:, ::-1], t[::-1]):
                if S.shape[0] >= tt.shape[0] and S.shape[1] >= tt.shape[1]:
                    best = max(best, ncc_max(S, tt))
        vs_src.append(best)
    gates["distinct_faces"] = {"n_faces": len(faces), "threshold": 0.5, "max_ncc_face_vs_face": worst[0],
                               "worst_pair_tile_ids": list(worst[1]), "median_ncc": float(np.median(pairs)),
                               "max_ncc_face_vs_source_A_B": float(max(vs_src)),
                               "method": "luminance at 12 px/in, DoG(1,6) band-pass, central 60 % template slid over the other face, r0/r180/flipH/flipV",
                               "pass": bool(worst[0] < 0.5)}

    # clearance: pixels whose distance to every joint centreline exceeds half joint + edge radius + 1 px
    tile_id = np.load(out_path("_work/tile_id.npy"))
    yy = (np.arange(H) + 0.5)
    dv = np.abs(((yy + mh / 2) % mh) - mh / 2)[:, None]
    row = np.minimum((yy // mh).astype(int), ROWS - 1)
    xx = (np.arange(W) + 0.5)[None, :]
    du = np.abs(((xx - row[:, None] * off + mw / 2) % mw) - mw / 2)
    dist_px = np.minimum(du, dv) - jpx / 2
    face_px = dist_px >= (rep["relief_mm"]["edge_radius"] / MM * PPI + 1)
    core = dist_px <= -1.0
    fmin = float(h[face_px].min())
    gates["clearance"] = {"face_min_mm": fmin, "face_max_mm": float(h[face_px].max()),
                          "face_median_mm": float(np.median(h[face_px])), "grout_core_max_mm": float(h[core].max()),
                          "full_scale_mm": full, "joint_step_mm": rep["relief_mm"]["face_design"],
                          "tile_ids_seen": int(len(np.unique(tile_id))),
                          "pass": bool(fmin > 1.0 and h[core].max() == 0.0 and abs(h.max() - full) < 1e-6)}
    gs = np.array(rep["colour"]["grout_srgb"])
    dcol = np.sqrt(((c[core] - gs) ** 2).sum(1))
    gates["colour_bump"] = {"grout_core_px": int(core.sum()), "share_within_12_of_grout": float((dcol < 12).mean()),
                            "face_px_near_grout_colour_share": float((np.sqrt(((c[face_px][::50] - gs) ** 2).sum(1)) < 6).mean()),
                            "pass": bool((dcol < 12).mean() > 0.99)}

    import e01_model_pattern as e01
    mp = e01.check()
    mpj = json.load(open(out_path("textures/model_pattern_check.json")))
    gates["model_pattern"] = {"horizontal": mpj["horizontal"], "vertical": mpj["vertical"], "pass": bool(mp)}

    allpass = all(v["pass"] for v in gates.values())
    out = {"all_pass": allpass, "gates": gates,
           "revit_sample_size": {"width_in": w_in, "height_in": h_in, "width": ftin(w_in), "height": ftin(h_in)}}
    json.dump(out, open(out_path("textures/validation.json"), "w"), indent=1)
    for k, v in gates.items():
        print("%-15s %s" % (k, "PASS" if v["pass"] else "FAIL"))
    print("ALL PASS" if allpass else "FAILED")
    sys.exit(0 if allpass else 1)


if __name__ == "__main__":
    main()
