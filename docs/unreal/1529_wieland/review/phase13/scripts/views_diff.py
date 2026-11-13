"""Phase 13, step 13.6: which views change when the hotel is on. Runs outside the editor (needs Pillow, numpy).

For each view, the picture with "Existing buildings (as surveyed)" is compared with the picture with
"Duke of Wells (proposed)": share of pixels whose largest colour difference is over 40 of 255. Leaves that move
between frames and temporal noise change scattered pixels only, so a view counts as changed when the share is
over 0.5 % of the frame. Also writes one sheet per view: existing | proposed | changed pixels in red.
Usage, from the plan folder: python -B review/phase13/scripts/views_diff.py
Writes review/phase13/views/changes.csv and review/phase13/views/sheet_<view>.jpg.
"""
import csv
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = "review/phase13/views"
VIEWS = ["S1", "S2", "S3", "S4", "S5", "S6", "S8", "S9", "D1", "D2", "D3", "D4", "D5", "RD", "RP", "SY"]
THRESHOLD, SHARE = 40, 0.5
LABEL = ("PROPOSED hotel, modelled from published renderings and records, not a survey. Real-time renderer, "
         "Nanite ray tracing off. 1920 x 1080, summer afternoon review condition.")


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


rows = []
for view in VIEWS:
    a = np.asarray(Image.open(f"{BASE}/existing/{view}_realtime.0000.png").convert("RGB")).astype(np.int16)
    b = np.asarray(Image.open(f"{BASE}/proposed/{view}_realtime.0000.png").convert("RGB")).astype(np.int16)
    mask = np.abs(a - b).max(axis=2) > THRESHOLD
    share = 100.0 * mask.mean()
    rows.append({"view": view, "changed_pixels_percent": round(share, 2), "changes": share > SHARE})
    small = lambda arr: Image.fromarray(arr.astype(np.uint8)).resize((960, 540), Image.LANCZOS)
    overlay = (b * 0.45).astype(np.int16)
    overlay[mask] = [255, 0, 0]
    page = Image.new("RGB", (2900, 620), (255, 255, 255))
    for i, part in enumerate((a, b, overlay)):
        page.paste(small(part), (10 + i * 970, 40))
    draw = ImageDraw.Draw(page)
    draw.text((10, 8), f"{view}: existing buildings (left) | Duke of Wells proposed (middle) | changed pixels in red "
                       f"(right): {share:.2f} % of the frame", fill=(0, 0, 0), font=font(22))
    draw.text((10, 588), LABEL, fill=(160, 0, 0), font=font(18))
    page.save(f"{BASE}/sheet_{view}.jpg", quality=85)
with open(f"{BASE}/changes.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
for row in rows:
    print(row)
