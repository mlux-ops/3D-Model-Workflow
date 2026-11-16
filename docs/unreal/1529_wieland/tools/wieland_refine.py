"""Phase 6 geometry refinement for the 1529 N. Wieland scene. Runs inside the Unreal editor.

Two jobs:

1. Count sharp edges near a camera. A sharp edge is a mesh edge where two faces meet at an
   outward (convex) corner and turn by SHARP_ANGLE degrees or more with nothing rounding it.
   Two faces lying back to back (a turn of SHEET_ANGLE or more) are the rim of a sheet that
   Revit modelled without thickness; that is not counted, because there is no corner to round.
2. Make a rounded copy of a mesh as a NEW asset. The Datasmith mesh is only read. The copy
   goes under /Game/Wieland1529/Interiors/Meshes and is put on the object as a recorded swap.

The rounding is done here, in plain Python, because the engine's own bevel tool needs clean
closed meshes and the Revit export is not clean: faces are separate sheets that only touch,
with T-shaped joints. The method: close the T-shaped joints, pull the border of every flat
(or smoothly curved) face back from each sharp edge by ROUND_CM, bridge the gap with a
narrow strip, and close each corner with a small polygon. Shading normals are then averaged
by face area, so the strip reads as a rounded edge.

Nothing here edits or saves an asset that Datasmith created.
"""

import bisect
import math
import time

import unreal

SHARP_ANGLE = 60.0   # degrees of turn between two faces at which an edge counts as sharp
GROUP_ANGLE = 50.0   # faces turning less than this belong to one smooth face; more is an edge to round
SHEET_ANGLE = 170.0  # two faces back to back are the rim of a sheet without thickness, not an edge
ROUND_CM = 0.2       # each face is pulled back 2 mm from a sharp edge (less where the part is small)
# A first pass rounds the edges; further, finer passes take care of what the first one had to
# leave: very acute edges (which need two cuts) and small parts.
PASSES_CM = (ROUND_CM, 0.05, 0.02, 0.01, 0.005, 0.005)
MESH_FOLDER = "/Game/Wieland1529/Interiors/Meshes"
WELD_CM = 0.005
# Before rounding, steps and slivers smaller than this are closed up. Two sizes are tried and the
# better result kept: 0.15 mm suits finely modelled fixtures, 0.6 mm closes the 0.4 mm steps
# that the Revit casework and doors carry (a step that small cannot be rounded by 2 mm).
MERGE_TRIALS_CM = (0.015, 0.06)

_ARRAY_CACHE = {}


# ----------------------------------------------------------------------------- vector helpers

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _length(a):
    return math.sqrt(_dot(a, a))


def _unit(a):
    length = math.sqrt(_dot(a, a))
    if length < 1e-12:
        return None
    return (a[0] / length, a[1] / length, a[2] / length)


def _normal(a, b, c):
    """Outward normal of a triangle. Unreal's front faces wind clockwise."""
    return _unit(_cross(_sub(c, a), _sub(b, a)))


def _segment_distance(p, a, b):
    ab = _sub(b, a)
    denom = _dot(ab, ab)
    t = 0.0 if denom < 1e-12 else max(0.0, min(1.0, _dot(_sub(p, a), ab) / denom))
    return _length(_sub(p, _add(a, _mul(ab, t))))


# ----------------------------------------------------------------------------- reading meshes

def _dynamic(static_mesh):
    """Read a static mesh into a temporary editable mesh. The asset is not changed."""
    dynamic = unreal.DynamicMesh()
    options = unreal.GeometryScriptCopyMeshFromAssetOptions()
    options.set_editor_property("apply_build_settings", False)
    options.set_editor_property("request_tangents", False)
    lod = unreal.GeometryScriptMeshReadLOD()
    result = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh_v2(
        static_mesh, dynamic, options, lod, True)
    outcome = result[1] if isinstance(result, tuple) else result
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        raise RuntimeError("could not read mesh %s" % static_mesh.get_path_name())
    return dynamic


def _arrays(dynamic):
    """Vertex positions and triangles of an editable mesh as plain Python lists."""
    _, position_list, _ = unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dynamic, False)
    positions = [(v.x, v.y, v.z) for v in unreal.GeometryScript_List.convert_vector_list_to_array(position_list)]
    _, triangle_list, _ = unreal.GeometryScript_MeshQueries.get_all_triangle_indices(dynamic, True)
    triangles = [(t.x, t.y, t.z) for t in unreal.GeometryScript_List.convert_triangle_list_to_array(triangle_list)]
    return positions, triangles


