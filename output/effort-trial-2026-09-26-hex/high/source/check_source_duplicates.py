"""Check whether the render's faces of one type are copies of each other (CG artwork
often reuses one texture). For every ordered pair (A, B) of same-type faces, a central
square window of A (high-passed luminance) is searched for in B under all 12 hexagon
dihedral transforms with FFT normalised cross-correlation. Near-1 peaks = duplicates.
Writes source/data/source_duplicate_check.json.
"""

import json

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve

import render_geom as g
from common import RENDER_PATH, out_path

img = np.asarray(Image.open(RENDER_PATH).convert("RGB")).astype(np.float64) / 255.0
L = img @ np.array([0.2126, 0.7152, 0.0722])
hp = L - ndimage.gaussian_filter(L, 4.0)
metrics = json.load(open(out_path("source", "data", "render_face_metrics.json")))


def face_type(r):
    if r["coherence"] > 0.6:
        return "chiseled"
    if r["hp_std"] > 0.0105:
        return "raw"
    return "matte"


def local(cx, cy, rot_deg, mirror, half=120):
    """Face-local square of side 2*half render px, rotated/mirrored about the centre."""
    yy, xx = np.mgrid[-half:half, -half:half].astype(np.float64)
    if mirror:
        xx = -xx
    t = np.radians(rot_deg)
    sx = cx + xx * np.cos(t) - yy * np.sin(t)
    sy = cy + xx * np.sin(t) + yy * np.cos(t)
    return ndimage.map_coordinates(hp, [sy, sx], order=1)


def ncc_max(tpl, img_):
    tpl = tpl - tpl.mean()
    n = tpl.size
    num = fftconvolve(img_, tpl[::-1, ::-1], mode="valid")
    s1 = fftconvolve(img_, np.ones_like(tpl), mode="valid")
    s2 = fftconvolve(img_ ** 2, np.ones_like(tpl), mode="valid")
    den = np.sqrt(np.maximum(s2 - s1 ** 2 / n, 1e-12)) * np.sqrt((tpl ** 2).sum())
    return float((num / den).max())


out = {}
for typ in ("raw", "matte", "chiseled"):
    ids = [r["render_id"] for r in metrics if face_type(r) == typ]
    res = []
    for a in ids:
        ca = metrics[a]["centre_xy"]
        tpl = local(ca[0], ca[1], 0, False, half=45)
        best = []
        for b in ids:
            if b == a:
                continue
            cb = metrics[b]["centre_xy"]
            m = 0.0
            for rot in range(0, 360, 60):
                for mir in (False, True):
                    m = max(m, ncc_max(tpl, local(cb[0], cb[1], rot, mir, half=130)))
            best.append((round(m, 3), b))
        best.sort(reverse=True)
        res.append({"face": a, "top_matches": best[:3]})
        print(typ, a, best[:3], flush=True)
    out[typ] = res
json.dump(out, open(out_path("source", "data", "source_duplicate_check.json"), "w"), indent=1)
