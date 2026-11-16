import sys, importlib, json, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_interiors as wi
import wieland_render
import wieland_truth as wt
for m in (wl, wi, wieland_render, wt):
    importlib.reload(m)
OUT = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase8/ground_truth/trial"
out = {"nanite_as_found": wt.cvar(wt.NANITE_MODE)}
out["begin"] = wt.begin("S1")
await wl.wait_frames(3.0)
out["rt"] = await wt.render("S1", "rt", OUT, 1280, 720, limit_seconds=120)
out["pt"] = await wt.render("S1", "pt", OUT, 1280, 720, samples=64, limit_seconds=240)
out["end"] = wt.end()
json.dumps(out, default=str)
