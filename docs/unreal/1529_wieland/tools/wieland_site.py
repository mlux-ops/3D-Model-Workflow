"""Phase 7: the site, its surroundings and vegetation of 1529 N. Wieland. Editor-side code.

Runs inside the Unreal editor's Python interpreter (sent by ue_call.py):

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_site as ws

Nothing here saves the earlier production level, and nothing here edits an asset that Datasmith
created. Functions that save say so and save named assets only.
"""

import array
import asyncio
import json
import math
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


# ---------------------------------------------------------------------------------------------
# Step 7.0: placed copies of the earlier production level's 58 parts in a level of their own.

REVIEW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "review", "phase7").replace(os.sep, "/")
OLD_READBACK = REVIEW + "/old_level_readback.json"


def new_level(path):
    """Make a new, empty level at the path and open it. Refuses when the asset exists already."""
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return {"error": "exists already: " + path}
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    made = bool(subsystem.new_level(path))
    return {"made": made, "world": world_path()}


def _require(path):
    if world_path() != path:
        raise RuntimeError("refused: the open level is %s, not %s" % (world_path(), path))


def old_parts():
    with open(OLD_READBACK, encoding="utf-8") as handle:
        records = json.load(handle)
    return [r for r in records if r["class"] == "StaticMeshActor" and r["label"].startswith("R15_PART_")]


def place_parts(start=0, count=1):
    """Place copies of parts [start, start + count) of the J1 record in the open level L_Surroundings_R15.

    A copy shows the same mesh at the old place plus SHIFT, and carries the old object's material
    overrides. A part whose copy exists already is passed over. Nothing is saved here.
    """
    _require(R15_LEVEL)
    existing = {a.get_actor_label() for a in actors()}
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    made, skipped, problems = [], 0, []
    for record in old_parts()[start:start + count]:
        label = record["label"]
        if label in existing:
            skipped += 1
            continue
        part = record["components"][0]
        mesh = unreal.load_asset(part["mesh"])
        if mesh is None:
            problems.append(label + ": mesh missing")
            continue
        location = unreal.Vector(record["location"][0] + SHIFT[0], record["location"][1] + SHIFT[1], record["location"][2] + SHIFT[2])
        rotation = unreal.Rotator(pitch=record["rotation"][0], yaw=record["rotation"][1], roll=record["rotation"][2])
        actor = subsystem.spawn_actor_from_object(mesh, location, rotation)
        if actor is None:
            problems.append(label + ": no object could be placed")
            continue
        actor.set_actor_label(label)
        actor.set_actor_scale3d(unreal.Vector(*record["scale"]))
        kind = "Glass" if "_glass_" in label else "Opaque"
        actor.set_folder_path(unreal.Name("Surroundings R15/" + kind))
        actor.tags = [unreal.Name(TAG_R15), unreal.Name("W1529.Kind.R15" + kind)]
        component = actor.static_mesh_component
        component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
        component.set_editor_property("cast_shadow", part["cast_shadow"])
        for index, slot in enumerate(part["slots"]):
            if slot["override"]:
                material = unreal.load_asset(slot["shown"])
                if material is None:
                    problems.append("%s: override material of slot %d missing" % (label, index))
                else:
                    component.set_material(index, material)
        made.append(label)
    return {"made": len(made), "skipped": skipped, "problems": problems, "first": made[:1]}


def verify_parts():
    """Read-only. Compare every copy in the open level with the J1 record: mesh, place, materials shown."""
    found = {a.get_actor_label(): a for a in actors() if TAG_R15 in [str(t) for t in a.tags]}
    wrong, slots, worst = [], 0, 0.0
    parts = old_parts()
    for record in parts:
        actor = found.get(record["label"])
        if actor is None:
            wrong.append(record["label"] + ": missing")
            continue
        part = record["components"][0]
        component = actor.static_mesh_component
        if _path(component.static_mesh) != part["mesh"]:
            wrong.append(record["label"] + ": other mesh")
        origin, extent = actor.get_actor_bounds(False)
        want = [record["bounds_origin"][i] + SHIFT[i] for i in range(3)]
        off = max(abs(origin.x - want[0]), abs(origin.y - want[1]), abs(origin.z - want[2]),
                  abs(extent.x - record["bounds_extent"][0]), abs(extent.y - record["bounds_extent"][1]),
                  abs(extent.z - record["bounds_extent"][2]))
        worst = max(worst, off)
        if off > 0.01:
            wrong.append("%s: bounds differ by %.3f cm" % (record["label"], off))
        if component.get_num_materials() != len(part["slots"]):
            wrong.append(record["label"] + ": slot count")
            continue
        for index, slot in enumerate(part["slots"]):
            slots += 1
            if _path(component.get_material(index)) != slot["shown"]:
                wrong.append("%s: slot %d shows another material" % (record["label"], index))
        if bool(component.get_editor_property("cast_shadow")) != part["cast_shadow"]:
            wrong.append(record["label"] + ": shadow setting")
    return {"parts_in_record": len(parts), "copies": len(found), "slots_compared": slots,
            "largest_bounds_difference_cm": round(worst, 4), "wrong": wrong[:12], "wrong_count": len(wrong)}


