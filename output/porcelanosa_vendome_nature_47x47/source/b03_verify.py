"""Independent verifier for the Porcelanosa Vendome Nature 47x47 maps and model pattern.

Re-reads every PNG and the .pat from disk and re-derives every gate from the geometry restated below. It does not
import the builder; the source faces are decoded here with LittleCMS (Pillow ImageCms, Adobe RGB -> sRGB), a
different path from the builder's float matrix decode. Writes <set>/validation.json; exits 1 on any failure.
Usage: python b03_verify.py [designed|free_mix|pieces|all]

Gates
  ihdr           colour 8-bit RGB (type 2), bump 16-bit grey (type 0), same W x H (IHDR bytes), non-interlaced
  quarter_inch   W, H = tiles x 1512 px at 32 px/in; Sample Size exact quarter-inch multiples (self-test: 47.3066,
                 189.2264 and 94.61 must fail); pixel aspect == physical aspect
  joints         bump == 0 exactly on, and only on, the 2 px joints centred on k x 47.25 in, both directions
  wrap           all four edges are 1 px half joints (left + right = top + bottom = one 2 px joint); colour and
                 bump steps across the wrap no larger than across interior joints
  identity       every cell's face, downsampled to the source's 1417 px, matches its declared source piece and
                 90-degree rotation (NCC > 0.97, mean |dRGB| < 3 levels vs the LittleCMS decode) and no other of
                 the 32 rotation variants (margin > 0.5); mirrored variants score lower than the declared one
  continuity     designed: vein continuity across all 8 designed vertical joints (incl. the 2 wrap joints), band-
                 passed 3 px strip NCC in the built map >= 0.40 and >= source value - 0.10; horizontal joints
                 reported (no designed continuity expected)
  adjacency      free_mix: each piece exactly twice, copies in different rotations, no piece touches a copy of
                 itself (8-neighbourhood, wrapped), no mirrored placement
  clearance      tile face above the grout floor (min > 0.5 x face design), grout == 0, max <= full scale
  colour_bump    joint pixels carry exactly the grout sRGB; face mean within 2 % (linear) of the source faces'
  cross_set      the same piece's face pixels are identical in every set (pieces r0 == designed r0 cells, free-mix
                 cells == rotated piece map), colour and bump; pieces: the 8 piece bumps are all different
  model_pattern  e01 analytic check (re-parsed .pat vs bump joints, all three sets)
  grout_variant  if a Color_<suffix>.png exists: identical to Color.png on every face pixel, grout only differs
"""
import glob
import io
import itertools
import json
import os
import sys

import numpy as np
from PIL import Image, ImageCms
from scipy.ndimage import gaussian_filter1d

from common import LUMA, ftin, ihdr, srgb_to_lin
from guard import out_path, ref

Image.MAX_IMAGE_PIXELS = None
PPI, MPX, JPX, FPX, MOD = 32, 1512, 2, 1510, 47.25
FACE_MM, FULL_MM = 1.5, 1.6
GROUT = (200, 199, 195)
SETS = {"designed": (4, 2), "free_mix": (4, 4), "pieces": (1, 1)}
STRIPS = [[1, 6, 7, 8], [2, 3, 4, 5]]


def is_quarter(x):
    return abs(x * 4 - round(x * 4)) < 1e-9


def src_srgb(k):
    im = Image.open(ref("100348304_%03d.jpg" % k))
    prof = ImageCms.ImageCmsProfile(io.BytesIO(im.info["icc_profile"]))
    return np.asarray(ImageCms.profileToProfile(im, prof, ImageCms.createProfile("sRGB"), outputMode="RGB")).astype(np.float64)


def rotcw(a, deg):
    return np.rot90(a, -deg // 90)


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-18))


def bp(p, s=1.0):
    return gaussian_filter1d(p, 1.2 * s) - gaussian_filter1d(p, 25 * s)


def down(face):
    return np.asarray(Image.fromarray(np.clip(np.round(face), 0, 255).astype(np.uint8)).resize((1417, 1417), Image.LANCZOS)).astype(np.float64)


SRC = None


def sources():
    global SRC
    if SRC is None:
        SRC = {k: src_srgb(k) for k in range(1, 9)}
    return SRC


def files_for(s):
    if s == "pieces":
        return [(out_path("pieces/Piece_%d_Color.png" % k), out_path("pieces/Piece_%d_Bump16.png" % k), [[{"piece": k, "rot_cw_deg": 0}]])
                for k in range(1, 9)]
    rep = json.load(open(out_path(s + "/report.json")))
    return [(out_path(s + "/Color.png"), out_path(s + "/Bump16.png"), rep["cells"])]


