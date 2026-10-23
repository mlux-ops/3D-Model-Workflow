# -*- coding: utf-8 -*-
"""Numeric side-view fidelity: registers my hosted no-disc side render onto the matte-white side photo
(scale + shift from the backplate height and back face only; nothing else is fitted) and compares
straight-line and circle fits of the silhouettes. All lengths in inches (photo px/in from the 5.25 in backplate).
Writes _work/side_metrics.json."""
import json
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe

ROOT = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce"
RUN = ROOT + "/max"

ph = Image.open(ROOT + "/inputs/KW1041_MWT_side_reference.jpg").convert("RGB")
mi = Image.open(RUN + "/views/hosted_no_disc_side.png").convert("RGB")


def mask_of(im, thr=250):
    return np.asarray(im).astype(int).min(axis=2) < thr


def plate_extent(mask):
    cnt = mask.sum(axis=0)
    first = int(np.nonzero(cnt >= 0.75 * cnt.max())[0].min())
    top, bot = None, None
    for x in range(first, first + 80):
        col = np.nonzero(mask[:, x])[0]
        if len(col):
            top = col.min() if top is None else min(top, col.min())
            bot = col.max() if bot is None else max(bot, col.max())
    return first, top, bot


mp = mask_of(ph)
mm0 = mask_of(mi)
x0p, tp, bp_ = plate_extent(mp)
x0m, tm, bm = plate_extent(mm0)
s = (bp_ - tp + 1) / float(bm - tm + 1)
ycp = (tp + bp_) / 2.0
ycm = (tm + bm) / 2.0
pxin = (bp_ - tp + 1) / 5.25
w, h = mi.size
mi2 = mi.resize((int(round(w * s)), int(round(h * s))), Image.LANCZOS)
canvas = Image.new("RGB", ph.size, (255, 255, 255))
canvas.paste(mi2, (int(round(x0p - x0m * s)), int(round(ycp - ycm * s))))
mm = mask_of(canvas)

res = {"photo_px_per_in": pxin, "scale": s, "backplate_back_face_x_px": x0p, "backplate_center_row_px": ycp}
inter = np.logical_and(mp, mm).sum()
union = np.logical_or(mp, mm).sum()
res["silhouette_iou"] = inter / float(union)
print("registration scale %.4f, photo px/in %.2f, silhouette IoU %.4f" % (s, pxin, res["silhouette_iou"]))


def col_top(mask, x):
    ys = np.nonzero(mask[:, x])[0]
    return ys.min() if len(ys) else None


def col_bot(mask, x):
    ys = np.nonzero(mask[:, x])[0]
    return ys.max() if len(ys) else None


def row_right(mask, y):
    xs = np.nonzero(mask[y])[0]
    return xs.max() if len(xs) else None


def fit_line(xs, ys):
    A = np.c_[xs, np.ones(len(xs))]
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    return coef


def fit_circle(x, y):
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x * x + y * y
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0], c[1]
    r = np.sqrt(c[2] + cx * cx + cy * cy)
    resid = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r
    return cx, cy, r, np.abs(resid).max()


# flat top / bottom edges of the body: columns between the plate and 640 px in front of it
xs_top = list(range(x0p + 120, x0p + 600, 10))
xs_bot = list(range(x0p + 100, x0p + 300, 10))
top_p = np.array([col_top(mp, x) for x in xs_top], float)
top_m = np.array([col_top(mm, x) for x in xs_top], float)
bot_p = np.array([col_bot(mp, x) for x in xs_bot], float)
bot_m = np.array([col_bot(mm, x) for x in xs_bot], float)
res["body_top_edge_row_px"] = [float(np.median(top_p)), float(np.median(top_m))]
res["body_bottom_edge_row_px"] = [float(np.median(bot_p)), float(np.median(bot_m))]
d_top = (np.median(top_m) - np.median(top_p)) / pxin
d_bot = (np.median(bot_m) - np.median(bot_p)) / pxin
dia_p = (np.median(bot_p) - np.median(top_p) + 1) / pxin
dia_m = (np.median(bot_m) - np.median(top_m) + 1) / pxin
print("body flat edges: top deviation (mine-photo) %.3f in, bottom %.3f in; body diameter photo %.3f in, mine %.3f in" % (d_top, d_bot, dia_p, dia_m))
res["body_top_dev_in"] = float(d_top)
res["body_bottom_dev_in"] = float(d_bot)
res["body_diameter_in"] = {"photo": float(dia_p), "mine": float(dia_m)}
top_flat_p, top_flat_m = np.median(top_p), np.median(top_m)
bot_flat_p, bot_flat_m = np.median(bot_p), np.median(bot_m)

