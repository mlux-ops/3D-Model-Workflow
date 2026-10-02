"""Repeat search on the finished atlas.

1. Patch search: 128 px (2 in) patches from matte and raw face interiors are matched against every position of the whole atlas (torus, half resolution,
   high-passed luminance) under all 8 dihedral transforms with normalised cross-correlation; windows touching a joint or a chiseled face are ignored.
   A positive control (a rotated, noise-degraded copy of one patch planted elsewhere) shows what a repeat looks like to this search.
2. Whole-face search: every pair of matte faces and of raw faces, centred, under the 12 symmetries of the hexagon (6 rotations x mirror).
Writes work/repeat_search.json.
"""
import json
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import scipy.fft as sfft
from scipy import ndimage as ndi
from PIL import Image
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
info = json.load(open(rg.WORK + "face_info.json"))
P = info["params"]
W, H = P["W"], P["H"]
type_of = {fc["index"]: fc["type"] for fc in info["faces"]}
color = np.asarray(Image.open(TEX + "Color.png").convert("RGB")).astype(np.float32)
ids = np.asarray(Image.open(TEX + "face_ids.png")).astype(np.int64)
lum = color @ np.array([0.299, 0.587, 0.114], np.float32)
del color

# high-passed luminance (atlas resolution), joints and pixels of chiseled faces zeroed later
hp_full = lum - ndi.gaussian_filter(lum, 8.0, mode="wrap")
hp_full = ndi.gaussian_filter(hp_full, 1.0, mode="wrap")

