"""Procedural rebuild of the John Hancock Center skyline mesh (P17T_824823 in L_Skyline_P17).

Builds a clean tapered tower with proud exterior X-bracing, horizontal ties at the X nodes,
corner columns, a louvred mechanical band, roof cap, roof penthouse and twin antenna masts.
Writes new assets only; the original P17R_824823 mesh is left untouched.

Run inside the Unreal Editor Python environment:
    exec(open(r'<this file>').read())
"""
import math
import unreal

# ---------------------------------------------------------------------------
# Asset locations
# ---------------------------------------------------------------------------
MESH_DIR = '/Game/Wieland1529/Surroundings/P17/TowersClean'
MESH_NAME = 'SM_P17_Hancock'
MAT_DIR = '/Game/Wieland1529/Surroundings/P17/Materials'
FACADE_PARENT = MAT_DIR + '/M_W1529_P17_Facade'
ROOF_MI = MAT_DIR + '/MI_P17_Roof_Grey'
MAST_MI = MAT_DIR + '/MI_P17_Mast_White'

# ---------------------------------------------------------------------------
# Tower dimensions (cm, mesh-local space of the P17T_824823 actor)
# Building frame: X = short axis, Y = long axis, Z = up.
# Real tower: 165 x 265 ft at grade tapering to 100 x 160 ft at the 1,128 ft roof.
# ---------------------------------------------------------------------------
CX, CY = -170.0, -250.0          # footprint centre measured from the original mesh
YAW = math.radians(0.5)          # grid rotation measured from the original mesh
ZG = -120.0                      # grade at the tower base (lowest point of the scan mesh)
ZBURY = -400.0                   # shaft bottom, buried below uneven terrain
# Heights stay the laser scan's (Phase 17): the scan mesh P17R_824823 has its main roof at local
# Z 34,360 cm, the rooftop structure at 34,593 cm, the mast bases at 35,153 cm, and mast tips at
# 43,155 cm (local -Y) and 42,463 cm (local +Y); Phase 17 table: masts 431.74 m above ground.
ZR = 34360.0                     # main roof, scan level
ROOFTOP_TOP = 34593.0            # rooftop structure, scan level
MAST_BASE_TOP = 35153.0          # mast bases, scan level
HX0, HY0 = 5029.0 * 0.5, 8077.0 * 0.5
HXR, HYR = 3048.0 * 0.5, 4877.0 * 0.5
KX = (HXR - HX0) / (ZR - ZG)     # half-width change per cm of height
KY = (HYR - HY0) / (ZR - ZG)

# Bracing layout: five stacked X's per face, nodes shared by all four faces.
N_PANELS = 5
Z_NODE0 = ZG + 900.0
NODES = [Z_NODE0 + i * (ZR - Z_NODE0) / N_PANELS for i in range(N_PANELS + 1)]

DIAG_W = 260.0                   # diagonal member width
DIAG_D = (46.0, 54.0)            # protrusion of the two diagonals of each X
DIAG_TRIM = 140.0                # pull diagonal ends back into the node blocks
TIE_H = 260.0                    # horizontal tie height
TIE_D = 62.0                     # tie protrusion
TOP_TIE = (ZR - 420.0, ZR + 150.0)
COL_W = 300.0                    # corner column width along each face
COL_D = 70.0                     # corner column protrusion
EMBED = 15.0                     # how far members sink into the glass plane

LOUVRE_Z = ZR - 1100.0           # mechanical floors band
PENT_HALF = (700.0, 2200.0)
MASTS = [  # (building-frame y offset, tip local Z), at the scan mesh's mast positions and heights
    (-1680.0, 43155.0),
    (1355.0, 42463.0),
]

# Low annex / plaza structures kept from the original mesh (outside the new footprint).
SOURCE_MESH = MESH_DIR + '/P17R_824823'
SOURCE_FACADE_MI = MAT_DIR + '/MI_P17_T_824823'
PODIUM_MAX_Z = 2330.0
PODIUM_MARGIN = 150.0

FLIP = True  # UE front faces wind opposite to the right-hand outward normal


