"""Phase 11, step 11.2: probe a finished camera move (the 900 eye positions of move_build.py) against the real
geometry of the open level. Read-only.

Reads review/phase11/paths/probe_job.json = {"route": "<name>"} and review/phase11/paths/<name>_move.json. Sweeps a
sphere of RADIUS cm from each frame's eye to the next and lists what it meets; also measures, every tenth frame,
the free distance to the sides, above and below the eye. Returns the list of things met (a closed glass door the
move passes through on purpose is expected) and the smallest clearances.
"""
import sys, json, math
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl

PATHS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/paths/"
RADIUS = 10.0
with open(PATHS + "probe_job.json", "r", encoding="utf-8") as handle:
    name = json.load(handle)["route"]
with open(PATHS + name + "_move.json", "r", encoding="utf-8") as handle:
    frames = json.load(handle)["frames"]
world = wl.world()
VIS = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1
NONE = unreal.DrawDebugTrace.NONE


def parts(hit):
    actor, location = None, None
    for item in hit.to_tuple():
        if actor is None and isinstance(item, unreal.Actor):
            actor = item
        if location is None and isinstance(item, unreal.Vector):
            location = item
    return (actor.get_actor_label() if actor else "?"), location


blocks = []
for a, b in zip(frames[:-1], frames[1:]):
    hit = unreal.SystemLibrary.sphere_trace_single(world, unreal.Vector(*a["loc"]), unreal.Vector(*b["loc"]), RADIUS, VIS, True, [], NONE, False)
    if hit is not None:
        label, _ = parts(hit)
        if blocks and blocks[-1]["label"] == label and a["f"] - blocks[-1]["to"] <= 2:
            blocks[-1]["to"] = a["f"]
        else:
            blocks.append({"label": label, "from": a["f"], "to": a["f"], "loc": a["loc"]})

tight = []
for frame in frames[::10]:
    here = unreal.Vector(*frame["loc"])
    yaw = math.radians(frame["rot"][1])
    row = {"f": frame["f"]}
    for key, direction in (("left", (math.sin(yaw), -math.cos(yaw), 0.0)), ("right", (-math.sin(yaw), math.cos(yaw), 0.0)),
                           ("up", (0.0, 0.0, 1.0)), ("down", (0.0, 0.0, -1.0))):
        end = unreal.Vector(here.x + direction[0] * 300.0, here.y + direction[1] * 300.0, here.z + direction[2] * 300.0)
        hit = unreal.SystemLibrary.line_trace_single(world, here, end, VIS, True, [], NONE, False)
        if hit is None:
            row[key] = None
        else:
            label, location = parts(hit)
            row[key] = round(math.dist((here.x, here.y, here.z), (location.x, location.y, location.z)), 1)
            row[key + "_on"] = label[:36]
    tight.append(row)
sides = sorted([r for r in tight if r.get("left") is not None or r.get("right") is not None],
               key=lambda r: min(v for v in (r.get("left"), r.get("right")) if v is not None))[:8]
heads = sorted([r for r in tight if r.get("up") is not None], key=lambda r: r["up"])[:6]
feet = [[r["f"], r.get("down")] for r in tight if r.get("down") is None or abs(r["down"] - 160.0) > 30.0]
with open(PATHS + name + "_move_probe.json", "w", encoding="utf-8") as handle:
    json.dump({"blocks": blocks, "clearances": tight}, handle)
json.dumps({"move": name, "blocks": blocks, "closest_sides": sides, "lowest_ceilings": heads, "eye_not_160_above_surface": feet})
