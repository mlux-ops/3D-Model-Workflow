"""Phase 9: the editor-side runs of the optimization phase and of profile M7. Runs inside the Unreal editor's Python.

    import phase9_profile_m7 as m7
    await m7.run(folder, "B0", parts=("exterior", "triplex", "penthouse", "roofdeck"))
    m7.pose("S1", cvars)   # hold the camera at one station under the same conditions, for the GPU profiler tool
    m7.unpose()

The paths and holds are those of profiles M4 and M6 (tools/phase6_profile_m4.py). What differs from M6:
- "Tier conditions": screen percentage 82 in the editor's 2,038 by 1,198 viewport, which computes the same number
  of pixels (1.64 million) as the plan's real-time tier does (67 percent of 2,560 by 1,440).
- `label` names the state of the scene that is measured (B0 is the scene as Phase 12 left it); it replaces "M4" in
  the job names and is part of the file names, so that every state is kept beside the others.
- `cvars` sets console variables for one run only and puts them back.
"""

import asyncio
import json
import os

import unreal

import phase6_profile_m4 as m4
import wieland_interiors as wi
import wieland_lighting as wl
import wieland_levels as wlv
import wieland_profile as wp

TIER = {"r.Editor.Viewport.ScreenPercentage": 82}

# station: (the point whose streaming boxes decide which unit levels are shown, the hold job)
STATIONS = {
    "S1": (m4.PARTS["exterior"][0], {"kind": "view", "loc": [-754.4, 1400.0, 158.6], "rot": [8.0, -88.82, 0.0]}),
    "S2": (m4.PARTS["exterior"][0], {"kind": "view", "loc": [1745.6, 1400.0, 151.9], "rot": [8.0, -133.82, 0.0]}),
    "S6": (m4.PARTS["exterior"][0], {"kind": "view", "loc": [-3508.8, 210.0, 173.1], "rot": [8.0, 1.18, 0.0]}),
    "D2": (m4.PARTS["penthouse"][0], {"kind": "view", "loc": list(wi.DESIGN_VIEWS["D2"][0]), "target": list(wi.DESIGN_VIEWS["D2"][1])}),
    "D5": (m4.PARTS["triplex"][0], {"kind": "view", "loc": list(wi.DESIGN_VIEWS["D5"][0]), "target": list(wi.DESIGN_VIEWS["D5"][1])}),
}

_POSE_FILE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/") + "/../profiles/2026-11-13_M7/pose_settings_before.json"


def _world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def lighting():
    """Counts the lit fixture lights and those of them that cast shadows, and reads the sun."""
    out = {"fixture_lights_on": 0, "fixture_lights_casting_shadows": 0}
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if actor.get_actor_label() == "LGT_Sun":
            out["sun_lux"] = actor.get_component_by_class(unreal.DirectionalLightComponent).get_editor_property("intensity")
        if isinstance(actor, unreal.Light) and not isinstance(actor, unreal.DirectionalLight):
            component = actor.get_component_by_class(unreal.LightComponent)
            if component and component.is_visible() and component.get_editor_property("intensity") > 0:
                out["fixture_lights_on"] += 1
                if component.get_editor_property("cast_shadows"):
                    out["fixture_lights_casting_shadows"] += 1
    return out


def idle_seconds():
    """Seconds since the last keyboard or mouse input on this computer (Windows' own counter)."""
    import ctypes

    class LastInput(ctypes.Structure):
        _fields_ = [("size", ctypes.c_uint), ("time", ctypes.c_uint)]

    info = LastInput(ctypes.sizeof(LastInput), 0)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))
    return ((ctypes.windll.kernel32.GetTickCount() - info.time) & 0xFFFFFFFF) / 1000.0


def polite_front(idle_needed=30.0):
    """Put a minimized editor window back on screen, and ask the editor to the front only when it is not in front
    already and nobody has used keyboard or mouse for idle_needed seconds. On 2026-11-13 at 05:40 somebody was
    working in a browser on this computer while state C2 was recorded: the unconditional wp.to_front() of the
    earlier runs pressed the Alt key into their work every ten seconds, and they minimized the editor twice."""
    restored = wl.window_restore()
    in_front = bool(wp._foreground())
    idle = idle_seconds()
    asked = False
    if not in_front and idle >= idle_needed:
        asked = True
        in_front = bool(wp.to_front().get("front"))
    return {"restored": restored, "front": in_front, "asked": asked, "idle_seconds": round(idle, 1)}


def _apply(world, cvars):
    for name in m4.QUALITY:
        m4._set(world, name, 3)
    for name, value in list(m4.OTHER.items()) + list(cvars.items()):
        m4._set(world, name, value)
    unreal.SystemLibrary.execute_console_command(world, "DisableAllScreenMessages")
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
    unreal.EditorLevelLibrary.editor_set_game_view(True)


