"""Phase 6, step 6.7: switchable alternatives for kitchen, bath and floor surfaces of 1529 N. Wieland.

The owner has not named the alternatives, so this tool builds the switching mechanism only, with the
engine's Variant Manager: a "Level Variant Sets" asset holds lists of named options (variant sets);
each option (variant) remembers, for a set of objects, which material each of their surfaces shows,
and puts all of them on in one action. Three lists are built: kitchen, bath and floor surfaces. Each
has two first options: "Revit as exported" (the material that Datasmith imported) and "Phase 5
candidates" (the candidate of material_alternatives.csv). Nothing imported is edited: an option only
sets a material override on the placed object, and "Revit as exported" removes nothing from disk.

What counts as which (measured, see classify()):
  floor    every surface of an object of the Revit category Floors (they lie in the shell level), outside baths;
  bath     every surface of an object that stands in a bath or powder room, the floor there included,
           and the walls that bound such a room, for their tile and stone surfaces only;
  kitchen  casework, appliances, sinks and faucets within KITCHEN_REACH of a cooktop on the same storey.
Only surfaces whose Revit material has a Phase 5 candidate can switch.

    import wieland_variants as wv
    wv.classify(csv_path)                 # read-only: what would switch
    wv.build(csv_path)                    # makes and saves the asset; returns counts
    wv.switch("Floor surfaces", "Phase 5 candidates")
    wv.state(csv_path)                    # which option every surface shows now
"""
import collections
import csv
import math

import unreal

import wieland_levels
import wieland_standins
import wieland_trim

ASSET_FOLDER = "/Game/Wieland1529/Interiors/Variants"
ASSET_NAME = "LVS_W1529_Interior_Alternatives"
ACTOR_LABEL = "W1529_Interior_Alternatives"
SETS = (("kitchen", "Kitchen surfaces"), ("bath", "Bath surfaces"), ("floor", "Floor surfaces"))
OPTION_REVIT = "Revit as exported"
OPTION_CANDIDATE = "Phase 5 candidates"
KITCHEN_REACH = 450.0   # cm from a cooktop, on the same storey
KITCHEN_CATEGORIES = ("Casework", "Specialty Equipment", "Plumbing Fixtures", "Generic Models")
COOKTOP = "Cooktop"
BATH_ROOMS = ("bath", "powder")
BATH_FIXTURES = ("Toilet", "Bath-", "Bathing", "Shower")
BATH_LARGEST = 700      # grid cells of 10 x 10 cm, that is 7 square metres of open floor (the largest
                        # named bath has 6.6); a 10 square metre room with one shower head is left out
WALL_FAMILIES = ("tile", "stone")   # of a wall that bounds a bath, only these surfaces switch
STOREY_CODES = ("L", "1", "2", "3", "4", "R")