def verify_map(s, cpath, bpath, cells, nc, nr):
    g = {}
    ci, bi = ihdr(cpath), ihdr(bpath)
    g["ihdr"] = {"colour": ci, "bump": bi, "pass": bool(ci["bit_depth"] == 8 and ci["colour_type"] == 2 and bi["bit_depth"] == 16
                                                       and bi["colour_type"] == 0 and (ci["w"], ci["h"]) == (bi["w"], bi["h"])
                                                       and ci["interlace"] == 0 and bi["interlace"] == 0)}
    W, H = ci["w"], ci["h"]
    w_in, h_in = W / PPI, H / PPI
    selftest = not is_quarter(47.3066) and not is_quarter(189.2264) and not is_quarter(94.61) and is_quarter(189.0) and is_quarter(94.5)
    g["quarter_inch"] = {"pixels": [W, H], "sample_size_in": [w_in, h_in], "feet_inches": [ftin(w_in), ftin(h_in)],
                         "expected_in": [nc * MOD, nr * MOD], "selftest_non_quarter_rejected": bool(selftest),
                         "pass": bool(W == nc * MPX and H == nr * MPX and is_quarter(w_in) and is_quarter(h_in) and selftest
                                      and abs(W / H - (nc * MOD) / (nr * MOD)) < 1e-12)}
    c = np.asarray(Image.open(cpath).convert("RGB")).astype(np.float64)
    b = np.asarray(Image.open(bpath)).astype(np.int64)
    h = b / 65535.0 * FULL_MM
    xs, ys = np.arange(W), np.arange(H)
    jx = ((xs % MPX) == 0) | ((xs % MPX) == MPX - 1)
    jy = ((ys % MPX) == 0) | ((ys % MPX) == MPX - 1)
    jmask = jx[None, :] | jy[:, None]
    zero = b == 0
    col_zero = np.flatnonzero(zero.all(0))
    row_zero = np.flatnonzero(zero.all(1))
    centres_x = [(float(col_zero[i]) + float(col_zero[i + 1]) + 1) / 2 for i in range(0, len(col_zero) - 1) if col_zero[i + 1] == col_zero[i] + 1]
    g["joints"] = {"joint_px": JPX, "joint_in": JPX / PPI, "zero_columns": col_zero.tolist(), "zero_rows": row_zero.tolist(),
                   "interior_joint_centres_px": centres_x,
                   "zero_exactly_on_joints": bool(np.array_equal(zero, jmask)),
                   "pass": bool(np.array_equal(zero, jmask) and np.array_equal(col_zero, np.flatnonzero(jx))
                                and np.array_equal(row_zero, np.flatnonzero(jy)))}
    L = srgb_to_lin(c) @ LUMA
    # Step ACROSS a joint = between the two face pixels that flank it (the joint pixels are grout on both sides and
    # would always give 0). Wrap: column W-2 vs column 1 (vertical wrap joint), row H-2 vs row 1 (horizontal).
    # Each wrap direction is compared with interior joints of the SAME direction (designed: vertical joints are
    # vein-continuous, horizontal joints are not). A single-piece map has no interior joint: its wrap joints are real
    # joints between the piece's own opposite edges, so the reference is the step across a joint between two
    # different supplied pieces (all ordered pairs, from the LittleCMS-decoded sources), i.e. an ordinary joint.
    S0 = sources()
    Ls = {k: srgb_to_lin(S0[k]) @ LUMA for k in S0}
    unrel = float(np.mean([np.abs(Ls[i][:, -1] - Ls[j][:, 0]).mean() for i in Ls for j in Ls if i != j]
                          + [np.abs(Ls[i][-1] - Ls[j][0]).mean() for i in Ls for j in Ls if i != j]))

    def steps(A):
        ev = float(np.abs(A[:, 1] - A[:, W - 2]).mean())
        eh = float(np.abs(A[1] - A[H - 2]).mean())
        iv = [float(np.abs(A[:, x + 1] - A[:, x - 2]).mean()) for x in range(MPX, W, MPX)]
        ih = [float(np.abs(A[y + 1] - A[y - 2]).mean()) for y in range(MPX, H, MPX)]
        return ev, eh, (float(np.mean(iv)) if iv else None), (float(np.mean(ih)) if ih else None)
    ev, eh, iv, ih = steps(L)
    bev, beh, biv, bih = steps(h)
    bump_ref = float(np.abs(h[4:-4, 4:-4] - h[4:-4, 1:-7]).mean())      # micro-relief's own 3 px step
    if iv is not None and ih is not None:
        ref_v, ref_h = iv, ih
        colour_ok = ev <= 1.5 * ref_v and eh <= 1.5 * ref_h
        src_own = None
    else:
        # single piece: the wrap joint is where the piece meets its own opposite edge, which is product content
        # (piece 8 is much darker along its bottom than its top). The build must not ADD to it: compare with the
        # same step measured on the source photo's own opposite edges.
        k = cells[0][0]["piece"]
        src_own = [float(np.abs(Ls[k][:, -1] - Ls[k][:, 0]).mean()), float(np.abs(Ls[k][-1] - Ls[k][0]).mean())]
        ref_v, ref_h = src_own
        colour_ok = ev <= 1.15 * ref_v + 0.01 and eh <= 1.15 * ref_h + 0.01
    bump_ok = max(bev, beh) <= 1.5 * max(biv if biv is not None else bump_ref, bih if bih is not None else bump_ref, bump_ref)
    g["wrap"] = {"edge_grout_share": {"left": float(zero[:, 0].mean()), "right": float(zero[:, -1].mean()),
                                      "top": float(zero[0].mean()), "bottom": float(zero[-1].mean())},
                 "left_plus_right_px": int(zero[:, 0].all()) + int(zero[:, -1].all()),
                 "top_plus_bottom_px": int(zero[0].all()) + int(zero[-1].all()),
                 "colour_lum_step_vertical_wrap_vs_ref": [ev, ref_v], "colour_lum_step_horizontal_wrap_vs_ref": [eh, ref_h],
                 "ref_basis": "interior joints of the same direction" if src_own is None else
                              "the source photo's own opposite-edge step (single-piece map); pass <= 1.15 x + 0.01",
                 "step_across_joint_between_different_pieces_mean": unrel,
                 "bump_step_wrap_v_h": [bev, beh], "bump_step_interior_v_h": [biv, bih], "bump_micro_3px_step": bump_ref,
                 "pass": bool(zero[:, 0].all() and zero[:, -1].all() and zero[0].all() and zero[-1].all()
                              and not zero[:, 1].all() and not zero[1].all() and colour_ok and bump_ok)}
    # identity
    S = sources()
    var = {}
    for k in range(1, 9):
        Lk = S[k] @ LUMA
        for d in (0, 90, 180, 270):
            var[(k, d, False)] = rotcw(Lk, d)[::4, ::4]
            var[(k, d, True)] = rotcw(Lk[:, ::-1], d)[::4, ::4]
    ident = []
    faces = {}
    for r, cc in itertools.product(range(nr), range(nc)):
        f = c[r * MPX + 1:r * MPX + 1 + FPX, cc * MPX + 1:cc * MPX + 1 + FPX]
        fh = b[r * MPX + 1:r * MPX + 1 + FPX, cc * MPX + 1:cc * MPX + 1 + FPX]
        faces[(r, cc)] = (f, fh)
        fd = down(f)
        fl = (fd @ LUMA)[::4, ::4]
        sc = {key: ncc(fl, v) for key, v in var.items()}
        best = max(sc, key=sc.get)
        decl = (cells[r][cc]["piece"], cells[r][cc]["rot_cw_deg"], False)
        others = [v for key, v in sc.items() if key[0] != decl[0] or key[1] != decl[1]]
        mir = max(v for key, v in sc.items() if key[0] == decl[0] and key[2])
        src = rotcw(S[decl[0]], decl[1])
        mad = float(np.abs(fd[8:-8, 8:-8] - src[8:-8, 8:-8]).mean())
        ident.append({"cell": [r, cc], "declared": [decl[0], decl[1]], "measured": [best[0], best[1], "mirror" if best[2] else "rotation"],
                      "ncc_declared": sc[decl], "best_other": max(others), "best_mirror_of_same_piece": mir,
                      "mean_abs_drgb_vs_littlecms": mad,
                      "ok": bool(best == decl and sc[decl] > 0.97 and sc[decl] - max(others) > 0.5 and mir < sc[decl] and mad < 3.0)})
    g["identity"] = {"cells": ident, "min_ncc_declared": min(x["ncc_declared"] for x in ident),
                     "max_other": max(x["best_other"] for x in ident), "max_mean_abs_drgb": max(x["mean_abs_drgb_vs_littlecms"] for x in ident),
                     "pass": bool(all(x["ok"] for x in ident))}
    # clearance + colour registration
    face = ~jmask
    gs = np.array(GROUT, float)
    src_mean = np.mean([srgb_to_lin(S[x["declared"][0]]).reshape(-1, 3).mean(0) for x in ident], 0)
    rel = srgb_to_lin(c[face]).mean(0) / src_mean - 1
    g["clearance"] = {"face_min_mm": float(h[face].min()), "face_max_mm": float(h[face].max()), "face_median_mm": float(np.median(h[face])),
                      "face_micro_sd_mm": float(h[face][h[face] > 1.45].std()), "grout_max_mm": float(h[jmask].max()),
                      "joint_depth_mm": FACE_MM, "full_scale_mm": FULL_MM, "clearance_face_above_grout_mm": float(h[face].min()),
                      "pass": bool(h[face].min() > 0.5 * FACE_MM and h[jmask].max() == 0 and h.max() <= FULL_MM + 1e-9)}
    g["colour_bump"] = {"joint_px": int(jmask.sum()), "joint_px_exact_grout": float((np.abs(c[jmask] - gs).max(1) == 0).mean()),
                        "face_mean_lin_vs_source_rel": [float(v) for v in rel], "face_mean_srgb": [float(v) for v in c[face].mean(0)],
                        "pass": bool((np.abs(c[jmask] - gs).max(1) == 0).all() and np.abs(rel).max() < 0.02)}
    return g, c, b, faces


