import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.append(T)
import unreal
import wieland_lighting as wl
importlib.reload(wl)

out = {"removed_before": wl.temp_clear()}
sun_actor = wl.by_label("LGT_Sun")
sun_actor.light_component.set_editor_property("intensity", 140000.0)
EV = 14.644  # f/8, 1/400 s, ISO 100
out["exposure"] = wl.set_exposure("LGT_Exposure_Outdoors", EV)
ev = out["exposure"]["ev100"]
sun = wl.read_sun()
out["sun"] = sun
OPEN = (-754.0, -1500.0, 5500.0)
OPEN2 = (-1754.0, -1500.0, 5500.0)
WALK = (-754.4, 250.0, 2.0)
wl.card_place("flat", OPEN)
wl.card_place("facing", OPEN2, sun["bearing"], sun["height"])
wl.card_place("walk", WALK)
# The sidewalk itself, 3 m south of the card, seen from eye height at the same downward angle.
wl.probe_place("concrete", (-454.4 - 80.0, 250.0, 62.0), (-454.4, 250.0, 2.0))
await wl.wait_frames(5.0)
out["flat_sun_and_sky"] = wl.card_read("flat")
out["facing_sun"] = wl.card_read("facing")
out["sidewalk_card"] = wl.card_read("walk")
out["sidewalk_concrete"] = wl.probe_read("concrete", ev)
wl.card_shade("flat", OPEN, sun["bearing"], sun["height"])
await wl.wait_frames(4.0)
out["flat_sky_only"] = wl.card_read("flat")
out["removed_after"] = wl.temp_clear()
out["dirty"] = wl.dirty()
out["file"] = wl.write_json("brightness_readings.json", out)
json.dumps(out)
