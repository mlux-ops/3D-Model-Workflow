"""Production step c04: side-by-side view of lifestyle Chiseled ridges vs atlas Chiseled faces, at
the same groove period and the same light-to-groove angle (as used by c02). Also reports the
non-periodic residual of a lifestyle MATTE window, i.e. the image's own speckle + compression
floor, so the c02 lifestyle ratio can be read against it.
Usage: python c04_ridge_compare_view.py Color.png Bump16.png face_ids.png report.json out_name.png
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from guard import LIFESTYLE_PATH, save_image
from c01_measure_ridge_irregularity import luma, wave_vector
from c02_ridge_roughness_ratio import LIFE_BOX, LIGHT_AZ_LIFE_DEG, H_RANGE_MM, PPI, rel, shade

Image.MAX_IMAGE_PIXELS = None
LIFE_MATTE_BOX = (410, 600, 590, 780)   # c03 centre_face window


def main():
    cpath, bpath, fpath, rpath, name = sys.argv[1:6]
    life = np.asarray(Image.open(LIFESTYLE_PATH).convert("RGB")).astype(np.float64) / 255.0
    x0, y0, x1, y1 = LIFE_BOX
    pl = life[y0:y1, x0:x1]
    rl = rel(luma(pl), np.ones(pl.shape[:2], bool))
    kl = wave_vector(rl)
    P_life = 1.0 / np.hypot(*kl)
    d_ang = LIGHT_AZ_LIFE_DEG - np.degrees(np.arctan2(kl[1], kl[0]))
    mx0, my0, mx1, my1 = LIFE_MATTE_BOX
    rm = rel(luma(life[my0:my1, mx0:mx1]), np.ones((my1 - my0, mx1 - mx0), bool))
    print("lifestyle relative-luma std: chiseled patch %.4f, matte window %.4f (speckle + compression floor)" % (rl.std(), rm.std()))
    col = np.asarray(Image.open(cpath).convert("RGB")).astype(np.float64) / 255.0
    b = np.asarray(Image.open(bpath)).astype(np.float64) / 65535.0 * H_RANGE_MM / 25.4 * PPI
    ids = np.asarray(Image.open(fpath)).astype(np.int32)
    rep = json.load(open(rpath, encoding="utf-8"))
    chis = [f["index"] for f in rep["faces"] if f["type"] == "chiseled"][:2]
    Hh, Ww = ids.shape
    tiles = [np.clip(pl, 0, 1)]
    for k in chis:
        yy, xx = np.nonzero(ids == k)
        ay = np.angle(np.exp(2j * np.pi * yy / Hh).mean()) / (2 * np.pi) * Hh
        ax = np.angle(np.exp(2j * np.pi * xx / Ww).mean()) / (2 * np.pi) * Ww
        cy, cx = int(round(ay)) % Hh, int(round(ax)) % Ww
        S = int(round(pl.shape[0] * 12.62 / P_life)) + 4
        ys = np.arange(cy - S // 2, cy + S // 2) % Hh
        xs = np.arange(cx - S // 2, cx + S // 2) % Ww
        hp_ = b[np.ix_(ys, xs)]
        m = ids[np.ix_(ys, xs)] == k
        ka = wave_vector(rel(hp_ - hp_.mean() + 100.0, m))
        sh = shade(hp_, np.degrees(np.arctan2(ka[1], ka[0])) + d_ang)[..., None] * col[np.ix_(ys, xs)]
        z = P_life / (1.0 / np.hypot(*ka))
        shz = np.stack([ndi.zoom(ndi.gaussian_filter(sh[..., c], max(0.0, 0.5 / z - 0.5)), z, order=1) for c in range(3)], -1)
        tiles.append(np.clip(shz[:pl.shape[0], :pl.shape[1]], 0, 1))
    # normalise each tile's mean AND contrast to the lifestyle patch, so only the texture (not the
    # harsher 15 deg Lambert light) is compared
    ref_m, ref_s = tiles[0].mean(), tiles[0].std()
    tiles = [tiles[0]] + [np.clip(ref_m + (t - t.mean()) * ref_s / max(t.std(), 1e-6), 0, 1) for t in tiles[1:]]
    ims = [Image.fromarray((t * 255).astype(np.uint8)).resize((t.shape[1] * 5 // 3, t.shape[0] * 5 // 3), Image.LANCZOS) for t in tiles]
    Wt = sum(i.size[0] for i in ims) + 6 * (len(ims) - 1)
    sheet = Image.new("RGB", (Wt, max(i.size[1] for i in ims)), (255, 255, 255))
    x = 0
    for i in ims:
        sheet.paste(i, (x, 0))
        x += i.size[0] + 6
    sheet.thumbnail((800, 800))
    save_image(sheet, "_work", name)
    print("wrote _work/%s (first tile = lifestyle, then atlas faces %s)" % (name, chis))


if __name__ == "__main__":
    main()
