"""Phase 15: save exactly the packages named in NAMES (set before running) by name, refusing L_R15_Production and anything not
currently unsaved. Returns each result and the unsaved list afterwards."""
import json
import unreal
EAL = unreal.EditorAssetLibrary
utils = unreal.EditorLoadingAndSavingUtils
NAMES = ["/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings", "/Game/Wieland1529/Surroundings/L_Surroundings", "/Game/Wieland1529/Surroundings/L_Surroundings_R15"]
out = {}
dirty_before = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
for name in NAMES:
    if "R15_Production" in name:
        out[name] = "refused"
        continue
    if name not in dirty_before:
        out[name] = "not unsaved, skipped"
        continue
    package = unreal.find_package(name) if hasattr(unreal, "find_package") else None
    if package is None:
        package = unreal.load_package(name)
    out[name] = bool(utils.save_packages([package], True))
dirty_after = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
json.dumps({"saved": out, "dirty_before": dirty_before, "dirty_after": dirty_after})
