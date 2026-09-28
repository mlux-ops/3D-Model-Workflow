"""Build the ElmStone Jute cross-cut 3 x 3 panel colour atlas (9228 x 4620, 64 px/in).

Every stone pixel is copied from the two supplied photos:
  * crosscut_swatch.webp  - 48 x 21 in at 41.667 px/in, Lanczos-resampled to 64 px/in
  * crosscut_floor_angled.jpg - rectified onto the floor plane (floor_geom.py,
    alpha from calibrate_floor.py) and resampled to 64 px/in in a single step

Each 48 x 24 in face is quilted from 5 x 3 blocks (10.75 x 8.75 in) chosen at
8 px/in by overlap match plus reuse, pairwise-sharing, distinctiveness,
orientation and far-row penalties, then composited at 64 px/in along
minimum-error (DP) seams with a 3 px feather. Hard rules: no source area twice
in one face, never reused in the same orientation, and never reused where a
cell flip would line it up with its earlier copy.

Floor blocks and quarter-turned swatch blocks keep their own structure above
~0.06 in; their grain band below that (which the floor photo cannot resolve,
and which carries the swatch's horizontal striation) comes from a bland swatch
window. The striation (period 5.79 px at 64 px/in) is phase-aligned along each
block row; rows take different phases so the grating shared by every cell does
not correlate whole cells.

Joints: 4 px (1/16 in) of sRGB (209,209,209), split 2 px on each atlas edge
so the wrap lands on a joint centre line.

Run:  python calibrate_floor.py   (once; writes floor_calibration.json)
      python build_atlas.py       (writes ../textures/Color.png + provenance)
"""
import json
import os
import time

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

from floor_geom import FLOOR, RUN, SWATCH, FloorGeom

