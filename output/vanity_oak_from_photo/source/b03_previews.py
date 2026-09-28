"""Review previews, all <= 800 px, all made from the delivered Color.png on disk (plus source crops for comparison).

_PREVIEW_map_whole.jpg          whole 48 x 24 in map
_PREVIEW_tiled_3x3.jpg          3 x 3 repetition (12 ft x 6 ft)
_PREVIEW_wrap_corner_1to1.png   800 x 800 px at 64 px/in centred on the four-way wrap corner (2 x 2 tiling)
_PREVIEW_centre_1to1.png        800 x 800 px at 64 px/in from the map centre
_PREVIEW_source_vs_built.jpg    rectified source photo vs built map, same inches per pixel (6 x 6 in at 64 px/in
                                each, top) and a room-scale pair (source door 27.9 x 10.2 in vs the same size of map)
_PREVIEW_vanity_mock.jpg        map laid on the user's largest panel 37 x 7.5 in (horizontal grain) and on a
                                24 x 48 in door rotated 90 deg (vertical grain), 14 px/in, with 1/8 in reveals
(_PREVIEW_source_crops_raw.jpg / _delit.jpg come from a02 / a04; _PREVIEW_leaf_layout.jpg from b01.)"""
import json

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

from common import lin_to_srgb, thumb
from guard import out_path

PPI = 64


def box_down(a, f):
    h, w = a.shape[0] // f * f, a.shape[1] // f * f
    return a[:h, :w].reshape(h // f, f, w // f, f, -1).mean((1, 3))


def resample(a, ppi_from, ppi_to):
    z = ppi_to / ppi_from
    return np.stack([ndi.zoom(a[..., c], z, order=3, mode="nearest") for c in range(3)], -1)


def main():
    m = np.asarray(Image.open(out_path("Color.png")), dtype=np.float64)
    H, W = m.shape[:2]
    thumb(m, out_path("_PREVIEW_map_whole.jpg"))
    t = np.tile(box_down(m, 4), (3, 3, 1))
    thumb(t, out_path("_PREVIEW_tiled_3x3.jpg"))
    t2 = np.tile(m, (2, 2, 1))
    Image.fromarray(t2[H - 400:H + 400, W - 400:W + 400].astype(np.uint8)).save(out_path("_PREVIEW_wrap_corner_1to1.png"))
    Image.fromarray(m[H // 2 - 400:H // 2 + 400, W // 2 - 400:W // 2 + 400].astype(np.uint8)).save(
        out_path("_PREVIEW_centre_1to1.png"))

    # source vs built at matched scale
    raw = lin_to_srgb(np.load(out_path("_work/crops/door_L.npy")))       # 32 px/in, grain horizontal (rotated)
    raw64 = resample(raw, 32, PPI)
    s = 6 * PPI
    y0, x0 = 60, 900
    pair = np.full((s + 30 + 330, 800, 3), 255.0)
    pair[:s, :s] = raw64[y0:y0 + s, x0:x0 + s]
    pair[:s, 800 - s:] = m[700:700 + s, 1500:1500 + s]
    # room scale: whole door crop (27.9 x 10.2 in) vs same inches of the map, at 12 px/in
    ds = resample(raw, 32, 12)
    ms = resample(m, PPI, 12)
    h2, w2 = ds.shape[:2]
    pair[s + 30:s + 30 + h2, :w2] = ds
    pair[s + 30:s + 30 + h2, 800 - w2:] = ms[100:100 + h2, 200:200 + w2]
    Image.fromarray(np.clip(np.round(pair), 0, 255).astype(np.uint8)).save(out_path("_PREVIEW_source_vs_built.jpg"),
                                                                              quality=92)

    # vanity mock at 14 px/in
    q = 14
    mq = resample(m, PPI, q)
    canvas = np.full((int(51 * q), int(66 * q), 3), 236.0)
    rev = (70, 58, 44)
    # 37 x 7.5 in panel, horizontal grain, map origin offset (2 in, 3 in)
    pw, ph = int(round(37 * q)), int(round(7.5 * q))
    oy, ox = 2 * q, 3 * q
    canvas[q:q + ph, q:q + pw] = mq[oy:oy + ph, ox:ox + pw]
    # 24 x 48 in door, vertical grain: map rotated 90 deg
    mr = np.rot90(mq, 1)
    dw, dh = int(round(24 * q)), int(round(48 * q))
    top = q + ph + q // 2
    left = int(round(40.5 * q))
    canvas[q:q + dh, left:left + dw] = mr[:dh, :dw]
    im = Image.fromarray(np.clip(np.round(canvas), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([q, q, q + pw - 1, q + ph - 1], outline=rev, width=2)
    d.rectangle([left, q, left + dw - 1, q + dh - 1], outline=rev, width=2)
    d.text((q, q + ph + 6), "largest panel 37 x 7.5 in (map as-is, horizontal grain)", fill=(40, 40, 40))
    d.text((q, q + ph + 22), "door 24 x 48 in (map Rotation 90 deg)", fill=(40, 40, 40))
    # a second, drawer-like stack of 37 x 7.5 panels using different map offsets
    for i, (oyi, oxi) in enumerate([(9, 6), (15, 10), (1, 9)]):
        yy = q + ph + 44 + i * (ph + q // 2)
        py, px = int(oyi * q), int(oxi * q)
        canvas_patch = mq[py:py + ph, px:px + pw]
        im.paste(Image.fromarray(np.clip(np.round(canvas_patch), 0, 255).astype(np.uint8)), (q, yy))
        d.rectangle([q, yy, q + pw - 1, yy + ph - 1], outline=rev, width=2)
    d.text((q, q + ph + 44 + 3 * (ph + q // 2) + 4), "37 x 7.5 in at three different texture offsets", fill=(40, 40, 40))
    im.thumbnail((800, 800), Image.LANCZOS)
    im.save(out_path("_PREVIEW_vanity_mock.jpg"), quality=92)
    print("previews written")


if __name__ == "__main__":
    main()
