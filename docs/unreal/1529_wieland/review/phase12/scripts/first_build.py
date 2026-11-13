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
# Step 12.2: the first rebuilt material only (Cabinet_Wood_Veneer): its images and its instance.
images = wr.import_images(RECIPES, only=["T_W1529_P12_OakVeneer02_Strong_C", "T_W1529_P12_OakVeneer02_C", "T_W1529_P12_OakVeneer02_N", "T_W1529_P12_OakVeneer02_R"])
built = wr.build(RECIPES, only=["Cabinet_Wood_Veneer"], rebuild=True)
json.dumps({"images": images, "built": built, "wrong": wr.verify(RECIPES).get("Cabinet_Wood_Veneer"), "unsaved": wr.dirty()})
