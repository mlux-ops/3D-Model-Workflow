"""Phase 6, step 6.5: grey stand-in blocks for furniture that is proposed but not approved.

Runs inside the Unreal editor with L_Site_M4 open. Nothing is acquired and no imported object is
edited: a stand-in is a plain grey box of the size given in furniture_proposal.csv, a new mesh asset
placed as a new object in the level of its unit, tagged W1529.Placeholder and W1529.Generated.

How a place is found. Each storey is laid out as a plan grid of 10 cm cells. A cell is closed where
a wall, a door, casework, a fixture, a stair, a railing or another fixed object stands, or where
there is no floor. From a point inside a room the open cells that can be reached without crossing a
closed cell are that room. A piece that belongs against a wall is put with its back to a wall
stretch that has no window or door, with clear floor in front; a free-standing piece is put on clear
floor near the middle of the room. Furniture that the Revit model already holds is kept clear of,
and a piece is left out where the room already holds Revit furniture of that kind.
Each half of the building is worked from its own geometry; nothing is mirrored.

Order of use:
    survey()                                  # read-only: every room, its size, the Revit furniture in it
    plan_room("T_1_living", "North")          # read-only: where the pieces of one room would go
    place(plan)                               # make the blocks
    write_csv(csv_path)                       # the list of every block in the level
Frame of the level: origin at the lot's south-west corner, north is -X, east is -Y, centimetres.
"""

import csv
import math

import unreal

import wieland_interiors
import wieland_levels
import wieland_refine
import wieland_trim

CELL = 10.0
X_MIN, Y_MIN, X_MAX, Y_MAX = -1420.0, -3030.0, -90.0, -310.0
NX = int(round((X_MAX - X_MIN) / CELL))
NY = int(round((Y_MAX - Y_MIN) / CELL))
STOREYS = {"L": ("Lower", -152.4), "1": ("Floor1", 203.2), "2": ("Floor2", 528.3), "3": ("Floor3", 853.4),
           "4": ("Floor4", 1178.6), "R": ("Roof", 1524.0)}
PENTHOUSE = ("3", "4", "R")
REACH = 700.0          # a room is followed at most this far from its starting point
FLOOR_REACH = 30.0     # a floor counts for a storey when its top is this near the storey's level
WALL, FIXED, DOOR, WINDOW, FURNITURE, PLACED, NO_FLOOR = 1, 2, 4, 8, 16, 32, 64
CLOSED = WALL | FIXED | DOOR | NO_FLOOR
FURNITURE_CATEGORIES = ("Furniture", "Furniture Systems")
# Furniture that the Revit model holds in another category: {part of the object name: what it is}.
FURNITURE_NAMES = {"Fritz-Hansen_PL113S": "sofa"}
OPEN_CATEGORIES = ("Floors", "Ceilings", "Roofs", "Lighting Fixtures", "Lighting Devices", "Electrical Fixtures",
                   "Topography", "Site", "Planting", "Entourage", "Rooms", "Structural Framing")
FREE_CLEAR = 3         # cells of clear floor round a free-standing piece
# Clear floor in front of a piece that stands against a wall, and the distance kept from every door, in
# cells: the generous pair is tried first, the tight pair where a small room leaves no other place.
CLEARANCES = ((6, 6), (3, 3))
EASE = 1.0             # every edge of a block is eased by this much, so that no edge is sharp
MESH_FOLDER = "/Game/Wieland1529/Interiors/Generated/Placeholders"
MATERIAL = MESH_FOLDER + "/M_W1529_Placeholder"
TAG_PLACEHOLDER = "W1529.Placeholder"
TAG_GENERATED = "W1529.Generated"
LABEL = "PH_"
FOLDER = "W1529_Generated/Placeholders"
HEAD = ["object", "unit", "floor", "room", "room_type", "piece", "proposal_item", "width_cm", "depth_cm", "height_cm",
        "x", "y", "floor_z", "turned_deg", "placed_as", "mesh", "note"]
NOTE = "grey stand-in (step 6.5); furniture is not approved; dressing waits for the owner"

