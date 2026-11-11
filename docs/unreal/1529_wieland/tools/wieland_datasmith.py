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
