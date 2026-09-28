"""Review previews for MSI Soreno Ivory 24x48 (every file <= 800 px so it can be opened directly).

textures/_PREVIEW_whole_colour.jpg       whole colour map
textures/_PREVIEW_whole_bump.jpg         whole bump map (8-bit view)
textures/_PREVIEW_tiling_3x3.jpg         3 x 3 repeat (36 x 36 ft), downsampled
textures/_PREVIEW_wrap_corner_1to1.jpg   2 x 2 repeat, 800 px at 1:1 centred on the shared corner
textures/_PREVIEW_joint_crossing_1to1.jpg 800 px at 1:1 over a T junction
textures/_PREVIEW_joint_crossing_4x.jpg  200 px around the same junction, 4x nearest-neighbour
textures/_PREVIEW_grazing_light.jpg      whole map lit at 15 deg elevation (colour x shading)
textures/_PREVIEW_grazing_light_1to1.jpg 800 px at 1:1 of the same render over a T junction
textures/_REVIEW_source_vs_built.jpg     source faces A and B vs four built tiles, same scale
textures/_REVIEW_source_vs_built_1to1.jpg 380 px detail pairs at 24 px/in
"""
import json

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import zoom

from guard import out_path

Image.MAX_IMAGE_PIXELS = None
PPI = 24


def save(a, name, maxside=800, quality=90):
    im = Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8))
    if max(im.size) > maxside:
        im.thumbnail((maxside, maxside), Image.LANCZOS)
    im.save(out_path("textures/" + name), quality=quality)
    return im.size


def main():
    rep = json.load(open(out_path("textures/report.json")))
    c = np.asarray(Image.open(out_path("textures/Color.png")).convert("RGB")).astype(np.float64)
    b = np.asarray(Image.open(out_path("textures/Bump16.png"))).astype(np.float64)
    H, W = b.shape
    h = b / 65535.0 * rep["relief_mm"]["full_scale"]
    mw, mh = rep["module_in"][0] * PPI, rep["module_in"][1] * PPI
    off = rep["row_offset_in"] * PPI
    sizes = {}
    sizes["whole_colour"] = save(c, "_PREVIEW_whole_colour.jpg")
    sizes["whole_bump"] = save(b / 65535 * 255, "_PREVIEW_whole_bump.jpg")
    small = np.asarray(Image.fromarray(c.astype(np.uint8)).resize((W // 4, H // 4), Image.LANCZOS)).astype(np.float64)
    sizes["tiling_3x3"] = save(np.tile(small, (3, 3, 1)), "_PREVIEW_tiling_3x3.jpg")
    t2 = np.tile(c, (2, 2, 1))
    sizes["wrap"] = save(t2[H - 400:H + 400, W - 400:W + 400], "_PREVIEW_wrap_corner_1to1.jpg")
    cx, cy = int(round(off + mw)), int(round(mh))          # row 1 vertical joint meets the first horizontal joint
    sizes["cross"] = save(c[cy - 400:cy + 400, cx - 400:cx + 400], "_PREVIEW_joint_crossing_1to1.jpg")
    z = c[cy - 100:cy + 100, cx - 100:cx + 100].repeat(4, 0).repeat(4, 1)
    sizes["cross4"] = save(z, "_PREVIEW_joint_crossing_4x.jpg")

    # grazing light: height in mm, pixel = 25.4/24 mm; light 15 deg above the horizon, azimuth 30 deg
    px_mm = 25.4 / PPI
    hx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / (2 * px_mm)
    hy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / (2 * px_mm)
    n = np.stack([-hx, -hy, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    el, az = np.radians(15), np.radians(30)
    l = np.array([np.cos(el) * np.cos(az), -np.cos(el) * np.sin(az), np.sin(el)])
    shade = np.clip(n @ l, 0, None) / np.sin(el)
    lit = c * (0.25 + 0.75 * shade)[..., None]
    sizes["grazing"] = save(lit, "_PREVIEW_grazing_light.jpg")
    sizes["grazing1"] = save(lit[cy - 400:cy + 400, cx - 400:cx + 400], "_PREVIEW_grazing_light_1to1.jpg")

    # source vs built at the same scale (all resampled to 24 px/in, then all downscaled by the same factor)
    mppi = rep["sources"]["master_ppi"]
    A = np.load(out_path("_work/master_A.npy"))
    B = np.load(out_path("_work/master_B.npy"))
    A24 = zoom(A, (PPI / mppi, PPI / mppi, 1), order=3)
    B24 = zoom(B, (PPI / mppi, PPI / mppi, 1), order=3)
    tw, th = int(rep["tile_drawn_in"][0] * PPI) - 8, int(rep["tile_drawn_in"][1] * PPI) - 8
    tiles = []
    for r, k in ((0, 1), (1, 1), (2, 1), (3, 1)):
        x0 = int(round(r * off + k * mw + 1.5)) + 4
        y0 = int(round(r * mh + 1.5)) + 4
        xi = (x0 + np.arange(tw)) % W
        tiles.append(c[y0:y0 + th][:, xi])
    s = 380.0 / tw
    cells = [zoom(x, (s, s, 1), order=1) for x in (A24[:th, :tw], B24[:th, :tw], *tiles)]
    ch = max(x.shape[0] for x in cells)
    canvas = np.full((3 * (ch + 18), 2 * 390, 3), 255.0)
    labels = ["source face A (MSI swatch)", "source face B (MSI swatch)", "built tile r0", "built tile r1",
              "built tile r2", "built tile r3"]
    for i, x in enumerate(cells):
        yy, xx = (i // 2) * (ch + 18), (i % 2) * 390
        canvas[yy:yy + x.shape[0], xx:xx + x.shape[1]] = x
    im = Image.fromarray(canvas.astype(np.uint8))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(labels):
        d.text(((i % 2) * 390 + 4, (i // 2) * (ch + 18) + ch + 3), t, fill=(0, 0, 0))
    im.save(out_path("textures/_REVIEW_source_vs_built.jpg"), quality=90)
    sizes["src_vs_built"] = im.size
    # 1:1 detail pairs at 24 px/in
    p = 380
    pair = np.full((p * 2 + 10, p * 2 + 10, 3), 255.0)
    pair[:p, :p] = A24[100:100 + p, 200:200 + p]
    pair[:p, p + 10:] = B24[100:100 + p, 600:600 + p]
    pair[p + 10:, :p] = tiles[0][100:100 + p, 200:200 + p]
    pair[p + 10:, p + 10:] = tiles[2][100:100 + p, 600:600 + p]
    sizes["src_vs_built_1to1"] = save(pair, "_REVIEW_source_vs_built_1to1.jpg")
    print(json.dumps(sizes))


if __name__ == "__main__":
    main()
