"""Phase 11: one line on the editor's state. Read-only."""
import sys, json, datetime
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
json.dumps({"world": wl.world_path(), "actors": len(wl.actors()), "dirty": wl.dirty(),
            "nanite_mode": unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode"),
            "pre_exposure": unreal.SystemLibrary.get_console_variable_float_value("r.EyeAdaptation.CachedLightingPreExposure"),
            "rendering": bool(unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()),
            "at": datetime.datetime.now().strftime("%H:%M:%S")})
