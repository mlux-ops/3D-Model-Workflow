"""Phase 13, step 13.6: real-time pictures of the project's views with one option of the list "Neighbour development" on.

Same camera, lens and fixed exposure as Phases 8 and 10 (tools/wieland_truth.py), at 1920 by 1080. Besides the
stations and design views, three views of the project's rear and south side that no earlier phase defined:
  RD  penthouse roof deck looking south (Phase 14's roof deck camera)
  RP  ground-level rear patio of the north triplex looking south (Phase 14's rear deck camera)
  SY  the south side of 1529 from Wieland Street (30 ft west of the lot line, 3 ft south of it), looking east along the south lot line
The job: review/phase13/views/job.json = {"option": "proposed" | "existing", "views": [...], "settle": s,
"warm_up_frames": n}. Pictures go to review/phase13/views/<option>/. Nothing is saved; the temporary camera is
removed at the end and r.RayTracing.Nanite.Mode is read back as 0.
Run: python -B tools/ue_call.py py review/phase13/scripts/views_rt.py 1500
"""
import json
import os
import sys

sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
import wieland_hotel as wh

BASE = T.rsplit("/", 1)[0] + "/review/phase13/views"
EXTRA = {
    "RD": ((-1300.0, -2150.0, 1684.0), (15.0, 1.18, 0.0)),
    "RP": ((-1370.0, -2800.0, 363.0), (18.0, 1.18, 0.0)),
    "SY": ((3.0 * wh.CM, 30.0 * wh.CM, 5.25 * wh.CM), (8.0, -90.0, 0.0)),
}
_original_view = wt.view


def _view(name):
    if name in EXTRA:
        loc, rot = EXTRA[name]
        return unreal.Vector(*loc), unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2])
    return _original_view(name)


wt.view = _view
with open(BASE + "/job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
option = {"proposed": wh.OPTION_PROPOSED, "existing": wh.OPTION_EXISTING}[job["option"]]
OUT = BASE + "/" + job["option"]
os.makedirs(OUT, exist_ok=True)
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
out = {"switch": wh.switch(option), "runs": []}
await wl.wait_frames(5.0)
try:
    for name in job["views"]:
        begin = wt.begin(name)
        await wl.wait_frames(job.get("settle", 6.0))
        record = await wt.render(name, "rt", OUT, 1920, 1080, suffix="", warm_up_frames=job.get("warm_up_frames"))
        record["begin"] = begin
        record["option"] = option
        out["runs"].append(record)
        with open(OUT + "/runs.jsonl", "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
finally:
    out["end"] = wt.end()
    out["state_after"] = wh.state()
json.dumps([(r["view"], r.get("seconds_waited"), r.get("file_bytes")) for r in out["runs"]]
           + [out["switch"], out["end"], out["state_after"]], default=str)
