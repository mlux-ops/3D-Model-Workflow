"""Production step d01: build the notes package (everything except the two maps, which are delivered
separately to the Belmont Revit Material Maps folder, per the owner's 2026-09-26 instruction).

Explicit allow-list; writes ELM_Formed_Hexagon_Sand_Package.zip inside this folder, re-opens it,
tests every member's CRC and prints the size and SHA-256.
"""
import glob
import hashlib
import os
import zipfile

from guard import RUN_DIR, out_path

NAME = "ELM_Formed_Hexagon_Sand_Package"
ALLOW = (["README.md", "METHOD_FROM_MAX_TRIAL.md", "SOURCE_SELECTION.md", "ERRORS.md",
          "textures/report.json", "textures/validation.json", "textures/face_ids.png",
          "textures/ELM_Formed_Hexagon_Sand_Model.pat", "textures/model_pattern_check.json"]
         + sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, "textures", "_*.jpg")))
         + sorted(os.path.relpath(p, RUN_DIR).replace("\\", "/") for p in glob.glob(os.path.join(RUN_DIR, "source", "*.py")))
         + ["references/elm_formed_hex_sand_layout_render.webp", "references/elm_formed_hex_sand_lifestyle_angled.webp",
            "_work/lifestyle_tone_windows.png", "_work/ridge_patches.png", "_work/ridge_compare_prod_v1.png",
            "_work/ridge_compare_maxtrial.png"])


def main():
    zp = out_path(NAME + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel in ALLOW:
            src = os.path.join(RUN_DIR, rel)
            if not os.path.isfile(src):
                raise FileNotFoundError(rel)
            z.write(src, NAME + "/" + rel)
    with zipfile.ZipFile(zp) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError("CRC failure in %s" % bad)
        n = len(z.namelist())
    h = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    print("%s: %d entries, %d bytes, sha256 %s" % (os.path.basename(zp), n, os.path.getsize(zp), h))


if __name__ == "__main__":
    main()
