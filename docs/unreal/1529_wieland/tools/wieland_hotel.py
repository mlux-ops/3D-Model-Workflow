"""Phase 13, inside the Unreal editor: the proposed hotel at 1520-1528 N. Wells ("The Duke of Wells").

Everything this module makes is PROPOSED, modelled from published renderings and records, not a survey.

It makes new assets only (under /Game/Wieland1529/Site/ProposedHotel), a new level
(/Game/Wieland1529/Site/L_ProposedHotel) inside the top level L_Site_M4, and one list in the project's
Variant Manager asset. It never edits an asset that Datasmith created, never saves the earlier level, and
saves by name only.

The meshes come from tools/phase13_hotel_meshes.py (JSON files), the images from
review/phase13/scripts/make_textures.py.
"""
import asyncio
import csv
import json
import os

import unreal

ROOT = "/Game/Wieland1529/Site/ProposedHotel"
LEVEL = "/Game/Wieland1529/Site/L_ProposedHotel"
TOP_LEVEL = "/Game/Wieland1529/L_Site_M4"
OLD_LEVEL = "/Game/Wieland/R15_Landscape/L_R15_Production"
TAG = "W1529.ProposedHotel"
PARENTS = "/Game/Wieland1529/Materials/Parents"
TEXTURES = "/Game/Wieland1529/Materials/Textures"
PLAN = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
MESH_FILES = PLAN + "/review/phase13/scratch/meshes"
HIDE_RECORD = PLAN + "/review/phase13/hidden_for_proposed_hotel.csv"
CM = 30.48006096

VARIANT_ASSET = "/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings"
VARIANT_LIST = "Neighbour development"
OPTION_PROPOSED = "Duke of Wells (proposed)"
OPTION_EXISTING = "Existing buildings (as surveyed)"
# Existing buildings that stand on the development's land (proposed_hotel.md, section 1.3): label, level, what it is
HIDE = [
    ("SB_782868", "/Game/Wieland1529/Surroundings/L_Surroundings", "plain block of the existing 3-storey building 1520 N. Wells"),
    ("R15_PART_opaque_xm04_yp01_part01", "/Game/Wieland1529/Surroundings/L_Surroundings_R15", "the existing house 1525 N. Wieland, walls and roof"),
    ("R15_PART_glass_xm04_yp01_part01", "/Game/Wieland1529/Surroundings/L_Surroundings_R15", "the existing house 1525 N. Wieland, glass"),
]

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary

