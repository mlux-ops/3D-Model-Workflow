import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_optimize as wo
importlib.reload(wo)
# Phase 9, J2: MegaLights switched on by the unbound post-process volume of the lighting level (not saved here),
# and the project-wide console variable put back to the project's value, 0.
unreal.SystemLibrary.execute_console_command(wo.world(), "r.MegaLights.EnableForProject 0")
out = {"before_dirty": wo.dirty()}
out["volume"] = wo.volume_settings(wo.OUTDOOR_VOLUME, {"mega_lights": True})
out["cvar"] = unreal.SystemLibrary.get_console_variable_float_value("r.MegaLights.EnableForProject")
out["after_dirty"] = wo.dirty()
wo.report(out)
