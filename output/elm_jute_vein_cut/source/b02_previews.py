"""Review previews (all <= 800 px) for one product.
Usage: python b02_previews.py veincut_24x48 | mosaic_1x3
Writes <dir>/_PREVIEW_*.jpg:
  colour_whole, bump_whole, colour_tiled3x3 (3 x 3 atlas repeats, atlas edges marked by nothing: judge it
  blind), wrap_corner_1to1 (800 px crop centred on the image's four-way wrap corner, rolled), grazing_bump
  (Lambert shading from the bump height, light 10 deg above the surface from the left, whole atlas and 1:1),
  source_vs_built (a real source face next to the built cell/chips at the same scale), cells_labelled."""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw

from guard import out_path

Image.MAX_IMAGE_PIXELS = None


def fit(im, n=800):
    im = im.copy()
    im.thumbnail((n, n), Image.LANCZOS)
    return im


def shade(h_mm, ppi, elev_deg=10.0, azim_deg=180.0):
    mm_px = 25.4 / ppi
    gy, gx = np.gradient(h_mm, mm_px)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    e, a = np.radians(elev_deg), np.radians(azim_deg)
    l = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    s = np.clip(n @ l, 0, None) / np.sin(e)          # flat face -> 1.0
    return np.clip(s * 0.62 * 255, 0, 255).astype(np.uint8)


def main(prod):
    D = prod + "/"
    rep = json.load(open(out_path(D + "report.json")))
    ppi = rep["ppi"]
    c = Image.open(out_path(D + "Color.png")).convert("RGB")
    b16 = np.asarray(Image.open(out_path(D + "Bump16.png"))).astype(np.float64)
    h = b16 / 65535 * rep["relief_mm"]["full_scale"]
    W, H = c.size
    fit(c).save(out_path(D + "_PREVIEW_colour_whole.jpg"), quality=90)
    fit(Image.fromarray((b16 / 256).astype(np.uint8))).save(out_path(D + "_PREVIEW_bump_whole.jpg"), quality=90)
    # 3 x 3 tiling at reduced scale
    small = fit(c, 800 // 3 + 1)
    t = Image.new("RGB", (small.width * 3, small.height * 3))
    for i in range(3):
        for j in range(3):
            t.paste(small, (i * small.width, j * small.height))
    fit(t).save(out_path(D + "_PREVIEW_colour_tiled3x3.jpg"), quality=90)
    # four-way wrap corner at 1:1
    a = np.asarray(c)
    r = np.roll(np.roll(a, 400, 0), 400, 1)[:800, :800]
    Image.fromarray(r).save(out_path(D + "_PREVIEW_wrap_corner_1to1.jpg"), quality=92)
    rb = np.roll(np.roll(h, 400, 0), 400, 1)[:800, :800]
    Image.fromarray(shade(rb, ppi)).save(out_path(D + "_PREVIEW_wrap_corner_bump_grazing_1to1.jpg"), quality=92)
    # grazing light
    sh = shade(h, ppi)
    fit(Image.fromarray(sh)).save(out_path(D + "_PREVIEW_grazing_bump_whole.jpg"), quality=90)
    cy, cx = H // 2, W // 2
    Image.fromarray(sh[cy - 400:cy + 400, cx - 400:cx + 400]).save(out_path(D + "_PREVIEW_grazing_bump_1to1.jpg"), quality=92)
    Image.fromarray(a[cy - 400:cy + 400, cx - 400:cx + 400]).save(out_path(D + "_PREVIEW_colour_centre_1to1.jpg"), quality=92)
    # labelled cells / source vs built
    if prod == "veincut_24x48":
        mw, mh = rep["module_px"]
        lab = fit(c)
        s = lab.width / W
        dr = ImageDraw.Draw(lab)
        for rr, row in enumerate(rep["cells"]):
            for cc, cell in enumerate(row):
                dr.text((cc * mw * s + 6, rr * mh * s + 4), "%s %s" % (cell["face"], cell["transform"]), fill=(200, 0, 0))
        lab.save(out_path(D + "_PREVIEW_cells_labelled.jpg"), quality=90)
        # source A (u09 native) vs built cell showing A r0, same scale (downsampled to 400 px wide each)
        from common import lin_to_srgb
        A = np.load(out_path("_work/faces/A.npy"))
        srcA = Image.fromarray(np.clip(np.round(lin_to_srgb(A)), 0, 255).astype(np.uint8))
        pos = [(rr, cc) for rr, row in enumerate(rep["cells"]) for cc, cell in enumerate(row)
               if cell["face"] == "A" and cell["transform"] == "r0"]
        if not pos:
            pos = [(rr, cc) for rr, row in enumerate(rep["cells"]) for cc, cell in enumerate(row) if cell["face"] == "A"]
        rr, cc = pos[0]
        cell = c.crop((cc * mw, rr * mh, (cc + 1) * mw, (rr + 1) * mh))
        comp = Image.new("RGB", (800, 440), "white")
        comp.paste(srcA.resize((800, 200), Image.LANCZOS), (0, 0))
        comp.paste(cell.resize((800, 200), Image.LANCZOS), (0, 240))
        dr = ImageDraw.Draw(comp)
        dr.text((5, 205), "top: source A (u09, planar de-lit)   bottom: built cell r%d c%d (%s)" % (
            rr, cc, rep["cells"][rr][cc]["transform"]), fill=(0, 0, 0))
        comp.save(out_path(D + "_PREVIEW_source_vs_built.jpg"), quality=90)
        # 1:1 detail comparison, 400 x 400 px of source (resampled to 36 px/in) and the same area built
        sc = ppi / (A.shape[1] / rep["tile_actual_in"][0])
        As = srcA.resize((int(A.shape[1] * sc), int(A.shape[0] * sc)), Image.LANCZOS)
        comp = Image.new("RGB", (800, 400), "white")
        comp.paste(As.crop((600, 300, 1000, 700)), (0, 0))
        j = int(round(rep["joint_in"] / 2 * ppi))
        cellx = cell if rep["cells"][rr][cc]["transform"] == "r0" else cell
        comp.paste(cellx.crop((600 + j, 300 + j, 1000 + j, 700 + j)), (400, 0))
        comp.save(out_path(D + "_PREVIEW_source_vs_built_1to1.jpg"), quality=92)
    else:
        mw, mh = rep["module_px"]
        # source sheet w07 vs a 12 x 12 in patch of the built map, both scaled to 400 px
        from guard import ref
        w07 = Image.open(ref("web/w07_ms_jute_veincut_1x3mosaic_01.jpg")).convert("RGB")
        u11 = Image.open(ref("user_supplied/u11_mosaic_1x3_installed.png")).convert("RGB")
        n12 = int(12 * ppi)
        patch = c.crop((0, 0, n12, n12))
        comp = Image.new("RGB", (800, 620), "white")
        comp.paste(w07.resize((400, 400), Image.LANCZOS), (0, 0))
        comp.paste(patch.resize((400, 400), Image.LANCZOS), (400, 0))
        uu = fit(u11, 400)
        comp.paste(uu, (0, 410))
        wide = c.crop((0, 0, int(24 * ppi), int(24 * ppi * uu.height / uu.width)))
        comp.paste(wide.resize((400, uu.height), Image.LANCZOS), (400, 410))
        ImageDraw.Draw(comp).text((5, 600), "left: MILE sheet w07 / user u11   right: built map, 12 in sheet / 24 in wide", fill=(0, 0, 0))
        comp.save(out_path(D + "_PREVIEW_source_vs_built.jpg"), quality=90)


if __name__ == "__main__":
    main(sys.argv[1])
