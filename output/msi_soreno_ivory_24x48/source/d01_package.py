"""Build the notes package: everything except the colour and bump maps and the .pat, which go to the Belmont
Revit Material Maps folder (owner instruction 2026-09-26). Explicit allow-list; re-opens the zip, tests
every member's CRC and prints the entry count, size and SHA-256 (also written to _work/package.json)."""
import glob
import hashlib
import json
import os
import zipfile

from guard import RUN_DIR, out_path

NAME = "MSI_Soreno_Ivory_24x48_Package"


def rel(pattern):
    return sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, pattern))
                  if os.path.isfile(p))


ALLOW = (["README.md", "SOURCE_SELECTION.md", "ERRORS.md",
          "textures/report.json", "textures/report_offwhite.json", "textures/validation.json",
          "textures/model_pattern_check.json", "textures/MSI_Soreno_Ivory_24x48_Model.pat",
          "_work/grid.json", "_work/dupes.json", "_work/master.json", "_work/fetch_log.json", "_work/ref_sizes.json",
          "_work/_VIEW_master_A.jpg", "_work/_VIEW_master_B.jpg", "_work/page.html"]
         + rel("textures/_*.jpg") + rel("source/*.py")
         + [p for p in rel("references/*") if p.lower().endswith((".jpg", ".jpeg", ".png", ".pdf"))]
         + rel("references/pdf_images/_thumbs/*.jpg"))


def main():
    zp = out_path(NAME + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for r in ALLOW:
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
