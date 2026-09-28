"""Revit model (surface) fill pattern for ELM Formed Hexagon Sand, matching the delivered maps.

Writes textures/ELM_Formed_Hexagon_Sand_Model.pat: flat-top hexagons, 10 in across the flats with a
1/8 in joint, so the joint-centreline hexagon is 10.125 in across the flats, side a = 10.125/sqrt(3).
Three line families (0, 60, 120 deg), each a dash of a and a gap of 2a, shift 1.5a, offset F/2.

The pattern origin is the colour map's top-left corner (pattern x = image x, pattern y = -image y).
The first face centre is at (0.5 * 8.7685, -0.5 * 10.125) in (report.json face_index_order).

Verification (independent of the writer): re-parses the .pat, expands the families over the whole
map, and on 25 row and 25 column scan lines compares the centre of every joint run in face_ids.png
(0 = joint) with the exact crossing of the nearest pattern line. Also samples points along the
lines and requires them to land on joint pixels. Writes textures/model_pattern_check.json and
textures/_PREVIEW_model_pattern.jpg; exits non-zero on failure.
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
F = 10.125                       # joint-centreline hexagon, across the flats (in)
A = F / math.sqrt(3)             # side = circumradius
COL_PITCH = 1.5 * A              # 8.7685 in
SAMPLE_W, SAMPLE_H = 8 * COL_PITCH, 7 * F
CX, CY = 0.5 * COL_PITCH, -0.5 * F   # first face centre, pattern coordinates (y up)
PAT = "textures/ELM_Formed_Hexagon_Sand_Model.pat"
NAME = "ELM Formed Hexagon Sand - 10in hex"


def rot(x, y, deg):
    t = math.radians(deg)
    return x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)


def families():
    fams = []
    for ang in (0, 60, 120):
        ox, oy = rot(-A / 2, F / 2, ang)      # start vertex of the top edge, rotated about the centre
        fams.append((ang, CX + ox, CY + oy, COL_PITCH, F / 2, [A, -2 * A]))
    return fams


def fmt(v):
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_pat():
    lines = [";%UNITS=INCH", ";%VERSION=3.0",
             ";; ELM Formed Hexagon Sand model pattern, generated 2026-09-26 by source/e01_model_pattern.py",
             ";; origin = top-left corner of the colour and bump maps; Sample Size 70.148 x 70.875 in",
             "*%s, flat-top 10in across flats 1/8in joint - matches colour and bump maps" % NAME,
             ";%TYPE=MODEL"]
    for ang, x, y, sh, off, dash in families():
        lines.append(", ".join(fmt(v) for v in [ang, x, y, sh, off] + list(dash)))
    open(out_path(PAT), "w", newline="\r\n").write("\n".join(lines) + "\n")


def parse_pat(path):
    pats, cur = {}, None
    for raw in open(path):
        s = raw.strip()
        if not s or s.startswith(";"):
            continue
        if s.startswith("*"):
            cur = s[1:].split(",")[0].strip()
            pats[cur] = []
            continue
        pats[cur].append([float(t) for t in s.split(",")])
    return pats


def expand(fams, w, h):
    """Segments (x0, y0, x1, y1) in pattern inches (y up) covering [0,w] x [-h,0]."""
    segs = []
    R = math.hypot(w, h) + 30
    c = np.array([w / 2, -h / 2])
    for f in fams:
        ang, ox, oy, sh, off = f[:5]
        dash = f[5:]
        a = math.radians(ang)
        d = np.array([math.cos(a), math.sin(a)])
        n = np.array([-math.sin(a), math.cos(a)])
        period = sum(abs(v) for v in dash)
        kmax = int(R / abs(off)) + 2
        for k in range(-kmax, kmax + 1):
            o = np.array([ox, oy]) + k * (sh * d + off * n)
            if abs(np.dot(c - o, n)) > R:
                continue
            t0 = np.dot(c - o, d)
            m0 = math.floor((t0 - R) / period)
            for m in range(m0, m0 + int(2 * R / period) + 2):
                t = m * period
                for v in dash:
                    if v > 0:
                        p0, p1 = o + t * d, o + (t + v) * d
                        segs.append((*p0, *p1))
                    t += abs(v)
    return segs


def check():
    fid = np.asarray(Image.open(out_path("textures/face_ids.png")))
    H, W = fid.shape
    joint = fid == 0
    sx, sy = W / SAMPLE_W, H / SAMPLE_H          # px per inch in x and y
    segs = expand(parse_pat(out_path(PAT))[NAME], SAMPLE_W, SAMPLE_H)
    # points along the lines must land on joint pixels (1/8 in joint = 8 px wide)
    pts = []
    for x0, y0, x1, y1 in segs:
        L = math.hypot(x1 - x0, y1 - y0) * sx
        for t in np.linspace(0.02, 0.98, max(2, int(L / 4))):
            px, py = (x0 + t * (x1 - x0)) * sx, -(y0 + t * (y1 - y0)) * sy
            if 0 <= px < W and 0 <= py < H:
                pts.append((int(py), int(px)))
    pts = np.array(pts)
    hit = float(joint[pts[:, 0], pts[:, 1]].mean())
    # joint-run centres vs exact line crossings
    offs, orphans = [], 0
    for axis in (0, 1):
        n_scan = H if axis == 0 else W
        for s in np.linspace(40, n_scan - 40, 25).astype(int):
            g = joint[s] if axis == 0 else joint[:, s]
            e = np.flatnonzero(np.diff(g.astype(np.int8)))
            runs = [(e[i] + 1, e[i + 1]) for i in range(len(e) - 1) if g[e[i] + 1]]
            cross = []
            if axis == 0:
                q = -(s + 0.5) / sy
                for x0, y0, x1, y1 in segs:
                    if y0 != y1 and (y0 - q) * (y1 - q) <= 0:
                        cross.append((x0 + (x1 - x0) * (q - y0) / (y1 - y0)) * sx)
            else:
                q = (s + 0.5) / sx
                for x0, y0, x1, y1 in segs:
                    if x0 != x1 and (x0 - q) * (x1 - q) <= 0:
                        cross.append(-(y0 + (y1 - y0) * (q - x0) / (x1 - x0)) * sy)
            cross = np.array(cross)
            for r0, r1 in runs:
                if r1 - r0 + 1 > 30:       # scan running along a horizontal joint: not a crossing
                    continue
                cen = (r0 + r1 + 1) / 2.0
                d = np.abs(cross - cen).min() if len(cross) else 1e9
                if d > 6:
                    orphans += 1
                else:
                    offs.append(d)
    offs = np.array(offs)
    cover = float(len(offs) / (len(offs) + orphans))
    # preview: 800 px crop of the colour map at 1:1 with the pattern in red
    c = np.asarray(Image.open(out_path("textures/Color.png")).convert("RGB"))
    img = Image.fromarray(c[1400:2200, 1400:2200].copy())
    dr = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in segs:
        dr.line([(x0 * sx - 1400, -y0 * sy - 1400), (x1 * sx - 1400, -y1 * sy - 1400)], fill=(255, 0, 0), width=1)
    img.save(out_path("textures/_PREVIEW_model_pattern.jpg"), quality=90)
    res = {"pattern": PAT, "side_in": A, "across_flats_in": F, "origin": "map top-left corner",
           "hit_rate_on_joint": hit, "joints_with_a_pattern_line": cover,
           "max_offset_px": float(offs.max()), "median_offset_px": float(np.median(offs)),
           "joint_runs_checked": int(len(offs)), "segments": len(segs),
           "pass": bool(hit > 0.98 and cover == 1.0 and offs.max() <= 1.5)}
    json.dump(res, open(out_path("textures/model_pattern_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res["pass"]


if __name__ == "__main__":
    write_pat()
    print(open(out_path(PAT)).read())
    sys.exit(0 if check() else 1)
