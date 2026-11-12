import sys
sys.dont_write_bytecode = True
TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_site as ws
out = TOOLS.replace("/tools", "/review/phase7/old_level_readback.json")
result = ws.inspect_level(ws.OLD_LEVEL, out)
result["dirty_after"] = ws.dirty()
result
