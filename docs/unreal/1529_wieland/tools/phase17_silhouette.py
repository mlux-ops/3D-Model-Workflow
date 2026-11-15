"""Phase 17: compare the modelled skyline with a freely licensed photograph taken from the north.

Usage:
    python -B -P phase17_silhouette.py <photo> <lat> <lon> <eye m above ground> <hfov guess deg> <yaw guess deg> <out prefix>
                                       [sky threshold 30] [crop top px 0] [crop bottom px 0]

1. Model skyline as seen from the photo's position: every tower and Zone 3 mesh of phase17_towers.py (vertices
   and points along every triangle edge), back to true heights (the D1 curvature drop added back) and lowered by the
   drop seen from the photo's position; for each azimuth (0.01 degree bins) the highest elevation angle.
2. Photo skyline: per image column, the first row from the top whose colour departs from the sky colour of that
   column (median of the top rows) by more than the threshold, after a 3 by 3 median filter.
3. Camera: yaw (map azimuth of the image centre, degrees east of north), pitch, roll and horizontal field of view,
   by a coarse search of yaw and field of view, then Nelder-Mead on all four, minimising the median absolute row
   difference over columns where both skylines exist (robust to trees and foreground in the photograph).
4. Tower tops: for each tower beyond 1 km and at least 120 m, the model top (highest vertex) is projected; the
   photo's skyline peak within 0.4 degree of it gives the photographed top; the angular error is reported in
   elevation (and azimuth), in degrees and in metres at the tower's distance.
Writes <out prefix>_overlay.png (photo, the photo skyline in cyan, the solved model skyline in magenta, tower tops
labelled) and <out prefix>_tops.csv, and prints the camera and the error summary.
"""

import csv
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

FT = 0.3048006096
FRAME = os.path.join(HERE, "..", "review", "phase2", "level_frame.json")
D1 = (-1300.0, -1560.0, 1684.0)
K = 0.13
R = 6371000.0
MESHES = os.environ.get("P17_TOWER_MESHES", "E:/Wieland1529_site_data/phase17/meshes_towers_clean")  # clean roofs from J23
MATS = "E:/Wieland1529_site_data/phase17/tower_materials.csv"
DTM = "E:/Wieland1529_site_data/phase17/rasters/view6ft_dtm.npz"


def affine(frame):
    """Level (cm) -> map (feet), as a 3x3 linear part and an offset, from three evaluated points."""
    o = np.array(frame.map_from_level(0.0, 0.0) + (0.0,))
    a = np.array(frame.map_from_level(100000.0, 0.0) + (0.0,)) - o
    b = np.array(frame.map_from_level(0.0, 100000.0) + (0.0,)) - o
    M = np.zeros((3, 3))
    M[:, 0] = a / 100000.0
    M[:, 1] = b / 100000.0
    zf = frame.level_from_map(o[0], o[1], 0.0)[2]
    return M, o, zf


