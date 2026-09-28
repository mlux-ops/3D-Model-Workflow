"""Step 1 analysis of the layout render: joint colour, joint mask, hex lattice.

Prints measurements; writes diagnostic crops to _work/.
"""
import os
import numpy as np
from PIL import Image
from guard import inp, save_image, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
H, W, _ = R.shape
lum = R @ np.array([0.2126, 0.7152, 0.0722])
chroma = R[..., 0] - R[..., 2]          # cream: R well above B; grey joint: small R-B
print("render", W, H)
print("R-B chroma percentiles", np.percentile(chroma, [0.5, 1, 2, 5, 25, 50, 75, 95, 99]))
print("lum percentiles", np.percentile(lum, [0.5, 1, 5, 25, 50, 75, 95, 99, 99.5]))

# joint candidates: low chroma
for thr in (20, 25, 30, 35):
    m = chroma < thr
    print("chroma<%d fraction %.4f" % (thr, m.mean()))

m = chroma < 30
rows = m.mean(axis=1)
cols = m.mean(axis=0)
# horizontal joint rows: row fraction peaks
idx = np.argsort(rows)[::-1][:60]
print("top rows by joint fraction:", sorted(idx.tolist()))
print("their fractions:", [round(rows[i], 3) for i in sorted(idx.tolist())])

# save a crop of joint mask at the top-left 800x800
crop = (m[:800, :800] * 255).astype(np.uint8)
save_image(Image.fromarray(crop), os.path.join(WORK_DIR, "render_jointmask_tl.png"))
# 1:1 crop of render around a joint crossing for colour sampling
save_image(Image.fromarray(R[250:650, 400:800].astype(np.uint8)), os.path.join(WORK_DIR, "render_crop_1to1_a.png"))
