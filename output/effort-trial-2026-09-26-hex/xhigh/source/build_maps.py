"""Build Color.png, Bump16.png, face_ids.png and report.json for the ELM Formed Hexagon Sand atlas.

Run after analyze_lattice.py, classify_render.py, measure_fft.py and prepare_pools.py
(run_all.py runs the whole chain).

Method
------
* Layout: 32 Matte / 11 Raw / 13 Chiseled faces (render mix 22 : 8 : 9 of 39 fully visible
  faces), placed by simulated annealing on the torus so no two Raw or two Chiseled faces
  touch, and Chiseled orientations (5 x 90, 5 x 30, 3 x 150 deg, render 3.5 : 4 : 2) are spread.
* Organic surface (Matte cloudiness and grain, Raw relief; Chiseled roughness, see below)
  is image-quilted from render pixels of the same face type: 28 px (Raw) / 36 px (Matte) blocks,
  translation only (no rotation or mirror, so the render's baked light direction stays
  consistent), overlap-SSD matching, minimum-error boundary cuts, and a usage penalty that
  spends fresh source pixels before any are reused. Quilting runs at render scale
  (31.09 px/in) and is resampled to 64 px/in (cubic).
* Chiseled grooves are rebuilt from measured geometry: straight, 5.051 mm pitch, at 90 / 30 /
  150 deg, channel shape ((1 + cos 2 pi phi) / 2) ** 1.65 (fitted to the render's folded
  profile). Their along-ridge depth modulation, the face roughness and the mottled colour are
  quilted from the render's own Chiseled faces with the grooves notched out (prepare_chiseled.py),
  so ridges break up the way the sources show instead of being machine-perfect.
* Relief terms are separate and in millimetres: Matte micro-relief, Raw relief, Chiseled
  channel depth, tile edge ease, joint floor. No global multiplier.
"""
import os
import json
import time
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import common as C
from guard import WORK_DIR, TEX_DIR, save_image, write_text

RNG_SEED = 20260926
rng = np.random.default_rng(RNG_SEED)

# ---------------- relief terms (mm, relative to the tile face plane = 0) -------------------
JOINT_DEPTH_MM = 2.50      # joint floor below the face plane
RAW_DEPTH_MM = 1.60        # Raw relief, highest point (0) to deepest point
CHIS_DEPTH_MM = 0.70       # Chiseled channel depth below the crest plane (vertical-groove / Raw contrast
                           # ratio under a left raking light 1.5-1.66 vs 1.50 in the lifestyle image)
CHIS_MOD_GAIN = 1.0        # channel depth x (1 + gain * m): m = render groove amplitude modulation (cv 0.29)
CHIS_MOD_CLIP = 0.6
CHIS_ROUGH_MM = 0.12       # std of Chiseled face roughness (render non-groove texture, 2.7x Matte; taken at
                           # ~45 % of the luminance-equivalent because part of it is aliasing of 6.2 px grooves)
MICRO_STD_MM = 0.015       # Matte micro-relief (std) -- essentially flat
EASE_DEPTH_MM = 0.35       # tile edge ease: drop at the arris
EASE_WIDTH_MM = 1.20       # tile edge ease: width into the face

# ---------------- source data --------------------------------------------------------------
P = np.load(os.path.join(WORK_DIR, "pools.npz"))
INFO = json.load(open(os.path.join(WORK_DIR, "pools.json")))
LAT = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
RPXIN = LAT["px_per_in"]                     # render px per inch (at the assumed 10.125 in module)
S_R = RPXIN / C.PX_PER_IN                    # render px per output px
KEYS = INFO["keys"]
owner_r = P["owner"]
resid = P["resid"]
FIELD = np.dstack([resid, P["h_raw"], P["h_micro"], P["lowY"]]).astype(np.float32)   # 6 channels
YMATCH = (resid @ np.array([0.2126, 0.7152, 0.0722], np.float32)).astype(np.float32)
POOLS = {"matte": P["pool_matte"], "raw": P["pool_raw"]}
GAMMA = INFO["chiseled_fit"]["gamma"]
periods = [m["period_px"] for m in INFO["chiseled_measure"].values()]
PERIOD_MM = float(np.mean(periods)) / RPXIN * C.MM_PER_IN
PERIOD_PX = PERIOD_MM / C.MM_PER_PX
JOINT_RGB = np.array(INFO["joint_rgb"])