# Materials the meshes use. "existing": one of the project's own instances, used as it is.
# "new": an instance made here from one of the project's own parent materials.
MATERIALS = {
    "RedBrick": {"new": "MI_W1529_PH_RedBrick", "parent": "M_W1529_Opaque",
                 "textures": {"BaseColorMap": ROOT + "/Textures/T_W1529_PH_RedBrick_C", "NormalMap": ROOT + "/Textures/T_W1529_PH_Brick_N",
                              "RoughnessMap": ROOT + "/Textures/T_W1529_PH_Brick_R"},
                 "scalars": {"SizeU_m": 6.5024, "SizeV_m": 4.3349, "WorldYawDeg": 0.0, "RoughnessScale": 1.0, "MacroVariation": 0.07,
                             "VariationSize_m": 9.0, "NormalStrength": 1.0}},
    "DarkBrick": {"new": "MI_W1529_PH_DarkBrick", "parent": "M_W1529_Opaque",
                  "textures": {"BaseColorMap": ROOT + "/Textures/T_W1529_PH_DarkBrick_C", "NormalMap": ROOT + "/Textures/T_W1529_PH_Brick_N",
                               "RoughnessMap": ROOT + "/Textures/T_W1529_PH_Brick_R"},
                  "scalars": {"SizeU_m": 6.5024, "SizeV_m": 4.3349, "WorldYawDeg": 0.0, "RoughnessScale": 0.95, "MacroVariation": 0.06,
                              "VariationSize_m": 9.0, "NormalStrength": 1.0}},
    "GreenRoof": {"new": "MI_W1529_PH_GreenRoof", "parent": "M_W1529_Opaque",
                  "textures": {"BaseColorMap": ROOT + "/Textures/T_W1529_PH_GreenRoof_C", "NormalMap": ROOT + "/Textures/T_W1529_PH_GreenRoof_N"},
                  "scalars": {"SizeU_m": 4.0, "SizeV_m": 4.0, "WorldYawDeg": 0.0, "RoughnessScale": 0.9, "MacroVariation": 0.10,
                              "VariationSize_m": 7.0},
                  "switches": {"AntiRepeat": True}},
    "MetalPanel": {"new": "MI_W1529_PH_MetalPanel", "parent": "M_W1529_Opaque",
                   "textures": {"BaseColorMap": ROOT + "/Textures/T_W1529_PH_MetalPanel_C", "NormalMap": ROOT + "/Textures/T_W1529_PH_MetalPanel_N"},
                   "scalars": {"SizeU_m": 1.2, "SizeV_m": 1.2, "WorldYawDeg": 0.0, "RoughnessScale": 0.45, "MacroVariation": 0.03,
                               "VariationSize_m": 5.0, "Metallic": 0.6}},
    "Interior": {"new": "MI_W1529_PH_Interior", "parent": "M_W1529_Opaque",
                 "textures": {"BaseColorMap": TEXTURES + "/T_W1529_P12_Flat_2D2E30_C"},
                 "scalars": {"RoughnessScale": 0.9, "MacroVariation": 0.15, "VariationSize_m": 3.0, "WorldYawDeg": 0.0}},
    "Blind": {"new": "MI_W1529_PH_Blind", "parent": "M_W1529_Opaque",
              "textures": {"BaseColorMap": TEXTURES + "/T_W1529_P12_Flat_E8E5DE_C"},
              "scalars": {"RoughnessScale": 0.8, "MacroVariation": 0.05, "VariationSize_m": 2.0, "WorldYawDeg": 0.0},
              "vectors": {"Tint": (0.78, 0.76, 0.72, 1.0)}},
    "Glass": {"new": "MI_W1529_PH_Glass", "parent": "M_W1529_Glass",
              "scalars": {"Opacity": 0.22, "OpacityGrazing": 0.7},
              "vectors": {"Tint": (0.80, 0.88, 0.86, 1.0)}},
    "Stone": {"existing": "/Game/Wieland1529/Materials/Rebuilt/MI_W1529_R_Indiana_Limestone_-_Full_Color_Blend_Seamless"},
    "Concrete": {"existing": "/Game/Wieland1529/Materials/Candidates/MI_W1529_C_Concrete__Precast"},
    "Metal": {"existing": "/Game/Wieland1529/Materials/Rebuilt/MI_W1529_R_Aluminum_-_Matte_Black_Powdercoat"},
}
TEXTURE_FILES = [
    # file name, kind
    ("T_W1529_PH_RedBrick_C", "colour"), ("T_W1529_PH_DarkBrick_C", "colour"), ("T_W1529_PH_Brick_N", "normal"),
    ("T_W1529_PH_Brick_R", "mask"), ("T_W1529_PH_GreenRoof_C", "colour"), ("T_W1529_PH_GreenRoof_N", "normal"),
    ("T_W1529_PH_MetalPanel_C", "colour"), ("T_W1529_PH_MetalPanel_N", "normal"),
]


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def world_path():
    return world().get_path_name().split(".")[0]


def actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def level_of(actor):
    return actor.get_outer().get_outer().get_path_name().split(".")[0]


def levels():
    return [level.get_outer().get_path_name().split(".")[0] for level in unreal.EditorLevelUtils.get_levels(world())]


def dirty():
    utils = unreal.EditorLoadingAndSavingUtils
    return sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))


