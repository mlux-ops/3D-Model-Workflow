import sys, json, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_site as ws
import wieland_truth as wt
# Phase 10, read-only: each station's camera as the pictures use it, and the highest visible surface of the
# site levels (ground, pavements, site works) straight under it. Nothing in the level is changed.
OUT = T.rsplit("/", 1)[0] + "/review/phase10/stations_now.json"
LEVELS = ("L_Surroundings", "L_SiteWorks", "L_Surroundings_R15")
spatial = unreal.GeometryScript_MeshSpatial
query = unreal.GeometryScriptSpatialQueryOptions()
down = unreal.Vector(0.0, 0.0, -1.0)
cameras = {}
for name in ("S1", "S2", "S3", "S4", "S5", "S6", "S9"):
    location, rotation = wt.view(name)
    cameras[name] = {"loc": [location.x, location.y, location.z], "rot": [rotation.pitch, rotation.yaw, rotation.roll],
                     "fov_h": wt.FOV, "under": []}
for actor in ws.actors():
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    level = ws.level_of(actor).rsplit("/", 1)[-1]
    if level not in LEVELS:
        continue
    component = actor.static_mesh_component
    mesh = component.static_mesh
    if mesh is None or not component.get_editor_property("visible") or actor.is_temporarily_hidden_in_editor():
        continue
    origin, extent = actor.get_actor_bounds(False)
    inside = [name for name, cam in cameras.items()
              if abs(cam["loc"][0] - origin.x) <= extent.x and abs(cam["loc"][1] - origin.y) <= extent.y]
    if not inside:
        continue
    dynamic = unreal.DynamicMesh()
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
        mesh, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        continue
    _, bvh = spatial.build_bvh_for_mesh(dynamic)
    inverse = actor.get_actor_transform().inverse()
    forward = actor.get_actor_transform()
    for name in inside:
        cam = cameras[name]
        start = unreal.MathLibrary.transform_location(inverse, unreal.Vector(cam["loc"][0], cam["loc"][1], cam["loc"][2]))
        _, hit, _ = spatial.find_nearest_ray_intersection_with_mesh(dynamic, bvh, start, down, query)
        if hit.hit:
            point = unreal.MathLibrary.transform_location(forward, hit.hit_position)
            cam["under"].append({"object": actor.get_actor_label(), "level": level, "z": round(point.z, 2)})
for cam in cameras.values():
    cam["under"].sort(key=lambda item: -item["z"])
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(cameras, handle, indent=1)
json.dumps({name: [cam["loc"][2], cam["under"][:2]] for name, cam in cameras.items()})
