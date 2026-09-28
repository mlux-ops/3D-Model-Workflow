"""Review images for the ELM Formed Hexagon Sand atlas.

Deliverable previews go to textures/; <=800 px viewing copies for self-review go to _work/.
"""
import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
import common as C
from guard import inp, save_image, TEX_DIR, WORK_DIR

col = np.asarray(Image.open(os.path.join(TEX_DIR, "Color.png")).convert("RGB")).astype(np.float32)
bump = np.asarray(Image.open(os.path.join(TEX_DIR, "Bump16.png"))).astype(np.float32)
fid = np.asarray(Image.open(os.path.join(TEX_DIR, "face_ids.png"))).astype(np.int32)
rep = json.load(open(os.path.join(TEX_DIR, "report.json")))
enc = rep["bump_encoding"]
h_mm = enc["black_mm"] + bump / 65535.0 * (enc["white_mm"] - enc["black_mm"])
H, W = h_mm.shape
try:
    FONT = ImageFont.truetype("arial.ttf", 22)
    FONT_S = ImageFont.truetype("arial.ttf", 15)
except OSError:
    FONT = FONT_S = ImageFont.load_default()


def view(im, name, maxs=800):
    v = im.copy()
    v.thumbnail((maxs, maxs), Image.LANCZOS)
    save_image(v, os.path.join(WORK_DIR, "view_" + name), quality=90)


from shading import shade, tone  # noqa: E402


# 1. atlas full ---------------------------------------------------------------------------------
atlas = Image.fromarray(col.astype(np.uint8))
a2k = atlas.copy()
a2k.thumbnail((2000, 2000), Image.LANCZOS)
save_image(a2k, os.path.join(TEX_DIR, "_PREVIEW_atlas_full.jpg"), quality=92)
view(atlas, "atlas_full.jpg")

# 2. wrap 2x2 -----------------------------------------------------------------------------------
t2 = np.tile(col.astype(np.uint8), (2, 2, 1))
w2 = Image.fromarray(t2)
w2.thumbnail((2000, 2000), Image.LANCZOS)
save_image(w2, os.path.join(TEX_DIR, "_PREVIEW_wrap_2x2.jpg"), quality=92)
view(w2, "wrap_2x2.jpg")

# 3. grazing light -------------------------------------------------------------------------------
GRAZE_ELEV, GRAZE_AZ, GRAZE_AMB = 20.0, 200.0, 0.35   # light from the left, slightly above; room fill 0.35
s = shade(h_mm, GRAZE_ELEV, GRAZE_AZ)
g = tone(col, s, amb=GRAZE_AMB)
gim = Image.fromarray(g)
g2k = gim.copy()
g2k.thumbnail((2000, 2000), Image.LANCZOS)
dg = ImageDraw.Draw(g2k)
cap = ("Bump16 decoded to mm, Lambert + cast shadows, light %.0f deg elevation from the left/upper-left, "
       "ambient %.2f" % (GRAZE_ELEV, GRAZE_AMB))
bb = dg.textbbox((0, 0), cap, font=FONT_S)
dg.rectangle([4, 4, bb[2] + 12, bb[3] + 10], fill=(255, 255, 255))
dg.text((8, 6), cap, fill=(0, 0, 0), font=FONT_S)
save_image(g2k, os.path.join(TEX_DIR, "_PREVIEW_grazing_light.jpg"), quality=92)
view(gim, "grazing_full.jpg")

