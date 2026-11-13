"""Phase 13, read-only: the height of the modelled ground over and around the planned development's land,
by tracing straight down at a grid of points. Site feet: north and east of the project lot's south-west corner.
Also reports the open world, its levels and what is unsaved.
"""
import json

import unreal

CM = 30.48006096
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
rows = []
for north in (-160, -149, -125, -100, -75, -50, -25, -12, 0, 10):
    for east in (-20, -5, 2, 15, 29, 60, 102, 150, 200, 204, 210, 225, 245):
        start = unreal.Vector(-north * CM, -east * CM, 20000.0)
        end = unreal.Vector(-north * CM, -east * CM, -3000.0)
        hits = unreal.SystemLibrary.line_trace_multi(world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [],
                                                     unreal.DrawDebugTrace.NONE, True)
        found = []
        for hit in hits or []:
            parts = hit.to_tuple()
            actor = parts[9]
            label = actor.get_actor_label() if actor else "?"
            found.append([label, round(parts[4].z / CM, 2)])
        ground = [f for f in found if f[0].startswith("SW_") or f[0].startswith("SG_")]
        rows.append({"north": north, "east": east, "first": found[0] if found else None, "ground": ground[0] if ground else None})
levels = [level.get_outer().get_path_name().split(".")[0] for level in unreal.EditorLevelUtils.get_levels(world)]
utils = unreal.EditorLoadingAndSavingUtils
dirty = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
json.dumps({"world": world.get_path_name(), "levels": levels, "dirty": dirty, "rows": rows})
