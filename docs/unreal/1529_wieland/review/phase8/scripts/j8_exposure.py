import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
importlib.reload(wl)
EV = 9.0
out = {}
# where the 4th floor's rear glass stands (the terrace behind it is outdoors)
start = unreal.Vector(-1100.0, -1800.0, 1178.6 + 160.0)
hit = unreal.SystemLibrary.line_trace_single(wl.world(), start, start + unreal.Vector(0.0, -900.0, 0.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                             True, [], unreal.DrawDebugTrace.NONE, False)
t = hit.to_tuple() if hit else None
out["rear_of_4th_floor"] = {"y": round(t[4].y, 1), "object": t[9].get_actor_label()[:60]} if t else None
rear4 = (t[4].y + 5.0) if t else -2140.0
# name: (x0, x1, y0, y1, z0, z1) in cm, 7 cm inside the outer wall faces
BOXES = {"LGT_Exposure_Interior_LowerTo3rd": (-1410.0, -98.0, -2504.0, -318.0, -150.0, 1170.0),
         "LGT_Exposure_Interior_4th": (-1410.0, -98.0, rear4, -318.0, 1170.0, 1515.0)}
for label, (x0, x1, y0, y1, z0, z1) in BOXES.items():
    out[label] = {"added": wl.add_to_lighting(unreal.PostProcessVolume, label, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))}
    volume = wl.by_label(label)
    volume.modify()
    volume.set_actor_scale3d(unreal.Vector((x1 - x0) / 200.0, (y1 - y0) / 200.0, (z1 - z0) / 200.0))
    volume.set_editor_property("unbound", False)
    volume.set_editor_property("priority", 1.0)
    volume.set_editor_property("blend_radius", 0.0)
    out[label]["exposure"] = wl.set_exposure(label, EV)
    o, e = volume.get_actor_bounds(False)
    out[label]["box"] = [round(v, 1) for v in (o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z)]
out["dirty"] = wl.dirty()
json.dumps(out)