def continuity(c, nc, nr, W):
    L = srgb_to_lin(c) @ LUMA
    S = sources()
    s = FPX / 1417.0
    out = []
    for r in range(nr):
        for k in range(1, nc + 1):
            xc = (k * MPX) % W
            y0, y1 = r * MPX + 1, r * MPX + 1 + FPX
            pa = bp(L[y0:y1, xc - 4:xc - 1].mean(1), s)
            pb = bp(L[y0:y1, xc + 1:xc + 4].mean(1), s)
            a, bb = STRIPS[r][k - 1], STRIPS[r][k % 4]
            la, lb = S[a] @ LUMA, S[bb] @ LUMA
            v_src = ncc(bp(la[:, -3:].mean(1)), bp(lb[:, :3].mean(1)))
            v = ncc(pa, pb)
            out.append({"row": r, "joint_x_px": int(k * MPX), "pieces": [a, bb], "wrap": bool(k == nc),
                        "ncc_built": v, "ncc_source": v_src, "ok": bool(v >= 0.40 and v >= v_src - 0.10)})
    horiz = []
    for r in range(1, nr + 1):
        yc = (r * MPX) % (nr * MPX)
        for cc in range(nc):
            x0, x1 = cc * MPX + 1, cc * MPX + 1 + FPX
            horiz.append(ncc(bp(L[yc - 4:yc - 1, x0:x1].mean(0), s), bp(L[yc + 1:yc + 4, x0:x1].mean(0), s)))
    rng = np.random.default_rng(3)
    base = []
    for _ in range(200):
        i, j = rng.integers(0, 8, 2) + 1
        x, y = rng.integers(10, 1400, 2)
        base.append(ncc(bp((S[i] @ LUMA)[:, x:x + 3].mean(1)), bp((S[j] @ LUMA)[:, y:y + 3].mean(1))))
    return {"vertical_joints": out, "min_ncc_built": min(o["ncc_built"] for o in out),
            "horizontal_joints_ncc": [float(x) for x in horiz], "horizontal_max": float(max(horiz)),
            "random_strip_baseline_p99": float(np.percentile(base, 99)),
            "note": "horizontal joints have no designed continuity (rows repeat strip A / strip B)",
            "pass": bool(all(o["ok"] for o in out))}


