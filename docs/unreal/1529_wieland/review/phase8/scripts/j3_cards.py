import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.append(T)
import unreal
import wieland_lighting as wl
importlib.reload(wl)

out = {"removed_before": wl.temp_clear()}
sun = wl.read_sun()
out["sun"] = sun
OPEN = (-754.0, -1500.0, 5500.0)       # 55 m above the lot, clear of every roof
OPEN2 = (-1754.0, -1500.0, 5500.0)     # a second card 10 m north, that one faces the sun
WALK = (-754.4, 250.0, 2.0)            # on the sidewalk in front of the building (S9 stands at y = 210)
wl.card_place("flat", OPEN)
wl.card_place("facing", OPEN2, sun["bearing"], sun["height"])
wl.card_place("walk", WALK)
await wl.wait_frames(4.0)
out["flat_sun_and_sky"] = wl.card_read("flat")
out["facing_sun"] = wl.card_read("facing")
out["sidewalk"] = wl.card_read("walk")
wl.card_shade("flat", OPEN, sun["bearing"], sun["height"])
await wl.wait_frames(4.0)
out["flat_sky_only"] = wl.card_read("flat")
out["removed_after"] = wl.temp_clear()
out["dirty"] = wl.dirty()
json.dumps(out)
