import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_site as ws
# Phase 10, read-only: the sun as the lighting level holds it today. The light shines along its forward
# direction, so the sun stands at the opposite bearing; a level heading of -88.82 degrees is true bearing 90.
out = []
for actor in ws.actors():
    if isinstance(actor, unreal.DirectionalLight):
        forward = actor.get_actor_forward_vector()
        yaw_to_sun = unreal.MathLibrary.deg_atan2(-forward.y, -forward.x)
        height = unreal.MathLibrary.deg_asin(-forward.z)
        component = actor.light_component
        out.append({"label": actor.get_actor_label(), "level": ws.level_of(actor),
                    "sun_true_bearing_deg": round((yaw_to_sun + 178.82) % 360.0, 3), "sun_height_deg": round(height, 3),
                    "lux": component.get_editor_property("intensity"), "visible": bool(component.get_editor_property("visible")),
                    "affects_world": bool(component.get_editor_property("affects_world"))})
with open(T.rsplit("/", 1)[0] + "/review/phase10/sun_now.json", "w", encoding="utf-8") as handle:
    json.dump(out, handle, indent=1)
json.dumps(out)
