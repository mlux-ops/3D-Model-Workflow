"""Build the blind review set for the 2026-09-26 hex effort trial.

Usage: python build_blind.py [seed]

Four atlases (high, xhigh, max, and the 2026-09-19 baseline) are relabelled A-D at random.
The key goes to blind_key.json; only neutral labels appear in blind/. Every image is at most
800 px on each side so a reviewer can Read it. Grazing-light images are computed here by one
shared routine at one fixed height scale, so arms are compared at the same Revit bump amount
rather than through each arm's own preview.
"""
import json
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade_hex as g  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
OUT = os.path.join(g.HERE, "blind")
INPUTS = os.path.join(g.TRIAL, "inputs")
HEIGHT_MM = 1.5          # same full-range height for every atlas (equal Revit bump amount)
LIGHT_ELEV_DEG = 15.0    # grazing, as in the brief (<= 20 deg)
LIGHT_AZ_DEG = 200.0     # from the left and slightly above, like the lifestyle image
CROP = 256               # 4 in at 64 px/in


def out_path(name):
    p = os.path.abspath(os.path.join(OUT, name))
    if not p.startswith(os.path.abspath(OUT) + os.sep):
        raise ValueError(f"refusing to write outside {OUT}: {p}")
    return p


def save_jpg(im, name):
    if max(im.size) > 800:
        raise ValueError(f"{name} is {im.size}, over 800 px")
    im.save(out_path(name), quality=92)


def load(tex_dir, is_baseline):
    names = ("Hex10_Dimensional_Color.png", "Hex10_Dimensional_Bump16.png") if is_baseline else ("Color.png", "Bump16.png")
    col = np.asarray(Image.open(os.path.join(tex_dir, names[0])).convert("RGB")).astype(np.float64)
    bump = g.load_grey16(os.path.join(tex_dir, names[1]))
    fpath = os.path.join(tex_dir, "face_ids.png")
    ids = g.faces_from_bump(bump) if is_baseline or not os.path.exists(fpath) else g.load_grey16(fpath).astype(np.int32)
    return col, bump, ids


