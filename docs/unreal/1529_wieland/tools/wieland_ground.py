"""Phase 7, step 7.2, editor side: the site ground's material, its instances and its meshes.

Runs inside the Unreal editor (through tools/ue_call.py, mode "wg"):

    wg.import_cover()                 the ground-cover picture -> a texture, saved by name
    wg.build_material()               the parent material M_W1529_SiteGround, saved by name
    wg.build_instances()              its instances and the kerb's instance, saved by name
    await wg.build_meshes(names)      mesh files of phase7_sitemesh.py -> mesh assets and placed objects

The ground material lays five covers flat from above at their physical size: asphalt, public sidewalk
concrete, private paving concrete, lawn and soil. Where each lies is read from one picture of the whole
site (red asphalt, green lawn, blue soil, alpha private paving, the rest public sidewalk), made off line
from the county parcels, the 2025 aerial photograph and the 2022 laser scan. Nothing here edits an asset
that Datasmith made, and nothing is saved except the asset being built.
"""

import asyncio
import json
import os
import time

import unreal

import wieland_parents as wpar
import wieland_site as ws
import wieland_surroundings as wsur
from wieland_materials import MEL

SITE = "/Game/Wieland1529/Site"
SITE_TEXTURES = SITE + "/Textures"
SITE_MATERIALS = SITE + "/Materials"
SITE_MESHES = SITE + "/Meshes"
WORKS_LEVEL = SITE + "/L_SiteWorks"
GROUND_FOLDER = ws.REVIEW + "/ground"
MESH_FOLDER = GROUND_FOLDER + "/mesh"
COVER_NAME = "T_W1529_SiteCover"
PARENT_NAME = "M_W1529_SiteGround"
POLYHAVEN = "/Game/Wieland/R15_Materials/PolyHaven"
TAG_SITE = "W1529.SiteGround"

ST = wpar.ST
MP = wpar.MP
CMOT = wpar.CMOT

# The four image sets, all recorded free (CC0) in asset_licences.csv. Size: metres one repeat covers, as the earlier
# level used them. The lawn has no licensed grass image: it is the brightness of the wood-chip image, coloured.
SETS = {
    "Asphalt": ("asphalt_03", 2.05),
    "Concrete": ("concrete_floor_03", 2.5),
    "Soil": ("dirt_floor", 2.07),
    "Lawn": ("wood_chips", 0.6),
}

_COVER_UV = """
return float2((WP.y - Origin.y) / Size, (WP.x - Origin.x) / Size);
"""

_TURNED_UV = """
return float2(-M.y, M.x) / (Size * 1.37) + float2(0.413, 0.719);
"""

_TURNED_NORMAL = """
return float3(TN.y, -TN.x, TN.z);
"""

_WEIGHTS = """
float j = (Fine.r - 0.5) * Break;
float a = smoothstep(0.40, 0.60, Cover.r + j * 0.3);
float l = smoothstep(0.35, 0.65, Cover.g + j) * (1.0 - a);
float s = smoothstep(0.35, 0.65, Cover.b + j) * (1.0 - a) * (1.0 - l);
float p = smoothstep(0.45, 0.55, 1.0 - Cover.a) * (1.0 - a) * (1.0 - l) * (1.0 - s);
return lerp(float4(a, l, s, p), float4(1.0, 0.0, 0.0, 0.0), saturate(Force));
"""

_SLABS = """
float2 q = (M + Offset) / Size;
float2 f = frac(q);
float2 d = min(f, 1.0 - f) * Size;
float joint = 1.0 - smoothstep(Width * 0.5, Width * 1.5, min(d.x, d.y));
float2 c = floor(q);
float h = frac(sin(dot(c, float2(12.9898, 78.233))) * 43758.5453);
return float3(joint, h, 0.0);
"""

_GREYED = """
float lum = dot(C, float3(0.3, 0.59, 0.11));
return lerp(C, float3(lum, lum, lum), Grey) * Tint;
"""

_CONCRETE = """
float lum = dot(C, float3(0.3, 0.59, 0.11));
float3 c = lerp(C, float3(lum, lum, lum), Grey) * Tint * (1.0 + Vary * (Slab.y - 0.5) * 2.0);
return lerp(c, c * (1.0 - Dark), Slab.x);
"""

