"""Phase 11, step 11.2: map what a walking camera meets on each floor of the north half. Read-only.

For every 10 cm cell of each floor it sweeps a small sphere upward from 100 to 170 cm above the finished floor
(what blocks a camera at eye height) and traces down from 90 cm above the floor (where the walking surface is:
floor, stair tread, or a piece of furniture). Writes review/phase11/paths/map_<floor>.json; the pictures are
drawn outside the editor by map_draw.py.
"""
import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl

PATHS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/paths/"
FLOOR_Z = {"L": -152.4, "1": 203.2, "2": 528.3, "3": 853.4, "4": 1178.6, "R": 1524.0}
CELL = 10.0
X0, X1, Y0, Y1 = -1430.0, -740.0, -3140.0, -280.0
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


with open(PATHS + "map_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
summary = {}
for floor in job["floors"]:
    z = FLOOR_Z[floor]
    labels, index, rows = [], {}, []
    nx, ny = int((X1 - X0) / CELL), int((Y1 - Y0) / CELL)
    blocked = 0
    for i in range(nx):
        x = X0 + (i + 0.5) * CELL
        row = []
        for j in range(ny):
            y = Y0 + (j + 0.5) * CELL
            hit = unreal.SystemLibrary.sphere_trace_single(world, unreal.Vector(x, y, z + 100.0), unreal.Vector(x, y, z + 170.0), 8.0,
                                                           VIS, True, [], NONE, False)
            block = -1
            if hit is not None:
                label, _ = parts(hit)
                if label not in index:
                    index[label] = len(labels)
                    labels.append(label)
                block = index[label]
                blocked += 1
            hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, z + 90.0), unreal.Vector(x, y, z - 190.0),
                                                         VIS, True, [], NONE, False)
            height = None
            if hit is not None:
                _, location = parts(hit)
                height = round(location.z - z, 1)
            row.append([block, height])
        rows.append(row)
    with open(PATHS + "map_%s.json" % floor, "w", encoding="utf-8") as handle:
        json.dump({"floor": floor, "z": z, "cell": CELL, "x0": X0, "y0": Y0, "nx": nx, "ny": ny, "labels": labels, "cells": rows}, handle)
    summary[floor] = {"cells": nx * ny, "blocked": blocked, "labels": len(labels)}
json.dumps(summary)
