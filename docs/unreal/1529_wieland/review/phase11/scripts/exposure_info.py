"""Phase 11: read the fixed exposure of each exposure volume of the lighting level and its box. Read-only."""
import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_interiors as wi
import wieland_truth as wt
out = {}
for label in list(wt.EXPOSURE_VOLUMES) + [wt.EXPOSURE_OUTDOORS]:
    volume = wl.by_label(label)
    if volume is None:
        out[label] = None
        continue
    origin, extent = volume.get_actor_bounds(False)
    ev = wl.read_exposure(label)["ev100"]
    out[label] = {"ev100": ev, "camera": wl.exposure_camera(ev),
                  "box": [[round(origin.x - extent.x), round(origin.x + extent.x)], [round(origin.y - extent.y), round(origin.y + extent.y)], [round(origin.z - extent.z), round(origin.z + extent.z)]]}
json.dumps({"volumes": out, "stand_ins": list(wi.REVIT_STAND_INS), "fov": wt.FOV})