_LAWN = """
float lum = dot(C, float3(0.3, 0.59, 0.11));
float3 tint = lerp(TintA, TintB, smoothstep(0.10, 0.90, Cloud.g));
// The stand-in image has deep black gaps between its chips; grass has none, so the dark end is lifted.
return saturate(0.15 + 0.85 * saturate(lum * Gain)) * tint;
"""

_MIX = """
float w = saturate(1.0 - W.x - W.y - W.z - W.w);
return A * W.x + L * W.y + S * W.z + P * W.w + K * w;
"""

_SHADE = """
return C * (1.0 + Macro * (Slow.g - 0.5) * 2.0);
"""

_FLAT = """
return normalize(float3(TN.xy * Strength, TN.z));
"""


def _texture(set_name, kind):
    return "%s/%s/T_R15_%s_%s" % (POLYHAVEN, set_name, set_name, kind)


def import_cover():
    """The ground-cover picture as a texture: numbers, not colour; with smaller copies for far away."""
    result = wpar.import_textures([[GROUND_FOLDER + "/" + COVER_NAME + ".tga", SITE_TEXTURES, COVER_NAME, "mask"]])
    texture = unreal.load_asset(SITE_TEXTURES + "/" + COVER_NAME)
    if texture is not None:
        result["size"] = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
        result["srgb"] = bool(texture.srgb)
    return result


def reimport_cover():
    """After the picture file changed: read it in again over the same texture and save it by name."""
    path = SITE_TEXTURES + "/" + COVER_NAME
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", GROUND_FOLDER + "/" + COVER_NAME + ".tga")
    task.set_editor_property("destination_path", SITE_TEXTURES)
    task.set_editor_property("destination_name", COVER_NAME)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    texture = unreal.load_asset(path)
    texture.set_editor_property("srgb", False)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    return {"saved": bool(unreal.EditorAssetLibrary.save_asset(path, False)), "size": texture.blueprint_get_size_x()}


