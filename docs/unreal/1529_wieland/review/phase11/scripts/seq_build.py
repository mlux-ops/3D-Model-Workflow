"""Phase 11, step 11.2: make the level sequence of one camera move from its frame-by-frame file. A NEW asset.

Reads review/phase11/seq_job.json = {"move": "triplex", "asset": "SEQ_W1529_Triplex"} and
review/phase11/paths/<move>_move.json (made by move_build.py). Creates /Game/Wieland1529/Delivery/<asset>:
30 pictures a second, frames 0 to 899, one camera that the sequence itself creates while it plays (a "spawnable";
nothing is added to any level), a key on every frame for the camera's place and direction, a camera cut over the
whole range, and a key on every frame for the exposure.

Exposure: the camera carries a fixed manual exposure for outdoors (BASE_EV at ISO 100) and the sequence keys the
camera's exposure compensation to BASE_EV minus the frame's exposure value, so that each frame is exposed at the
value move_build.py gave it. (A bounded exposure volume is not applied to a rendered view, see wieland_truth.py.)

Saves the new asset only. Refuses to run if the asset already exists.
"""
import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
importlib.reload(wt)

BASE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/"
FOLDER = "/Game/Wieland1529/Delivery"
BASE_EV = 14.644
LABEL = "TEMP_sequence_camera"
MOTION_BLUR = 0.2   # the engine's 0.5 smears a walk at 1.9 m/s through rooms; 0.2 keeps a trace of it

with open(BASE + "seq_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
with open(BASE + "paths/%s_move.json" % job["move"], "r", encoding="utf-8") as handle:
    move = json.load(handle)
frames = move["frames"]
path = FOLDER + "/" + job["asset"]
if unreal.EditorAssetLibrary.does_asset_exist(path):
    raise RuntimeError("the asset %s already exists; this tool does not overwrite" % path)

tools = unreal.AssetToolsHelpers.get_asset_tools()
sequence = tools.create_asset(job["asset"], FOLDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
sequence.set_display_rate(unreal.FrameRate(move["fps"], 1))
sequence.set_playback_start(0)
sequence.set_playback_end(len(frames))

# a camera in the level only long enough to hand its settings to the sequence
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
first = frames[0]
camera = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(*first["loc"]),
                                       unreal.Rotator(pitch=first["rot"][0], yaw=first["rot"][1], roll=first["rot"][2]))
camera.set_actor_label(LABEL)
camera.tags = [wl.TAG_TEMP]
component = camera.get_cine_camera_component()
filmback = component.get_editor_property("filmback")
filmback.set_editor_property("sensor_width", 36.0)
filmback.set_editor_property("sensor_height", 20.25)
component.set_editor_property("filmback", filmback)
lens = component.get_editor_property("lens_settings")
lens.set_editor_property("min_focal_length", 24.0)
lens.set_editor_property("max_focal_length", 24.0)
component.set_editor_property("lens_settings", lens)
component.set_editor_property("current_focal_length", 24.0)
focus = component.get_editor_property("focus_settings")
focus.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
component.set_editor_property("focus_settings", focus)
# A cine camera puts its own aperture into the exposure (f/2.8 unless told), so it is set to the f/8 the lighting
# level's exposure is written for; found on the first test frames, which came out three stops too bright.
lens.set_editor_property("min_f_stop", 1.2)
lens.set_editor_property("max_f_stop", 22.0)
component.set_editor_property("lens_settings", lens)
component.set_editor_property("current_aperture", 8.0)
wt._camera_exposure(component, BASE_EV)
settings = component.get_editor_property("post_process_settings")
settings.set_editor_property("override_auto_exposure_bias", True)
settings.set_editor_property("auto_exposure_bias", BASE_EV - first["ev"])
settings.set_editor_property("override_motion_blur_amount", True)
settings.set_editor_property("motion_blur_amount", MOTION_BLUR)
component.set_editor_property("post_process_settings", settings)
field_of_view = component.get_editor_property("field_of_view")

camera_binding = sequence.add_spawnable_from_instance(camera)
# add_possessable also makes an empty binding for the level camera itself; it is removed again below
component_binding = sequence.add_possessable(component)
component_binding.set_parent(camera_binding)
camera_binding.set_display_name("W1529_Camera")
for binding in list(sequence.get_bindings()):
    if str(binding.get_display_name()) == LABEL and not binding.get_tracks() and not binding.get_child_possessables():
        binding.remove()
actors.destroy_actor(camera)

LINEAR = unreal.MovieSceneKeyInterpolation.LINEAR
transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
transform_section = transform_track.add_section()
transform_section.set_range(0, len(frames))
channels = transform_section.get_all_channels()
names = [str(channel.get_name()) for channel in channels]
for frame in frames:
    time = unreal.FrameNumber(frame["f"])
    pitch, yaw, roll = frame["rot"]
    for index, value in enumerate((frame["loc"][0], frame["loc"][1], frame["loc"][2], roll, pitch, yaw)):
        channels[index].add_key(time, value, 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, LINEAR)

exposure_track = component_binding.add_track(unreal.MovieSceneFloatTrack)
exposure_track.set_property_name_and_path("AutoExposureBias", "PostProcessSettings.AutoExposureBias")
exposure_section = exposure_track.add_section()
exposure_section.set_range(0, len(frames))
exposure_channel = exposure_section.get_all_channels()[0]
for frame in frames:
    exposure_channel.add_key(unreal.FrameNumber(frame["f"]), BASE_EV - frame["ev"], 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, LINEAR)

cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
cut_section = cut_track.add_section()
cut_section.set_range(0, len(frames))
cut_section.set_camera_binding_id(sequence.get_binding_id(camera_binding))

saved = bool(unreal.EditorAssetLibrary.save_asset(path, False))
json.dumps({"asset": sequence.get_path_name(), "saved": saved, "frames": len(frames), "field_of_view": round(field_of_view, 2),
            "transform_channels": names[:6], "transform_keys": [len(channel.get_keys()) for channel in channels[:6]],
            "exposure_keys": len(exposure_channel.get_keys()),
            "playback": [sequence.get_playback_start(), sequence.get_playback_end()],
            "bindings": [str(binding.get_display_name()) for binding in sequence.get_bindings()], "dirty": wl.dirty()}, default=str)
