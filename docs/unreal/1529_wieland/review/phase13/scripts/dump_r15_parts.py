"""Phase 13, step 13.1, read-only: write the raw mesh data of the earlier detailed building parts that reach
onto the planned development's land, with each part's placement, for working out off line which triangles
stand on the land. Nothing in the project is changed.
"""
import importlib
import json
import sys

import unreal

TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
OUT = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase13/scratch"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_site
importlib.reload(wieland_site)

LABELS = ["R15_PART_opaque_xm04_yp01_part01", "R15_PART_glass_xm04_yp01_part01",
          "R15_PART_opaque_xm04_yp02_part01", "R15_PART_glass_xm04_yp02_part01"]
found = {a.get_actor_label(): a for a in wieland_site.actors() if a.get_actor_label() in LABELS}
result = {}
for label in LABELS:
    actor = found[label]
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    mesh_path = component.static_mesh.get_path_name().split(".")[0]
    record = wieland_site.dump_mesh(mesh_path, OUT + "/" + label + ".npz")
    location, rotation, scale = actor.get_actor_location(), actor.get_actor_rotation(), actor.get_actor_scale3d()
    record.update({"mesh": mesh_path, "location": [location.x, location.y, location.z],
                   "rotation": [rotation.pitch, rotation.yaw, rotation.roll], "scale": [scale.x, scale.y, scale.z],
                   "materials": [component.get_material(i).get_path_name() if component.get_material(i) else None
                                 for i in range(component.get_num_materials())]})
    result[label] = record
json.dumps(result)
