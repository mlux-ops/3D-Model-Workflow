"""Phase 11, step 11.2: start the render of a run of frames of one camera move, and return at once.

Reads review/phase11/seq_render_job.json:
    {"asset": "SEQ_W1529_Triplex", "name": "triplex", "folder": "D:/.../animation_frames/triplex",
     "start": 0, "end": 150,            frames start to end-1 (the engine's custom range excludes its end frame)
     "tier": "rt" or "pt", "samples": 8, "warm_up_frames": 64, "width": 3840, "height": 2160,
     "anti_aliasing": "TSR" or "NONE" or null (null leaves the project's own method),
     "quality": [4, 4, 4]}              levels of the engine's quality groups for bounced light, reflections, shadows
Files are named <name>.<frame, four digits>.png. The render runs on the editor's own ticks through Movie Render
Graph's quick render of a level sequence, in the editor's world (no play session), as the stills were made.

Before starting it puts the editor in the state of the animation and reads it back:
r.RayTracing.Nanite.Mode must read 0 (it is never changed here); Revit's ground slab and massing are hidden for
the session; on-screen messages are off; Lumen's stored lighting is kept at a higher pre-exposure so that the
bright outdoor frames are not clipped (r.EyeAdaptation.CachedLightingPreExposure 7); for the real-time tier the
engine's quality groups for bounced light, reflections and shadows are set to the job's levels (4, "cinematic",
is the highest; 3 is "epic", the level the walk-through uses); for the path-traced tier the slots for tree leaves are raised as for the stills.
seq_end.py puts all of that back.
"""
import sys, json, os, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_interiors as wi
import wieland_truth as wt
for m in (wl, wi, wt):
    importlib.reload(m)

BASE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/"
QUALITY = ("sg.GlobalIlluminationQuality", "sg.ReflectionQuality", "sg.ShadowQuality")
PRE_EXPOSURE = "r.EyeAdaptation.CachedLightingPreExposure"

with open(BASE + "seq_render_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
if queue.is_rendering():
    raise RuntimeError("a render is already running")
if wt.cvar(wt.NANITE_MODE) != 0:
    raise RuntimeError("r.RayTracing.Nanite.Mode does not read 0; not rendering")
path_traced = job.get("tier", "rt") == "pt"
sequence = unreal.EditorAssetLibrary.load_asset("/Game/Wieland1529/Delivery/" + job["asset"])
if sequence is None:
    raise RuntimeError("no sequence " + job["asset"])
folder = job["folder"].replace("\\", "/")
os.makedirs(folder, exist_ok=True)

state = {"stand_ins_hidden": wt._stand_ins(True)}
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
state[PRE_EXPOSURE] = wt.cvar(PRE_EXPOSURE, 7)
if path_traced:
    state[wt.APPEND] = wt.cvar(wt.APPEND, wt.APPEND_FOR_TREES)
else:
    levels = job.get("quality") or [4, 4, 4]
    for name, level in zip(QUALITY, levels):
        state[name] = wt.cvar(name, int(level))
editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor.editor_set_viewport_realtime(True)
unreal.SystemLibrary.execute_console_command(wl.world(), "viewmode lit")

settings = unreal.MovieGraphQuickRenderModeSettings()
settings.set_configuration_type(unreal.MovieGraphQuickRenderConfigurationType.BASIC)
settings.set_editor_property("post_render_behavior", unreal.MoviePipelinePostRenderActionType.DO_NOTHING)
settings.set_editor_property("execution_mode", unreal.MovieGraphQuickRenderExecutionMode.EDITOR_WORLD)
settings.set_editor_property("level_sequence_override", sequence)
settings.set_editor_property("frame_range_type", unreal.MovieGraphQuickRenderFrameRangeType.CUSTOM)
settings.set_editor_property("override_custom_start_frame", True)
settings.set_editor_property("custom_start_frame", int(job["start"]))
settings.set_editor_property("override_custom_end_frame", True)
settings.set_editor_property("custom_end_frame", int(job["end"]))
basic = settings.get_basic_config()


def override(prop, value, flag=None):
    basic.set_editor_property(flag or ("override_" + prop), True)
    basic.set_editor_property(prop, value)


override("use_path_traced_renderer", path_traced, "override_b_use_path_traced_renderer")
override("use_deferred_renderer", not path_traced, "override_b_use_deferred_renderer")
if path_traced:
    override("path_traced_spatial_sample_count", int(job.get("samples", 1024)))
else:
    override("deferred_spatial_sample_count", int(job.get("samples", 8)))
    if job.get("anti_aliasing"):
        override("deferred_anti_aliasing_method", getattr(unreal.AntiAliasingMethod, "AAM_" + job["anti_aliasing"]))
override("temporal_sample_count", 1)
override("num_warm_up_frames", int(job.get("warm_up_frames", 64)))
override("output_resolution", unreal.MovieGraphLibrary.named_resolution_from_size(int(job.get("width", 3840)), int(job.get("height", 2160))))
override("output_directory", unreal.DirectoryPath(path=folder))
override("file_name_format", job["name"] + ".{frame_number}")
state["anti_aliasing"] = str(basic.get_editor_property("deferred_anti_aliasing_method"))
state["denoiser"] = str(basic.get_editor_property("path_traced_denoiser_type"))
quick = unreal.get_editor_subsystem(unreal.MovieGraphQuickRenderSubsystem)
quick.begin_quick_render(unreal.MovieGraphQuickRenderMode.CURRENT_SEQUENCE, settings)
state["rendering"] = bool(queue.is_rendering())
state["nanite_mode"] = wt.cvar(wt.NANITE_MODE)
state["range"] = [job["start"], job["end"]]
json.dumps(state, default=str)
