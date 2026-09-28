"""Locate where one face's content sits inside a larger image (same print): position, orientation, scale.

For the query face, 9 templates (8 x 5 in) are matched over the target at 8 px/in, all 4 orientations
(r0, r180, flipH, flipV) and scales 0.90..1.10. The consensus orientation/scale is the one with the most
templates above NCC 0.5; each template's best location then gives the affine offset (query px -> target px).
Also reports how much of the target is covered by the located query box (the rest is new content).

Usage: python a04_locate.py            (runs the pairs listed in PAIRS)"""
import json

import numpy as np
from scipy.ndimage import zoom

from a03_dupes import FACES, T_PPI, load, ncc_map
from guard import out_path, ref
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
FACES.update({
    "w15_slab%d" % i: (ref("web/w15_ms_veincut_jute_48x110_panel.jpg"), (i * 1000 + 6, 4, i * 1000 + 994, 2282), 1,
                       2286 / 110.0) for i in range(4)})
FACES.update({"w12_panel": (ref("web/w12_ms_jute_veincut_panel_12x24.jpg"), None, 0, 25.0),
              "w14_top": (ref("web/w14_ms_jute_veincut_48x110_04.jpg"), (0, 0, 2039, 2330), 1, 2039 / 48.0)})
PAIRS = [("u09", "w14_48x110"), ("old05", "w14_48x110"), ("w05_r0half", "old05"), ("w05_r1half", "old05"),
         ("u09", "w15_slab0"), ("u09", "w15_slab1"), ("u09", "w15_slab2"), ("u09", "w15_slab3"),
         ("old05", "w15_slab0"), ("old05", "w15_slab1"), ("old05", "w15_slab2"), ("old05", "w15_slab3"),
         ("w14_top", "w15_slab0"), ("w14_top", "w15_slab1"), ("w14_top", "w15_slab2"), ("w14_top", "w15_slab3"),
         ("u09", "w12_panel"), ("old05", "w12_panel"), ("w14_48x110", "w12_panel")]
ORI = ["r0", "r180", "flipH", "flipV"]


def orient(t, k):
    return (t, t[::-1, ::-1], t[:, ::-1], t[::-1])[k]


def locate(q, tname):
    Q, T = load(q), load(tname)
    h, w = Q.shape
    th, tw = int(5 * T_PPI), int(8 * T_PPI)
    tpls = []
    for fy in (0.2, 0.5, 0.8):
        for fx in (0.2, 0.5, 0.8):
            y0 = max(0, min(int(fy * h - th / 2), h - th))
            x0 = max(0, min(int(fx * w - tw / 2), w - tw))
            tpls.append(((x0, y0), Q[y0:y0 + th, x0:x0 + tw]))
    best = {}
    for s in np.arange(0.90, 1.101, 0.02):
        for k in range(4):
            hits = []
            for (x0, y0), t in tpls:
                tt = orient(zoom(t, s, order=1), k)
                if T.shape[0] <= tt.shape[0] or T.shape[1] <= tt.shape[1]:
                    continue
                m = ncc_map(T, tt)
                iy, ix = np.unravel_index(np.argmax(m), m.shape)
                hits.append((float(m[iy, ix]), (x0, y0), (int(ix), int(iy))))
            if not hits:
                continue
            good = [hh for hh in hits if hh[0] > 0.5]
            key = (round(float(s), 2), ORI[k])
            best[key] = (len(good), float(np.median([hh[0] for hh in hits])), hits)
    key = max(best, key=lambda kk: (best[kk][0], best[kk][1]))
    n, med, hits = best[key]
    res = {"query": q, "target": tname, "scale": key[0], "orientation": key[1], "templates_above_0.5": n,
           "median_ncc": med, "q_shape_8ppi": [w, h], "t_shape_8ppi": [T.shape[1], T.shape[0]]}
    if n >= 3:
        # estimated placement of the query's full box in target coordinates (8 px/in), from good hits
        s = key[0]
        k = ORI.index(key[1])
        boxes = []
        for c, (x0, y0), (ix, iy) in hits:
            if c <= 0.5:
                continue
            tw_s, th_s = int(round(tw * s)), int(round(th * s))
            # template top-left in oriented, scaled query coordinates
            if k == 0:
                qx, qy = x0 * s, y0 * s
            elif k == 1:
                qx, qy = (w - x0 - tw) * s, (h - y0 - th) * s
            elif k == 2:
                qx, qy = (w - x0 - tw) * s, y0 * s
            else:
                qx, qy = x0 * s, (h - y0 - th) * s
            boxes.append((ix - qx, iy - qy))
        bx = np.median(np.array(boxes), 0)
        res["query_box_in_target_8ppi"] = [float(bx[0]), float(bx[1]), float(bx[0] + w * s), float(bx[1] + h * s)]
        res["query_box_in_target_in"] = [v / T_PPI for v in res["query_box_in_target_8ppi"]]
        res["box_spread_px"] = float(np.abs(np.array(boxes) - bx).max())
    return res


def main():
    out = []
    for q, t in PAIRS:
        r = locate(q, t)
        out.append(r)
        print("%-11s in %-11s  n>0.5=%d/9 med=%.3f  %s s=%.2f  box_in=%s spread=%s" % (
            q, t, r["templates_above_0.5"], r["median_ncc"], r["orientation"], r["scale"],
            [round(v, 1) for v in r.get("query_box_in_target_in", [])], r.get("box_spread_px")), flush=True)
    json.dump(out, open(out_path("_work/locate.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