def _jobs(part, label):
    point, jobs = m4.PARTS[part]
    return point, [dict(job, name=job["name"].replace("M4_", label + "_", 1)) for job in jobs]


async def run(folder, label, parts=("exterior", "triplex", "penthouse", "roofdeck"), cvars=None, trial_seconds=None,
              only_holds=False, skip_first_walk=False, note=""):
    """Records the named parts one after the other. Puts every setting back. Returns a short record."""
    world = _world()
    os.makedirs(folder, exist_ok=True)
    cvars = dict(TIER if cvars is None else cvars)
    before = {name: m4._get(name) for name in m4.QUALITY + list(m4.OTHER) + list(cvars)}
    with open("%s/settings_before_%s.json" % (folder, label), "w", encoding="utf-8") as handle:
        json.dump(before, handle)
    size = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_size()
    lights = lighting()
    _apply(world, cvars)
    out = []
    try:
        for part in parts:
            point, jobs = _jobs(part, label)
            if only_holds:
                jobs = [job for job in jobs if job["kind"] == "view"]
            if skip_first_walk:
                jobs = [job for job in jobs if not job["name"].endswith("_first_walk")]
            if not jobs:
                continue
            if trial_seconds:
                jobs = [dict(jobs[0], seconds=float(trial_seconds), name=jobs[0]["name"] + "_trial")]
            shown = wlv.show_for(point)
            front = polite_front()
            restored = front["restored"]
            info = {"step": "Phase 9, state %s, part %s%s" % (label, part, (": " + note) if note else ""),
                    "level": world.get_path_name(),
                    "quality": "Epic (3), pool %s, screen percentage %s, t.MaxFPS 1000, Game View on"
                               % (cvars.get("r.Streaming.PoolSize", m4.OTHER["r.Streaming.PoolSize"]),
                                  cvars.get("r.Editor.Viewport.ScreenPercentage", m4.OTHER["r.Editor.Viewport.ScreenPercentage"])),
                    "view_mode": "Lit",
                    "lighting": "L_Light_SummerAfternoon: sun %s lux, sky, haze, fog, clouds, fixed exposure; %s fixture lights on, "
                                "%s of them casting shadows" % (lights.get("sun_lux"), lights["fixture_lights_on"],
                                                               lights["fixture_lights_casting_shadows"]),
                    "console_variables_for_this_run": cvars,
                    "viewport_pixels": [size.x, size.y], "unit_levels_shown": shown,
                    "materials": "Phase 12 active", "found_before": before, "foreground_attempt": front}
            path = "%s/capture_%s_%s.json" % (folder, label, part)
            if os.path.exists(path):
                os.remove(path)
            wp.start(jobs, path, info)
            ticks = 0
            while wp.status()["active"]:
                restored += polite_front()["restored"]
                ticks += 1
                await asyncio.sleep(2)
            out.append([part, shown, wp.status()["finished_jobs"], wp.status()["error"], {"times_window_restored": restored}])
    finally:
        for name, value in before.items():
            m4._set(world, name, value)
        unreal.EditorLevelLibrary.editor_set_game_view(False)
        wlv.show_all()
    await asyncio.sleep(1)
    now = {name: m4._get(name) for name in before}
    return {"label": label, "parts": out, "settings_put_back": now == before, "viewport_pixels": [size.x, size.y],
            "lighting": lights, "view_mode": str(unreal.AutomationLibrary.get_editor_active_viewport_view_mode())}


def pose(station, cvars=None):
    """Holds the camera at one station under the measuring conditions and leaves it there, so that the GPU profiler
    tool can be called from outside. The settings found are written to a file once; unpose() puts them back."""
    world = _world()
    cvars = dict(TIER if cvars is None else cvars)
    if not os.path.exists(_POSE_FILE):
        before = {name: m4._get(name) for name in m4.QUALITY + list(m4.OTHER) + list(cvars)}
        os.makedirs(os.path.dirname(_POSE_FILE), exist_ok=True)
        with open(_POSE_FILE, "w", encoding="utf-8") as handle:
            json.dump(before, handle)
    _apply(world, cvars)
    point, job = STATIONS[station]
    shown = wlv.show_for(point)
    wp._force_realtime()
    wp._place(job, 0.0)
    front = polite_front()
    size = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_size()
    return {"station": station, "shown": shown, "front": front, "viewport_pixels": [size.x, size.y], "cvars": cvars,
            "job": job}


def unpose():
    world = _world()
    if not os.path.exists(_POSE_FILE):
        return {"put_back": False, "reason": "no settings file"}
    with open(_POSE_FILE, encoding="utf-8") as handle:
        before = json.load(handle)
    for name, value in before.items():
        m4._set(world, name, value)
    unreal.EditorLevelLibrary.editor_set_game_view(False)
    wlv.show_all()
    os.remove(_POSE_FILE)
    return {"put_back": True, "settings": before}
