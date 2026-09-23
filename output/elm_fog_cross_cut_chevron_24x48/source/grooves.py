"""Measured chevron-groove field of ELM's Fog Cross-Cut Chevron Deco slab swatch.

Each horizontal band carries straight, parallel grooves. Their cross-profile is
measured by projecting the band's luminance onto the groove normal and
averaging along the lines (every 0.25 px bin averages ~100 px of line). The
result is a 1D function P_k(u) per band: the real groove sequence of the
product, including its uneven line weights, with the stone print averaged out.

Two uses:
  * de-groove the slab colour: subtract beta_c * P_k(u(x, y)) per channel, so
    the colour carries no baked groove shading;
  * relief: the bump extrudes the same P_k along the groove direction, so every
    groove is exactly straight and parallel by construction.
"""
import numpy as np
from scipy import ndimage as ndi

import chevron_common as cc

BIN = 0.25          # px, projection bin
HP_SIGMA = 40.0     # px along u: removes the print's slow drift from the profile
LP_SIGMA = 0.6      # px along u: removes JPEG noise, keeps the ~3.7 px detail
SPINE_MARGIN = 3    # rows either side of a spine left out of the profile fit


def band_of_rows(spines, H):
    band = np.zeros(H, dtype=int)
    for k in range(len(spines) - 1):
        band[spines[k]:spines[k + 1]] = k
    return band


class BandProfile:
    def __init__(self, k, line_deg, u0, prof, counts):
        self.k = k
        self.line_deg = line_deg
        self.a = np.radians(line_deg - 90.0)      # normal angle, px coords (y down)
        self.u0 = u0
        self.prof = prof
        self.counts = counts

    def u(self, x, y):
        return x * np.cos(self.a) + y * np.sin(self.a)

    def __call__(self, x, y):
        t = (self.u(x, y) - self.u0) / BIN
        return np.interp(t.ravel(), np.arange(self.prof.size), self.prof).reshape(np.shape(t))


def measure_profiles(L, spines):
    H, W = L.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    out = []
    for k in range(len(spines) - 1):
        y0, y1 = spines[k] + SPINE_MARGIN, spines[k + 1] - SPINE_MARGIN
        bp = BandProfile(k, cc.BAND_LINE_DEG[k], 0.0, None, None)
        u = bp.u(xx[y0:y1], yy[y0:y1]).ravel()
        # the whole band (edge rows included) must be covered when evaluated later
        uall = bp.u(xx[spines[k]:spines[k + 1]], yy[spines[k]:spines[k + 1]])
        u0 = uall.min() - 4 * BIN
        n = int(np.ceil((uall.max() - u0) / BIN)) + 8
        idx = np.clip(((u - u0) / BIN).astype(int), 0, n - 1)
        v = L[y0:y1].ravel()
        s = np.bincount(idx, v, n)
        c = np.bincount(idx, None, n)
        raw = np.where(c > 0, s / np.maximum(c, 1), np.nan)
        # fill empty/low-count ends from the band's own folded mean profile
        good = c >= 20
        pitch_bins = cc.BAND_PITCH_PX[k] / BIN
        ph = np.mod(np.arange(n), pitch_bins)
        fold_b = np.clip((ph / pitch_bins * 64).astype(int), 0, 63)
        fs = np.bincount(fold_b[good], raw[good], 64)
        fc = np.bincount(fold_b[good], None, 64)
        fold = fs / np.maximum(fc, 1)
        trend = ndi.gaussian_filter1d(np.where(good, raw, np.nanmean(raw[good])), HP_SIGMA / BIN, mode="nearest")
        fill = fold[fold_b] - fold.mean() + trend
        w = np.clip(c / 60.0, 0, 1)
        filled = np.where(good, w * raw + (1 - w) * fill, fill)
        filled = np.where(np.isnan(filled), fill, filled)
        hp = filled - ndi.gaussian_filter1d(filled, HP_SIGMA / BIN, mode="nearest")
        prof = ndi.gaussian_filter1d(hp, LP_SIGMA / BIN, mode="nearest")
        bp.u0, bp.prof, bp.counts = u0, prof, c
        out.append(bp)
    return out


def groove_field(profiles, spines, H, W):
    """P_k(u) evaluated on the slab pixel grid, band by band."""
    G = np.zeros((H, W))
    xx = np.arange(W, dtype=np.float64)[None, :]
    for bp in profiles:
        r0, r1 = spines[bp.k], spines[bp.k + 1]
        yy = np.arange(r0, r1, dtype=np.float64)[:, None]
        G[r0:r1] = bp(np.broadcast_to(xx, (r1 - r0, W)), np.broadcast_to(yy, (r1 - r0, W)))
    return G


def refine_spines(L, profiles, spines, search=8):
    """Move each interior spine to the row split that best explains the grooves."""
    H, W = L.shape
    hp = L - ndi.gaussian_filter(L, 6)
    xx = np.arange(W, dtype=np.float64)
    out = list(spines)
    for j in range(1, len(spines) - 1):
        above, below = profiles[j - 1], profiles[j]
        s0 = spines[j]
        rows = np.arange(s0 - search, s0 + search)
        sc_a, sc_b = [], []
        for r in rows:
            y = np.full(W, float(r))
            ga, gb = above(xx, y), below(xx, y)
            sc_a.append(np.dot(hp[r], ga) / (np.linalg.norm(ga) + 1e-9))
            sc_b.append(np.dot(hp[r], gb) / (np.linalg.norm(gb) + 1e-9))
        sc_a, sc_b = np.array(sc_a), np.array(sc_b)
        best, best_r = -np.inf, s0
        for i, r in enumerate(rows):
            tot = sc_a[:i].sum() + sc_b[i:].sum()
            if tot > best:
                best, best_r = tot, int(r)
        out[j] = best_r
    return out


def degroove_slab(rgb):
    """Return (de-grooved rgb, report, profiles, spines) for the slab swatch."""
    H, W = rgb.shape[:2]
    L = cc.lum(rgb)
    spines = list(cc.SPINE_ROWS)
    prof = measure_profiles(L, spines)
    spines = refine_spines(L, prof, spines)
    prof = measure_profiles(L, spines)
    G = groove_field(prof, spines, H, W)
    band = band_of_rows(spines, H)
    out = rgb.copy()
    betas = []
    for k in range(len(spines) - 1):
        r0, r1 = spines[k], spines[k + 1]
        g = G[r0:r1]
        # fit on both signals high-passed alike (20 px keeps the groove sub-harmonics);
        # a 6 px high-pass on the channel only biased beta ~10 % low
        gh = g - ndi.gaussian_filter(g, 20)
        bk = []
        for c in range(3):
            ch = rgb[r0:r1, :, c]
            chp = ch - ndi.gaussian_filter(ch, 20)
            beta = float((chp * gh).sum() / (gh * gh).sum())
            out[r0:r1, :, c] = ch - beta * g
            bk.append(beta)
        betas.append(bk)
    rep = {
        "spines_refined": spines,
        "beta_per_band_rgb": betas,
        "profile_std_per_band": [float(p.prof.std()) for p in prof],
        "removed_std_rgb": (rgb - out).reshape(-1, 3).std(0).tolist(),
        "band_of_row_check": int(band[-1]),
    }
    return out, rep, prof, spines
