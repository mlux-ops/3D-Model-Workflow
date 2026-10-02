"""Measure the finished maps and write textures/report.json (format, wrap seams, joints, relief, clearance, mix, per-face records)."""
import json
import os
import struct
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
info = json.load(open(rg.WORK + "face_info.json"))
P = info["params"]
W, H = P["W"], P["H"]
FULL_MM, PLANE_MM = P["FULL_MM"], P["PLANE_MM"]
MM_PER_LEVEL = FULL_MM / 65535.0
PX_MM = 25.4 / P["PPI"]
FACE_R = P["FACE_R"]
report = {}


def png_header(path):
    with open(path, "rb") as f:
        b = f.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR"
    w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", b[16:29])
    return dict(width=w, height=h, bit_depth=depth, colour_type=ctype, colour_type_name={0: "greyscale", 2: "RGB", 3: "indexed", 4: "grey+alpha", 6: "RGBA"}[ctype], interlace=inter)


hdr = {n: png_header(TEX + n) for n in ("Color.png", "Bump16.png", "face_ids.png")}
fmt_ok = (hdr["Color.png"]["width"] == W and hdr["Color.png"]["height"] == H and hdr["Color.png"]["bit_depth"] == 8 and hdr["Color.png"]["colour_type"] == 2
          and all(hdr[n]["width"] == W and hdr[n]["height"] == H and hdr[n]["bit_depth"] == 16 and hdr[n]["colour_type"] == 0 for n in ("Bump16.png", "face_ids.png")))
report["format"] = dict(headers_from_png_bytes=hdr, expected_size=[W, H], pass_=bool(fmt_ok))
print("format", fmt_ok, hdr)

color = np.asarray(Image.open(TEX + "Color.png").convert("RGB"))
bump = np.asarray(Image.open(TEX + "Bump16.png")).astype(np.int64)
ids = np.asarray(Image.open(TEX + "face_ids.png")).astype(np.int64)
assert color.shape == (H, W, 3) and bump.shape == (H, W) and ids.shape == (H, W)
lum = color.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
hmm = bump.astype(np.float64) * MM_PER_LEVEL

# ---- wrap seam steps: mean |neighbour difference| across the wrap vs across every interior column/row pair
def pair_steps(a, axis):
    a = a.astype(np.float64)
    if axis == 1:
        interior = np.abs(a[:, 1:] - a[:, :-1]).mean(axis=0)
        seam = np.abs(a[:, 0] - a[:, -1]).mean()
    else:
        interior = np.abs(a[1:, :] - a[:-1, :]).mean(axis=1)
        seam = np.abs(a[0, :] - a[-1, :]).mean()
    return dict(seam_mean_abs_step=float(seam), interior_mean_abs_step=float(interior.mean()), interior_p99_pair_step=float(np.percentile(interior, 99)),
                interior_max_pair_step=float(interior.max()), seam_over_interior_mean=float(seam / interior.mean()),
                seam_within_interior_p99=bool(seam <= np.percentile(interior, 99)))


rgbs = {}
for name, arr, unit in (("colour_luminance_levels", lum, "8-bit levels"), ("bump_mm", hmm, "mm")):
    rgbs[name] = dict(unit=unit, x_wrap=pair_steps(arr, 1), y_wrap=pair_steps(arr, 0))
# per-channel colour seam
rgbs["colour_rgb_levels_x_wrap_seam_mean"] = [float(np.abs(color[:, 0, k].astype(float) - color[:, -1, k].astype(float)).mean()) for k in range(3)]
rgbs["colour_rgb_levels_y_wrap_seam_mean"] = [float(np.abs(color[0, :, k].astype(float) - color[-1, :, k].astype(float)).mean()) for k in range(3)]
report["wrap_seam_steps"] = rgbs
print("wrap steps", json.dumps(rgbs, indent=0)[:1500])

