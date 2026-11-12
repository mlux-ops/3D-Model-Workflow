"""Phase 5, step 5.2: the seven parent materials and the texture import.

Runs inside the Unreal editor (through the agent server's Python tool):

    import wieland_parents as wpar
    wpar.import_textures(items)      # image files -> textures, saved by name
    wpar.build_parent("Opaque")      # one of PARENT_NAMES, saved by name

A parent material is a recipe with named settings. An instance of it sets
those values and nothing else, so every candidate of this phase is an
instance of one of these seven. Nothing here touches an asset that Datasmith
created, and nothing is saved except the asset being built.
"""

import unreal

from wieland_materials import MATERIALS, MEL

PARENTS = MATERIALS + "/Parents"
TEXTURES = MATERIALS + "/Textures"
CANDIDATES = MATERIALS + "/Candidates"
LIBRARY = MATERIALS + "/Library"
# The building stands 1.18 degrees off the world axes (the station cameras
# look along -88.82 and 1.18 degrees); world mapping is turned to match.
BUILDING_YAW = 1.18
FOOT_M = 0.3048

ST = unreal.MaterialSamplerType
MP = unreal.MaterialProperty
CMOT = unreal.CustomMaterialOutputType

_WORLD_UV = """
float yaw = YawDeg * 0.01745329;
float c = cos(yaw), s = sin(yaw);
float3 p = float3(WP.x * c + WP.y * s, WP.y * c - WP.x * s, WP.z) * 0.01;
float3 n = float3(N.x * c + N.y * s, N.y * c - N.x * s, N.z);
float3 a = abs(n);
float2 uv;
if (a.z >= a.x && a.z >= a.y) { uv = float2(p.x, -p.y); }
else if (a.x >= a.y) { uv = float2(p.y * (n.x >= 0.0 ? 1.0 : -1.0), -p.z); }
else { uv = float2(-p.x * (n.y >= 0.0 ? 1.0 : -1.0), -p.z); }
return Swap > 0.5 ? uv.yx : uv;
"""

_MESH_UV = """
float2 uv = UV * 0.3048;
return Swap > 0.5 ? uv.yx : uv;
"""

_WORLD_NORMAL = """
float yaw = YawDeg * 0.01745329;
float c = cos(yaw), s = sin(yaw);
float3 n = float3(N.x * c + N.y * s, N.y * c - N.x * s, N.z);
float3 a = abs(n);
float3 T, B;
if (a.z >= a.x && a.z >= a.y) { T = float3(1, 0, 0); B = float3(0, -1, 0); }
else if (a.x >= a.y) { T = float3(0, n.x >= 0.0 ? 1.0 : -1.0, 0); B = float3(0, 0, -1); }
else { T = float3(n.y >= 0.0 ? -1.0 : 1.0, 0, 0); B = float3(0, 0, -1); }
if (Swap > 0.5) { float3 t = T; T = B; B = t; }
float3 w = TN.x * T + TN.y * B;
w = float3(w.x * c - w.y * s, w.x * s + w.y * c, w.z);
return normalize(w + TN.z * N);
"""

_STRENGTH = """
float3 n = float3(TN.xy * Strength, TN.z);
return normalize(n);
"""

_VARY = """
float mask = smoothstep(0.38, 0.62, Cloud.r);
float3 colour = lerp(C1, C2, mask);
float shade = 1.0 + Macro * (Cloud2.g - 0.5) * 2.0;
return colour * Tint * shade;
"""

_WEATHER = """
float base = saturate(1.0 - (Height - GroundZ) / max(BaseHeight, 1.0));
float dirt = BaseDirt * base * base * (0.5 + Cloud.r);
float streak = Streaks * smoothstep(0.55, 0.80, StreakCloud.b) * smoothstep(0.30, 0.70, Cloud.g);
float moss = Moss * base * smoothstep(0.50, 0.70, Cloud.g);
float wear = EdgeWear * (1.0 - Paint);
float soil = saturate(dirt + streak);
float3 colour = lerp(Colour, DirtColour, soil);
colour = lerp(colour, MossColour, saturate(moss));
colour = lerp(colour, saturate(colour * 1.3 + 0.05), saturate(wear));
float rough = lerp(Rough, 0.9, saturate(soil + moss));
return float4(colour, rough);
"""

