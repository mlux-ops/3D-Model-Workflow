"""Phase 12: the work list with what the Revit export and the scene say about each material (read-only).

    python -B worklist.py <material_audit.csv> <material_params.json> <uses.json> [group]
"""
import csv
import json
import re
import sys

BRAND = re.compile("brizo|hansgrohe|kohler", re.I)


def group_of(row):
    name, decision, note = row["material"], row["decision"].strip(), row["owner_note"].strip()
    if BRAND.search(name):
        return "brand"
    if decision == "rebuild":
        return "rebuild"
    if decision == "":
        return "blank"
    if decision == "keep" and note:
        return "keep_note"
    return decision


def main(audit_csv, params_json, uses_json, only=None):
    with open(params_json, encoding="utf-8") as handle:
        params = json.load(handle)["materials"]
    with open(uses_json, encoding="utf-8") as handle:
        uses = json.load(handle)
    with open(audit_csv, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        group = group_of(row)
        if only and group != only:
            continue
        name = row["material"]
        material = params.get(name, {})
        scalars, vectors = material.get("scalars", {}), material.get("vectors", {})
        colour = [round(v * 255) for v in vectors.get("DiffuseColor", [])[:3]]
        image = ""
        texture = material.get("textures", {}).get("DiffuseMap") or {}
        if texture.get("path", "").startswith("/Game"):
            image = "img %sx%s %.2fm" % (texture.get("x"), texture.get("y"),
                                         0.3048 / float(scalars.get("DiffuseMap_UVScaleX", 1) or 1))
        use = uses.get(name, {})
        labels = sorted(use.get("labels", {}).items(), key=lambda kv: -kv[1])[:2]
        extra = ""
        if scalars.get("Transparency"):
            extra += " T%.2f" % scalars["Transparency"]
        if scalars.get("SelfIlluminationLuminance"):
            extra += " L%d/%dK" % (scalars["SelfIlluminationLuminance"], scalars.get("SelfIlluminationColorTemperature", 0))
        print("%s|%s|%s|c%s|s%s|%s g%.2f%s|%s|slots %s|big %s|%s|%s" % (
            group, name[:52], row["family"], row["confidence"], row.get("objects_using_it", ""), colour,
            scalars.get("Glossiness", -1), extra, image, use.get("slots_mesh", 0), use.get("largest_m", ""),
            "; ".join("%s x%d" % (k[:38], v) for k, v in labels), row["owner_note"][:90]))


if __name__ == "__main__":
    main(*sys.argv[1:5])