def _rows(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _storey_code(z):
    code = "L"
    for name in STOREY_CODES:
        if z >= wieland_standins.STOREYS[name][1] - 30.0:
            code = name
    return code


def _bath_cells():
    """{storey code: set of grid cells} of the bath and powder rooms of both halves."""
    cells = collections.defaultdict(set)
    grids = {}
    for half in ("North", "South"):
        for name, (code, x, y) in wieland_standins.rooms(half).items():
            if not any(word in name for word in BATH_ROOMS):
                continue
            if code not in grids:
                grids[code] = wieland_standins.storey_grid(code)[0]
            cells[code] |= wieland_standins.region(grids[code], x, y)
    # The list of named rooms does not hold every bath: a room that holds a toilet, a bathtub or a
    # shower is a bath as well, unless it is larger than any bath (then the fixture was read through
    # a wall, or the room is open to others).
    for label, category, box in wieland_standins.parts():
        if category != "Plumbing Fixtures" or not any(word in label for word in BATH_FIXTURES):
            continue
        code = _storey_code((box[2] + box[5]) / 2.0)
        if code not in grids:
            grids[code] = wieland_standins.storey_grid(code)[0]
        found = wieland_standins.region(grids[code], (box[0] + box[3]) / 2.0, (box[1] + box[4]) / 2.0)
        if 0 < len(found) <= BATH_LARGEST:
            cells[code] |= found
    return cells


def _touches(cells, box, grow):
    i0, i1 = wieland_standins._cells(box[0], box[3], wieland_standins.X_MIN, wieland_standins.NX)
    j0, j1 = wieland_standins._cells(box[1], box[4], wieland_standins.Y_MIN, wieland_standins.NY)
    for i in range(i0 - grow, i1 + grow + 1):
        for j in range(j0 - grow, j1 + grow + 1):
            if (i, j) in cells:
                return True
    return False


def classify(csv_path):
    """Read-only. The surfaces that can switch: {"kitchen" | "bath" | "floor": [(actor, component, slot,
    Revit material path, candidate path, category)]}, and the surfaces with a candidate that belong to
    none of the three lists, counted by category."""
    candidates = {}
    families = {}
    for row in _rows(csv_path):
        key = row["revit_asset"].split(".")[0]
        candidates[key] = row["candidate_asset"]
        families[key] = row["family"]
    baths = _bath_cells()
    parts = wieland_trim._building_components()
    cooktops = []
    for actor, component, category in parts:
        if COOKTOP in actor.get_actor_label():
            box = wieland_trim._component_box(component)
            cooktops.append(((box[0] + box[3]) / 2.0, (box[1] + box[4]) / 2.0,
                             _storey_code((box[2] + box[5]) / 2.0)))
    found = {"kitchen": [], "bath": [], "floor": []}
    other = collections.Counter()
    for actor, component, category in parts:
        box = wieland_trim._component_box(component)
        middle = ((box[0] + box[3]) / 2.0, (box[1] + box[4]) / 2.0, (box[2] + box[5]) / 2.0)
        code = _storey_code(middle[2] if category != "Floors" else box[5])
        small = (middle[0] - 5.0, middle[1] - 5.0, box[2], middle[0] + 5.0, middle[1] + 5.0, box[5])
        # A floor, ceiling or door counts by its middle; a fixture stands on closed cells against a
        # wall, so it counts when its box touches the open floor of a bath.
        whole = category not in ("Floors", "Ceilings", "Roofs", "Doors", "Walls", "Windows")
        in_bath = _touches(baths.get(code, ()), box if whole else small, 1)
        wall_of_bath = category == "Walls" and _touches(baths.get(code, ()), box, 2)
        in_kitchen = (category in KITCHEN_CATEGORIES and not in_bath and any(
            code == c and math.hypot(middle[0] - x, middle[1] - y) <= KITCHEN_REACH for x, y, c in cooktops))
        for slot in range(component.get_num_materials()):
            material = component.get_material(slot)
            if material is None:
                continue
            key = material.get_path_name().split(".")[0]
            # A slot that shows the candidate already still belongs to its Revit material.
            mesh_material = component.static_mesh.get_material(slot)
            if mesh_material is not None:
                key = mesh_material.get_path_name().split(".")[0]
            if key not in candidates:
                continue
            entry = (actor, component, slot, key, candidates[key], category)
            if in_bath and category != "Walls":
                found["bath"].append(entry)
            elif wall_of_bath:
                if families[key] in WALL_FAMILIES:
                    found["bath"].append(entry)
                else:
                    other["Walls beside a bath, not tile or stone"] += 1
            elif category == "Floors":
                found["floor"].append(entry)
            elif in_kitchen:
                found["kitchen"].append(entry)
            else:
                other[category] += 1
    return found, other


def summary(csv_path):
    """Read-only. Counts of classify(): surfaces, objects and materials per list."""
    found, other = classify(csv_path)
    result = {}
    for key, entries in found.items():
        materials = collections.Counter(entry[3].rsplit("/", 1)[-1] for entry in entries)
        categories = collections.Counter(entry[5] for entry in entries)
        units = collections.Counter(wieland_levels._level_name(entry[0]) for entry in entries)
        result[key] = {"surfaces": len(entries), "objects": len(set(entry[0].get_path_name() for entry in entries)),
                       "materials": dict(materials.most_common()), "categories": dict(categories.most_common()),
                       "levels": dict(units)}
    result["with a candidate but in none of the three lists"] = dict(other.most_common())
    return result


def _library():
    return unreal.VariantManagerLibrary


def asset():
    return unreal.load_asset(ASSET_FOLDER + "/" + ASSET_NAME)


def _property_path(actor, component, slot):
    """The name under which the Variant Manager offers the material of one surface, or None."""
    wanted = "Material[%d]" % slot
    paths = [str(path) for path in _library().get_capturable_properties(actor)]
    name = component.get_name()
    exact = [path for path in paths if path.endswith(wanted) and name in path]
    if exact:
        return exact[0]
    loose = [path for path in paths if path.endswith(wanted)]
    return loose[0] if len(loose) == 1 else None


def build(csv_path, only=None):
    """Makes (or remakes) the variant sets of the lists named in `only` (all three without it) and saves
    the asset. Returns counts. The level is not changed: the values are written into the options
    directly, not taken from what the level shows."""
    library = _library()
    sets_asset = asset()
    if sets_asset is None:
        sets_asset = library.create_level_variant_sets_asset(ASSET_NAME, ASSET_FOLDER)
    found, _ = classify(csv_path)
    result = {}
    for key, title in SETS:
        if only and key not in only:
            continue
        for index in reversed(range(sets_asset.get_num_variant_sets())):
            old = sets_asset.get_variant_set(index)
            if str(old.get_display_text()) == title:
                library.remove_variant_set(sets_asset, old)
        variant_set = unreal.VariantSet()
        variant_set.set_display_text(title)
        library.add_variant_set(sets_asset, variant_set)
        made = {}
        for option in (OPTION_REVIT, OPTION_CANDIDATE):
            variant = unreal.Variant()
            variant.set_display_text(option)
            library.add_variant(variant_set, variant)
            made[option] = variant
        loaded = {}
        captured, missed = 0, 0
        by_actor = collections.defaultdict(list)
        for entry in found[key]:
            by_actor[entry[0].get_path_name()].append(entry)
        for entries in by_actor.values():
            actor = entries[0][0]
            for option, variant in made.items():
                library.add_actor_binding(variant, actor)
            for actor, component, slot, revit, candidate, category in entries:
                path = _property_path(actor, component, slot)
                if path is None:
                    missed += 1
                    continue
                for option, variant in made.items():
                    target = revit if option == OPTION_REVIT else candidate
                    if target not in loaded:
                        loaded[target] = unreal.load_asset(target)
                    value = library.capture_property(variant, actor, path)
                    if value is None or loaded[target] is None:
                        missed += 1
                        continue
                    library.set_value_object(value, loaded[target])
                captured += 1
        result[title] = {"objects": len(by_actor), "surfaces": captured, "surfaces_not_offered_by_the_engine": missed}
    unreal.EditorAssetLibrary.save_loaded_asset(sets_asset, False)
    return result


def _variant(title, option):
    sets_asset = asset()
    if sets_asset is None:
        return None
    for index in range(sets_asset.get_num_variant_sets()):
        variant_set = sets_asset.get_variant_set(index)
        if str(variant_set.get_display_text()) != title:
            continue
        for number in range(variant_set.get_num_variants()):
            variant = variant_set.get_variant(number)
            if str(variant.get_display_text()) == option:
                return variant
    return None


def switch(title, option):
    """One action: put one option of one list on. Returns True when the option exists."""
    variant = _variant(title, option)
    if variant is None:
        return False
    variant.switch_on()
    return True


def state(csv_path):
    """Read-only. For each list, how many of its surfaces show the Revit material, the candidate, or
    something else, in the level as it is now."""
    found, _ = classify(csv_path)
    result = {}
    for key, title in SETS:
        counts = collections.Counter()
        for actor, component, slot, revit, candidate, category in found[key]:
            shown = component.get_material(slot)
            path = shown.get_path_name().split(".")[0] if shown is not None else ""
            counts["revit" if path == revit else "candidate" if path == candidate else "other"] += 1
        result[title] = dict(counts)
    return result


def clear_overrides(csv_path):
    """Puts every surface of the three lists back to no override at all (the imported state), so that
    the unit levels are as they were before any option was tried. Returns the number put back."""
    found, _ = classify(csv_path)
    count = 0
    for entries in found.values():
        for actor, component, slot, revit, candidate, category in entries:
            overrides = list(component.get_editor_property("override_materials"))
            if slot < len(overrides) and overrides[slot] is not None:
                component.set_material(slot, None)
                count += 1
    return count
