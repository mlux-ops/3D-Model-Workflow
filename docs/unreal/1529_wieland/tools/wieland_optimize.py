"""Phase 9: the changes of the optimization phase, made inside the Unreal editor's Python.

Every change is made on an asset of this project's own folders (never on an asset Datasmith created, never on
/Game/Wieland/R15_Landscape/L_R15_Production) and is saved by name with save_levels(); nothing here uses "Save All".

    import wieland_optimize as wo
    wo.volume_settings("LGT_Exposure_Outdoors", {"mega_lights": True})    # set on a post-process volume, with its override flag
    wo.save_levels(["/Game/Wieland1529/Lighting/L_Light_SummerAfternoon"])
"""

import json

import unreal

LIGHTING_LEVEL = "/Game/Wieland1529/Lighting/L_Light_SummerAfternoon"
OUTDOOR_VOLUME = "LGT_Exposure_Outdoors"
# Settings of a post-process volume whose override flag is not "override_" + name.
OVERRIDE_NAMES = {"mega_lights": "override_b_mega_lights"}


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def level_of(actor):
    return actor.get_outer().get_outermost().get_name()


def dirty():
    """Names of the packages with unsaved changes."""
    return sorted([p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
                  + [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()])


def volume(label):
    for actor in actors():
        if isinstance(actor, unreal.PostProcessVolume) and actor.get_actor_label() == label:
            return actor
    raise RuntimeError("no post-process volume labelled " + label)


def volume_settings(label, values=None, clear=()):
    """Set (with the override flag on) or clear (override flag off) settings of one post-process volume of the
    lighting level. Returns what the volume holds for those settings afterwards."""
    actor = volume(label)
    if level_of(actor) != LIGHTING_LEVEL:
        raise RuntimeError("%s is in %s, not in the lighting level" % (label, level_of(actor)))
    settings = actor.get_editor_property("settings")
    for name, value in (values or {}).items():
        settings.set_editor_property(OVERRIDE_NAMES.get(name, "override_" + name), True)
        settings.set_editor_property(name, value)
    for name in clear:
        settings.set_editor_property(OVERRIDE_NAMES.get(name, "override_" + name), False)
    if values or clear:
        actor.modify()
        actor.set_editor_property("settings", settings)
    settings = actor.get_editor_property("settings")
    out = {}
    for name in list(values or {}) + list(clear):
        out[name] = [bool(settings.get_editor_property(OVERRIDE_NAMES.get(name, "override_" + name))),
                     str(settings.get_editor_property(name))]
    return out


def save_levels(packages):
    """Save the named level packages, and only those. Refuses the production landscape level."""
    saved = {}
    for name in packages:
        if "L_R15_Production" in name:
            raise RuntimeError("refused: " + name)
        package = unreal.find_package(name)
        if package is None:
            saved[name] = "not loaded"
            continue
        saved[name] = bool(unreal.EditorLoadingAndSavingUtils.save_packages([package], True))
    return {"saved": saved, "still_unsaved": dirty()}


def report(value):
    return json.dumps(value, default=str)
