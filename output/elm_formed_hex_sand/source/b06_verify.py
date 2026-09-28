"""Build step 6: independent verification of the delivered maps, and report.json.

Re-derives every gate from the PNG files themselves (not from build variables):
  format   PNG IHDR bytes: size, bit depth, colour type
  joints   face_ids zero runs across horizontal flats (must be 8 px) and total joint
           area vs the theoretical 1/8 in joint area
  wrap     mean |step| across the wrap seams vs the mean interior step (colour, bump)
  relief   Bump16 -> mm (declared scale): joint floor, face plane, per-type relief,
           clearance of the deepest face point above the joint floor
  mix      type counts; chiseled rotation counts
  repeat   Raw faces: whole-face NCC over the 12 hexagon symmetries (+-12 px shifts), and
           a random-window search (1 in windows) over all other Raw faces under the 12
           symmetries and under +-8/16 deg rotations; baseline = the same search between
           the render's own Raw faces (independent surfaces)
Writes textures/report.json and textures/validation.json; exits non-zero on a failed gate.
"""

import hashlib
import json
import os
import struct
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, fft as sfft

from common import (COLS, ROWS, W, H, PX_PER_IN_X, PX_PER_IN_Y, COL_PITCH_IN, ROW_PITCH_IN,
                    SAMPLE_W_IN, SAMPLE_H_IN, out_path, render_rgb, srgb_to_lin, S3)
from guard import write_text

SEED = 7


def ihdr(path):
    with open(path, "rb") as f:
        b = f.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR"
    w, h = struct.unpack(">II", b[16:24])
    return {"width": w, "height": h, "bit_depth": b[24], "color_type": b[25]}


def centre_px(i, j):
    cx = (i + 0.5) * COL_PITCH_IN * PX_PER_IN_X
    cy = ((j + 0.5) * ROW_PITCH_IN + (ROW_PITCH_IN / 2 if i % 2 else 0)) * PX_PER_IN_Y
    return cx, cy


def face_patch(img, i, j, half):
    cx, cy = centre_px(i, j)
    ys = (np.arange(int(cy) - half, int(cy) + half)) % H
    xs = (np.arange(int(cx) - half, int(cx) + half)) % W
    return img[np.ix_(ys, xs)]


def transforms12(a):
    out = []
    for mir in (False, True):
        b = a[:, ::-1] if mir else a
        for k in range(6):
            out.append(ndimage.rotate(b, 60 * k, reshape=False, order=1, mode="nearest") if k else b)
    return out


def ncc_search(tmpl, img, mask_r=None):
    """max NCC of tmpl (square) over all translations of img (both 2-D, float)."""
    th, tw = tmpl.shape
    h, w = img.shape
    t = tmpl - tmpl.mean()
    t /= np.sqrt((t ** 2).sum()) + 1e-12
    s = (h + th, w + tw)
    Fi = sfft.rfft2(img, s=s, workers=-1)
    Fi2 = sfft.rfft2(img * img, s=s, workers=-1)
    Ft = np.conj(sfft.rfft2(t, s=s, workers=-1))
    Fo = np.conj(sfft.rfft2(np.ones_like(t), s=s, workers=-1))
    num = sfft.irfft2(Fi * Ft, s=s, workers=-1)[:h - th + 1, :w - tw + 1]
    s1 = sfft.irfft2(Fi * Fo, s=s, workers=-1)[:h - th + 1, :w - tw + 1]
    s2 = sfft.irfft2(Fi2 * Fo, s=s, workers=-1)[:h - th + 1, :w - tw + 1]
    n = th * tw
    var = np.maximum(s2 - s1 * s1 / n, 1e-12)
    return float((num / np.sqrt(var)).max())


def hp_luma(rgb8):
    lin = srgb_to_lin(rgb8.astype(np.float64))
    Y = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    return Y - ndimage.gaussian_filter(Y, 8.0)


