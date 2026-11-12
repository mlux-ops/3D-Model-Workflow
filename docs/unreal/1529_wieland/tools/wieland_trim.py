"""Phase 6, step 6.2: baseboards for the 1529 N. Wieland interiors. Runs inside the Unreal editor.

The Revit model has no baseboards. This tool makes them as new mesh assets and places them as new
objects in the unit levels; no imported object or asset is edited.

Rule. Every wall is cut a little above each finished floor. The cut gives the outline of the wall,
broken at door openings. A baseboard runs along each piece of outline that
  - belongs to a wall face finished in gypsum board or paint (not masonry, stone, siding, tile),
  - stands over a floor slab of that storey,
  - is not covered by casework, an appliance, a plumbing fixture, a stair, a door or a window,
  - does not disappear into another wall, and
  - is at least MIN_RUN long.
Each half of the building is made from its own walls; nothing is mirrored.

Order of use, with L_Site_M4 open:
    runs, info = plan_runs()                      # read-only
    write_runs(runs, csv_path)                    # the list for the owner
    build(runs, "NorthTriplex", "Floor1")         # one mesh asset and one object; see build_all()
Frame of the level: origin at the lot's south-west corner, north is -X, east is -Y, centimetres.
"""

import csv
import math

import unreal

import wieland_levels
import wieland_refine

FLOORS = (("Lower", -152.4), ("Floor1", 203.2), ("Floor2", 528.3), ("Floor3", 853.4), ("Floor4", 1178.6))
PENTHOUSE_FLOORS = ("Floor3", "Floor4")
CUT = 5.0          # height of the cut above the finished floor
THICK = 1.2        # baseboard thickness
HEIGHT = 10.0      # baseboard height
EASE = 0.2         # every edge of a baseboard is eased by this much
SINK = 0.2         # the board is set this far into the wall and the floor, so the eased back edges do not show
MIN_RUN = 10.0
STEP = 2.5
FLOOR_REACH = 8.0  # a floor slab counts for a storey when its top is this near the storey's level
# Wall faces that take a baseboard, by the name of the Revit material on the face.
BOARD_FACES = ("09_23_00_Gypsum_Wall_Board", "Gypsum_Wall_Board", "BM_White_Dove_-_Eggshell",
               "TF27_Warm_White_Painted_Drywall")
WALLS = ("Walls",)
FLOOR_CATEGORIES = ("Floors",)
# Objects that stand against a wall down to the floor, so that no baseboard runs behind them.
BLOCKERS = ("Casework", "Doors", "Windows", "Plumbing Fixtures", "Specialty Equipment", "Generic Models", "Stairs",
            "Runs", "Landings", "Supports", "Railings", "Structural Columns", "Curtain Panels",
            "Curtain Wall Mullions", "Mechanical Equipment")
LOOSE_BLOCKERS = ("Generic Models", "Railings", "Supports")
LOOSE_LIMIT = 300.0  # a loose blocker counts only when its box is at most this long in plan
# A door is tested by its true outline, not by its box: the box of a pocket door covers the whole pocket,
# where the wall face is free and takes a board.
OUTLINE_BLOCKERS = ("Doors",)
OUTLINE_HEIGHTS = (3.0, 8.0)  # the outline is cut at these heights above the finished floor
OUTLINE_REACH = 1.5           # a board is covered where a door part comes this near its middle line
MESH_FOLDER = "/Game/Wieland1529/Interiors/Generated"
BOARD_MATERIAL = ("/Game/Wieland1529/Building/Datasmith/25-006_1527_N_Wieland-3DView-3D_View_188/Materials/"
                  "BM_White_Dove_-_Semi_Gloss")
TAG_GENERATED = "W1529.Generated"
LABEL = "GEN_Baseboard_"
RUN_HEAD = ["object", "unit", "floor", "run", "x1", "y1", "x2", "y2", "floor_top_z", "length_cm", "faces_x", "faces_y",
            "wall", "wall_type", "face_material", "rule"]