_GLASS = """
float soil = saturate(Dirt * (0.4 + 0.6 * Cloud.r));
float edge = pow(1.0 - saturate(abs(Facing)), 4.0);
float opacity = lerp(lerp(Opacity, OpacityGrazing, edge), 0.85, soil);
float rough = saturate(Rough + 0.5 * soil);
return float2(opacity, rough);
"""

_GROUND = """
float n = (Cloud.r - 0.5) * Contrast + 0.5;
return saturate(n + (Bias - 0.5) * 2.0 + VertexPaint * (0.5 - Paint) * 2.0);
"""


class _Graph:
    """A thin wrapper over the editor's material tools: make nodes, wire them."""

    def __init__(self, material):
        self.material = material
        self.count = 0

    def node(self, cls, **props):
        column, row = self.count // 10, self.count % 10
        expression = MEL.create_material_expression(self.material, cls, -3200 + 300 * column, -900 + 190 * row)
        self.count += 1
        for key, value in props.items():
            expression.set_editor_property(key, value)
        return expression

    def link(self, source, target, pin, output=""):
        if not MEL.connect_material_expressions(source, output, target, pin):
            raise RuntimeError("could not wire %s to pin '%s' of %s" % (source.get_name(), pin, target.get_name()))

    def out(self, source, prop, output=""):
        if not MEL.connect_material_property(source, output, prop):
            raise RuntimeError("could not wire %s to %s" % (source.get_name(), prop))

    def scalar(self, name, default, group):
        return self.node(unreal.MaterialExpressionScalarParameter, parameter_name=name, default_value=default,
                         group=group)

    def vector(self, name, default, group):
        return self.node(unreal.MaterialExpressionVectorParameter, parameter_name=name,
                         default_value=unreal.LinearColor(*default), group=group)

    def switch(self, name, default, group, when_true, when_false):
        expression = self.node(unreal.MaterialExpressionStaticSwitchParameter, parameter_name=name,
                               default_value=default, group=group)
        self.link(when_true, expression, "True")
        self.link(when_false, expression, "False")
        return expression

    def texture(self, name, default, sampler, group):
        return self.node(unreal.MaterialExpressionTextureObjectParameter, parameter_name=name,
                         texture=unreal.load_asset(default), sampler_type=sampler, group=group)

    def sample(self, texture, uv, sampler):
        expression = self.node(unreal.MaterialExpressionTextureSample, sampler_type=sampler,
                               texture=texture.get_editor_property("texture"),
                               sampler_source=unreal.SamplerSourceMode.SSM_WRAP_WORLD_GROUP_SETTINGS)
        self.link(texture, expression, "Tex")
        if uv is not None:
            self.link(uv, expression, "UVs")
        return expression

    def custom(self, description, code, output_type, inputs):
        """inputs: list of (name, node) or (name, node, output name)."""
        expression = self.node(unreal.MaterialExpressionCustom, description=description, code=code.strip(),
                               output_type=output_type)
        pins = []
        for item in inputs:
            pin = unreal.CustomInput()
            pin.set_editor_property("input_name", item[0])
            pins.append(pin)
        expression.set_editor_property("inputs", pins)
        for item in inputs:
            self.link(item[1], expression, item[0], item[2] if len(item) > 2 else "")
        return expression

    def binary(self, cls, a, b):
        expression = self.node(cls)
        self.link(a, expression, "A")
        self.link(b, expression, "B")
        return expression

    def mask(self, source, r=False, g=False, b=False, a=False):
        expression = self.node(unreal.MaterialExpressionComponentMask, r=r, g=g, b=b, a=a)
        self.link(source, expression, "")
        return expression

    def append(self, a, b):
        return self.binary(unreal.MaterialExpressionAppendVector, a, b)

    def constant(self, value):
        return self.node(unreal.MaterialExpressionConstant, r=value)

    def to_tangent(self, world_vector):
        expression = self.node(unreal.MaterialExpressionTransform,
                               transform_source_type=unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_WORLD,
                               transform_type=unreal.MaterialVectorCoordTransform.TRANSFORM_TANGENT)
        self.link(world_vector, expression, "")
        return expression


def _new_material(name):
    """Make (or empty and reuse) a parent material; returns it."""
    path = PARENTS + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.load_asset(path)
        MEL.delete_all_material_expressions(material)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, PARENTS, unreal.Material, unreal.MaterialFactoryNew())
    return material