def adjacency(cells):
    n = len(cells)
    lab = {(r, c): cells[r][c]["piece"] for r in range(n) for c in range(n)}
    counts = {k: sum(1 for v in lab.values() if v == k) for k in range(1, 9)}
    touching = []
    for (r, c), k in lab.items():
        for dr, dc in itertools.product((-1, 0, 1), repeat=2):
            if (dr, dc) != (0, 0) and lab[((r + dr) % n, (c + dc) % n)] == k:
                touching.append([[r, c], [(r + dr) % n, (c + dc) % n], k])
    rots = {k: sorted(cells[r][c]["rot_cw_deg"] for (r, c), v in lab.items() if v == k) for k in range(1, 9)}
    return {"piece_counts": counts, "rotations_per_piece": rots, "same_piece_touching": touching,
            "pass": bool(all(v == 2 for v in counts.values()) and not touching and all(len(set(v)) == 2 for v in rots.values()))}


def main(which):
    import e01_model_pattern as e01
    mp_ok = e01.check()
    mpj = json.load(open(out_path("_work/model_pattern_check.json")))
    allpass = True
    piece_faces = {}
    for s in ([which] if which != "all" else ["pieces", "designed", "free_mix"]):
        nc, nr = SETS[s]
        results = []
        for cpath, bpath, cells in files_for(s):
            g, c, b, faces = verify_map(s, cpath, bpath, cells, nc, nr)
            if s == "designed":
                g["continuity"] = continuity(c, nc, nr, c.shape[1])
            if s == "free_mix":
                g["adjacency"] = adjacency(cells)
                mirrored = [x for x in g["identity"]["cells"] if x["measured"][2] != "rotation"]
                g["adjacency"]["mirrored_cells"] = len(mirrored)
                g["adjacency"]["pass"] = bool(g["adjacency"]["pass"] and not mirrored)
            # cross-set consistency against the piece maps
            if s == "pieces":
                piece_faces[cells[0][0]["piece"]] = faces[(0, 0)]
            else:
                if not piece_faces:
                    for k in range(1, 9):
                        pc = np.asarray(Image.open(out_path("pieces/Piece_%d_Color.png" % k)).convert("RGB")).astype(np.float64)
                        pb = np.asarray(Image.open(out_path("pieces/Piece_%d_Bump16.png" % k))).astype(np.int64)
                        piece_faces[k] = (pc[1:1 + FPX, 1:1 + FPX], pb[1:1 + FPX, 1:1 + FPX])
                bad = []
                for (r, cc), (f, fh) in faces.items():
                    k, d = cells[r][cc]["piece"], cells[r][cc]["rot_cw_deg"]
                    pf, pb = piece_faces[k]
                    if not (np.array_equal(f, rotcw(pf, d)) and np.array_equal(fh, rotcw(pb, d))):
                        bad.append([r, cc])
                g["cross_set"] = {"cells_identical_to_rotated_piece_maps": len(faces) - len(bad), "mismatched": bad, "pass": not bad}
            vpath = glob.glob(os.path.join(os.path.dirname(cpath), os.path.basename(cpath).replace("Color.png", "Color_*.png")))
            if vpath:
                gv = []
                jm = np.zeros(c.shape[:2], bool)
                jm[:, [x for x in range(c.shape[1]) if x % MPX in (0, MPX - 1)]] = True
                jm[[y for y in range(c.shape[0]) if y % MPX in (0, MPX - 1)], :] = True
                for vp in vpath:
                    cv = np.asarray(Image.open(vp).convert("RGB")).astype(np.float64)
                    gv.append({"file": os.path.basename(vp), "faces_identical": bool(np.array_equal(cv[~jm], c[~jm])),
                               "grout_srgb": [float(v) for v in cv[jm].mean(0)]})
                g["grout_variant"] = {"variants": gv, "pass": all(x["faces_identical"] for x in gv)}
            g["model_pattern"] = {"file": mpj["file"], "header_ok": mpj["header_ok"], "maps": mpj["maps"], "pass": bool(mp_ok)}
            ok = all(v["pass"] for v in g.values())
            results.append({"colour": os.path.basename(cpath), "bump": os.path.basename(bpath), "all_pass": ok, "gates": g})
        if s == "pieces":
            bs = [piece_faces[k][1][4:-4, 4:-4] for k in range(1, 9)]      # face interior: excludes the shared edge profile
            diff = all(not np.array_equal(bs[i], bs[j]) for i in range(8) for j in range(i + 1, 8))
            corr = max(ncc(bs[i].astype(float), bs[j].astype(float)) for i in range(8) for j in range(i + 1, 8))
            extra = {"piece_bumps_all_different": bool(diff), "max_bump_ncc_between_pieces": corr, "pass": bool(diff)}
        else:
            extra = {"pass": True}
        set_pass = all(x["all_pass"] for x in results) and extra["pass"]
        W, H = SETS[s][0] * MOD, SETS[s][1] * MOD
        out = {"set": s, "all_pass": set_pass, "maps": results, "set_checks": extra,
               "revit_sample_size": {"width_in": W, "height_in": H, "width": ftin(W), "height": ftin(H)},
               "revit_bump_amount_editor": 60}
        json.dump(out, open(out_path(s + "/validation.json"), "w"), indent=1)
        print("== %s: %s" % (s, "ALL PASS" if set_pass else "FAILED"))
        for x in results:
            print("  %-22s %s" % (x["colour"], " ".join("%s:%s" % (k, "PASS" if v["pass"] else "FAIL") for k, v in x["gates"].items())))
        allpass = allpass and set_pass
    sys.exit(0 if allpass else 1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
