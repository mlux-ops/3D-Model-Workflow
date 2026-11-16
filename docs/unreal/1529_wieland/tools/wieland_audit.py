"""Phase 7, step 7.1-b: the audit fixes that need no photograph (A5, ML2, A10).

Runs inside the Unreal editor's Python, next to wieland_site (ws). Nothing of the earlier production
level is edited: the changes are made on the fitted mesh assets of Phase 7 (/Game/Wieland1529/Surroundings/R15Fit),
as material overrides on the placed copies in L_Surroundings_R15, and as new objects in a new level.
"""

import csv
import math
import os

import unreal

import wieland_site as ws

MATERIALS = "/Game/Wieland1529/Surroundings/Materials"
RECORD = ws.REVIEW + "/audit_fixes.csv"
TAG_PLACEHOLDER = "W1529.Placeholder"
R15_LEVEL = "/Game/Wieland1529/Surroundings/L_Surroundings_R15"

PART_1525 = "R15_PART_opaque_xm04_yp01_part01"
PART_1533 = "R15_PART_opaque_xm05_yp01_part01"

# A5. The 1525 house in the mesh's own coordinates (cm), measured from the siding slats:
# slats outside at x -15471.9 / -14850.8 and y -6734.3 / -5238.8, inside at x -15448.0 / -14868.6 and
# y -6725.9 / -5259.6; the gable line of the slats runs from z 664 at the wall to 872 at the ridge.
BACKING = {"x0": -15446.0, "x1": -14870.0, "y0": -6724.0, "y1": -5262.0, "z_base": -8.0, "z_eave": 656.0, "z_ridge": 864.0}
SLOT_SIDING = 1
SLOT_STEPS = 2
TRIANGLES_1525 = 11328   # the fitted mesh before the backing wall is added


def _copy(label):
    for actor in ws.r15_copies():
        if actor.get_actor_label() == label:
            return actor
    raise RuntimeError("copy missing: " + label)


