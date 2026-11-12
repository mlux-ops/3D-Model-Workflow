"""Phase 8: the lighting level, the sun, physical brightness and fixed exposure.

Runs inside the Unreal editor's Python. Nothing here edits an asset that Datasmith created.
The lighting of one condition lives in its own level under /Game/Wieland1529/Lighting, which the
top level loads always. Level axes of this project: north is -X, east is -Y, up is +Z, and the
lot's front line runs 1.18 degrees west of true north, so a compass bearing B (degrees clockwise
from true north) is the level yaw B - 178.82.
"""
import asyncio
import csv
import json
import math
import os

import unreal

MASTER_LEVEL = "/Game/Wieland1529/L_Site_M4"
SITE_LEVEL = "/Game/Wieland1529/L_Site_M2"
OLD_LEVEL = "/Game/Wieland/R15_Landscape/L_R15_Production"
LIGHT_FOLDER = "/Game/Wieland1529/Lighting"
CONDITIONS = {
    # name: (level asset, year, month, day, hour, minute, time zone, daylight saving)
    "SummerAfternoon": (LIGHT_FOLDER + "/L_Light_SummerAfternoon", 2026, 8, 15, 15, 30, -6.0, True),
}
LATITUDE = 41.910215
LONGITUDE = -87.635389
BEARING_TO_YAW = -178.82
NOAA = {"SummerAfternoon": (241.67, 46.34)}  # bearing, height; read from the NOAA page in Phase 1
TAG_GENERATED = "W1529.Generated"
TAG_LIGHTING = "W1529.Lighting"
TAG_PLACEHOLDER = "W1529.Placeholder"
TAG_TEMP = "W1529TempLightCheck"
ACTOR_FOLDER = "W1529_Lighting"
REVIEW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "review", "phase8").replace(os.sep, "/")
CARD_MATERIAL = "/Game/Wieland1529/Scratch/M_P1_Lambert50"
CARD_PER_1000_LUX = 153.375  # Phase 1, step 1.11: what this card reads through this camera under 1,000 lux


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def world_path():
    return world().get_path_name().split(".")[0]


def actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def level_of(actor):
    return actor.get_outer().get_outermost().get_name()


def levels():
    return [level.get_outermost().get_name() for level in unreal.EditorLevelUtils.get_levels(world())]


def dirty():
    utils = unreal.EditorLoadingAndSavingUtils
    return [p.get_name() for p in utils.get_dirty_map_packages()] + [p.get_name() for p in utils.get_dirty_content_packages()]


def _current(level_path):
    return bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(level_path.split("/")[-1]))


def _spawn(cls, label, tags, location=(0.0, 0.0, 0.0), rotation=None):
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_class(cls, unreal.Vector(*location), rotation or unreal.Rotator())
    actor.set_actor_label(label)
    actor.tags = list(tags)
    actor.set_folder_path(ACTOR_FOLDER)
    return actor


def by_label(label, level_path=None):
    for actor in actors():
        if actor.get_actor_label() == label and (level_path is None or level_of(actor) == level_path):
            return actor
    return None


# ---------------------------------------------------------------------------------------------
# The sun.

def sun_calc(condition="SummerAfternoon"):
    """Bearing and height of the sun from the Sun Position plugin's own calculation."""
    _, year, month, day, hour, minute, zone, saving = CONDITIONS[condition]
    data = unreal.SunPositionFunctionLibrary.get_sun_position(LATITUDE, LONGITUDE, zone, saving, year, month, day, hour, minute, 0)
    # The plugin returns the height plus 180 degrees; that convention is removed here (Phase 1, step 1.10).
    height = data.corrected_elevation - 180.0 if data.corrected_elevation > 90.0 else data.corrected_elevation
    plain = data.elevation - 180.0 if data.elevation > 90.0 else data.elevation
    return {"bearing": data.azimuth, "height": height, "height_without_bending": plain}


def sun_rotation(bearing, height):
    """Rotation of a directional light whose light comes FROM the given bearing and height."""
    yaw = bearing + BEARING_TO_YAW + 180.0
    yaw = (yaw + 180.0) % 360.0 - 180.0
    return unreal.Rotator(pitch=-height, yaw=yaw, roll=0.0)


