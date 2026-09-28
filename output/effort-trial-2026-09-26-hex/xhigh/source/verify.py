"""Independent verification of the delivered maps. Re-derives every gate from the PNG files
(headers and pixels), writes report.json["verification"], exits non-zero on a hard failure."""
import os
import sys
import json
import struct
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve
import common as C
from guard import TEX_DIR, write_text

fails = []
V = {}


def png_header(path):
    with open(path, "rb") as f:
        b = f.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    assert b[12:16] == b"IHDR"
    w, h = struct.unpack(">II", b[16:24])
    return {"width": w, "height": h, "bit_depth": b[24], "colour_type": b[25]}


# ---------------- 1. formats ----------------------------------------------------------------------
want = {"Color.png": (8, 2), "Bump16.png": (16, 0), "face_ids.png": (16, 0)}
V["png_headers"] = {}
for fn, (bd, ct) in want.items():
    hd = png_header(os.path.join(TEX_DIR, fn))
    ok = hd["width"] == C.W and hd["height"] == C.H and hd["bit_depth"] == bd and hd["colour_type"] == ct
    hd["ok"] = bool(ok)
    V["png_headers"][fn] = hd
    if not ok:
        fails.append("header %s %s" % (fn, hd))
print("headers", V["png_headers"])

col = np.asarray(Image.open(os.path.join(TEX_DIR, "Color.png")).convert("RGB")).astype(np.float64)
bimg = Image.open(os.path.join(TEX_DIR, "Bump16.png"))
bump = np.asarray(bimg).astype(np.float64)
fid = np.asarray(Image.open(os.path.join(TEX_DIR, "face_ids.png"))).astype(np.int64)
rep = json.load(open(os.path.join(TEX_DIR, "report.json")))
enc = rep["bump_encoding"]
hmm = enc["black_mm"] + bump / 65535.0 * (enc["white_mm"] - enc["black_mm"])
V["decoded"] = {"bump_mode": bimg.mode, "bump_min": int(bump.min()), "bump_max": int(bump.max()),
                "face_ids_unique": int(len(np.unique(fid)))}
if bump.max() <= 255:
    fails.append("bump decoded as 8-bit")
ids = np.unique(fid)
if not (ids[0] == 0 and np.array_equal(ids[1:], np.arange(1, 57))):
    fails.append("face ids not 0 + 1..56")

# ---------------- 2. wrap seam steps ---------------------------------------------------------------


def seam_steps(a, axis):
    """mean |step| across the wrap seam vs the mean |step| between adjacent interior lines."""
    if axis == 1:
        seam = np.abs(a[:, 0] - a[:, -1])
        inner = np.abs(np.diff(a, axis=1))
    else:
        seam = np.abs(a[0] - a[-1])
        inner = np.abs(np.diff(a, axis=0))
    s, i = float(seam.mean()), float(inner.mean())
    return {"seam_mean_step": round(s, 4), "interior_mean_step": round(i, 4), "ratio": round(s / i, 4),
            "seam_p99_step": round(float(np.percentile(seam, 99)), 4),
            "interior_p99_step": round(float(np.percentile(inner, 99)), 4)}


lum = col @ np.array([0.2126, 0.7152, 0.0722])
V["wrap"] = {"colour_luma_levels": {"left_right": seam_steps(lum, 1), "top_bottom": seam_steps(lum, 0)},
             "bump_16bit": {"left_right": seam_steps(bump, 1), "top_bottom": seam_steps(bump, 0)},
             "bump_mm": {"left_right": seam_steps(hmm, 1), "top_bottom": seam_steps(hmm, 0)}}