def hx(z):
    return HX0 + KX * (z - ZG)


def hy(z):
    return HY0 + KY * (z - ZG)


# ---------------------------------------------------------------------------
# Small vector helpers (tuples)
# ---------------------------------------------------------------------------
def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def length(a):
    return math.sqrt(dot(a, a))


def norm(a):
    l = length(a)
    return (a[0] / l, a[1] / l, a[2] / l)


def to_local(p):
    c, s = math.cos(YAW), math.sin(YAW)
    return (CX + p[0] * c - p[1] * s, CY + p[0] * s + p[1] * c, p[2])


def to_building(p):
    c, s = math.cos(YAW), math.sin(YAW)
    dx, dy = p[0] - CX, p[1] - CY
    return (dx * c + dy * s, -dx * s + dy * c, p[2])


# ---------------------------------------------------------------------------
# Geometry accumulator: quads stored per material slot, oriented outward
# ---------------------------------------------------------------------------
QUADS = {}


def quad(slot, pts, uvs, inside):
    """Store a planar quad whose front faces away from the point `inside`."""
    n = cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))
    if length(n) < 1e-6:
        n = cross(sub(pts[2], pts[0]), sub(pts[3], pts[0]))
    ctr = mul(add(add(pts[0], pts[1]), add(pts[2], pts[3])), 0.25)
    if dot(n, sub(ctr, inside)) < 0.0:
        pts = [pts[0], pts[3], pts[2], pts[1]]
        uvs = [uvs[0], uvs[3], uvs[2], uvs[1]]
    QUADS.setdefault(slot, []).append((pts, uvs))


def planar_uvs(pts):
    """Metre UVs from the quad's own edges (members and caps)."""
    u_axis = sub(pts[1], pts[0])
    lu = length(u_axis)
    u_axis = norm(u_axis) if lu > 1e-6 else (1.0, 0.0, 0.0)
    nrm = cross(sub(pts[1], pts[0]), sub(pts[3], pts[0]))
    v_axis = norm(cross(nrm, u_axis)) if length(nrm) > 1e-6 else (0.0, 0.0, 1.0)
    return [(dot(sub(p, pts[0]), u_axis) / 100.0, dot(sub(p, pts[0]), v_axis) / 100.0) for p in pts]


def hexa(slot, ring_a, ring_b, caps=True):
    """Closed six-sided solid from two corresponding 4-point rings."""
    allp = ring_a + ring_b
    inside = mul((sum(p[0] for p in allp), sum(p[1] for p in allp), sum(p[2] for p in allp)), 1.0 / 8.0)
    for i in range(4):
        j = (i + 1) % 4
        pts = [ring_a[i], ring_a[j], ring_b[j], ring_b[i]]
        quad(slot, pts, planar_uvs(pts), inside)
    if caps:
        quad(slot, list(ring_a), planar_uvs(list(ring_a)), inside)
        quad(slot, list(ring_b), planar_uvs(list(ring_b)), inside)


# ---------------------------------------------------------------------------
# Tower parts
# ---------------------------------------------------------------------------
FACES = [('x', 1.0), ('x', -1.0), ('y', 1.0), ('y', -1.0)]


def face_point(face, t, z):
    axis, s = face
    if axis == 'x':
        return (s * hx(z), t * hy(z), z)
    return (t * hx(z), s * hy(z), z)


def face_normal(face):
    axis, s = face
    if axis == 'x':
        return norm((s, 0.0, -KX))
    return norm((0.0, s, -KY))


def face_base_width_m(face):
    return (2.0 * HY0 if face[0] == 'x' else 2.0 * HX0) / 100.0


