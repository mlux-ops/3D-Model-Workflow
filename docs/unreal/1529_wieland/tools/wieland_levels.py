"""Phase 6, step 6.8: the interior levels of the 1529 N. Wieland scene. Runs inside the Unreal editor.

The Datasmith level L_Building is never changed or saved here. It is copied as new level assets,
one for the common parts ("shell") and one for each of the four units. In each copy the objects
of the other groups are deleted, the recorded mesh swaps are applied and the copy is saved by
name. A new top level then loads the surroundings, the shell and the unit levels.

After a Revit reimport the copies are stale: run plan(), duplicate(), trim() for each group and
make_master() again (see phase6_results.md, "How to resume").

Frame of the level: origin at the lot's south-west corner, north is -X, east is -Y, centimetres.
"""

import csv

import unreal

SOURCE_LEVEL = "/Game/Wieland1529/Building/L_Building"
SOURCE_MASTER = "/Game/Wieland1529/L_Site_M2"
MASTER_LEVEL = "/Game/Wieland1529/L_Site_M4"
LEVEL_FOLDER = "/Game/Wieland1529/Interiors/Levels"
UNIT_GROUPS = ("NorthTriplex", "NorthPenthouse", "SouthTriplex", "SouthPenthouse")
GROUPS = ("Shell",) + UNIT_GROUPS
DROP = "Dropped"  # the Datasmith scene object: kept in L_Building only, so a reimport never reaches a copy
TAG_UNIT = "W1529.Unit."
PARTY_X = -754.38
PENTHOUSE_Z = 853.4  # finished floor of the 3rd floor: the penthouse starts here
# Categories that stand inside one unit even when Phase 4 could not tell (see plan()).
MOVABLE = ("Casework", "Furniture", "Furniture Systems", "Plumbing Fixtures", "Specialty Equipment", "Lighting Fixtures",
           "Light Source", "Generic Models", "Stairs", "Railings", "Landings", "Supports", "Doors", "Electrical Fixtures",
           "Electrical Equipment", "Mechanical Equipment", "Runs", "Top Rails", "Handrails", "Stringers")
PLAN_HEAD = ["actor_name", "label", "class", "category", "phase4_unit", "level_group", "reason",
             "x_min", "y_min", "z_min", "x_max", "y_max", "z_max"]


def level_path(group):
    return "%s/L_W1529_%s" % (LEVEL_FOLDER, group)


def _world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def _actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def _level_name(actor):
    return actor.get_outer().get_outer().get_name()


def _unit_tag(actor):
    for tag in actor.tags:
        text = str(tag)
        if text.startswith(TAG_UNIT):
            return text[len(TAG_UNIT):]
    return ""


def _metadata(actor):
    data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
    if data is None:
        return {}
    values = data.get_editor_property("metadata") or {}
    return {str(key): str(value) for key, value in values.items()}


def _category(actor):
    category = _metadata(actor).get("Element*Category")
    if category:
        return category
    try:
        layers = [str(layer) for layer in actor.get_editor_property("layers")]
    except Exception:
        layers = []
    return layers[0] if layers else ""


def mesh_box(actor):
    """Extent of the actor's own meshes, or None. The actor's anchor point and editor icon are left out:
    Datasmith puts the anchor of some families at Revit's project base point, far from the geometry."""
    box = None
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        if component.static_mesh is None:
            continue
        origin, extent, _ = unreal.SystemLibrary.get_component_bounds(component)
        this = (origin.x - extent.x, origin.y - extent.y, origin.z - extent.z,
                origin.x + extent.x, origin.y + extent.y, origin.z + extent.z)
        box = this if box is None else (min(box[0], this[0]), min(box[1], this[1]), min(box[2], this[2]),
                                        max(box[3], this[3]), max(box[4], this[4]), max(box[5], this[5]))
    return box


def _own_box(actor):
    box = mesh_box(actor)
    if box is not None:
        return box, "mesh"
    if isinstance(actor, unreal.Light):
        p = actor.get_actor_location()
        return (p.x, p.y, p.z, p.x, p.y, p.z), "light"
    return None, ""