def save_current(expected_path):
    """Save the open level by name; refuses when the open level is not the expected one."""
    _require(expected_path)
    if expected_path == OLD_LEVEL:
        raise RuntimeError("refused: the earlier production level is never saved")
    saved = bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
    return {"saved": saved, "level": expected_path, "still_marked": dirty()}


# ---------------------------------------------------------------------------------------------
# Height maps: the top surface of a mesh on a shared grid, read by rays cast straight down.

CELL = 50.0  # cm; cell (i, j) has its centre at ((i + 0.5) * CELL, (j + 0.5) * CELL) in level coordinates


async def height_grid(mesh_path, offset, out_prefix, top=60000.0, chunk=4000):
    """Read-only. Writes <out_prefix>.json (header) and <out_prefix>.f32 (rows of float32, -99999 = no hit).

    offset: where the mesh's origin stands in the level, [x, y, z] in cm.
    """
    mesh_asset = unreal.load_asset(mesh_path)
    if mesh_asset is None:
        return {"error": "mesh missing: " + mesh_path}
    dynamic = unreal.DynamicMesh()
    options = unreal.GeometryScriptCopyMeshFromAssetOptions()
    lod = unreal.GeometryScriptMeshReadLOD()
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh_asset, dynamic, options, lod)
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        return {"error": "mesh could not be read: " + mesh_path}
    triangles = dynamic.get_triangle_count()
    _, bvh = unreal.GeometryScript_MeshSpatial.build_bvh_for_mesh(dynamic)
    box = mesh_asset.get_bounding_box()
    i0 = int(math.floor((box.min.x + offset[0]) / CELL))
    i1 = int(math.floor((box.max.x + offset[0]) / CELL))
    j0 = int(math.floor((box.min.y + offset[1]) / CELL))
    j1 = int(math.floor((box.max.y + offset[1]) / CELL))
    ni, nj = i1 - i0 + 1, j1 - j0 + 1
    values = array.array("f", [-99999.0]) * (ni * nj)
    query = unreal.GeometryScriptSpatialQueryOptions()
    down = unreal.Vector(0.0, 0.0, -1.0)
    spatial = unreal.GeometryScript_MeshSpatial
    hits = 0
    done = 0
    for i in range(ni):
        x = (i0 + i + 0.5) * CELL - offset[0]
        for j in range(nj):
            y = (j0 + j + 0.5) * CELL - offset[1]
            _, hit, _ = spatial.find_nearest_ray_intersection_with_mesh(dynamic, bvh, unreal.Vector(x, y, top), down, query)
            if hit.hit:
                values[i * nj + j] = hit.hit_position.z + offset[2]
                hits += 1
            done += 1
            if done % chunk == 0:
                await asyncio.sleep(0)
    os.makedirs(os.path.dirname(out_prefix), exist_ok=True)
    with open(out_prefix + ".f32", "wb") as handle:
        values.tofile(handle)
    header = {"mesh": mesh_path, "offset": list(offset), "cell_cm": CELL, "i0": i0, "j0": j0, "ni": ni, "nj": nj,
              "triangles": triangles, "hits": hits}
    with open(out_prefix + ".json", "w", encoding="utf-8") as handle:
        json.dump(header, handle)
    return header


async def height_jobs(jobs_path, start=0, count=1000):
    """Read-only. Runs height_grid for jobs [start, start + count) of a JSON list of {name, mesh, offset, group}."""
    with open(jobs_path, "r", encoding="utf-8") as handle:
        jobs = json.load(handle)
    out = {"jobs": len(jobs), "done": 0, "errors": [], "cells_hit": 0}
    for job in jobs[start:start + count]:
        prefix = REVIEW + "/heights/" + job["group"] + "/" + job["name"]
        header = await height_grid(job["mesh"], job["offset"], prefix)
        if "error" in header:
            out["errors"].append(header["error"])
        else:
            out["done"] += 1
            out["cells_hit"] += header["hits"]
        await asyncio.sleep(0)
    return out
