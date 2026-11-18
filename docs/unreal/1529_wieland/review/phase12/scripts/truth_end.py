import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
# After a path-traced picture: removes the temporary camera if it is still there, puts the two ray tracing
# settings back, and reads them back.
end = wt.end()
json.dumps({"end": end, "nanite_mode": wt.cvar(wt.NANITE_MODE), "append_instances": wt.cvar(wt.APPEND)}, default=str)
