"""Phase 7, step 7.1, editor side: stand-in materials for the Phase 4 survey buildings.

Runs inside the Unreal editor (through tools/ue_call.py, mode "wm"):

    wm.build_material()              the parent material M_W1529_Massing, saved by name
    wm.build_instances(names)        one instance per building from review/phase7/massing/plan.json, saved by name
    wm.apply(names)                  each instance put on its building as an override on the placed object
    wm.state()                       how many buildings carry their instance

A Phase 4 building is one mesh with one material slot, shaped from the 2022 laser scan. The parent material here
tells roof from wall by the way the surface faces, lays a wall image set on the walls at its physical size
(read twice and mixed through a cloud picture so that no repeat shows), a roofing image on the roof in the roof's
measured colour, and draws windows on the walls as material: glass, frame, stone lintel and sill, some with
blinds. The Phase 5 parent M_W1529_Opaque cannot do this on a single slot, which is why this parent exists; it
uses the same image sets and the same world mapping in metres. Nothing here edits a mesh or any asset that
Datasmith made; nothing is saved except the asset being built.
"""

import json

import unreal

import wieland_parents as wpar
import wieland_site as ws
from wieland_materials import MEL

FOLDER = "/Game/Wieland1529/Surroundings/Materials"
INSTANCES = FOLDER + "/Buildings"
PARENT_NAME = "M_W1529_Massing"
PLAN = ws.REVIEW + "/massing/plan.json"
POLYHAVEN = "/Game/Wieland/R15_Materials/PolyHaven"
TAG_PLACEHOLDER = "W1529.Placeholder"
LEVEL = "/Game/Wieland1529/Surroundings/L_Surroundings"

ST = wpar.ST
MP = wpar.MP
CMOT = wpar.CMOT

_WINDOWS = """
float3 a = abs(N);
float wall = 1.0 - smoothstep(0.35, 0.60, a.z);
bool faceX = a.x >= a.y;
float u = (faceX ? WP.y : WP.x) * 0.01 + Offset;
float h = (WP.z - BaseZ) * 0.01;
float front = faceX ? FrontX : 1.0 - FrontX;
float allow = saturate(front + Side) * wall * saturate(Amount);
float fi = floor((h - 0.2) / Floor);
float fh = h - 0.2 - fi * Floor;
allow *= step(0.0, fi) * step((fi + 1.0) * Floor + 0.2, WallTop);
float ci = floor(u / Period);
float du = abs(u - ci * Period - Period * 0.5);
float dv = fh - Sill;
float aa = max(length(Cam - WP) * 0.00001, 0.002);
float hw = Size.x * 0.5;
float tall = Size.y;
float fr = 0.06;
float opening = (1.0 - smoothstep(hw - aa, hw + aa, du)) * smoothstep(-aa, aa, dv) * (1.0 - smoothstep(tall - aa, tall + aa, dv));
float glass = (1.0 - smoothstep(hw - fr - aa, hw - fr + aa, du)) * smoothstep(fr - aa, fr + aa, dv)
    * (1.0 - smoothstep(tall - fr - aa, tall - fr + aa, dv));
glass *= smoothstep(0.025 - aa, 0.025 + aa, abs(dv - tall * 0.5));
float wide = 1.0 - smoothstep(hw + 0.12 - aa, hw + 0.12 + aa, du);
float lintel = wide * smoothstep(tall - aa, tall + aa, dv) * (1.0 - smoothstep(tall + 0.22 - aa, tall + 0.22 + aa, dv));
float sill = wide * smoothstep(-0.09 - aa, -0.09 + aa, dv) * (1.0 - smoothstep(-aa, aa, dv));
float hsh = frac(sin(dot(float3(ci, fi, Seed + (faceX ? 17.0 : 3.0)), float3(12.9898, 78.233, 37.719))) * 43758.5453);
float keep = step(0.07, hsh) * allow;
float blind = step(0.55, frac(hsh * 7.13));
float drop = 0.25 + 0.75 * frac(hsh * 13.7);
float lowered = blind * step(1.0 - drop, dv / tall);
return float4(glass * keep, saturate(opening - glass) * keep, saturate(lintel + sill) * keep, lowered * (0.55 + 0.45 * frac(hsh * 29.3)));
"""

