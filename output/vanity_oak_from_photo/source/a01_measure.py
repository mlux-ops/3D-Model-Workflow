"""Measure the vanity front: fit every reveal line, intersect them into panel quads, fit the front-plane homography,
and derive inch coordinates and native px/in for every panel.

Assumption (disclosed): overall vanity width = 48 in (product not identified; 48 in class vanity). The vertical
scale of the front plane is set so horizontal and vertical px/in agree on average over the front face (the plane is
rotated only mildly, so the residual anisotropy is ~cos(theta), reported).

Writes _work/measure.json and _work/_VIEW_measure_overlay.jpg."""
import json

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

from common import load_rgb, lum, thumb
from guard import SOURCE_PHOTO, out_path

VANITY_W_IN = 48.0

# approximate positions from the reveal-peak survey (_work/explore_profiles.py); x for verticals, (x, y) for horizontals
VERT = {"V0": (422, 460, 1140), "V1": (699.5, 460, 1110), "V2": (966, 430, 1105), "V3": (1224, 405, 1075),
        "V4": (1471, 395, 1035)}
HORZ = {"AT": [(465, 374), (590, 367), (830, 353), (1100, 336), (1350, 321), (1450, 313)],
        "HT": [(465, 442), (590, 434), (830, 418), (1100, 400), (1350, 384), (1450, 377)],
        "HL1": [(435, 684), (465, 682), (590, 672), (690, 664)],
        "HL2": [(435, 925), (465, 922), (590, 910), (690, 902)],
        "HR1": [(1232, 614), (1350, 608), (1450, 601), (1462, 600)],
        "HR2": [(1232, 842), (1350, 834), (1450, 824), (1462, 823)],
        "HB": [(465, 1161), (590, 1146), (830, 1120), (1100, 1088), (1350, 1054), (1450, 1046)],
        "RB": [(465, 1229), (590, 1214), (1350, 1128), (1450, 1112)]}
HRANGE = {"AT": (440, 1460), "HT": (432, 1462), "HL1": (432, 690), "HL2": (432, 690), "HR1": (1232, 1462),
          "HR2": (1232, 1462), "HB": (432, 1462), "RB": (440, 1460)}


def ridge(R, axis_vals, pred, horizontal, win=9):
    """Track the dark-line ridge: for each sample position, parabola-refined argmax within +-win of prediction."""
    pts = []
    for t, p in zip(axis_vals, pred):
        c = int(round(p))
        prof = R[c - win:c + win + 1, t] if horizontal else R[t, c - win:c + win + 1]
        k = int(np.argmax(prof))
        if 0 < k < len(prof) - 1:
            a, b, d = prof[k - 1], prof[k], prof[k + 1]
            off = 0.5 * (a - d) / (a - 2 * b + d) if (a - 2 * b + d) != 0 else 0.0
        else:
            off = 0.0
        pts.append((t, c - win + k + off, prof[k]))
    return np.array(pts)


def robust_line(pts):
    t, s = pts[:, 0], pts[:, 1]
    keep = np.ones(len(t), bool)
    for _ in range(5):
        A = np.c_[np.ones(keep.sum()), t[keep]]
        coef, *_ = np.linalg.lstsq(A, s[keep], rcond=None)
        res = s - (coef[0] + coef[1] * t)
        sd = max(np.std(res[keep]), 0.3)
        keep = np.abs(res) < max(2.5 * sd, 1.0)
    return coef, float(np.sqrt(np.mean(res[keep] ** 2))), int(keep.sum()), len(t)


def intersect(v, h):
    """v: x = a + b*y ; h: y = c + d*x"""
    a, b = v
    c, d = h
    y = (c + d * a) / (1 - d * b)
    return np.array([a + b * y, y])


def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, Vt = np.linalg.svd(np.array(A, float))
    Hm = Vt[-1].reshape(3, 3)
    return Hm / Hm[2, 2]