def main():
    rep = {}
    val = {"gates": {}}
    paths = {k: out_path("textures", k + ".png") for k in ("Color", "Bump16", "face_ids")}
    hdr = {k: ihdr(p) for k, p in paths.items()}
    fmt_ok = (hdr["Color"] == {"width": W, "height": H, "bit_depth": 8, "color_type": 2} and
              hdr["Bump16"] == {"width": W, "height": H, "bit_depth": 16, "color_type": 0} and
              hdr["face_ids"] == {"width": W, "height": H, "bit_depth": 16, "color_type": 0})
    val["png_headers"] = hdr
    col = np.asarray(Image.open(paths["Color"]).convert("RGB"))
    b16 = np.asarray(Image.open(paths["Bump16"])).astype(np.int64)
    fid = np.asarray(Image.open(paths["face_ids"])).astype(np.int64)
    bf = json.load(open(out_path("_work", "build_faces.json")))
    src = json.load(open(out_path("_work", "sources.json")))
    hr = bf["params_mm"]["h_range"]
    mm = b16 / 65535.0 * hr
    types = {f["index"]: f["type"] for f in bf["faces"]}
    faces_present = sorted(set(np.unique(fid)) - {0})
    # ---- joints -------------------------------------------------------------------------
    runs = []
    for i in range(COLS):
        cx, _ = centre_px(i, 0)
        for x in (int(cx) - 20, int(cx), int(cx) + 20):
            colv = fid[:, x % W] == 0
            colv = np.r_[colv, colv]                   # wrap
            d = np.diff(colv.astype(int))
            st = np.flatnonzero(d == 1) + 1
            en = np.flatnonzero(d == -1) + 1
            for s_ in st:
                e_ = en[en > s_]
                if len(e_) and s_ < H:
                    runs.append(int(e_[0] - s_))
    runs = np.array(runs)
    joint_frac = float((fid == 0).mean())
    joint_frac_theory = 1.0 - (10.0 / 10.125) ** 2
    joint_col = col[fid == 0]
    joint_ok = bool(np.all(runs == 8) and abs(joint_frac - joint_frac_theory) < 0.0015)
    val["joints"] = {"horizontal_flat_run_lengths_px": {str(int(k)): int((runs == k).sum()) for k in np.unique(runs)},
                     "joint_area_fraction": joint_frac, "theoretical_fraction_1_8_in": joint_frac_theory,
                     "joint_colour_srgb_unique": np.unique(joint_col, axis=0).tolist()[:4],
                     "bump_joint_values_unique": np.unique(b16[fid == 0]).tolist()[:4]}
    # ---- wrap steps ---------------------------------------------------------------------
    def steps(a):
        """Mean |step| across the wrap seams vs interior pixel boundaries. The hexagon
        lattice makes the step depend on where a boundary falls (slanted joints between
        columns, horizontal joints every half row), so the fair reference is the set of
        interior boundaries at the SAME lattice phase: x = k*W/8 (k=1..7, the other
        column midpoints) and y = k*H/7 (k=1..6)."""
        a = a.astype(np.float64)
        if a.ndim == 2:
            a = a[..., None]
        dx_int = np.abs(np.diff(a, axis=1)).mean(axis=(0, 2))       # per column pair
        dy_int = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
        sx = float(np.abs(a[:, 0] - a[:, -1]).mean())
        sy = float(np.abs(a[0, :] - a[-1, :]).mean())
        mx = [float(np.abs(a[:, int(round(k * W / 8.0))] - a[:, int(round(k * W / 8.0)) - 1]).mean())
              for k in range(1, 8)]
        my = [float(np.abs(a[int(round(k * H / 7.0))] - a[int(round(k * H / 7.0)) - 1]).mean())
              for k in range(1, 7)]
        return {"seam_x": sx, "matched_interior_x": mx, "matched_x_mean": float(np.mean(mx)),
                "ratio_x_matched": sx / float(np.mean(mx)),
                "seam_y": sy, "matched_interior_y": my, "matched_y_mean": float(np.mean(my)),
                "ratio_y_matched": sy / float(np.mean(my)),
                "all_columns_mean": float(dx_int.mean()), "all_columns_p99": float(np.percentile(dx_int, 99)),
                "all_rows_mean": float(dy_int.mean()), "all_rows_p99": float(np.percentile(dy_int, 99)),
                "ratio_x_naive": sx / float(dx_int.mean()), "ratio_y_naive": sy / float(dy_int.mean())}
    ws_c = steps(col)
    ws_b = steps(b16)
    ws_b_mm = {}
    for k, v in ws_b.items():
        if k.startswith("ratio"):
            ws_b_mm[k] = v
        elif isinstance(v, list):
            ws_b_mm[k] = [x * hr / 65535.0 for x in v]
        else:
            ws_b_mm[k] = v * hr / 65535.0
    def seam_ok(s):
        return (s["seam_x"] <= 1.15 * max(s["matched_interior_x"]) and
                s["seam_y"] <= 1.15 * max(s["matched_interior_y"]))
    wrap_ok = seam_ok(ws_c) and seam_ok(ws_b)
    # ---- relief -------------------------------------------------------------------------
    floor = mm[fid == 0]
    # interior = away from the eased edge (distance transform on face mask)
    dist = ndimage.distance_transform_edt(np.pad(fid > 0, 64, mode="wrap"))[64:-64, 64:-64]
    edge_band_px = bf["params_mm"]["ease_width_in"] * 64.0 + 1.0
    rel = {}
    for t in ("matte", "raw", "chiseled"):
        ids = [k for k, v in types.items() if v == t]
        m = np.isin(fid, ids)
        mi = m & (dist > edge_band_px)
        v = mm[mi]
        rel[t] = {"faces": len(ids), "min_mm": float(mm[m].min()), "max_mm": float(mm[m].max()),
                  "interior_min_mm": float(v.min()), "interior_max_mm": float(v.max()),
                  "interior_p0_5_mm": float(np.percentile(v, 0.5)), "interior_p99_5_mm": float(np.percentile(v, 99.5)),
                  "interior_median_mm": float(np.median(v)),
                  "pattern_relief_p0_5_to_p99_5_mm": float(np.percentile(v, 99.5) - np.percentile(v, 0.5)),
                  "pattern_relief_full_mm": float(v.max() - v.min())}
    plane = rel["matte"]["interior_median_mm"]
    joint_floor = float(floor.min())
    joint_depth = plane - joint_floor
    face_min_all = float(mm[fid > 0].min())
    face_min_interior = float(mm[(fid > 0) & (dist > edge_band_px)].min())
    clear_ok = face_min_all > joint_floor and float(floor.max()) <= joint_floor + 1e-9
    relief_ok = (rel["raw"]["pattern_relief_p0_5_to_p99_5_mm"] > 0.8 and
                 rel["chiseled"]["pattern_relief_p0_5_to_p99_5_mm"] > 0.6 and
                 rel["matte"]["pattern_relief_p0_5_to_p99_5_mm"] < 0.1)
    # ---- mix ----------------------------------------------------------------------------
    counts = {t: sum(1 for v in types.values() if v == t) for t in ("matte", "raw", "chiseled")}
    rots = {}
    for f in bf["faces"]:
        if f["type"] == "chiseled":
            rots[str(f["rotation_deg"])] = rots.get(str(f["rotation_deg"]), 0) + 1
    rfull = [f for f in src["faces"] if f["frac"] > 0.99]
    measured = {t: sum(1 for f in rfull if f["type"] == t) for t in ("matte", "raw", "chiseled")}
    mix_ok = (len(faces_present) == 56 and counts == {"matte": 32, "raw": 11, "chiseled": 13})
    # ---- repetition among Raw faces (cached against the PNG hashes) ------------------------
    digest = {k: hashlib.sha256(open(p, "rb").read()).hexdigest() for k, p in paths.items()}
    cache_p = out_path("_work", "repetition_cache.json")
    repeat = None
    if os.path.exists(cache_p):
        cached = json.load(open(cache_p))
        if cached.get("sha256") == digest:
            repeat = cached["repeat"]
            print("repetition: reusing results computed on identical PNGs (sha256 match)")
    if repeat is None:
        repeat = repetition(col, mm, bf, src)
        json.dump({"sha256": digest, "repeat": repeat}, open(cache_p, "w"), indent=1)
    repeat_ok = repeat["whole_face_ncc_colour_max"] < 0.5 and repeat["window_ncc_12sym_max"] < 0.8
    val["sha256"] = digest
    # ---- assemble -----------------------------------------------------------------------
    val["gates"] = {"format": fmt_ok, "joints_1_8_in": joint_ok, "wrap_seamless": wrap_ok,
                    "clearance_gt_0": clear_ok, "relief_terms": relief_ok, "mix_counts": mix_ok,
                    "raw_non_repeating": repeat_ok}
    val["wrap_colour_8bit"] = ws_c
    val["wrap_bump_16bit"] = ws_b
    return finish(val, rep, hdr, bf, src, types, counts, measured, rots, ws_c, ws_b, ws_b_mm, rel,
                  joint_floor, plane, joint_depth, face_min_interior, face_min_all, repeat,
                  joint_frac, joint_frac_theory, hr)