def build_material():
    """Build (or rebuild) and save the parent material of the site ground."""
    path = SITE_MATERIALS + "/" + PARENT_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.load_asset(path)
        MEL.delete_all_material_expressions(material)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            PARENT_NAME, SITE_MATERIALS, unreal.Material, unreal.MaterialFactoryNew())
    g = wpar._Graph(material)
    position = g.node(unreal.MaterialExpressionWorldPosition)
    metres = g.node(unreal.MaterialExpressionMultiply, const_b=0.01)
    g.link(g.mask(position, r=True, g=True), metres, "A")

    def rgb(sample):
        return g.mask(sample, r=True, g=True, b=True)

    # Where each cover lies.
    cover_map = g.texture("CoverMap", wpar.TEXTURES + "/T_W1529_WhiteLinear", ST.SAMPLERTYPE_MASKS, "1 Cover picture")
    cover_uv = g.custom("Place on the cover picture", _COVER_UV, CMOT.CMOT_FLOAT2, [
        ("WP", position), ("Origin", g.vector("CoverOrigin_cm", (0, 0, 0, 0), "1 Cover picture")),
        ("Size", g.scalar("CoverSize_cm", 30900.0, "1 Cover picture"))])
    cover = g.sample(cover_map, cover_uv, ST.SAMPLERTYPE_MASKS)
    cover4 = g.node(unreal.MaterialExpressionAppendVector)
    g.link(cover, cover4, "A", "RGB")
    g.link(cover, cover4, "B", "A")

    noise = g.texture("VariationCloud", wpar.TEXTURES + "/T_W1529_Noise", ST.SAMPLERTYPE_MASKS, "3 Variation")
    cloud_uv = g.binary(unreal.MaterialExpressionDivide, metres, g.scalar("VariationSize_m", 4.0, "3 Variation"))
    cloud = rgb(g.sample(noise, cloud_uv, ST.SAMPLERTYPE_MASKS))
    slow_uv = g.node(unreal.MaterialExpressionMultiply, const_b=0.23)
    g.link(cloud_uv, slow_uv, "A")
    slow = rgb(g.sample(noise, slow_uv, ST.SAMPLERTYPE_MASKS))
    fine_uv = g.binary(unreal.MaterialExpressionDivide, metres, g.scalar("EdgeBreakSize_m", 0.9, "3 Variation"))
    fine = rgb(g.sample(noise, fine_uv, ST.SAMPLERTYPE_MASKS))
    weights = g.custom("Share of each cover", _WEIGHTS, CMOT.CMOT_FLOAT4, [
        ("Cover", cover4), ("Fine", fine), ("Break", g.scalar("EdgeBreak", 0.5, "3 Variation")),
        ("Force", g.scalar("AllAsphalt", 0.0, "1 Cover picture"))])
    blend = g.custom("Mix amount of the two readings", "return smoothstep(0.38, 0.62, Cloud.r);", CMOT.CMOT_FLOAT1,
                     [("Cloud", cloud)])

    def mix(a, b):
        expression = g.node(unreal.MaterialExpressionLinearInterpolate)
        g.link(a, expression, "A")
        g.link(b, expression, "B")
        g.link(blend, expression, "Alpha")
        return expression

    def layer(name):
        """One image set read twice, the second time turned a quarter and at another size, mixed through the cloud."""
        set_name, size_default = SETS[name]
        group = "2 " + name
        size = g.scalar(name + "_Size_m", size_default, group)
        uv = g.binary(unreal.MaterialExpressionDivide, metres, size)
        uv2 = g.custom(name + ": second reading", _TURNED_UV, CMOT.CMOT_FLOAT2, [("M", metres), ("Size", size)])
        colour_map = g.texture(name + "_BaseColorMap", _texture(set_name, "BaseColor"), ST.SAMPLERTYPE_COLOR, group)
        normal_map = g.texture(name + "_NormalMap", _texture(set_name, "Normal"), ST.SAMPLERTYPE_NORMAL, group)
        arm_map = g.texture(name + "_ARMMap", _texture(set_name, "ARM"), ST.SAMPLERTYPE_MASKS, group)
        colour = mix(rgb(g.sample(colour_map, uv, ST.SAMPLERTYPE_COLOR)), rgb(g.sample(colour_map, uv2, ST.SAMPLERTYPE_COLOR)))
        turned = g.custom(name + ": relief of the second reading", _TURNED_NORMAL, CMOT.CMOT_FLOAT3,
                          [("TN", rgb(g.sample(normal_map, uv2, ST.SAMPLERTYPE_NORMAL)))])
        normal = mix(rgb(g.sample(normal_map, uv, ST.SAMPLERTYPE_NORMAL)), turned)
        arm = mix(rgb(g.sample(arm_map, uv, ST.SAMPLERTYPE_MASKS)), rgb(g.sample(arm_map, uv2, ST.SAMPLERTYPE_MASKS)))
        return colour, normal, arm

    asphalt, concrete, soil, lawn = layer("Asphalt"), layer("Concrete"), layer("Soil"), layer("Lawn")

    def tinted(colour, name, default, group):
        expression = g.node(unreal.MaterialExpressionMultiply)
        g.link(colour, expression, "A")
        g.link(g.vector(name, default, group), expression, "B")
        return expression

    def slabs(name, size_default, width_default, vary_default, dark_default, tint_default):
        group = "2 " + name
        slab = g.custom(name + ": joints and slabs", _SLABS, CMOT.CMOT_FLOAT3, [
            ("M", metres), ("Offset", g.mask(g.vector(name + "_JointOffset_m", (0, 0, 0, 0), group), r=True, g=True)),
            ("Size", g.scalar(name + "_SlabSize_m", size_default, group)),
            ("Width", g.scalar(name + "_JointWidth_m", width_default, group))])
        colour = g.custom(name + ": colour", _CONCRETE, CMOT.CMOT_FLOAT3, [
            ("C", concrete[0]), ("Tint", g.mask(g.vector(name + "_Tint", tint_default, group), r=True, g=True, b=True)),
            ("Vary", g.scalar(name + "_SlabVariation", vary_default, group)),
            ("Dark", g.scalar(name + "_JointDarkness", dark_default, group)), ("Slab", slab), ("Grey", concrete_grey)])
        return colour

    # The free image sets are warmer than Chicago's grey concrete and aged asphalt: part of their colour is taken out.
    concrete_grey = g.scalar("Concrete_Grey", 0.6, "2 Concrete")
    walk = slabs("Walk", 1.524, 0.012, 0.07, 0.55, (1.0, 0.99, 0.97, 1))
    paving = slabs("Paving", 3.048, 0.012, 0.05, 0.45, (0.86, 0.85, 0.83, 1))
    asphalt_colour = g.custom("Asphalt: colour", _GREYED, CMOT.CMOT_FLOAT3, [
        ("C", asphalt[0]), ("Grey", g.scalar("Asphalt_Grey", 0.75, "2 Asphalt")),
        ("Tint", g.mask(g.vector("Asphalt_Tint", (0.62, 0.63, 0.66, 1), "2 Asphalt"), r=True, g=True, b=True))])
    soil_colour = tinted(soil[0], "Soil_Tint", (0.75, 0.7, 0.65, 1), "2 Soil")
    lawn_colour = g.custom("Lawn: colour", _LAWN, CMOT.CMOT_FLOAT3, [
        ("C", lawn[0]), ("Cloud", cloud),
        ("TintA", g.mask(g.vector("Lawn_TintA", (0.11, 0.16, 0.05, 1), "2 Lawn"), r=True, g=True, b=True)),
        ("TintB", g.mask(g.vector("Lawn_TintB", (0.15, 0.18, 0.07, 1), "2 Lawn"), r=True, g=True, b=True)),
        ("Gain", g.scalar("Lawn_Gain", 2.2, "2 Lawn"))])

    def mixed(description, a, k, p, l, s):
        return g.custom(description, _MIX, CMOT.CMOT_FLOAT3, [("W", weights), ("A", a), ("K", k), ("P", p), ("L", l), ("S", s)])

    colour = mixed("Colour of the covers", asphalt_colour, walk, paving, lawn_colour, soil_colour)
    shaded = g.custom("Slow change of brightness", _SHADE, CMOT.CMOT_FLOAT3, [
        ("C", colour), ("Slow", slow), ("Macro", g.scalar("MacroVariation", 0.12, "3 Variation"))])
    g.out(shaded, MP.MP_BASE_COLOR)
    # Grass is matt: the wood-chip image that stands in for it is smoother than grass and showed a blue sheen of the sky.
    lawn_arm = g.custom("Lawn: matt", "return float3(A.r, max(A.g, Least), A.b);", CMOT.CMOT_FLOAT3,
                        [("A", lawn[2]), ("Least", g.scalar("Lawn_LeastRoughness", 0.9, "2 Lawn"))])
    arm = mixed("Occlusion and roughness of the covers", asphalt[2], concrete[2], concrete[2], lawn_arm, soil[2])
    rough = g.node(unreal.MaterialExpressionSaturate)
    g.link(g.binary(unreal.MaterialExpressionMultiply, g.mask(arm, g=True), g.scalar("RoughnessScale", 1.0, "3 Variation")), rough, "")
    g.out(rough, MP.MP_ROUGHNESS)
    g.out(g.mask(arm, r=True), MP.MP_AMBIENT_OCCLUSION)
    normal = mixed("Relief of the covers", asphalt[1], concrete[1], concrete[1], lawn[1], soil[1])
    # Seen from above, the image's right is world +X and its down is world +Y, so the relief image's three numbers
    # are already a world direction (as in M_W1529_GroundBlend).
    flat = g.custom("Relief laid flat", _FLAT, CMOT.CMOT_FLOAT3, [("TN", normal), ("Strength", g.scalar("NormalStrength", 1.0, "3 Variation"))])
    g.out(g.to_tangent(flat), MP.MP_NORMAL)
    g.out(g.scalar("Specular", 0.5, "3 Variation"), MP.MP_SPECULAR)
    return wpar._finish(material)


