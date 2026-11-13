import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_hotel as wh
out = {}
for lab in ("LGT_Exposure_Outdoors", "LGT_Exposure_Interior_LowerTo3rd", "LGT_Exposure_Interior_4th"):
    v = wl.by_label(lab)
    r = wl.read_exposure(lab)
    o, e = v.get_actor_bounds(False)
    r["bounds_c"] = [round(o.x), round(o.y), round(o.z)]; r["bounds_half"] = [round(e.x), round(e.y), round(e.z)]
    r["priority"] = v.get_editor_property("priority"); r["blend_weight"] = v.get_editor_property("blend_weight"); r["enabled"] = v.get_editor_property("enabled")
    out[lab] = r
d = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, -6.0, True, 2026, 6, 21, 12, 0, 0)
out["fields"] = [x for x in dir(d) if not x.startswith("_")]
out["noon_jun"] = {k: str(getattr(d, k)) for k in out["fields"] if not callable(getattr(d, k))}
d = unreal.SunPositionFunctionLibrary.get_sun_position(wl.LATITUDE, wl.LONGITUDE, -6.0, False, 2026, 12, 21, 12, 0, 0)
out["noon_dec"] = {k: str(getattr(d, k)) for k in out["fields"] if not callable(getattr(d, k))}
out["hotel"] = wh.measure()
out["viewport"] = wl.window_restore()
json.dumps(out, default=str)
