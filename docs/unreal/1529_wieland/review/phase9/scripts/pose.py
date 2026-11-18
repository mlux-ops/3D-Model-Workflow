import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import phase9_profile_m7 as m7
# Phase 9: hold the camera at a station under tier conditions (or put everything back), as asked in
# review/phase9/scripts/pose.json = {"station": "D2" or "", "cvars": {...}, "commands": ["console command", ...]}.
HERE = T.rsplit("/", 1)[0] + "/review/phase9/scripts"
with open(HERE + "/pose.json", encoding="utf-8") as handle:
    job = json.load(handle)
if job.get("station"):
    out = m7.pose(job["station"], dict(m7.TIER, **job.get("cvars", {})))
else:
    out = m7.unpose()
for command in job.get("commands", []):
    unreal.SystemLibrary.execute_console_command(m7._world(), command)
json.dumps(out, default=str)