def _unit_of_box(box):
    """The unit a box stands in, or None when it crosses the party line or the 3rd floor."""
    if box[3] <= PARTY_X + 30.0:
        half = "North"
    elif box[0] >= PARTY_X - 30.0:
        half = "South"
    else:
        return None
    if box[2] >= PENTHOUSE_Z - 40.0:
        return half + "Penthouse"
    if box[5] <= PENTHOUSE_Z + 5.0:
        return half + "Triplex"
    return None


def plan(out_csv):
    """Read-only: decide the level of every object of L_Building and write the list.

    A unit object goes to its unit's level. A common or site object goes to the shell, except
    where it is a fitting or fixture whose mesh lies wholly inside one unit: Phase 4 measured
    such objects by an extent that included the anchor point, which for some families lies at
    Revit's project base point, and so marked them as site or common.
    """
    actors = [a for a in _actors() if _level_name(a) == "L_Building"]
    by_name = {a.get_name(): a for a in actors}
    boxes = {}
    for actor in actors:
        boxes[actor.get_name()] = _own_box(actor)
    rows = []
    counts = {}
    for actor in actors:
        name = actor.get_name()
        class_name = actor.get_class().get_name()
        unit = _unit_tag(actor)
        category = _category(actor)
        box, kind = boxes[name]
        if box is None:
            # A holder without geometry takes the extent of what hangs under it.
            found = []
            stack = list(actor.get_attached_actors())
            while stack:
                child = stack.pop()
                child_box = boxes.get(child.get_name(), (None, ""))[0]
                if child_box is not None:
                    found.append(child_box)
                stack.extend(child.get_attached_actors())
            if found:
                box = (min(b[0] for b in found), min(b[1] for b in found), min(b[2] for b in found),
                       max(b[3] for b in found), max(b[4] for b in found), max(b[5] for b in found))
                kind = "children"
        if class_name == "DatasmithSceneActor":
            group, reason = DROP, "the Datasmith scene object stays in L_Building only"
        elif unit in UNIT_GROUPS:
            group, reason = unit, "Phase 4 unit"
        else:
            group, reason = "Shell", "Phase 4 %s" % (unit.lower() or "unmarked")
            if category in MOVABLE and box is not None:
                inside = _unit_of_box(box)
                if inside is not None:
                    group = inside
                    reason = "moved from %s: its %s lies wholly inside this unit" % (unit.lower() or "unmarked", kind)
        counts[group] = counts.get(group, 0) + 1
        shown = [round(v, 1) for v in box] if box is not None else [""] * 6
        rows.append([name, actor.get_actor_label(), class_name, category, unit, group, reason] + shown)
    del by_name
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(PLAN_HEAD)
        writer.writerows(rows)
    return {"objects": len(rows), "groups": counts,
            "moved": sum(1 for row in rows if row[6].startswith("moved"))}


def read_plan(plan_csv):
    with open(plan_csv, newline="", encoding="utf-8") as handle:
        return {row["actor_name"]: row for row in csv.DictReader(handle)}


def duplicate(group):
    """Copy L_Building as the level of one group and save the copy. Refuses to overwrite."""
    target = level_path(group)
    if unreal.EditorAssetLibrary.does_asset_exist(target):
        raise RuntimeError("refused: %s exists already" % target)
    made = unreal.EditorAssetLibrary.duplicate_asset(SOURCE_LEVEL, target)
    if made is None:
        raise RuntimeError("could not copy %s to %s" % (SOURCE_LEVEL, target))
    saved = unreal.EditorAssetLibrary.save_asset(target, False)
    return {"level": target, "saved": bool(saved)}


def open_level(path, discard=False):
    """Open a level in place of the open one. The editor refuses while the open level has unsaved
    changes; discard=True drops them (nothing is saved either way). Use it only after checking
    that the unsaved changes are the session's own work state."""
    policy = unreal.LevelEditorUnsavedChangesPolicy.DISCARD if discard else unreal.LevelEditorUnsavedChangesPolicy.FAIL
    return bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(path, policy))


