"""Phase 13: measure the built hotel in the editor with straight-line probes, not from the generator's numbers.

A probe is a line from outside the building to its first meeting with one of the hotel's placed objects (objects
of other levels are stepped over). Probes straight down give roof and terrace heights; level probes give the
position of each wall; a column of level probes up a window line counts the storeys (each storey shows as one
run of probes that go deeper, into the window recess).

Hotel frame: a = feet east of sub-area A's west line, b = feet south of its north line, z = feet above the
hotel's first floor. Site feet: east = 28.75 + a, north = -24.75 - b; the first floor is 1.0 ft above level zero.

Run in the editor: python -B tools/ue_call.py py review/phase13/scripts/measure_traces.py 600
Writes review/phase13/measure_traces.json.
"""
import json
import os
import sys

import unreal

sys.dont_write_bytecode = True
TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_hotel as wh

CM = 30.48006096
WEST_LINE, NORTH_LINE, FIRST_FLOOR = 28.75, -24.75, 1.0
OUT = wh.PLAN + "/review/phase13/measure_traces.json"
HOTEL = {actor.get_path_name() for actor in wh.hotel_actors()}
WORLD = wh.world()


def point(a, b, z):
    east, north = WEST_LINE + a, NORTH_LINE - b
    return unreal.Vector(-north * CM, -east * CM, (z + FIRST_FLOOR) * CM)


def probe(start, end):
    """Feet from start to the first hotel object on the line, and that object's label; None when nothing is met."""
    ignore = []
    for _ in range(12):
        hit = unreal.SystemLibrary.line_trace_single(WORLD, point(*start), point(*end), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                     True, ignore, unreal.DrawDebugTrace.NONE, False)
        if hit is None:
            return None, None
        fields = hit.to_tuple()
        actor = fields[9]
        if actor is not None and actor.get_path_name() in HOTEL:
            return fields[3] / CM, actor.get_actor_label()
        if actor is None:
            return None, None
        ignore.append(actor)
    return None, None


def down(a, b):
    distance, label = probe((a, b, 260.0), (a, b, -20.0))
    return (None, None) if distance is None else (round(260.0 - distance, 2), label)


def wall(axis, start_value, direction, fixed, z, spread):
    """Position of a wall along one axis ('a' or 'b'): several probes side by side; the outermost reading that
    at least two probes give is the wall, deeper ones are window recesses. Returns (wall position, how many
    probes gave it, of how many)."""
    readings = []
    for offset in spread:
        if axis == "a":
            start, end = (start_value, fixed + offset, z), (start_value + direction * 400.0, fixed + offset, z)
        else:
            start, end = (fixed + offset, start_value, z), (fixed + offset, start_value + direction * 400.0, z)
        distance, _ = probe(start, end)
        if distance is not None:
            readings.append(round(start_value + direction * distance, 1))
    if not readings:
        return None, 0, len(spread)
    repeated = [value for value in set(readings) if readings.count(value) >= 2] or readings
    outer = min(repeated) if direction > 0 else max(repeated)      # the wall; deeper readings are window recesses
    return outer, readings.count(outer), len(spread)


