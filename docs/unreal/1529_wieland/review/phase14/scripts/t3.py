import sys, json, importlib
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase14/scripts")
import p14
importlib.reload(p14)
unreal = p14.unreal
jobs = json.load(open(p14.OUT + "/scripts/t3_jobs.json"))
out = []
p14.camera("roofdeck")
for j in jobs:
    p14.look("roofdeck", yaw=j["yaw"], pitch=j["pitch"], loc=tuple(j["loc"]))
    s = p14.set_sun(j["day"], j["hour"])
    ev = j.get("ev") or p14.ev_for(s["height"])
    p14.set_ev(ev)
    ok = await p14.shoot(p14.FRAMES + "/test/" + j["name"] + ".png", settle=j.get("settle", 3.0))
    out.append([j["name"], ok, round(s["bearing"], 1), round(s["height"], 1), round(ev, 2)])
json.dumps(out)
