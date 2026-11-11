"""Archive-level readback of the Material-Browser-authored ADSKLIB.

Reads the library as a ZIP (never writes to it), checks that it holds exactly
the three deliverable materials with their five image bindings, extracts
Revit's own material thumbnails as evidence, and writes
source/adsklib_validation.json. Exits non-zero if any gate fails.

This is NOT a Revit load test. It proves what Revit wrote into the file,
not that a second project resolves the images.

Run:
    C:/Python314/python.exe -I output/clear_reeded_glass/source/verify_adsklib.py
"""
import hashlib
import json
import os
import re
import sys
import zipfile

RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LIB_NAME = "Clear_Reeded_Glass_0p5in_R2025.adsklib"
LIB_PATH = os.path.join(RUN_DIR, LIB_NAME)
TEXTURE_DIR = os.path.join(RUN_DIR, "textures")
REPORT_PATH = os.path.join(RUN_DIR, "source", "adsklib_validation.json")

BASE_NAME = "Clear Reeded Glass - 0.5in Vertical Reed"
HEIGHT_NAME = BASE_NAME + " (PBR Height Map)"
NORMAL_NAME = BASE_NAME + " (PBR Normal Map)"

BUMP_FILE = "Clear_Reeded_Glass_0p5in_Bump_16bit.png"
NORMAL_FILE = "Clear_Reeded_Glass_0p5in_Normal_16bit.png"
COLOR_FILE = "Clear_Reeded_Glass_0p5in_Color.png"

# filename -> number of bindings expected across the three materials
EXPECTED_BINDINGS = {BUMP_FILE: 2, NORMAL_FILE: 1, COLOR_FILE: 3}

EXPECTED_SLOTS = {
    "solidglass_bump_map:UnifiedBitmap": 1,
    "solidglass_transmittance_custom_color:UnifiedBitmap": 1,
    "surface_albedo:UnifiedBitmap": 2,
    "surface_normal:BumpMap": 2,
}