# Rooms that are not in wieland_interiors.ROOMS_NORTH: (storey code, x, y) of a point inside, north half.
EXTRA_ROOMS_NORTH = {
    "P_R_roof_room": ("R", -1150.0, -1200.0),
    "P_R_front_roof_deck": ("R", -1100.0, -600.0),
    "P_R_rear_roof_deck": ("R", -1100.0, -2000.0),
}
ROOM_TYPES = {
    "T_L_garage": "Garage", "T_L_family_room": "Family room (lower floor)", "T_L_bedroom_a": "Bedroom (secondary)",
    "T_L_bedroom_b": "Bedroom (secondary)", "T_1_dining": "Dining room", "T_1_living": "Living room",
    "T_2_primary_bedroom": "Primary bedroom", "T_2_bedroom_b": "Bedroom (secondary)",
    "T_2_rear_bedroom": "Bedroom (secondary)", "P_3_front_bedroom": "Primary bedroom", "P_3_hall": "Hall and entry",
    "P_3_bedroom_b": "Bedroom (secondary)", "P_3_bedroom_c": "Bedroom (secondary)",
    "P_3_rear_bedroom": "Bedroom (secondary)", "P_4_living_dining": "Living room + Dining room",
    "P_4_rear_terrace": "Roof deck and rear terrace (penthouse)",
    "P_R_front_roof_deck": "Roof deck and rear terrace (penthouse)",
    "P_R_rear_roof_deck": "Roof deck and rear terrace (penthouse)",
}
# The pieces that give a room its volume, by room type:
# (short name, item of furniture_proposal.csv, width, depth, height, how it stands, how many,
#  words in the name of a Revit furniture object that make the piece unnecessary).
# "wall": back to a wall; "wall or free": back to a wall, or on clear floor where no wall stretch serves;
# "edge": back to a wall, parapet or railing; "free": on clear floor;
# "set": a dining table with its chairs (see SETS), on clear floor;
# "parking": on the parking space that the Revit model draws in this half, along its length.
PIECES = {
    "Living room": (
        ("sofa", "Sofa, three seats", 240.0, 95.0, 80.0, "wall or free", 1, ("sofa", "seat", "zip", "sectional")),
        ("media_cabinet", "Media cabinet, low", 244.0, 52.0, 68.0, "wall", 1, ("media", "credenza", "sideboard")),
        ("coffee_table", "Coffee table", 120.0, 60.0, 39.0, "free", 1, ("coffee", "centre_tabl", "center_tabl")),
        ("lounge_chair", "Lounge chair", 101.0, 119.0, 117.0, "free", 2, ("lounge", "armchair")),
    ),
    "Family room (lower floor)": (
        ("sectional_sofa", "Sectional sofa", 280.0, 160.0, 80.0, "wall or free", 1, ("sofa", "seat", "zip", "sectional")),
        ("shelving_unit", "Shelving unit", 235.0, 72.0, 231.0, "wall", 1, ("shelv", "book")),
        ("coffee_table_round", "Coffee table, round", 130.0, 130.0, 49.0, "free", 1,
         ("coffee", "centre_tabl", "center_tabl")),
    ),
    "Dining room": (
        ("dining_table", "Dining table for eight", 240.0, 105.0, 75.0, "set", 1,
         ("diningtab", "dining_tab", "dining-tab", "table_r")),
        ("sideboard", "Sideboard", 244.0, 52.0, 68.0, "wall", 1, ("sideboard", "credenza", "media")),
    ),
    "Primary bedroom": (
        ("bed_king", "Bed, king, with bedding", 200.0, 215.0, 105.0, "wall", 1, ("bed",)),
        ("dresser", "Dresser", 114.0, 49.0, 188.0, "wall", 1, ("dresser", "drawer")),
        ("armchair", "Armchair", 82.0, 99.0, 102.0, "free", 1, ("armchair", "lounge")),
    ),
    "Bedroom (secondary)": (
        ("bed_queen", "Bed, queen, with bedding", 160.0, 210.0, 105.0, "wall", 1, ("bed",)),
        ("desk", "Desk and chair", 140.0, 70.0, 75.0, "wall", 1, ("desk",)),
        ("display_shelves", "Display shelves", 108.0, 37.0, 156.0, "wall", 1, ("shelv", "book")),
    ),
    "Hall and entry": (
        ("console_table", "Console table", 140.0, 35.0, 80.0, "wall", 1, ("console",)),
    ),
    "Garage": (
        ("car", "Car", 480.0, 190.0, 145.0, "parking", 1, ("car", "vehicle")),
    ),
    "Roof deck and rear terrace (penthouse)": (
        ("outdoor_sectional", "Outdoor sectional sofa", 280.0, 200.0, 70.0, "edge", 1,
         ("sofa", "seat", "sectional")),
        ("outdoor_dining", "Outdoor dining table for six, with chairs", 200.0, 100.0, 75.0, "set", 1,
         ("diningtab", "dining_tab", "dining-tab", "table_r")),
        ("planter", "Planters with shrubs", 60.0, 60.0, 120.0, "edge", 4, ("planter",)),
    ),
}
SEAT_WORDS = ("sofa", "seat", "zip", "sectional")
WITH_SEATS = ("coffee_table", "coffee_table_round", "lounge_chair", "armchair")
# The chairs of a dining set: (chair width, depth, height, chairs on each long side, chairs at each end).
SETS = {"dining_table": (43.0, 58.0, 97.0, 3, 1), "outdoor_dining": (55.0, 55.0, 85.0, 3, 0)}
SET_CHAIR_OUT = 15.0             # how far the middle of a chair stands outside the table edge
SET_CHAIR_STEP = 65.0            # spacing of the chairs along a long side


