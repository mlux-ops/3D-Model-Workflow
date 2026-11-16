"""Phase 11: free the editor's memory without closing it (this session runs inside the editor's panel, so closing
the editor would end it). Refuses if anything is unsaved or a render is running; opens a new empty level (never
saved), collects garbage, and returns the open level and what is unsaved."""
import json
import unreal
utils = unreal.EditorLoadingAndSavingUtils
dirty = sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))
if dirty:
    raise RuntimeError("unsaved packages: %s" % dirty)
if unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering():
    raise RuntimeError("a render is running")
utils.new_blank_map(False)
unreal.SystemLibrary.collect_garbage()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
json.dumps({"open": world.get_path_name(), "dirty": sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))})