RULE = "baseboard %d x %d mm by rule (step 6.2); not in the Revit model; for the owner to confirm" % (
    round(THICK * 10), round(HEIGHT * 10))


def _component_box(component):
    origin, extent, _ = unreal.SystemLibrary.get_component_bounds(component)
    return (origin.x - extent.x, origin.y - extent.y, origin.z - extent.z,
            origin.x + extent.x, origin.y + extent.y, origin.z + extent.z)


def _building_components():
    """(actor, component, category) of every mesh of the interior levels."""
    found = []
    for actor in wieland_levels._actors():
        if not wieland_levels._level_name(actor).startswith("L_W1529_"):
            continue
        if TAG_GENERATED in [str(tag) for tag in actor.tags]:
            continue
        category = wieland_levels._category(actor)
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            if component.static_mesh is not None:
                found.append((actor, component, category))
    return found


def _material_ids(static_mesh):
    """Positions, triangles and one material number per triangle of a mesh, as plain lists."""
    dynamic = wieland_refine._dynamic(static_mesh)
    positions, triangles = wieland_refine._arrays(dynamic)
    result = unreal.GeometryScript_Materials.get_all_triangle_material_i_ds(dynamic)
    index_list = [item for item in result if isinstance(item, unreal.GeometryScriptIndexList)][0]
    materials = [m for m in unreal.GeometryScript_List.convert_index_list_to_array(index_list) if m >= 0]
    if len(materials) != len(triangles):
        materials = [0] * len(triangles)
    return positions, triangles, materials


def _cut(positions, triangles, materials, flipped, height):
    """Cut a mesh (world positions) with a level plane: pieces (point, point, outward direction, material)."""
    pieces = []
    for number, (i, j, k) in enumerate(triangles):
        a, b, c = positions[i], positions[j], positions[k]
        da, db, dc = a[2] - height, b[2] - height, c[2] - height
        if (da > 0.0) == (db > 0.0) == (dc > 0.0):
            continue
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        # Unreal's front faces wind clockwise: the outward direction is (c - a) x (b - a).
        nx, ny, nz = vy * uz - vz * uy, vz * ux - vx * uz, vx * uy - vy * ux
        if flipped:
            nx, ny, nz = -nx, -ny, -nz
        flat = math.hypot(nx, ny)
        if flat < 1e-9 or flat < 0.5 * abs(nz):
            continue  # not an upright face
        points = []
        for (p, dp), (q, dq) in (((a, da), (b, db)), ((b, db), (c, dc)), ((c, dc), (a, da))):
            if (dp > 0.0) != (dq > 0.0):
                t = dp / (dp - dq)
                points.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        if len(points) == 2:
            pieces.append((points[0], points[1], (nx / flat, ny / flat), materials[number]))
    return pieces


def _lines(pieces, eligible):
    """Join the pieces of one wall into straight stretches: (direction, offset, start, end, material name).

    Only pieces whose material is in `eligible` (material number -> name) are used."""
    groups = {}
    for p, q, n, material in pieces:
        if material not in eligible:
            continue
        angle = round(math.degrees(math.atan2(n[1], n[0])) / 2.0) * 2.0
        if angle == -180.0:
            angle = 180.0
        groups.setdefault((angle, material), []).append((p, q))
    lines = []
    for (angle, material), items in groups.items():
        n = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        t = (-n[1], n[0])
        spans = []
        for p, q in items:
            offset = (p[0] * n[0] + p[1] * n[1] + q[0] * n[0] + q[1] * n[1]) / 2.0
            s1, s2 = p[0] * t[0] + p[1] * t[1], q[0] * t[0] + q[1] * t[1]
            spans.append((offset, min(s1, s2), max(s1, s2)))
        spans.sort()
        clusters = []
        for span in spans:
            if clusters and span[0] - clusters[-1][-1][0] < 0.1:
                clusters[-1].append(span)
            else:
                clusters.append([span])
        for cluster in clusters:
            offset = sum(span[0] for span in cluster) / len(cluster)
            cluster.sort(key=lambda span: span[1])
            start, end = cluster[0][1], cluster[0][2]
            for _, s1, s2 in cluster[1:]:
                if s1 <= end + 0.3:
                    end = max(end, s2)
                else:
                    lines.append((n, offset, start, end, eligible[material]))
                    start, end = s1, s2
            lines.append((n, offset, start, end, eligible[material]))
    return lines