def _full_arrays(dynamic):
    """Positions, triangles, three texture coordinates per triangle, one material number per triangle."""
    positions, triangles = _arrays(dynamic)
    result = unreal.GeometryScript_UVs.get_mesh_per_vertex_u_vs(dynamic, 0)
    uv_lists = [item for item in result if isinstance(item, unreal.GeometryScriptUVList)]
    flags = [item for item in result if isinstance(item, bool)]
    has_split = bool(flags[-1]) if len(flags) >= 2 else False
    uvs = []
    if uv_lists:
        uvs = [(v.x, v.y) for v in unreal.GeometryScript_List.convert_uv_list_to_array(uv_lists[0])]
    if len(uvs) < len(positions):
        uvs = uvs + [(0.0, 0.0)] * (len(positions) - len(uvs))
    triangle_uvs = [(uvs[i], uvs[j], uvs[k]) for i, j, k in triangles]
    if has_split:
        # A vertex on a texture seam has more than one coordinate: read those triangles one by one.
        for number in range(len(triangles)):
            got = unreal.GeometryScript_MeshQueries.get_triangle_u_vs(dynamic, 0, number)
            found = [item for item in got if isinstance(item, unreal.Vector2D)]
            if len(found) == 3:
                triangle_uvs[number] = tuple((v.x, v.y) for v in found)
    result = unreal.GeometryScript_Materials.get_all_triangle_material_i_ds(dynamic)
    index_list = [item for item in result if isinstance(item, unreal.GeometryScriptIndexList)][0]
    materials = [m for m in unreal.GeometryScript_List.convert_index_list_to_array(index_list) if m >= 0]
    if len(materials) != len(triangles):
        materials = [0] * len(triangles)
    return positions, triangles, triangle_uvs, materials


def mesh_arrays(static_mesh):
    key = static_mesh.get_path_name()
    if key not in _ARRAY_CACHE:
        _ARRAY_CACHE[key] = _arrays(_dynamic(static_mesh))
    return _ARRAY_CACHE[key]


def forget(static_mesh=None):
    if static_mesh is None:
        _ARRAY_CACHE.clear()
    else:
        _ARRAY_CACHE.pop(static_mesh.get_path_name(), None)


# ----------------------------------------------------------------------------- counting sharp edges

def sharp_edges(positions, triangles, flipped=False, angle=SHARP_ANGLE, near=None, radius=200.0):
    """Sharp convex edges of one mesh. positions are already in the space of `near`.

    A mirrored object (negative scale) reverses the winding, which `flipped` corrects.
    Returns a list of (point a, point b, turn in degrees).
    """
    weld = {}
    index = []
    for p in positions:
        key = (round(p[0] / WELD_CM), round(p[1] / WELD_CM), round(p[2] / WELD_CM))
        index.append(weld.setdefault(key, len(weld)))
    normals = []
    edges = {}
    for number, (i, j, k) in enumerate(triangles):
        a, b, c = positions[i], positions[j], positions[k]
        normal = _normal(a, b, c)
        if normal is not None and flipped:
            normal = (-normal[0], -normal[1], -normal[2])
        normals.append(normal)
        if normal is None:
            continue
        corners = (index[i], index[j], index[k])
        if corners[0] == corners[1] or corners[1] == corners[2] or corners[0] == corners[2]:
            continue
        for first, second, other in ((i, j, k), (j, k, i), (k, i, j)):
            edge = (index[first], index[second])
            if edge[0] > edge[1]:
                edge = (edge[1], edge[0])
            edges.setdefault(edge, []).append((number, first, second, other))
    limit = math.cos(math.radians(angle))
    sheet = math.cos(math.radians(SHEET_ANGLE))
    found = []
    for uses in edges.values():
        if len(uses) != 2:
            continue
        (t1, a_index, b_index, _), (t2, _, _, other2) = uses
        n1, n2 = normals[t1], normals[t2]
        cosine = max(-1.0, min(1.0, _dot(n1, n2)))
        if cosine > limit + 1e-9 or cosine < sheet:
            continue
        a, b = positions[a_index], positions[b_index]
        if _dot(_sub(positions[other2], a), n1) >= -1e-6:
            continue  # the second face rises above the first: an inside corner, not an edge
        if near is not None and _segment_distance(near, a, b) > radius:
            continue
        found.append((a, b, math.degrees(math.acos(cosine))))
    return found


def _world_positions(component, positions):
    transform = component.get_world_transform()
    out = []
    for p in positions:
        w = transform.transform_location(unreal.Vector(p[0], p[1], p[2]))
        out.append((w.x, w.y, w.z))
    scale = component.get_world_scale()
    return out, (scale.x * scale.y * scale.z) < 0.0


