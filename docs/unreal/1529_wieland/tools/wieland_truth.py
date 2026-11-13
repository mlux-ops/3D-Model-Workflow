"""Phase 8, steps 8.7 and 8.8: one still of a station or design view, path traced (the ground truth) or
with the real-time renderer, both through tools/wieland_render.py so that the two share camera, size and
exposure.

Runs inside the Unreal editor's Python. The camera is a temporary camera actor that the viewport is locked
to ("piloting"), so the render takes the camera's view angle. Nothing here is saved to a level; the
temporary camera carries the tag that makes wieland_lighting.save() refuse to save while it exists.

    import wieland_truth as wt
    wt.begin("S1")                                  # camera, viewport, stand-ins hidden
    await wt.render("S1", "pt", folder, 3840, 2160)  # waits until the file is written
    wt.end()                                        # camera removed, stand-ins shown, Nanite mode back to 0
"""
import json
import os
import time

import unreal

import wieland_interiors as wi
import wieland_lighting as wl
import wieland_render

NANITE_MODE = "r.RayTracing.Nanite.Mode"
# Slots for the parts of Nanite assemblies (each Megaplant tree is one, with thousands of leaf parts) in the
# ray tracing scene. At the engine's 10,000 most leaves of the 34 trees are left out of a path-traced
# picture (trial at S2, review/phase8/ground_truth/trial/S2_tree_trials_sheet.jpg); 400,000 holds them all.
APPEND = "r.RayTracing.Nanite.MaxAppendInstances"
APPEND_DEFAULT = 10000
APPEND_FOR_TREES = 400000
CAMERA_LABEL = "TEMP_truth_camera"
FOV = 73.74  # 24 mm lens on a 36 mm wide frame, as at every station and design view
VIEWS = ("S1", "S2", "S3", "S4", "S5", "S6", "S9", "D1", "D2", "D3", "D4", "D5")


def view(name):
    """Location and rotation of a station (S...) or design view (D...)."""
    if name in wi.DESIGN_VIEWS:
        location, target = wi.DESIGN_VIEWS[name]
        return unreal.Vector(*location), wi.look_at(location, target)
    path = os.path.join(os.path.dirname(wl.REVIEW), "phase4", "stations", "station_cameras.json")
    with open(path, "r", encoding="utf-8") as handle:
        record = json.load(handle)["cameras"][name]
    rot = record["rot"]
    return unreal.Vector(*record["loc"]), unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2])


def cvar(name, value=None):
    if value is not None:
        unreal.SystemLibrary.execute_console_command(wl.world(), "%s %s" % (name, value))
    return unreal.SystemLibrary.get_console_variable_float_value(name)


EXPOSURE_VOLUMES = ("LGT_Exposure_Interior_LowerTo3rd", "LGT_Exposure_Interior_4th")
EXPOSURE_OUTDOORS = "LGT_Exposure_Outdoors"


def exposure_at(location):
    """The fixed exposure the lighting level gives a camera at this place: the interior volume that holds
    the point, else the outdoor one. Returns (label of the volume, exposure value at ISO 100)."""
    for label in EXPOSURE_VOLUMES:
        volume = wl.by_label(label)
        if volume is None:
            continue
        origin, extent = volume.get_actor_bounds(False)
        if (abs(location.x - origin.x) <= extent.x and abs(location.y - origin.y) <= extent.y
                and abs(location.z - origin.z) <= extent.z):
            return label, wl.read_exposure(label)["ev100"]
    return EXPOSURE_OUTDOORS, wl.read_exposure(EXPOSURE_OUTDOORS)["ev100"]


def _camera_exposure(component, ev100):
    """Quick Render does not apply a bounded exposure volume to the view (found at D3: the kitchen came out
    at the outdoor exposure in both renderers), so the temporary camera carries the same setting itself."""
    camera = wl.exposure_camera(ev100)
    settings = component.get_editor_property("post_process_settings")
    for name, value in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
                        ("auto_exposure_apply_physical_camera_exposure", True),
                        ("auto_exposure_bias", 0.0),
                        ("camera_iso", camera["iso"]),
                        ("camera_shutter_speed", camera["shutter_one_over_s"]),
                        ("depth_of_field_fstop", camera["fstop"])):
        settings.set_editor_property("override_" + name, True)
        settings.set_editor_property(name, value)
    component.set_editor_property("post_process_settings", settings)
    component.set_editor_property("post_process_blend_weight", 1.0)


