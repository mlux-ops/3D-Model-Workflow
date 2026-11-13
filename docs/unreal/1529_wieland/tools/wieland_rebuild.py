"""Phase 12: rebuilt materials of 1529 N. Wieland, made active by override (runs inside the editor).

Reads review/phase12/recipes.json (written by phase12_recipes.py). Nothing that Datasmith imported is
edited: a rebuilt material is a new instance under /Game/Wieland1529/Materials/Rebuilt/, and it is shown
by a material override on the placed object. Every override is listed in a table, held in a Variant
Manager list with the two options "Revit as exported" and "Phase 12 active", and removed by revert().

    import wieland_rebuild as wr
    wr.build_parents()                    # the two parents this phase adds (copies of the Opaque parent)
    wr.import_images(recipes)             # the images the recipes name; existing ones are left alone
    wr.build(recipes, only=[...])         # the instances; rebuild=True remakes existing ones
    wr.sync(recipes, table_csv)           # sets and removes overrides so that the level matches the recipes
    wr.save_levels()                      # saves the building levels that sync() changed, by name
    wr.build_variants(recipes)            # the Variant Manager list
    wr.switch("Revit as exported")        # or "Phase 12 active"
    wr.revert(table_csv)                  # removes every override of this phase (does not save)
"""
import collections
import csv
import json

import unreal

import wieland_parents as wp
from wieland_materials import MATERIALS, MEL

REBUILT = MATERIALS + "/Rebuilt"
CANDIDATES = MATERIALS + "/Candidates"
OURS = (REBUILT + "/", CANDIDATES + "/")
DATASMITH = "/Game/Wieland1529/Building/Datasmith/25-006_1527_N_Wieland-3DView-3D_View_188/Materials/"
BUILDING_LEVELS = ("L_W1529_Shell", "L_W1529_NorthTriplex", "L_W1529_NorthPenthouse", "L_W1529_SouthTriplex",
                   "L_W1529_SouthPenthouse")
NEVER_SAVE = "/Game/Wieland/R15_Landscape/L_R15_Production"
VARIANT_FOLDER = MATERIALS + "/Variants"
VARIANT_ASSET = "LVS_W1529_Phase12_Materials"
VARIANT_SET = "Phase 12 materials"
OPTION_REVIT = "Revit as exported"
OPTION_ACTIVE = "Phase 12 active"

_EMISSIVE = "M_W1529_Emissive"
_STONE = "M_W1529_StoneBlend"

_MACRO = """
float3 ratio = lerp(float3(1.0, 1.0, 1.0), Map.rgb * 2.0, Amount);
return Colour * ratio;
"""


def _load(recipes_json):
    with open(recipes_json, encoding="utf-8") as handle:
        return json.load(handle)


def _copy_of_opaque(name):
    """A fresh copy of the Phase 5 Opaque parent under a new name. The Opaque parent is not changed.
    Returns (material, whether it was there already); an existing copy is returned as it is."""
    path = wp.PARENTS + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.load_asset(path), True
    source = wp.PARENTS + "/" + wp.PARENT_NAMES["Opaque"]
    material = unreal.EditorAssetLibrary.duplicate_asset(source, path)
    if material is None:
        raise RuntimeError("could not copy %s to %s" % (source, path))
    return material, False


