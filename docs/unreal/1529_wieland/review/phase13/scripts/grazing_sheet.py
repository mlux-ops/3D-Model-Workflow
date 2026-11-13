"""Phase 13: sheet of the grazing-light check (grazing left, review sun right) with a detail figure per picture:
the spread of fine brightness changes (picture minus a 6-pixel blur) over the middle half of the frame, divided by
its mean brightness, the same kind of figure as Phase 12's swatch test (pass at 0.010 or more under grazing light).
Usage, from the plan folder: python -B review/phase13/scripts/grazing_sheet.py"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = "review/phase13/grazing"
NAMES = ["wells_red_brick", "wells_dark_brick", "west_dark_bay", "green_roof", "penthouse_metal"]
font = ImageFont.truetype("arial.ttf", 22)


def detail(img):
    g = img.convert("L")
    w, h = g.size
    g = g.crop((w // 4, h // 4, 3 * w // 4, 3 * h // 4))
    a = np.asarray(g, dtype=float)
    b = np.asarray(g.filter(ImageFilter.GaussianBlur(6)), dtype=float)
    return float((a - b).std() / max(1.0, a.mean()))


rows, out = [], {}
for n in NAMES:
    pair = [Image.open("%s/%s_%s.png" % (BASE, n, k)).convert("RGB") for k in ("grazing", "review")]
    vals = [detail(p) for p in pair]
    out[n] = {"grazing": round(vals[0], 4), "review": round(vals[1], 4), "passes": vals[0] >= 0.010}
    rows.append((n, [p.resize((960, 540), Image.LANCZOS) for p in pair], vals))
page = Image.new("RGB", (1940, len(rows) * 590 + 60), "white")
d = ImageDraw.Draw(page)
for i, (n, pics, vals) in enumerate(rows):
    y = 10 + i * 590
    d.text((10, y), "%s: grazing sun 8 degrees, exposure EV 11.5 (left, detail %.3f) | review sun 15 Aug 15:30 (right, detail %.3f)" % (n, vals[0], vals[1]),
           fill="black", font=font)
    page.paste(pics[0], (10, y + 35))
    page.paste(pics[1], (975, y + 35))
d.text((10, len(rows) * 590 + 20), "PROPOSED hotel, modelled from published renderings and records, not a survey. Editor viewport, real-time renderer.",
       fill=(160, 0, 0), font=font)
page.save(BASE + "/grazing_sheet.jpg", quality=85)
json.dump(out, open(BASE + "/grazing_detail.json", "w"), indent=1)
print(json.dumps(out, indent=1))
