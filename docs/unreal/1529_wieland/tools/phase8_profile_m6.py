"""Phase 8, step 8.11: profile M6, the same paths and holds as profile M4 (tools/phase6_profile_m4.py) under the
Phase 8 lighting. Runs inside the Unreal editor's Python.

    import phase8_profile_m6 as m6
    await m6.run(folder, parts=("exterior", "triplex", "penthouse", "roofdeck"))

Conditions: as M4 (named quality Epic, screen percentage 100, texture pool 1,000, frame limit 1000, Game View on,
view mode Lit, editor brought to the front every 10 seconds), so that M6 minus M4 is the cost of the lighting.
What differs from M4 is the lighting alone: the summer-afternoon lighting level (sun 160,000 lux, sky, haze, fog,
clouds, fixed exposure) and the 314 lit fixture lights in the unit levels.

`cvars` sets console variables for one run only and puts them back; `tag` is added to the file names, so that a
variant (for example MegaLights on) is kept beside the plain run.
"""

import asyncio
import json
import os

import unreal

import phase6_profile_m4 as m4
import wieland_levels as wlv
import wieland_profile as wp


def _jobs(part):
    point, jobs = m4.PARTS[part]
    return point, [dict(job, name=job["name"].replace("M4_", "M6_", 1)) for job in jobs]


def _lighting():
    out = {}
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        label = actor.get_actor_label()
        if label == "LGT_Sun":
            out["sun_lux"] = actor.get_component_by_class(unreal.DirectionalLightComponent).get_editor_property("intensity")
        if isinstance(actor, unreal.Light) and not isinstance(actor, unreal.DirectionalLight):
            component = actor.get_component_by_class(unreal.LightComponent)
            if component and component.is_visible() and component.get_editor_property("intensity") > 0:
                out["fixture_lights_on"] = out.get("fixture_lights_on", 0) + 1
                if component.get_editor_property("cast_shadows"):
                    out["fixture_lights_casting_shadows"] = out.get("fixture_lights_casting_shadows", 0) + 1
    return out


async def run(folder, parts=("exterior", "triplex", "penthouse", "roofdeck"), tag="", trial_seconds=None, cvars=None,
              only_holds=False):
    """Records the named parts one after the other. Puts every setting back. Returns a short record."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    os.makedirs(folder, exist_ok=True)
    cvars = dict(cvars or {})
    before = {name: m4._get(name) for name in m4.QUALITY + list(m4.OTHER) + list(cvars)}
    with open(folder + "/settings_before%s.json" % tag, "w", encoding="utf-8") as handle:
        json.dump(before, handle)
    size = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_size()
    lighting = _lighting()
    for name in m4.QUALITY:
        m4._set(world, name, 3)
    for name, value in list(m4.OTHER.items()) + list(cvars.items()):
        m4._set(world, name, value)
    unreal.SystemLibrary.execute_console_command(world, "DisableAllScreenMessages")
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
    unreal.EditorLevelLibrary.editor_set_game_view(True)
    out = []
    try:
        for part in parts:
            point, jobs = _jobs(part)
            if only_holds:
                jobs = [job for job in jobs if job["kind"] == "view"]
                if not jobs:
                    continue
            if trial_seconds:
                jobs = [dict(jobs[0], seconds=float(trial_seconds), name=jobs[0]["name"] + "_trial")]
            shown = wlv.show_for(point)
            front = wp.to_front()
            info = {"step": "Phase 8, step 8.11: profile M6, part " + part + (", variant " + tag if tag else ""),
                    "level": world.get_path_name(),
                    "quality": "Epic (3), pool 1000, SP 100, t.MaxFPS 1000, Game View on", "view_mode": "Lit",
                    "lighting": "L_Light_SummerAfternoon: sun %s lux, sky atmosphere with haze, sky light, height fog, volumetric "
                                "clouds, fixed exposure (EV 14.64 outdoors, EV 9.0 indoors); %s fixture lights on, %s of them casting "
                                "shadows" % (lighting.get("sun_lux"), lighting.get("fixture_lights_on"),
                                             lighting.get("fixture_lights_casting_shadows")),
                    "console_variables_for_this_run": cvars,
                    "viewport_pixels": [size.x, size.y], "unit_levels_shown": shown,
                    "site": "default after Phase 7: earlier detailed buildings, new ground, 34 trees leaf-on with wind, far city",
                    "interior_lists": "as saved", "found_before": before, "foreground_attempt": front}
            path = "%s/capture_M6_%s%s.json" % (folder, part, tag)
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
            m4._set(world, name, value)
        unreal.EditorLevelLibrary.editor_set_game_view(False)
        wlv.show_all()
    await asyncio.sleep(1)
    now = {name: m4._get(name) for name in before}
    return {"parts": out, "settings_put_back": now == before, "viewport_pixels": [size.x, size.y], "lighting": lighting,
            "view_mode": str(unreal.AutomationLibrary.get_editor_active_viewport_view_mode())}
