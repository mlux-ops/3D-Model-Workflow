"""Phase 18: orthographic top-view depth captures for the owner's path-drawing plans.

Runs inside the Unreal Editor's Python (it needs `unreal`, numpy and cv2, which the editor ships).
Every actor it spawns (one SceneCapture2D, marker cubes) is temporary and is removed again by
cleanup(); nothing is saved.

Image orientation (fixed by the drawing page's formula, see manifest.json):
  pixel u (right) follows world +X (south), pixel v (down) follows world +Y (west, toward the street).
  So the rear (east, -Y) is at the top, the street at the bottom, north (-X) on the left.
  A camera looking straight down with yaw -90 gives exactly that.
"""

import os

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")

import cv2
import numpy as np
import unreal

SIZE = 2048
TAG = "PH18_TEMP"
SCRATCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "review", "phase18", "scratch")


def world():
    return unreal.EditorLevelLibrary.get_editor_world()


def temp_actors():
    return [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if TAG in [str(t) for t in a.tags]]


def cleanup():
    """Remove the actors this script spawned (unsaved, never part of any level file)."""
    n = 0
    for a in temp_actors():
        unreal.EditorLevelLibrary.destroy_actor(a)
        n += 1
    return n


def _rt():
    rt = unreal.RenderingLibrary.create_render_target2d(world(), SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA32F)
    return rt


def capture_depth(cx, cy, cam_z, ortho_width, near_cm=0.0, show_only=None, look_up=False, name="cap"):
    """Orthographic depth capture centred on (cx, cy). Returns a SIZE x SIZE float array of
    distances (cm) from the camera plane; very large values mean nothing was hit."""
    os.makedirs(SCRATCH, exist_ok=True)
    pitch = 90.0 if look_up else -90.0
    rot = unreal.Rotator(roll=0.0, pitch=pitch, yaw=-90.0)
    act = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(cx, cy, cam_z), rot)
    act.tags = [unreal.Name(TAG)]
    comp = act.capture_component2d
    rt = _rt()
    comp.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC)
    comp.set_editor_property("ortho_width", float(ortho_width))
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_SCENE_DEPTH)
    comp.set_editor_property("capture_every_frame", False)
    comp.set_editor_property("capture_on_movement", False)
    comp.set_editor_property("auto_calculate_ortho_planes", False)
    comp.set_editor_property("override_custom_near_clipping_plane", True)
    comp.set_editor_property("custom_near_clipping_plane", float(near_cm))
    comp.set_editor_property("texture_target", rt)
    if show_only is not None:
        comp.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
        for a in show_only:
            comp.show_only_actor_components(a, True)
    comp.capture_scene()
    fn = name + ".exr"
    unreal.RenderingLibrary.export_render_target(world(), rt, SCRATCH, fn)
    img = cv2.imread(os.path.join(SCRATCH, fn), cv2.IMREAD_UNCHANGED)
    unreal.EditorLevelLibrary.destroy_actor(act)
    if img is None:
        raise RuntimeError("could not read " + fn)
    d = img[..., 2] if img.ndim == 3 else img  # cv2 is BGR(A); depth is in R
    d = d.astype(np.float64)
    if look_up:
        # Looking up with yaw -90 keeps +X to the right but puts +Y at the top: flip vertically.
        d = d[::-1, :]
    return d
