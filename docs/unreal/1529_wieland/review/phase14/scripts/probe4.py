import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
w = wl.world()
def up(p, dz=4000):
    return unreal.SystemLibrary.line_trace_single(w, unreal.Vector(*p), unreal.Vector(p[0], p[1], p[2] + dz), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
def name(h):
    if h is None: return None
    try:
        return h.get_editor_property("component").get_owner().get_actor_label()[:50] + " z=%d" % h.get_editor_property("impact_point").z
    except Exception as e:
        return str(e)
out = {"roof": {}, "patio": {}}
for x in (-1330, -1100, -900, -754, -600, -400, -180):
    for y in (-700, -1100, -1411, -1700, -2000, -2300):
        h = up((x, y, 1681))
        out["roof"]["%d,%d" % (x, y)] = name(h)
for x in (-1300, -1190, -1000, -754, -500, -400, -250):
    for y in (-2600, -2750, -2900):
        out["patio]"] = None
        out["patio"]["%d,%d" % (x, y)] = name(up((x, y, 360)))
json.dumps(out)
