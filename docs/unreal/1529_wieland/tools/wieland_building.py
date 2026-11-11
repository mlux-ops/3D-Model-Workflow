"""Editor-side helper for the building level of Phase 3: what was imported, how it is grouped, and the
Unreal-side settings that have to be put back after every reimport.

Runs inside the Unreal editor's Python interpreter, with the building level open
(/Game/Wieland1529/Building/L_Building). Every function that changes anything refuses to run on any
other level. Nothing here saves; save the level and the changed assets by name afterwards.

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_building

The level frame is Phase 2's: the origin is the lot's south-west corner, north is -X, east is -Y,
centimetres. The lot is 1508.76 cm along the street (x from -1508.76 to 0) and 3115.06 cm deep
(y from -3115.06 to 0); its centre line, the party line between the two halves, is x = -754.38.

Everything here can be run again and gives the same result, so that after a reimport the same calls
put the grouping, the lights, the Nanite settings and the texture limits back:

    inventory(path)          read-only: every imported object with its Revit data, place, meshes, materials, lights
    apply_groups(path)       sort every object into a unit, a floor and a category; folders and tags
    group_counts()           read-only: how many objects each group holds
    hide_test()              hide each unit and each floor in turn and count what goes (nothing is saved)
    lights_off(path)         switch every imported light off and list it
    nanite_candidates()      read-only: which imported meshes are opaque and which are not
    set_nanite(...)          switch Nanite on for the opaque meshes, a batch at a time
    texture_report()         read-only: the imported textures by size
"""

import asyncio
import csv
import json
import time

import unreal

BUILDING_ROOT = "/Game/Wieland1529/Building/"
ASSET_ROOT = "/Game/Wieland1529/Building/Datasmith"
TAG_PREFIX = "W1529."

LOT_NORTH_X, LOT_SOUTH_X = -1508.76, 0.0
LOT_REAR_Y, LOT_FRONT_Y = -3115.06, 0.0
PARTY_LINE_X = -754.38

# Floor levels of the drawings, in cm above grade: 1st 203.2, 2nd 528.32, 3rd 853.44, 4th 1178.56, roof 1504.
# An object belongs to the highest floor whose threshold lies at or below its reference height.
FLOORS = (("Lower level and grade", "Lower", -1.0e9), ("1st floor", "Floor1", 195.0), ("2nd floor", "Floor2", 520.0),
          ("3rd floor", "Floor3", 845.0), ("4th floor", "Floor4", 1170.0), ("Roof", "Roof", 1495.0))
SEVERAL = ("Several floors", "Several")
# Which floors make a triplex and which a penthouse. Read from sheet T1.5 of drawing set 25-006: unit 2A is
# 2,807.11 sq ft, which is two equal floors of 1,403.56, and unit 1A is 3,043.84 sq ft over three levels.
TRIPLEX_FLOORS = ("Lower", "Floor1", "Floor2")
PENTHOUSE_FLOORS = ("Floor3", "Floor4", "Roof")
UNITS = {("North", "Triplex"): ("North triplex", "NorthTriplex"), ("North", "Penthouse"): ("North penthouse", "NorthPenthouse"),
         ("South", "Triplex"): ("South triplex", "SouthTriplex"), ("South", "Penthouse"): ("South penthouse", "SouthPenthouse")}
COMMON = ("Common to the building", "Common")
SITE = ("Site and surroundings", "Site")


def _world_path():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()


def _require_building_level():
    path = _world_path()
    if not path.startswith(BUILDING_ROOT):
        raise RuntimeError("refused: the open level is %s, not a level under %s" % (path, BUILDING_ROOT))
    return path


def _actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def _layers(actor):
    try:
        return [str(layer) for layer in actor.get_editor_property("layers")]
    except Exception:
        return []


def _revit_id(actor):
    for tag in actor.tags:
        text = str(tag)
        if text.startswith("Revit.Element.Id."):
            return text[len("Revit.Element.Id."):]
    return None


def _metadata(actor):
    data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
    if data is None:
        return {}
    values = data.get_editor_property("metadata") or {}
    return {str(key): str(value) for key, value in values.items()}


def _box(actor):
    """The actor's own extent in level coordinates: (x_min, y_min, z_min, x_max, y_max, z_max), and whether it has any size."""
    origin, extent = actor.get_actor_bounds(False)
    has_size = (extent.x + extent.y + extent.z) > 0.01
    if not has_size:
        location = actor.get_actor_location()
        return (location.x, location.y, location.z, location.x, location.y, location.z), False
    return (origin.x - extent.x, origin.y - extent.y, origin.z - extent.z, origin.x + extent.x, origin.y + extent.y, origin.z + extent.z), True


