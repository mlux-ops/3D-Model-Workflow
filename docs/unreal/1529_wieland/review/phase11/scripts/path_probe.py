"""Phase 11, step 11.2: probe one camera route against the real geometry of the open level. Read-only.

Reads review/phase11/paths/probe_job.json = {"route": "<name>"} and review/phase11/paths/<name>_route.json =
{"points": [[x, y, floor_z_hint], ...]}. Walks the route in plan every STEP cm; at each sample it traces down
to find the walking surface (floor or stair tread) near the height interpolated between the two way points,
sets the eye EYE cm above it, then sweeps a small sphere from eye to eye and lists what it meets.
Writes review/phase11/paths/<name>_probe.json and returns a short summary.
"""
import sys, json, math
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl

PATHS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/paths/"
STEP = 10.0
EYE = 160.0
RADIUS = 12.0

with open(PATHS + "probe_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
name = job["route"]
with open(PATHS + name + "_route.json", "r", encoding="utf-8") as handle:
    route = json.load(handle)
points = route["points"]
world = wl.world()
VIS = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1
NONE = unreal.DrawDebugTrace.NONE


def label_of(hit):
    data = hit.to_tuple()
    actor = None
    for item in data:
        if isinstance(item, unreal.Actor):
            actor = item
            break
    location = None
    for item in data:
        if isinstance(item, unreal.Vector):
            location = item
            break
    return (actor.get_actor_label() if actor else "?"), location


def down(x, y, z_hint):
    hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, z_hint + 100.0), unreal.Vector(x, y, z_hint - 100.0),
                                                 VIS, True, [], NONE, False)
    if hit is None:
        return None, "nothing"
    label, location = label_of(hit)
    return location.z, label


samples = []
distance = 0.0
for i in range(len(points) - 1):
    a, b = points[i], points[i + 1]
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    count = max(1, int(round(length / STEP)))
    for k in range(count + (1 if i == len(points) - 2 else 0)):
        f = k / float(count)
        x, y, hint = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f
        floor, label = down(x, y, hint)
        samples.append({"d": round(distance + length * f, 1), "x": round(x, 1), "y": round(y, 1), "hint": round(hint, 1),
                        "floor": None if floor is None else round(floor, 1), "on": label, "way": i})
    distance += length

# eye heights: the floor found, else the hint; smoothed over 40 cm each way so stair treads do not shake the camera
raw = [(s["floor"] if s["floor"] is not None else s["hint"]) + EYE for s in samples]
for i, s in enumerate(samples):
    window = raw[max(0, i - 4):i + 5]
    s["eye"] = round(sum(window) / len(window), 1)

blocks = []
for i in range(len(samples) - 1):
    a, b = samples[i], samples[i + 1]
    hit = unreal.SystemLibrary.sphere_trace_single(world, unreal.Vector(a["x"], a["y"], a["eye"]), unreal.Vector(b["x"], b["y"], b["eye"]),
                                                   RADIUS, VIS, True, [], NONE, False)
    if hit is not None:
        label, _ = label_of(hit)
        a["hit"] = label
        if blocks and blocks[-1]["label"] == label and a["d"] - blocks[-1]["to"] <= 2 * STEP:
            blocks[-1]["to"] = a["d"]
        else:
            blocks.append({"label": label, "from": a["d"], "to": a["d"], "x": a["x"], "y": a["y"], "eye": a["eye"]})

no_floor = [s["d"] for s in samples if s["floor"] is None]
jumps = []
for i in range(len(samples) - 1):
    a, b = samples[i], samples[i + 1]
    if a["floor"] is not None and b["floor"] is not None and abs(b["floor"] - a["floor"]) > 25.0:
        jumps.append([b["d"], a["floor"], b["floor"], b["on"]])
out = {"route": name, "length_m": round(distance / 100.0, 2), "samples": samples, "blocks": blocks, "no_floor": no_floor, "jumps": jumps}
with open(PATHS + name + "_probe.json", "w", encoding="utf-8") as handle:
    json.dump(out, handle)
ways = []
for i in range(len(points)):
    first = next((s for s in samples if s["way"] == i), samples[-1]) if i < len(points) - 1 else samples[-1]
    ways.append([i, first["d"], first["floor"], first["on"][:40]])
json.dumps({"length_m": out["length_m"], "blocks": blocks[:40], "block_count": len(blocks), "no_floor_count": len(no_floor),
            "no_floor_first": no_floor[:10], "jumps": jumps[:30], "ways": ways})