# upper cut-face edge: rightmost silhouette x per row between the flat top and the globe start
y_globe_start = int(min(np.nonzero(mp[:, x0p + int(0.8 * (np.nonzero(mp.any(axis=0))[0].max() - x0p)):].any(axis=1))[0].min(), 900))
lines = {}
for name, mask, flat in (("photo", mp, top_flat_p), ("mine", mm, top_flat_m)):
    rows = np.arange(int(flat) + 30, min(y_globe_start, int(flat) + 190), 4)
    xr = np.array([row_right(mask, y) for y in rows], float)
    a, b = fit_line(rows.astype(float), xr)
    ang = np.degrees(np.arctan(abs(a)))
    lines[name] = (a, b, ang)
    print("upper cut-face edge (%s): rows %d..%d, x = %.4f*y + %.1f -> %.2f deg from vertical" % (name, rows[0], rows[-1], a, b, ang))
xref = 800.0
xp_ref = lines["photo"][0] * xref + lines["photo"][1]
xm_ref = lines["mine"][0] * xref + lines["mine"][1]
print("  upper edge x at row 800: photo %.1f mine %.1f -> mine - photo %.3f in" % (xp_ref, xm_ref, (xm_ref - xp_ref) / pxin))
res["upper_cut_face"] = {"angle_deg": {"photo": float(lines["photo"][2]), "mine": float(lines["mine"][2])},
                         "x_at_row800_dev_in": float((xm_ref - xp_ref) / pxin)}

# lower cut-face edge: bottom silhouette row per column in the sloped part
lines2 = {}
for name, mask, flat in (("photo", mp, bot_flat_p), ("mine", mm, bot_flat_m)):
    xs2 = np.arange(x0p + 300, x0p + 900, 2)
    yb = np.array([col_bot(mask, x) if col_bot(mask, x) is not None else -1 for x in xs2], float)
    sel = (yb < flat - 30) & (yb > flat - 200)
    idx = np.nonzero(sel)[0]
    # contiguous run starting at the first selected column
    run = [idx[0]]
    for i in idx[1:]:
        if i == run[-1] + 1:
            run.append(i)
        else:
            break
    xs_run = xs2[run].astype(float)
    ys_run = yb[run]
    c, d0 = fit_line(xs_run, ys_run)
    ang = np.degrees(np.arctan(1.0 / abs(c)))
    lines2[name] = (c, d0, ang, xs_run[0], xs_run[-1])
    print("lower cut-face edge (%s): cols %d..%d, y = %.3f*x + %.1f -> %.2f deg from vertical" % (name, xs_run[0], xs_run[-1], c, d0, ang))
yref = flat_ref = 1600.0
xp_l = (yref - lines2["photo"][1]) / lines2["photo"][0]
xm_l = (yref - lines2["mine"][1]) / lines2["mine"][0]
print("  lower edge x at row 1600: photo %.1f mine %.1f -> mine - photo %.3f in" % (xp_l, xm_l, (xm_l - xp_l) / pxin))
res["lower_cut_face"] = {"angle_deg": {"photo": float(lines2["photo"][2]), "mine": float(lines2["mine"][2])},
                         "x_at_row1600_dev_in": float((xm_l - xp_l) / pxin)}

# globe: circle fit to the right boundary (rightmost silhouette pixel per row)
x_far_p = np.nonzero(mp.any(axis=0))[0].max()
circ = {}
for name, mask in (("photo", mp), ("mine", mm)):
    x_far = np.nonzero(mask.any(axis=0))[0].max()
    rows_all = np.arange(0, mask.shape[0])
    xr_all = np.array([row_right(mask, y) if row_right(mask, y) is not None else -1 for y in rows_all], float)
    sel = xr_all >= x_far - 1.2 * pxin
    rows = rows_all[sel][3:-3][::3]
    xr = xr_all[sel][3:-3][::3]
    cx, cy, r, rmax = fit_circle(xr, rows.astype(float))
    circ[name] = (cx, cy, r, rmax)
    print("globe right-boundary circle (%s): centre (%.1f, %.1f) r %.1f px = %.3f in dia %.3f in; max residual %.1f px" % (
        name, cx, cy, r, r / pxin, 2 * r / pxin, rmax))
