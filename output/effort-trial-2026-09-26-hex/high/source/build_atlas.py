"""Step 4: build the seamless 8 x 7 hexagon atlas (Color.png, Bump16.png, face_ids.png,
report.json) from the render source layers.

Geometry: flat-top hexagons on a torus (common.atlas_centres); every pixel belongs to the
nearest centre, so the maps wrap by construction. Face = hexnorm < 320 px (10 in across
the flats at 64 px/in); joint = 320..328 px band (1/8 in), 4 px of it on each image edge.

Face types: the render mix (22 matte / 8 raw / 9 chiseled of 39 complete faces) scaled to
56 -> 32 / 11 / 13. Positions are chosen by annealing a cost that penalises same-type
neighbours (raw, chiseled) and same-orientation chiseled neighbours and unbalanced rows /
columns on the torus.

Sources:
  * "pure" faces: one complete render face, resampled 31.1 -> 64 px/in (bicubic) under one
    of the 12 hexagon symmetries (60 deg rotations x mirror). The outer 2 px ring that
    touches the render's drawn joint line is replaced by reflection across the safe
    boundary.
  * Raw and Matte need more faces (11 / 32) than the render holds complete (8 / 22).
    The extra faces are mosaics: 5 organically bounded cells, each filled with source
    pixels from a Raw/Matte render face at an arbitrary rotation, mirror and offset. A
    usage map keeps every source pixel to at most two appearances in the atlas; a cell
    never uses a render face already used by the same face or any of its six neighbours;
    reused pixels are steered to bland areas (low low-frequency contrast) so distinctive
    clouds are not repeated; and every reuse of a render face sits at least 12 deg away
    from any hexagon symmetry (60 deg rotations x mirror) of its earlier appearances, so
    no window is a rotated/mirrored copy of another. Cells are blended: low-frequency tone cross-faded over a wide (40 px)
    window, detail over a narrow one with variance-preserving weights so seams don't flatten.
  * Chiseled (13 from 9): the groove geometry was measured (one groove design at
    90 / 150 / 30 deg = the three hexagon rotations). Each face re-evaluates the measured
    groove profile at 64 px/in on the source's own demodulated phase/amplitude field plus the
    source residual. The 4 extra faces reuse sources at a different hexagon rotation
    (so a different groove orientation) and mirror.

Depth model (separate terms, mm, face plane = 0, white = high):
  Matte grain std 0.010 mm; Raw relief 1.00 mm (p0.5..p99.5, peaks at the face plane);
  Chiseled groove depth 0.60 mm (p0.5..p99.5); joint floor -1.60 mm; eased edge over the
  last 3 px of the face. Bump16 encodes [-1.60, +0.05] mm linearly to [0, 65535].
"""

import json
import math

import numpy as np
from PIL import Image
from scipy import ndimage

import render_geom as g
import source_layers as sl
from common import (COLS, FACE_APOTHEM, H, JOINT_HALF, PPI, ROWS, SAMPLE_H_IN, SAMPLE_W_IN, W,
                    atlas_centres, hexnorm, out_path, save_png)

RNG = np.random.default_rng(20260926)
COUNTS = {"matte": 32, "raw": 11, "chiseled": 13}
CHIS_ORIENT_COUNTS = {90: 4, 150: 6, 30: 3}      # render: 3 / 4 / 2 of 9 complete faces
MATTE_GRAIN_STD_MM = 0.010
RAW_RELIEF_MM = 1.00
CHIS_RELIEF_MM = 0.60
JOINT_FLOOR_MM = -1.60
H_MIN_MM, H_MAX_MM = JOINT_FLOOR_MM, 0.05
EDGE_EASE_PX = (317.0, 321.0)
SCALE = g.RPPI / PPI                         # render px per atlas px
SAFE_T = sl.SAFE_N / SCALE                   # safe apothem in atlas px (~317.8)
MOSAIC_CELLS = {"raw": 5, "matte": 5}

# ---------------------------------------------------------------- source layers
S = sl.build()
Hs, Ws = S["size"][1], S["size"][0]
pool = S["pool"]
by_entry = {p["entry"]: p for p in pool}
full = {t: [p for p in pool if p["full"] and p["type"] == t] for t in COUNTS}
partial = {t: [p for p in pool if (not p["full"]) and p["type"] == t] for t in COUNTS}
rgb_src = S["colour"]
hgt_src = S["height"]
zre, zim = np.real(S["z"]), np.imag(S["z"])
idmap, safe = S["idmap"], S["safe"]

