"""Revit model (surface) fill pattern for ELM Vivid Ligne Noir, matching the delivered maps.

Writes textures/ELM_Vivid_Ligne_Noir_Model.pat with two model patterns (tiles vertical, the
layout of the maps, and tiles horizontal). Pattern lines are the joint centrelines of the
2.75 x 9.6875 in drawn tile (actual 9.66, see b01_build.py) with a 3/16 in joint: module 2.9375 x 9.875 in.

Verification (independent of the writer): re-parses the .pat, expands every line family into
segments over the whole map, rasterises them at the map's 100 px/in with the image top-left
corner at the pattern origin (a joint intersection, as built), and measures
  * hit rate: share of sampled pattern points that fall on grout pixels of Color.png
  * coverage: share of grout-centre pixels within 1 px of a pattern line.
Writes textures/model_pattern_check.json and _PREVIEW_model_pattern.jpg; exits non-zero on failure.
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
PPI = 100
TILE_W, TILE_H, JOINT = 2.75, 9.6875, 0.1875   # drawn length, see b01_build.py
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT
PAT = "textures/ELM_Vivid_Ligne_Noir_Model.pat"

PATTERNS = [
    ("ELM Vivid Ligne Noir R2 - Vertical stack",
     "2.75x9-11/16in tile 3/16in joint - tiles vertical - matches colour and bump maps",
     [(0, 0, 0, 0, MOD_H, []), (90, 0, 0, 0, MOD_W, [])]),
    ("ELM Vivid Ligne Noir R2 - Horizontal stack",
     "2.75x9-11/16in tile 3/16in joint - tiles horizontal - rotate maps 90 deg",
     [(0, 0, 0, 0, MOD_W, []), (90, 0, 0, 0, MOD_H, [])]),
]


def fmt(v):
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_pat():
    lines = [";%UNITS=INCH", ";%VERSION=3.0",
             ";; ELM Vivid Ligne Noir model patterns, generated 2026-09-26 by source/e01_model_pattern.py"]
    for name, desc, fams in PATTERNS:
        lines += ["*%s, %s" % (name, desc), ";%TYPE=MODEL"]
        for ang, x, y, sh, off, dash in fams:
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
    R = math.hypot(w, h) + 20
    for f in fams:
        ang, ox, oy, sh, off = f[:5]
        dash = f[5:]
        a = math.radians(ang)
        d = np.array([math.cos(a), math.sin(a)])
        n = np.array([-math.sin(a), math.cos(a)])
        period = sum(abs(v) for v in dash) if dash else None
        kmax = int(R / abs(off)) + 2
        for k in range(-kmax, kmax + 1):
            o = np.array([ox, oy]) + k * (sh * d + off * n)
            # parameter range along the line covering the window
            c = np.array([w / 2, -h / 2])
            t0 = np.dot(c - o, d)
            if abs(np.dot(c - o, n)) > R:
                continue
            if not dash:
                p0, p1 = o + (t0 - R) * d, o + (t0 + R) * d
                segs.append((*p0, *p1))
                continue
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
    c = np.asarray(Image.open(out_path("textures/Color.png")))
    H, W = c.shape[:2]
    grout = c.mean(2) > 128
    pats = parse_pat(out_path(PAT))
    segs = expand(pats["ELM Vivid Ligne Noir R2 - Vertical stack"], W / PPI, H / PPI)
    # image coordinates: x = x_pat, y = -y_pat (image y points down), in px
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    pts = []
    for x0, y0, x1, y1 in segs:
        a = (x0 * PPI, -y0 * PPI)
        b = (x1 * PPI, -y1 * PPI)
        dr.line([a, b], fill=255, width=1)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        for t in np.linspace(0, 1, max(2, int(L / 5))):
            px, py = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            if 0 <= px < W and 0 <= py < H:
                pts.append((int(py), int(px)))
    pts = np.array(pts)
    hit = float(grout[pts[:, 0], pts[:, 1]].mean())
    line = np.asarray(img) > 0
    # analytic offset: centre of every grout run on sampled scan lines vs the nearest pattern line,
    # with lines intersected exactly (not rasterised)
    offs, orphans = [], 0
    for axis in (0, 1):          # 0: scan rows -> vertical joints; 1: scan columns -> horizontal joints
        n_scan = H if axis == 0 else W
        for s in np.linspace(150, n_scan - 150, 25).astype(int):
            g = grout[s] if axis == 0 else grout[:, s]
            e = np.flatnonzero(np.diff(g.astype(np.int8)))
            runs = [(e[i] + 1, e[i + 1]) for i in range(len(e) - 1) if g[e[i] + 1]]
            # pattern crossings of this scan line (pixel units, pixel centres at +0.5)
            q = (s + 0.5) / PPI
            cross = []
            for x0, y0, x1, y1 in segs:
                if axis == 0:   # horizontal scan at image y = q -> pattern y = -q
                    if (y0 + q) * (y1 + q) <= 0 and y0 != y1:
                        cross.append((x0 + (x1 - x0) * (-q - y0) / (y1 - y0)) * PPI)
                else:           # vertical scan at x = q
                    if (x0 - q) * (x1 - q) <= 0 and x0 != x1:
                        cross.append(-(y0 + (y1 - y0) * (q - x0) / (x1 - x0)) * PPI)
            cross = np.array(sorted(set(np.round(cross, 6))))
            for r0, r1 in runs:
                cen = (r0 + r1 + 1) / 2.0
                d = np.abs(cross - cen).min() if len(cross) else 1e9
                if d > JOINT * PPI / 2:
                    orphans += 1
                else:
                    offs.append(d)
    offs = np.array(offs)
    cover = float(len(offs) / (len(offs) + orphans))
    # preview: 800 px crop at 1:1 over a joint crossing plus the whole map, lines in red
    x0, y0 = int(3 * MOD_W * PPI) - 400, int(MOD_H * PPI) - 400
    crop = c[y0:y0 + 800, x0:x0 + 800].copy()
    crop[line[y0:y0 + 800, x0:x0 + 800]] = (255, 0, 0)
    Image.fromarray(crop).save(out_path("textures/_PREVIEW_model_pattern.jpg"), quality=90)
    res = {"pattern": PAT, "hit_rate_on_grout": hit, "joints_with_a_pattern_line": cover,
           "max_offset_px": float(offs.max()), "median_offset_px": float(np.median(offs)),
           "joint_runs_checked": int(len(offs)), "segments": len(segs),
           "pass": bool(hit > 0.99 and cover == 1.0 and offs.max() <= 1.0)}
    json.dump(res, open(out_path("textures/model_pattern_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res["pass"]


if __name__ == "__main__":
    write_pat()
    print(open(out_path(PAT)).read())
    sys.exit(0 if check() else 1)
