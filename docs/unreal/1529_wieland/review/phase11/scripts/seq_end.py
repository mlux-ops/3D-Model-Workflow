"""Phase 11, step 11.2: put the editor back after animation renders, and read the settings back.

Shows Revit's ground slab and massing again, puts the engine's quality groups back to the level in
review/phase11/seq_end_job.json = {"quality": 3} (the level read before the first animation render), puts the
slots for tree leaves back to the engine's 10,000, and reads r.RayTracing.Nanite.Mode (never changed; must be 0).
The pre-exposure of Lumen's stored lighting is left at 7 for the session, because any later real-time picture at
the outdoor exposure needs it; it goes back to the project's 4 when the editor restarts.
"""
import sys, json, importlib
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
with open(BASE + "seq_end_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
if queue.is_rendering():
    raise RuntimeError("a render is running; nothing put back")
out = {"stand_ins_shown": wt._stand_ins(False)}
for name in ("sg.GlobalIlluminationQuality", "sg.ReflectionQuality", "sg.ShadowQuality"):
    out[name] = wt.cvar(name, int(job["quality"]))
out[wt.APPEND] = wt.cvar(wt.APPEND, wt.APPEND_DEFAULT)
out["nanite_mode"] = wt.cvar(wt.NANITE_MODE)
out["pre_exposure"] = wt.cvar("r.EyeAdaptation.CachedLightingPreExposure")
out["dirty"] = wl.dirty()
json.dumps(out, default=str)
