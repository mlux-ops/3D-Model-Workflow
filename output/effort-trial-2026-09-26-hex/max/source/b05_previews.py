"""Build step 5: preview and review images (all JPEG, written through the guard).

  textures/_PREVIEW_atlas_full.jpg        Color.png, long side 2000 px
  textures/_PREVIEW_wrap_2x2.jpg          2 x 2 repeat, long side 2000 px
  textures/_REVIEW_wrap_seam.jpg          four-way corner of the repeat, colour + bump, x3
  textures/_REVIEW_face_types.jpg         atlas labelled with index / type / rotation
  textures/_PREVIEW_grazing_light.jpg     colour shaded by the bump, light 15 deg above the
                                          wall from the left, with cast shadows
  textures/_PREVIEW_grazing_light_detail.jpg   1:1 grazing crops of each face type
  textures/_REVIEW_crops_1to1.jpg         1:1 atlas crop of each type beside the matching
                                          render region at the same physical scale
"""

import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from common import (COLS, ROWS, W, H, PX_PER_IN_X, PX_PER_IN_Y, COL_PITCH_IN, ROW_PITCH_IN,
                    out_path, render_rgb, srgb_to_lin, lin_to_srgb)
from guard import save_image

LIGHT_ELEV_DEG = 15.0
AMBIENT = 0.25


def font(sz):
    for p in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def fit_width(im, w):
    """Resize so the LONGER side is w px (previews must be <= 2000 px)."""
    k = w / float(max(im.width, im.height))
    return im.resize((int(round(im.width * k)), int(round(im.height * k))), Image.LANCZOS)


def grazing(col_lin, h_mm, elev_deg=LIGHT_ELEV_DEG, from_left=True):
    """Lambertian shading of the height field (mm) at 64 px/in with cast shadows."""
    px_mm = 25.4 / 64.0
    hp = np.pad(h_mm, ((1, 1), (1, 1)), mode="wrap")
    gx = (hp[1:-1, 2:] - hp[1:-1, :-2]) / (2 * px_mm)
    gy = (hp[2:, 1:-1] - hp[:-2, 1:-1]) / (2 * px_mm)
    t = np.deg2rad(elev_deg)
    lx = -np.cos(t) if from_left else np.cos(t)      # toward the light (image x)
    lz = np.sin(t)
    nz = 1.0 / np.sqrt(1 + gx * gx + gy * gy)
    ndl = (-gx * lx + lz) * nz                       # n = (-gx, -gy, 1)/|.|, light has no y part
    shade = np.clip(ndl, 0, None) / lz
    # cast shadows: sweep along the light direction, periodic prefix of 600 px
    tan_t = np.tan(t)
    step = px_mm * tan_t
    pre = 600
    hh = np.concatenate([h_mm[:, -pre:], h_mm], axis=1) if from_left else None
    s = np.full(h_mm.shape[0], -np.inf)
    lit = np.ones_like(h_mm, dtype=bool)
    for x in range(hh.shape[1]):
        col = hh[:, x]
        if x >= pre:
            lit[:, x - pre] = col >= s - 1e-6
        # horizon for the next pixel: every earlier pixel drops by one light step
        s = np.maximum(s, col) - step
    shade = np.where(lit, shade, 0.0)
    f = AMBIENT + (1 - AMBIENT) * shade
    return col_lin * f[..., None]


