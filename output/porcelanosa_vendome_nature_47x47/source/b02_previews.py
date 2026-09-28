"""Previews (every one <= 800 px on its long side) of the built maps, read from disk.

Per set (designed, free_mix): whole colour, whole bump, 3 x 3 tiling, wrap four-way corner 1:1, grazing-light bump
(whole and 1:1). Designed: 1:1 crops of all 8 designed joints (strip A and strip B sheets). Pieces: contact sheet
of the 8 piece maps and one piece tiled 2 x 2. Source vs built (face 1 source, built designed cell).
Writes <set>/_PREVIEW_*.jpg.  Usage: python b02_previews.py"""
import numpy as np
from PIL import Image

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
MPX = 1512


def load(d, name=""):
    c = np.asarray(Image.open(out_path("%s/%sColor.png" % (d, name))).convert("RGB"))
    b = np.asarray(Image.open(out_path("%s/%sBump16.png" % (d, name)))).astype(np.float64) / 65535
    return c, b


def save(arr, rel, maxs=800):
    im = Image.fromarray(arr)
    im.thumbnail((maxs, maxs), Image.LANCZOS)
    im.save(out_path(rel), quality=90)


def hill(b, full_mm=1.6, ppi=32, az=315.0, el=12.0, exag=6.0):
    """Grazing-light shading of the height map (elevation el degrees), relief exaggerated for visibility."""
    h = b * full_mm / 25.4 * ppi * exag            # height in px units
    gy, gx = np.gradient(h)
    a, e = np.radians(az), np.radians(el)
    lx, ly, lz = np.cos(e) * np.cos(a), -np.cos(e) * np.sin(a), np.sin(e)
    n = np.sqrt(gx * gx + gy * gy + 1)
    s = (-gx * lx - gy * ly + lz) / n
    return np.clip(s / max(np.percentile(s, 99.5), 1e-6) * 235, 0, 255).astype(np.uint8)


def bump8(b):
    return np.clip(b * 255, 0, 255).astype(np.uint8)


def main():
    for d in ("designed", "free_mix"):
        c, b = load(d)
        H, W = b.shape
        save(c, d + "/_PREVIEW_colour.jpg")
        save(bump8(b), d + "/_PREVIEW_bump.jpg")
        small = np.asarray(Image.fromarray(c).resize((W // 8, H // 8), Image.LANCZOS))
        save(np.tile(small, (3, 3, 1)), d + "/_PREVIEW_tiled_3x3.jpg")
        t = np.tile(c, (2, 2, 1))[H - 200:H + 200, W - 200:W + 200]
        save(t, d + "/_PREVIEW_wrap_corner_1to1.jpg")
        tb = np.tile(b, (2, 2))[H - 200:H + 200, W - 200:W + 200]
        save(hill(tb), d + "/_PREVIEW_wrap_corner_bump_graze_1to1.jpg")
        hs = hill(b.reshape(H // 8, 8, W // 8, 8).mean((1, 3)), ppi=4)      # float block mean to <= 756 px: no resize after shading
        save(hs, d + "/_PREVIEW_bump_graze_whole.jpg")
        y0, x0 = MPX - 400, MPX - 400
        save(hill(b[y0:y0 + 800, x0:x0 + 800]), d + "/_PREVIEW_bump_graze_1to1.jpg")
        save(c[y0:y0 + 800, x0:x0 + 800], d + "/_PREVIEW_colour_cross_1to1.jpg")
    # designed joints 1:1: 4 joints per sheet, 190 px wide each (95 either side), 700 rows of the vein-busiest part
    c, b = load("designed")
    H, W = b.shape
    lumi = c.astype(np.float64).mean(2)
    for r, tag in ((0, "stripA_1-6-7-8"), (1, "stripB_2-3-4-5")):
        crops = []
        for k in range(1, 5):
            xc = (k * MPX) % W
            y_lo = r * MPX + 1
            e = np.abs(np.diff(lumi[y_lo:y_lo + MPX - 2, (xc - 6) % W], axis=0)) + np.abs(np.diff(lumi[y_lo:y_lo + MPX - 2, (xc + 5) % W], axis=0))
            y0 = y_lo + int(np.argmax(np.convolve(e, np.ones(700), "valid")))
            cols = np.arange(xc - 95, xc + 95) % W
            crops.append(c[y0:y0 + 700][:, cols])
            crops.append(np.full((700, 10, 3), (255, 0, 0), np.uint8))
        save(np.concatenate(crops[:-1], 1), "designed/_PREVIEW_joints_%s_1to1.jpg" % tag)
    # source vs built: face 1 (source, Adobe RGB file shown as decoded sRGB) vs designed cell (0,0)
    from colour_io import load_face_lin
    from common import lin_to_srgb
    src = np.round(lin_to_srgb(load_face_lin(1))).astype(np.uint8)
    s1 = np.asarray(Image.fromarray(src).resize((390, 390), Image.LANCZOS))
    b1 = np.asarray(Image.fromarray(c[:MPX, :MPX]).resize((390, 390), Image.LANCZOS))
    save(np.concatenate([s1, np.full((390, 20, 3), 255, np.uint8), b1], 1), "designed/_PREVIEW_source_vs_built_face1.jpg")
    # pieces
    tiles = []
    for k in range(1, 9):
        pc, pb = load("pieces", "Piece_%d_" % k)
        tiles.append(np.asarray(Image.fromarray(pc).resize((190, 190), Image.LANCZOS)))
        if k == 1:
            save(np.tile(pc, (2, 2, 1))[MPX - 200:MPX + 200, MPX - 200:MPX + 200], "pieces/_PREVIEW_piece1_wrap_corner_1to1.jpg")
            save(hill(np.tile(pb, (2, 2))[MPX - 200:MPX + 200, MPX - 200:MPX + 200]), "pieces/_PREVIEW_piece1_wrap_corner_bump_graze_1to1.jpg")
    gap = np.full((190, 8, 3), 40, np.uint8)
    row1 = np.concatenate(sum([[t, gap] for t in tiles[:4]], [])[:-1], 1)
    row2 = np.concatenate(sum([[t, gap] for t in tiles[4:]], [])[:-1], 1)
    save(np.concatenate([row1, np.full((8, row1.shape[1], 3), 40, np.uint8), row2], 0), "pieces/_PREVIEW_pieces_1-8.jpg")


if __name__ == "__main__":
    main()
