import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.append(T)
import unreal
import wieland_lighting as wl
importlib.reload(wl)

# J6: one temporary light 1 m above the card in open air, sun and sky light off for the duration.
IES = ("/Game/Wieland1529/Building/Datasmith/25-006_1527_N_Wieland-3DView-3D_View_188/Textures/"
       "LDT_File_-_DOWNLED_20W_V_2_FLP_IES")
out = {"windows_restored": wl.window_restore(), "removed_before": wl.temp_clear()}
sun = wl.by_label("LGT_Sun").light_component
sky = wl.by_label("LGT_SkyLight").light_component
profile = unreal.load_asset(IES)
out["file_asset"] = {"class": profile.get_class().get_name(), "brightness": profile.get_editor_property("brightness"),
                     "multiplier": profile.get_editor_property("texture_multiplier")}
sun.set_visibility(False)
sky.set_visibility(False)
try:
    wl.card_place("flat", wl.OPEN_AIR)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    where = unreal.Vector(wl.OPEN_AIR[0], wl.OPEN_AIR[1], wl.OPEN_AIR[2] + 100.0)
    actor = subsystem.spawn_actor_from_class(unreal.PointLight, where, unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0))
    actor.set_actor_label("TEMP_test_light")
    actor.tags = [wl.TAG_TEMP, "testlight"]
    light = actor.light_component
    light.set_mobility(unreal.ComponentMobility.MOVABLE)
    light.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    light.set_editor_property("attenuation_radius", 1000.0)
    await wl.wait_frames(3.0)
    out["dark"] = wl.card_read("flat")["lux"]

    async def case(name, lumens, file_asset, use_file, scale=1.0, rotation=None):
        light.set_editor_property("ies_texture", file_asset)
        light.set_editor_property("use_ies_brightness", use_file)
        light.set_editor_property("ies_brightness_scale", scale)
        light.set_editor_property("intensity", lumens)
        actor.set_actor_rotation(rotation or unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0), False)
        await wl.wait_frames(3.0)
        reading = wl.card_read("flat")
        out[name] = {"lux": round(reading["lux"], 2), "set_lumens": lumens, "file": bool(file_asset), "brightness_from_file": use_file,
                     "intensity_after": light.intensity}

    await case("a_no_file_1000_lm", 1000.0, None, False)
    await case("b_file_2231_lm_own_value", 2231.0, profile, False)
    await case("c_file_brightness_from_file", 2231.0, profile, True)
    await case("c2_file_brightness_from_file_other_lumens", 500.0, profile, True)
    await case("d_file_own_value_light_axis_level", 2231.0, profile, False, 1.0, unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
    await case("e_file_own_value_light_axis_up", 2231.0, profile, False, 1.0, unreal.Rotator(pitch=90.0, yaw=0.0, roll=0.0))
    await case("g_file_brightness_from_file_scale_4pi", 2231.0, profile, True, 12.566371)
    light.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
    await case("f_file_own_value_in_candela_795", 794.91, profile, False)
    await case("h_no_file_candela_795", 794.91, None, False)
finally:
    out["removed_after"] = wl.temp_clear()
    sun.set_visibility(True)
    sky.set_visibility(True)
await wl.wait_frames(2.0)
out["sun_and_sky_back"] = [bool(sun.is_visible()), bool(sky.is_visible())]
out["check_after"] = (await wl.daylight_readings(5.0, False))["short"]
out["dirty"] = wl.dirty()
out["file"] = wl.write_json("photometric_file_test.json", out)
json.dumps(out)