def grazing(col, h01, ppi):
    """Lambert shading of the colour by a height map already normalised 0..1 over the WHOLE atlas's
    range (never per crop, which would exaggerate flat faces), at a fixed physical height scale."""
    h = h01 * (HEIGHT_MM / 25.4 * ppi)   # height in pixels at this scale
    gy, gx = np.gradient(h)
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    el, az = np.radians(LIGHT_ELEV_DEG), np.radians(LIGHT_AZ_DEG)
    L = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    lam = np.clip(n @ L, 0, None) / np.sin(el)                    # flat face = 1.0
    shade = 0.3 + 0.7 * lam
    return np.clip(col * shade[..., None], 0, 255)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def wrap_crop(a, cy, cx, size):
    h, w = a.shape[:2]
    ys = (np.arange(cy - size // 2, cy - size // 2 + size)) % h
    xs = (np.arange(cx - size // 2, cx - size // 2 + size)) % w
    return a[np.ix_(ys, xs)]


def face_centres(ids):
    h, w = ids.shape
    cents = {}
    for fid in np.unique(ids):
        if fid == 0:
            continue
        yy, xx = np.nonzero(ids == fid)
        ay = np.angle(np.exp(2j * np.pi * yy / h).mean()) / (2 * np.pi) * h
        ax = np.angle(np.exp(2j * np.pi * xx / w).mean()) / (2 * np.pi) * w
        cents[int(fid)] = (int(round(ay)) % h, int(round(ax)) % w)
    return cents


def face_types(tex_dir, ids, bump, is_baseline):
    """Arm's own labels when present; otherwise the grader's independent classification."""
    labels = {}
    rpath = os.path.join(tex_dir, "report.json")
    if not is_baseline and os.path.exists(rpath):
        rep = json.load(open(rpath, encoding="utf-8"))
        for f in rep.get("faces") or rep.get("per_face") or []:
            if isinstance(f, dict) and "index" in f and "type" in f:
                labels[int(f["index"])] = str(f["type"]).lower()
    if labels:
        return labels
    full = float(bump.max() - bump.min()) or 1.0
    grey = np.zeros_like(bump)
    faces = g.face_crops(ids, [grey, bump])
    cls = {fid: g.classify(f["crops"][1], f["mask"], full) for fid, f in faces.items()}
    energies = np.array([v[0] for v in cls.values()])
    thr = max(0.004, float(np.percentile(energies, 20)) * 2.5)
    return {fid: ("matte" if e < thr else "chiseled" if c > 0.45 else "raw") for fid, (e, c, a) in cls.items()}


def build_one(label, tex_dir, is_baseline):
    col, bump, ids = load(tex_dir, is_baseline)
    h, w = bump.shape
    types = face_types(tex_dir, ids, bump, is_baseline)
    cents = face_centres(ids)

    # 1. whole atlas, colour
    save_jpg(to_img(col).resize((int(800 * w / h), 800) if h > w else (800, int(800 * h / w)), Image.LANCZOS), f"{label}_1_atlas.jpg")

    # 2. 2x2 repeat at 400 px per tile
    small = to_img(col).resize((400, int(400 * h / w)), Image.LANCZOS)
    rep = Image.new("RGB", (800, small.size[1] * 2))
    for oy in (0, small.size[1]):
        for ox in (0, 400):
            rep.paste(small, (ox, oy))
    rep = rep.crop((0, 0, 800, min(800, rep.size[1])))
    save_jpg(rep, f"{label}_2_repeat_2x2.jpg")

    # 3. centre region 1600x1600 (25 in) under grazing light, shown at half scale (32 px/in)
    cy, cx = h // 2, w // 2
    reg_c = wrap_crop(col, cy, cx, 1600)
    lo_all, full_all = float(bump.min()), float(bump.max() - bump.min()) or 1.0
    reg_b = (wrap_crop(bump, cy, cx, 1600) - lo_all) / full_all
    gz = grazing(reg_c, reg_b, g.PPI)
    save_jpg(to_img(gz).resize((800, 800), Image.LANCZOS), f"{label}_3_grazing_centre_25in.jpg")

    # 4. 1:1 crops (64 px/in, 4 in square) of one face per type: colour on top, grazing below
    sheet = Image.new("RGB", (3 * CROP, 2 * CROP + 18), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(("matte", "raw", "chiseled")):
        cand = [f for f, tt in types.items() if tt == t and f in cents]
        if not cand:
            d.text((i * CROP + 4, 2), f"{t}: none", fill=(0, 0, 0))
            continue
        f = min(cand, key=lambda k: (cents[k][0] - cy) ** 2 + (cents[k][1] - cx) ** 2)
        fy, fx = cents[f]
        cc = wrap_crop(col, fy, fx, CROP)
        bb = (wrap_crop(bump, fy, fx, CROP) - lo_all) / full_all
        sheet.paste(to_img(cc), (i * CROP, 18))
        sheet.paste(to_img(grazing(cc, bb, g.PPI)), (i * CROP, 18 + CROP))
        d.text((i * CROP + 4, 2), t, fill=(0, 0, 0))
    save_jpg(sheet, f"{label}_4_crops_1to1_colour_over_grazing.jpg")

    # 5. contact sheet of every raw face (colour | grazing), 120 px per face, for spotting repeats
    raw = sorted(f for f, t in types.items() if t == "raw" and f in cents)
    cell = 120
    per_row = 6
    rows = max(1, (len(raw) + per_row - 1) // per_row)
    cs = Image.new("RGB", (per_row * cell, min(800, rows * cell * 2)), (255, 255, 255))
    for k, f in enumerate(raw):
        fy, fx = cents[f]
        cc = wrap_crop(col, fy, fx, 660)
        bb = (wrap_crop(bump, fy, fx, 660) - lo_all) / full_all
        r, c = divmod(k, per_row)
        y = r * cell * 2
        if y + 2 * cell > cs.size[1]:
            break
        cs.paste(to_img(cc).resize((cell, cell), Image.LANCZOS), (c * cell, y))
        cs.paste(to_img(grazing(cc, bb, g.PPI)).resize((cell, cell), Image.LANCZOS), (c * cell, y + cell))
    save_jpg(cs, f"{label}_5_raw_faces_colour_over_grazing.jpg")
    return {"n_raw_shown": len(raw), "types": {t: sum(1 for v in types.values() if v == t) for t in ("matte", "raw", "chiseled")}}


def sources():
    r = Image.open(os.path.join(INPUTS, "elm_formed_hex_sand_layout_render.webp")).convert("RGB")
    r.resize((800, int(800 * r.size[1] / r.size[0])), Image.LANCZOS).save(out_path("SRC_1_render_full.jpg"), quality=92)
    cx, cy = r.size[0] // 2, r.size[1] // 2
    r.crop((cx - 400, cy - 400, cx + 400, cy + 400)).save(out_path("SRC_2_render_centre_native_31ppi.jpg"), quality=92)
    life = Image.open(os.path.join(INPUTS, "elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")
    life.resize((int(800 * life.size[0] / life.size[1]), 800), Image.LANCZOS).save(out_path("SRC_3_lifestyle_angled.jpg"), quality=92)
    lw, lh = life.size
    life.crop((lw // 2 - 400, lh // 4, lw // 2 + 400, lh // 4 + 800)).save(out_path("SRC_4_lifestyle_native_crop.jpg"), quality=92)


def main(seed=None):
    os.makedirs(OUT, exist_ok=True)
    items = {"high": (g.ARMS["high"], False), "xhigh": (g.ARMS["xhigh"], False), "max": (g.ARMS["max"], False),
             "baseline_2026-09-19": (g.BASELINE, True)}
    rng = random.Random(seed if seed is not None else int.from_bytes(os.urandom(8), "big"))
    labels = ["A", "B", "C", "D"]
    rng.shuffle(labels)
    key = dict(zip(labels, items.keys()))
    json.dump(key, open(os.path.join(g.HERE, "blind_key.json"), "w", encoding="utf-8"), indent=1)
    sources()
    info = {}
    for lab in sorted(key):
        tex, is_base = items[key[lab]]
        info[lab] = build_one(lab, tex, is_base)
        print(lab, "done")
    json.dump(info, open(out_path("blind_info.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