# joint colour: darkest core pixels of the render's drawn joint line
jband = np.abs(S["dist"] - g.F / 2.0) < 0.75
jl = S["rgb"][jband].mean(axis=1)
JOINT_RGB = S["rgb"][jband][jl <= np.percentile(jl, 20)].mean(axis=0)
FACE_RGB = S["rgb"][S["safe"]].mean(axis=0)

# global height normalisation per type (over complete source faces)
def type_values(t):
    m = np.zeros((Hs, Ws), bool)
    for p in full[t]:
        m |= (idmap == p["entry"]) & safe & (S["dist"] < sl.SAFE_N - 6)
    return m

raw_m = type_values("raw")
raw_lo, raw_hi = np.percentile(hgt_src[raw_m], [0.5, 99.5])
mat_m = type_values("matte")
mat_med, mat_std = np.median(hgt_src[mat_m]), hgt_src[mat_m].std()


def chis_value(entry, sx, sy):
    """Measured groove model + residual at render coords (sx, sy)."""
    c = S["chis"][entry]
    zr = ndimage.map_coordinates(zre, [sy, sx], order=1, mode="nearest")
    zi = ndimage.map_coordinates(zim, [sy, sx], order=1, mode="nearest")
    ph = 2 * np.pi * (c["f"][0] * sx + c["f"][1] * sy) + np.arctan2(zi, zr)
    prof = np.asarray(c["profile"])
    nb = len(prof)
    v = np.hypot(zr, zi) * np.interp(np.mod(ph, 2 * np.pi), (np.arange(nb) + 0.5) / nb * 2 * np.pi, prof, period=2 * np.pi)
    return v + ndimage.map_coordinates(hgt_src, [sy, sx], order=3, mode="nearest")


# chiseled normalisation from the model values over complete faces
_cv = []
for p in full["chiseled"]:
    ys, xs = np.nonzero((idmap == p["entry"]) & safe & (S["dist"] < sl.SAFE_N - 6))
    sel = RNG.choice(len(xs), 20000, replace=False)
    _cv.append(chis_value(p["entry"], xs[sel].astype(float), ys[sel].astype(float)))
_cv = np.concatenate(_cv)
chis_lo, chis_hi = np.percentile(_cv, [0.5, 99.5])


def to_mm(t, v):
    if t == "raw":
        mm = (v - raw_hi) * RAW_RELIEF_MM / (raw_hi - raw_lo)
        floor = -1.15 * RAW_RELIEF_MM          # soft floor keeps outliers above the joint
        return np.where(mm < -RAW_RELIEF_MM, -RAW_RELIEF_MM + (floor + RAW_RELIEF_MM) * np.tanh((mm + RAW_RELIEF_MM) / (floor + RAW_RELIEF_MM)), np.minimum(mm, 0.02))
    if t == "chiseled":
        mm = (v - chis_hi) * CHIS_RELIEF_MM / (chis_hi - chis_lo)
        floor = -1.15 * CHIS_RELIEF_MM
        return np.where(mm < -CHIS_RELIEF_MM, -CHIS_RELIEF_MM + (floor + CHIS_RELIEF_MM) * np.tanh((mm + CHIS_RELIEF_MM) / (floor + CHIS_RELIEF_MM)), np.minimum(mm, 0.02))
    mm = (v - mat_med) * MATTE_GRAIN_STD_MM / mat_std
    return np.clip(mm, -0.035, 0.035)


# ---------------------------------------------------------------- transforms
def src_coords(entry, u, v, rot_deg, mirror, t=(0.0, 0.0)):
    """Atlas-local offsets (u right, v down, atlas px) -> render coords.
    target = Rot(rot_deg, CCW as seen) o Mirror(x) applied to the source."""
    p = by_entry[entry]
    th = math.radians(rot_deg)
    c, s = math.cos(th), math.sin(th)
    x = (c * u - s * v) * SCALE
    y = (s * u + c * v) * SCALE
    if mirror:
        x = -x
    return p["cx"] + t[0] + x, p["cy"] + t[1] + y


