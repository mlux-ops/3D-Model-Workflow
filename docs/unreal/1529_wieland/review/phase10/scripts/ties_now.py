import sys, json, os, array, asyncio
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
# Phase 10, read-only: a fine height map (5 cm cells) of the neighbouring buildings as they stand in the
# level today, in a window around each point that the plat of survey ties to a neighbour's wall.
# The windows: review/phase10/heights/ties_job.json = [{"name": ..., "x": cm, "y": cm, "half": cm}, ...]
# The objects: review/phase10/heights/objects.json (written by heights_now.py).
# Output: review/phase10/heights/ties/<name>.json and .f32 (rows of float32 along y, -99999 = no hit).
BASE = T.rsplit("/", 1)[0] + "/review/phase10/heights"
CELL = 5.0
with open(BASE + "/ties_job.json", "r", encoding="utf-8") as handle:
    windows = json.load(handle)
with open(BASE + "/objects.json", "r", encoding="utf-8") as handle:
    objects = [item for item in json.load(handle) if item["visible"]]
os.makedirs(BASE + "/ties", exist_ok=True)
spatial = unreal.GeometryScript_MeshSpatial
query = unreal.GeometryScriptSpatialQueryOptions()
down = unreal.Vector(0.0, 0.0, -1.0)
out = []
loaded = {}
for window in windows:
    half = window["half"]
    n = int(round(2 * half / CELL))
    values = array.array("f", [-99999.0]) * (n * n)
    used = []
    for item in objects:
        mesh = unreal.load_asset(item["mesh"])
        box = mesh.get_bounding_box()
        ox, oy, oz = item["offset"]
        if (box.max.x + ox < window["x"] - half or box.min.x + ox > window["x"] + half
                or box.max.y + oy < window["y"] - half or box.min.y + oy > window["y"] + half):
            continue
        if item["mesh"] not in loaded:
            dynamic = unreal.DynamicMesh()
            _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
                mesh, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
            if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
                continue
            _, bvh = spatial.build_bvh_for_mesh(dynamic)
            loaded[item["mesh"]] = (dynamic, bvh)
        dynamic, bvh = loaded[item["mesh"]]
        used.append(item["label"])
        done = 0
        for i in range(n):
            x = window["x"] - half + (i + 0.5) * CELL - ox
            for j in range(n):
                y = window["y"] - half + (j + 0.5) * CELL - oy
                _, hit, _ = spatial.find_nearest_ray_intersection_with_mesh(dynamic, bvh, unreal.Vector(x, y, 60000.0), down, query)
                if hit.hit and hit.hit_position.z + oz > values[i * n + j]:
                    values[i * n + j] = hit.hit_position.z + oz
                done += 1
                if done % 4000 == 0:
                    await asyncio.sleep(0)
    with open(BASE + "/ties/" + window["name"] + ".f32", "wb") as handle:
        values.tofile(handle)
    header = {"name": window["name"], "x": window["x"], "y": window["y"], "half": half, "cell_cm": CELL, "n": n, "objects": used,
              "hits": sum(1 for v in values if v > -90000.0)}
    with open(BASE + "/ties/" + window["name"] + ".json", "w", encoding="utf-8") as handle:
        json.dump(header, handle)
    out.append([header["name"], len(used), header["hits"]])
json.dumps(out)
