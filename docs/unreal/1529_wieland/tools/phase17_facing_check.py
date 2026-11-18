"""Phase 17: which way do the faces of the built meshes point, as the engine draws them?

Usage:
    python -B phase17_facing_check.py <mesh folder or .json> [...]

Mesh files are those of phase17_towers.py / phase17_clean.py / phase17_terrain.py: vertices in level cm about a
pivot, triangles, tri_mat. The engine takes a triangle's front from (v2 - v0) x (v1 - v0) in level coordinates (the
opposite of the right-hand rule; measured on the imported meshes with GeometryScript's face normal, J23b), and draws
only the front of a one-sided material.

For each mesh:
- roofs: triangles whose normal is more than 60 degrees from horizontal; the share of their area whose front faces
  up (a roof seen from above, or the ground);
- walls: triangles within 10 degrees of vertical; a point 5 cm off each wall's centre on either side is tested
  against the solid (inside when a roof triangle of the same mesh lies above it in plan); the share of the judged wall
  area whose front faces out of the solid. Walls that the test cannot judge (both sides inside or both outside, for
  example a wall under a higher overhang) are reported apart.
Both shares should be 1.0.
"""

import glob
import json
import os
import sys

import numpy as np


def point_in_tris_xy(p, A, B, C):
    """Indices of triangles (plan projection) that contain point p (x, y)."""
    def sgn(p1, p2, p3):
        return (p1[..., 0] - p3[..., 0]) * (p2[..., 1] - p3[..., 1]) - (p2[..., 0] - p3[..., 0]) * (p1[..., 1] - p3[..., 1])
    P = np.broadcast_to(p, A.shape)
    d1, d2, d3 = sgn(P, A, B), sgn(P, B, C), sgn(P, C, A)
    neg = (d1 < 0) | (d2 < 0) | (d3 < 0)
    pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
    return np.nonzero(~(neg & pos))[0]


def check(path, max_walls=400):
    d = json.load(open(path, encoding="utf-8"))
    v = np.asarray(d["vertices"], np.float64)
    t = np.asarray(d["triangles"], np.int64)
    if not len(t):
        return None
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    front = np.cross(c - a, b - a)  # the engine's front direction
    area = 0.5 * np.linalg.norm(front, axis=1)
    ln = np.linalg.norm(front, axis=1) + 1e-12
    fz = front[:, 2] / ln
    roof = np.abs(fz) > 0.5
    wall = np.abs(fz) < 0.17
    roof_up = float(area[roof & (fz > 0)].sum())
    roof_all = float(area[roof].sum())
    R = np.nonzero(roof)[0]
    A2, B2, C2 = a[R][:, :2], b[R][:, :2], c[R][:, :2]
    Rz = np.maximum(np.maximum(a[R][:, 2], b[R][:, 2]), c[R][:, 2])
    out_ok = out_bad = unknown = 0.0
    W = np.nonzero(wall)[0]
    if len(W) > max_walls:
        W = np.random.default_rng(1).choice(W, max_walls, replace=False)
    for i in W:
        cen = (a[i] + b[i] + c[i]) / 3.0
        hn = front[i].copy()
        hn[2] = 0.0
        hn /= (np.linalg.norm(hn) + 1e-12)
        inside = []
        for s in (1.0, -1.0):
            p = cen + s * 5.0 * hn
            hit = point_in_tris_xy(p[:2], A2, B2, C2)
            inside.append(bool(len(hit) and (Rz[hit] > p[2]).any()))
        if inside[0] == inside[1]:
            unknown += area[i]
        elif not inside[0]:
            out_ok += area[i]   # the front side is outside the solid
        else:
            out_bad += area[i]
    judged = out_ok + out_bad
    return {"mesh": os.path.basename(path),
            "roofs_facing_up": round(roof_up / roof_all, 3) if roof_all else None,
            "walls_facing_out": round(out_ok / judged, 3) if judged else None,
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
        up = [r["roofs_facing_up"] for r in rows if r["roofs_facing_up"] is not None]
        wo = [r["walls_facing_out"] for r in rows if r["walls_facing_out"] is not None]
        print(json.dumps({"summary": True, "meshes": len(rows),
                          "median_roofs_facing_up": float(np.median(up)) if up else None,
                          "meshes_roofs_up_below_0.95": sum(1 for x in up if x < 0.95),
                          "median_walls_facing_out": float(np.median(wo)) if wo else None,
                          "meshes_walls_out_below_0.9": sum(1 for x in wo if x < 0.9)}))


if __name__ == "__main__":
    main()
