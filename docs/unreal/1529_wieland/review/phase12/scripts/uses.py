import sys, json, csv, re, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
# Read-only: for every Revit material shown in the open world, which placed objects show it
# (level, object label, bounding box sides of the mesh part in metres), and the largest part per material.
ROOT = os.path.dirname(T)
OUT = ROOT + "/review/phase12/uses.json"
PREFIX = "/Game/Wieland1529/Building/Datasmith/25-006_1527_N_Wieland-3DView-3D_View_188/Materials/"
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
found = {}
for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
    level = actor.get_outer().get_outer().get_name()
    for component in actor.get_components_by_class(unreal.MeshComponent):
        overrides = list(component.get_editor_property("override_materials"))
        mesh = component.static_mesh if isinstance(component, unreal.StaticMeshComponent) else None
        for index in range(component.get_num_materials()):
            shown = component.get_material(index)
            base = mesh.get_material(index) if mesh is not None else None
            for material, kind in ((shown, "shown"), (base, "mesh")):
                if material is None:
                    continue
                path = material.get_path_name().split(".")[0]
                if not path.startswith(PREFIX):
                    continue
                name = path[len(PREFIX):]
                entry = found.setdefault(name, {"slots_shown": 0, "slots_mesh": 0, "overridden": 0, "levels": {},
                                                "labels": {}, "largest_m": [0.0, 0.0], "largest": ""})
                if kind == "shown":
                    entry["slots_shown"] += 1
                else:
                    entry["slots_mesh"] += 1
                    if index < len(overrides) and overrides[index] is not None:
                        entry["overridden"] += 1
                    entry["levels"][level] = entry["levels"].get(level, 0) + 1
                    label = re.sub(r"[_ ]?\d+$", "", actor.get_actor_label())
                    entry["labels"][label] = entry["labels"].get(label, 0) + 1
                    origin, extent, radius = unreal.SystemLibrary.get_component_bounds(component)
                    sides = sorted([extent.x * 0.02, extent.y * 0.02, extent.z * 0.02], reverse=True)
                    if sides[0] * sides[1] > entry["largest_m"][0] * entry["largest_m"][1]:
                        entry["largest_m"] = [round(sides[0], 3), round(sides[1], 3)]
                        entry["largest"] = actor.get_actor_label()
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(found, handle, indent=1, sort_keys=True)
json.dumps({"materials": len(found), "slots_mesh": sum(e["slots_mesh"] for e in found.values()),
            "overridden": sum(e["overridden"] for e in found.values())})