def _inside(boxes, x, y, z_low, z_high, skip=None):
    for number, box in enumerate(boxes):
        if number == skip:
            continue
        if box[0] <= x <= box[3] and box[1] <= y <= box[4] and box[2] < z_high and box[5] > z_low:
            return True
    return False


def _near(doors, x, y):
    """True when a part of a door comes within OUTLINE_REACH of the point. doors = [(box, pieces)]."""
    for box, pieces in doors:
        if not (box[0] - OUTLINE_REACH <= x <= box[3] + OUTLINE_REACH
                and box[1] - OUTLINE_REACH <= y <= box[4] + OUTLINE_REACH):
            continue
        for (px, py), (qx, qy) in pieces:
            dx, dy = qx - px, qy - py
            length = dx * dx + dy * dy
            f = 0.0 if length < 1e-12 else max(0.0, min(1.0, ((x - px) * dx + (y - py) * dy) / length))
            if math.hypot(x - px - dx * f, y - py - dy * f) <= OUTLINE_REACH:
                return True
    return False


def plan_runs(window=None, floors=None):
    """Read-only: every baseboard run of the building. window = (x_min, y_min, x_max, y_max) limits the
    work to runs whose middle lies inside it. Returns (runs, info); a run is a dict."""
    parts = _building_components()
    walls = [(actor, component) for actor, component, category in parts if category in WALLS]
    wall_boxes = [_component_box(component) for _, component in walls]
    blocker_boxes = []
    outline_parts = []
    for _, component, category in parts:
        if category not in BLOCKERS:
            continue
        box = _component_box(component)
        if category in OUTLINE_BLOCKERS:
            outline_parts.append((component, box))
            continue
        longest = max(box[3] - box[0], box[4] - box[1])
        shortest = min(box[3] - box[0], box[4] - box[1])
        # The test uses the object's box. A box says little about a large open object (the massing of
        # the neighbours, a facade frame, a long guardrail), so those do not count.
        if category in LOOSE_BLOCKERS and longest > LOOSE_LIMIT:
            continue
        if shortest > 600.0:
            continue
        blocker_boxes.append(box)
    floor_boxes = [_component_box(component) for _, component, category in parts if category in FLOOR_CATEGORIES]
    meshes = {}
    outlines = {}
    runs = []
    info = {"walls": len(walls), "lines": 0, "too_short": 0, "pocket_faces": 0}
    for floor, level in FLOORS:
        if floors is not None and floor not in floors:
            continue
        height = level + CUT
        floor_runs = []
        doors = []
        for component, box in outline_parts:
            if not (box[2] < level + OUTLINE_HEIGHTS[-1] and box[5] > level + OUTLINE_HEIGHTS[0]):
                continue
            if window is not None and (box[3] < window[0] or box[0] > window[2] or box[4] < window[1]
                                       or box[1] > window[3]):
                continue
            key = component.static_mesh.get_path_name()
            if key not in outlines:
                outlines[key] = wieland_refine._arrays(wieland_refine._dynamic(component.static_mesh))
            positions, triangles = outlines[key]
            world, flipped = wieland_refine._world_positions(component, positions)
            pieces = []
            for above in OUTLINE_HEIGHTS:
                pieces.extend((a, b) for a, b, _, _ in _cut(world, triangles, [0] * len(triangles), flipped,
                                                            level + above))
            if pieces:
                doors.append((box, pieces))
        for number, (actor, component) in enumerate(walls):
            box = wall_boxes[number]
            if not (box[2] < height < box[5]):
                continue
            if window is not None and (box[3] < window[0] or box[0] > window[2] or box[4] < window[1]
                                       or box[1] > window[3]):
                continue
            names = {}
            for slot, material in enumerate(component.get_materials()):
                if material is not None and material.get_name() in BOARD_FACES:
                    names[slot] = material.get_name()
            if not names:
                continue
            key = component.static_mesh.get_path_name()
            if key not in meshes:
                meshes[key] = _material_ids(component.static_mesh)
            positions, triangles, materials = meshes[key]
            world, flipped = wieland_refine._world_positions(component, positions)
            pieces = _cut(world, triangles, materials, flipped, height)
            metadata = wieland_levels._metadata(actor)
            for n, offset, start, end, face in _lines(pieces, names):
                info["lines"] += 1
                t = (-n[1], n[0])
                tally = {}
                # A face that looks across the wall but lies inside the wall's own box is the inside of a
                # door pocket, not a room face.
                across = abs(n[0]) > 0.7 if box[3] - box[0] < box[4] - box[1] else abs(n[1]) > 0.7
                probe = (n[0] * (offset + THICK / 2.0) + t[0] * (start + end) / 2.0,
                         n[1] * (offset + THICK / 2.0) + t[1] * (start + end) / 2.0)
                if across and box[0] < probe[0] < box[3] and box[1] < probe[1] < box[4]:
                    info["pocket_faces"] = info.get("pocket_faces", 0) + 1
                    continue

                def state(s):
                    """Floor top under the board at distance s along the line, or None where no board goes."""
                    x = n[0] * (offset + THICK / 2.0) + t[0] * s
                    y = n[1] * (offset + THICK / 2.0) + t[1] * s
                    top = None
                    for fb in floor_boxes:
                        if fb[0] <= x <= fb[3] and fb[1] <= y <= fb[4] and abs(fb[5] - level) <= FLOOR_REACH:
                            top = fb[5] if top is None else max(top, fb[5])
                    if top is None:
                        tally["no floor"] = tally.get("no floor", 0) + 1
                        return None
                    if _inside(blocker_boxes, x, y, top + 0.5, top + HEIGHT):
                        tally["covered"] = tally.get("covered", 0) + 1
                        return None
                    if _near(doors, x, y):
                        tally["door"] = tally.get("door", 0) + 1
                        return None
                    if _inside(wall_boxes, x, y, top + 0.5, top + HEIGHT, skip=number):
                        tally["in a wall"] = tally.get("in a wall", 0) + 1
                        return None
                    tally["board"] = tally.get("board", 0) + 1
                    return top

                count = max(1, int(math.ceil((end - start) / STEP)))
                marks = [start + (end - start) * i / count for i in range(count + 1)]
                states = [state(s) is not None for s in marks]
                stretches = []
                i = 0
                while i <= count:
                    if not states[i]:
                        i += 1
                        continue
                    j = i
                    while j < count and states[j + 1]:
                        j += 1
                    low, high = marks[i], marks[j]
                    if i > 0:  # find the true start between the last bad mark and the first good one
                        bad, good = marks[i - 1], marks[i]
                        for _ in range(5):
                            middle = (bad + good) / 2.0
                            if state(middle) is not None:
                                good = middle
                            else:
                                bad = middle
                        low = good
                    if j < count:
                        good, bad = marks[j], marks[j + 1]
                        for _ in range(5):
                            middle = (bad + good) / 2.0
                            if state(middle) is not None:
                                good = middle
                            else:
                                bad = middle
                        high = good
                    stretches.append((low, high))
                    i = j + 1
                if window is not None:  # a trial: keep what happened to each line, for checking
                    info.setdefault("detail", []).append((actor.get_actor_label(), round(n[0], 2), round(n[1], 2),
                                                          round(offset, 1), round(start, 1), round(end, 1), face,
                                                          dict(tally)))
                for low, high in stretches:
                    if high - low < MIN_RUN:
                        info["too_short"] += 1
                        continue
                    middle = (low + high) / 2.0
                    mx = n[0] * offset + t[0] * middle
                    my = n[1] * offset + t[1] * middle
                    if window is not None and not (window[0] <= mx <= window[2] and window[1] <= my <= window[3]):
                        continue
                    half = "North" if mx + n[0] * THICK < wieland_levels.PARTY_X else "South"
                    unit = half + ("Penthouse" if floor in PENTHOUSE_FLOORS else "Triplex")
                    floor_runs.append({
                        "unit": unit, "floor": floor, "n": n, "t": t, "offset": offset, "start": low, "end": high,
                        "top": state(middle), "wall": actor.get_actor_label(),
                        "wall_type": metadata.get("Element*Type", ""), "face": face})
        floor_runs = _joined(floor_runs)
        _corners(floor_runs)
        runs.extend(floor_runs)
    kept = []
    for run in runs:
        if run["end"] - run["start"] >= MIN_RUN:
            kept.append(run)
        else:
            info["too_short"] += 1
    info["runs"] = len(kept)
    info["length_m"] = round(sum(run["end"] - run["start"] for run in kept) / 100.0, 1)
    return kept, info


