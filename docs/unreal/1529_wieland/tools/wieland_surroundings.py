"""Editor-side: turn the mesh files of build_surroundings.py into static meshes and placed objects.

Runs inside the Unreal editor's Python interpreter with the surroundings level open
(/Game/Wieland1529/Surroundings/L_Surroundings). It refuses to run on any other level. Nothing here
saves; save the level and the new assets by name afterwards.

    await wieland_surroundings.build("<folder of mesh files>", start=0, count=40)

Each mesh file becomes one static mesh asset under /Game/Wieland1529/Surroundings/Meshes and one
object in the level, placed at the file's pivot, in a folder and with tags that name its zone and
kind. A file whose object already exists in the level is skipped, so the call can be repeated.
"""

import asyncio
import json
import os
import time

import unreal

LEVEL_ROOT = "/Game/Wieland1529/Surroundings/"
MESH_ROOT = "/Game/Wieland1529/Surroundings/Meshes/"
GREY = "/Engine/BasicShapes/BasicShapeMaterial"
TAG_PREFIX = "W1529."


def _world_path():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()


def _require_level():
    path = _world_path()
    if not path.startswith(LEVEL_ROOT):
        raise RuntimeError("refused: the open level is %s, not a level under %s" % (path, LEVEL_ROOT))


def _existing():
    return {a.get_actor_label(): a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}


def _make_mesh(data):
    mesh = unreal.DynamicMesh()
    buffers = unreal.GeometryScriptSimpleMeshBuffers()
    buffers.vertices = [unreal.Vector(v[0], v[1], v[2]) for v in data["vertices"]]
    buffers.triangles = [unreal.IntVector(t[0], t[1], t[2]) for t in data["triangles"]]
    mesh.append_buffers_to_mesh(buffers)
    split = unreal.GeometryScriptSplitNormalsOptions()
    split.split_by_opening_angle = True
    split.opening_angle_deg = 35.0
    split.split_by_face_group = False
    mesh.compute_split_normals(split, unreal.GeometryScriptCalculateNormalsOptions())
    return mesh


async def build(folder, start=0, count=40):
    """Build a batch of mesh files. Returns where the next batch starts, or None when all are done."""
    _require_level()
    names = sorted(n for n in os.listdir(folder) if n.endswith(".json"))
    batch = names[start:start + count]
    existing = _existing()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    grey = unreal.EditorAssetLibrary.load_asset(GREY)
    made = skipped = failed = 0
    problems = []
    started = time.time()
    for file_name in batch:
        with open(os.path.join(folder, file_name), encoding="utf-8") as handle:
            data = json.load(handle)
        name = data["name"]
        if name in existing:
            skipped += 1
            continue
        asset_path = MESH_ROOT + name
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            static_mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        else:
            options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
            options.enable_nanite = True
            options.enable_collision = True
            options.enable_recompute_normals = False
            static_mesh, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(_make_mesh(data), asset_path, options)
        if static_mesh is None:
            failed += 1
            problems.append(name)
            continue
        pivot = data["pivot"]
        actor = actors.spawn_actor_from_object(static_mesh, unreal.Vector(pivot[0], pivot[1], pivot[2]), unreal.Rotator(0.0, 0.0, 0.0))
        if actor is None:
            failed += 1
            problems.append(name)
            continue
        actor.set_actor_label(name)
        kind = "Buildings" if data.get("kind") == "building" else "Ground"
        actor.set_folder_path(unreal.Name("Surroundings/Zone %d/%s" % (data.get("zone", 2), kind)))
        actor.tags = [unreal.Name(TAG_PREFIX + "Zone.%d" % data.get("zone", 2)), unreal.Name(TAG_PREFIX + "Kind." + kind)]
        component = actor.static_mesh_component
        if grey is not None:
            component.set_material(0, grey)
        component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
        made += 1
        await asyncio.sleep(0)
    nxt = start + len(batch)
    return {"from": start, "to": nxt, "of": len(names), "made": made, "skipped": skipped, "failed": failed, "problems": problems[:8],
            "seconds": round(time.time() - started, 1), "next": nxt if nxt < len(names) else None}


def summary():
    """Read-only: what the surroundings level holds."""
    zones, kinds = {}, {}
    total = 0
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        tags = [str(t) for t in actor.tags]
        if not any(t.startswith(TAG_PREFIX) for t in tags):
            continue
        total += 1
        for tag in tags:
            if tag.startswith(TAG_PREFIX + "Zone."):
                zones[tag[-1]] = zones.get(tag[-1], 0) + 1
            if tag.startswith(TAG_PREFIX + "Kind."):
                kinds[tag.split(".")[-1]] = kinds.get(tag.split(".")[-1], 0) + 1
    return {"level": _world_path(), "objects": total, "by_zone": zones, "by_kind": kinds}
