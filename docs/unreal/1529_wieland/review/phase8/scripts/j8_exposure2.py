import sys, importlib, json, collections
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_fixtures as wf
importlib.reload(wl)
importlib.reload(wf)
out = {"hits": []}
rear = None
for x in (-1100.0, -1300.0, -500.0):
    start = unreal.Vector(x, -1500.0, 1178.6 + 100.0)
    for _ in range(12):
        hit = unreal.SystemLibrary.line_trace_single(wl.world(), start, unreal.Vector(x, -2700.0, start.z), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                     True, [], unreal.DrawDebugTrace.NONE, False)
        if not hit:
            break
        t = hit.to_tuple()
        label = t[9].get_actor_label() if t[9] else ""
        out["hits"].append((x, round(t[4].y, 1), label[:50]))
        if label.split("_")[0] in ("Walls", "Windows", "Doors", "Curtain"):
            rear = t[4].y if rear is None else max(rear, t[4].y)
            break
        start = unreal.Vector(x, t[4].y - 2.0, start.z)
out["rear_y"] = rear
if rear is not None:
    label = "LGT_Exposure_Interior_4th"
    x0, x1, y0, y1, z0, z1 = -1410.0, -98.0, rear + 5.0, -318.0, 1170.0, 1515.0
    volume = wl.by_label(label)
    volume.modify()
    volume.set_actor_location(unreal.Vector((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), False, False)
    volume.set_actor_scale3d(unreal.Vector((x1 - x0) / 200.0, (y1 - y0) / 200.0, (z1 - z0) / 200.0))
    o, e = volume.get_actor_bounds(False)
    out["box"] = [round(v, 1) for v in (o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z)]
# fixture bodies of the model that came without any light
with_light = set(key for key in wf._groups())
ids_with_light = set(rid for (_l, rid) in with_light)
bare = collections.Counter()
for (level, rid), meshes in wf._bodies().items():
    if rid not in ids_with_light:
        owner = meshes[0].get_owner() if meshes else None
        meta = wf._metadata(owner) if owner else {}
        bare[(meta.get("Element*Family", "?"), meta.get("Element*Type", "?"))] += 1
out["fixture_bodies_without_light"] = [(k[0], k[1], n) for k, n in bare.items()]
json.dumps(out)