def matched_steps(a):
    """The left/right seam lies on the midline between an odd and an even column (x = 0), which
    crosses slanted joints; compare it with the interior odd|even midlines at x = 2, 4, 6 x W/8.
    The top/bottom seam lies on even columns' horizontal joints (y = 0); compare with y = k x H/7.
    Also compare steps between pixels of the same face (no joint in between) only."""
    out = {}
    xs = [int(round(m * C.PITCH_X)) for m in (2, 4, 6)]
    seam = np.abs(a[:, 0] - a[:, -1])
    inner = np.concatenate([np.abs(a[:, x] - a[:, x - 1]) for x in xs])
    same_s = (fid[:, 0] == fid[:, -1]) & (fid[:, 0] > 0)
    same_i = np.concatenate([(fid[:, x] == fid[:, x - 1]) & (fid[:, x] > 0) for x in xs])
    out["left_right"] = {"seam_mean": round(float(seam.mean()), 4), "matched_interior_mean": round(float(inner.mean()), 4),
                         "seam_p99": round(float(np.percentile(seam, 99)), 4),
                         "matched_interior_p99": round(float(np.percentile(inner, 99)), 4),
                         "within_face_seam_mean": round(float(seam[same_s].mean()), 4),
                         "within_face_interior_mean": round(float(inner[same_i].mean()), 4),
                         "within_face_ratio": round(float(seam[same_s].mean() / inner[same_i].mean()), 4)}
    ys = [int(round(k * C.PITCH_Y)) for k in range(1, C.NR)]
    seam = np.abs(a[0] - a[-1])
    inner = np.concatenate([np.abs(a[y] - a[y - 1]) for y in ys])
    same_s = (fid[0] == fid[-1]) & (fid[0] > 0)
    same_i = np.concatenate([(fid[y] == fid[y - 1]) & (fid[y] > 0) for y in ys])
    out["top_bottom"] = {"seam_mean": round(float(seam.mean()), 4), "matched_interior_mean": round(float(inner.mean()), 4),
                         "seam_p99": round(float(np.percentile(seam, 99)), 4),
                         "matched_interior_p99": round(float(np.percentile(inner, 99)), 4),
                         "within_face_seam_mean": round(float(seam[same_s].mean()), 4),
                         "within_face_interior_mean": round(float(inner[same_i].mean()), 4),
                         "within_face_ratio": round(float(seam[same_s].mean() / inner[same_i].mean()), 4)}
    return out


def adjacent_steps(a):
    """seam step vs the steps one pixel either side of it (same lattice position, offset by 1 px)."""
    lr = np.abs(a[:, 0] - a[:, -1]).mean()
    lr_adj = 0.5 * (np.abs(a[:, 1] - a[:, 0]).mean() + np.abs(a[:, -1] - a[:, -2]).mean())
    tb = np.abs(a[0] - a[-1]).mean()
    tb_adj = 0.5 * (np.abs(a[1] - a[0]).mean() + np.abs(a[-1] - a[-2]).mean())
    return {"left_right": {"seam_mean": round(float(lr), 4), "adjacent_mean": round(float(lr_adj), 4),
                           "ratio": round(float(lr / lr_adj), 4)},
            "top_bottom": {"seam_mean": round(float(tb), 4), "adjacent_mean": round(float(tb_adj), 4),
                           "ratio": round(float(tb / tb_adj), 4)}}


V["wrap_matched"] = {"colour_luma_levels": matched_steps(lum), "bump_mm": matched_steps(hmm)}
V["wrap_adjacent"] = {"colour_luma_levels": adjacent_steps(lum), "bump_mm": adjacent_steps(hmm),
                      "bump_16bit": adjacent_steps(bump)}
print("wrap adjacent", json.dumps(V["wrap_adjacent"]))
for k, d in V["wrap_matched"].items():
    for ax, st in d.items():
        if st["within_face_ratio"] > 1.5:
            fails.append("wrap %s %s within-face ratio %.2f" % (k, ax, st["within_face_ratio"]))
print("wrap", json.dumps(V["wrap"]["colour_luma_levels"]), json.dumps(V["wrap"]["bump_mm"]))
print("wrap matched", json.dumps(V["wrap_matched"]))

# ---------------- 3. joint width ---------------------------------------------------------------------
jm = fid == 0
# vertical runs of joint pixels on columns that cross horizontal joints away from vertices
runs = []
for x in range(0, C.W, 7):
    colj = jm[:, x]
    # wrap-aware run lengths
    rolled = np.roll(colj, -int(np.argmin(colj)))
    d = np.diff(np.r_[0, rolled.astype(np.int8), 0])
    st, en = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    runs.extend((en - st).tolist())
runs = np.array(runs)
frac = jm.mean()
implied = C.MODULE_F_IN * (1 - np.sqrt(1 - frac))          # joint width (in) implied by the joint area
V["joint"] = {"vertical_run_px_mode": int(np.bincount(runs).argmax()),
              "vertical_run_px_hist": {str(k): int(v) for k, v in enumerate(np.bincount(runs)) if v},
              "joint_area_fraction": round(float(frac), 5),
              "theoretical_area_fraction_1_8in": round(1 - (C.FLATS_IN / C.MODULE_F_IN) ** 2, 5),
              "implied_width_in": round(float(implied), 4), "implied_width_px": round(float(implied * 64), 3)}
