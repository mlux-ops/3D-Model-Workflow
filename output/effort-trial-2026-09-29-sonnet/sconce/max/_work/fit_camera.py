# -*- coding: utf-8 -*-
"""Joint perspective-camera + disc fit against the oblique Midnight Black photo.

World frame (wall frame): X along the wall (image right at yaw 0), Y up, Z out of the wall. Inches.
Features: backplate back-rim left arc, disc outline, globe silhouette.
"""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw
import json

WORK = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/"
SRC = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/833919_midnight_black.jpg"

# ---- observations (from analyze_mb.py, fit_disc_ellipse.py, left_outline.py) ----
disc_ell = np.load(WORK + "mb_ellipse.npy")            # cx, cy, A, B, majx, majy
left = np.load(WORK + "mb_left.npy")                    # (x,y) leftmost per row (step 6)
left = left[(left[:, 1] >= 440) & (left[:, 1] <= 1400)]
bnd = np.load(WORK + "mb_boundary.npy")                 # non-glass silhouette boundary points

cx, cy, A, B, mx, my = disc_ell
maj = np.array([mx, my])
mnr = np.array([-my, mx])
# disc outline observations = boundary points within 3 px of the fitted disc ellipse
q = np.c_[bnd[:, 0] - cx, bnd[:, 1] - cy] @ np.c_[maj, mnr]
rr = np.sqrt((q[:, 0] / A) ** 2 + (q[:, 1] / B) ** 2)
disc_obs = bnd[np.abs(rr - 1) * np.sqrt(A * B) < 3.0][::6]
left_obs = left[::2]
globe = dict(cx=1238.5, cy=970.4, r=410.4)
print("obs: disc %d pts, left arc %d pts" % (len(disc_obs), len(left_obs)))

R_BP = 2.625
R_DISC = 4.0
R_GLOBE = 1.75
YG = -0.442  # from the side reference photo


def cam_basis(psi, delta):
    c = np.array([np.sin(psi) * np.cos(delta), np.sin(delta), np.cos(psi) * np.cos(delta)])
    r = np.array([np.cos(psi), 0.0, -np.sin(psi)])
    u = np.array([-np.sin(psi) * np.sin(delta), np.cos(delta), -np.cos(psi) * np.sin(delta)])
    return c, r, u


def project(P, cam):
    psi, delta, D, F, u0, v0 = cam
    c, r, u = cam_basis(psi, delta)
    C = D * c
    p = P - C
    xc = p @ r
    yc = p @ u
    zc = p @ (-c)
    return np.c_[u0 + F * xc / zc, v0 - F * yc / zc], zc


def circle_pts(centre, normal, radius, n=720):
    normal = normal / np.linalg.norm(normal)
    a = np.array([1.0, 0, 0]) if abs(normal[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(normal, a)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(normal, e1)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return centre + radius * (np.outer(np.cos(t), e1) + np.outer(np.sin(t), e2))


def model_curves(x, fixed):
    psi, delta, logD, F, u0, v0, theta, Yd, Zd, Zg = x
    D = np.exp(logD)
    cam = (psi, delta, D, F, u0, v0)
    n = np.array([0.0, -np.sin(theta), np.cos(theta)])
    disc = circle_pts(np.array([0.0, Yd, Zd]), n, R_DISC)
    bp = circle_pts(np.array([0.0, 0.0, 0.0]), np.array([0, 0, 1.0]), R_BP)
    dpx, _ = project(disc, cam)
    bpx, _ = project(bp, cam)
    gc, zc = project(np.array([[0.0, YG, Zg]]), cam)
    gr = F * R_GLOBE / np.sqrt(zc[0] ** 2 - R_GLOBE ** 2)
    return dpx, bpx, gc[0], gr


def residuals(x, fixed):
    dpx, bpx, gc, gr = model_curves(x, fixed)
    tree_d = cKDTree(dpx)
    tree_b = cKDTree(bpx)
    rd = tree_d.query(disc_obs)[0]
    rb = tree_b.query(left_obs)[0]
    rg = np.array([gc[0] - globe["cx"], gc[1] - globe["cy"], (gr - globe["r"])]) * 3.0
    res = np.concatenate([rd * 1.0, rb * 1.0, rg])
    reg = []
    if fixed.get("theta") is not None:
        reg.append((x[6] - fixed["theta"]) * 3000.0)
    if fixed.get("logD") is not None:
        reg.append((x[2] - fixed["logD"]) * 4000.0)
    return np.concatenate([res, np.array(reg)])


def run(fixed, x0, tag):
    lo = [-1.5, -0.8, np.log(15), 500, 0, 0, np.radians(5), -3, 0.0, 3.0]
    hi = [-0.3, 0.8, np.log(600), 40000, 1779, 1779, np.radians(35), 3, 4.0, 4.4]
    sol = least_squares(residuals, x0, args=(fixed,), bounds=(lo, hi), x_scale=[0.1, 0.1, 0.3, 500, 30, 30, 0.1, 0.3, 0.3, 0.3], max_nfev=4000)
    x = sol.x
    res = residuals(x, fixed)
    npts = len(disc_obs) + len(left_obs)
    rms_d = np.sqrt(np.mean(res[:len(disc_obs)] ** 2))
    rms_b = np.sqrt(np.mean(res[len(disc_obs):npts] ** 2))
    print("[%s] psi=%.2f delta=%.2f D=%.1f in F=%.0f px (scale@D=%.1f px/in) u0=%.0f v0=%.0f | theta=%.2f deg Yd=%.3f Zd=%.3f Zg=%.3f | rms disc %.2f left %.2f globe-res %s" % (
        tag, np.degrees(x[0]), np.degrees(x[1]), np.exp(x[2]), x[3], x[3] / np.exp(x[2]), x[4], x[5], np.degrees(x[6]), x[7], x[8], x[9], rms_d, rms_b,
        np.round(res[npts:npts + 3] / 3.0, 2)))
    return x


x0 = np.array([np.radians(-56), np.radians(-12), np.log(120), 234 * 120, 889.5, 889.5, np.radians(18), 0.0, 2.05, 3.75])
xs = {}
xs["free"] = run({}, x0, "free")
xs["theta18"] = run({"theta": np.radians(18)}, x0, "theta=18")
for Dv in (40, 80, 160, 320):
    xs["D%d" % Dv] = run({"logD": np.log(Dv), "theta": np.radians(18)}, x0, "D=%d,th=18" % Dv)
    xs["D%dfree" % Dv] = run({"logD": np.log(Dv)}, x0, "D=%d free th" % Dv)

json.dump({k: list(map(float, v)) for k, v in xs.items()}, open(safe(WORK + "camera_fit.json"), "w"), indent=1)

# overlay for the free solution
x = xs["free"]
img = Image.open(SRC).convert("RGB")
dr = ImageDraw.Draw(img)
dpx, bpx, gc, gr = model_curves(x, {})
dr.line([tuple(p) for p in dpx] + [tuple(dpx[0])], fill=(255, 0, 0), width=4)
dr.line([tuple(p) for p in bpx] + [tuple(bpx[0])], fill=(0, 255, 0), width=4)
dr.ellipse((gc[0] - gr, gc[1] - gr, gc[0] + gr, gc[1] + gr), outline=(0, 128, 255), width=4)
img.resize((800, 800)).save(safe(WORK + "thumbs/mb_camfit.png"))