# ---- 1. patch search at half resolution
Wh, Hh = (W // 2) * 2, H
hp = hp_full[:Hh, :Wh].reshape(Hh // 2, 2, Wh // 2, 2).mean(axis=(1, 3)).astype(np.float32)
ids_h = ids[::2, ::2][:hp.shape[0], :hp.shape[1]]
lut = np.zeros(int(ids.max()) + 1, bool)
for k, t in type_of.items():
    lut[k] = t in ("matte", "raw")
face_ok = lut[ids_h]
face_ok = ndi.binary_erosion(face_ok, structure=np.ones((3, 3), bool), iterations=3)
PS = 64
Vbox = ndi.uniform_filter(face_ok.astype(np.float32), PS, mode="wrap")
Vstart = np.roll(Vbox, (-PS // 2, -PS // 2), axis=(0, 1)) > 0.9999
hp = np.where(face_ok, hp, 0.0).astype(np.float32)
sh, sw = hp.shape
print("half-res atlas", hp.shape, "valid window starts", int(Vstart.sum()))


def dihedral(p, t):
    q = np.rot90(p, t & 3)
    return q[:, ::-1] if t & 4 else q


def correlate(patch, F_ref, valid, sigma):
    """NCC map (start positions) of one zero-mean patch against the stored image spectrum."""
    p = patch - patch.mean()
    sp = p.std()
    pad = np.zeros(shape, np.float32)
    pad[:PS, :PS] = p
    c = sfft.irfft2(F_ref * np.conj(sfft.rfft2(pad, workers=-1)), s=shape, workers=-1)
    ncc = c / (PS * PS * sigma * sp + 1e-9)
    ncc[~valid] = -1.0
    return ncc


# torus: tile the half-res atlas by one window on right/bottom so that windows crossing the wrap are seen without padding artefacts
tile_h, tile_w = sh + PS, sw + PS
hp_t = np.tile(hp, (2, 2))[:tile_h, :tile_w]
fo_t = np.tile(face_ok, (2, 2))[:tile_h, :tile_w]
shape = (sfft.next_fast_len(tile_h + PS), sfft.next_fast_len(tile_w + PS))
F_img = sfft.rfft2(hp_t, s=shape, workers=-1)
Vt = ndi.uniform_filter(fo_t.astype(np.float32), PS, mode="constant")
Vt = np.roll(Vt, (-PS // 2, -PS // 2), axis=(0, 1)) > 0.9999
mt1 = np.roll(ndi.uniform_filter(hp_t, PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1))
mt2 = np.roll(ndi.uniform_filter(hp_t * hp_t, PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1))
sigt = np.sqrt(np.maximum(mt2 - mt1 * mt1, 1e-6))
valid = np.zeros(shape, bool)
valid[:tile_h - PS + 1, :tile_w - PS + 1] = Vt[:tile_h - PS + 1, :tile_w - PS + 1]
valid[sh:, :] = False
valid[:, sw:] = False
sigma = np.ones(shape, np.float32)
sigma[:tile_h, :tile_w] = sigt
del mt1, mt2, Vt, sigt
print("torus-tiled fft shape", shape, "valid starts", int(valid.sum()))

rng = np.random.default_rng(20260929)
cands = np.argwhere(Vstart)
face_at = lambda y, x: int(ids_h[min(y + PS // 2, sh - 1), min(x + PS // 2, sw - 1)])
by_face = {}
for (y, x) in cands:
    by_face.setdefault(face_at(y, x), []).append((int(y), int(x)))
patches = []
for fid, lst in sorted(by_face.items()):
    if fid == 0 or type_of.get(fid) not in ("matte", "raw"):
        continue
    n = 4 if type_of[fid] == "matte" else 6
    for k in rng.choice(len(lst), size=min(n, len(lst)), replace=False):
        patches.append((fid, lst[int(k)]))
if len(sys.argv) > 1:
    keep = rng.choice(len(patches), size=min(int(sys.argv[1]), len(patches)), replace=False)
    patches = [patches[int(k)] for k in sorted(keep)]
print("patches", len(patches))


def circ_dist(a, b, n):
    d = abs(a - b) % n
    return min(d, n - d)


t0 = time.time()
results = []
EXC = PS + 16
for pi, (fid, (y0, x0)) in enumerate(patches):
    patch = hp[y0:y0 + PS, x0:x0 + PS]
    best = (-2.0, None)
    yy = np.arange(shape[0])[:, None]
    xx = np.arange(shape[1])[None, :]
    near = (np.minimum((yy - y0) % sh, (y0 - yy) % sh) < EXC) & (np.minimum((xx - x0) % sw, (x0 - xx) % sw) < EXC)
    near_pad = np.zeros(shape, bool)
    near_pad[:] = near
    for t in range(8):
        ncc = correlate(dihedral(patch, t), F_img, valid & ~near_pad, sigma)
        k = int(np.argmax(ncc))
        v = float(ncc.flat[k])
        if v > best[0]:
            my, mx = divmod(k, shape[1])
            best = (v, dict(transform=t, at_start_px_half_res=[int(my), int(mx)], matched_face=face_at(my, mx), matched_type=type_of.get(face_at(my, mx))))
    results.append(dict(face=fid, type=type_of[fid], start_half_res=[y0, x0], max_ncc=best[0], match=best[1]))
    if pi == 0:
        print("first patch %.1f s -> estimated total %.0f s" % (time.time() - t0, (time.time() - t0) * len(patches)))
    if pi % 20 == 19:
        print(" %d / %d patches, %.0f s, running max %.3f" % (pi + 1, len(patches), time.time() - t0, max(r["max_ncc"] for r in results)))

mx = np.array([r["max_ncc"] for r in results])
summary = dict(
    patch_size_atlas_px=PS * 2, patch_size_in=PS * 2 / P["PPI"], n_patches=len(results), n_matte=sum(1 for r in results if r["type"] == "matte"), n_raw=sum(1 for r in results if r["type"] == "raw"),
    n_windows_searched=int(valid.sum()), transforms=8,
    max_ncc_overall=float(mx.max()), p99_ncc=float(np.percentile(mx, 99)), median_of_patch_max_ncc=float(np.median(mx)), mean_of_patch_max_ncc=float(mx.mean()),
    count_over_0_30=int((mx > 0.30).sum()), count_over_0_40=int((mx > 0.40).sum()), count_over_0_50=int((mx > 0.50).sum()), worst=sorted(results, key=lambda r: -r["max_ncc"])[:5])
print("patch search summary", json.dumps({k: v for k, v in summary.items() if k != "worst"}, indent=0))
print("worst", summary["worst"][:3])

# positive control: plant a rotated (t=5), noise-degraded copy of patch 0 at another valid location and search again
fid0, (y0, x0) = patches[0]
src = hp[y0:y0 + PS, x0:x0 + PS]
rng2 = np.random.default_rng(7)
ctrl = {}
for snr_name, noise in (("noise_std_equals_patch_std", 1.0), ("noise_std_2x_patch_std", 2.0)):
    hp_c = hp.copy()
    far = [c for c in cands if circ_dist(c[0], y0, sh) > 600 and circ_dist(c[1], x0, sw) > 600]
    ty, tx = far[int(rng2.integers(len(far)))]
    planted = dihedral(src, 5) + rng2.normal(0, noise * src.std(), (PS, PS)).astype(np.float32)
    hp_c[ty:ty + PS, tx:tx + PS] = planted
    hp_ct = np.tile(hp_c, (2, 2))[:tile_h, :tile_w]
    Fc = sfft.rfft2(hp_ct, s=shape, workers=-1)
    mt1 = np.roll(ndi.uniform_filter(hp_ct, PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1))
    mt2 = np.roll(ndi.uniform_filter(hp_ct * hp_ct, PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1))
    sig_c = np.ones(shape, np.float32)
    sig_c[:tile_h, :tile_w] = np.sqrt(np.maximum(mt2 - mt1 * mt1, 1e-6))
    best = (-2, None)
    for t in range(8):
        ncc = correlate(dihedral(src, t), Fc, valid, sig_c)
        # exclude the source itself
        yy = np.arange(shape[0])[:, None]
        xx = np.arange(shape[1])[None, :]
        near = (np.minimum((yy - y0) % sh, (y0 - yy) % sh) < EXC) & (np.minimum((xx - x0) % sw, (x0 - xx) % sw) < EXC)
        ncc[near] = -1
        k = int(np.argmax(ncc))
        if ncc.flat[k] > best[0]:
            best = (float(ncc.flat[k]), (t, *divmod(k, shape[1])))
    ctrl[snr_name] = dict(planted_at=[int(ty), int(tx)], found_ncc=best[0], found=dict(transform=best[1][0], at=[best[1][1], best[1][2]]))
    print("control", snr_name, ctrl[snr_name])
summary["positive_control"] = ctrl

# ---- 2. whole-face search under the 12 hexagon symmetries (quarter resolution)
Q = 4
half = 324 // Q
faces = {}
for fc in info["faces"]:
    if fc["type"] not in ("matte", "raw"):
        continue
    cy, cx = int(round(fc["cy"])), int(round(fc["cx"]))
    ys = (np.arange(cy - 324, cy + 324) % H)
    xs = (np.arange(cx - 324, cx + 324) % W)
    win = hp_full[np.ix_(ys, xs)]
    win = win.reshape(648 // Q, Q, 648 // Q, Q).mean(axis=(1, 3))
    faces[fc["index"]] = (fc["type"], win)
yy, xx = np.mgrid[0:648 // Q, 0:648 // Q]
V = yy - (648 // Q - 1) / 2.0
U = xx - (648 // Q - 1) / 2.0
dq = np.maximum(np.abs(V), np.abs(U) * (np.sqrt(3) / 2) + np.abs(V) / 2)
mask = dq <= 300.0 / Q


def sym(a, k):
    b = a[:, ::-1] if k >= 6 else a
    return ndi.rotate(b, 60.0 * (k % 6), reshape=False, order=1, mode="constant") if k % 6 else b


def normalise(a):
    v = a[mask]
    return (a - v.mean()) * mask / (v.std() * np.sqrt(mask.sum()) + 1e-9)


wf = dict(matte=[], raw=[])
for t in ("matte", "raw"):
    idl = [k for k, v in faces.items() if v[0] == t]
    base = {k: normalise(faces[k][1]) for k in idl}
    trans = {k: [normalise(sym(faces[k][1], s)) for s in range(12)] for k in idl}
    for a in range(len(idl)):
        for b in range(a + 1, len(idl)):
            vals = [float((base[idl[a]] * trans[idl[b]][s]).sum()) for s in range(12)]
            wf[t].append(max(vals))
wf_summary = {t: dict(n_pairs=len(v), max_ncc=float(max(v)), mean_of_pair_max=float(np.mean(v)), p99=float(np.percentile(v, 99)), count_over_0_30=int(sum(1 for x in v if x > 0.30))) for t, v in wf.items()}
print("whole-face", wf_summary)
summary["whole_face_pairs"] = dict(resolution_px_per_in=P["PPI"] / Q, symmetries=12, **wf_summary)

json.dump(dict(summary=summary, patches=results), open(guard.safe(rg.WORK + "repeat_search.json"), "w"), indent=1)
print("done %.0f s" % (time.time() - t0))
