"""Make <=800 px thumbnails of every reference image (for viewing) and list native sizes.
Usage: python a00_thumbs.py [extra image paths to also thumbnail (read-only)...]"""
import glob
import json
import os
import sys

from PIL import Image

from guard import RUN_DIR, out_path

Image.MAX_IMAGE_PIXELS = None


def thumb(p, tag):
    im = Image.open(p)
    info = {"file": p, "size": im.size, "mode": im.mode, "format": im.format}
    im = im.convert("RGB")
    im.thumbnail((800, 800))
    dst = out_path("_work/thumbs/%s.jpg" % tag)
    im.save(dst, quality=90)
    info["thumb"] = dst
    return info


def main():
    files = sorted(glob.glob(os.path.join(RUN_DIR, "references", "**", "*.*"), recursive=True))
    files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"))
             and "_thumbs" not in f]
    files += sys.argv[1:]
    out = []
    for f in files:
        tag = os.path.splitext(os.path.basename(f))[0]
        if f in sys.argv[1:]:
            tag = "ext_" + tag
        try:
            out.append(thumb(f, tag))
        except Exception as e:  # noqa: BLE001 - record and continue
            out.append({"file": f, "error": repr(e)})
    json.dump(out, open(out_path("_work/thumbs/index.json"), "w"), indent=1)
    for o in out:
        print(o.get("size"), o.get("mode"), os.path.basename(o["file"]), o.get("error", ""))


if __name__ == "__main__":
    main()
