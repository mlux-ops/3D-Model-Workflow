"""Phase 14: sun-path timelapse frames from two decks. Runs inside the editor (sent with tools/ue_call.py py).
Nothing is saved in the project: sun, exposure and camera are all temporary and put back by restore()."""
import sys, os, json, math, asyncio
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl

PLAN = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland"
OUT = PLAN + "/review/phase14"
FRAMES = OUT + "/frames"
SNAPSHOT = OUT + "/start_state.json"
# Cameras in level centimetres (+X is south, -Y is east). Yaw 1.18 looks due south (bearing = yaw + 178.82).
DECKS = {
    "roofdeck": {"name": "Penthouse roof deck", "loc": (-1300.0, -2150.0, 1684.0), "yaw": 1.18, "pitch": 15.0},
    "reardeck": {"name": "Rear patio deck", "loc": (-1370.0, -2800.0, 363.0), "yaw": 1.18, "pitch": 18.0},
}
DAYS = {
    "summer": {"label": "21 June 2026", "month": 6, "day": 21, "dst": True, "zone": "CDT"},
    "winter": {"label": "21 December 2026", "month": 12, "day": 21, "dst": False, "zone": "CST"},
}
# Exposure value stepped with the height of the sun (degrees -> EV at ISO 100); the fixed outdoor value is 14.644 above 25 degrees.
EV_STEPS = [(-5.0, 6.0), (0.0, 7.5), (5.0, 10.0), (10.0, 12.0), (15.0, 13.2), (25.0, 14.644)]
CAM_LABEL = "TEMP_P14_camera"
EXPOSURE_LABELS = ("LGT_Exposure_Outdoors", "LGT_Exposure_Interior_LowerTo3rd", "LGT_Exposure_Interior_4th")


def ev_for(height):
    if height <= EV_STEPS[0][0]:
        return EV_STEPS[0][1]
    for (h0, e0), (h1, e1) in zip(EV_STEPS, EV_STEPS[1:]):
        if height <= h1:
            return e0 + (e1 - e0) * (height - h0) / (h1 - h0)
    return EV_STEPS[-1][1]


def sun_at(day, hour):
    d = DAYS[day]
    h = int(math.floor(hour))
    m = int(math.floor((hour - h) * 60))
    s = int(round(((hour - h) * 60 - m) * 60))
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        h += 1
    data = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, -6.0, d["dst"], 2026, d["month"], d["day"], h, m, s)
    height = data.corrected_elevation - 180.0 if data.corrected_elevation > 90.0 else data.corrected_elevation
    return data, {"bearing": data.azimuth, "height": height}


def span_hours(span):
    d = span.to_dict()
    return d["days"] * 24.0 + d["hours"] + d["minutes"] / 60.0 + d["seconds"] / 3600.0 + d["milliseconds"] / 3600000.0


def sun_times(day):
    data, _ = sun_at(day, 12.0)
    return {"sunrise": span_hours(data.sunrise_time), "sunset": span_hours(data.sunset_time), "solar_noon": span_hours(data.solar_noon)}


def set_sun(day, hour):
    data, s = sun_at(day, hour)
    wl.by_label("LGT_Sun").set_actor_rotation(wl.sun_rotation(s["bearing"], s["height"]), False)
    return s


def set_ev(ev):
    return wl.set_exposure("LGT_Exposure_Outdoors", ev)


def clock(day, hour):
    h = int(hour)
    m = int(round((hour - h) * 60))
    if m == 60:
        h += 1
        m = 0
    return "%02d:%02d %s" % (h, m, DAYS[day]["zone"])


def camera(deck):
    cfg = DECKS[deck]
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in wl.actors():
        if a.get_actor_label() == CAM_LABEL:
            sub.destroy_actor(a)
    cam = sub.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*cfg["loc"]), unreal.Rotator(pitch=cfg["pitch"], yaw=cfg["yaw"], roll=0.0))
    cam.set_actor_label(CAM_LABEL)
    cam.tags = [wl.TAG_TEMP]
    comp = cam.get_component_by_class(unreal.CameraComponent)
    comp.set_editor_property("field_of_view", 100.0)
    comp.set_editor_property("aspect_ratio", 1920.0 / 1080.0)
    comp.set_editor_property("constrain_aspect_ratio", True)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.pilot_level_actor(cam)
    les.editor_set_viewport_realtime(True)
    return cam


def look(deck, yaw=None, pitch=None, loc=None):
    cfg = DECKS[deck]
    for a in wl.actors():
        if a.get_actor_label() == CAM_LABEL:
            a.set_actor_location(unreal.Vector(*(loc or cfg["loc"])), False, False)
            a.set_actor_rotation(unreal.Rotator(pitch=cfg["pitch"] if pitch is None else pitch, yaw=cfg["yaw"] if yaw is None else yaw, roll=0.0), False)
            return True
    return False


async def shoot(path, settle=1.0):
    await asyncio.sleep(settle)
    if os.path.exists(path):
        os.remove(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, path)
    waited = 0.0
    while not os.path.exists(path) and waited < 60.0:
        await asyncio.sleep(0.2)
        waited += 0.2
    await asyncio.sleep(0.2)
    return os.path.exists(path)


def snapshot_state():
    if os.path.exists(SNAPSHOT):
        return json.load(open(SNAPSHOT))
    snap = {"sun": wl.read_sun(), "exposure": {l: wl.read_exposure(l) for l in EXPOSURE_LABELS},
            "nanite": unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode")}
    json.dump(snap, open(SNAPSHOT, "w"), indent=1, default=str)
    return snap


def restore():
    """Sun to the review condition (15 August 2026, 15:30 CDT), exposure to what it was at the start; camera away."""
    snap = json.load(open(SNAPSHOT))
    out = {}
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    try:
        les.eject_pilot_level_actor()
    except Exception as e:
        out["eject"] = str(e)
    out["temp_removed"] = wl.temp_clear()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in wl.actors():
        if a.get_actor_label() == CAM_LABEL:
            sub.destroy_actor(a)
            out["temp_removed"] += 1
    c = wl.CONDITIONS["SummerAfternoon"]
    data = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, c[6], c[7], c[1], c[2], c[3], c[4], c[5], 0)
    height = data.corrected_elevation - 180.0 if data.corrected_elevation > 90.0 else data.corrected_elevation
    wl.by_label("LGT_Sun").set_actor_rotation(wl.sun_rotation(data.azimuth, height), False)
    wl.set_exposure("LGT_Exposure_Outdoors", snap["exposure"]["LGT_Exposure_Outdoors"]["ev100"])
    out["sun"] = wl.read_sun()
    out["exposure"] = {l: wl.read_exposure(l) for l in EXPOSURE_LABELS}
    out["nanite"] = unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode")
    out["dirty"] = wl.dirty()
    return out