EDGE_N = [(0.0, 1.0), (0.0, -1.0), (math.sqrt(3) / 2, 0.5), (-math.sqrt(3) / 2, 0.5),
          (math.sqrt(3) / 2, -0.5), (-math.sqrt(3) / 2, -0.5)]


def reflect_inside(u, v, lim):
    """Reflect points whose hexnorm exceeds lim back across the nearest edge line."""
    proj = np.stack([u * a + v * b for a, b in EDGE_N], 0)
    k = np.argmax(proj, 0)
    n = proj.max(0)
    over = np.maximum(n - lim, 0.0)
    ea = np.array([a for a, _ in EDGE_N])[k]
    eb = np.array([b for _, b in EDGE_N])[k]
    return u - 2 * over * ea, v - 2 * over * eb


def orient_after(src_deg, rot, mirror):
    o = (180.0 - src_deg) if mirror else src_deg
    return (o + rot) % 180.0


# ---------------------------------------------------------------- layout (types)
centres = atlas_centres()
NF = len(centres)
cr = {idx: (c, r) for idx, c, r, _, _ in centres}
idx_of = {(c, r): idx for idx, c, r, _, _ in centres}


def neighbours(idx):
    c, r = cr[idx]
    out = [(c, r - 1), (c, r + 1)]
    rows = (r - 1, r) if c % 2 == 0 else (r, r + 1)
    for dc in (-1, 1):
        for rr in rows:
            out.append((c + dc, rr))
    return [idx_of[(cc % COLS, rr % ROWS)] for cc, rr in out]


NB = {i: neighbours(i) for i in idx_of.values()}
types = ["matte"] * COUNTS["matte"] + ["raw"] * COUNTS["raw"] + ["chiseled"] * COUNTS["chiseled"]
orients = [None] * (COUNTS["matte"] + COUNTS["raw"]) + sum([[o] * n for o, n in CHIS_ORIENT_COUNTS.items()], [])
lab = list(zip(types, orients))
RNG.shuffle(lab)


def cost(lab):
    cst = 0.0
    for i in range(1, NF + 1):
        ti, oi = lab[i - 1]
        for j in NB[i]:
            if j <= i:
                continue
            tj, oj = lab[j - 1]
            if ti == tj == "raw":
                cst += 3
            if ti == tj == "chiseled":
                cst += 2 + (3 if oi == oj else 0)
    for t in ("raw", "chiseled"):
        for c in range(COLS):
            n = sum(1 for r in range(ROWS) if lab[idx_of[(c, r)] - 1][0] == t)
            cst += 0.5 * (n - COUNTS[t] / COLS) ** 2
        for r in range(ROWS):
            n = sum(1 for c in range(COLS) if lab[idx_of[(c, r)] - 1][0] == t)
            cst += 0.5 * (n - COUNTS[t] / ROWS) ** 2
    return cst


cur = cost(lab)
T = 2.0
for it in range(30000):
    a, b = RNG.integers(0, NF, 2)
    if lab[a] == lab[b]:
        continue
    lab[a], lab[b] = lab[b], lab[a]
    nc = cost(lab)
    if nc <= cur or RNG.random() < math.exp((cur - nc) / T):
        cur = nc
    else:
        lab[a], lab[b] = lab[b], lab[a]
    T = max(0.02, T * 0.9997)
layout_cost = cur

# ---------------------------------------------------------------- source assignment
plan = {}
TRANSFORMS = [(r, m) for r in range(0, 360, 60) for m in (False, True)]
for t in ("raw", "matte"):
    slots = [i for i in range(1, NF + 1) if lab[i - 1][0] == t]
    RNG.shuffle(slots)
    srcs = list(full[t])
    RNG.shuffle(srcs)
    for k, i in enumerate(slots):
        if k < len(srcs):
            rot, mir = TRANSFORMS[RNG.integers(0, 12)]
            plan[i] = {"kind": "pure", "entry": srcs[k]["entry"], "rot": rot, "mirror": mir}
        else:
            plan[i] = {"kind": "mosaic"}
