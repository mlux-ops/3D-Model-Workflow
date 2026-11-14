"""Phase 17: which way do the faces of the built meshes point?

Usage:
    python -B phase17_facing_check.py <mesh folder or .json> [...]

For every mesh file (phase17_towers.py / phase17_clean.py format: level cm about a pivot, triangles, tri_mat) the
right-hand normal (v1 - v0) x (v2 - v0) of each triangle is computed in level coordinates. Roof-like triangles
(normal more than 60 degrees from horizontal) give the convention: the sign of their vertical component on the
upward-facing tops. For each wall triangle (normal within 10 degrees of horizontal) a point is taken 5 cm off its
centre along the normal and tested against the solid: inside when a roof triangle of the same mesh lies above it in
plan. A wall agrees with the roofs when its right-hand normal points out of the solid exactly when the roofs'
right-hand normals point up. The report gives, per mesh, the share of roof and wall area that agrees.
"""

import glob
import json
import os
import sys

import numpy as np


def tri_normals(v, t):
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(n, axis=1)
    return a, b, c, n, area


def point_in_tris_xy(p, A, B, C):
    """Indices of triangles (plan projection) that contain point p (x, y)."""
    def sgn(p1, p2, p3):
        return (p1[..., 0] - p3[..., 0]) * (p2[..., 1] - p3[..., 1]) - (p2[..., 0] - p3[..., 0]) * (p1[..., 1] - p3[..., 1])
    P = np.broadcast_to(p, A.shape)
    d1, d2, d3 = sgn(P, A, B), sgn(P, B, C), sgn(P, C, A)
    neg = (d1 < 0) | (d2 < 0) | (d3 < 0)
    pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
    return np.nonzero(~(neg & pos))[0]


def check(path):
    d = json.load(open(path, encoding="utf-8"))
    v = np.asarray(d["vertices"], np.float64)
    t = np.asarray(d["triangles"], np.int64)
    if not len(t):
        return None
    a, b, c, n, area = tri_normals(v, t)
    ln = np.linalg.norm(n, axis=1) + 1e-12
    nz = n[:, 2] / ln
    roof = np.abs(nz) > 0.5
    wall = np.abs(nz) < 0.17
    # Roof convention: area-weighted sign of nz over roof triangles.
    roof_up = float(area[roof & (nz > 0)].sum())
    roof_dn = float(area[roof & (nz < 0)].sum())
    conv = 1.0 if roof_up >= roof_dn else -1.0
    # Plan triangles of the roofs, with their mean height, for the inside test.
    R = np.nonzero(roof)[0]
    A2, B2, C2 = a[R][:, :2], b[R][:, :2], c[R][:, :2]
    Rz = (a[R][:, 2] + b[R][:, 2] + c[R][:, 2]) / 3.0
    agree = disagree = unknown = 0.0
    W = np.nonzero(wall)[0]
    rng = np.random.default_rng(1)
    if len(W) > 400:
        W = rng.choice(W, 400, replace=False)
    for i in W:
        cen = (a[i] + b[i] + c[i]) / 3.0
        hn = n[i].copy()
        hn[2] = 0.0
        hn /= (np.linalg.norm(hn) + 1e-12)
        res = []
        for s in (1.0, -1.0):
            p = cen + s * 5.0 * hn
            hit = point_in_tris_xy(p[:2], A2, B2, C2)
            res.append(bool(len(hit) and (Rz[hit] > p[2]).any()))
        out_pos, out_neg = (not res[0]), (not res[1])
        if out_pos == out_neg:
            unknown += area[i]
            continue
        # Right-hand normal points out (out_pos) and roofs' right-hand normals point up (conv > 0): agree.
        if out_pos == (conv > 0):
            agree += area[i]
        else:
            disagree += area[i]
    judged = agree + disagree
    return {"mesh": os.path.basename(path), "roof_rh_up_share": round(roof_up / max(roof_up + roof_dn, 1e-9), 3),
            "walls_agree_share": round(agree / judged, 3) if judged else None,
            "walls_judged_m2": round(judged / 1e4, 1), "walls_unknown_m2": round(unknown / 1e4, 1)}


def main():
    files = []
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            files += sorted(f for f in glob.glob(os.path.join(arg, "*.json")) if not f.endswith("_record.json"))
        else:
            files.append(arg)
    rows = []
    for f in files:
        try:
            r = check(f)
        except (KeyError, ValueError):
            continue
        if r:
            rows.append(r)
            print(json.dumps(r))
    if rows:
        ws = [r["walls_agree_share"] for r in rows if r["walls_agree_share"] is not None]
        print(json.dumps({"meshes": len(rows), "median_walls_agree": float(np.median(ws)) if ws else None,
                          "meshes_walls_agree_below_0.9": sum(1 for w in ws if w < 0.9),
                          "median_roof_rh_up": float(np.median([r["roof_rh_up_share"] for r in rows]))}))


if __name__ == "__main__":
    main()