SEED = 20260925
PPI = 64
SW_PPI = 2000 / 48.0                        # swatch spans the 48 in panel length
FACE_W, FACE_H = 3072, 1536                 # 48 x 24 in stone face
CELL_W, CELL_H = 3076, 1540                 # + 1/16 in joint
NCELL = 3
JOINT_HALF = 2
JOINT_RGB = (209, 209, 209)
BW, BH = 688, 560                           # block 10.75 x 8.75 in
NCOL, NROW = 5, 3
STEP_X = (FACE_W - BW) // (NCOL - 1)        # 596 -> 92 px overlap
STEP_Y = (FACE_H - BH) // (NROW - 1)        # 488 -> 72 px overlap
S = 8                                       # search at 8 px/in
FINE_SIGMA = 3.8                            # px at 64 px/in: grain band split
FEATHER = 3.0                               # px
FLAT_SIGMA_IN = 10.0                        # lighting-flattening scale
# floor plane window (inches); rows run far (Z1) to near
FX0, FX1, FZ0, FZ1 = -72.0, 54.0, -9.625, 36.5
# selection weights (costs are mean squared RGB error per 8 px/in pixel)
LAM_USE, LAM_ORIENT, LAM_MIX, LAM_FAR = 12.0, 12.0, 4.0, 5.0
ANISO_C = 0.5       # across-direction blur (source px) = ANISO_C*sqrt((alpha/(u*K))^2 - 1)
LAM_USE2 = 2.0      # convex reuse term: spreads reuse instead of piling it on bland areas
LAM_PAIR = 10.0     # convex pairwise-sharing term: spreads shared source across face pairs
FACE_PX8 = (FACE_W // S) * (FACE_H // S)
TOL_REL, TOL_ABS = 0.08, 2.0

TEX = os.path.join(RUN, "textures")
OUT_PNG = os.path.join(TEX, "Color.png")
OUT_PROV = os.path.join(TEX, "_provenance.json")

# D4 orientations as (k quarter-turns, flip-lr). Swatch: no quarter turns,
# because its striation is horizontal.
ORIENTS_ALL = [(k, f) for k in range(4) for f in (0, 1)]
ORIENTS_SW = [(0, 0), (0, 1), (2, 0), (2, 1)]


def orient(a, t):
    k, f = t
    a = np.rot90(a, k, axes=(0, 1))
    return np.flip(a, 1) if f else a


def unorient(a, t):
    k, f = t
    if f:
        a = np.flip(a, 1)
    return np.rot90(a, -k, axes=(0, 1))


def vflipped(t):
    return t[0] == 2


def block_mean(a, n):
    h, w = a.shape[0] // n * n, a.shape[1] // n * n
    a = a[:h, :w]
    sh = (h // n, n, w // n, n) + a.shape[2:]
    return a.reshape(sh).mean(axis=(1, 3))


def norm_lowpass(img, mask, sigma):
    m = mask.astype(np.float64)
    den = np.maximum(ndi.gaussian_filter(m, sigma), 1e-6)
    return np.stack([ndi.gaussian_filter(img[..., c] * m, sigma) / den
                     for c in range(img.shape[2])], -1)


def box_sum(a, h, w):
    """Sum of a over every h x w window ('valid' positions)."""
    c = np.pad(np.cumsum(np.cumsum(a, 0), 1), ((1, 0), (1, 0)))
    return c[h:, w:] - c[:-h, w:] - c[h:, :-w] + c[:-h, :-w]


def stripe_params(gray64):
    hp = gray64 - ndi.gaussian_filter(gray64, (6, 1.5))
    prof = hp.mean(1)
    y = np.arange(len(prof))
    ps = np.linspace(5.70, 5.90, 2001)
    amp = [abs((prof * np.exp(-2j * np.pi * y / p)).sum()) for p in ps]
    p = float(ps[int(np.argmax(amp))])
    phi = float(np.angle((prof * np.exp(-2j * np.pi * y / p)).sum()))
    a = float(2 * abs((prof * np.exp(-2j * np.pi * y / p)).sum()) / len(y))
    return p, phi, a


def row_phases(omega, n, seed):
    """Stripe phase for each block row of each face (n faces x NROW).

    The swatch striation is horizontal, so a phase change hidden in a
    horizontal seam barely shows, while one across a vertical seam would.
    Rows share one phase along their length; the per-row phases are chosen
    so the striation shared by every cell does not correlate whole cells,
    directly or flipped (max |correlation| of the stripe term minimised)."""
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    c = omega * (FACE_H - 1)
    edges = [0] + [r * STEP_Y + (BH - STEP_Y) // 2 for r in range(1, NROW)] + [FACE_H]
    L = np.diff(edges) / FACE_H
    i, j = np.triu_indices(n, 1)

    def corr(x):
        ph = x.reshape(n, NROW)
        return np.concatenate([(L * np.cos(ph[i] - ph[j])).sum(1),
                               (L * np.cos(ph[i] + ph[j][:, ::-1] + c)).sum(1)])
    best = None
    for _ in range(60):
        r = minimize(lambda x: np.log(np.exp(40 * np.abs(corr(x))).sum()) / 40,
                     rng.uniform(0, 2 * np.pi, n * NROW), method="L-BFGS-B")
        m = float(np.abs(corr(r.x)).max())
        if best is None or m < best[0]:
            best = (m, r.x % (2 * np.pi))
    return best[1].reshape(n, NROW), best[0]


def dp_seam(err):
    """Minimum-cost top-to-bottom path through err (rows x cols); returns col per row."""
    h, w = err.shape
    cost = err.copy()
    back = np.zeros((h, w), np.int64)
    for i in range(1, h):
        prev = cost[i - 1]
        l = np.r_[np.inf, prev[:-1]]
        r = np.r_[prev[1:], np.inf]
        stack = np.stack([l, prev, r])
        arg = np.argmin(stack, 0)
        back[i] = arg - 1
        cost[i] += stack[arg, np.arange(w)]
    path = np.zeros(h, np.int64)
    path[-1] = int(np.argmin(cost[-1]))
    for i in range(h - 1, 0, -1):
        path[i - 1] = path[i] + back[i, path[i]]
    return path


def save_png(arr, path, icc):
    for attempt in range(5):
        try:
            Image.fromarray(arr, "RGB").save(path, optimize=False, icc_profile=icc)
            return attempt
        except OSError as e:
            if getattr(e, "errno", None) != 22 or attempt == 4:
                raise
            print("  PNG save OSError errno 22, retrying", flush=True)
            time.sleep(1.0)


class Sources:
    def __init__(self):
        t0 = time.time()
        # ---------------- swatch ----------------
        sw_img = Image.open(SWATCH).convert("RGB")
        self.icc = Image.open(SWATCH).info.get("icc_profile")
        sw = np.asarray(sw_img.resize((int(round(2000 * PPI / SW_PPI)), int(round(875 * PPI / SW_PPI))),
                                      Image.LANCZOS)).astype(np.float64)
        self.mu = sw.reshape(-1, 3).mean(0)
        sw8raw = block_mean(sw, S)
        L8 = norm_lowpass(sw8raw, np.ones(sw8raw.shape[:2], bool), FLAT_SIGMA_IN * S)
        L64 = self._up(L8, sw.shape[:2])
        self.sw64 = sw - L64 + self.mu
        self.sw8 = block_mean(self.sw64, S)
        self.sw8_valid = np.ones(self.sw8.shape[:2], bool)
        gray = self.sw64.mean(2)
        self.P, self.phi0, self.stripe_amp = stripe_params(gray)
        self.omega = 2 * np.pi / self.P
        self.sw_lp = ndi.gaussian_filter(self.sw64, (FINE_SIGMA, FINE_SIGMA, 0))
        self.sw_fine = self.sw64 - self.sw_lp
        # bland grain donors: low crack-edge energy over a whole block window
        dog = ndi.gaussian_filter(gray, 1.5) - ndi.gaussian_filter(gray, 6.0)
        e = ndi.gaussian_filter(dog ** 2, 20.0)
        win = box_sum(e, BH, BW) / (BH * BW)
        self.donor_thresh = float(np.quantile(win, 0.30))
        # window-start masks per orientation, evaluated in the oriented frame
        self.donor_ok = {t: box_sum(np.ascontiguousarray(orient(e, t)), BH, BW) / (BH * BW) <= self.donor_thresh
                         for t in ORIENTS_SW}
        # ---------------- floor ----------------
        self.geo = FloorGeom()
        fl = np.asarray(Image.open(FLOOR).convert("RGB")).astype(np.float64)
        # 0.7 px prefilter: suppresses 8x8 JPEG block edges before the 3-12x
        # perspective magnification
        fl = np.stack([ndi.gaussian_filter(fl[..., c], 0.7) for c in range(3)], -1)
        # The floor photo resolves 2.3-3.1x more across the floor than into it. A row-dependent
        # horizontal blur (rows are lines of constant depth) halves that gap so rectified
        # floor content does not read as streaked in one direction.
        for yy in range(fl.shape[0]):
            ratio = self.geo.alpha / ((yy - self.geo.y_vp) * self.geo.K)
            sx = ANISO_C * np.sqrt(max(ratio * ratio - 1.0, 0.0))
            fl[yy] = ndi.gaussian_filter1d(fl[yy], sx, axis=0, mode="nearest")
        self.fl = fl
        f32, XX, ZZ, x, y = self.geo.rectify(self.fl, 32, FX0, FX1, FZ0, FZ1)
        v32 = self._valid(XX, ZZ, x, y) & np.isfinite(f32[..., 0])
        f32 = np.where(np.isfinite(f32), f32, 0.0)
        f8raw = block_mean(f32, 4)
        self.fl8_valid = block_mean(v32.astype(float), 4) > 0.999
        self.fl_L8 = norm_lowpass(f8raw, self.fl8_valid, FLAT_SIGMA_IN * S)
        # contrast match floor -> swatch in the 0.15-1.5 in band, per channel
        g = []
        er = ndi.binary_erosion(self.fl8_valid, iterations=12)
        for c in range(3):
            fb = f8raw[..., c] - self.fl_L8[..., c]
            fb = np.where(self.fl8_valid, fb, 0.0)
            db = ndi.gaussian_filter(fb, 0.15 * S) - ndi.gaussian_filter(fb, 1.5 * S)
            sb = ndi.gaussian_filter(self.sw8[..., c], 0.15 * S) - ndi.gaussian_filter(self.sw8[..., c], 1.5 * S)
            g.append(sb[12:-12, 12:-12].std() / db[er].std())
        self.gain = np.array(g)
        self.fl8 = (f8raw - self.fl_L8) * self.gain + self.mu
        self.fl8[~self.fl8_valid] = self.mu
        # far-row penalty map (depth resolution falls with Z)
        z8 = FZ1 - (np.arange(self.fl8.shape[0]) + 0.5) / S
        self.fl8_far = np.clip(z8 / FZ1, 0, 1)[:, None] * np.ones((1, self.fl8.shape[1]))
        # distinctiveness maps
        self.sw8_D = self._distinct(self.sw8, self.sw8_valid)
        self.fl8_D = self._distinct(self.fl8, self.fl8_valid)
        self.floor_res = {"top_row": self.geo.local_res(15.3), "bottom_row": self.geo.local_res(347.5)}
        print("sources ready %.1fs  gain %s  stripe P=%.4f phi0=%.3f amp=%.2f"
              % (time.time() - t0, np.round(self.gain, 3), self.P, self.phi0, self.stripe_amp), flush=True)

    def _valid(self, XX, ZZ, x, y):
        ok = self.geo.valid_mask(XX, ZZ, x, y, joint_clear=0.4)
        return ok & (y < 347.5) & (y > 15.0)

    @staticmethod
    def _up(a8, shape):
        yy = (np.arange(shape[0]) + 0.5) / S - 0.5
        xx = (np.arange(shape[1]) + 0.5) / S - 0.5
        Y, X = np.meshgrid(yy, xx, indexing="ij")
        return np.stack([ndi.map_coordinates(a8[..., c], [Y, X], order=1, mode="nearest")
                         for c in range(a8.shape[2])], -1)

    @staticmethod
    def _distinct(img8, valid):
        g = np.where(valid, img8.mean(2), np.nan)
        g = np.where(np.isfinite(g), g, np.nanmean(g))
        d = ndi.gaussian_filter(g, 0.25 * S) - ndi.gaussian_filter(g, 2.0 * S)
        e = np.sqrt(ndi.gaussian_filter(d ** 2, 1.5 * S))
        e = e / np.median(e[valid])
        return np.clip(e, 0.5, 3.0)

    def floor_block64(self, r0, c0, h8, w8, t):
        """64 px/in floor content for the original 8-px/in region [r0:r0+h8, c0:c0+w8],
        toned, fine band removed, then oriented by t."""
        m = 16
        X0 = FX0 + (c0 * S - m) / PPI
        X1 = FX0 + ((c0 + w8) * S + m) / PPI
        Z1 = FZ1 - (r0 * S - m) / PPI
        Z0 = FZ1 - ((r0 + h8) * S + m) / PPI
        f, _, _, _, _ = self.geo.rectify(self.fl, PPI, X0, X1, Z0, Z1)
        f = np.where(np.isfinite(f), f, np.nanmean(f))
        yy = (np.arange(f.shape[0]) + r0 * S - m + 0.5) / S - 0.5
        xx = (np.arange(f.shape[1]) + c0 * S - m + 0.5) / S - 0.5
        Y, X = np.meshgrid(yy, xx, indexing="ij")
        L = np.stack([ndi.map_coordinates(self.fl_L8[..., c], [Y, X], order=1, mode="nearest")
                      for c in range(3)], -1)
        tone = (f - L) * self.gain + self.mu
        lp = ndi.gaussian_filter(tone, (FINE_SIGMA, FINE_SIGMA, 0))
        lp = lp[m:m + h8 * S, m:m + w8 * S]
        return orient(lp, t)


def aligned_row(rho_nom, y_dest, phi_src, phi_face, P, omega, lo, hi):
    """Integer source row nearest rho_nom with omega*(rho - y_dest) + phi_src == phi_face (mod 2pi)."""
    target = y_dest + (phi_face - phi_src) / omega
    k = np.round((rho_nom - target) / P)
    cands = [target + (k + d) * P for d in (-2, -1, 0, 1, 2)]
    cands = [int(round(c)) for c in cands if lo <= round(c) <= hi]
    rho = min(cands, key=lambda c: abs(c - rho_nom))
    err = ((omega * (rho - y_dest) + phi_src - phi_face + np.pi) % (2 * np.pi)) - np.pi
    return rho, float(err)


def donor_fine(src, rng, y0, phi_f):
    """Grain band (below ~0.06 in) of a bland swatch window, flipped at random, stripe phase aligned."""
    dt = ORIENTS_SW[int(rng.integers(4))]
    fine_o = orient(src.sw_fine, dt)
    dr, dc = np.nonzero(src.donor_ok[dt])
    q = int(rng.integers(len(dr)))
    phi_src = src.phi0 if not vflipped(dt) else -(src.omega * (src.sw64.shape[0] - 1) + src.phi0)
    rho, perr = aligned_row(int(dr[q]), y0, phi_src, phi_f, src.P, src.omega, 0, fine_o.shape[0] - BH)
    return (fine_o[rho:rho + BH, int(dc[q]):int(dc[q]) + BW],
            {"orient_rot90": int(dt[0]), "orient_fliplr": int(dt[1]), "oriented_row": int(rho),
             "oriented_col": int(dc[q]), "stripe_phase_err_rad": round(perr, 3)})


COINCIDE_IN = 10.0      # reject a reuse that lands within this distance of a flip-mirror of an earlier use
COINCIDE_OVERLAP = 0.15
_filter_stats = {"calls": 0, "candidates_rejected": 0, "tolerance_widened": 0, "fallbacks": 0}


def coincidence_filter(pick, cands, pools, fi, d0, h8, w8):
    """Drop candidates whose source overlaps an earlier block of another face AND whose content would
    sit at the same place in that face under one of the four cell flips (a book-match or mirror repeat
    that also raises whole-cell correlation)."""
    H8, W8 = FACE_H // S, FACE_W // S
    keep = np.ones(len(pick), bool)
    arr = np.array(pick)
    for ci in np.unique(arr[:, 0]):
        name, t = cands[ci][0], cands[ci][1]
        p = pools[name]
        recs = [r for r in p["records"] if r["face"] != fi]
        if not recs:
            continue
        o = p["oriented"][t]
        A, b = o["A"], o["b"]
        sel = np.nonzero(arr[:, 0] == ci)[0]
        I0 = arr[sel, 1].astype(float)
        J0 = arr[sel, 2].astype(float)
        s1 = (A @ np.vstack([I0, J0])).T + b
        s2 = (A @ np.vstack([I0 + h8 - 1, J0 + w8 - 1])).T + b
        rmin, rmax = np.minimum(s1[:, 0], s2[:, 0]), np.maximum(s1[:, 0], s2[:, 0]) + 1
        cmin, cmax = np.minimum(s1[:, 1], s2[:, 1]), np.maximum(s1[:, 1], s2[:, 1]) + 1
        c_cand = d0[None, :] - np.column_stack([I0, J0]) - (A.T @ b)[None, :]
        for rb in recs:
            G = rb["M"] @ A
            if abs(G[0, 1]) > 0.5:          # quarter-turn relation: never a cell flip
                continue
            gy, gx = G[0, 0], G[1, 1]
            tF = np.array([H8 - 1 if gy < 0 else 0, W8 - 1 if gx < 0 else 0], float)
            T = rb["c"][None, :] - c_cand @ G.T
            dist = np.hypot(*(T - tF[None, :]).T)
            r0, c0, r1, c1 = rb["rect"]
            ov = (np.clip(np.minimum(rmax, r1) - np.maximum(rmin, r0), 0, None)
                  * np.clip(np.minimum(cmax, c1) - np.maximum(cmin, c0), 0, None)) / (h8 * w8)
            keep[sel[(ov > COINCIDE_OVERLAP) & (dist < COINCIDE_IN * S)]] = False
    _filter_stats["calls"] += 1
    _filter_stats["candidates_rejected"] += int((~keep).sum())
    return [pk for pk, k in zip(pick, keep) if k]


def main():
    t_start = time.time()
    rng = np.random.default_rng(SEED)
    src = Sources()
    phases, phase_v = row_phases(src.omega, NCELL * NCELL, SEED + 1)
    print("row stripe phases chosen, worst cell-pair stripe correlation = %.3f" % phase_v, flush=True)

    # oriented search stacks
    lp8 = lambda a: np.stack([ndi.gaussian_filter(a[..., c], 0.7) for c in range(3)], -1)
    pools = {
        "swatch": dict(img=lp8(src.sw8), valid=src.sw8_valid, D=src.sw8_D, far=np.zeros(src.sw8.shape[:2]),
                       orients=ORIENTS_ALL),
        "floor": dict(img=lp8(src.fl8), valid=src.fl8_valid, D=src.fl8_D, far=src.fl8_far,
                      orients=ORIENTS_ALL),
    }
    h8, w8 = BH // S, BW // S
    for name, p in pools.items():
        p["U"] = np.zeros(p["valid"].shape)
        p["UT"] = {t: np.zeros(p["valid"].shape) for t in p["orients"]}
        p["idx_r"], p["idx_c"] = np.meshgrid(np.arange(p["valid"].shape[0]), np.arange(p["valid"].shape[1]),
                                             indexing="ij")
        p["oriented"] = {}
        for t in p["orients"]:
            img = np.ascontiguousarray(orient(p["img"], t))
            val = np.ascontiguousarray(orient(p["valid"], t))
            ok = box_sum((~val).astype(float), h8, w8) < 0.5
            p["oriented"][t] = dict(img=img, ok=ok, D=np.ascontiguousarray(orient(p["D"], t)),
                                    far=box_sum(np.ascontiguousarray(orient(p["far"], t)), h8, w8) / (h8 * w8),
                                    r=np.ascontiguousarray(orient(p["idx_r"], t)),
                                    c=np.ascontiguousarray(orient(p["idx_c"], t)))
            ro, co = p["oriented"][t]["r"], p["oriented"][t]["c"]
            # oriented (row, col) -> original (row, col):  s = A o + b
            p["oriented"][t]["A"] = np.array([[ro[1, 0] - ro[0, 0], ro[0, 1] - ro[0, 0]],
                                              [co[1, 0] - co[0, 0], co[0, 1] - co[0, 0]]], float)
            p["oriented"][t]["b"] = np.array([ro[0, 0], co[0, 0]], float)
        p["records"] = []
        n_ok = sum(int(o["ok"].sum()) for o in p["oriented"].values())
        print("pool %s: %d valid block positions over %d orientations" % (name, n_ok, len(p["orients"])),
              flush=True)

    atlas = np.zeros((CELL_H * NCELL, CELL_W * NCELL, 3), np.uint8)
    atlas[:] = JOINT_RGB
    prov = {"seed": SEED, "blocks": [], "faces": []}
    E_stats = []
    for p in pools.values():
        p["Cov"] = []
    for fi in range(NCELL * NCELL):
        t_face = time.time()
        canvas = np.zeros((FACE_H, FACE_W, 3), np.float64)
        filled = np.zeros((FACE_H, FACE_W), bool)
        cls = {}
        shared = np.zeros(NCELL * NCELL)     # 8 px/in pixels of source shared with each earlier face
        for p in pools.values():
            p["Uface"] = np.zeros(p["valid"].shape)
        for r in range(NROW):
            for c in range(NCOL):
                y0, x0 = r * STEP_Y, c * STEP_X
                phi_f = float(phases[fi, r])
                # ---- 8 px/in template & overlap mask
                tmpl = block_mean(canvas[y0:y0 + BH, x0:x0 + BW], S)
                M = block_mean(filled[y0:y0 + BH, x0:x0 + BW].astype(float), S) > 0.999
                if M.any():
                    tmpl = norm_lowpass(tmpl, M, 0.7)
                Mf = M.astype(float)
                nM = max(Mf.sum(), 1.0)
                nbr = [cls.get((r, c - 1)), cls.get((r - 1, c))]
                cands = []
                for name, p in pools.items():
                    for t, o in p["oriented"].items():
                        img = o["img"]
                        if M.any():
                            k = (tmpl * Mf[..., None])[::-1, ::-1]
                            cross = sum(fftconvolve(img[..., ch], k[..., ch], mode="valid") for ch in range(3))
                            s2 = fftconvolve((img ** 2).sum(2), Mf[::-1, ::-1], mode="valid")
                            t2 = float(((tmpl ** 2).sum(2) * Mf).sum())
                            E = np.maximum(s2 - 2 * cross + t2, 0) / nM
                        else:
                            E = np.zeros(o["ok"].shape)
                        Uo = np.ascontiguousarray(orient(p["U"] * p["D"], t))
                        use = box_sum(Uo, h8, w8) / (h8 * w8)
                        UTo = np.ascontiguousarray(orient(p["UT"][t] * p["D"], t))
                        use_t = box_sum(UTo, h8, w8) / (h8 * w8)
                        Uf = np.ascontiguousarray(orient(p["Uface"], t))
                        face_ov = box_sum(Uf, h8, w8) / (h8 * w8)
                        U2o = np.ascontiguousarray(orient(p["U"] ** 2, t))
                        use2 = box_sum(U2o, h8, w8) / (h8 * w8)
                        pair = np.zeros_like(use)
                        for fp, cov in enumerate(p["Cov"]):
                            ov = box_sum(np.ascontiguousarray(orient(cov.astype(float), t)), h8, w8) / (h8 * w8)
                            sn = shared[fp] / (0.25 * FACE_PX8)
                            pair += ov * (0.5 + sn * sn)
                        mix = LAM_MIX * sum(1 for n in nbr if n is not None and n != name)
                        cost = (E + LAM_USE * use + LAM_USE2 * use2 + LAM_ORIENT * use_t + LAM_PAIR * pair + mix
                                + LAM_FAR * o["far"])
                        UTr = np.ascontiguousarray(orient(p["UT"][t], t))
                        same_or = box_sum(UTr, h8, w8) / (h8 * w8)
                        # no source area is reused in the same orientation, and none twice in one face
                        ok = o["ok"] & (face_ov < 0.05) & (same_or < 0.10)
                        cost = np.where(ok, cost, np.inf)
                        cands.append((name, t, cost, E))
                cmin = min(float(cc[2].min()) for cc in cands)
                for widen in (1, 2, 4, 8):
                    tol = cmin + widen * max(TOL_REL * abs(cmin), TOL_ABS)
                    pick = []
                    for ci, (name, t, cost, E) in enumerate(cands):
                        rr, cc_ = np.nonzero(cost <= tol)
                        pick += [(ci, a, b) for a, b in zip(rr, cc_)]
                    kept = coincidence_filter(pick, cands, pools, fi, np.array([y0 / S, x0 / S]), h8, w8)
                    if kept:
                        break
                    _filter_stats["tolerance_widened"] += 1
                if kept:
                    pick = kept
                else:
                    _filter_stats["fallbacks"] += 1
                ci, i0, j0 = pick[int(rng.integers(len(pick)))]
                name, t, cost, E = cands[ci]
                p = pools[name]
                o = p["oriented"][t]
                if M.any():
                    E_stats.append(float(E[i0, j0]))
                # ---- update usage (original coordinates)
                rr = o["r"][i0:i0 + h8, j0:j0 + w8]
                cc_ = o["c"][i0:i0 + h8, j0:j0 + w8]
                p["U"][rr, cc_] += 1
                p["UT"][t][rr, cc_] += 1
                p["Uface"][rr, cc_] += 1
                for fp, cov in enumerate(p["Cov"]):
                    shared[fp] += cov[rr, cc_].sum()
                r0o, c0o = int(rr.min()), int(cc_.min())
                At, bt = o["A"], o["b"]
                p["records"].append({"face": fi, "M": At.T, "c": np.array([y0 / S, x0 / S]) - np.array([i0, j0])
                                     - At.T @ bt, "rect": (r0o, c0o, int(rr.max()) + 1, int(cc_.max()) + 1)})
                # ---- 64 px/in content
                rec = {"face": fi, "row": r, "col": c, "dest_xywh": [x0, y0, BW, BH], "source": name,
                       "orient_rot90": int(t[0]), "orient_fliplr": int(t[1]),
                       "cost": float(cost[i0, j0]), "overlap_err": float(E[i0, j0])}
                if name == "swatch":
                    oimg = orient(src.sw64 if t[0] % 2 == 0 else src.sw_lp, t)
                    if t[0] % 2 == 0:
                        # unrotated or flipped: keep the swatch grain itself, stripe phase aligned
                        phi_src = src.phi0 if not vflipped(t) else -(src.omega * (src.sw64.shape[0] - 1) + src.phi0)
                        rho, perr = aligned_row(i0 * S, y0, phi_src, phi_f, src.P, src.omega, 0,
                                                oimg.shape[0] - BH)
                        rec["stripe_phase_err_rad"] = round(perr, 3)
                    else:
                        # quarter-turned: structure above the grain band only; grain from a donor,
                        # so the striation stays horizontal
                        rho = i0 * S
                    col0 = j0 * S
                    blk = oimg[rho:rho + BH, col0:col0 + BW]
                    if t[0] % 2 == 1:
                        fine, drec = donor_fine(src, rng, y0, phi_f)
                        blk = blk + fine
                        rec["grain_donor"] = drec
                    # original 64 px/in rectangle
                    rI, cI = np.meshgrid(np.arange(src.sw64.shape[0]), np.arange(src.sw64.shape[1]), indexing="ij")
                    rO, cO = orient(rI, t)[rho:rho + BH, col0:col0 + BW], orient(cI, t)[rho:rho + BH, col0:col0 + BW]
                    wO, hO = int(cO.max() - cO.min() + 1), int(rO.max() - rO.min() + 1)
                    rec.update({"src_rect_64ppi_xywh": [int(cO.min()), int(rO.min()), wO, hO],
                                "src_rect_native_px_xywh": [round(cO.min() * SW_PPI / PPI, 1),
                                                            round(rO.min() * SW_PPI / PPI, 1),
                                                            round(wO * SW_PPI / PPI, 1), round(hO * SW_PPI / PPI, 1)]})
                else:
                    blk = src.floor_block64(r0o, c0o, rr.max() - r0o + 1, cc_.max() - c0o + 1, t)
                    blk = blk[:BH, :BW]
                    fine, drec = donor_fine(src, rng, y0, phi_f)
                    blk = blk + fine
                    Xa = FX0 + c0o / S
                    Za = FZ1 - (rr.max() + 1) / S
                    rec.update({"src_plane_rect_in": {"X0": round(Xa, 3), "X1": round(FX0 + (cc_.max() + 1) / S, 3),
                                                      "Z0": round(Za, 3), "Z1": round(FZ1 - r0o / S, 3)},
                                "grain_donor": drec})
                # ---- DP seams at 64 px/in
                reg_c = canvas[y0:y0 + BH, x0:x0 + BW]
                reg_f = filled[y0:y0 + BH, x0:x0 + BW]
                mask = np.ones((BH, BW), bool)
                if reg_f.any():
                    a_lp = ndi.gaussian_filter(reg_c, (2, 2, 0))
                    b_lp = ndi.gaussian_filter(blk, (2, 2, 0))
                    err = ((a_lp - b_lp) ** 2).sum(2)
                    ox, oy = BW - STEP_X, BH - STEP_Y
                    if c > 0:
                        path = dp_seam(err[:, :ox])
                        mask &= np.arange(BW)[None, :] > path[:, None]
                    if r > 0:
                        path = dp_seam(err[:oy, :].T)
                        mask &= np.arange(BH)[:, None] > path[None, :]
                w = ndi.gaussian_filter(mask.astype(float), FEATHER, mode="nearest")
                w = np.where(reg_f, w, 1.0)[..., None]
                canvas[y0:y0 + BH, x0:x0 + BW] = reg_c * (1 - w) + blk * w
                filled[y0:y0 + BH, x0:x0 + BW] = True
                cls[(r, c)] = name
                prov["blocks"].append(rec)
        assert filled.all()
        for p in pools.values():
            p["Cov"].append(p["Uface"] > 0)
        gy, gx = divmod(fi, NCELL)
        Y0, X0 = gy * CELL_H + JOINT_HALF, gx * CELL_W + JOINT_HALF
        atlas[Y0:Y0 + FACE_H, X0:X0 + FACE_W] = np.clip(np.round(canvas), 0, 255).astype(np.uint8)
        n_sw = sum(1 for v in cls.values() if v == "swatch")
        prov["faces"].append({"face": fi, "atlas_row": gy, "atlas_col": gx, "stone_origin_px": [X0, Y0],
                              "stripe_phase_rad_by_row": phases[fi].tolist(), "swatch_blocks": n_sw, "floor_blocks": 15 - n_sw})
        print("face %d done %.1fs  swatch blocks %d  floor blocks %d" % (fi, time.time() - t_face, n_sw, 15 - n_sw),
              flush=True)

    os.makedirs(TEX, exist_ok=True)
    retries = save_png(atlas, OUT_PNG, src.icc)
    prov.update({
        "atlas_px": [atlas.shape[1], atlas.shape[0]], "ppi": PPI,
        "cell_px": [CELL_W, CELL_H], "face_px": [FACE_W, FACE_H], "joint_px": 2 * JOINT_HALF,
        "joint_rgb": JOINT_RGB, "block_px": [BW, BH], "grid": [NCOL, NROW], "overlap_px": [BW - STEP_X, BH - STEP_Y],
        "swatch": {"native_ppi": SW_PPI, "resample": "Lanczos 2000x875 -> 3072x1344 (x1.536)",
                   "tone": "lighting flatten sigma %.0f in (field range is +-0.6 levels)" % FLAT_SIGMA_IN,
                   "stripe_period_px64": src.P, "stripe_phase0_rad": src.phi0, "stripe_amp_levels": src.stripe_amp},
        "floor": {"alpha": src.geo.alpha, "K_in": src.geo.K, "vp_px": [src.geo.x_vp, src.geo.y_vp],
                  "plane_window_in": [FX0, FX1, FZ0, FZ1], "prefilter_px": 0.7, "aniso_c": ANISO_C,
                  "tone_gain_rgb": src.gain.tolist(), "target_mean_rgb": src.mu.tolist(),
                  "source_res_ppi_across_depth": {k: list(v) for k, v in src.floor_res.items()}},
        "grain_band_sigma_px64": FINE_SIGMA, "donor_window_threshold": src.donor_thresh,
        "stripe_row_phase_worst_abs_corr": phase_v,
        "weights": {"LAM_USE": LAM_USE, "LAM_USE2": LAM_USE2, "LAM_PAIR": LAM_PAIR, "LAM_ORIENT": LAM_ORIENT, "LAM_MIX": LAM_MIX, "LAM_FAR": LAM_FAR,
                    "TOL_REL": TOL_REL, "TOL_ABS": TOL_ABS},
        "overlap_err_stats": {"mean": float(np.mean(E_stats)), "median": float(np.median(E_stats)),
                              "max": float(np.max(E_stats))},
        "usage_max": {k: float(p["U"].max()) for k, p in pools.items()},
        "usage_mean_valid": {k: float(p["U"][p["valid"]].mean()) for k, p in pools.items()},
        "coincidence_filter": dict(_filter_stats, distance_in=COINCIDE_IN, min_overlap=COINCIDE_OVERLAP),
        "png_save_retries": retries, "build_seconds": time.time() - t_start,
    })
    with open(OUT_PROV, "w") as f:
        json.dump(prov, f, indent=1)
    print("wrote %s (%d x %d) in %.0fs" % (OUT_PNG, atlas.shape[1], atlas.shape[0], time.time() - t_start))


if __name__ == "__main__":
    main()