def _record(rows):
    """Adds or replaces rows of audit_fixes.csv by their key (finding + item)."""
    fields = ["finding", "item", "object", "what_was_there", "what_is_there_now", "how", "evidence", "status"]
    known = {}
    if os.path.exists(RECORD):
        with open(RECORD, newline="", encoding="utf-8") as handle:
            known = {(r["finding"], r["item"]): r for r in csv.DictReader(handle)}
    for row in rows:
        known[(row["finding"], row["item"])] = row
    with open(RECORD, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for key in sorted(known):
            writer.writerow(known[key])
    return len(known)


def _bounds(dynamic):
    box = unreal.GeometryScript_MeshQueries.get_mesh_bounding_box(dynamic)
    return (box.min.x, box.min.y, box.min.z), (box.max.x, box.max.y, box.max.z)


def _backing_mesh():
    """A closed block in the shape of the house (walls and gable), a few cm inside the slats."""
    b = BACKING
    centre = 0.5 * (b["x0"] + b["x1"])
    length = b["y1"] - b["y0"]
    primitives = unreal.GeometryScript_Primitives
    for roll, sign in ((90.0, 1.0), (-90.0, -1.0), (90.0, -1.0), (-90.0, 1.0)):
        outline = [(b["x0"], b["z_base"]), (b["x1"], b["z_base"]), (b["x1"], b["z_eave"]), (centre, b["z_ridge"]), (b["x0"], b["z_eave"])]
        if sign < 0:
            outline = [(x, -z) for x, z in reversed(outline)]
        dynamic = unreal.DynamicMesh()
        transform = unreal.Transform(unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(roll=roll, pitch=0.0, yaw=0.0), unreal.Vector(1.0, 1.0, 1.0))
        primitives.append_simple_extrude_polygon(dynamic, unreal.GeometryScriptPrimitiveOptions(), transform,
                                                 [unreal.Vector2D(x, z) for x, z in outline], length, 0, True)
        low, high = _bounds(dynamic)
        if abs(low[2] - b["z_base"]) < 1.0 and abs(high[2] - b["z_ridge"]) < 1.0:
            shift = b["y0"] - low[1]
            moved = unreal.DynamicMesh()
            unreal.GeometryScript_MeshEdits.append_mesh(
                moved, dynamic, unreal.Transform(unreal.Vector(0.0, shift, 0.0), unreal.Rotator(0.0, 0.0, 0.0), unreal.Vector(1.0, 1.0, 1.0)))
            return moved, {"roll": roll, "sign": sign}
    raise RuntimeError("no orientation gave the expected block")


def backing_1525(flip=False, redo=False):
    """A5: adds the backing wall to the fitted mesh of the 1525 part (material slot of the siding). Saves the asset by name."""
    path = ws.FIT_FOLDER + "/SM_R15fit_" + PART_1525[len("R15_PART_"):]
    asset, dynamic = ws._dynamic(path)
    before = int(dynamic.get_triangle_count())
    if before != TRIANGLES_1525:
        if not redo:
            return {"skipped": "the mesh has %d triangles, not %d: the backing wall is already there" % (before, TRIANGLES_1525)}
        # The backing wall was added after the fitted triangles: take it off again before it is rebuilt.
        extra = unreal.GeometryScript_List.convert_array_to_index_list(list(range(TRIANGLES_1525, before)), unreal.GeometryScriptIndexType.TRIANGLE)
        unreal.GeometryScript_MeshEdits.delete_triangles_from_mesh(dynamic, extra, True)
        before = int(dynamic.get_triangle_count())
        if before != TRIANGLES_1525:
            raise RuntimeError("%d triangles after taking the backing wall off, %d expected" % (before, TRIANGLES_1525))
    block, how = _backing_mesh()
    if flip:
        unreal.GeometryScript_Normals.flip_normals(block)
    count = int(block.get_triangle_count())
    materials = unreal.GeometryScript_Materials
    materials.enable_material_i_ds(block)
    for triangle in range(count):
        materials.set_triangle_material_id(block, triangle, SLOT_SIDING)
    slots_before = [ws._path(s.material_interface) for s in asset.static_materials]
    unreal.GeometryScript_MeshEdits.append_mesh(dynamic, block, unreal.Transform())
    options = unreal.GeometryScriptCopyMeshToAssetOptions()
    options.enable_recompute_normals = False
    options.emit_transaction = False
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    nanite = bool(meshes.get_nanite_settings(asset).enabled)
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dynamic, asset, options, unreal.GeometryScriptMeshWriteLOD())
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        raise RuntimeError("the mesh asset could not be written")
    settings = meshes.get_nanite_settings(asset)
    if bool(settings.enabled) != nanite:
        settings.enabled = nanite
        meshes.set_nanite_settings(asset, settings, True)
    slots_after = [ws._path(s.material_interface) for s in asset.static_materials]
    low, high = _bounds(block)
    return {"triangles_before": before, "added": count, "triangles_after": int(dynamic.get_triangle_count()), "how": how, "flip": flip,
            "block_low": [round(v, 1) for v in low], "block_high": [round(v, 1) for v in high],
            "slots_same": slots_before == slots_after, "nanite": bool(meshes.get_nanite_settings(asset).enabled),
            "saved": bool(unreal.EditorAssetLibrary.save_loaded_asset(asset, False))}


def _instance_copy(source_path, name):
    """A named copy of a material instance under the surroundings materials folder (made once)."""
    library = unreal.EditorAssetLibrary
    target = MATERIALS + "/" + name
    if not library.does_asset_exist(target):
        if library.duplicate_asset(source_path, target) is None:
            raise RuntimeError("could not make " + target)
        library.save_asset(target, False)
    return unreal.load_asset(target)


