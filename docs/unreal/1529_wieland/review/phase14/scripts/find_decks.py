import sys, json, re
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
pat = re.compile(r"deck|patio|terrace|balcon|pergola|roof|rail|guard|parapet|pool|garden|porch", re.I)
rows = []
for a in wl.actors():
    lab = a.get_actor_label()
    if pat.search(lab) and isinstance(a, (unreal.StaticMeshActor, unreal.Actor)):
        o, e = a.get_actor_bounds(False)
        rows.append((wl.level_of(a).split("/")[-1], lab[:60], round(o.x), round(o.y), round(o.z), round(e.x), round(e.y), round(e.z)))
from collections import Counter
c = Counter((r[0], re.sub(r"[_\d]+$", "", r[1])[:40]) for r in rows)
out = {"n": len(rows), "kinds": [[k[0], k[1], v] for k, v in c.most_common(60)]}
json.dumps(out)
