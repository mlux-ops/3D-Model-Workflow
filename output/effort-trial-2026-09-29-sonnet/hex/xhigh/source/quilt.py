"""Efros-Freeman image quilting with min-cut seams, random dihedral block transforms and source-reuse tracking.

Library: stack of equally sized source windows (nL, S, S, C) with boolean masks (nL, S, S).
Blocks are only taken where the whole B x B window lies inside a mask.
"""
import numpy as np
from scipy import ndimage as ndi


def d4_offsets(B):
    """Index offsets (8, B, B) for the 8 dihedral transforms: t bit 2 = mirror, bits 0-1 = quarter turns."""
    a = np.arange(B)
    gy, gx = np.meshgrid(a, a, indexing="ij")
    oy = np.zeros((8, B, B), np.int64)
    ox = np.zeros((8, B, B), np.int64)
    for t in range(8):
        y, x = gy.copy(), gx.copy()
        if t & 4:
            x = B - 1 - x
        for _ in range(t & 3):
            y, x = x.copy(), B - 1 - y
        oy[t], ox[t] = y, x
    return oy, ox


def pad_windows(arrs, fill=0):
    """Pad a list of (h, w, ...) arrays to a common (H, W) with zeros/False, and stack them."""
    H = max(a.shape[0] for a in arrs)
    W = max(a.shape[1] for a in arrs)
    out = []
    for a in arrs:
        pw = [(0, H - a.shape[0]), (0, W - a.shape[1])] + [(0, 0)] * (a.ndim - 2)
        out.append(np.pad(a, pw, constant_values=fill))
    return np.stack(out)


class Library:
    def __init__(self, stack, masks, block, stride=3, allowed_t=(0, 1, 2, 3, 4, 5, 6, 7)):
        self.stack = stack.astype(np.float32)
        self.masks = masks
        self.SH, self.SW = stack.shape[1], stack.shape[2]
        self.C = stack.shape[-1]
        self.B = block
        self.allowed_t = np.array(allowed_t)
        cand = []
        for n in range(len(stack)):
            frac = ndi.uniform_filter(masks[n].astype(np.float32), block, mode="constant")
            ys, xs = np.nonzero(frac > 1.0 - 0.5 / (block * block))
            # uniform_filter is centred; convert centre index to window origin
            ys0, xs0 = ys - block // 2, xs - block // 2
            ok = (ys0 >= 0) & (xs0 >= 0) & (ys0 + block <= self.SH) & (xs0 + block <= self.SW) & (ys0 % stride == 0) & (xs0 % stride == 0)
            for y, x in zip(ys0[ok], xs0[ok]):
                cand.append((n, y, x))
        self.cand = np.array(cand, np.int64)
        self.oy, self.ox = d4_offsets(block)
        # per-channel scale so that every channel weighs equally in the overlap error
        vals = np.concatenate([stack[n][masks[n]] for n in range(len(stack))], axis=0)
        self.scale = vals.std(axis=0) + 1e-6
        self.used = np.zeros((len(stack), self.SH, self.SW), np.float32)

    def gather(self, cidx, tvec):
        n = self.cand[cidx, 0][:, None, None]
        y0 = self.cand[cidx, 1][:, None, None]
        x0 = self.cand[cidx, 2][:, None, None]
        yy = y0 + self.oy[tvec]
        xx = x0 + self.ox[tvec]
        return self.stack[n, yy, xx] / self.scale, (n[:, 0, 0], y0[:, 0, 0], x0[:, 0, 0])

    def usage(self, cidx):
        """Mean prior use of each candidate window (0 = never used)."""
        n = self.cand[cidx, 0]
        y0 = self.cand[cidx, 1]
        x0 = self.cand[cidx, 2]
        B = self.B
        # integral image of usage per library window, computed lazily on demand
        out = np.empty(len(cidx), np.float32)
        for k in range(len(cidx)):
            out[k] = self.used[n[k], y0[k]:y0[k] + B, x0[k]:x0[k] + B].mean()
        return out