def model_points(frame):
    M, o, z0cm = affine(frame)
    d1e, d1n = frame.map_from_level(D1[0], D1[1])
    pts, owner = [], []
    recs = {json.loads(l)["name"]: json.loads(l) for l in open(os.path.join(MESHES, "towers_record.jsonl"), encoding="utf-8")}
    for path in sorted(glob.glob(os.path.join(MESHES, "P17*_*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        v = np.asarray(d["vertices"], np.float64) + np.asarray(d["pivot"])
        t = np.asarray(d["triangles"], np.int64)
        # vertices plus three points on each edge
        e = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            for f in (0.25, 0.5, 0.75):
                e.append(v[t[:, i]] * (1 - f) + v[t[:, j]] * f)
        allp = np.vstack([v] + e)
        en = allp[:, :2] @ M[:2, :2].T + o[:2]
        z_ft = (allp[:, 2] - z0cm) / 30.48006096  # height in feet above the level datum
        dist = np.hypot(en[:, 0] - d1e, en[:, 1] - d1n) * FT
        z_ft = z_ft + dist * dist / (2 * R) * (1 - K) / FT  # true height (D1 drop added back)
        pts.append(np.column_stack([en, z_ft]))
        owner.append(np.full(len(allp), int(d["name"].split("_")[1])))
    return np.vstack(pts), np.concatenate(owner), frame


def main(argv):
    photo, lat, lon, eye_m, hfov0, yaw0, prefix = argv[1], float(argv[2]), float(argv[3]), float(argv[4]), float(argv[5]), float(argv[6]), argv[7]
    thr = float(argv[8]) if len(argv) > 8 else 30.0
    crop_top = int(argv[9]) if len(argv) > 9 else 0
    crop_bot = int(argv[10]) if len(argv) > 10 else 0
    frame = g.LevelFrame.load(FRAME)
    ce, cn = g.state_plane_from_lat_lon(lat, lon)
    dtm = np.load(DTM)
    r = int((float(dtm["y1"]) - cn) / float(dtm["cell"]))
    c = int((ce - float(dtm["x0"])) / float(dtm["cell"]))
    ground_ft = float(np.nanmedian(dtm["z"][max(r - 2, 0):r + 3, max(c - 2, 0):c + 3]))
    # Model heights from model_points are feet above NAVD 88 (map elevation 0), like the ground model.
    cam_z_ft = ground_ft + eye_m / FT
    P, owner, _ = model_points(frame)
    de, dn = P[:, 0] - ce, P[:, 1] - cn
    dist_ft = np.hypot(de, dn)
    keep = dist_ft > 300
    de, dn, dist_ft, P, owner = de[keep], dn[keep], dist_ft[keep], P[keep], owner[keep]
    drop_ft = (dist_ft * FT) ** 2 / (2 * R) * (1 - K) / FT
    az = (np.degrees(np.arctan2(de, dn)) + 360.0) % 360.0          # grid azimuth, degrees east of grid north
    el = np.degrees(np.arctan2(P[:, 2] - drop_ft - cam_z_ft, dist_ft))
    # Grid north to true north: the State Plane grid is rotated by the convergence angle at the camera.
    conv = g.convergence_and_scale(lat, lon)[0]
    az = (az + conv) % 360.0
    bins = np.round(az * 100).astype(int)
    env = np.full(36000, -90.0)
    np.maximum.at(env, bins % 36000, el)
    tower_top = {}
    order = np.argsort(-el)
    for i in order:
        o_ = int(owner[i])
        if o_ not in tower_top:
            tower_top[o_] = (float(az[i]), float(el[i]), float(dist_ft[i] * FT))

    img = Image.open(photo).convert("RGB")
    orig_h = img.height
    if crop_top or crop_bot:
        img = img.crop((0, crop_top, img.width, img.height - crop_bot))
    scale = 1.0
    if img.width > 3000:
        scale = 3000.0 / img.width
        img = img.resize((3000, int(img.height * scale)))
    a = np.asarray(img).astype(np.float64)
    # principal point: the centre of the original photograph, wherever it was cropped
    cy = (orig_h / 2.0 - crop_top) * scale
    a = ndimage.median_filter(a, size=(3, 3, 1))
    H, W = a.shape[:2]
    # Sky edge: twilight skies change colour from top to bottom, so each pixel is compared with the smoothed sky a
    # few rows above it (not with the top rows), and the edge must persist for several rows (stars, aircraft and
    # sensor noise do not).
    s = ndimage.gaussian_filter(a, sigma=(2.0, 2.0, 0))
    gap, run = 8, 6
    diff = np.zeros((H, W))
    diff[gap:] = np.sqrt(((s[gap:] - s[:-gap]) ** 2).sum(axis=2))
    bad = diff > thr
    ref = np.roll(s, gap, axis=0)  # ref[r] = the sky gap rows above row r
    for k in range(1, run):
        bad &= np.sqrt(((np.roll(s, -k, axis=0) - ref) ** 2).sum(axis=2)) > thr
    bad[: max(gap + 2, H // 40)] = False
    first = np.where(bad.any(axis=0), bad.argmax(axis=0), -1).astype(float)
    first[first <= 2] = np.nan
    first[first < 0] = np.nan

    def predicted(params):
        yaw, pitch, roll, hfov = params
        f = (W / 2.0) / math.tan(math.radians(hfov) / 2.0)
        u = np.arange(W) - W / 2.0
        az_u = (yaw + np.degrees(np.arctan(u / f))) % 360.0
        e_u = env[np.round(az_u * 100).astype(int) % 36000]
        # pinhole: row from elevation, with the column's distance from the centre
        dx = np.radians(az_u - yaw)
        rows = cy - f * np.tan(np.radians(e_u) - math.radians(pitch)) / np.cos(dx) + u * math.tan(math.radians(roll))
        rows[e_u <= -89] = np.nan
        return rows

    def cost(params):
        pr = predicted(params)
        ok = np.isfinite(pr) & np.isfinite(first)
        if ok.sum() < W * 0.2:
            return 1e6
        return float(np.median(np.abs(pr[ok] - first[ok])))

    landmarks = os.environ.get("P17_LANDMARKS", "")
    if landmarks:
        # Camera lined up by landmarks instead of by the whole skyline (the photograph's near buildings are not in
        # the model): P17_LANDMARKS="<county id>:<column>,<county id>:<column>" gives the horizontal centre of two
        # towers in the original photograph's pixels; P17_HORIZON="<row>" the lake horizon row there. The towers'
        # model azimuths (mean over their vertices) fix yaw and field of view; the horizon (true dip from the eye
        # height, with refraction) fixes pitch; roll 0. Every tower top is then an independent measurement.
        cen = {}
        for o_ in np.unique(owner):
            m = owner == o_
            zs = P[m, 2]
            m = m & (P[:, 2] >= 0.85 * np.percentile(zs, 95))  # the tower's upper part, not its podium
            cen[int(o_)] = math.degrees(math.atan2(np.mean(np.sin(np.radians(az[m]))), np.mean(np.cos(np.radians(az[m]))))) % 360
        lm = [(int(x.split(":")[0]), float(x.split(":")[1]) * scale) for x in landmarks.split(",")]
        (id1, u1), (id2, u2) = lm[:2]
        a1, a2 = cen[id1], cen[id2]

        def lm_err(params):
            yaw_, hf_ = params
            f_ = (W / 2.0) / math.tan(math.radians(hf_) / 2.0)
            e1 = W / 2.0 + f_ * math.tan(math.radians(((a1 - yaw_ + 180) % 360) - 180)) - u1
            e2 = W / 2.0 + f_ * math.tan(math.radians(((a2 - yaw_ + 180) % 360) - 180)) - u2
            return e1 * e1 + e2 * e2
        sol = optimize.minimize(lm_err, (yaw0, hfov0), method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 8000})
        yaw, hfov = sol.x
        f0 = (W / 2.0) / math.tan(math.radians(hfov) / 2.0)
        v_h = (float(os.environ["P17_HORIZON"]) - crop_top) * scale
        dip = -math.degrees(math.sqrt(2 * eye_m * (1 - K) / R))
        if os.environ.get("P17_HORIZON_DIST_M"):
            # the row given is a far shore's water line at this distance, not the open-lake horizon
            dh = float(os.environ["P17_HORIZON_DIST_M"])
            dip = -math.degrees(eye_m / dh + dh * (1 - K) / (2 * R))
        pitch = dip - math.degrees(math.atan((cy - v_h) / f0))
        roll = 0.0

        class _R:
            pass
        res = _R()
        res.x = (yaw, pitch, roll, hfov)
        res.fun = cost(res.x)
    else:
        best = None
        for yaw in np.arange(yaw0 - 25, yaw0 + 25, 0.25):
            for hf in np.arange(max(5.0, hfov0 * 0.6), hfov0 * 1.4, max(0.5, hfov0 * 0.04)):
                for pitch in (-2.0, 0.0, 2.0, 4.0):
                    cst = cost((yaw, pitch, 0.0, hf))
                    if best is None or cst < best[0]:
                        best = (cst, (yaw, pitch, 0.0, hf))
        res = optimize.minimize(cost, best[1], method="Nelder-Mead", options={"xatol": 1e-3, "fatol": 1e-3, "maxiter": 4000})
        yaw, pitch, roll, hfov = res.x
    f = (W / 2.0) / math.tan(math.radians(hfov) / 2.0)
    pr = predicted(res.x)
    names = {r_["bldg_id"]: r_["name"] for r_ in csv.DictReader(open(MATS, encoding="utf-8"))}
    recs = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(MESHES, "towers_record.jsonl"), encoding="utf-8")}
    rows_out = []
    draw = ImageDraw.Draw(img)
    for u in range(W - 1):
        if np.isfinite(first[u]) and np.isfinite(first[u + 1]):
            draw.line([(u, first[u]), (u + 1, first[u + 1])], fill=(0, 255, 255), width=1)
        if np.isfinite(pr[u]) and np.isfinite(pr[u + 1]):
            draw.line([(u, pr[u]), (u + 1, pr[u + 1])], fill=(255, 0, 255), width=1)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for bid, (taz, tel, tdist) in tower_top.items():
        rec = recs.get(str(bid))
        if rec is None or rec["distance_m"] < 1000 or rec["top_incl_masts_m"] < 120:
            continue
        du = math.tan(math.radians(((taz - yaw + 180) % 360) - 180)) * f
        u = W / 2.0 + du
        if not (5 <= u < W - 5):
            continue
        # the modelled skyline must be this tower at its top (not hidden behind a nearer, higher one)
        if abs(env[int(round(taz * 100)) % 36000] - tel) > 0.02:
            continue
        win = int(max(3, math.tan(math.radians(0.4)) * f))
        lo, hi = int(max(0, u - win)), int(min(W, u + win))
        seg = first[lo:hi]
        if not np.isfinite(seg).any():
            continue
        k = int(np.nanargmin(seg)) + lo
        row_photo = first[k]
        az_photo = (yaw + math.degrees(math.atan((k - W / 2.0) / f))) % 360
        el_photo = pitch + math.degrees(math.atan((cy - row_photo) * math.cos(math.radians(az_photo - yaw)) / f))
        el_err = el_photo - tel
        az_err = ((az_photo - taz + 180) % 360) - 180
        rows_out.append({"county_id": bid, "name": names.get(str(bid), ""), "distance_m": round(tdist, 1),
                         "model_top_m": rec["top_incl_masts_m"], "model_el_deg": round(tel, 4), "photo_el_deg": round(el_photo, 4),
                         "el_err_deg": round(el_err, 4), "az_err_deg": round(az_err, 4),
                         "el_err_m_at_distance": round(math.tan(math.radians(el_err)) * tdist, 2)})
        draw.ellipse([u - 4, cy - f * math.tan(math.radians(tel - pitch)) - 4, u + 4, cy - f * math.tan(math.radians(tel - pitch)) + 4], outline=(255, 255, 0), width=2)
        draw.text((u + 6, cy - f * math.tan(math.radians(tel - pitch)) - 22), (names.get(str(bid)) or str(bid))[:22], fill=(255, 255, 0), font=font)
    img.save(prefix + "_overlay.png")
    if rows_out:
        with open(prefix + "_tops.csv", "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(rows_out[0].keys()))
            w.writeheader()
            w.writerows(rows_out)
    errs = np.array([abs(r_["el_err_deg"]) for r_ in rows_out]) if rows_out else np.array([np.nan])
    summary = {"photo": os.path.basename(photo), "camera_ground_ft": round(ground_ft, 2), "yaw_deg": round(yaw, 3), "pitch_deg": round(pitch, 3),
               "roll_deg": round(roll, 3), "hfov_deg": round(hfov, 3), "median_row_misfit_px": round(res.fun, 2), "image_px": [W, H],
               "tops": len(rows_out), "top_el_err_median_deg": round(float(np.nanmedian(errs)), 4),
               "top_el_err_max_deg": round(float(np.nanmax(errs)), 4), "px_per_deg": round(f * math.radians(1), 1)}
    json.dump(summary, open(prefix + "_summary.json", "w"), indent=1)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