def build_parents():
    """Makes the two parents this phase adds; each is the Opaque parent with one more block.

    M_W1529_Emissive: adds light given off by the surface, EmissiveColor (brightness 1) times
    Luminance_cd_m2 (candela per square metre; the project's exposure is in physical units).
    M_W1529_StoneBlend: adds MacroColorMap, a very large image laid in world metres (MacroSize_m) whose
    value, times two, multiplies the colour, so that 0.5 grey changes nothing; MacroColorAmount fades it.
    """
    result = {}
    material, existed = _copy_of_opaque(_EMISSIVE)
    if not existed:
        g = wp._Graph(material)
        colour = g.vector("EmissiveColor", (1, 1, 1, 1), "6 Light")
        luminance = g.scalar("Luminance_cd_m2", 0.0, "6 Light")
        glow = g.binary(unreal.MaterialExpressionMultiply, g.mask(colour, r=True, g=True, b=True), luminance)
        g.out(glow, wp.MP.MP_EMISSIVE_COLOR)
        result[_EMISSIVE] = wp._finish(material)
    else:
        result[_EMISSIVE] = "already there"
    material, existed = _copy_of_opaque(_STONE)
    if not existed:
        before = MEL.get_material_property_input_node(material, wp.MP.MP_BASE_COLOR)
        if before is None:
            raise RuntimeError("the copy of the Opaque parent has nothing wired to its colour")
        output = MEL.get_material_property_input_node_output_name(material, wp.MP.MP_BASE_COLOR)
        g = wp._Graph(material)
        macro_map = g.texture("MacroColorMap", wp.TEXTURES + "/T_W1529_WhiteLinear", wp.ST.SAMPLERTYPE_MASKS,
                              "3 Variation")
        size = g.scalar("MacroSize_m", 24.4, "3 Variation")
        amount = g.scalar("MacroColorAmount", 1.0, "3 Variation")
        # The same parameter name as in the Opaque mapping; both follow one setting.
        turn = g.scalar("WorldYawDeg", wp.BUILDING_YAW, "1 Mapping")
        flat = g.custom("World mapping in metres (zones)", wp._WORLD_UV, wp.CMOT.CMOT_FLOAT2,
                        [("WP", g.node(unreal.MaterialExpressionWorldPosition)),
                         ("N", g.node(unreal.MaterialExpressionVertexNormalWS)), ("YawDeg", turn),
                         ("Swap", g.constant(0.0))])
        sample = g.sample(macro_map, g.binary(unreal.MaterialExpressionDivide, flat, size), wp.ST.SAMPLERTYPE_MASKS)
        mixed = g.custom("Zones of colour", _MACRO, wp.CMOT.CMOT_FLOAT3,
                         [("Colour", before, output), ("Map", g.mask(sample, r=True, g=True, b=True)),
                          ("Amount", amount)])
        g.out(mixed, wp.MP.MP_BASE_COLOR)
        result[_STONE] = wp._finish(material)
    else:
        result[_STONE] = "already there"
    return result


def import_images(recipes_json, only=None):
    """Imports the images the recipes name (all, or those whose asset name is in `only`)."""
    items = [item for item in _load(recipes_json)["imports"] if only is None or item[2] in only]
    return wp.import_textures(items)


def build(recipes_json, only=None, rebuild=False):
    """Builds and saves the instances of the recipes (all, or the materials named in `only`)."""
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    built, skipped, problems = [], 0, []
    for recipe in _load(recipes_json)["rebuild"]:
        name = recipe["material"]
        if only is not None and name not in only:
            continue
        path = recipe["asset"]
        exists = unreal.EditorAssetLibrary.does_asset_exist(path)
        if exists and not rebuild:
            skipped += 1
            continue
        try:
            parent = unreal.load_asset(recipe["parent"])
            if parent is None:
                raise RuntimeError("parent missing: " + recipe["parent"])
            if exists:
                instance = unreal.load_asset(path)
                MEL.clear_all_material_instance_parameters(instance)
            else:
                folder, asset_name = path.rsplit("/", 1)
                instance = tools.create_asset(asset_name, folder, unreal.MaterialInstanceConstant,
                                              unreal.MaterialInstanceConstantFactoryNew())
            MEL.set_material_instance_parent(instance, parent)
            for key, value in recipe["switches"].items():
                MEL.set_material_instance_static_switch_parameter_value(instance, key, bool(value))
            for key, value in recipe["scalars"].items():
                if not MEL.set_material_instance_scalar_parameter_value(instance, key, float(value)):
                    problems.append("%s: no number called %s" % (name, key))
            for key, value in recipe["vectors"].items():
                if not MEL.set_material_instance_vector_parameter_value(instance, key, unreal.LinearColor(*value)):
                    problems.append("%s: no colour called %s" % (name, key))
            for key, value in recipe["textures"].items():
                texture = unreal.load_asset(value)
                if texture is None:
                    problems.append("%s: image missing: %s" % (name, value))
                    continue
                if not MEL.set_material_instance_texture_parameter_value(instance, key, texture):
                    problems.append("%s: no image called %s" % (name, key))
            MEL.update_material_instance(instance)
            if not unreal.EditorAssetLibrary.save_asset(path, False):
                problems.append("%s: not saved" % name)
            built.append(name)
        except Exception as error:  # one bad recipe must not stop the rest
            problems.append("%s: %s" % (name, error))
    return {"built": len(built), "skipped_existing": skipped, "problems": problems}


