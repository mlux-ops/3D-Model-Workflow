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
# Read-only: how each relief image named by a recipe is stored (a relief image must be a normal map).
out = {}
for r in json.load(open(RECIPES, encoding="utf-8"))["rebuild"]:
    path = r["textures"].get("NormalMap")
    if path and path not in out:
        t = unreal.load_asset(path)
        out[path.rsplit("/", 1)[-1]] = None if t is None else [str(t.get_editor_property("compression_settings")), bool(t.get_editor_property("srgb")), t.blueprint_get_size_x(), t.blueprint_get_size_y(), bool(t.get_editor_property("flip_green_channel"))]
json.dumps(out)
