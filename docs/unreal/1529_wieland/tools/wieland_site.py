"""Phase 7: the site, its surroundings and vegetation of 1529 N. Wieland. Editor-side code.

Runs inside the Unreal editor's Python interpreter (sent by ue_call.py):

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_site as ws

Nothing here saves the earlier production level, and nothing here edits an asset that Datasmith
created. Functions that save say so and save named assets only.
"""

import json
import os

import unreal

OLD_LEVEL = "/Game/Wieland/R15_Landscape/L_R15_Production"
SITE_LEVEL = "/Game/Wieland1529/L_Site_M2"
PHASE4_LEVEL = "/Game/Wieland1529/Surroundings/L_Surroundings"
R15_LEVEL = "/Game/Wieland1529/Surroundings/L_Surroundings_R15"
VEGETATION_LEVEL = "/Game/Wieland1529/Vegetation/L_Vegetation"
# The earlier production level sits in the Phase 2 frame by a shift only (Phase 3, phase3_results.md).
SHIFT = (15482.32, 5053.7, 0.0)
TAG_GENERATED = "W1529.Generated"
TAG_PLACEHOLDER = "W1529.Placeholder"
TAG_R15 = "W1529.R15Copy"


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def world_path():
    return world().get_path_name().split(".")[0]


def actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def level_of(actor):
    """Package path of the level that holds the object."""
    return actor.get_outer().get_outer().get_path_name().split(".")[0]


def levels():
    return [level.get_outer().get_path_name().split(".")[0] for level in unreal.EditorLevelUtils.get_levels(world())]


def dirty():
    utils = unreal.EditorLoadingAndSavingUtils
    return sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))


def open_level(path, discard=True):
    """Open a level; with discard, changes in the level open now are thrown away, never saved."""
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if discard:
        return bool(subsystem.load_level(path, unreal.LevelEditorUnsavedChangesPolicy.DISCARD))
    return bool(subsystem.load_level(path))


def _path(thing):
    return thing.get_path_name().split(".")[0] if thing is not None else ""


def _vec(v):
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


def _rot(r):
    return [round(r.pitch, 4), round(r.yaw, 4), round(r.roll, 4)]


def _component_record(component):
    mesh = component.static_mesh
    overrides = list(component.get_editor_property("override_materials"))
    slots = []
    for index in range(component.get_num_materials()):
        shown = component.get_material(index)
        own = mesh.get_material(index) if mesh is not None else None
        slots.append({"shown": _path(shown), "mesh": _path(own),
                      "override": bool(index < len(overrides) and overrides[index] is not None)})
    transform = component.get_world_transform()
    record = {"component": component.get_name(), "class": component.get_class().get_name(), "mesh": _path(mesh),
              "location": _vec(transform.translation), "rotation": _rot(transform.rotation.rotator()),
              "scale": _vec(transform.scale3d), "slots": slots,
              "cast_shadow": bool(component.get_editor_property("cast_shadow")),
              "visible": bool(component.get_editor_property("visible")),
              "mobility": str(component.get_editor_property("mobility"))}
    if mesh is not None:
        meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        record["nanite"] = bool(meshes.get_nanite_settings(mesh).enabled)
        box = mesh.get_bounding_box()
        record["mesh_box"] = [_vec(box.min), _vec(box.max)]
    if isinstance(component, unreal.InstancedStaticMeshComponent):
        count = component.get_instance_count()
        record["instances"] = count
        places = []
        for index in range(count):
            t = component.get_instance_transform(index, True)
            places.append(_vec(t.translation) + _rot(t.rotation.rotator()) + _vec(t.scale3d))
        record["instance_transforms"] = places
    return record


def inspect_level(level_path, out_json):
    """Read-only. Every object of one loaded level: label, class, place, bounds, meshes and materials."""
    records = []
    for actor in actors():
        if level_of(actor) != level_path:
            continue
        origin, extent = actor.get_actor_bounds(False)
        record = {"label": actor.get_actor_label(), "name": actor.get_name(), "class": actor.get_class().get_name(),
                  "location": _vec(actor.get_actor_location()), "rotation": _rot(actor.get_actor_rotation()),
                  "scale": _vec(actor.get_actor_scale3d()), "bounds_origin": _vec(origin), "bounds_extent": _vec(extent),
                  "folder": str(actor.get_folder_path()), "tags": [str(t) for t in actor.tags],
                  "hidden": bool(actor.is_temporarily_hidden_in_editor()),
                  "components": [_component_record(c) for c in actor.get_components_by_class(unreal.StaticMeshComponent)]}
        records.append(record)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=1)
    classes = {}
    for record in records:
        classes[record["class"]] = classes.get(record["class"], 0) + 1
    return {"level": level_path, "objects": len(records), "classes": classes}
