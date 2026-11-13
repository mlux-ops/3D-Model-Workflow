"""Phase 13 (closing check of the material rule): the hotel's materials under grazing light and under the review sun.

Close views from points in site feet (wieland_hotel.picture, editor viewport, nothing placed), each taken twice: with
the project's sun LGT_Sun turned to a raking direction 8 degrees above the horizon, nearly parallel to the face looked
at, and with the sun at the review condition (15 August 2026, 15:30). At the end the sun is put back to the review
condition and read back. The grazing pictures are taken with the outdoor exposure lowered to EV 11.5 (the low sun
gives far less light on the face than the fixed daylight EV 14.644 expects); the exposure is put back and read back.
Nothing is saved.
Run: python -B tools/ue_call.py py review/phase13/scripts/grazing.py 600 -> review/phase13/grazing/*.png
"""
import json
import sys

sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_hotel as wh

OUT = wh.PLAN + "/review/phase13/grazing"
# name: (east, north, up, yaw, pitch, raking sun bearing, what is looked at)
SHOTS = {
    "wells_red_brick": (222.0, -40.0, 45.0, 90.0, 5.0, 180.0, "red brick of the north wing, Wells face (faces east)"),
    "wells_dark_brick": (222.0, -105.0, 45.0, 90.0, 5.0, 0.0, "dark grey projecting part, Wells face (faces east)"),
    "west_dark_bay": (40.0, -86.0, 70.0, -90.0, 5.0, 180.0, "west face of the tower: dark middle bay and red side bays (faces west)"),
    "green_roof": (40.0, -30.0, 55.0, 0.0, -35.0, 270.0, "planted roof of the garage (horizontal)"),
    "penthouse_metal": (118.0, -47.0, 147.0, 0.0, 0.0, 270.0, "metal panel of the mechanical penthouse, north face"),
}


def sun(bearing, height):
    wl.by_label("LGT_Sun").set_actor_rotation(wl.sun_rotation(bearing, height), False)


def review_sun():
    c = wl.CONDITIONS["SummerAfternoon"]
    data = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, c[6], c[7], c[1], c[2], c[3], c[4], c[5], 0)
    height = data.corrected_elevation - 180.0 if data.corrected_elevation > 90.0 else data.corrected_elevation
    sun(data.azimuth, height)


EXPOSURE = "LGT_Exposure_Outdoors"
out = {"state": wh.state(), "shots": [], "exposure_before": wl.read_exposure(EXPOSURE)}
ev_before = out["exposure_before"]["ev100"]
try:
    for name, (east, north, up, yaw, pitch, bearing, what) in SHOTS.items():
        sun(bearing, 8.0)
        wl.set_exposure(EXPOSURE, 11.5)
        a = await wh.picture("%s/%s_grazing.png" % (OUT, name), east, north, up, yaw, pitch, settle=4.0)
        review_sun()
        wl.set_exposure(EXPOSURE, ev_before)
        b = await wh.picture("%s/%s_review.png" % (OUT, name), east, north, up, yaw, pitch, settle=4.0)
        out["shots"].append([name, what, bearing, a, b])
finally:
    review_sun()
    wl.set_exposure(EXPOSURE, ev_before)
    out["exposure_after"] = wl.read_exposure(EXPOSURE)
    out["sun_after"] = wl.read_sun()
json.dumps(out, default=str)
