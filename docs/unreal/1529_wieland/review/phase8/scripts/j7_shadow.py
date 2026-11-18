import sys, importlib, json, math
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.append(T)
import unreal
import wieland_lighting as wl
importlib.reload(wl)

# J7: the shadow of a 3 m pole on a flat board in open air, read from straight above.
POLE = 300.0          # cm
BOARD = 1200.0        # cm
PIXEL = 2.0           # cm per pixel
SIZE = 512            # pixels, so the picture covers 10.24 m
bearing, height = wl.NOAA["SummerAfternoon"]
length = POLE / math.tan(math.radians(height))
yaw = math.radians((bearing + 180.0) + wl.BEARING_TO_YAW)
along = (math.cos(yaw), math.sin(yaw))          # level direction in which the shadow points
across = (-along[1], along[0])
base = (wl.OPEN_AIR[0], wl.OPEN_AIR[1], wl.OPEN_AIR[2] + 400.0)
out = {"windows_restored": wl.window_restore(), "removed_before": wl.temp_clear(),
       "expected": {"length_cm": round(length, 1), "shadow_bearing": (bearing + 180.0) % 360.0, "along": along},
       "sun_as_placed": wl.read_sun()}
subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    def box(label, location, scale):
        actor = subsystem.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location), unreal.Rotator())
        actor.set_actor_label(label)
        actor.tags = [wl.TAG_TEMP, "shadowcheck"]
        component = actor.static_mesh_component
        component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube"))
        component.set_material(0, unreal.load_asset(wl.CARD_MATERIAL))
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        return actor

    # The engine's cube is 100 cm on a side with its centre at the actor's position.
    box("TEMP_shadow_board", (base[0], base[1], base[2] - 5.0), (BOARD / 100.0, BOARD / 100.0, 0.1))
    box("TEMP_shadow_pole", (base[0], base[1], base[2] + POLE / 2.0), (0.1, 0.1, POLE / 100.0))
    eye = unreal.Vector(base[0], base[1], base[2] + 2000.0)
    capture = subsystem.spawn_actor_from_class(unreal.SceneCapture2D, eye, unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0))
    capture.set_actor_label("TEMP_shadow_capture")
    capture.tags = [wl.TAG_TEMP, "shadowcheck"]
    target = unreal.RenderingLibrary.create_render_target2d(wl.world(), SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA32F)
    c = capture.capture_component2d
    c.set_editor_property("texture_target", target)
    c.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC)
    c.set_editor_property("ortho_width", SIZE * PIXEL)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_HDR)
    c.set_editor_property("show_flag_settings", [unreal.EngineShowFlagsSetting(show_flag_name="Tonemapper", enabled=False)])
    c.set_editor_property("capture_every_frame", True)
    c.set_editor_property("always_persist_rendering_state", True)
    await wl.wait_frames(6.0)
    right, up = capture.get_actor_right_vector(), capture.get_actor_up_vector()
    out["camera_axes"] = {"right": [round(right.x, 3), round(right.y, 3)], "up": [round(up.x, 3), round(up.y, 3)]}
    pixels = unreal.RenderingLibrary.read_render_target_raw(wl.world(), target, False)
    out["pixels_read"] = len(pixels)

    def value(dx, dy):
        """Brightness at a level offset (cm) from the pole's foot."""
        u = int(round(SIZE / 2.0 + (dx * right.x + dy * right.y) / PIXEL))
        v = int(round(SIZE / 2.0 - (dx * up.x + dy * up.y) / PIXEL))
        if not (0 <= u < SIZE and 0 <= v < SIZE):
            return None
        p = pixels[v * SIZE + u]
        return 0.2126 * p.r + 0.7152 * p.g + 0.0722 * p.b

    lengthwise = [(d, value(along[0] * d, along[1] * d)) for d in range(20, 440, 2)]
    sunlit = max(v for d, v in lengthwise if v is not None)
    shade = min(v for d, v in lengthwise if v is not None and d < 250)
    half = (sunlit + shade) / 2.0
    tip = None
    for (d0, v0), (d1, v1) in zip(lengthwise, lengthwise[1:]):
        if d0 >= 100 and v0 < half <= v1:
            tip = d0 + (half - v0) / (v1 - v0) * (d1 - d0)
            break
    out["sunlit"], out["shade"], out["tip_cm"] = sunlit, shade, tip
    # Sideways: across the shadow at 60 percent of its length, where is its middle?
    at = 0.6 * length
    sideways = [(s, value(along[0] * at + across[0] * s, along[1] * at + across[1] * s)) for s in range(-60, 62, 2)]
    dark = [s for s, v in sideways if v is not None and v < half]
    out["sideways_middle_cm"] = (min(dark) + max(dark)) / 2.0 if dark else None
    out["sideways_width_cm"] = (max(dark) - min(dark) + 2) if dark else None
    out["lengthwise_profile"] = [[d, round(v, 4)] for d, v in lengthwise if d % 10 == 0]
    out["sideways_profile"] = [[s, round(v, 4)] for s, v in sideways if s % 6 == 0]
    if tip is not None:
        out["tip_error_cm"] = round(tip - length, 1)
        if out["sideways_middle_cm"] is not None:
            # a sideways shift at 60 percent of the length grows in proportion to the tip
            out["tip_sideways_error_cm"] = round(out["sideways_middle_cm"] / 0.6, 1)
            out["bearing_error_deg"] = round(math.degrees(math.atan2(out["sideways_middle_cm"], at)), 2)
        out["height_from_shadow_deg"] = round(math.degrees(math.atan2(POLE, tip)), 2)
finally:
    out["removed_after"] = wl.temp_clear()
out["dirty"] = wl.dirty()
out["file"] = wl.write_json("shadow_check.json", out)
json.dumps(out)
