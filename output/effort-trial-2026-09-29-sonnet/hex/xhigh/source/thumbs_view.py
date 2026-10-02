"""Write <=800 px viewing copies of the review images into work/thumbs/ (viewing aid only)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import guard
import render_grid as rg

TEX = guard.RUN + "/textures/"
OUT = rg.WORK + "thumbs/"


def whole(name, out, w=800):
    im = Image.open(TEX + name).convert("RGB")
    s = w / im.size[0]
    im.resize((w, int(round(im.size[1] * s))), Image.LANCZOS).save(guard.safe(OUT + out), quality=92)


def part(name, out, box, w=800):
    im = Image.open(TEX + name).convert("RGB").crop(box)
    s = w / im.size[0]
    im.resize((w, int(round(im.size[1] * s))), Image.LANCZOS).save(guard.safe(OUT + out), quality=92)


if __name__ == "__main__":
    whole("_PREVIEW_atlas_full.jpg", "v_atlas.jpg")
    whole("_PREVIEW_grazing_light.jpg", "v_graze.jpg")
    whole("_PREVIEW_wrap_2x2.jpg", "v_wrap.jpg")
    whole("_REVIEW_wrap_seam.jpg", "v_seam.jpg")
    im = Image.open(TEX + "_REVIEW_crops_1to1.jpg")
    w, h = im.size
    part("_REVIEW_crops_1to1.jpg", "v_crops_top.jpg", (0, 0, w, h // 2), w)
    part("_REVIEW_crops_1to1.jpg", "v_crops_bot.jpg", (0, h // 2, w, h), w)
    im = Image.open(TEX + "_REVIEW_face_types.jpg")
    w, h = im.size
    for n, box in (("tl", (0, 0, w // 2, h // 2)), ("tr", (w // 2, 0, w, h // 2)), ("bl", (0, h // 2, w // 2, h)), ("br", (w // 2, h // 2, w, h))):
        part("_REVIEW_face_types.jpg", "v_types_%s.jpg" % n, box)
    print("ok")
