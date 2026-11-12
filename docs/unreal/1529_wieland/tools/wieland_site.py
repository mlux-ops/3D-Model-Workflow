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


# ---------------------------------------------------------------------------------------------
# Step 7.0: the earlier detailed buildings as the default view of L_Site_M2, switchable.

VARIANT_FOLDER = "/Game/Wieland1529/Surroundings"
VARIANT_ASSET = "LVS_W1529_Surroundings"
VARIANT_LIST = "Surroundings"
OPTION_R15 = "Earlier detailed buildings"
OPTION_PHASE4 = "Phase 4 survey massing"
VISIBLE_PROPERTY = "Static Mesh Component / Visible"
HIDDEN_LIST = REVIEW + "/phase4_hidden_buildings.json"


def add_sublevel(path):
    """With L_Site_M2 open: add a level to it as always loaded. Does nothing when it is there already."""
    _require(SITE_LEVEL)
    if path in levels():
        return {"added": False, "levels": levels()}
    streaming = unreal.EditorLevelUtils.add_level_to_world(world(), path, unreal.LevelStreamingAlwaysLoaded)
    return {"added": streaming is not None, "levels": levels()}


def hidden_names():
    with open(HIDDEN_LIST, "r", encoding="utf-8") as handle:
        return json.load(handle)["hidden_with_earlier_detailed_buildings"]


def _by_label(labels):
    wanted = set(labels)
    return {a.get_actor_label(): a for a in actors() if a.get_actor_label() in wanted}


def r15_copies():
    return [a for a in actors() if any(str(t) == TAG_R15 for t in a.tags)]


def set_visible(labels, visible):
    """Sets the mesh component of the named objects visible or not. Returns how many were changed."""
    found = _by_label(labels)
    changed = 0
    for label in labels:
        actor = found.get(label)
        if actor is None:
            continue
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if bool(component.get_editor_property("visible")) != bool(visible):
            component.modify()
            component.set_visibility(bool(visible), False)
            changed += 1
    return {"asked": len(labels), "found": len(found), "changed": changed}


def visible_state():
    """Read-only: how many of the earlier copies and of the Phase 4 buildings on the hide list are visible."""
    names = hidden_names()
    found = _by_label(names)
    copies = r15_copies()
    seen = lambda a: bool(a.get_component_by_class(unreal.StaticMeshComponent).get_editor_property("visible"))
    others = [a for a in actors() if a.get_actor_label().startswith("SB_") and a.get_actor_label() not in found]
    return {"earlier_copies": len(copies), "earlier_copies_visible": sum(1 for a in copies if seen(a)),
            "phase4_on_hide_list": len(found), "phase4_on_hide_list_visible": sum(1 for a in found.values() if seen(a)),
            "phase4_other_buildings": len(others), "phase4_other_buildings_visible": sum(1 for a in others if seen(a))}


def variant_asset():
    return unreal.load_asset(VARIANT_FOLDER + "/" + VARIANT_ASSET)


def build_variants():
    """Makes (or remakes) the list "Surroundings" with its two options and saves the asset by name.

    The values are written into the options directly: the earlier copies visible and the Phase 4 buildings
    of the hide list not visible, and the other way round.
    """
    _require(SITE_LEVEL)
    library = unreal.VariantManagerLibrary
    sets_asset = variant_asset()
    if sets_asset is None:
        sets_asset = library.create_level_variant_sets_asset(VARIANT_ASSET, VARIANT_FOLDER)
    for index in reversed(range(sets_asset.get_num_variant_sets())):
        old = sets_asset.get_variant_set(index)
        if str(old.get_display_text()) == VARIANT_LIST:
            library.remove_variant_set(sets_asset, old)
    variant_set = unreal.VariantSet()
    variant_set.set_display_text(VARIANT_LIST)
    library.add_variant_set(sets_asset, variant_set)
    copies = r15_copies()
    phase4 = list(_by_label(hidden_names()).values())
    result = {"earlier_copies": len(copies), "phase4_buildings": len(phase4), "values": 0, "missed": 0}
    for option in (OPTION_R15, OPTION_PHASE4):
        variant = unreal.Variant()
        variant.set_display_text(option)
        library.add_variant(variant_set, variant)
        for group, shown in ((copies, option == OPTION_R15), (phase4, option == OPTION_PHASE4)):
            for actor in group:
                library.add_actor_binding(variant, actor)
                value = library.capture_property(variant, actor, VISIBLE_PROPERTY)
                if value is None:
                    result["missed"] += 1
                    continue
                library.set_value_bool(value, shown)
                result["values"] += 1
    result["saved"] = bool(unreal.EditorAssetLibrary.save_loaded_asset(sets_asset, False))
    return result