def _joined(runs):
    """Runs that continue each other in one line on one floor level (two wall objects built end to end)
    become one run, so that the board shows no joint there."""
    done = []
    for run in sorted(runs, key=lambda r: (r["unit"], round(r["n"][0], 3), round(r["n"][1], 3),
                                           round(r["offset"], 0), r["start"])):
        last = done[-1] if done else None
        if (last is not None and last["unit"] == run["unit"] and abs(last["n"][0] - run["n"][0]) < 1e-3
                and abs(last["n"][1] - run["n"][1]) < 1e-3 and abs(last["offset"] - run["offset"]) < 0.1
                and abs(last["top"] - run["top"]) < 0.1 and run["start"] - last["end"] < 0.5):
            last["end"] = max(last["end"], run["end"])
            if run["wall"] not in last["wall"].split(" + "):
                last["wall"] += " + " + run["wall"]
        else:
            done.append(run)
    return done


def _end_point(run, which):
    s = run[which]
    return (run["n"][0] * run["offset"] + run["t"][0] * s, run["n"][1] * run["offset"] + run["t"][1] * s)


def _corners(runs):
    """Where two runs meet at a corner: lengthen both at an outside corner so the boards close it;
    shorten one at an inside corner so the boards do not lie in each other."""
    ends = []
    for number, run in enumerate(runs):
        for which, sign in (("start", -1.0), ("end", 1.0)):
            ends.append((number, which, _end_point(run, which), (run["t"][0] * sign, run["t"][1] * sign)))
    change = {}
    for number, which, point, onward in ends:
        for other, _, other_point, _ in ends:
            if other == number:
                continue
            if math.hypot(point[0] - other_point[0], point[1] - other_point[1]) > 1.0:
                continue
            facing = runs[other]["n"][0] * onward[0] + runs[other]["n"][1] * onward[1]
            if facing > 0.7:
                change[(number, which)] = THICK + EASE
            elif facing < -0.7 and number > other:
                change[(number, which)] = -THICK
    for (number, which), amount in change.items():
        if which == "start":
            runs[number]["start"] -= amount
        else:
            runs[number]["end"] += amount


