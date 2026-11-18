import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_fixtures as wf
importlib.reload(wl)
importlib.reload(wf)

# J8 (b): one recessed can light, lit from the table, read with a card 1.5 m beneath it.
MODEL = wf.REVIEW + "/fixture_lights_before.csv"
ONE = "15876009"
DROP = 150.0
out = {"windows_restored": wl.window_restore(), "removed_before": wl.temp_clear()}
dry = wf.apply(MODEL, dry_run=True)
out["dry_run_all"] = {k: (v if not isinstance(v, list) else v[:12]) for k, v in dry.items()}
group = [m for (level, rid), ms in wf._groups().items() if rid == ONE for m in ms]
main = max(group, key=lambda m: m[1].intensity)
loc = main[1].get_world_location()
out["light_at"] = [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)]
out["lights_in_fixture"] = len(group)
sun = wl.by_label("LGT_Sun").light_component
sky = wl.by_label("LGT_SkyLight").light_component
sun.set_visibility(False)
sky.set_visibility(False)

def capture():
    for actor in wl.actors():
        tags = [str(t) for t in actor.tags]
        if wl.TAG_TEMP in tags and "under" in tags and isinstance(actor, unreal.SceneCapture2D):
            return actor.capture_component2d

async def read(name, gi):
    flags = [unreal.EngineShowFlagsSetting(show_flag_name="Tonemapper", enabled=False)]
    if not gi:
        flags.append(unreal.EngineShowFlagsSetting(show_flag_name="GlobalIllumination", enabled=False))
    capture().set_editor_property("show_flag_settings", flags)
    await wl.wait_frames(4.0)
    out[name] = round(wl.card_read("under")["lux"], 2)

try:
    wl.card_place("under", (loc.x, loc.y, loc.z - DROP))
    await read("a_before_dark_no_bounce", False)
    out["apply_with_body_shadow"] = {k: v for k, v in wf.apply(MODEL, only_revit_ids={ONE}, body_casts_shadow=True).items() if v}
    await read("b_lit_body_casts_shadow_no_bounce", False)
    out["apply_no_body_shadow"] = {k: v for k, v in wf.apply(MODEL, only_revit_ids={ONE}, body_casts_shadow=False).items() if v}
    await read("c_lit_body_no_shadow_no_bounce", False)
    await read("d_lit_body_no_shadow_with_bounce", True)
    comp = main[1]
    out["light_now"] = {"units": str(comp.get_editor_property("intensity_units")), "intensity": comp.intensity,
                        "forward": [round(v, 3) for v in comp.get_forward_vector().to_tuple()],
                        "mobility": str(comp.get_editor_property("mobility")), "visible": comp.is_visible(),
                        "file": comp.get_editor_property("ies_texture").get_name()}
    out["expected_direct_lux"] = round(comp.intensity / (DROP / 100.0) ** 2, 1)
finally:
    out["removed_after"] = wl.temp_clear()
    sun.set_visibility(True)
    sky.set_visibility(True)
out["dirty"] = wl.dirty()
out["file"] = wl.write_json("fixture_one_test.json", out)
json.dumps(out)
