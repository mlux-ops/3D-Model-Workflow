"""Relief-contrast calibration: relative high-pass luminance contrast of each face type
under raking light, in the lifestyle image vs the atlas grazing-light render.

Lifestyle windows (tile face only, no props or cast plant shadow) were picked from 1:1
crops. The measure is std(Y - G(Y, s)) / mean(Y) in linear light, s = 0.25 in, which is
insensitive to the soft shadow gradients across the wall. The atlas measure uses the
same physical s (16 px at 64 px/in; lifestyle ~36 px/in -> 9 px).
"""

import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from common import lifestyle_rgb, srgb_to_lin, out_path
from b05_previews import grazing

LIFE_WINDOWS = {
    # name: (x0, y0, w, h) in lifestyle px; chosen on tile face away from props/plant
    "raw": [(400, 1160, 110, 110), (480, 1050, 110, 110)],
    "chiseled": [(680, 330, 140, 190), (700, 470, 120, 120)],
    "matte": [(457, 180, 100, 100), (457, 590, 100, 100)],
}


def rel_hp(Y, s):
    hp = Y - ndimage.gaussian_filter(Y, s)
    return float(hp.std() / Y.mean())


def main():
    L = srgb_to_lin(lifestyle_rgb())
    Y = 0.2126 * L[..., 0] + 0.7152 * L[..., 1] + 0.0722 * L[..., 2]
    out = {"lifestyle": {}, "atlas": {}}
    for t, wins in LIFE_WINDOWS.items():
        v = []
        for x0, y0, w, h in wins:
            v.append(rel_hp(Y[y0:y0 + h, x0:x0 + w], 9.0))
        out["lifestyle"][t] = float(np.mean(v))
    bf = json.load(open(out_path("_work", "build_faces.json")))
    col8 = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB"))
    b16 = np.asarray(Image.open(out_path("textures", "Bump16.png"))).astype(np.float64)
    fid = np.asarray(Image.open(out_path("textures", "face_ids.png"))).astype(np.int32)
    h_mm = b16 / 65535.0 * bf["params_mm"]["h_range"]
    for elev in (10.0, 15.0, 20.0):
        g = grazing(srgb_to_lin(col8.astype(np.float64)), h_mm, elev_deg=elev)
        Yg = 0.2126 * g[..., 0] + 0.7152 * g[..., 1] + 0.0722 * g[..., 2]
        hp = Yg - ndimage.gaussian_filter(Yg, 16.0)
        inner = ndimage.binary_erosion(fid > 0, iterations=40)
        res = {}
        for t in ("raw", "chiseled", "matte"):
            ids = [f["index"] for f in bf["faces"] if f["type"] == t]
            m = np.isin(fid, ids) & inner
            res[t] = float(hp[m].std() / Yg[m].mean())
        out["atlas"]["elev_%d" % int(elev)] = res
    print(json.dumps(out, indent=1))
    json.dump(out, open(out_path("_work", "contrast_calibration.json"), "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
