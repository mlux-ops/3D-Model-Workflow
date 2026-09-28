"""Notes package for one product: everything except the colour and bump maps and the .pat's delivered copy, which go
to the Belmont Revit Material Maps folder (owner instruction 2026-09-26; the .pat is also kept in the package).
Explicit allow-list; re-opens the zip, tests every member's CRC, and records entries / bytes / SHA-256 in
_work/package_<prod>.json.  Usage: python d01_package.py veincut_24x48 | mosaic_1x3"""
import glob
import hashlib
import json
import os
import sys
import zipfile

from guard import RUN_DIR, out_path

NAMES = {"veincut_24x48": ("ELM_Jute_Vein_Cut_24x48_Package", "ELM_Jute_Vein_Cut_24x48_Model.pat"),
         "mosaic_1x3": ("ELM_Jute_Vein_Cut_1x3_Mosaic_Package", "ELM_Jute_Vein_Cut_1x3_Mosaic_Model.pat")}


def rel(pattern):
    return sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, pattern))
                  if os.path.isfile(p))


def main(prod):
    name, pat = NAMES[prod]
    allow = ([prod + "/README.md", "SOURCE_SELECTION.md", "ERRORS.md", prod + "/report.json", prod + "/validation.json",
              prod + "/model_pattern_check.json", prod + "/" + pat]
             + rel(prod + "/_PREVIEW_*.jpg") + rel("source/*.py")
             + ["_work/" + f for f in ("faces.json", "locate.json", "measure.json", "ridges.json", "mosaic_stats.json",
                                       "mosaic_sources.json", "fetch_log.json")]
             + rel("_work/dupes*.json") + rel("_work/faces/_VIEW_*.jpg")
             + [p for p in rel("references/*/*") if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".pdf"))])
    zp = out_path(name + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for r in allow:
            src = os.path.join(RUN_DIR, r)
            if not os.path.isfile(src):
                raise FileNotFoundError(r)
            z.write(src, name + "/" + r)
    with zipfile.ZipFile(zp) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError("CRC failure in %s" % bad)
        n = len(z.namelist())
    h = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    info = {"zip": os.path.basename(zp), "entries": n, "bytes": os.path.getsize(zp), "sha256": h, "crc_test": "pass"}
    json.dump(info, open(out_path("_work/package_%s.json" % prod), "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main(sys.argv[1])