def swap(label, slot, instance):
    """A recorded swap: the material shown in one slot of a placed copy (an override; the mesh asset keeps its own)."""
    actor = _copy(label)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    before = ws._path(component.get_material(slot))
    component.modify()
    component.set_material(slot, instance)
    return {"object": label, "slot": slot, "before": before, "now": ws._path(component.get_material(slot))}


def steps_1525():
    """A5: the steps and porch slab of 1525 lose the stretched concrete image and get world-mapped concrete."""
    instance = _instance_copy("/Game/Wieland1529/Site/Materials/MI_W1529_SiteKerb", "MI_W1529_R15_StepConcrete")
    return swap(PART_1525, SLOT_STEPS, instance)


VIEWS = {
    # name: (place x, y, z in cm; pitch, yaw; what it shows)
    "A5_front": ((321.0, 1000.0, 170.0), (14.0, -90.0), "the 1525 house from the far side of Wieland, eye height"),
    "A5_gable": ((321.0, 500.0, 500.0), (22.0, -90.0), "the gable of 1525 from 7 m, 5 m up"),
    "A5_steps": ((321.0, 240.0, 160.0), (-22.0, -90.0), "the steps of 1525 from the sidewalk"),
    "A5_side": ((1500.0, 600.0, 170.0), (12.0, -146.0), "1525 from the south-west: front and south side wall"),
}


