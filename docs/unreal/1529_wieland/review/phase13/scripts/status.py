"""Phase 13, read-only: what the editor has open, what is unsaved, and the settings that must hold."""
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
levels = [level.get_outermost().get_name() for level in unreal.EditorLevelUtils.get_levels(world)]
dirty = [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
dirty += [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
result = {
    "world": world.get_path_name(),
    "levels": levels,
    "objects": len(actors),
    "unsaved": dirty,
    "r.RayTracing.Nanite.Mode": unreal.SystemLibrary.get_console_variable_int_value("r.RayTracing.Nanite.Mode"),
    "r.Material.UseShaderCompilationParameters": unreal.SystemLibrary.get_console_variable_int_value("r.Material.UseShaderCompilationParameters"),
}
result
