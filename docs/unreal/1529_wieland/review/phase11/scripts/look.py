"""Phase 11: one small real-time picture from any point, to check a place before a camera move goes there.

Reads review/phase11/look_job.json = {"name": "L_family", "location": [x, y, z], "target": [x, y, z][, "ev100": 7.0]} or {"name", "move", "frame"} and writes
review/phase11/scratch/look/<name>_realtime.0000.png at 1,280 by 720 through the same temporary camera as the stills.
Nothing is saved; the camera is removed at the end.
"""
import sys, importlib, json, math
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
BASE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/"
with open(BASE + "look_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
if wt.cvar(wt.NANITE_MODE) != 0:
    raise RuntimeError("r.RayTracing.Nanite.Mode does not read 0; not rendering")
name = job["name"]
if "move" in job:
    # a frame of a camera move made by move_build.py: {"name", "move": "triplex", "frame": 420}
    with open(BASE + "paths/%s_move.json" % job["move"], "r", encoding="utf-8") as handle:
        frame = json.load(handle)["frames"][job["frame"]]
    pitch, yaw = math.radians(frame["rot"][0]), math.radians(frame["rot"][1])
    job["location"] = frame["loc"]
    job["target"] = [frame["loc"][0] + 100.0 * math.cos(pitch) * math.cos(yaw), frame["loc"][1] + 100.0 * math.cos(pitch) * math.sin(yaw),
                     frame["loc"][2] + 100.0 * math.sin(pitch)]
    job.setdefault("ev100", frame["ev"])
wi.DESIGN_VIEWS[name] = (tuple(job["location"]), tuple(job["target"]))
begin = wt.begin(name)
if "ev100" in job:
    # an exposure other than the one the lighting level gives this place (the move sets its own, frame by frame)
    camera = [a for a in wl.actors() if a.get_actor_label() == wt.CAMERA_LABEL][0]
    wt._camera_exposure(camera.camera_component, job["ev100"])
    begin["exposure_from"] = "job, EV %s" % job["ev100"]
await wl.wait_frames(job.get("settle", 3.0))
record = await wt.render(name, "rt", BASE + "scratch/look", job.get("width", 1280), job.get("height", 720), warm_up_frames=job.get("warm_up_frames", 32), limit_seconds=240.0)
end = wt.end()
del wi.DESIGN_VIEWS[name]
json.dumps([name, record.get("seconds_to_file"), record.get("file_bytes"), begin.get("exposure_from"), end], default=str)
