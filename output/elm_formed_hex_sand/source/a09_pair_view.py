"""Step 9: side-by-side view of two render faces (contrast-stretched band-pass luma) under
every hexagon symmetry, to see whether a high NCC pair is a copied texture."""

import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from common import load_lattice, render_rgb, luma, gaussian, out_path
from a07_dup_check import face_patch, transform, ncc_max
from guard import save_image


def main():
    ida, idb = int(sys.argv[1]), int(sys.argv[2])
    cells = {c["id"]: c for c in json.load(open(out_path("_work", "cells_raw.json")))}
    L = luma(render_rgb())
    band = gaussian(L, 1.0) - gaussian(L, 8.0)
    low = gaussian(L, 6.0) - gaussian(L, 40.0)
    for nm, arr in (("band", band), ("low", low)):
        A0 = face_patch(arr, cells[ida], 80)
        B = face_patch(arr, cells[idb], 115)
        best = (-1, 0, False)
        for k in range(6):
            for mir in (False, True):
                v = ncc_max(transform(A0, k, mir)[20:-20, 20:-20], B, 60)
                if v > best[0]:
                    best = (v, k, mir)
        print("%s: best NCC %.3f at rot %d*60 mirror %s" % (nm, best[0], best[1], best[2]))
    # picture: both faces' band-pass and low-pass, stretched
    tiles = []
    for arr in (band, low):
        row = []
        for i in (ida, idb):
            P = face_patch(arr, cells[i], 150)
            P = (P - P.mean()) / (4 * P.std() + 1e-9) * 128 + 128
            row.append(np.clip(P, 0, 255))
        tiles.append(np.concatenate(row, axis=1))
    im = Image.fromarray(np.concatenate(tiles, axis=0).astype(np.uint8))
    im = im.resize((im.width * 800 // im.width, im.height * 800 // im.width), Image.LANCZOS)
    save_image(im, "_work", "pair_%d_%d.png" % (ida, idb))


if __name__ == "__main__":
    sys.exit(main())
