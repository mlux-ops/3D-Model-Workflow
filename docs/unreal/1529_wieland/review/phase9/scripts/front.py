import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import ctypes
import unreal
import wieland_profile as wp
# Phase 9: which window is in front, is the editor's main window minimised, and ask the editor to the front.
user = ctypes.windll.user32
out = {}


def title(window):
    buffer = ctypes.create_unicode_buffer(200)
    user.GetWindowTextW(window, buffer, 200)
    return buffer.value


front = user.GetForegroundWindow()
out["front_before"] = title(front)
own = wp._own_main_window()
out["editor_window"] = title(own) if own else None
out["editor_minimised"] = bool(user.IsIconic(own)) if own else None
if own and user.IsIconic(own):
    out["restored"] = bool(user.ShowWindow(own, 9))  # 9 = restore to the size it had before it was minimised
out["to_front"] = str(wp.to_front())
out["front_after"] = title(user.GetForegroundWindow())
out["editor_minimised_after"] = bool(user.IsIconic(own)) if own else None
viewport = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_viewport_size() if hasattr(unreal.UnrealEditorSubsystem, "get_viewport_size") else None
out["viewport"] = str(viewport)
out["status"] = wp.status()
json.dumps(out, default=str)
