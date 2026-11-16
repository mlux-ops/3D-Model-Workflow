"""Phase 11, step 11.2: read the walking surfaces inside each stair's box, to lay the camera moves on the treads. Read-only.

For every 20 cm cell of each box it traces straight down from the top of the box and, after each surface found,
again from 15 cm under it, up to six surfaces. Writes review/phase11/paths/stairs.json:
{box name: {"x": [...], "y": [...], "cells": [[[z, ...] per y] per x]}}.
"""
import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl

PATHS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/paths/"
# name: x_min, x_max, y_min, y_max, z_bottom, z_top
BOXES = {
    "A_L_to_1": (-1010.0, -750.0, -2110.0, -1850.0, -160.0, 290.0),
    "B_1_to_2": (-1030.0, -750.0, -1480.0, -1210.0, 195.0, 620.0),
    "C_3_to_4": (-900.0, -750.0, -1130.0, -640.0, 845.0, 1270.0),
    "D_4_to_roof": (-1420.0, -1000.0, -1130.0, -850.0, 1170.0, 1620.0),
    "E_rear_core": (-890.0, -750.0, -2600.0, -2240.0, 520.0, 1620.0),
    "F_entry": (-870.0, -750.0, -1220.0, -570.0, 0.0, 950.0),
    "G_patio": (-1190.0, -750.0, -3130.0, -3000.0, -10.0, 300.0),
}
CELL = 20.0
world = wl.world()
VIS = unreal.TraceTypeQuery.TRACE_TYPE_QUERY1
NONE = unreal.DrawDebugTrace.NONE


def hit_z(hit):
    for item in hit.to_tuple():
        if isinstance(item, unreal.Vector):
            return item.z
    return None


out = {}
for name, (x0, x1, y0, y1, zb, zt) in BOXES.items():
    xs = [x0 + CELL * (i + 0.5) for i in range(int((x1 - x0) / CELL))]
    ys = [y0 + CELL * (j + 0.5) for j in range(int((y1 - y0) / CELL))]
    cells = []
    for x in xs:
        row = []
        for y in ys:
            found, top = [], zt
            for _ in range(6):
                if top <= zb:
                    break
                hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, top), unreal.Vector(x, y, zb), VIS, True, [], NONE, False)
                if hit is None:
                    break
                z = hit_z(hit)
                if z is None:
                    break
                found.append(round(z, 0))
                top = z - 15.0
            row.append(found)
        cells.append(row)
    out[name] = {"x": xs, "y": ys, "cells": cells}
with open(PATHS + "stairs.json", "w", encoding="utf-8") as handle:
    json.dump(out, handle)
json.dumps({name: [len(box["x"]), len(box["y"])] for name, box in out.items()})
