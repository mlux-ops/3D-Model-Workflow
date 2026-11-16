import sys, json
sys.dont_write_bytecode = True
import unreal

# Phase 9, J2: where can the real-time settings be stored without touching a project settings file?
# Reads the post-process volumes of the lighting level and looks for a console-variable asset class. Changes nothing.
out = {"console_variables_asset_class": hasattr(unreal, "ConsoleVariablesAsset"),
       "console_variables_names": [n for n in dir(unreal) if "ConsoleVariables" in n][:12],
       "settings_fields_megalights": [n for n in dir(unreal.PostProcessSettings) if "mega" in n.lower()],
       "volumes": []}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(actor, unreal.PostProcessVolume):
        settings = actor.get_editor_property("settings")
        entry = {"label": actor.get_actor_label(), "level": actor.get_outer().get_outermost().get_name(),
                 "unbound": bool(actor.get_editor_property("unbound")), "priority": actor.get_editor_property("priority"),
                 "enabled": bool(actor.get_editor_property("enabled"))}
        for name in dir(unreal.PostProcessSettings):
            if name.startswith("override_"):
                try:
                    if settings.get_editor_property(name):
                        field = name[len("override_"):]
                        try:
                            entry[field] = str(settings.get_editor_property(field))
                        except Exception:
                            entry[field] = "set"
                except Exception:
                    pass
        out["volumes"].append(entry)
json.dumps(out)
