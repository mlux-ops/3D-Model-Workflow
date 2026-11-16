import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_materials as wm
import wieland_rebuild as wr
importlib.reload(wr)
ROOT = T.rsplit("/", 1)[0]
RECIPES = ROOT + "/review/phase12/recipes.json"
TABLE = ROOT + "/review/phase12/applied_slots.csv"
# Step 12.2 batch, part 1: the two extra parents and every image the recipes name.
parents = wr.build_parents()
images = wr.import_images(RECIPES)
json.dumps({"parents": parents, "imported": len(images.get("imported", [])), "failed": images.get("failed"), "already_there": images.get("already_there"), "unsaved": wr.dirty()})