def apply_h(Hm, p):
    p = np.atleast_2d(p)
    q = np.c_[p, np.ones(len(p))] @ Hm.T
    return q[:, :2] / q[:, 2:3]


def main():
    L = lum(load_rgb(SOURCE_PHOTO))
    R = ndi.gaussian_filter(L, 5) - ndi.gaussian_filter(L, 1)
    lines, fitinfo = {}, {}
    for k, (x0, y0, y1) in VERT.items():
        ys = np.arange(y0, y1, 6)
        coef, rms, n, tot = robust_line(ridge(R, ys, np.full(len(ys), x0), horizontal=False))
        # refine once around the fitted line
        coef, rms, n, tot = robust_line(ridge(R, ys, coef[0] + coef[1] * ys, horizontal=False, win=4))
        lines[k] = coef.tolist()
        fitinfo[k] = {"rms_px": round(rms, 3), "inliers": n, "samples": tot}
    for k, pts in HORZ.items():
        xs = np.arange(*HRANGE[k], 6)
        px, py = np.array(pts).T
        pred = np.interp(xs, px, py)
        coef, rms, n, tot = robust_line(ridge(R, xs, pred, horizontal=True))
        coef, rms, n, tot = robust_line(ridge(R, xs, coef[0] + coef[1] * xs, horizontal=True, win=4))
        lines[k] = coef.tolist()
        fitinfo[k] = {"rms_px": round(rms, 3), "inliers": n, "samples": tot}

    P = lambda v, h: intersect(lines[v], lines[h])
    # front frame (inside reveals V0..V4, HT..HB) -> unit rectangle first, to test planarity/symmetry
    frame_img = np.array([P("V0", "HT"), P("V4", "HT"), P("V4", "HB"), P("V0", "HB")])
    H1 = homography(frame_img, [(0, 0), (1, 0), (1, 1), (0, 1)])
    mid_y = lambda v: 0.5 * (P(v, "HT")[1] + P(v, "HB")[1])
    u = {v: float(apply_h(H1, [[lines[v][0] + lines[v][1] * mid_y(v), mid_y(v)]])[0, 0]) for v in VERT}
    sym = {"u_V1": u["V1"], "u_V2": u["V2"], "u_V3": u["V3"], "left_col_minus_right_col": u["V1"] - (1 - u["V3"]),
           "door1_minus_door2": (u["V2"] - u["V1"]) - (u["V3"] - u["V2"])}

    # overall width: left silhouette of side/post junction and right post silhouette, measured on a mid row
    rowband = R[700:1000].mean(0)
    xl = 300 + int(np.argmax(rowband[300:345]))
    xr = 1488 + int(np.argmax(rowband[1488:1515]))
    ymid = 850.0
    ul = apply_h(H1, [[xl, ymid]])[0, 0]
    ur = apply_h(H1, [[xr, ymid]])[0, 0]
    frame_w_in = VANITY_W_IN / (ur - ul)          # inches per unit u
    # choose vertical scale so the mean horizontal and vertical px/in agree over the front face
    Hi = np.linalg.inv(H1)

    def jac(uu, vv, sx, sy):
        e = 1e-4
        p0 = apply_h(Hi, [[uu, vv]])[0]
        pu = apply_h(Hi, [[uu + e, vv]])[0]
        pv = apply_h(Hi, [[uu, vv + e]])[0]
        return np.linalg.norm(pu - p0) / (e * sx), np.linalg.norm(pv - p0) / (e * sy)

    grid = [(a, b) for a in np.linspace(0.05, 0.95, 10) for b in np.linspace(0.05, 0.95, 10)]
    hx = np.array([jac(a, b, frame_w_in, 1.0)[0] for a, b in grid])
    vy1 = np.array([jac(a, b, frame_w_in, 1.0)[1] for a, b in grid])       # px per unit v
    frame_h_in = float(np.exp(np.mean(np.log(vy1)) - np.mean(np.log(hx))))  # so that geo-mean vert px/in == horiz
    S = np.diag([frame_w_in, frame_h_in, 1.0])
    Hin = S @ H1                                   # image px -> front-plane inches (origin at V0/HT corner)

    def quad(v0, v1, h0, h1):
        return [P(v0, h0).tolist(), P(v1, h0).tolist(), P(v1, h1).tolist(), P(v0, h1).tolist()]

    panels = {"drawer_L1": quad("V0", "V1", "HT", "HL1"), "drawer_L2": quad("V0", "V1", "HL1", "HL2"),
              "drawer_L3": quad("V0", "V1", "HL2", "HB"), "door_L": quad("V1", "V2", "HT", "HB"),
              "door_R": quad("V2", "V3", "HT", "HB"), "drawer_R1": quad("V3", "V4", "HT", "HR1"),
              "drawer_R2": quad("V3", "V4", "HR1", "HR2"), "drawer_R3": quad("V3", "V4", "HR2", "HB"),
              "apron": quad("V0", "V4", "AT", "HT"), "bottom_rail": quad("V0", "V4", "HB", "RB")}
    info = {}
    for k, q in panels.items():
        qi = apply_h(Hin, q)
        w_in = 0.5 * (np.linalg.norm(qi[1] - qi[0]) + np.linalg.norm(qi[2] - qi[3]))
        h_in = 0.5 * (np.linalg.norm(qi[3] - qi[0]) + np.linalg.norm(qi[2] - qi[1]))
        qa = np.array(q)
        w_px = 0.5 * (np.linalg.norm(qa[1] - qa[0]) + np.linalg.norm(qa[2] - qa[3]))
        h_px = 0.5 * (np.linalg.norm(qa[3] - qa[0]) + np.linalg.norm(qa[2] - qa[1]))
        info[k] = {"quad_img": [[round(a, 2) for a in p] for p in q],
                   "quad_in": [[round(a, 3) for a in p] for p in qi.tolist()],
                   "w_in": round(float(w_in), 3), "h_in": round(float(h_in), 3),
                   "px_per_in_h": round(float(w_px / w_in), 2), "px_per_in_v": round(float(h_px / h_in), 2)}
    aniso = hx / (np.array([jac(a, b, frame_w_in, frame_h_in)[1] for a, b in grid]))
    out = {"source": SOURCE_PHOTO, "assumed_vanity_width_in": VANITY_W_IN, "lines": lines, "line_fit": fitinfo,
           "symmetry_check_unit_u": {k: round(v, 4) for k, v in sym.items()},
           "silhouette_x_px": [xl, xr], "front_frame_w_in": round(frame_w_in, 3), "front_frame_h_in": round(frame_h_in, 3),
           "post_allowance_in_each": round((VANITY_W_IN - frame_w_in) / 2, 3),
           "anisotropy_h_over_v": {"min": round(float(aniso.min()), 3), "max": round(float(aniso.max()), 3)},
           "H_img_to_in": Hin.tolist(), "panels": info}
    json.dump(out, open(out_path("_work/measure.json"), "w"), indent=1)

    im = Image.open(SOURCE_PHOTO).convert("RGB")
    d = ImageDraw.Draw(im)
    for k, q in panels.items():
        d.polygon([tuple(p) for p in q], outline=(255, 0, 0) if "door" in k else (0, 90, 255))
    thumb(im, out_path("_work/_VIEW_measure_overlay.jpg"))
    print(json.dumps({k: out[k] for k in ("symmetry_check_unit_u", "silhouette_x_px", "front_frame_w_in",
                                          "front_frame_h_in", "post_allowance_in_each", "anisotropy_h_over_v")}, indent=1))
    for k, v in info.items():
        print(k, v["w_in"], v["h_in"], v["px_per_in_h"], v["px_per_in_v"])
    print(json.dumps(fitinfo))


if __name__ == "__main__":
    main()
