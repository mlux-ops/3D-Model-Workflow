"""Diagnostic: 1:1 crops (enlarged 2x, contrast-stretched) of chosen render cells side by side."""
import os
import sys
import json
import numpy as np
from PIL import Image
from guard import inp, save_image, WORK_DIR

R = np.asarray(Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")).astype(np.float64)
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
cells = {"%d,%d" % (c["j"], c["k"]): c for c in L["cells"]}
names = sys.argv[1].split(";")
out = sys.argv[2]
half = int(sys.argv[3]) if len(sys.argv) > 3 else 100
zoom = int(sys.argv[4]) if len(sys.argv) > 4 else 2
ims = []
for n in names:
    c = cells[n]
    cx, cy = int(round(c["cx"])), int(round(c["cy"]))
    p = R[cy - half:cy + half, cx - half:cx + half]
    # stretch around the face mean so relief is visible
    m = p.reshape(-1, 3).mean(axis=0)
    p = np.clip(m + (p - m) * 3.0, 0, 255).astype(np.uint8)
    im = Image.fromarray(p).resize((2 * half * zoom, 2 * half * zoom), Image.NEAREST)
    ims.append(im)
sheet = Image.new("RGB", (sum(i.width for i in ims) + 6 * (len(ims) - 1), ims[0].height), (255, 0, 0))
x = 0
for i in ims:
    sheet.paste(i, (x, 0))
    x += i.width + 6
save_image(sheet, os.path.join(WORK_DIR, out), quality=92)
print(sheet.size)