def _finish(material):
    MEL.layout_material_expressions(material)
    MEL.recompile_material(material)
    errors = [e.get_name() for e in MEL.get_material_error_expressions(material)]
    saved = unreal.EditorAssetLibrary.save_asset(material.get_path_name().split(".")[0], False)
    stats = MEL.get_statistics(material)
    return {"material": material.get_name(), "saved": saved, "errors": errors,
            "pixel_instructions": stats.get_editor_property("num_pixel_shader_instructions"),
            "samplers": stats.get_editor_property("num_samplers")}


def _mapping(g, world=True):
    """Where on the image a point of the surface falls.

    Returns (uv in repeats, uv in metres, turn, swap). In world mode the image
    is laid flat on whichever of the three world planes the surface faces
    most, in metres; in mesh mode the mesh's own coordinates are used, which
    Datasmith writes at 1 per foot.
    """
    size_u = g.scalar("SizeU_m", 1.0, "1 Mapping")
    size_v = g.scalar("SizeV_m", 1.0, "1 Mapping")
    swap = g.scalar("TurnQuarter", 0.0, "1 Mapping")
    coordinate = g.node(unreal.MaterialExpressionTextureCoordinate)
    mesh = g.custom("Mesh coordinates in metres", _MESH_UV, CMOT.CMOT_FLOAT2, [("UV", coordinate), ("Swap", swap)])
    turn = None
    if world:
        turn = g.scalar("WorldYawDeg", BUILDING_YAW, "1 Mapping")
        position = g.node(unreal.MaterialExpressionWorldPosition)
        normal = g.node(unreal.MaterialExpressionVertexNormalWS)
        flat = g.custom("World mapping in metres", _WORLD_UV, CMOT.CMOT_FLOAT2,
                        [("WP", position), ("N", normal), ("YawDeg", turn), ("Swap", swap)])
        metres = g.switch("UseMeshUV", False, "1 Mapping", mesh, flat)
    else:
        metres = mesh
    uv = g.binary(unreal.MaterialExpressionDivide, metres, g.append(size_u, size_v))
    return uv, metres, turn, swap


def _relief(g, tangent_normal, turn, swap, world=True):
    """Relief image to the surface's own frame; world mode needs it turned."""
    strength = g.scalar("NormalStrength", 1.0, "2 Surface")
    strong = g.custom("Relief strength", _STRENGTH, CMOT.CMOT_FLOAT3, [("TN", tangent_normal), ("Strength", strength)])
    if not world:
        return strong
    normal = g.node(unreal.MaterialExpressionVertexNormalWS)
    in_world = g.custom("Relief in world mapping", _WORLD_NORMAL, CMOT.CMOT_FLOAT3,
                        [("TN", strong), ("N", normal), ("YawDeg", turn), ("Swap", swap)])
    # The same switch parameter as in _mapping; both follow one setting.
    return g.switch("UseMeshUV", False, "1 Mapping", strong, g.to_tangent(in_world))