# chiseled: sources cycled; each target orientation reached by a hexagon rotation
cslots = [i for i in range(1, NF + 1) if lab[i - 1][0] == "chiseled"]
RNG.shuffle(cslots)
csrc = list(full["chiseled"])
RNG.shuffle(csrc)
used_combo = {}
for k, i in enumerate(cslots):
    p = csrc[k % len(csrc)]
    want = lab[i - 1][1]
    opts = []
    for rot, mir in TRANSFORMS:
        if abs(((orient_after(p["groove_deg"], rot, mir) - want + 90) % 180) - 90) < 5:
            prev = used_combo.get(p["entry"])
            if prev is None or (prev[2] != want):
                opts.append((rot, mir))
    if not opts:  # fall back to any matching orientation
        opts = [(rot, mir) for rot, mir in TRANSFORMS
                if abs(((orient_after(p["groove_deg"], rot, mir) - want + 90) % 180) - 90) < 5]
    rot, mir = opts[RNG.integers(0, len(opts))]
    used_combo[p["entry"]] = (rot, mir, want)
    plan[i] = {"kind": "pure", "entry": p["entry"], "rot": rot, "mirror": mir,
               "reuse": k >= len(csrc)}

# pixel lists of each Raw/Matte entry's safe area (mosaic offsets are drawn from them)
ENTRY_PIX = {p["entry"]: np.nonzero((idmap == p["entry"]) & safe) for t in ("raw", "matte") for p in partial[t] + full[t]}

# usage map (render px) for mosaic sourcing
usage = np.zeros((Hs, Ws), np.float32)
entry_uses = {}
entry_xf = {}      # every (rotation, mirror) at which a render face already appears


def far_from_symmetry(e, rot, mir, lo=12.0):
    """True when this appearance of source e is not (up to translation) one of the 12
    hexagon symmetries of any earlier appearance: same mirror -> rotation difference,
    opposite mirror -> rotation sum, must sit >= lo deg from every multiple of 60."""
    for r0, m0 in entry_xf.get(e, []):
        rel = (rot - r0) if mir == m0 else (rot + r0)
        d = rel % 60.0
        if d < lo or d > 60.0 - lo:
            return False
    return True
for i, pl in plan.items():
    if pl["kind"] == "pure":
        usage[(idmap == pl["entry"]) & safe] += 1.0
        entry_uses.setdefault(pl["entry"], set()).add(i)
        entry_xf.setdefault(pl["entry"], []).append((float(pl["rot"]), bool(pl["mirror"])))
# distinctive low-frequency features (clouds, blotches): reusing them is what makes a
# repeat recognisable, so reused source pixels are scored by this contrast map
_Ls = S["rgb"] @ np.array([0.2126, 0.7152, 0.0722])
LFC = np.abs(ndimage.gaussian_filter(_Ls, 6.0) - ndimage.gaussian_filter(_Ls, 40.0))
LFC = (LFC / np.median(LFC[safe])).astype(np.float32)

# ---------------------------------------------------------------- atlas rasterisation
atlas_id = np.zeros((H, W), np.uint16)
atlas_norm = np.full((H, W), 1e9, np.float32)
colour = np.zeros((H, W, 3), np.float32)
height = np.zeros((H, W), np.float32)
face_type_img = np.zeros((H, W), np.uint8)

BX, BY = 380, 335
cent = {idx: (cx, cy) for idx, _, _, cx, cy in centres}
report_faces = []


def face_region(idx):
    cx, cy = cent[idx]
    xs = np.arange(int(math.floor(cx - BX)), int(math.ceil(cx + BX)))
    ys = np.arange(int(math.floor(cy - BY)), int(math.ceil(cy + BY)))
    U, V = np.meshgrid(xs + 0.5 - cx, ys + 0.5 - cy)
    return xs % W, ys % H, U, V


# pass 1: nearest-centre ownership
for idx in cent:
    xw, yw, U, V = face_region(idx)
    n = hexnorm(U, V).astype(np.float32)
    sub = atlas_norm[np.ix_(yw, xw)]
    m = n < sub
    sub[m] = n[m]
    atlas_norm[np.ix_(yw, xw)] = sub
    ids = atlas_id[np.ix_(yw, xw)]
    ids[m] = idx
    atlas_id[np.ix_(yw, xw)] = ids


