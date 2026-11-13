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
# J9, after the restart: D4 and D5 small and at few samples first, to check framing and exposure and to time them.
OUT = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase8/ground_truth/trial"
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
out = {}
for name in ("D4", "D5"):
    out[name + "_begin"] = wt.begin(name)
    await wl.wait_frames(6.0)
    r = await wt.render(name, "pt", OUT, 1280, 720, samples=64, limit_seconds=400, suffix="_trial64")
    out[name] = [r.get("seconds_to_file"), r.get("file_bytes"), r["nanite_mode_during"]]
out["end"] = wt.end()
json.dumps(out, default=str)
