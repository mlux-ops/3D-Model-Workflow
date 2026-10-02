"""Image quilting (patch-based texture synthesis with min-error boundary cut) from source pixels.

Channels are plain floats. `cplx` lists (re, im) channel pairs that carry a complex field whose global phase is free:
a candidate patch is rotated by the phase that best aligns it with the canvas before its cost is evaluated.
"""
import numpy as np
from scipy import ndimage


def _valid_positions(mask, p):
    m = mask.astype(np.int32)
    c = np.pad(m.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    H, W = mask.shape
    s = c[p:, p:] - c[:-p, p:] - c[p:, :-p] + c[:-p, :-p]
    ys, xs = np.nonzero(s == p * p)
    return ys, xs


def _transform(patch, t, allowed):
    """patch (N,p,p,C). t in 0..7: bit0 flipud, bit1 fliplr, bit2 transpose."""
    if t & 1 and "flipud" in allowed:
        patch = patch[:, ::-1]
    if t & 2 and "fliplr" in allowed:
        patch = patch[:, :, ::-1]
    if t & 4 and "transpose" in allowed:
        patch = patch.transpose(0, 2, 1, 3)
    return patch


def _cut_vertical(err):
    """err (h, w) -> boolean mask (h, w) True = take NEW patch, cut path chosen by DP (left-to-right seam)."""
    h, w = err.shape
    E = err.copy()
    for i in range(1, h):
        prev = E[i - 1]
        left = np.concatenate([[np.inf], prev[:-1]])
        right = np.concatenate([prev[1:], [np.inf]])
        E[i] += np.minimum(np.minimum(left, right), prev)
    path = np.zeros(h, dtype=int)
    path[-1] = int(np.argmin(E[-1]))
    for i in range(h - 2, -1, -1):
        j = path[i + 1]
        lo, hi = max(j - 1, 0), min(j + 2, w)
        path[i] = lo + int(np.argmin(E[i, lo:hi]))
    cols = np.arange(w)[None, :]
    return cols >= path[:, None]


def quilt(sources, out_hw, patch, overlap, rng, n_cand=150, weights=None, cplx=(), allowed=("flipud", "fliplr", "transpose"),
          tol=0.08, avoid_reuse=True, used=None, reuse_w=0.6):
    """sources: list of (arr (H,W,C) float32, mask (H,W) bool). Returns (out (h,w,C), provenance list).
    `used` may be a dict shared between calls so that source areas already used in earlier faces are penalised too."""
    C = sources[0][0].shape[2]
    p, ov = patch, overlap
    step = p - ov
    H, W = out_hw
    nby = int(np.ceil((H - ov) / step))
    nbx = int(np.ceil((W - ov) / step))
    HH, WW = nby * step + ov, nbx * step + ov
    out = np.zeros((HH, WW, C), np.float32)
    filled = np.zeros((HH, WW), bool)
    w = np.ones(C, np.float32) if weights is None else np.asarray(weights, np.float32)
    pos = []
    for si, (a, m) in enumerate(sources):
        ys, xs = _valid_positions(m, p)
        keep = ((ys % 3) == 0) & ((xs % 3) == 0)
        ys, xs = ys[keep], xs[keep]
        pos.append(np.stack([np.full(len(ys), si), ys, xs], 1))
    pos = np.concatenate(pos, 0)
    used = {} if used is None else used
    hb = max(1, p // 2)
    prov = []
    cpl = [(a, b) for a, b in cplx]

    def reuse_pen(m):
        by_, bx_ = m[1] // hb, m[2] // hb
        s = 0.0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                s += used.get((m[0], by_ + dy, bx_ + dx), 0) * (1.0 if (dy == 0 and dx == 0) else 0.5)
        return 1.0 + reuse_w * s
    for by in range(nby):
        for bx in range(nbx):
            y0, x0 = by * step, bx * step
            need_l = bx > 0
            need_t = by > 0
            k = min(n_cand, len(pos))
            idx = rng.choice(len(pos), size=k, replace=False)
            cand = np.empty((k, p, p, C), np.float32)
            meta = []
            for n, ii in enumerate(idx):
                si, y, x = pos[ii]
                t = int(rng.integers(0, 8))
                q = sources[si][0][y:y + p, x:x + p][None]
                q = _transform(q, t, allowed)
                cand[n] = q[0]
                meta.append((si, y, x, t))
            if not (need_l or need_t):
                choice = int(rng.integers(0, k))
                if avoid_reuse:
                    pen0 = np.array([reuse_pen(m) for m in meta], np.float32)
                    choice = int(rng.choice(np.argsort(pen0)[:max(3, k // 6)]))
                best = cand[choice]
                si_, y_, x_, _t = meta[choice]
                used[(si_, y_ // hb, x_ // hb)] = used.get((si_, y_ // hb, x_ // hb), 0) + 1
                out[y0:y0 + p, x0:x0 + p] = best
                filled[y0:y0 + p, x0:x0 + p] = True
                prov.append((by, bx) + meta[choice])
                continue
            ov_mask = np.zeros((p, p), bool)
            if need_l:
                ov_mask[:, :ov] = True
            if need_t:
                ov_mask[:ov, :] = True
            cur = out[y0:y0 + p, x0:x0 + p]
            fmask = filled[y0:y0 + p, x0:x0 + p] & ov_mask
            for (ca, cb) in cpl:
                z_out = cur[..., ca] + 1j * cur[..., cb]
                z_c = cand[..., ca] + 1j * cand[..., cb]
                s = (z_out[None] * np.conj(z_c))[:, fmask].sum(1)
                ph = np.exp(1j * np.angle(s))
                z_c = z_c * ph[:, None, None]
                cand[..., ca] = z_c.real
                cand[..., cb] = z_c.imag
            diff = (cand - cur[None]) ** 2 * w
            cost_map = diff.sum(-1)
            cost = cost_map[:, fmask].sum(1) / fmask.sum()
            if avoid_reuse:
                pen = np.array([reuse_pen(m) for m in meta], np.float32)
                cost = cost * pen
            order = np.argsort(cost)
            thr = cost[order[0]] * (1 + tol) + 1e-9
            pool = order[cost[order] <= thr]
            choice = int(rng.choice(pool[:8]))
            new = cand[choice]
            e = cost_map[choice]
            take = np.ones((p, p), bool)
            if need_l:
                seam = _cut_vertical(e[:, :ov])
                take[:, :ov] &= seam
            if need_t:
                seam = _cut_vertical(e[:ov, :].T).T
                take[:ov, :] &= seam
            alpha = ndimage.gaussian_filter(take.astype(np.float32), 0.8)
            alpha = np.where(fmask, alpha, 1.0)
            out[y0:y0 + p, x0:x0 + p] = cur * (1 - alpha[..., None]) + new * alpha[..., None]
            filled[y0:y0 + p, x0:x0 + p] = True
            si, y, x, t = meta[choice]
            key = (si, y // hb, x // hb)
            used[key] = used.get(key, 0) + 1
            prov.append((by, bx, si, y, x, t))
    return out[:H, :W], prov
