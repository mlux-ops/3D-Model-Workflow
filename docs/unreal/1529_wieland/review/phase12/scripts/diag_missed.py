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
# Step 12.4: what the Variant Manager offers for one object whose surface it did not take.
found = None
for actor, component, slot, revit, override in wr._slots():
    if actor.get_actor_label() == "Railings_Railing_Fence_-_Regular":
        found = (actor, component, slot)
        break
actor, component, slot = found
paths = [str(p) for p in unreal.VariantManagerLibrary.get_capturable_properties(actor)]
json.dumps({"component": component.get_name(), "slots": component.get_num_materials(),
            "material_paths": [p for p in paths if "Material" in p][:40], "count": len(paths)})
