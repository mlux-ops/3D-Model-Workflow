"""Step 6: objective checks on the delivered maps; results merged into textures/report.json
under "checks".

  * PNG header bytes (IHDR): width, height, bit depth, colour type
  * face_ids: values 0..56, joint width along column centre lines
  * repetition between faces of one type (Raw is the graded case; Matte and Chiseled are
    reported too): whole-face NCC over the 12 hexagon symmetries (60 deg rotations x
    mirror) on high-passed bump (Raw, Chiseled) or low-passed colour luminance (Matte
    clouds); and a random-window patch search: 64 x 64 px windows from each Raw face
    searched by FFT NCC in every other Raw face under all 12 symmetries.
"""

import json
import struct

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve

from common import W, H, atlas_centres, hexnorm, out_path

Image.MAX_IMAGE_PIXELS = None
RNG = np.random.default_rng(7)


def ihdr(path):
    with open(path, "rb") as f:
        head = f.read(33)
    assert head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR"
    w, h, depth, ctype = struct.unpack(">IIBB", head[16:26])
    return {"width": w, "height": h, "bit_depth": depth, "colour_type": ctype,
            "colour_type_name": {0: "greyscale", 2: "RGB", 3: "palette", 4: "grey+alpha", 6: "RGBA"}[ctype]}


checks = {"png_headers": {n: ihdr(out_path("textures", n)) for n in ("Color.png", "Bump16.png", "face_ids.png")}}
fid = np.asarray(Image.open(out_path("textures", "face_ids.png"))).astype(np.int32)
code = np.asarray(Image.open(out_path("textures", "Bump16.png"))).astype(np.float64)
col = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB")).astype(np.float64)
lum = col @ np.array([0.2126, 0.7152, 0.0722])
checks["face_ids"] = {"unique_values": int(len(np.unique(fid))), "min": int(fid.min()), "max": int(fid.max()),
                      "joint_fraction": float((fid == 0).mean())}
rep = json.load(open(out_path("textures", "report.json")))
ftype = {f["index"]: f["type"] for f in rep["faces"]}
cent = {i: (cx, cy) for i, _, _, cx, cy in atlas_centres()}

hp_bump = code - ndimage.gaussian_filter(code, 8.0, mode="wrap")
lp_lum = ndimage.gaussian_filter(lum, 6.0, mode="wrap") - ndimage.gaussian_filter(lum, 60.0, mode="wrap")
R = 300
yy, xx = np.mgrid[-R:R, -R:R].astype(np.float64)
inside = hexnorm(xx, yy) < 300


def local(field, idx, rot, mir):
    cx, cy = cent[idx]
    t = np.radians(rot)
    u = -xx if mir else xx
    x = cx + np.cos(t) * u - np.sin(t) * yy
    y = cy + np.sin(t) * u + np.cos(t) * yy
    return ndimage.map_coordinates(field, [np.mod(y, H), np.mod(x, W)], order=1, mode="grid-wrap")


def whole_face(field, typ):
    ids = [i for i in cent if ftype[i] == typ]
    base = {i: local(field, i, 0, False) for i in ids}
    worst = []
    for a_i, a in enumerate(ids):
        va = base[a][inside]
        va = (va - va.mean()) / (va.std() + 1e-9)
        for b in ids[a_i + 1:]:
            m = -1.0
            for rot in range(0, 360, 60):
                for mir in (False, True):
                    vb = local(field, b, rot, mir)[inside]
                    vb = (vb - vb.mean()) / (vb.std() + 1e-9)
                    m = max(m, float((va * vb).mean()))
            worst.append((m, a, b))
    worst.sort(reverse=True)
    return {"faces": len(ids), "max_ncc": worst[0][0], "max_pair": worst[0][1:], "top5": worst[:5],
            "median_pair_max_ncc": float(np.median([w[0] for w in worst]))}


checks["repetition_whole_face"] = {
    "raw_bump_highpass": whole_face(hp_bump, "raw"),
    "chiseled_bump_highpass": whole_face(hp_bump, "chiseled"),
    "matte_colour_lowfreq": whole_face(lp_lum, "matte"),
}
print(json.dumps(checks["repetition_whole_face"], indent=1), flush=True)


def ncc_search(tpl, img):
    tpl = tpl - tpl.mean()
    n = tpl.size
    num = fftconvolve(img, tpl[::-1, ::-1], mode="valid")
    ones = np.ones_like(tpl)
    s1 = fftconvolve(img, ones, mode="valid")
    s2 = fftconvolve(img ** 2, ones, mode="valid")
    den = np.sqrt(np.maximum(s2 - s1 ** 2 / n, 1e-9)) * np.sqrt((tpl ** 2).sum())
    return float((num / den).max())


def patch_search(field, typ, per_face=6, win=64):
    ids = [i for i in cent if ftype[i] == typ]
    loc = {(i, r, m): local(field, i, r, m) for i in ids for r in range(0, 360, 60) for m in (False, True)}
    res = []
    for a in ids:
        la = loc[(a, 0, False)]
        for _ in range(per_face):
            while True:
                x0, y0 = RNG.integers(0, 2 * R - win, 2)
                if hexnorm(x0 + win / 2 - R, y0 + win / 2 - R) < 300 - win * 0.75:
                    break
            tpl = la[y0:y0 + win, x0:x0 + win]
            best = (-1.0, None)
            for b in ids:
                if b == a:
                    continue
                for r in range(0, 360, 60):
                    for m in (False, True):
                        s = ncc_search(tpl, loc[(b, r, m)])
                        if s > best[0]:
                            best = (s, (b, r, m))
            res.append((best[0], a, best[1]))
    res.sort(key=lambda t: -t[0])
    return {"windows": len(res), "window_px": win, "max_ncc": res[0][0], "max_hit": [res[0][1], list(res[0][2])],
            "median_best_ncc": float(np.median([r[0] for r in res])),
            "count_over_0_6": int(sum(r[0] > 0.6 for r in res)), "top5": [[r[0], r[1], list(r[2])] for r in res[:5]]}


checks["repetition_patch_search"] = {"raw_bump_highpass": patch_search(hp_bump, "raw")}
print(json.dumps(checks["repetition_patch_search"], indent=1), flush=True)
rep["checks"] = checks
json.dump(rep, open(out_path("textures", "report.json"), "w"), indent=1, default=float)
print(json.dumps(checks["png_headers"], indent=1), json.dumps(checks["face_ids"]))
