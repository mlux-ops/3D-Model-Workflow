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
APPEND = "r.RayTracing.Nanite.MaxAppendInstances"
out = {"append_as_found": wt.cvar(APPEND)}
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
out["begin"] = wt.begin("S2")
await wl.wait_frames(3.0)
out["rt"] = (await wt.render("S2", "rt", OUT, 1280, 720, limit_seconds=120))["seconds_to_file"]
out["pt_mode2_append10000"] = (await wt.render("S2", "pt", OUT, 1280, 720, samples=64, limit_seconds=240, suffix="_append10000"))["seconds_to_file"]
wt.cvar(APPEND, 400000)
await wl.wait_frames(3.0)
out["pt_mode2_append400000"] = (await wt.render("S2", "pt", OUT, 1280, 720, samples=64, limit_seconds=240, suffix="_append400000"))["seconds_to_file"]
wt.cvar(APPEND, 10000)
out["pt_mode0"] = (await wt.render("S2", "pt", OUT, 1280, 720, samples=64, limit_seconds=240, nanite_mode=0, suffix="_mode0"))["seconds_to_file"]
out["append_after"] = wt.cvar(APPEND)
out["end"] = wt.end()
json.dumps(out, default=str)
