"""Phase 13, step 13.7: how much of 1529 N. Wieland the hotel puts in shadow on 15 August, hour by hour.

Read-only. The sun is not moved: its direction is worked out from the Sun Position plugin for each clock time and
used only for line tests. Points: a grid every 2.5 ft over the project lot (north 0 to 49.5, east 0 to 102.2 in
site feet); each point is the first drawn surface met by a line straight down (roof, roof deck, terrace, yard); points
that land on a surface inside 1529 (ceilings, furniture, interior partitions, lower floors; 1529 has roof parts without
collision) are left out and counted separately, so the shares are of outdoor points only. From
each point a line goes 600 m toward the sun and lists every object it passes through. A point is in shadow
"as surveyed" when anything other than a hotel object is on the line, and "with the hotel" when anything other
than the three existing objects the proposed option hides is on the line. Line tests see collision shapes, so
hidden objects still count unless excluded here, as done.
Run: python -B tools/ue_call.py py review/phase13/scripts/shadow_traces.py 900
Writes review/phase13/shadow/shadow_traces.json.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_hotel as wh
import wieland_interiors as wi

CM = wh.CM
OUT = wh.PLAN + "/review/phase13/shadow"
os.makedirs(OUT, exist_ok=True)
WORLD = wh.world()
HOTEL = {a.get_path_name() for a in wh.hotel_actors()}
HIDDEN = {a.get_path_name() for a in wh._existing_objects()}
TRACE = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1
HOURS = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 15.5, 16.0, 17.0, 18.0, 19.0]


def vec(east, north, up_cm):
    return unreal.Vector(-north * CM, -east * CM, up_cm)


def shown(actor):
    """True when the object draws: not a Revit stand-in, and at least one visible mesh component. Hidden objects
    still have collision, so they are stepped over here rather than counted as casting shadow."""
    if actor.get_actor_label() in wi.REVIT_STAND_INS or actor.is_hidden_ed():
        return actor.get_path_name() in HIDDEN
    comps = actor.get_components_by_class(unreal.PrimitiveComponent)
    return any(c.get_editor_property("visible") for c in comps) or actor.get_path_name() in HIDDEN or actor.get_path_name() in HOTEL


def first_surface(east, north):
    """First drawn surface straight down (Revit stand-ins, hotel and hide-list objects stepped over)."""
    ignore = [a for a in wh.hotel_actors()] + list(wh._existing_objects())
    for _ in range(16):
        hit = unreal.SystemLibrary.line_trace_single(WORLD, vec(east, north, 9000.0), vec(east, north, -1000.0), TRACE,
                                                     True, ignore, unreal.DrawDebugTrace.NONE, False)
        if hit is None:
            return None
        fields = hit.to_tuple()
        actor = fields[9]
        if actor is None:
            return None
        if shown(actor):
            return fields[4], actor.get_actor_label()  # impact point, object
        ignore.append(actor)
    return None


# Surfaces that are inside 1529: a line from above that lands on them has passed through a roof without collision
# (the plan pictures show 1529 open from above). Such points are not outdoor places and are left out of the shares.
INTERIOR = ("Ceilings_", "Furniture_", "Walls_Basic_Wall_C1010_Interior", "Floors_Floor_Generic_-_1_-2_")


def interior(label):
    return label.startswith(INTERIOR) or "Interior_Partition" in label


def blockers(start, end):
    found, ignore = [], []
    for _ in range(16):
        hit = unreal.SystemLibrary.line_trace_single(WORLD, start, end, TRACE, True, ignore,
                                                     unreal.DrawDebugTrace.NONE, False)
        if hit is None:
            break
        actor = hit.to_tuple()[9]
        if actor is None:
            break
        if shown(actor):
            found.append(actor.get_path_name())
        ignore.append(actor)
    return found


points, skipped = [], []
for i in range(20):
    for j in range(41):
        north, east = 1.25 + 2.5 * i, 1.25 + 2.5 * j
        surface = first_surface(east, north)
        if surface is None:
            continue
        loc, label = surface
        if interior(label):
            skipped.append([north, east, label])
            continue
        points.append({"north": north, "east": east, "z_ft": round(loc.z / CM, 2), "on": label,
                       "start": unreal.Vector(loc.x, loc.y, loc.z + 5.0)})

results = []
for hour in HOURS:
    h, m = int(hour), int(round((hour - int(hour)) * 60))
    data = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, -6.0, True, 2026, 8, 15, h, m, 0)
    height = data.corrected_elevation - 180.0 if data.corrected_elevation > 90.0 else data.corrected_elevation
    to_sun = unreal.MathLibrary.get_forward_vector(wl.sun_rotation(data.azimuth, height)) * -60000.0
    rows = []
    for p in points:
        found = blockers(p["start"], p["start"] + to_sun)
        existing = any(f not in HOTEL for f in found)
        proposed = any(f not in HIDDEN for f in found)
        rows.append([p["north"], p["east"], p["z_ft"], int(existing), int(proposed), int(any(f in HOTEL for f in found))])
    results.append({"clock_cdt": "%02d:%02d" % (h, m), "sun_bearing": round(data.azimuth, 1),
                    "sun_height": round(height, 1), "points": rows})

summary = []
for r in results:
    pts = r["points"]
    n = len(pts)
    roof = [p for p in pts if p[2] >= 45.0]
    summary.append({"clock_cdt": r["clock_cdt"], "sun_bearing": r["sun_bearing"], "sun_height": r["sun_height"],
                    "points": n, "shade_existing_pct": round(100.0 * sum(p[3] for p in pts) / n, 1),
                    "shade_proposed_pct": round(100.0 * sum(p[4] for p in pts) / n, 1),
                    "new_shade_by_hotel_pct": round(100.0 * sum(1 for p in pts if p[4] and not p[3]) / n, 1),
                    "hotel_on_line_pct": round(100.0 * sum(p[5] for p in pts) / n, 1),
                    "roof_points": len(roof),
                    "roof_hotel_on_line_pct": round(100.0 * sum(p[5] for p in roof) / max(1, len(roof)), 1),
                    "roof_new_shade_pct": round(100.0 * sum(1 for p in roof if p[4] and not p[3]) / max(1, len(roof)), 1)})
with open(OUT + "/shadow_traces.json", "w", encoding="utf-8") as handle:
    json.dump({"note": __doc__, "summary": summary, "results": results,
               "surfaces": sorted({p["on"] for p in points}),
               "left_out_interior": {"count": len(skipped), "labels": sorted({x[2] for x in skipped}), "points": skipped}}, handle, indent=1)
json.dumps([len(points), len(skipped)] + summary)
