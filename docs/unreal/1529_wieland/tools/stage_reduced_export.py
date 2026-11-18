"""Make a staged copy of a Datasmith export in which oversized images are reduced.

Usage:
    python stage_reduced_export.py <export folder> <new folder> [--max-side 4096]

<export folder> holds one .udatasmith file and its "_Assets" folder. The new
folder gets the same file and the same assets, except that every image whose
longer side exceeds --max-side is written reduced to that size (Lanczos, 8 bits
per channel, same file name and type) instead of being copied. The source is
only read. A manifest, reduced_images.json, is written into the new folder.

Why: importing a 8,192 by 16,384 pixel image into Unreal takes several GB of
memory each, and on this workstation the reimport of the second export ran the
editor out of memory (2026-11-11 16:30).

Needs Pillow.
"""

import json
import os
import shutil
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    source, target = argv[1], argv[2]
    max_side = int(argv[argv.index("--max-side") + 1]) if "--max-side" in argv else 4096
    if os.path.exists(target):
        print("target exists, nothing done:", target)
        return 1
    reduced, copied, failed = [], 0, []
    for folder, _, files in os.walk(source):
        relative = os.path.relpath(folder, source)
        out_folder = os.path.join(target, relative) if relative != "." else target
        os.makedirs(out_folder, exist_ok=True)
        for name in files:
            src = os.path.join(folder, name)
            dst = os.path.join(out_folder, name)
            if name.lower().endswith(IMAGE_TYPES):
                try:
                    with Image.open(src) as picture:
                        width, height = picture.size
                        mode = picture.mode
                        if max(width, height) > max_side:
                            scale = max_side / float(max(width, height))
                            size = (max(1, round(width * scale)), max(1, round(height * scale)))
                            if mode in ("I;16", "I;16B", "I;16L", "I"):
                                picture = picture.point(lambda v: v / 256.0).convert("L")
                            elif mode not in ("RGB", "RGBA", "L", "LA"):
                                picture = picture.convert("RGBA" if "A" in mode else "RGB")
                            small = picture.resize(size, Image.LANCZOS)
                            small.save(dst)
                            reduced.append({"file": os.path.relpath(dst, target), "from": [width, height], "to": list(size), "mode_from": mode,
                                            "mode_to": small.mode, "bytes_from": os.path.getsize(src), "bytes_to": os.path.getsize(dst)})
                            continue
                except Exception as exc:
                    failed.append({"file": name, "error": repr(exc)})
            shutil.copy2(src, dst)
            copied += 1
    manifest = {"source": source, "max_side": max_side, "copied_unchanged": copied, "reduced": reduced, "could_not_read_so_copied": failed}
    with open(os.path.join(target, "reduced_images.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=1)
    print(json.dumps({"copied_unchanged": copied, "reduced": reduced, "could_not_read_so_copied": failed}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
