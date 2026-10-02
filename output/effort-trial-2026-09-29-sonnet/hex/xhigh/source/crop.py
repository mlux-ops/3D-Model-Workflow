"""crop.py src x0 y0 w h zoom out  -- crop from a source image (webp or png), zoom by integer, save <=800px review image."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import guard

src, x0, y0, w, h, zoom, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
path = guard.inp(src) if not os.path.isabs(src) and not os.path.exists(src) else src
im = Image.open(path).convert("RGB").crop((x0, y0, x0 + w, y0 + h))
if zoom != 1:
    im = im.resize((w * zoom, h * zoom), Image.LANCZOS)
assert im.size[0] <= 800 and im.size[1] <= 800, im.size
guard.save_image(im, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/xhigh/work/thumbs/" + out)
print(im.size)
