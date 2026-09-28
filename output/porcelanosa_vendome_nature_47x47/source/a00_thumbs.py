"""Thumbnails (<= 800 px) of every reference, a numbered contact sheet of the 8 faces, and native sizes.
Usage: python a00_thumbs.py"""
import glob
import json
import os

from PIL import Image, ImageDraw

from guard import RUN_DIR, out_path

Image.MAX_IMAGE_PIXELS = None


def main():
    files = sorted(glob.glob(os.path.join(RUN_DIR, "references", "*.jpg")))
    out = []
    for f in files:
        im = Image.open(f)
        info = {"file": os.path.basename(f), "size": im.size, "mode": im.mode, "format": im.format,
                "dpi": [float(v) for v in im.info.get("dpi", ())], "icc": bool(im.info.get("icc_profile")), "exif_bytes": len(im.info.get("exif", b""))}
        t = im.convert("RGB")
        t.thumbnail((800, 800))
        t.save(out_path("_work/thumbs/%s.jpg" % os.path.splitext(os.path.basename(f))[0]), quality=90)
        out.append(info)
    json.dump(out, open(out_path("_work/thumbs/index.json"), "w"), indent=1)
    # contact sheet: faces 1..8 at 190 px, numbered
    s = 190
    sheet = Image.new("RGB", (4 * s + 5 * 6, 2 * s + 3 * 6 + 2 * 18), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    for i in range(8):
        im = Image.open(os.path.join(RUN_DIR, "references", "100348304_%03d.jpg" % (i + 1))).convert("RGB").resize((s, s), Image.LANCZOS)
        x, y = 6 + (i % 4) * (s + 6), 6 + (i // 4) * (s + 24) + 18
        sheet.paste(im, (x, y))
        dr.text((x, y - 15), "face %d" % (i + 1), fill=(255, 255, 0))
    sheet.save(out_path("_work/_VIEW_contact_sheet.jpg"), quality=90)
    for o in out:
        print(o)


if __name__ == "__main__":
    main()