def rooms(half):
    """{room: (storey code, x, y)} of one half; the south half by mirroring the starting points only."""
    found = {}
    # A room view is (storey, camera x, y, target x, y). The camera often stands in a doorway; the point
    # half-way to its target lies inside the room.
    for name, value in wieland_interiors.ROOMS_NORTH.items():
        found[name] = (value[0], (value[1] + value[3]) / 2.0, (value[2] + value[4]) / 2.0)
    found.update(EXTRA_ROOMS_NORTH)
    if half == "South":
        found = {name: (code, 2.0 * wieland_levels.PARTY_X - x, y) for name, (code, x, y) in found.items()}
    return found


def _cells(low, high, origin, count):
    first = max(0, int(math.floor((low - origin) / CELL + 0.5)))
    last = min(count - 1, int(math.ceil((high - origin) / CELL - 0.5)) - 0)
    return first, last


def _mark(grid, box, bit):
    i0, i1 = _cells(box[0], box[3], X_MIN, NX)
    j0, j1 = _cells(box[1], box[4], Y_MIN, NY)
    for i in range(i0, i1 + 1):
        row = grid[i]
        for j in range(j0, j1 + 1):
            row[j] |= bit


_parts = None


def parts(refresh=False):
    """(label, category, box) of every imported mesh of the interior levels; read once and kept."""
    global _parts
    if _parts is None or refresh:
        _parts = [(actor.get_actor_label(), category, wieland_trim._component_box(component))
                  for actor, component, category in wieland_trim._building_components()]
    return _parts


def blocks():
    """The stand-in objects in the level."""
    return [actor for actor in wieland_levels._actors()
            if TAG_PLACEHOLDER in [str(tag) for tag in actor.tags]]


def storey_grid(code):
    """The plan grid of one storey and the boxes behind it: (grid, floor tops, wall boxes, fixed boxes,
    furniture [(label, box)])."""
    level = STOREYS[code][1]
    low, high = level + 10.0, level + 180.0
    grid = [[0] * NY for _ in range(NX)]
    tops = [[None] * NY for _ in range(NX)]
    wall_boxes, fixed_boxes, furniture = [], [], []
    for label, category, box in parts():
        if category in ("Floors", "Roofs"):
            if abs(box[5] - level) <= FLOOR_REACH and box[5] - box[2] < 120.0:
                i0, i1 = _cells(box[0], box[3], X_MIN, NX)
                j0, j1 = _cells(box[1], box[4], Y_MIN, NY)
                for i in range(i0, i1 + 1):
                    for j in range(j0, j1 + 1):
                        if tops[i][j] is None or box[5] > tops[i][j]:
                            tops[i][j] = box[5]
            continue
        if category in OPEN_CATEGORIES:
            continue
        stair = "Stair" in category or category in ("Runs", "Landings", "Supports", "Railings")
        if not (box[2] < high and box[5] > (level - 100.0 if stair else low)):
            continue
        named = [kind for name, kind in FURNITURE_NAMES.items() if name in label]
        if category in FURNITURE_CATEGORIES or named:
            furniture.append((label + " (%s)" % named[0] if named else label, box))
            if box[5] - box[2] > 5.0:  # a rug does not stand in the way
                _mark(grid, box, FURNITURE)
            continue
        if category == "Walls":
            _mark(grid, box, WALL)
            wall_boxes.append(box)
            continue
        if category == "Doors":
            _mark(grid, box, DOOR)
            fixed_boxes.append(box)
            continue
        if "Window" in category or "Curtain" in category:
            _mark(grid, box, WINDOW | FIXED)
            fixed_boxes.append(box)
            continue
        if min(box[3] - box[0], box[4] - box[1]) > 600.0:
            continue  # a box this large says nothing about where the object stands
        if category in ("Generic Models", "Railings", "Supports") and max(box[3] - box[0], box[4] - box[1]) > 1500.0:
            continue
        _mark(grid, box, FIXED)
        fixed_boxes.append(box)
    for i in range(NX):
        for j in range(NY):
            if tops[i][j] is None:
                grid[i][j] |= NO_FLOOR
    for actor in blocks():
        origin, extent = actor.get_actor_bounds(False)
        box = (origin.x - extent.x, origin.y - extent.y, origin.z - extent.z,
               origin.x + extent.x, origin.y + extent.y, origin.z + extent.z)
        if box[2] < high and box[5] > low:
            _mark(grid, box, PLACED)
    return grid, tops, wall_boxes, fixed_boxes, furniture


