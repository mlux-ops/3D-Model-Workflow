import sys, importlib, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.append(T)
import unreal
import wieland_site as ws
import wieland_lighting as wl
importlib.reload(wl)

# J4: fog at 0.005, then the cloud layer added with the engine's own cloud material; readings without and
# with it, and pictures from S1, S2, S6 and S9. Nothing is saved here.
out = {"windows_restored": wl.window_restore()}
FOG = unreal.ExponentialHeightFogComponent
CLOUD = unreal.VolumetricCloudComponent
wl.props("LGT_HeightFog", FOG, [], {"fog_density": 0.005})
out["before_cloud"] = (await wl.daylight_readings(5.0, True))["short"]
out["add"] = wl.add_to_lighting(unreal.VolumetricCloud, "LGT_Clouds")
names = ["layer_bottom_altitude", "layer_height", "tracing_start_max_distance", "tracing_max_distance", "material",
         "view_sample_count_scale", "reflection_view_sample_count_scale_value", "shadow_view_sample_count_scale",
         "use_per_sample_atmospheric_light_transmittance", "sky_light_cloud_bottom_occlusion", "visible"]
out["cloud"] = wl.props("LGT_Clouds", CLOUD, names)
sun = wl.by_label("LGT_Sun").light_component
out["sun_cloud_shadow"] = {k: str(sun.get_editor_property(k)) for k in ("cast_cloud_shadows", "cast_shadows_on_clouds", "cast_shadows_on_atmosphere")}
out["with_cloud"] = (await wl.daylight_readings(5.0, True))["short"]
ws.shots_begin(3)
try:
    out["shots"] = str(await ws.shots(["S1", "S2", "S6", "S9"], wl.REVIEW + "/sky", "_j4_cloud", 1280, 720))
finally:
    ws.shots_end()
out["dirty"] = wl.dirty()
json.dumps(out)
