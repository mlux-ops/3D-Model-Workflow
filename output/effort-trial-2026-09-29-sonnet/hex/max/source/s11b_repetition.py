"""Step 11b: repetition tests on the finished maps -> work/repetition.json

python s11b_repetition.py [faces|patch_bump|patch_colour]     (no argument = all three, in that order)

Whole-face comparison (part "faces")
  Every pair of Raw faces (Bump16 height, and colour luminance) and every pair of Matte faces (colour
  luminance): disc of radius 300 atlas px centred on the face, normalised cross-correlation (NCC) of the
  zero-mean discs with a +-12 atlas-px shift tolerance, for every mirror x rotation
  (Raw 5 deg steps, Matte 15 deg steps; both contain the 12 D6 elements = mirror x 0/60/../300 deg).
  The best NCC over all transforms, over the D6 elements only and over the off-D6 angles only are kept.
  Positive controls: a face compared with a mirrored, rotated and shifted copy of itself.
Random-window search (parts "patch_bump", "patch_colour")
  Two 256 px discs per Raw face are drawn at random inside the Raw faces (8 px eroded), then searched over
  every position of every Raw face (torus FFT NCC, disc completely inside a Raw face) under the 12 D6
  elements. Two off-D6 rotations (20, 40 deg) are searched the same way as a null. Positive controls: an
  exact and a noisy copy planted after a D6 element at another position must be found again.
Chiseled faces are not tested numerically: their grooves repeat by design.
All searches run on 2x-reduced copies of the maps (linear resampling, torus preserving)."""

import json
import os
import sys
import time

import numpy as np
import scipy.fft as sfft
from scipy import ndimage as ndi
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path, save_text, load_gray16  # noqa: E402
from geometry import W, H, face_centres  # noqa: E402
from design import FULL_SCALE_MM  # noqa: E402

LUMW = np.array([0.2126, 0.7152, 0.0722], np.float32)
W2, H2 = 2245, 2268
FX, FY = W2 / W, H2 / H
SHIFT = 6
WIN_HALF = 160
FACE_R = 150
PATCH_N = 128
PATCH_R = PATCH_N // 2
RNG_SEED = 20260929
D6 = [(m, 60 * k) for m in (0, 1) for k in range(6)]
NULL = [(0, 20), (0, 40)]


def half_res(a):
    return ndi.zoom(a.astype(np.float32), (H2 / H, W2 / W), order=1, mode="grid-wrap", grid_mode=True)


def disc(n, r):
    yy, xx = np.mgrid[0:n, 0:n]
    return np.hypot(yy - (n - 1) / 2.0, xx - (n - 1) / 2.0) <= r


def face_window(A, cx, cy, half):
    xi = (int(round(cx * FX)) - half + np.arange(2 * half)) % W2
    yi = (int(round(cy * FY)) - half + np.arange(2 * half)) % H2
    return A[np.ix_(yi, xi)]


def transform(win, mirror, ang):
    w = win[:, ::-1] if mirror else win
    if ang % 360 != 0:
        w = ndi.rotate(w, ang, reshape=False, order=1, mode="reflect")
    return np.ascontiguousarray(w)


def prep(win, mask):
    return ((win - win[mask].mean()) * mask).astype(np.float32)


def lag_max(fa, fb, n):
    corr = sfft.irfft2(fa * np.conj(fb), s=(n, n))
    idx = np.arange(-SHIFT, SHIFT + 1) % n
    return float(corr[np.ix_(idx, idx)].max())


def transforms_of(win, step, mask):
    out = []
    for m in (0, 1):
        for a in np.arange(0, 360, step):
            t = prep(transform(win, m, float(a)), mask)
            out.append(((m, int(a)), sfft.rfft2(t), float(np.sqrt((t ** 2).sum()))))
    return out


def best_match(wa, wb, step):
    n = 2 * WIN_HALF
    mask = disc(n, FACE_R)
    ta = prep(wa, mask)
    fa, na = sfft.rfft2(ta), float(np.sqrt((ta ** 2).sum()))
    best = (-2.0, None)
    for key, fb, nb in transforms_of(wb, step, mask):
        v = lag_max(fa, fb, n) / (na * nb)
        if v > best[0]:
            best = (v, key)
    return best


