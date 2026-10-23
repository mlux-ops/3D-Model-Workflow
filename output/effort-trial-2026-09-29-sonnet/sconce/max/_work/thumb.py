# -*- coding: utf-8 -*-
"""thumb.py <src> <out_name> [x0 y0 x1 y1] [--max 800] : crop (source px) and downscale so no side exceeds 800 px."""
import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe
from PIL import Image

args = sys.argv[1:]
mx = 800
if "--max" in args:
    i = args.index("--max")
    mx = min(800, int(args[i + 1]))
    del args[i:i + 2]
src, name = args[0], args[1]
im = Image.open(src).convert("RGB")
if len(args) >= 6:
    x0, y0, x1, y1 = [int(v) for v in args[2:6]]
    im = im.crop((x0, y0, x1, y1))
s = min(1.0, float(mx) / max(im.size))
if s < 1.0:
    im = im.resize((max(1, int(round(im.size[0] * s))), max(1, int(round(im.size[1] * s)))), Image.LANCZOS)
out = safe("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/_work/thumbs/" + name + ".png")
im.save(out)
print(out, im.size)
