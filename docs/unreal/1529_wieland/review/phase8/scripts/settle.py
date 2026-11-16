"""Phase 8: let the open level settle before a heavy step. Waits the given seconds while the editor draws
frames, then returns what is still being prepared (shader and asset compilation) and the Nanite mode."""
import sys
sys.dont_write_bytecode = True
TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import unreal
import wieland_lighting as wl

wl.window_restore()
await wl.wait_frames(240.0)
out = {"world": wl.world_path(), "dirty": wl.dirty(),
       "shader_jobs_left": unreal.ShaderCompilingManager.get_num_remaining_jobs() if hasattr(unreal, "ShaderCompilingManager") else None,
       "nanite": unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode")}
try:
    out["assets_compiling"] = unreal.AssetCompilingManager.get_num_remaining_assets() if hasattr(unreal, "AssetCompilingManager") else None
except Exception as error:
    out["assets_compiling"] = str(error)
out