def compare_faces(wins, step, label):
    n = 2 * WIN_HALF
    mask = disc(n, FACE_R)
    base = []
    for w in wins:
        t = prep(w, mask)
        base.append((sfft.rfft2(t), float(np.sqrt((t ** 2).sum()))))
    res = {}
    t0 = time.time()
    for b in range(1, len(wins)):
        tb = transforms_of(wins[b], step, mask)
        for a_ in range(b):
            fa, na = base[a_]
            best, best_d6, best_off = (-2.0, None), -2.0, -2.0
            for key, fb, nb in tb:
                v = lag_max(fa, fb, n) / (na * nb)
                if v > best[0]:
                    best = (v, key)
                if key[1] % 60 == 0:
                    best_d6 = max(best_d6, v)
                else:
                    best_off = max(best_off, v)
            res[(a_, b)] = (best[0], best[1], best_d6, best_off)
    print("%s: %d faces, %d pairs, %d transforms per pair, %.0fs"
          % (label, len(wins), len(res), 2 * len(np.arange(0, 360, step)), time.time() - t0))
    return res


def summarise(res, labels, step):
    items = sorted(((v[0], k, v) for k, v in res.items()), reverse=True)
    all_ = np.array([v[0] for v in res.values()])
    d6 = np.array([v[2] for v in res.values()])
    off = np.array([v[3] for v in res.values()])
    top = []
    for val, (a, b), v in items[:5]:
        top.append({"faces": [int(labels[a]), int(labels[b])], "ncc": round(float(val), 4),
                    "mirror": int(v[1][0]), "rotation_deg": int(v[1][1]), "ncc_best_d6": round(float(v[2]), 4)})
    return {
        "faces": len(labels), "pairs": len(res), "rotation_step_deg": step,
        "max_ncc_any_transform": float(all_.max()),
        "max_ncc_d6_elements": float(d6.max()),
        "max_ncc_off_d6_angles": float(off.max()),
        "median_pair_max_ncc_d6": float(np.median(d6)),
        "p95_pair_max_ncc_d6": float(np.percentile(d6, 95)),
        "median_pair_max_ncc_off_d6": float(np.median(off)),
        "top5_pairs": top,
    }


def store(key, value):
    p = out_path("work", "repetition.json")
    cur = json.load(open(p)) if os.path.exists(p) else {}
    cur[key] = value
    save_text(json.dumps(cur, indent=1), "work", "repetition.json")


def load_maps(need_bump, need_colour):
    t0 = time.time()
    layout = json.load(open(out_path("work", "layout.json")))["faces"]
    types = {f["index"]: f["type"] for f in layout}
    fid = load_gray16(out_path("textures", "face_ids.png"))
    out = {"types": types, "centres": face_centres()}
    if need_bump:
        bump = load_gray16(out_path("textures", "Bump16.png")).astype(np.float32) * (FULL_SCALE_MM / 65535.0)
        out["bump2"] = half_res(bump)
    if need_colour:
        colour = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB")).astype(np.float32)
        out["lum2"] = half_res(colour @ LUMW)
    raw_ids = [i for i, t in types.items() if t == "raw"]
    eroded = ndi.binary_erosion(np.isin(fid, raw_ids), iterations=8, border_value=1)
    out["raw_mask2"] = half_res(eroded.astype(np.float32)) >= 0.99
    out["face_map2"] = np.rint(half_res(np.where(eroded, fid, 0).astype(np.float32))).astype(np.int32)
    print("maps loaded %.0fs" % (time.time() - t0))
    return out


