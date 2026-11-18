import sys, json, importlib, csv
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal

# Phase 9, steps 9.2, 9.3 and 9.5: a census of what the scene draws. Reads only; changes nothing.
# Per level: mesh components by kind, how many of the opaque ones are Nanite, how many cast shadow, how many can
# move, how often each mesh is repeated, and the trees with their wind. Writes review/phase9/census.csv (one row
# per mesh asset and level) and returns the totals.
OUT = T.rsplit("/", 1)[0] + "/review/phase9/census.csv"


def blend(material):
    try:
        return str(material.get_blend_mode()) if material is not None else "none"
    except Exception:
        return "unknown"


levels = {}
rows = {}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    level = actor.get_outer().get_outermost().get_name().split("/")[-1]
    entry = levels.setdefault(level, {"mesh_components": 0, "instances": 0, "opaque_nanite": 0, "opaque_not_nanite": 0,
                                      "see_through": 0, "cast_shadow": 0, "not_nanite_cast_shadow": 0, "movable": 0,
                                      "skinned": 0, "hidden": 0, "triangles_not_nanite": 0})
    for component in actor.get_components_by_class(unreal.MeshComponent):
        if isinstance(component, unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            if mesh is None:
                continue
            count = component.get_instance_count() if isinstance(component, unreal.InstancedStaticMeshComponent) else 1
            materials = component.get_materials()
            blends = [blend(m) for m in materials]
            see_through = any("TRANSLUCENT" in b or "ADDITIVE" in b for b in blends)
            nanite = bool(mesh.get_editor_property("nanite_settings").get_editor_property("enabled"))
            shadow = bool(component.get_editor_property("cast_shadow"))
            visible = component.is_visible() and not actor.is_temporarily_hidden_in_editor() and not actor.is_hidden_ed()
            entry["mesh_components"] += 1
            entry["instances"] += count
            if not visible:
                entry["hidden"] += 1
            if see_through:
                entry["see_through"] += 1
            elif nanite:
                entry["opaque_nanite"] += 1
            else:
                entry["opaque_not_nanite"] += 1
                if visible:
                    entry["triangles_not_nanite"] += mesh.get_num_triangles(0) * count
            if shadow:
                entry["cast_shadow"] += 1
                if not nanite and visible:
                    entry["not_nanite_cast_shadow"] += 1
            if component.get_editor_property("mobility") == unreal.ComponentMobility.MOVABLE:
                entry["movable"] += 1
            key = (level, mesh.get_path_name())
            row = rows.setdefault(key, {"level": level, "mesh": mesh.get_path_name(), "components": 0, "instances": 0,
                                        "nanite": nanite, "see_through": see_through, "cast_shadow": 0, "visible": 0,
                                        "triangles": mesh.get_num_triangles(0), "material_slots": len(materials)})
            row["components"] += 1
            row["instances"] += count
            row["cast_shadow"] += 1 if shadow else 0
            row["visible"] += 1 if visible else 0
        elif isinstance(component, (unreal.SkinnedMeshComponent, unreal.InstancedSkinnedMeshComponent)):
            entry["skinned"] += 1

with open(OUT, "w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["level", "mesh", "components", "instances", "nanite", "see_through",
                                                "cast_shadow", "visible", "triangles", "material_slots"])
    writer.writeheader()
    for key in sorted(rows):
        writer.writerow(rows[key])

repeated = sorted(((r["components"], r["level"], r["mesh"].split(".")[-1], r["nanite"], r["see_through"]) for r in rows.values()
                   if r["components"] >= 20), reverse=True)[:25]
not_nanite = sorted(((r["triangles"] * r["instances"], r["level"], r["mesh"].split(".")[-1], r["components"], r["cast_shadow"])
                     for r in rows.values() if not r["nanite"] and not r["see_through"] and r["visible"]), reverse=True)[:25]
json.dumps({"levels": levels, "most_repeated": repeated, "largest_opaque_not_nanite": not_nanite, "mesh_assets": len(rows)})
