"""Phase 11, read-only: the scene state the stills and the animation need: hotel option, sun, exposure, settings."""
import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_hotel as wh
importlib.reload(wh)
cv = unreal.SystemLibrary.get_console_variable_float_value
json.dumps({"hotel": wh.state(), "sun": wl.read_sun(), "nanite_mode": cv("r.RayTracing.Nanite.Mode"),
            "append": cv("r.RayTracing.Nanite.MaxAppendInstances"), "pre_exposure": cv("r.EyeAdaptation.CachedLightingPreExposure"),
            "gi_quality": cv("sg.GlobalIlluminationQuality"), "dirty": wl.dirty()}, default=str)
