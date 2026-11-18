"""Phase 15: the two check sheets that have no Phase 12 counterpart. Reference pictures come from Phase 13 (git history,
commit 26b8b768, extracted to review/phase15/scratch/): its aerial with the hotel and its roof-deck sheet (existing / proposed).
Run from the plan folder: python -B review/phase15/scripts/sheets.py"""
from PIL import Image, ImageDraw, ImageFont
S = "review/phase15/"
try:
    font = ImageFont.truetype("arial.ttf", 26)
    small = ImageFont.truetype("arial.ttf", 22)
except OSError:
    font = small = ImageFont.load_default()
NOTE = "Real-time renderer, Nanite ray tracing off, summer afternoon review condition (15 August 15:30). Phase 15 check, 2026-11-13."

def sheet(panels, labels, out, note):
    H = 900
    ims = [p.resize((int(p.width * H / p.height), H)) for p in panels]
    W = sum(i.width for i in ims) + 10 * (len(ims) - 1)
    s = Image.new("RGB", (W, H + 80), "white")
    d = ImageDraw.Draw(s)
    x = 0
    for im, lab in zip(ims, labels):
        s.paste(im, (x, 40))
        d.text((x + 8, 8), lab, fill="black", font=font)
        x += im.width + 10
    d.text((8, H + 48), note, fill=(150, 0, 0), font=small)
    s.save(out, quality=88)

# Aerial: Phase 13's aerial with the hotel (its own camera, higher and nearer) and the Phase 15 aerial, with the two
# restored objects marked where their bounds project (SB_782868 at about 925, 652 and 1525 N. Wieland at about 944, 441
# on a 1920 x 1080 frame).
air = Image.open(S + "views/AIR_realtime.0000.png").convert("RGB").resize((1920, 1080))
d = ImageDraw.Draw(air)
for (cx, cy, w, h, text) in ((925, 652, 260, 230, "1520 N. Wells (survey block SB_782868), shown again"),
                             (944, 441, 120, 150, "1525 N. Wieland, shown again")):
    d.rectangle((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2), outline=(255, 220, 0), width=5)
    d.text((cx + w // 2 + 8, cy - 14), text, fill=(255, 220, 0), font=font)
m2 = Image.open(S + "scratch/p13_m2.png").convert("RGB")
sheet([m2, air], ["Phase 13 (withdrawn): hotel on, its own camera", "Phase 15: hotel removed, aerial from the south-east over Wells Street"],
      S + "sheet_AIR_hotel_removed.jpg", NOTE + " The two cameras differ; Phase 12 has no aerial view.")

# Roof deck: Phase 13's roof-deck sheet looking south (left: existing buildings, middle: with the hotel) and the Phase 15
# view from the same point looking east.
rd = Image.open(S + "scratch/p13_sheet_RD.jpg").convert("RGB")
existing = rd.crop((10, 40, 970, 580))
proposed = rd.crop((980, 40, 1940, 580))
rde = Image.open(S + "views/RDE_realtime.0000.png").convert("RGB")
sheet([existing, proposed, rde], ["Phase 13, looking south: existing buildings", "Phase 13, looking south: with the hotel (withdrawn)",
                                  "Phase 15: hotel removed, roof deck looking east over the rear"],
      S + "sheet_RDE_hotel_removed.jpg", NOTE + " Phase 12 has no roof-deck view looking east; its D1 (south-east) is compared in sheet_D1_vs_phase12_realtime.jpg.")
print("ok")
