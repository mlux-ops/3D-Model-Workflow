import sys, json, importlib
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase14/scripts")
import p14
importlib.reload(p14)
out = p14.restore()
unreal = p14.unreal
import wieland_hotel as wh
out["hotel"] = wh.state()
out["world"] = p14.wl.world_path()
json.dumps(out, default=str)