cxp, cyp, rp, _ = circ["photo"]
cxm, cym, rm, _ = circ["mine"]
print("  globe centre from plate back face, along wall normal: photo %.3f in mine %.3f in (mine - photo %.3f)" % (
    (cxp - x0p) / pxin, (cxm - x0p) / pxin, (cxm - cxp) / pxin))
print("  globe centre height above plate centre: photo %.3f in mine %.3f in (mine - photo %.3f)" % (
    (ycp - cyp) / pxin, (ycp - cym) / pxin, (cyp - cym) / pxin * -1 if False else (cyp - cym) / pxin))
res["globe_circle_fit"] = {
    "photo": {"diameter_in": float(2 * rp / pxin), "centre_out_from_back_face_in": float((cxp - x0p) / pxin),
              "centre_below_plate_centre_in": float((cyp - ycp) / pxin)},
    "mine": {"diameter_in": float(2 * rm / pxin), "centre_out_from_back_face_in": float((cxm - x0p) / pxin),
             "centre_below_plate_centre_in": float((cym - ycp) / pxin)},
}
res["far_right_x_dev_in"] = float((np.nonzero(mm.any(axis=0))[0].max() - x_far_p) / pxin)
res["depth_in"] = {"photo": float((x_far_p - x0p + 1) / pxin), "mine": float((np.nonzero(mm.any(axis=0))[0].max() - x0p + 1) / pxin)}
print("overall depth from back face: photo %.3f in, mine %.3f in" % (res["depth_in"]["photo"], res["depth_in"]["mine"]))

# backplate thickness: columns where the silhouette height is above 95 percent of the plate height
thk_px = {}
for name, mask in (("photo", mp), ("mine", mm)):
    cnt = mask.sum(axis=0)
    ph_ = cnt.max()
    cols = np.nonzero(cnt >= 0.9 * ph_)[0]
    run = [cols[0]]
    for c_ in cols[1:]:
        if c_ == run[-1] + 1:
            run.append(c_)
        else:
            break
    thk_px[name] = len(run)
    print("backplate thickness (%s): %d px = %.3f in" % (name, len(run), len(run) / pxin))
    res.setdefault("backplate_thickness_in", {})[name] = float(len(run) / pxin)

# same comparison with both registered on the backplate FRONT face instead of the back face
shift = (thk_px["photo"] - thk_px["mine"]) / pxin
print("plate thickness difference (photo - mine) %.3f in" % shift)
rel = {
    "plate_thickness_difference_in": float(shift),
    "upper_cut_face_x_dev_in": float((xm_ref - xp_ref) / pxin + shift),
    "lower_cut_face_x_dev_in": float((xm_l - xp_l) / pxin + shift),
    "globe_centre_out_from_plate_front_in": {
        "photo": float((cxp - x0p - thk_px["photo"]) / pxin),
        "mine": float((cxm - x0p - thk_px["mine"]) / pxin)},
    "depth_from_plate_front_in": {
        "photo": float((x_far_p - x0p - thk_px["photo"] + 1) / pxin),
        "mine": float((np.nonzero(mm.any(axis=0))[0].max() - x0p - thk_px["mine"] + 1) / pxin)},
}
res["registered_on_plate_front_face"] = rel
print("REGISTERED ON PLATE FRONT FACE:")
print("  upper cut-face x deviation (mine - photo) %.3f in ; lower %.3f in" % (rel["upper_cut_face_x_dev_in"], rel["lower_cut_face_x_dev_in"]))
print("  globe centre out from plate front: photo %.3f in mine %.3f in" % (
    rel["globe_centre_out_from_plate_front_in"]["photo"], rel["globe_centre_out_from_plate_front_in"]["mine"]))
print("  depth from plate front: photo %.3f in mine %.3f in" % (
    rel["depth_from_plate_front_in"]["photo"], rel["depth_from_plate_front_in"]["mine"]))

res["note"] = "registration: scale and vertical centre from backplate height, x from back face; nothing else fitted"
with open(safe(RUN + "/_work/side_metrics.json"), "w") as f:
    json.dump(res, f, indent=1)
print("wrote _work/side_metrics.json")
