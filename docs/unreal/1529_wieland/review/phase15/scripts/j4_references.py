"""Phase 15, J4, read-only: every asset under /Game whose name or path marks it as the hotel's; for each, its class, its users
(referencers, from the asset registry) and whether any user lies outside the hotel; whether Datasmith made it (asset user data)."""
import json
import unreal
ar = unreal.AssetRegistryHelpers.get_asset_registry()
EAL = unreal.EditorAssetLibrary
HOTEL_ROOT = "/Game/Wieland1529/Site/ProposedHotel"
LEVEL = "/Game/Wieland1529/Site/L_ProposedHotel"
def is_hotel_pkg(p):
    return p.startswith(HOTEL_ROOT + "/") or p == LEVEL or p.startswith(LEVEL + "_") or "/__ExternalActors__/Wieland1529/Site/L_ProposedHotel" in p or "/__ExternalObjects__/Wieland1529/Site/L_ProposedHotel" in p
cands = set(str(p).split(".")[0] for p in EAL.list_assets(HOTEL_ROOT, True, False))
if EAL.does_asset_exist(LEVEL):
    cands.add(LEVEL)
for p in EAL.list_assets("/Game", True, False):
    p = str(p).split(".")[0]
    name = p.split("/")[-1]
    if "_PH_" in name or "ProposedHotel" in p or "DukeOfWells" in p.replace(" ", ""):
        cands.add(p)
opts = unreal.AssetRegistryDependencyOptions(True, True, True, True, True)
rows = []
for p in sorted(cands):
    data = ar.get_assets_by_package_name(p)
    cls = str(data[0].asset_class_path.asset_name) if data else "?"
    refs = [str(r) for r in (ar.get_referencers(p, opts) or [])]
    outside = [r for r in refs if not is_hotel_pkg(r)]
    rows.append({"asset": p, "class": cls, "users": len(refs), "users_outside_hotel": outside})
by_class = {}
for r in rows:
    by_class[r["class"]] = by_class.get(r["class"], 0) + 1
json.dumps({"count": len(rows), "by_class": by_class, "outside_hotel_folder": [r["asset"] for r in rows if not is_hotel_pkg(r["asset"])],
            "with_outside_users": [r for r in rows if r["users_outside_hotel"]], "rows": rows})