# ---- face ids and joints
uids = np.unique(ids)
face_counts = {int(u): int((ids == u).sum()) for u in uids if u > 0}
exp_face_px = 2 * np.sqrt(3) * FACE_R * FACE_R
joint_px = int((ids == 0).sum())
centreline = 56 * 3 * (648.0 / np.sqrt(3))
expected_joint_px = 56 * (2 * np.sqrt(3) * P["MOD_R"] ** 2 - 2 * np.sqrt(3) * FACE_R ** 2)
# vertical scan through each even-column face centre: run of id 0 between vertically adjacent faces
runs = []
for fc in info["faces"]:
    if fc["i"] % 2 == 0:
        x = int(np.floor(fc["cx"]))
        col = ids[:, x]
        yj = int(round(fc["cy"] + 324.0)) % H
        ys = (yj + np.arange(-12, 12)) % H
        runs.append(int((col[ys] == 0).sum()))
# perpendicular scan across sloped edges: from a face centre outward along the normal at 30 degrees (down-right)
perp = []
for fc in info["faces"]:
    ang = np.radians(30.0)
    n = np.array([np.cos(ang), np.sin(ang)])
    cx, cy = fc["cx"], fc["cy"]
    t = np.arange(FACE_R - 10, FACE_R + 24 - 0.0, 0.05)
    xs = np.round(cx + n[0] * t - 0.5).astype(int) % W
    ys = np.round(cy + n[1] * t - 0.5).astype(int) % H
    v = ids[ys, xs] == 0
    seg = t[v]
    # the perpendicular hex-distance of the point along this ray is t * cos(0) since n is an edge normal
    if seg.size:
        perp.append(float(seg.max() - seg.min() + 0.05))
report["face_ids"] = dict(
    n_faces=len(face_counts), ids_min=min(face_counts), ids_max=max(face_counts), joint_value=0,
    face_pixel_count_min=min(face_counts.values()), face_pixel_count_max=max(face_counts.values()), expected_face_pixel_count=float(exp_face_px),
    joint_pixels=joint_px, expected_joint_pixels=float(expected_joint_px), joint_area_over_centreline_length_px=float(joint_px / centreline),
    vertical_joint_run_px_min=min(runs), vertical_joint_run_px_max=max(runs), sloped_joint_perpendicular_width_px_min=min(perp), sloped_joint_perpendicular_width_px_max=max(perp),
    specified_joint_width_px=8, specified_joint_width_in=0.125)
print("faces", report["face_ids"])
joint_ok = (min(runs) >= 7 and max(runs) <= 9 and abs(joint_px / centreline - 8.0) < 0.3 and len(face_counts) == 56 and min(face_counts) == 1 and max(face_counts) == 56)
report["face_ids"]["pass_"] = bool(joint_ok)

# ---- relief per face type: heights above the joint floor in mm
joint_floor = float(hmm[ids == 0].min())
joint_vals = hmm[ids == 0]
type_of = {fc["index"]: fc["type"] for fc in info["faces"]}
tmap = np.zeros(H * W, np.uint8)
lut = np.zeros(int(ids.max()) + 1, np.uint8)
for k, t in type_of.items():
    lut[k] = {"matte": 1, "raw": 2, "chiseled": 3}[t]
tmap = lut[ids]
relief = {}
gy_, gx_ = np.gradient(hmm, PX_MM)
slope = np.degrees(np.arctan(np.hypot(gy_, gx_)))
for t, code in (("matte", 1), ("raw", 2), ("chiseled", 3)):
    v = hmm[tmap == code]
    s = slope[tmap == code]
    relief[t] = dict(
        n_faces=int(sum(1 for x in type_of.values() if x == t)), face_plane_median_mm=float(np.median(v)), min_mm=float(v.min()), max_mm=float(v.max()),
        std_mm=float(v.std()), p1_mm=float(np.percentile(v, 1)), p99_mm=float(np.percentile(v, 99)), p1_to_p99_relief_mm=float(np.percentile(v, 99) - np.percentile(v, 1)),
        min_to_max_mm=float(v.max() - v.min()), slope_p50_deg=float(np.percentile(s, 50)), slope_p99_deg=float(np.percentile(s, 99)),
        clearance_above_joint_floor_mm=float(v.min() - joint_floor))