def _window_grid(code, height):
    """Cells of windows and glazed walls that a piece of this height would stand in front of."""
    level = STOREYS[code][1]
    grid = [[0] * NY for _ in range(NX)]
    for label, category, box in parts():
        if ("Window" in category or "Curtain" in category) and box[2] < level + height and box[5] > level + 5.0:
            grown = (box[0] - 5.0, box[1] - 5.0, box[2], box[3] + 5.0, box[4] + 5.0, box[5])
            _mark(grid, grown, 1)
    return grid


def region(grid, x, y):
    """The open cells reached from (x, y): a set of (i, j)."""
    si = int((x - X_MIN) / CELL)
    sj = int((y - Y_MIN) / CELL)
    start = None
    for radius in range(0, 8):
        for i in range(si - radius, si + radius + 1):
            for j in range(sj - radius, sj + radius + 1):
                if 0 <= i < NX and 0 <= j < NY and not grid[i][j] & CLOSED:
                    start = (i, j)
                    break
            if start:
                break
        if start:
            break
    if start is None:
        return set()
    reach = int(REACH / CELL)
    seen = {start}
    queue = [start]
    while queue:
        i, j = queue.pop()
        for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if (a, b) in seen or not (0 <= a < NX and 0 <= b < NY):
                continue
            if abs(a - si) > reach or abs(b - sj) > reach or grid[a][b] & CLOSED:
                continue
            seen.add((a, b))
            queue.append((a, b))
    return seen


def _furniture_in(cells, furniture):
    found = []
    for label, box in furniture:
        i = int(((box[0] + box[3]) / 2.0 - X_MIN) / CELL)
        j = int(((box[1] + box[4]) / 2.0 - Y_MIN) / CELL)
        if any((i + a, j + b) in cells for a in (-1, 0, 1) for b in (-1, 0, 1)):
            found.append((label, box))
    return found


def survey(halves=("North", "South")):
    """Read-only. For every room: storey, open floor in m2, extent, and the Revit furniture standing in it."""
    result = []
    grids = {}
    for half in halves:
        for name, (code, x, y) in sorted(rooms(half).items()):
            if code not in grids:
                grids[code] = storey_grid(code)
            grid, tops, _, _, furniture = grids[code]
            cells = region(grid, x, y)
            inside = _furniture_in(cells, furniture)
            if cells:
                extent = (round(X_MIN + min(i for i, _ in cells) * CELL), round(Y_MIN + min(j for _, j in cells) * CELL),
                          round(X_MIN + (max(i for i, _ in cells) + 1) * CELL),
                          round(Y_MIN + (max(j for _, j in cells) + 1) * CELL))
            else:
                extent = None
            result.append({"half": half, "room": name, "storey": STOREYS[code][0],
                           "open_m2": round(len(cells) * CELL * CELL / 10000.0, 1), "extent": extent,
                           "furniture": sorted(label for label, _ in inside)})
    return result


class _Sums(object):
    """Counts of marked cells in any rectangle of the grid."""

    def __init__(self, test):
        self.table = [[0] * (NY + 1) for _ in range(NX + 1)]
        for i in range(NX):
            row, above, line = self.table[i + 1], self.table[i], 0
            for j in range(NY):
                line += 1 if test(i, j) else 0
                row[j + 1] = above[j + 1] + line

    def count(self, i0, j0, i1, j1):
        """Marked cells with i0 <= i < i1 and j0 <= j < j1; the part outside the grid counts as none."""
        i0, j0, i1, j1 = max(0, i0), max(0, j0), min(NX, i1), min(NY, j1)
        if i1 <= i0 or j1 <= j0:
            return 0
        t = self.table
        return t[i1][j1] - t[i0][j1] - t[i1][j0] + t[i0][j0]