def _floor_of(reference_z):
    chosen = FLOORS[0]
    for floor in FLOORS:
        if reference_z >= floor[2]:
            chosen = floor
    return chosen[0], chosen[1]


def classify(category, box, has_size, is_light):
    """Half, floor and unit of one object from its category and its extent. Returns names and tag tokens."""
    x0, y0, z0, x1, y1, z1 = box
    height = z1 - z0
    centre_x, centre_y = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    if is_light or not has_size:
        reference = z0
    elif category == "Floors":
        reference = z1 - 2.0
    elif category == "Roofs":
        reference = z1
    elif category == "Ceilings":
        reference = z0
    else:
        reference = z0 + min(0.5 * height, 50.0)
    if has_size and height > 500.0 and category not in ("Floors", "Roofs", "Ceilings"):
        floor_name, floor_tag = SEVERAL
    else:
        floor_name, floor_tag = _floor_of(reference)
    on_lot = (LOT_NORTH_X - 50.0 <= centre_x <= LOT_SOUTH_X + 50.0) and (LOT_REAR_Y - 50.0 <= centre_y <= LOT_FRONT_Y + 50.0)
    if x1 <= PARTY_LINE_X + 30.0:
        half = "North"
    elif x0 >= PARTY_LINE_X - 30.0:
        half = "South"
    else:
        half = "Both"
    if category in ("Site", "Levels", "Views", "Location Data", "Survey Point", "Project Base Point") or not on_lot:
        unit_name, unit_tag = SITE
    elif half == "Both" or floor_tag == "Several":
        unit_name, unit_tag = COMMON
    else:
        kind = "Triplex" if floor_tag in TRIPLEX_FLOORS else "Penthouse"
        unit_name, unit_tag = UNITS[(half, kind)]
    return {"half": half, "floor": floor_name, "floor_tag": floor_tag, "unit": unit_name, "unit_tag": unit_tag}


def _records():
    """One record for every imported actor except the single top object."""
    records = []
    for actor in _actors():
        class_name = actor.get_class().get_name()
        if class_name == "DatasmithSceneActor":
            continue
        layers = _layers(actor)
        metadata = _metadata(actor)
        category = metadata.get("Element*Category") or (layers[0] if layers else "")
        box, has_size = _box(actor)
        is_light = isinstance(actor, unreal.Light)
        records.append({"actor": actor, "name": actor.get_name(), "label": actor.get_actor_label(), "class": class_name,
                        "layers": layers, "category": category, "family": metadata.get("Element*Family"),
                        "type": metadata.get("Element*Type"), "revit_id": _revit_id(actor), "box": box, "has_size": has_size,
                        "is_light": is_light})
    by_name = {record["name"]: record for record in records}
    # An object with no geometry of its own (a family's holder, a light's holder) takes its place from what hangs under it.
    for record in records:
        if record["has_size"] or record["is_light"]:
            continue
        stack = list(record["actor"].get_attached_actors())
        boxes = []
        while stack:
            child = stack.pop()
            child_record = by_name.get(child.get_name())
            if child_record is not None and (child_record["has_size"] or child_record["is_light"]):
                boxes.append(child_record["box"])
            stack.extend(child.get_attached_actors())
        if boxes:
            record["box"] = (min(b[0] for b in boxes), min(b[1] for b in boxes), min(b[2] for b in boxes),
                             max(b[3] for b in boxes), max(b[4] for b in boxes), max(b[5] for b in boxes))
            record["has_size"] = True
            record["from_children"] = True
    return records


def inventory(out_path):
    """Read-only: write every imported object with its Revit data, its place, its meshes, materials and lights."""
    rows = []
    material_use = {}
    mesh_use = {}
    for record in _records():
        actor = record["actor"]
        row = {k: record[k] for k in ("name", "label", "class", "layers", "category", "family", "type", "revit_id", "has_size")}
        row["box_cm"] = [round(v, 1) for v in record["box"]]
        row.update(classify(record["category"], record["box"], record["has_size"], record["is_light"]))
        meshes = []
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.static_mesh
            if mesh is None:
                continue
            materials = []
            for index in range(component.get_num_materials()):
                material = component.get_material(index)
                path = material.get_path_name() if material else None
                materials.append(path)
                if path:
                    material_use[path] = material_use.get(path, 0) + 1
            meshes.append({"mesh": mesh.get_path_name(), "materials": materials})
            mesh_use[mesh.get_path_name()] = mesh_use.get(mesh.get_path_name(), 0) + 1
        if meshes:
            row["meshes"] = meshes
        lights = []
        for component in actor.get_components_by_class(unreal.LightComponent):
            lights.append({"class": component.get_class().get_name(), "intensity": component.intensity,
                           "visible": bool(component.get_editor_property("visible"))})
        if lights:
            row["lights"] = lights
        rows.append(row)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"level": _world_path(), "written_unix": time.time(), "objects": rows, "material_use": material_use, "mesh_use": mesh_use}, handle)
    return {"objects": len(rows), "with_meshes": sum(1 for r in rows if "meshes" in r), "with_lights": sum(1 for r in rows if "lights" in r),
            "materials_in_use": len(material_use), "meshes_in_use": len(mesh_use), "without_revit_id": sum(1 for r in rows if not r["revit_id"])}


