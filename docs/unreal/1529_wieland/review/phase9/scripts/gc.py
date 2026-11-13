import json
import unreal
# Phase 9: free what the editor no longer uses (garbage collection), to raise free commit before a heavy step.
# Changes no asset and saves nothing.
unreal.SystemLibrary.collect_garbage()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "r.Streaming.PoolSize")
json.dumps({"collected": True, "unsaved_packages": [str(p.get_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
            + [str(p.get_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]})
