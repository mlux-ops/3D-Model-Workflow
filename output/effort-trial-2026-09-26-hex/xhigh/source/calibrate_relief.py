"""Relief calibration against the lifestyle image (diagnostic; informs the mm terms in build_maps.py).

The lifestyle photo/render shows Matte, Raw and Chiseled faces under one raking light from the left.
Band-passed luminance contrast (std / mean) inside hand-picked rectangles fully inside faces is
compared with the same measure on the atlas shaded from the left at several elevations, after
resampling the atlas to the lifestyle's ~49 px/in. Only contrast RATIOS between face types are
compared, because the lifestyle's light elevation and exposure are unknown.
"""
import os
import sys
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import common as C
from guard import inp, TEX_DIR, WORK_DIR, write_text
from shading import shade

LS = np.asarray(Image.open(inp("elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")).astype(np.float64)
lum_ls = LS @ np.array([0.2126, 0.7152, 0.0722])
LS_PPI = 49.0            # across-flats of the vertical-groove face spans ~490 px for 10 in


def contrast(lum, box, s_lo, s_hi):
    x0, y0, x1, y1 = box
    p = lum[y0:y1, x0:x1]
    bp = ndi.gaussian_filter(p, s_lo) - ndi.gaussian_filter(p, s_hi)
    m = 6
    return float(bp[m:-m, m:-m].std() / p.mean())


boxes = {"chiseled_vertical": (650, 200, 890, 600), "raw": (100, 360, 330, 620),
         "matte": (380, 100, 600, 400), "chiseled_diagonal": (660, 700, 880, 900)}
ls = {k: contrast(lum_ls, b, 0.7, 7.7) for k, b in boxes.items()}
print("lifestyle contrast", {k: round(v, 4) for k, v in ls.items()})
print("lifestyle ratios: chis_vert/raw %.2f  chis_diag/raw %.2f  matte/raw %.2f" % (
    ls["chiseled_vertical"] / ls["raw"], ls["chiseled_diagonal"] / ls["raw"], ls["matte"] / ls["raw"]))

col = np.asarray(Image.open(os.path.join(TEX_DIR, "Color.png")).convert("RGB")).astype(np.float64)
bump = np.asarray(Image.open(os.path.join(TEX_DIR, "Bump16.png"))).astype(np.float64)
rep = json.load(open(os.path.join(TEX_DIR, "report.json")))
enc = rep["bump_encoding"]
hmm = enc["black_mm"] + bump / 65535.0 * (enc["white_mm"] - enc["black_mm"])
cen = C.face_centres()
faces = rep["faces"]
pick = {"chiseled_vertical": [f for f in faces if f.get("groove_angle_image_deg") == 90],
        "chiseled_diagonal": [f for f in faces if f.get("groove_angle_image_deg") in (30, 150)],
        "raw": [f for f in faces if f["type"] == "raw"], "matte": [f for f in faces if f["type"] == "matte"][:8]}
sc = LS_PPI / C.PX_PER_IN
out = {"lifestyle": ls, "atlas": {}}
for elev in (15, 20, 30, 40):
    s = shade(hmm, elev, 180.0, shadows=True)
    lumA = (col @ np.array([0.2126, 0.7152, 0.0722])) * (0.28 + 0.72 * s)
    res = {}
    for k, fs in pick.items():
        vals = []
        for f in fs:
            cx, cy = cen[f["index"] - 1]
            half = 170
            ys = (np.arange(-half, half) + int(cy)) % C.H
            xs = (np.arange(-half, half) + int(cx)) % C.W
            p = ndi.zoom(lumA[np.ix_(ys, xs)], sc, order=1)
            vals.append(contrast(p, (0, 0, p.shape[1], p.shape[0]), 0.7, 7.7))
        res[k] = float(np.median(vals))
    out["atlas"][str(elev)] = res
    print("elev %2d: contrast %s | chis_vert/raw %.2f  chis_diag/raw %.2f  matte/raw %.2f" % (
        elev, {k: round(v, 4) for k, v in res.items()}, res["chiseled_vertical"] / res["raw"],
        res["chiseled_diagonal"] / res["raw"], res["matte"] / res["raw"]))
write_text(os.path.join(WORK_DIR, "relief_calibration.json"), json.dumps(out, indent=1))
