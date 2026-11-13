import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
importlib.reload(wl)
out = {"temp_cleared": wl.temp_clear(), "world": wl.world_path()}
U = "/Game/Wieland1529/Interiors/Levels/L_W1529_"
out["saved"] = wl.save([U + "NorthTriplex", U + "SouthTriplex", U + "NorthPenthouse", U + "SouthPenthouse",
                        "/Game/Wieland1529/Lighting/L_Light_SummerAfternoon"])
json.dumps(out, default=str)
