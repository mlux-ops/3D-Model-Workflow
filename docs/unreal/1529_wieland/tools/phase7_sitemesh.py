"""Phase 7, step 7.2: the mesh files of the site ground (roadway, everything beside it, kerbs).

Reads   review/phase7/ground/cover.npz, shapes.json, kerb_lines.json, sources.npz   (phase7_groundcover.py)
        review/phase7/heights/combined.npz                                          (phase7_heights.py)
Writes  review/phase7/ground/mesh/SW_ground_<a>_<b>.json   everything that is not a street's roadway, 50 m pieces
        review/phase7/ground/mesh/SW_road_<a>_<b>.json     the streets' roadway, lower by the kerb height
        review/phase7/ground/mesh/SW_kerb.json             the kerb stones along the roadway
        review/phase7/ground/mesh_summary.json

The heights are those of the Phase 4 ground (2022 laser scan), read off its own meshes at 0.5 m, so the
buildings that were fitted to that ground in step 7.0 still meet it. The laser scan is too coarse to hold a
kerb, so the kerb is made here: the roadway lies KERB_CM lower than the ground beside it, and that drop
runs out to nothing over RAMP_CM towards an alley mouth, where an alley meets the roadway flush.
The lot of 1529 is left open, as in Phase 4: the house model has its own ground there.

Run from the plan folder:  python -B tools/phase7_sitemesh.py
Nothing in Unreal is touched.
"""

import json
import math
import os

import numpy as np
import shapely
from scipy import ndimage
from shapely import wkt
from shapely.geometry import LineString, MultiPoint, box

OUT = "review/phase7/ground"
CELL = 100.0             # cm: size of a ground cell
PIECE = 50               # cells per piece and side: 50 m
KERB_CM = 13.0           # height of the kerb face above the roadway
RAMP_CM = 150.0          # the kerb runs out over this length towards an alley mouth
RAMP_START_CM = 40.0
KERB_TOP_CM = 15.0       # width of the kerb stone seen from above
KERB_PROUD_CM = 1.5      # the kerb stone stands this far above the ground behind it
KERB_STEP_CM = 50.0
LOT_RECT = (-1508.76, 0.0, -3115.1, 0.0)   # x_min, x_max, y_min, y_max
NONE = -99999.0
HEIGHT_CELL = 50.0


def heights():
    data = np.load("review/phase7/heights/combined.npz")
    ground = data["ground_p4"].astype(np.float64)
    missing = ground < NONE / 2
    _, nearest = ndimage.distance_transform_edt(missing, return_indices=True)
    return ground[nearest[0], nearest[1]], int(data["i0"]), int(data["j0"])


def bilinear(field, u, v):
    u = np.clip(u, 0.0, field.shape[0] - 1.001)
    v = np.clip(v, 0.0, field.shape[1] - 1.001)
    a = np.floor(u).astype(int)
    b = np.floor(v).astype(int)
    fu = u - a
    fv = v - b
    return (field[a, b] * (1 - fu) * (1 - fv) + field[a + 1, b] * fu * (1 - fv)
            + field[a, b + 1] * (1 - fu) * fv + field[a + 1, b + 1] * fu * fv)


class Builder:
    """Collects the triangles of one mesh file; points that fall together are one point."""

    def __init__(self, name, kind, pivot):
        self.name, self.kind, self.pivot = name, kind, pivot
        self.index = {}
        self.vertices = []
        self.triangles = []

    def point(self, x, y, z):
        key = (round(x * 10), round(y * 10), round(z * 10))
        number = self.index.get(key)
        if number is None:
            number = len(self.vertices)
            self.index[key] = number
            self.vertices.append([round(x - self.pivot[0], 2), round(y - self.pivot[1], 2), round(z - self.pivot[2], 2)])
        return number

    def triangle(self, p, q, r, outward):
        """p, q, r: (x, y, z). The corner order is set so that the face looks along 'outward'."""
        normal = np.cross(np.subtract(q, p), np.subtract(r, p))
        if float(np.dot(normal, normal)) < 1e-4:
            return
        if float(np.dot(normal, outward)) > 0:      # the convention of build_surroundings.py
            q, r = r, q
        a, b, c = self.point(*p), self.point(*q), self.point(*r)
        if a != b and b != c and a != c:
            self.triangles.append([a, b, c])

    def write(self, folder):
        if not self.triangles:
            return 0
        with open(folder + "/" + self.name + ".json", "w", encoding="utf-8") as handle:
            json.dump({"name": self.name, "kind": self.kind, "pivot": self.pivot, "vertices": self.vertices,
                       "triangles": self.triangles}, handle)
        return len(self.triangles)