def _surface(name, kind):
    """The Opaque, Metal and Fabric parents share one recipe.

    Colour, relief and roughness images at a physical size; an optional
    second reading of each image, shifted, mixed in through a cloud pattern so
    that the repeat does not show (AntiRepeat); a slow change of brightness
    (MacroVariation); and four weathering layers that are all zero until an
    instance sets them (Weathering).
    """
    material = _new_material(name)
    g = _Graph(material)
    uv, metres, turn, swap = _mapping(g)
    colour_map = g.texture("BaseColorMap", TEXTURES + "/T_W1529_White", ST.SAMPLERTYPE_COLOR, "2 Surface")
    normal_map = g.texture("NormalMap", TEXTURES + "/T_W1529_FlatNormal", ST.SAMPLERTYPE_NORMAL, "2 Surface")
    rough_map = g.texture("RoughnessMap", TEXTURES + "/T_W1529_WhiteLinear", ST.SAMPLERTYPE_MASKS, "2 Surface")
    noise = g.texture("VariationCloud", TEXTURES + "/T_W1529_Noise", ST.SAMPLERTYPE_MASKS, "3 Variation")
    tint = g.vector("Tint", (1, 1, 1, 1), "2 Surface")
    rough_scale = g.scalar("RoughnessScale", 0.5, "2 Surface")
    macro = g.scalar("MacroVariation", 0.0, "3 Variation")
    cloud_size = g.scalar("VariationSize_m", 4.0, "3 Variation")

    cloud_uv = g.binary(unreal.MaterialExpressionDivide, metres, cloud_size)
    cloud = g.sample(noise, cloud_uv, ST.SAMPLERTYPE_MASKS)
    slow_uv = g.node(unreal.MaterialExpressionMultiply, const_b=0.37)
    g.link(cloud_uv, slow_uv, "A")
    cloud_slow = g.sample(noise, slow_uv, ST.SAMPLERTYPE_MASKS)

    shift = g.node(unreal.MaterialExpressionConstant2Vector, r=0.413, g=0.719)
    uv2 = g.binary(unreal.MaterialExpressionAdd, uv, shift)

    def rgb(sample):
        return g.mask(sample, r=True, g=True, b=True)

    c1 = rgb(g.sample(colour_map, uv, ST.SAMPLERTYPE_COLOR))
    c2 = g.switch("AntiRepeat", False, "3 Variation", rgb(g.sample(colour_map, uv2, ST.SAMPLERTYPE_COLOR)), c1)
    n1 = rgb(g.sample(normal_map, uv, ST.SAMPLERTYPE_NORMAL))
    n2 = g.switch("AntiRepeat", False, "3 Variation", rgb(g.sample(normal_map, uv2, ST.SAMPLERTYPE_NORMAL)), n1)
    r1 = rgb(g.sample(rough_map, uv, ST.SAMPLERTYPE_MASKS))
    r2 = g.switch("AntiRepeat", False, "3 Variation", rgb(g.sample(rough_map, uv2, ST.SAMPLERTYPE_MASKS)), r1)

    colour = g.custom("Mix and vary colour", _VARY, CMOT.CMOT_FLOAT3,
                      [("C1", c1), ("C2", c2), ("Cloud", rgb(cloud)), ("Cloud2", rgb(cloud_slow)),
                       ("Tint", tint), ("Macro", macro)])
    blend = g.custom("Mix amount", "return smoothstep(0.38, 0.62, Cloud.r);", CMOT.CMOT_FLOAT1,
                     [("Cloud", rgb(cloud))])

    def mix(a, b):
        expression = g.node(unreal.MaterialExpressionLinearInterpolate)
        g.link(a, expression, "A")
        g.link(b, expression, "B")
        g.link(blend, expression, "Alpha")
        return expression

    rough = g.node(unreal.MaterialExpressionSaturate)
    g.link(g.binary(unreal.MaterialExpressionMultiply, g.mask(mix(r1, r2), r=True), rough_scale), rough, "")
    normal_mixed = mix(n1, n2)

    # Weathering: dirt at wall bases, streaks, moss and edge wear. All four
    # amounts are zero by default, and the whole block is left out of the
    # shader unless an instance turns Weathering on.
    height = g.mask(g.node(unreal.MaterialExpressionWorldPosition), b=True)
    streak_uv = g.binary(unreal.MaterialExpressionDivide, metres,
                         g.node(unreal.MaterialExpressionConstant2Vector, r=0.45, g=7.0))
    streak = g.sample(noise, streak_uv, ST.SAMPLERTYPE_MASKS)
    paint = g.mask(g.node(unreal.MaterialExpressionVertexColor), r=True)
    weathered = g.custom("Weathering", _WEATHER, CMOT.CMOT_FLOAT4, [
        ("Colour", colour), ("Rough", rough), ("Height", height), ("Cloud", rgb(cloud)),
        ("StreakCloud", rgb(streak)), ("Paint", paint),
        ("BaseDirt", g.scalar("BaseDirtAmount", 0.0, "4 Weathering")),
        ("BaseHeight", g.scalar("BaseDirtHeight_cm", 60.0, "4 Weathering")),
        ("GroundZ", g.scalar("GroundHeight_cm", 0.0, "4 Weathering")),
        ("Streaks", g.scalar("StreakAmount", 0.0, "4 Weathering")),
        ("Moss", g.scalar("MossAmount", 0.0, "4 Weathering")),
        ("EdgeWear", g.scalar("EdgeWearAmount", 0.0, "4 Weathering")),
        ("DirtColour", g.vector("DirtColor", (0.05, 0.045, 0.04, 1), "4 Weathering")),
        ("MossColour", g.vector("MossColor", (0.06, 0.09, 0.03, 1), "4 Weathering"))])
    colour_out = g.switch("Weathering", False, "4 Weathering", g.mask(weathered, r=True, g=True, b=True), colour)
    rough_out = g.switch("Weathering", False, "4 Weathering", g.mask(weathered, a=True), rough)

    g.out(colour_out, MP.MP_BASE_COLOR)
    g.out(rough_out, MP.MP_ROUGHNESS)
    g.out(_relief(g, normal_mixed, turn, swap), MP.MP_NORMAL)
    g.out(g.scalar("Metallic", 1.0 if kind == "metal" else 0.0, "2 Surface"), MP.MP_METALLIC)
    g.out(g.scalar("Specular", 0.5, "2 Surface"), MP.MP_SPECULAR)
    if kind == "metal":
        # Brushed metal stretches its highlight across the grain.
        g.out(g.scalar("Anisotropy", 0.0, "2 Surface"), MP.MP_ANISOTROPY)
    if kind == "fabric":
        material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_CLOTH)
        g.out(g.vector("FuzzColor", (0.5, 0.5, 0.5, 1), "2 Surface"), MP.MP_SUBSURFACE_COLOR)
        g.out(g.scalar("ClothAmount", 0.6, "2 Surface"), MP.MP_CUSTOM_DATA0)
    return _finish(material)


