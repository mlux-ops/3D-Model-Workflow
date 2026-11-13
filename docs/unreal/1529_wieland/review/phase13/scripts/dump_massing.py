"""Phase 13 (closing check), read-only: dump the mesh of the Revit neighbour massing stand-in and the Revit grade,
with each mesh component's world placement, to test off line whether they have geometry on the hotel's land.
Run: python -B tools/ue_call.py py review/phase13/scripts/dump_massing.py 300 -> review/phase13/scratch/massing_*.npz"""
import importlib
import json
import sys

import unreal

TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
OUT = TOOLS.rsplit("/", 1)[0] + "/review/phase13/scratch"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_site
import wieland_interiors as wi

result = {}
for actor in wieland_site.actors():
    label = actor.get_actor_label()
    if label not in wi.REVIT_STAND_INS:
        continue
    for n, comp in enumerate(actor.get_components_by_class(unreal.StaticMeshComponent)):
        if comp.static_mesh is None:
            continue
        mesh_path = comp.static_mesh.get_path_name().split(".")[0]
        record = wieland_site.dump_mesh(mesh_path, "%s/massing_%s_%d.npz" % (OUT, label, n))
        t = comp.get_world_transform()
        loc, rot, sc = t.translation, t.rotation.rotator(), t.scale3d
        record.update({"actor": label, "level": actor.get_outermost().get_name(), "mesh": mesh_path,
                       "location": [loc.x, loc.y, loc.z], "rotation": [rot.pitch, rot.yaw, rot.roll],
                       "scale": [sc.x, sc.y, sc.z], "visible": bool(comp.get_editor_property("visible")),
                       "hidden_in_game": bool(comp.get_editor_property("hidden_in_game")),
                       "temporarily_hidden": bool(actor.is_temporarily_hidden_in_editor())})
        result["%s_%d" % (label, n)] = record
json.dumps(result, default=str)