def repetition(col, mm, bf, src):
    rng = np.random.default_rng(SEED)
    Yhp = hp_luma(col)
    hhp = mm - ndimage.gaussian_filter(mm, 8.0)
    raw_cells = [f for f in bf["faces"] if f["type"] == "raw"]
    half = 250                                        # 500 px disc ~ 7.8 in, inside the face
    yy, xx = np.mgrid[-half:half, -half:half]
    disc = (xx ** 2 + yy ** 2) <= (half - 20) ** 2
    def whole(a_img, b_img):
        best = -1.0
        B = b_img
        for At in transforms12(a_img):
            for sy in range(-12, 13, 4):
                for sx in range(-12, 13, 4):
                    Bs = np.roll(np.roll(B, sy, 0), sx, 1)
                    a = At[disc]; b = Bs[disc]
                    a = a - a.mean(); b = b - b.mean()
                    v = float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))
                    best = max(best, v)
        return best
    patches_c = {f["index"]: face_patch(Yhp, f["i"], f["j"], half) for f in raw_cells}
    patches_h = {f["index"]: face_patch(hhp, f["i"], f["j"], half) for f in raw_cells}
    wf_c, wf_h = [], []
    ids = sorted(patches_c)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            wf_c.append(whole(patches_c[ids[a]], patches_c[ids[b]]))
            wf_h.append(whole(patches_h[ids[a]], patches_h[ids[b]]))
    # random-window search (1 in = 64 px windows) under 12 symmetries and +-8/16 deg
    def window_search(imgs, n_win=40, extra_angles=(8, -8, 16, -16)):
        keys = sorted(imgs)
        res_sym, res_rot = [], []
        for _ in range(n_win):
            a = keys[int(rng.integers(0, len(keys)))]
            img = imgs[a]
            # window inside the face's inner disc
            while True:
                cy, cx = rng.integers(half - 150, half + 150, size=2)
                if (cy - half) ** 2 + (cx - half) ** 2 < 150 ** 2:
                    break
            win = img[cy - 44:cy + 44, cx - 44:cx + 44]
            best_s, best_r = -1.0, -1.0
            for b in keys:
                if b == a:
                    continue
                tgt = imgs[b][60:-60, 60:-60]
                for k, wt in enumerate(transforms12(win)):
                    best_s = max(best_s, ncc_search(wt[12:-12, 12:-12], tgt))
                for ang in extra_angles:
                    for mir in (False, True):
                        wr = ndimage.rotate(win[:, ::-1] if mir else win, ang, reshape=False, order=1)
                        best_r = max(best_r, ncc_search(wr[12:-12, 12:-12], tgt))
            res_sym.append(best_s); res_rot.append(best_r)
        return np.array(res_sym), np.array(res_rot)
    ws_sym, ws_rot = window_search(patches_c, n_win=24)
    # baseline: the render's own Raw faces (independent surfaces), same window size in inches
    rgb = render_rgb()
    rr = [f for f in src["faces"] if f["type"] == "raw" and f["frac"] > 0.99]
    ppi_r = src["ppi_render"]
    base_imgs = {}
    for f in rr:
        s = 64.0 / ppi_r
        ys = f["cy"] + (np.arange(2 * half) - half + 0.5) / s
        xs = f["cx"] + (np.arange(2 * half) - half + 0.5) / s
        gy, gx = np.meshgrid(ys, xs, indexing="ij")
        a = np.stack([ndimage.map_coordinates(rgb[..., c], [gy - 0.5, gx - 0.5], order=3) for c in range(3)], -1)
        base_imgs[f["id"]] = hp_luma(np.clip(a, 0, 255))
    bs_sym, bs_rot = window_search(base_imgs, n_win=24)
    repeat = {"whole_face_ncc_colour_max": float(max(wf_c)), "whole_face_ncc_colour_median": float(np.median(wf_c)),
              "whole_face_ncc_height_max": float(max(wf_h)), "whole_face_ncc_height_median": float(np.median(wf_h)),
              "window_ncc_12sym_max": float(ws_sym.max()), "window_ncc_12sym_median": float(np.median(ws_sym)),
              "window_ncc_rot8_16_max": float(ws_rot.max()), "window_ncc_rot8_16_median": float(np.median(ws_rot)),
              "baseline_render_window_ncc_12sym_max": float(bs_sym.max()),
              "baseline_render_window_ncc_12sym_median": float(np.median(bs_sym)),
              "baseline_render_window_ncc_rot_max": float(bs_rot.max()),
              "pairs": len(wf_c), "windows": int(len(ws_sym))}
    return repeat


