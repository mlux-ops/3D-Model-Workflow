import sys, json
sys.dont_write_bytecode = True
import unreal

# Phase 9: which levels are loaded, whether each is shown in the editor, and how many objects each holds.
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
counts = {}
hidden = {}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    name = actor.get_outer().get_outermost().get_name()
    counts[name] = counts.get(name, 0) + 1
    if actor.is_temporarily_hidden_in_editor() or actor.is_hidden_ed():
        hidden[name] = hidden.get(name, 0) + 1
out = []
for level in unreal.EditorLevelUtils.get_levels(world):
    name = level.get_outermost().get_name()
    out.append({"level": name, "shown": bool(level.get_editor_property("is_visible")) if hasattr(level, "is_visible") else None,
                "objects": counts.get(name, 0), "hidden_objects": hidden.get(name, 0)})
tools = [name for name in dir(unreal.EditorLevelUtils) if "visib" in name.lower()]
json.dumps({"levels": out, "visibility_functions": tools})