def sample_pure(pl, t, U, V):
    u, v = reflect_inside(U, V, SAFE_T - 0.5)
    sx, sy = src_coords(pl["entry"], u, v, pl["rot"], pl["mirror"])
    col = np.stack([ndimage.map_coordinates(rgb_src[..., c], [sy, sx], order=3, mode="nearest") for c in range(3)], -1)
    if t == "chiseled":
        hv = chis_value(pl["entry"], sx, sy)
    else:
        hv = ndimage.map_coordinates(hgt_src, [sy, sx], order=3, mode="nearest")
    return col, to_mm(t, hv)


def smooth_warp(shape, sigma, amp):
    a = ndimage.gaussian_filter(RNG.standard_normal(shape), sigma)
    return a / (a.std() + 1e-12) * amp


def build_mosaic(idx, t, U, V):
    K = MOSAIC_CELLS[t]
    # seeds: spread inside the face
    seeds = []
    while len(seeds) < K:
        p = RNG.uniform(-300, 300, 2)
        if hexnorm(p[0], p[1]) < 280 and all(np.hypot(*(p - q)) > 190 for q in seeds):
            seeds.append(p)
    wu = U + smooth_warp(U.shape, 35, 28)
    wv = V + smooth_warp(U.shape, 35, 28)
    d = np.stack([np.hypot(wu - s[0], wv - s[1]) for s in seeds], 0)
    lab_ = np.argmin(d, 0)
    region = hexnorm(U, V) < 322
    sig = 6.0
    cells = []
    for k in range(K):
        ind = ((lab_ == k) & region).astype(float)
        wk = ndimage.gaussian_filter(ind, sig)
        dt = ndimage.distance_transform_edt(ind == 0)
        fp = (dt < 3 * sig) & region            # sampled support (feather tails)
        core = (dt < sig) & region              # where the cell is visibly present
        cells.append((ind, wk, fp, core))
    cand_entries = partial[t] + full[t]
    cell_info = []
    samples = []
    for k, (ind, wk, fp, core) in enumerate(cells):
        fy, fx = np.nonzero(fp)
        sub = RNG.choice(len(fx), min(len(fx), 5000), replace=False)
        uu, vv = U[fy[sub], fx[sub]], V[fy[sub], fx[sub]]
        incore = core[fy[sub], fx[sub]]
        cu, cv = U[fy, fx].mean(), V[fy, fx].mean()
        best = None
        banned = {e for e, users in entry_uses.items() if idx in users or users & set(NB[idx])}
        allowed = [p for p in cand_entries if p["entry"] not in banned] or cand_entries
        for trial in range(4000):
            if best is not None and trial >= 700 and best[0] < 1.5:
                break
            p = allowed[RNG.integers(0, len(allowed))]
            rot = float(RNG.uniform(0, 360))
            mir = bool(RNG.integers(0, 2))
            if not far_from_symmetry(p["entry"], rot, mir):
                continue
            ys_, xs_ = ENTRY_PIX[p["entry"]]
            j = RNG.integers(0, len(xs_))
            ccx, ccy = src_coords(p["entry"], np.array([cu]), np.array([cv]), rot, mir)
            tt = (xs_[j] - ccx[0], ys_[j] - ccy[0])
            sx, sy = src_coords(p["entry"], uu, vv, rot, mir, tt)
            ix, iy = np.round(sx).astype(int), np.round(sy).astype(int)
            if ix.min() < 1 or iy.min() < 1 or ix.max() >= Ws - 2 or iy.max() >= Hs - 2:
                continue
            if not np.all((idmap[iy, ix] == p["entry"]) & safe[iy, ix]):
                continue
            us = usage[iy[incore], ix[incore]]
            # hard: a source pixel appears at most twice in the atlas (once pure, once here)
            over = float((us >= 2).mean())
            # prefer unused pixels, and bland areas where reuse is unavoidable
            sc = us.mean() + 0.6 * float((LFC[iy[incore], ix[incore]] * (us > 0)).mean()) + 10.0 * over + RNG.uniform(0, 0.02)
            if best is None or sc < best[0]:
                best = (sc, p["entry"], rot, mir, tt)
        if best is None:
            raise RuntimeError("no valid mosaic source for face %d cell %d" % (idx, k))
        _, e, rot, mir, tt = best
        sx, sy = src_coords(e, U[fp], V[fp], rot, mir, tt)
        ix = np.clip(np.round(sx).astype(int), 0, Ws - 1)
        iy = np.clip(np.round(sy).astype(int), 0, Hs - 1)
        cm = core[fp]
        lin = np.unique(iy[cm] * Ws + ix[cm])
        usage.ravel()[lin] += 1.0
        entry_uses.setdefault(e, set()).add(idx)
        entry_xf.setdefault(e, []).append((rot, mir))
        col = np.zeros(U.shape + (3,))
        hv = np.zeros(U.shape)
        for c in range(3):
            col[..., c][fp] = ndimage.map_coordinates(rgb_src[..., c], [sy, sx], order=3, mode="nearest")
        hv[fp] = ndimage.map_coordinates(hgt_src, [sy, sx], order=3, mode="nearest")
        samples.append((col, hv, fp))
        cell_info.append({"score": round(float(best[0]), 3), "render_entry": int(e), "render_centre_xy": [round(by_entry[e]["cx"], 1), round(by_entry[e]["cy"], 1)],
                          "source_full_face": bool(by_entry[e]["full"]), "rotation_deg": round(rot, 1), "mirrored": mir,
                          "offset_render_px": [round(tt[0], 1), round(tt[1], 1)], "area_frac": float(ind.sum() / region.sum())})
    # blend: low frequencies linear, detail variance-preserving
    # detail (grain, relief) switches over the narrow feather; the low-frequency tone
    # (clouds) is cross-faded over a wide one so cells never leave sharp tone steps
    wsum = sum(c[1] for c in cells) + 1e-9
    ws = [c[1] / wsum for c in cells]
    ls = 30.0
    wide = []
    for (ind, _, fp, _), (col, hv, _) in zip(cells, samples):
        reach = ndimage.gaussian_filter(fp.astype(float), ls)
        wide.append(ndimage.gaussian_filter(ind, 40.0) * (reach > 0.02))
    wwsum = sum(wide) + 1e-9
    wide = [x / wwsum for x in wide]
    low_c = np.zeros(U.shape + (3,))
    det_c = np.zeros(U.shape + (3,))
    low_h = np.zeros(U.shape)
    det_h = np.zeros(U.shape)
    w2 = np.zeros(U.shape)
    for (col, hv, fp), wk, wl in zip(samples, ws, wide):
        fpf = fp.astype(float)
        nrm = ndimage.gaussian_filter(fpf, ls) + 1e-9
        lc = np.stack([ndimage.gaussian_filter(col[..., c] * fpf, ls) / nrm for c in range(3)], -1)
        lh = ndimage.gaussian_filter(hv * fpf, ls) / nrm
        low_c += wl[..., None] * lc
        det_c += wk[..., None] * (col - lc) * fpf[..., None]
        low_h += wl * lh
        det_h += wk * (hv - lh) * fpf
        w2 += wk ** 2
    sq = np.sqrt(np.maximum(w2, 1e-6))
    col = low_c + det_c / sq[..., None]
    hv = low_h + det_h / sq
    return col, to_mm(t, hv), cell_info


