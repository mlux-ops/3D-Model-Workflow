"""Step 12: review images written next to the textures (all <= 2000 px wide; the review views
were made from thumbnails or crops of these, <= 800 px wide).

Two raking lights, both at EL_DEG elevation:
  light B  from the upper left (the render's light axis turned 90 deg). It is the main light of the
           previews because all three Chiseled groove sets are lit across their grooves
           (cos to the groove normals 0.55 / 0.45 / 1.0).
  light R  along the render's own light axis, the direction the source shading was measured with
           (lower left). The Chiseled set whose grooves run almost parallel to it is nearly blind
           to it, which is a property of the light, not of the map.

_PREVIEW_atlas_full.jpg      colour atlas
_PREVIEW_wrap_2x2.jpg        colour atlas tiled 2 x 2
_PREVIEW_wrap_2x2_grazing.jpg  the same under light B
_REVIEW_wrap_seam.jpg        four-way wrap corner, magnified 2x (nearest): colour | light B |
                             bump | light R
_REVIEW_face_types.jpg       light-B atlas with every face labelled by index and type
_PREVIEW_grazing_light.jpg   colour shaded by the bump map under light B
_PREVIEW_grazing_light_renderlight.jpg  the same under light R
_REVIEW_crops_1to1.jpg       per type: atlas crop (1:1) | render region at the same physical scale
                             (x2.058) | atlas under light R | atlas under light B"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import save_image, out_path, load_gray16, RENDER_PATH  # noqa: E402
from geometry import W, H, MM_PER_PX, face_centres, source_to_atlas_scale  # noqa: E402
from s02_profile_grid import load_srgb  # noqa: E402
from s08_raw_height import face_centre  # noqa: E402

EL_DEG = 20.0


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def shade(colour, hmm, az_deg, el_deg=EL_DEG, gain=0.9):
    """colour uint8 (h,w,3), hmm float32 mm (h,w) -> uint8 shaded colour (Lambert, distant light)."""
    az, el = np.deg2rad(az_deg), np.deg2rad(el_deg)
    lx, ly, lz = np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)
    gy, gx = np.gradient(hmm, MM_PER_PX)
    r = (lz - gx * lx - gy * ly) / np.sqrt(1.0 + gx * gx + gy * gy) / lz
    r = np.clip(gain * r, 0.0, 1.25)
    return np.clip(colour.astype(np.float32) * r[..., None], 0, 255).astype(np.uint8)


def to_width(arr, width, resample=Image.LANCZOS):
    im = Image.fromarray(arr)
    h = int(round(im.height * width / im.width))
    return im.resize((width, h), resample)


def save_jpg(im, name):
    save_image(im, "textures", name, quality=90, subsampling=0)


def crop_wrap(arr, cx, cy, half):
    ys = (np.arange(cy - half, cy + half)) % arr.shape[0]
    xs = (np.arange(cx - half, cx + half)) % arr.shape[1]
    return arr[np.ix_(ys, xs)]


def main():
    build = json.load(open(out_path("work", "build_stats.json")))
    full_mm = build["full_scale_mm"]
    layout = json.load(open(out_path("work", "layout.json")))
    faces = layout["faces"]
    centres = face_centres()
    psi_light = json.load(open(out_path("work", "pool_raw_info.json")))["psi_toward_light_deg"]
    colour = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB"))
    hmm = load_gray16(out_path("textures", "Bump16.png")).astype(np.float32) * (full_mm / 65535.0)
    print("loaded", colour.shape, hmm.shape, "light toward", psi_light)

    save_jpg(to_width(colour, 2000), "_PREVIEW_atlas_full.jpg")

    az_r, az_b = psi_light, psi_light + 90.0
    sh1 = shade(colour, hmm, az_b)
    save_jpg(to_width(sh1, 2000), "_PREVIEW_grazing_light.jpg")
    sh2 = shade(colour, hmm, az_r)
    save_jpg(to_width(sh2, 2000), "_PREVIEW_grazing_light_renderlight.jpg")
    del sh2

    for name, arr in (("_PREVIEW_wrap_2x2.jpg", colour), ("_PREVIEW_wrap_2x2_grazing.jpg", sh1)):
        big = np.tile(arr, (2, 2, 1))
        save_jpg(to_width(big, 2000), name)
        del big

    half = 96
    panels = []
    for arr in (colour, sh1):
        panels.append(crop_wrap(np.roll(arr, (H // 2, W // 2), axis=(0, 1)), W // 2, H // 2, half))
    hg = np.roll(hmm, (H // 2, W // 2), axis=(0, 1))
    hc = crop_wrap(hg, W // 2, H // 2, half)
    lo, hi = np.percentile(hc, [1, 99])
    hgrey = np.clip((hc - lo) / (hi - lo + 1e-9), 0, 1)
    panels.append(np.repeat((hgrey * 255).astype(np.uint8)[..., None], 3, axis=2))
    cg = np.roll(colour, (H // 2, W // 2), axis=(0, 1))
    panels.append(crop_wrap(shade(cg, hg, az_r), W // 2, H // 2, half))
    mag = [np.asarray(Image.fromarray(p).resize((2 * half * 2, 2 * half * 2), Image.NEAREST)) for p in panels]
    grid = np.vstack([np.hstack(mag[:2]), np.hstack(mag[2:])])
    im = Image.fromarray(grid)
    d = ImageDraw.Draw(im)
    step = 4 * half
    for ox, oy in ((0, 0), (step, 0), (0, step), (step, step)):
        m = 2 * half
        d.polygon([(ox + m - 6, oy), (ox + m + 6, oy), (ox + m, oy + 8)], fill=(255, 0, 0))
        d.polygon([(ox, oy + m - 6), (ox, oy + m + 6), (ox + 8, oy + m)], fill=(255, 0, 0))
    save_jpg(im, "_REVIEW_wrap_seam.jpg")

    lab = to_width(sh1, 1600)
    sc = 1600.0 / W
    d = ImageDraw.Draw(lab)
    f_small = font(15)
    colours = {"matte": (0, 90, 0), "raw": (200, 0, 0), "chiseled": (0, 0, 200)}
    short = {"vert": "vert", "diagS": "diagS", "diagF": "diagF"}
    for f, c in zip(faces, centres):
        txt = "%d %s" % (f["index"], f["type"] if f["type"] != "chiseled" else "chis-" + short[f["orientation"]])
        x, y = c["cx"] * sc, c["cy"] * sc
        for ox in (0, W):
            for oy in (0, H):
                xx, yy = x - ox * sc, y - oy * sc
                if -80 < xx < 1680 and -30 < yy < lab.height + 30:
                    d.text((xx, yy), txt, font=f_small, fill=colours[f["type"]], anchor="mm",
                           stroke_width=2, stroke_fill=(255, 255, 255))
    save_jpg(lab, "_REVIEW_face_types.jpg")

    pool_info = json.load(open(out_path("work", "pool_info.json")))
    grid_j = json.load(open(out_path("work", "render_grid.json")))
    render = load_srgb(RENDER_PATH)
    scale = source_to_atlas_scale()
    size = 256
    src_half = size / scale / 2.0
    kinds = [("matte", None), ("raw", None), ("chiseled", "vert"), ("chiseled", "diagS"), ("chiseled", "diagF")]
    render_pick = {
        ("matte", None): tuple(pool_info["matte"][0]),
        ("raw", None): (1, 1),
    }
    for c_ in pool_info["chiseled"]:
        render_pick.setdefault(("chiseled", c_["kind"]), (c_["i"], c_["j"]))
    rows = []
    for typ, ori in kinds:
        k = next(i for i, f in enumerate(faces) if f["type"] == typ and (ori is None or f["orientation"] == ori))
        c = centres[k]
        cx, cy = int(round(c["cx"])), int(round(c["cy"]))
        a_col = crop_wrap(colour, cx, cy, size // 2)
        a_h = crop_wrap(hmm, cx, cy, size // 2)
        a_sh_r = shade(a_col, a_h, az_r)
        a_sh_b = shade(a_col, a_h, az_b)
        ri, rj = render_pick[(typ, ori)]
        rcx, rcy = face_centre(grid_j, ri, rj)
        x0, y0 = int(round(rcx - src_half)), int(round(rcy - src_half))
        x1, y1 = x0 + int(round(2 * src_half)), y0 + int(round(2 * src_half))
        r_crop = np.clip(render[y0:y1, x0:x1], 0, 255).astype(np.uint8)
        r_big = np.asarray(Image.fromarray(r_crop).resize((size, size), Image.LANCZOS))
        row = np.hstack([a_col, r_big, a_sh_r, a_sh_b])
        im = Image.fromarray(row)
        dd = ImageDraw.Draw(im)
        dd.text((4, 4), "atlas face %d (%s%s)" % (faces[k]["index"], typ, "" if ori is None else " " + ori),
                font=font(13), fill=(0, 0, 0), stroke_width=2, stroke_fill=(255, 255, 255))
        dd.text((size + 4, 4), "render face (%d,%d) x%.3f" % (ri, rj, scale), font=font(13), fill=(0, 0, 0),
                stroke_width=2, stroke_fill=(255, 255, 255))
        dd.text((2 * size + 4, 4), "atlas, light R (render's)", font=font(13), fill=(0, 0, 0),
                stroke_width=2, stroke_fill=(255, 255, 255))
        dd.text((3 * size + 4, 4), "atlas, light B", font=font(13), fill=(0, 0, 0),
                stroke_width=2, stroke_fill=(255, 255, 255))
        rows.append(np.asarray(im))
    save_jpg(Image.fromarray(np.vstack(rows)), "_REVIEW_crops_1to1.jpg")
    print("previews written")


if __name__ == "__main__":
    main()
