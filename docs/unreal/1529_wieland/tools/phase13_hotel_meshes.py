"""Phase 13: the meshes of the proposed hotel at 1520-1528 N. Wells, its rear garage and the three homes,
made from the numbers in proposed_hotel.md alone (numpy only, outside the editor).

Everything here is PROPOSED, modelled from published renderings and records, not a survey.

Frame used in this file: site feet (east, north, up). East and north are counted from the south-west corner of
the project lot; up is counted from the level's zero. The hotel's own numbers are a (feet east of sub-area A's
west line), b (feet south of sub-area A's north line) and z (feet above the hotel's first floor), exactly as in
proposed_hotel.md; E(), N() and H() turn them into site feet.

Output: one JSON file per group and material ({"name", "group", "material", "vertices" in level centimetres,
"triangles"}), and measures.json with the extents of every group in feet.

Usage: python -B tools/phase13_hotel_meshes.py <output folder>
"""
import json
import os
import sys

import numpy as np

CM = 30.48006096
A_WEST = 28.75        # sub-area A's west line, feet east of the Wieland line (PD)
A_NORTH = -24.75      # sub-area A's north line, feet north of the project lot's south line (PD)
FIRST_FLOOR = 1.0     # the hotel's first floor above the level's zero: the modelled Wells Street pavement

# Floor levels in feet above the first floor. Written in the PD: 1, 2, 3, 7, 9, 11, 12. The others: equal division.
F = {1: 0.0, 2: 17.0, 3: 32.33, 4: 42.42, 5: 52.50, 6: 62.58, 7: 72.67, 8: 83.17, 9: 93.67, 10: 104.17,
     11: 114.67, 12: 127.67}
PENTHOUSE = 142.0
TOP = 151.33

RED, DARK, STONE, CONCRETE, GREEN = "RedBrick", "DarkBrick", "Stone", "Concrete", "GreenRoof"
METAL, PANEL, GLASS, INTERIOR, BLIND = "Metal", "MetalPanel", "Glass", "Interior", "Blind"


def E(a):
    return A_WEST + a


def N(b):
    return A_NORTH - b


def H(z):
    return FIRST_FLOOR + z


