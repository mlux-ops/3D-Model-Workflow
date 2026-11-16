"""Phase 6, step 6.10: the jobs of profile M4 and the editor-side run. Runs inside the Unreal editor's Python.

    import phase6_profile_m4 as m4
    await m4.run(folder, parts=("exterior", "triplex", "penthouse", "roofdeck"))

The conditions are those of profiles M2, M3 and M5 (named quality Epic, screen percentage 100, texture pool
1,000, frame limit 1000, Game View on, view mode Lit, placeholder sun with sky), so that the numbers compare.

The two interior paths are defined here, because Phase 11 has not fixed them yet. They are provisional: straight
legs between room points of the north half at eye height (160 cm over each finished floor), with a short climb
where the storey changes. A leg can cross a wall or a floor; the stairs are not followed. Each is one continuous
30-second move at one speed:
  triplex    lower-level family room, up to the 1st floor living room, dining room, kitchen, up to the 2nd floor,
             primary bedroom to the rear bedroom, down and out: the last 10 seconds on the covered and uncovered patios
  penthouse  3rd floor front bedroom and hall, up to the 4th floor living room and kitchen (20 seconds),
             then the last 10 seconds on the roof deck
While a path is recorded, only those unit levels are shown that the streaming boxes load at that place (the editor
itself keeps every level in memory; in the running scene the boxes unload the others).
"""

import asyncio
import json
import os

import unreal

import wieland_interiors as wi
import wieland_levels as wl
import wieland_profile as wp

QUALITY = ["sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality", "sg.GlobalIlluminationQuality", "sg.ReflectionQuality",
           "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality", "sg.FoliageQuality", "sg.ShadingQuality", "sg.LandscapeQuality"]
OTHER = {"r.Streaming.PoolSize": 1000, "r.Editor.Viewport.ScreenPercentage": 100, "t.MaxFPS": 1000, "Slate.bAllowThrottling": 0, "r.VSync": 0}

EXTERIOR = {"kind": "path", "loc": [3745.62, 1403.7, 158.2], "end": [-4654.38, 1403.7, 158.2], "target": [-754.38, -311.1, 303.2], "seconds": 60.0}
Z = {"L": 7.6, "1": 363.2, "2": 688.3, "3": 1013.4, "4": 1338.6, "R": 1684.0}
# The triplex path: 20 seconds indoors, then 10 seconds on the patios (the legs are sized so that the speed is one).
TRIPLEX_IN = [[-1150.0, -1750.0, Z["L"]], [-1000.0, -1500.0, Z["L"]], [-1000.0, -1500.0, Z["1"]], [-1050.0, -1050.0, Z["1"]],
              [-1250.0, -560.0, Z["1"]], [-1050.0, -1050.0, Z["1"]], [-1050.0, -1050.0, Z["2"]], [-900.0, -950.0, Z["2"]],
              [-1100.0, -1950.0, Z["2"]], [-1180.0, -2180.0, Z["2"]], [-1180.0, -2180.0, Z["1"]], [-1190.0, -2262.0, Z["1"]]]
TRIPLEX_PATIO = [[-1190.0, -2262.0, Z["1"]], [-1190.0, -2800.0, Z["1"]], [-1000.0, -2990.0, Z["1"]], [-1300.0, -2990.0, Z["1"]],
                 [-1300.0, -2800.0, Z["1"]], [-1000.0, -2800.0, Z["1"]], [-1150.0, -2990.0, Z["1"]], [-1190.0, -2700.0, Z["1"]]]
PENTHOUSE_IN = [[-1050.0, -850.0, Z["3"]], [-1000.0, -1000.0, Z["3"]], [-1000.0, -2000.0, Z["3"]], [-1000.0, -2000.0, Z["4"]],
                [-1000.0, -1250.0, Z["4"]], [-960.0, -840.0, Z["4"]], [-1000.0, -1250.0, Z["4"]]]
ROOF_DECK = [[-1000.0, -1250.0, Z["R"]], [-1300.0, -1560.0, Z["R"]], [-1100.0, -2300.0, Z["R"]], [-900.0, -1700.0, Z["R"]]]

