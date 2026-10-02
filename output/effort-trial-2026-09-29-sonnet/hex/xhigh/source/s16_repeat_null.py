"""Interpret the atlas repeat search.

A. Null reference: the same patch search run on the source render itself (whose complete matte and raw faces are known to be unique, see
   work/source_copy_check.json), at the same physical patch size and scale, no torus, 8 dihedral transforms.
B. The top atlas matches, re-measured at full resolution in a fine band and a coarse band, and written to a contact sheet
   (textures/_REVIEW_repeat_top_matches.jpg, every pair is patch-with-transform | matched window).
Writes work/repeat_null.json.
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import scipy.fft as sfft
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
PS = 62
rng = np.random.default_rng(20260930)


def dihedral(p, t):
    q = np.rot90(p, t & 3)
    return q[:, ::-1] if t & 4 else q


# ---- A. render null
render = rg.load_render()
Hr, Wr = render.shape[:2]
Lr = render @ np.array([0.299, 0.587, 0.114])
hpr = Lr - ndi.gaussian_filter(Lr, 4.0)
hpr = ndi.gaussian_filter(hpr, 0.5).astype(np.float32)
Z = np.load(rg.WORK + "libs.npz")
faces = {}
for name in ("matte", "raw"):
    for k in range(int(Z[name + "_n"])):
        i, j, vis = (int(v) for v in Z["%s_%d_id" % (name, k)])
        if vis >= 95:
            faces[(i, j)] = name
feats = {(f["i"], f["j"]): f for f in json.load(open(rg.WORK + "render_faces_raw.json"))}
yy, xx = np.mgrid[0:Hr, 0:Wr].astype(np.float64)
ok = np.zeros((Hr, Wr), bool)
owner = np.zeros((Hr, Wr), np.int16)
names = {}
for n, ((i, j), name) in enumerate(sorted(faces.items()), start=1):
    f = feats[(i, j)]
    d = rg.hex_dist(xx, yy, f["cx"], f["cy"])
    m = d < 0.90
    ok |= m
    owner[m] = n
    names[n] = (i, j, name)
ok = ndi.binary_erosion(ok, structure=np.ones((3, 3), bool), iterations=2)
Vs = np.roll(ndi.uniform_filter(ok.astype(np.float32), PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1)) > 0.9999
hpr = np.where(ok, hpr, 0).astype(np.float32)
shape = (sfft.next_fast_len(Hr + PS), sfft.next_fast_len(Wr + PS))
F = sfft.rfft2(hpr, s=shape, workers=-1)
m1 = np.roll(ndi.uniform_filter(hpr, PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1))
m2 = np.roll(ndi.uniform_filter(hpr * hpr, PS, mode="constant"), (-PS // 2, -PS // 2), axis=(0, 1))
sigma = np.ones(shape, np.float32)
sigma[:Hr, :Wr] = np.sqrt(np.maximum(m2 - m1 * m1, 1e-6))
valid = np.zeros(shape, bool)
valid[:Hr - PS + 1, :Wr - PS + 1] = Vs[:Hr - PS + 1, :Wr - PS + 1]
print("render null: windows", int(valid.sum()), "faces", len(names))

by_face = {}
for (y, x) in np.argwhere(Vs):
    by_face.setdefault(int(owner[min(y + PS // 2, Hr - 1), min(x + PS // 2, Wr - 1)]), []).append((int(y), int(x)))
res = []
EXC = PS + 16
for n, lst in sorted(by_face.items()):
    if n == 0:
        continue
    cnt = 4 if names[n][2] == "matte" else 6
    for k in rng.choice(len(lst), size=min(cnt, len(lst)), replace=False):
        y0, x0 = lst[int(k)]
        patch = hpr[y0:y0 + PS, x0:x0 + PS]
        best = -2.0
        near = (np.abs(np.arange(shape[0])[:, None] - y0) < EXC) & (np.abs(np.arange(shape[1])[None, :] - x0) < EXC)
        for t in range(8):
            p = dihedral(patch, t)
            p = p - p.mean()
            pad = np.zeros(shape, np.float32)
            pad[:PS, :PS] = p
            c = sfft.irfft2(F * np.conj(sfft.rfft2(pad, workers=-1)), s=shape, workers=-1)
            ncc = c / (PS * PS * sigma * p.std() + 1e-9)
            ncc[~valid | near] = -1
            best = max(best, float(ncc.max()))
        res.append(dict(face=names[n][:2], type=names[n][2], max_ncc=best))
mx = np.array([r["max_ncc"] for r in res])
mxm = np.array([r["max_ncc"] for r in res if r["type"] == "matte"])
mxr = np.array([r["max_ncc"] for r in res if r["type"] == "raw"])
null = dict(n_patches=len(res), n_windows=int(valid.sum()), patch_size_in=PS / rg.PX_PER_IN, max_ncc=float(mx.max()), p99=float(np.percentile(mx, 99)), median=float(np.median(mx)),
            mean=float(mx.mean()), count_over_0_30=int((mx > 0.30).sum()), count_over_0_40=int((mx > 0.40).sum()), count_over_0_50=int((mx > 0.50).sum()),
            matte=dict(n=len(mxm), max=float(mxm.max()), median=float(np.median(mxm)), over_0_40=int((mxm > 0.40).sum())),
            raw=dict(n=len(mxr), max=float(mxr.max()), median=float(np.median(mxr)), over_0_40=int((mxr > 0.40).sum())))
print("render null", json.dumps(null))

# ---- B. top atlas matches at full resolution, fine and coarse bands
rs = json.load(open(rg.WORK + "repeat_search.json"))
top = sorted(rs["patches"], key=lambda r: -r["max_ncc"])[:8]
color = np.asarray(Image.open(TEX + "Color.png").convert("RGB")).astype(np.float32)
lum = color @ np.array([0.299, 0.587, 0.114], np.float32)
Ha, Wa = lum.shape
band_fine = ndi.gaussian_filter(lum, 1.0, mode="wrap") - ndi.gaussian_filter(lum, 3.0, mode="wrap")
band_coarse = ndi.gaussian_filter(lum, 8.0, mode="wrap") - ndi.gaussian_filter(lum, 24.0, mode="wrap")
S = 128
sheet = Image.new("RGB", (4 * 192, 4 * 192), (255, 255, 255))
rows = []


def win(a, y, x):
    return a[np.ix_(np.arange(y, y + S) % Ha, np.arange(x, x + S) % Wa)]


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


for n, r in enumerate(top):
    y0, x0 = (2 * v for v in r["start_half_res"])
    my, mx_ = (2 * v for v in r["match"]["at_start_px_half_res"])
    t = r["match"]["transform"]
    entry = dict(face=r["face"], matched_face=r["match"]["matched_face"], transform=t, ncc_half_res_search=r["max_ncc"])
    for nm, arr in (("fine", band_fine), ("coarse", band_coarse)):
        entry["ncc_" + nm + "_band"] = ncc(dihedral(win(arr, y0, x0), t), win(arr, my, mx_))
    ip = dihedral(win(lum, y0, x0), t)
    im = win(lum, my, mx_)
    both = np.concatenate([ip, im])
    lo, hi = np.percentile(both, 1), np.percentile(both, 99)
    tiles = [np.clip((a - lo) / (hi - lo + 1e-6) * 255, 0, 255).astype(np.uint8) for a in (ip, im)]
    for q, tile in enumerate(tiles):
        img = Image.fromarray(tile).resize((192, 192), Image.LANCZOS).convert("RGB")
        d = ImageDraw.Draw(img)
        d.text((4, 4), "%s f%d fine %.2f" % (("patch" if q == 0 else "match"), r["face"] if q == 0 else r["match"]["matched_face"], entry["ncc_fine_band"]) if q == 0 else "match f%d" % r["match"]["matched_face"], fill=(255, 0, 0))
        sheet.paste(img, (((n % 2) * 2 + q) * 192, (n // 2) * 192))
    rows.append(entry)
    print(entry)
guard.save_image(sheet, TEX + "_REVIEW_repeat_top_matches.jpg", quality=92)
json.dump(dict(render_null=null, top_atlas_matches=rows), open(guard.safe(rg.WORK + "repeat_null.json"), "w"), indent=1)
print("done")