def _box_distance(point, origin, extent):
    dx = max(abs(point[0] - origin.x) - extent.x, 0.0)
    dy = max(abs(point[1] - origin.y) - extent.y, 0.0)
    dz = max(abs(point[2] - origin.z) - extent.z, 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def components_near(camera, radius=200.0):
    """(actor, component) pairs whose bounding box comes within radius of the camera."""
    out = []
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for actor in actors:
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            if component.static_mesh is None or not component.is_visible():
                continue
            origin, extent, _ = unreal.SystemLibrary.get_component_bounds(component)
            if _box_distance(camera, origin, extent) <= radius:
                out.append((actor, component))
    return out


def count_near(camera, radius=200.0, angle=SHARP_ANGLE):
    """Count sharp edges within radius of camera, per object. Returns (total, total cm, rows)."""
    rows = []
    total = 0
    total_cm = 0.0
    for actor, component in components_near(camera, radius):
        positions, triangles = mesh_arrays(component.static_mesh)
        world, flipped = _world_positions(component, positions)
        found = sharp_edges(world, triangles, flipped, angle, camera, radius)
        if found:
            length = sum(_length(_sub(b, a)) for a, b, _ in found)
            rows.append((actor.get_actor_label(), component.static_mesh.get_path_name(), len(found), round(length, 1)))
            total += len(found)
            total_cm += length
    rows.sort(key=lambda row: -row[2])
    return total, round(total_cm, 1), rows


_COUNTS = {}


def count_begin(name, camera, radius=200.0, angle=SHARP_ANGLE):
    """Start a count that is carried out in short steps (the editor must not be held long)."""
    todo = components_near(camera, radius)
    _COUNTS[name] = {"camera": camera, "radius": radius, "angle": angle, "todo": todo, "rows": []}
    return len(todo)


def count_step(name, seconds=12.0):
    """Work on a started count for about `seconds`. Returns the number of objects still to do."""
    import time
    state = _COUNTS[name]
    start = time.time()
    while state["todo"] and time.time() - start < seconds:
        actor, component = state["todo"].pop()
        positions, triangles = mesh_arrays(component.static_mesh)
        world, flipped = _world_positions(component, positions)
        found = sharp_edges(world, triangles, flipped, state["angle"], state["camera"], state["radius"])
        if found:
            length = sum(_length(_sub(b, a)) for a, b, _ in found)
            state["rows"].append((actor.get_actor_label(), component.static_mesh.get_path_name(), len(found),
                                  round(length, 1)))
    return len(state["todo"])


def count_result(name):
    """(total, total cm, rows) of a finished count, rows sorted by count."""
    rows = sorted(_COUNTS[name]["rows"], key=lambda row: -row[2])
    return sum(row[2] for row in rows), round(sum(row[3] for row in rows), 1), rows


# ----------------------------------------------------------------------------- rounding

def _weld(positions):
    """Merge vertices that sit at the same place. Returns (index per vertex, merged positions)."""
    cells = {}
    index = []
    merged = []
    for p in positions:
        key = (round(p[0] / WELD_CM), round(p[1] / WELD_CM), round(p[2] / WELD_CM))
        number = cells.get(key)
        if number is None:
            number = len(merged)
            cells[key] = number
            merged.append(p)
        index.append(number)
    return index, merged


def _merge(positions, tolerance):
    """Like _weld, but merges every vertex that lies within tolerance of an earlier one."""
    cells = {}
    index = []
    merged = []
    limit = tolerance * tolerance
    for p in positions:
        cx, cy, cz = int(math.floor(p[0] / tolerance)), int(math.floor(p[1] / tolerance)), int(math.floor(p[2] / tolerance))
        number = None
        for dx in (0, -1, 1):
            for dy in (0, -1, 1):
                for dz in (0, -1, 1):
                    for candidate in cells.get((cx + dx, cy + dy, cz + dz), ()):
                        q = merged[candidate]
                        if (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 + (q[2] - p[2]) ** 2 <= limit:
                            number = candidate
                            break
                    if number is not None:
                        break
                if number is not None:
                    break
            if number is not None:
                break
        if number is None:
            number = len(merged)
            merged.append(p)
            cells.setdefault((cx, cy, cz), []).append(number)
        index.append(number)
    return index, merged


def _close_t_joints(points, corners_list, uv_list, material_list):
    """Where a vertex of one face lies part-way along an open edge of another, split that edge.

    points: merged positions. corners_list: per triangle three merged indices. uv_list: per
    triangle three texture coordinates. Returns new (corners_list, uv_list, material_list).
    """
    use = {}
    for a, b, c in corners_list:
        for first, second in ((a, b), (b, c), (c, a)):
            key = (first, second) if first < second else (second, first)
            use[key] = use.get(key, 0) + 1
    lines = {}
    for (a, b), count in use.items():
        if count != 1:
            continue
        direction = _unit(_sub(points[b], points[a]))
        if direction is None:
            continue
        for axis in range(3):
            if abs(direction[axis]) > 1e-6:
                if direction[axis] < 0.0:
                    direction = (-direction[0], -direction[1], -direction[2])
                break
        foot = _sub(points[a], _mul(direction, _dot(points[a], direction)))
        key = (round(direction[0], 3), round(direction[1], 3), round(direction[2], 3),
               round(foot[0] / 0.02), round(foot[1] / 0.02), round(foot[2] / 0.02))
        entry = lines.setdefault(key, (direction, {}))
        entry[1][a] = _dot(points[a], direction)
        entry[1][b] = _dot(points[b], direction)
    edge_points = {}
    for direction, members in lines.values():
        if len(members) < 3:
            continue
        ordered = sorted((t, v) for v, t in members.items())
        values = [t for t, _ in ordered]
        for (a, b), count in use.items():
            if count != 1 or a not in members or b not in members:
                continue
            low, high = sorted((members[a], members[b]))
            start = bisect.bisect_right(values, low + 2.0 * WELD_CM)
            end = bisect.bisect_left(values, high - 2.0 * WELD_CM)
            if end > start:
                edge_points[(a, b)] = [v for _, v in ordered[start:end] if v != a and v != b]
    if not edge_points:
        return corners_list, uv_list, material_list
    out_corners, out_uvs, out_materials = [], [], []
    for corners, uvs, material in zip(corners_list, uv_list, material_list):
        stack = [(corners, uvs)]
        guard = 0
        while stack:
            (a, b, c), (ua, ub, uc) = stack.pop()
            guard += 1
            split = None
            if guard < 400:
                for (first, second, third), (uf, us, ut) in (((a, b, c), (ua, ub, uc)), ((b, c, a), (ub, uc, ua)),
                                                               ((c, a, b), (uc, ua, ub))):
                    key = (first, second) if first < second else (second, first)
                    inner = edge_points.get(key)
                    if not inner:
                        continue
                    for middle in inner:
                        whole = _sub(points[second], points[first])
                        t = _dot(_sub(points[middle], points[first]), whole) / max(_dot(whole, whole), 1e-12)
                        if 1e-4 < t < 1.0 - 1e-4 and _segment_distance(points[middle], points[first], points[second]) < 0.02:
                            um = (uf[0] + (us[0] - uf[0]) * t, uf[1] + (us[1] - uf[1]) * t)
                            split = (((first, middle, third), (uf, um, ut)), ((middle, second, third), (um, us, ut)))
                            break
                    if split:
                        break
            if split:
                stack.append(split[0])
                stack.append(split[1])
            else:
                out_corners.append((a, b, c))
                out_uvs.append((ua, ub, uc))
                out_materials.append(material)
    return out_corners, out_uvs, out_materials


def round_pass(positions, triangles, triangle_uvs, materials, distance, merge=0.0):
    """One rounding pass over a triangle list.

    positions: per vertex; triangles: three vertex indices each; triangle_uvs: three texture
    coordinates per triangle; materials: one number per triangle. Returns (positions,
    triangles, triangle_uvs, materials, report) in the same form, with every triangle owning
    its three vertices.

    Only outward corners that turn GROUP_ANGLE or more are rounded. Around each vertex the
    faces are sorted into fans that end at such an edge or at an open border; every fan gets
    its own copy of the vertex, pulled back so that it sits `distance` from each rounded edge.
    A fan that ends at an open border or at an inside corner slides along that border or
    inside corner, so the outline stays where it was. All copies of one vertex are pulled by
    the same share, which keeps each strip at an even slope to both its faces.
    """
    index, points = _merge(positions, merge) if merge > 0.0 else _weld(positions)
    corners_list, uv_list, material_list = [], [], []
    for (i, j, k), uvs, material in zip(triangles, triangle_uvs, materials):
        a, b, c = index[i], index[j], index[k]
        if a == b or b == c or a == c:
            continue
        if _normal(points[a], points[b], points[c]) is None:
            continue
        corners_list.append((a, b, c))
        uv_list.append(uvs)
        material_list.append(material)
    corners_list, uv_list, material_list = _close_t_joints(points, corners_list, uv_list, material_list)
    count = len(corners_list)
    normals = [_normal(points[a], points[b], points[c]) for a, b, c in corners_list]

    # Edges: key (low, high) -> list of (triangle, from, to) in the triangle's own winding.
    edges = {}
    for t, (a, b, c) in enumerate(corners_list):
        if normals[t] is None:
            continue
        for first, second in ((a, b), (b, c), (c, a)):
            key = (first, second) if first < second else (second, first)
            edges.setdefault(key, []).append((t, first, second))

    def node(t, v):
        return 3 * t + corners_list[t].index(v)

    parent = list(range(3 * count))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    limit = math.cos(math.radians(GROUP_ANGLE))
    sheet = math.cos(math.radians(SHEET_ANGLE))
    round_edges = []
    border_edges = []  # open borders and inside corners: a fan ends there without being rounded
    for key, uses in edges.items():
        if len(uses) != 2 or uses[0][1] == uses[1][1]:
            border_edges.append((key, uses))
            continue
        (t1, first, _), (t2, _, _) = uses
        cosine = _dot(normals[t1], normals[t2])
        if cosine <= limit:
            a2, b2, c2 = corners_list[t2]
            other = a2 + b2 + c2 - key[0] - key[1]
            if cosine >= sheet and _dot(_sub(points[other], points[first]), normals[t1]) < -1e-6:
                round_edges.append((key, uses))
            else:
                border_edges.append((key, uses))
            continue
        for v in key:
            parent[find(node(t1, v))] = find(node(t2, v))

    # Per fan: its rounded ends and its border ends.
    fans = {}

    def fan(t, v):
        return fans.setdefault(find(node(t, v)), {"v": v, "R": [], "B": []})

    for key, uses in round_edges:
        for t, _, _ in uses:
            fan(t, key[0])["R"].append((key[1], t))
            fan(t, key[1])["R"].append((key[0], t))
    wanted = set(fans)
    for key, uses in border_edges:
        for t, _, _ in uses:
            for v, u in ((key[0], key[1]), (key[1], key[0])):
                cid = find(node(t, v))
                if cid in wanted:
                    fans[cid]["B"].append(u)

    share = {}
    reasons = {}

    def freeze(v, why):
        if share.get(v, 1.0) > 0.0:
            reasons[why] = reasons.get(why, 0) + 1
        share[v] = 0.0

    def inward(v, u, t):
        along = _unit(_sub(points[u], points[v]))
        a, b, c = corners_list[t]
        third = a + b + c - u - v
        side = _cross(normals[t], along)
        if _dot(side, _sub(points[third], points[v])) < 0.0:
            side = (-side[0], -side[1], -side[2])
        return side

    def slide(v, toward, sides):
        direction = _unit(_sub(points[toward], points[v]))
        if direction is None:
            return None
        rate = _dot(direction, sides[0])
        if rate < 0.15:
            return _mul(sides[0], distance)  # the border carries straight on: pull square to the edge
        return _mul(direction, distance / rate)

    moves = {}
    for cid, info in fans.items():
        v = info["v"]
        rounded_ends, border_ends = info["R"], info["B"]
        if len(rounded_ends) + len(border_ends) != 2:
            freeze(v, "faces do not form a simple fan")
            continue
        sides = [inward(v, u, t) for u, t in rounded_ends]
        move = None
        if border_ends:
            move = slide(v, border_ends[0], sides)
            if move is None:
                freeze(v, "border of no length")
                continue
        else:
            (m1, m2) = sides
            together = _dot(m1, m2)
            if together < -0.999:
                freeze(v, "knife point")
                continue
            # The shortest pull that ends `distance` from both edges.
            move = _mul(_add(m1, m2), distance / (1.0 + together))
        size = _length(move)
        if size > 4.0 * distance:
            share[v] = min(share.get(v, 1.0), 4.0 * distance / size)
        else:
            share.setdefault(v, 1.0)
        moves[cid] = move

    def place(t, v):
        move = moves.get(find(node(t, v)))
        if move is None:
            return points[v]
        amount = share.get(v, 0.0)
        if amount <= 0.0:
            return points[v]
        return _add(points[v], _mul(move, amount))

    # Reduce the pull wherever it would fold a triangle over (parts smaller than the rounding).
    reduced = set()
    for _ in range(6):
        changed = False
        for t, (a, b, c) in enumerate(corners_list):
            if share.get(a, 0.0) <= 0.0 and share.get(b, 0.0) <= 0.0 and share.get(c, 0.0) <= 0.0:
                continue
            new_normal = _normal(place(t, a), place(t, b), place(t, c))
            if new_normal is None or _dot(new_normal, normals[t]) < 0.7:
                for v in (a, b, c):
                    amount = share.get(v, 0.0)
                    if amount > 0.0:
                        share[v] = amount * 0.5 if amount > 0.07 else 0.0
                        reduced.add(v)
                        changed = True
        if not changed:
            break

    out_positions, out_triangles, out_uvs, out_materials = [], [], [], []

    def emit(p0, p1, p2, u0, u1, u2, material):
        if _normal(p0, p1, p2) is None:
            return
        base = len(out_positions)
        out_positions.extend((p0, p1, p2))
        out_uvs.append((u0, u1, u2))
        out_triangles.append((base, base + 1, base + 2))
        out_materials.append(material)

    fan_uv = {}
    fan_material = {}
    for t, (a, b, c) in enumerate(corners_list):
        ua, ub, uc = uv_list[t]
        for v, uv in ((a, ua), (b, ub), (c, uc)):
            cid = find(node(t, v))
            if cid in wanted and cid not in fan_uv:
                fan_uv[cid] = uv
                fan_material[cid] = material_list[t]
        emit(place(t, a), place(t, b), place(t, c), ua, ub, uc, material_list[t])

    # Strips along the rounded edges, and the order of fans around each corner.
    after = {}
    rounded = 0
    for key, uses in round_edges:
        (t1, a, b), (t2, _, _) = uses
        a1, b1, a2, b2 = place(t1, a), place(t1, b), place(t2, a), place(t2, b)
        fa1, fb1, fa2, fb2 = find(node(t1, a)), find(node(t1, b)), find(node(t2, a)), find(node(t2, b))
        before = len(out_triangles)
        emit(b1, a1, a2, fan_uv[fb1], fan_uv[fa1], fan_uv[fa2], material_list[t1])
        emit(b1, a2, b2, fan_uv[fb1], fan_uv[fa2], fan_uv[fb2], material_list[t1])
        if len(out_triangles) > before:
            rounded += 1
        after.setdefault(a, {})[fa2] = fa1
        after.setdefault(b, {})[fb1] = fb2

    # Corner polygons where three or more rounded edges meet.
    for v, following in after.items():
        if len(following) < 3 or share.get(v, 0.0) <= 0.0:
            continue
        start = next(iter(following))
        ring = [start]
        current = following.get(start)
        while current is not None and current != start and len(ring) <= len(following):
            ring.append(current)
            current = following.get(current)
        if current != start or len(ring) != len(following):
            continue
        amount = share[v]
        spots = [_add(points[v], _mul(moves[cid], amount)) if cid in moves else points[v] for cid in ring]
        material = fan_material[ring[0]]
        if len(ring) == 3:
            emit(spots[0], spots[1], spots[2], fan_uv[ring[0]], fan_uv[ring[1]], fan_uv[ring[2]], material)
        else:
            middle = _mul((sum(q[0] for q in spots), sum(q[1] for q in spots), sum(q[2] for q in spots)),
                          1.0 / len(spots))
            for n in range(len(ring)):
                following_n = (n + 1) % len(ring)
                emit(middle, spots[n], spots[following_n], fan_uv[ring[n]], fan_uv[ring[n]],
                     fan_uv[ring[following_n]], material)

    report = {"edges_rounded": rounded, "corners_left": sum(1 for value in share.values() if value <= 0.0),
              "reasons": reasons, "reduced": len(reduced)}
    return out_positions, out_triangles, out_uvs, out_materials, report


def rounded_arrays(static_mesh):
    """Rounded geometry of a mesh as plain lists, with the counts before and after."""
    dynamic = _dynamic(static_mesh)
    positions, triangles, triangle_uvs, materials = _full_arrays(dynamic)
    before = len(sharp_edges(positions, triangles))
    low = [min(p[k] for p in positions) for k in range(3)]
    high = [max(p[k] for p in positions) for k in range(3)]
    centre = tuple((low[k] + high[k]) / 2.0 for k in range(3))
    local = [_sub(p, centre) for p in positions]
    slack = 0.01
    chosen = None
    for merge in MERGE_TRIALS_CM:
        state = (local, triangles, triangle_uvs, materials)
        best = None
        left = before
        passes = 0
        report = {"edges_rounded": 0, "corners_left": 0, "reduced": 0}
        for number, distance in enumerate(PASSES_CM):
            result = round_pass(state[0], state[1], state[2], state[3], distance, merge if number == 0 else 0.0)
            state = result[:4]
            if number == 0:
                report = result[4]
            now = len(sharp_edges(state[0], state[1]))
            # A pass that pushes a vertex outside the original outline is not kept.
            outside = any(abs(p[k]) > (high[k] - low[k]) / 2.0 + slack for p in state[0] for k in range(3))
            if best is None or (now < left and not outside):
                best = state
                left = now
                passes = number + 1
            if now == 0 or outside:
                break
        out_positions = [_add(p, centre) for p in best[0]]
        stray = sum(1 for p in out_positions
                    if any(p[k] < low[k] - slack or p[k] > high[k] + slack for k in range(3)))
        lost = len(best[1]) < len(triangles)
        rank = (1 if (stray or lost) else 0, left)
        if chosen is None or rank < chosen[0]:
            info = {"before": before, "after": left, "triangles_before": len(triangles),
                    "triangles_after": len(best[1]), "passes": passes, "stray_vertices": stray,
                    "edges_rounded": report["edges_rounded"], "corners_left": report["corners_left"],
                    "reduced": report["reduced"], "merge_cm": merge}
            chosen = (rank, out_positions, best[1], best[2], best[3], info)
        if rank == (0, 0):
            break
    return chosen[1], chosen[2], chosen[3], chosen[4], chosen[5]


def _dynamic_from_arrays(positions, triangles, triangle_uvs, materials):
    """Build an editable mesh from plain lists in which every triangle owns its three vertices."""
    uvs = [uv for triple in triangle_uvs for uv in triple]
    buffers = unreal.GeometryScriptSimpleMeshBuffers()
    buffers.set_editor_property("vertices", [unreal.Vector(p[0], p[1], p[2]) for p in positions])
    buffers.set_editor_property("uv0", [unreal.Vector2D(u[0], u[1]) for u in uvs])
    buffers.set_editor_property("triangles", [unreal.IntVector(t[0], t[1], t[2]) for t in triangles])
    dynamic = unreal.DynamicMesh()
    unreal.GeometryScript_MeshEdits.append_buffers_to_mesh(dynamic, buffers, 0)
    unreal.GeometryScript_Materials.enable_material_i_ds(dynamic)
    index_list = unreal.GeometryScript_List.convert_array_to_index_list(list(materials))
    unreal.GeometryScript_Materials.set_all_triangle_material_i_ds(dynamic, index_list)
    weld = unreal.GeometryScriptWeldEdgesOptions()
    weld.set_editor_property("tolerance", WELD_CM)
    weld.set_editor_property("only_unique_pairs", False)
    unreal.GeometryScript_MeshRepair.weld_mesh_edges(dynamic, weld)
    split = unreal.GeometryScriptSplitNormalsOptions()
    split.set_editor_property("split_by_opening_angle", True)
    split.set_editor_property("opening_angle_deg", GROUP_ANGLE)
    split.set_editor_property("split_by_face_group", False)
    calculate = unreal.GeometryScriptCalculateNormalsOptions()
    calculate.set_editor_property("angle_weighted", False)
    calculate.set_editor_property("area_weighted", True)
    unreal.GeometryScript_Normals.compute_split_normals(dynamic, split, calculate)
    return dynamic


def rounded_name(static_mesh):
    return "SM_W1529_R_" + static_mesh.get_name()


def rounded_copy(static_mesh, folder=MESH_FOLDER, save=True, only_good=False):
    """Create (or return, if it exists) the rounded copy of a mesh as a new saved asset.

    Returns a dict: path, existed, sharp edges before and after, triangles before and after.
    With only_good, a copy that fails good_copy() is not written and the path is None.
    """
    path = "%s/%s" % (folder, rounded_name(static_mesh))
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        before_positions, before_triangles = mesh_arrays(static_mesh)
        existing = unreal.EditorAssetLibrary.load_asset(path)
        positions, triangles = mesh_arrays(existing)
        return {"path": path, "existed": True, "before": len(sharp_edges(before_positions, before_triangles)),
                "after": len(sharp_edges(positions, triangles)), "triangles_before": len(before_triangles),
                "triangles_after": len(triangles)}
    positions, triangles, triangle_uvs, materials, info = rounded_arrays(static_mesh)
    if only_good and not good_copy(info):
        info["path"] = None
        info["existed"] = False
        return info
    dynamic = _dynamic_from_arrays(positions, triangles, triangle_uvs, materials)
    options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    options.set_editor_property("enable_recompute_normals", False)
    options.set_editor_property("enable_recompute_tangents", True)
    options.set_editor_property("enable_collision", False)
    source_nanite = static_mesh.get_editor_property("nanite_settings")
    options.set_editor_property("enable_nanite", bool(source_nanite.enabled))
    options.set_editor_property("nanite_settings", source_nanite)
    result = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic, path, options)
    new_mesh, outcome = result if isinstance(result, tuple) else (result, unreal.GeometryScriptOutcomePins.SUCCESS)
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS or new_mesh is None:
        raise RuntimeError("could not create %s" % path)
    new_mesh.set_editor_property("static_materials", static_mesh.get_editor_property("static_materials"))
    if save:
        unreal.EditorAssetLibrary.save_asset(path, False)
    info["path"] = path
    info["existed"] = False
    return info


# ----------------------------------------------------------------------------- swaps

def good_copy(info):
    """A rounded copy is used only if it has fewer sharp edges, lost no faces and has no stray vertex."""
    return (info["after"] < info["before"] and info["triangles_after"] >= info["triangles_before"]
            and not info.get("stray_vertices"))


def swap_meshes(mapping, actors=None):
    """Put new meshes on the objects that use the source meshes. mapping: source path -> new path.

    Only the object's reference changes (an override in the level); the Datasmith mesh asset is
    untouched. Returns rows (actor label, component name, source path, new path).
    """
    if actors is None:
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    loaded = {}
    rows = []
    for actor in actors:
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.static_mesh
            if mesh is None:
                continue
            source = mesh.get_path_name()
            target = mapping.get(source)
            if target is None:
                continue
            if target not in loaded:
                loaded[target] = unreal.EditorAssetLibrary.load_asset(target)
            component.set_static_mesh(loaded[target])
            rows.append((actor.get_actor_label(), component.get_name(), source, loaded[target].get_path_name()))
    return rows


def swaps_from_csv(csv_path, actors=None, folder="/Game/Wieland1529/Building/Datasmith"):
    """Apply again the swaps recorded in mesh_swaps.csv (after a restart, or in a derived level).

    A row's imported mesh is found by name among the meshes the objects use now, under `folder`.
    Returns (rows applied, recorded names that no object uses).
    """
    import csv
    wanted = {}
    with open(csv_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            wanted[row["imported_mesh_name"]] = row["replacement_mesh_path"]
    if actors is None:
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    mapping = {}
    for actor in actors:
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.static_mesh
            if mesh is None:
                continue
            path = mesh.get_path_name()
            if path.startswith(folder) and mesh.get_name() in wanted:
                mapping[path] = wanted[mesh.get_name()]
    rows = swap_meshes(mapping, actors)
    used = set(path.split(".")[-1] for path in mapping)
    return rows, sorted(name for name in wanted if name not in used)


# ----------------------------------------------------------------------------- batch

_BATCH = {}


def batch_begin(paths, max_triangles=60000, seconds_per_tick=0.5):
    """Round a list of meshes in the background, a little on every editor tick.

    paths: mesh asset paths. Results collect in _BATCH: done (source path -> info dict),
    skipped (source path -> reason), errors (source path -> message). Returns the number queued.
    """
    batch_end()
    _BATCH.clear()
    _BATCH.update({"todo": list(paths), "done": {}, "skipped": {}, "errors": {}, "current": None,
                   "max_triangles": max_triangles, "seconds": seconds_per_tick, "started": time.time(),
                   "finished": None})
    _BATCH["handle"] = unreal.register_slate_post_tick_callback(_batch_tick)
    return len(_BATCH["todo"])


def _batch_tick(delta_seconds):
    end = time.time() + _BATCH["seconds"]
    while _BATCH["todo"] and time.time() < end:
        path = _BATCH["todo"].pop()
        _BATCH["current"] = path
        try:
            mesh = unreal.EditorAssetLibrary.load_asset(path)
            if mesh is None:
                _BATCH["skipped"][path] = "not found"
                continue
            count = mesh.get_num_triangles(0)
            if count > _BATCH["max_triangles"]:
                _BATCH["skipped"][path] = "over %d triangles (%d)" % (_BATCH["max_triangles"], count)
                continue
            positions, triangles = mesh_arrays(mesh)
            before = len(sharp_edges(positions, triangles))
            forget(mesh)
            if before == 0:
                _BATCH["skipped"][path] = "no sharp edge"
                continue
            info = rounded_copy(mesh, only_good=True)
            forget()
            _BATCH["done"][path] = info
        except Exception as error:  # one bad mesh must not stop the batch
            _BATCH["errors"][path] = "%s: %s" % (type(error).__name__, error)
    if not _BATCH["todo"]:
        _BATCH["current"] = None
        _BATCH["finished"] = time.time()
        batch_end()


def batch_end():
    handle = _BATCH.pop("handle", None)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)


def batch_status():
    """(left, done, skipped, errors, current path, seconds running)."""
    stop = _BATCH.get("finished") or time.time()
    return (len(_BATCH.get("todo", ())), len(_BATCH.get("done", ())), len(_BATCH.get("skipped", ())),
            len(_BATCH.get("errors", ())), _BATCH.get("current"), round(stop - _BATCH.get("started", stop), 1))
