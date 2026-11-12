"""Phase 7, step 7.3: the trees, placed in the editor from the plan of phase7_trees.py.

Runs inside the Unreal editor's Python, next to wieland_site (ws). Every tree is one object in the level
L_Vegetation with one instanced skinned mesh component (the kind of component the Megaplant trees need for
wind). Every tree is a stand-in: its place and size are from the 2022 laser scan and aerial photograph,
not from a site visit, and the Megaplant library has no licence record.
"""

import csv
import json
import os

import unreal

import wieland_site as ws

LEVEL = "/Game/Wieland1529/Vegetation/L_Vegetation"
FOLDER = "/Game/Wieland1529/Vegetation"
PLAN = ws.REVIEW + "/vegetation/trees_plan.json"
POSITIONS = ws.REVIEW + "/vegetation/tree_positions.csv"
TAG_PLACEHOLDER = "W1529.Placeholder"
TAG_FROM_DATA = "W1529.SurveyedFromDataNotSiteVisit"
TAG_TREE = "W1529.Tree"
NO_LEAVES = FOLDER + "/Materials/M_W1529_NoLeaves"
FOLIAGE_SLOT = 1          # every Megaplant tree: slot 0 bark, slot 1 foliage
WIND_NAME = "WindProvider"


def plan():
    with open(PLAN, encoding="utf-8") as handle:
        return json.load(handle)["trees"]


def trees():
    """The placed trees by label."""
    return {a.get_actor_label(): a for a in ws.actors() if any(str(t) == TAG_TREE for t in a.tags)}


def _component(actor):
    return actor.get_component_by_class(unreal.InstancedSkinnedMeshComponent)


def ground_z(x, y):
    """Height of the Phase 7 site ground (objects SG_ and SW_) under a point; None when no ground is found.

    A ray is cast straight down; whatever it meets that is not site ground (a building, a tree, a hidden
    Revit object that still has collision) is left out and the ray is cast again.
    """
    ignore = []
    for _ in range(12):
        hit = unreal.SystemLibrary.line_trace_single(ws.world(), unreal.Vector(x, y, 40000.0), unreal.Vector(x, y, -1000.0),
                                                     unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore, unreal.DrawDebugTrace.NONE, True)
        if hit is None:
            return None
        values = hit.to_tuple()
        actors = [v for v in values if isinstance(v, unreal.Actor)]
        places = [v for v in values if isinstance(v, unreal.Vector)]
        if not actors or not places:
            return None
        label = actors[0].get_actor_label()
        if label.startswith("SG_") or label.startswith("SW_"):
            return places[0].z
        ignore.append(actors[0])
    return None


def reground(names):
    """Sets the named trees at their planned trunk place, size and ground height again. Returns the heights found."""
    out = {}
    have = trees()
    for tree in plan():
        if tree["name"] not in names or tree["name"] not in have:
            continue
        z = ground_z(tree["trunk_x"], tree["trunk_y"])
        out[tree["name"]] = None if z is None else round(z, 1)
        if z is not None:
            actor = have[tree["name"]]
            actor.modify()
            actor.set_actor_location(unreal.Vector(tree["trunk_x"], tree["trunk_y"], z), False, False)
            component = _component(actor)
            component.modify()
            component.clear_instances()
            component.add_instance(unreal.Transform(unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, tree["yaw"]),
                                                    unreal.Vector(tree["scale_xy"], tree["scale_xy"], tree["scale_z"])), 0, False)
    return out


def place(names=None):
    """Places the trees of the plan that are not there yet. L_Vegetation must be loaded under L_Site_M2."""
    ws._require(ws.SITE_LEVEL)
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not editor.set_current_level_by_name(LEVEL.split("/")[-1]):
        raise RuntimeError("the vegetation level is not loaded")
    spawner = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    subobjects = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    have = trees()
    out = {"placed": 0, "there_already": 0, "no_ground": [], "problems": []}
    try:
        for tree in plan():
            if names is not None and tree["name"] not in names:
                continue
            if tree["name"] in have:
                out["there_already"] += 1
                continue
            z = ground_z(tree["trunk_x"], tree["trunk_y"])
            if z is None:
                out["no_ground"].append(tree["name"])
                z = 0.0
            mesh = unreal.load_asset(tree["asset"])
            if mesh is None:
                out["problems"].append(tree["name"] + ": model missing")
                continue
            actor = spawner.spawn_actor_from_class(unreal.Actor, unreal.Vector(tree["trunk_x"], tree["trunk_y"], z), unreal.Rotator(0.0, 0.0, 0.0))
            actor.set_actor_label(tree["name"])
            actor.tags = [unreal.Name(TAG_TREE), unreal.Name(TAG_PLACEHOLDER), unreal.Name(TAG_FROM_DATA)]
            handles = subobjects.k2_gather_subobject_data_for_instance(actor)
            params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.InstancedSkinnedMeshComponent, blueprint_context=None)
            _, fail = subobjects.add_new_subobject(params)
            component = _component(actor)
            if component is None:
                out["problems"].append(tree["name"] + ": no component (" + str(fail) + ")")
                continue
            component.set_skinned_asset_and_update(mesh)
            component.add_instance(unreal.Transform(unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, tree["yaw"]),
                                                    unreal.Vector(tree["scale_xy"], tree["scale_xy"], tree["scale_z"])), 0, False)
            component.set_transform_provider(unreal.new_object(unreal.DynamicWindData, component, WIND_NAME))
            out["placed"] += 1
    finally:
        editor.set_current_level_by_name(ws.world_path().split("/")[-1])
    return out


