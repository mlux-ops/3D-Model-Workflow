"""Phase 11: list the walls and floors that reach below the lot's ground plane (z -1), to find the outline of the lower level. Read-only."""
import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
rows = []
for actor in wl.actors():
    label = actor.get_actor_label()
    if not (label.startswith("Walls_") or label.startswith("Floors_")):
        continue
    origin, extent = actor.get_actor_bounds(False)
    lo, hi = origin.z - extent.z, origin.z + extent.z
    if lo < -30.0 and hi > -150.0:
        rows.append([label[:70], round(origin.x - extent.x), round(origin.x + extent.x), round(origin.y - extent.y), round(origin.y + extent.y), round(lo), round(hi)])
rows.sort(key=lambda r: (r[0][:12], r[1], r[3]))
json.dumps(rows)
