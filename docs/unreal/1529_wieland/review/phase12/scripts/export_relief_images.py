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
# Read-only: writes the relief images of the two stone and tile materials out of the project as files,
# so that the depth of their relief can be measured outside the editor. Nothing in the project changes.
OUT = "C:/Users/cowey/AppData/Local/Temp/p12prev/relief/"
done = {}
for name in ("bump_Kit_Kat_Speckle__Stack__HE8CGJ_", "bump_Larvikite_Stack_192_8_x_145_2_inches__M2MLUQ___4_"):
    texture = unreal.load_asset(wr.DATASMITH.replace("/Materials/", "/Textures/") + name)
    task = unreal.AssetExportTask()
    task.set_editor_property("object", texture)
    task.set_editor_property("filename", OUT + name + ".png")
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("replace_identical", True)
    done[name] = bool(unreal.Exporter.run_asset_export_task(task))
json.dumps({"written": done, "unsaved": wr.dirty()})
