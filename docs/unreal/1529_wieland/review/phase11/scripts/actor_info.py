import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_interiors as wi
out = {"stand_ins": list(wi.REVIT_STAND_INS)}
for actor in wl.actors():
    label = actor.get_actor_label()
    if label in ("SG_lot_placeholder", "FAR_CityStandIn") or label in wi.REVIT_STAND_INS:
        origin, extent = actor.get_actor_bounds(False)
        out[label] = {"class": actor.get_class().get_name(), "level": actor.get_outer().get_outer().get_name() if actor.get_outer() else None,
                      "origin": [round(v, 1) for v in (origin.x, origin.y, origin.z)], "extent": [round(v, 1) for v in (extent.x, extent.y, extent.z)],
                      "hidden_editor": actor.is_temporarily_hidden_in_editor(), "hidden_game": actor.get_editor_property("hidden"),
                      "comps": [(c.get_name(), c.get_class().get_name(), c.is_visible(), str(c.get_collision_enabled())) for c in actor.get_components_by_class(unreal.PrimitiveComponent)][:6]}
json.dumps(out)
