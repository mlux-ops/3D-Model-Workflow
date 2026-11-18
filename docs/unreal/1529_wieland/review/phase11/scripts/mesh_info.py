import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
out = {}
for actor in wl.actors():
    label = actor.get_actor_label()
    if label in ("SG_lot_placeholder", "FAR_CityStandIn"):
        comp = actor.static_mesh_component
        mesh = comp.static_mesh
        t = actor.get_actor_transform()
        out[label] = {"mesh": mesh.get_path_name(), "tris": mesh.get_num_triangles(0), "verts": mesh.get_num_vertices(0),
                      "nanite": mesh.get_editor_property("nanite_settings").enabled,
                      "materials": [m.get_path_name() if m else None for m in comp.get_materials()],
                      "loc": str(t.translation), "rot": str(t.rotation.rotator()), "scale": str(t.scale3d),
                      "mesh_bounds": str(mesh.get_bounding_box()), "level_package": actor.get_outermost().get_name(),
                      "cast_shadow": comp.cast_shadow, "mobility": str(comp.mobility)}
json.dumps(out)
