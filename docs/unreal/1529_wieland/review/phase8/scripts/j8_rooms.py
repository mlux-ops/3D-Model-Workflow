import sys, importlib, json, math
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_fixtures as wf
importlib.reload(wl)
importlib.reload(wf)
# Illuminance at table height (80 cm above the floor) in six rooms, by day: fixtures on, then fixtures off.
ROOMS = {"D2_penthouse_4th_front": (-960.0, -840.0, 1178.6), "D3_triplex_1st_kitchen": (-1100.0, -930.0, 203.2),
         "D4_triplex_2nd": (-1375.0, -2020.0, 528.3), "D5_triplex_1st_living": (-1190.0, -2262.0, 203.2),
         "triplex_lower_family_room": (-1150.0, -1750.0, -152.4), "penthouse_3rd_hall": (-1000.0, -1000.0, 853.4)}
out = {"windows_restored": wl.window_restore(), "removed_before": wl.temp_clear(), "rooms": {}}
lit = [c for ms in wf._groups().values() for (_a, c, _f, _m) in ms if c.get_editor_property("visible")]
out["lights_lit"] = len(lit)
try:
    for name, (x, y, z) in ROOMS.items():
        wl.card_place(name, (x, y, z + 80.0))
    await wl.wait_frames(8.0)
    for name in ROOMS:
        out["rooms"][name] = {"lux_fixtures_on": round(wl.card_read(name)["lux"], 1)}
    for c in lit:
        c.set_visibility(False)
    await wl.wait_frames(8.0)
    for name in ROOMS:
        out["rooms"][name]["lux_daylight_only"] = round(wl.card_read(name)["lux"], 1)
finally:
    for c in lit:
        c.set_visibility(True)
    out["removed_after"] = wl.temp_clear()
for name, r in out["rooms"].items():
    for key in ("lux_fixtures_on", "lux_daylight_only"):
        lux = max(r[key], 0.01)
        r[key.replace("lux_", "ev100_for_middle_grey_")] = round(math.log2(lux * 0.18 / math.pi * 8.0), 2)
out["file"] = wl.write_json("room_readings.json", out)
json.dumps(out)
