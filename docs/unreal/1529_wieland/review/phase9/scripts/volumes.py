import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_optimize as wo
# Phase 9, step 9.4: read the Lumen, reflection and ray-tracing settings every post-process volume holds
# (only those whose override flag is on). Reads only; changes nothing.
NAMES = ["lumen_ray_lighting_mode", "lumen_scene_lighting_quality", "lumen_scene_detail", "lumen_scene_view_distance",
         "lumen_scene_lighting_update_speed", "lumen_final_gather_quality", "lumen_final_gather_lighting_update_speed",
         "lumen_max_trace_distance", "lumen_reflection_quality", "lumen_max_reflection_bounces",
         "lumen_max_roughness_to_trace_reflections", "lumen_max_refraction_bounces", "lumen_front_layer_translucency_reflections",
         "lumen_surface_cache_resolution", "lumen_full_skylight_leaking_distance", "lumen_skylight_leaking",
         "lumen_diffuse_color_boost", "dynamic_global_illumination_method", "reflection_method", "translucency_type",
         "ray_tracing_translucency_refraction", "ray_tracing_translucency_max_roughness", "mega_lights",
         "ray_tracing_ao", "path_tracing_max_bounces"]
out = {}
for actor in wo.actors():
    if not isinstance(actor, unreal.PostProcessVolume):
        continue
    settings = actor.get_editor_property("settings")
    held = {}
    for name in NAMES:
        flag = wo.OVERRIDE_NAMES.get(name, "override_" + name)
        try:
            if settings.get_editor_property(flag):
                held[name] = str(settings.get_editor_property(name))
        except Exception as error:
            held[name] = "unreadable: %s" % str(error)[:60]
    origin, extent = actor.get_actor_bounds(False)
    out[actor.get_actor_label()] = {"level": wo.level_of(actor).split("/")[-1], "unbound": bool(actor.get_editor_property("unbound")),
                                    "enabled": bool(actor.get_editor_property("enabled")),
                                    "priority": actor.get_editor_property("priority"),
                                    "blend_radius": actor.get_editor_property("blend_radius"),
                                    "centre_cm": [round(origin.x), round(origin.y), round(origin.z)],
                                    "half_size_cm": [round(extent.x), round(extent.y), round(extent.z)], "held": held}
json.dumps(out)
