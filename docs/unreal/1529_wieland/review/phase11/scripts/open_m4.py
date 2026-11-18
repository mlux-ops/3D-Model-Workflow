"""Phase 11: open the top level L_Site_M4 (after an editor restart, which opens the earlier production level)."""
import sys, json, datetime
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
ok = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Wieland1529/L_Site_M4')
meshes = {}
for actor in wl.actors():
    if actor.get_actor_label() in ("SG_lot_placeholder", "FAR_CityStandIn"):
        meshes[actor.get_actor_label()] = actor.static_mesh_component.static_mesh.get_name()
json.dumps({"loaded": bool(ok), "world": wl.world_path(), "actors": len(wl.actors()), "dirty": wl.dirty(), "meshes": meshes,
            "nanite_mode": unreal.SystemLibrary.get_console_variable_float_value("r.RayTracing.Nanite.Mode"),
            "at": datetime.datetime.now().strftime("%H:%M:%S")})
