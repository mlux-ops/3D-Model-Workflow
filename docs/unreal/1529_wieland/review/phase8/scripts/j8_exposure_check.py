import sys, importlib, json, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_interiors as wi
importlib.reload(wl)
importlib.reload(wi)
OUT = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase8/exposure"
out = {"restored_windows": wl.window_restore()}
out["views"] = wi.views_begin()
await wl.wait_frames(3.0)
for name in ("D2", "D3", "D1"):
    path = "%s/%s_realtime_check.png" % (OUT, name)
    if os.path.exists(path):
        os.remove(path)
    out[name] = wi.view_shot(name, path, 1280, 720)
    await wl.wait_frames(4.0)
out["exposure"] = {l: wl.read_exposure(l) for l in ("LGT_Exposure_Outdoors", "LGT_Exposure_Interior_LowerTo3rd", "LGT_Exposure_Interior_4th")}
out["end"] = wi.views_end()
out["dirty"] = wl.dirty()
json.dumps(out, default=str)