# The look after the first station pictures: the concrete a little greyer and darker, the asphalt without its blue
# cast (the sky light adds blue of its own in shadow), the big private slabs varying a little more.
LOOK_SCALARS = {"Concrete_Grey": 0.8, "Paving_SlabVariation": 0.09}
LOOK_VECTORS = {"Asphalt_Tint": (0.46, 0.46, 0.47, 1.0), "Soil_Tint": (0.5, 0.45, 0.4, 1.0), "Walk_Tint": (0.88, 0.88, 0.87, 1.0),
                "Paving_Tint": (0.74, 0.74, 0.73, 1.0)}

INSTANCES = {
    # name: (parent, scalars, vectors, textures)
    "MI_W1529_SiteGround": (SITE_MATERIALS + "/" + PARENT_NAME, dict(LOOK_SCALARS), dict(LOOK_VECTORS),
                            {"CoverMap": SITE_TEXTURES + "/" + COVER_NAME}),
    "MI_W1529_SiteRoad": (SITE_MATERIALS + "/" + PARENT_NAME, dict(LOOK_SCALARS, AllAsphalt=1.0), dict(LOOK_VECTORS),
                          {"CoverMap": SITE_TEXTURES + "/" + COVER_NAME}),
    "MI_W1529_SiteKerb": (wpar.PARENTS + "/M_W1529_Opaque",
                          {"SizeU_m": 2.4, "SizeV_m": 2.4, "RoughnessScale": 1.0, "MacroVariation": 0.15, "VariationSize_m": 3.0},
                          {"Tint": (0.92, 0.91, 0.89, 1.0)},
                          {"BaseColorMap": wpar.TEXTURES + "/T_W1529_Concrete046_C", "NormalMap": wpar.TEXTURES + "/T_W1529_Concrete046_N",
                           "RoughnessMap": wpar.TEXTURES + "/T_W1529_Concrete046_R"}),
}
INSTANCE_SWITCHES = {"MI_W1529_SiteKerb": {"AntiRepeat": True}}