def read_sun(label="LGT_Sun"):
    """Bearing and height of the placed sun, worked out from the direction its light travels."""
    actor = by_label(label)
    if actor is None:
        return {"error": "no " + label}
    forward = actor.get_actor_forward_vector()
    to_sun = (-forward.x, -forward.y, -forward.z)
    height = math.degrees(math.asin(max(-1.0, min(1.0, to_sun[2]))))
    yaw = math.degrees(math.atan2(to_sun[1], to_sun[0]))
    bearing = (yaw - BEARING_TO_YAW) % 360.0
    return {"bearing": bearing, "height": height, "level": level_of(actor),
            "lux": actor.light_component.intensity, "visible": bool(actor.light_component.is_visible())}


def make_level(condition="SummerAfternoon"):
    """With L_Site_M4 open: make the lighting level of the condition, add it as always loaded, fill it."""
    if world_path() != MASTER_LEVEL:
        return {"error": "open " + MASTER_LEVEL + " first; open is " + world_path()}
    path = CONDITIONS[condition][0]
    out = {"level": path}
    if path not in levels():
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            streaming = unreal.EditorLevelUtils.add_level_to_world(world(), path, unreal.LevelStreamingAlwaysLoaded)
            out["added_existing"] = streaming is not None
        else:
            streaming = unreal.EditorLevelUtils.create_new_streaming_level(unreal.LevelStreamingAlwaysLoaded, path, False)
            out["created"] = streaming is not None
    if path not in levels():
        out["error"] = "the level is not loaded"
        return out
    out["current"] = _current(path)
    tags = [TAG_GENERATED, TAG_LIGHTING, TAG_LIGHTING + "." + condition]
    calc = sun_calc(condition)
    if by_label("LGT_Sun", path) is None:
        sun = _spawn(unreal.DirectionalLight, "LGT_Sun", tags, (0.0, 0.0, 3000.0), sun_rotation(calc["bearing"], calc["height"]))
        light = sun.light_component
        light.set_mobility(unreal.ComponentMobility.MOVABLE)
        light.set_editor_property("intensity", 100000.0)
        light.set_editor_property("atmosphere_sun_light", True)
        light.set_editor_property("atmosphere_sun_light_index", 0)
        light.set_editor_property("use_temperature", False)
        light.set_editor_property("light_source_angle", 0.5357)
        light.set_editor_property("cast_shadows", True)
    if by_label("LGT_SkyAtmosphere", path) is None:
        _spawn(unreal.SkyAtmosphere, "LGT_SkyAtmosphere", tags, (0.0, 0.0, 0.0))
    if by_label("LGT_SkyLight", path) is None:
        sky = _spawn(unreal.SkyLight, "LGT_SkyLight", tags, (0.0, 0.0, 3200.0))
        component = sky.light_component
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_editor_property("real_time_capture", True)
        component.set_editor_property("intensity", 1.0)
    if by_label("LGT_Exposure_Outdoors", path) is None:
        volume = _spawn(unreal.PostProcessVolume, "LGT_Exposure_Outdoors", tags, (0.0, 0.0, 0.0))
        volume.set_editor_property("unbound", True)
        volume.set_editor_property("priority", 0.0)
        set_exposure("LGT_Exposure_Outdoors", 14.5)
    _current(MASTER_LEVEL)
    out["sun_calc"] = calc
    out["sun_placed"] = read_sun()
    out["levels"] = len(levels())
    return out


def exposure_camera(ev100):
    """A camera setting that gives the exposure value at ISO 100: aperture f/8, shutter 1/x second."""
    fstop = 8.0
    shutter = (2.0 ** ev100) / (fstop * fstop)  # 1 / seconds
    return {"iso": 100.0, "fstop": fstop, "shutter_one_over_s": shutter}


