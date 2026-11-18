"""Phase 14: when does direct sun reach the deck floor? For each frame, the mean scene brightness of a patch of deck floor
(pixel brightness made linear and multiplied back by the exposure that frame used), printed against the clock time.
Usage: python -B sun_on_floor.py <deck> <day>"""
import sys, os, json
import numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROI = {"reardeck": (680, 920, 1440, 1040), "roofdeck": (760, 900, 1160, 1010)}  # x0, y0, x1, y1 on a 1920 by 1080 frame


def ev_for(h):
    steps = [(-5.0, 6.0), (0.0, 7.5), (5.0, 10.0), (10.0, 12.0), (15.0, 13.2), (25.0, 14.644)]
    if h <= steps[0][0]:
        return steps[0][1]
    for (h0, e0), (h1, e1) in zip(steps, steps[1:]):
        if h <= h1:
            return e0 + (e1 - e0) * (h - h0) / (h1 - h0)
    return steps[-1][1]


def main(deck, day, folder=None):
    folder = folder or "%s/frames/%s_%s" % (OUT, deck, day)
    rows = [json.loads(l) for l in open(folder + "/frames_log.jsonl")]
    by = {r[0]: r for r in rows}
    meta = json.load(open(folder + "/meta.json"))
    zone = meta["date"]["zone"]
    values = []
    for i in range(240):
        if i not in by:
            continue
        h, bearing, height = by[i][1], by[i][2], by[i][3]
        a = np.asarray(Image.open("%s/f%03d.png" % (folder, i)).convert("RGB").crop(ROI[deck]), dtype=np.float64) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        lum = (0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]).mean()
        values.append((i, h, height, lum * 2.0 ** ev_for(height)))
    scene = np.array([v[3] for v in values])
    print("deck %s day %s: floor brightness (scene units) min %.1f max %.1f" % (deck, day, scene.min(), scene.max()))
    def clock(h):
        t = int(round(h * 60))
        return "%02d:%02d %s" % (t // 60, t % 60, zone)
    for i, h, height, v in values[::8]:
        print("  f%03d %s sun height %5.1f  floor %8.1f" % (i, clock(h), height, v))
    print("sudden changes (frame to frame more than 1.6 times up or down; sun reaches or leaves the floor patch):")
    for (i0, h0, _, v0), (i1, h1, _, v1) in zip(values, values[1:]):
        if i1 == i0 + 1 and (v1 > 1.6 * v0 or v1 < v0 / 1.6):
            print("  between f%03d (%s) and f%03d (%s): %.0f -> %.0f" % (i0, clock(h0), i1, clock(h1), v0, v1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
