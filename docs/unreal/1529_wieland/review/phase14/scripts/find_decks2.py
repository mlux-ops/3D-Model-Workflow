import sys, json, re
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
pat = re.compile(r"terrace|roof_deck_out|roof_deck_pl|Level_Story|SV_W1529_Outdoor|Glass_Railing|Floors_Floor.*(ROOF|4th|3rd|4)|rear_patio", re.I)
rows = []
for a in wl.actors():
    lab = a.get_actor_label()
    if pat.search(lab):
        o, e = a.get_actor_bounds(False)
        rows.append("%s | %s | c=(%d,%d,%d) half=(%d,%d,%d)" % (wl.level_of(a).split("/")[-1][-16:], lab[:55], o.x, o.y, o.z, e.x, e.y, e.z))
rows.sort()
json.dumps(rows)