for idx in sorted(cent):
    t, o = lab[idx - 1]
    pl = plan[idx]
    xw, yw, U, V = face_region(idx)
    own = atlas_id[np.ix_(yw, xw)] == idx
    if pl["kind"] == "pure":
        col, hmm = sample_pure(pl, t, U, V)
        p = by_entry[pl["entry"]]
        info = {"index": idx, "type": t, "rotation_deg": pl["rot"], "mirrored": pl["mirror"],
                "source": "render face (complete) centred at (%.1f, %.1f) px of elm_formed_hex_sand_layout_render.webp, "
                          "resampled %.2f -> 64 px/in%s" % (p["cx"], p["cy"], g.RPPI,
                                                            "; reused chiseled source at a different hexagon rotation" if pl.get("reuse") else ""),
                "source_render_centre_xy": [round(p["cx"], 1), round(p["cy"], 1)]}
        if t == "chiseled":
            info["groove_orientation_deg"] = round(orient_after(p["groove_deg"], pl["rot"], pl["mirror"]), 1)
            info["source_groove_deg"] = round(p["groove_deg"], 2)
    else:
        col, hmm, cells = build_mosaic(idx, t, U, V)
        big = max(cells, key=lambda c: c["area_frac"])
        info = {"index": idx, "type": t, "rotation_deg": big["rotation_deg"], "mirrored": big["mirrored"],
                "source": "mosaic of %d feather-blended cells of render %s pixels at arbitrary rotations "
                          "(rotation_deg/mirrored given for the largest cell; all cells listed)" % (len(cells), t),
                "cells": cells}
    n = hexnorm(U, V)
    # eased edge + joint floor
    s = np.clip((n - EDGE_EASE_PX[0]) / (EDGE_EASE_PX[1] - EDGE_EASE_PX[0]), 0, 1)
    s = s * s * (3 - 2 * s)
    hfin = hmm * (1 - s) + JOINT_FLOOR_MM * s
    a = np.clip(n - (FACE_APOTHEM - 0.5), 0, 1)[..., None]
    cfin = col * (1 - a) + JOINT_RGB[None, None, :] * a
    sub_c = colour[np.ix_(yw, xw)]
    sub_c[own] = cfin[own]
    colour[np.ix_(yw, xw)] = sub_c
    sub_h = height[np.ix_(yw, xw)]
    sub_h[own] = hfin[own]
    height[np.ix_(yw, xw)] = sub_h
    sub_t = face_type_img[np.ix_(yw, xw)]
    sub_t[own] = {"matte": 1, "raw": 2, "chiseled": 3}[t]
    face_type_img[np.ix_(yw, xw)] = sub_t
    report_faces.append(info)
    print("face", idx, t, pl["kind"], flush=True)