_WALL_COLOUR = """
float mask = smoothstep(0.38, 0.62, Cloud.r);
float3 colour = lerp(C1, C2, mask) * Tint;
colour *= 1.0 + Macro * (Slow.g - 0.5) * 2.0;
float h = (WP.z - BaseZ) * 0.01;
float base = saturate(1.0 - h / 0.9);
return colour * (1.0 - Dirt * base * base * (0.5 + Cloud.g));
"""

_ROUGH = """
float r = lerp(lerp(R1, R2, smoothstep(0.38, 0.62, Cloud.r)).g, lerp(R1, R2, smoothstep(0.38, 0.62, Cloud.r)).r, saturate(FromRed));
return saturate(r * Scale);
"""

_ROOF_COLOUR = """
float l1 = dot(C1, float3(0.3, 0.59, 0.11));
float l2 = dot(C2, float3(0.3, 0.59, 0.11));
float lum = lerp(l1, l2, smoothstep(0.38, 0.62, Cloud.r));
float gain = clamp(lum / 0.038, 0.9, 1.12);
return Colour * gain * (1.0 + Macro * (Slow.g - 0.5) * 2.0);
"""

_COMPOSE = """
float roof = smoothstep(0.35, 0.60, N.z);
float3 glass = lerp(GlassC, BlindC * W.w, step(0.01, W.w));
float3 c = lerp(Wall, Stone, W.z);
c = lerp(c, Frame, W.y);
c = lerp(c, glass, W.x);
return lerp(c, Roof, roof);
"""

_COMPOSE_ROUGH = """
float roof = smoothstep(0.35, 0.60, N.z);
float r = lerp(WallR, 0.80, W.z);
r = lerp(r, 0.45, W.y);
r = lerp(r, GlassR, W.x);
return lerp(r, RoofR, roof);
"""

_COMPOSE_NORMAL = """
float roof = smoothstep(0.35, 0.60, N.z);
float3 n = lerp(WallN, N, saturate(W.x + W.y));
float3 r = normalize(N + float3(RoofTN.x, -RoofTN.y, 0.0) * 0.6);
return normalize(lerp(n, r, roof));
"""

_ROOF_UV2 = """
return M / Size + float2(0.413, 0.719);
"""


