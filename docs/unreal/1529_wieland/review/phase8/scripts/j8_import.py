import sys
sys.dont_write_bytecode = True
T = 'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools'
if T not in sys.path:
    sys.path.insert(0, T)
import importlib
import unreal
import wieland_fixtures as wf
importlib.reload(wf)
out = {}
for (family, kind), row in wf.read_table().items():
    asset = row['profile_asset']
    if not asset or asset in out:
        continue
    name = asset.split('/')[-1]
    path = wf.import_profile(row['photometric_file'], name)
    loaded = unreal.load_asset(path)
    out[asset] = (loaded.get_class().get_name(), round(loaded.get_editor_property('brightness'), 1) if loaded else None)
str(out)
