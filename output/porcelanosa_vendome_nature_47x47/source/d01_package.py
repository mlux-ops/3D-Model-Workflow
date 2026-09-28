"""Notes package: everything except the colour and bump maps, which go to the Belmont Revit Material Maps folder
(owner instruction 2026-09-26). The .pat is delivered there and is also kept in the package.
Explicit allow-list; re-opens the zip, tests every member's CRC, records entries / bytes / SHA-256 in
_work/package.json.  Usage: python d01_package.py"""
import glob
import hashlib
import json
import os
import zipfile

from guard import RUN_DIR, out_path

NAME = "Porcelanosa_Vendome_Nature_47x47_Package"


def rel(pattern):
    return sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, pattern))
                  if os.path.isfile(p))


def main():
    allow = (["README.md", "SOURCE_SELECTION.md", "ERRORS.md", "_work/Porcelanosa_Vendome_Nature_47x47_Model.pat",
              "_work/model_pattern_check.json", "_work/edges.json", "_work/lighting.json", "_work/grout_variant_test.json",
              "_work/references_sha256.txt", "_work/thumbs/index.json", "_work/_VIEW_contact_sheet.jpg", "_work/verify_log.txt"]
             + [s + "/" + f for s in ("designed", "free_mix", "pieces") for f in ("report.json", "validation.json")]
             + rel("*/_PREVIEW_*.jpg") + rel("_work/joints_src/_VIEW_*.jpg") + rel("source/*.py")
             + rel("references/*.jpg") + rel("references/*.pdf"))
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
        n = len(z.namelist())
    h = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    info = {"zip": os.path.basename(zp), "entries": n, "bytes": os.path.getsize(zp), "sha256": h, "crc_test": "pass"}
    json.dump(info, open(out_path("_work/package.json"), "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
