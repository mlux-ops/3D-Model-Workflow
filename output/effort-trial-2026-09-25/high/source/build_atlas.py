"""Stage 2: quilt 9 independent tile faces from real photo patches and assemble the atlas.

Every face pixel is copied from a prepared photographic source (dihedral transforms only),
joined along minimum-error boundary cuts with a narrow feather (Gaussian sigma 1.5 px).
Joints: 4 px (1/16 in at 64 px/in) of sRGB (209,209,209). The atlas edge bisects a joint
(2 px each side), so the wrap on both axes lands inside a uniform joint.
Deterministic: fixed RNG seed. Run prep_sources.py first.
"""
import json, os, time
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
from scipy.ndimage import uniform_filter, gaussian_filter, maximum_filter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(ROOT, '_work')
TEX = os.path.join(ROOT, 'textures')
os.makedirs(TEX, exist_ok=True)

FACE_W, FACE_H, JOINT = 3072, 1536, 4
CELL_W, CELL_H = FACE_W + JOINT, FACE_H + JOINT       # 3076 x 1540
ATLAS_W, ATLAS_H = 3 * CELL_W, 3 * CELL_H             # 9228 x 4620
JOINT_RGB = (209, 209, 209)
P, OV = 640, 160                 # patch and overlap, full-res px (10 in / 2.5 in)
STEP = P - OV
Q = 4                            # matching done at 1/4 scale
PQ, OVQ = P // Q, OV // Q
STRIDE_Q = 4                     # candidate stride at 1/4 scale (16 full px)
SEED = 20260925
W_USE, W_CELL, TOPK, W_RARE = 0.9, 2.5, 4, 6.0

TRANSFORMS = ['id', 'fliph', 'flipv', 'rot180', 'rot90', 'rot270', 'transpose', 'antitranspose']
_TF = {'id': lambda x: x,
       'fliph': lambda x: x[:, ::-1],
       'flipv': lambda x: x[::-1],
       'rot180': lambda x: x[::-1, ::-1],
       'rot90': lambda x: np.rot90(x, 1),
       'rot270': lambda x: np.rot90(x, 3),
       'transpose': lambda x: np.swapaxes(x, 0, 1),
       'antitranspose': lambda x: np.swapaxes(x[::-1, ::-1], 0, 1)}


def tf(a, t):
    return _TF[t](a)


def inv_rect(t, y, x, h, w, H, W):
    """Map a window (y,x,h,w) in transform t of an HxW image back to original coords."""
    idx = np.arange(H * W).reshape(H, W)
    win = tf(idx, t)[y:y + h, x:x + w]
    ys, xs = np.unravel_index(win.ravel(), (H, W))
    return int(ys.min()), int(xs.min()), int(ys.max() - ys.min() + 1), int(xs.max() - xs.min() + 1)


def min_cut_vertical(err):
    """err: (h, w). Column index of the minimum-cost top-to-bottom cut for each row."""
    h, w = err.shape
    E = err.copy()
    back = np.zeros((h, w), int)
    for i in range(1, h):
        prev = np.stack([np.r_[np.inf, E[i - 1, :-1]], E[i - 1], np.r_[E[i - 1, 1:], np.inf]])
        k = prev.argmin(0)
        back[i] = k - 1
        E[i] += prev[k, np.arange(w)]
    path = np.zeros(h, int)
    path[-1] = int(E[-1].argmin())
    for i in range(h - 1, 0, -1):
        path[i - 1] = path[i] + back[i, path[i]]
    return path


def save_png(img, path):
    # machine quirk: large PNG saves sometimes raise OSError errno 22; retry
    for attempt in range(4):
        try:
            Image.fromarray(img, 'RGB').save(path)
            return attempt
        except OSError as ex:
            print('save retry', attempt, ex, flush=True)
            if attempt == 3:
                raise


