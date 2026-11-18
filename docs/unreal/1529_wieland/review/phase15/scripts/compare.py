"""Phase 15: side-by-side sheet and pixel difference of one new picture against a reference picture.
Usage: python -B compare.py <new png> <reference png> <out jpg> "<left label>" "<right label>" [--no-diff]
Prints the share of pixels changed by more than 40 of 255 on any channel (the threshold Phase 13 used) and the mean
absolute difference, when the two pictures have the same size."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
new_path, ref_path, out_path, left, right = sys.argv[1:6]
no_diff = "--no-diff" in sys.argv
a = Image.open(ref_path).convert("RGB")
b = Image.open(new_path).convert("RGB")
result = {}
if a.size == b.size and not no_diff:
    x = np.asarray(a, dtype=np.int16)
    y = np.asarray(b, dtype=np.int16)
    d = np.abs(x - y)
    changed = d.max(axis=2) > 40
    result = {"changed_pct": round(100.0 * changed.mean(), 2), "mean_abs": round(float(d.mean()), 2)}
    rows = np.where(changed.any(axis=1))[0]
    cols = np.where(changed.any(axis=0))[0]
    if len(rows):
        result["changed_box_px"] = [int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())]
W = 1600
def fit(im):
    return im.resize((W, int(im.height * W / im.width)))
a2, b2 = fit(a), fit(b)
panels = [a2, b2]
labels = [right, left]
if result:
    mask = Image.fromarray((np.abs(np.asarray(a, dtype=np.int16) - np.asarray(b, dtype=np.int16)).max(axis=2) > 40).astype(np.uint8) * 255)
    panels.append(fit(mask.convert("RGB")))
    labels.append("changed > 40/255: %.2f %%" % result["changed_pct"])
H = max(p.height for p in panels)
sheet = Image.new("RGB", (W * len(panels), H + 40), "white")
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("arial.ttf", 24)
except OSError:
    font = ImageFont.load_default()
for i, (p, lab) in enumerate(zip(panels, labels)):
    sheet.paste(p, (i * W, 40))
    draw.text((i * W + 10, 8), lab, fill="black", font=font)
sheet.save(out_path, quality=88)
print(result)
