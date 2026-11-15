"""Phase 20: side-by-side sheets of the Phase 17 and Phase 20 stills of the same views, and the panoramas.

Usage: python -B -P phase20_compare_sheets.py <tier realtime|pathtraced> <view> [<view> ...]
       python -B -P phase20_compare_sheets.py panorama <deck D1S|D1>

Left: Phase 17 (review/phase17/stills, or review/phase17/panorama/final). Right: Phase 20 (review/phase20/...).
Both 1,600 px wide (panoramas: one above the other, 3,200 px wide). Prints the share of pixels whose brightness changed
by more than 10 levels (of 255): the same tier, the same light and the same camera, so it shows where the materials
changed.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def changed(a, b):
    a = np.asarray(a.convert("L"), np.int16)
    b = np.asarray(b.convert("L").resize((a.shape[1], a.shape[0])), np.int16)
    return round(float((np.abs(a - b) > 10).mean()), 3)


def main(argv):
    out = {}
    if argv[1] == "panorama":
        deck = argv[2]
        a = Image.open(os.path.join(DOCS, "review", "phase17", "panorama", "final", "%s_panorama_sheet_final.png" % deck)).convert("RGB")
        b = Image.open(os.path.join(DOCS, "review", "phase20", "panorama", "%s_panorama_sheet_p20.png" % deck)).convert("RGB")
        w = 3200
        a = a.resize((w, int(a.height * w / a.width)))
        b = b.resize((w, int(b.height * w / b.width)))
        s = Image.new("RGB", (w, a.height + b.height + 60), "white")
        d = ImageDraw.Draw(s)
        d.text((8, 6), "%s Phase 17 (materials by type and research)" % deck, fill="black")
        s.paste(a, (0, 30))
        d.text((8, a.height + 36), "%s Phase 20 (materials refined from photographs)" % deck, fill="black")
        s.paste(b, (0, a.height + 60))
        s.save(os.path.join(DOCS, "review", "phase20", "panorama", "compare_%s_p17_p20.jpg" % deck), quality=85)
        out[deck] = changed(a, b)
    else:
        tier = argv[1]
        for view in argv[2:]:
            a = Image.open(os.path.join(DOCS, "review", "phase17", "stills", "%s_%s.0000.png" % (view, tier))).convert("RGB")
            b = Image.open(os.path.join(DOCS, "review", "phase20", "stills", "%s_%s.0000.png" % (view, tier))).convert("RGB")
            a.thumbnail((1600, 1600))
            b.thumbnail((1600, 1600))
            s = Image.new("RGB", (a.width + b.width, a.height + 30), "white")
            d = ImageDraw.Draw(s)
            d.text((8, 6), "%s Phase 17 %s" % (view, tier), fill="black")
            d.text((a.width + 8, 6), "%s Phase 20 %s (materials refined from photographs)" % (view, tier), fill="black")
            s.paste(a, (0, 30))
            s.paste(b, (a.width, 30))
            s.save(os.path.join(DOCS, "review", "phase20", "stills", "compare_%s_%s.jpg" % (view, tier)), quality=85)
            out[view] = changed(a, b)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