def write_runs(runs, csv_path):
    counts = {}
    rows = []
    for run in runs:
        key = (run["unit"], run["floor"])
        counts[key] = counts.get(key, 0) + 1
        a, b = _end_point(run, "start"), _end_point(run, "end")
        rows.append([LABEL + "%s_%s" % key, run["unit"], run["floor"], counts[key], round(a[0], 1), round(a[1], 1),
                     round(b[0], 1), round(b[1], 1), round(run["top"], 1), round(run["end"] - run["start"], 1),
                     round(run["n"][0], 2), round(run["n"][1], 2), run["wall"], run["wall_type"], run["face"], RULE])
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(RUN_HEAD)
        writer.writerows(rows)
    return {"rows": len(rows), "objects": len(counts),
            "per_object": sorted(("%s_%s" % key, n) for key, n in counts.items())}


def _eased_box(centre, axes, half):
    """A box with every edge eased by EASE: positions and triangles, each triangle with its own vertices."""
    def place(local):
        return tuple(centre[i] + axes[0][i] * local[0] + axes[1][i] * local[1] + axes[2][i] * local[2]
                     for i in range(3))

    def corner_point(axis, signs):
        return tuple(signs[i] * (half[i] if i == axis else half[i] - EASE) for i in range(3))

    faces = []
    for axis in range(3):
        first, second = [i for i in range(3) if i != axis]
        for sign in (-1.0, 1.0):
            quad = []
            for s1, s2 in ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)):
                signs = [0.0, 0.0, 0.0]
                signs[axis], signs[first], signs[second] = sign, s1, s2
                quad.append(corner_point(axis, signs))
            faces.append(quad)
    for axis in range(3):  # the edges that run along this axis
        first, second = [i for i in range(3) if i != axis]
        for s1 in (-1.0, 1.0):
            for s2 in (-1.0, 1.0):
                quad = []
                for face_axis, along in ((first, -1.0), (first, 1.0), (second, 1.0), (second, -1.0)):
                    signs = [0.0, 0.0, 0.0]
                    signs[axis], signs[first], signs[second] = along, s1, s2
                    quad.append(corner_point(face_axis, signs))
                faces.append(quad)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                faces.append([corner_point(axis, (sx, sy, sz)) for axis in range(3)])
    positions, triangles = [], []
    for face in faces:
        fans = [(face[0], face[1], face[2])] if len(face) == 3 else [(face[0], face[1], face[2]),
                                                                     (face[0], face[2], face[3])]
        for a, b, c in fans:
            u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
            v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
            normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            middle = ((a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0, (a[2] + b[2] + c[2]) / 3.0)
            # Unreal's front faces wind clockwise, so in the level the cross product of a well-ordered face
            # points inwards. The axes of a run (along, out of the wall, up) are a mirrored frame, which
            # turns the order round once more: here, in the box's own frame, it must point outwards.
            if normal[0] * middle[0] + normal[1] * middle[1] + normal[2] * middle[2] < 0.0:
                b, c = c, b
            base = len(positions)
            positions.extend([place(a), place(b), place(c)])
            triangles.append((base, base + 1, base + 2))
    return positions, triangles


def run_arrays(runs):
    """Mesh lists of a set of runs, in level coordinates."""
    positions, triangles, uvs = [], [], []
    for run in runs:
        n, t = run["n"], run["t"]
        length = run["end"] - run["start"]
        middle = (run["start"] + run["end"]) / 2.0
        out = run["offset"] + (THICK - SINK) / 2.0
        centre = (n[0] * out + t[0] * middle, n[1] * out + t[1] * middle, run["top"] + (HEIGHT - SINK) / 2.0)
        axes = ((t[0], t[1], 0.0), (n[0], n[1], 0.0), (0.0, 0.0, 1.0))
        half = (length / 2.0, (THICK + SINK) / 2.0, (HEIGHT + SINK) / 2.0)
        box_positions, box_triangles = _eased_box(centre, axes, half)
        base = len(positions)
        positions.extend(box_positions)
        for i, j, k in box_triangles:
            triangles.append((base + i, base + j, base + k))
            triple = []
            for index in (i, j, k):
                p = box_positions[index]
                along = (p[0] * t[0] + p[1] * t[1]) / 100.0
                triple.append((along, (p[2] - run["top"]) / 100.0))
            uvs.append(tuple(triple))
    return positions, triangles, uvs


def object_name(unit, floor, suffix=""):
    return "%s%s_%s%s" % (LABEL, unit, floor, suffix)


def build(runs, unit, floor, suffix="", save=True):
    """Make the mesh asset of one unit's storey and place it as one new object in that unit's level.
    Refuses when the asset or the object exists. Does not save the level; see wieland_levels.save_unit_level()."""
    chosen = [run for run in runs if run["unit"] == unit and run["floor"] == floor]
    if not chosen:
        return {"object": object_name(unit, floor, suffix), "runs": 0}
    name = object_name(unit, floor, suffix)
    path = "%s/SM_W1529_G_%s" % (MESH_FOLDER, name[len("GEN_"):])
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError("refused: %s exists already" % path)
    if any(actor.get_actor_label() == name for actor in wieland_levels._actors()):
        raise RuntimeError("refused: an object %s exists already" % name)
    world = wieland_levels._world()
    target = None
    for level in unreal.EditorLevelUtils.get_levels(world):
        if level.get_outermost().get_name() == wieland_levels.level_path(unit):
            target = level
    if target is None:
        raise RuntimeError("the level of %s is not loaded" % unit)
    positions, triangles, uvs = run_arrays(chosen)
    dynamic = wieland_refine._dynamic_from_arrays(positions, triangles, uvs, [0] * len(triangles))
    options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    options.set_editor_property("enable_recompute_normals", False)
    options.set_editor_property("enable_recompute_tangents", True)
    options.set_editor_property("enable_collision", False)
    options.set_editor_property("enable_nanite", True)
    result = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic, path, options)
    mesh, outcome = result if isinstance(result, tuple) else (result, unreal.GeometryScriptOutcomePins.SUCCESS)
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS or mesh is None:
        raise RuntimeError("could not create %s" % path)
    material = unreal.EditorAssetLibrary.load_asset(BOARD_MATERIAL)
    if material is None:
        raise RuntimeError("the material %s is missing" % BOARD_MATERIAL)
    mesh.set_material(0, material)
    saved = bool(unreal.EditorAssetLibrary.save_asset(path, False)) if save else False
    unreal.EditorLevelUtils.make_level_current(unreal.GameplayStatics.get_streaming_level(
        world, wieland_levels.level_path(unit)))
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = subsystem.spawn_actor_from_object(mesh, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator())
    where = wieland_levels._level_name(actor)
    if where != wieland_levels.level_path(unit).split("/")[-1]:
        subsystem.destroy_actor(actor)
        raise RuntimeError("the object went to %s, not to the level of %s" % (where, unit))
    actor.set_actor_label(name)
    actor.set_folder_path("W1529_Generated/Baseboards")
    half = "North" if unit.startswith("North") else "South"
    actor.tags = [unreal.Name(TAG_GENERATED), unreal.Name("W1529.Unit." + unit), unreal.Name("W1529.Floor." + floor),
                  unreal.Name("W1529.Half." + half)]
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
    edges = wieland_refine.sharp_edges(positions, triangles)
    return {"object": name, "mesh": path, "mesh_saved": saved, "runs": len(chosen),
            "length_m": round(sum(run["end"] - run["start"] for run in chosen) / 100.0, 1),
            "triangles": len(triangles), "sharp_edges": len(edges), "level": where}