PARTS = {
    # part: (the point whose streaming boxes decide which unit levels are shown, the jobs)
    "exterior": ([-754.4, 1400.0, 158.6], [
        dict(EXTERIOR, name="M4_exterior_path_first_walk"),
        dict(EXTERIOR, name="M4_exterior_path"),
        {"kind": "view", "name": "M4_hold_S1", "loc": [-754.4, 1400.0, 158.6], "rot": [8.0, -88.82, 0.0], "seconds": 10.0},
        {"kind": "view", "name": "M4_hold_S2", "loc": [1745.6, 1400.0, 151.9], "rot": [8.0, -133.82, 0.0], "seconds": 10.0},
        {"kind": "view", "name": "M4_hold_S6", "loc": [-3508.8, 210.0, 173.1], "rot": [8.0, 1.18, 0.0], "seconds": 10.0}]),
    "triplex": ([-1100.0, -930.0, 363.0], [
        {"kind": "route", "name": "M4_triplex_path_first_walk", "points": TRIPLEX_IN + TRIPLEX_PATIO[1:], "seconds": 30.0},
        {"kind": "route", "name": "M4_triplex_path", "points": TRIPLEX_IN + TRIPLEX_PATIO[1:], "seconds": 30.0},
        {"kind": "view", "name": "M4_hold_D5", "loc": list(wi.DESIGN_VIEWS["D5"][0]), "target": list(wi.DESIGN_VIEWS["D5"][1]), "seconds": 10.0}]),
    "penthouse": ([-960.0, -840.0, 1339.0], [
        {"kind": "route", "name": "M4_penthouse_path_indoors_first_walk", "points": PENTHOUSE_IN, "seconds": 20.0},
        {"kind": "route", "name": "M4_penthouse_path_indoors", "points": PENTHOUSE_IN, "seconds": 20.0},
        {"kind": "view", "name": "M4_hold_D2", "loc": list(wi.DESIGN_VIEWS["D2"][0]), "target": list(wi.DESIGN_VIEWS["D2"][1]), "seconds": 10.0}]),
    "roofdeck": ([-1300.0, -1560.0, 1684.0], [
        {"kind": "route", "name": "M4_penthouse_path_roof_deck", "points": ROOF_DECK, "seconds": 10.0}]),
}


def length_m(points):
    return sum(sum((points[i + 1][k] - points[i][k]) ** 2 for k in range(3)) ** 0.5 for i in range(len(points) - 1)) / 100.0


def _get(name):
    return unreal.SystemLibrary.get_console_variable_float_value(name)


def _set(world, name, value):
    unreal.SystemLibrary.execute_console_command(world, "%s %s" % (name, int(value) if float(value) == int(value) else value))


async def run(folder, parts=("exterior", "triplex", "penthouse", "roofdeck"), tag="", trial_seconds=None):
    """Records the named parts one after the other. Puts every setting back. Returns a short record."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    os.makedirs(folder, exist_ok=True)
    before = {name: _get(name) for name in QUALITY + list(OTHER)}
    with open(folder + "/settings_before%s.json" % tag, "w", encoding="utf-8") as handle:
        json.dump(before, handle)
    size = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_size()
    sun = [a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label() == "Placeholder_Sun"]
    lux = sun[0].get_component_by_class(unreal.DirectionalLightComponent).get_editor_property("intensity") if sun else None
    for name in QUALITY:
        _set(world, name, 3)
    for name, value in OTHER.items():
        _set(world, name, value)
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
    unreal.EditorLevelLibrary.editor_set_game_view(True)
    out = []
    try:
        for part in parts:
            point, jobs = PARTS[part]
            jobs = [dict(job) for job in jobs]
            if trial_seconds:
                jobs = [dict(jobs[0], seconds=float(trial_seconds), name=jobs[0]["name"] + "_trial")]
            shown = wl.show_for(point)
            front = wp.to_front()
            info = {"step": "Phase 6, step 6.10: profile M4, part " + part, "level": world.get_path_name(),
                    "quality": "Epic (3), pool 1000, SP 100, t.MaxFPS 1000, Game View on", "view_mode": "Lit",
                    "lighting": "Placeholder_Sun %s lux, pitch -45, yaw -135, sky atmosphere and sky light; no interior lighting" % lux,
                    "viewport_pixels": [size.x, size.y], "unit_levels_shown": shown,
                    "site": "default after Phase 7: earlier detailed buildings, new ground, 34 trees leaf-on with wind, far city",
                    "interior_lists": "Revit as exported (kitchen, bath, floor)", "found_before": before, "foreground_attempt": front}
            path = "%s/capture_M4_%s%s.json" % (folder, part, tag)
            if os.path.exists(path):
                os.remove(path)
            wp.start(jobs, path, info)
            ticks = 0
            while wp.status()["active"]:
                if ticks % 5 == 0:
                    wp.to_front()
                ticks += 1
                await asyncio.sleep(2)
            out.append([part, shown, wp.status()["finished_jobs"], wp.status()["error"]])
    finally:
        for name, value in before.items():
            _set(world, name, value)
        unreal.EditorLevelLibrary.editor_set_game_view(False)
        wl.show_all()
    await asyncio.sleep(1)
    now = {name: _get(name) for name in before}
    return {"parts": out, "settings_put_back": now == before, "viewport_pixels": [size.x, size.y], "sun_lux": lux,
            "view_mode": str(unreal.AutomationLibrary.get_editor_active_viewport_view_mode())}