def switch(option):
    """One action: put one option of the list "Surroundings" on."""
    sets_asset = variant_asset()
    if sets_asset is None:
        return {"error": "no variant asset"}
    for index in range(sets_asset.get_num_variant_sets()):
        variant_set = sets_asset.get_variant_set(index)
        if str(variant_set.get_display_text()) != VARIANT_LIST:
            continue
        for number in range(variant_set.get_num_variants()):
            variant = variant_set.get_variant(number)
            if str(variant.get_display_text()) == option:
                variant.switch_on()
                return {"option": option, "state": visible_state()}
    return {"error": "no such option: " + option}


def save_levels(paths):
    """Save the named loaded levels (the top level or its sublevels) by name. Refuses the earlier level."""
    out = {}
    for path in paths:
        if path == OLD_LEVEL or path not in levels():
            out[path] = "refused"
            continue
        package = unreal.find_package(path)
        out[path] = bool(unreal.EditorLoadingAndSavingUtils.save_packages([package], False)) if package else "no package"
    out["left_marked"] = dirty()
    return out


# ---------------------------------------------------------------------------------------------
# Station pictures from the editor's viewport (view mode Lit, a named quality, settings put back).

STATION_CAMERAS = REVIEW + "/../phase4/stations/station_cameras.json"
SHOT_TAG = "W1529TempStation"
QUALITY_SETTINGS = ("sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality", "sg.GlobalIlluminationQuality",
                    "sg.ReflectionQuality", "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality",
                    "sg.FoliageQuality", "sg.ShadingQuality", "sg.LandscapeQuality")
CAPTURE_SETTINGS = {"t.MaxFPS": 1000}
BEFORE_FILE = REVIEW + "/scratch/settings_before.json"   # kept in a file: the module is reloaded between calls


def _before_read():
    if os.path.exists(BEFORE_FILE):
        with open(BEFORE_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def _get(name):
    return unreal.SystemLibrary.get_console_variable_float_value(name)


def _set(name, value):
    text = str(int(value)) if float(value) == int(value) else str(value)
    unreal.SystemLibrary.execute_console_command(world(), "%s %s" % (name, text))


def settings_now():
    names = list(QUALITY_SETTINGS) + list(CAPTURE_SETTINGS) + ["r.RayTracing.Nanite.Mode", "r.Material.UseShaderCompilationParameters",
                                                             "r.Streaming.PoolSize", "r.ScreenPercentage"]
    return {name: _get(name) for name in names}


def shots_begin(quality=3):
    """Temporary cameras at the stations, the named quality (3 = Epic), the capture settings. Nothing is saved."""
    before = _before_read()
    if not before:
        before = {name: _get(name) for name in list(QUALITY_SETTINGS) + list(CAPTURE_SETTINGS)}
        os.makedirs(os.path.dirname(BEFORE_FILE), exist_ok=True)
        with open(BEFORE_FILE, "w", encoding="utf-8") as handle:
            json.dump(before, handle)
    for name in QUALITY_SETTINGS:
        _set(name, quality)
    for name, value in CAPTURE_SETTINGS.items():
        _set(name, value)
    with open(STATION_CAMERAS, "r", encoding="utf-8") as handle:
        cameras = json.load(handle)["cameras"]
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor.set_current_level_by_name(world_path().split("/")[-1])
    have = {str(t) for a in actors() for t in a.tags if SHOT_TAG in [str(x) for x in a.tags]}
    made = 0
    for name, record in cameras.items():
        if name in have:
            continue
        loc, rot = record["loc"], record["rot"]
        camera = subsystem.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2]))
        camera.set_actor_label("TEMP_" + name)
        camera.tags = [SHOT_TAG, name]
        component = camera.camera_component
        component.set_editor_property("field_of_view", record["fov_h"])
        component.set_editor_property("constrain_aspect_ratio", True)
        component.set_editor_property("aspect_ratio", 16.0 / 9.0)
        made += 1
    return {"cameras_made": made, "before": before, "now": settings_now()}