def trim(group, plan_csv, swaps_csv=None):
    """With the copy of one group open on its own: delete the objects of the other groups, correct
    the unit mark of moved objects, apply the recorded mesh swaps. Does not save; see save_open()."""
    world_path = _world().get_path_name().split(".")[0]
    if world_path != level_path(group):
        raise RuntimeError("refused: the open level is %s, not %s" % (world_path, level_path(group)))
    rows = read_plan(plan_csv)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    remove, keep, unknown = [], [], []
    for actor in _actors():
        row = rows.get(actor.get_name())
        if row is None:
            unknown.append(actor.get_name())
        elif row["level_group"] == group:
            keep.append((actor, row))
        else:
            remove.append(actor)
    removed = len(remove)
    if remove:
        subsystem.destroy_actors(remove)
    retagged = 0
    worst = 0.0
    for actor, row in keep:
        if group in UNIT_GROUPS and row["phase4_unit"] != group:
            tags = [tag for tag in actor.tags if not str(tag).startswith(TAG_UNIT)]
            tags.append(unreal.Name(TAG_UNIT + group))
            actor.tags = tags
            retagged += 1
        box = mesh_box(actor)
        if box is not None and row["x_min"] != "":
            was = [float(row[key]) for key in ("x_min", "y_min", "z_min", "x_max", "y_max", "z_max")]
            worst = max(worst, max(abs(a - b) for a, b in zip(box, was)))
    swapped = 0
    unused = []
    if swaps_csv:
        import wieland_refine
        applied, unused = wieland_refine.swaps_from_csv(swaps_csv, [actor for actor, _ in keep])
        swapped = len(applied)
    return {"group": group, "kept": len(keep), "removed": removed, "not_in_plan": unknown, "retagged": retagged,
            "largest_shift_cm": round(worst, 3), "swapped_components": swapped}


def save_open(group):
    """Save the open level by name; refuses unless it is the copy of this group."""
    world_path = _world().get_path_name().split(".")[0]
    if world_path != level_path(group):
        raise RuntimeError("refused: the open level is %s, not %s" % (world_path, level_path(group)))
    return bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())


def sublevels():
    """Read-only: (package name, streaming class, loaded) of every sublevel of the open level."""
    world = _world()
    found = []
    for level in unreal.EditorLevelUtils.get_levels(world):
        package = level.get_outermost().get_name()
        if package == world.get_outermost().get_name():
            continue
        streaming = unreal.GameplayStatics.get_streaming_level(world, package)
        found.append((package, streaming.get_class().get_name() if streaming else "", True))
    return found


def make_master():
    """Make the top level L_Site_M4 as a copy of L_Site_M2 as saved, take L_Building out of it and
    add the shell (always loaded) and the four unit levels (loaded on request, so that step 6.8
    can load them by where the viewer stands). Saves L_Site_M4 by name. Refuses to overwrite."""
    if unreal.EditorAssetLibrary.does_asset_exist(MASTER_LEVEL):
        raise RuntimeError("refused: %s exists already" % MASTER_LEVEL)
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not editor.new_level_from_template(MASTER_LEVEL, SOURCE_MASTER):
        raise RuntimeError("could not make %s from %s" % (MASTER_LEVEL, SOURCE_MASTER))
    world = _world()
    if world.get_path_name().split(".")[0] != MASTER_LEVEL:
        raise RuntimeError("the open level is %s" % world.get_path_name())
    removed = []
    for level in unreal.EditorLevelUtils.get_levels(world):
        if level.get_outermost().get_name() == SOURCE_LEVEL:
            removed.append(bool(unreal.EditorLevelUtils.remove_level_from_world(level)))
    added = []
    for group in GROUPS:
        kind = unreal.LevelStreamingAlwaysLoaded if group == "Shell" else unreal.LevelStreamingDynamic
        streaming = unreal.EditorLevelUtils.add_level_to_world(world, level_path(group), kind)
        added.append((group, streaming is not None))
    persistent = world.get_outermost().get_name()
    editor.set_current_level_by_name(persistent.split("/")[-1])
    saved = bool(editor.save_current_level())
    return {"level": MASTER_LEVEL, "removed_L_Building": removed, "added": added, "saved": saved,
            "sublevels": sublevels()}


def census():
    """Read-only: objects per level and per unit mark in what is loaded now."""
    counts = {}
    for actor in _actors():
        key = (_level_name(actor), _unit_tag(actor) or "-")
        counts[key] = counts.get(key, 0) + 1
    return sorted((level, unit, n) for (level, unit), n in counts.items())
