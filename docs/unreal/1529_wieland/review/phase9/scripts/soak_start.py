import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import phase9_profile_m7 as m7
# Phase 9, step 9.11: start the soak (FOLDER, LOOPS and CSV_EVERY are set by the line the caller puts in front).
if not m7._W.get("active"):
    importlib.reload(m7)
M7 = T.rsplit("/", 1)[0] + "/profiles/2026-11-13_M7"
r = m7.soak_start(M7 + "/" + FOLDER, loops=LOOPS, csv_every=CSV_EVERY, note="final state of Phase 9: changes 1 and 2")
json.dumps(r)
