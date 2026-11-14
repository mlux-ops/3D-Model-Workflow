"""Editor-side, Phase 17: the skyline and laser-scan surroundings levels, their facade material, and mesh import.

Runs inside the Unreal editor's Python (through ue_call.py py). Nothing here saves on its own; save() saves named
assets only, never "Save All", and refuses L_R15_Production.

    import wieland_p17 as p
    p.ensure_facade_material()                       # parent material and the panel colour map
    p.ensure_level("/Game/Wieland1529/Surroundings/L_Skyline_P17")
    await p.build(folder, names, mesh_root, folder_label, slots)   # slots: name -> [wall, roof, mast] material paths

Mesh files are those of phase17_towers.py: vertices in level cm about a pivot, triangles, tri_mat (0 wall, 1 roof,
2 mast) and uv0_m (UV channel 0 in metres: along each wall and up from the ground; roofs east and north).
"""

import asyncio
import json
import os
import time

import unreal

ROOT = "/Game/Wieland1529/Surroundings/P17/"
MAT_ROOT = ROOT + "Materials/"
PARENT = MAT_ROOT + "M_W1529_P17_Facade"
NOISE = MAT_ROOT + "T_W1529_P17_PanelNoise"
NOISE_FILE = "E:/Wieland1529_site_data/phase17/textures/T_W1529_P17_PanelNoise.png"
LEVEL_ROOT = "/Game/Wieland1529/Surroundings/"
NEVER_SAVE = "/Game/Wieland/R15_Landscape/L_R15_Production"
TAG_PREFIX = "W1529."

# The window grid, computed per pixel. p is the position in grid cells (one cell = one window bay by one floor); the
# coverage of the glass rectangle is integrated over the pixel's footprint (an analytic box filter), so far away
# the facade averages to the right mix of glass and frame instead of shimmering.
GRID_HLSL = r"""
float2 c = float2(max(Spacing, 0.05), max(FloorH, 0.05));
float2 off = frac(ObjPos.xy * float2(0.000173, 0.000291)) * 512.0;
float2 p = UV / c + off;
float2 lo = float2(0.5 * MullW / c.x, SpandH / c.y);
float2 hi = float2(1.0 - 0.5 * MullW / c.x, 1.0);
float2 w = max(max(abs(ddx(p)), abs(ddy(p))), float2(1e-4, 1e-4));
float2 x0 = p - 0.5 * w;
float2 x1 = p + 0.5 * w;
float2 F0 = floor(x0) * (hi - lo) + clamp(frac(x0), lo, hi) - lo;
float2 F1 = floor(x1) * (hi - lo) + clamp(frac(x1), lo, hi) - lo;
float2 cov = saturate((F1 - F0) / w);
float m = cov.x * cov.y * Pattern;
float fade = saturate(max(w.x, w.y) * 1.5 - 0.25);
float2 cell = floor(p);
return float4(m, fade, (fmod(cell.x, 1024.0) + 0.5) / 1024.0, (fmod(cell.y, 1024.0) + 0.5) / 1024.0);
"""


def _mel():
    return unreal.MaterialEditingLibrary


def ensure_noise_texture():
    if unreal.EditorAssetLibrary.does_asset_exist(NOISE):
        return unreal.EditorAssetLibrary.load_asset(NOISE)
    task = unreal.AssetImportTask()
    task.filename = NOISE_FILE
    task.destination_path = MAT_ROOT[:-1]
    task.destination_name = "T_W1529_P17_PanelNoise"
    task.automated = True
    task.save = False
    task.replace_existing = False
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex = unreal.EditorAssetLibrary.load_asset(NOISE)
    # One texel per window: no filtering, no mip maps, no compression, linear values.
    tex.set_editor_property("filter", unreal.TextureFilter.TF_NEAREST)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
    tex.set_editor_property("srgb", False)
    return tex


def _scalar(mat, name, value, x, y):
    node = _mel().create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", value)
    return node


def _vector(mat, name, rgb, x, y):
    node = _mel().create_material_expression(mat, unreal.MaterialExpressionVectorParameter, x, y)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    return node


