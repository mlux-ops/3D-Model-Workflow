"""Review images (all <= 800 px on the long side) into textures/_*.jpg:

_PREVIEW_whole.jpg          whole colour map, downscaled
_PREVIEW_wrap_2x2.jpg       the map tiled 2 x 2 around its corner at 1:1 (800 x 800 crop centred on the seam)
_PREVIEW_grazing_whole.jpg  whole map lit at 15 deg from the left (ribs vertical, so relief shows)
_PREVIEW_grazing_1to1.jpg   800 x 800 px 1:1 crop of the grazing render over a joint crossing
_PREVIEW_colour_1to1.jpg    same crop of the colour map, contrast stretched x3 for inspection
_PREVIEW_vs_swatch.jpg      ELM swatch (rotated, resampled to 100 ppi) beside one built tile, same scale
_PREVIEW_bump_1to1.jpg      same 1:1 crop of the bump map
"""
import json

import numpy as np
from PIL import Image

from guard import out_path, ref

Image.MAX_IMAGE_PIXELS = None
MM_PER_PX = 25.4 / 100


def shade(h_mm, albedo_lin, elev_deg=15.0, az_deg=180.0):
    gy, gx = np.gradient(h_mm, MM_PER_PX)
    n = np.dstack([-gx, -gy, np.ones_like(h_mm)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    # az_deg is the compass direction the light comes from in the image plane: 180 = from the left (-x)
    e, a = np.radians(elev_deg), np.radians(az_deg)
    L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    lam = np.clip((n * L).sum(2), 0, None) / np.sin(e) * 0.5
    return albedo_lin * lam[..., None]


def to_srgb(lin):
    c = np.clip(lin, 0, 1)
    return np.clip(255 * np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055), 0, 255).astype(np.uint8)


def save(arr, name, size=800):
    im = Image.fromarray(arr) if isinstance(arr, np.ndarray) else arr
    im = im.copy()
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(out_path("textures/" + name), quality=90)


def main():
    rep = json.load(open(out_path("textures/report.json")))
    c = np.asarray(Image.open(out_path("textures/Color.png")))
    b = np.asarray(Image.open(out_path("textures/Bump16.png"))).astype(np.float64)
    h = b / 65535 * rep["relief_mm"]["full_scale"]
    H, W = h.shape
    lin = (c / 255.0)
    lin = np.where(lin <= 0.04045, lin / 12.92, ((lin + 0.055) / 1.055) ** 2.4)

    save(c, "_PREVIEW_whole.jpg")
    # wrap 2x2 around the corner, 1:1
    t = np.tile(c, (2, 2, 1))
    save(t[H - 400:H + 400, W - 400:W + 400], "_PREVIEW_wrap_2x2.jpg")
    tb = np.tile(h, (2, 2))
    tl = np.tile(lin, (2, 2, 1))
    g = shade(tb[H - 400:H + 400, W - 400:W + 400], tl[H - 400:H + 400, W - 400:W + 400] * 3.0)
    save(to_srgb(g), "_PREVIEW_wrap_2x2_grazing.jpg")

    # grazing whole (compute on a 1/4 decimated copy to keep memory low; relief is smooth at 4 px)
    g = shade(h[::4, ::4], lin[::4, ::4] * 3.0)
    save(to_srgb(g), "_PREVIEW_grazing_whole.jpg")

    # 1:1 crops over a joint crossing: column boundary 3, row boundary 1
    x0, y0 = int(3 * rep["module_in"][0] * 100) - 400, int(rep["module_in"][1] * 100) - 400
    sl = (slice(y0, y0 + 800), slice(x0, x0 + 800))
    save(to_srgb(shade(h[sl], lin[sl] * 3.0)), "_PREVIEW_grazing_1to1.jpg")
    cc = c[sl].astype(np.float64)
    m = np.median(cc[cc.mean(2) < 120].reshape(-1, 3), 0)
    save(np.clip((cc - m) * 3 + m, 0, 255).astype(np.uint8), "_PREVIEW_colour_1to1.jpg")
    save((b[sl] / 257).astype(np.uint8), "_PREVIEW_bump_1to1.jpg")

    # swatch vs built tile at 100 ppi, ribs vertical
    sw = Image.open(ref("elm_page_main-image_template.jpg")).convert("RGB")
    k = 100 / rep["delight"]["source_ppi"]
    sw = sw.resize((round(sw.width * k), round(sw.height * k)), Image.LANCZOS).rotate(90, expand=True)
    sw = np.asarray(sw)
    tile_w, tile_h = int(rep["tile_drawn_in"][0] * 100), int(rep["tile_drawn_in"][1] * 100)
    ox, oy = int(0.09375 * 100), int(0.09375 * 100)
    tile_c = c[oy:oy + tile_h, ox:ox + tile_w]
    tile_g = to_srgb(shade(h[oy:oy + tile_h, ox:ox + tile_w], lin[oy:oy + tile_h, ox:ox + tile_w] * 3.0,
                           elev_deg=40))
    hh = max(sw.shape[0], tile_h)
    canvas = np.full((hh, sw.shape[1] + 2 * tile_w + 40, 3), 255, np.uint8)
    canvas[:sw.shape[0], :sw.shape[1]] = sw
    canvas[:tile_h, sw.shape[1] + 20:sw.shape[1] + 20 + tile_w] = tile_c
    canvas[:tile_h, sw.shape[1] + 40 + tile_w:] = tile_g
    save(canvas, "_PREVIEW_vs_swatch.jpg")
    print("previews written")


if __name__ == "__main__":
    main()
