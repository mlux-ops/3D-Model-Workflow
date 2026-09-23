"""Review previews for the ELM Fog Cross-Cut Chevron 24x48 maps (diagnostic only).

Shading here is a simple Lambertian diagnostic computed from the 16-bit bump in
millimetres. It is not a Revit or renderer image.
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

import chevron_common as cc
import grooves

T = os.path.join(cc.PROD, "textures")
NAME = "ELM_Fog_CrossCut_Chevron_24x48"
REP = json.load(open(os.path.join(T, "build_report.json")))
PPI = REP["px_per_in"]
PX_MM = 25.4 / PPI


def save(img, name, q=90):
    p = os.path.abspath(os.path.join(T, name))
    assert p.startswith(os.path.abspath(cc.PROD) + os.sep)
    img.save(p, quality=q)
    print("wrote", name, img.size)


def shade(h_mm, az_deg, el_deg, px_mm=PX_MM):
    gy, gx = np.gradient(h_mm, px_mm)
    nx, ny, nz = -gx, -gy, np.ones_like(h_mm)
    n = np.sqrt(nx * nx + ny * ny + 1)
    az, el = np.radians(az_deg), np.radians(el_deg)
    l = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    s = (nx * l[0] + ny * l[1] + nz * l[2]) / n
    return np.clip(s, 0, 1) / np.sin(el)      # 1.0 = flat face


def tile(a, nx, ny):
    return np.tile(a, (ny, nx) + (1,) * (a.ndim - 2))


def to_img(a, lo=0.0, hi=255.0):
    return Image.fromarray(np.clip((a - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8))


def down(img, width):
    return img.resize((width, int(round(img.size[1] * width / img.size[0]))), Image.LANCZOS)


def main():
    col = np.asarray(Image.open(os.path.join(T, NAME + "_Color.png"))).astype(np.float64)
    bmp = np.asarray(Image.open(os.path.join(T, NAME + "_Bump16.png"))).astype(np.float64) / 65535.0 * REP["relief"]["height_range_mm"]
    rgh = np.asarray(Image.open(os.path.join(T, NAME + "_Roughness.png"))).astype(np.float64)
    H, W = bmp.shape
    cw, ch = W // 3, H // 4

    # 1. whole atlas, clean and labelled
    save(down(Image.fromarray(col.astype(np.uint8)), 1800), "_PREVIEW_atlas_full.jpg")
    lab = down(Image.fromarray(col.astype(np.uint8)), 1800)
    d = ImageDraw.Draw(lab)
    sc = 1800 / W
    for cell in REP["cells"]:
        x, y = cell["col"] * cw * sc, cell["row"] * ch * sc
        d.rectangle([x + 2, y + 2, x + cw * sc - 3, y + ch * sc - 3], outline=(200, 0, 0), width=2)
        d.text((x + 10, y + 8), "r%d c%d  %s%s  %s  X0 %.1f in" % (cell["row"], cell["col"], cell["face"],
               " rot180" if cell["rot180"] else "", cell["row_type"], cell["groove_slab_offset_in"]), fill=(160, 0, 0))
    save(lab, "_REVIEW_cell_grid.jpg")

    # 2. 3x3 repetition of each map (432 x 288 in)
    save(down(Image.fromarray(tile(col, 3, 3).astype(np.uint8)), 1800), "_PREVIEW_tiling3x3_color.jpg")
    sh = shade(bmp, 180.0, 15.0)
    save(down(to_img(tile(sh, 3, 3), 0.0, 2.0), 1800), "_PREVIEW_tiling3x3_bump_grazing.jpg")
    save(down(to_img(tile(rgh, 3, 3), 120, 240), 1800), "_PREVIEW_tiling3x3_roughness.jpg")

    # 3. grazing light over the whole atlas, colour x shading, two light azimuths
    for az, tag in ((180.0, "left"), (270.0, "top")):
        s = shade(bmp, az, 15.0)
        lit = np.clip(col * (0.35 + 0.65 * s[..., None] / 1.0), 0, 255)
        save(down(Image.fromarray(lit.astype(np.uint8)), 1800), "_PREVIEW_grazing_light_%s.jpg" % tag)

    # 4. native-resolution close-up of one tile corner region, grazing 12 deg from the left
    y0, x0 = ch - 260, cw - 520            # straddles a four-way joint corner
    crop_h = bmp[y0:y0 + 520, x0:x0 + 1040]
    crop_c = col[y0:y0 + 520, x0:x0 + 1040]
    s = shade(crop_h, 200.0, 12.0)
    lit = np.clip(crop_c * (0.30 + 0.70 * s[..., None]), 0, 255)
    save(Image.fromarray(lit.astype(np.uint8)).resize((2080, 1040), Image.LANCZOS), "_PREVIEW_relief_closeup_grazing.jpg")
    save(Image.fromarray(crop_c.astype(np.uint8)).resize((2080, 1040), Image.LANCZOS), "_PREVIEW_relief_closeup_color.jpg")

    # 5. four-way wrap seam of the atlas itself, magnified (colour | bump shading | roughness)
    k = 96
    def corner(a):
        t2 = tile(a, 2, 2)
        return t2[H - k:H + k, W - k:W + k]
    cc_ = corner(col)
    cb = corner(shade(bmp, 200.0, 20.0))
    cr = corner(rgh)
    grey3 = lambda im: np.repeat(np.asarray(im)[..., None], 3, 2).astype(np.float64)
    strip = np.concatenate([cc_, grey3(to_img(cb, 0, 2.0)), grey3(to_img(cr, 120, 240))], 1)
    save(Image.fromarray(strip.astype(np.uint8)).resize((strip.shape[1] * 4, strip.shape[0] * 4), Image.NEAREST),
         "_REVIEW_wrap_seam.jpg")

    # 6. wall-scale view: 20 ft x 9 ft wall, atlas repeated from the lower-left
    wall_w, wall_h = int(240 * PPI), int(108 * PPI)
    reps_x, reps_y = int(np.ceil(wall_w / W)), int(np.ceil(wall_h / H))
    wall = tile(col, reps_x, reps_y)[-wall_h:, :wall_w]
    # symmetric light (az 180) so neither groove direction is favoured at wall scale
    wsh = tile(shade(bmp, 180.0, 25.0), reps_x, reps_y)[-wall_h:, :wall_w]
    wall = np.clip(wall * (0.45 + 0.55 * wsh[..., None]), 0, 255)
    save(down(Image.fromarray(wall.astype(np.uint8)), 1800), "_PREVIEW_wall_scale_20x9ft.jpg")

    # 7. source faces as used (de-grooved, tone-matched), plus the de-groove before/after
    slab = cc.load_slab()
    dg, _, _, _ = grooves.degroove_slab(slab)
    a = Image.fromarray(np.clip(slab[545:745, 2000:2400], 0, 255).astype(np.uint8)).resize((800, 400), Image.LANCZOS)
    b = Image.fromarray(np.clip(dg[545:745, 2000:2400], 0, 255).astype(np.uint8)).resize((800, 400), Image.LANCZOS)
    both = Image.new("RGB", (800, 810), (255, 0, 0))
    both.paste(a, (0, 0))
    both.paste(b, (0, 410))
    save(both, "_REVIEW_degroove_before_after.jpg")
    th = down(Image.fromarray(np.clip(dg, 0, 255).astype(np.uint8)), 1600)
    save(th, "_REVIEW_source_slab_degrooved.jpg")


if __name__ == "__main__":
    main()
