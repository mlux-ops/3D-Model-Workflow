# -*- coding: utf-8 -*-
"""CPython 3: registers the model geometry to the black product photo (weak-perspective camera fit).

Unknowns: azimuth, elevation, roll, scale, tx, ty, perspective k. Data: disc rim ellipse points, backplate rim points on the
left of the silhouette, and the sphere/disc boundary. Writes work/camera_fit_black.json and work/camera_fit_black.png (overlay)."""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull, Delaunay, cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path, dump_json  # noqa: E402

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
WORK = RUN + 'work/'
raw = np.asarray(Image.open(WORK + 'thumbs/833919_midnight_black_t.png').convert('L'), float)
H, W = raw.shape

TH = np.radians(18.179439648215258)
N = np.array([0, -np.sin(TH), np.cos(TH)])
EX = np.array([1.0, 0, 0])
EY = np.array([0, np.cos(TH), np.sin(TH)])
C0 = np.array([0, 0, 1.975])
CD = C0 + N * 0.047
S = np.array([0, -0.5828845845544276, 3.75])
R_SPH = 1.75
YV = np.array([0, 1.0, 0])

# ---- data
dark = raw < 140
lab, n = ndi.label(dark)
dark = lab == (1 + int(np.argmax(ndi.sum(dark, lab, range(1, n + 1)))))
dark = ndi.binary_fill_holes(dark)
edge = dark & ~ndi.binary_erosion(dark)
ys, xs = np.nonzero(edge)
pts = np.c_[xs, ys].astype(float)
SC0 = np.array([543.0, 426.0])
far = np.hypot(pts[:, 0] - SC0[0], pts[:, 1] - SC0[1]) > 215
rim_pts = pts[far & (pts[:, 0] > 240)]
plate_pts = pts[far & (pts[:, 0] < 232)]
# sphere/disc boundary: sphere = bright component around (500,430) within the dark silhouette hull
bright = raw > 170
labb, nb = ndi.label(bright)
sph = labb == labb[430, 500]
sph = ndi.binary_fill_holes(sph)
sph_edge = sph & ~ndi.binary_erosion(sph)
near_dark = ndi.binary_dilation(dark, iterations=3)
sy, sx = np.nonzero(sph_edge & near_dark)
sph_pts = np.c_[sx, sy].astype(float)
_hull = Delaunay(pts[ConvexHull(pts).vertices])
_dd = np.hypot(sph_pts[:, 0] - SC0[0], sph_pts[:, 1] - SC0[1])
sph_pts = sph_pts[(_hull.find_simplex(sph_pts) >= 0) & (_dd > 140) & (_dd < 225)]
print('points: disc rim', len(rim_pts), 'plate', len(plate_pts), 'sphere/disc boundary', len(sph_pts))

# sphere circle fit (free), for reference
A = np.c_[2 * sph_pts[:, 0], 2 * sph_pts[:, 1], np.ones(len(sph_pts))]
b = (sph_pts ** 2).sum(1)
cx, cy, c0 = np.linalg.lstsq(A, b, rcond=None)[0]
r_free = np.sqrt(c0 + cx * cx + cy * cy)
print('free circle fit to sphere/disc boundary: centre (%.1f, %.1f) r %.1f px' % (cx, cy, r_free))

PHI = np.linspace(0, 2 * np.pi, 1440, endpoint=False)
rim_pts = rim_pts[::4]
plate_pts = plate_pts[::3]
sph_pts = sph_pts[::3]


def camera(az, el, roll):
    a, e, rl = np.radians(az), np.radians(el), np.radians(roll)
    d = np.array([-np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e)])
    fwd = -d
    right = np.cross(fwd, YV)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    r2 = right * np.cos(rl) + up * np.sin(rl)
    u2 = -right * np.sin(rl) + up * np.cos(rl)
    return d, r2, u2


def project(P, p):
    az, el, roll, s, tx, ty, k = p
    d, r, u = camera(az, el, roll)
    P = np.atleast_2d(P)
    w = P @ d
    sc = s * (1 + k * w)
    return np.c_[sc * (P @ r) + tx, -sc * (P @ u) + ty], sc


def nearest(curve, pts_):
    return cKDTree(curve).query(pts_)[0]