# ---------------- 1. layout ------------------------------------------------------------------
N = C.NR * C.NC
NB = [C.neighbours(n) for n in range(N)]
NB2 = []
for n in range(N):
    s = set()
    for m in NB[n]:
        s.update(NB[m])
    s.discard(n)
    s.difference_update(NB[n])
    NB2.append(sorted(s))
COUNTS = {"matte": 32, "raw": 11, "chiseled": 13}
ORIENT_COUNTS = {90: 5, 30: 5, 150: 3}


def layout_cost(t):
    c = 0.0
    for n in range(N):
        for m in NB[n]:
            if m < n:
                continue
            a, b = t[n], t[m]
            if a == b and a != "matte":
                c += 8.0
            elif a != "matte" and b != "matte":
                c += 1.5
        for m in NB2[n]:
            if m > n and t[n] == t[m] and t[n] != "matte":
                c += 1.0
    nm = np.array([x != "matte" for x in t]).reshape(C.NR, C.NC)
    exp_r = nm.sum() / C.NR
    exp_c = nm.sum() / C.NC
    c += 0.5 * ((nm.sum(axis=1) - exp_r) ** 2).sum() + 0.5 * ((nm.sum(axis=0) - exp_c) ** 2).sum()
    for kind in ("raw", "chiseled"):
        km = np.array([x == kind for x in t]).reshape(C.NR, C.NC)
        c += 0.5 * ((km.sum(axis=1) - km.sum() / C.NR) ** 2).sum() + 0.5 * ((km.sum(axis=0) - km.sum() / C.NC) ** 2).sum()
    return c


def anneal(items, cost, iters, t0, t1, can_swap):
    cur = list(items)
    cc = cost(cur)
    best, bc = list(cur), cc
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        a, b = rng.integers(0, len(cur), 2)
        if not can_swap(cur, a, b):
            continue
        cur[a], cur[b] = cur[b], cur[a]
        nc = cost(cur)
        if nc <= cc or rng.random() < np.exp((cc - nc) / T):
            cc = nc
            if cc < bc:
                best, bc = list(cur), cc
        else:
            cur[a], cur[b] = cur[b], cur[a]
    return best, bc


types0 = sum([[k] * v for k, v in COUNTS.items()], [])
rng.shuffle(types0)
TYPES, tcost = anneal(types0, layout_cost, 30000, 3.0, 0.02, lambda t, a, b: t[a] != t[b])
chis_idx = [n for n in range(N) if TYPES[n] == "chiseled"]
orients0 = sum([[k] * v for k, v in ORIENT_COUNTS.items()], [])
rng.shuffle(orients0)


def orient_cost(o):
    om = dict(zip(chis_idx, o))
    c = 0.0
    for n in chis_idx:
        for m in NB2[n] + NB[n]:
            if m in om and m > n and om[m] == om[n]:
                c += 1.0
    return c


