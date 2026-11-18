"""Phase 3, step 3.5: the starting table for the material audit.

Usage:
    python material_audit.py <building inventory .json> <export .udatasmith> <out .csv>

Lists every material in use in the building level, with how many mesh slots
use it, on how many objects, in which Revit categories, and, from the export
file, which image files the material names and which of those are missing
from the export's folder. Materials that are not from the import (the
engine's own) are listed too and marked, so that a surface left on a default
or placeholder material shows.

The inventory is written by wieland_building.inventory() in the editor.
"""

import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

BARE_AMPERSAND = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)")


def sanitize(label):
    return re.sub(r"[^0-9A-Za-z_\-]", "_", label or "")


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as handle:
        inventory = json.load(handle)
    export = argv[2]
    with open(export, encoding="utf-8", errors="replace") as handle:
        root = ET.fromstring(BARE_AMPERSAND.sub("&amp;", handle.read()))
    folder = os.path.dirname(export)
    textures = {}
    for texture in root.iter("Texture"):
        path = texture.get("file") or ""
        textures[texture.get("name")] = {"file": os.path.basename(path), "present": bool(path) and os.path.isfile(os.path.join(folder, path))}
    by_label = {}
    for material in root.iter("MaterialInstance"):
        images = []
        for prop in material.iter("KeyValueProperty"):
            value = prop.get("val")
            if value in textures:
                images.append(textures[value])
        by_label.setdefault(sanitize(material.get("label")), []).append(images)
    use = {}
    for item in inventory["objects"]:
        for mesh in item.get("meshes", []):
            for path in mesh["materials"]:
                if not path:
                    path = "(empty slot)"
                entry = use.setdefault(path, {"slots": 0, "objects": set(), "categories": {}})
                entry["slots"] += 1
                entry["objects"].add(item["name"])
                entry["categories"][item["category"]] = entry["categories"].get(item["category"], 0) + 1
    rows = []
    for path, entry in use.items():
        name = path.rsplit(".", 1)[-1]
        imported = path.startswith("/Game/Wieland1529/Building/")
        candidates = by_label.get(name) or by_label.get(re.sub(r"_\d+$", "", name)) or []
        images = candidates[0] if candidates else []
        missing = sorted({i["file"] for i in images if not i["present"] and i["file"]})
        rows.append({
            "material": name,
            "from_the_import": imported,
            "mesh_slots_using_it": entry["slots"],
            "objects_using_it": len(entry["objects"]),
            "categories": "; ".join("%s %d" % kv for kv in sorted(entry["categories"].items(), key=lambda kv: -kv[1])[:6]),
            "found_in_export": bool(candidates),
            "image_files": "; ".join(sorted({i["file"] for i in images if i["file"]})),
            "image_missing_from_the_export": "; ".join(missing),
            "confidence": "",
            "decision": "",
            "asset_path": path,
        })
    rows.sort(key=lambda r: (-r["mesh_slots_using_it"], r["material"]))
    with open(argv[3], "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "materials_in_use": len(rows),
        "from_the_import": sum(1 for r in rows if r["from_the_import"]),
        "not_from_the_import": [[r["material"], r["mesh_slots_using_it"], r["categories"]] for r in rows if not r["from_the_import"]],
        "matched_to_the_export": sum(1 for r in rows if r["found_in_export"]),
        "with_a_missing_image": [[r["material"], r["image_missing_from_the_export"], r["mesh_slots_using_it"]] for r in rows if r["image_missing_from_the_export"]],
        "with_images": sum(1 for r in rows if r["image_files"]),
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
