"""Check whether the render reuses identical face textures: pairwise NCC of high-passed luminance between faces of one type, over 60-degree rotations and mirrors."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import guard
import render_grid as rg

im = rg.load_render()
H, W = im.shape[:2]
L = im @ np.array([0.299, 0.587, 0.114])
hp = L - ndi.gaussian_filter(L, 5.0)
pad = 230
hpp = np.pad(hp, pad, mode="constant")
yy, xx = np.mgrid[0:H + 2 * pad, 0:W + 2 * pad].astype(np.float64)
yy -= pad
xx -= pad
feats = json.load(open(rg.WORK + "render_faces_raw.json"))


def ftype(f):
    if f["hf"] > 4.5:
        return "chiseled"
    if f["hf"] >= 1.6 or f["coh"] >= 0.1:
        return "raw" if f["coh"] > 0.2 else "matte"
    return "matte"


R = 150  # analysis radius (px), inside the face (face inradius ~155)
n = 2 * R + 1
gy, gx = np.mgrid[-R:R + 1, -R:R + 1]
disc = (gx ** 2 + gy ** 2) <= R ** 2


def patch(f, dx=0.0, dy=0.0):
    cx, cy = f["cx"] + dx, f["cy"] + dy
    x0, y0 = int(round(cx)) + pad - R, int(round(cy)) + pad - R
    return hpp[y0:y0 + n, x0:x0 + n]


def transforms(a):
    out = []
    for m in (False, True):
        b = a[:, ::-1] if m else a
        for k in range(4):
            out.append((90 * k, m, np.rot90(b, k)))
    return out


def ncc(a, b):
    a = a[disc]
    b = b[disc]
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-12))


res = {}
for typ in ("raw", "matte", "chiseled"):
    fs = [f for f in feats if ftype(f) == typ and f["visfrac"] > 0.95]
    print(typ, "complete faces", len(fs))
    best = []
    for a in range(len(fs)):
        for b in range(a + 1, len(fs)):
            A = patch(fs[a])
            bestv = (-2, None)
            for (rot, m, Bt) in transforms(patch(fs[b])):
                # small shift search +-3 px via cross-correlation at few offsets
                for sy in (-2, 0, 2):
                    for sx in (-2, 0, 2):
                        Bs = np.roll(Bt, (sy, sx), axis=(0, 1))
                        v = ncc(A, Bs)
                        if v > bestv[0]:
                            bestv = (v, (rot, m, sy, sx))
            best.append((bestv[0], (fs[a]["i"], fs[a]["j"]), (fs[b]["i"], fs[b]["j"]), bestv[1]))
    best.sort(key=lambda t: -t[0])
    print(" top pairs (ncc, faceA, faceB, (rot90, mirror, shift)):")
    for t in best[:6]:
        print("  %.3f %s %s %s" % t)
    vals = np.array([t[0] for t in best])
    print(" ncc over %d pairs: mean %.3f  median %.3f  max %.3f" % (len(vals), vals.mean(), np.median(vals), vals.max()))
    res[typ] = dict(pairs=len(vals), mean=float(vals.mean()), median=float(np.median(vals)), max=float(vals.max()), top=[[float(t[0]), list(t[1]), list(t[2]), list(map(lambda v: v if not isinstance(v, (bool, np.bool_)) else bool(v), t[3]))] for t in best[:6]])
json.dump(res, open(guard.safe(rg.WORK + "source_copy_check.json"), "w"), indent=1)