def apply_groups(out_csv):
    """Give every object a folder (Building/<unit>/<floor>/<category>) and three tags (unit, floor, half), and list them."""
    _require_building_level()
    rows = []
    for record in _records():
        actor = record["actor"]
        group = classify(record["category"], record["box"], record["has_size"], record["is_light"])
        category = record["category"] or "Uncategorised"
        folder = "Building/%s/%s/%s" % (group["unit"], group["floor"], category)
        tags = [tag for tag in actor.tags if not str(tag).startswith(TAG_PREFIX)]
        tags += [unreal.Name(TAG_PREFIX + "Unit." + group["unit_tag"]), unreal.Name(TAG_PREFIX + "Floor." + group["floor_tag"]),
                 unreal.Name(TAG_PREFIX + "Half." + group["half"])]
        actor.modify(True)
        actor.tags = tags
        actor.set_folder_path(unreal.Name(folder))
        rows.append({"actor_name": record["name"], "label": record["label"], "class": record["class"], "revit_element_id": record["revit_id"],
                     "category": category, "unit": group["unit"], "floor": group["floor"], "half": group["half"],
                     "x_min": round(record["box"][0], 1), "y_min": round(record["box"][1], 1), "z_min": round(record["box"][2], 1),
                     "x_max": round(record["box"][3], 1), "y_max": round(record["box"][4], 1), "z_max": round(record["box"][5], 1)})
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return group_counts()


def group_counts():
    """Read-only: how many objects carry each unit tag and each floor tag, and how many carry none."""
    units, floors, halves = {}, {}, {}
    total = untagged = 0
    for actor in _actors():
        if actor.get_class().get_name() == "DatasmithSceneActor":
            continue
        total += 1
        found = {"Unit": None, "Floor": None, "Half": None}
        for tag in actor.tags:
            text = str(tag)
            if text.startswith(TAG_PREFIX):
                kind, _, value = text[len(TAG_PREFIX):].partition(".")
                found[kind] = value
        if not found["Unit"] or not found["Floor"]:
            untagged += 1
            continue
        units[found["Unit"]] = units.get(found["Unit"], 0) + 1
        floors[found["Floor"]] = floors.get(found["Floor"], 0) + 1
        halves[found["Half"]] = halves.get(found["Half"], 0) + 1
    return {"objects": total, "without_a_group": untagged, "by_unit": units, "sum_of_units": sum(units.values()),
            "by_floor": floors, "sum_of_floors": sum(floors.values()), "by_half": halves}


def hide_test():
    """Hide each unit and then each floor in turn, count what is hidden, and show everything again. Nothing is saved."""
    _require_building_level()
    actors = [a for a in _actors() if a.get_class().get_name() != "DatasmithSceneActor"]
    tags_of = {a.get_name(): set(str(t) for t in a.tags) for a in actors}
    result = {"objects": len(actors), "groups": {}}
    counts = group_counts()
    for kind, values in (("Unit", counts["by_unit"]), ("Floor", counts["by_floor"])):
        for value, expected in values.items():
            tag = TAG_PREFIX + kind + "." + value
            hidden = 0
            for actor in actors:
                if tag in tags_of[actor.get_name()]:
                    actor.set_is_temporarily_hidden_in_editor(True)
                    hidden += 1
            still_shown_with_tag = sum(1 for a in actors if tag in tags_of[a.get_name()] and not a.is_temporarily_hidden_in_editor())
            for actor in actors:
                actor.set_is_temporarily_hidden_in_editor(False)
            result["groups"][kind + "." + value] = {"expected": expected, "hidden": hidden, "left_behind": still_shown_with_tag}
    result["all_shown_again"] = all(not a.is_temporarily_hidden_in_editor() for a in actors)
    return result


