import sys, json, re
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_site as ws
# Phase 10, read-only: which objects of the level today are street furniture or the like (poles, wires, lamps,
# hydrants, signs, fences, railings, stoops, cars), found by the words in their label or in their mesh's name,
# outside the building's own levels. Writes review/phase10/furniture_now.json. Nothing is changed.
WORDS = re.compile(r"pole|wire|cable|lamp|light|hydrant|sign|fence|rail|stoop|stair|step|car|vehicle|bench|bin|trash|meter|post|gate|bollard", re.I)
SKIP = ("L_W1529_", "L_Building", "L_Lighting")
found = []
for actor in ws.actors():
    level = ws.level_of(actor)
    if any(part in level for part in SKIP):
        continue
    label = actor.get_actor_label()
    meshes = []
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = component.static_mesh
        if mesh is not None:
            meshes.append(mesh.get_name())
    text = label + " " + " ".join(meshes)
    if not WORDS.search(text):
        continue
    origin, extent = actor.get_actor_bounds(False)
    found.append({"label": label, "level": level.rsplit("/", 1)[-1], "class": actor.get_class().get_name(),
                  "meshes": sorted(set(meshes))[:4], "x": round(origin.x, 1), "y": round(origin.y, 1), "z": round(origin.z, 1),
                  "size_cm": [round(extent.x * 2, 1), round(extent.y * 2, 1), round(extent.z * 2, 1)],
                  "hidden": bool(actor.is_temporarily_hidden_in_editor() or actor.is_hidden_ed()),
                  "tags": [str(tag) for tag in actor.tags]})
found.sort(key=lambda item: (item["level"], item["label"]))
with open(T.rsplit("/", 1)[0] + "/review/phase10/furniture_now.json", "w", encoding="utf-8") as handle:
    json.dump(found, handle, indent=1)
levels = {}
for item in found:
    levels[item["level"]] = levels.get(item["level"], 0) + 1
json.dumps({"found": len(found), "by_level": levels})