def ensure_facade_material():
    """The parent: a window grid in metres on UV channel 0 (u along the wall, v up), glass and frame colours, and a
    per-window variation read from a colour map of random values (one texel per window, 1,024 by 1,024 windows
    before any repeat, offset per building from its position). Far away the variation fades and the grid averages."""
    if unreal.EditorAssetLibrary.does_asset_exist(PARENT):
        return unreal.EditorAssetLibrary.load_asset(PARENT)
    tex = ensure_noise_texture()
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = tools.create_asset("M_W1529_P17_Facade", MAT_ROOT[:-1], unreal.Material, unreal.MaterialFactoryNew())
    _facade_graph(mat, tex)
    return mat


def _mask(mat, x, y, channels):
    """A component mask with every channel set explicitly (unset channels keep defaults that are not all off)."""
    node = _mel().create_material_expression(mat, unreal.MaterialExpressionComponentMask, x, y)
    for c in "rgba":
        node.set_editor_property(c, c in channels)
    return node


def rebuild_facade_material():
    """Rebuild the parent's graph in place (its instances keep their values by parameter name) and report the
    compile result. Fixes the first build's masks, which carried channels they were not meant to."""
    mat = unreal.EditorAssetLibrary.load_asset(PARENT)
    _mel().delete_all_material_expressions(mat)
    _facade_graph(mat, ensure_noise_texture())
    try:
        st = _mel().get_statistics(mat)
        return {"ok": True, "ps": st.num_pixel_shader_instructions, "samplers": st.num_samplers}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _facade_graph(mat, tex):
    mel = _mel()
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1400, 0)
    objpos = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1400, 100)
    params = {
        "FloorH": _scalar(mat, "FloorHeight", 3.9, -1400, 200),
        "Spacing": _scalar(mat, "BayWidth", 1.5, -1400, 280),
        "MullW": _scalar(mat, "FrameWidth", 0.12, -1400, 360),
        "SpandH": _scalar(mat, "SpandrelHeight", 1.0, -1400, 440),
        "Pattern": _scalar(mat, "WindowPattern", 1.0, -1400, 520),
    }
    custom = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -1000, 200)
    custom.set_editor_property("code", GRID_HLSL)
    custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    custom.set_editor_property("description", "P17 window grid")
    inputs = []
    for name in ["UV", "ObjPos"] + list(params.keys()):
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", name)
        inputs.append(ci)
    custom.set_editor_property("inputs", inputs)
    mel.connect_material_expressions(uv, "", custom, "UV")
    mel.connect_material_expressions(objpos, "", custom, "ObjPos")
    for name, node in params.items():
        mel.connect_material_expressions(node, "", custom, name)
    glass_mask = _mask(mat, -700, 100, "r")
    fade = _mask(mat, -700, 200, "g")
    cell_uv = _mask(mat, -700, 300, "ba")
    for node in (glass_mask, fade, cell_uv):
        mel.connect_material_expressions(custom, "", node, "")
    sample = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -500, 300)
    sample.set_editor_property("parameter_name", "PanelVariation")
    sample.set_editor_property("texture", tex)
    sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    mel.connect_material_expressions(cell_uv, "", sample, "UVs")
    # Variation amount, faded with distance: v = (noise - 0.5) * amount * (1 - fade)
    glass = _vector(mat, "GlassColor", (0.05, 0.06, 0.07), -500, -200)
    frame = _vector(mat, "FrameColor", (0.03, 0.03, 0.03), -500, -100)
    gvar = _scalar(mat, "GlassVariation", 0.35, -500, 500)
    fvar = _scalar(mat, "FrameVariation", 0.12, -500, 580)
    groug = _scalar(mat, "GlassRoughness", 0.08, -500, 660)
    frough = _scalar(mat, "FrameRoughness", 0.55, -500, 740)
    gmetal = _scalar(mat, "GlassMetallic", 0.0, -500, 820)
    fmetal = _scalar(mat, "FrameMetallic", 0.0, -500, 900)
    half = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 360)
    half.set_editor_property("r", 0.5)
    r_ch = _mask(mat, -300, 300, "r")
    g_ch = _mask(mat, -300, 420, "g")
    mel.connect_material_expressions(sample, "RGB", r_ch, "")
    mel.connect_material_expressions(sample, "RGB", g_ch, "")
    one_minus = mel.create_material_expression(mat, unreal.MaterialExpressionOneMinus, -300, 200)
    mel.connect_material_expressions(fade, "", one_minus, "")

    def varied(colour, channel, amount, x, y):
        sub = mel.create_material_expression(mat, unreal.MaterialExpressionSubtract, x, y)
        mel.connect_material_expressions(channel, "", sub, "A")
        mel.connect_material_expressions(half, "", sub, "B")
        mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, x + 120, y)
        mel.connect_material_expressions(sub, "", mul, "A")
        mel.connect_material_expressions(amount, "", mul, "B")
        mul2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, x + 240, y)
        mel.connect_material_expressions(mul, "", mul2, "A")
        mel.connect_material_expressions(one_minus, "", mul2, "B")
        add1 = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, x + 360, y)
        mel.connect_material_expressions(mul2, "", add1, "A")
        add1.set_editor_property("const_b", 1.0)
        out = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, x + 480, y)
        mel.connect_material_expressions(colour, "", out, "A")
        mel.connect_material_expressions(add1, "", out, "B")
        return out
    glass_v = varied(glass, r_ch, gvar, -200, -260)
    frame_v = varied(frame, g_ch, fvar, -200, -60)
    base = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, 400, -100)
    mel.connect_material_expressions(frame_v, "", base, "A")
    mel.connect_material_expressions(glass_v, "", base, "B")
    mel.connect_material_expressions(glass_mask, "", base, "Alpha")
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, 400, 100)
    mel.connect_material_expressions(frough, "", rough, "A")
    mel.connect_material_expressions(groug, "", rough, "B")
    mel.connect_material_expressions(glass_mask, "", rough, "Alpha")
    metal = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, 400, 250)
    mel.connect_material_expressions(fmetal, "", metal, "A")
    mel.connect_material_expressions(gmetal, "", metal, "B")
    mel.connect_material_expressions(glass_mask, "", metal, "Alpha")
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    mat.set_editor_property("used_with_nanite", True)
    mel.recompile_material(mat)


