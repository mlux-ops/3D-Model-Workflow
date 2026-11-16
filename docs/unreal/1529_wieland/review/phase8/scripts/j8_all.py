import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_fixtures as wf
importlib.reload(wl)
importlib.reload(wf)
MODEL = wf.REVIEW + "/fixture_lights_before.csv"
out = {"apply": wf.apply(MODEL)}
out["inventory"] = wf.inventory(wf.LIGHTS)
out["dirty"] = wl.dirty()
json.dumps(out)