if abs(implied - C.JOINT_IN) > 0.01:
    fails.append("joint width %.4f in" % implied)
print("joint", V["joint"])

# ---------------- 4. relief from Bump16 ----------------------------------------------------------
_, edge_d, _, _ = C.lattice_maps()
types = {f["index"]: f["type"] for f in rep["faces"]}
tarr = np.zeros(57, object)
for k, v in types.items():
    tarr[k] = v
ftype = tarr[fid]
joint_vals = hmm[jm]
core = jm & (edge_d < C.HALF_JOINT_PX - 0.5)
floor = float(np.median(hmm[core]))
V["relief"] = {"joint_floor_mm": round(floor, 4), "joint_core_max_mm": round(float(hmm[core].max()), 4),
               "joint_pixels_max_mm": round(float(joint_vals.max()), 4)}
ease_w_px = rep["relief_terms_mm"]["edge_ease_width"] / C.MM_PER_PX
interior = (~jm) & (edge_d >= C.HALF_JOINT_PX + ease_w_px)
for t in ("matte", "raw", "chiseled"):
    m = (ftype == t) & interior
    mall = (ftype == t) & (~jm)
    v = hmm[m]
    lo, hi = np.percentile(v, [0.1, 99.9])
    V["relief"][t] = {"pattern_relief_mm_p0.1_p99.9": round(float(hi - lo), 4),
                      "pattern_max_mm": round(float(v.max()), 4), "pattern_min_mm": round(float(v.min()), 4),
                      "pattern_std_mm": round(float(v.std()), 4),
                      "deepest_face_pixel_incl_edge_mm": round(float(hmm[mall].min()), 4),
                      "clearance_pattern_to_joint_floor_mm": round(float(v.min() - floor), 4),
                      "clearance_any_face_pixel_to_joint_floor_mm": round(float(hmm[mall].min() - floor), 4)}
    if hmm[mall].min() - floor <= 0:
        fails.append("clearance %s" % t)
V["relief"]["joint_depth_below_face_plane_mm"] = round(-floor, 4)
print("relief", json.dumps(V["relief"], indent=0))

# ---------------- 5. mix ----------------------------------------------------------------------------
cnt = {t: sum(1 for f in rep["faces"] if f["type"] == t) for t in ("matte", "raw", "chiseled")}
orient = {}
for f in rep["faces"]:
    if f["type"] == "chiseled":
        orient[str(f["groove_angle_image_deg"])] = orient.get(str(f["groove_angle_image_deg"]), 0) + 1
V["mix"] = {"counts": cnt, "fractions": {k: round(v / 56, 4) for k, v in cnt.items()},
            "render_fractions_fully_visible": rep["mix_ratio_render"]["fraction"], "chiseled_orientations": orient}
print("mix", V["mix"])

# ---------------- 6. Raw repetition ---------------------------------------------------------------
# half resolution (32 px/in, close to the render's 31.08 px/in) height field
H2, W2 = C.H // 2, C.W // 2


def half(a):
    return a[:2 * H2, :2 * W2].reshape(H2, 2, W2, 2).mean(axis=(1, 3))


hh = half(hmm)
fh = fid[0:2 * H2:2, 0:2 * W2:2]
ed2 = edge_d[0:2 * H2:2, 0:2 * W2:2] / 2.0
cen = C.face_centres() / 2.0
raw_faces = [f["index"] for f in rep["faces"] if f["type"] == "raw"]
Hh, Wh = hh.shape


def dihedral(img, k):
    """12 symmetries of the flat-top hexagon applied to a square patch centred on the face centre:
    rotation by 60*(k%6) deg, mirrored (x -> -x) if k >= 6."""
    ang = 60.0 * (k % 6)
    out = img[:, ::-1] if k >= 6 else img
    return ndi.rotate(out, ang, reshape=False, order=1, mode="nearest")


r_in = 136                                          # half-res px (4.25 in): inside the face, away from the ease
yy, xx = np.mgrid[-r_in:r_in + 1, -r_in:r_in + 1]
hexm = (np.abs(yy) <= r_in * 0.86) & (np.abs(xx) * np.sqrt(3) / 2 + np.abs(yy) / 2 <= r_in * 0.86)
patches = {}
for n in raw_faces:
    cx, cy = cen[n - 1]
    ys = (np.arange(-r_in, r_in + 1) + int(round(cy - 0.5))) % Hh
    xs = (np.arange(-r_in, r_in + 1) + int(round(cx - 0.5))) % Wh
    patches[n] = hh[np.ix_(ys, xs)]


