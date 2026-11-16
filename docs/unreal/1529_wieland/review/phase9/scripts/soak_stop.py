import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import phase9_profile_m7 as m7
import wieland_profile as wp
# Phase 9, step 9.11: stop the soak early (owner's decision of 2026-11-13 07:06) and put every setting back.
before = m7.soak_status()
out = {"before": before}
if before["soak"].get("active"):
    out["cancel"] = wp.cancel()
if before["watching"] or before["soak"].get("active"):
    out["end"] = m7.soak_end()
out["after"] = m7.soak_status()
json.dumps(out)
