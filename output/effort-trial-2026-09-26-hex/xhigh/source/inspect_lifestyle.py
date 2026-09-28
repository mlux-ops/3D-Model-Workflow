"""Diagnostic crops of the lifestyle image at 1:1 (each <= 700 px)."""
import os
import numpy as np
from PIL import Image
from guard import inp, save_image, WORK_DIR

L = Image.open(inp("elm_formed_hex_sand_lifestyle_angled.webp")).convert("RGB")
print(L.size)
boxes = {"ls_tl": (0, 0, 700, 700), "ls_tr": (560, 0, 1000, 700), "ls_ml": (0, 600, 700, 1300),
         "ls_mr": (500, 600, 1000, 1300), "ls_bl": (200, 1100, 800, 1650)}
for n, b in boxes.items():
    save_image(L.crop(b), os.path.join(WORK_DIR, n + ".jpg"), quality=90)
