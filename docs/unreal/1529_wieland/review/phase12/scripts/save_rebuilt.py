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
# Saves by name the rebuilt instances that the swatch job left marked as unsaved. Nothing else is saved.
before = wr.dirty()
saved, refused = 0, []
for package in before:
    if package.startswith("/Game/Wieland1529/Materials/Rebuilt/"):
        if unreal.EditorAssetLibrary.save_asset(package, only_if_is_dirty=True):
            saved += 1
        else:
            refused.append(package)
    else:
        refused.append(package)
json.dumps({"unsaved_before": len(before), "saved": saved, "not_saved": refused, "unsaved_after": wr.dirty()})