def cover_frame():
    with open(GROUND_FOLDER + "/cover_summary.json", encoding="utf-8") as handle:
        summary = json.load(handle)
    origin = summary["grid_origin_cm"]
    return origin, summary["cells"][0] * summary["cell_cm"]


def build_instances(only=None):
    """Make (or reset) and save the instances. The ground and road instances get the cover picture's place and size."""
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    origin, size = cover_frame()
    out = {}
    for name, (parent_path, scalars, vectors, textures) in INSTANCES.items():
        if only is not None and name not in only:
            continue
        path = SITE_MATERIALS + "/" + name
        problems = []
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            instance = unreal.load_asset(path)
            MEL.clear_all_material_instance_parameters(instance)
        else:
            instance = tools.create_asset(name, SITE_MATERIALS, unreal.MaterialInstanceConstant,
                                          unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(instance, unreal.load_asset(parent_path))
        scalars, vectors = dict(scalars), dict(vectors)
        if parent_path.endswith(PARENT_NAME):
            scalars["CoverSize_cm"] = size
            vectors["CoverOrigin_cm"] = (origin[0], origin[1], 0.0, 0.0)
        for key, value in INSTANCE_SWITCHES.get(name, {}).items():
            MEL.set_material_instance_static_switch_parameter_value(instance, key, bool(value))
        for key, value in scalars.items():
            if not MEL.set_material_instance_scalar_parameter_value(instance, key, float(value)):
                problems.append("no number called " + key)
        for key, value in vectors.items():
            if not MEL.set_material_instance_vector_parameter_value(instance, key, unreal.LinearColor(*value)):
                problems.append("no colour called " + key)
        for key, value in textures.items():
            texture = unreal.load_asset(value)
            if texture is None or not MEL.set_material_instance_texture_parameter_value(instance, key, texture):
                problems.append("image not set: " + key)
        MEL.update_material_instance(instance)
        out[name] = {"saved": bool(unreal.EditorAssetLibrary.save_asset(path, False)), "problems": problems}
    return out


MATERIAL_OF_KIND = {"ground": "MI_W1529_SiteGround", "road": "MI_W1529_SiteRoad", "kerb": "MI_W1529_SiteKerb"}


def mesh_names():
    return sorted(n[:-5] for n in os.listdir(MESH_FOLDER) if n.endswith(".json"))


def set_current_level():
    """With L_Site_M2 open: new objects go into the level L_SiteWorks. Returns the level new objects go to."""
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    done = bool(subsystem.set_current_level_by_name(unreal.Name("L_SiteWorks")))
    current = subsystem.get_current_level()
    return {"set": done, "current": current.get_outer().get_path_name() if current else None}


async def build_meshes(names, record_path=None):
    """Mesh files -> mesh assets under SITE_MESHES and objects in the level L_SiteWorks.

    Works with L_SiteWorks open on its own, or with L_Site_M2 open and L_SiteWorks made the level new objects go to.
    An object that exists already is passed over; a mesh asset that exists already is used as it is. Each new
    mesh asset is saved by name. The level is not saved here.
    """
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    current = subsystem.get_current_level()
    current_path = current.get_outer().get_path_name().split(".")[0] if current else ""
    if current_path != WORKS_LEVEL:
        raise RuntimeError("refused: new objects would go to %s, not %s" % (current_path, WORKS_LEVEL))
    existing = {a.get_actor_label() for a in ws.actors()}
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    made, skipped, problems, records = 0, 0, [], []
    started = time.time()
    for name in names:
        if name in existing:
            skipped += 1
            continue
        with open(MESH_FOLDER + "/" + name + ".json", encoding="utf-8") as handle:
            data = json.load(handle)
        asset_path = SITE_MESHES + "/" + name
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            static_mesh = unreal.load_asset(asset_path)
        else:
            mesh, record = wsur._make_mesh(data)
            records.append(record)
            if not wsur._mesh_is_whole(record):
                problems.append(name + ": mesh in memory has no UV channel or no triangles; no asset made")
                continue
            options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
            options.enable_nanite = True
            nanite = unreal.MeshNaniteSettings()
            nanite.enabled = True
            options.nanite_settings = nanite
            options.enable_collision = True
            options.enable_recompute_normals = False
            static_mesh, _outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, asset_path, options)
            if static_mesh is not None:
                wsur._ensure_nanite(static_mesh)
                if not unreal.EditorAssetLibrary.save_asset(asset_path, False):
                    problems.append(name + ": mesh asset not saved")
        if static_mesh is None:
            problems.append(name + ": no asset came back")
            continue
        pivot = data["pivot"]
        actor = actors.spawn_actor_from_object(static_mesh, unreal.Vector(pivot[0], pivot[1], pivot[2]), unreal.Rotator(0.0, 0.0, 0.0))
        if actor is None:
            problems.append(name + ": no object could be placed")
            continue
        actor.set_actor_label(name)
        actor.set_folder_path(unreal.Name("Site works/" + {"ground": "Ground", "road": "Roadway", "kerb": "Kerbs"}[data["kind"]]))
        actor.tags = [unreal.Name(ws.TAG_GENERATED), unreal.Name(TAG_SITE), unreal.Name("W1529.Kind.Site" + data["kind"].capitalize())]
        component = actor.static_mesh_component
        material = unreal.load_asset(SITE_MATERIALS + "/" + MATERIAL_OF_KIND[data["kind"]])
        if material is None:
            problems.append(name + ": material missing")
        else:
            component.set_material(0, material)
        component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
        made += 1
        await asyncio.sleep(0)
    if record_path and records:
        with open(record_path, "a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
    return {"asked": len(names), "made": made, "skipped": skipped, "problems": problems[:8],
            "rejected_triangles": sum(r["rejected"] for r in records), "open_edges": sum(r["open_edges"] for r in records),
            "seconds": round(time.time() - started, 1)}


def site_objects():
    return [a for a in ws.actors() if any(str(t) == TAG_SITE for t in a.tags)]


def phase4_ground():
    """The Phase 4 ground pieces that the site ground replaces (not the lot's placeholder)."""
    return [a for a in ws.actors() if a.get_actor_label().startswith("SG_") and a.get_actor_label() != "SG_lot_placeholder"]


def show_phase4_ground(visible):
    labels = [a.get_actor_label() for a in phase4_ground()]
    return ws.set_visible(labels, visible)


# ---------------------------------------------------------------------------------------------
# The switch between the site ground and the Phase 4 survey ground, in the variant asset of the surroundings.
GROUND_LIST = "Site ground"
GROUND_OPTION_NEW = "Site ground (Phase 7)"
GROUND_OPTION_OLD = "Phase 4 survey ground"
GROUND_RECORD = ws.REVIEW + "/phase4_hidden_ground.csv"


def _visible(actor):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    return bool(component.get_editor_property("visible"))


def ground_state():
    new, old = site_objects(), phase4_ground()
    return {"site_objects": len(new), "site_visible": sum(_visible(a) for a in new),
            "phase4_tiles": len(old), "phase4_visible": sum(_visible(a) for a in old)}


def build_ground_variants():
    """Adds (or remakes) the list "Site ground" in the variant asset, two options, and saves the asset by name."""
    ws._require(ws.SITE_LEVEL)
    library = unreal.VariantManagerLibrary
    sets_asset = ws.variant_asset()
    for index in reversed(range(sets_asset.get_num_variant_sets())):
        old = sets_asset.get_variant_set(index)
        if str(old.get_display_text()) == GROUND_LIST:
            library.remove_variant_set(sets_asset, old)
    variant_set = unreal.VariantSet()
    variant_set.set_display_text(GROUND_LIST)
    library.add_variant_set(sets_asset, variant_set)
    result = {"values": 0, "missed": 0}
    for option, new_shown in ((GROUND_OPTION_NEW, True), (GROUND_OPTION_OLD, False)):
        variant = unreal.Variant()
        variant.set_display_text(option)
        library.add_variant(variant_set, variant)
        for group, shown in ((site_objects(), new_shown), (phase4_ground(), not new_shown)):
            for actor in group:
                library.add_actor_binding(variant, actor)
                value = None
                for name in library.get_capturable_properties(actor):
                    if str(name).endswith("/ Visible") and "Billboard" not in str(name):
                        value = library.capture_property(variant, actor, str(name))
                        break
                if value is None:
                    result["missed"] += 1
                    continue
                library.set_value_bool(value, shown)
                result["values"] += 1
    result["saved"] = bool(unreal.EditorAssetLibrary.save_loaded_asset(sets_asset, False))
    result["state"] = ground_state()
    return result


def switch_ground(option):
    out = ws.switch_list(GROUND_LIST, option)
    return {"asked": option, "error": out.get("error"), "state": ground_state()}


def ground_record():
    """The Phase 4 ground pieces that are hidden, one line each, with how to bring them back."""
    import csv
    rows = []
    for actor in sorted(phase4_ground(), key=lambda a: a.get_actor_label()):
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        rows.append({"object": actor.get_actor_label(), "level": ws.level_of(actor), "mesh": ws._path(component.static_mesh),
                     "visible": _visible(actor),
                     "override": "mesh component property Visible = False on the placed object; nothing deleted",
                     "how_to_undo": "Variant Manager, list '%s', option '%s'" % (GROUND_LIST, GROUND_OPTION_OLD)})
    with open(GROUND_RECORD, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


# ---------------------------------------------------------------------------------------------
# Pictures for the repository's gate on seamless, non-repeating materials.
GATE_VIEWS = {
    # name: (place x, y, z in cm; pitch, yaw; what it shows)
    "G1_asphalt_3x3": ((-754.0, 900.0, 410.0), (-90.0, 180.0), "straight down on the roadway, 6.15 m across: three by three of the asphalt image (2.05 m), with the corners where four meet"),
    "G2_walk_3x3": ((-754.0, 160.0, 500.0), (-90.0, 180.0), "straight down on the sidewalk and kerb, 7.5 m across: three by three of the concrete image (2.5 m)"),
    "G3_paving_3x3": ((1500.0, -3000.0, 500.0), (-90.0, 180.0), "straight down on private paving, 7.5 m across: three by three of the concrete image (2.5 m)"),
    "G4_close": ((-400.0, 230.0, 45.0), (-12.0, 180.0), "close: 45 cm above the sidewalk, looking north along it"),
    "G5_road_low": ((2500.0, 900.0, 120.0), (-6.0, 180.0), "low over the roadway, looking north along 70 m and more of it"),
    "G6_wide": ((-754.0, -1557.5, 26000.0), (-90.0, 180.0), "wide: straight down from 260 m, the whole site ground (309 m square)"),
    "G8_carpark_3x3": ((2000.0, -1500.0, 410.0), (-90.0, 180.0), "straight down on the car park south of the lot, 6.15 m across: three by three of the asphalt image, on the ground material itself"),
    "G7_block": ((-754.0, 500.0, 6000.0), (-90.0, 180.0), "straight down from 60 m, 90 m across: street, sidewalks and yards"),
}
SUN_LABEL = "Placeholder_Sun"


def _sun():
    for actor in ws.actors():
        if actor.get_actor_label() == SUN_LABEL:
            return actor
    return None


def sun_pitch(pitch=None):
    """Read, or set for a test, the height of the review daylight (degrees below the horizon line, negative)."""
    sun = _sun()
    rotation = sun.get_actor_rotation()
    before = rotation.pitch
    if pitch is not None:
        sun.set_actor_rotation(unreal.Rotator(pitch=pitch, yaw=rotation.yaw, roll=rotation.roll), False)
    return {"before": round(before, 2), "now": round(sun.get_actor_rotation().pitch, 2)}


def gate_cameras():
    """Temporary cameras for the gate pictures; ws.shots_end() removes them with the station cameras."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_current_level_by_name(ws.world_path().split("/")[-1])
    made = 0
    for name, (place, turn, _what) in GATE_VIEWS.items():
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
