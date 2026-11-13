import sys, json, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_site as ws
# Phase 10, read-only: the top surface of every neighbouring building as it stands in the level today
# (the earlier detailed buildings after Phase 7's fit to the ground), on the shared 0.5 m grid, by rays cast
# straight down on each mesh. One height map per placed object, in review/phase10/heights/r15fit/.
# The job: review/phase10/heights/job.json = {"start": n, "count": n}. Nothing in the level is changed.
BASE = T.rsplit("/", 1)[0] + "/review/phase10/heights"
with open(BASE + "/job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
found = []
for actor in ws.actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if not ws.level_of(actor).endswith("L_Surroundings_R15"):
        continue
    component = actor.static_mesh_component
    mesh = component.static_mesh
    if mesh is None:
        continue
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    found.append({"label": actor.get_actor_label(), "mesh": mesh.get_path_name().split(".")[0],
                  "offset": [location.x, location.y, location.z],
                  "rotation": [rotation.pitch, rotation.yaw, rotation.roll],
                  "scale": [scale.x, scale.y, scale.z],
                  "visible": bool(component.get_editor_property("visible")),
                  "hidden_in_editor": bool(actor.is_temporarily_hidden_in_editor()),
                  "tags": [str(tag) for tag in actor.tags]})
found.sort(key=lambda item: item["label"])
with open(BASE + "/objects.json", "w", encoding="utf-8") as handle:
    json.dump(found, handle, indent=1)
out = {"objects": len(found), "done": [], "skipped": [], "errors": []}
for item in found[job["start"]:job["start"] + job["count"]]:
    plain = (all(abs(v) < 1e-4 for v in item["rotation"]) and all(abs(v - 1.0) < 1e-6 for v in item["scale"]))
    if not plain or not item["visible"]:
        out["skipped"].append([item["label"], "turned or scaled" if not plain else "not visible"])
        continue
    header = await ws.height_grid(item["mesh"], item["offset"], BASE + "/r15fit/" + item["label"])
    if "error" in header:
        out["errors"].append(header["error"])
    else:
        out["done"].append([item["label"], header["triangles"], header["hits"]])
json.dumps(out)
