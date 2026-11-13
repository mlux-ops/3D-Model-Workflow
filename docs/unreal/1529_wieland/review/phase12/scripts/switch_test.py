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
# Step 12.4: the switch tested both ways, and the surfaces the Variant Manager cannot hold.
out = {}
out["revit_on"] = wr.switch(wr.OPTION_REVIT)
out["state_revit"] = wr.state(RECIPES)
out["active_on"] = wr.switch(wr.OPTION_ACTIVE)
out["state_active"] = wr.state(RECIPES)
wanted = wr._wanted(RECIPES)
missed = []
for actor, component, slot, revit, override in wr._slots():
    if revit in wanted and wr._property_path(unreal.VariantManagerLibrary, actor, component, slot) is None:
        missed.append([wr._level_name(actor), actor.get_actor_label(), component.get_name(), slot, revit.rsplit("/", 1)[-1]])
out["not_in_the_list"] = missed
out["unsaved"] = wr.dirty()
json.dumps(out)
