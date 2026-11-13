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
# Step 12.2 batch, part 3: a swatch picture of every rebuilt material, on the Phase 5 swatch stage.
import re
level = wm.build_swatch_level()
OUT = ROOT + "/review/phase12/swatches/rebuilt/"
items = [[r["material"], r["asset"], OUT + re.sub(r"[^A-Za-z0-9_-]", "_", r["material"]) + ".png"]
         for r in json.load(open(RECIPES, encoding="utf-8"))["rebuild"]]
json.dumps({"level": level, "job": wm.swatch_start(items, settle=6.0, overwrite=True)})