def _stand_ins(hidden):
    count = 0
    for actor in wl.actors():
        if actor.get_actor_label() in wi.REVIT_STAND_INS:
            actor.set_is_temporarily_hidden_in_editor(hidden)
            count += 1
    return count


def begin(name):
    """Place the temporary camera at the view, lock the viewport to it, hide Revit's slab and massing."""
    end(restore_nanite=False)
    location, rotation = view(name)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    camera = subsystem.spawn_actor_from_class(unreal.CameraActor, location, rotation)
    camera.set_actor_label(CAMERA_LABEL)
    camera.tags = [wl.TAG_TEMP, name]
    component = camera.camera_component
    component.set_editor_property("field_of_view", FOV)
    component.set_editor_property("constrain_aspect_ratio", True)
    component.set_editor_property("aspect_ratio", 16.0 / 9.0)
    exposure_label, ev100 = exposure_at(location)
    _camera_exposure(component, ev100)
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor.pilot_level_actor(camera)
    editor.editor_set_viewport_realtime(True)
    unreal.SystemLibrary.execute_console_command(wl.world(), "viewmode lit")
    return {"view": name, "location": [round(v, 1) for v in (location.x, location.y, location.z)],
            "rotation": [round(v, 2) for v in (rotation.pitch, rotation.yaw, rotation.roll)],
            "exposure_from": exposure_label, "ev100": round(ev100, 3),
            "stand_ins_hidden": _stand_ins(True), "windows_restored": wl.window_restore()}


def end(restore_nanite=True):
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in list(wl.actors()):
        if actor.get_actor_label() == CAMERA_LABEL:
            editor.eject_pilot_level_actor()
            subsystem.destroy_actor(actor)
            removed += 1
    out = {"cameras_removed": removed, "stand_ins_shown": _stand_ins(False)}
    if restore_nanite:
        out["nanite_mode"] = cvar(NANITE_MODE, 0)
        out["append_instances"] = cvar(APPEND, APPEND_DEFAULT)
    return out


async def render(name, tier, folder, width=3840, height=2160, samples=None, play_in_editor=False,
                 warm_up_frames=None, nanite_mode=None, limit_seconds=900.0, suffix="", append_instances=None):
    """Render the view the viewport is locked to and wait for the file.

    tier "pt" is the Path Tracer (r.RayTracing.Nanite.Mode 2 unless given), tier "rt" the real-time
    renderer (mode left as found unless given). Returns the record of wieland_render.status() plus the
    Nanite mode in force and the seconds waited.
    """
    path_traced = tier == "pt"
    if nanite_mode is None and path_traced:
        nanite_mode = 2
    if nanite_mode is not None:
        cvar(NANITE_MODE, nanite_mode)
    if append_instances is None and path_traced:
        append_instances = APPEND_FOR_TREES
    if append_instances is not None and cvar(APPEND) != append_instances:
        cvar(APPEND, append_instances)
        await wl.wait_frames(3.0)
    if samples is None:
        samples = 1024 if path_traced else 1
    file_name = "%s_%s%s" % (name, "pathtraced" if path_traced else "realtime", suffix)
    target = os.path.join(folder, file_name + ".0000.png")
    if os.path.exists(target):
        os.remove(target)
    started = time.time()
    wieland_render.still(folder, file_name, width, height, path_traced=path_traced, samples=samples,
                         play_in_editor=play_in_editor, warm_up_frames=warm_up_frames)
    record = wieland_render.status()
    while time.time() - started < limit_seconds:
        await wl.wait_frames(1.0)
        record = wieland_render.status()
        if record.get("file_bytes") and not record.get("is_rendering"):
            break
    record["nanite_mode_during"] = cvar(NANITE_MODE)
    record["append_instances_during"] = cvar(APPEND)
    record["seconds_waited"] = round(time.time() - started, 1)
    record["view"] = name
    record["tier"] = tier
    return record
