"""Phase 5: build the candidates, and switch them on and off in the scene.

Runs inside the Unreal editor:

    import wieland_candidates as wc
    wc.build_candidates(csv_path)          # one instance per row, saved by name
    wc.alternatives_on(csv_path)           # show the candidates in the open level
    wc.alternatives_off()                  # back to the Revit materials

csv_path is material_candidates.csv, or material_alternatives.csv (the table of
swaps); both carry the columns material, revit_asset and candidate_asset.

A candidate is an instance (a material that only sets the values of a parent
material). A switchable alternative is a material swap the scene can turn on
and off: turning it on puts the candidate on every mesh slot of the open
level that shows the Revit material, as an override on the placed object;
turning it off removes exactly those overrides. No material, mesh or other
asset that Datasmith created is edited, and nothing is saved by these calls.
A level must never be saved while the alternatives are on.
"""

import csv
import json

import unreal

MEL = unreal.MaterialEditingLibrary
TAG = "W1529Alt"

_STATE = {"on": [], "table": None}


def _rows(csv_path):
    with open(csv_path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_candidates(csv_path, start=0, count=1000, rebuild=False):
    """Build and save the instances of rows [start, start + count); returns a summary."""
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    built, skipped, problems = [], 0, []
    for row in _rows(csv_path)[start:start + count]:
        path = row["candidate_asset"]
        exists = unreal.EditorAssetLibrary.does_asset_exist(path)
        if exists and not rebuild:
            skipped += 1
            continue
        try:
            if exists:
                instance = unreal.load_asset(path)
                MEL.clear_all_material_instance_parameters(instance)
            else:
                folder, name = path.rsplit("/", 1)
                instance = tools.create_asset(name, folder, unreal.MaterialInstanceConstant,
                                              unreal.MaterialInstanceConstantFactoryNew())
            parent = unreal.load_asset(row["parent"])
            if parent is None:
                raise RuntimeError("parent missing: " + row["parent"])
            MEL.set_material_instance_parent(instance, parent)
            for key, value in json.loads(row["switches"]).items():
                MEL.set_material_instance_static_switch_parameter_value(instance, key, bool(value))
            for key, value in json.loads(row["scalars"]).items():
                if not MEL.set_material_instance_scalar_parameter_value(instance, key, float(value)):
                    problems.append("%s: no number called %s" % (row["material"], key))
            for key, value in json.loads(row["vectors"]).items():
                if not MEL.set_material_instance_vector_parameter_value(instance, key, unreal.LinearColor(*value)):
                    problems.append("%s: no colour called %s" % (row["material"], key))
            for key, value in json.loads(row["textures"]).items():
                texture = unreal.load_asset(value)
                if texture is None:
                    problems.append("%s: image missing: %s" % (row["material"], value))
                    continue
                if not MEL.set_material_instance_texture_parameter_value(instance, key, texture):
                    problems.append("%s: no image called %s" % (row["material"], key))
            MEL.update_material_instance(instance)
            if not unreal.EditorAssetLibrary.save_asset(path, False):
                problems.append("%s: not saved" % row["material"])
            built.append(row["material"])
        except Exception as error:  # one bad row must not stop the rest
            problems.append("%s: %s" % (row["material"], error))
    return {"built": len(built), "skipped_existing": skipped, "problems": problems}


def _components():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        for component in actor.get_components_by_class(unreal.MeshComponent):
            yield actor, component


def count_uses(csv_path):
    """How many mesh slots of the open level show each Revit material that has a candidate."""
    wanted = {row["revit_asset"].split(".")[0]: row["material"] for row in _rows(csv_path)}
    uses = {}
    for _actor, component in _components():
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            if material is None:
                continue
            key = material.get_path_name().split(".")[0]
            if key in wanted:
                uses[wanted[key]] = uses.get(wanted[key], 0) + 1
    return uses


def largest_surfaces(csv_path, out_json):
    """For each Revit material that has a candidate: the largest placed object that shows it.

    Writes {material: {"largest_m": [a, b], "objects": n, "object": label, "at_cm": [x, y, z]}}; a and b are
    the two longest sides of the object's bounding box in metres, which bounds the largest uninterrupted
    surface from above.
    """
    wanted = {row["revit_asset"].split(".")[0]: row["material"] for row in _rows(csv_path)}
    found = {}
    for actor, component in _components():
        names = set()
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            if material is not None:
                name = wanted.get(material.get_path_name().split(".")[0])
                if name:
                    names.add(name)
        if not names:
            continue
        origin, extent = actor.get_actor_bounds(False)
        sides = sorted([extent.x * 0.02, extent.y * 0.02, extent.z * 0.02], reverse=True)
        for name in names:
            entry = found.setdefault(name, {"largest_m": [0.0, 0.0], "objects": 0, "object": "", "at_cm": []})
            entry["objects"] += 1
            if sides[0] * sides[1] > entry["largest_m"][0] * entry["largest_m"][1]:
                entry["largest_m"] = [round(sides[0], 3), round(sides[1], 3)]
                entry["object"] = actor.get_actor_label()
                entry["at_cm"] = [round(origin.x, 1), round(origin.y, 1), round(origin.z, 1)]
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(found, handle, indent=1, sort_keys=True)
    return {"materials_placed": len(found), "materials_not_placed": len(set(wanted.values()) - set(found))}


def alternatives_on(csv_path, only=None):
    """Put each candidate on every slot of the open level that shows its Revit material.

    Only slots that have no override of their own are touched, so that
    alternatives_off() can put back exactly what was there (nothing).
    """
    if _STATE["on"]:
        return {"error": "the alternatives are already on; call alternatives_off() first"}
    swaps = {}
    for row in _rows(csv_path):
        if only and row["material"] not in only:
            continue
        candidate = unreal.load_asset(row["candidate_asset"])
        if candidate is not None:
            swaps[row["revit_asset"].split(".")[0]] = candidate
    slots, kept = 0, 0
    for actor, component in _components():
        overrides = list(component.get_editor_property("override_materials"))
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            if material is None:
                continue
            candidate = swaps.get(material.get_path_name().split(".")[0])
            if candidate is None:
                continue
            if index < len(overrides) and overrides[index] is not None:
                kept += 1
                continue
            component.set_material(index, candidate)
            _STATE["on"].append((component, index))
            slots += 1
    return {"slots_switched": slots, "slots_left_because_they_had_their_own_override": kept,
            "candidates": len(swaps)}


def alternatives_off():
    """Remove exactly the overrides that alternatives_on() set."""
    removed = 0
    for component, index in _STATE["on"]:
        try:
            component.set_material(index, None)
            removed += 1
        except Exception:
            pass
    _STATE["on"] = []
    return {"slots_put_back": removed}


def alternatives_state():
    return {"slots_on": len(_STATE["on"])}


def dirty_packages():
    utils = unreal.EditorLoadingAndSavingUtils
    return sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))


def reload_dirty(prefixes):
    """Put packages the editor marked as changed back to their state on disk; nothing is saved."""
    utils = unreal.EditorLoadingAndSavingUtils
    packages = [p for p in list(utils.get_dirty_content_packages()) if p.get_name().startswith(tuple(prefixes))]
    if packages:
        utils.reload_packages(packages, unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE)
    return {"reloaded": len(packages), "still_marked": dirty_packages()}
