"""Phase 13, step 13.1, read-only: every object of the open world whose bounds overlap the planned
development's land (Planned Development 1335: from the project's south lot line 149.55 ft south, from the
Wieland Street line 204.50 ft east), in site feet (north, east of the project lot's south-west corner).
"""
import json

import unreal

CM = 30.48006096
NORTH = (-149.55, 0.0)
EAST = (0.0, 204.5)
MARGIN = 1.0  # ft: an object must reach this far inside the land to be listed

actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
rows = []
for actor in actors:
    components = actor.get_components_by_class(unreal.StaticMeshComponent)
    if not components:
        continue
    origin, extent = actor.get_actor_bounds(False)
    if extent.x <= 0 and extent.y <= 0:
        continue
    north = (-(origin.x + extent.x) / CM, -(origin.x - extent.x) / CM)
    east = (-(origin.y + extent.y) / CM, -(origin.y - extent.y) / CM)
    if north[1] < NORTH[0] + MARGIN or north[0] > NORTH[1] - MARGIN:
        continue
    if east[1] < EAST[0] + MARGIN or east[0] > EAST[1] - MARGIN:
        continue
    size_n = north[1] - north[0]
    size_e = east[1] - east[0]
    mesh = components[0].static_mesh
    rows.append({
        "label": actor.get_actor_label(),
        "level": actor.get_outer().get_outermost().get_name().split("/")[-1],
        "class": actor.get_class().get_name(),
        "mesh": mesh.get_path_name() if mesh else None,
        "tags": [str(t) for t in actor.tags],
        "hidden_editor": actor.is_temporarily_hidden_in_editor(),
        "hidden_game": bool(actor.get_editor_property("hidden")),
        "component_visible": components[0].is_visible(),
        "south": round(north[0], 1), "north": round(north[1], 1),
        "west": round(east[0], 1), "east": round(east[1], 1),
        "top_ft": round((origin.z + extent.z) / CM, 1), "bottom_ft": round((origin.z - extent.z) / CM, 1),
        "big": size_n > 400 or size_e > 400,
    })
rows.sort(key=lambda r: (r["level"], r["label"]))
json.dumps(rows)