def _glass(name):
    """Window glass: tint, reflection, see-through that falls off at a glancing angle, dirt.

    Refracting (off by default) bends what is seen through the pane by the
    index of refraction; it is meant for the offline tier.
    """
    material = _new_material(name)
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    material.set_editor_property("translucency_lighting_mode",
                                 unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    material.set_editor_property("two_sided", True)
    g = _Graph(material)
    uv, metres, turn, swap = _mapping(g)
    normal_map = g.texture("NormalMap", TEXTURES + "/T_W1529_FlatNormal", ST.SAMPLERTYPE_NORMAL, "2 Surface")
    noise = g.texture("VariationCloud", TEXTURES + "/T_W1529_Noise", ST.SAMPLERTYPE_MASKS, "3 Variation")
    cloud = g.mask(g.sample(noise, g.binary(unreal.MaterialExpressionDivide, metres,
                                            g.scalar("VariationSize_m", 1.5, "3 Variation")), ST.SAMPLERTYPE_MASKS),
                   r=True, g=True, b=True)
    tint = g.vector("Tint", (0.9, 0.95, 0.93, 1), "2 Surface")
    dirt = g.scalar("DirtAmount", 0.0, "4 Weathering")
    dirt_colour = g.vector("DirtColor", (0.25, 0.23, 0.2, 1), "4 Weathering")
    facing = g.node(unreal.MaterialExpressionDotProduct)
    g.link(g.node(unreal.MaterialExpressionVertexNormalWS), facing, "A")
    g.link(g.node(unreal.MaterialExpressionCameraVectorWS), facing, "B")
    both = g.custom("See-through and roughness", _GLASS, CMOT.CMOT_FLOAT2, [
        ("Opacity", g.scalar("Opacity", 0.12, "2 Surface")),
        ("OpacityGrazing", g.scalar("OpacityGrazing", 0.6, "2 Surface")),
        ("Rough", g.scalar("Roughness", 0.03, "2 Surface")),
        ("Facing", facing), ("Dirt", dirt), ("Cloud", cloud)])
    soil = g.custom("Dirt amount", "return saturate(Dirt * (0.4 + 0.6 * Cloud.r));", CMOT.CMOT_FLOAT1,
                    [("Dirt", dirt), ("Cloud", cloud)])
    colour = g.node(unreal.MaterialExpressionLinearInterpolate)
    g.link(tint, colour, "A")
    g.link(dirt_colour, colour, "B")
    g.link(soil, colour, "Alpha")
    g.out(colour, MP.MP_BASE_COLOR)
    g.out(g.mask(both, r=True), MP.MP_OPACITY)
    g.out(g.mask(both, g=True), MP.MP_ROUGHNESS)
    g.out(g.scalar("Specular", 0.5, "2 Surface"), MP.MP_SPECULAR)
    g.out(g.scalar("Metallic", 0.0, "2 Surface"), MP.MP_METALLIC)
    sample = g.mask(g.sample(normal_map, uv, ST.SAMPLERTYPE_NORMAL), r=True, g=True, b=True)
    g.out(_relief(g, sample, turn, swap), MP.MP_NORMAL)
    index = g.scalar("IndexOfRefraction", 1.52, "5 Offline tier")
    g.out(g.switch("Refracting", False, "5 Offline tier", index, g.constant(1.0)), MP.MP_REFRACTION)
    return _finish(material)


def _foliage(name):
    """Leaves and bark: a cut-out image lit from both sides; IsBark turns the cut-out off."""
    material = _new_material(name)
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    material.set_editor_property("two_sided", True)
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
    g = _Graph(material)
    uv, _metres, _turn, _swap = _mapping(g, world=False)
    colour_map = g.texture("BaseColorMap", TEXTURES + "/T_W1529_White", ST.SAMPLERTYPE_COLOR, "2 Surface")
    normal_map = g.texture("NormalMap", TEXTURES + "/T_W1529_FlatNormal", ST.SAMPLERTYPE_NORMAL, "2 Surface")
    sample = g.sample(colour_map, uv, ST.SAMPLERTYPE_COLOR)
    colour = g.node(unreal.MaterialExpressionMultiply)
    g.link(sample, colour, "A", "RGB")
    g.link(g.vector("Tint", (1, 1, 1, 1), "2 Surface"), colour, "B")
    g.out(colour, MP.MP_BASE_COLOR)
    alpha = g.node(unreal.MaterialExpressionMultiply, const_b=1.0)
    g.link(sample, alpha, "A", "A")
    g.out(g.switch("IsBark", False, "2 Surface", g.constant(1.0), alpha), MP.MP_OPACITY_MASK)
    g.out(g.scalar("Roughness", 0.6, "2 Surface"), MP.MP_ROUGHNESS)
    g.out(g.scalar("Specular", 0.3, "2 Surface"), MP.MP_SPECULAR)
    through = g.node(unreal.MaterialExpressionMultiply)
    g.link(colour, through, "A")
    g.link(g.vector("SubsurfaceTint", (0.5, 0.6, 0.2, 1), "2 Surface"), through, "B")
    g.out(through, MP.MP_SUBSURFACE_COLOR)
    relief = g.mask(g.sample(normal_map, uv, ST.SAMPLERTYPE_NORMAL), r=True, g=True, b=True)
    g.out(_relief(g, relief, None, None, world=False), MP.MP_NORMAL)
    return _finish(material)


def _ground(name):
    """Two ground covers laid flat from above in metres, mixed through a cloud pattern.

    BlendBias moves the edge between them; VertexPaint lets painted vertex
    colour (red) decide where each lies, for the edges of paving and planting.
    """
    material = _new_material(name)
    g = _Graph(material)
    position = g.node(unreal.MaterialExpressionWorldPosition)
    metres = g.node(unreal.MaterialExpressionMultiply, const_b=0.01)
    g.link(g.mask(position, r=True, g=True), metres, "A")
    noise = g.texture("VariationCloud", TEXTURES + "/T_W1529_Noise", ST.SAMPLERTYPE_MASKS, "3 Variation")
    cloud = g.mask(g.sample(noise, g.binary(unreal.MaterialExpressionDivide, metres,
                                            g.scalar("BlendSize_m", 3.0, "3 Variation")), ST.SAMPLERTYPE_MASKS),
                   r=True, g=True, b=True)
    alpha = g.custom("Where cover B lies", _GROUND, CMOT.CMOT_FLOAT1, [
        ("Cloud", cloud), ("Contrast", g.scalar("BlendContrast", 4.0, "3 Variation")),
        ("Bias", g.scalar("BlendBias", 0.5, "3 Variation")),
        ("VertexPaint", g.scalar("VertexPaint", 0.0, "3 Variation")),
        ("Paint", g.mask(g.node(unreal.MaterialExpressionVertexColor), r=True))])

    def layer(letter, tint_default, rough_default):
        group = "2 Cover " + letter
        uv = g.binary(unreal.MaterialExpressionDivide, metres, g.scalar(letter + "_Size_m", 2.0, group))
        colour_map = g.texture(letter + "_BaseColorMap", TEXTURES + "/T_W1529_White", ST.SAMPLERTYPE_COLOR, group)
        normal_map = g.texture(letter + "_NormalMap", TEXTURES + "/T_W1529_FlatNormal", ST.SAMPLERTYPE_NORMAL, group)
        colour = g.node(unreal.MaterialExpressionMultiply)
        g.link(g.sample(colour_map, uv, ST.SAMPLERTYPE_COLOR), colour, "A", "RGB")
        g.link(g.vector(letter + "_Tint", tint_default, group), colour, "B")
        normal = g.mask(g.sample(normal_map, uv, ST.SAMPLERTYPE_NORMAL), r=True, g=True, b=True)
        return colour, normal, g.scalar(letter + "_Roughness", rough_default, group)

    def mix(a, b):
        expression = g.node(unreal.MaterialExpressionLinearInterpolate)
        g.link(a, expression, "A")
        g.link(b, expression, "B")
        g.link(alpha, expression, "Alpha")
        return expression

    a, b = layer("A", (0.10, 0.08, 0.06, 1), 0.95), layer("B", (0.12, 0.17, 0.06, 1), 0.85)
    g.out(mix(a[0], b[0]), MP.MP_BASE_COLOR)
    g.out(mix(a[2], b[2]), MP.MP_ROUGHNESS)
    # Seen from above, the image's right is world +X and its down is world +Y,
    # so the relief image's three numbers are already a world direction.
    flat = g.custom("Relief laid flat", "return normalize(TN);", CMOT.CMOT_FLOAT3, [("TN", mix(a[1], b[1]))])
    g.out(g.to_tangent(flat), MP.MP_NORMAL)
    return _finish(material)


def _decal(name):
    """A decal: an image with its own cut-out, projected onto whatever lies under it."""
    material = _new_material(name)
    material.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    g = _Graph(material)
    colour_map = g.texture("ColorMap", TEXTURES + "/T_W1529_White", ST.SAMPLERTYPE_COLOR, "2 Surface")
    normal_map = g.texture("NormalMap", TEXTURES + "/T_W1529_FlatNormal", ST.SAMPLERTYPE_NORMAL, "2 Surface")
    sample = g.sample(colour_map, None, ST.SAMPLERTYPE_COLOR)
    colour = g.node(unreal.MaterialExpressionMultiply)
    g.link(sample, colour, "A", "RGB")
    g.link(g.vector("Tint", (1, 1, 1, 1), "2 Surface"), colour, "B")
    g.out(colour, MP.MP_BASE_COLOR)
    opacity = g.node(unreal.MaterialExpressionMultiply)
    g.link(sample, opacity, "A", "A")
    g.link(g.scalar("Opacity", 1.0, "2 Surface"), opacity, "B")
    g.out(opacity, MP.MP_OPACITY)
    g.out(g.scalar("Roughness", 0.8, "2 Surface"), MP.MP_ROUGHNESS)
    g.out(g.mask(g.sample(normal_map, None, ST.SAMPLERTYPE_NORMAL), r=True, g=True, b=True), MP.MP_NORMAL)
    return _finish(material)


PARENT_NAMES = {
    "Opaque": "M_W1529_Opaque", "Glass": "M_W1529_Glass", "Metal": "M_W1529_Metal", "Fabric": "M_W1529_Fabric",
    "Foliage": "M_W1529_Foliage", "Ground": "M_W1529_GroundBlend", "Decal": "M_W1529_Decal",
}


def build_parent(key):
    """Build and save one of the seven parents; rebuilding an existing one keeps its instances."""
    name = PARENT_NAMES[key]
    if key in ("Opaque", "Metal", "Fabric"):
        return _surface(name, key.lower())
    return {"Glass": _glass, "Foliage": _foliage, "Ground": _ground, "Decal": _decal}[key](name)


def import_textures(items):
    """Import image files as textures and save each by name.

    items: list of [file, destination folder, asset name, kind], where kind is
    "colour", "normal" or "mask" (numbers, not colour: roughness, clouds).
    Existing assets are left alone.
    """
    tasks, wanted = [], []
    for source, folder, name, kind in items:
        if unreal.EditorAssetLibrary.does_asset_exist(folder + "/" + name):
            continue
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", source)
        task.set_editor_property("destination_path", folder)
        task.set_editor_property("destination_name", name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("save", False)
        tasks.append(task)
        wanted.append((folder + "/" + name, kind))
    if tasks:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    result = {"imported": [], "failed": [], "already_there": len(items) - len(tasks)}
    for path, kind in wanted:
        texture = unreal.load_asset(path)
        if texture is None:
            result["failed"].append(path)
            continue
        if kind == "normal":
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        elif kind == "mask":
            texture.set_editor_property("srgb", False)
            texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        else:
            texture.set_editor_property("srgb", True)
        unreal.EditorAssetLibrary.save_asset(path, False)
        result["imported"].append([path, texture.blueprint_get_size_x(), texture.blueprint_get_size_y()])
    return result
