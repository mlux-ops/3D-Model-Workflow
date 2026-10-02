"""Review images (all written under textures/)."""
import json
from PIL import ImageDraw, ImageFont
from scipy import ndimage
from common import *
import srcs

TEX = RUN + "/textures/"
LO, HI = -1.6, 0.8


def load_all():
    Image.MAX_IMAGE_PIXELS = None
    col = np.asarray(Image.open(TEX + "Color.png").convert("RGB"))
    b = np.asarray(Image.open(TEX + "Bump16.png")).astype(np.float64)
    ids = np.asarray(Image.open(TEX + "face_ids.png")).astype(np.int32)
    hmm = b / 65535.0 * (HI - LO) + LO
    return col, hmm, ids


def shade(h, az_deg, el_deg, px_mm=25.4 / 64.0):
    gy, gx = np.gradient(h, px_mm)
    a = np.deg2rad(az_deg); el = np.deg2rad(el_deg)
    l = np.array([np.cos(a) * np.cos(el), np.sin(a) * np.cos(el), np.sin(el)])
    nrm = np.sqrt(gx * gx + gy * gy + 1.0)
    return np.clip((-gx * l[0] - gy * l[1] + l[2]) / nrm, 0, 1)


def grazing(col, h, az=200.0, el=15.0):
    """colour shaded by bump under a low raking light; normalised so a flat surface keeps its colour."""
    flat = np.sin(np.deg2rad(el))
    s = shade(h, az, el)
    k = np.clip(0.45 + 0.55 * (s / flat), 0.2, 1.6)      # 1.0 on flat ground, 0.45 ambient floor
    return np.clip(col.astype(np.float32) * k[..., None], 0, 255).astype(np.uint8)


def thumb(img_arr, width, mode="RGB", resample=Image.LANCZOS):
    im = Image.fromarray(img_arr) if isinstance(img_arr, np.ndarray) else img_arr
    s = width / im.width
    return im.resize((width, round(im.height * s)), resample)


def main():
    col, h, ids = load_all()
    H_, W_ = col.shape[:2]
    # 1 atlas full
    save_img(thumb(col, 2000), TEX + "_PREVIEW_atlas_full.jpg", quality=92)
    # 2 wrap 2x2 (each tile 1000 px wide)
    t = thumb(col, 1000)
    a = np.asarray(t)
    two = np.tile(a, (2, 2, 1))
    save_img(Image.fromarray(two), TEX + "_PREVIEW_wrap_2x2.jpg", quality=92)
    # 3 wrap seam: four-way corner magnified (colour, bump shaded)
    sh = shade(h, 200, 25)
    rc = np.roll(np.roll(col, H_ // 2, 0), W_ // 2, 1)
    rs = np.roll(np.roll(sh, H_ // 2, 0), W_ // 2, 1)
    r = 100
    m = Image.new("RGB", (1600, 1600))
    # row 0: the four-way corner (atlas 0,0); row 1: seam through a joint junction (x=0 at a hex vertex, y=324)
    for row, (ay, ax) in enumerate(((0, 0), (324, 0))):
        cy, cx = (ay + H_ // 2) % H_, (ax + W_ // 2) % W_
        pc = Image.fromarray(rc[cy - r:cy + r, cx - r:cx + r]).resize((800, 800), Image.NEAREST)
        ps = Image.fromarray((rs[cy - r:cy + r, cx - r:cx + r] * 255).astype(np.uint8)).resize((800, 800), Image.NEAREST).convert("RGB")
        m.paste(pc, (0, 800 * row)); m.paste(ps, (800, 800 * row))
    save_img(m, TEX + "_REVIEW_wrap_seam.jpg", quality=95)
    # 4 face types labelled
    meta = json.load(open(RUN + "/work/build_meta.json"))
    im = thumb(col, 2000).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        f = ImageFont.load_default()
    sc = 2000 / W_
    colors = {"matte": (60, 60, 60), "raw": (200, 30, 30), "chiseled": (20, 60, 200)}
    for mt in meta:
        x, y = mt["cx"] * sc, mt["cy"] * sc
        lab = "%d %s" % (mt["index"], mt["type"][:4].upper() if mt["type"] != "chiseled" else "CHIS %d" % mt["rotation_deg"])
        d.text((x - 60, y - 15), lab, fill=colors[mt["type"]], font=f)
        for dx, dy in ((0, 0), (W_ * sc, 0), (-W_ * sc, 0), (0, H_ * sc), (0, -H_ * sc)):
            if dx or dy:
                d.text((x - 60 + dx, y - 15 + dy), lab, fill=colors[mt["type"]], font=f)
    save_img(im, TEX + "_REVIEW_face_types.jpg", quality=90)
    # 5 grazing
    g = grazing(col, h, 200, 15)
    save_img(thumb(g, 2000, resample=Image.BOX if False else Image.LANCZOS), TEX + "_PREVIEW_grazing_light.jpg", quality=92)
    save_img(Image.fromarray(g[:1400, :1400]).resize((800, 800), Image.LANCZOS), RUN + "/work/graz_crop_tl.png")
    # 6 1:1 crops next to render at the same physical scale
    types = {}
    for mt in meta:
        types.setdefault(mt["type"], []).append(mt)
    render = Image.open(RENDER).convert("RGB")
    lat = json.load(open(RUN + "/work/render_lattice.json"))
    hexes = json.load(open(RUN + "/work/render_hexes.json"))
    pick_render = {"matte": (2, 3), "raw": (1, 2), "chiseled": (0, 3)}
    pick_ours = {"matte": None, "raw": None, "chiseled": 90}
    CR = 320
    rows = []
    for t_ in ("matte", "raw", "chiseled"):
        cand = types[t_]
        if t_ == "chiseled":
            mt = [c for c in cand if c["rotation_deg"] == 90][0]
        else:
            mt = cand[len(cand) // 2]
        cx, cy = int(round(mt["cx"])), int(round(mt["cy"]))
        ys = (np.arange(cy - CR // 2, cy + CR // 2)) % H_
        xs = (np.arange(cx - CR // 2, cx + CR // 2)) % W_
        ours = col[np.ix_(ys, xs)]
        ourg = g[np.ix_(ys, xs)]
        i, j = pick_render[t_]
        hx = [q for q in hexes if q["i"] == i and q["j"] == j][0]
        half = CR / 2 / srcs.F_UP
        rc_ = render.crop((int(hx["cx"] - half), int(hx["cy"] - half), int(hx["cx"] + half), int(hx["cy"] + half))).resize((CR, CR), Image.BICUBIC)
        row = np.concatenate([ours, ourg, np.asarray(rc_)], axis=1)
        rows.append(row)
    save_img(Image.fromarray(np.concatenate(rows, axis=0)), TEX + "_REVIEW_crops_1to1.jpg", quality=95)


if __name__ == "__main__":
    main()