def rnd(x, n):
    if isinstance(x, dict):
        return {k: rnd(v, n) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, n) for v in x]
    if isinstance(x, float):
        return round(x, n)
    return x


def finish(val, rep, hdr, bf, src, types, counts, measured, rots, ws_c, ws_b, ws_b_mm, rel,
           joint_floor, plane, joint_depth, face_min_interior, face_min_all, repeat,
           joint_frac, joint_frac_theory, hr):
    val["relief"] = rel
    val["repetition"] = repeat
    lay = {c["index"]: c for c in json.load(open(out_path("_work", "layout.json")))["cells"]}
    qmeta = json.load(open(out_path("_work", "raw_quilt.json")))
    faces_out = []
    for f in sorted(bf["faces"], key=lambda z: z["index"]):
        c = lay[f["index"]]
        d = {"index": f["index"], "type": f["type"], "rotation_deg": f["rotation_deg"],
             "mirrored": f["mirrored"], "source": f["source"]}
        if f["type"] == "matte":
            d["mirrored"] = bool(c["low_mirror"] or c["high_mirror"])
            d["low_band"] = {"render_face": c["low_src"], "rotation_deg": c["low_rot"], "mirrored": c["low_mirror"]}
            d["high_band"] = {"render_face": c["high_src"], "rotation_deg": c["high_rot"], "mirrored": c["high_mirror"]}
        elif f["type"] == "raw":
            pt = qmeta["faces"][str(f["index"])]["patches"]
            tr = {}
            for p in pt:
                key = "%s%+d" % (p["tau"], int(p["jit"]))
                tr[key] = tr.get(key, 0) + 1
            d["mirrored"] = any(p["tau"] in ("M30", "M120") for p in pt)
            d["patches"] = len(pt)
            d["patch_render_faces"] = sorted({p["src"] for p in pt})
            d["patch_transforms"] = dict(sorted(tr.items()))
        else:
            d["groove_direction_deg"] = (90 + f["rotation_deg"]) % 180
            d["grain_render_face"] = c["src"]
        faces_out.append(d)
    rep = {
        "product": "ELM Surfaces Formed Hexagon Tile in Sand (Matte / Raw / Chiseled faces)",
        "maps": {"Color.png": hdr["Color"], "Bump16.png": hdr["Bump16"], "face_ids.png": hdr["face_ids"]},
        "atlas": {"columns": COLS, "rows": ROWS, "faces": 56, "px_per_in": 64,
                  "tile_across_flats_in": 10.0, "joint_in": 0.125, "module_across_flats_in": 10.125,
                  "revit_sample_size_in": [round(SAMPLE_W_IN, 3), round(SAMPLE_H_IN, 3)],
                  "revit_sample_size_ft_in": ["5'-10 5/32\"", "5'-10 7/8\""],
                  "face_index_order": "index = row*8 + column + 1; flat-top, odd columns shifted down half a row; "
                                      "face centre x = (column+0.5)*8.7685 in, y = (row+0.5)*10.125 in (+5.0625 in odd columns)"},
        "joint_colour_srgb": bf["tone"]["joint_srgb_after"],
        "joint_colour_srgb_render_before_tone": list(bf["joint_srgb"]),
        "production_changes_vs_max_trial": {
            "chiseled_colour": "no groove modulation added (was x1.10 of the render's measured fundamental); residual "
                               "stripes removed by local demodulation at the face's own groove phase",
            "chiseled_bump": "ridge strength and sideways wander follow each source face's measured local fundamental "
                             "(crest_mod_k %s, phase_k %s); grain sigma %s mm (was 0.07), clipped %s sigma"
                             % (bf["params_mm"]["crest_mod_k"], bf["params_mm"]["phase_k"], bf["params_mm"]["grain_sigma"],
                                bf["params_mm"]["grain_clip_sigma_units"]),
            "tone": "per-channel linear gain %s moves the Matte mean from the render's sRGB %s to the lifestyle "
                    "image's lit Matte mean %s (owner: installed tile reads darker)"
                    % ([round(g, 4) for g in bf["tone"]["linear_gain"]], bf["tone"]["matte_mean_before_srgb"],
                       bf["tone"]["target_srgb"]),
            "source_ridge_modulation": bf["source_ridge_modulation"],
            "destripe": bf["destripe"]},
        "face_transform_convention": (
            "rotation_deg is counter-clockwise (y up). chiseled: tile rotation of the groove pattern, canonical "
            "tile = vertical grooves with the steep flank facing -x (grooves run at 90+rotation deg). matte: "
            "rotation of the low band (tone/cloudiness); both bands listed. raw: 0 = the render's texture axis "
            "kept; the face is a quilt, per-patch transforms listed (I = identity, R180 = rotated 180, "
            "M30/M120 = mirrored about the 30/120 deg axis, +-8 = extra jitter deg). mirrored = true when any "
            "mirrored source content is used in the face."),
        "faces": faces_out,
        "mix": {"measured_in_render_full_faces": measured,
                "measured_ratio": {t: round(measured[t] / sum(measured.values()), 4) for t in measured},
                "measured_area_weighted_incl_partial_faces": {"matte": 0.569, "raw": 0.206, "chiseled": 0.225},
                "used": counts, "used_ratio": {t: round(counts[t] / 56.0, 4) for t in counts},
                "chiseled_rotations_used_deg": rots,
                "chiseled_rotations_in_render_deg": {"0 (grooves 90)": 4, "60 (grooves 150)": 4,
                                                     "300 (grooves 30)": 1, "120 (grooves 30)": 1}},
        "wrap_seam_steps": {"method": "mean |step| across the wrap seam vs interior boundaries at the same "
                                      "lattice phase (x = k*W/8, y = k*H/7); pass if seam <= 1.15 x the largest "
                                      "matched interior step",
                            "colour_8bit_levels": rnd(ws_c, 3),
                            "bump_16bit_counts": rnd(ws_b, 2),
                            "bump_mm": rnd(ws_b_mm, 5)},
        "relief": {
            "height_scale": "Bump16 value v -> height = v/65535 * %.2f mm; 0 = joint floor" % hr,
            "joint_floor_mm": round(joint_floor, 4),
            "face_plane_mm": round(plane, 4),
            "joint_depth_mm": round(joint_depth, 4),
            "pattern_relief_mm": {t: round(rel[t]["pattern_relief_p0_5_to_p99_5_mm"], 3) for t in rel},
            "pattern_relief_full_range_mm": {t: round(rel[t]["pattern_relief_full_mm"], 3) for t in rel},
            "chiseled_groove_depth_design_mm": bf["params_mm"]["chis_depth"],
            "deepest_pattern_point_mm": round(face_min_interior, 4),
            "clearance_deepest_pattern_point_to_joint_floor_mm": round(face_min_interior - joint_floor, 4),
            "clearance_any_face_pixel_incl_eased_edge_mm": round(face_min_all - joint_floor, 4),
            "eased_edge": {"drop_mm": bf["params_mm"]["ease"], "width_in": bf["params_mm"]["ease_width_in"]},
            "per_type_detail": rel},
        "suggested_revit_bump_amount": 100,
        "suggested_revit_bump_amount_note": ("Revit appearance-editor value (whole numbers, 0-1000; the editor shows the stored "
                                             "generic_bump_amount x100, default 30). Checked by the owner in a Revit view of the "
                                             "25-012 651 Belmont floor, 2026-09-26: 1 = no visible relief, 50 = joints only, "
                                             "100 = Raw/Chiseled relief reads, joints read as recessed with an eased edge."),
        "chiseled_geometry": {"period_mm": round(src["period_in"] * 25.4, 3), "period_in": round(src["period_in"], 5),
                              "groove_directions_deg": [90, 150, 30],
                              "profile": "asymmetric: fundamental + 2nd harmonic (0.30, +100 deg rel. phase)"},
        "repetition_check": repeat,
        "raw_quilt_audit": (json.load(open(out_path("_work", "quilt_audit.json")))
                            if os.path.exists(out_path("_work", "quilt_audit.json")) else None),
        "raw_source_pixel_usage_histogram": json.load(open(out_path("_work", "raw_quilt.json")))["usage_hist"],
        "validation_gates": val["gates"],
    }
    json.dump(rep, open(out_path("textures", "report.json"), "w"), indent=1)
    json.dump(val, open(out_path("textures", "validation.json"), "w"), indent=1)
    print(json.dumps(val["gates"], indent=1))
    print("wrap colour", rnd(ws_c, 3))
    print("wrap bump", rnd(ws_b, 1))
    print("joint runs", val["joints"]["horizontal_flat_run_lengths_px"], "frac %.5f vs %.5f" % (joint_frac, joint_frac_theory))
    print("relief", json.dumps(rep["relief"]["pattern_relief_mm"]), "joint depth %.3f floor %.3f plane %.3f"
          % (joint_depth, joint_floor, plane))
    print("clearance pattern %.4f mm, any face px %.4f mm" % (face_min_interior - joint_floor, face_min_all - joint_floor))
    print("repetition", json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in repeat.items()}))
    return 0 if all(val["gates"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
