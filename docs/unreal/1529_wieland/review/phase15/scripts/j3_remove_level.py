"""Phase 15, J3 (no saving here): with L_Site_M4 open, count hotel objects by level, remove the hotel level from the top level,
collect garbage, and read back the levels, the object count, hotel objects and the unsaved packages."""
import json
import unreal
TAG = "W1529.ProposedHotel"
LEVEL = "/Game/Wieland1529/Site/L_ProposedHotel"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if w.get_path_name().split(".")[0] != "/Game/Wieland1529/L_Site_M4":
    raise RuntimeError("refused: open level is " + w.get_path_name())
def acts():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def lvl(a):
    return a.get_outer().get_outer().get_path_name().split(".")[0]
def hotel(a):
    return any(str(t) == TAG for t in a.tags) or "_PH_" in a.get_actor_label() or lvl(a) == LEVEL
by_level = {}
for a in acts():
    if hotel(a):
        by_level[lvl(a)] = by_level.get(lvl(a), 0) + 1
out = {"hotel_by_level_before": by_level, "actors_before": len(acts())}
target = None
for level in unreal.EditorLevelUtils.get_levels(w):
    if level.get_outer().get_path_name().split(".")[0] == LEVEL:
        target = level
out["found_level"] = target is not None
if target is not None:
    out["removed"] = bool(unreal.EditorLevelUtils.remove_level_from_world(target))
target = None
unreal.SystemLibrary.collect_garbage()
levels = [l.get_outer().get_path_name().split(".")[0] for l in unreal.EditorLevelUtils.get_levels(w)]
out["levels"] = len(levels)
out["hotel_level_still_listed"] = LEVEL in levels
out["actors_after"] = len(acts())
out["hotel_objects_after"] = sum(1 for a in acts() if hotel(a))
utils = unreal.EditorLoadingAndSavingUtils
out["dirty"] = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
json.dumps(out)
