import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl
import wieland_truth as wt
import wieland_rebuild as wr
# After the renders: the temporary camera of each picture was placed in and removed from the top level
# /Game/Wieland1529/L_Site_M4, which leaves that level marked as unsaved. It is saved by name, and only if it
# is the one unsaved package and no temporary camera is left in it.
NAME = "/Game/Wieland1529/L_Site_M4"
before = wr.dirty()
cameras = [a.get_actor_label() for a in wl.actors() if a.get_actor_label() == wt.CAMERA_LABEL]
saved = False
if before == [NAME] and not cameras:
    package = unreal.load_package(NAME)
    saved = unreal.EditorLoadingAndSavingUtils.save_packages([package], True)
json.dumps({"unsaved_before": before[:10], "temporary_cameras": cameras, "saved": saved, "unsaved_after": wr.dirty()[:10],
            "nanite": wt.cvar(wt.NANITE_MODE)})
