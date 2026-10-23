# -*- coding: utf-8 -*-
"""Disc edge (rim) thickness from the Midnight Black hero photo.
The rim band is the dark strip between the outer silhouette and the lighter disc face on the upper-left arc.
Profiles are sampled along the ellipse normal (ellipse from fit_disc_ellipse: centre (872.0, 889.4), A 907.9, B 526.4, lean 13.44 deg).
The band's apparent width = t * sin(angle(N, view)) * cos(psi), psi = angle between the projected disc normal and the edge normal."""
import json
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe

ROOT = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce"
RUN = ROOT + "/max"
im = np.asarray(Image.open(ROOT + "/inputs/833919_midnight_black.jpg").convert("L")).astype(float)

cx, cy, A, B, lean = 872.0, 889.4, 907.9, 526.4, np.radians(13.44)
# ellipse frame: major axis direction (image coords x right, y down) leaning from vertical by `lean`
# unit major vector: leaning to the right at the top?  Determine sign by testing which sign puts the boundary on the silhouette.
best = None
for sgn in (+1, -1):
    maj = np.array([np.sin(sgn * lean), -np.cos(sgn * lean)])
    mnr = np.array([np.cos(sgn * lean), np.sin(sgn * lean)])
    score = 0
    for u in np.linspace(0, 2 * np.pi, 360, endpoint=False):
        p = np.array([cx, cy]) + A * np.cos(u) * maj + B * np.sin(u) * mnr
        x, y = int(round(p[0])), int(round(p[1]))
        if 0 <= x < im.shape[1] and 0 <= y < im.shape[0]:
            # boundary should have white outside and dark inside: compare 6 px out and in
            n = np.array([np.cos(u) / A, 0]) * 0
            score += 0
    best = (sgn, maj, mnr) if best is None else best
sgn = None
res_by_sign = {}
for sgn in (+1, -1):
    maj = np.array([np.sin(sgn * lean), -np.cos(sgn * lean)])
    mnr = np.array([np.cos(sgn * lean), np.sin(sgn * lean)])
    contrast = []
    for u in np.linspace(np.radians(100), np.radians(260), 60):
        pt = np.array([cx, cy]) + A * np.cos(u) * maj + B * np.sin(u) * mnr
        nrm = np.array([np.cos(u) / A * maj[0] + np.sin(u) / B * mnr[0], np.cos(u) / A * maj[1] + np.sin(u) / B * mnr[1]])
        nrm /= np.hypot(*nrm)
        out = pt + 8 * nrm
        inn = pt - 8 * nrm
        vo = ndimage.map_coordinates(im, [[out[1]], [out[0]]], order=1, mode="nearest")[0]
        vi = ndimage.map_coordinates(im, [[inn[1]], [inn[0]]], order=1, mode="nearest")[0]
        contrast.append(vo - vi)
    res_by_sign[sgn] = float(np.mean(contrast))
print("mean outside-minus-inside luminance by lean sign:", res_by_sign)
sgn = max(res_by_sign, key=res_by_sign.get)
maj = np.array([np.sin(sgn * lean), -np.cos(sgn * lean)])
mnr = np.array([np.cos(sgn * lean), np.sin(sgn * lean)])
print("lean sign", sgn, "major", maj, "minor", mnr)

rows = []
sin_view = float(np.sqrt(1.0 - (B / A) ** 2))   # sin of the angle between the disc normal and the view; B/A = cos of that angle
scale = A / 4.0
for udeg in range(0, 360, 4):
    u = np.radians(udeg)
    pt = np.array([cx, cy]) + A * np.cos(u) * maj + B * np.sin(u) * mnr
    if not (5 < pt[0] < im.shape[1] - 5 and 5 < pt[1] < im.shape[0] - 5):
        continue
    nrm = np.cos(u) / A * maj + np.sin(u) / B * mnr
    nrm /= np.hypot(*nrm)
    # locate the actual silhouette edge along the normal (largest drop) within +-12 px
    ts = np.arange(-14, 14.01, 0.5)
    xs = pt[0] + ts * nrm[0]
    ys = pt[1] + ts * nrm[1]
    prof = ndimage.map_coordinates(im, [ys, xs], order=1, mode="nearest")
    if prof[0] > 60 and prof[-1] > 200:
        continue
    # outside = high luminance (background); walk inward (negative t) from the first sample below 150
    k_out = int(np.argmax(prof < 150)) if np.any(prof < 150) else None
    if k_out is None or prof[-1] < 150:
        continue
    # extend the profile inward from the silhouette edge for 40 px
    edge_t = ts[k_out]
    ts2 = np.arange(0, 50.01, 0.5)
    xs2 = pt[0] + (edge_t - ts2) * nrm[0]
    ys2 = pt[1] + (edge_t - ts2) * nrm[1]
    p2 = ndimage.map_coordinates(im, [ys2, xs2], order=1, mode="nearest")
    face = float(np.median(p2[ts2 >= 35]))
    band = float(np.median(p2[ts2 <= 1.5]))
    if face - band < 12:
        continue
    half = 0.5 * (face + band)
    idx = np.nonzero(p2 > half)[0]
    if len(idx) == 0:
        continue
    w = float(ts2[idx[0]])
    cos_psi = abs(np.dot(nrm, mnr))
    rows.append((udeg, float(pt[0]), float(pt[1]), band, face, w, float(cos_psi)))

print("u  x  y  band_lum  face_lum  width_px  cos_psi  t_est_in")
ts_est = []
for r in rows:
    t_est = r[5] / (scale * sin_view * max(r[6], 1e-3))
    ts_est.append((r, t_est))
    print("%3d %6.0f %6.0f %6.1f %6.1f %6.2f %5.2f %6.3f" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], t_est))
good = [t for (r, t) in ts_est if r[6] > 0.5]
if good:
    print("t_est (cos_psi > 0.5): median %.3f in, mean %.3f, min %.3f, max %.3f, n=%d" % (np.median(good), np.mean(good), np.min(good), np.max(good), len(good)))
with open(safe(RUN + "/_work/disc_rim_measure.json"), "w") as f:
    json.dump({"rows": rows, "t_est_median_in": float(np.median(good)) if good else None, "n": len(good),
               "scale_px_per_in": scale, "sin_view": sin_view}, f, indent=1)