def part_faces():
    m = load_maps(True, True)
    types, centres = m["types"], m["centres"]
    raw_c = [c for c in centres if types[c["index"]] == "raw"]
    matte_c = [c for c in centres if types[c["index"]] == "matte"]
    store("_note", "NCC = normalised cross-correlation of zero-mean discs (radius %d atlas px); shift tolerance "
                   "+-%d atlas px; Raw sweep 5 deg, Matte sweep 15 deg" % (2 * FACE_R, 2 * SHIFT))

    wins = [face_window(m["bump2"], c["cx"], c["cy"], WIN_HALF) for c in raw_c]
    res = compare_faces(wins, 5, "raw whole-face (bump)")
    store("raw_whole_face_bump", summarise(res, [c["index"] for c in raw_c], 5))

    wins_l = [face_window(m["lum2"], c["cx"], c["cy"], WIN_HALF) for c in raw_c]
    res = compare_faces(wins_l, 5, "raw whole-face (colour luminance)")
    store("raw_whole_face_colour", summarise(res, [c["index"] for c in raw_c], 5))

    wins_m = [face_window(m["lum2"], c["cx"], c["cy"], WIN_HALF) for c in matte_c]
    res = compare_faces(wins_m, 15, "matte whole-face (colour luminance)")
    store("matte_whole_face_colour", summarise(res, [c["index"] for c in matte_c], 15))

    w0 = wins[0]
    controls = []
    for (mir, ang, dy, dx) in ((1, 180.0, 3, -4), (0, 60.0, -2, 5), (1, 120.0, 0, 0)):
        cw = np.roll(transform(w0, mir, ang), (dy, dx), axis=(0, 1))
        v, key = best_match(w0, cw, 5)
        controls.append({"planted": {"mirror": mir, "rotation_deg": ang, "shift_px": [dx, dy]},
                         "recovered_transform": list(key), "ncc": float(v)})
    store("whole_face_positive_controls", controls)
    print(json.dumps(controls))


