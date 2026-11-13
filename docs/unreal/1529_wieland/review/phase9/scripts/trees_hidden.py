import sys, json, os
sys.dont_write_bytecode = True
import unreal
# Phase 9 diagnostic: hide or show the 34 trees in the editor only (the "temporarily hidden" flag, which is not
# saved with a level). The wanted state is read from review/phase9/scripts/trees_hidden.txt ("1" hides, "0" shows).
HERE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase9/scripts"
with open(HERE + "/trees_hidden.txt") as handle:
    hide = handle.read().strip() == "1"
count = 0
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if any(str(tag) == "W1529.Tree" for tag in actor.tags):
        actor.set_is_temporarily_hidden_in_editor(hide)
        count += 1
dirty = [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
json.dumps({"trees": count, "hidden": hide, "dirty_maps": dirty})
