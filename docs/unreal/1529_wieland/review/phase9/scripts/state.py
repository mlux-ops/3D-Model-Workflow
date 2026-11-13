import sys, json
sys.dont_write_bytecode = True
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
get = unreal.SystemLibrary.get_console_variable_float_value
names = ["r.RayTracing.Nanite.Mode", "r.Material.UseShaderCompilationParameters", "r.Editor.Viewport.ScreenPercentage",
         "r.ScreenPercentage", "r.Streaming.PoolSize", "t.MaxFPS", "r.MegaLights.EnableForProject", "r.MegaLights.Allowed",
         "r.Lumen.HardwareRayTracing", "r.Lumen.HardwareRayTracing.LightingMode", "r.Shadow.Virtual.Enable",
         "r.Shadow.Virtual.MaxPhysicalPages", "r.RayTracing.Shadows", "r.Lumen.WorldCache.Supported",
         "sg.ShadowQuality", "sg.GlobalIlluminationQuality", "sg.ReflectionQuality", "sg.FoliageQuality",
         "r.AntiAliasingMethod", "r.RayTracing.Nanite.MaxAppendInstances", "r.Lumen.Reflections.HardwareRayTracing.Translucent.Refraction.EnableForProject"]
size = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_size()
dirty = [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()] + \
        [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
levels = unreal.EditorLevelUtils.get_levels(world)
json.dumps({"world": world.get_path_name(), "levels": len(levels), "dirty": dirty, "viewport": [size.x, size.y],
            "cvars": {n: get(n) for n in names}})
