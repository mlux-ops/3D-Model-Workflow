"""List every reference image with pixel size and write <=800 px thumbnails to references/_thumbs/.
Also writes _work/ref_sizes.json."""
import glob
import hashlib
import json
import os

from PIL import Image

from guard import INPUT_DIR, out_path

Image.MAX_IMAGE_PIXELS = None


def main():
    rows = []
    files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.*")) + glob.glob(os.path.join(INPUT_DIR, "pdf_images", "*.png")))
    for p in files:
        if p.lower().endswith(".pdf"):
            continue
        im = Image.open(p)
        rel = os.path.relpath(p, INPUT_DIR).replace("\\", "/")
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
        rows.append({"file": rel, "px": list(im.size), "mode": im.mode, "bytes": os.path.getsize(p), "sha16": sha})
        t = im.convert("RGB")
        t.thumbnail((800, 800), Image.LANCZOS)
        t.save(out_path("references/_thumbs/" + os.path.splitext(os.path.basename(p))[0] + ".jpg"), quality=88)
        print("%-75s %5d x %-5d %s %s" % (rel, im.size[0], im.size[1], im.mode, sha))
    json.dump(rows, open(out_path("_work/ref_sizes.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
