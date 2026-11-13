import sys, json, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
# Phase 10, station S8, one path-traced plan picture, in three calls so that the level can settle five minutes
# between placing the camera and rendering. The step is read from review/phase10/realtime/S8/pt_job.json:
#   {"step": "begin"}   place the same temporary camera as s8_plan.py; r.RayTracing.Nanite.Mode stays 0
#   {"step": "render"}  one picture, 2160 by 2160, Path Tracer, 1024 samples (mode 2 during the render only)
#   {"step": "end"}     camera removed, stand-ins shown, mode back to 0 and read back
OUT = T.rsplit("/", 1)[0] + "/review/phase10/realtime/S8"
with open(OUT + "/pt_job.json", "r", encoding="utf-8") as handle:
    step = json.load(handle)["step"]
CENTRE = (-754.4, -1557.5)
HEIGHT = 200000.0
FOV = 3.4368
YAW_TRUE_NORTH = 181.18
out = {"step": step}
if step == "begin":
    unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
    wt.end(restore_nanite=True)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    camera = subsystem.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(CENTRE[0], CENTRE[1], HEIGHT),
                                              unreal.Rotator(pitch=-90.0, yaw=YAW_TRUE_NORTH, roll=0.0))
    camera.set_actor_label(wt.CAMERA_LABEL)
    camera.tags = [wl.TAG_TEMP, "S8"]
    component = camera.camera_component
    component.set_editor_property("field_of_view", FOV)
    component.set_editor_property("constrain_aspect_ratio", True)
    component.set_editor_property("aspect_ratio", 1.0)
    out["ev100"] = wl.read_exposure(wt.EXPOSURE_OUTDOORS)["ev100"]
    wt._camera_exposure(component, out["ev100"])
    editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor.pilot_level_actor(camera)
    editor.editor_set_viewport_realtime(True)
    unreal.SystemLibrary.execute_console_command(wl.world(), "viewmode lit")
    out["stand_ins_hidden"] = wt._stand_ins(True)
elif step == "render":
    try:
        out["record"] = await wt.render("S8", "pt", OUT, 2160, 2160, samples=1024, warm_up_frames=64)
    finally:
        out["nanite_mode_after"] = wt.cvar(wt.NANITE_MODE, 0)
        out["append_after"] = wt.cvar(wt.APPEND, wt.APPEND_DEFAULT)
else:
    out["end"] = wt.end()
out["nanite_mode"] = wt.cvar(wt.NANITE_MODE)
json.dumps(out, default=str)
