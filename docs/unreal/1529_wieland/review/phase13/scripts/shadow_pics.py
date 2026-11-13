"""Phase 13, step 13.7: plan-view pictures (station S8's camera, 80 m straight above the lot, north up) of the
hotel's shadow on 15 August 2026 at 09:00, 12:30 and 15:30 CDT, with both options of "Neighbour development".

The project's sun LGT_Sun is turned for each clock time from the Sun Position plugin, exposure stays at the
project's fixed daylight value; at the end the sun goes back to the review condition (15 August, 15:30) and is
read back, the temporary camera is removed and the proposed option is put back on. Nothing is saved.
Run: python -B tools/ue_call.py py review/phase13/scripts/shadow_pics.py 900
Pictures: review/phase13/shadow/<option>/S8_realtime_<hhmm>.0000.png
"""
import json
import os
import sys

sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
import wieland_hotel as wh

BASE = wh.PLAN + "/review/phase13/shadow"
TIMES = [(9, 0), (12, 30), (15, 30)]


def set_sun(hour, minute):
    data = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, -6.0, True, 2026, 8, 15, hour, minute, 0)
    height = data.corrected_elevation - 180.0 if data.corrected_elevation > 90.0 else data.corrected_elevation
    wl.by_label("LGT_Sun").set_actor_rotation(wl.sun_rotation(data.azimuth, height), False)
    return {"bearing": round(data.azimuth, 2), "height": round(height, 2)}


out = {"sun_before": wl.read_sun(), "runs": []}
unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
try:
    for key, option in (("existing", wh.OPTION_EXISTING), ("proposed", wh.OPTION_PROPOSED)):
        wh.switch(option)
        folder = BASE + "/" + key
        os.makedirs(folder, exist_ok=True)
        for hour, minute in TIMES:
            sun = set_sun(hour, minute)
            wt.begin("S8")
            await wl.wait_frames(10.0)
            record = await wt.render("S8", "rt", folder, 1920, 1080, suffix="_%02d%02d" % (hour, minute), warm_up_frames=64)
            out["runs"].append([key, "%02d:%02d" % (hour, minute), sun, record.get("file_bytes"), record.get("seconds_waited")])
finally:
    out["end"] = wt.end()
    c = wl.CONDITIONS["SummerAfternoon"]
    out["sun_restored_to"] = set_sun(c[4], c[5])
    out["sun_after"] = wl.read_sun()
    out["switch"] = wh.switch(wh.OPTION_PROPOSED)
    out["nanite"] = unreal.SystemLibrary.get_console_variable_int_value("r.RayTracing.Nanite.Mode")
json.dumps(out, default=str)
