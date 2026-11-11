"""Editor-side helper for the Datasmith import and reimport tests.

Runs inside the Unreal editor's Python interpreter. A Datasmith import blocks
the editor's main thread for minutes, and the tool call that starts it may
time out before it ends. So start_import() and start_reimport() write a JSON
record to the result path when the work ends, whether it succeeded or failed.
If the call times out, wait for that file; do not start the import again.
Then call the read-only helpers.

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_datasmith
    wieland_datasmith.start_import("<file.udatasmith>", "/Game/Wieland1529/Scratch/P1", "<result.json>")

Safety: every function that changes the level refuses to run unless the open
level lies under /Game/Wieland1529/Scratch/. Nothing here saves anything.
"""

import json
import os
import time
import traceback

import unreal

SCRATCH_ROOT = "/Game/Wieland1529/Scratch/"
_STATE = {}


def _world_path():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()


def _require_scratch_level():
    path = _world_path()
    if not path.startswith(SCRATCH_ROOT):
        raise RuntimeError("refused: the open level is %s, not a scratch level under %s" % (path, SCRATCH_ROOT))
    return path


def _write(record):
    with open(_STATE["result_path"], "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=1)


def _run():
    record = _STATE["record"]
    started = time.time()
    try:
        _require_scratch_level()
        if _STATE["kind"] == "import":
            scene = unreal.DatasmithSceneElement.construct_datasmith_scene_from_file(_STATE["file"])
            if scene is None:
                raise RuntimeError("the file could not be opened as a Datasmith scene")
            options = scene.get_options(unreal.DatasmithImportOptions)
            base = options.get_editor_property("base_options")
            base.set_editor_property("scene_handling", unreal.DatasmithImportScene.CURRENT_LEVEL)
            mesh_options = base.get_editor_property("static_mesh_options")
            mesh_options.set_editor_property("generate_lightmap_u_vs", bool(_STATE["lightmap_uvs"]))
            base.set_editor_property("static_mesh_options", mesh_options)
            options.set_editor_property("base_options", base)
            check = options.get_editor_property("base_options")
            record["options_as_set"] = {
                "scene_handling": str(check.get_editor_property("scene_handling")),
                "include_geometry": bool(check.get_editor_property("include_geometry")),
                "include_material": bool(check.get_editor_property("include_material")),
                "include_light": bool(check.get_editor_property("include_light")),
                "include_camera": bool(check.get_editor_property("include_camera")),
                "generate_lightmap_u_vs": bool(check.get_editor_property("static_mesh_options").get_editor_property("generate_lightmap_u_vs")),
            }
            result = scene.import_scene(_STATE["destination"])
        else:
            scene = unreal.DatasmithSceneElement.get_existing_datasmith_scene(_STATE["scene_asset"])
            if scene is None:
                raise RuntimeError("no imported Datasmith scene at " + _STATE["scene_asset"])
            result = scene.reimport_scene()
        record["import_succeed"] = bool(result.import_succeed)
        record["imported_actors"] = len(result.imported_actors)
        record["imported_meshes"] = len(result.imported_meshes)
        record["scene_asset"] = result.scene.get_path_name() if result.scene else None
        scene.destroy_scene()
    except Exception as exc:
        record["error"] = repr(exc)
        record["traceback"] = traceback.format_exc()[-2000:]
    record["seconds"] = round(time.time() - started, 1)
    record["finished_unix"] = time.time()
    _write(record)
    _STATE["done"] = True
    return record


def _schedule(kind, result_path, record):
    if os.path.exists(result_path):
        raise RuntimeError("result file already exists: " + result_path)
    _STATE["kind"] = kind
    _STATE["result_path"] = result_path
    _STATE["record"] = record
    _STATE["done"] = False
    return _run()


def start_import(file_path, destination_folder, result_path, lightmap_uvs=False):
    """Import file_path into the open scratch level. Blocks until the import ends."""
    level = _require_scratch_level()
    if not os.path.exists(file_path):
        raise RuntimeError("no such file: " + file_path)
    if not destination_folder.startswith(SCRATCH_ROOT):
        raise RuntimeError("refused: assets must go under " + SCRATCH_ROOT)
    _STATE.clear()
    _STATE.update(file=file_path, destination=destination_folder, lightmap_uvs=bool(lightmap_uvs))
    return _schedule("import", result_path, {
        "kind": "import",
        "file": file_path,
        "file_bytes": os.path.getsize(file_path),
        "destination": destination_folder,
        "level": level,
        "engine": unreal.SystemLibrary.get_engine_version(),
        "scheduled_unix": time.time(),
    })


def start_reimport(scene_asset_path, result_path):
    """Reimport an imported Datasmith scene asset from its recorded source file. Blocks until it ends."""
    level = _require_scratch_level()
    _STATE.clear()
    _STATE.update(scene_asset=scene_asset_path)
    return _schedule("reimport", result_path, {
        "kind": "reimport",
        "scene_asset": scene_asset_path,
        "level": level,
        "engine": unreal.SystemLibrary.get_engine_version(),
        "scheduled_unix": time.time(),
    })


def finish_asset_compilation():
    """Wait until the editor has finished preparing every loaded asset. Returns the seconds it took.

    In 5.9.0 a Datasmith reimport that replaces a changed mesh crashes the
    editor if that mesh is still being prepared in the background, which it is
    for some seconds after a level loads (reimport R2 of Phase 1). Call this in
    its own tool call after loading the level and before start_reimport().
    Never start a reimport in the call that loads the level.
    """
    started = time.time()
    unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()
    return round(time.time() - started, 2)


def source_file(scene_asset_path, new_file=None):
    """Read, and with new_file change, the source file an imported Datasmith scene asset records.

    The change is made to the loaded asset only; it reaches disk when the asset is saved.
    """
    asset = unreal.EditorAssetLibrary.load_asset(scene_asset_path)
    if asset is None:
        raise RuntimeError("no asset at " + scene_asset_path)
    data = asset.get_editor_property("asset_import_data")
    before = data.get_first_filename()
    if new_file is not None:
        if not os.path.exists(new_file):
            raise RuntimeError("no such file: " + new_file)
        data.scripted_add_filename(new_file, 0, "")
    return {"before": before, "now": data.get_first_filename()}


def count_components(prefixes=()):
    """Read-only: mesh and light components in the open level.

    Datasmith attaches some parts to one actor as components, so counting
    actors undercounts; this is the count to set beside the export file's
    ActorMesh and Light elements. For each text in prefixes it also counts the
    mesh components whose mesh asset name, or whose owning actor's label,
    begins with that text.
    """
    components = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors_components()
    meshes = 0
    meshes_without_mesh = 0
    lights = 0
    light_classes = {}
    distinct_meshes = set()
    by_mesh_name = {prefix: 0 for prefix in prefixes}
    by_actor_label = {prefix: 0 for prefix in prefixes}
    for component in components:
        if isinstance(component, unreal.StaticMeshComponent):
            meshes += 1
            mesh = component.static_mesh
            if mesh is None:
                meshes_without_mesh += 1
            else:
                distinct_meshes.add(mesh.get_path_name())
            owner = component.get_owner()
            label = owner.get_actor_label() if owner is not None else ""
            name = mesh.get_name() if mesh is not None else ""
            for prefix in prefixes:
                if name.startswith(prefix):
                    by_mesh_name[prefix] += 1
                if label.startswith(prefix):
                    by_actor_label[prefix] += 1
        elif isinstance(component, unreal.LightComponent):
            lights += 1
            class_name = component.get_class().get_name()
            light_classes[class_name] = light_classes.get(class_name, 0) + 1
    return {
        "level": _world_path(),
        "components": len(components),
        "static_mesh_components": meshes,
        "static_mesh_components_without_mesh": meshes_without_mesh,
        "distinct_meshes_in_use": len(distinct_meshes),
        "light_components": lights,
        "light_component_classes": light_classes,
        "mesh_components_by_mesh_name_prefix": by_mesh_name,
        "mesh_components_by_actor_label_prefix": by_actor_label,
    }


def check_assignments(table_path):
    """Read-only: which of the Unreal-side material assignments in the saved table are still in place.

    The table is the one written for the reimport rehearsal: "on_objects"
    (a material override on one placed object, stored in the level),
    "on_meshes" (a material slot changed on an imported mesh, stored in the
    mesh) and "extra_edits_to_imported_materials" (colour and glossiness set
    directly on imported materials).
    """
    with open(table_path, encoding="utf-8") as handle:
        table = json.load(handle)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    by_name = {}
    by_revit_id = {}
    for actor in actors:
        by_name[actor.get_name()] = actor
        for tag in actor.tags:
            text = str(tag)
            if text.startswith("Revit.Element.Id."):
                by_revit_id.setdefault(text, []).append(actor)
    rows = []
    number = 0
    for entry in table.get("on_objects", []):
        number += 1
        row = {"no": number, "kind": "on object", "what": entry.get("actor"), "kept": False}
        actor = by_name.get(entry.get("actor_name"))
        row["found_by"] = "actor name"
        if actor is None or actor.get_actor_label() != entry.get("actor"):
            candidates = by_revit_id.get(entry.get("revit_element_id"), [])
            same_label = [a for a in candidates if a.get_actor_label() == entry.get("actor")]
            actor = (same_label or candidates or [None])[0]
            row["found_by"] = "Revit element id"
        if actor is None:
            row["problem"] = "the object is not in the level"
        else:
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            if component is None:
                row["problem"] = "the object has no mesh component"
            else:
                material = component.get_material(entry.get("slot", 0))
                row["material_now"] = material.get_path_name() if material else None
                mesh = component.static_mesh
                row["mesh_now"] = mesh.get_path_name() if mesh else None
                row["same_mesh"] = row["mesh_now"] == entry.get("mesh")
                row["kept"] = row["material_now"] == entry.get("assigned_material")
        rows.append(row)
    for entry in table.get("on_meshes", []):
        number += 1
        row = {"no": number, "kind": "on mesh", "what": entry.get("mesh", "").rsplit(".", 1)[-1], "kept": False}
        mesh = unreal.EditorAssetLibrary.load_asset(entry.get("mesh"))
        if mesh is None:
            row["problem"] = "the mesh asset is not in the project"
        else:
            material = mesh.get_material(entry.get("slot", 0))
            row["material_now"] = material.get_path_name() if material else None
            row["kept"] = row["material_now"] == entry.get("assigned_material")
        rows.append(row)
    edits = []
    for entry in table.get("extra_edits_to_imported_materials", []):
        row = {"material": entry.get("material", "").rsplit("/", 1)[-1], "kept": False}
        instance = unreal.EditorAssetLibrary.load_asset(entry.get("material"))
        if instance is None:
            row["problem"] = "the material is not in the project"
        else:
            colour = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(instance, "DiffuseColor")
            gloss = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(instance, "Glossiness")
            row["colour_now"] = [round(colour.r, 4), round(colour.g, 4), round(colour.b, 4)]
            row["glossiness_now"] = round(gloss, 4)
            want = entry.get("set_to", {})
            want_colour = want.get("DiffuseColor", [None, None, None])
            colour_kept = all(w is not None and abs(n - w) < 0.002 for n, w in zip(row["colour_now"], want_colour))
            gloss_kept = want.get("Glossiness") is not None and abs(gloss - want["Glossiness"]) < 0.002
            row["kept"] = bool(colour_kept and gloss_kept)
        edits.append(row)
    return {
        "level": _world_path(),
        "kept_on_objects": sum(1 for r in rows if r["kind"] == "on object" and r["kept"]),
        "kept_on_meshes": sum(1 for r in rows if r["kind"] == "on mesh" and r["kept"]),
        "kept_total": sum(1 for r in rows if r["kept"]),
        "of": len(rows),
        "material_edits_kept": sum(1 for r in edits if r["kept"]),
        "material_edits_of": len(edits),
        "rows": rows,
        "material_edits": edits,
    }


def count_level():
    """Read-only: what the open level holds, by actor class, with the Datasmith counts."""
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    classes = {}
    mesh_actors = 0
    mesh_actors_without_mesh = 0
    lights = 0
    light_classes = {}
    revit_elements = set()
    for actor in actors:
        name = actor.get_class().get_name()
        classes[name] = classes.get(name, 0) + 1
        if isinstance(actor, unreal.StaticMeshActor):
            mesh_actors += 1
            component = actor.static_mesh_component
            if component is None or component.static_mesh is None:
                mesh_actors_without_mesh += 1
        if isinstance(actor, unreal.Light):
            lights += 1
            light_classes[name] = light_classes.get(name, 0) + 1
        for tag in actor.tags:
            text = str(tag)
            if text.startswith("Revit.Element.Id."):
                revit_elements.add(text)
    return {
        "level": _world_path(),
        "actors": len(actors),
        "classes": classes,
        "static_mesh_actors": mesh_actors,
        "static_mesh_actors_without_mesh": mesh_actors_without_mesh,
        "lights": lights,
        "light_classes": light_classes,
        "distinct_revit_element_ids": len(revit_elements),
    }


def bounds_by_tag(tag_text):
    """Read-only: bounding boxes (cm) of every actor carrying the given tag."""
    found = []
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if any(str(tag) == tag_text for tag in actor.tags):
            origin, extent = actor.get_actor_bounds(False)
            found.append({
                "label": actor.get_actor_label(),
                "class": actor.get_class().get_name(),
                "min": [origin.x - extent.x, origin.y - extent.y, origin.z - extent.z],
                "max": [origin.x + extent.x, origin.y + extent.y, origin.z + extent.z],
            })
    return found


def bounds_by_label(label_part):
    """Read-only: bounding boxes (cm) of every actor whose label contains label_part."""
    found = []
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        label = actor.get_actor_label()
        if label_part in label:
            origin, extent = actor.get_actor_bounds(False)
            found.append({
                "label": label,
                "class": actor.get_class().get_name(),
                "tags": [str(tag) for tag in actor.tags][:6],
                "min": [origin.x - extent.x, origin.y - extent.y, origin.z - extent.z],
                "max": [origin.x + extent.x, origin.y + extent.y, origin.z + extent.z],
            })
    return found