def _require_top():
    if world_path() != TOP_LEVEL:
        raise RuntimeError("refused: the open level is %s, not %s" % (world_path(), TOP_LEVEL))


def material_path(key):
    recipe = MATERIALS[key]
    return recipe["existing"] if "existing" in recipe else ROOT + "/Materials/" + recipe["new"]


# ---- images and materials -----------------------------------------------------------------------------
def import_textures(folder):
    """Import the images made by make_textures.py and save each by name. Existing assets are left alone."""
    tasks, wanted = [], []
    for name, kind in TEXTURE_FILES:
        if EAL.does_asset_exist(ROOT + "/Textures/" + name):
            continue
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", folder + "/" + name + ".png")
        task.set_editor_property("destination_path", ROOT + "/Textures")
        task.set_editor_property("destination_name", name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("save", False)
        tasks.append(task)
        wanted.append((ROOT + "/Textures/" + name, kind))
    if tasks:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    result = {"imported": [], "failed": [], "already_there": len(TEXTURE_FILES) - len(tasks)}
    for path, kind in wanted:
        texture = unreal.load_asset(path)
        if texture is None:
            result["failed"].append(path)
            continue
        if kind == "normal":
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        elif kind == "mask":
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        else:
            texture.set_editor_property("srgb", True)
        EAL.save_asset(path, False)
        result["imported"].append([path.split("/")[-1], texture.blueprint_get_size_x(), texture.blueprint_get_size_y()])
    return result


def make_materials(remake=False):
    """Make the new material instances from the project's own parents and save each by name."""
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    made, problems = [], []
    for key, recipe in MATERIALS.items():
        if "existing" in recipe:
            if not EAL.does_asset_exist(recipe["existing"]):
                problems.append("%s: the project's instance is missing: %s" % (key, recipe["existing"]))
            continue
        path = ROOT + "/Materials/" + recipe["new"]
        if EAL.does_asset_exist(path):
            if not remake:
                continue
            instance = unreal.load_asset(path)
            MEL.clear_all_material_instance_parameters(instance)
        else:
            instance = tools.create_asset(recipe["new"], ROOT + "/Materials", unreal.MaterialInstanceConstant,
                                          unreal.MaterialInstanceConstantFactoryNew())
        parent = unreal.load_asset(PARENTS + "/" + recipe["parent"])
        if parent is None:
            problems.append("%s: no parent %s" % (key, recipe["parent"]))
            continue
        MEL.set_material_instance_parent(instance, parent)
        for name, value in recipe.get("switches", {}).items():
            MEL.set_material_instance_static_switch_parameter_value(instance, name, bool(value))
        for name, value in recipe.get("scalars", {}).items():
            if not MEL.set_material_instance_scalar_parameter_value(instance, name, float(value)):
                problems.append("%s: no number called %s" % (key, name))
        for name, value in recipe.get("vectors", {}).items():
            if not MEL.set_material_instance_vector_parameter_value(instance, name, unreal.LinearColor(*value)):
                problems.append("%s: no colour called %s" % (key, name))
        for name, value in recipe.get("textures", {}).items():
            texture = unreal.load_asset(value)
            if texture is None:
                problems.append("%s: image missing: %s" % (key, value))
                continue
            if not MEL.set_material_instance_texture_parameter_value(instance, name, texture):
                problems.append("%s: no image called %s" % (key, name))
        MEL.update_material_instance(instance)
        if not EAL.save_asset(path, False):
            problems.append("%s: not saved" % key)
        made.append(recipe["new"])
    return {"made": made, "problems": problems}


# ---- the level ------------------------------------------------------------------------------------------
def ensure_level():
    """With L_Site_M4 open: make the hotel's level inside it (always loaded), or add it when it exists already."""
    _require_top()
    if LEVEL in levels():
        return {"made": False, "added": False, "levels": len(levels())}
    if EAL.does_asset_exist(LEVEL):
        streaming = unreal.EditorLevelUtils.add_level_to_world(world(), LEVEL, unreal.LevelStreamingAlwaysLoaded)
        return {"made": False, "added": streaming is not None, "levels": len(levels())}
    streaming = unreal.EditorLevelUtils.create_new_streaming_level(unreal.LevelStreamingAlwaysLoaded, LEVEL, False)
    return {"made": streaming is not None, "added": streaming is not None, "levels": len(levels())}


def _streaming(path):
    for streaming in world().get_editor_property("streaming_levels") if hasattr(world(), "get_editor_property") else []:
        if str(streaming.get_world_asset_package_name()).endswith(path.split("/")[-1]):
            return streaming
    return None


def _set_current(path):
    """Make one loaded level the one new objects go into. Returns the level's path as the editor reports it."""
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor.set_current_level_by_name(path.split("/")[-1])
    current = editor.get_current_level()
    return current.get_outer().get_path_name().split(".")[0] if current else None


def hotel_actors():
    return [a for a in actors() if any(str(t) == TAG for t in a.tags)]


# ---- meshes -----------------------------------------------------------------------------------------------
def _dynamic_mesh(data):
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
    return mesh


def _nanite(static_mesh, wanted):
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    settings = meshes.get_nanite_settings(static_mesh)
    if bool(settings.enabled) != bool(wanted):
        settings.enabled = bool(wanted)
        meshes.set_nanite_settings(static_mesh, settings, True)
    return bool(meshes.get_nanite_settings(static_mesh).enabled)


async def build(groups, remake=False):
    """Make the mesh assets of the named groups, save each by name, and place one object per mesh in the
    hotel's level. With remake, the geometry of assets that exist is replaced from the files."""
    _require_top()
    if LEVEL not in levels():
        raise RuntimeError("the hotel's level is not loaded; run ensure_level() first")
    current = _set_current(LEVEL)
    if current != LEVEL:
        raise RuntimeError("could not make the hotel's level current (current is %s)" % current)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    existing = {a.get_actor_label(): a for a in hotel_actors()}
    made, placed, problems, records = 0, 0, [], []
    try:
        for file_name in sorted(os.listdir(MESH_FILES)):
            if not file_name.startswith("SM_W1529_PH_"):
                continue
            with open(os.path.join(MESH_FILES, file_name), encoding="utf-8") as handle:
                data = json.load(handle)
            if data["group"] not in groups:
                continue
            name, key = data["name"], data["material"]
            glass = key == "Glass"
            asset_path = ROOT + "/Meshes/" + name
            static_mesh = unreal.load_asset(asset_path) if EAL.does_asset_exist(asset_path) else None
            if static_mesh is None:
                mesh = _dynamic_mesh(data)
                options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
                options.enable_nanite = not glass
                nanite = unreal.MeshNaniteSettings()
                nanite.enabled = not glass
                options.nanite_settings = nanite
                options.enable_collision = True
                options.enable_recompute_normals = False
                static_mesh, _ = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, asset_path, options)
                made += 1
            elif remake:
                mesh = _dynamic_mesh(data)
                options = unreal.GeometryScriptCopyMeshToAssetOptions()
                options.enable_recompute_normals = False
                options.emit_transaction = False
                unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh, static_mesh, options, unreal.GeometryScriptMeshWriteLOD())
                made += 1
            if static_mesh is None:
                problems.append(name + ": no asset came back")
                continue
            nanite_on = _nanite(static_mesh, not glass)
            material = unreal.load_asset(material_path(key))
            if material is None:
                problems.append(name + ": material missing: " + material_path(key))
            else:
                static_mesh.set_material(0, material)
            if not EAL.save_loaded_asset(static_mesh, False):
                problems.append(name + ": asset not saved")
            actor = existing.get(name)
            if actor is None:
                actor = subsystem.spawn_actor_from_object(static_mesh, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
                if actor is None:
                    problems.append(name + ": no object could be placed")
                    continue
                actor.set_actor_label(name)
                actor.set_folder_path(unreal.Name("ProposedHotel/" + data["group"]))
                actor.tags = [unreal.Name(TAG), unreal.Name(TAG + "." + data["group"])]
                component = actor.static_mesh_component
                component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
                placed += 1
            if level_of(actor) != LEVEL:
                problems.append("%s: stands in %s, not in the hotel's level" % (name, level_of(actor)))
            description = static_mesh.get_static_mesh_description(0)
            records.append([name, len(data["triangles"]), description.get_triangle_count() if description else -1, nanite_on])
            await asyncio.sleep(0)
    finally:
        _set_current(TOP_LEVEL)
    short = [r for r in records if r[1] != r[2]]
    return {"meshes_made": made, "objects_placed": placed, "objects_now": len(hotel_actors()), "problems": problems,
            "triangle_counts_differ": short, "records": len(records)}


def save(top=False):
    """Save the hotel's level by name, and with top=True the top level L_Site_M4 by name. Never anything else."""
    out = {}
    for path in dirty():
        if path.startswith(ROOT + "/"):
            out[path.split("/")[-1]] = bool(EAL.save_asset(path, False))
    for path in [LEVEL] + ([TOP_LEVEL] if top else []):
        if path == OLD_LEVEL or path not in levels():
            out[path] = "refused"
            continue
        package = unreal.find_package(path)
        out[path] = bool(unreal.EditorLoadingAndSavingUtils.save_packages([package], False)) if package else "no package"
    out["left_marked"] = dirty()
    return out


def measure():
    """Read-only: the extents of the placed objects per group, in site feet, read back from the editor."""
    groups = {}
    for actor in hotel_actors():
        group = [str(t).split(".")[-1] for t in actor.tags if str(t).startswith(TAG + ".")][0]
        origin, extent = actor.get_actor_bounds(False)
        record = groups.setdefault(group, {"objects": 0, "north": [1e9, -1e9], "east": [1e9, -1e9], "up": [1e9, -1e9]})
        record["objects"] += 1
        for key, low, high in (("north", -(origin.x + extent.x) / CM, -(origin.x - extent.x) / CM),
                               ("east", -(origin.y + extent.y) / CM, -(origin.y - extent.y) / CM),
                               ("up", (origin.z - extent.z) / CM, (origin.z + extent.z) / CM)):
            record[key] = [round(min(record[key][0], low), 2), round(max(record[key][1], high), 2)]
    return groups


# ---- looking ----------------------------------------------------------------------------------------------
def look(east, north, up, yaw, pitch):
    """Put the editor's view at a point given in site feet. Yaw 0 looks toward the level's +X (south)."""
    location = unreal.Vector(-north * CM, -east * CM, up * CM)
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(location, unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    return True


async def picture(path, east, north, up, yaw, pitch, width=1920, height=1080, settle=3.0):
    """One picture of the editor's view from a point in site feet. Nothing is placed in the level."""
    look(east, north, up, yaw, pitch)
    await asyncio.sleep(settle)
    if os.path.exists(path):
        os.remove(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    unreal.AutomationLibrary.take_high_res_screenshot(width, height, path)
    waited = 0.0
    while not os.path.exists(path) and waited < 60.0:
        await asyncio.sleep(0.25)
        waited += 0.25
    return os.path.exists(path)


# ---- the Variant Manager list -----------------------------------------------------------------------------
def _existing_objects():
    found = {}
    for actor in actors():
        label = actor.get_actor_label()
        for wanted, level, _ in HIDE:
            if label == wanted and level_of(actor) == level:
                found[label] = actor
    return [found[label] for label, _, _ in HIDE if label in found]


def _visible(actor):
    return bool(actor.get_component_by_class(unreal.StaticMeshComponent).get_editor_property("visible"))


def state():
    """Read-only: which of the two groups is shown."""
    hotel = hotel_actors()
    existing = _existing_objects()
    return {"hotel_objects": len(hotel), "hotel_visible": sum(1 for a in hotel if _visible(a)),
            "existing_objects": len(existing), "existing_visible": sum(1 for a in existing if _visible(a))}


def _capture_visible(library, variant, actor):
    for name in library.get_capturable_properties(actor):
        if str(name).endswith("/ Visible") and "Billboard" not in str(name):
            return library.capture_property(variant, actor, str(name))
    return None


def build_variants():
    """Adds (or remakes) the list "Neighbour development" in the project's variant asset and saves the asset by name.

    "Duke of Wells (proposed)": the hotel's objects visible, the existing buildings on its land not visible.
    "Existing buildings (as surveyed)": the other way round. Only the property Visible of placed objects is
    recorded; no mesh, no asset and no Datasmith object is edited or deleted.
    """
    _require_top()
    library = unreal.VariantManagerLibrary
    sets_asset = unreal.load_asset(VARIANT_ASSET)
    if sets_asset is None:
        return {"error": "no variant asset"}
    for index in reversed(range(sets_asset.get_num_variant_sets())):
        old = sets_asset.get_variant_set(index)
        if str(old.get_display_text()) == VARIANT_LIST:
            library.remove_variant_set(sets_asset, old)
    variant_set = unreal.VariantSet()
    variant_set.set_display_text(VARIANT_LIST)
    library.add_variant_set(sets_asset, variant_set)
    hotel, existing = hotel_actors(), _existing_objects()
    result = {"hotel_objects": len(hotel), "existing_objects": len(existing), "values": 0, "missed": []}
    for option in (OPTION_PROPOSED, OPTION_EXISTING):
        variant = unreal.Variant()
        variant.set_display_text(option)
        library.add_variant(variant_set, variant)
        for group, shown in ((hotel, option == OPTION_PROPOSED), (existing, option == OPTION_EXISTING)):
            for actor in group:
                library.add_actor_binding(variant, actor)
                value = _capture_visible(library, variant, actor)
                if value is None:
                    result["missed"].append(actor.get_actor_label())
                    continue
                library.set_value_bool(value, shown)
                result["values"] += 1
    result["saved"] = bool(EAL.save_loaded_asset(sets_asset, False))
    result["lists"] = [str(sets_asset.get_variant_set(i).get_display_text()) for i in range(sets_asset.get_num_variant_sets())]
    return result


def switch(option):
    """One action: put one option of the list "Neighbour development" on."""
    sets_asset = unreal.load_asset(VARIANT_ASSET)
    for index in range(sets_asset.get_num_variant_sets()):
        variant_set = sets_asset.get_variant_set(index)
        if str(variant_set.get_display_text()) != VARIANT_LIST:
            continue
        for number in range(variant_set.get_num_variants()):
            variant = variant_set.get_variant(number)
            if str(variant.get_display_text()) == option:
                variant.switch_on()
                return {"option": option, "state": state()}
    return {"error": "no such list or option"}


def write_hide_record():
    """The recorded overrides: which existing objects the proposed option hides, and how to undo it."""
    rows = []
    found = {a.get_actor_label(): a for a in _existing_objects()}
    for label, level, what in HIDE:
        actor = found.get(label)
        component = actor.get_component_by_class(unreal.StaticMeshComponent) if actor else None
        rows.append({"object": label, "level": level, "what_it_is": what, "found": actor is not None,
                     "mesh": component.static_mesh.get_path_name().split(".")[0] if component else "",
                     "override": "mesh component property Visible = False on the placed object while the option '%s' is on; "
                                 "mesh asset and object untouched, nothing deleted" % OPTION_PROPOSED,
                     "how_to_undo": "Variant Manager, list '%s', option '%s'; or tick Visible on the component" % (VARIANT_LIST, OPTION_EXISTING)})
    with open(HIDE_RECORD, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows
