"""Phase 13, read-only: the project's own parent materials, material instances and textures that the hotel's
materials can be made from. Nothing is changed.
"""
import json

import unreal

registry = unreal.AssetRegistryHelpers.get_asset_registry()
rows = []
for folder in ["/Game/Wieland1529/Materials", "/Game/Wieland1529/Surroundings/Materials"]:
    for data in registry.get_assets_by_path(folder, recursive=True):
        kind = str(data.asset_class_path.asset_name)
        path = str(data.package_name)
        row = {"path": path, "class": kind}
        if kind == "MaterialInstanceConstant":
            asset = unreal.load_asset(path)
            parent = asset.get_editor_property("parent")
            row["parent"] = parent.get_name() if parent else None
        rows.append(row)
rows.sort(key=lambda r: r["path"])
json.dumps(rows)
