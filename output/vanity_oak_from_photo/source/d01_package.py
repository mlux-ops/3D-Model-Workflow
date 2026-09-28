"""Notes package: everything except the colour map (which goes to the Belmont Revit Material Maps folder, standing
instruction 2026-09-26). Explicit allow-list; re-opens the zip, tests every member's CRC, and records entries /
bytes / SHA-256 in _work/package.json."""
import glob
import hashlib
import json
import os
import zipfile

from guard import RUN_DIR, out_path

NAME = "Vanity_Oak_Color_Map_Package"


def rel(pattern):
    return sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, pattern))
                  if os.path.isfile(p))


def main():
    allow = (["README.md", "SOURCE_SELECTION.md", "ERRORS.md", "validation.json",
              "references/u12_vanity_product_photo.jpg"]
             + rel("_PREVIEW_*.jpg") + rel("_PREVIEW_*.png") + rel("source/*.py")
             + ["_work/" + f for f in ("measure.json", "crops.json", "source_dupes.json", "delight.json", "layout.json",
                                       "upscale.json")])
    zp = out_path(NAME + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for r in allow:
            src = os.path.join(RUN_DIR, r)
            if not os.path.isfile(src):
                raise FileNotFoundError(r)
            z.write(src, NAME + "/" + r)
    with zipfile.ZipFile(zp) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError("CRC failure in %s" % bad)
        names = z.namelist()
    assert not any(n.lower().endswith("color.png") for n in names), "colour map must not be in the notes zip"
    h = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    info = {"zip": os.path.basename(zp), "entries": len(names), "bytes": os.path.getsize(zp), "sha256": h,
            "crc_test": "pass"}
    json.dump(info, open(out_path("_work/package.json"), "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
