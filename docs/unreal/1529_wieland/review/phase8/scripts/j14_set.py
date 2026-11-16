"""Phase 8, J14: with L_Site_M2 open, add the lighting level as always loaded, make the placeholder sun, sky
and sky light not visible (recorded in review/phase8/placeholder_overrides.csv), read back, and save
L_Site_M2 by name. Nothing else is saved."""
import json

import unreal

import wieland_lighting as wl

out = {"world": wl.world_path()}
light_level = wl.CONDITIONS["SummerAfternoon"][0]
if wl.world_path() != wl.SITE_LEVEL:
    out["error"] = "L_Site_M2 is not the open level"
else:
    if light_level not in wl.levels():
        streaming = unreal.EditorLevelUtils.add_level_to_world(wl.world(), light_level, unreal.LevelStreamingAlwaysLoaded)
        out["added"] = streaming is not None
    if light_level not in wl.levels():
        out["error"] = "the lighting level is not loaded"
    else:
        wl._current(wl.SITE_LEVEL)
        rows = wl.placeholders(False)
        out["placeholders"] = rows
        out["recorded"] = wl.record_placeholders([row for row in rows if row["before"] != row["after"]])
        out["sun"] = wl.read_sun()
        out["exposure"] = wl.read_exposure("LGT_Exposure_Outdoors")
        out["levels"] = sorted(wl.levels())
        out["dirty_before_save"] = wl.dirty()
        out["saved"] = wl.save([wl.SITE_LEVEL])
        out["dirty"] = wl.dirty()
json.dumps(out, default=str)
