import sys
sys.dont_write_bytecode = True
TOOLS = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_site as ws
out = []
for actor in ws.actors():
    if actor.get_actor_label() in ("R15_InstancedTrees", "R15_InstancedLandscape", "SunSky", "PostProcessVolume", "ExponentialHeightFog"):
        for c in actor.get_components_by_class(unreal.ActorComponent):
            row = {"actor": actor.get_actor_label(), "component": c.get_name(), "class": c.get_class().get_name()}
            for prop in ("static_mesh", "skinned_asset", "skeletal_mesh"):
                try:
                    row[prop] = c.get_editor_property(prop).get_path_name()
                except Exception:
                    pass
            try:
                row["instances"] = c.get_instance_count()
            except Exception:
                pass
            out.append(row)
out