def ensure_instance(name, params):
    """A material instance of the facade parent. params: {"GlassColor": (r, g, b), "FloorHeight": 3.9, ...}.
    An instance that exists is updated to the given values."""
    path = MAT_ROOT + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mi = unreal.EditorAssetLibrary.load_asset(path)
    else:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        mi = tools.create_asset(name, MAT_ROOT[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        _mel().set_material_instance_parent(mi, unreal.EditorAssetLibrary.load_asset(PARENT))
    for key, value in params.items():
        if isinstance(value, (list, tuple)):
            _mel().set_material_instance_vector_parameter_value(mi, key, unreal.LinearColor(value[0], value[1], value[2], 1.0))
        else:
            _mel().set_material_instance_scalar_parameter_value(mi, key, float(value))
    _mel().update_material_instance(mi)
    return mi


def world_path():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()


def ensure_level(path):
    """Open the level at path, creating an empty one if it does not exist. Never touches L_R15_Production."""
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        if not world_path().startswith(path + "."):
            les.load_level(path)
    else:
        les.new_level(path)
    return world_path()


def _make_mesh(data):
    mesh = unreal.DynamicMesh()
    buffers = unreal.GeometryScriptSimpleMeshBuffers()
    buffers.vertices = [unreal.Vector(v[0], v[1], v[2]) for v in data["vertices"]]
    buffers.triangles = [unreal.IntVector(t[0], t[1], t[2]) for t in data["triangles"]]
    buffers.uv0 = [unreal.Vector2D(u[0], u[1]) for u in data["uv0_m"]]
    mesh.append_buffers_to_mesh(buffers)
    if mesh.get_num_uv_sets() < 1:
        mesh.set_num_uv_sets(1)
    mesh.enable_material_i_ds()
    ids = unreal.GeometryScript_List.convert_array_to_index_list(list(data["tri_mat"]), unreal.GeometryScriptIndexType.MATERIAL_ID)
    mesh.set_all_triangle_material_i_ds(ids)
    split = unreal.GeometryScriptSplitNormalsOptions()
    split.split_by_opening_angle = True
    split.opening_angle_deg = 35.0
    mesh.compute_split_normals(split, unreal.GeometryScriptCalculateNormalsOptions())
    return mesh


def _existing():
    return {a.get_actor_label(): a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}


async def build(folder, names, mesh_root, folder_label, slots, tags=(), replace=False):
    """Import mesh files as Nanite static meshes under mesh_root and place one object each in the open level (which
    must be under /Game/Wieland1529/Surroundings/). slots: {name: [wall, roof, mast] material paths} or one list
    for all. An object that exists is skipped unless replace=True (then its asset's geometry is replaced)."""
    if not world_path().startswith(LEVEL_ROOT):
        raise RuntimeError("refused: open level %s is not under %s" % (world_path(), LEVEL_ROOT))
    existing = _existing()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    out = {"made": 0, "skipped": 0, "replaced": 0, "problems": [], "records": []}
    started = time.time()
    for name in names:
        with open(os.path.join(folder, name + ".json"), encoding="utf-8") as handle:
            data = json.load(handle)
        if name in existing and not replace:
            out["skipped"] += 1
            continue
        mesh = _make_mesh(data)
        path = mesh_root + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            sm = unreal.EditorAssetLibrary.load_asset(path)
            options = unreal.GeometryScriptCopyMeshToAssetOptions()
            options.enable_recompute_normals = False
            options.emit_transaction = False
            options.replace_materials = False
            unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh, sm, options, unreal.GeometryScriptMeshWriteLOD())
            out["replaced"] += 1
        else:
            options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
            options.enable_nanite = True
            nanite = unreal.MeshNaniteSettings()
            nanite.enabled = True
            options.nanite_settings = nanite
            options.enable_collision = False
            options.enable_recompute_normals = False
            sm, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, path, options)
        if sm is None:
            out["problems"].append(name + ": no asset")
            continue
        settings = meshes.get_nanite_settings(sm)
        if not settings.enabled:
            settings.enabled = True
            meshes.set_nanite_settings(sm, settings, True)
        mats = slots.get(name) if isinstance(slots, dict) else slots
        while len(sm.static_materials) < 3:
            sm.add_material(unreal.EditorAssetLibrary.load_asset(mats[len(sm.static_materials)]))
        for i, mpath in enumerate(mats[:3]):
            sm.set_material(i, unreal.EditorAssetLibrary.load_asset(mpath))
        actor = existing.get(name)
        pivot = data["pivot"]
        if actor is None:
            actor = actors.spawn_actor_from_object(sm, unreal.Vector(pivot[0], pivot[1], pivot[2]), unreal.Rotator(0.0, 0.0, 0.0))
            if actor is None:
                out["problems"].append(name + ": not placed")
                continue
            actor.set_actor_label(name)
            out["made"] += 1
        else:
            actor.set_actor_location(unreal.Vector(pivot[0], pivot[1], pivot[2]), False, False)
        actor.set_folder_path(unreal.Name(folder_label))
        actor.tags = [unreal.Name(TAG_PREFIX + "P17")] + [unreal.Name(TAG_PREFIX + t) for t in tags]
        comp = actor.static_mesh_component
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
        desc = sm.get_static_mesh_description(0)
        out["records"].append({"name": name, "triangles": desc.get_triangle_count() if desc else None,
                               "nanite": bool(meshes.get_nanite_settings(sm).enabled), "sections": len(sm.static_materials)})
        await asyncio.sleep(0)
    out["seconds"] = round(time.time() - started, 1)
    return out