def verify(recipes_json):
    """Read-only. Recipes whose saved instance is missing or differs from the recipe: {material: [what]}."""
    wrong = {}
    for recipe in _load(recipes_json)["rebuild"]:
        instance = unreal.load_asset(recipe["asset"])
        if instance is None:
            wrong[recipe["material"]] = ["no asset"]
            continue
        found = []
        parent = instance.get_editor_property("parent")
        if parent is None or parent.get_path_name().split(".")[0] != recipe["parent"]:
            found.append("parent")
        for key, value in recipe["scalars"].items():
            if abs(MEL.get_material_instance_scalar_parameter_value(instance, key) - float(value)) > 1e-4:
                found.append(key)
        for key, value in recipe["vectors"].items():
            colour = MEL.get_material_instance_vector_parameter_value(instance, key)
            if max(abs(a - b) for a, b in zip((colour.r, colour.g, colour.b), value[:3])) > 1e-4:
                found.append(key)
        for key, value in recipe["textures"].items():
            texture = MEL.get_material_instance_texture_parameter_value(instance, key)
            if texture is None or texture.get_path_name().split(".")[0] != value:
                found.append(key)
        for key, value in recipe["switches"].items():
            if bool(MEL.get_material_instance_static_switch_parameter_value(instance, key)) != bool(value):
                found.append(key)
        if found:
            wrong[recipe["material"]] = found
    return wrong


def _level_name(actor):
    return actor.get_outer().get_outer().get_name()


