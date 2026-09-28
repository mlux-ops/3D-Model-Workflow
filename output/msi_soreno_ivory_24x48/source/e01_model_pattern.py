"""Revit model (surface) fill pattern for MSI Soreno Ivory 24x48, matching the delivered maps.

Writes textures/MSI_Soreno_Ivory_24x48_Model.pat with two model patterns:
  1. "... - 1-3 Bond Horizontal": tiles horizontal, the layout of the maps
  2. "... - 1-3 Bond Vertical":   the same pattern rotated 90 deg (rotate the maps 90 deg to match)
Lines are the joint centrelines of the drawn 47.2083 x 23.625 in tile with a 1/8 in joint
(module 47.3333 x 23.75 in); each row steps +1/3 module (15.7778 in). Vertical joints are dashed
families (dash one module height, gap two, period three rows). Pattern origin = the maps' top-left
corner, pattern x = image x, pattern y = -image y.

Verification (independent of the writer): re-parses the .pat, expands every family into segments over
the map, and for both patterns (the rotated one against the maps rotated 90 deg CCW)
  * compares every grout run's centre on sampled scan lines with the exact analytic line crossing
    (all runs must be matched, max offset <= 1 px)
  * checks every sampled line point lies on grout (bump height < 0.3 mm).
Writes textures/model_pattern_check.json and textures/_PREVIEW_model_pattern.jpg; exits non-zero on failure.
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
PPI = 24
TILE_W, TILE_H, JOINT = 47.0 + 5.0 / 24.0, 23.625, 0.125   # drawn, see b01_build.py
MOD_W, MOD_H = TILE_W + JOINT, TILE_H + JOINT
OFF = MOD_W / 3.0
PAT = "textures/MSI_Soreno_Ivory_24x48_Model.pat"
N1 = "MSI Soreno Ivory 24x48 - 1-3 Bond Horizontal"
N2 = "MSI Soreno Ivory 24x48 - 1-3 Bond Vertical"
PATTERNS = [
    (N1, "600x1200mm drawn 47-5/24x23-5/8in 1/8in joint - 1/3 offset - tiles horizontal - matches maps",
     [(0, 0, 0, 0, MOD_H, []),
      (90, 0, -MOD_H, MOD_H, OFF, [MOD_H, -2 * MOD_H])]),
    (N2, "600x1200mm drawn 47-5/24x23-5/8in 1/8in joint - 1/3 offset - tiles vertical - rotate maps 90 deg",
     [(90, 0, 0, 0, MOD_H, []),
      (0, 0, 0, MOD_H, OFF, [MOD_H, -2 * MOD_H])]),
]
GROUT_MM = 0.3


def fmt(v):
    s = ("%.8f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_pat():
    lines = [";%UNITS=INCH", ";%VERSION=3.0",
             ";; MSI Soreno Ivory 24x48 (NSORIVO2448) model patterns, generated 2026-09-26 by source/e01_model_pattern.py"]
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
    c = np.array([w / 2, -h / 2])
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
            if abs(np.dot(c - o, n)) > R:
                continue
            t0 = np.dot(c - o, d)
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


def check_one(grout, segs, label):
    H, W = grout.shape
    pts = []
    for x0, y0, x1, y1 in segs:
        a = (x0 * PPI, -y0 * PPI)
        b = (x1 * PPI, -y1 * PPI)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        for t in np.linspace(0, 1, max(2, int(L / 3))):
            px, py = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            if 0 <= px < W and 0 <= py < H:
                pts.append((min(int(py), H - 1), min(int(px), W - 1)))
    pts = np.array(pts)
    on = grout[pts[:, 0], pts[:, 1]]
    offs, orphans = [], 0
    for axis in (0, 1):          # 0: scan rows -> vertical joints; 1: scan columns -> horizontal joints
        n_scan = H if axis == 0 else W
        for s in np.linspace(40, n_scan - 40, 41).astype(int):
            g = grout[s] if axis == 0 else grout[:, s]
            e = np.flatnonzero(np.diff(g.astype(np.int8)))
            runs = [(e[i] + 1, e[i + 1]) for i in range(len(e) - 1) if g[e[i] + 1]]
            q = (s + 0.5) / PPI
            cross = []
            for x0, y0, x1, y1 in segs:
                if axis == 0:
                    if (y0 + q) * (y1 + q) <= 0 and y0 != y1:
                        cross.append((x0 + (x1 - x0) * (-q - y0) / (y1 - y0)) * PPI)
                else:
                    if (x0 - q) * (x1 - q) <= 0 and x0 != x1:
                        cross.append(-(y0 + (y1 - y0) * (q - x0) / (x1 - x0)) * PPI)
            cross = np.array(sorted(set(np.round(cross, 6))))
            for r0, r1 in runs:
                if r1 - r0 + 1 > 8:      # a run along a joint (scan line inside a joint), not across it
                    continue
                cen = (r0 + r1 + 1) / 2.0
                dmin = np.abs(cross - cen).min() if len(cross) else 1e9
                if dmin > JOINT * PPI / 2 + 1:
                    orphans += 1
                else:
                    offs.append(dmin)
    offs = np.array(offs)
    return {"pattern": label, "segments": len(segs), "sampled_points": int(len(pts)),
            "points_on_grout": float(on.mean()), "joint_runs_matched": int(len(offs)),
            "joint_runs_unmatched": int(orphans), "max_offset_px": float(offs.max()),
            "median_offset_px": float(np.median(offs)),
            "pass": bool(on.all() and orphans == 0 and len(offs) > 50 and offs.max() <= 1.0)}


def check():
    rep = json.load(open(out_path("textures/report.json")))
    b = np.asarray(Image.open(out_path("textures/Bump16.png"))).astype(np.float64)
    h = b / 65535 * rep["relief_mm"]["full_scale"]
    grout = h < GROUT_MM
    H, W = grout.shape
    pats = parse_pat(out_path(PAT))
    s1 = expand(pats[N1], W / PPI, H / PPI)
    r1 = check_one(grout, s1, N1)
    g2 = np.rot90(grout, 1)
    s2 = expand(pats[N2], g2.shape[1] / PPI, g2.shape[0] / PPI)
    r2 = check_one(g2, s2, N2 + " (maps rotated 90 deg CCW)")
    # preview: 800 px crop at 1:1 around a T junction, pattern lines in red
    c = np.asarray(Image.open(out_path("textures/Color.png"))).copy()
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in s1:
        dr.line([(x0 * PPI, -y0 * PPI), (x1 * PPI, -y1 * PPI)], fill=255, width=1)
    line = np.asarray(img) > 0
    cx, cy = int(round((OFF + MOD_W) * PPI)), int(round(MOD_H * PPI))
    x0, y0 = cx - 400, cy - 400
    crop = c[y0:y0 + 800, x0:x0 + 800].copy()
    crop[line[y0:y0 + 800, x0:x0 + 800]] = (255, 0, 0)
    Image.fromarray(crop).save(out_path("textures/_PREVIEW_model_pattern.jpg"), quality=92)
    res = {"file": PAT, "grout_definition": "bump height < %.2f mm" % GROUT_MM, "horizontal": r1, "vertical": r2,
           "pass": bool(r1["pass"] and r2["pass"])}
    json.dump(res, open(out_path("textures/model_pattern_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res["pass"]


if __name__ == "__main__":
    if "--check-only" not in sys.argv:
        write_pat()
    print(open(out_path(PAT)).read())
    sys.exit(0 if check() else 1)
