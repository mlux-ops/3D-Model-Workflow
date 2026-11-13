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
out = {}
out["begin"] = wt.begin("D3")
await wl.wait_frames(3.0)
out["rt_editor_world"] = (await wt.render("D3", "rt", OUT, 1280, 720, limit_seconds=120, suffix="_editorworld"))["seconds_to_file"]
out["pt_editor_world_16"] = (await wt.render("D3", "pt", OUT, 1280, 720, samples=16, limit_seconds=240, suffix="_editorworld16"))["seconds_to_file"]
cam = wl.by_label(wt.CAMERA_LABEL)
loc = cam.get_actor_location()
out["camera"] = [loc.x, loc.y, loc.z]
for label in ("LGT_Exposure_Interior_LowerTo3rd",):
    v = wl.by_label(label)
    o, e = v.get_actor_bounds(False)
    out[label] = [round(x, 1) for x in (o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z)]
    out[label + "_enabled"] = [v.get_editor_property("enabled"), v.get_editor_property("unbound"), v.get_editor_property("priority"), v.get_editor_property("blend_weight")]
out["end"] = wt.end()
json.dumps(out, default=str)
