import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_site as ws
# Phase 10, read-only: every object of the vegetation level as it stands today (place, and the size of its box).
out = []
for actor in ws.actors():
    if not ws.level_of(actor).endswith("/L_Vegetation"):
        continue
    location = actor.get_actor_location()
    origin, extent = actor.get_actor_bounds(False)
    out.append({"label": actor.get_actor_label(), "class": actor.get_class().get_name(),
                "x": round(location.x, 1), "y": round(location.y, 1), "z": round(location.z, 1),
                "box_height_m": round(extent.z * 2 / 100.0, 2),
                "box_width_m": round(max(extent.x, extent.y) * 2 / 100.0, 2),
                "top_z": round(origin.z + extent.z, 1),
                "hidden": bool(actor.is_temporarily_hidden_in_editor())})
out.sort(key=lambda item: item["label"])
with open(T.rsplit("/", 1)[0] + "/review/phase10/trees_now.json", "w", encoding="utf-8") as handle:
    json.dump(out, handle, indent=1)
json.dumps({"objects": len(out), "first": out[:1]})