def build_shaft():
    z_breaks = [ZBURY, ZG]
    step = 1700.0
    z = ZG + step
    while z < LOUVRE_Z - 200.0:
        z_breaks.append(z)
        z += step
    z_breaks += [LOUVRE_Z, ZR]
    for face in FACES:
        n_t = 24 if face[0] == 'x' else 16
        w0 = face_base_width_m(face)
        for i in range(n_t):
            t0 = -1.0 + 2.0 * i / n_t
            t1 = -1.0 + 2.0 * (i + 1) / n_t
            u0 = (t0 + 1.0) * 0.5 * w0
            u1 = (t1 + 1.0) * 0.5 * w0
            for k in range(len(z_breaks) - 1):
                za, zb = z_breaks[k], z_breaks[k + 1]
                slot = 'Louvre' if za >= LOUVRE_Z - 1.0 else 'Glass'
                pts = [face_point(face, t0, za), face_point(face, t1, za),
                       face_point(face, t1, zb), face_point(face, t0, zb)]
                va, vb = (za - ZG) / 100.0, (zb - ZG) / 100.0
                uvs = [(u0, va), (u1, va), (u1, vb), (u0, vb)]
                quad(slot, pts, uvs, (0.0, 0.0, 0.5 * (za + zb)))
    roof = [(-hx(ZR), -hy(ZR), ZR), (hx(ZR), -hy(ZR), ZR), (hx(ZR), hy(ZR), ZR), (-hx(ZR), hy(ZR), ZR)]
    quad('Roof', roof, planar_uvs(roof), (0.0, 0.0, ZR - 1000.0))


def build_corner_columns():
    z_top = TOP_TIE[1]
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            def ring(z):
                x_in, x_out = sx * (hx(z) - COL_W), sx * (hx(z) + COL_D)
                y_in, y_out = sy * (hy(z) - COL_W), sy * (hy(z) + COL_D)
                return [(x_in, y_in, z), (x_out, y_in, z), (x_out, y_out, z), (x_in, y_out, z)]
            hexa('Structure', ring(ZBURY), ring(z_top))


def build_ties():
    bands = [(zn - TIE_H * 0.5, zn + TIE_H * 0.5) for zn in NODES[:-1]] + [TOP_TIE]
    for (za, zb) in bands:
        for face in FACES:
            axis, s = face

            def ring(z):
                if axis == 'x':
                    xi, xo, yh = s * (hx(z) - EMBED), s * (hx(z) + TIE_D), hy(z)
                    return [(xi, -yh, z), (xo, -yh, z), (xo, yh, z), (xi, yh, z)]
                yi, yo, xh = s * (hy(z) - EMBED), s * (hy(z) + TIE_D), hx(z)
                return [(-xh, yi, z), (-xh, yo, z), (xh, yo, z), (xh, yi, z)]
            hexa('Structure', ring(za), ring(zb))


def diagonal(face, p0, p1, depth):
    e = sub(p1, p0)
    l = length(e)
    e_n = mul(e, 1.0 / l)
    p0 = add(p0, mul(e_n, DIAG_TRIM))
    p1 = sub(p1, mul(e_n, DIAG_TRIM))
    n = face_normal(face)
    b = norm(cross(n, e_n))
    hw = DIAG_W * 0.5

    def ring(p):
        return [add(add(p, mul(b, -hw)), mul(n, -EMBED)),
                add(add(p, mul(b, hw)), mul(n, -EMBED)),
                add(add(p, mul(b, hw)), mul(n, depth)),
                add(add(p, mul(b, -hw)), mul(n, depth))]
    hexa('Structure', ring(p0), ring(p1))


def build_bracing():
    for face in FACES:
        for k in range(N_PANELS):
            za, zb = NODES[k], NODES[k + 1]
            diagonal(face, face_point(face, -1.0, za), face_point(face, 1.0, zb), DIAG_D[0])
            diagonal(face, face_point(face, 1.0, za), face_point(face, -1.0, zb), DIAG_D[1])