def cameras(views=None):
    """Temporary cameras; ws.shots_end() removes them with the station cameras."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(ws.world_path().split("/")[-1])
    made = 0
    for name, (place, turn, _what) in (views or VIEWS).items():
        camera = subsystem.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*place),
                                                  unreal.Rotator(pitch=turn[0], yaw=turn[1], roll=0.0))
        camera.set_actor_label("TEMP_" + name)
        camera.tags = [ws.SHOT_TAG, name]
        component = camera.camera_component
        component.set_editor_property("field_of_view", 73.74)
        component.set_editor_property("constrain_aspect_ratio", True)
        component.set_editor_property("aspect_ratio", 16.0 / 9.0)
        made += 1
    return made


# ML2. The brick of 1533 (slots 0 and 1 of its part) was one worn-brick image set, mapped by the mesh's own
# coordinates at 2.5 m a repeat and stretched to twice the height; on the blank side wall it showed as bands.
SLOTS_1533_BRICK = (0, 1)


def brick_1533():
    """ML2: a varied brick (Phase 5 parent, mapped in world metres, second reading mixed in, slow change of brightness)."""
    mel = unreal.MaterialEditingLibrary
    instance = _instance_copy("/Game/Wieland1529/Materials/Candidates/MI_W1529_C_Brick__Common", "MI_W1529_R15_1533Brick")
    mel.set_material_instance_static_switch_parameter_value(instance, "AntiRepeat", True)
    mel.set_material_instance_scalar_parameter_value(instance, "MacroVariation", 0.07)
    mel.set_material_instance_scalar_parameter_value(instance, "VariationSize_m", 6.0)
    # A little darker and browner, towards the brick the earlier level showed on this building.
    mel.set_material_instance_vector_parameter_value(instance, "Tint", unreal.LinearColor(0.80, 0.74, 0.74, 1.0))
    mel.update_material_instance(instance)
    saved = bool(unreal.EditorAssetLibrary.save_loaded_asset(instance, False))
    return {"instance": ws._path(instance), "saved": saved, "swaps": [swap(PART_1533, slot, instance) for slot in SLOTS_1533_BRICK]}


VIEWS_ML2 = {
    # The blank side wall of 1533 faces the lot and stands behind the new house; for the test pictures the
    # building level is switched to not visible (level_visible) and switched back afterwards.
    "ML2_street": ((-200.0, 900.0, 170.0), (14.0, -122.0), "the blank south side wall of 1533 from the far side of Wieland, as in the earlier render front_context"),
    "ML2_wall": ((0.0, -1250.0, 800.0), (0.0, 180.0), "square on to the side wall from 15 m: the whole wall, 17.6 m long and 15.3 m high"),
    "ML2_close": ((-1200.0, -1250.0, 300.0), (0.0, 180.0), "the side wall from 3 m: 4.5 m across, more than three repeats of the brick image each way with the corners where four meet"),
    "ML2_front": ((-2700.0, 1150.0, 170.0), (16.0, -90.0), "the street front of 1533 from the far side of Wieland"),
}


def level_visible(level_path, visible):
    """For test pictures only: shows or hides one loaded level in the editor. Nothing is saved by this."""
    world = ws.world()
    for level in unreal.EditorLevelUtils.get_levels(world):
        if level.get_outermost().get_name() == level_path:
            unreal.EditorLevelUtils.set_level_visibility(level, bool(visible), False)
            return True
    return False


def show_1533(old):
    """For the before picture only: puts the earlier brick back on the copy (old=True) or the varied brick (old=False)."""
    if old:
        first = unreal.load_asset("/Game/Wieland/R15_Materials/Production/MI_R15_W1533_Brick")
        second = unreal.load_asset("/Game/Wieland/R15_Materials/Production/MI_R15_sexkaitb_UV")
        return [swap(PART_1533, 0, first)["now"], swap(PART_1533, 1, second)["now"]]
    instance = unreal.load_asset(MATERIALS + "/MI_W1529_R15_1533Brick")
    return [swap(PART_1533, slot, instance)["now"] for slot in SLOTS_1533_BRICK]


# A10. The distant-city stand-in: one mesh of plain blocks and a ground apron, in its own level.
# The layout comes from phase7_farcity.py (a fixed seed; not from a survey or a photograph).
FAR_LEVEL = "/Game/Wieland1529/Surroundings/L_FarCity"
FAR_FOLDER = "/Game/Wieland1529/Surroundings/FarCity"
FAR_MESH = FAR_FOLDER + "/SM_W1529_FarCity"
FAR_PLAN = ws.REVIEW + "/farcity/plan.json"
FAR_LABEL = "FAR_CityStandIn"
POLYHAVEN = "/Game/Wieland/R15_Materials/PolyHaven"
PHASE5 = "/Game/Wieland1529/Materials/Textures"
MASSING_PARENT = MATERIALS + "/M_W1529_Massing"

# kind: (instance name, colour image, relief image, roughness image, roughness in red, size u, size v, tint, roof colour, numbers)
FAR_KINDS = {
    0: ("MI_W1529_FarCity_Brick", POLYHAVEN + "/factory_brick/T_R15_factory_brick_BaseColor", POLYHAVEN + "/factory_brick/T_R15_factory_brick_Normal",
        POLYHAVEN + "/factory_brick/T_R15_factory_brick_ARM", 0.0, 1.0, 1.0, (0.80, 0.68, 0.63), (0.10, 0.10, 0.10),
        {"FloorHeight_m": 3.0, "WindowPeriod_m": 2.6, "WindowWidth_m": 1.1, "WindowHeight_m": 1.7, "Sill_m": 0.8, "Seed": 11.0}),
    1: ("MI_W1529_FarCity_Tower", PHASE5 + "/T_W1529_Concrete046_C", PHASE5 + "/T_W1529_Concrete046_N", PHASE5 + "/T_W1529_Concrete046_R",
        1.0, 2.4, 2.4, (0.58, 0.62, 0.66), (0.16, 0.16, 0.17),
        {"FloorHeight_m": 3.6, "WindowPeriod_m": 3.0, "WindowWidth_m": 2.4, "WindowHeight_m": 2.4, "Sill_m": 0.7, "Seed": 37.0}),
    2: ("MI_W1529_FarCity_Light", POLYHAVEN + "/yellow_brick/T_R15_yellow_brick_BaseColor", POLYHAVEN + "/yellow_brick/T_R15_yellow_brick_Normal",
        POLYHAVEN + "/yellow_brick/T_R15_yellow_brick_ARM", 0.0, 2.5, 2.5, (0.88, 0.86, 0.82), (0.13, 0.13, 0.13),
        {"FloorHeight_m": 3.2, "WindowPeriod_m": 2.8, "WindowWidth_m": 1.4, "WindowHeight_m": 1.9, "Sill_m": 0.8, "Seed": 59.0}),
}
FAR_APRON_SLOT = 3
FAR_APRON_MATERIAL = "/Game/Wieland1529/Site/Materials/MI_W1529_SiteRoad"


def far_instances():
    """Three instances of the Phase 7 building parent (walls with windows as material, roof by direction) for the far blocks."""
    mel = unreal.MaterialEditingLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    parent = unreal.load_asset(MASSING_PARENT)
    out = []
    for kind, (name, colour, relief, rough, rough_red, size_u, size_v, tint, roof, numbers) in FAR_KINDS.items():
        path = FAR_FOLDER + "/" + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            instance = unreal.load_asset(path)
            mel.clear_all_material_instance_parameters(instance)
        else:
            instance = tools.create_asset(name, FAR_FOLDER, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(instance, parent)
        scalars = {"BaseZ_cm": 0.0, "WallTop_m": 500.0, "FrontX": 1.0, "SideWindows": 1.0, "WindowAmount": 1.0, "WindowOffset_m": 1.0,
                   "Wall_SizeU_m": size_u, "Wall_SizeV_m": size_v, "RoughFromRed": rough_red}
        scalars.update(numbers)
        problems = [key for key, value in scalars.items() if not mel.set_material_instance_scalar_parameter_value(instance, key, float(value))]
        vectors = {"Wall_Tint": tint + (1.0,), "Roof_Colour": roof + (1.0,), "Frame_Colour": (0.03, 0.03, 0.03, 1.0), "Stone_Colour": (0.55, 0.54, 0.50, 1.0)}
        problems += [key for key, value in vectors.items() if not mel.set_material_instance_vector_parameter_value(instance, key, unreal.LinearColor(*value))]
        for key, value in (("Wall_BaseColorMap", colour), ("Wall_NormalMap", relief), ("Wall_RoughnessMap", rough)):
            texture = unreal.load_asset(value)
            if texture is None or not mel.set_material_instance_texture_parameter_value(instance, key, texture):
                problems.append(key)
        mel.update_material_instance(instance)
        out.append({"instance": path, "problems": problems, "saved": bool(unreal.EditorAssetLibrary.save_asset(path, False))})
    return out


def far_mesh():
    """Makes (or remakes) the mesh asset of the far blocks and the apron from the plan. Saves the asset by name."""
    import json
    with open(FAR_PLAN, encoding="utf-8") as handle:
        plan = json.load(handle)
    primitives = unreal.GeometryScript_Primitives
    options = unreal.GeometryScriptPrimitiveOptions()
    base = plan["base_cm"]
    total = unreal.DynamicMesh()
    counts = {}
    identity = unreal.Rotator(0.0, 0.0, 0.0)
    one = unreal.Vector(1.0, 1.0, 1.0)
    for kind in sorted(FAR_KINDS):
        part = unreal.DynamicMesh()
        boxes = [b for b in plan["boxes"] if b["kind"] == kind]
        for box in boxes:
            primitives.append_box(part, options, unreal.Transform(unreal.Vector(box["x"], box["y"], base), identity, one),
                                  box["sx"], box["sy"], box["h"] - base, 0, 0, 0, unreal.GeometryScriptPrimitiveOriginMode.BASE)
        if kind:
            unreal.GeometryScript_Materials.remap_material_i_ds(part, 0, kind)
        unreal.GeometryScript_MeshEdits.append_mesh(total, part, unreal.Transform())
        counts[kind] = len(boxes)
    apron = unreal.DynamicMesh()
    side = 2.0 * plan["apron"]["half_side_cm"]
    primitives.append_box(apron, options, unreal.Transform(unreal.Vector(0.0, 0.0, plan["apron"]["top_cm"] - 100.0), identity, one),
                          side, side, 100.0, 0, 0, 0, unreal.GeometryScriptPrimitiveOriginMode.BASE)
    unreal.GeometryScript_Materials.remap_material_i_ds(apron, 0, FAR_APRON_SLOT)
    unreal.GeometryScript_MeshEdits.append_mesh(total, apron, unreal.Transform())
    library = unreal.EditorAssetLibrary
    if library.does_asset_exist(FAR_MESH):
        asset = unreal.load_asset(FAR_MESH)
        write = unreal.GeometryScriptCopyMeshToAssetOptions()
        write.enable_recompute_normals = False
        write.emit_transaction = False
        _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(total, asset, write, unreal.GeometryScriptMeshWriteLOD())
    else:
        create = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
        create.enable_recompute_normals = False
        create.enable_nanite = True
        create.enable_collision = False
        asset, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(total, FAR_MESH, create)
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS or asset is None:
        raise RuntimeError("the far-city mesh could not be written")
    materials = [unreal.load_asset(FAR_FOLDER + "/" + FAR_KINDS[kind][0]) for kind in sorted(FAR_KINDS)] + [unreal.load_asset(FAR_APRON_MATERIAL)]
    slots = []
    for index, material in enumerate(materials):
        slot = unreal.StaticMaterial()
        slot.material_interface = material
        slot.material_slot_name = "far_%d" % index
        slots.append(slot)
    asset.set_editor_property("static_materials", slots)
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    settings = meshes.get_nanite_settings(asset)
    if not settings.enabled:
        settings.enabled = True
        meshes.set_nanite_settings(asset, settings, True)
    low, high = _bounds(total)
    return {"boxes": counts, "triangles": int(total.get_triangle_count()), "low": [round(v) for v in low], "high": [round(v) for v in high],
            "slots": [ws._path(s.material_interface) for s in asset.static_materials], "nanite": bool(meshes.get_nanite_settings(asset).enabled),
            "saved": bool(library.save_loaded_asset(asset, False))}


def far_place():
    """With L_FarCity loaded under L_Site_M2: one object showing the far-city mesh, labelled and tagged as a stand-in."""
    ws._require(ws.SITE_LEVEL)
    for actor in ws.actors():
        if actor.get_actor_label() == FAR_LABEL:
            return {"placed": False, "level": ws.level_of(actor)}
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not editor.set_current_level_by_name(FAR_LEVEL.split("/")[-1]):
        raise RuntimeError("the far-city level is not loaded")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_label(FAR_LABEL)
    actor.tags = [unreal.Name(TAG_PLACEHOLDER), unreal.Name("W1529.FarCityStandIn")]
    component = actor.static_mesh_component
    component.set_static_mesh(unreal.load_asset(FAR_MESH))
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    editor.set_current_level_by_name(ws.world_path().split("/")[-1])
    return {"placed": True, "level": ws.level_of(actor), "materials": [m.get_name() for m in component.get_materials()]}


VIEWS_A10 = {
    "A10_south": ((-11000.0, 800.0, 170.0), (2.0, 0.0), "eye height on Wieland 95 m north of the lot, looking south along the street"),
    "A10_north": ((9000.0, 800.0, 170.0), (2.0, 180.0), "eye height on Wieland 90 m south of the lot, looking north along the street"),
    "A10_east": ((-754.0, 6000.0, 3000.0), (-3.0, -90.0), "from 30 m up, 60 m west of the lot, looking east over the house"),
    "A10_southeast": ((-3000.0, 3000.0, 4500.0), (-4.0, -45.0), "from 45 m up, looking south-east over the house to the tall groups"),
    "A10_high": ((-754.0, -1500.0, 30000.0), (-30.0, 0.0), "from 300 m up over the lot, looking south: the whole stand-in and its edge"),
}
