"""Phase 12: print what the Revit export says about every work-list material (read-only).

    python -B dump_revit_values.py <material_audit.csv> <material_params.json>
"""
import csv
import json
import os
import re
import sys

BRAND = re.compile("brizo|hansgrohe|kohler", re.I)
KEYS = ("Glossiness", "Transparency", "SelfIlluminationLuminance", "SelfIlluminationColorTemperature", "BumpAmount",
        "DiffuseMap_UVScaleX", "DiffuseMap_UVScaleY", "IsMetal", "Metallic")


def main(audit_csv, params_json):
    with open(params_json, encoding="utf-8") as handle:
        params = json.load(handle)["materials"]
    with open(audit_csv, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        name, decision = row["material"], row["decision"].strip()
        if not (BRAND.search(name) or decision in ("rebuild", "") or name == "Door_-_Frame"):
            continue
        material = params.get(name)
        if not material:
            print(name, "NO PARAMETERS")
            continue
        scalars, vectors = material["scalars"], material["vectors"]
        if "DiffuseColor" not in vectors:
            print(name, "NOT A REVIT MATERIAL:", material.get("parent"))
            continue
        colour = [round(v * 255) for v in vectors["DiffuseColor"][:3]]
        images = {}
        for key, texture in material["textures"].items():
            if texture and texture.get("path", "").startswith("/Game"):
                images[key] = os.path.basename((texture.get("source_file") or texture["path"]).replace("\\", "/"))[:60]
        values = {k: round(scalars[k], 3) for k in KEYS if k in scalars}
        for key in ("Transparency", "SelfIlluminationLuminance", "BumpAmount"):
            if not values.get(key):
                values.pop(key, None)
        if "SelfIlluminationLuminance" not in values:
            values.pop("SelfIlluminationColorTemperature", None)
        if "DiffuseMap" not in images:
            values.pop("DiffuseMap_UVScaleX", None)
            values.pop("DiffuseMap_UVScaleY", None)
        glow = ""
        if scalars.get("SelfIlluminationLuminance"):
            glow = {k: [round(x, 2) for x in v[:3]] for k, v in vectors.items() if k != "DiffuseColor"}
        print(name[:48], colour, values, images, glow)


if __name__ == "__main__":
    main(*sys.argv[1:3])
