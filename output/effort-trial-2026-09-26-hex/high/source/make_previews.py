"""Step 5: review images from the built maps (textures/*.png) and the render."""

import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import render_geom as g
from common import RENDER_PATH, W, H, PPI, atlas_centres, out_path, RUN_DIR

Image.MAX_IMAGE_PIXELS = None
col = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB")).astype(np.float32) / 255.0
code = np.asarray(Image.open(out_path("textures", "Bump16.png"))).astype(np.float32)
rep = json.load(open(out_path("textures", "report.json")))
enc = rep["relief_mm"]["bump16_encoding"]
hmm = code / 65535.0 * (enc["code_65535_mm"] - enc["code_0_mm"]) + enc["code_0_mm"]
PITCH_MM = 25.4 / PPI

try:
    FONT = ImageFont.truetype("arial.ttf", 22)
    FONT_S = ImageFont.truetype("arial.ttf", 16)
except OSError:
    FONT = FONT_S = ImageFont.load_default()


def shade(h, c, elev_deg=15.0, az_deg=45.0):
    """Lambert shading of the colour by the bump under a low raking light plus a 0.35
    ambient term (no cast shadows); az measured from +x toward the top of the image.
    Flat face = 0.9 x colour; highlights roll off softly instead of clipping."""
    hx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / (2 * PITCH_MM)
    hy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / (2 * PITCH_MM)
    n = np.stack([-hx, -hy, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    e, a = np.radians(elev_deg), np.radians(az_deg)
    l = np.array([np.cos(e) * np.cos(a), -np.cos(e) * np.sin(a), np.sin(e)])
    s = np.clip(n @ l, 0, None) / np.sin(e)
    s = np.where(s > 1, 1 + 0.35 * np.tanh((s - 1) / 0.35 * 1.0), s)   # soft highlight roll-off
    return np.clip(c * (0.35 + 0.55 * s)[..., None], 0, 1)


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def fit(im, maxpx):
    s = maxpx / max(im.size)
    return im.resize((max(1, round(im.size[0] * s)), max(1, round(im.size[1] * s))), Image.LANCZOS) if s < 1 else im


# 1. full atlas
full_img = to_img(col)
fit(full_img, 2000).save(out_path("textures", "_PREVIEW_atlas_full.jpg"), quality=92)

# 2. 2x2 wrap
t2 = fit(full_img, 1000)
w2, h2 = t2.size
tiled = Image.new("RGB", (2 * w2, 2 * h2))
for i in range(2):
    for j in range(2):
        tiled.paste(t2, (i * w2, j * h2))
tiled.save(out_path("textures", "_PREVIEW_wrap_2x2.jpg"), quality=92)

# 3. four-way corner, magnified (colour and grazing light), 3x nearest
graz = shade(hmm, col)
R = 110
def corner(a):
    t = np.concatenate([np.concatenate([a[-R:, -R:], a[-R:, :R]], 1), np.concatenate([a[:R, -R:], a[:R, :R]], 1)], 0)
    return to_img(t).resize((6 * R, 6 * R), Image.NEAREST)
cc, cg = corner(col), corner(graz)
seam = Image.new("RGB", (12 * R + 20, 6 * R + 40), (255, 255, 255))
seam.paste(cc, (0, 40))
seam.paste(cg, (6 * R + 20, 40))
d = ImageDraw.Draw(seam)
d.text((5, 8), "Colour: four tile corners meeting (atlas wrapped), 3x", fill=(0, 0, 0), font=FONT_S)
d.text((6 * R + 25, 8), "Bump under 15 deg raking light, same crop", fill=(0, 0, 0), font=FONT_S)
for x0 in (0, 6 * R + 20):
    d.line([(x0 + 3 * R, 40), (x0 + 3 * R, 40 + 6 * R)], fill=(255, 0, 0), width=1)
    d.line([(x0, 40 + 3 * R), (x0 + 6 * R, 40 + 3 * R)], fill=(255, 0, 0), width=1)
seam.save(out_path("textures", "_REVIEW_wrap_seam.jpg"), quality=92)

# 4. face types labelled
ft = fit(full_img, 2000)
sc = ft.size[0] / W
d = ImageDraw.Draw(ft)
faces = {f["index"]: f for f in rep["faces"]}
colours = {"matte": (40, 40, 40), "raw": (170, 40, 20), "chiseled": (20, 60, 170)}
for idx, c, r, cx, cy in atlas_centres():
    f = faces[idx]
    lab = "%d %s" % (idx, f["type"])
    lab2 = ""
    if f["type"] == "chiseled":
        lab2 = "grooves %.0f deg" % f["groove_orientation_deg"]
    elif "cells" in f:
        lab2 = "mosaic"
    for ox in (-W, 0, W):
        for oy in (-H, 0, H):
            x, y = (cx + ox) * sc, (cy + oy) * sc
            if -60 < x < ft.size[0] + 60 and -30 < y < ft.size[1] + 30:
                d.text((x - 55, y - 14), lab, fill=colours[f["type"]], font=FONT)
                if lab2:
                    d.text((x - 50, y + 12), lab2, fill=colours[f["type"]], font=FONT_S)
ft.save(out_path("textures", "_REVIEW_face_types.jpg"), quality=92)

# 5. grazing light, full atlas
fit(to_img(graz), 2000).save(out_path("textures", "_PREVIEW_grazing_light.jpg"), quality=92)

# 6. 1:1 crops per type next to the render at the same physical scale
render = Image.open(RENDER_PATH).convert("RGB")
CROP_IN = 5.0
cpx = int(CROP_IN * PPI)                 # 320 atlas px
panels = []
for t in ("matte", "raw", "chiseled"):
    f = next(f for f in rep["faces"] if f["type"] == t and "cells" not in f)
    idx = f["index"]
    cx, cy = next((a, b) for i, _, _, a, b in atlas_centres() if i == idx)
    xs = (np.arange(int(cx - cpx / 2), int(cx - cpx / 2) + cpx)) % W
    ys = (np.arange(int(cy - cpx / 2), int(cy - cpx / 2) + cpx)) % H
    a_c = to_img(col[np.ix_(ys, xs)])
    a_g = to_img(graz[np.ix_(ys, xs)])
    sx, sy = f["source_render_centre_xy"]
    rh = CROP_IN * g.RPPI / 2
    # render crop in the source orientation, upsampled to the same px/in (bicubic)
    r_c = render.crop((int(sx - rh), int(sy - rh), int(sx - rh) + int(2 * rh), int(sy - rh) + int(2 * rh))).resize((cpx, cpx), Image.BICUBIC)
    panels.append((t, idx, f, r_c, a_c, a_g))
pad, top = 12, 34
out = Image.new("RGB", (3 * cpx + 4 * pad, 3 * (cpx + top) + pad), (255, 255, 255))
d = ImageDraw.Draw(out)
for k, (t, idx, f, r_c, a_c, a_g) in enumerate(panels):
    y = k * (cpx + top) + top
    for j, (im, lab) in enumerate(((r_c, "render (source orientation) %s" % t),
                                  (a_c, "atlas face %d colour (rot %s, mirror %s)" % (idx, f["rotation_deg"], f["mirrored"])),
                                  (a_g, "atlas face %d, 15 deg raking light" % idx))):
        x = pad + j * (cpx + pad)
        out.paste(im, (x, y))
        d.text((x, y - 22), lab, fill=(0, 0, 0), font=FONT_S)
d.text((pad, 3 * (cpx + top) - 8), "each crop = 5 in square at 64 px/in (render upsampled from %.1f px/in)" % g.RPPI, fill=(0, 0, 0), font=FONT_S)
out.save(out_path("textures", "_REVIEW_crops_1to1.jpg"), quality=93)
print("previews written")
