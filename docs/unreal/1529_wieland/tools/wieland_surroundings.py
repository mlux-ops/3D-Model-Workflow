"""Editor-side: turn the mesh files of build_surroundings.py into static meshes and placed objects.

Runs inside the Unreal editor's Python interpreter with the surroundings level open
(/Game/Wieland1529/Surroundings/L_Surroundings). It refuses to run on any other level. Nothing here
saves; save the level and the new assets by name afterwards.

    await wieland_surroundings.check("<folder of mesh files>", start=0, count=40)    # read-only count
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
    """Build the mesh of one file in memory. Returns the mesh and a record of what was counted on it.

    A static mesh must have at least one UV channel (a set of texture coordinates); the editor stops with
    "NumUVs > 0" on one that has none (2026-11-11). So channel 0 is filled twice over: per vertex in the
    buffers, and then by a box projection of 1 m, which also gives walls coordinates that are not squashed.
    """
    mesh = unreal.DynamicMesh()
    buffers = unreal.GeometryScriptSimpleMeshBuffers()
    buffers.vertices = [unreal.Vector(v[0], v[1], v[2]) for v in data["vertices"]]
    buffers.triangles = [unreal.IntVector(t[0], t[1], t[2]) for t in data["triangles"]]
    buffers.uv0 = [unreal.Vector2D(v[0] / 100.0, v[1] / 100.0) for v in data["vertices"]]
    mesh.append_buffers_to_mesh(buffers)
    if mesh.get_num_uv_sets() < 1:
        mesh.set_num_uv_sets(1)
    box = unreal.Transform(unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0), unreal.Vector(100.0, 100.0, 100.0))
    mesh.set_mesh_u_vs_from_box_projection(0, box, unreal.GeometryScriptMeshSelection(), 2)
    split = unreal.GeometryScriptSplitNormalsOptions()
    split.split_by_opening_angle = True
    split.opening_angle_deg = 35.0
    split.split_by_face_group = False
    mesh.compute_split_normals(split, unreal.GeometryScriptCalculateNormalsOptions())
    _, without_uv, channel_ok = mesh.get_all_unset_uv_triangle_i_ds(0)
    in_file = len(data["triangles"])
    in_mesh = mesh.get_triangle_count()
    record = {"name": data["name"], "triangles_in_file": in_file, "triangles_in_mesh": in_mesh, "rejected": in_file - in_mesh,
              "uv_channels": mesh.get_num_uv_sets(), "triangles_without_uv": unreal.GeometryScript_List.get_index_list_length(without_uv) if channel_ok else in_mesh,
              "open_edges": mesh.get_num_open_border_edges()}
    return mesh, record


def _mesh_is_whole(record):
    return record["uv_channels"] >= 1 and record["triangles_without_uv"] == 0 and record["triangles_in_mesh"] > 0


def _asset_matches(static_mesh, data):
    """True when an asset that already exists holds the file's mesh: its triangle count, and a UV channel."""
    description = static_mesh.get_static_mesh_description(0)
    if description is None:
        return False
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    return description.get_triangle_count() == len(data["triangles"]) and meshes.get_num_uv_channels(static_mesh, 0) >= 1


def _ensure_nanite(static_mesh):
    """Switch Nanite on for a mesh asset that lacks it. Returns whether it is on afterwards."""
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    settings = meshes.get_nanite_settings(static_mesh)
    if not settings.enabled:
        settings.enabled = True
        meshes.set_nanite_settings(static_mesh, settings, True)
    return bool(meshes.get_nanite_settings(static_mesh).enabled)


def _read(folder, file_name):
    with open(os.path.join(folder, file_name), encoding="utf-8") as handle:
        return json.load(handle)


async def check(folder, start=0, count=40):
    """Read-only: build each file's mesh in memory and count; makes no asset and no object."""
    names = sorted(n for n in os.listdir(folder) if n.endswith(".json"))
    records = []
    for file_name in names[start:start + count]:
        _, record = _make_mesh(_read(folder, file_name))
        records.append(record)
        await asyncio.sleep(0)
    return records


async def build(folder, start=0, count=40, record_path=None):
    """Build a batch of mesh files. Returns where the next batch starts, or None when all are done.

    With record_path, one line per file made is added to that file (JSON lines), with the triangles the
    append rejected. An asset that already exists is used only if it holds the file's mesh; one that does
    not is left alone and reported under "problems", never silently used.
    """
    _require_level()
    names = sorted(n for n in os.listdir(folder) if n.endswith(".json"))
    batch = names[start:start + count]
    existing = _existing()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    grey = unreal.EditorAssetLibrary.load_asset(GREY)
    made = skipped = failed = rejected = 0
    problems = []
    records = []
    started = time.time()
    for file_name in batch:
        data = _read(folder, file_name)
        name = data["name"]
        if name in existing:
            skipped += 1
            continue
        asset_path = MESH_ROOT + name
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            static_mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
            if static_mesh is None or not _asset_matches(static_mesh, data):
                failed += 1
                problems.append(name + ": an asset exists that does not hold this file's mesh; left alone")
                continue
        else:
            mesh, record = _make_mesh(data)
            records.append(record)
            rejected += record["rejected"]
            if not _mesh_is_whole(record):
                failed += 1
                problems.append(name + ": mesh in memory has no UV channel or no triangles; no asset made")
                continue
            options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
            # enable_nanite alone left the first asset without Nanite in 5.9.0; the setting that counts is nanite_settings
            options.enable_nanite = True
            nanite = unreal.MeshNaniteSettings()
            nanite.enabled = True
            options.nanite_settings = nanite
            options.enable_collision = True
            options.enable_recompute_normals = False
            static_mesh, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, asset_path, options)
        if static_mesh is None:
            failed += 1
            problems.append(name + ": no asset came back")
            continue
        if not _ensure_nanite(static_mesh):
            problems.append(name + ": Nanite could not be switched on; the object was placed without it")
        pivot = data["pivot"]
        actor = actors.spawn_actor_from_object(static_mesh, unreal.Vector(pivot[0], pivot[1], pivot[2]), unreal.Rotator(0.0, 0.0, 0.0))
        if actor is None:
            failed += 1
            problems.append(name + ": no object could be placed")
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
    if record_path and records:
        with open(record_path, "a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
    nxt = start + len(batch)
    return {"from": start, "to": nxt, "of": len(names), "made": made, "skipped": skipped, "failed": failed, "rejected_triangles": rejected,
            "problems": problems[:8], "seconds": round(time.time() - started, 1), "next": nxt if nxt < len(names) else None}


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
