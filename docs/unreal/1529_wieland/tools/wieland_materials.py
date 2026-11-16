"""Editor-side helpers for Phase 5 (materials) of the 1529 N. Wieland scene.

Runs inside the Unreal editor's Python interpreter. Usage from the agent
server's Python tool:

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_materials as wm

Nothing here edits an asset that Datasmith created. Candidates are new
material instances under /Game/Wieland1529/Materials/, and they reach the
scene only as component overrides that alternatives_on() sets and
alternatives_off() clears (see material_alternatives.csv).
"""

import csv
import json
import os

import unreal

MEL = unreal.MaterialEditingLibrary
DATASMITH_MATERIALS = "/Game/Wieland1529/Building/Datasmith"
MATERIALS = "/Game/Wieland1529/Materials"


SWATCH_LEVEL = MATERIALS + "/L_W1529_Swatch"
# One flat partition wall from the import, 2.48 m wide and 2.95 m tall. Its
# texture coordinates advance by 1 per foot (30.48 cm), read from the mesh.
SWATCH_WALL = ("/Game/Wieland1529/Building/Datasmith/25-006_1527_N_Wieland-3DView-3D_View_188/Geometries/"
               "Walls_Basic_Wall_C1010_Interior_Partition__3-1_2__Stud_W__2_GYP__89")
SWATCH_TAG = "W1529Swatch"


def _world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def _actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def _spawn(cls, location, rotation=None, label=None, role=None):
    actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        cls, unreal.Vector(*location), rotation or unreal.Rotator(0, 0, 0))
    if label:
        actor.set_actor_label(label)
    actor.tags = [SWATCH_TAG] + ([role] if role else [])
    return actor


def _mesh_actor(mesh_path, centre, yaw, label, role, scale=(1.0, 1.0, 1.0)):
    """Place a mesh so that the centre of its bounds lands on `centre`."""
    actor = _spawn(unreal.StaticMeshActor, (0, 0, 0), unreal.Rotator(0, 0, yaw), label, role)
    component = actor.static_mesh_component
    component.set_static_mesh(unreal.load_asset(mesh_path))
    actor.set_actor_scale3d(unreal.Vector(*scale))
    origin, _extent = actor.get_actor_bounds(False)
    actor.set_actor_location(unreal.Vector(*centre) - origin, False, False)
    return actor