async def swap_build(folder, pairs, mesh_root):
    """Clean-roof rebuild (phase17_clean.py): for each (new mesh name, existing object label), make the new mesh as a
    Nanite static mesh under mesh_root (the old mesh asset is kept, never edited or deleted), give it the old mesh's
    three material slots, and swap it onto the existing object, so the Variant Manager values that name the object
    still hold. Returns records for mesh_swaps.csv; nothing is saved here."""
    if not (world_path().startswith(LEVEL_ROOT) or world_path().startswith(SITE + ".")):
        raise RuntimeError("refused: open level %s is neither the working level nor under %s" % (world_path(), LEVEL_ROOT))
    existing = _existing()
    meshes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    out = {"swapped": 0, "problems": [], "records": [], "assets": []}
    started = time.time()
    for name, label in pairs:
        actor = existing.get(label)
        if actor is None:
            out["problems"].append(label + ": no such object")
            continue
        comp = actor.static_mesh_component
        old = comp.static_mesh
        with open(os.path.join(folder, name + ".json"), encoding="utf-8") as handle:
            data = json.load(handle)
        mesh = _make_mesh(data)
        path = mesh_root + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            sm = unreal.EditorAssetLibrary.load_asset(path)
            options = unreal.GeometryScriptCopyMeshToAssetOptions()
            options.enable_recompute_normals = False
            options.emit_transaction = False
            options.replace_materials = False
            unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh, sm, options, unreal.GeometryScriptMeshWriteLOD())
        else:
            options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
            options.enable_nanite = True
            nanite = unreal.MeshNaniteSettings()
            nanite.enabled = True
            options.nanite_settings = nanite
            options.enable_collision = False
            options.enable_recompute_normals = False
            sm, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, path, options)
        if sm is None:
            out["problems"].append(name + ": no asset")
            continue
        settings = meshes.get_nanite_settings(sm)
        if not settings.enabled:
            settings.enabled = True
            meshes.set_nanite_settings(sm, settings, True)
        mats = [old.get_material(i) for i in range(3)] if old is not None else []
        while len(sm.static_materials) < 3:
            sm.add_material(mats[len(sm.static_materials)] if len(mats) > len(sm.static_materials) else None)
        for i, m in enumerate(mats[:3]):
            if m is not None:
                sm.set_material(i, m)
        pivot = data["pivot"]
        before = actor.get_actor_location()
        comp.set_static_mesh(sm)
        actor.set_actor_location(unreal.Vector(pivot[0], pivot[1], pivot[2]), False, False)
        out["swapped"] += 1
        out["assets"].append(path)
        out["records"].append({"object": label, "old_mesh": old.get_path_name().split(".")[0] if old else "",
                               "new_mesh": path, "triangles": len(data["triangles"]),
                               "moved_cm": round(before.distance(actor.get_actor_location()), 2),
                               "materials": [m.get_name() if m else "" for m in mats[:3]]})
        await asyncio.sleep(0)
    out["seconds"] = round(time.time() - started, 1)
    return out


