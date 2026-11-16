import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
ROOT = T.rsplit("/", 1)[0]
P9 = ROOT + "/review/phase9"
M7 = ROOT + "/profiles/2026-11-13_M7"
