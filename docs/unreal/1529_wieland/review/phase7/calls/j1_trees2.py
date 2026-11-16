import json
import sys
sys.dont_write_bytecode = True
out = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if actor.get_actor_label() != "R15_InstancedTrees":
        continue
    for c in actor.get_components_by_class(unreal.InstancedSkinnedMeshComponent):
        row = {"component": c.get_name(), "asset": c.get_editor_property("skinned_asset").get_path_name().split(".")[0]}
        ct = c.get_world_transform()
        row["component_location"] = [ct.translation.x, ct.translation.y, ct.translation.z]
        inst = []
        for d in c.get_editor_property("instance_data"):
            fields = {}
            for name in ("transform", "animation_index"):
                try:
                    v = d.get_editor_property(name)
                    if name == "transform":
                        q = v.rotation
                        v = [v.translation.x, v.translation.y, v.translation.z, q.x, q.y, q.z, q.w, v.scale3d.x, v.scale3d.y, v.scale3d.z]
                    fields[name] = v
                except Exception as error:
                    fields[name] = "unreadable: %s" % error
            inst.append(fields)
        row["instances"] = inst
        for prop in ("transform_provider", "cast_shadow", "mobility", "num_custom_data_floats", "disallow_nanite", "evaluate_world_position_offset"):
            try:
                row[prop] = str(c.get_editor_property(prop))
            except Exception as error:
                row[prop] = "unreadable"
        o, e, _radius = unreal.SystemLibrary.get_component_bounds(c)
        row["bounds_origin"] = [o.x, o.y, o.z]
        row["bounds_extent"] = [e.x, e.y, e.z]
        row["materials"] = [m.get_path_name().split(".")[0] if m else "" for m in c.get_materials()]
        out.append(row)
path = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase7/old_level_trees.json"
with open(path, "w", encoding="utf-8") as handle:
    json.dump(out, handle, indent=1)
[(r["component"], [round(x, 3) for x in r["instances"][0]["transform"]] if isinstance(r["instances"][0]["transform"], list) else r["instances"][0], r["cast_shadow"], r["mobility"], len(r["materials"])) for r in out]