def _slots():
    """Every surface of the open world whose mesh carries a Datasmith material:
    (actor, component, slot, Revit material path, the override on it or None)."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.static_mesh
            if mesh is None:
                continue
            overrides = list(component.get_editor_property("override_materials"))
            for slot in range(component.get_num_materials()):
                base = mesh.get_material(slot)
                if base is None:
                    continue
                path = base.get_path_name().split(".")[0]
                if not path.startswith(DATASMITH):
                    continue
                yield actor, component, slot, path, overrides[slot] if slot < len(overrides) else None


def _wanted(recipes_json):
    data = _load(recipes_json)
    return {item["revit"]: item["asset"] for item in data["rebuild"] + data["candidates"]}


def sync(recipes_json, table_csv, dry_run=False):
    """Makes the level show what the recipes say: a surface whose Revit material has a rebuilt or
    candidate material gets that as an override; a surface that carries an override of this phase
    which the recipes no longer ask for gets it removed. Overrides that are not of this phase are left
    alone and counted. Writes the table of all overrides of this phase. Saves nothing."""
    wanted = _wanted(recipes_json)
    loaded, rows = {}, []
    counts = collections.Counter()
    for actor, component, slot, revit, override in _slots():
        target = wanted.get(revit)
        current = override.get_path_name().split(".")[0] if override is not None else None
        if current is not None and not current.startswith(OURS):
            counts["left: another override is on the surface"] += 1
            continue
        if target != current:
            if target is None:
                counts["override removed"] += 1
                if not dry_run:
                    component.modify()
                    component.set_material(slot, None)
            else:
                if target not in loaded:
                    loaded[target] = unreal.load_asset(target)
                if loaded[target] is None:
                    counts["asset missing"] += 1
                    continue
                counts["override set"] += 1
                if not dry_run:
                    component.modify()
                    component.set_material(slot, loaded[target])
        elif target is not None:
            counts["already right"] += 1
        if target is not None:
            rows.append([_level_name(actor), actor.get_actor_label(), actor.get_name(), component.get_name(), slot,
                         revit.rsplit("/", 1)[-1], target])
    if not dry_run:
        rows.sort()
        with open(table_csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["level", "object_label", "object_name", "component", "surface_slot", "revit_material",
                             "active_material"])
            writer.writerows(rows)
    return {"counts": dict(counts), "surfaces_with_an_active_material": len(rows),
            "levels": dict(collections.Counter(row[0] for row in rows)), "unsaved": dirty()}


def revert(table_csv=None):
    """Removes every override of this phase from the open world (does not save). Returns the count."""
    count = 0
    for actor, component, slot, revit, override in _slots():
        if override is not None and override.get_path_name().split(".")[0].startswith(OURS):
            component.modify()
            component.set_material(slot, None)
            count += 1
    return {"overrides_removed": count, "unsaved": dirty()}


def state(recipes_json):
    """Read-only. How many surfaces show what, against the recipes."""
    wanted = _wanted(recipes_json)
    counts = collections.Counter()
    for actor, component, slot, revit, override in _slots():
        target = wanted.get(revit)
        current = override.get_path_name().split(".")[0] if override is not None else None
        if target is None:
            counts["no change asked: " + ("as exported" if current is None else "OVERRIDDEN")] += 1
        elif current == target:
            counts["active material shown"] += 1
        elif current is None or current == revit:
            counts["change asked, Revit material shown"] += 1
        else:
            counts["change asked, something else shown"] += 1
    return dict(counts)


def dirty():
    utils = unreal.EditorLoadingAndSavingUtils
    return sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))


def save_levels():
    """Saves the unsaved packages when, and only when, every one of them belongs to the five building
    levels; otherwise saves nothing and returns what stood in the way."""
    utils = unreal.EditorLoadingAndSavingUtils
    packages = list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages())
    foreign = sorted(p.get_name() for p in packages
                     if not any(level in p.get_name() for level in BUILDING_LEVELS) or NEVER_SAVE in p.get_name())
    if foreign:
        return {"saved": False, "not_building_levels": foreign}
    names = sorted(p.get_name() for p in packages)
    saved = utils.save_packages(packages, True) if packages else True
    return {"saved": bool(saved), "packages": names, "still_unsaved": dirty()}


def _property_path(library, actor, component, slot):
    wanted = "Material[%d]" % slot
    paths = [str(path) for path in library.get_capturable_properties(actor)]
    name = component.get_name()
    exact = [path for path in paths if path.endswith(wanted) and name in path]
    if exact:
        return exact[0]
    loose = [path for path in paths if path.endswith(wanted)]
    return loose[0] if len(loose) == 1 else None


def variant_asset():
    return unreal.load_asset(VARIANT_FOLDER + "/" + VARIANT_ASSET)


def build_variants(recipes_json):
    """Makes (or remakes) the Variant Manager list of this phase and saves the asset: one list with the
    options "Revit as exported" and "Phase 12 active", holding every surface whose material this phase
    changed. The level is not changed by building it."""
    library = unreal.VariantManagerLibrary
    wanted = _wanted(recipes_json)
    sets_asset = variant_asset()
    if sets_asset is None:
        sets_asset = library.create_level_variant_sets_asset(VARIANT_ASSET, VARIANT_FOLDER)
    for index in reversed(range(sets_asset.get_num_variant_sets())):
        old = sets_asset.get_variant_set(index)
        if str(old.get_display_text()) == VARIANT_SET:
            library.remove_variant_set(sets_asset, old)
    variant_set = unreal.VariantSet()
    variant_set.set_display_text(VARIANT_SET)
    library.add_variant_set(sets_asset, variant_set)
    made = {}
    for option in (OPTION_REVIT, OPTION_ACTIVE):
        variant = unreal.Variant()
        variant.set_display_text(option)
        library.add_variant(variant_set, variant)
        made[option] = variant
    by_actor = collections.defaultdict(list)
    for actor, component, slot, revit, override in _slots():
        if revit in wanted:
            by_actor[actor.get_path_name()].append((actor, component, slot, revit, wanted[revit]))
    loaded, captured, missed = {}, 0, 0
    for entries in by_actor.values():
        actor = entries[0][0]
        for variant in made.values():
            library.add_actor_binding(variant, actor)
        for actor, component, slot, revit, active in entries:
            path = _property_path(library, actor, component, slot)
            if path is None:
                missed += 1
                continue
            for option, variant in made.items():
                target = revit if option == OPTION_REVIT else active
                if target not in loaded:
                    loaded[target] = unreal.load_asset(target)
                value = library.capture_property(variant, actor, path)
                if value is None or loaded[target] is None:
                    missed += 1
                    continue
                library.set_value_object(value, loaded[target])
            captured += 1
    saved = unreal.EditorAssetLibrary.save_loaded_asset(sets_asset, False)
    return {"objects": len(by_actor), "surfaces": captured, "surfaces_not_offered_by_the_engine": missed,
            "saved": bool(saved), "asset": VARIANT_FOLDER + "/" + VARIANT_ASSET}


def switch(option):
    """One action: put one option of the Phase 12 list on. Returns True when the option exists.
    This changes the level in memory; it does not save."""
    sets_asset = variant_asset()
    if sets_asset is None:
        return False
    for index in range(sets_asset.get_num_variant_sets()):
        variant_set = sets_asset.get_variant_set(index)
        if str(variant_set.get_display_text()) != VARIANT_SET:
            continue
        for number in range(variant_set.get_num_variants()):
            variant = variant_set.get_variant(number)
            if str(variant.get_display_text()) == option:
                variant.switch_on()
                return True
    return False