def build_all(runs):
    """build() for every unit and storey that has runs. Returns one result per object."""
    results = []
    for key in sorted(set((run["unit"], run["floor"]) for run in runs)):
        results.append(build(runs, key[0], key[1]))
    return results


def remove(name, delete_mesh=False):
    """Take a generated object out of its level again (only objects this tool made)."""
    removed = 0
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in wieland_levels._actors():
        if actor.get_actor_label() == name and TAG_GENERATED in [str(tag) for tag in actor.tags]:
            subsystem.destroy_actor(actor)
            removed += 1
    deleted = False
    if delete_mesh:
        path = "%s/SM_W1529_G_%s" % (MESH_FOLDER, name[len("GEN_"):])
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            deleted = bool(unreal.EditorAssetLibrary.delete_asset(path))
    return {"removed": removed, "mesh_deleted": deleted}


def generated():
    """Read-only: (level, label, mesh) of every generated object."""
    found = []
    for actor in wieland_levels._actors():
        if TAG_GENERATED in [str(tag) for tag in actor.tags]:
            mesh = ""
            if isinstance(actor, unreal.StaticMeshActor) and actor.static_mesh_component.static_mesh is not None:
                mesh = actor.static_mesh_component.static_mesh.get_path_name().split(".")[0]
            found.append((wieland_levels._level_name(actor), actor.get_actor_label(), mesh))
    return sorted(found)
