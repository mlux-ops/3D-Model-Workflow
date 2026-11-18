"""Phase 5, step 5.5: prepare one of this repository's material packages for the Unreal library.

    python -B phase5_library.py <package folder> <work folder> <asset stem> <material_library.csv>

A package (under output\\ at the repository root) holds a colour image, a
16-bit height image, a relief (normal) image, a roughness image and a
manifest with the physical size of the field in inches and the relief in
millimetres. This script

  * reads the manifest and checks each image against the checksum it records;
  * writes copies of the colour, relief and roughness images whose sides are
    powers of two (the graphics card can only keep smaller versions of an
    image for distant views when its sides are powers of two); the copy shows
    the same field, so the physical size is unchanged and is carried by the
    material's SizeU_m and SizeV_m, not by the pixel count;
  * measures the wrap of the copies (the step across the wrapping edge
    against the strongest step inside, as phase5_material_tests.py does);
  * adds or replaces the package's row in material_library.csv, in the
    columns that wieland_candidates.build_candidates() reads, with the relief
    figures of the manifest.

The package itself is not changed. The import into the editor is done by
wieland_parents.import_textures() with the items this script prints.
"""

import csv
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
INCH_M = 0.0254
FIELDS = ["material", "family", "confidence", "revit_asset", "candidate_asset", "parent", "scalars", "vectors",
          "textures", "switches", "physical_field_size", "source_and_licence", "what_it_rests_on", "for_the_owner",
          "package", "field_in", "source_pixels", "library_pixels", "pixels_per_metre", "pattern_relief_mm",
          "grout_step_mm", "clearance_mm", "relief_status", "seam_figure", "relief_image_convention"]
TEXTURES = "/Game/Wieland1529/Materials/Textures"
LIBRARY = "/Game/Wieland1529/Materials/Library"
PARENT = "/Game/Wieland1529/Materials/Parents/M_W1529_Opaque"


def power_of_two(value, limit=8192):
    size = 1
    while size * 2 <= min(value * 1.25, limit):
        size *= 2
    return size


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def seam_figure(image):
    lum = np.asarray(image.convert("RGB"), dtype=np.float64) / 255.0 @ np.array([0.2126, 0.7152, 0.0722])
    figures = []
    for axis in (0, 1):
        lines = np.moveaxis(lum, axis, 0).reshape(lum.shape[axis], -1)
        inside = np.abs(np.diff(lines, axis=0)).mean(axis=1).max()
        edge = np.abs(lines[0] - lines[-1]).mean()
        figures.append(edge / max(inside, 0.002))
    return max(figures)


def main(package, work, stem, out_csv):
    with open(os.path.join(package, "manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
    os.makedirs(work, exist_ok=True)
    width_in, height_in = manifest["atlas_size_in"]
    size_u, size_v = width_in * INCH_M, height_in * INCH_M
    items, seams, source_pixels, library_pixels = [], [], None, None
    for key, suffix, kind in (("color", "C", "colour"), ("normal", "N", "normal"), ("roughness", "R", "mask")):
        entry = manifest["maps"][key]
        source = os.path.join(package, entry["path"].replace("\\", os.sep))
        if sha256(source) != entry["sha256"]:
            raise SystemExit("checksum differs from the manifest: " + source)
        image = Image.open(source)
        source_pixels = image.size
        target = (power_of_two(image.size[0]), power_of_two(image.size[1]))
        library_pixels = target
        mode = "L" if kind == "mask" else "RGB"
        copy = image.convert(mode).resize(target, Image.LANCZOS)
        out = os.path.join(work, "T_W1529_%s_%s.png" % (stem, suffix))
        copy.save(out)
        seams.append(seam_figure(copy))
        items.append([out, TEXTURES, "T_W1529_%s_%s" % (stem, suffix), kind])
    relief = manifest["relief"]
    row = {
        "material": manifest["material"],
        "family": "tile, interior finish (repository package)",
        "confidence": "",
        "revit_asset": "",
        "candidate_asset": "%s/MI_W1529_L_%s" % (LIBRARY, stem),
        "parent": PARENT,
        "scalars": json.dumps({"SizeU_m": round(size_u, 5), "SizeV_m": round(size_v, 5), "NormalStrength": 1.0,
                               "RoughnessScale": 1.0, "MacroVariation": 0.0}, sort_keys=True),
        "vectors": json.dumps({"Tint": [1.0, 1.0, 1.0, 1.0]}),
        "textures": json.dumps({"BaseColorMap": "%s/T_W1529_%s_C" % (TEXTURES, stem),
                                "NormalMap": "%s/T_W1529_%s_N" % (TEXTURES, stem),
                                "RoughnessMap": "%s/T_W1529_%s_R" % (TEXTURES, stem)}, sort_keys=True),
        "switches": json.dumps({"AntiRepeat": False, "UseMeshUV": False}, sort_keys=True),
        "physical_field_size": "%.3f by %.3f m" % (size_u, size_v),
        "source_and_licence": ("This repository's package %s (SKU %s). The colour image is derived from the "
                               "manufacturer's product pictures (%s); the manufacturer's terms for them are not "
                               "recorded." % (os.path.basename(os.path.normpath(package)), manifest.get("sku", ""),
                                              manifest.get("url", ""))),
        "what_it_rests_on": "The package's manifest and README; nothing was re-derived.",
        "for_the_owner": "Not assigned to any surface. The owner names the surfaces, if any, that carry this tile.",
        "package": package,
        "field_in": "%s x %s" % (width_in, height_in),
        "source_pixels": "%d x %d" % source_pixels,
        "library_pixels": "%d x %d" % library_pixels,
        "pixels_per_metre": "%d across, %d up" % (round(library_pixels[0] / size_u), round(library_pixels[1] / size_v)),
        "pattern_relief_mm": relief["pattern_relief_mm"],
        "grout_step_mm": relief["grout_step_mm"],
        "clearance_mm": round(relief["clearance_mm"], 3),
        "relief_status": relief["status"],
        "seam_figure": "%.2f" % max(seams),
        "relief_image_convention": "OpenGL in the package (per its README); the green channel is flipped on the "
                                   "Unreal texture, not in the file.",
    }
    rows = []
    if os.path.exists(out_csv):
        with open(out_csv, encoding="utf-8", newline="") as handle:
            rows = [r for r in csv.DictReader(handle) if r["material"] != row["material"]]
    rows.append(row)
    with open(out_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"items": items, "seam_figure": row["seam_figure"], "field_m": [size_u, size_v],
                      "library_pixels": library_pixels, "pixels_per_metre": row["pixels_per_metre"]}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
