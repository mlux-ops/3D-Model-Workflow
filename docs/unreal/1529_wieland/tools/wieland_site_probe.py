"""Editor-side: read the top surface of the open level on a grid, by tracing straight down.

Runs inside the Unreal editor's Python interpreter. Read-only: it moves,
changes and saves nothing.

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_site_probe
    await wieland_site_probe.height_grid(x_min, x_max, y_min, y_max, step, "<out prefix>")

height_grid traces down at every point of a grid in level coordinates
(centimetres) and writes two files: <out prefix>.f32, the height of the
first surface hit at each point as 32-bit floats, row by row (x outer, y
inner), with -99999 where nothing was hit; and <out prefix>.json, which
says how to read it. It yields to the editor between chunks, so the editor
stays responsive.
"""

import array
import asyncio
import json
import time

import unreal

NOTHING = -99999.0


def one(x_cm, y_cm, top_cm=30000.0, bottom_cm=-3000.0):
    """Height (cm) of the first surface under a level point, and the name of what was hit; None if nothing."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x_cm, y_cm, top_cm), unreal.Vector(x_cm, y_cm, bottom_cm),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return None
    parts = hit.to_tuple()
    location = parts[4]
    actor = parts[9]
    return {"z_cm": location.z, "actor": actor.get_actor_label() if actor else None}


async def height_grid(x_min_cm, x_max_cm, y_min_cm, y_max_cm, step_cm, out_prefix, top_cm=30000.0, bottom_cm=-3000.0, chunk=600):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    nx = int((x_max_cm - x_min_cm) / step_cm) + 1
    ny = int((y_max_cm - y_min_cm) / step_cm) + 1
    values = array.array("f")
    started = time.time()
    hits = 0
    actors = {}
    done = 0
    for ix in range(nx):
        x = x_min_cm + ix * step_cm
        for iy in range(ny):
            y = y_min_cm + iy * step_cm
            hit = unreal.SystemLibrary.line_trace_single(
                world, unreal.Vector(x, y, top_cm), unreal.Vector(x, y, bottom_cm),
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            if hit is None:
                values.append(NOTHING)
            else:
                parts = hit.to_tuple()
                values.append(parts[4].z)
                hits += 1
                actor = parts[9]
                if actor is not None:
                    label = actor.get_actor_label()
                    actors[label] = actors.get(label, 0) + 1
            done += 1
            if done % chunk == 0:
                await asyncio.sleep(0)
    with open(out_prefix + ".f32", "wb") as handle:
        values.tofile(handle)
    header = {
        "world": world.get_path_name(),
        "x_min_cm": x_min_cm, "y_min_cm": y_min_cm, "step_cm": step_cm, "nx": nx, "ny": ny,
        "order": "x outer, y inner; value = height in cm of the first surface hit tracing down; %s where nothing was hit" % NOTHING,
        "points": nx * ny, "hits": hits, "seconds": round(time.time() - started, 1),
        "trace": "line_trace_single, visibility channel, complex collision, from z %s down to %s" % (top_cm, bottom_cm),
        "actors_hit": dict(sorted(actors.items(), key=lambda item: -item[1])[:70]),
        "actors_hit_count": len(actors),
    }
    with open(out_prefix + ".json", "w", encoding="utf-8") as handle:
        json.dump(header, handle, indent=1)
    return {k: header[k] for k in ("world", "nx", "ny", "points", "hits", "seconds", "actors_hit_count")}