def main():
    rng = np.random.default_rng(SEED)
    src = np.load(os.path.join(WORK, 'src_swatch.npy')).astype(np.float32)
    H0, W0 = src.shape[:2]
    srcq = src.reshape(H0 // Q, Q, W0 // Q, Q, 3).mean((1, 3))
    Hq, Wq = srcq.shape[:2]
    # distinctiveness: local contrast at ~2 in scale; distinctive regions cost more to reuse
    lum = srcq.mean(2)
    loc = np.sqrt(np.maximum(uniform_filter(lum ** 2, 32) - uniform_filter(lum, 32) ** 2, 0))
    # rare features (small bright/dark flakes > 3 sigma from their surroundings) are the most
    # recognisable when repeated: weight their reuse much more heavily
    dev = np.abs(lum - uniform_filter(lum, 24))
    rare = maximum_filter((dev > 3 * dev.std()).astype(np.float64), 12)
    distinct = 0.5 + loc / loc.mean() + W_RARE * gaussian_filter(rare, 3)
    full_t = {t: np.ascontiguousarray(tf(src, t)) for t in TRANSFORMS}
    q_t = {t: np.ascontiguousarray(tf(srcq, t)) for t in TRANSFORMS}
    q2_t = {t: (q_t[t] ** 2).sum(2) for t in TRANSFORMS}
    usage = np.zeros((Hq, Wq))          # global usage count, original 1/4-scale coords
    atlas = np.empty((ATLAS_H, ATLAS_W, 3), np.uint8)
    atlas[:] = JOINT_RGB
    report_cells = []
    nx = int(np.ceil((FACE_W - OV) / STEP))
    ny = int(np.ceil((FACE_H - OV) / STEP))
    cw, ch = (nx - 1) * STEP + P, (ny - 1) * STEP + P
    t0 = time.time()
    for ci in range(3):
        for cj in range(3):
            cell_use = np.zeros((Hq, Wq))
            canvas = np.zeros((ch, cw, 3), np.float32)
            canq = np.zeros((ch // Q, cw // Q, 3), np.float32)
            patches = []
            for py in range(ny):
                for px in range(nx):
                    y0, x0 = py * STEP, px * STEP
                    yq, xq = y0 // Q, x0 // Q
                    M = np.zeros((PQ, PQ), np.float32)
                    if px > 0:
                        M[:, :OVQ] = 1
                    if py > 0:
                        M[:OVQ, :] = 1
                    T = canq[yq:yq + PQ, xq:xq + PQ]
                    pen_map = (W_USE * usage + W_CELL * cell_use) * distinct
                    best = []
                    for t in TRANSFORMS:
                        S = q_t[t]
                        if M.sum() > 0:
                            ssd = fftconvolve(q2_t[t], M[::-1, ::-1], mode='valid')
                            for c in range(3):
                                ssd -= 2 * fftconvolve(S[..., c], (M * T[..., c])[::-1, ::-1], mode='valid')
                            ssd += (M[..., None] * T ** 2).sum()
                            ssd = np.maximum(ssd, 0) / M.sum()
                        else:
                            ssd = np.zeros((S.shape[0] - PQ + 1, S.shape[1] - PQ + 1))
                        pen = uniform_filter(tf(pen_map, t), PQ, mode='constant')
                        pen = pen[PQ // 2:PQ // 2 + ssd.shape[0], PQ // 2:PQ // 2 + ssd.shape[1]]
                        cost = ssd / 4.0 + pen
                        cs = cost[::STRIDE_Q, ::STRIDE_Q]
                        for f in np.argsort(cs, axis=None)[:TOPK]:
                            a_, b_ = np.unravel_index(f, cs.shape)
                            best.append((float(cs[a_, b_]), t, int(a_ * STRIDE_Q), int(b_ * STRIDE_Q),
                                         float(ssd[a_ * STRIDE_Q, b_ * STRIDE_Q])))
                    best.sort(key=lambda r: r[0])
                    _, t, sy, sx, err_ov = best[int(rng.integers(0, TOPK))]
                    pq = q_t[t][sy:sy + PQ, sx:sx + PQ]
                    pf = full_t[t][sy * Q:sy * Q + P, sx * Q:sx * Q + P]
                    # minimum-error boundary cut through the overlap(s), at 1/4 scale
                    mask = np.ones((PQ, PQ), np.float32)
                    e = ((pq - T) ** 2).sum(2)
                    if px > 0:
                        cut = min_cut_vertical(e[:, :OVQ])
                        for r in range(PQ):
                            mask[r, :cut[r]] = 0
                    if py > 0:
                        cut = min_cut_vertical(e[:OVQ, :].T)
                        for c in range(PQ):
                            mask[:cut[c], c] = 0
                    mf = gaussian_filter(np.kron(mask, np.ones((Q, Q), np.float32)), 1.5)
                    inside = np.ones((P, P), bool)
                    if py > 0:
                        inside[:OV, :] = False
                    if px > 0:
                        inside[:, :OV] = False
                    mf[inside] = 1.0
                    reg = canvas[y0:y0 + P, x0:x0 + P]
                    canvas[y0:y0 + P, x0:x0 + P] = reg * (1 - mf[..., None]) + pf * mf[..., None]
                    canq[yq:yq + PQ, xq:xq + PQ] = canvas[y0:y0 + P, x0:x0 + P].reshape(PQ, Q, PQ, Q, 3).mean((1, 3))
                    oy, ox, oh, ow = inv_rect(t, sy, sx, PQ, PQ, Hq, Wq)
                    usage[oy:oy + oh, ox:ox + ow] += 1
                    cell_use[oy:oy + oh, ox:ox + ow] += 1
                    patches.append({'dest_face_xy': [x0, y0], 'transform': t,
                                    'src_rect_swatch64_xywh': [ox * Q, oy * Q, ow * Q, oh * Q],
                                    'overlap_rms': round(float(np.sqrt(err_ov / 3)), 2)})
            face = canvas[:FACE_H, :FACE_W]
            ay, ax = ci * CELL_H + 2, cj * CELL_W + 2
            atlas[ay:ay + FACE_H, ax:ax + FACE_W] = np.clip(np.round(face), 0, 255).astype(np.uint8)
            report_cells.append({'cell': f'r{ci}c{cj}', 'face_origin_xy': [ax, ay],
                                 'source': 'crosscut_swatch.webp (destriped, 64 px/in)', 'patches': patches})
            print(f'cell r{ci}c{cj} done {time.time() - t0:.0f}s', flush=True)
    retries = save_png(atlas, os.path.join(TEX, 'Color.png'))
    json.dump({'cells': report_cells, 'png_save_retries': retries,
               'usage_max': float(usage.max()), 'usage_mean': float(usage.mean()),
               'params': {'patch_px': P, 'overlap_px': OV, 'seed': SEED, 'transforms': TRANSFORMS,
                          'W_USE': W_USE, 'W_CELL': W_CELL, 'TOPK': TOPK, 'W_RARE': W_RARE}},
              open(os.path.join(WORK, 'build_cells.json'), 'w'), indent=1)
    print('saved Color.png; usage max/mean', usage.max(), round(usage.mean(), 2))


if __name__ == '__main__':
    main()
