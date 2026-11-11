"""Build the allow-list delivery ZIP for the clear reeded glass material.

Only the files named below go in. The disposable QA project, raw view
exports, logs and probe output are left out on purpose.

Run:
    C:/Python314/python.exe -I output/clear_reeded_glass/source/package.py
"""
import hashlib
import json
import os
import sys
import zipfile

RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOP = "Clear_Reeded_Glass_0p5in_R2025"
ZIP_NAME = TOP + "_Package.zip"

ALLOW_LIST = [
    "Clear_Reeded_Glass_0p5in_R2025.adsklib",
    "README.md",
    "textures/Clear_Reeded_Glass_0p5in_Bump_16bit.png",
    "textures/Clear_Reeded_Glass_0p5in_Normal_16bit.png",
    "textures/Clear_Reeded_Glass_0p5in_Color.png",
    "source/build_maps.py",
    "source/build_revit.py",
    "source/verify_adsklib.py",
    "source/map_validation.json",
    "source/revit_validation.json",
    "source/adsklib_validation.json",
    "evidence/maps_grazing_light_from_left.png",
    "evidence/maps_bump_wrap_3x3.png",
    "evidence/maps_profile_section.png",
    "evidence/revit_realistic_viewport_comparison.png",
    "evidence/revit_realistic_oblique_default_material.png",
    "evidence/adsklib_thumbnail_solid_glass_default.png",
    "evidence/adsklib_thumbnail_pbr_height_map.png",
    "evidence/adsklib_thumbnail_pbr_normal_map.png",
]


def out_path(*parts):
    """Every write goes through here; refuses anything outside the run dir."""
    path = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([path, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("write outside run dir refused: %s" % path)
    return path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    missing = [rel for rel in ALLOW_LIST if not os.path.isfile(os.path.join(RUN_DIR, rel))]
    if missing:
        print("MISSING, nothing written: %s" % missing)
        return 1

    validation = json.load(open(os.path.join(RUN_DIR, "source", "adsklib_validation.json"), encoding="utf-8"))
    if not validation.get("all_gates_pass"):
        print("adsklib_validation.json does not pass; refusing to package")
        return 1
    lib_sha = sha256_file(os.path.join(RUN_DIR, ALLOW_LIST[0]))
    if lib_sha != validation.get("sha256"):
        print("library changed since it was validated; re-run verify_adsklib.py")
        return 1

    target = out_path(ZIP_NAME)
    candidate = target + ".candidate"
    with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in ALLOW_LIST:
            archive.write(os.path.join(RUN_DIR, rel), TOP + "/" + rel)

    with zipfile.ZipFile(candidate) as archive:
        bad = archive.testzip()
        names = archive.namelist()
        if bad is not None:
            print("CRC failure in %s; candidate left at %s" % (bad, candidate))
            return 1
        if sorted(names) != sorted(TOP + "/" + rel for rel in ALLOW_LIST):
            print("entry list does not match the allow-list; candidate left at %s" % candidate)
            return 1
        for rel in ALLOW_LIST:
            packed = hashlib.sha256(archive.read(TOP + "/" + rel)).hexdigest()
            if packed != sha256_file(os.path.join(RUN_DIR, rel)):
                print("content mismatch for %s; candidate left at %s" % (rel, candidate))
                return 1

    if os.path.exists(target):
        print("refusing to overwrite existing %s; candidate left at %s" % (target, candidate))
        return 1
    os.replace(candidate, target)

    manifest = {
        "package": target,
        "entries": len(ALLOW_LIST),
        "size_bytes": os.path.getsize(target),
        "sha256": sha256_file(target),
        "top_folder": TOP,
        "files": ALLOW_LIST,
        "excluded_on_purpose": ["qa/ (disposable Revit project and raw exports)", "logs", "probe output"],
    }
    with open(out_path("source", "package_manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    print(json.dumps({k: manifest[k] for k in ("package", "entries", "size_bytes", "sha256")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