def _distance(box, x, y):
    dx = max(box[0] - x, 0.0, x - box[3])
    dy = max(box[1] - y, 0.0, y - box[4])
    return math.hypot(dx, dy)


def _find(code, grid, cells, windows, others, seed, width, depth, mode, front_clear, door_clear, near=None):
    """The best place for one piece: (x, y, turned, back) or None. `others` are boxes to keep away from.
    A free-standing piece goes as near as it can to `near`, or to the middle of the room without it."""
    is_open = _Sums(lambda i, j: (i, j) in cells and not grid[i][j] & (FURNITURE | PLACED))
    taken = _Sums(lambda i, j: bool(grid[i][j] & (FURNITURE | PLACED)))
    doors = _Sums(lambda i, j: bool(grid[i][j] & DOOR))
    backing = _Sums(lambda i, j: bool(grid[i][j] & (WALL if mode == "wall" else (WALL | FIXED))))
    glazed = _Sums(lambda i, j: bool(windows[i][j]))
    wn = int(math.ceil(width / CELL - 0.01))
    dn = int(math.ceil(depth / CELL - 0.01))
    if cells:
        cx = X_MIN + (sum(i for i, _ in cells) / float(len(cells)) + 0.5) * CELL
        cy = Y_MIN + (sum(j for _, j in cells) / float(len(cells)) + 0.5) * CELL
    else:
        return None
    if near is not None:
        cx, cy = near
    i_low, i_high = min(i for i, _ in cells), max(i for i, _ in cells)
    j_low, j_high = min(j for _, j in cells), max(j for _, j in cells)
    best = None
    for turned, (a, b) in ((0, (wn, dn)), (90, (dn, wn))):
        for i in range(i_low, i_high - a + 2):
            for j in range(j_low, j_high - b + 2):
                if is_open.count(i, j, i + a, j + b) != a * b:
                    continue
                x = X_MIN + (i + a / 2.0) * CELL
                y = Y_MIN + (j + b / 2.0) * CELL
                if mode in ("free", "set"):
                    c = FREE_CLEAR
                    if is_open.count(i - c, j - c, i + a + c, j + b + c) != (a + 2 * c) * (b + 2 * c):
                        continue
                    if doors.count(i - door_clear, j - door_clear, i + a + door_clear, j + b + door_clear):
                        continue
                    score = -math.hypot(x - cx, y - cy)
                    if best is None or score > best[0]:
                        best = (score, x, y, turned, None)
                    continue
                if taken.count(i - 2, j - 2, i + a + 2, j + b + 2):
                    continue
                if doors.count(i - door_clear, j - door_clear, i + a + door_clear, j + b + door_clear):
                    continue
                # The back is one of the two long sides: towards -y or +y when not turned, -x or +x when turned.
                if turned == 0:
                    sides = (("-y", (i, j - 2, i + a, j), (i, j + b, i + a, j + b + front_clear), a),
                             ("+y", (i, j + b, i + a, j + b + 2), (i, j - front_clear, i + a, j), a))
                else:
                    sides = (("-x", (i - 2, j, i, j + b), (i + a, j, i + a + front_clear, j + b), b),
                             ("+x", (i + a, j, i + a + 2, j + b), (i - front_clear, j, i, j + b), b))
                for back, behind, front, length in sides:
                    if backing.count(*behind) < 1.6 * length:
                        continue
                    if glazed.count(*behind):
                        continue
                    if is_open.count(*front) != length * front_clear:
                        continue
                    away = min([300.0] + [_distance(box, x, y) for box in others])
                    score = away - 0.05 * math.hypot(x - seed[0], y - seed[1])
                    if best is None or score > best[0]:
                        best = (score, x, y, turned, back)
    if best is None:
        return None
    return best[1], best[2], best[3], best[4]


def _snap(x, y, turned, back, width, depth, boxes, level):
    """Move a wall piece so that its back stands 1 cm off the face behind it."""
    if back is None:
        return x, y
    half_w, half_d = width / 2.0, depth / 2.0
    low, high = level + 10.0, level + 60.0
    if back in ("-y", "+y"):
        sign = -1.0 if back == "-y" else 1.0
        edge = y + sign * (math.ceil(depth / CELL - 0.01) * CELL / 2.0)
        faces = []
        for box in boxes:
            if box[5] < low or box[2] > high or box[3] < x - half_w or box[0] > x + half_w:
                continue
            face = box[4] if sign < 0 else box[1]
            if abs(face - edge) <= 25.0:
                faces.append(face)
        if faces:
            face = max(faces) if sign < 0 else min(faces)
            y = face - sign * (half_d + 1.0)
        return x, y
    sign = -1.0 if back == "-x" else 1.0
    edge = x + sign * (math.ceil(depth / CELL - 0.01) * CELL / 2.0)
    faces = []
    for box in boxes:
        if box[5] < low or box[2] > high or box[4] < y - half_w or box[1] > y + half_w:
            continue
        face = box[3] if sign < 0 else box[0]
        if abs(face - edge) <= 25.0:
            faces.append(face)
    if faces:
        face = max(faces) if sign < 0 else min(faces)
        x = face - sign * (half_d + 1.0)
    return x, y


