"""Build the notes package: everything except the two maps, which go to the Belmont Revit
Material Maps folder (owner instruction 2026-09-26). Explicit allow-list; re-opens the zip,
tests every member's CRC and prints the size and SHA-256."""
import glob
import hashlib
import os
import zipfile

from guard import RUN_DIR, out_path

NAME = "ELM_Vivid_Ligne_Noir_Package"


def rel(pattern):
    return sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, pattern)))


ALLOW = (["README.md", "SOURCE_SELECTION.md", "ERRORS.md", "textures/report.json", "textures/validation.json",
          "_work/measure.json", "textures/ELM_Vivid_Ligne_Noir_Model.pat", "textures/model_pattern_check.json",
          "textures/report_charcoal.json"]
         + rel("textures/_*.jpg") + rel("source/*.py")
         + [p for p in rel("references/*") if os.path.isfile(os.path.join(RUN_DIR, p))
            and os.path.basename(p).startswith(("elm_", "landoftile_", "nemo_"))])


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
    print("%s: %d entries, %d bytes, sha256 %s" % (os.path.basename(zp), n, os.path.getsize(zp), h))


if __name__ == "__main__":
    main()