def storeys(axis, start_value, direction, fixed, z_low, z_high, step=0.25):
    """Up one window line: the depth read every `step` feet. A storey is one run of readings at least 0.3 ft
    deeper than the wall. Returns the runs as (z from, z to)."""
    depths = []
    z = z_low
    while z <= z_high:
        if axis == "a":
            distance, _ = probe((start_value, fixed, z), (start_value + direction * 400.0, fixed, z))
        else:
            distance, _ = probe((fixed, start_value, z), (fixed, start_value + direction * 400.0, z))
        depths.append((z, distance))
        z += step
    known = sorted(d for _, d in depths if d is not None)
    if not known:
        return []
    face = known[len(known) // 10]                       # the wall: near the smallest distance, ignoring sills
    runs, begun = [], None
    for z, distance in depths:
        deep = distance is not None and distance > face + 0.3 and distance < face + 6.0
        if deep and begun is None:
            begun = z
        if not deep and begun is not None:
            if z - begun >= 3.0:
                runs.append((round(begun, 2), round(z, 2)))
            begun = None
    return runs


def window_line(axis, start_value, direction, low, high, z, step=0.25):
    """Along a face at one height: the middle of the first recess at least 3 ft wide (a window)."""
    readings = []
    value = low
    while value <= high:
        if axis == "a":
            distance, _ = probe((start_value, value, z), (start_value + direction * 400.0, value, z))
        else:
            distance, _ = probe((value, start_value, z), (value, start_value + direction * 400.0, z))
        readings.append((value, distance))
        value += step
    known = sorted(d for _, d in readings if d is not None)
    if not known:
        return None
    face = known[len(known) // 10]
    begun = None
    for value, distance in readings:
        deep = distance is not None and face + 0.3 < distance < face + 6.0
        if deep and begun is None:
            begun = value
        if not deep and begun is not None:
            if value - begun >= 3.0:
                return round((begun + value) / 2.0, 2)
            begun = None
    return None


SPREAD = [-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5, 6.0]
result = {"frame": "a east of sub-area A's west line, b south of its north line, z above the hotel's first floor; feet",
          "heights": {}, "walls": {}, "storeys": {}, "homes": {}}

for name, a, b in (("garage roof (planted)", 24.0, 62.0), ("3rd floor terrace, north strip", 100.0, 6.0),
                   ("3rd floor terrace, south strip", 100.0, 118.5), ("2nd floor terrace, middle of the Wells front", 166.0, 55.0),
                   ("south wing roof (7th floor terrace)", 163.0, 104.0), ("north wing roof (9th floor terrace)", 163.0, 20.0),
                   ("dark projecting part roof (11th floor terrace)", 154.0, 90.0),
                   ("12th floor terrace, west side", 56.0, 60.0), ("12th floor terrace, east side", 141.0, 60.0),
                   ("12th floor roof", 125.0, 55.0), ("mechanical penthouse roof (top of the building)", 90.0, 62.0)):
    result["heights"][name] = down(a, b)

for name, axis, start, direction, fixed, z in (
        ("garage west wall", "a", -80.0, 1, 62.0, 12.0),
        ("base north wall", "b", -60.0, 1, 120.0, 12.0),
        ("base south wall", "b", 200.0, -1, 120.0, 12.0),
        ("north wing east wall (Wells line)", "a", 260.0, -1, 20.0, 50.0),
        ("south wing east wall (Wells line)", "a", 260.0, -1, 104.0, 50.0),
        ("tower north wall", "b", -60.0, 1, 100.0, 60.0),
        ("tower south wall", "b", 200.0, -1, 100.0, 60.0),
        ("tower west wall, red side bay", "a", -80.0, 1, 27.0, 60.0),
        ("tower west wall, dark middle bay", "a", -80.0, 1, 62.0, 60.0),
        ("tower east wall (above the north wing)", "a", 260.0, -1, 30.0, 110.0),
        ("dark projecting part, east wall", "a", 260.0, -1, 90.0, 100.0),
        ("north wing south wall", "b", 200.0, -1, 163.0, 85.0),
        ("south wing north wall", "b", 62.0, 1, 163.0, 60.0),
        ("12th floor west wall", "a", -80.0, 1, 56.0, 135.0),
        ("12th floor east wall", "a", 260.0, -1, 56.0, 135.0),
        ("12th floor north wall", "b", -60.0, 1, 110.0, 135.0),
        ("12th floor south wall (east part)", "b", 200.0, -1, 118.0, 135.0),
        ("12th floor south wall (leg)", "b", 200.0, -1, 82.0, 135.0),
        ("penthouse west wall", "a", -80.0, 1, 62.0, 147.0),
        ("penthouse east wall", "a", 260.0, -1, 62.0, 147.0),
        ("penthouse north wall", "b", -60.0, 1, 90.0, 147.0),
        ("penthouse south wall", "b", 200.0, -1, 90.0, 147.0)):
    result["walls"][name] = wall(axis, start, direction, fixed, z, SPREAD)

# storeys: floors 1 to 9 up a window line of the north wing's Wells face, floors 10 and 11 up a window line of
# the tower's east face above that wing, floor 12 up a window line of the 12th floor's east face
line_wing = window_line("a", 260.0, -1, 2.0, 39.0, 50.0)
line_tower = window_line("a", 260.0, -1, 14.0, 66.0, 110.0)
line_top = window_line("a", 141.0, -1, 26.0, 86.0, 135.0)      # from inside the terrace's glass guard
result["storeys"]["window lines (b)"] = {"north wing": line_wing, "tower east face": line_tower, "12th floor": line_top}
if line_wing is not None:
    result["storeys"]["floors 1-9, north wing on Wells"] = storeys("a", 260.0, -1, line_wing, 0.5, 93.0)
if line_tower is not None:
    result["storeys"]["floors 10-11, tower east face"] = storeys("a", 260.0, -1, line_tower, 94.5, 127.0)
if line_top is not None:
    result["storeys"]["floor 12"] = storeys("a", 141.0, -1, line_top, 128.5, 141.5)
# the tower's north face, floors 3 to 11, as a second count
line_north = window_line("b", -60.0, 1, 52.0, 146.0, 60.0)
result["storeys"]["window lines (b)"]["tower north face (a)"] = line_north
if line_north is not None:
    result["storeys"]["floors 3-11, tower north face"] = storeys("b", -60.0, 1, line_north, 33.5, 127.0)

# the homes, in site feet: top of the roof deck above level zero, and the four walls at 20 ft above level zero
# (each probe starts in the open, a few feet outside the wall it looks for)
for name, east, north, to_north, to_south in (("Home 1 (south)", 16.0, -122.0, 28.0, 30.0), ("Home 2 (north)", 16.0, -52.0, 28.0, 30.0),
                                              ("Home 3", 30.0, -12.0, 28.0, 13.0)):
    a, b = east - WEST_LINE, NORTH_LINE - north
    top, _ = down(a, b)
    record = {"roof deck above level zero": None if top is None else round(top + FIRST_FLOOR, 2)}
    for side, axis, start, direction, fixed in (("west wall, east", "a", a - 40.0, 1, b), ("east wall, east", "a", a + 60.0, -1, b),
                                                ("north wall, north", "b", b - to_north, 1, a), ("south wall, north", "b", b + to_south, -1, a)):
        value, _, _ = wall(axis, start, direction, fixed, 19.0, [-4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0])
        if value is not None:
            value = round(WEST_LINE + value, 2) if axis == "a" else round(NORTH_LINE - value, 2)
        record[side] = value
    result["homes"][name] = record

with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=1)
json.dumps(result)
