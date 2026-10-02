import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import guard

W = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/xhigh/work/thumbs/"

for name, tag in (("elm_formed_hex_sand_layout_render.webp", "render"), ("elm_formed_hex_sand_lifestyle_angled.webp", "life")):
    im = Image.open(guard.inp(name)).convert("RGB")
    print(name, im.size)
    im.save(guard.safe(W + tag + "_full.png"))
    t = im.copy()
    t.thumbnail((800, 800), Image.LANCZOS)
    guard.save_image(t, W + tag + "_800.png")
    if tag == "render":
        w, h = im.size
        # four 1000x944 quadrants, shown at 800 wide
        for qi, (x0, y0) in enumerate(((0, 0), (w // 2, 0), (0, h // 2), (w // 2, h // 2))):
            q = im.crop((x0, y0, x0 + w // 2, y0 + h // 2))
            q.thumbnail((800, 800), Image.LANCZOS)
            guard.save_image(q, W + "render_q%d.png" % qi)
