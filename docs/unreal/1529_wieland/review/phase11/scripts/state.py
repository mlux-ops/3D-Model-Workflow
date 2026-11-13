import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
# Phase 11: read-only state of the editor (open world, levels, unsaved packages, the watched console variables).
world = wl.world()
levels = []
for streaming in world.get_editor_property("streaming_levels") if hasattr(world, "streaming_levels") else unreal.EditorLevelUtils.get_levels(world):
    try:
        levels.append((str(streaming.get_world_asset_package_name()).split("/")[-1], bool(streaming.is_level_loaded()), bool(streaming.is_level_visible())))
    except Exception:
        levels.append((streaming.get_path_name().split(".")[0].split("/")[-1], None, None))
names = ("r.RayTracing.Nanite.Mode", "r.RayTracing.Nanite.MaxAppendInstances", "r.Material.UseShaderCompilationParameters",
         "r.ScreenPercentage", "sg.GlobalIlluminationQuality", "sg.ShadowQuality", "t.MaxFPS", "r.Lumen.WorldCache.Supported")
cv = {n: unreal.SystemLibrary.get_console_variable_float_value(n) for n in names}
try:
    compiling = unreal.AssetCompilingManager.get().get_num_remaining_assets()
except Exception as error:
    compiling = repr(error)
size = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_camera_info()
json.dumps({"world": wl.world_path(), "levels": levels, "dirty": wl.dirty(), "cvars": cv, "compiling": compiling,
            "actors": len(wl.actors())})