def disc_kernel_full(n, r):
    k = np.zeros((H2, W2), np.float32)
    yy, xx = np.mgrid[-n // 2:n // 2, -n // 2:n // 2]
    msk = np.hypot(yy + 0.5, xx + 0.5) <= r
    k[np.ix_(yy[:, 0] % H2, xx[0] % W2)] = msk
    return k


def template_full(t):
    n = t.shape[0]
    T = np.zeros((H2, W2), np.float32)
    T[np.ix_(np.arange(-n // 2, n // 2) % H2, np.arange(-n // 2, n // 2) % W2)] = t
    return T


class PatchSearch:
    def __init__(self, atlas, valid_mask):
        self.A = atlas
        self.fA = sfft.rfft2(atlas, workers=4)
        K = disc_kernel_full(PATCH_N, PATCH_R)
        self.fK = np.conj(sfft.rfft2(K, workers=4))
        self.nd = float(K.sum())
        s1 = sfft.irfft2(self.fA * self.fK, s=(H2, W2), workers=4)
        s2 = sfft.irfft2(sfft.rfft2(atlas * atlas, workers=4) * self.fK, s=(H2, W2), workers=4)
        self.sigma = np.sqrt(np.maximum(s2 / self.nd - (s1 / self.nd) ** 2, 1e-12))
        inside = sfft.irfft2(sfft.rfft2(valid_mask.astype(np.float32), workers=4) * self.fK, s=(H2, W2), workers=4)
        self.valid = inside >= self.nd - 0.5

    def run(self, tmpl, exclude_at=None):
        T = template_full(tmpl)
        num = sfft.irfft2(self.fA * np.conj(sfft.rfft2(T, workers=4)), s=(H2, W2), workers=4)
        sig_t = float(np.sqrt((tmpl ** 2).sum() / self.nd))
        ncc = num / (self.nd * self.sigma * sig_t)
        ok = self.valid.copy()
        if exclude_at is not None:
            y0, x0 = exclude_at
            dy = (np.arange(H2) - y0 + H2 // 2) % H2 - H2 // 2
            dx = (np.arange(W2) - x0 + W2 // 2) % W2 - W2 // 2
            ok &= ~((np.abs(dy)[:, None] < PATCH_N) & (np.abs(dx)[None, :] < PATCH_N))
        ncc = np.where(ok, ncc, -2.0)
        k = int(np.argmax(ncc))
        return float(ncc.flat[k]), (k // W2, k % W2)


def patch_window(A, y, x):
    return A[np.ix_((y - PATCH_R + np.arange(PATCH_N)) % H2, (x - PATCH_R + np.arange(PATCH_N)) % W2)]


def patch_test(A, raw_mask2, face_map2, label):
    rng = np.random.default_rng(RNG_SEED)
    A0 = np.where(raw_mask2, A - A[raw_mask2].mean(), 0.0).astype(np.float32)
    S = PatchSearch(A0, raw_mask2)
    ys, xs = np.nonzero(S.valid)
    face_of = face_map2[ys, xs]
    print("%s: valid window centres %d in %d Raw faces" % (label, len(ys), len(np.unique(face_of))))
    picks = []
    for fidx in np.unique(face_of):
        sel = np.nonzero(face_of == fidx)[0]
        for s in rng.choice(sel, size=2, replace=False):
            picks.append((int(ys[s]), int(xs[s]), int(fidx)))
    mask = disc(PATCH_N, PATCH_R)
    per_window = []
    t0 = time.time()
    for (y, x, fidx) in picks:
        win = patch_window(A0, y, x)
        best = {}
        for grp, lst in (("d6", D6), ("null", NULL)):
            best[grp] = (-2.0, None, None)
            for (mir, ang) in lst:
                t = prep(transform(win, mir, float(ang)), mask)
                v, pos = S.run(t, exclude_at=(y, x) if (mir == 0 and ang == 0) else None)
                if v > best[grp][0]:
                    best[grp] = (v, (mir, ang), pos)
        per_window.append({
            "face_index": fidx, "window_at_atlas_xy": [int(x / FX), int(y / FY)],
            "d6_best_ncc": round(best["d6"][0], 4), "d6_transform": list(best["d6"][1]),
            "d6_match_at_atlas_xy": [int(best["d6"][2][1] / FX), int(best["d6"][2][0] / FY)],
            "null_best_ncc": round(best["null"][0], 4), "null_transform": list(best["null"][1]),
            "null_match_at_atlas_xy": [int(best["null"][2][1] / FX), int(best["null"][2][0] / FY)]})
    print("%s: %d windows x %d transforms, %.0fs" % (label, len(picks), len(D6) + len(NULL), time.time() - t0))
    d6v = np.array([p["d6_best_ncc"] for p in per_window])
    nlv = np.array([p["null_best_ncc"] for p in per_window])

    y, x, fidx = picks[0]
    win = patch_window(A0, y, x)
    other = next(p for p in picks if p[2] != fidx)
    planted = transform(win, 1, 120.0)
    ctrl = {}
    for name, noise in (("exact_copy", 0.0), ("noisy_copy_noise_std_0.5x", 0.5)):
        A2 = A0.copy()
        yi = (other[0] - PATCH_R + np.arange(PATCH_N)) % H2
        xi = (other[1] - PATCH_R + np.arange(PATCH_N)) % W2
        pw = planted + noise * float(win[mask].std()) * rng.standard_normal(planted.shape).astype(np.float32)
        A2[np.ix_(yi, xi)] = np.where(mask, pw, A2[np.ix_(yi, xi)])
        Sc = PatchSearch(A2, raw_mask2)
        t = prep(transform(win, 1, 120.0), mask)
        v, pos = Sc.run(t, exclude_at=None)
        ctrl[name] = {"ncc": v,
                      "found_at_planted_position": bool(abs(pos[0] - other[0]) <= 2 and abs(pos[1] - other[1]) <= 2)}
    return {
        "windows": len(picks), "window_diameter_atlas_px": 2 * PATCH_N,
        "valid_window_centres_half_res": int(len(ys)),
        "max_ncc_d6_elements": float(d6v.max()), "median_ncc_d6_elements": float(np.median(d6v)),
        "max_ncc_off_d6_null": float(nlv.max()), "median_ncc_off_d6_null": float(np.median(nlv)),
        "positive_controls_planted_after_mirror_rot120": ctrl,
        "top4_windows": sorted(per_window, key=lambda p: -p["d6_best_ncc"])[:4],
        "top4_null_windows": sorted(per_window, key=lambda p: -p["null_best_ncc"])[:4],
        "per_window": per_window,
    }


def part_patch(kind):
    m = load_maps(kind == "patch_bump", kind == "patch_colour")
    if kind == "patch_bump":
        out = patch_test(m["bump2"], m["raw_mask2"], m["face_map2"], "raw patches (bump)")
        store("raw_patch_search_bump", out)
    else:
        out = patch_test(m["lum2"], m["raw_mask2"], m["face_map2"], "raw patches (colour luminance)")
        store("raw_patch_search_colour", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("top4_windows", "top4_null_windows", "per_window")},
                     indent=1))


def main():
    t0 = time.time()
    parts = sys.argv[1:] or ["faces", "patch_bump", "patch_colour"]
    for p in parts:
        if p == "faces":
            part_faces()
        else:
            part_patch(p)
    print("done %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
