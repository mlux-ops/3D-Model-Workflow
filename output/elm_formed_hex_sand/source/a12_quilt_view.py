"""Review helper: mosaic of the quilted Raw faces (relative luma on the quilting grid),
contrast-stretched, beside two render Raw faces at the same scale for comparison."""

import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from common import out_path, hex_edge_distance_local
from guard import save_image


def main():
    meta = json.load(open(out_path("_work", "raw_quilt.json")))
    q = np.load(out_path("_work", "raw_quilt.npz"))
    src = json.load(open(out_path("_work", "sources.json")))
    rel = np.load(out_path("_work", "src_rel.npy")).astype(np.float64)
    ppi = src["ppi_render"]
    tiles = []
    keys = sorted(meta["faces"], key=int)
    for k in keys:
        cur = q["cur_%s" % k]
        G_h, G_w = cur.shape
        gy, gx = np.mgrid[0:G_h, 0:G_w]
        e = hex_edge_distance_local(gx + 0.5 - G_w / 2, gy + 0.5 - G_h / 2, 5.0 * ppi)
        a = np.where(e >= 0, cur, np.nan)
        tiles.append(a)
    for f in src["faces"]:
        if f["id"] in (10, 29):
            G_h, G_w = tiles[0].shape
            gy, gx = np.mgrid[0:G_h, 0:G_w].astype(np.float64)
            px = f["cx"] + gx + 0.5 - G_w / 2
            py = f["cy"] + gy + 0.5 - G_h / 2
            a = ndimage.map_coordinates(rel, [py - 0.5, px - 0.5], order=1)
            e = hex_edge_distance_local(gx + 0.5 - G_w / 2, gy + 0.5 - G_h / 2, 5.0 * ppi - 6)
            tiles.append(np.where(e >= 0, a, np.nan))
    s = np.nanstd(np.concatenate([t[np.isfinite(t)] for t in tiles]))
    imgs = []
    for t in tiles:
        v = np.where(np.isfinite(t), np.clip(t / (3 * s) * 127 + 128, 0, 255), 255)
        imgs.append(v.astype(np.uint8))
    G_h, G_w = imgs[0].shape
    cols = 4
    rows = (len(imgs) + cols - 1) // cols
    canvas = np.full((rows * G_h, cols * G_w), 255, np.uint8)
    for n, im in enumerate(imgs):
        r, c = divmod(n, cols)
        canvas[r * G_h:(r + 1) * G_h, c * G_w:(c + 1) * G_w] = im
    out = Image.fromarray(canvas)
    k = 800.0 / out.width
    save_image(out.resize((800, int(out.height * k)), Image.LANCZOS), "_work", "quilt_mosaic.png")
    # one face at 1:1 grid resolution (render scale), for seam inspection
    save_image(Image.fromarray(imgs[len(keys) - 1]), "_work", "quilt_last_face.png")
    print("faces", keys, "+ render 10, 29 at the end")


if __name__ == "__main__":
    sys.exit(main())