def build_material():
    """Build (or rebuild) and save the parent material of the survey buildings."""
    path = FOLDER + "/" + PARENT_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.load_asset(path)
        MEL.delete_all_material_expressions(material)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            PARENT_NAME, FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    g = wpar._Graph(material)
    position = g.node(unreal.MaterialExpressionWorldPosition)
    normal = g.node(unreal.MaterialExpressionVertexNormalWS)
    camera = g.node(unreal.MaterialExpressionCameraPositionWS)
    zero = g.constant(0.0)

    def rgb(sample):
        return g.mask(sample, r=True, g=True, b=True)

    # Walls: the Phase 5 world mapping in metres, on whichever world plane the wall faces most.
    yaw = g.scalar("WorldYawDeg", 0.0, "1 Mapping")
    metres = g.custom("World mapping in metres", wpar._WORLD_UV, CMOT.CMOT_FLOAT2,
                      [("WP", position), ("N", normal), ("YawDeg", yaw), ("Swap", zero)])
    size = g.append(g.scalar("Wall_SizeU_m", 2.0, "2 Wall"), g.scalar("Wall_SizeV_m", 2.0, "2 Wall"))
    uv = g.binary(unreal.MaterialExpressionDivide, metres, size)
    uv2 = g.binary(unreal.MaterialExpressionAdd, uv, g.node(unreal.MaterialExpressionConstant2Vector, r=0.413, g=0.0))
    noise = g.texture("VariationCloud", wpar.TEXTURES + "/T_W1529_Noise", ST.SAMPLERTYPE_MASKS, "4 Variation")
    cloud_uv = g.binary(unreal.MaterialExpressionDivide, metres, g.scalar("VariationSize_m", 4.0, "4 Variation"))
    cloud = rgb(g.sample(noise, cloud_uv, ST.SAMPLERTYPE_MASKS))
    slow_uv = g.node(unreal.MaterialExpressionMultiply, const_b=0.23)
    g.link(cloud_uv, slow_uv, "A")
    slow = rgb(g.sample(noise, slow_uv, ST.SAMPLERTYPE_MASKS))
    macro = g.scalar("MacroVariation", 0.12, "4 Variation")
    base_z = g.scalar("BaseZ_cm", 0.0, "3 Windows")

    colour_map = g.texture("Wall_BaseColorMap", wpar.TEXTURES + "/T_W1529_White", ST.SAMPLERTYPE_COLOR, "2 Wall")
    normal_map = g.texture("Wall_NormalMap", wpar.TEXTURES + "/T_W1529_FlatNormal", ST.SAMPLERTYPE_NORMAL, "2 Wall")
    rough_map = g.texture("Wall_RoughnessMap", wpar.TEXTURES + "/T_W1529_WhiteLinear", ST.SAMPLERTYPE_MASKS, "2 Wall")
    wall_colour = g.custom("Wall colour", _WALL_COLOUR, CMOT.CMOT_FLOAT3, [
        ("C1", rgb(g.sample(colour_map, uv, ST.SAMPLERTYPE_COLOR))), ("C2", rgb(g.sample(colour_map, uv2, ST.SAMPLERTYPE_COLOR))),
        ("Cloud", cloud), ("Slow", slow), ("Macro", macro),
        ("Tint", g.mask(g.vector("Wall_Tint", (1, 1, 1, 1), "2 Wall"), r=True, g=True, b=True)),
        ("WP", position), ("BaseZ", base_z), ("Dirt", g.scalar("BaseDirt", 0.35, "4 Variation"))])
    wall_rough = g.custom("Wall roughness", _ROUGH, CMOT.CMOT_FLOAT1, [
        ("R1", rgb(g.sample(rough_map, uv, ST.SAMPLERTYPE_MASKS))), ("R2", rgb(g.sample(rough_map, uv2, ST.SAMPLERTYPE_MASKS))),
        ("Cloud", cloud), ("FromRed", g.scalar("RoughFromRed", 0.0, "2 Wall")), ("Scale", g.scalar("Wall_RoughnessScale", 1.0, "2 Wall"))])
    blend = g.custom("Mix amount of the two readings", "return smoothstep(0.38, 0.62, Cloud.r);", CMOT.CMOT_FLOAT1, [("Cloud", cloud)])
    wall_tn = g.node(unreal.MaterialExpressionLinearInterpolate)
    g.link(rgb(g.sample(normal_map, uv, ST.SAMPLERTYPE_NORMAL)), wall_tn, "A")
    g.link(rgb(g.sample(normal_map, uv2, ST.SAMPLERTYPE_NORMAL)), wall_tn, "B")
    g.link(blend, wall_tn, "Alpha")
    wall_n = g.custom("Wall relief in world mapping", wpar._WORLD_NORMAL, CMOT.CMOT_FLOAT3,
                      [("TN", wall_tn), ("N", normal), ("YawDeg", yaw), ("Swap", zero)])

    # Roof: roofing felt from above, in the roof's measured colour.
    roof_size = g.scalar("Roof_Size_m", 2.0, "5 Roof")
    flat = g.node(unreal.MaterialExpressionMultiply, const_b=0.01)
    g.link(g.mask(position, r=True, g=True), flat, "A")
    roof_uv = g.binary(unreal.MaterialExpressionDivide, flat, roof_size)
    roof_uv2 = g.custom("Roof: second reading", _ROOF_UV2, CMOT.CMOT_FLOAT2, [("M", flat), ("Size", roof_size)])
    roof_c = g.texture("Roof_BaseColorMap", POLYHAVEN + "/bitumen/T_R15_bitumen_BaseColor", ST.SAMPLERTYPE_COLOR, "5 Roof")
    roof_n = g.texture("Roof_NormalMap", POLYHAVEN + "/bitumen/T_R15_bitumen_Normal", ST.SAMPLERTYPE_NORMAL, "5 Roof")
    roof_a = g.texture("Roof_ARMMap", POLYHAVEN + "/bitumen/T_R15_bitumen_ARM", ST.SAMPLERTYPE_MASKS, "5 Roof")
    roof_colour = g.custom("Roof colour", _ROOF_COLOUR, CMOT.CMOT_FLOAT3, [
        ("C1", rgb(g.sample(roof_c, roof_uv, ST.SAMPLERTYPE_COLOR))), ("C2", rgb(g.sample(roof_c, roof_uv2, ST.SAMPLERTYPE_COLOR))),
        ("Cloud", cloud), ("Slow", slow), ("Macro", macro),
        ("Colour", g.mask(g.vector("Roof_Colour", (0.1, 0.1, 0.1, 1), "5 Roof"), r=True, g=True, b=True))])
    roof_rough = g.mask(g.sample(roof_a, roof_uv, ST.SAMPLERTYPE_MASKS), g=True)
    roof_tn = rgb(g.sample(roof_n, roof_uv, ST.SAMPLERTYPE_NORMAL))

    # Windows, drawn as material.
    windows = g.custom("Windows", _WINDOWS, CMOT.CMOT_FLOAT4, [
        ("WP", position), ("N", normal), ("Cam", camera), ("BaseZ", base_z),
        ("Offset", g.scalar("WindowOffset_m", 0.0, "3 Windows")), ("FrontX", g.scalar("FrontX", 0.0, "3 Windows")),
        ("Side", g.scalar("SideWindows", 0.0, "3 Windows")), ("Amount", g.scalar("WindowAmount", 1.0, "3 Windows")),
        ("Floor", g.scalar("FloorHeight_m", 3.3, "3 Windows")), ("WallTop", g.scalar("WallTop_m", 10.0, "3 Windows")),
        ("Period", g.scalar("WindowPeriod_m", 2.4, "3 Windows")),
        ("Size", g.append(g.scalar("WindowWidth_m", 1.1, "3 Windows"), g.scalar("WindowHeight_m", 1.8, "3 Windows"))),
        ("Sill", g.scalar("Sill_m", 0.8, "3 Windows")), ("Seed", g.scalar("Seed", 0.0, "3 Windows"))])

    def colour_of(name, default):
        return g.mask(g.vector(name, default, "3 Windows"), r=True, g=True, b=True)

    colour = g.custom("Colour", _COMPOSE, CMOT.CMOT_FLOAT3, [
        ("N", normal), ("W", windows), ("Wall", wall_colour), ("Roof", roof_colour),
        ("Stone", colour_of("Stone_Colour", (0.6, 0.58, 0.53, 1))), ("Frame", colour_of("Frame_Colour", (0.035, 0.03, 0.028, 1))),
        ("GlassC", colour_of("Glass_Colour", (0.012, 0.016, 0.02, 1))), ("BlindC", colour_of("Blind_Colour", (0.5, 0.48, 0.44, 1)))])
    g.out(colour, MP.MP_BASE_COLOR)
    rough = g.custom("Roughness", _COMPOSE_ROUGH, CMOT.CMOT_FLOAT1, [
        ("N", normal), ("W", windows), ("WallR", wall_rough), ("RoofR", roof_rough),
        ("GlassR", g.scalar("Glass_Roughness", 0.06, "3 Windows"))])
    g.out(rough, MP.MP_ROUGHNESS)
    world_normal = g.custom("Relief", _COMPOSE_NORMAL, CMOT.CMOT_FLOAT3, [
        ("N", normal), ("W", windows), ("WallN", wall_n), ("RoofTN", roof_tn)])
    g.out(g.to_tangent(world_normal), MP.MP_NORMAL)
    g.out(g.scalar("Specular", 0.5, "4 Variation"), MP.MP_SPECULAR)
    return wpar._finish(material)


