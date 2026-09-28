"""Diagnostic: lifestyle face crops next to the atlas shaded from the left at the lifestyle's scale
(~49 px/in), same physical size, for Raw, vertical Chiseled and Matte. Writes _work/view_ls_compare.jpg."""
import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import common as C
from guard import inp, TEX_DIR, WORK_DIR, save_image
from shading import shade, tone

elev = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
LS = Image.open(inp("elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")
col = np.asarray(Image.open(os.path.join(TEX_DIR, "Color.png")).convert("RGB")).astype(np.float64)
bump = np.asarray(Image.open(os.path.join(TEX_DIR, "Bump16.png"))).astype(np.float64)
rep = json.load(open(os.path.join(TEX_DIR, "report.json")))
enc = rep["bump_encoding"]
hmm = enc["black_mm"] + bump / 65535.0 * (enc["white_mm"] - enc["black_mm"])
cen = C.face_centres()
SZ = 196                                       # 4 in at 49 px/in
boxes = {"raw": (110, 380), "chiseled_vertical": (660, 250), "matte": (400, 150)}
pick = {"raw": [f for f in rep["faces"] if f["type"] == "raw"][2],
        "chiseled_vertical": [f for f in rep["faces"] if f.get("groove_angle_image_deg") == 90][1],
        "matte": [f for f in rep["faces"] if f["type"] == "matte"][3]}
rows = []
for k, (x0, y0) in boxes.items():
    a = LS.crop((x0, y0, x0 + SZ, y0 + SZ))
    f = pick[k]
    cx, cy = cen[f["index"] - 1]
    half = 128
    ys = (np.arange(-half, half) + int(cy)) % C.H
    xs = (np.arange(-half, half) + int(cx)) % C.W
    hh, cc = hmm[np.ix_(ys, xs)], col[np.ix_(ys, xs)]
    s = shade(hh, elev, 180.0, shadows=True)
    g = Image.fromarray(tone(cc, s, amb=0.35)).resize((SZ, SZ), Image.LANCZOS)
    rows.append((k, a, g))
sheet = Image.new("RGB", (2 * SZ + 30, len(rows) * (SZ + 22) + 8), (255, 255, 255))
d = ImageDraw.Draw(sheet)
for i, (k, a, g) in enumerate(rows):
    y = 4 + i * (SZ + 22)
    d.text((4, y), "%s: lifestyle | atlas, light from left %.0f deg" % (k, elev), fill=(0, 0, 0))
    sheet.paste(a, (0, y + 16))
    sheet.paste(g, (SZ + 30, y + 16))
sheet = sheet.resize((sheet.width * 3 // 2, sheet.height * 3 // 2), Image.LANCZOS)
save_image(sheet, os.path.join(WORK_DIR, "view_ls_compare.jpg"), quality=92)
print(sheet.size)