per_face = {}
for fc in info["faces"]:
    m = ids == fc["index"]
    v = hmm[m]
    per_face[fc["index"]] = dict(min_mm=float(v.min()), max_mm=float(v.max()), std_mm=float(v.std()), clearance_mm=float(v.min() - joint_floor))
worst = min(per_face.items(), key=lambda kv: kv[1]["clearance_mm"])
report["relief_mm"] = dict(
    definition="height above the joint floor from Bump16 (65535 = %.1f mm full scale); face pixels are those with a face id" % FULL_MM,
    joint_floor_mm=joint_floor, joint_floor_median_mm=float(np.median(joint_vals)), face_plane_design_mm=PLANE_MM, grout_step_mm=float(PLANE_MM - joint_floor),
    per_type=relief, worst_face_index=int(worst[0]), worst_face_clearance_mm=float(worst[1]["clearance_mm"]),
    global_min_face_height_mm=float(min(r["min_mm"] for r in relief.values())),
    clearance_mm=float(min(r["min_mm"] for r in relief.values()) - joint_floor),
    clearance_positive=bool(min(r["min_mm"] for r in relief.values()) - joint_floor > 0),
    bump_levels_used=[int(bump.min()), int(bump.max())], full_scale_mm=FULL_MM,
    note="Millimetre values are design heights chosen so that the raking-light look matches the sources; they are not measured depths of the real tile.")
print("relief", json.dumps(report["relief_mm"], indent=0)[:2500])

# ---- mix
Z = np.load(rg.WORK + "libs.npz")
def cnt(name, thr=95):
    n = int(Z[name + "_n"])
    return sum(1 for k in range(n) if int(Z["%s_%d_id" % (name, k)][2]) >= thr)
meas = dict(matte=cnt("matte"), raw=cnt("raw"))
chis_w = [int(Z["chis_%d_id" % k][2]) for k in range(int(Z["chis_n"]))]
meas["chiseled"] = len(chis_w)
tot = sum(meas.values())
used = {t: sum(1 for fc in info["faces"] if fc["type"] == t) for t in ("matte", "raw", "chiseled")}
utot = sum(used.values())
ch_used = {}
for fc in info["faces"]:
    if fc["type"] == "chiseled":
        ch_used[str(fc["rotation_deg"])] = ch_used.get(str(fc["rotation_deg"]), 0) + 1
ch_meas = {str(w): chis_w.count(w) for w in (0, 60, 120)}
lay = json.load(open(rg.WORK + "layout.json"))
report["mix"] = dict(
    render_complete_faces_classified=tot,
    measured_counts=meas, measured_ratio={k: v / tot for k, v in meas.items()},
    used_counts=used, used_ratio={k: v / utot for k, v in used.items()},
    chiseled_wave_angle_counts_render={"0 (vertical grooves)": ch_meas["0"], "60": ch_meas["60"], "120": ch_meas["120"]},
    chiseled_wave_angle_counts_used={"0 (vertical grooves)": ch_used.get("0", 0), "60": ch_used.get("60", 0), "120": ch_used.get("120", 0)},
    layout=dict(seed=lay["seed"], energy=lay["energy"], max_shift_match_fraction=lay["max_shift_match"], raw_raw_adjacent_pairs=lay["raw_raw_adjacent"], chiseled_chiseled_adjacent_pairs=lay["chis_chis_adjacent"]))
print("mix", json.dumps(report["mix"], indent=0)[:1500])

# ---- faces
report["faces"] = [dict(index=fc["index"], column=fc["i"], row=fc["j"], type=fc["type"], rotation_deg=fc["rotation_deg"], mirrored=fc["mirrored"], source=fc["source"],
                        centre_px=[fc["cx"], fc["cy"]], **per_face[fc["index"]]) for fc in info["faces"]]

