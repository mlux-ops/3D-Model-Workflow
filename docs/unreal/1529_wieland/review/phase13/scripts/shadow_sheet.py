"""Phase 13, step 13.7: one sheet of the plan-view shadow pictures, existing (top row) and proposed (bottom row) at
09:00, 12:30 and 15:30 CDT on 15 August 2026, with the project lot outlined. Runs outside the editor.
Usage, from the plan folder: python -B review/phase13/scripts/shadow_sheet.py -> review/phase13/shadow/shadow_sheet.jpg"""
from PIL import Image, ImageDraw, ImageFont

BASE = "review/phase13/shadow"
TIMES = ["0900", "1230", "1530"]
W, H = 960, 540
try:
    F, f = ImageFont.truetype("arial.ttf", 24), ImageFont.truetype("arial.ttf", 18)
except OSError:
    F = f = ImageFont.load_default()
page = Image.new("RGB", (3 * W + 40, 2 * H + 150), (255, 255, 255))
d = ImageDraw.Draw(page)
d.text((10, 8), "Shadow of the proposed hotel on 1529 N. Wieland, 15 August 2026, plan view from 80 m (north up). "
       "Top: existing buildings. Bottom: Duke of Wells (proposed).", fill=(0, 0, 0), font=F)
for r, key in enumerate(("existing", "proposed")):
    for c, t in enumerate(TIMES):
        im = Image.open(f"{BASE}/{key}/S8_realtime_{t}.0000.png").convert("RGB").resize((W, H), Image.LANCZOS)
        x, y = 10 + c * (W + 10), 45 + r * (H + 10)
        page.paste(im, (x, y))
        d.rectangle([x, y, x + 260, y + 30], fill=(255, 255, 255))
        d.text((x + 6, y + 4), f"{key}, {t[:2]}:{t[2:]} CDT", fill=(0, 0, 0), font=f)
d.text((10, 2 * H + 70), "PROPOSED hotel, modelled from published renderings and records, not a survey. Real-time renderer, "
       "Nanite ray tracing off, fixed daylight exposure. Sun from the Sun Position plugin (41.910215, -87.635389).",
       fill=(160, 0, 0), font=f)
d.text((10, 2 * H + 100), "Line tests over the 639 outdoor points of the lot (review/phase13/shadow/shadow_traces.json): new shade from the hotel "
       "0.3 % at 09:00, 4.7 % at 12:00, 4.9 % at 13:00, 0.2 % at 15:30; roof-deck level at most 3.6 % (12:00).",
       fill=(0, 0, 0), font=f)
page.save(f"{BASE}/shadow_sheet.jpg", quality=85)
