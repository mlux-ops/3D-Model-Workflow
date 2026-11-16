"""Phase 11: put back every editor setting the renders of J7 and J9 changed for the session, and read them back.
Run after the last render (refuses while one runs). Complements seq_end.py, which left the pre-exposure at 7:

    Revit's ground slab and massing       shown again (they were hidden in the editor only, never saved)
    sg.GlobalIlluminationQuality,
    sg.ReflectionQuality, sg.ShadowQuality  3, the level read before the first render of J7 (05:02)
    r.RayTracing.Nanite.MaxAppendInstances  10,000, the engine's value (raised for the path-traced frames)
    r.EyeAdaptation.CachedLightingPreExposure  4, the project's value read at 05:02 (7 during the renders)
    on-screen messages                     on again (EnableAllScreenMessages; there is no read-back for this one)
    level viewport real-time drawing       on, the editor's normal state (the render tool switched it on; the state
                                           before 00:09 was not recorded)
    r.RayTracing.Nanite.Mode               never changed; must read 0
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

if unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering():
    raise RuntimeError("a render is running; nothing put back")
out = {}
try:
    out["stand_ins_shown"] = wt._stand_ins(False)
except Exception as error:  # the level may be an empty one; then there is nothing to show
    out["stand_ins_shown"] = "not in this level: %s" % error
for name in ("sg.GlobalIlluminationQuality", "sg.ReflectionQuality", "sg.ShadowQuality"):
    out[name] = wt.cvar(name, 3)
out[wt.APPEND] = wt.cvar(wt.APPEND, wt.APPEND_DEFAULT)
out["r.EyeAdaptation.CachedLightingPreExposure"] = wt.cvar("r.EyeAdaptation.CachedLightingPreExposure", 4)
unreal.SystemLibrary.execute_console_command(wl.world(), "EnableAllScreenMessages")
out["screen_messages"] = "EnableAllScreenMessages sent"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_viewport_realtime(True)
out["viewport_realtime"] = bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_get_viewport_realtime()) \
    if hasattr(unreal.LevelEditorSubsystem, "editor_get_viewport_realtime") else "set on (no read-back in this version)"
out["r.RayTracing.Nanite.Mode"] = wt.cvar(wt.NANITE_MODE)
out["dirty"] = wl.dirty()
json.dumps(out, default=str)