def set_exposure(label, ev100):
    """Fixed exposure on a post-process volume: automatic exposure off, set as a camera (ISO 100, f/8, 1/x s)."""
    volume = by_label(label)
    if volume is None:
        return {"error": "no " + label}
    camera = exposure_camera(ev100)
    settings = volume.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_apply_physical_camera_exposure", True)
    settings.set_editor_property("auto_exposure_apply_physical_camera_exposure", True)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.0)
    settings.set_editor_property("override_camera_iso", True)
    settings.set_editor_property("camera_iso", camera["iso"])
    settings.set_editor_property("override_camera_shutter_speed", True)
    settings.set_editor_property("camera_shutter_speed", camera["shutter_one_over_s"])
    settings.set_editor_property("override_depth_of_field_fstop", True)
    settings.set_editor_property("depth_of_field_fstop", camera["fstop"])
    volume.set_editor_property("settings", settings)
    return read_exposure(label)


def read_exposure(label):
    volume = by_label(label)
    if volume is None:
        return {"error": "no " + label}
    s = volume.get_editor_property("settings")
    iso, shutter, fstop = s.camera_iso, s.camera_shutter_speed, s.depth_of_field_fstop
    ev100 = math.log2(fstop * fstop * shutter) - math.log2(iso / 100.0) - s.auto_exposure_bias
    return {"label": label, "method": str(s.auto_exposure_method), "physical_camera": bool(s.auto_exposure_apply_physical_camera_exposure),
            "iso": iso, "shutter_one_over_s": shutter, "fstop": fstop, "bias": s.auto_exposure_bias, "ev100": ev100,
            "unbound": bool(volume.unbound), "level": level_of(volume)}


# ---------------------------------------------------------------------------------------------
# The placeholder sun and sky of earlier phases: made not visible, never deleted.

def placeholders(visible=None):
    """State of the placeholder sun, sky and sky light in the open top level; with visible given, set it."""
    out = []
    for actor in actors():
        if TAG_PLACEHOLDER not in [str(t) for t in actor.tags]:
            continue
        if not isinstance(actor, (unreal.DirectionalLight, unreal.SkyLight, unreal.SkyAtmosphere)):
            continue
        components = actor.get_components_by_class(unreal.LightComponentBase) + actor.get_components_by_class(unreal.SkyAtmosphereComponent)
        before = [bool(c.is_visible()) for c in components]
        if visible is not None:
            actor.modify()
            for c in components:
                c.modify()
                c.set_visibility(bool(visible))
        out.append({"label": actor.get_actor_label(), "class": actor.get_class().get_name(), "level": level_of(actor),
                    "before": before, "after": [bool(c.is_visible()) for c in components]})
    return out


