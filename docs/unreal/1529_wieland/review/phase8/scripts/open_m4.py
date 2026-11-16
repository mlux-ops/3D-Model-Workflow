import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_levels as wlv
importlib.reload(wl)
importlib.reload(wlv)
out = {"before": wl.world_path(), "dirty_before": wl.dirty()}
if wl.MASTER_LEVEL not in wl.world_path():
    out["opened"] = wlv.open_level(wl.MASTER_LEVEL, discard=False)
out["after"] = wl.world_path()
out["levels"] = len(wl.levels())
out["dirty"] = wl.dirty()
out["nanite"] = unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode")
json.dumps(out, default=str)