def _unit(code, x):
    half = "North" if x < wieland_levels.PARTY_X else "South"
    return half + ("Penthouse" if code in PENTHOUSE else "Triplex")


def plan_room(room, half, grid_data=None, keep=False):
    """Read-only. Where the pieces of one room would go: (blocks, left out). A block is a dict; a piece
    that is left out is (room, half, piece, reason). With keep, the planned blocks stay marked in the
    grid that was passed, so that the next room of an open plan keeps clear of them."""
    code, x, y = rooms(half)[room]
    room_type = ROOM_TYPES.get(room)
    if room_type is None:
        return [], [(room, half, "", "no furniture of volume is proposed for this kind of room")]
    level = STOREYS[code][1]
    grid, tops, wall_boxes, fixed_boxes, furniture = grid_data or storey_grid(code)
    if not keep:
        grid = [list(row) for row in grid]
    cells = region(grid, x, y)
    inside = _furniture_in(cells, furniture)
    planned, left = [], []
    others = [box for _, box in inside]
    pieces = [entry for name in room_type.split(" + ") for entry in PIECES[name]]
    # A coffee table and the loose chairs belong with the sofas, so they are looked for from the middle
    # of the sofas of the room (those of the Revit model, or the stand-in planned a moment ago).
    seats = [((box[0] + box[3]) / 2.0, (box[1] + box[4]) / 2.0) for label, box in inside
             if any(word in label.lower() for word in SEAT_WORDS)]
    for piece, item, width, depth, height, mode, count, words in pieces:
        present = [label for label, _ in inside if any(word in label.lower() for word in words)]
        if present:
            left.append((room, half, piece, "the Revit model already has %d such object(s) here, e.g. %s"
                         % (len(present), present[0])))
            continue
        windows = _window_grid(code, height)
        for number in range(1, count + 1):
            if mode == "parking":
                spaces = [box for label, category, box in parts() if category == "Parking"
                          and ((box[0] + box[3]) / 2.0 < wieland_levels.PARTY_X) == (half == "North")]
                if not spaces:
                    left.append((room, half, piece, "the Revit model draws no parking space in this half"))
                    continue
                box = spaces[0]
                px, py = (box[0] + box[3]) / 2.0, (box[1] + box[4]) / 2.0
                turned = 0 if box[3] - box[0] > box[4] - box[1] else 90
                i = min(NX - 1, max(0, int((px - X_MIN) / CELL)))
                j = min(NY - 1, max(0, int((py - Y_MIN) / CELL)))
                top = tops[i][j] if tops[i][j] is not None else box[5]
                unit = _unit(code, px)
                planned.append({"object": "%s%s_%s_%s_%d" % (LABEL, unit, room, piece, number), "unit": unit,
                                "floor": STOREYS[code][0], "room": room, "room_type": room_type,
                                "piece": "%s_%d" % (piece, number), "item": item, "width": width, "depth": depth,
                                "height": height, "x": px, "y": py, "z": top, "turned": turned,
                                "mode": "on the Revit parking space"})
                continue
            if mode == "set":
                chair = SETS[piece]
                span_w = width + (2.0 * (SET_CHAIR_OUT + chair[1] / 2.0) if chair[4] else 0.0)
                span_d = depth + 2.0 * (SET_CHAIR_OUT + chair[1] / 2.0)
            else:
                span_w, span_d = width, depth
            found = None
            stands = mode
            tries = {"set": ("free",), "wall or free": ("wall", "free")}.get(mode, (mode,))
            for attempt in tries:
                for front_clear, door_clear in CLEARANCES:
                    near = None
                    if seats and piece in WITH_SEATS:
                        near = (sum(a for a, _ in seats) / len(seats), sum(b for _, b in seats) / len(seats))
                    found = _find(code, grid, cells, windows, others, (x, y), span_w, span_d, attempt,
                                  front_clear, door_clear, near)
                    if found is not None:
                        break
                if found is not None:
                    stands = "set" if mode == "set" else attempt
                    break
            if found is None:
                left.append((room, half, "%s_%d" % (piece, number), "no place of %d x %d cm with the clearances"
                             % (round(span_w), round(span_d))))
                continue
            px, py, turned, back = found
            if piece in ("sofa", "sectional_sofa"):
                seats.append((px, py))
            px, py = _snap(px, py, turned, back, span_w, span_d,
                           wall_boxes if stands == "wall" else wall_boxes + fixed_boxes, level)
            i = min(NX - 1, max(0, int((px - X_MIN) / CELL)))
            j = min(NY - 1, max(0, int((py - Y_MIN) / CELL)))
            top = tops[i][j] if tops[i][j] is not None else level
            unit = _unit(code, px)
            made = []

            def add(name, w, d, h, bx, by):
                made.append({"object": "%s%s_%s_%s" % (LABEL, unit, room, name), "unit": unit,
                             "floor": STOREYS[code][0], "room": room, "room_type": room_type, "piece": name,
                             "item": item, "width": w, "depth": d, "height": h, "x": bx, "y": by, "z": top,
                             "turned": turned,
                             "mode": stands if back is None else "%s, back to %s" % (stands, back)})

            add("%s_%d" % (piece, number), width, depth, height, px, py)
            if mode == "set":
                spots = []
                for side in (-1.0, 1.0):
                    for step in range(chair[3]):
                        spots.append(((step - (chair[3] - 1) / 2.0) * SET_CHAIR_STEP,
                                      side * (depth / 2.0 + SET_CHAIR_OUT), False))
                    for _ in range(chair[4]):
                        spots.append((side * (width / 2.0 + SET_CHAIR_OUT), 0.0, True))
                for along, out, at_end in spots:
                    dx, dy = (along, out) if turned == 0 else (out, along)
                    # A chair at an end of the table is turned a quarter against the table.
                    w, d = (chair[1], chair[0]) if at_end else (chair[0], chair[1])
                    add("%s_%d_chair_%d" % (piece, number, len(made)), w, d, chair[2], px + dx, py + dy)
            planned.extend(made)
            half_x, half_y = (span_w / 2.0, span_d / 2.0) if turned == 0 else (span_d / 2.0, span_w / 2.0)
            box = (px - half_x, py - half_y, top, px + half_x, py + half_y, top + height)
            _mark(grid, box, PLACED)
            others.append(box)
    return planned, left