def out_path(*parts):
    """Every write goes through here; refuses anything outside the run dir."""
    path = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([path, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("write outside run dir refused: %s" % path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tolerant_count(blob, text):
    """Count occurrences of text in blob.

    The asset streams are chunked, and a chunk boundary can drop a few
    framing bytes into the middle of a string. Count exact hits, plus hits
    where one gap of up to 8 arbitrary bytes sits somewhere inside the text.
    """
    needle = text.encode("latin-1")
    exact = blob.count(needle)
    gapped = 0
    for cut in range(1, len(needle)):
        pattern = re.escape(needle[:cut]) + b"(?s:.{1,8}?)" + re.escape(needle[cut:])
        gapped += len(re.findall(pattern, blob))
    return exact + gapped


def main():
    report = {
        "stage": "started",
        "library": LIB_PATH,
        "note": "archive readback only; not a Revit load test",
        "gates": {},
        "errors": [],
    }
    try:
        if not os.path.isfile(LIB_PATH):
            raise RuntimeError("library not found: %s" % LIB_PATH)

        report["size_bytes"] = os.path.getsize(LIB_PATH)
        report["sha256"] = sha256_file(LIB_PATH)

        archive = zipfile.ZipFile(LIB_PATH)
        bad_member = archive.testzip()
        names = archive.namelist()
        report["entries"] = len(names)
        report["gates"]["zip_crc_clean"] = bad_member is None

        roots = sorted({n.split("/")[0] for n in names if "/AssetData/" in n})
        report["library_guid"] = roots
        report["gates"]["single_asset_library"] = len(roots) == 1
        root = roots[0]

        toc = archive.read(root + "/AssetData/AssetTableOfContents.bin")
        inst = archive.read(root + "/AssetData/InstanceProperties.bin")
        defs = archive.read(root + "/AssetData/DefinitionIteratorProperties.bin")

        # --- materials -----------------------------------------------------
        material_count = toc.count(b"physicalmaterial")
        report["material_count"] = material_count
        report["gates"]["exactly_three_materials"] = material_count == 3

        report["appearance_schemas"] = {
            "SolidGlassSchema": toc.count(b"SolidGlassSchema"),
            "PrismTransparentSchema": toc.count(b"PrismTransparentSchema"),
        }
        report["gates"]["one_solid_glass_two_transparent"] = (
            report["appearance_schemas"]["SolidGlassSchema"] == 1
            and report["appearance_schemas"]["PrismTransparentSchema"] == 2
        )

        found_names = {
            "base": tolerant_count(defs, BASE_NAME) > 0,
            "height": tolerant_count(defs, HEIGHT_NAME) > 0,
            "normal": tolerant_count(defs, NORMAL_NAME) > 0,
        }
        report["material_names_found"] = {
            BASE_NAME: found_names["base"],
            HEIGHT_NAME: found_names["height"],
            NORMAL_NAME: found_names["normal"],
        }
        report["gates"]["three_material_names_present"] = all(found_names.values())
        report["gates"]["no_qa_material_exported"] = (
            b"QA " not in defs and b"QA " not in inst and b"QA " not in toc
        )

        # --- image bindings ------------------------------------------------
        binding_counts = {name: tolerant_count(inst, name) for name in EXPECTED_BINDINGS}
        report["image_bindings"] = binding_counts
        report["gates"]["five_image_bindings_by_filename"] = binding_counts == EXPECTED_BINDINGS

        slot_counts = {slot: toc.count(slot.encode("latin-1")) for slot in EXPECTED_SLOTS}
        report["connected_slots"] = slot_counts
        report["gates"]["connected_slots_as_built"] = slot_counts == EXPECTED_SLOTS

        bound_dir = TEXTURE_DIR + os.sep
        report["bound_directory_expected"] = bound_dir
        report["bound_directory_found"] = tolerant_count(inst, bound_dir + COLOR_FILE) > 0
        report["bound_path_kind"] = "absolute"

        # --- companion textures on disk -------------------------------------
        textures = {}
        for name in EXPECTED_BINDINGS:
            path = os.path.join(TEXTURE_DIR, name)
            present = os.path.isfile(path)
            textures[name] = {
                "present": present,
                "size_bytes": os.path.getsize(path) if present else None,
                "sha256": sha256_file(path) if present else None,
            }
        report["companion_textures"] = textures
        report["gates"]["companion_textures_present"] = all(t["present"] for t in textures.values())

        # --- Revit's own thumbnails, as evidence ------------------------------
        thumbs = []
        asset_ids = sorted(
            {n.split("/")[2] for n in names if "/Resources/" in n and "/thumbnail/0/" in n and "_physmat_" not in n}
        )
        for asset_id in asset_ids:
            members = [
                n for n in names
                if n.startswith("%s/Resources/%s/thumbnail/0/" % (root, asset_id)) and n.endswith("_png")
            ]
            if not members:
                continue
            marker = (asset_id + "_physmat_aspects_1:").encode("latin-1")
            if marker + b"SolidGlass" in toc:
                label = "solid_glass_default"
            else:
                slot = (asset_id + "_physmat_aspects_1_surface_normal:BumpMap").encode("latin-1")
                start = inst.rfind(slot)
                tail = inst[start:] if start >= 0 else b""
                pos_bump = tail.find(BUMP_FILE.encode("latin-1"))
                pos_norm = tail.find(NORMAL_FILE.encode("latin-1"))
                if pos_norm >= 0 and (pos_bump < 0 or pos_norm < pos_bump):
                    label = "pbr_normal_map"
                elif pos_bump >= 0:
                    label = "pbr_height_map"
                else:
                    label = "unidentified_" + asset_id
            data = archive.read(members[0])
            target = out_path("evidence", "adsklib_thumbnail_%s.png" % label)
            with open(target, "wb") as handle:
                handle.write(data)
            thumbs.append({"asset_id": asset_id, "label": label, "file": target, "bytes": len(data)})
        report["thumbnails"] = thumbs
        report["gates"]["three_material_thumbnails_extracted"] = len(thumbs) == 3 and len(
            {t["label"] for t in thumbs}
        ) == 3

        report["all_gates_pass"] = all(report["gates"].values())
        report["stage"] = "complete"
    except Exception as exc:  # report first, then re-raise
        report["errors"].append("%s: %s" % (type(exc).__name__, exc))
        report["all_gates_pass"] = False
        with open(out_path("source", "adsklib_validation.json"), "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        raise

    with open(out_path("source", "adsklib_validation.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    for gate, ok in report["gates"].items():
        print("%-40s %s" % (gate, "PASS" if ok else "FAIL"))
    print("report: %s" % REPORT_PATH)
    if not report["all_gates_pass"]:
        print("ADSKLIB READBACK FAILED")
        return 1
    print("ADSKLIB READBACK PASS (archive level; not a Revit load test)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
