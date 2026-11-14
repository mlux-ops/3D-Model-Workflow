"""Phase 15, read-only: the open level, its sub-levels, hotel objects, the three hidden objects, the variant lists, hotel assets."""
import json, datetime
import unreal
EAL = unreal.EditorAssetLibrary
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
w = ues.get_editor_world()
acts = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def lvl(a):
    return a.get_outer().get_outer().get_path_name().split(".")[0]
HIDE = ["SB_782868", "R15_PART_opaque_xm04_yp01_part01", "R15_PART_glass_xm04_yp01_part01"]
hidden = {}
hotel = []
for a in acts:
    lab = a.get_actor_label()
    if lab in HIDE:
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        hidden[lab] = {"level": lvl(a), "visible": bool(c.get_editor_property("visible")) if c else None,
                       "hidden_in_game": bool(c.get_editor_property("hidden_in_game")) if c else None,
                       "actor_hidden_game": bool(a.get_editor_property("hidden")), "hidden_ed": a.is_temporarily_hidden_in_editor()}
    if any(str(t) == "W1529.ProposedHotel" for t in a.tags) or "ProposedHotel" in lvl(a) or "_PH_" in lab or "Hotel" in lab:
        hotel.append([lab, lvl(a)])
levels = [l.get_outer().get_path_name().split(".")[0] for l in unreal.EditorLevelUtils.get_levels(w)]
streaming = [str(s.get_world_asset_package_name()) for s in unreal.EditorLevelUtils.get_streaming_levels(w)] if hasattr(unreal.EditorLevelUtils, "get_streaming_levels") else "n/a"
lists = {}
sa = unreal.load_asset("/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings")
if sa:
    for i in range(sa.get_num_variant_sets()):
        vs = sa.get_variant_set(i)
        opts = {}
        for j in range(vs.get_num_variants()):
            v = vs.get_variant(j)
            opts[str(v.get_display_text())] = v.get_num_actors()
        lists[str(vs.get_display_text())] = opts
ph_assets = [str(p) for p in EAL.list_assets("/Game/Wieland1529/Site/ProposedHotel", True, False)]
utils = unreal.EditorLoadingAndSavingUtils
dirty = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
json.dumps({"at": datetime.datetime.now().strftime("%H:%M:%S"), "world": w.get_path_name().split(".")[0], "actors": len(acts),
            "levels": levels, "streaming": streaming, "hotel_objects": len(hotel), "hotel_sample": hotel[:5], "hidden": hidden,
            "lists": lists, "ph_asset_count": len(ph_assets), "level_asset": EAL.does_asset_exist("/Game/Wieland1529/Site/L_ProposedHotel"),
            "dirty": dirty, "nanite_mode": unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode")}, indent=1)
