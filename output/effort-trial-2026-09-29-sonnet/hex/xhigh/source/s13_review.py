"""Review images built from the finished maps (Color.png, Bump16.png, face_ids.png, work/face_info.json)."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
THUMB = rg.WORK + "thumbs/"
info = json.load(open(rg.WORK + "face_info.json"))
P = info["params"]
W, H = P["W"], P["H"]
FULL_MM = P["FULL_MM"]
PX_MM = 25.4 / P["PPI"]

color = np.asarray(Image.open(TEX + "Color.png").convert("RGB"))
bump = np.asarray(Image.open(TEX + "Bump16.png"))
ids = np.asarray(Image.open(TEX + "face_ids.png"))
assert color.shape == (H, W, 3) and bump.shape == (H, W) and ids.shape == (H, W)


def fit(img, longest):
    h, w = img.size[1], img.size[0]
    s = longest / max(h, w)
    return img.resize((int(round(w * s)), int(round(h * s))), Image.LANCZOS)


def save_jpg(img, name, q=92):
    guard.save_image(img, TEX + name, quality=q)


def tile2(a):
    return np.concatenate([np.concatenate([a, a], axis=1)] * 2, axis=0)


def crop_wrapped(a, cy, cx, hh, ww):
    ys = (np.arange(cy - hh // 2, cy - hh // 2 + hh)) % a.shape[0]
    xs = (np.arange(cx - ww // 2, cx - ww // 2 + ww)) % a.shape[1]
    return a[np.ix_(ys, xs)]


def grazing(colr, bmp, elev=18.0, az=225.0, brightness=0.72):
    h = bmp.astype(np.float32) * (FULL_MM / 65535.0)
    out = np.empty_like(colr)
    e, a = np.radians(elev), np.radians(az)
    L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)], np.float32)
    step = 512
    for y0 in range(0, h.shape[0], step):
        y1 = min(y0 + step, h.shape[0])
        ys = np.arange(y0 - 1, y1 + 1) % h.shape[0]
        blk = h[ys]
        mid = blk[1:-1]
        gy = (blk[2:] - blk[:-2]) / (2 * PX_MM)
        gx = (np.roll(mid, -1, axis=1) - np.roll(mid, 1, axis=1)) / (2 * PX_MM)
        I = (-gx * L[0] - gy * L[1] + L[2]) / np.sqrt(gx * gx + gy * gy + 1.0)
        f = np.clip(I / np.sin(e), 0.12, 2.6)
        out[y0:y1] = np.clip(colr[y0:y1].astype(np.float32) * (brightness * f)[..., None], 0, 255).astype(np.uint8)
    return out


def font(size):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size=size)


# 1. full atlas preview
save_jpg(fit(Image.fromarray(color), 2000), "_PREVIEW_atlas_full.jpg")
print("wrote _PREVIEW_atlas_full.jpg")

# 2. 2x2 wrap preview
save_jpg(fit(Image.fromarray(tile2(color)), 2000), "_PREVIEW_wrap_2x2.jpg")
print("wrote _PREVIEW_wrap_2x2.jpg")

# 3. wrap seam review: four-way corner (atlas corner and the top edge through an odd-column face), colour + bump, magnified
bimg = (bump >> 8).astype(np.uint8)
panels = []
for (cy, cx) in ((0, 0), (0, int(round(1 * P["COLP"])))):
    a = crop_wrapped(color, cy, cx, 240, 240)
    b = np.repeat(crop_wrapped(bimg, cy, cx, 240, 240)[..., None], 3, axis=2)
    pa = Image.fromarray(a).resize((600, 600), Image.LANCZOS)
    pb = Image.fromarray(b).resize((600, 600), Image.LANCZOS)
    panels.append((pa, pb))
sheet = Image.new("RGB", (1200 + 10, 1200 + 10), (255, 0, 255))
sheet.paste(panels[0][0], (0, 0))
sheet.paste(panels[0][1], (610, 0))
sheet.paste(panels[1][0], (0, 610))
sheet.paste(panels[1][1], (610, 610))
d = ImageDraw.Draw(sheet)
f18 = font(20)
for (x, y, t) in ((8, 8, "corner (0,0) colour, 2.5x"), (618, 8, "corner (0,0) Bump16 (high byte), 2.5x"), (8, 618, "top edge x=561 colour, 2.5x"), (618, 618, "top edge x=561 Bump16, 2.5x")):
    d.text((x, y), t, fill=(255, 0, 0), font=f18, stroke_width=2, stroke_fill=(255, 255, 255))
save_jpg(sheet, "_REVIEW_wrap_seam.jpg")
print("wrote _REVIEW_wrap_seam.jpg")

# 4. face types with labels
scale = 1800 / W
lab = fit(Image.fromarray(color), 1800)
d = ImageDraw.Draw(lab)
fnt = font(22)
tcol = {"matte": (40, 90, 220), "raw": (220, 40, 40), "chiseled": (20, 150, 60)}
tshort = {"matte": "matte", "raw": "raw", "chiseled": "chis"}
for fc in info["faces"]:
    for sx in (-1, 0, 1):
        for sy in (-1, 0, 1):
            x = (fc["cx"] + sx * W) * scale
            y = (fc["cy"] + sy * H) * scale
            if -60 <= x <= lab.size[0] + 60 and -60 <= y <= lab.size[1] + 60:
                txt = "%d\n%s" % (fc["index"], tshort[fc["type"]])
                if fc["type"] == "chiseled":
                    txt += " %d" % fc["rotation_deg"]
                d.multiline_text((x - 30, y - 24), txt, fill=tcol[fc["type"]], font=fnt, stroke_width=3, stroke_fill=(255, 255, 255), align="center")
save_jpg(lab, "_REVIEW_face_types.jpg")
print("wrote _REVIEW_face_types.jpg")

# 5. grazing light
gz = grazing(color, bump)
save_jpg(fit(Image.fromarray(gz), 2000), "_PREVIEW_grazing_light.jpg")
guard.save_image(Image.fromarray(gz), rg.WORK + "grazing_full.png")
print("wrote _PREVIEW_grazing_light.jpg")

# 6. 1:1 crops beside the render at the same physical scale
render = rg.load_render()
feats = {(f["i"], f["j"]): f for f in json.load(open(rg.WORK + "render_faces_raw.json"))}
S = P["S_UP"]
CROP = 380
rows = []
picks = [("matte", None, (1, 1)), ("raw", None, (3, 3)), ("chiseled", 0, (3, 3)), ("chiseled", 120, None)]
atlas_faces = info["faces"]
libids = np.load(rg.WORK + "libs.npz")
raw_ids = [tuple(int(v) for v in libids["raw_%d_id" % k][:2]) for k in range(int(libids["raw_n"]))]
raw_full = [tuple(int(v) for v in libids["raw_%d_id" % k][:2]) for k in range(int(libids["raw_n"])) if int(libids["raw_%d_id" % k][2]) > 95]
matte_full = [tuple(int(v) for v in libids["matte_%d_id" % k][:2]) for k in range(int(libids["matte_n"])) if int(libids["matte_%d_id" % k][2]) > 95]
chis_waves = {(int(libids["chis_%d_id" % k][0]), int(libids["chis_%d_id" % k][1])): int(libids["chis_%d_id" % k][2]) for k in range(int(libids["chis_n"]))}
sel = {"matte": matte_full[3], "raw": raw_full[1]}
sel["chis0"] = [k for k, v in chis_waves.items() if v == 0][0]
sel["chis120"] = [k for k, v in chis_waves.items() if v == 120][0]
atl = {"matte": [f for f in atlas_faces if f["type"] == "matte"][6], "raw": [f for f in atlas_faces if f["type"] == "raw"][2],
       "chis0": [f for f in atlas_faces if f["type"] == "chiseled" and f["rotation_deg"] == 0][0], "chis120": [f for f in atlas_faces if f["type"] == "chiseled" and f["rotation_deg"] == 120][0]}
labels = {"matte": "matte", "raw": "raw", "chis0": "chiseled 0", "chis120": "chiseled 120"}
font16 = font(18)
sheet = Image.new("RGB", (2 * CROP + 10, 4 * (CROP + 10)), (255, 255, 255))
for r, key in enumerate(["matte", "raw", "chis0", "chis120"]):
    fc = atl[key]
    a = crop_wrapped(color, int(round(fc["cy"])), int(round(fc["cx"])), CROP, CROP)
    src = feats[sel[key]]
    n = int(round(CROP / S))
    n += n % 2
    y0, x0 = int(round(src["cy"])) - n // 2, int(round(src["cx"])) - n // 2
    rc = render[y0:y0 + n, x0:x0 + n]
    rc = np.asarray(Image.fromarray(np.clip(rc, 0, 255).astype(np.uint8)).resize((CROP, CROP), Image.BICUBIC))
    sheet.paste(Image.fromarray(a), (0, r * (CROP + 10)))
    sheet.paste(Image.fromarray(rc), (CROP + 10, r * (CROP + 10)))
    dd = ImageDraw.Draw(sheet)
    dd.text((6, r * (CROP + 10) + 4), "atlas: %s (face %d)" % (labels[key], fc["index"]), fill=(255, 0, 0), font=font16, stroke_width=2, stroke_fill=(255, 255, 255))
    dd.text((CROP + 16, r * (CROP + 10) + 4), "render: face i%d j%d, bicubic x%.2f" % (sel[key][0], sel[key][1], S), fill=(255, 0, 0), font=font16, stroke_width=2, stroke_fill=(255, 255, 255))
save_jpg(sheet, "_REVIEW_crops_1to1.jpg")
print("wrote _REVIEW_crops_1to1.jpg", sheet.size)
