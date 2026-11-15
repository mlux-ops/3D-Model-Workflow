import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import phase9_profile_m7 as m7
importlib.reload(m7)
M7 = T.rsplit("/", 1)[0] + "/profiles/2026-11-13_M7"
r = await m7.run(M7 + "/P20R2", "P20R2", parts=("exterior", "roofdeck"), skip_first_walk=True,
                 note="Phase 20 round 2: Hancock rebuilt, 10 landmark meshes and a spire added, 21 instances set from photographs")
json.dumps(r)
