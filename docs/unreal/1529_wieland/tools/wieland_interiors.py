"""Phase 6 (interiors) helpers for the 1529 N. Wieland scene. Runs inside the Unreal editor.

Nothing here edits an asset that Datasmith created and nothing here saves a level that
Datasmith owns. Temporary cameras are spawned with a tag and removed by views_end().

Frame of the level: origin at the lot's south-west corner, north is -X, east is -Y,
centimetres. The street is on the +Y side. The party line between the halves is X = -754.38.
"""

import math

import unreal

PARTY_X = -754.38
VIEW_FOV = 73.74  # 24 mm lens on a 36 mm wide frame
VIEW_TAG = "W1529TempDesignView"
REVIT_STAND_INS = ("Site_GRADE_GRADE", "Generic_Models_SURROUNDING_BUILDINGS_SURROUNDING_BUILDINGS")

# name: (camera location, point looked at). Eye height is 160 cm above the finished floor.
DESIGN_VIEWS = {
    "D1": ((-1300.0, -1560.0, 1684.0), (-900.0, -2300.0, 1640.0)),
    "D2": ((-960.0, -840.0, 1339.0), (-1200.0, -330.0, 1320.0)),
    "D3": ((-1100.0, -930.0, 363.0), (-1340.0, -560.0, 320.0)),
    "D4": ((-1375.0, -2020.0, 688.0), (-1250.0, -2210.0, 630.0)),
    "D5": ((-1190.0, -2262.0, 363.0), (-1190.0, -2800.0, 330.0)),
}

# Finished floor heights in cm: lower level, 1st, 2nd, 3rd, 4th floor and roof deck.
FLOOR_Z = {"L": -152.4, "1": 203.2, "2": 528.3, "3": 853.4, "4": 1178.6, "R": 1524.0}

# Rooms of the north half (the source half). name: (floor key, camera x, y, target x, y).
# The south half is the mirror of each across PARTY_X. Names: T = triplex, P = penthouse.
ROOMS_NORTH = {
    "T_L_garage": ("L", -1100.0, -1300.0, -1150.0, -800.0),
    "T_L_family_room": ("L", -1150.0, -1750.0, -1220.0, -2250.0),
    "T_L_bath": ("L", -830.0, -2180.0, -830.0, -2330.0),
    "T_L_bedroom_a": ("L", -1160.0, -2640.0, -1350.0, -2900.0),
    "T_L_bedroom_b": ("L", -800.0, -2640.0, -930.0, -2900.0),
    "T_1_kitchen": ("1", -1250.0, -560.0, -1150.0, -1000.0),
    "T_1_powder_room": ("1", -960.0, -1050.0, -960.0, -880.0),
    "T_1_dining": ("1", -1050.0, -1050.0, -1300.0, -1350.0),
    "T_1_living": ("1", -1000.0, -1500.0, -1300.0, -2150.0),
    "T_2_primary_bedroom": ("2", -900.0, -950.0, -1300.0, -550.0),
    "T_2_primary_bath": ("2", -1260.0, -1050.0, -1260.0, -1400.0),
    "T_2_laundry": ("2", -830.0, -1820.0, -830.0, -1560.0),
    "T_2_bedroom_b": ("2", -1100.0, -1950.0, -1350.0, -1750.0),
    "T_2_rear_bedroom": ("2", -1180.0, -2180.0, -900.0, -2450.0),
    "T_2_rear_bath": ("2", -1250.0, -2290.0, -1380.0, -2450.0),
    "P_3_front_bedroom": ("3", -1050.0, -850.0, -1300.0, -450.0),
    "P_3_primary_bath": ("3", -1150.0, -900.0, -1350.0, -1200.0),
    "P_3_hall": ("3", -1000.0, -1000.0, -1000.0, -2000.0),
    "P_3_bedroom_b": ("3", -1100.0, -1560.0, -1350.0, -1300.0),
    "P_3_bedroom_c": ("3", -1100.0, -1790.0, -1350.0, -2050.0),
    "P_3_rear_bedroom": ("3", -1180.0, -2130.0, -900.0, -2450.0),
    "P_3_rear_bath": ("3", -1260.0, -2350.0, -1390.0, -2450.0),
    "P_4_living_dining": ("4", -1000.0, -1250.0, -1300.0, -2000.0),
    "P_4_rear_terrace": ("4", -1100.0, -2130.0, -1100.0, -2480.0),
}