# 4. wrap seam: four-way corner of the 2x2 repeat, colour and grazing-lit bump, magnified 3x -------
cs = 130
tg = np.tile(g, (2, 2, 1))
pieces = []
for src in (t2, tg):
    crop = src[H - cs // 2:H + cs // 2, W - cs // 2:W + cs // 2]
    im = Image.fromarray(crop).resize((cs * 3, cs * 3), Image.NEAREST)
    d = ImageDraw.Draw(im)
    d.line([(cs * 3 // 2, 0), (cs * 3 // 2, 10)], fill=(255, 0, 0), width=2)
    d.line([(0, cs * 3 // 2), (10, cs * 3 // 2)], fill=(255, 0, 0), width=2)
    pieces.append(im)
seam = Image.new("RGB", (cs * 6 + 10, cs * 3 + 30), (255, 255, 255))
seam.paste(pieces[0], (0, 30))
seam.paste(pieces[1], (cs * 3 + 10, 30))
d = ImageDraw.Draw(seam)
d.text((4, 4), "4-way wrap corner (red ticks = image edge), 3x: colour | grazing-lit bump", fill=(0, 0, 0), font=FONT_S)
save_image(seam, os.path.join(TEX_DIR, "_REVIEW_wrap_seam.jpg"), quality=95)
view(seam, "wrap_seam.jpg")

# 5. face types labelled -------------------------------------------------------------------------
lab = atlas.copy()
lab.thumbnail((2000, 2000), Image.LANCZOS)
sc = lab.width / float(W)
d = ImageDraw.Draw(lab)
cen = C.face_centres()
for f in rep["faces"]:
    cx, cy = cen[f["index"] - 1]
    t = f["type"]
    txt = "%d %s" % (f["index"], {"matte": "MATTE", "raw": "RAW", "chiseled": "CHIS"}[t])
    if t == "chiseled":
        txt += " %d°" % f["groove_angle_image_deg"]
    colr = {"matte": (40, 40, 40), "raw": (170, 30, 30), "chiseled": (20, 60, 170)}[t]
    for dx_, dy_ in ((0, 0), (C.W, 0), (0, C.H), (C.W, C.H), (-C.W, 0), (0, -C.H)):
        x, y = (cx + dx_) * sc, (cy + dy_) * sc
        if -60 < x < lab.width + 60 and -20 < y < lab.height + 20:
            bb = d.textbbox((0, 0), txt, font=FONT)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            d.rectangle([x - tw / 2 - 3, y - th / 2 - 3, x + tw / 2 + 3, y + th / 2 + 5], fill=(255, 255, 255))
            d.text((x - tw / 2, y - th / 2), txt, fill=colr, font=FONT)
save_image(lab, os.path.join(TEX_DIR, "_REVIEW_face_types.jpg"), quality=92)
view(lab, "face_types.jpg")

# 6. 1:1 crops of each face type next to the render at the same physical scale ---------------------
R = Image.open(inp("elm_formed_hex_sand_layout_render.webp")).convert("RGB")
LAT = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
cells = {"%d,%d" % (c["j"], c["k"]): c for c in LAT["cells"]}
rpx = LAT["px_per_in"]
CROP = 256                                   # 4.0 in at 64 px/in
rsz = CROP / C.PX_PER_IN * rpx               # same 4.0 in in render px
picks = [("matte", None, "3,4"), ("raw", None, "1,2"), ("chiseled", 90, "2,1"), ("chiseled", 30, "0,1"),
         ("chiseled", 150, "1,4")]
rows = []
for t, ang, rk in picks:
    fs = [f for f in rep["faces"] if f["type"] == t and (ang is None or f.get("groove_angle_image_deg") == ang)]
    f = fs[len(fs) // 2]
    cx, cy = cen[f["index"] - 1]
    x0, y0 = int(cx - CROP / 2) % W, int(cy - CROP / 2) % H
    ours = np.roll(np.roll(col, -y0, 0), -x0, 1)[:CROP, :CROP].astype(np.uint8)
    ours_g = np.roll(np.roll(g, -y0, 0), -x0, 1)[:CROP, :CROP]
    c = cells[rk]
    rc = R.crop((int(c["cx"] - rsz / 2), int(c["cy"] - rsz / 2), int(c["cx"] - rsz / 2) + int(round(rsz)),
                 int(c["cy"] - rsz / 2) + int(round(rsz)))).resize((CROP, CROP), Image.BICUBIC)
    rows.append((t, ang, f["index"], rk, Image.fromarray(ours), Image.fromarray(ours_g), rc))
sheet = Image.new("RGB", (3 * CROP + 40, len(rows) * (CROP + 28) + 30), (255, 255, 255))
d = ImageDraw.Draw(sheet)
d.text((6, 6), "1:1 at 64 px/in, 4.0 x 4.0 in each | atlas colour | atlas grazing-lit | render (same 4 in, resampled)",
       fill=(0, 0, 0), font=FONT_S)
for r, (t, ang, idx, rk, a, ag, rc) in enumerate(rows):
    y = 30 + r * (CROP + 28)
    name = t.upper() + ("" if ang is None else " %d°" % ang)
    d.text((6, y + 2), "%s — atlas face %d | render cell %s" % (name, idx, rk), fill=(0, 0, 0), font=FONT_S)
    sheet.paste(a, (0, y + 24))
    sheet.paste(ag, (CROP + 20, y + 24))
    sheet.paste(rc, (2 * CROP + 40, y + 24))
save_image(sheet, os.path.join(TEX_DIR, "_REVIEW_crops_1to1.jpg"), quality=95)
view(sheet.crop((0, 0, sheet.width, 30 + 3 * (CROP + 28))), "crops_a.jpg")
view(sheet.crop((0, 30 + 3 * (CROP + 28), sheet.width, sheet.height)), "crops_b.jpg")

# 7. extra self-review views: 1:1 grazing crops around a raw face and a joint crossing -------------
for nm, (x0, y0) in {"g11_a": (1200, 1200), "g11_b": (2600, 2900)}.items():
    save_image(Image.fromarray(g[y0:y0 + 700, x0:x0 + 700]), os.path.join(WORK_DIR, "view_%s.jpg" % nm), quality=92)
    save_image(Image.fromarray(col[y0:y0 + 700, x0:x0 + 700].astype(np.uint8)), os.path.join(WORK_DIR, "view_%s_col.jpg" % nm), quality=92)
print("previews written")