def shot(name, out_path, width=1920, height=1080):
    """Ask for one picture; the file appears a few frames later."""
    for actor in actors():
        tags = [str(t) for t in actor.tags]
        if SHOT_TAG in tags and name in tags:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            unreal.AutomationLibrary.take_high_res_screenshot(width, height, out_path, actor)
            return True
    return False


async def shots(names, folder, suffix, width=1920, height=1080, wait_frames=600):
    """Take the named station pictures one after the other, waiting for each file."""
    out = {}
    for name in names:
        path = "%s/%s_%s.png" % (folder, name, suffix)
        if os.path.exists(path):
            os.remove(path)
        if not shot(name, path, width, height):
            out[name] = "no camera"
            continue
        frames = 0
        while not os.path.exists(path) and frames < wait_frames:
            await asyncio.sleep(0.05)
            frames += 1
        out[name] = os.path.exists(path)
    return out


def shots_end():
    """Remove the temporary cameras and put the settings back. Returns what the settings read afterwards."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in list(actors()):
        if SHOT_TAG in [str(t) for t in actor.tags]:
            subsystem.destroy_actor(actor)
            removed += 1
    before = _before_read()
    for name, value in before.items():
        _set(name, value)
    if os.path.exists(BEFORE_FILE):
        os.remove(BEFORE_FILE)
    return {"cameras_removed": removed, "put_back": before, "now": settings_now(), "dirty": dirty()}


# ---------------------------------------------------------------------------------------------
# Raw mesh data of a part, for working out off line which triangles are ground and how far to move.

def _dynamic(mesh_path):
    mesh_asset = unreal.load_asset(mesh_path)
    if mesh_asset is None:
        raise RuntimeError("mesh missing: " + mesh_path)
    dynamic = unreal.DynamicMesh()
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
        mesh_asset, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        raise RuntimeError("mesh could not be read: " + mesh_path)
    return mesh_asset, dynamic


def dump_mesh(mesh_path, out_path):
    """Read-only. Writes vertex positions, triangle corners and triangle material numbers to a .npz file."""
    import numpy
    mesh_asset, dynamic = _dynamic(mesh_path)
    lists = unreal.GeometryScript_List
    # Each query returns its list and a flag for gaps in the numbering as its last two values.
    positions, vertex_gaps = unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dynamic, False)[-2:]
    corners, triangle_gaps = unreal.GeometryScript_MeshQueries.get_all_triangle_indices(dynamic, False)[-2:]
    material_ids = unreal.GeometryScript_Materials.get_all_triangle_material_i_ds(dynamic)[-2]
    p = numpy.array([(v.x, v.y, v.z) for v in lists.convert_vector_list_to_array(positions)], dtype=numpy.float64)
    t = numpy.array([(c.x, c.y, c.z) for c in lists.convert_triangle_list_to_array(corners)], dtype=numpy.int32)
    m = numpy.array(list(lists.convert_index_list_to_array(material_ids)), dtype=numpy.int32)
    slots = [(str(s.material_slot_name), _path(s.material_interface)) for s in mesh_asset.static_materials]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    numpy.savez_compressed(out_path, positions=p, triangles=t, material_ids=m,
                           slot_names=numpy.array([s[0] for s in slots]), slot_materials=numpy.array([s[1] for s in slots]))
    return {"vertices": int(p.shape[0]), "triangles": int(t.shape[0]), "material_ids": int(m.shape[0]), "slots": len(slots),
            "vertex_gaps": bool(vertex_gaps), "triangle_gaps": bool(triangle_gaps)}


async def dump_parts(start=0, count=100):
    out = {"done": 0, "triangles": 0, "gaps": []}
    for record in old_parts()[start:start + count]:
        mesh_path = record["components"][0]["mesh"]
        result = dump_mesh(mesh_path, REVIEW + "/fit/raw/" + record["label"] + ".npz")
        out["done"] += 1
        out["triangles"] += result["triangles"]
        if result["vertex_gaps"] or result["triangle_gaps"] or result["triangles"] != result["material_ids"]:
            out["gaps"].append(record["label"])
        await asyncio.sleep(0)
    return out


# ---------------------------------------------------------------------------------------------
# The fit: new mesh assets, made from the earlier parts' meshes, that sit on the surveyed ground.
# The earlier mesh assets are only read. What to leave out and how far to move is worked out off line
# by phase7_fit.py; here it is applied, written to a new asset and put on the copy as a recorded swap.

FIT_FOLDER = "/Game/Wieland1529/Surroundings/R15Fit"
FIT_SWAPS = REVIEW + "/r15_fit_swaps.csv"
TAG_GROUND_ONLY = "W1529.R15GroundOnly"


def fit_part(label):
    """Makes (or remakes) the fitted mesh asset of one part and puts it on the part's copy. Saves the asset by name.

    Returns one record for r15_fit_swaps.csv. A part of which nothing stays (ground only) gets no asset:
    its copy is made not visible and is given the tag W1529.R15GroundOnly in place of W1529.R15Copy.
    """
    import numpy
    record = [r for r in old_parts() if r["label"] == label][0]
    source_path = record["components"][0]["mesh"]
    raw = numpy.load(REVIEW + "/fit/raw/" + label + ".npz")
    plan = numpy.load(REVIEW + "/fit/plan/" + label + ".npz")
    actor = _by_label([label]).get(label)
    if actor is None:
        raise RuntimeError("copy missing: " + label)
    location, scale, rotation = actor.get_actor_location(), actor.get_actor_scale3d(), actor.get_actor_rotation()
    if (max(abs(location.x - SHIFT[0]), abs(location.y - SHIFT[1]), abs(location.z - SHIFT[2])) > 0.01
            or max(abs(scale.x - 1), abs(scale.y - 1), abs(scale.z - 1)) > 1e-6
            or max(abs(rotation.pitch), abs(rotation.yaw), abs(rotation.roll)) > 1e-6):
        raise RuntimeError("copy is not at the plain shift: " + label)
    component = actor.static_mesh_component
    out = {"part": label, "earlier_mesh": source_path, "fitted_mesh": "", "triangles_before": int(plan["triangles"]),
           "triangles_left_out": int(plan["remove"].shape[0]), "triangles_after": 0, "lowest_move_cm": "", "highest_move_cm": "",
           "nanite": "", "slots": "", "saved": "", "note": ""}
    kept = int(plan["triangles"]) - int(plan["remove"].shape[0])
    if kept == 0:
        component.modify()
        component.set_visibility(False, False)
        actor.modify()
        actor.tags = [unreal.Name(TAG_GROUND_ONLY)] + [t for t in actor.tags if str(t) not in (TAG_R15, TAG_GROUND_ONLY)]
        out["note"] = "ground only: nothing stays; the copy is not visible and is no longer in the list of options"
        return out
    source, dynamic = _dynamic(source_path)
    lists = unreal.GeometryScript_List
    positions = unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dynamic, False)[-2]
    now = numpy.array([(v.x, v.y, v.z) for v in lists.convert_vector_list_to_array(positions)], dtype=numpy.float64)
    if now.shape != raw["positions"].shape or float(numpy.abs(now - raw["positions"]).max()) > 1e-3:
        raise RuntimeError("the mesh read now differs from the raw data: " + label)
    lift = plan["lift"]
    moved = [unreal.Vector(float(p[0]), float(p[1]), float(p[2] + d)) for p, d in zip(now, lift)]
    edits = unreal.GeometryScript_MeshEdits
    edits.set_all_mesh_vertex_positions(dynamic, lists.convert_array_to_vector_list(moved))
    remove = [int(i) for i in plan["remove"]]
    if remove:
        edits.delete_triangles_from_mesh(dynamic, lists.convert_array_to_index_list(remove, unreal.GeometryScriptIndexType.TRIANGLE), True)
    after = int(dynamic.get_triangle_count())
    if after != kept:
        raise RuntimeError("%s: %d triangles stay in memory, %d expected" % (label, after, kept))
    target_path = FIT_FOLDER + "/SM_R15fit_" + label[len("R15_PART_"):]
    library = unreal.EditorAssetLibrary
    target = library.load_asset(target_path) if library.does_asset_exist(target_path) else library.duplicate_asset(source_path, target_path)
    if target is None:
        raise RuntimeError("no new asset: " + target_path)
    options = unreal.GeometryScriptCopyMeshToAssetOptions()
    options.enable_recompute_normals = False
    options.emit_transaction = False
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dynamic, target, options, unreal.GeometryScriptMeshWriteLOD())
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        raise RuntimeError("the new asset could not be written: " + target_path)
    # Nanite as on the earlier mesh: on for the opaque parts, off for the glass parts (Nanite cannot show see-through materials).
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    wanted = bool(meshes.get_nanite_settings(source).enabled)
    settings = meshes.get_nanite_settings(target)
    if bool(settings.enabled) != wanted:
        settings.enabled = wanted
        meshes.set_nanite_settings(target, settings, True)
    out["nanite"] = bool(meshes.get_nanite_settings(target).enabled)
    if out["nanite"] != wanted:
        raise RuntimeError("Nanite setting differs from the earlier mesh: " + target_path)
    same_slots = [_path(s.material_interface) for s in target.static_materials] == [_path(s.material_interface) for s in source.static_materials]
    shown_before = [_path(component.get_material(i)) for i in range(component.get_num_materials())]
    component.modify()
    component.set_static_mesh(target)
    shown_after = [_path(component.get_material(i)) for i in range(component.get_num_materials())]
    used = lift[numpy.unique(raw["triangles"][numpy.setdiff1d(numpy.arange(int(plan["triangles"])), plan["remove"])])]
    out.update({"fitted_mesh": target_path, "triangles_after": after,
                "lowest_move_cm": round(float(used.min()), 1), "highest_move_cm": round(float(used.max()), 1),
                "slots": "same" if same_slots and shown_before == shown_after else "DIFFERENT",
                "saved": bool(library.save_loaded_asset(target, False))})
    return out


async def fit_parts(start=0, count=1):
    """Fits parts [start, start + count) and writes or extends r15_fit_swaps.csv. Nothing but the new assets is saved."""
    import csv
    _require(SITE_LEVEL)
    rows, problems = [], []
    for record in old_parts()[start:start + count]:
        try:
            rows.append(fit_part(record["label"]))
        except Exception as error:
            problems.append("%s: %s" % (record["label"], error))
        await asyncio.sleep(0)
    known = {}
    if os.path.exists(FIT_SWAPS):
        with open(FIT_SWAPS, newline="", encoding="utf-8") as handle:
            known = {r["part"]: r for r in csv.DictReader(handle)}
    for row in rows:
        known[row["part"]] = row
    if known:
        with open(FIT_SWAPS, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(next(iter(known.values())).keys()))
            writer.writeheader()
            for part in sorted(known):
                writer.writerow(known[part])
    return {"done": len(rows), "problems": problems, "rows": rows if len(rows) <= 2 else len(rows), "dirty": dirty()}