def lights_off(out_csv):
    """Switch every imported light off (its component's Visible setting) and list each with its fixture's name."""
    _require_building_level()
    rows = []
    for actor in _actors():
        components = actor.get_components_by_class(unreal.LightComponent)
        if not components:
            continue
        parent = actor.get_attach_parent_actor()
        fixture = parent if parent is not None and parent.get_class().get_name() != "DatasmithSceneActor" else actor
        for component in components:
            was = bool(component.get_editor_property("visible"))
            if was:
                actor.modify(True)
                component.set_editor_property("visible", False)
            ies = component.get_editor_property("ies_texture") if hasattr(component, "ies_texture") else None
            location = component.get_world_location()
            rows.append({"light_actor": actor.get_name(), "light_label": actor.get_actor_label(), "light_class": component.get_class().get_name(),
                         "fixture_label": fixture.get_actor_label(), "fixture_revit_element_id": _revit_id(fixture) or _revit_id(actor),
                         "fixture_family": _metadata(fixture).get("Element*Family"), "fixture_type": _metadata(fixture).get("Element*Type"),
                         "intensity": round(component.intensity, 3), "intensity_units": str(component.get_editor_property("intensity_units")).split(".")[-1].rstrip(">").split(":")[0],
                         "use_temperature": bool(component.get_editor_property("use_temperature")), "temperature_k": round(component.get_editor_property("temperature"), 0),
                         "light_distribution_file": ies.get_name() if ies else "",
                         "x_cm": round(location.x, 1), "y_cm": round(location.y, 1), "z_cm": round(location.z, 1),
                         "was_on": was, "is_on_now": bool(component.get_editor_property("visible"))})
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return {"lights": len(rows), "were_on": sum(1 for r in rows if r["was_on"]), "on_now": sum(1 for r in rows if r["is_on_now"]),
            "with_a_light_distribution_file": sum(1 for r in rows if r["light_distribution_file"]),
            "fixture_families": len(set(r["fixture_family"] for r in rows))}


def _imported_meshes():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    return [a for a in registry.get_assets_by_path(ASSET_ROOT, recursive=True) if str(a.asset_class_path.asset_name) == "StaticMesh"]


def nanite_candidates():
    """Read-only: the imported meshes sorted into opaque (to become Nanite) and not opaque (glass and the like, left as they are)."""
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    opaque, other, already = [], [], 0
    blend_counts = {}
    for data in _imported_meshes():
        mesh = data.get_asset()
        modes = set()
        for index in range(len(mesh.static_materials)):
            material = mesh.get_material(index)
            if material is not None:
                modes.add(str(material.get_blend_mode()).split(".")[-1].split(":")[0])
        for mode in modes:
            blend_counts[mode] = blend_counts.get(mode, 0) + 1
        is_opaque = bool(modes) and all(mode in ("BLEND_OPAQUE", "BLEND_MASKED") for mode in modes)
        if subsystem.get_nanite_settings(mesh).enabled:
            already += 1
        (opaque if is_opaque else other).append(str(data.package_name))
    return {"meshes": len(opaque) + len(other), "opaque": len(opaque), "not_opaque": len(other), "nanite_already_on": already,
            "blend_modes": blend_counts, "not_opaque_examples": [p.rsplit("/", 1)[-1] for p in other[:12]], "opaque_paths": opaque, "other_paths": other}


async def set_nanite(mesh_paths, start=0, count=120, enable=True):
    """Switch Nanite on (or off) for a batch of meshes. Returns where to start the next batch, or None when done."""
    _require_building_level()
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    changed = 0
    started = time.time()
    batch = mesh_paths[start:start + count]
    for number, path in enumerate(batch):
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        if mesh is None:
            continue
        settings = subsystem.get_nanite_settings(mesh)
        if bool(settings.enabled) != bool(enable):
            settings.enabled = bool(enable)
            subsystem.set_nanite_settings(mesh, settings, True)
            changed += 1
        if number % 20 == 19:
            await asyncio.sleep(0)
    nxt = start + len(batch)
    return {"from": start, "to": nxt, "changed": changed, "seconds": round(time.time() - started, 1), "next": nxt if nxt < len(mesh_paths) else None}


def texture_report():
    """Read-only: the imported textures, largest first, with the settings that decide how much video memory each can take."""
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    rows = []
    for data in registry.get_assets_by_path(ASSET_ROOT, recursive=True):
        if str(data.asset_class_path.asset_name) != "Texture2D":
            continue
        texture = data.get_asset()
        rows.append({"texture": str(data.asset_name), "path": str(data.package_name), "width": texture.blueprint_get_size_x(), "height": texture.blueprint_get_size_y(),
                     "virtual_texture": bool(texture.get_editor_property("virtual_texture_streaming")),
                     "max_texture_size": int(texture.get_editor_property("max_texture_size")),
                     "lod_bias": int(texture.get_editor_property("lod_bias")), "never_stream": bool(texture.get_editor_property("never_stream"))})
    rows.sort(key=lambda r: -(r["width"] * r["height"]))
    return rows
