"""Revit model (surface) fill patterns matching the delivered maps (stack bond, both products).

Writes <dir>/<file>.pat with two model patterns each:
  1. "... - Stack Horizontal": long side horizontal, the layout of the maps
  2. "... - Stack Vertical":   the same pattern rotated 90 deg (rotate the maps 90 deg to match)
Lines are the joint centrelines at real scale (drawn tile + joint module). Pattern origin = the maps' top-left
corner (a joint-centre crossing); the first tile face starts JOINT/2 right of and JOINT/2 below the origin.
Pattern x = image x, pattern y = -image y.

Verification (independent of the writer): re-parses the .pat, expands every family into segments over the
map, and for both patterns (the rotated one against the maps rotated 90 deg CCW)
  * compares every grout run's centre on sampled scan lines with the exact analytic line crossing
    (every run must be matched, max offset <= 1 px)
  * checks every sampled line point lies on grout (bump height below GROUT_MM).
Writes <dir>/model_pattern_check.json and <dir>/_PREVIEW_model_pattern.jpg (1:1, pattern lines red).
Usage: python e01_model_pattern.py veincut_24x48|mosaic_1x3 [--check-only]"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

from guard import out_path

Image.MAX_IMAGE_PIXELS = None


def spec(prod):
    rep = json.load(open(out_path(prod + "/report.json")))
    if prod == "veincut_24x48":
        mw, mh = rep["module_in"]
        name = "ELM Jute Vein-Cut 24x48"
        desc = "600x1200mm drawn 47-5/24x23-5/8in 1/8in joint - stack bond"
        pat = prod + "/ELM_Jute_Vein_Cut_24x48_Model.pat"
    else:
        mw, mh = rep["chip_pitch_in"]
        name = "ELM Jute Vein-Cut 1x3 Mosaic"
        desc = "1x3 chips 2-15/16x15/16in 1/16in joint - stack"
        pat = prod + "/ELM_Jute_Vein_Cut_1x3_Mosaic_Model.pat"
    n1, n2 = name + " - Stack Horizontal", name + " - Stack Vertical"
    pats = [(n1, desc + " - long side horizontal - matches maps", [(0, 0, 0, 0, mh), (90, 0, 0, 0, mw)]),
            (n2, desc + " - long side vertical - rotate maps 90 deg", [(90, 0, 0, 0, mh), (0, 0, 0, 0, mw)])]
    return rep, mw, mh, name, pat, n1, n2, pats


def fmt(v):
    s = ("%.8f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_pat(prod):
    rep, mw, mh, name, pat, n1, n2, pats = spec(prod)
    lines = [";%UNITS=INCH", ";%VERSION=3.0",
             ";; %s model patterns, generated 2026-09-26 by source/e01_model_pattern.py" % name,
             ";; origin = texture maps' top-left corner (joint-centre crossing); first tile face starts %s in right, %s in down" % (
                 fmt(rep["joint_in"] / 2), fmt(rep["joint_in"] / 2))]
    for nm, desc, fams in pats:
        lines += ["*%s, %s" % (nm, desc), ";%TYPE=MODEL"]
        for fam in fams:
            lines.append(", ".join(fmt(v) for v in fam))
    open(out_path(pat), "w", newline="\r\n").write("\n".join(lines) + "\n")


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


def check_one(grout, segs, label, ppi, joint_px):
    H, W = grout.shape
    pts = []
    for x0, y0, x1, y1 in segs:
        a = (x0 * ppi, -y0 * ppi)
        b = (x1 * ppi, -y1 * ppi)
        # clip to the image
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
        for s in np.linspace(7, n_scan - 7, 61).astype(int):
            g = grout[s] if axis == 0 else grout[:, s]
            if g.mean() > 0.5:
                continue                         # scan line runs along a joint
            e = np.flatnonzero(np.diff(g.astype(np.int8)))
            runs = [(e[i] + 1, e[i + 1]) for i in range(len(e) - 1) if g[e[i] + 1]]
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
                dmin = np.abs(cross - cen).min() if len(cross) else 1e9
                if dmin > joint_px / 2 + 1:
                    orphans += 1
                else:
                    offs.append(dmin)
    offs = np.array(offs)
    return {"pattern": label, "segments": len(segs), "sampled_points": int(len(pts)),
            "points_on_grout": float(on.mean()), "joint_runs_matched": int(len(offs)),
            "joint_runs_unmatched": int(orphans), "max_offset_px": float(offs.max()) if len(offs) else None,
            "median_offset_px": float(np.median(offs)) if len(offs) else None,
            "pass": bool(on.all() and orphans == 0 and len(offs) > 50 and offs.max() <= 1.0)}


def check(prod):
    rep, mw, mh, name, pat, n1, n2, _ = spec(prod)
    ppi = rep["ppi"]
    b = np.asarray(Image.open(out_path(prod + "/Bump16.png"))).astype(np.float64)
    h = b / 65535 * rep["relief_mm"]["full_scale"]
    grout_mm = 0.2 * rep["relief_mm"]["face_design"]
    grout = h < grout_mm
    H, W = grout.shape
    pats, hdr = parse_pat(out_path(pat))
    hdr_ok = hdr[0] == ";%UNITS=INCH" and hdr[1] == ";%VERSION=3.0" and sum(1 for x in hdr if x == ";%TYPE=MODEL") == 2
    jpx = rep["joint_in"] * ppi
    s1 = expand(pats[n1], W / ppi, H / ppi)
    r1 = check_one(grout, s1, n1, ppi, jpx)
    g2 = np.rot90(grout, 1)
    s2 = expand(pats[n2], g2.shape[1] / ppi, g2.shape[0] / ppi)
    r2 = check_one(g2, s2, n2 + " (maps rotated 90 deg CCW)", ppi, jpx)
    # 1:1 overlay preview around an interior joint crossing
    c = np.asarray(Image.open(out_path(prod + "/Color.png"))).copy()
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in s1:
        dr.line([(x0 * ppi, -y0 * ppi), (x1 * ppi, -y1 * ppi)], fill=255, width=1)
    line = np.asarray(img) > 0
    cx, cy = int(round(mw * ppi * (1 if prod == "veincut_24x48" else 3))), int(round(mh * ppi * (1 if prod == "veincut_24x48" else 8)))
    x0, y0 = max(cx - 400, 0), max(cy - 400, 0)
    crop = c[y0:y0 + 800, x0:x0 + 800].copy()
    crop[line[y0:y0 + 800, x0:x0 + 800]] = (255, 0, 0)
    Image.fromarray(crop).save(out_path(prod + "/_PREVIEW_model_pattern.jpg"), quality=92)
    res = {"file": pat, "header_ok": bool(hdr_ok), "grout_definition": "bump height < %.2f mm" % grout_mm,
           "horizontal": r1, "vertical": r2, "pass": bool(hdr_ok and r1["pass"] and r2["pass"])}
    json.dump(res, open(out_path(prod + "/model_pattern_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res["pass"]


if __name__ == "__main__":
    prod = sys.argv[1]
    if "--check-only" not in sys.argv:
        write_pat(prod)
    print(open(out_path(spec(prod)[4])).read())
    sys.exit(0 if check(prod) else 1)
