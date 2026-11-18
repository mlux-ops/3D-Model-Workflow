"""Phase 11 (J2): save, by name, the two levels whose ground objects received the cut meshes. Nothing else is saved."""
import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
result = wl.save(["/Game/Wieland1529/Surroundings/L_Surroundings", "/Game/Wieland1529/Surroundings/L_FarCity"])
meshes = {}
for actor in wl.actors():
    if actor.get_actor_label() in ("SG_lot_placeholder", "FAR_CityStandIn"):
        meshes[actor.get_actor_label()] = actor.static_mesh_component.static_mesh.get_path_name()
json.dumps({"save": result, "meshes": meshes}, default=str)