def save(paths):
    """Save named assets (levels or assets); refuses L_R15_Production."""
    done = []
    for p in paths:
        if p.startswith(NEVER_SAVE):
            raise RuntimeError("refused to save " + p)
        done.append((p, bool(unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False))))
    return done


def save_current_level():
    path = world_path().split(".")[0]
    if path.startswith(NEVER_SAVE):
        raise RuntimeError("refused to save " + path)
    return bool(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())


# ---------------------------------------------------------------------------------------------------------------
# Pictures from the decks, for the check sheets. A temporary camera, piloted, never saved.

SITE = "/Game/Wieland1529/L_Site_M4"
CAM_LABEL = "TEMP_P17_CAM"


def levels():
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    return [l.get_outer().get_path_name().split(".")[0] for l in unreal.EditorLevelUtils.get_levels(w)]


def open_site():
    """Open the working level (changes in the level open now are discarded, never saved)."""
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(SITE)
    return {"world": world_path(), "levels": levels()}


def attach(path):
    """Add a level to the open working level as always loaded (the working level then needs saving by name)."""
    if not world_path().startswith(SITE + "."):
        raise RuntimeError("refused: the working level is not open")
    if path in levels():
        return False
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    return unreal.EditorLevelUtils.add_level_to_world(w, path, unreal.LevelStreamingAlwaysLoaded) is not None