def _min_cut_vertical(err):
    """err (h, w) -> boolean mask (h, w), True right of the cheapest top-to-bottom path."""
    h, w = err.shape
    cost = err.copy()
    for r in range(1, h):
        left = np.concatenate([[np.inf], cost[r - 1, :-1]])
        right = np.concatenate([cost[r - 1, 1:], [np.inf]])
        cost[r] += np.minimum(np.minimum(left, cost[r - 1]), right)
    path = np.zeros(h, np.int64)
    path[-1] = int(np.argmin(cost[-1]))
    for r in range(h - 2, -1, -1):
        c = path[r + 1]
        lo, hi = max(c - 1, 0), min(c + 2, w)
        path[r] = lo + int(np.argmin(cost[r, lo:hi]))
    cols = np.arange(w)[None, :]
    return cols >= path[:, None]


def quilt(lib, out_h, out_w, overlap, rng, n_cand=160, tol=0.12, reuse_weight=1.0, top_k=6):
    """Synthesise a canvas (out_h, out_w, C) in library units. Returns canvas and the list of placed blocks."""
    B, ov, C = lib.B, overlap, lib.C
    stride = B - ov
    nby = int(np.ceil((out_h - ov) / stride))
    nbx = int(np.ceil((out_w - ov) / stride))
    Hc, Wc = nby * stride + ov, nbx * stride + ov
    canvas = np.zeros((Hc, Wc, C), np.float32)
    placed = []
    K = len(lib.cand)
    for r in range(nby):
        for c in range(nbx):
            y0, x0 = r * stride, c * stride
            cidx = rng.integers(0, K, n_cand)
            tvec = lib.allowed_t[rng.integers(0, len(lib.allowed_t), n_cand)]
            blocks, (bn, by, bx) = lib.gather(cidx, tvec)
            err = np.zeros(n_cand, np.float64)
            npx = 0
            if c > 0:
                ref = canvas[y0:y0 + B, x0:x0 + ov] / lib.scale
                err += ((blocks[:, :, :ov] - ref[None]) ** 2).sum(axis=(1, 2, 3))
                npx += B * ov * C
            if r > 0:
                ref = canvas[y0:y0 + ov, x0:x0 + B] / lib.scale
                err += ((blocks[:, :ov, :] - ref[None]) ** 2).sum(axis=(1, 2, 3))
                npx += B * ov * C
            if r > 0 and c > 0:
                ref = canvas[y0:y0 + ov, x0:x0 + ov] / lib.scale
                err -= ((blocks[:, :ov, :ov] - ref[None]) ** 2).sum(axis=(1, 2, 3))
                npx -= ov * ov * C
            score = err / max(npx, 1)
            use = lib.usage(cidx)
            score = score + reuse_weight * use * (np.median(score) + 1e-6 if npx else 1.0)
            order = np.argsort(score)
            best = score[order[0]]
            pool = [k for k in order[:top_k] if score[k] <= best * (1 + tol) + 1e-9]
            k = int(pool[rng.integers(0, len(pool))])
            blk = blocks[k]
            keep = np.ones((B, B), bool)
            if c > 0:
                ref = canvas[y0:y0 + B, x0:x0 + ov] / lib.scale
                e = ((blk[:, :ov] - ref) ** 2).sum(axis=-1)
                keep[:, :ov] &= _min_cut_vertical(e)
            if r > 0:
                ref = canvas[y0:y0 + ov, x0:x0 + B] / lib.scale
                e = ((blk[:ov, :] - ref) ** 2).sum(axis=-1)
                keep[:ov, :] &= _min_cut_vertical(e.T).T
            region = canvas[y0:y0 + B, x0:x0 + B]
            region[keep] = blk[keep] * lib.scale
            lib.used[bn[k], by[k]:by[k] + B, bx[k]:bx[k] + B] += 1.0
            placed.append((int(bn[k]), int(by[k]), int(bx[k]), int(tvec[k])))
    return canvas, placed
