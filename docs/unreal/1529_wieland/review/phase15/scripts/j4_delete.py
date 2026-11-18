"""Phase 15, J4: delete the hotel's own assets (the level, then meshes, material instances, textures under
/Game/Wieland1529/Site/ProposedHotel), each only if the asset registry shows no user outside the hotel and the asset carries
no Datasmith data; then remove the emptied folder. Never touches anything outside that folder and the level."""
import json
import unreal
ar = unreal.AssetRegistryHelpers.get_asset_registry()
EAL = unreal.EditorAssetLibrary
ROOT = "/Game/Wieland1529/Site/ProposedHotel"
LEVEL = "/Game/Wieland1529/Site/L_ProposedHotel"
opts = unreal.AssetRegistryDependencyOptions(True, True, True, True, True)
def hotel_pkg(p):
    return p.startswith(ROOT + "/") or p == LEVEL
order = [LEVEL] + sorted(str(p).split(".")[0] for p in EAL.list_assets(ROOT + "/Meshes", True, False)) \
        + sorted(str(p).split(".")[0] for p in EAL.list_assets(ROOT + "/Materials", True, False)) \
        + sorted(str(p).split(".")[0] for p in EAL.list_assets(ROOT + "/Textures", True, False))
rest = set(str(p).split(".")[0] for p in EAL.list_assets(ROOT, True, False)) - set(order)
deleted, kept = [], []
for p in order:
    if not EAL.does_asset_exist(p):
        kept.append([p, "did not exist"])
        continue
    outside = [str(r) for r in (ar.get_referencers(p, opts) or []) if not hotel_pkg(str(r))]
    if outside:
        kept.append([p, "used by " + ", ".join(outside)])
        continue
    if p != LEVEL:
        obj = unreal.load_asset(p)
        dsm = False
        if obj is not None and hasattr(obj, "get_asset_user_data_of_class") and hasattr(unreal, "DatasmithAssetUserData"):
            try:
                dsm = obj.get_asset_user_data_of_class(unreal.DatasmithAssetUserData) is not None
            except Exception:
                dsm = False
        obj = None
        if dsm:
            kept.append([p, "carries Datasmith data"])
            continue
    if EAL.delete_asset(p):
        deleted.append(p)
    else:
        kept.append([p, "delete_asset returned False"])
left = [str(p) for p in EAL.list_assets(ROOT, True, False)]
folder_removed = EAL.delete_directory(ROOT) if not left else False
json.dumps({"planned": len(order), "unexpected_other_assets": sorted(rest), "deleted": len(deleted), "deleted_list": deleted,
            "kept": kept, "left_in_folder": left, "folder_removed": bool(folder_removed),
            "level_exists": EAL.does_asset_exist(LEVEL), "folder_exists": EAL.does_directory_exist(ROOT)})