def ncc(a, b, m):
    a, b = a[m] - a[m].mean(), b[m] - b[m].mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-12))


pair_max = []
for i, a in enumerate(raw_faces):
    for b in raw_faces[i + 1:]:
        best = max(ncc(patches[a], dihedral(patches[b], k), hexm) for k in range(12))
        pair_max.append((best, a, b))
pair_max.sort(reverse=True)
V["raw_repetition"] = {"whole_face_ncc_max_over_12_transforms": {
    "max": round(pair_max[0][0], 4), "pair": pair_max[0][1:], "median": round(float(np.median([p[0] for p in pair_max])), 4),
    "pairs": len(pair_max)}}
print("raw whole-face NCC max %.3f (faces %s), median %.3f" % (pair_max[0][0], pair_max[0][1:], np.median([p[0] for p in pair_max])))

# random-window search: windows from raw faces searched over every raw-face pixel of the atlas
# (other faces, and the same face beyond one window width), under the 12 transforms
rng = np.random.default_rng(7)
raw_mask = np.isin(fh, raw_faces) & (ed2 > 3 + ease_w_px / 2)
img = hh - ndi.uniform_filter(hh, 64, mode="wrap")         # remove slow tilt so NCC sees texture


def window_search(wsz, nwin):
    ones = np.ones((wsz, wsz))
    F_img = np.fft.rfft2(img)
    s1 = fftconvolve(np.pad(img, ((0, wsz), (0, wsz)), mode="wrap"), ones, mode="valid")[:Hh, :Wh]
    s2 = fftconvolve(np.pad(img * img, ((0, wsz), (0, wsz)), mode="wrap"), ones, mode="valid")[:Hh, :Wh]
    n = wsz * wsz
    den_img = np.sqrt(np.maximum(s2 - s1 * s1 / n, 1e-9))
    # a window position (top-left) is admissible when the whole window lies in raw-face interior
    adm = fftconvolve(np.pad(raw_mask.astype(float), ((0, wsz), (0, wsz)), mode="wrap"), ones, mode="valid")[:Hh, :Wh] > n - 0.5
    adm[Hh - wsz:, :] = False            # half-res image drops one column of the odd width: no wrapping windows
    adm[:, Wh - wsz:] = False
    ys, xs = np.nonzero(adm)
    res = []
    for w in range(nwin):
        i = rng.integers(0, len(ys))
        y0, x0 = ys[i], xs[i]
        src_face = fh[(y0 + wsz // 2) % Hh, (x0 + wsz // 2) % Wh]
        tpl0 = img[np.ix_((np.arange(wsz) + y0) % Hh, (np.arange(wsz) + x0) % Wh)]
        # exclude the window's own neighbourhood (within one window width) and inadmissible positions
        dy = np.abs(((np.arange(Hh) - y0 + Hh // 2) % Hh) - Hh // 2)
        dx = np.abs(((np.arange(Wh) - x0 + Wh // 2) % Wh) - Wh // 2)
        ok = adm & ~((dy[:, None] < wsz) & (dx[None, :] < wsz))
        best = (-1, None)
        for k in range(12):
            if k == 0:
                tpl = tpl0
            else:
                big = img[np.ix_((np.arange(2 * wsz) + y0 - wsz // 2) % Hh, (np.arange(2 * wsz) + x0 - wsz // 2) % Wh)]
                tpl = dihedral(big, k)[wsz // 2:wsz // 2 + wsz, wsz // 2:wsz // 2 + wsz]
            t = tpl - tpl.mean()
            t = t / np.sqrt((t * t).sum() + 1e-12)
            tp = np.zeros_like(img)
            tp[:wsz, :wsz] = t
            corr = np.fft.irfft2(F_img * np.conj(np.fft.rfft2(tp)), s=img.shape)
            nc = corr / den_img
            v = np.where(ok, nc, -1)
            j = int(np.argmax(v))
            if v.flat[j] > best[0]:
                best = (float(v.flat[j]), (k, int(j // Wh), int(j % Wh), int(fh[(j // Wh + wsz // 2) % Hh, (j % Wh + wsz // 2) % Wh])))
        res.append((best[0], int(src_face), best[1]))
    vals = np.array([r[0] for r in res])
    return {"window_in": wsz / 32.0, "windows": nwin, "max_ncc": round(float(vals.max()), 4),
            "p95_ncc": round(float(np.percentile(vals, 95)), 4), "median_ncc": round(float(np.median(vals)), 4),
            "windows_over_0.9": int((vals > 0.9).sum()), "windows_over_0.8": int((vals > 0.8).sum()),
            "worst": sorted(res, key=lambda r: -r[0])[:3]}


for wsz, nw in ((16, 24), (32, 24), (64, 24)):
    r = window_search(wsz, nw)
    V["raw_repetition"]["window_%.1fin" % (wsz / 32.0)] = r
    print("raw window %.0f in: max %.3f p95 %.3f median %.3f  >0.9: %d  >0.8: %d" % (
        r["window_in"], r["max_ncc"], r["p95_ncc"], r["median_ncc"], r["windows_over_0.9"], r["windows_over_0.8"]))

# ---------------- 7. ghost joint lines inside faces --------------------------------------------------
l2 = half(lum)
dark = np.clip(ndi.gaussian_filter(l2, 2.0) - l2, 0, None)
L = 31
resp = []
for ang in (0, 60, 120):
    k = np.zeros((L, L))
    c = L // 2
    for t in np.linspace(-c, c, 4 * L):
        k[int(round(c + t * np.sin(np.radians(ang)))), int(round(c + t * np.cos(np.radians(ang))))] = 1
    k /= k.sum()
    resp.append(fftconvolve(np.pad(dark, c, mode="wrap"), k, mode="valid"))
resp = np.max(resp, axis=0)
on_joint = resp[(fh == 0)]
ftype2 = tarr[fh]
inside = (fh > 0) & (ed2 > 12) & ((ftype2 == "matte") | (ftype2 == "raw"))
inside_ch = (fh > 0) & (ed2 > 12) & (ftype2 == "chiseled")
V["ghost_joint_check"] = {"joint_line_response_median": round(float(np.median(on_joint)), 3),
                          "matte_raw_inside_response_p99.99": round(float(np.percentile(resp[inside], 99.99)), 3),
                          "matte_raw_inside_response_max": round(float(resp[inside].max()), 3),
                          "chiseled_inside_response_max": round(float(resp[inside_ch].max()), 3),
                          "note": "oriented (0/60/120 deg, 1 in) dark-line filter on colour luma; a copied render joint "
                                  "inside a Matte or Raw face would score near the joint median. Chiseled faces are "
                                  "listed separately: their 30/90/150 deg grooves partly excite the filter."}
if resp[inside].max() > 0.6 * np.median(on_joint):
    fails.append("possible ghost joint inside a Matte/Raw face")
print("ghost", V["ghost_joint_check"])

V["hard_failures"] = fails
rep["verification"] = V
# top-level summaries, measured from the PNG files
rep["wrap_seam_steps"] = {
    "method": "mean |difference| between the last and first pixel line of the image (the wrap seam) vs the mean "
              "|difference| one pixel either side of the seam; ratio ~1 means no seam",
    "colour_luma_8bit_levels": V["wrap_adjacent"]["colour_luma_levels"],
    "bump_16bit": V["wrap_adjacent"]["bump_16bit"], "bump_mm": V["wrap_adjacent"]["bump_mm"],
    "within_face_vs_matched_interior": {k: {ax: v["within_face_ratio"] for ax, v in d.items()}
                                        for k, d in V["wrap_matched"].items()}}
R_ = V["relief"]
rep["relief_mm"] = {
    "joint_depth_below_face_plane": R_["joint_depth_below_face_plane_mm"],
    "pattern_relief_p0.1_p99.9": {t: R_[t]["pattern_relief_mm_p0.1_p99.9"] for t in ("matte", "raw", "chiseled")},
    "deepest_pattern_point": {t: R_[t]["pattern_min_mm"] for t in ("matte", "raw", "chiseled")},
    "clearance_deepest_pattern_to_joint_floor": {t: R_[t]["clearance_pattern_to_joint_floor_mm"] for t in ("matte", "raw", "chiseled")},
    "clearance_any_face_pixel_incl_edge_ease_to_joint_floor": {t: R_[t]["clearance_any_face_pixel_to_joint_floor_mm"]
                                                               for t in ("matte", "raw", "chiseled")},
    "note": "decoded from Bump16.png with report['bump_encoding']; pattern = face pixels beyond the 1.2 mm edge "
            "ease; joint floor = median of joint-core pixels"}
write_text(os.path.join(TEX_DIR, "report.json"), json.dumps(rep, indent=1, default=lambda o: o if not isinstance(o, np.integer) else int(o)))
if fails:
    print("FAIL:", fails)
    sys.exit(1)
print("verification passed hard gates")
