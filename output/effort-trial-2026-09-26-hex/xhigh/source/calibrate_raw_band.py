"""Choose the render-luminance band used as relief for Raw (and Matte) so the relief's feature
scale under raking light matches the lifestyle image.

Measure: spectral centroid (cycles/mm) of band-passed luminance inside lifestyle face boxes
(~49 px/in). Candidate recipes: heights from render source faces (Yres) with different band
weights, upsampled to 64 px/in, shaded from the left at 30 deg, resampled to 49 px/in, same
measure. Writes _work/raw_band_calibration.json.
"""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import common as C
from guard import inp, WORK_DIR, write_text
from shading import shade

LS = np.asarray(Image.open(inp("elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")).astype(np.float64)
lum_ls = LS @ np.array([0.2126, 0.7152, 0.0722])
LS_PPI = 49.0
P = np.load(os.path.join(WORK_DIR, "pools.npz"))
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
INFO = json.load(open(os.path.join(WORK_DIR, "pools.json")))
RPXIN = L["px_per_in"]
Yres = (P["resid"] @ np.array([0.2126, 0.7152, 0.0722], np.float32)).astype(np.float64)
cells = {"%d,%d" % (c["j"], c["k"]): c for c in L["cells"]}


def centroid(p, ppi):
    p = p - ndi.gaussian_filter(p, 12.0 * ppi / 49.0)
    p = p[8:-8, 8:-8]
    n = min(p.shape)
    p = p[:n, :n] * np.outer(np.hanning(n), np.hanning(n))
    F = np.abs(np.fft.fftshift(np.fft.fft2(p))) ** 2
    fy, fx = np.meshgrid(np.fft.fftshift(np.fft.fftfreq(n)), np.fft.fftshift(np.fft.fftfreq(n)), indexing="ij")
    f_mm = np.hypot(fx, fy) * ppi / 25.4                     # cycles per mm
    band = (f_mm > 0.04) & (f_mm < 0.45)
    return float((F[band] * f_mm[band]).sum() / F[band].sum())


ls_boxes = {"raw": [(110, 380, 196), (130, 420, 150)], "matte": [(400, 150, 196), (420, 120, 150)]}
ls_c = {k: float(np.mean([centroid(lum_ls[y:y + s, x:x + s], LS_PPI) for x, y, s in b])) for k, b in ls_boxes.items()}
print("lifestyle centroid cyc/mm", {k: round(v, 4) for k, v in ls_c.items()})

recipes = {"band 0.7-18 (current raw)": [(0.7, 18.0, 1.0)],
           "band 0.7-6 (current matte)": [(0.7, 6.0, 1.0)],
           "0.7-5 + 0.35 x 5-18": [(0.7, 5.0, 1.0), (5.0, 18.0, 0.35)],
           "0.7-4 + 0.25 x 4-18": [(0.7, 4.0, 1.0), (4.0, 18.0, 0.25)],
           "0.7-3": [(0.7, 3.0, 1.0)],
           "0.5-3": [(0.5, 3.0, 1.0)],
           "0.7-2.5": [(0.7, 2.5, 1.0)],
           "0.5-3 + 0.3 x 3-12": [(0.5, 3.0, 1.0), (3.0, 12.0, 0.3)],
           "0.5-3 + 0.2 x 3-18": [(0.5, 3.0, 1.0), (3.0, 18.0, 0.2)],
           "0.4-3": [(0.4, 3.0, 1.0)]}
out = {"lifestyle": ls_c, "raw": {}, "matte": {}}
for kind in ("raw", "matte"):
    ks = [k for k, t in INFO["types"].items() if t == kind and k in cells and cells[k]["full"]][:4]
    for name, rec in recipes.items():
        cs = []
        for k in ks:
            c = cells[k]
            cx, cy = int(round(c["cx"])), int(round(c["cy"]))
            y = Yres[cy - 70:cy + 70, cx - 70:cx + 70]
            h = sum(w * (ndi.gaussian_filter(y, a) - ndi.gaussian_filter(y, b)) for a, b, w in rec)
            hu = ndi.zoom(h, C.PX_PER_IN / RPXIN, order=3)
            hu = hu / hu.std() * (0.275 if kind == "raw" else 0.015)
            s = shade(hu, 30.0, 180.0, shadows=True)
            g = ndi.zoom(s, LS_PPI / C.PX_PER_IN, order=1)
            cs.append(centroid(g, LS_PPI))
        out[kind][name] = float(np.mean(cs))
        print("%-5s %-28s centroid %.4f cyc/mm (lifestyle %.4f)" % (kind, name, np.mean(cs), ls_c[kind]))
write_text(os.path.join(WORK_DIR, "raw_band_calibration.json"), json.dumps(out, indent=1))