def build_roof_and_masts():
    px, py = PENT_HALF
    z0, z1 = ZR, ROOFTOP_TOP

    def box_ring(cx, cy, hxx, hyy, z):
        return [(cx - hxx, cy - hyy, z), (cx + hxx, cy - hyy, z), (cx + hxx, cy + hyy, z), (cx - hxx, cy + hyy, z)]
    hexa('Structure', box_ring(0.0, 0.0, px, py, z0 - 50.0), box_ring(0.0, 0.0, px, py, z1))
    for (my, z_tip) in MASTS:
        hexa('Structure', box_ring(0.0, my, 420.0, 420.0, z1 - 20.0), box_ring(0.0, my, 380.0, 380.0, MAST_BASE_TOP))
        span = z_tip - MAST_BASE_TOP
        segs = [(0.0, 0.30, 190.0, 125.0), (0.30, 0.70, 125.0, 75.0), (0.70, 1.0, 75.0, 28.0)]
        for (f0, f1, h0, h1) in segs:
            za = MAST_BASE_TOP + span * f0
            zb = MAST_BASE_TOP + span * f1
            hexa('Mast', box_ring(0.0, my, h0, h0, za), box_ring(0.0, my, h1, h1, zb))


RAW_TRIS = {}


def collect_podium():
    """Copy low original triangles that sit clearly outside the new tower footprint."""
    src = unreal.load_asset(SOURCE_MESH)
    md = src.get_static_mesh_description(0)
    group_slot = {0: 'Podium', 1: 'Roof'}
    kept = 0
    for t in range(md.get_triangle_count()):
        tid = unreal.TriangleID(t)
        if not md.is_triangle_valid(tid):
            continue
        slot = group_slot.get(md.get_triangle_polygon_group(tid).id_value)
        if slot is None:
            continue
        vis = md.get_triangle_vertex_instances(tid)
        pts, uvs = [], []
        for vi in vis:
            p = md.get_vertex_position(md.get_vertex_instance_vertex(vi))
            pts.append((p.x, p.y, p.z))
            uv = md.get_vertex_instance_uv(vi, 0)
            uvs.append((uv.x, uv.y))
        if max(p[2] for p in pts) > PODIUM_MAX_Z:
            continue
        ctr = to_building((sum(p[0] for p in pts) / 3.0, sum(p[1] for p in pts) / 3.0, sum(p[2] for p in pts) / 3.0))
        zc = max(ctr[2], ZG)
        inside = abs(ctr[0]) < hx(zc) + PODIUM_MARGIN and abs(ctr[1]) < hy(zc) + PODIUM_MARGIN
        if inside:
            continue
        RAW_TRIS.setdefault(slot, []).append((pts, uvs))
        kept += 1
    return kept


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def get_or_create_mi(name, scalars, vectors):
    path = MAT_DIR + '/' + name
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        mi = tools.create_asset(name, MAT_DIR, unreal.MaterialInstanceConstant,
                                unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, unreal.load_asset(FACADE_PARENT))
    for k, v in scalars.items():
        mel.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, c in vectors.items():
        mel.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(c[0], c[1], c[2], 1.0))
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi, only_if_is_dirty=False)
    return mi


def build_materials():
    glass = get_or_create_mi('MI_P17_Hancock_Glass', {
        'WindowPattern': 1.0, 'FloorHeight': 3.35, 'BayWidth': 1.55, 'FrameWidth': 0.22,
        'SpandrelHeight': 0.95, 'GlassRoughness': 0.08, 'GlassMetallic': 0.6, 'GlassVariation': 0.3,
        'FrameRoughness': 0.5, 'FrameMetallic': 0.3, 'FrameVariation': 0.05,
    }, {'GlassColor': (0.095, 0.080, 0.062), 'FrameColor': (0.012, 0.012, 0.013)})
    structure = get_or_create_mi('MI_P17_Hancock_Structure', {
        'WindowPattern': 0.0, 'FrameRoughness': 0.6, 'FrameMetallic': 0.2, 'FrameVariation': 0.02,
    }, {'GlassColor': (0.008, 0.008, 0.009), 'FrameColor': (0.008, 0.008, 0.009)})
    louvre = get_or_create_mi('MI_P17_Hancock_Louvre', {
        'WindowPattern': 1.0, 'FloorHeight': 0.45, 'BayWidth': 0.30, 'FrameWidth': 0.10,
        'SpandrelHeight': 0.12, 'GlassRoughness': 0.45, 'GlassMetallic': 0.2, 'GlassVariation': 0.05,
        'FrameRoughness': 0.5, 'FrameMetallic': 0.3, 'FrameVariation': 0.02,
    }, {'GlassColor': (0.022, 0.022, 0.024), 'FrameColor': (0.045, 0.045, 0.047)})
    return {
        'Glass': glass,
        'Structure': structure,
        'Louvre': louvre,
        'Roof': unreal.load_asset(ROOF_MI),
        'Mast': unreal.load_asset(MAST_MI),
        'Podium': unreal.load_asset(SOURCE_FACADE_MI),
    }