ORIENTS, ocost = anneal(orients0, orient_cost, 4000, 1.0, 0.01, lambda o, a, b: o[a] != o[b])
ORIENT = dict(zip(chis_idx, ORIENTS))
adj_same = sum(1 for n in range(N) for m in NB[n] if m > n and TYPES[n] == TYPES[m] and TYPES[n] != "matte")
print("layout cost %.2f, same-type non-matte adjacencies %d, orientation cost %.1f" % (tcost, adj_same, ocost))
for i in range(C.NR):
    print("   " + " ".join("%-3s" % ("M" if TYPES[i * C.NC + j] == "matte" else
                                       "R" if TYPES[i * C.NC + j] == "raw" else "C%d" % (ORIENT[i * C.NC + j] // 30))
                           for j in range(C.NC)))


# ---------------- 2. quilting at render scale ----------------------------------------------
class Pool:
    """A quilting source: field (h, w, ch) copied into the output, ymatch (h, w) used for overlap
    matching, mask of usable pixels, keyfn(y, x) naming the render face a block came from."""

    def __init__(self, name, block, overlap, field, ymatch, mask, keyfn):
        self.name, self.B, self.O = name, block, overlap
        self.field, self.ymatch, self.mask, self.keyfn = field, ymatch, mask, keyfn
        m = mask
        sat = np.pad(m.astype(np.int32), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
        B = block
        full = sat[B:, B:] - sat[:-B, B:] - sat[B:, :-B] + sat[:-B, :-B]
        vy, vx = np.nonzero(full == B * B)
        self.vy, self.vx = vy.astype(np.int32), vx.astype(np.int32)
        self.valid = np.zeros(m.shape, bool)
        self.valid[vy, vx] = True
        self.U = np.zeros(m.shape, np.float32)          # number of distinct placements per source pixel
        self.TC = np.full(m.shape, -1, np.int64)         # first placement code that used each source pixel
        self.sigma2 = float(ymatch[m].var())
        self.copied = 0
        self.reused = 0
        self.refresh()

    def refresh(self):
        self.satU = np.pad(self.U, ((1, 0), (1, 0))).cumsum(0).cumsum(1)

    def meanU(self, sy, sx, r0=0, c0=0):
        """mean usage over block rows r0..B-1, cols c0..B-1 (the part a block adds beyond its overlaps)."""
        B = self.B
        s = self.satU
        a, b = sy + r0, sx + c0
        return (s[sy + B, sx + B] - s[a, sx + B] - s[sy + B, b] + s[a, b]) / float((B - r0) * (B - c0))


def min_cut_vertical(err):
    """err (rows, cols): min-cost top-to-bottom path; returns per-row column index."""
    r, c = err.shape
    cost = err.copy()
    back = np.zeros((r, c), np.int32)
    for i in range(1, r):
        prev = cost[i - 1]
        cand = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
        k = np.argmin(cand, axis=0)
        back[i] = k - 1
        cost[i] += cand[k, np.arange(c)]
    path = np.zeros(r, np.int32)
    path[-1] = int(np.argmin(cost[-1]))
    for i in range(r - 1, 0, -1):
        path[i - 1] = path[i] + back[i, path[i]]
    return path


def quilt(pool, Wc, Hc, face_n, K=1500, lam_u=2.0, tol=0.10, apothem=158.5):
    """Quilt a canvas covering the face hexagon (flat-top, given apothem in render px).
    Blocks that do not touch the hexagon are skipped so pool pixels are not spent on corners."""
    B, O = pool.B, pool.O
    step = B - O
    nx = int(np.ceil((Wc - O) / step))
    ny = int(np.ceil((Hc - O) / step))
    Wq, Hq = nx * step + O, ny * step + O
    canvas = np.zeros((Hq, Wq, pool.field.shape[2]), np.float32)
    cy_match = np.zeros((Hq, Wq), np.float32)
    gy, gx = np.mgrid[0:Hq, 0:Wq].astype(np.float64)
    ady, adx = np.abs(gy - (Hq - 1) / 2.0), np.abs(gx - (Wq - 1) / 2.0)
    need = (ady <= apothem) & (adx * np.sqrt(3) / 2 + ady / 2 <= apothem)
    srcpos = {}
    prov = []
    srcidx = np.full((Hq, Wq), -1, np.int64)       # final source pixel (linear render index) per canvas pixel
    WR = pool.field.shape[1]
    for by in range(ny):
        pool.refresh()
        for bx in range(nx):
            y0, x0 = by * step, bx * step
            if not need[y0:y0 + B, x0:x0 + B].any():
                continue
            has_l = (by, bx - 1) in srcpos
            has_t = (by - 1, bx) in srcpos
            # overlap pixel set (block-relative)
            ov = np.zeros((B, B), bool)
            if has_l:
                ov[:, :O] = True
            if has_t:
                ov[:O, :] = True
            r0, c0 = (O if has_t else 0), (O if has_l else 0)
            ci = rng.integers(0, len(pool.vy), K)
            sy, sx = pool.vy[ci], pool.vx[ci]
            extra = []
            if has_l:
                ly, lx = srcpos[(by, bx - 1)]
                extra.append((ly, lx + step))
            if has_t:
                ty, tx = srcpos[(by - 1, bx)]
                extra.append((ty + step, tx))
            ex = [(a, b) for a, b in extra if 0 <= a < pool.valid.shape[0] and 0 <= b < pool.valid.shape[1]
                  and pool.valid[a, b] and pool.meanU(a, b, r0, c0) < 0.3]
            if ex:
                sy = np.r_[sy, [a for a, b in ex]].astype(np.int32)
                sx = np.r_[sx, [b for a, b in ex]].astype(np.int32)
            mu = pool.meanU(sy, sx, r0, c0)
            if ov.any():
                rr, cc = np.nonzero(ov)
                cand = pool.ymatch[sy[:, None] + rr[None, :], sx[:, None] + cc[None, :]]
                tgt = cy_match[y0 + rr, x0 + cc]
                ssd = ((cand - tgt[None, :]) ** 2).mean(axis=1) / pool.sigma2
            else:
                ssd = np.zeros(len(sy))
            cost = ssd + lam_u * mu
            cmin = cost.min()
            ok = np.nonzero(cost <= cmin + tol * max(cmin, 0.05))[0]
            pick = ok[rng.integers(0, len(ok))]
            py, px = int(sy[pick]), int(sx[pick])
            blk = pool.field[py:py + B, px:px + B]
            yblk = pool.ymatch[py:py + B, px:px + B]
            # minimum-error boundary cut
            newm = np.ones((B, B), bool)
            if has_l:
                e = ((canvas[y0:y0 + B, x0:x0 + O, :3] - blk[:, :O, :3]) ** 2).sum(axis=2)
                path = min_cut_vertical(e)
                for i in range(B):
                    newm[i, :path[i]] = False
            if has_t:
                e = ((canvas[y0:y0 + O, x0:x0 + B, :3] - blk[:O, :, :3]) ** 2).sum(axis=2)
                path = min_cut_vertical(e.T)
                for j in range(B):
                    newm[:path[j], j] = False
            if has_l or has_t:
                wgt = ndi.gaussian_filter(newm.astype(np.float32), 0.8)
                wgt = np.where(newm, np.maximum(wgt, 0.5), np.minimum(wgt, 0.5))
                wgt[~ov] = 1.0                   # pixels outside any overlap are always new
            else:
                wgt = np.ones((B, B), np.float32)
            canvas[y0:y0 + B, x0:x0 + B] = wgt[..., None] * blk + (1 - wgt[..., None]) * canvas[y0:y0 + B, x0:x0 + B]
            cy_match[y0:y0 + B, x0:x0 + B] = wgt * yblk + (1 - wgt) * cy_match[y0:y0 + B, x0:x0 + B]
            took = (wgt > 0.5) & need[y0:y0 + B, x0:x0 + B]
            # usage accounting: a source pixel counts as re-used only when a different placement
            # (face, translation) copies it; continuation blocks share their neighbour's placement
            code = (int(face_n) * 8192 + (y0 - py + 4096)) * 8192 + (x0 - px + 4096)
            u = pool.U[py:py + B, px:px + B]
            tc = pool.TC[py:py + B, px:px + B]
            newuse = took & (tc != code)
            pool.copied += int(took.sum())
            pool.reused += int((newuse & (u > 0)).sum())
            u[newuse] += 1.0
            tc[took & (tc == -1)] = code
            lin = (py + np.arange(B))[:, None] * WR + (px + np.arange(B))[None, :]
            sub = srcidx[y0:y0 + B, x0:x0 + B]
            sub[took] = lin[took]
            srcpos[(by, bx)] = (py, px)
            prov.append(pool.keyfn(py + B // 2, px + B // 2))
    srcidx[~need] = -1
    return canvas, prov, srcidx


# canvas: covers the owner region of a face (|dx| <= 374.1, |dy| <= 324 output px) + margin
HALF_W_R = 374.2 * S_R + 8
HALF_H_R = 324.0 * S_R + 8
WC, HC = int(np.ceil(2 * HALF_W_R)), int(np.ceil(2 * HALF_H_R))
render_key = lambda y, x: KEYS[int(owner_r[y, x])]
pools = {"matte": Pool("matte", 36, 9, FIELD, YMATCH, POOLS["matte"], render_key),
         "raw": Pool("raw", 28, 7, FIELD, YMATCH, POOLS["raw"], render_key)}
# Chiseled: per orientation class, render Chiseled faces with grooves notched out, rotated so
# their grooves lie along the class direction (prepare_chiseled.py); channels R G B rough mod ymatch
CP = np.load(os.path.join(WORK_DIR, "chis_pool.npz"))
CPI = json.load(open(os.path.join(WORK_DIR, "chis_pool.json")))
for cls in ORIENT_COUNTS:
    fld = CP["field_%d" % cls]
    kid = CP["kid_%d" % cls]
    ks = CPI["classes"]["%d_keys" % cls]
    pools["chis_%d" % cls] = Pool("chis_%d" % cls, 28, 7, fld[..., :5], np.ascontiguousarray(fld[..., 5]),
                                  CP["mask_%d" % cls], (lambda kid_, ks_: lambda y, x: ks_[int(kid_[y, x])])(kid, ks))
print("canvas %d x %d render px; pool valid block positions: %s" % (
    WC, HC, {k: len(p.vy) for k, p in pools.items()}))


def pool_of(n):
    return {"raw": "raw", "matte": "matte"}.get(TYPES[n], "chis_%d" % ORIENT.get(n, 0))


order = list(rng.permutation(N))
quilts, provs, srcmaps = {}, {}, {}
t0 = time.time()
for n in order:
    cv, pv, sm = quilt(pools[pool_of(n)], WC, HC, n)
    quilts[n], provs[n], srcmaps[n] = cv, pv, sm
print("quilting %.1f s" % (time.time() - t0))
for k, p in pools.items():
    print("pool %-8s pool coverage %.1f %%" % (k, 100.0 * (p.U[p.mask] > 0).mean()))
# exact duplicate measure: share of quilted face pixels whose source pixel also appears at another
# output location (any face); this is the figure reported
DUP = {}
FACE_DUP = {}
for k in pools:
    ns = [n for n in range(N) if pool_of(n) == k]
    vals = np.concatenate([srcmaps[n][srcmaps[n] >= 0] for n in ns])
    mult = np.bincount(vals)
    DUP[k] = float((mult[vals] >= 2).mean())
    for n in ns:
        v = srcmaps[n][srcmaps[n] >= 0]
        FACE_DUP[n] = float((mult[v] >= 2).mean())
    print("pool %-5s: %.1f %% of quilted pixels duplicate a source pixel used elsewhere (exact count)" % (k, 100 * DUP[k]))

# ---------------- 3. output lattice ------------------------------------------------------------
t0 = time.time()
owner, edge_d, dxm, dym = C.lattice_maps()
print("lattice %.1f s" % (time.time() - t0))
face_ids = np.where(edge_d >= C.HALF_JOINT_PX, owner.astype(np.int32) + 1, 0).astype(np.uint16)

# ---------------- 4. per-face composition ------------------------------------------------------
color = np.zeros((C.H, C.W, 3), np.float64)
height = np.zeros((C.H, C.W), np.float64)
raw_lo, raw_hi = np.percentile(P["h_raw"][POOLS["raw"]], [0.5, 99.5])
micro_std = float(P["h_micro"][POOLS["matte"]].std())
tm = {t: np.array(v) for t, v in INFO["type_mean_rgb"].items()}
offs = {t: [np.array(v) for v in INFO["face_offsets"][t].values()] for t in ("matte", "raw", "chiseled")}
off_keys = {t: list(INFO["face_offsets"][t].keys()) for t in offs}
off_cycle = {t: list(rng.permutation(len(offs[t]))) for t in offs}
faces = []

# channel-shape mean over a period and colour modulation amplitude:
# the render's folded groove profile has rms ~= rms_render levels (all orientations alike, so it is
# treated as non-directional crest/channel shading and baked as channel darkening)
phg = (np.arange(4096) + 0.5) / 4096
cshape = ((1 + np.cos(2 * np.pi * phg)) / 2.0) ** GAMMA
cs_mean, cs_std = cshape.mean(), cshape.std()
render_rms = float(np.median([np.std(m["profile_lum"]) for m in INFO["chiseled_measure"].values()]))
CH_COLOR_AMP = render_rms / cs_std          # levels per unit channel shape
print("groove pitch %.3f mm = %.3f px; gamma %.2f; render stripe rms %.2f levels -> channel darkening %.2f levels"
      % (PERIOD_MM, PERIOD_PX, GAMMA, render_rms, CH_COLOR_AMP))


def raw_to_mm(h):
    """render raw relief (levels) -> mm, top at 0, 0.5th percentile at -RAW_DEPTH_MM, soft knees."""
    t = (h - raw_lo) / (raw_hi - raw_lo)          # 0 .. 1 for the 0.5 .. 99.5 percentile band
    # soft limit both ends so nothing exceeds [0, 1] by more than a small knee
    t = np.where(t > 1, 1 + 0.02 * np.tanh((t - 1) / 0.02), t)
    t = np.where(t < 0, 0.04 * np.tanh(t / 0.04), t)
    return -RAW_DEPTH_MM * (1.0 - t)


flat_owner = owner.ravel()
order_px = np.argsort(flat_owner, kind="stable")
bounds = np.searchsorted(flat_owner[order_px], np.arange(N + 1))
for n in range(N):
    idx = order_px[bounds[n]:bounds[n + 1]]
    yy, xx = np.unravel_index(idx, owner.shape)
    dx, dy = dxm[yy, xx].astype(np.float64), dym[yy, xx].astype(np.float64)
    cv = quilts[n]
    qy = (cv.shape[0] - 1) / 2.0 + dy * S_R
    qx = (cv.shape[1] - 1) / 2.0 + dx * S_R
    samp = np.stack([ndi.map_coordinates(cv[..., ch], [qy, qx], order=3, mode="nearest") for ch in range(cv.shape[2])], 1)
    t = TYPES[n]
    k = off_cycle[t].pop(0) if off_cycle[t] else int(rng.integers(0, len(offs[t])))
    off = offs[t][k] + rng.normal(0, 0.25, 3)
    rgb = tm[t] + off + samp[:, :3]
    rec = {"index": n + 1, "row": int(n // C.NC), "col": int(n % C.NC), "type": t,
           "centre_px": [round(float(v), 2) for v in C.face_centres()[n]],
           "tone_offset_rgb": [round(float(v), 2) for v in off], "tone_offset_from_render_face": off_keys[t][k]}
    if t == "matte":
        h = samp[:, 4] / micro_std * MICRO_STD_MM
        rec.update(rotation_deg=0, mirrored=False)
    elif t == "raw":
        h = raw_to_mm(samp[:, 3])
        rec.update(rotation_deg=0, mirrored=False)
    else:
        ang = ORIENT[n]                                   # groove direction, image coords (y down)
        nrm = np.radians(ang - 90.0)
        phase0 = rng.random()
        u = (dx * np.cos(nrm) + dy * np.sin(nrm)) / PERIOD_PX + phase0
        cs = ((1 + np.cos(2 * np.pi * u)) / 2.0) ** GAMMA
        mod = np.clip(CHIS_MOD_GAIN * samp[:, 4], -CHIS_MOD_CLIP, CHIS_MOD_CLIP)
        depth = CHIS_DEPTH_MM * (1.0 + mod)
        # chiselling removes material: roughness is capped at +1 sigma above the crest plane
        rough = np.clip(samp[:, 3] / CPI["rough_std"], -4, 1.0) * CHIS_ROUGH_MM
        h = -depth * cs + rough
        rgb = rgb - CH_COLOR_AMP * ((1.0 + mod) * cs - cs_mean)[:, None] * (rgb / 243.0)
        rot = {90: 0, 30: 60, 150: 300}[ang]
        rec.update(rotation_deg=rot, mirrored=False, groove_angle_image_deg=ang, groove_phase=round(float(phase0), 4),
                   groove_pitch_mm=round(PERIOD_MM, 4))
    color[yy, xx] = rgb
    height[yy, xx] = h
    # provenance
    pv = provs[n]
    src_counts = {}
    for key_ in pv:
        src_counts[key_] = src_counts.get(key_, 0) + 1
    tot = float(len(pv))
    srcs = ", ".join("%s %.0f%%" % (k_, 100 * v / tot) for k_, v in sorted(src_counts.items(), key=lambda a: -a[1]))
    if t in ("raw", "matte"):
        desc = ("image-quilted from render %s faces (render cell j,k: share of blocks) %s; translation only, "
                "no rotation or mirror; resampled 31.08 -> 64 px/in; %.0f %% of its pixels share a source pixel "
                "with another output location" % (t.capitalize(), srcs, 100 * FACE_DUP[n]))
    else:
        desc = ("grooves rebuilt from measured render geometry (straight, pitch %.3f mm, angle %d deg image coords, "
                "channel ((1+cos)/2)^%.2f, depth %.2f mm); surface roughness, mottled colour and along-ridge depth "
                "modulation image-quilted from the render's Chiseled faces with their grooves notched out, each source "
                "face rotated by a multiple of 60 deg to this groove direction (render cell j,k: share of blocks) %s; "
                "resampled 31.08 -> 64 px/in" % (PERIOD_MM, ORIENT[n], GAMMA, CHIS_DEPTH_MM, srcs))
    rec["source"] = desc
    faces.append(rec)

# ---------------- 5. edges, joints -------------------------------------------------------------
d_mm = (edge_d.astype(np.float64) - C.HALF_JOINT_PX) * C.MM_PER_PX        # >0 inside the tile
ease = EASE_DEPTH_MM * (1.0 - C.smoothstep(0.0, EASE_WIDTH_MM, d_mm))
tile_h = height - ease
is_joint = face_ids == 0
# joint floor; the outermost half pixel of the joint takes part of the step (anti-aliasing)
edge_px = edge_d.astype(np.float64)
aa = np.clip(edge_px - (C.HALF_JOINT_PX - 0.5), 0.0, 0.5)                 # 0 .. 0.5 on the joint side
height = np.where(is_joint, -JOINT_DEPTH_MM + aa * (tile_h + JOINT_DEPTH_MM), tile_h)
alpha = np.clip(edge_px - C.HALF_JOINT_PX + 0.5, 0.0, 1.0)                  # colour coverage, 1 px AA
color = alpha[..., None] * color + (1 - alpha[..., None]) * JOINT_RGB[None, None, :]

# ---------------- 6. export ----------------------------------------------------------------------
h_floor = -JOINT_DEPTH_MM
h_top = float(height.max())
bump = np.round((height - h_floor) / (h_top - h_floor) * 65535.0)
bump16 = np.clip(bump, 0, 65535).astype(np.uint16)
col8 = C.to_srgb8(color)
os.makedirs(TEX_DIR, exist_ok=True)
save_image(Image.fromarray(col8, "RGB"), os.path.join(TEX_DIR, "Color.png"), optimize=False)
save_image(Image.fromarray(bump16), os.path.join(TEX_DIR, "Bump16.png"))
save_image(Image.fromarray(face_ids), os.path.join(TEX_DIR, "face_ids.png"))
np.save(os.path.join(WORK_DIR, "height_mm.npy"), height.astype(np.float32))
np.save(os.path.join(WORK_DIR, "edge_d.npy"), edge_d)

# ---------------- 7. report (build-side facts; verify.py adds measured gates) -------------------
CELLSTATS = json.load(open(os.path.join(WORK_DIR, "render_cell_stats.json")))
full_c = {t: 0 for t in COUNTS}
wt_c = {t: 0.0 for t in COUNTS}
or_c = {"90": 0.0, "30": 0.0, "150": 0.0}
for s in CELLSTATS:
    ty = INFO["types"]["%d,%d" % (s["j"], s["k"])]
    wt_c[ty] += s["vis"]
    full_c[ty] += int(s["vis"] >= 0.99)
    if ty == "chiseled":
        a = min((90, 30, 150), key=lambda v: abs(((s["groove_deg_img"] - v) + 90) % 180 - 90))
        or_c[str(a)] += min(1.0, s["vis"])
nfull = float(sum(full_c.values()))
mix_render = {"fully_visible_faces": full_c,
              "fraction": {t: round(v / nfull, 4) for t, v in full_c.items()},
              "visibility_weighted_faces": {t: round(v, 2) for t, v in wt_c.items()},
              "visibility_weighted_fraction": {t: round(v / sum(wt_c.values()), 4) for t, v in wt_c.items()},
              "chiseled_orientations_deg_image": {k: round(v, 2) for k, v in or_c.items()},
              "note": "counted in the render's 45 classified cells: faces with >= 99 % of their inset interior "
                      "visible count 1; the weighted count adds partly visible faces by visible fraction"}
mix_used = {"faces": COUNTS, "fraction": {k: round(v / 56.0, 4) for k, v in COUNTS.items()},
            "chiseled_orientations_deg_image": {str(k): v for k, v in ORIENT_COUNTS.items()}}
report = {
    "product": "ELM Surfaces Formed collection, Hexagon Tile in Sand (Matte / Raw / Chiseled mix)",
    "atlas": {"columns": C.NC, "rows": C.NR, "faces": N, "px_per_in": C.PX_PER_IN,
              "width_px": C.W, "height_px": C.H, "hexagon": "flat-top, 10.000 in across flats (assumed reading of 10 x 10)",
              "joint_in": C.JOINT_IN, "joint_px": 2 * C.HALF_JOINT_PX, "module_across_flats_in": C.MODULE_F_IN,
              "revit_sample_size_in": [round(C.SAMPLE_W_IN, 3), round(C.SAMPLE_H_IN, 3)],
              "revit_sample_size_ftin": ["5'-10 5/32\"", "5'-10 7/8\""], "repeat": "on, both directions"},
    "revit": {"sample_size_in": [round(C.SAMPLE_W_IN, 3), round(C.SAMPLE_H_IN, 3)],
              "sample_size_ftin": ["5'-10 5/32\"", "5'-10 7/8\""], "repeat": "on, both directions",
              "bump_amount_suggested": 0.5,
              "bump_amount_note": "start at 0.5 (repo convention 0.3-0.5 for dimensional tiles); the joint uses the "
                                  "full 0-65535 range and Raw about 65 %, so lower towards 0.3 if joints read too "
                                  "heavy. Not validated in Revit in this trial."},
    "joint_rgb": [int(round(v)) for v in JOINT_RGB],
    "joint_rgb_source": "median of the darkest 20 % of render pixels on the joint centreline",
    "mix_ratio_render": mix_render, "mix_ratio_used": mix_used,
    "layout": {"seed": RNG_SEED, "anneal_cost": round(tcost, 3), "same_type_non_matte_adjacent_pairs": adj_same},
    "relief_terms_mm": {"joint_depth": JOINT_DEPTH_MM, "raw_relief": RAW_DEPTH_MM, "chiseled_channel_depth": CHIS_DEPTH_MM,
                        "chiseled_depth_modulation": "channel depth x (1 + m), m = render groove amplitude "
                                                     "modulation, clipped +-%.1f" % CHIS_MOD_CLIP,
                        "chiseled_roughness_std": CHIS_ROUGH_MM, "matte_micro_std": MICRO_STD_MM,
                        "edge_ease_depth": EASE_DEPTH_MM, "edge_ease_width": EASE_WIDTH_MM},
    "bump_encoding": {"black_mm": h_floor, "white_mm": round(h_top, 4), "mm_per_16bit_step": (h_top - h_floor) / 65535.0,
                      "white_is_high": True},
    "chiseled_geometry": {"pitch_mm": round(PERIOD_MM, 4), "pitch_px_64ppi": round(PERIOD_PX, 3),
                          "angles_deg_image_measured": {k: v["groove_deg_img"] for k, v in INFO["chiseled_measure"].items()},
                          "angles_used_deg_image": [90, 30, 150],
                          "channel_shape": "((1 + cos 2 pi phi) / 2) ** %.2f, crest plane at 0" % GAMMA,
                          "profile_fit": INFO["chiseled_fit"], "colour_channel_darkening_levels": round(CH_COLOR_AMP, 2),
                          "rotation_convention": "rotation_deg is the hexagon rotation of the vertical-groove face, "
                                                 "counter-clockwise as viewed: 0 -> vertical, 60 -> 30 deg image angle "
                                                 "('\\'), 300 -> 150 deg image angle ('/')"},
    "quilting": {"raw_block_px_render": 28, "matte_block_px_render": 36, "render_px_per_in": RPXIN,
                 "duplicate_percent": {k: round(100.0 * v, 2) for k, v in DUP.items()},
                 "pool_coverage_percent": {k: round(100.0 * float((p.U[p.mask] > 0).mean()), 2) for k, p in pools.items()},
                 "note": "duplicate_percent = share of quilted face pixels whose render source pixel also appears "
                         "at another output location (same or other face), counting both copies; the pools are "
                         "smaller than the atlas needs (Raw: ~8.7 render faces of pixels for 11 atlas faces, Matte "
                         "~25 for 32, Chiseled 9 for 13). The three Chiseled class pools are the same 9 render faces "
                         "rotated, so they also share content across classes, under the rebuilt grooves."},
    "faces": faces,
}
write_text(os.path.join(TEX_DIR, "report.json"), json.dumps(report, indent=1))
print("wrote Color.png, Bump16.png, face_ids.png, report.json; bump white = %.4f mm, black = %.2f mm" % (h_top, h_floor))
