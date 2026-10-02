"""Review helper for step 09: Chiseled source luminance | groove component G | remainder, for one
face per groove family (centre crop 128 px, shown at 2x, 768 px wide)."""

import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import save_image, out_path  # noqa: E402
from s08_raw_height import LUMW  # noqa: E402

PICK = [1, 3, 7]        # (2,1) vertical, (0,1) diagS, (1,2) diagF in pool order


def tile(a, lo, hi, cen, half=64, mag=2):
    cx, cy = int(round(cen[0])), int(round(cen[1]))
    sub = a[cy - half:cy + half, cx - half:cx + half]
    sub = np.clip((sub - lo) / (hi - lo), 0, 1)
    im = Image.fromarray((sub * 255).astype(np.uint8)).resize((half * 2 * mag, half * 2 * mag), Image.NEAREST)
    return np.asarray(im)


def main():
    info = json.load(open(out_path("work", "pool_info.json")))["chiseled"]
    rgb = np.load(out_path("work", "pool_chis_rgb.npy"))
    G = np.load(out_path("work", "pool_chis_G.npy"))
    rows = []
    for k in PICK:
        cen = info[k]["centre"]
        lum = rgb[k] @ LUMW
        mu = lum[int(cen[1]) - 64:int(cen[1]) + 64, int(cen[0]) - 64:int(cen[0]) + 64].mean()
        rest = lum - mu - G[k]
        rows.append(np.hstack([tile(lum, mu - 30, mu + 30, cen), tile(G[k], -30, 30, cen), tile(rest, -30, 30, cen)]))
        print(info[k]["kind"], "crop lum std %.2f  G std %.2f  rest std %.2f" %
              (lum[int(cen[1]) - 64:int(cen[1]) + 64, int(cen[0]) - 64:int(cen[0]) + 64].std(),
               G[k][int(cen[1]) - 64:int(cen[1]) + 64, int(cen[0]) - 64:int(cen[0]) + 64].std(),
               rest[int(cen[1]) - 64:int(cen[1]) + 64, int(cen[0]) - 64:int(cen[0]) + 64].std()))
    save_image(Image.fromarray(np.vstack(rows)), "work", "thumbs", "chis_G_montage.png")


if __name__ == "__main__":
    main()