def room_views(mirror=False):
    """Camera table for views_begin() built from ROOMS_NORTH; mirror=True gives the south half."""
    out = {}
    for name, (floor, cx, cy, tx, ty) in ROOMS_NORTH.items():
        z = FLOOR_Z[floor] + 160.0
        if mirror:
            cx, tx = 2.0 * PARTY_X - cx, 2.0 * PARTY_X - tx
        out[("S_" if mirror else "N_") + name] = ((cx, cy, z), (tx, ty, z - 30.0))
    return out


def _actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def look_at(location, target):
    dx, dy, dz = (target[0] - location[0], target[1] - location[1], target[2] - location[2])
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    return unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0)


def views_begin(views=None, hide_stand_ins=True, work_light=0.0):
    """Spawn one temporary camera per view; hide Revit's slab and massing in the editor only.

    work_light is the intensity in candela of a temporary lamp placed just above each camera.
    It is for looking at geometry before Phase 7 has lit the rooms; 0 places none.
    """
    views = views or DESIGN_VIEWS
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    views_end(show_stand_ins=False)
    made = 0
    for name, (location, target) in views.items():
        camera = subsystem.spawn_actor_from_class(
            unreal.CameraActor, unreal.Vector(*location), look_at(location, target))
        camera.set_actor_label("TEMP_" + name)
        camera.tags = [VIEW_TAG, name]
        component = camera.camera_component
        component.set_editor_property("field_of_view", VIEW_FOV)
        component.set_editor_property("constrain_aspect_ratio", True)
        component.set_editor_property("aspect_ratio", 16.0 / 9.0)
        made += 1
        if work_light > 0.0:
            lamp = subsystem.spawn_actor_from_class(
                unreal.PointLight, unreal.Vector(location[0], location[1], location[2] + 30.0), unreal.Rotator())
            lamp.set_actor_label("TEMP_lamp_" + name)
            lamp.tags = [VIEW_TAG]
            light = lamp.point_light_component
            light.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
            light.set_editor_property("intensity", work_light)
            light.set_editor_property("attenuation_radius", 1200.0)
            light.set_editor_property("source_radius", 8.0)
            light.set_editor_property("cast_shadows", True)
    hidden = 0
    if hide_stand_ins:
        for actor in _actors():
            if actor.get_actor_label() in REVIT_STAND_INS:
                actor.set_is_temporarily_hidden_in_editor(True)
                hidden += 1
    return {"cameras": made, "hidden": hidden}


def view_shot(name, out_path, width=1920, height=1080):
    for actor in _actors():
        tags = [str(t) for t in actor.tags]
        if VIEW_TAG in tags and name in tags:
            unreal.AutomationLibrary.take_high_res_screenshot(width, height, out_path, actor)
            return True
    return False


_QUEUE = {"items": [], "done": [], "wait": 0.0, "handle": None, "gap": 3.0}


def _queue_tick(delta_seconds):
    _QUEUE["wait"] -= delta_seconds
    if _QUEUE["wait"] > 0.0:
        return
    if not _QUEUE["items"]:
        if _QUEUE["handle"] is not None:
            unreal.unregister_slate_post_tick_callback(_QUEUE["handle"])
            _QUEUE["handle"] = None
        return
    name, out_path, width, height = _QUEUE["items"].pop(0)
    _QUEUE["done"].append((name, view_shot(name, out_path, width, height)))
    _QUEUE["wait"] = _QUEUE["gap"]


def shoot_queue(names, folder, suffix, width=1280, height=720, gap_seconds=3.0):
    """Take one screenshot per named view, one every gap_seconds, without blocking the editor."""
    _QUEUE["items"] = [(n, "%s/%s%s.png" % (folder.rstrip("/"), n, suffix), width, height) for n in names]
    _QUEUE["done"] = []
    _QUEUE["wait"] = gap_seconds
    _QUEUE["gap"] = gap_seconds
    if _QUEUE["handle"] is None:
        _QUEUE["handle"] = unreal.register_slate_post_tick_callback(_queue_tick)
    return len(_QUEUE["items"])


def shoot_status():
    return {"left": len(_QUEUE["items"]), "done": len(_QUEUE["done"]),
            "failed": [n for n, ok in _QUEUE["done"] if not ok], "running": _QUEUE["handle"] is not None}


def views_end(show_stand_ins=True):
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    shown = 0
    for actor in list(_actors()):
        if VIEW_TAG in [str(t) for t in actor.tags]:
            subsystem.destroy_actor(actor)
            removed += 1
        elif show_stand_ins and actor.get_actor_label() in REVIT_STAND_INS:
            actor.set_is_temporarily_hidden_in_editor(False)
            shown += 1
    return {"removed": removed, "shown": shown}