class Builder:
    def __init__(self):
        self.parts = {}
        self.group = None
        self.random = np.random.default_rng(1335)

    # ---- the two primitives ---------------------------------------------------------------------------
    def quad(self, material, p0, p1, p2, p3, out):
        part = self.parts.setdefault((self.group, material), {"v": [], "t": [], "o": []})
        base = len(part["v"])
        part["v"] += [p0, p1, p2, p3]
        part["t"] += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
        part["o"] += [out, out]

    def box(self, material, e0, e1, n0, n1, z0, z1, skip=()):
        e0, e1 = min(e0, e1), max(e0, e1)
        n0, n1 = min(n0, n1), max(n0, n1)
        z0, z1 = min(z0, z1), max(z0, z1)
        if "e+" not in skip:
            self.quad(material, (e1, n0, z0), (e1, n1, z0), (e1, n1, z1), (e1, n0, z1), (1, 0, 0))
        if "e-" not in skip:
            self.quad(material, (e0, n0, z0), (e0, n1, z0), (e0, n1, z1), (e0, n0, z1), (-1, 0, 0))
        if "n+" not in skip:
            self.quad(material, (e0, n1, z0), (e1, n1, z0), (e1, n1, z1), (e0, n1, z1), (0, 1, 0))
        if "n-" not in skip:
            self.quad(material, (e0, n0, z0), (e1, n0, z0), (e1, n0, z1), (e0, n0, z1), (0, -1, 0))
        if "z+" not in skip:
            self.quad(material, (e0, n0, z1), (e1, n0, z1), (e1, n1, z1), (e0, n1, z1), (0, 0, 1))
        if "z-" not in skip:
            self.quad(material, (e0, n0, z0), (e1, n0, z0), (e1, n1, z0), (e0, n1, z0), (0, 0, -1))

    def flat(self, material, e0, e1, n0, n1, z):
        self.box(material, e0, e1, n0, n1, z, z, skip=("e+", "e-", "n+", "n-", "z-"))

    # ---- things given in the coordinates of a wall ------------------------------------------------------
    # A wall is a vertical plane: axis "E" means east = pos, running along north; axis "N" means north = pos,
    # running along east. sign +1: the wall faces east (or north); -1: west (or south). u runs along the wall
    # (north or east in site feet), d is the distance out of the wall (negative: into the building).
    @staticmethod
    def _pt(axis, pos, sign, u, d, z):
        return (pos + sign * d, u, z) if axis == "E" else (u, pos + sign * d, z)

    @staticmethod
    def _out(axis, sign):
        return (sign, 0, 0) if axis == "E" else (0, sign, 0)

    @staticmethod
    def _along(axis, direction):
        return (0, direction, 0) if axis == "E" else (direction, 0, 0)

    def wquad(self, material, axis, pos, sign, d, u0, u1, z0, z1):
        """A rectangle parallel to the wall at distance d, facing out."""
        p = lambda u, z: self._pt(axis, pos, sign, u, d, z)
        self.quad(material, p(u0, z0), p(u1, z0), p(u1, z1), p(u0, z1), self._out(axis, sign))

    def wbox(self, material, axis, pos, sign, u0, u1, d0, d1, z0, z1, back=False, bottom=True):
        """A box on the wall, from distance d0 to d1 (d1 further out). The face toward the building is left out."""
        d0, d1 = min(d0, d1), max(d0, d1)
        a = self._pt(axis, pos, sign, u0, d0, z0)
        c = self._pt(axis, pos, sign, u1, d1, z1)
        skip = []
        if not back:
            skip.append(("e-" if sign > 0 else "e+") if axis == "E" else ("n-" if sign > 0 else "n+"))
        if not bottom:
            skip.append("z-")
        self.box(material, a[0], c[0], a[1], c[1], a[2], c[2], skip=skip)

    def wall(self, material, axis, pos, sign, u0, u1, z0, z1, openings=(), bands=()):
        """A wall with rectangular openings, each filled according to its kind. bands: (top, material) pairs
        that replace the wall's material below `top`, lowest first."""
        u0, u1 = min(u0, u1), max(u0, u1)
        us, zs = {u0, u1}, {z0, z1}
        for o in openings:
            us.update(min(max(v, u0), u1) for v in (o["u0"], o["u1"]))
            zs.update(min(max(v, z0), z1) for v in (o["z0"], o["z1"]))
        for top, _ in bands:
            if z0 < top < z1:
                zs.add(top)
        us, zs = sorted(us), sorted(zs)
        for j in range(len(zs) - 1):
            zc = 0.5 * (zs[j] + zs[j + 1])
            if zs[j + 1] - zs[j] < 1e-6:
                continue
            chosen = material
            for top, band_material in bands:
                if zc < top:
                    chosen = band_material
                    break
            start = None
            for i in range(len(us) - 1):
                uc = 0.5 * (us[i] + us[i + 1])
                solid = not any(o["u0"] < uc < o["u1"] and o["z0"] < zc < o["z1"] for o in openings)
                if solid and start is None:
                    start = us[i]
                if not solid and start is not None:
                    self.wquad(chosen, axis, pos, sign, 0.0, start, us[i], zs[j], zs[j + 1])
                    start = None
            if start is not None:
                self.wquad(chosen, axis, pos, sign, 0.0, start, us[-1], zs[j], zs[j + 1])
        for o in openings:
            if o["z0"] >= z0 - 1e-6 and o["z1"] <= z1 + 1e-6:
                self.fill(material, axis, pos, sign, o)

    def _reveals(self, axis, pos, sign, o, depth, jamb, sill):
        """The four inner faces of an opening, from the wall's face back to `depth` behind it."""
        p = lambda u, d, z: self._pt(axis, pos, sign, u, d, z)
        u0, u1, z0, z1 = o["u0"], o["u1"], o["z0"], o["z1"]
        self.quad(jamb, p(u0, 0, z0), p(u0, -depth, z0), p(u0, -depth, z1), p(u0, 0, z1), self._along(axis, 1))
        self.quad(jamb, p(u1, 0, z0), p(u1, -depth, z0), p(u1, -depth, z1), p(u1, 0, z1), self._along(axis, -1))
        self.quad(jamb, p(u0, 0, z1), p(u1, 0, z1), p(u1, -depth, z1), p(u0, -depth, z1), (0, 0, -1))
        self.quad(sill, p(u0, 0, z0), p(u1, 0, z0), p(u1, -depth, z0), p(u0, -depth, z0), (0, 0, 1))

    def _room(self, axis, pos, sign, o, front, depth):
        """A dark box behind the glass, seen from outside: sides, floor, ceiling and back wall."""
        self._reveals(axis, pos, sign, {"u0": o["u0"], "u1": o["u1"], "z0": o["z0"], "z1": o["z1"]}, 0.0, INTERIOR, INTERIOR)
        p = lambda u, d, z: self._pt(axis, pos, sign, u, d, z)
        u0, u1, z0, z1 = o["u0"], o["u1"], o["z0"], o["z1"]
        back = front - depth
        self.quad(INTERIOR, p(u0, front, z0), p(u0, back, z0), p(u0, back, z1), p(u0, front, z1), self._along(axis, 1))
        self.quad(INTERIOR, p(u1, front, z0), p(u1, back, z0), p(u1, back, z1), p(u1, front, z1), self._along(axis, -1))
        self.quad(INTERIOR, p(u0, front, z1), p(u1, front, z1), p(u1, back, z1), p(u0, back, z1), (0, 0, -1))
        self.quad(INTERIOR, p(u0, front, z0), p(u1, front, z0), p(u1, back, z0), p(u0, back, z0), (0, 0, 1))
        self.wquad(INTERIOR, axis, pos, sign, back, u0, u1, z0, z1)

    def _glazing(self, axis, pos, sign, o, depth, frame, bar, columns, rows, heavy=()):
        """Frame, bars and glass of a window set `depth` behind the wall's face. heavy: column lines as wide as the frame."""
        u0, u1, z0, z1 = o["u0"], o["u1"], o["z0"], o["z1"]
        front, glass = -depth + 0.20, -depth + 0.08
        for a, c in ((u0, u0 + frame), (u1 - frame, u1)):
            self.wbox(METAL, axis, pos, sign, a, c, -depth, front, z0, z1)
        for a, c in ((z0, z0 + frame), (z1 - frame, z1)):
            self.wbox(METAL, axis, pos, sign, u0 + frame, u1 - frame, -depth, front, a, c)
        for index in range(1, columns):
            centre = u0 + (u1 - u0) * index / columns
            half = 0.5 * (frame if index in heavy else bar)
            self.wbox(METAL, axis, pos, sign, centre - half, centre + half, -depth, front - 0.06, z0 + frame, z1 - frame)
        for index in range(1, rows):
            centre = z0 + (z1 - z0) * index / rows
            self.wbox(METAL, axis, pos, sign, u0 + frame, u1 - frame, -depth, front - 0.08, centre - 0.5 * bar, centre + 0.5 * bar)
        self.wquad(GLASS, axis, pos, sign, glass, u0, u1, z0, z1)

    def fill(self, material, axis, pos, sign, o):
        kind = o["kind"]
        u0, u1, z0, z1 = o["u0"], o["u1"], o["z0"], o["z1"]
        width, height = u1 - u0, z1 - z0
        if kind == "window":
            depth = 0.67
            self._reveals(axis, pos, sign, o, depth, material, STONE)
            self.wbox(STONE, axis, pos, sign, u0 - 0.2, u1 + 0.2, -0.05, 0.15, z0 - 0.33, z0)
            columns = 4 if width > 6.0 else 2
            self._glazing(axis, pos, sign, o, depth, 0.17, 0.07, columns, max(2, int(round(height / 1.9))), heavy=(columns // 2,))
            self._room(axis, pos, sign, o, -depth, 2.5)
            if self.random.random() < 0.75:
                drop = height * self.random.uniform(0.12, 0.6)
                self.wquad(BLIND, axis, pos, sign, -depth - 0.25, u0, u1, z1 - drop, z1)
        elif kind == "store":
            depth = 0.67
            self._reveals(axis, pos, sign, o, depth, material, STONE)
            columns = max(2, int(round(width / 4.75)))
            self._glazing(axis, pos, sign, o, depth, 0.25, 0.17, columns, 1)
            self.wbox(METAL, axis, pos, sign, u0 + 0.25, u1 - 0.25, -depth, -depth + 0.14, z1 - 2.7, z1 - 2.5)
            self._room(axis, pos, sign, o, -depth, 5.0)
        elif kind == "panel":
            # a blind panel: recessed face brick of contrasting colour
            self._reveals(axis, pos, sign, o, 0.33, material, material)
            self.wquad(DARK, axis, pos, sign, -0.33, u0, u1, z0, z1)
        elif kind == "door":
            # a solid door or garage door of metal, set back
            depth = o.get("depth", 1.0)
            self._reveals(axis, pos, sign, o, depth, material, CONCRETE)
            self.wquad(o.get("leaf", PANEL), axis, pos, sign, -depth, u0, u1, z0, z1)
        else:
            raise ValueError(kind)

    def band(self, material, axis, pos, sign, u0, u1, z0, z1, out=0.25):
        self.wbox(material, axis, pos, sign, min(u0, u1), max(u0, u1), 0.0, out, z0, z1)

    def parapet(self, material, axis, pos, sign, u0, u1, z, height, thick=1.0):
        """A parapet flush with the wall below, `height` including its 0.25 ft stone coping."""
        u0, u1 = min(u0, u1), max(u0, u1)
        self.wbox(material, axis, pos, sign, u0, u1, -thick, 0.0, z, z + height - 0.25, back=True, bottom=False)
        self.wbox(STONE, axis, pos, sign, u0, u1, -thick - 0.08, 0.08, z + height - 0.25, z + height, back=True)

    def railing(self, axis, pos, sign, u0, u1, z, height, inset=0.5):
        """A painted metal railing with pickets, `inset` behind the wall's face."""
        u0, u1 = min(u0, u1), max(u0, u1)
        d0, d1 = -inset - 0.12, -inset
        self.wbox(METAL, axis, pos, sign, u0, u1, d0 - 0.04, d1 + 0.04, z + height - 0.12, z + height, back=True)
        self.wbox(METAL, axis, pos, sign, u0, u1, d0, d1, z + 0.25, z + 0.37, back=True)
        count = max(1, int(round((u1 - u0) / 5.0)))
        for index in range(count + 1):
            centre = u0 + 0.08 + (u1 - u0 - 0.16) * index / count
            self.wbox(METAL, axis, pos, sign, centre - 0.08, centre + 0.08, d0 - 0.02, d1 + 0.02, z, z + height - 0.12, back=True)
        pickets = int((u1 - u0) / 0.42)
        for index in range(1, pickets):
            centre = u0 + (u1 - u0) * index / pickets
            self.wbox(METAL, axis, pos, sign, centre - 0.03, centre + 0.03, d0 + 0.03, d1 - 0.03, z + 0.37, z + height - 0.12, back=True)

    def glass_guard(self, axis, pos, sign, u0, u1, z, height, inset=0.4):
        u0, u1 = min(u0, u1), max(u0, u1)
        self.wquad(GLASS, axis, pos, sign, -inset, u0, u1, z, z + height - 0.1)
        self.wbox(METAL, axis, pos, sign, u0, u1, -inset - 0.08, -inset + 0.08, z + height - 0.1, z + height, back=True)
        self.wbox(METAL, axis, pos, sign, u0, u1, -inset - 0.06, -inset + 0.06, z, z + 0.25, back=True)

    # ---- output -------------------------------------------------------------------------------------------
    def write(self, folder):
        os.makedirs(folder, exist_ok=True)
        for name in os.listdir(folder):
            if name.endswith(".json"):
                os.remove(os.path.join(folder, name))
        measures = {}
        for (group, material), part in sorted(self.parts.items()):
            feet = np.array(part["v"], dtype=np.float64)
            vertices = np.stack([-feet[:, 1] * CM, -feet[:, 0] * CM, feet[:, 2] * CM], axis=1)
            triangles = np.array(part["t"], dtype=np.int64)
            out = np.array(part["o"], dtype=np.float64)
            out = np.stack([-out[:, 1], -out[:, 0], out[:, 2]], axis=1)
            normal = np.cross(vertices[triangles[:, 1]] - vertices[triangles[:, 0]], vertices[triangles[:, 2]] - vertices[triangles[:, 0]])
            # Unreal shows the face of a triangle on the side its corners run clockwise (tools/build_surroundings.py, wind)
            flip = np.einsum("ij,ij->i", normal, out) > 0
            triangles[flip] = triangles[flip][:, [0, 2, 1]]
            name = "SM_W1529_PH_%s_%s" % (group, material)
            with open(os.path.join(folder, name + ".json"), "w", encoding="utf-8") as handle:
                json.dump({"name": name, "group": group, "material": material, "pivot": [0.0, 0.0, 0.0],
                           "vertices": np.round(vertices, 3).tolist(), "triangles": triangles.tolist()}, handle)
            record = measures.setdefault(group, {"triangles": 0, "east": [1e9, -1e9], "north": [1e9, -1e9], "up": [1e9, -1e9], "materials": {}})
            record["triangles"] += len(triangles)
            record["materials"][material] = len(triangles)
            for key, column in (("east", 0), ("north", 1), ("up", 2)):
                record[key] = [round(min(record[key][0], feet[:, column].min()), 3), round(max(record[key][1], feet[:, column].max()), 3)]
        with open(os.path.join(folder, "measures.json"), "w", encoding="utf-8") as handle:
            json.dump(measures, handle, indent=1)
        return measures


# ---- openings ---------------------------------------------------------------------------------------------
def window(u, floor, width=7.5):
    """The standard hotel window of a floor, centred on u (site feet along the wall)."""
    if floor == 2:
        z0, z1 = F[2] + 2.0, F[2] + 12.5
    elif floor == 11:
        z0, z1 = F[11] + 1.5, F[11] + 10.5
    else:
        z0, z1 = F[floor] + 1.5, F[floor] + 9.0
    return {"kind": "window", "u0": u - width / 2, "u1": u + width / 2, "z0": H(z0), "z1": H(z1)}


def small_window(u, floor):
    return {"kind": "window", "u0": u - 2.0, "u1": u + 2.0, "z0": H(F[floor] + 3.5), "z1": H(F[floor] + 8.5)}


def panel(u, floor, width=7.5):
    return {"kind": "panel", "u0": u - width / 2, "u1": u + width / 2, "z0": H(F[floor] + 1.5), "z1": H(F[floor] + 9.0)}


def columns(centres, floors, make=window):
    return [make(u, floor) for floor in floors for u in centres]


# Window columns of the Wells Street front, feet south of sub-area A's north line (flat elevation, scaled)
B_NORTH_WING = (33.3, 20.6, 8.0)
B_RECESS = (61.2, 48.2)
B_DARK = (75.7,)
B_SOUTH_WING = (91.5, 104.1, 116.8)
A_TOWER = tuple(57.3 + 13.85 * k for k in range(7))      # north and south faces of the tower: seven columns
A_WING = (156.5, 168.5)
WEST_BAY = (42.9, 80.9)                                   # the dark middle bay of the west face, b from..to
WEST_BACK = 2.0                                           # how far that bay is set back
T_W, T_E, T_N, T_S = 48.4, 149.3, 12.0, 112.4             # the tower, floors 3 to 11 (a, a, b, b)
FRONT = 175.75                                            # the Wells Street face (a)
WING_N, WING_S = 41.0, 84.5                               # the wings' inner faces (b)
D_E, D_N = 158.3, 68.3                                    # the dark grey projecting part (a east face, b north face)
LOT_S = 124.8


def hotel_base(m):
    """Floors 1 and 2: the lowest storeys, built and looked at first."""
    m.group = "Base"
    low, top = H(-3.0), H(F[3])
    stone_base = [(H(2.0), STONE)]
    # north and south walls on the lot lines: blank face brick
    m.wall(RED, "N", N(0), 1, E(T_W), E(FRONT), low, top)
    m.wall(RED, "N", N(LOT_S), -1, E(T_W), E(FRONT), low, top)
    # Wells Street front, north wing: three shopfronts, three windows above
    shop = lambda b, width=9.5: {"kind": "store", "u0": N(b) - width / 2, "u1": N(b) + width / 2, "z0": H(2.0), "z1": H(13.5)}
    m.wall(RED, "E", E(FRONT), 1, N(WING_N), N(0), low, top, bands=stone_base,
           openings=[shop(b) for b in B_NORTH_WING] + columns([N(b) for b in B_NORTH_WING], [2]))
    # south wing: the garage entrance at the south end, two shopfronts, three windows above
    garage = {"kind": "door", "u0": N(122.3), "u1": N(111.3), "z0": H(0.1), "z1": H(11.5), "depth": 1.5}
    m.wall(RED, "E", E(FRONT), 1, N(LOT_S), N(WING_S), low, top, bands=stone_base,
           openings=[garage] + [shop(b) for b in B_SOUTH_WING[:2]] + columns([N(b) for b in B_SOUTH_WING], [2]))
    # the middle: one storey with the glazed entrance under a metal canopy
    entrance = {"kind": "store", "u0": N(81.5), "u1": N(44.0), "z0": H(0.3), "z1": H(12.0)}
    m.wall(PANEL, "E", E(FRONT), 1, N(WING_S), N(WING_N), low, H(F[2]), openings=[entrance])
    m.box(METAL, E(FRONT), E(FRONT + 6.0), N(80.0), N(45.5), H(12.6), H(13.4))
    m.flat(CONCRETE, E(T_E), E(FRONT), N(WING_S), N(WING_N), H(F[2]))
    m.parapet(PANEL, "E", E(FRONT), 1, N(WING_S), N(WING_N), H(F[2]), 1.0)
    m.railing("E", E(FRONT), 1, N(WING_S), N(WING_N), H(F[2]) + 1.0, 2.5)
    # second floor behind the terrace: the tower's east face, the dark part, and the wings' inner faces
    m.wall(RED, "E", E(T_E), 1, N(D_N), N(WING_N), H(F[2]), top, openings=columns([N(b) for b in B_RECESS], [2]))
    m.wall(DARK, "E", E(D_E), 1, N(WING_S), N(D_N), H(F[2]), top, openings=columns([N(b) for b in B_DARK], [2]))
    m.wall(DARK, "N", N(D_N), 1, E(T_E), E(D_E), H(F[2]), top)
    m.wall(RED, "N", N(WING_N), -1, E(T_E), E(FRONT), H(F[2]), top, openings=columns([E(a) for a in A_WING], [2]))
    m.wall(RED, "N", N(WING_S), 1, E(D_E), E(FRONT), H(F[2]), top, openings=columns([E(167.0)], [2]))
    # stone band at the third floor level, on the street front and round into the recess
    z0, z1 = H(F[3] - 0.9), H(F[3] + 0.6)
    m.band(STONE, "E", E(FRONT), 1, N(WING_N), N(0), z0, z1)
    m.band(STONE, "E", E(FRONT), 1, N(LOT_S), N(WING_S), z0, z1)
    m.band(STONE, "N", N(WING_N), -1, E(T_E), E(FRONT), z0, z1)
    m.band(STONE, "N", N(WING_S), 1, E(D_E), E(FRONT), z0, z1)


def hotel_tower(m):
    """Floors 3 to 11: the tower, the two wings on Wells Street, the dark grey part, and their terraces."""
    m.group = "Tower"
    base, top = H(F[3]), H(F[12])
    floors = list(range(3, 12))
    # tower north and south faces: seven window columns
    m.wall(RED, "N", N(T_N), 1, E(T_W), E(T_E), base, top, openings=columns([E(a) for a in A_TOWER], floors))
    m.wall(RED, "N", N(T_S), -1, E(T_W), E(T_E), base, top, openings=columns([E(a) for a in A_TOWER], floors))
    # tower west face: red side bays (a column of small windows and a column of recessed dark panels each),
    # and the dark grey middle bay set back, with three window columns
    m.wall(RED, "E", E(T_W), -1, N(WEST_BAY[0]), N(T_N), base, top,
           openings=columns([N(20.0)], floors, small_window) + columns([N(33.0)], floors, panel))
    m.wall(RED, "E", E(T_W), -1, N(T_S), N(WEST_BAY[1]), base, top,
           openings=columns([N(104.4)], floors, small_window) + columns([N(91.0)], floors, panel))
    m.wall(DARK, "E", E(T_W + WEST_BACK), -1, N(WEST_BAY[1]), N(WEST_BAY[0]), base, top,
           openings=columns([N(49.2), N(61.9), N(74.6)], floors))
    m.wall(DARK, "N", N(WEST_BAY[0]), -1, E(T_W), E(T_W + WEST_BACK), base, top)
    m.wall(DARK, "N", N(WEST_BAY[1]), 1, E(T_W), E(T_W + WEST_BACK), base, top)
    # tower east face, where it shows: in the recess, above the north wing, above the dark part
    m.wall(RED, "E", E(T_E), 1, N(D_N), N(WING_N), base, top, openings=columns([N(b) for b in B_RECESS], floors))
    m.wall(RED, "E", E(T_E), 1, N(WING_N), N(T_N), H(F[9]), top, openings=columns([N(b) for b in B_NORTH_WING[:2]], [9, 10, 11]))
    m.wall(RED, "E", E(T_E), 1, N(T_S), N(D_N), H(F[11]), top, openings=columns([N(b) for b in B_DARK + B_SOUTH_WING[:2]], [11]))
    # north wing on Wells Street, up to the 9th floor terrace
    wing_top = H(F[9])
    m.wall(RED, "E", E(FRONT), 1, N(WING_N), N(0), base, wing_top, openings=columns([N(b) for b in B_NORTH_WING], range(3, 9)))
    m.wall(RED, "N", N(0), 1, E(T_E), E(FRONT), base, wing_top, openings=columns([E(a) for a in A_WING], range(3, 9), panel))
    m.wall(RED, "N", N(WING_N), -1, E(T_E), E(FRONT), base, wing_top, openings=columns([E(a) for a in A_WING], range(3, 9)))
    m.wall(RED, "E", E(T_E), -1, N(T_N), N(0), base, wing_top)
    m.flat(CONCRETE, E(T_E), E(FRONT), N(WING_N), N(0), wing_top)
    for axis, pos, sign, u0, u1 in (("E", E(FRONT), 1, N(WING_N), N(0)), ("N", N(0), 1, E(T_E), E(FRONT)),
                                    ("N", N(WING_N), -1, E(T_E), E(FRONT)), ("E", E(T_E), -1, N(T_N), N(0))):
        m.parapet(RED, axis, pos, sign, u0, u1, wing_top, 1.25)
        m.railing(axis, pos, sign, u0, u1, wing_top + 1.25, 2.5)
    # south wing, up to the 7th floor terrace
    wing_top = H(F[7])
    m.wall(RED, "E", E(FRONT), 1, N(LOT_S), N(WING_S), base, wing_top, openings=columns([N(b) for b in B_SOUTH_WING], range(3, 7)))
    m.wall(RED, "N", N(LOT_S), -1, E(T_E), E(FRONT), base, wing_top, openings=columns([E(a) for a in A_WING], range(3, 7), panel))
    m.wall(RED, "N", N(WING_S), 1, E(D_E), E(FRONT), base, wing_top, openings=columns([E(167.0)], range(3, 7)))
    m.wall(RED, "E", E(T_E), -1, N(LOT_S), N(T_S), base, wing_top)
    m.flat(CONCRETE, E(T_E), E(FRONT), N(LOT_S), N(WING_S), wing_top)
    for axis, pos, sign, u0, u1 in (("E", E(FRONT), 1, N(LOT_S), N(WING_S)), ("N", N(LOT_S), -1, E(T_E), E(FRONT)),
                                    ("N", N(WING_S), 1, E(D_E), E(FRONT)), ("E", E(T_E), -1, N(LOT_S), N(T_S))):
        m.parapet(RED, axis, pos, sign, u0, u1, wing_top, 1.25)
        m.railing(axis, pos, sign, u0, u1, wing_top + 1.25, 2.5)
    # the dark grey projecting part, up to the 11th floor terrace
    dark_top = H(F[11])
    m.wall(DARK, "E", E(D_E), 1, N(WING_S), N(D_N), base, dark_top, openings=columns([N(b) for b in B_DARK], range(3, 11)))
    m.wall(DARK, "E", E(D_E), 1, N(T_S), N(WING_S), wing_top, dark_top, openings=columns([N(b) for b in B_SOUTH_WING[:2]], range(7, 11)))
    m.wall(DARK, "N", N(D_N), 1, E(T_E), E(D_E), base, dark_top)
    m.wall(DARK, "N", N(T_S), -1, E(T_E), E(D_E), wing_top, dark_top)
    m.flat(CONCRETE, E(T_E), E(D_E), N(T_S), N(D_N), dark_top)
    for axis, pos, sign, u0, u1 in (("E", E(D_E), 1, N(T_S), N(D_N)), ("N", N(D_N), 1, E(T_E), E(D_E)), ("N", N(T_S), -1, E(T_E), E(D_E))):
        m.parapet(DARK, axis, pos, sign, u0, u1, dark_top, 1.25)
        m.railing(axis, pos, sign, u0, u1, dark_top + 1.25, 2.5)
    # third floor terraces north and south of the tower, on the base
    m.flat(CONCRETE, E(T_W), E(T_E), N(T_N), N(0), base)
    m.flat(CONCRETE, E(T_W), E(T_E), N(LOT_S), N(T_S), base)
    m.parapet(RED, "N", N(0), 1, E(T_W), E(T_E), base, 3.5)
    m.parapet(RED, "N", N(LOT_S), -1, E(T_W), E(T_E), base, 3.5)
    # light stone band under the 12th floor terrace
    z0, z1 = top - 1.3, top + 0.5
    m.band(STONE, "N", N(T_N), 1, E(T_W) - 0.4, E(T_E) + 0.4, z0, z1, out=0.4)
    m.band(STONE, "N", N(T_S), -1, E(T_W) - 0.4, E(T_E) + 0.4, z0, z1, out=0.4)
    m.band(STONE, "E", E(T_E), 1, N(T_S), N(T_N), z0, z1, out=0.4)
    m.band(STONE, "E", E(T_W), -1, N(WEST_BAY[0]), N(T_N), z0, z1, out=0.4)
    m.band(STONE, "E", E(T_W), -1, N(T_S), N(WEST_BAY[1]), z0, z1, out=0.4)
    m.band(STONE, "E", E(T_W + WEST_BACK), -1, N(WEST_BAY[1]), N(WEST_BAY[0]), z0, z1, out=0.4)


def hotel_top(m):
    """The 12th floor with its terrace, the mechanical penthouse and the pergola."""
    m.group = "Top"
    deck = H(F[12])
    m.flat(CONCRETE, E(T_W + WEST_BACK), E(T_E), N(T_S), N(T_N), deck + 0.5)
    m.flat(CONCRETE, E(T_W), E(T_W + WEST_BACK), N(WEST_BAY[0]), N(T_N), deck + 0.5)
    m.flat(CONCRETE, E(T_W), E(T_W + WEST_BACK), N(T_S), N(WEST_BAY[1]), deck + 0.5)
    guard = deck + 0.5
    m.glass_guard("N", N(T_N), 1, E(T_W), E(T_E), guard, 3.5)
    m.glass_guard("N", N(T_S), -1, E(T_W), E(T_E), guard, 3.5)
    m.glass_guard("E", E(T_E), 1, N(T_S), N(T_N), guard, 3.5)
    m.glass_guard("E", E(T_W), -1, N(WEST_BAY[0]), N(T_N), guard, 3.5)
    m.glass_guard("E", E(T_W), -1, N(T_S), N(WEST_BAY[1]), guard, 3.5)
    m.glass_guard("E", E(T_W + WEST_BACK), -1, N(WEST_BAY[1]), N(WEST_BAY[0]), guard, 3.5)
    # the 12th floor: dark grey brick; main part and a leg to the south
    w, e, n, s, leg_e, leg_s = 64.0, 132.5, 24.6, 88.5, 100.0, 103.8
    roof = H(PENTHOUSE)
    low = deck + 0.5
    tall = lambda u, width=8.0: {"kind": "window", "u0": u - width / 2, "u1": u + width / 2, "z0": low + 0.3, "z1": low + 9.8}
    plain = lambda u: {"kind": "window", "u0": u - 3.75, "u1": u + 3.75, "z0": low + 2.5, "z1": low + 10.0}
    m.wall(DARK, "E", E(e), 1, N(s), N(n), low, roof, openings=[tall(N(b)) for b in (32.6, 48.6, 64.5, 80.5)])
    m.wall(DARK, "N", N(n), 1, E(w), E(e), low, roof, openings=[plain(E(a)) for a in (75.0, 90.0, 105.0, 120.0)])
    m.wall(DARK, "N", N(s), -1, E(leg_e), E(e), low, roof, openings=[plain(E(a)) for a in (108.5, 123.0)])
    m.wall(DARK, "E", E(leg_e), 1, N(leg_s), N(s), low, roof, openings=[plain(N(96.2))])
    m.wall(DARK, "N", N(leg_s), -1, E(w), E(leg_e), low, roof, openings=[plain(E(a)) for a in (73.5, 90.0)])
    m.wall(DARK, "E", E(w), -1, N(leg_s), N(n), low, roof, openings=[plain(N(b)) for b in (35.0, 50.0, 65.0, 80.0, 95.0)])
    m.flat(GREEN, E(w), E(e), N(s), N(n), roof)
    m.flat(GREEN, E(w), E(leg_e), N(leg_s), N(s), roof)
    for axis, pos, sign, u0, u1 in (("E", E(e), 1, N(s), N(n)), ("N", N(n), 1, E(w), E(e)), ("N", N(s), -1, E(leg_e), E(e)),
                                    ("E", E(leg_e), 1, N(leg_s), N(s)), ("N", N(leg_s), -1, E(w), E(leg_e)), ("E", E(w), -1, N(leg_s), N(n))):
        m.parapet(DARK, axis, pos, sign, u0, u1, roof, 1.5)
    # mechanical penthouse: metal panel; its roof is the top of the building, 151 ft 4 in above the first floor
    mw, me, mn, ms = 66.0, 114.2, 42.6, 82.5
    m.box(PANEL, E(mw), E(me), N(ms), N(mn), roof, H(TOP), skip=("z-",))
    # steel pergola on the terrace east of the 12th floor
    p_w, p_e, p_n, p_s, p_top = 133.5, 146.5, 30.0, 82.0, deck + 0.5 + 9.5
    for a in (p_e - 0.5,):
        for b in (p_n, 0.5 * (p_n + p_s) - 0.25, p_s - 0.5):
            m.box(METAL, E(a), E(a + 0.5), N(b + 0.5), N(b), deck + 0.5, p_top - 0.67)
    m.box(METAL, E(p_e - 0.5), E(p_e), N(p_s), N(p_n), p_top - 0.67, p_top)
    m.box(METAL, E(e), E(e + 0.5), N(p_s), N(p_n), p_top - 0.67, p_top)
    count = int(round((p_s - p_n) / 2.6))
    for index in range(count + 1):
        b = p_n + (p_s - p_n - 0.25) * index / count
        m.box(METAL, E(e), E(p_e + 1.0), N(b + 0.25), N(b), p_top, p_top + 0.5)


def garage(m):
    """The three-storey parking garage behind the tower, with its planted roof."""
    m.group = "Garage"
    low, roof = -3.0, H(F[3])
    m.wall(RED, "N", N(0), 1, E(0), E(T_W), low, roof)
    m.wall(RED, "N", N(LOT_S), -1, E(0), E(T_W), low, roof)
    # west wall: behind the homes; between them the two driveways lead in, with small windows above
    doors = [{"kind": "door", "u0": N(61.9), "u1": N(51.9), "z0": -0.5, "z1": 8.5},
             {"kind": "door", "u0": N(72.6), "u1": N(62.6), "z0": -0.5, "z1": 8.5}]
    lights = [{"kind": "window", "u0": N(b) - 1.5, "u1": N(b) + 1.5, "z0": z, "z1": z + 3.0}
              for b in (56.9, 67.6) for z in (13.0, 22.5)]
    m.wall(CONCRETE, "E", E(0), -1, N(LOT_S), N(0), low, roof, openings=doors + lights)
    m.flat(GREEN, E(0), E(T_W), N(LOT_S), N(0), roof)
    m.parapet(RED, "N", N(0), 1, E(0), E(T_W), roof, 3.5)
    m.parapet(RED, "N", N(LOT_S), -1, E(0), E(T_W), roof, 3.5)
    m.parapet(CONCRETE, "E", E(0), -1, N(LOT_S), N(0), roof, 3.5)


def home(m, name, material, e0, e1, n0, n1, roof, band_material=None):
    """Homes 1 and 2: three storeys, five window columns to Wieland Street, the door in the middle."""
    m.group = name
    low, floors = -2.0, (1.5, 13.0, 24.5)
    step = (n1 - n0 - 11.3) / 4.0
    centres = [n0 + 5.65 + step * k for k in range(5)]
    front = []
    for index, level in enumerate(floors):
        for k, u in enumerate(centres):
            if index == 0 and k == 2:
                front.append({"kind": "door", "u0": u - 2.0, "u1": u + 2.0, "z0": level, "z1": level + 8.5, "depth": 0.6, "leaf": METAL})
            else:
                front.append({"kind": "window", "u0": u - 2.25, "u1": u + 2.25, "z0": level + 2.0, "z1": level + 9.0})
    m.wall(material, "E", e0, -1, n0, n1, low, roof, openings=front)
    m.box(STONE, e0 - 4.0, e0, centres[2] - 3.0, centres[2] + 3.0, low, floors[0])            # the stoop
    side = [{"kind": "window", "u0": u - 1.75, "u1": u + 1.75, "z0": level + 2.0, "z1": level + 9.0}
            for level in floors for u in (e0 + 6.0, e0 + 15.0)]
    # the sides that face the driveways have windows; the sides close to a lot line or to Home 3 are blank
    m.wall(material, "N", n1, 1, e0, e1, low, roof, openings=side if name == "Home1" else ())
    m.wall(material, "N", n0, -1, e0, e1, low, roof, openings=side if name == "Home2" else ())
    m.wall(material, "E", e1, 1, n0, n1, low, roof)
    m.flat(CONCRETE, e0, e1, n0, n1, roof)
    for axis, pos, sign, u0, u1 in (("E", e0, -1, n0, n1), ("E", e1, 1, n0, n1), ("N", n1, 1, e0, e1), ("N", n0, -1, e0, e1)):
        m.parapet(material, axis, pos, sign, u0, u1, roof, 3.5)
    if band_material:
        for level in floors[1:]:
            m.band(band_material, "E", e0, -1, n0, n1, level - 0.9, level - 0.1, out=0.12)


def home3(m):
    """Home 3 on Lot 3 (1525 N. Wieland): a narrow red brick front with a garage door, long sides."""
    m.group = "Home3"
    e0, e1, n0, n1 = 2.6, 59.8, -22.3, -1.7
    low, roof, floors = -2.0, 34.25, (1.0, 12.5, 23.5)
    front = [{"kind": "door", "u0": -20.8, "u1": -11.8, "z0": 0.0, "z1": 8.5},
             {"kind": "door", "u0": -8.0, "u1": -4.3, "z0": 1.0, "z1": 9.5, "depth": 0.6, "leaf": METAL}]
    for level in floors[1:]:
        front += [{"kind": "window", "u0": u - 2.25, "u1": u + 2.25, "z0": level + 2.0, "z1": level + 9.0} for u in (-17.0, -7.0)]
    m.wall(RED, "E", e0, -1, n0, n1, low, roof, openings=front)
    m.box(STONE, e0 - 2.6, e0, -8.5, -3.8, low, 1.0)
    rear = [{"kind": "window", "u0": u - 2.25, "u1": u + 2.25, "z0": level + 2.0, "z1": level + 9.0} for level in floors for u in (-17.0, -7.0)]
    m.wall(RED, "E", e1, 1, n0, n1, low, roof, openings=rear)
    south = [{"kind": "window", "u0": u - 1.75, "u1": u + 1.75, "z0": level + 2.0, "z1": level + 9.0} for level in floors[1:] for u in (10.0, 20.0)]
    m.wall(RED, "N", n0, -1, e0, e1, low, roof, openings=south)
    m.wall(RED, "N", n1, 1, e0, e1, low, roof)          # blank: 1.7 ft from the project lot's south line
    m.flat(CONCRETE, e0, e1, n0, n1, roof)
    for axis, pos, sign, u0, u1 in (("E", e0, -1, n0, n1), ("E", e1, 1, n0, n1), ("N", n1, 1, e0, e1), ("N", n0, -1, e0, e1)):
        m.parapet(RED, axis, pos, sign, u0, u1, roof, 3.75)
    for level in floors[1:]:
        m.band(STONE, "E", e0, -1, n0, n1, level - 0.9, level - 0.1, out=0.12)


def main():
    folder = sys.argv[1]
    m = Builder()
    hotel_base(m)
    hotel_tower(m)
    hotel_top(m)
    garage(m)
    home(m, "Home1", STONE, 5.5, 27.3, -146.15, -97.65, 36.5)
    home(m, "Home2", DARK, 5.5, 27.3, -76.35, -27.15, 36.5, band_material=STONE)
    home3(m)
    measures = m.write(folder)
    for group, record in measures.items():
        print(group, record["triangles"], "triangles; east", record["east"], "north", record["north"], "up", record["up"])
    print("hotel top above its first floor: %.2f ft" % (measures["Top"]["up"][1] - FIRST_FLOOR))


if __name__ == "__main__":
    main()
