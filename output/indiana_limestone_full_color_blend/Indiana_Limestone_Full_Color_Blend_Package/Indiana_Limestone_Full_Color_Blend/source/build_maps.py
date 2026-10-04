"""Build a seamless, non-repeating Indiana Limestone Full Color Blend texture.

Inputs: the two supplied 47 x 94 in colour maps (1000 x 2000 px, 21.28 px/in).
Output: one 192 x 192 in (16'-0" x 16'-0") tile at 4096 x 4096 px (21.33 px/in).

Layers, all periodic on the output torus:
  1. zone field   - buff vs gray, soft meandering mostly-vertical bands, buff share
                    and both colours measured from the sources (analysis.json)
  2. detail       - real grain + mottle (source minus its 40 px low-pass), rebuilt by
                    toroidal image quilting (Efros-Freeman min-error cuts). Buff-zone
                    patches go where the output is buff, gray-zone patches where gray.
                    A (position, flip) is used once; patches holding the few
                    iron/rust spots are excluded so no landmark is duplicated.
  3. inclusions   - a handful of unique iron spots drawn at the source spots' measured
                    colour offset, so the product's occasional spot remains.
Bump: 16-bit grey from the detail luminance (darker pores lower).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
REFS = [ROOT / "references/01_supplied_colormap_A_47x94.webp",
        ROOT / "references/02_supplied_colormap_B_47x94.webp"]
NAME = "Indiana Limestone Full Color Blend"
SIZE_IN = 192.0
N = 4096                      # output px per side
PPI = N / SIZE_IN             # 21.333 px/in (source 21.277 -> 0.26 % scale, ignored)
P, O = 160, 32                # quilting patch (7.5 in) and overlap, px
S = P - O                     # 128 px step; N / S = 32 placements per side
SIG_ZONE = 40.0
BUMP_AMOUNT = 15              # Revit editor value (stored value x100)
SEED = 20261003


def out_path(rel):
    p = (ROOT / rel).resolve()
    if ROOT.resolve() not in p.parents:
        raise RuntimeError(f"write outside run dir refused: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float64) / 255.0


def wblur(a, s):
    sig = (s, s, 0) if a.ndim == 3 else s
    return ndi.gaussian_filter(a, sig, mode="wrap")


def periodic_noise(rng, n, corr_x_px, corr_y_px):
    """Gaussian random field, periodic on n x n, gaussian spectrum, unit std."""
    f = np.fft.fftfreq(n)
    fy, fx = np.meshgrid(f, f, indexing="ij")
    amp = np.exp(-0.5 * ((fx * corr_x_px * 2 * np.pi) ** 2 + (fy * corr_y_px * 2 * np.pi) ** 2) / 4)
    z = np.fft.ifft2(np.fft.fft2(rng.standard_normal((n, n))) * amp).real
    return (z - z.mean()) / z.std()


# ---------------------------------------------------------------- source prep
def prepare_sources(ana):
    pools = {"buff": [], "gray": []}
    dets, spot_deltas, excluded = [], [], 0
    for si, p in enumerate(REFS):
        a = load(p)
        low = ndi.gaussian_filter(a, (SIG_ZONE, SIG_ZONE, 0), mode="reflect")
        det = a - low
        thr = ana["sources"][si]["chroma_threshold"]
        buff = (low[..., 0] - low[..., 2]) > thr
        # iron/rust spots: strong local chroma + darkening in the 2 px-blurred detail
        d2 = ndi.gaussian_filter(det, (2, 2, 0), mode="reflect")
        chroma = d2[..., 0] - d2[..., 2]
        lum = d2.mean(-1)
        spot = (chroma > 6 * chroma.std()) | (lum < -7 * lum.std())
        spot = ndi.binary_dilation(spot, iterations=4)
        if spot.any():
            lab, k = ndi.label(spot)
            for i in range(1, k + 1):
                m = lab == i
                spot_deltas.append(det[m & (det.mean(-1) < np.percentile(det[m].mean(-1), 40))].mean(0))
        spot_any = ndi.maximum_filter(spot.astype(np.uint8), size=P, origin=-(P // 2)) > 0
        h, w = buff.shape
        for zone, zmask in (("buff", buff), ("gray", ~buff)):
            core = ndi.binary_erosion(zmask, iterations=70)
            # patch top-left (y, x) valid if whole patch inside core and spot-free
            ok = ndi.minimum_filter(core.astype(np.uint8), size=P, origin=-(P // 2)) > 0
            ok[h - P + 1:, :] = False
            ok[:, w - P + 1:] = False
            excluded += int((ok & spot_any).sum())
            ok &= ~spot_any
            ys, xs = np.nonzero(ok[::4, ::4])
            for y, x in zip(ys * 4, xs * 4):
                pools[zone].append((si, int(y), int(x)))
        dets.append(det.astype(np.float32))
    return dets, {k: np.array(v, dtype=np.int32) for k, v in pools.items()}, spot_deltas, excluded


def get_patch(dets, cand, flip):
    si, y, x = cand
    p = dets[si][y:y + P, x:x + P]
    if flip & 1:
        p = p[:, ::-1]
    if flip & 2:
        p = p[::-1, :]
    return p


def min_path(e):
    """Vertical min-cost path through e (rows x cols); returns col index per row."""
    r, c = e.shape
    cost = e.copy()
    for i in range(1, r):
        prev = cost[i - 1]
        left = np.r_[np.inf, prev[:-1]]
        right = np.r_[prev[1:], np.inf]
        cost[i] += np.minimum(np.minimum(left, prev), right)
    path = np.empty(r, dtype=int)
    path[-1] = int(np.argmin(cost[-1]))
    for i in range(r - 2, -1, -1):
        j = path[i + 1]
        lo, hi = max(0, j - 1), min(c, j + 2)
        path[i] = lo + int(np.argmin(cost[i, lo:hi]))
    return path


def quilt(dets, pools, zone, rng, report):
    n_side = N // S
    D = np.zeros((N, N, 3), np.float32)
    F = np.zeros((N, N), bool)
    # a source position may be reused only in a different flip/rotation, and the
    # same (position, flip) neighbourhood is retired after one use
    used = {k: np.zeros((len(v), 4), bool) for k, v in pools.items()}
    ncand = 700
    zone_choice = []
    for i in range(n_side):
        for j in range(n_side):
            y0, x0 = i * S, j * S
            rows = np.arange(y0, y0 + P) % N
            cols = np.arange(x0, x0 + P) % N
            ix = np.ix_(rows, cols)
            E = D[ix]
            Fm = F[ix]
            zk = "buff" if zone[(y0 + P // 2) % N, (x0 + P // 2) % N] > 0.5 else "gray"
            zone_choice.append(zk)
            pool = pools[zk]
            avail = np.flatnonzero(~used[zk])
            sel = rng.choice(avail, size=min(ncand, len(avail)), replace=False)
            pick, flips = sel // 4, sel % 4
            if Fm.any():
                w = Fm[::2, ::2].astype(np.float32)[..., None]
                Es = E[::2, ::2]
                ssd = np.empty(len(pick))
                for k, (ci, fl) in enumerate(zip(pick, flips)):
                    pt = get_patch(dets, pool[ci], fl)[::2, ::2]
                    ssd[k] = float((w * (pt - Es) ** 2).sum())
                best = ssd.min()
                good = np.nonzero(ssd <= best * 1.10 + 1e-12)[0]
                k = int(rng.choice(good))
            else:
                k = 0
            ci, fl = pick[k], flips[k]
            sy, sx = pool[ci][1], pool[ci][2]
            same = (pool[:, 0] == pool[ci][0]) & (np.abs(pool[:, 1] - sy) < P // 6) & (np.abs(pool[:, 2] - sx) < P // 6)
            used[zk][same, fl] = True
            patch = get_patch(dets, pool[ci], fl)
            M = np.ones((P, P), bool)
            if Fm.any():
                e = ((patch - E) ** 2).sum(-1)
                if Fm[P // 2, :O].all():          # left
                    pth = min_path(e[:, :O])
                    M &= ~(np.arange(P)[None, :] < pth[:, None])
                if Fm[:O, P // 2].all():          # top
                    pth = min_path(e[:O, :].T)
                    M &= ~(np.arange(P)[:, None] < pth[None, :])
                if j == n_side - 1 and Fm[P // 2, P - O:].all():   # right (wrap)
                    pth = min_path(e[:, P - O:]) + (P - O)
                    M &= ~(np.arange(P)[None, :] > pth[:, None])
                if i == n_side - 1 and Fm[P - O:, P // 2].all():   # bottom (wrap)
                    pth = min_path(e[P - O:, :].T) + (P - O)
                    M &= ~(np.arange(P)[:, None] > pth[None, :])
            M |= ~Fm
            alpha = ndi.gaussian_filter(M.astype(np.float32), 0.8)
            alpha[~Fm] = 1.0
            D[ix] = alpha[..., None] * patch + (1 - alpha[..., None]) * E
            F[ix] = True
    report["quilt"] = {
        "placements": n_side * n_side, "patch_px": P, "overlap_px": O,
        "buff_placements": zone_choice.count("buff"), "gray_placements": zone_choice.count("gray"),
        "pool_sizes": {k: int(len(v)) for k, v in pools.items()},
        "pool_position_flips_retired": {k: int(v.sum()) for k, v in used.items()},
    }
    assert F.all()
    return D.astype(np.float64)


# ---------------------------------------------------------------- zone field
def zone_field(rng, buff_frac):
    # broad mostly-vertical bands (source: 1-2 soft boundaries per 47 in width,
    # running the full 94 in height): horizontal corr ~12 in, vertical ~72 in,
    # plus a gentle wobble so boundaries waver like the source edges. Narrow
    # spurs and islands are removed (open/close, 2.5 in) so the zones read as
    # irregular bands, not as memorable figures that betray the 16 ft repeat.
    base = periodic_noise(rng, N, 12.0 * PPI, 72.0 * PPI)
    wob = periodic_noise(rng, N, 3.0 * PPI, 6.0 * PPI)
    f = base + 0.05 * wob
    t = np.quantile(f, 1 - buff_frac)
    hard = (f > t).astype(np.float64)
    r = int(2.5 * PPI)
    disk = np.hypot(*np.mgrid[-r:r + 1, -r:r + 1]) <= r
    pad = 2 * r + 2                       # periodic morphology: wrap-pad, operate, crop
    m = np.pad(hard > 0.5, pad, mode="wrap")
    m = ndi.binary_closing(ndi.binary_opening(m, disk), disk)[pad:-pad, pad:-pad]
    return np.clip(wblur(m.astype(np.float64), 1.5 * PPI), 0, 1)


def inclusions(rng, deltas, k=14):
    out = np.zeros((N, N, 3))
    delta = np.mean(deltas, axis=0) if deltas else np.array([0.02, -0.01, -0.05])
    yy, xx = np.mgrid[-24:25, -24:25]
    for _ in range(k):
        cy, cx = rng.integers(0, N, 2)
        r = rng.uniform(0.12, 0.45) * PPI
        ang = np.arctan2(yy, xx)
        rr = r * (1 + 0.35 * np.sin(3 * ang + rng.uniform(0, 6.3)) + 0.2 * np.sin(5 * ang + rng.uniform(0, 6.3)))
        blob = np.clip((rr - np.hypot(yy, xx)) / 1.5 + 0.5, 0, 1)
        blob = ndi.gaussian_filter(blob, 0.7) * rng.uniform(0.6, 1.0)
        rows = (np.arange(-24, 25) + cy) % N
        cols = (np.arange(-24, 25) + cx) % N
        out[np.ix_(rows, cols)] += blob[..., None] * delta
    return out


def save_png8(arr, rel):
    p = out_path(rel)
    Image.fromarray(np.clip(np.round(arr * 255), 0, 255).astype(np.uint8), "RGB").save(p)
    return p


def save_png16(h, rel):
    p = out_path(rel)
    Image.fromarray(np.clip(np.round(h * 65535), 0, 65535).astype(np.uint16)).save(p)
    return p


def png_header(p):
    b = Path(p).read_bytes()[16:26]
    w, h = int.from_bytes(b[0:4], "big"), int.from_bytes(b[4:8], "big")
    return {"w": w, "h": h, "bit_depth": b[8], "color_type": b[9]}


def main():
    ana = json.loads((ROOT / "source/analysis.json").read_text())
    rng = np.random.default_rng(SEED)
    report = {"seed": SEED, "size_in": SIZE_IN, "px": N, "px_per_in": PPI}
    dets, pools, spot_deltas, excl = prepare_sources(ana)
    report["source_spots_found"] = len(spot_deltas)
    report["patch_positions_excluded_for_spots"] = excl
    zone = zone_field(rng, ana["overall_buff_fraction"])
    report["zone_buff_fraction"] = float((zone > 0.5).mean())
    det = quilt(dets, pools, zone, rng, report)
    buff = np.array(ana["buff_rgb_mean"]); gray = np.array(ana["gray_rgb_mean"])
    lowvar = periodic_noise(rng, N, 8 * PPI, 8 * PPI)[..., None] * np.array(ana["buff_rgb_std"])
    base = zone[..., None] * buff + (1 - zone[..., None]) * gray + lowvar
    inc = inclusions(rng, spot_deltas)
    color = base + det + inc
    report["color_mean_rgb"] = color.reshape(-1, 3).mean(0).tolist()
    report["source_mean_rgb"] = np.mean([s["mean_rgb"] for s in ana["sources"]], axis=0).tolist()

    # bump: pores (darker detail) low; iron spots flush. Full 16-bit range.
    lum = ndi.gaussian_filter(det.mean(-1), 0.6, mode="wrap")
    h = -lum
    lo, hi = np.percentile(h, [0.05, 99.95])
    h = np.clip((h - lo) / (hi - lo), 0, 1)

    ft = "16'-0in x 16'-0in"
    cp = save_png8(color, f"textures/{NAME} - {ft}.png")
    bp = save_png16(h, f"textures/{NAME} - {ft} - Bump {BUMP_AMOUNT}.png")
    report["files"] = {"color": cp.name, "bump": bp.name,
                       "color_header": png_header(cp), "bump_header": png_header(bp)}
    report["sample_size"] = {"width_in": SIZE_IN, "height_in": SIZE_IN, "revit": "16'-0\" x 16'-0\""}
    report["revit_bump_amount"] = BUMP_AMOUNT
    out_path("source/build_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