def hide_labels(prefixes, hidden=True):
    """Hide (temporarily, in the editor only; not saved) the objects whose label starts with one of prefixes."""
    n = 0
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if any(a.get_actor_label().startswith(p) for p in prefixes):
            a.set_is_temporarily_hidden_in_editor(hidden)
            n += 1
    return n


def cam(location, rotation, fov_h, ev100=None):
    """Place the temporary camera (level cm; rotation pitch, yaw, roll in degrees) and pilot the viewport with it."""
    cam_end()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    c = sub.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*location), unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
    c.set_actor_label(CAM_LABEL)
    comp = c.camera_component
    comp.set_editor_property("field_of_view", fov_h)
    comp.set_editor_property("constrain_aspect_ratio", True)
    comp.set_editor_property("aspect_ratio", 16.0 / 9.0)
    if ev100 is not None:
        s = comp.get_editor_property("post_process_settings")
        s.set_editor_property("override_auto_exposure_method", True)
        s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
        s.set_editor_property("override_auto_exposure_apply_physical_camera_exposure", True)
        s.set_editor_property("auto_exposure_apply_physical_camera_exposure", False)
        s.set_editor_property("override_auto_exposure_bias", True)
        s.set_editor_property("auto_exposure_bias", -float(ev100))
        comp.set_editor_property("post_process_settings", s)
        comp.set_editor_property("post_process_blend_weight", 1.0)
    ed = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ed.pilot_level_actor(c)
    ed.editor_set_viewport_realtime(True)
    return c


def shot(out_path, width=1920, height=1080):
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() == CAM_LABEL:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            if os.path.exists(out_path):
                os.remove(out_path)
            unreal.AutomationLibrary.take_high_res_screenshot(width, height, out_path, a)
            return True
    return False


async def shot_wait(out_path, width=1920, height=1080, settle_frames=120, wait_frames=1200):
    for _ in range(settle_frames):
        await asyncio.sleep(0)
    if not shot(out_path, width, height):
        return False
    n = 0
    while not os.path.exists(out_path) and n < wait_frames:
        await asyncio.sleep(0.05)
        n += 1
    return os.path.exists(out_path)


def cam_end():
    ed = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = 0
    for a in list(sub.get_all_level_actors()):
        if a.get_actor_label() == CAM_LABEL:
            ed.eject_pilot_level_actor()
            sub.destroy_actor(a)
            n += 1
    return n


# ---------------------------------------------------------------------------------------------------------------
# Switching: the Variant Manager list "Surroundings" with a third option, the new default.

OPTION_P17 = "Laser-scan model (Phase 17)"
P17_LEVELS = ("/Game/Wieland1529/Surroundings/L_Skyline_P17", "/Game/Wieland1529/Surroundings/L_Surroundings_P17")


def _all_actors():
    return list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())


def surroundings_groups():
    """The objects each option shows or hides, by label and tag (read-only)."""
    import wieland_site as ws
    acts = _all_actors()
    hide_list = set(ws.hidden_names())
    r15 = [a for a in acts if any(str(t) == ws.TAG_R15 for t in a.tags)]
    sb = [a for a in acts if a.get_actor_label().startswith("SB_")]
    far = [a for a in acts if a.get_actor_label().startswith("FAR_")]
    p17 = [a for a in acts if any(str(t) == TAG_PREFIX + "P17" for t in a.tags)]
    return {"r15": r15, "sb_hide": [a for a in sb if a.get_actor_label() in hide_list],
            "sb_other": [a for a in sb if a.get_actor_label() not in hide_list], "far": far, "p17": p17}


