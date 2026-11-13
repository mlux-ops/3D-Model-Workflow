import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_hotel as wh
out = {"world": wl.world_path(), "dirty": wl.dirty(), "levels": [str(l) for l in wl.levels()][:20]}
out["hotel"] = wh.state()
out["sun"] = wl.read_sun()
out["nanite"] = unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode")
try:
    out["exposure"] = wl.read_exposure("LGT_Exposure_Outdoors")
except Exception as e:
    out["exposure"] = str(e)
out["conditions"] = wl.CONDITIONS
json.dumps(out, default=str)
