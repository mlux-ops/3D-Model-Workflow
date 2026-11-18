"""Phase 11: open the top level L_Site_M4 again (from the empty level of blank_level.py). Refuses if anything is unsaved."""
import json
import unreal
utils = unreal.EditorLoadingAndSavingUtils
dirty = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
if dirty:
    raise RuntimeError("unsaved packages: %s" % dirty)
utils.load_map("/Game/Wieland1529/L_Site_M4")
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
levels = unreal.EditorLevelUtils.get_levels(world)
json.dumps({"open": world.get_path_name(), "levels": len(levels), "nanite_mode": unreal.SystemLibrary.get_console_variable_int_value("r.RayTracing.Nanite.Mode"),
            "dirty": sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))})