def measure():
    """Reads every placed tree back and writes tree_positions.csv: what stands there against the data."""
    have = trees()
    rows = []
    for tree in plan():
        actor = have.get(tree["name"])
        row = {"tree": tree["name"], "data_x_cm": tree["x"], "data_y_cm": tree["y"], "data_height_m": tree["height_m"],
               "data_crown_width_m": tree["crown_width_m"], "in_wieland_right_of_way": tree["in_wieland_right_of_way"],
               "distance_from_lot_ft": tree["distance_from_lot_ft"]}
        if actor is None:
            row.update({"placed": "no"})
            rows.append(row)
            continue
        component = _component(actor)
        place_now = actor.get_actor_location()
        mesh = component.get_skinned_asset()
        bounds = mesh.get_bounds()
        instance = component.get_instance_transform(component.get_instance_id(0), False) if hasattr(component, "get_instance_id") else None
        scale = instance.scale3d if instance is not None else unreal.Vector(tree["scale_xy"], tree["scale_xy"], tree["scale_z"])
        height = (bounds.origin.z + bounds.box_extent.z) * scale.z / 100.0
        width = 2.0 * max(bounds.box_extent.x, bounds.box_extent.y) * scale.x / 100.0
        offset = ((place_now.x - tree["x"]) ** 2 + (place_now.y - tree["y"]) ** 2) ** 0.5 / 100.0
        row.update({
            "placed": "yes", "placed_x_cm": round(place_now.x, 1), "placed_y_cm": round(place_now.y, 1), "ground_z_cm": round(place_now.z, 1),
            "trunk_offset_from_data_m": round(offset, 3), "placed_height_m": round(height, 2), "height_difference_m": round(height - tree["height_m"], 2),
            "placed_crown_width_m": round(width, 2), "crown_width_difference_m": round(width - tree["crown_width_m"], 2),
            "trunk_diameter": "not known: no survey of the trunk exists", "model": tree["asset"].split("/")[-1],
            "species_of_model": tree["species_of_model"], "real_species": "not known (no site visit)",
            "scale_width": tree["scale_xy"], "scale_height": tree["scale_z"], "source": tree["source"], "note": tree["note"],
            "data_point_lies_on": tree["data_point_lies_on"], "trunk_note": tree["trunk_note"], "planned_trunk_shift_m": tree["trunk_shift_m"],
            "tags": " ".join(str(t) for t in actor.tags), "leaves": "off" if ws._path(component.get_material(FOLIAGE_SLOT)) == NO_LEAVES else "on",
            "wind": "on" if component.get_transform_provider() is not None else "off"})
        rows.append(row)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    os.makedirs(os.path.dirname(POSITIONS), exist_ok=True)
    with open(POSITIONS, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    placed = [r for r in rows if r.get("placed") == "yes"]
    return {"trees_in_plan": len(rows), "placed": len(placed),
            "largest_trunk_offset_m": max([r["trunk_offset_from_data_m"] for r in placed] or [0]),
            "largest_height_difference_m": max([abs(r["height_difference_m"]) for r in placed] or [0]),
            "largest_crown_difference_m": max([abs(r["crown_width_difference_m"]) for r in placed] or [0]),
            "tagged_placeholder": sum(1 for r in placed if TAG_PLACEHOLDER in r["tags"]),
            "tagged_from_data": sum(1 for r in placed if TAG_FROM_DATA in r["tags"])}


def no_leaves_material():
    """A material that draws nothing (masked, fully cut away): put in the foliage slot it gives the leaf-off state."""
    library = unreal.EditorAssetLibrary
    if library.does_asset_exist(NO_LEAVES):
        return unreal.load_asset(NO_LEAVES)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    folder, name = NO_LEAVES.rsplit("/", 1)
    material = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    material.set_editor_property("two_sided", True)
    zero = mel.create_material_expression(material, unreal.MaterialExpressionConstant, -300, 0)
    zero.set_editor_property("r", 0.0)
    mel.connect_material_property(zero, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    usage_ok = [mel.set_material_usage(material, usage)[0] if isinstance(mel.set_material_usage(material, usage), tuple) else True
                for usage in (unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH, unreal.MaterialUsage.MATUSAGE_NANITE)]
    mel.recompile_material(material)
    library.save_loaded_asset(material, False)
    return material


def season(leaves):
    """Leaf-on (True) or leaf-off (False) for every placed tree: the foliage slot shows the model's leaves or nothing."""
    blank = no_leaves_material()
    changed = 0
    for tree in plan():
        actor = trees().get(tree["name"])
        if actor is None:
            continue
        component = _component(actor)
        wanted = unreal.load_asset(tree["materials"][FOLIAGE_SLOT]) if leaves else blank
        if ws._path(component.get_material(FOLIAGE_SLOT)) != ws._path(wanted):
            component.modify()
            component.set_material(FOLIAGE_SLOT, wanted)
            changed += 1
    return {"leaves": "on" if leaves else "off", "changed": changed}


SEASON_LIST = "Season"
SEASON_ON = "Leaf-on (summer)"
SEASON_OFF = "Leaf-off (November)"
SEASON_PROPERTY = "DefaultSceneRoot / InstancedSkinnedMesh / Material[%d]" % FOLIAGE_SLOT


def build_season_variants():
    """Makes (or remakes) the list "Season" in the Variant Manager asset: one action for leaf-on or leaf-off. Saves the asset by name."""
    ws._require(ws.SITE_LEVEL)
    library = unreal.VariantManagerLibrary
    sets_asset = ws.variant_asset()
    if sets_asset is None:
        raise RuntimeError("no variant asset")
    for index in reversed(range(sets_asset.get_num_variant_sets())):
        old = sets_asset.get_variant_set(index)
        if str(old.get_display_text()) == SEASON_LIST:
            library.remove_variant_set(sets_asset, old)
    variant_set = unreal.VariantSet()
    variant_set.set_display_text(SEASON_LIST)
    library.add_variant_set(sets_asset, variant_set)
    blank = no_leaves_material()
    have = trees()
    out = {"trees": 0, "values": 0, "missed": 0}
    for option in (SEASON_ON, SEASON_OFF):
        variant = unreal.Variant()
        variant.set_display_text(option)
        library.add_variant(variant_set, variant)
        for tree in plan():
            actor = have.get(tree["name"])
            if actor is None:
                continue
            library.add_actor_binding(variant, actor)
            value = library.capture_property(variant, actor, SEASON_PROPERTY)
            if value is None:
                out["missed"] += 1
                continue
            library.set_value_object(value, unreal.load_asset(tree["materials"][FOLIAGE_SLOT]) if option == SEASON_ON else blank)
            out["values"] += 1
    out["trees"] = len(have)
    out["saved"] = bool(unreal.EditorAssetLibrary.save_loaded_asset(sets_asset, False))
    return out


def leaves_state():
    have = trees()
    off = sum(1 for a in have.values() if ws._path(_component(a).get_material(FOLIAGE_SLOT)) == NO_LEAVES)
    return {"trees": len(have), "leaf_off": off, "leaf_on": len(have) - off}


def wind(on, names=None):
    """Wind on or off: with the wind provider the engine moves the tree's bones; without it the tree stands still."""
    changed = 0
    for label, actor in trees().items():
        if names is not None and label not in names:
            continue
        component = _component(actor)
        has = component.get_transform_provider() is not None
        if on and not has:
            component.modify()
            component.set_transform_provider(unreal.new_object(unreal.DynamicWindData, component, WIND_NAME))
            changed += 1
        elif not on and has:
            component.modify()
            component.set_transform_provider(None)
            changed += 1
    return {"wind": "on" if on else "off", "changed": changed}


def show(visible):
    """All trees visible or not (for the cost measurement and for pictures without trees)."""
    changed = 0
    for actor in trees().values():
        component = _component(actor)
        if bool(component.get_editor_property("visible")) != bool(visible):
            component.modify()
            component.set_visibility(bool(visible), False)
            changed += 1
    return {"visible": bool(visible), "changed": changed}


VIEWS = {
    # name: (place x, y, z in cm; pitch, yaw; what it shows)
    "V1_frontage": ((-1876.0, 1500.0, 170.0), (24.0, -90.0), "the frontage parkway tree T01 (12.7 m) from the far sidewalk"),
    "V2_street_north": ((2500.0, 900.0, 170.0), (8.0, -172.0), "Wieland looking north past the lot: the two frontage trees T03 and T01"),
    "V3_street_south": ((-5500.0, 900.0, 170.0), (8.0, -8.0), "Wieland looking south past the lot"),
    "V4_above": ((-754.0, -1500.0, 14000.0), (-89.0, 180.0), "straight down from 140 m: the trees against the ground"),
    "V5_rear": ((684.0, -5500.0, 170.0), (22.0, 90.0), "the large tree T02 (23.8 m) south-east of the lot, from the east"),
}


def cameras(views=None):
    """Temporary cameras; ws.shots_end() removes them with the station cameras."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(ws.world_path().split("/")[-1])
    made = 0
    for name, (where, turn, _what) in (views or VIEWS).items():
        camera = subsystem.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*where), unreal.Rotator(pitch=turn[0], yaw=turn[1], roll=0.0))
        camera.set_actor_label("TEMP_" + name)
        camera.tags = [ws.SHOT_TAG, name]
        component = camera.camera_component
        component.set_editor_property("field_of_view", 73.74)
        component.set_editor_property("constrain_aspect_ratio", True)
        component.set_editor_property("aspect_ratio", 16.0 / 9.0)
        made += 1
    return made