def plan_all(room_names=None, halves=("North", "South")):
    """plan_room() for every room of both halves. Returns (blocks, left out)."""
    planned, left = [], []
    grids = {}
    for half in halves:
        for room, (code, _, _) in sorted(rooms(half).items()):
            if room_names is not None and room not in room_names:
                continue
            if code not in grids:
                grids[code] = storey_grid(code)
            a, b = plan_room(room, half, grids[code], keep=True)
            planned.extend(a)
            left.extend(b)
    return planned, left


def material():
    """The one grey material of the stand-ins; made when missing."""
    if unreal.EditorAssetLibrary.does_asset_exist(MATERIAL):
        return unreal.EditorAssetLibrary.load_asset(MATERIAL)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    made = tools.create_asset(MATERIAL.split("/")[-1], MESH_FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    if made is None:
        raise RuntimeError("could not create %s" % MATERIAL)
    library = unreal.MaterialEditingLibrary
    colour = library.create_material_expression(made, unreal.MaterialExpressionConstant3Vector, -400, 0)
    colour.set_editor_property("constant", unreal.LinearColor(0.35, 0.35, 0.35, 1.0))
    library.connect_material_property(colour, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = library.create_material_expression(made, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", 0.8)
    library.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    library.recompile_material(made)
    unreal.EditorAssetLibrary.save_asset(MATERIAL, False)
    return made


def mesh_path(width, depth, height):
    return "%s/SM_W1529_PH_%dx%dx%d" % (MESH_FOLDER, round(width), round(depth), round(height))


def mesh(width, depth, height):
    """The block of one size: width along X, depth along Y, standing on its origin. Made when missing.
    Returns (mesh, sharp edges counted on it or None when it existed)."""
    path = mesh_path(width, depth, height)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path), None
    positions, triangles = wieland_trim._eased_box(
        (0.0, 0.0, height / 2.0), ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        (width / 2.0, depth / 2.0, height / 2.0), ease=EASE)
    uvs = []
    for a, b, c in triangles:
        triple = []
        for index in (a, b, c):
            p = positions[index]
            triple.append(((p[0] + p[1]) / 100.0, (p[2] + p[1]) / 100.0))
        uvs.append(tuple(triple))
    dynamic = wieland_refine._dynamic_from_arrays(positions, triangles, uvs, [0] * len(triangles))
    options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    options.set_editor_property("enable_recompute_normals", False)
    options.set_editor_property("enable_recompute_tangents", True)
    options.set_editor_property("enable_collision", False)
    options.set_editor_property("enable_nanite", False)
    result = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic, path, options)
    made, outcome = result if isinstance(result, tuple) else (result, unreal.GeometryScriptOutcomePins.SUCCESS)
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS or made is None:
        raise RuntimeError("could not create %s" % path)
    made.set_material(0, material())
    unreal.EditorAssetLibrary.save_asset(path, False)
    return made, len(wieland_refine.sharp_edges(positions, triangles))


def place(planned):
    """Make the planned blocks as new objects in the levels of their units. Does not save the levels;
    see wieland_levels.save_unit_level(). Returns a summary."""
    world = wieland_levels._world()
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    existing = set(actor.get_actor_label() for actor in blocks())
    made, sharp, new_meshes = 0, 0, 0
    for unit in sorted(set(block["unit"] for block in planned)):
        streaming = unreal.GameplayStatics.get_streaming_level(world, wieland_levels.level_path(unit))
        if streaming is None:
            raise RuntimeError("the level of %s is not loaded" % unit)
        unreal.EditorLevelUtils.make_level_current(streaming)
        for block in planned:
            if block["unit"] != unit:
                continue
            if block["object"] in existing:
                raise RuntimeError("refused: an object %s exists already" % block["object"])
            asset, edges = mesh(block["width"], block["depth"], block["height"])
            if edges is not None:
                new_meshes += 1
                sharp += edges
            actor = subsystem.spawn_actor_from_object(
                asset, unreal.Vector(block["x"], block["y"], block["z"]),
                unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(block["turned"])))
            where = wieland_levels._level_name(actor)
            if where != wieland_levels.level_path(unit).split("/")[-1]:
                subsystem.destroy_actor(actor)
                raise RuntimeError("the object went to %s, not to the level of %s" % (where, unit))
            actor.set_actor_label(block["object"])
            actor.set_folder_path(FOLDER)
            half = "North" if unit.startswith("North") else "South"
            actor.tags = [unreal.Name(TAG_PLACEHOLDER), unreal.Name(TAG_GENERATED),
                          unreal.Name("W1529.Unit." + unit), unreal.Name("W1529.Floor." + block["floor"]),
                          unreal.Name("W1529.Half." + half), unreal.Name("W1529.Room." + block["room"]),
                          unreal.Name("W1529.Item." + block["item"]),
                          unreal.Name("W1529.Stands." + block["mode"])]
            actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
            existing.add(block["object"])
            made += 1
    return {"blocks": made, "new_meshes": new_meshes, "sharp_edges_on_new_meshes": sharp}