def geometry():
    disc = CD + 4.0 * (np.cos(PHI)[:, None] * EX + np.sin(PHI)[:, None] * EY)
    plate = np.c_[2.625 * np.cos(PHI), 2.625 * np.sin(PHI), np.full_like(PHI, 0.125)]
    plate_b = np.c_[2.625 * np.cos(PHI), 2.625 * np.sin(PHI), np.zeros_like(PHI)]
    return disc, plate, plate_b


DISC, PLATE, PLATE_B = geometry()


def residuals(p):
    dproj, _ = project(DISC, p)
    pf, _ = project(PLATE, p)
    pb, _ = project(PLATE_B, p)
    plate_curve = np.r_[pf, pb]
    res = []
    res.append(nearest(dproj[::4], rim_pts))
    res.append(0.5 * np.minimum(nearest(plate_curve[::4], plate_pts), 40))
    sp, sc = project(S, p)
    res.append(np.abs(np.hypot(sph_pts[:, 0] - sp[0, 0], sph_pts[:, 1] - sp[0, 1]) - R_SPH * sc[0]))
    return np.concatenate(res)


best = None
for az0 in (50, 60):
    for el0 in (-10, 10):
        for rl0 in (-8, 4):
            p0 = [az0, el0, rl0, 99.0, 382.0, 389.0, 0.0]
            try:
                r = least_squares(residuals, p0, loss='soft_l1', f_scale=3.0,
                                  bounds=([0, -40, -40, 60, 200, 200, -0.05], [90, 60, 40, 140, 560, 560, 0.08]))
            except Exception as exc:  # noqa: BLE001
                print('fail', exc)
                continue
            if best is None or r.cost < best.cost:
                best = r
p = best.x
res = residuals(p)
nd, npl = len(rim_pts), len(plate_pts)
print('fit az %.2f el %.2f roll %.2f scale %.2f tx %.1f ty %.1f k %.4f' % tuple(p))
print('rms px: disc rim %.2f, plate %.2f (x0.5 scaled, capped 40), sphere %.2f' % (
    np.sqrt(np.mean(res[:nd] ** 2)), np.sqrt(np.mean((2 * res[nd:nd + npl]) ** 2)), np.sqrt(np.mean(res[nd + npl:] ** 2))))
print('cost', best.cost)

# sensitivity: profile over roll
prof = []
for roll in (-20, -15, -10, -5, 0, 5, 10):
    def rr(q, roll=roll):
        return residuals([q[0], q[1], roll, q[2], q[3], q[4], q[5]])
    r = least_squares(rr, [p[0], p[1], p[3], p[4], p[5], p[6]], loss='soft_l1', f_scale=3.0,
                      bounds=([0, -40, 60, 200, 200, -0.05], [90, 60, 140, 560, 560, 0.08]))
    prof.append({'roll': roll, 'az': float(r.x[0]), 'el': float(r.x[1]), 'cost': float(r.cost)})
    print('roll %4d -> az %.1f el %.1f cost %.1f' % (roll, r.x[0], r.x[1], r.cost))

# overlay
im = Image.open(WORK + 'thumbs/833919_midnight_black_t.png').convert('RGB')
dr = ImageDraw.Draw(im)
dproj, _ = project(DISC, p)
pf, _ = project(PLATE, p)
pb, _ = project(PLATE_B, p)
for c, col in ((dproj, (255, 0, 0)), (pf, (0, 160, 255)), (pb, (0, 200, 0))):
    dr.line([tuple(q) for q in np.r_[c, c[:1]]], fill=col, width=2)
sp, sc = project(S, p)
rr_ = R_SPH * sc[0]
dr.ellipse([sp[0, 0] - rr_, sp[0, 1] - rr_, sp[0, 0] + rr_, sp[0, 1] + rr_], outline=(255, 0, 255), width=2)
im.save(safe_path(WORK + 'camera_fit_black.png'))
dump_json({'az_deg': float(p[0]), 'el_deg': float(p[1]), 'roll_deg': float(p[2]), 'px_per_in': float(p[3]), 'tx': float(p[4]), 'ty': float(p[5]),
           'k_perspective_per_in': float(p[6]), 'cost': float(best.cost), 'free_sphere_circle_px': [float(cx), float(cy), float(r_free)],
           'roll_profile': prof}, WORK + 'camera_fit_black.json')