# ---------------------------------------------------------------- write maps
joint = atlas_norm >= FACE_APOTHEM
fid = np.where(joint, 0, atlas_id).astype(np.uint16)
col8 = np.clip(np.round(colour * 255.0), 0, 255).astype(np.uint8)
code = np.clip(np.round((height - H_MIN_MM) / (H_MAX_MM - H_MIN_MM) * 65535.0), 0, 65535).astype(np.uint16)
save_png(Image.fromarray(col8, "RGB"), "textures", "Color.png", optimize=False)
save_png(Image.fromarray(code), "textures", "Bump16.png")
save_png(Image.fromarray(fid), "textures", "face_ids.png")

# ---------------------------------------------------------------- measurements
def seam_steps(a):
    """Wrap step across each image edge vs the same step at lattice-equivalent interior
    lines (x = m * W/8 cuts the lattice exactly like x = 0; y = m * H/7 like y = 0), so the
    ratio is ~1 for a seamless wrap. Mean over rows/columns and channels."""
    a = a.astype(np.float64)
    if a.ndim == 2:
        a = a[..., None]
    lr = np.abs(a[:, 0] - a[:, -1]).mean()
    tb = np.abs(a[0] - a[-1]).mean()
    lr_int = [np.abs(a[:, int(round(m * W / COLS))] - a[:, int(round(m * W / COLS)) - 1]).mean() for m in range(1, COLS)]
    tb_int = [np.abs(a[int(round(m * H / ROWS))] - a[int(round(m * H / ROWS)) - 1]).mean() for m in range(1, ROWS)]
    return {"left_right_seam_mean_abs": lr, "left_right_equivalent_interior_mean_abs": float(np.mean(lr_int)),
            "left_right_ratio": lr / np.mean(lr_int),
            "top_bottom_seam_mean_abs": tb, "top_bottom_equivalent_interior_mean_abs": float(np.mean(tb_int)),
            "top_bottom_ratio": tb / np.mean(tb_int),
            "all_interior_column_step_mean_abs": float(np.abs(np.diff(a, axis=1)).mean()),
            "all_interior_row_step_mean_abs": float(np.abs(np.diff(a, axis=0)).mean())}


hmm_dec = code.astype(np.float64) / 65535.0 * (H_MAX_MM - H_MIN_MM) + H_MIN_MM
relief = {}
interior = atlas_norm < EDGE_EASE_PX[0] - 1
for t, k in (("matte", 1), ("raw", 2), ("chiseled", 3)):
    m = interior & (face_type_img == k)
    v = hmm_dec[m]
    relief[t] = {"min_mm": float(v.min()), "max_mm": float(v.max()), "p0_5_mm": float(np.percentile(v, 0.5)),
                 "p99_5_mm": float(np.percentile(v, 99.5)), "relief_p0_5_to_p99_5_mm": float(np.percentile(v, 99.5) - np.percentile(v, 0.5)),
                 "std_mm": float(v.std())}
