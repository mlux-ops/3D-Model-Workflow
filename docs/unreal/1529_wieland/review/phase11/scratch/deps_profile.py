import unreal, json
reg = unreal.AssetRegistryHelpers.get_asset_registry()
opt = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
out = {}
for p in ("/Game/Wieland1529/Delivery/L_W1529_Profile", "/Game/Wieland1529/L_Site_M4"):
    deps = [str(d) for d in (reg.get_dependencies(p, opt) or [])]
    out[p] = {"levels": sorted(d for d in deps if "/L_" in d.split("/")[-1] or d.split("/")[-1].startswith("L_")), "profile_sequence": [d for d in deps if "ProfilePaths" in d], "count": len(deps)}
json.dumps(out)