def main():
    bf = json.load(open(out_path("_work", "build_faces.json")))
    col8 = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB"))
    b16 = np.asarray(Image.open(out_path("textures", "Bump16.png"))).astype(np.float64)
    fid = np.asarray(Image.open(out_path("textures", "face_ids.png"))).astype(np.int32)
    hrange = bf["params_mm"]["h_range"]
    h_mm = b16 / 65535.0 * hrange
    im = Image.fromarray(col8)
    # 1 atlas full
    save_image(fit_width(im, 2000), "textures", "_PREVIEW_atlas_full.jpg", quality=92)
    # 2 wrap 2x2
    t2 = np.tile(col8, (2, 2, 1))
    save_image(fit_width(Image.fromarray(t2), 2000), "textures", "_PREVIEW_wrap_2x2.jpg", quality=92)
    # 3 wrap seams, colour | bump, x3: the four-way corner, then the edges where they cut
    #   through textured faces (Raw 25 left/right, Raw 52 top/bottom, Chiseled 24 left/right)
    r = 110
    b2full = np.tile(b16, (2, 2))
    panels = [("four-way corner", H, W, True, True),
              ("left/right edge through Raw face 25", 2268, W, False, True),
              ("top/bottom edge through Raw face 52", H, 1964, True, False),
              ("left/right edge through Chiseled face 24", 1944, W, False, True)]
    rowsimg = []
    for title, yc, xc, hline, vline in panels:
        cc = t2[yc - r:yc + r, xc - r:xc + r]
        b2 = b2full[yc - r:yc + r, xc - r:xc + r]
        lo, hi = np.percentile(b2, 1), np.percentile(b2, 99.5)
        bb = np.clip((b2 - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
        pc = Image.fromarray(cc).resize((2 * r * 3, 2 * r * 3), Image.NEAREST)
        pb = Image.fromarray(bb).convert("RGB").resize((2 * r * 3, 2 * r * 3), Image.NEAREST)
        canvas = Image.new("RGB", (2 * r * 3 * 2 + 20, 2 * r * 3 + 40), (255, 255, 255))
        canvas.paste(pc, (0, 40)); canvas.paste(pb, (2 * r * 3 + 20, 40))
        d = ImageDraw.Draw(canvas)
        for x0 in (0, 2 * r * 3 + 20):
            if vline:
                d.line([(x0 + r * 3, 40), (x0 + r * 3, 48)], fill=(255, 0, 0), width=3)
                d.line([(x0 + r * 3, 32 + 2 * r * 3), (x0 + r * 3, 40 + 2 * r * 3)], fill=(255, 0, 0), width=3)
            if hline:
                d.line([(x0, 40 + r * 3), (x0 + 8, 40 + r * 3)], fill=(255, 0, 0), width=3)
                d.line([(x0 + 2 * r * 3 - 8, 40 + r * 3), (x0 + 2 * r * 3, 40 + r * 3)], fill=(255, 0, 0), width=3)
        d.text((5, 8), "Wrap seam, %s (red ticks = image edge), colour | bump, x3" % title,
               fill=(0, 0, 0), font=font(18))
        rowsimg.append(np.asarray(canvas))
    save_image(Image.fromarray(np.concatenate(rowsimg, axis=0)), "textures", "_REVIEW_wrap_seam.jpg", quality=92)
    # 4 face types labelled
    lab = fit_width(im, 2000)
    s = lab.width / float(W)
    d = ImageDraw.Draw(lab)
    fn = font(20)
    for f in bf["faces"]:
        i, j = f["i"], f["j"]
        cx = (i + 0.5) * COL_PITCH_IN * PX_PER_IN_X
        cy = ((j + 0.5) * ROW_PITCH_IN + (ROW_PITCH_IN / 2 if i % 2 else 0)) * PX_PER_IN_Y
        cy = cy % H
        if cy > H - 120 or cy < 60:
            cy = 70
        txt = "%d %s" % (f["index"], {"matte": "MATTE", "raw": "RAW", "chiseled": "CHIS"}[f["type"]])
        if f["type"] == "chiseled":
            txt += "\nrot %d" % f["rotation_deg"]
        colr = {"matte": (40, 40, 40), "raw": (180, 0, 0), "chiseled": (0, 60, 200)}[f["type"]]
        x, y = cx * s, cy * s
        d.multiline_text((x - 38, y - 14), txt, fill=colr, font=fn, align="center",
                         stroke_width=2, stroke_fill=(255, 255, 255))
    save_image(lab, "textures", "_REVIEW_face_types.jpg", quality=92)
    # 5 grazing light
    col_lin = srgb_to_lin(col8.astype(np.float64))
    g = grazing(col_lin, h_mm)
    g8 = np.round(lin_to_srgb(g)).astype(np.uint8)
    save_image(fit_width(Image.fromarray(g8), 2000), "textures", "_PREVIEW_grazing_light.jpg", quality=92)
    # detail crops, 1:1: one face of each type (and each chiseled rotation)
    picks = []
    for typ, rotd in (("matte", None), ("raw", None), ("chiseled", 0), ("chiseled", 60), ("chiseled", 300), ("chiseled", 120)):
        for f in bf["faces"]:
            if f["type"] == typ and (rotd is None or f["rotation_deg"] == rotd):
                picks.append(f)
                break
    tiles = []
    for f in picks:
        i, j = f["i"], f["j"]
        cx = int((i + 0.5) * COL_PITCH_IN * PX_PER_IN_X)
        cy = int(((j + 0.5) * ROW_PITCH_IN + (ROW_PITCH_IN / 2 if i % 2 else 0)) * PX_PER_IN_Y) % H
        ys = np.arange(cy - 130, cy + 130) % H
        xs = np.arange(cx - 130, cx + 130) % W
        tiles.append(g8[np.ix_(ys, xs)])
    rows = [np.concatenate(tiles[k:k + 3], axis=1) for k in range(0, len(tiles), 3)]
    det = Image.fromarray(np.concatenate(rows, axis=0))
    save_image(det, "textures", "_PREVIEW_grazing_light_detail.jpg", quality=92)
    # 6 crops 1:1 vs render at the same physical scale
    src = json.load(open(out_path("_work", "sources.json")))
    rfaces = {x["id"]: x for x in src["faces"]}
    rgb = render_rgb().astype(np.uint8)
    ppi_r = src["ppi_render"]
    half_px = 180                                  # 360 px = 5.63 in at 64 px/in
    half_in = half_px / 64.0
    rows = []
    pairs = [("matte", None, 20), ("raw", None, 29), ("chiseled", 0, 11), ("chiseled", 60, 30)]
    fn2 = font(16)
    for typ, rotd, rid in pairs:
        f = [x for x in bf["faces"] if x["type"] == typ and (rotd is None or x["rotation_deg"] == rotd)][0]
        i, j = f["i"], f["j"]
        cx = int((i + 0.5) * COL_PITCH_IN * PX_PER_IN_X)
        cy = int(((j + 0.5) * ROW_PITCH_IN + (ROW_PITCH_IN / 2 if i % 2 else 0)) * PX_PER_IN_Y) % H
        ys = np.arange(cy - half_px, cy + half_px) % H
        xs = np.arange(cx - half_px, cx + half_px) % W
        a = Image.fromarray(col8[np.ix_(ys, xs)])
        rf = rfaces[rid]
        rx0 = int(round(rf["cx"] - half_in * ppi_r)); ry0 = int(round(rf["cy"] - half_in * ppi_r))
        rw = int(round(2 * half_in * ppi_r))
        b = Image.fromarray(rgb[ry0:ry0 + rw, rx0:rx0 + rw]).resize((2 * half_px, 2 * half_px), Image.BICUBIC)
        row = Image.new("RGB", (4 * half_px + 10, 2 * half_px + 26), (255, 255, 255))
        row.paste(a, (0, 26)); row.paste(b, (2 * half_px + 10, 26))
        dd = ImageDraw.Draw(row)
        dd.text((4, 4), "atlas face %d %s%s (1:1, 5.6 in)" % (f["index"], typ, "" if rotd is None else " rot %d" % rotd),
                fill=(0, 0, 0), font=fn2)
        dd.text((2 * half_px + 14, 4), "render face %d, same scale (x%.2f)" % (rid, 64.0 / ppi_r),
                fill=(0, 0, 0), font=fn2)
        rows.append(np.asarray(row))
    save_image(Image.fromarray(np.concatenate(rows, axis=0)), "textures", "_REVIEW_crops_1to1.jpg", quality=93)
    print("previews written")


if __name__ == "__main__":
    sys.exit(main())
