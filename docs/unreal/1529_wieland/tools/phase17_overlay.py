"""Phase 17: draw a building's laser returns over a picture taken from a deck, with the picture's own camera.

Usage:
    python -B -P phase17_overlay.py <camera json> <picture png> <out png> <county id> [id ...]

<camera json>: {"loc": [x, y, z] level cm, "rot": [pitch, yaw, roll] degrees, "fov": horizontal degrees}.
Returns (classes other than ground, vegetation, water and noise) are taken to level cm with the Phase 2 level
frame, lowered by the curvature drop seen from the camera (as the meshes are), and projected with the engine's
camera convention (x forward, y right, z up; yaw about z, pitch up). Each return is a small dot, the highest return
of each image column in a brighter colour, so the scan's skyline can be compared with the model's.
"""

import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

FT = 0.3048006096
FRAME = os.path.join(HERE, "..", "review", "phase2", "level_frame.json")
PC = "D:/Wieland1529_lidar/derived"
SKIP = [2, 3, 4, 5, 7, 9, 18]


def returns(bid):
    xs, ys, zs = [], [], []
    for path in sorted(glob.glob(os.path.join(PC, "pc_*.npz"))):
        if path.endswith("_willis.npz") or not os.path.exists(path + ".source.txt"):
            continue
        d = np.load(path)
        labels = [str(v) for v in d["labels"]]
        if bid not in labels:
            continue
        sel = (d["box"] == labels.index(bid)) & ~np.isin(d["cls"], SKIP)
        xs.append(d["x"][sel]); ys.append(d["y"][sel]); zs.append(d["z"][sel])
    if not xs:
        return None
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(zs)


def project(frame, cam, e, n, z_ft, width, height):
    """Map feet to pixel columns and rows (and depth in cm)."""
    o = frame.origin_east_ft if hasattr(frame, "origin_east_ft") else None
    pts = np.array([frame.level_from_map(a, b, c) for a, b, c in zip(e, n, z_ft)], dtype=np.float64)
    loc = np.array(cam["loc"], dtype=np.float64)
    d = pts - loc
    dist_h = np.hypot(d[:, 0], d[:, 1]) / 100.0
    d[:, 2] -= dist_h * dist_h / (2.0 * 6371000.0) * (1.0 - 0.13) * 100.0
    p, y = math.radians(cam["rot"][0]), math.radians(cam["rot"][1])
    fwd = np.array([math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p)])
    right = np.array([-math.sin(y), math.cos(y), 0.0])
    up = np.array([-math.sin(p) * math.cos(y), -math.sin(p) * math.sin(y), math.cos(p)])
    zf = d @ fwd
    f = (width / 2.0) / math.tan(math.radians(cam["fov"]) / 2.0)
    u = width / 2.0 + (d @ right) / zf * f
    v = height / 2.0 - (d @ up) / zf * f
    return u, v, zf


def main(argv):
    cam = json.load(open(argv[1]))
    pic = Image.open(argv[2]).convert("RGB")
    out = argv[3]
    frame = g.LevelFrame.load(FRAME)
    W, H = pic.size
    draw = ImageDraw.Draw(pic)
    report = {}
    for bid in argv[4:]:
        r = returns(bid)
        if r is None:
            report[bid] = "no returns"
            continue
        x, y, z = r
        if len(x) > 400000:
            k = np.random.default_rng(1).choice(len(x), 400000, replace=False)
            x, y, z = x[k], y[k], z[k]
        u, v, zf = project(frame, cam, x, y, z, W, H)
        ok = (zf > 0) & (u >= 0) & (u < W) & (v >= 0) & (v < H)
        for a, b in zip(u[ok][::4], v[ok][::4]):
            draw.point((a, b), fill=(255, 60, 60))
        cols = np.floor(u[ok]).astype(int)
        top = {}
        for c, vv in zip(cols, v[ok]):
            if c not in top or vv < top[c]:
                top[c] = vv
        for c, vv in top.items():
            draw.rectangle([c, vv - 1, c, vv + 1], fill=(255, 255, 0))
        report[bid] = {"returns_drawn": int(ok.sum()), "highest_row": float(v[ok].min()) if ok.any() else None}
    pic.save(out)
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