rs = json.load(open(rg.WORK + "repeat_search.json"))["summary"]
rn = json.load(open(rg.WORK + "repeat_null.json"))
report["non_repeating"] = dict(
    method="Normalised cross-correlation of 2 in patches (high-passed luminance, half resolution) against every window of the whole atlas on the torus, 8 dihedral transforms, "
           "windows touching joints or chiseled faces ignored; whole-face NCC of every matte pair and raw pair under the 12 hexagon symmetries. Chiseled faces are not covered "
           "(their grooves repeat by design and the grain is under the grooves); see README.",
    atlas_patch_search={k: v for k, v in rs.items() if k not in ("worst", "whole_face_pairs")},
    atlas_worst_matches=[dict(patch_face=w["face"], matched_face=w["match"]["matched_face"], transform=w["match"]["transform"], ncc=w["max_ncc"]) for w in rs["worst"]],
    whole_face_pairs=rs["whole_face_pairs"],
    reference_null_source_render_unique_faces=rn["render_null"],
    top_atlas_matches_remeasured_full_resolution=rn["top_atlas_matches"],
    reading="No patch or face matched above NCC 0.50; the source render's own unique faces reach 0.68 under the same search. The 0.4-0.5 matches are consistent with source library blocks being reused "
            "(about 1.4x reuse was unavoidable; the face 42 / face 25 pair visibly shares a dark micro-mark after contrast stretching, see _REVIEW_repeat_top_matches.jpg) and are not visible in the unstretched colour map; a planted copy degraded by noise 2x the patch std scores 0.44-0.46, "
            "so matches near 0.5 cannot be separated from a heavily degraded copy by this test alone.")

gc = json.load(open(rg.WORK + "groove_check.json"))
report["chiseled_groove_check"] = dict(
    method="FFT peak (5x5 power-weighted centroid) of a 384 px window at each chiseled face centre in Color.png, band period 8-22 px; angle is the groove wave-vector angle in image coordinates (0 = vertical grooves)",
    source_pitch_in=gc["source_pitch_in"], atlas_pitch_in_mean=gc["pitch_in_mean"], atlas_pitch_in_min=gc["pitch_in_min"], atlas_pitch_in_max=gc["pitch_in_max"],
    max_angle_error_deg=gc["max_angle_error_deg"], mean_angle_error_deg=gc["mean_angle_error_deg"], faces=gc["faces"])
report["fidelity_band_std"] = dict(
    note="Band-pass luminance std (difference of Gaussians, sigma 1,2,4,8,16 render px, then the residual to sigma 32); atlas measured at equivalent physical scale. Text as printed by t_contrast.py and t_life_contrast.py.",
    render_vs_atlas=[l.rstrip() for l in open(rg.WORK + "contrast_render_vs_atlas.txt") if l.strip()],
    lifestyle_vs_grazing_preview=[l.rstrip() for l in open(rg.WORK + "contrast_lifestyle_vs_preview.txt") if l.strip()])

report["suggested_revit_bump_amount"] = dict(
    value=100,
    scale="whole number on the Revit editor scale (stored float x100)",
    basis="AGENTS.md calibration for a full-range 16-bit dimensional map at 2.6 mm full scale with a 1.6 mm joint: 1 showed nothing, 50 joints only, 100 tile relief readable. Same scale and joint here. Not verified in Revit for this build (Revit is out of scope for the trial).")
report["sample_size_in"] = [70.148, 70.875]
report["atlas_px"] = [W, H]
report["px_per_in"] = P["PPI"]
report["build_params"] = P

json.dump(report, open(guard.safe(TEX + "report.json"), "w"), indent=1)
print("wrote report.json; format pass", report["format"]["pass_"], "joint pass", report["face_ids"]["pass_"], "clearance positive", report["relief_mm"]["clearance_positive"])
