import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_optimize as wo
importlib.reload(wo)
# Phase 9: set or clear settings of post-process volumes of the lighting level, as asked in
# review/phase9/scripts/vol_set.json = {"volumes": {"<label>": {"values": {...}, "clear": [...]}}, "save": false}.
# A value written as "Enum:<EnumClass>.<NAME>" is turned into that enum value. Saves the lighting level by name
# only when "save" is true.
HERE = T.rsplit("/", 1)[0] + "/review/phase9/scripts"
with open(HERE + "/vol_set.json", encoding="utf-8") as handle:
    job = json.load(handle)


def value_of(value):
    if isinstance(value, str) and value.startswith("Enum:"):
        enum_class, name = value[5:].split(".")
        return getattr(getattr(unreal, enum_class), name)
    return value


out = {"before_unsaved": wo.dirty(), "volumes": {}}
for label, change in job.get("volumes", {}).items():
    values = {name: value_of(value) for name, value in change.get("values", {}).items()}
    out["volumes"][label] = wo.volume_settings(label, values, tuple(change.get("clear", [])))
if job.get("save"):
    out["save"] = wo.save_levels([wo.LIGHTING_LEVEL])
out["after_unsaved"] = wo.dirty()
wo.report(out)