jcore = (atlas_norm > EDGE_EASE_PX[1] + 0.5)
joint_floor = float(np.median(hmm_dec[jcore]))
deepest = min(relief[t]["min_mm"] for t in relief)
# joint width measured on the face-id map along the vertical centre line of each even column
jw = []
for c in range(0, COLS, 2):
    x = int((c + 0.5) * W / COLS)
    colv = fid[:, x] == 0
    runs = np.diff(np.concatenate([[0], colv.astype(int), [0]]))
    st, en = np.nonzero(runs == 1)[0], np.nonzero(runs == -1)[0]
    jw += [int(e - s_) for s_, e in zip(st, en) if s_ > 0 and e < H]

counts_used = {t: sum(1 for x in lab if x[0] == t) for t in COUNTS}
counts_src = {t: len(full[t]) for t in COUNTS}
rep = {
    "product": "ELM Surfaces Formed Hexagon Tile in Sand (Matte / Raw / Chiseled mix)",
    "atlas": {"size_px": [W, H], "columns": COLS, "rows": ROWS, "faces": NF, "px_per_in": PPI,
              "revit_sample_size_in": [SAMPLE_W_IN, SAMPLE_H_IN], "repeat": "on, both directions",
              "across_flats_in": 10.0, "joint_in": 0.125, "joint_px": 8,
              "joint_rgb": [int(round(v * 255)) for v in JOINT_RGB],
              "render_face_mean_rgb": [int(round(v * 255)) for v in FACE_RGB]},
    "render_scale_px_per_in": g.RPPI,
    "mix": {"measured_in_render_complete_faces": counts_src,
            "measured_ratio": {t: counts_src[t] / sum(counts_src.values()) for t in COUNTS},
            "used": counts_used, "used_ratio": {t: counts_used[t] / NF for t in COUNTS},
            "chiseled_orientation_render": {"90": 3, "150": 4, "30": 2},
            "chiseled_orientation_used": {str(k): v for k, v in CHIS_ORIENT_COUNTS.items()},
            "layout_cost": layout_cost},
    "chiseled_geometry_measured": {str(p["entry"]): {"groove_deg": p["groove_deg"], "period_mm": p["period_mm"],
                                                      "period_in": p["period_in"]} for p in full["chiseled"]},
    "wrap_seam_steps": {"color_8bit": seam_steps(col8), "bump_16bit_codes": seam_steps(code)},
    "relief_mm": {"face_plane_mm": 0.0, "per_type_interior": relief, "joint_floor_mm": joint_floor,
                  "joint_depth_mm": -joint_floor, "deepest_pattern_point_mm": deepest,
                  "clearance_deepest_pattern_to_joint_floor_mm": deepest - joint_floor,
                  "design_terms": {"matte_grain_std_mm": MATTE_GRAIN_STD_MM, "raw_relief_mm": RAW_RELIEF_MM,
                                   "chiseled_groove_depth_mm": CHIS_RELIEF_MM, "joint_floor_mm": JOINT_FLOOR_MM,
                                   "edge_ease_px": list(EDGE_EASE_PX)},
                  "bump16_encoding": {"code_0_mm": H_MIN_MM, "code_65535_mm": H_MAX_MM,
                                      "mm_per_code": (H_MAX_MM - H_MIN_MM) / 65535.0}},
    "joint_width_px_measured": {"min": int(min(jw)), "max": int(max(jw)), "count": len(jw)},
    "suggested_revit_bump_amount": 1.0,
    "suggested_revit_bump_amount_note": "starting value, not verified in Revit (no Revit in this trial); "
                                        "the map encodes 1.65 mm full range, so raise toward 1.5 if Raw/Chiseled read shallow",
    "faces": sorted(report_faces, key=lambda f: f["index"]),
}
json.dump(rep, open(out_path("textures", "report.json"), "w"), indent=1, default=float)
print(json.dumps({k: rep[k] for k in ("mix", "wrap_seam_steps", "relief_mm", "joint_width_px_measured")}, indent=1, default=float))
