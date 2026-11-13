import sys, json, os
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
# Phase 10, station S8: the plan view. A temporary camera straight down over the lot centre, 120 m by 120 m
# on the ground, true north up (the level's -X is 1.18 degrees east of true north), real-time renderer,
# 2160 by 2160 (5.6 cm to the pixel). The camera is removed afterwards; nothing is saved.
# The first try used a parallel-projection camera and gave a black picture (the quick render does not draw
# the scene for such a camera). This one stands 2 km up with a 3.44 degree lens instead: over 60 m from the
# centre a roof 12 m high is drawn 0.36 m further out than its foot, which is noted on the sheet.
OUT = T.rsplit("/", 1)[0] + "/review/phase10/realtime/S8"
os.makedirs(OUT, exist_ok=True)
CENTRE = (-754.4, -1557.5)     # review/phase2/stations.csv, S8
HEIGHT = 200000.0
FOV = 3.4368            # 2 * atan(60 m / 2000 m)
YAW_TRUE_NORTH = 181.18
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
wt.end(restore_nanite=False)
location = unreal.Vector(CENTRE[0], CENTRE[1], HEIGHT)
rotation = unreal.Rotator(pitch=-90.0, yaw=YAW_TRUE_NORTH, roll=0.0)
subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera = subsystem.spawn_actor_from_class(unreal.CameraActor, location, rotation)
camera.set_actor_label(wt.CAMERA_LABEL)
camera.tags = [wl.TAG_TEMP, "S8"]
component = camera.camera_component
component.set_editor_property("field_of_view", FOV)
component.set_editor_property("constrain_aspect_ratio", True)
component.set_editor_property("aspect_ratio", 1.0)
ev100 = wl.read_exposure(wt.EXPOSURE_OUTDOORS)["ev100"]
wt._camera_exposure(component, ev100)
editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor.pilot_level_actor(camera)
editor.editor_set_viewport_realtime(True)
unreal.SystemLibrary.execute_console_command(wl.world(), "viewmode lit")
hidden = wt._stand_ins(True)
out = {"ev100": ev100, "stand_ins_hidden": hidden}
try:
    await wl.wait_frames(25.0)
    record = await wt.render("S8", "rt", OUT, 2160, 2160, warm_up_frames=64)
    out["record"] = record
finally:
    out["end"] = wt.end()
json.dumps(out, default=str)
