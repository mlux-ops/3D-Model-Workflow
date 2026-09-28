"""Revit model (surface) fill pattern for the Porcelanosa Vendome Nature 47x47 tile grid.

One pattern: a square stack-bond grid is identical when rotated 90 degrees, and the product has no diagonal
(45 degree) layout, so no second pattern is needed. Lines are the joint centrelines at the drawn module 47.25 in
(47-3/16 in drawn face + 1/16 in joint). Pattern origin = the maps' top-left corner (a joint-centre crossing);
the first tile face starts 1/32 in right of and 1/32 in below the origin. Pattern x = image x, y = -image y.
The same pattern fits all three map sets (designed, free_mix, pieces), whose top-left corners are all joint
crossings on the same 47.25 in grid.

Verification (independent of the writer): re-parses the .pat from disk, expands every family into segments over
each map, then on 61 + 61 sampled scan lines compares every grout run's centre (grout = bump height 0) with the
exact analytic line crossing (every run matched, max offset <= 1 px), and checks every sampled pattern-line
point lies on grout. Writes _work/model_pattern_check.json and designed/_PREVIEW_model_pattern_1to1.jpg.
Usage: python e01_model_pattern.py [--check-only]"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
PAT = "_work/Porcelanosa_Vendome_Nature_47x47_Model.pat"
NAME = "Porcelanosa Vendome Nature 47x47 - Stack"
DESC = "1200x1200mm drawn 47-3/16in + 1/16in joint = 47-1/4in grid"
MOD = 47.25
JOINT = 1.0 / 16.0
FAMS = [(0, 0, 0, 0, MOD), (90, 0, 0, 0, MOD)]
SETS = [("designed", "designed/Bump16.png"), ("free_mix", "free_mix/Bump16.png"), ("piece_1", "pieces/Piece_1_Bump16.png")]


def fmt(v):
    s = ("%.8f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_pat():
    lines = [";%UNITS=INCH", ";%VERSION=3.0",
             ";; Porcelanosa Vendome Nature 47x47 (code 100348304) model pattern, generated 2026-09-27 by source/e01_model_pattern.py",
             ";; origin = texture maps' top-left corner (joint-centre crossing); first tile face starts %s in right, %s in down" % (
                 fmt(JOINT / 2), fmt(JOINT / 2)),
             "*%s, %s" % (NAME, DESC), ";%TYPE=MODEL"]
    lines += [", ".join(fmt(v) for v in f) for f in FAMS]
    open(out_path(PAT), "w", newline="\r\n").write("\n".join(lines) + "\n")


def parse_pat(path):
    pats, cur, hdr = {}, None, []
    for raw in open(path):
        s = raw.strip()
        if not s:
            continue
        if s.startswith(";"):
            hdr.append(s)
            continue
        if s.startswith("*"):
            cur = s[1:].split(",")[0].strip()
            pats[cur] = []
            continue
        pats[cur].append([float(t) for t in s.split(",")])
    return pats, hdr


def expand(fams, w, h):
    """Segments (x0, y0, x1, y1) in pattern inches (y up) covering [0,w] x [-h,0]."""
    segs = []
    R = math.hypot(w, h) + 20
    c = np.array([w / 2, -h / 2])
    for f in fams:
        ang, ox, oy, sh, off = f[:5]
        a = math.radians(ang)
        d = np.array([math.cos(a), math.sin(a)])
        n = np.array([-math.sin(a), math.cos(a)])
        kmax = int(R / abs(off)) + 2
        for k in range(-kmax, kmax + 1):
            o = np.array([ox, oy]) + k * (sh * d + off * n)
            if abs(np.dot(c - o, n)) > R:
                continue
            t0 = np.dot(c - o, d)
            p0, p1 = o + (t0 - R) * d, o + (t0 + R) * d
            segs.append((*p0, *p1))
    return segs


def check_one(grout, segs, label, ppi, joint_px):
    H, W = grout.shape
    pts = []
    for x0, y0, x1, y1 in segs:
        a = (x0 * ppi, -y0 * ppi)
        b = (x1 * ppi, -y1 * ppi)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        for t in np.linspace(0, 1, max(2, int(L / 3))):
            px, py = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            # a line exactly on a pixel boundary (x = k * 1512) is sampled on both adjoining pixels
            for qx, qy in ((px, py), (px - 1e-6, py - 1e-6)):
                if 0 <= qx < W and 0 <= qy < H:
                    pts.append((min(int(qy), H - 1), min(int(qx), W - 1)))
    pts = np.array(pts)
    on = grout[pts[:, 0], pts[:, 1]]
    offs, orphans = [], 0
    for axis in (0, 1):
        n_scan = H if axis == 0 else W
        for s in np.linspace(7, n_scan - 7, 61).astype(int):
            g = grout[s] if axis == 0 else grout[:, s]
            if g.mean() > 0.5:
                continue
            gp = np.r_[False, g, False]
            e = np.flatnonzero(np.diff(gp.astype(np.int8)))
            runs = [(e[i], e[i + 1] - 1) for i in range(0, len(e), 2)]
            q = (s + 0.5) / ppi
            cross = []
            for x0, y0, x1, y1 in segs:
                if axis == 0:
                    if (y0 + q) * (y1 + q) <= 0 and y0 != y1:
                        cross.append((x0 + (x1 - x0) * (-q - y0) / (y1 - y0)) * ppi)
                else:
                    if (x0 - q) * (x1 - q) <= 0 and x0 != x1:
                        cross.append(-(y0 + (y1 - y0) * (q - x0) / (x1 - x0)) * ppi)
            cross = np.array(sorted(set(np.round(cross, 6))))
            for r0, r1 in runs:
                if r1 - r0 + 1 > 3 * joint_px + 2:
                    continue
                cen = (r0 + r1 + 1) / 2.0
                if r0 == 0 or r1 == len(g) - 1:          # half joint on the image edge: centre is the edge itself
                    cen = 0.0 if r0 == 0 else float(len(g))
                dmin = np.abs(cross - cen).min() if len(cross) else 1e9
                if dmin > joint_px / 2 + 1:
                    orphans += 1
                else:
                    offs.append(dmin)
    offs = np.array(offs)
    return {"map": label, "segments": len(segs), "sampled_points": int(len(pts)),
            "points_on_grout": float(on.mean()), "joint_runs_matched": int(len(offs)),
            "joint_runs_unmatched": int(orphans), "max_offset_px": float(offs.max()) if len(offs) else None,
            "median_offset_px": float(np.median(offs)) if len(offs) else None,
            "pass": bool(on.all() and orphans == 0 and len(offs) >= 20 and offs.max() <= 1.0)}


def check():
    ppi = 32
    pats, hdr = parse_pat(out_path(PAT))
    hdr_ok = (hdr[0] == ";%UNITS=INCH" and hdr[1] == ";%VERSION=3.0"
              and sum(1 for x in hdr if x == ";%TYPE=MODEL") == len(pats) == 1 and NAME in pats)
    res = {"file": PAT, "header_ok": bool(hdr_ok), "patterns": list(pats), "families": pats.get(NAME),
           "grout_definition": "bump height == 0 (grout floor)", "maps": []}
    for label, p in SETS:
        b = np.asarray(Image.open(out_path(p)))
        grout = b == 0
        H, W = grout.shape
        segs = expand(pats[NAME], W / ppi, H / ppi)
        res["maps"].append(check_one(grout, segs, label, ppi, JOINT * ppi))
        if label == "designed":
            c = np.asarray(Image.open(out_path("designed/Color.png")).convert("RGB")).copy()
            img = Image.new("L", (W, H), 0)
            dr = ImageDraw.Draw(img)
            for x0, y0, x1, y1 in segs:
                dr.line([(x0 * ppi, -y0 * ppi), (x1 * ppi, -y1 * ppi)], fill=255, width=1)
            line = np.asarray(img) > 0
            cx, cy = 1512, 1512
            crop = c[cy - 400:cy + 400, cx - 400:cx + 400].copy()
            crop[line[cy - 400:cy + 400, cx - 400:cx + 400]] = (255, 0, 0)
            Image.fromarray(crop).save(out_path("designed/_PREVIEW_model_pattern_1to1.jpg"), quality=92)
            # right half: same crop without the overlay, to see the grout underneath
            Image.fromarray(c[cy - 40:cy + 40, cx - 40:cx + 40].repeat(8, 0).repeat(8, 1)).save(
                out_path("designed/_PREVIEW_model_pattern_crossing_x8_no_overlay.jpg"), quality=92)
            ov = c[cy - 40:cy + 40, cx - 40:cx + 40].copy()
            ov[line[cy - 40:cy + 40, cx - 40:cx + 40]] = (255, 0, 0)
            Image.fromarray(ov.repeat(8, 0).repeat(8, 1)).save(out_path("designed/_PREVIEW_model_pattern_crossing_x8.jpg"), quality=92)
    res["pass"] = bool(hdr_ok and all(m["pass"] for m in res["maps"]))
    json.dump(res, open(out_path("_work/model_pattern_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res["pass"]


if __name__ == "__main__":
    if "--check-only" not in sys.argv:
        write_pat()
    print(open(out_path(PAT)).read())
    sys.exit(0 if check() else 1)
