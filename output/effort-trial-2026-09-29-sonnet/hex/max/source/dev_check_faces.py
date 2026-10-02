"""Development check for s10b_faces: source-centre consistency, timing and one crop per face type."""

import json
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import save_image, out_path  # noqa: E402
from geometry import face_centres, window_offsets, hex_inside  # noqa: E402
import s10b_faces as F  # noqa: E402


def main():
    t0 = time.time()
    P = F.Pools()
    print("pools loaded %.1fs" % (time.time() - t0))
    grid = json.load(open(out_path("work", "render_grid.json")))
    err = []
    for c in P.info["chiseled"]:
        wc = F.win_centre(grid, c["i"], c["j"])
        err.append((wc[0] - c["centre"][0], wc[1] - c["centre"][1]))
    print("chiseled centre check (computed - stored), max abs:", np.abs(np.array(err)).max())

    layout = json.load(open(out_path("work", "layout.json")))["faces"]
    centres = face_centres()
    picks = {"matte": 0, "raw": 1}
    for k, f in enumerate(layout):
        if f["type"] == "chiseled" and f["orientation"] not in picks:
            picks[f["orientation"]] = k
    print("picks", picks)
    tiles = []
    for name, k in picks.items():
        f = layout[k]
        c = centres[k]
        dx, dy = window_offsets(c["cx"], c["cy"], 384)
        t1 = time.time()
        if f["type"] == "matte":
            rgb, st = F.build_matte(f, P, dx, dy)
            hgt = np.zeros(dx.shape)
        elif f["type"] == "raw":
            rgb, st = F.raw_albedo(f, P, dx, dy)
            dxf, dyf = window_offsets(c["cx"], c["cy"], 512)
            hc, st2 = F.raw_height(f, P, dxf, dyf)
            hgt = hc[128:-128, 128:-128]
            gy, gx = np.gradient(hc)
            ins = hex_inside(dxf, dyf) > 4
            print("  raw hc std %.3f  rms|grad| per atlas px %.4f  (%s)" % (hc[ins].std(), np.sqrt((gx ** 2 + gy ** 2)[ins].mean()), st2))
        else:
            rgb, G, st = F.build_chiseled(f, P, dx, dy)
            hgt = G
        print(name, "face", f["index"], "built %.1fs" % (time.time() - t1), st)
        ins = hex_inside(dx, dy)
        col = np.clip(rgb, 0, 255).astype(np.uint8)
        col[ins < 4] = (211, 202, 188)
        h = (hgt - hgt[ins > 4].mean())
        s = 3.0 * h[ins > 4].std() + 1e-9
        hv = np.clip(128 + 127 * h / s, 0, 255).astype(np.uint8)
        tiles.append(np.hstack([col[::2, ::2], np.repeat(hv[::2, ::2, None], 3, axis=2)]))
    save_image(Image.fromarray(np.vstack(tiles[:2])), "work", "thumbs", "dev_faces_a.png")
    save_image(Image.fromarray(np.vstack(tiles[2:4])), "work", "thumbs", "dev_faces_b.png")
    save_image(Image.fromarray(np.vstack(tiles[4:])), "work", "thumbs", "dev_faces_c.png")


if __name__ == "__main__":
    main()
