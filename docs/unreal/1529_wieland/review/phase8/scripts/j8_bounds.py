import sys
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
FLOOR_Z = {"L": -152.4, "1": 203.2, "2": 528.3, "3": 853.4, "4": 1178.6, "R": 1524.0}
out = {}
lv = {}
for a in wl.actors():
    label = a.get_actor_label()
    level = wl.level_of(a)
    lv[level] = lv.get(level, 0) + 1
    if not (label.startswith("Walls_") or label.startswith("Roofs_") or label.startswith("Floors_")):
        continue
    o, e = a.get_actor_bounds(False)
    if e.x > 5000 or e.y > 5000:
        continue
    for k, z in FLOOR_Z.items():
        mid = z + 150.0
        if label.startswith("Walls_") and o.z - e.z < mid < o.z + e.z:
            r = out.setdefault(k, [1e9, -1e9, 1e9, -1e9, 0])
            r[0] = min(r[0], o.x - e.x); r[1] = max(r[1], o.x + e.x); r[2] = min(r[2], o.y - e.y); r[3] = max(r[3], o.y + e.y); r[4] += 1
    if label.startswith("Roofs_"):
        out.setdefault("roofs", []).append((label[:40], round(o.x - e.x), round(o.x + e.x), round(o.y - e.y), round(o.y + e.y), round(o.z - e.z), round(o.z + e.z)))
str({k: ([round(v) for v in r] if k != "roofs" else r) for k, r in out.items()}) + "\n" + str(lv)