# ---------------------------------------------------------------------------
# Mesh asset
# ---------------------------------------------------------------------------
SLOT_ORDER = ['Glass', 'Structure', 'Louvre', 'Roof', 'Mast', 'Podium']


def build_mesh(mats):
    path = MESH_DIR + '/' + MESH_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mesh = unreal.load_asset(path)
    else:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        mesh = tools.create_asset(MESH_NAME, MESH_DIR, unreal.StaticMesh, None)
        if mesh is None:
            raise RuntimeError('Could not create ' + path)

    static_mats = []
    for name in SLOT_ORDER:
        sm = unreal.StaticMaterial(material_interface=mats[name], material_slot_name=name)
        static_mats.append(sm)
    mesh.set_editor_property('static_materials', static_mats)

    desc = unreal.StaticMesh.create_static_mesh_description(mesh)
    groups = {}
    for name in SLOT_ORDER:
        pg = desc.create_polygon_group()
        desc.set_polygon_group_material_slot_name(pg, name)
        groups[name] = pg

    n_quads = sum(len(v) for v in QUADS.values())
    n_raw = sum(len(v) for v in RAW_TRIS.values())
    desc.reserve_new_vertices(n_quads * 4 + n_raw * 3)
    desc.reserve_new_vertex_instances(n_quads * 4 + n_raw * 3)
    desc.reserve_new_triangles(n_quads * 2 + n_raw)

    # Original podium triangles keep their source winding and UVs (already mesh-local).
    for name in SLOT_ORDER:
        pg = groups[name]
        for pts, uvs in RAW_TRIS.get(name, []):
            vis = []
            for p, uv in zip(pts, uvs):
                vid = desc.create_vertex()
                desc.set_vertex_position(vid, unreal.Vector(p[0], p[1], p[2]))
                vi = desc.create_vertex_instance(vid)
                desc.set_vertex_instance_uv(vi, unreal.Vector2D(uv[0], uv[1]), 0)
                vis.append(vi)
            desc.create_triangle(pg, vis)

    for name in SLOT_ORDER:
        pg = groups[name]
        for pts, uvs in QUADS.get(name, []):
            vis = []
            for p, uv in zip(pts, uvs):
                vid = desc.create_vertex()
                lp = to_local(p)
                desc.set_vertex_position(vid, unreal.Vector(lp[0], lp[1], lp[2]))
                vi = desc.create_vertex_instance(vid)
                desc.set_vertex_instance_uv(vi, unreal.Vector2D(uv[0], uv[1]), 0)
                vis.append(vi)
            tris = [(vis[0], vis[1], vis[2]), (vis[0], vis[2], vis[3])]
            for tri in tris:
                order = [tri[0], tri[2], tri[1]] if FLIP else list(tri)
                desc.create_triangle(pg, order)

    mesh.build_from_static_mesh_descriptions([desc], False, False)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False)
    return mesh, n_quads


def run():
    QUADS.clear()
    RAW_TRIS.clear()
    n_podium = collect_podium()
    build_shaft()
    build_corner_columns()
    build_ties()
    build_bracing()
    build_roof_and_masts()
    mats = build_materials()
    mesh, n_quads = build_mesh(mats)
    bb = mesh.get_bounding_box()
    return (f'{mesh.get_path_name()} quads={n_quads} podium_tris={n_podium} tris={mesh.get_num_triangles(0)} '
            f'min=({bb.min.x:.0f},{bb.min.y:.0f},{bb.min.z:.0f}) max=({bb.max.x:.0f},{bb.max.y:.0f},{bb.max.z:.0f}) '
            f'slots={[str(m.material_slot_name) for m in mesh.static_materials]} nodes={[round(z) for z in NODES]}')


RESULT = run()
