import sys
import importlib
sys.dont_write_bytecode = True
TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_site as ws
importlib.reload(ws)
cvar = unreal.SystemLibrary.get_console_variable_int_value("r.Material.UseShaderCompilationParameters")
quality = unreal.SystemLibrary.get_console_variable_int_value("sg.ViewDistanceQuality")
result = {"engine": unreal.SystemLibrary.get_engine_version(), "world": ws.world_path(), "levels": ws.levels(),
          "objects": len(ws.actors()), "dirty": ws.dirty(), "UseShaderCompilationParameters": cvar,
          "sg.ViewDistanceQuality": quality}
result