def plan():
    with open(PLAN, encoding="utf-8") as handle:
        return json.load(handle)


def build_instances(names=None):
    """Make (or reset) and save one instance per building of the plan."""
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    parent = unreal.load_asset(FOLDER + "/" + PARENT_NAME)
    out = {"made": 0, "saved": 0, "problems": []}
    for name, record in plan().items():
        if names is not None and name not in names:
            continue
        instance_name = "MI_W1529_" + name
        path = INSTANCES + "/" + instance_name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            instance = unreal.load_asset(path)
            MEL.clear_all_material_instance_parameters(instance)
        else:
            instance = tools.create_asset(instance_name, INSTANCES, unreal.MaterialInstanceConstant,
                                          unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(instance, parent)
        for key, value in record["scalars"].items():
            if not MEL.set_material_instance_scalar_parameter_value(instance, key, float(value)):
                out["problems"].append(name + ": no number called " + key)
        for key, value in record["vectors"].items():
            if not MEL.set_material_instance_vector_parameter_value(instance, key, unreal.LinearColor(*value)):
                out["problems"].append(name + ": no colour called " + key)
        for key, value in record["textures"].items():
            texture = unreal.load_asset(value)
            if texture is None or not MEL.set_material_instance_texture_parameter_value(instance, key, texture):
                out["problems"].append(name + ": image not set: " + key)
        MEL.update_material_instance(instance)
        out["made"] += 1
        out["saved"] += 1 if unreal.EditorAssetLibrary.save_asset(path, False) else 0
    return out


def _buildings():
    found = {}
    for actor in ws.actors():
        label = actor.get_actor_label()
        if label.startswith("SB_") and ws.level_of(actor).split(".")[0] == LEVEL:
            found[label] = actor
    return found


def apply(names=None):
    """Put each building's instance on its placed object (an override; the mesh asset keeps its grey material)."""
    buildings = _buildings()
    out = {"applied": 0, "missing": []}
    for name in plan():
        if names is not None and name not in names:
            continue
        actor = buildings.get(name)
        instance = unreal.load_asset(INSTANCES + "/MI_W1529_" + name)
        if actor is None or instance is None:
            out["missing"].append(name)
            continue
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.modify()
        component.set_material(0, instance)
        tags = list(actor.tags)
        if unreal.Name(TAG_PLACEHOLDER) not in tags:
            actor.modify()
            tags.append(unreal.Name(TAG_PLACEHOLDER))
            actor.set_editor_property("tags", tags)
        out["applied"] += 1
    return out


def state():
    buildings = _buildings()
    dressed = 0
    bare = []
    for name, actor in buildings.items():
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        material = component.get_material(0)
        if material is not None and material.get_name() == "MI_W1529_" + name:
            dressed += 1
        else:
            bare.append(name)
    return {"buildings": len(buildings), "dressed": dressed, "bare": bare[:20],
            "tagged": sum(1 for a in buildings.values() if unreal.Name(TAG_PLACEHOLDER) in list(a.tags))}


VIEWS = {
    # name: (place x, y, z in cm; pitch, yaw; what it shows)
    "M1_trial": ((-405.0, 3600.0, 2600.0), (-28.0, 90.0), "the trial building SB_781424, 60 m west of the lot, from above the Wieland houses"),
    "M2_close": ((-405.0, 5200.0, 700.0), (-5.0, 90.0), "the same building's east wall from 8 m, 7 m up"),
    "M3_west": ((-754.0, -1500.0, 9000.0), (-58.0, 90.0), "from 90 m up over the lot, looking west over the block"),
    "M4_east": ((-754.0, 1500.0, 9000.0), (-58.0, -90.0), "from 90 m up over Wieland, looking east over the block"),
    "M5_north": ((6000.0, -1500.0, 9000.0), (-58.0, 180.0), "from 90 m up south of the lot, looking north"),
    "M6_south": ((-8000.0, -1500.0, 9000.0), (-58.0, 0.0), "from 90 m up north of the lot, looking south"),
    "M7_street": ((-11000.0, 800.0, 170.0), (2.0, 0.0), "eye height on Wieland 95 m north of the lot, looking south along the street"),
}


def cameras():
    """Temporary cameras for the buildings' pictures; ws.shots_end() removes them with the station cameras."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(ws.world_path().split("/")[-1])
    made = 0
    for name, (place, turn, _what) in VIEWS.items():
        camera = subsystem.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*place),
                                                  unreal.Rotator(pitch=turn[0], yaw=turn[1], roll=0.0))
        camera.set_actor_label("TEMP_" + name)
        camera.tags = [ws.SHOT_TAG, name]
        component = camera.camera_component
        component.set_editor_property("field_of_view", 73.74)
        component.set_editor_property("constrain_aspect_ratio", True)
        component.set_editor_property("aspect_ratio", 16.0 / 9.0)
        made += 1
    return made