def record_placeholders(rows, out_csv=None):
    out_csv = out_csv or REVIEW + "/placeholder_overrides.csv"
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    new = not os.path.exists(out_csv)
    with open(out_csv, "a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new:
            writer.writerow(["object", "class", "in_level", "visible_before", "visible_after", "how", "to_undo"])
        for row in rows:
            writer.writerow([row["label"], row["class"], row["level"], row["before"], row["after"],
                             "component property Visible set by tools/wieland_lighting.py placeholders(False)",
                             "wieland_lighting.placeholders(True), then save the level by name"])
    return len(rows)


def save(paths):
    """Save the named loaded levels by name. Refuses the earlier production level and any temporary object."""
    left = [a.get_actor_label() for a in actors() if TAG_TEMP in [str(t) for t in a.tags]]
    if left:
        return {"error": "temporary objects are still in the level", "objects": left}
    out = {}
    for path in paths:
        if path == OLD_LEVEL or path not in levels():
            out[path] = "refused"
            continue
        package = unreal.find_package(path)
        out[path] = bool(unreal.EditorLoadingAndSavingUtils.save_packages([package], False)) if package else "no package"
    out["left_marked"] = dirty()
    return out


# ---------------------------------------------------------------------------------------------
# Reading light in lux: a 50 percent matte card and a capture camera (the method of Phase 1, step 1.11).

def card_place(name, location, facing_bearing=None, facing_height=90.0):
    """Put a 1 m card with its centre at the location. By default it lies flat, facing up; with a bearing
    and height its face points that way (for a card that faces the sun). A capture camera looks at it
    from the same side and angle as in Phase 1, so the Phase 1 calibration holds."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    _current(MASTER_LEVEL)
    if facing_bearing is None:
        rotation = unreal.Rotator()
    else:
        # The plane's face normal is its +Z. Pitch the plane so that +Z points at the bearing and height.
        yaw = facing_bearing + BEARING_TO_YAW
        rotation = unreal.Rotator(pitch=-(90.0 - facing_height), yaw=yaw, roll=0.0)
    card = subsystem.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location), rotation)
    card.set_actor_label("TEMP_card_" + name)
    card.tags = [TAG_TEMP, name]
    component = card.static_mesh_component
    component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Plane"))
    component.set_material(0, unreal.load_asset(CARD_MATERIAL))
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    transform = card.get_actor_transform()
    eye = transform.transform_location(unreal.Vector(-80.0, 0.0, 60.0))
    centre = card.get_actor_location()
    direction = centre - eye
    capture = subsystem.spawn_actor_from_class(unreal.SceneCapture2D, eye, direction.rotator())
    capture.set_actor_label("TEMP_capture_" + name)
    capture.tags = [TAG_TEMP, name]
    target = unreal.RenderingLibrary.create_render_target2d(world(), 128, 128, unreal.TextureRenderTargetFormat.RTF_RGBA32F)
    c = capture.capture_component2d
    c.set_editor_property("texture_target", target)
    c.set_editor_property("fov_angle", 20.0)
    c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR)
    c.set_editor_property("capture_every_frame", True)
    c.set_editor_property("always_persist_rendering_state", True)
    normal = transform.transform_vector(unreal.Vector(0.0, 0.0, 1.0))
    return {"card": card.get_actor_label(), "normal": [normal.x, normal.y, normal.z]}


def card_read(name):
    """The card's brightness at the centre pixel, and the lux that brightness means."""
    for actor in actors():
        tags = [str(t) for t in actor.tags]
        if TAG_TEMP in tags and name in tags and isinstance(actor, unreal.SceneCapture2D):
            target = actor.capture_component2d.texture_target
            pixel = unreal.RenderingLibrary.read_render_target_raw_pixel(world(), target, 64, 64)
            luminance = 0.2126 * pixel.r + 0.7152 * pixel.g + 0.0722 * pixel.b
            return {"r": pixel.r, "g": pixel.g, "b": pixel.b, "luminance": luminance,
                    "lux": luminance * 1000.0 / CARD_PER_1000_LUX}
    return {"error": "no capture named " + name}


def card_shade(name, location, to_sun_bearing, to_sun_height, distance=300.0, size=120.0):
    """A small black disc between the card and the sun, so that the card reads the sky alone."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    yaw = math.radians(to_sun_bearing + BEARING_TO_YAW)
    pitch = math.radians(to_sun_height)
    d = (math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch))
    where = unreal.Vector(location[0] + d[0] * distance, location[1] + d[1] * distance, location[2] + d[2] * distance)
    shade = subsystem.spawn_actor_from_class(unreal.StaticMeshActor, where,
                                             unreal.Rotator(pitch=-(90.0 - to_sun_height), yaw=to_sun_bearing + BEARING_TO_YAW, roll=0.0))
    shade.set_actor_label("TEMP_shade_" + name)
    shade.tags = [TAG_TEMP, name + "_shade"]
    component = shade.static_mesh_component
    component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Plane"))
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    shade.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 1.0))
    return shade.get_actor_label()


def temp_clear():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in list(actors()):
        if TAG_TEMP in [str(t) for t in actor.tags]:
            subsystem.destroy_actor(actor)
            removed += 1
    return removed


async def wait_frames(seconds=2.0):
    """Let the editor draw for a while (a capture needs some frames before bounced light settles)."""
    steps = int(seconds / 0.05)
    for _ in range(steps):
        await asyncio.sleep(0.05)
    return steps


def write_json(name, data):
    path = REVIEW + "/" + name
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1)
    return path
