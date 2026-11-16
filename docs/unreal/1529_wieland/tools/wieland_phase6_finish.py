"""Phase 6 finish (after Phase 7): bring the Phase 6 top level L_Site_M4 up to the site as it now stands.

Runs inside the Unreal editor's Python, next to wieland_site (ws) and wieland_levels.

Phase 7 changed L_Site_M2: it added four levels (the earlier detailed neighbour buildings, the site ground,
the distant-city stand-in and the trees) and made two Revit site objects not visible in L_Building.
L_Site_M4 and its shell level are copies from before that, so they showed neither. Here:
  - the four Phase 7 levels are added to L_Site_M4 as always loaded (nothing in them is changed);
  - the two Revit site objects in the shell copy are made not visible, as an override on the placed object.
Nothing that Datasmith created is edited: the shell level is a Phase 6 copy, and the mesh assets are not touched.
"""

import csv
import os

import unreal

import wieland_levels as wl
import wieland_site as ws

SITE_LEVELS = (
    ("/Game/Wieland1529/Surroundings/L_Surroundings_R15", "the earlier detailed neighbour buildings (the default view of Phase 7)"),
    ("/Game/Wieland1529/Site/L_SiteWorks", "the site ground: roadway, kerbs, sidewalks, paving, lawn"),
    ("/Game/Wieland1529/Surroundings/L_FarCity", "the distant-city stand-in"),
    ("/Game/Wieland1529/Vegetation/L_Vegetation", "the 34 trees"),
)
SHELL = wl.level_path("Shell")
REVIT_SITE_OBJECTS = ("Generic_Models_SURROUNDING_BUILDINGS_SURROUNDING_BUILDINGS", "Site_GRADE_GRADE")
RECORD = ws.REVIEW.replace("/phase7", "/phase6") + "/finish/m4_fixes.csv"


def _require_master():
    if ws.world_path() != wl.MASTER_LEVEL:
        raise RuntimeError("the open level is %s, not %s" % (ws.world_path(), wl.MASTER_LEVEL))


def add_site_levels(only=None):
    """Adds the Phase 7 levels that L_Site_M4 does not load yet, as always loaded."""
    _require_master()
    have = ws.levels()
    out = []
    for path, what in SITE_LEVELS:
        if only is not None and path not in only:
            continue
        if path in have:
            out.append((path, "there already"))
            continue
        streaming = unreal.EditorLevelUtils.add_level_to_world(ws.world(), path, unreal.LevelStreamingAlwaysLoaded)
        out.append((path, "added" if streaming is not None else "FAILED"))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(wl.MASTER_LEVEL.split("/")[-1])
    return out


def _shell_objects():
    return {a.get_actor_label(): a for a in ws.actors()
            if a.get_actor_label() in REVIT_SITE_OBJECTS and ws.level_of(a) == SHELL}


def hide_revit_in_shell(labels=None, visible=False):
    """Makes the mesh of the named Revit site objects in the shell copy visible or not (children keep their own state)."""
    _require_master()
    out = []
    for label, actor in _shell_objects().items():
        if labels is not None and label not in labels:
            continue
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            if component.get_owner() != actor:
                continue
            before = bool(component.get_editor_property("visible"))
            if before != bool(visible):
                component.modify()
                component.set_visibility(bool(visible), False)
            out.append((label, before, bool(component.get_editor_property("visible"))))
    return out


def state():
    """Read-only: what L_Site_M4 loads and shows now."""
    _require_master()
    shown = {label: [bool(c.get_editor_property("visible")) for c in actor.get_components_by_class(unreal.StaticMeshComponent)
                     if c.get_owner() == actor] for label, actor in _shell_objects().items()}
    acts = ws.actors()
    return {"levels": ws.levels(), "revit_site_objects_visible": shown, "surroundings": ws.visible_state(),
            "trees": sum(1 for a in acts if any(str(t) == "W1529.Tree" for t in a.tags)),
            "streaming_boxes": sum(1 for a in acts if a.get_actor_label().startswith("SV_W1529_")),
            "baseboards": sum(1 for a in acts if a.get_actor_label().startswith("GEN_Baseboard_")),
            "stand_ins": sum(1 for a in acts if a.get_actor_label().startswith("PH_")),
            "marked_as_changed": ws.dirty()}


def record(rows):
    os.makedirs(os.path.dirname(RECORD), exist_ok=True)
    with open(RECORD, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["what", "object_or_level", "in_level", "before", "after", "how", "to_undo"])
        writer.writerows(rows)
    return len(rows)


def save():
    """Saves L_Site_M4 and the shell level by name (both refuse while temporary cameras or lamps are in them)."""
    _require_master()
    return {"L_Site_M4": wl.save_master(), "L_W1529_Shell": wl.save_unit_level("Shell"), "marked_as_changed": ws.dirty()}