def main():
    cover = np.load(OUT + "/cover.npz")
    x0, y0, step = float(cover["x0"]), float(cover["y0"]), float(cover["step"])
    with open(OUT + "/shapes.json", encoding="utf-8") as handle:
        shapes = json.load(handle)
    roadway = wkt.loads(shapes["roadway"])
    inside = np.load(OUT + "/sources.npz")["inside"]
    edge = inside & ~ndimage.binary_erosion(inside)
    ii, jj = np.nonzero(edge)
    hull = MultiPoint(np.column_stack([x0 + (ii + 0.5) * step, y0 + (jj + 0.5) * step])).convex_hull.buffer(-10.0)
    domain = hull.difference(box(LOT_RECT[0], LOT_RECT[2], LOT_RECT[1], LOT_RECT[3]))
    road = roadway.intersection(domain)
    upper = domain.difference(roadway)
    shapely.prepare(road)
    shapely.prepare(upper)

    xa = math.floor(domain.bounds[0] / CELL) * CELL
    ya = math.floor(domain.bounds[1] / CELL) * CELL
    n_a = int(math.ceil((domain.bounds[2] - xa) / CELL))
    n_b = int(math.ceil((domain.bounds[3] - ya) / CELL))

    # Height and kerb drop at the corners of the cells; inside a cell both are read off its four corners,
    # so two pieces that meet along a cell's side meet without a gap.
    ground, i0, j0 = heights()
    cx = xa + np.arange(n_a + 1) * CELL
    cy = ya + np.arange(n_b + 1) * CELL
    gx, gy = np.meshgrid(cx, cy, indexing="ij")
    corner_z = bilinear(ground, gx / HEIGHT_CELL - 0.5 - i0, gy / HEIGHT_CELL - 0.5 - j0)
    away = ndimage.distance_transform_edt(~cover["flush"]) * step
    drop = KERB_CM * np.clip((away - RAMP_START_CM) / RAMP_CM, 0.0, 1.0)
    ci = np.clip(((gx - x0) / step).astype(int), 0, drop.shape[0] - 1)
    cj = np.clip(((gy - y0) / step).astype(int), 0, drop.shape[1] - 1)
    corner_drop = drop[ci, cj]

    def height(x, y):
        return float(bilinear(corner_z, np.float64((x - xa) / CELL), np.float64((y - ya) / CELL)))

    def kerb_drop(x, y):
        return float(bilinear(corner_drop, np.float64((x - xa) / CELL), np.float64((y - ya) / CELL)))

    aa, bb = np.meshgrid(np.arange(n_a), np.arange(n_b), indexing="ij")
    aa, bb = aa.ravel(), bb.ravel()
    boxes = shapely.box(xa + aa * CELL, ya + bb * CELL, xa + (aa + 1) * CELL, ya + (bb + 1) * CELL)
    whole_road = shapely.contains(road, boxes)
    whole_upper = shapely.contains(upper, boxes)
    part_road = shapely.intersects(road, boxes) & ~whole_road
    part_upper = shapely.intersects(upper, boxes) & ~whole_upper

    builders = {}

    def builder(kind, a, b):
        key = (kind, a // PIECE, b // PIECE)
        if key not in builders:
            pivot = [xa + key[1] * PIECE * CELL, ya + key[2] * PIECE * CELL, 0.0]
            builders[key] = Builder("SW_%s_%d_%d" % (kind, key[1], key[2]), kind, pivot)
        return builders[key]

    up = (0.0, 0.0, 1.0)

    def surface(kind, a, b, ring):
        target = builder(kind, a, b)
        lowered = kind == "road"
        points = [(x, y, height(x, y) - (kerb_drop(x, y) if lowered else 0.0)) for x, y in ring]
        target.triangle(points[0], points[1], points[2], up)

    for k in np.nonzero(whole_road | whole_upper)[0]:
        a, b = int(aa[k]), int(bb[k])
        kind = "road" if whole_road[k] else "ground"
        x1, y1, x2, y2 = xa + a * CELL, ya + b * CELL, xa + (a + 1) * CELL, ya + (b + 1) * CELL
        surface(kind, a, b, [(x1, y1), (x2, y1), (x2, y2)])
        surface(kind, a, b, [(x1, y1), (x2, y2), (x1, y2)])

    for kind, flags, shape in (("road", part_road, road), ("ground", part_upper, upper)):
        chosen = np.nonzero(flags)[0]
        pieces = shapely.intersection(boxes[chosen], shape)
        for k, piece in zip(chosen, pieces):
            a, b = int(aa[k]), int(bb[k])
            for polygon in getattr(piece, "geoms", [piece]):
                if polygon.geom_type != "Polygon" or polygon.area < 0.5:
                    continue
                for triangle in shapely.constrained_delaunay_triangles(polygon).geoms:
                    surface(kind, a, b, list(triangle.exterior.coords)[:3])

    # The step between the two: a wall along the roadway's edge, as high as the kerb drop there. It belongs to the
    # roadway's mesh; where there is a kerb stone the stone stands in front of it.
    wall = 0
    edge_line = roadway.boundary.intersection(domain.buffer(-1.0))
    chosen = np.nonzero(part_road)[0]
    runs = shapely.intersection(boxes[chosen], edge_line)
    for k, run in zip(chosen, runs):
        a, b = int(aa[k]), int(bb[k])
        target = builder("road", a, b)
        for line in getattr(run, "geoms", [run]):
            if line.geom_type != "LineString":
                continue
            coords = list(line.coords)
            for (px, py), (qx, qy) in zip(coords[:-1], coords[1:]):
                length = math.hypot(qx - px, qy - py)
                if length < 0.05:
                    continue
                dp, dq = kerb_drop(px, py), kerb_drop(qx, qy)
                if max(dp, dq) < 0.05:
                    continue
                side = ((qy - py) / length, -(qx - px) / length, 0.0)
                mx, my = (px + qx) / 2 + side[0] * 3.0, (py + qy) / 2 + side[1] * 3.0
                if not shapely.contains_xy(road, mx, my):
                    side = (-side[0], -side[1], 0.0)
                zp, zq = height(px, py), height(qx, qy)
                target.triangle((px, py, zp), (qx, qy, zq), (qx, qy, zq - dq), side)
                target.triangle((px, py, zp), (qx, qy, zq - dq), (px, py, zp - dp), side)
                wall += 2

    # The kerb stones: a top KERB_TOP_CM wide on the sidewalk side, standing KERB_PROUD_CM above the ground, a face
    # down to below the roadway, and a small back.
    with open(OUT + "/kerb_lines.json", encoding="utf-8") as handle:
        kerb_lines = json.load(handle)["lines"]
    kerb = Builder("SW_kerb", "kerb", [0.0, 0.0, 0.0])
    kerb_length = 0.0
    for coords in kerb_lines:
        line = LineString(coords).intersection(domain.buffer(-20.0))
        for part in getattr(line, "geoms", [line]):
            if part.geom_type != "LineString" or part.length < 100.0:
                continue
            kerb_length += part.length
            count = max(int(math.ceil(part.length / KERB_STEP_CM)), 1)
            stations = [part.interpolate(part.length * n / count) for n in range(count + 1)]
            xy = np.array([[p.x, p.y] for p in stations])
            along = np.gradient(xy, axis=0)
            along /= np.maximum(np.linalg.norm(along, axis=1, keepdims=True), 1e-9)
            side = np.column_stack([along[:, 1], -along[:, 0]])
            middle = len(xy) // 2
            if not shapely.contains_xy(road, xy[middle, 0] + side[middle, 0] * 20.0, xy[middle, 1] + side[middle, 1] * 20.0):
                side = -side
            rows = []
            for (x, y), (sx, sy) in zip(xy, side):
                top = height(x, y) + KERB_PROUD_CM
                foot = height(x, y) - kerb_drop(x, y) - 3.0
                back = (x - sx * (KERB_TOP_CM + 0.5), y - sy * (KERB_TOP_CM + 0.5))
                front = (x + sx * 0.5, y + sy * 0.5)
                rows.append(((back[0], back[1], top - 5.0), (back[0], back[1], top), (front[0], front[1], top),
                             (front[0], front[1], foot), (sx, sy)))
            for first, second in zip(rows[:-1], rows[1:]):
                sx, sy = first[4]
                for n, outward in ((0, (-sx, -sy, 0.0)), (1, up), (2, (sx, sy, 0.0))):
                    kerb.triangle(first[n], second[n], second[n + 1], outward)
                    kerb.triangle(first[n], second[n + 1], first[n + 1], outward)

    folder = OUT + "/mesh"
    os.makedirs(folder, exist_ok=True)
    for name in os.listdir(folder):
        os.remove(folder + "/" + name)
    counts = {"ground": 0, "road": 0, "kerb": 0}
    files = {"ground": 0, "road": 0, "kerb": 0}
    for target in list(builders.values()) + [kerb]:
        written = target.write(folder)
        if written:
            counts[target.kind] += written
            files[target.kind] += 1
    summary = {"cell_cm": CELL, "piece_m": PIECE * CELL / 100.0, "kerb_height_cm": KERB_CM, "kerb_ramp_cm": RAMP_CM,
               "kerb_stone_top_cm": KERB_TOP_CM, "kerb_stone_proud_cm": KERB_PROUD_CM,
               "area_m2": {"all": round(domain.area / 1e4), "roadway": round(road.area / 1e4), "beside the roadway": round(upper.area / 1e4)},
               "files": files, "triangles": counts, "kerb_wall_triangles": wall, "kerb_length_m": round(kerb_length / 100.0),
               "height_cm_lowest_and_highest": [round(float(corner_z.min()), 1), round(float(corner_z.max()), 1)]}
    with open(OUT + "/mesh_summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
