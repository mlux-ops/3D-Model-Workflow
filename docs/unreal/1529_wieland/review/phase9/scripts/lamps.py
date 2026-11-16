import sys, json, importlib
sys.dont_write_bytecode = True
import unreal
# Phase 9: count the lamps as the editor holds them now. Reads only; changes nothing.
# Per level: light components, how many are lit (visible, affecting the world, intensity above 0), how many of the
# lit cast shadows, how many actors are hidden in the editor, and the sum of the lit intensities by unit.
out = {}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    level = actor.get_outer().get_outermost().get_name().split("/")[-1]
    for component in actor.get_components_by_class(unreal.LocalLightComponent):
        entry = out.setdefault(level, {"lights": 0, "lit": 0, "lit_cast_shadow": 0, "actor_hidden_in_editor": 0, "not_visible": 0,
                                       "not_affecting_world": 0, "zero_intensity": 0, "intensity_sum": {}, "mega_lights_allowed": 0})
        entry["lights"] += 1
        hidden = actor.is_temporarily_hidden_in_editor() or actor.is_hidden_ed()
        visible = component.is_visible()
        affects = bool(component.get_editor_property("affects_world"))
        intensity = float(component.get_editor_property("intensity"))
        entry["actor_hidden_in_editor"] += 1 if hidden else 0
        entry["not_visible"] += 0 if visible else 1
        entry["not_affecting_world"] += 0 if affects else 1
        entry["zero_intensity"] += 1 if intensity <= 0 else 0
        if visible and affects and intensity > 0 and not hidden:
            entry["lit"] += 1
            entry["lit_cast_shadow"] += 1 if component.get_editor_property("cast_shadows") else 0
            unit = str(component.get_editor_property("intensity_units")).split(".")[-1].split(":")[0]
            entry["intensity_sum"][unit] = round(entry["intensity_sum"].get(unit, 0.0) + intensity, 1)
            try:
                entry["mega_lights_allowed"] += 1 if component.get_editor_property("allow_mega_lights") else 0
            except Exception:
                entry["mega_lights_allowed"] = "unreadable"
json.dumps(out)
