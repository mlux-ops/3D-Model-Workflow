"""Diagnostic: measure the render's column centres directly from horizontal joint segments
and the slanted-joint offset versus the fitted lattice, to detect lattice drift."""
import os
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from guard import inp, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
lum = R @ np.array([0.2126, 0.7152, 0.0722])
dark = ndi.gaussian_filter(lum, 3.0) - lum            # thin dark line detector
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
y0, hf, x0, pitch, Rc = L["y0"], L["half_f"], L["x0"], L["col_pitch"], L["Rc"]

# 1. horizontal joint rows: segments of dark line; find their midpoints
mids = []
for k in range(11):
    yk = y0 + k * hf
    band = dark[int(round(yk)) - 2:int(round(yk)) + 3].max(axis=0)
    on = ndi.binary_closing(band > 2.5, iterations=3)
    lab, n = ndi.label(on)
    for s in ndi.find_objects(lab):
        a, b = s[0].start, s[0].stop
        if b - a > 0.6 * Rc and b - a < 1.3 * Rc:
            mids.append((k, (a + b - 1) / 2.0, b - a))
mids = np.array(mids)
# assign column index
j = np.round((mids[:, 1] - x0) / pitch)
A = np.vstack([np.ones(len(j)), j]).T
(cx0, cp), *_ = np.linalg.lstsq(A, mids[:, 1], rcond=None)
res = mids[:, 1] - (cx0 + cp * j)
print("segments %d; fitted column x0 %.2f pitch %.3f (lattice had %.2f / %.3f)" % (len(mids), cx0, cp, x0, pitch))
print("segment length median %.1f px (Rc model %.1f)" % (np.median(mids[:, 2]), Rc))
print("residual std %.2f px, max %.2f" % (res.std(), np.abs(res).max()))
for jj in sorted(set(j.astype(int))):
    sel = j == jj
    print("  col %2d: mean x %.1f  predicted(old) %.1f  predicted(new) %.1f" % (
        jj, mids[sel, 1].mean(), x0 + jj * pitch, cx0 + jj * cp))
