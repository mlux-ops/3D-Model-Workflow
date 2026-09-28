"""Make <=800 px thumbnails and crops of the two inputs for visual inspection."""
import sys
import numpy as np
from PIL import Image
from guard import inp, save_image, WORK_DIR
import os

R = Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")
L = Image.open(inp("elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")
print("render", R.size, "lifestyle", L.size)


def thumb(img, name, maxw=800):
    im = img.copy()
    im.thumbnail((maxw, maxw), Image.LANCZOS)
    save_image(im, os.path.join(WORK_DIR, name), quality=92)
    print(name, im.size)


thumb(R, "render_thumb.jpg")
thumb(L, "lifestyle_thumb.jpg")

# quadrant crops of the render at half resolution (1000x944 -> each quadrant 500 wide)
w, h = R.size
for i, (x0, y0) in enumerate([(0, 0), (w // 2, 0), (0, h // 2), (w // 2, h // 2)]):
    c = R.crop((x0, y0, x0 + w // 2, y0 + h // 2))
    thumb(c, "render_q%d.jpg" % i)