def listing():
    """Read-only: one row per stand-in object in the level, read back from the level itself."""
    rows = []
    for actor in blocks():
        tags = [str(tag) for tag in actor.tags]

        def tag(prefix):
            for value in tags:
                if value.startswith(prefix):
                    return value[len(prefix):]
            return ""

        label = actor.get_actor_label()
        room = tag("W1529.Room.")
        unit = tag("W1529.Unit.")
        asset = actor.static_mesh_component.static_mesh
        size = asset.get_name().split("_")[-1].split("x") if asset is not None else ["", "", ""]
        location = actor.get_actor_location()
        head = "%s%s_%s_" % (LABEL, unit, room)
        rows.append([label, unit, tag("W1529.Floor."), room, ROOM_TYPES.get(room, ""),
                     label[len(head):] if label.startswith(head) else label, tag("W1529.Item."),
                     size[0], size[1], size[2], round(location.x, 1), round(location.y, 1), round(location.z, 1),
                     int(round(actor.get_actor_rotation().yaw)), tag("W1529.Stands."),
                     asset.get_path_name().split(".")[0] if asset is not None else "", NOTE])
    return sorted(rows)


def write_csv(csv_path):
    rows = listing()
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEAD)
        writer.writerows(rows)
    return len(rows)


def remove(labels=None):
    """Take stand-in objects out of the level again: all of them, or those with the given names."""
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in blocks():
        if labels is None or actor.get_actor_label() in labels:
            subsystem.destroy_actor(actor)
            removed += 1
    return removed