def build_swatch_level():
    """Make and save the swatch level; returns what it placed.

    Two copies of one wall from the import and a sphere stand in front of a
    grid backdrop. The left wall is lit from the front (45 degrees off the
    wall's face); the right wall is lit only by a light that runs 8 degrees
    off its face, which shows relief. The camera, the lights and the exposure
    are fixed, so every swatch picture is taken the same way.
    """
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(SWATCH_LEVEL):
        levels.load_level(SWATCH_LEVEL)
        return {"loaded": SWATCH_LEVEL, "actors": len(_actors())}
    if not levels.new_level(SWATCH_LEVEL):
        raise RuntimeError("could not create " + SWATCH_LEVEL)
    grid = unreal.load_asset("/Engine/EngineMaterials/WorldGridMaterial")
    floor = _mesh_actor("/Engine/BasicShapes/Plane", (300, 0, 0), 0, "Swatch_Floor", "backdrop", (30, 30, 1))
    back = _mesh_actor("/Engine/BasicShapes/Cube", (160, 0, 250), 0, "Swatch_Backdrop", "backdrop", (0.1, 12, 5))
    for actor in (floor, back):
        actor.static_mesh_component.set_material(0, grid)
    wall_front = _mesh_actor(SWATCH_WALL, (0, -165, 150), 90, "Swatch_Wall_FrontLight", "target")
    wall_graze = _mesh_actor(SWATCH_WALL, (0, 165, 150), 90, "Swatch_Wall_GrazingLight", "target")
    sphere = _mesh_actor("/Engine/BasicShapes/Sphere", (-200, 0, 62), 0, "Swatch_Sphere", "target", (0.8, 0.8, 0.8))
    graze_only = unreal.LightingChannels(channel0=False, channel1=True, channel2=False)
    wall_graze.static_mesh_component.set_editor_property("lighting_channels", graze_only)

    front = _spawn(unreal.DirectionalLight, (-300, -300, 500), unreal.Rotator(0, -35, 30), "Swatch_Light_Front", "light")
    front.light_component.set_intensity(6.0)
    front.light_component.set_editor_property("lighting_channels",
                                              unreal.LightingChannels(channel0=True, channel1=False, channel2=False))
    direction = unreal.Vector(0.139, -0.93, -0.34)
    graze = _spawn(unreal.DirectionalLight, (-300, 300, 500), unreal.MathLibrary.make_rot_from_x(direction),
                   "Swatch_Light_Grazing", "light")
    graze.light_component.set_intensity(40.0)
    graze.light_component.set_editor_property("lighting_channels", graze_only)
    # No sky: both lights stay white, and the surroundings that shiny
    # materials mirror are the engine's own studio panorama.
    for light in (front, graze):
        light.light_component.set_editor_property("atmosphere_sun_light", False)
    sky = _spawn(unreal.SkyLight, (0, 0, 300), None, "Swatch_SkyLight", "light")
    sky.light_component.set_editor_property("source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    sky.light_component.set_editor_property(
        "cubemap", unreal.load_asset("/Engine/EditorMaterials/AssetViewer/EpicQuadPanorama_CC+EV1"))
    sky.light_component.set_intensity(1.0)

    volume = _spawn(unreal.PostProcessVolume, (0, 0, 0), None, "Swatch_Exposure", "light")
    volume.set_editor_property("unbound", True)
    settings = volume.get_editor_property("settings")
    for name, value in (("override_auto_exposure_method", True),
                        ("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
                        ("override_auto_exposure_bias", True), ("auto_exposure_bias", 0.0),
                        ("override_auto_exposure_apply_physical_camera_exposure", True),
                        ("auto_exposure_apply_physical_camera_exposure", False),
                        ("override_vignette_intensity", True), ("vignette_intensity", 0.0),
                        ("override_bloom_intensity", True), ("bloom_intensity", 0.0)):
        settings.set_editor_property(name, value)
    volume.set_editor_property("settings", settings)

    camera = _spawn(unreal.CameraActor, (-640, 0, 140), unreal.Rotator(0, 0, 0), "Swatch_Camera", "camera")
    component = camera.camera_component
    component.set_editor_property("field_of_view", 55.0)
    component.set_editor_property("aspect_ratio", 2.0)
    component.set_editor_property("constrain_aspect_ratio", True)
    saved = levels.save_current_level()
    return {"created": SWATCH_LEVEL, "saved": saved, "actors": len(_actors())}


def _swatch(role):
    return [a for a in _actors() if SWATCH_TAG in [str(t) for t in a.tags] and role in [str(t) for t in a.tags]]


def swatch_apply(material):
    """Put a material on the sphere and both walls (override on the swatch actors only)."""
    for actor in _swatch("target"):
        component = actor.static_mesh_component
        for slot in range(component.get_num_materials()):
            component.set_material(slot, material)


def swatch_exposure(bias):
    volume = [a for a in _swatch("light") if isinstance(a, unreal.PostProcessVolume)][0]
    settings = volume.get_editor_property("settings")
    settings.set_editor_property("auto_exposure_bias", bias)
    volume.set_editor_property("settings", settings)


_JOB = {"state": "idle"}


def _tick(delta):
    job = _JOB
    try:
        if job["state"] != "running":
            return
        job["clock"] += delta
        if job["stage"] == "next":
            if job["index"] >= len(job["items"]):
                job["state"] = "done"
                unreal.unregister_slate_post_tick_callback(job["handle"])
                return
            name, path, out = job["items"][job["index"]]
            if os.path.exists(out) and not job["overwrite"]:
                job["skipped"] += 1
                job["index"] += 1
                return
            material = unreal.load_asset(path)
            if material is None:
                job["errors"].append([name, "asset not found"])
                job["index"] += 1
                return
            swatch_apply(material)
            job["stage"], job["clock"] = "settle", 0.0
        elif job["stage"] == "settle" and job["clock"] >= job["settle"]:
            name, path, out = job["items"][job["index"]]
            unreal.AutomationLibrary.take_high_res_screenshot(
                job["size"][0], job["size"][1], out, job["camera"])
            job["stage"], job["clock"] = "write", 0.0
        elif job["stage"] == "write":
            name, path, out = job["items"][job["index"]]
            if os.path.exists(out) and os.path.getsize(out) > 0:
                job["done"] += 1
                job["index"] += 1
                job["stage"] = "next"
            elif job["clock"] > 20.0:
                job["errors"].append([name, "no picture after 20 s"])
                job["index"] += 1
                job["stage"] = "next"
    except Exception as error:
        job["state"] = "failed"
        job["error"] = repr(error)
        unreal.unregister_slate_post_tick_callback(job["handle"])


def swatch_start(items, size=(1600, 800), settle=1.2, overwrite=False):
    """Take one swatch picture per item [name, asset path, output file]; returns at once.

    The work is done a step per editor frame, so no call has to wait for it.
    Read swatch_status() to follow it.
    """
    if _JOB.get("state") == "running":
        raise RuntimeError("a swatch job is already running")
    cameras = _swatch("camera")
    if not cameras:
        raise RuntimeError("the swatch level is not open")
    for _name, _path, out in items:
        os.makedirs(os.path.dirname(out), exist_ok=True)
    _JOB.clear()
    _JOB.update({"state": "running", "stage": "next", "items": list(items), "index": 0, "clock": 0.0,
                 "size": size, "settle": settle, "overwrite": overwrite, "camera": cameras[0],
                 "done": 0, "skipped": 0, "errors": []})
    _JOB["handle"] = unreal.register_slate_post_tick_callback(_tick)
    return swatch_status()


def swatch_status():
    return {key: _JOB.get(key) for key in ("state", "stage", "index", "done", "skipped", "errors", "error")
            if key in _JOB} | {"of": len(_JOB.get("items", []))}


def swatch_cancel():
    if _JOB.get("state") == "running":
        _JOB["state"] = "cancelled"
        unreal.unregister_slate_post_tick_callback(_JOB["handle"])
    return swatch_status()


def _texture_info(texture):
    if texture is None:
        return None
    info = {"path": texture.get_path_name(), "class": texture.get_class().get_name()}
    try:
        info["x"] = texture.blueprint_get_size_x()
        info["y"] = texture.blueprint_get_size_y()
    except Exception:
        pass
    for prop in ("srgb", "compression_settings", "virtual_texture_streaming", "lod_group"):
        try:
            info[prop] = str(texture.get_editor_property(prop))
        except Exception:
            pass
    try:
        data = texture.get_editor_property("asset_import_data")
        info["source_file"] = data.get_first_filename() if data else None
    except Exception:
        info["source_file"] = None
    return info


def material_params(material):
    """All parameters of a material instance, with the values in force."""
    out = {"path": material.get_path_name(), "class": material.get_class().get_name()}
    parent = material.get_editor_property("parent") if isinstance(material, unreal.MaterialInstance) else None
    out["parent"] = parent.get_path_name() if parent else None
    base = material.get_base_material()
    out["base"] = base.get_path_name() if base else None
    try:
        out["blend_mode"] = str(material.get_blend_mode())
    except Exception:
        out["blend_mode"] = None
    scalars, vectors, textures, switches = {}, {}, {}, {}
    if isinstance(material, unreal.MaterialInstanceConstant):
        for name in MEL.get_scalar_parameter_names(material):
            scalars[str(name)] = MEL.get_material_instance_scalar_parameter_value(material, name)
        for name in MEL.get_vector_parameter_names(material):
            value = MEL.get_material_instance_vector_parameter_value(material, name)
            vectors[str(name)] = [round(value.r, 5), round(value.g, 5), round(value.b, 5), round(value.a, 5)]
        for name in MEL.get_texture_parameter_names(material):
            textures[str(name)] = _texture_info(MEL.get_material_instance_texture_parameter_value(material, name))
        for name in MEL.get_static_switch_parameter_names(material):
            switches[str(name)] = MEL.get_material_instance_static_switch_parameter_value(material, name)
        out["overridden_scalars"] = [str(p.parameter_info.name) for p in material.get_editor_property("scalar_parameter_values")]
        out["overridden_vectors"] = [str(p.parameter_info.name) for p in material.get_editor_property("vector_parameter_values")]
        out["overridden_textures"] = [str(p.parameter_info.name) for p in material.get_editor_property("texture_parameter_values")]
    out["scalars"], out["vectors"], out["textures"], out["switches"] = scalars, vectors, textures, switches
    return out


def dump_params(audit_csv, out_json):
    """Step 5.0: read every audited material's parameters into a JSON file."""
    rows = list(csv.DictReader(open(audit_csv, encoding="utf-8")))
    result, missing = {}, []
    for row in rows:
        path = row["asset_path"]
        material = unreal.load_asset(path) if path.startswith("/") else None
        if material is None:
            missing.append(row["material"])
            continue
        result[row["material"]] = material_params(material)
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"materials": result, "missing": missing}, handle, indent=1)
    parents = {}
    for item in result.values():
        parents[item["parent"]] = parents.get(item["parent"], 0) + 1
    return {"read": len(result), "missing": missing, "parents": parents}
