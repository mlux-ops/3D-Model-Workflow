"""Phase 15, J6: one real-time picture of one view, the hotel removed. Same camera, 24 mm lens and fixed exposure as
Phases 8, 10 and 12 (tools/wieland_truth.py). Besides the stations and design views, two views no earlier phase kept:
  AIR  aerial from the south-east over Wells Street: 250 ft up, 350 ft south and 420 ft east of 1529's south-west lot
       corner, looking north-west at the former hotel land and 1529 (yaw 130.7, pitch -28.6)
  RDE  1529's penthouse roof deck (Phase 13's roof-deck point, north 42.65 ft, east 70.5 ft, 55.25 ft up) looking east
       over the rear of 1529 toward Wells Street (yaw -90, pitch -12)
The job: review/phase15/views/job.json = {"views": [...], "width": w, "height": h, "settle": s, "warm_up_frames": n}.
Nothing is saved; the temporary camera is removed at the end and r.RayTracing.Nanite.Mode is read back."""
import json
import sys
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
CM = 30.48006096
OUT = T.rsplit("/", 1)[0] + "/review/phase15/views"
EXTRA = {
    "AIR": ((350.0 * CM, -420.0 * CM, 250.0 * CM), (-28.6, 130.7, 0.0)),
    "RDE": ((-1300.0, -2150.0, 1684.0), (-12.0, -90.0, 0.0)),
}
_original_view = wt.view
def _view(name):
    if name in EXTRA:
        loc, rot = EXTRA[name]
        return unreal.Vector(*loc), unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2])
    return _original_view(name)
wt.view = _view
with open(OUT + "/job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
out = {"runs": [], "nanite_before": wt.cvar("r.RayTracing.Nanite.Mode")}
try:
    for name in job["views"]:
        begin = wt.begin(name)
        await wl.wait_frames(job.get("settle", 10.0))
        record = await wt.render(name, "rt", OUT, job.get("width", 3840), job.get("height", 2160), suffix="",
                                 warm_up_frames=job.get("warm_up_frames"))
        record["begin"] = begin
        out["runs"].append(record)
        with open(OUT + "/runs.jsonl", "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
finally:
    out["end"] = wt.end()
    out["nanite_after"] = wt.cvar("r.RayTracing.Nanite.Mode")
json.dumps([(r["view"], r.get("seconds_waited"), r.get("file_bytes"), r.get("nanite_mode_during")) for r in out["runs"]]
           + [out["nanite_before"], out["nanite_after"], out["end"]], default=str)