def build_surroundings_list():
    """Remake the list "Surroundings" with three options, every binding explicit, and save the asset by name:
    Earlier detailed buildings: the earlier copies, the Phase 4 buildings they do not cover, the far-city stand-in.
    Phase 4 survey massing: all Phase 4 buildings and the far-city stand-in.
    Laser-scan model (Phase 17): the Phase 17 buildings, skyline and ground only.
    The ground of Phase 4 and the site works are in no option (always shown)."""
    import wieland_site as ws
    if not world_path().startswith(SITE + "."):
        raise RuntimeError("refused: the working level is not open")
    lib = unreal.VariantManagerLibrary
    sets_asset = ws.variant_asset()
    for index in reversed(range(sets_asset.get_num_variant_sets())):
        old = sets_asset.get_variant_set(index)
        if str(old.get_display_text()) == ws.VARIANT_LIST:
            lib.remove_variant_set(sets_asset, old)
    vset = unreal.VariantSet()
    vset.set_display_text(ws.VARIANT_LIST)
    lib.add_variant_set(sets_asset, vset)
    g = surroundings_groups()
    plan = {
        OPTION_P17: {"r15": False, "sb_hide": False, "sb_other": False, "far": False, "p17": True},
        ws.OPTION_R15: {"r15": True, "sb_hide": False, "sb_other": True, "far": True, "p17": False},
        ws.OPTION_PHASE4: {"r15": False, "sb_hide": True, "sb_other": True, "far": True, "p17": False},
    }
    out = {k: len(v) for k, v in g.items()}
    out["values"] = 0
    out["missed"] = 0
    for option, shown in plan.items():
        variant = unreal.Variant()
        variant.set_display_text(option)
        lib.add_variant(vset, variant)
        for group, visible in shown.items():
            for actor in g[group]:
                lib.add_actor_binding(variant, actor)
                value = lib.capture_property(variant, actor, ws.VISIBLE_PROPERTY)
                if value is None:
                    out["missed"] += 1
                    continue
                lib.set_value_bool(value, visible)
                out["values"] += 1
    out["saved"] = bool(unreal.EditorAssetLibrary.save_loaded_asset(sets_asset, False))
    return out


def set_option_direct(option):
    """Show and hide the option's objects directly (as the Phase 7 pictures do; the switch itself once asserted)."""
    import wieland_site as ws
    g = surroundings_groups()
    plan = {
        OPTION_P17: {"r15": False, "sb_hide": False, "sb_other": False, "far": False, "p17": True},
        ws.OPTION_R15: {"r15": True, "sb_hide": False, "sb_other": True, "far": True, "p17": False},
        ws.OPTION_PHASE4: {"r15": False, "sb_hide": True, "sb_other": True, "far": True, "p17": False},
    }[option]
    changed = 0
    for group, visible in plan.items():
        for actor in g[group]:
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp is None:
                continue
            if bool(comp.get_editor_property("visible")) != visible:
                comp.modify()
                comp.set_visibility(visible, False)
                changed += 1
    return {"option": option, "changed": changed, "groups": {k: len(v) for k, v in g.items()}}


# ---------------------------------------------------------------------------------------------------------------
# Ground beyond the 300 m square: one land-cover colour map over the whole box (no repeat), water apart.

GROUND = MAT_ROOT + "M_W1529_P17_Ground"
LANDCOVER = MAT_ROOT + "T_W1529_P17_LandCover"
LANDCOVER_FILE = "E:/Wieland1529_site_data/phase17/meshes_ground/T_W1529_P17_LandCover.png"


def ensure_ground_material():
    if unreal.EditorAssetLibrary.does_asset_exist(GROUND):
        return unreal.EditorAssetLibrary.load_asset(GROUND)
    if not unreal.EditorAssetLibrary.does_asset_exist(LANDCOVER):
        task = unreal.AssetImportTask()
        task.filename = LANDCOVER_FILE
        task.destination_path = MAT_ROOT[:-1]
        task.destination_name = "T_W1529_P17_LandCover"
        task.automated = True
        task.save = False
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex = unreal.EditorAssetLibrary.load_asset(LANDCOVER)
    tex.set_editor_property("srgb", True)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = tools.create_asset("M_W1529_P17_Ground", MAT_ROOT[:-1], unreal.Material, unreal.MaterialFactoryNew())
    mel = _mel()
    sample = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    sample.set_editor_property("parameter_name", "LandCover")
    sample.set_editor_property("texture", tex)
    rough = _scalar(mat, "Roughness", 0.92, -500, 250)
    mel.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mat.set_editor_property("used_with_nanite", True)
    mel.recompile_material(mat)
    return mat
