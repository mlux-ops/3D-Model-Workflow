"""Phase 4: make the meshes of the surroundings from the 2022 map data, in the level frame.

Usage:
    python build_surroundings.py <site data folder> <phase 2 results folder> <out folder> <manifest .json>

Writes one JSON file per object into <out folder> (outside the repository: the
shapes derive from the county's footprints), each holding a name, a pivot in
level coordinates (cm), vertices relative to the pivot and triangles. The
editor-side tool wieland_surroundings.py turns each file into a static mesh
and a placed object. A manifest of what was made, with each building's
measured heights, goes to <manifest .json> inside the repository.

Buildings: one object per 2022 footprint. Walls follow the footprint from the
ground to the roof; the roof is the 2022 top surface inside the footprint,
smoothed over 3 ft and capped at its 97th percentile so that tree crowns
hanging over a roof do not become spikes. The two houses that stood on the
lot in 2022 are left out; so is any footprint that the data square cuts.

Ground: the 2022 bare-ground surface as tiles of 164 ft (50 m): the four
tiles around the lot at 1 ft cells, the rest at 4 ft. The lot itself is cut
out, because the building brings its own ground, ramps and patios.

Triangles are wound for Unreal: a face is seen from the side from which its
corners run clockwise.

Needs NumPy, SciPy, Shapely and Pillow.
"""

import json
import math
import os
import sys

import numpy as np
from scipy import ndimage
from scipy.spatial import Delaunay, cKDTree
from shapely.geometry import Point, Polygon, box
from shapely.prepared import prep

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_analysis  # noqa: E402
import wieland_geo  # noqa: E402

FT_CM = wieland_geo.CM_PER_US_SURVEY_FOOT
LOT_X = (-1508.76, 0.0)
LOT_Y = (-3115.06, 0.0)
ROOF_STEP_CM = 100.0
TILE_FT = 164
ZONE_1_CM = 4000.0


class Frame:
    def __init__(self, frame, raster):
        self.f = frame
        self.r = raster
        self.t = math.radians(frame.north_grid_bearing_deg)

    def level_from_map(self, east, north):
        d_e = np.asarray(east) - self.f.origin_east_ft
        d_n = np.asarray(north) - self.f.origin_north_ft
        along_n = d_e * math.sin(self.t) + d_n * math.cos(self.t)
        along_e = d_e * math.cos(self.t) - d_n * math.sin(self.t)
        return -along_n * FT_CM, -along_e * FT_CM

    def map_from_level(self, x, y):
        along_n = -np.asarray(x) / FT_CM
        along_e = -np.asarray(y) / FT_CM
        east = self.f.origin_east_ft + along_n * math.sin(self.t) + along_e * math.cos(self.t)
        north = self.f.origin_north_ft + along_n * math.cos(self.t) - along_e * math.sin(self.t)
        return east, north

    def cells(self, x, y):
        east, north = self.map_from_level(x, y)
        col = np.floor((east - self.r.x0) / self.r.px).astype(np.int64)
        row = np.floor((self.r.y1 - north) / self.r.py).astype(np.int64)
        return row, col

    def z_cm(self, height_ft):
        return (np.asarray(height_ft) - self.f.origin_height_ft) * FT_CM


def wind(vertices, triangles, outward):
    """Order each triangle so that Unreal shows its face toward `outward` (one vector per triangle)."""
    v = np.asarray(vertices)
    t = np.asarray(triangles)
    normal = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
    flip = np.einsum("ij,ij->i", normal, outward) > 0
    t[flip] = t[flip][:, [0, 2, 1]]
    return t


def densify(ring, step):
    out = []
    for (x0, y0), (x1, y1) in zip(ring[:-1], ring[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        parts = max(1, int(math.ceil(length / step)))
        for k in range(parts):
            out.append((x0 + (x1 - x0) * k / parts, y0 + (y1 - y0) * k / parts))
    return out


def building_mesh(polygon, frame, top_smooth, ground, valid):
    """Vertices (level cm) and triangles of one building, or None if it cannot be made."""
    polygon = polygon.simplify(15.0)
    if polygon.geom_type != "Polygon" or polygon.area < 4.0e4:
        return None
    polygon = Polygon(polygon.exterior)
    prepared = prep(polygon)
    minx, miny, maxx, maxy = polygon.bounds
    # cells of the surface that lie inside the footprint, a little in from its edge
    inner = polygon.buffer(-45.0)
    if inner.is_empty:
        inner = polygon
    inner_prepared = prep(inner)
    gx, gy = np.meshgrid(np.arange(minx, maxx + 30.0, 30.0), np.arange(miny, maxy + 30.0, 30.0))
    gx, gy = gx.ravel(), gy.ravel()
    inside = np.array([inner_prepared.contains(Point(a, b)) for a, b in zip(gx, gy)])
    if inside.sum() < 6:
        return None
    sx, sy = gx[inside], gy[inside]
    row, col = frame.cells(sx, sy)
    ok = (row >= 0) & (row < top_smooth.shape[0]) & (col >= 0) & (col < top_smooth.shape[1])
    if ok.sum() < 6 or not ok.all():
        return None
    ok &= valid[row, col]
    if ok.sum() < 6:
        return None
    sx, sy, row, col = sx[ok], sy[ok], row[ok], col[ok]
    heights = frame.z_cm(top_smooth[row, col])
    ground_here = float(np.percentile(frame.z_cm(ground[row, col]), 10)) - 30.0
    cap = float(np.percentile(heights, 97))
    heights = np.clip(heights, ground_here + 200.0, cap)
    tree = cKDTree(np.column_stack([sx, sy]))

    boundary = densify(list(polygon.exterior.coords), ROOF_STEP_CM)
    ix, iy = np.meshgrid(np.arange(minx + 50.0, maxx, ROOF_STEP_CM), np.arange(miny + 50.0, maxy, ROOF_STEP_CM))
    interior = [(a, b) for a, b in zip(ix.ravel(), iy.ravel()) if inner_prepared.contains(Point(a, b))]
    points = np.array(boundary + interior)
    _, nearest = tree.query(points)
    z = heights[nearest]
    count_boundary = len(boundary)
    triangulation = Delaunay(points)
    keep = []
    for simplex in triangulation.simplices:
        centre = points[simplex].mean(axis=0)
        if prepared.contains(Point(centre[0], centre[1])):
            keep.append(simplex)
    if not keep:
        return None
    roof_vertices = np.column_stack([points, z])
    roof = wind(roof_vertices, np.array(keep), np.tile([0.0, 0.0, 1.0], (len(keep), 1)))

    # walls: each boundary point gets a second vertex at the ground
    base = np.column_stack([points[:count_boundary], np.full(count_boundary, ground_here)])
    vertices = np.vstack([roof_vertices, base])
    offset = len(roof_vertices)
    wall, outward = [], []
    for i in range(count_boundary):
        j = (i + 1) % count_boundary
        mid = (points[i] + points[j]) / 2.0
        direction = points[j] - points[i]
        length = math.hypot(direction[0], direction[1])
        if length < 1.0e-6:
            continue
        perpendicular = np.array([direction[1], -direction[0]]) / length
        if prepared.contains(Point(mid[0] + perpendicular[0] * 5.0, mid[1] + perpendicular[1] * 5.0)):
            perpendicular = -perpendicular
        out = [perpendicular[0], perpendicular[1], 0.0]
        wall.append([i, j, offset + j])
        wall.append([i, offset + j, offset + i])
        outward += [out, out]
    walls = wind(vertices, np.array(wall), np.array(outward))
    triangles = np.vstack([roof, walls])
    stats = {"ground_cm": round(ground_here + 30.0, 1), "roof_typical_cm": round(float(np.median(heights)), 1), "roof_high_cm": round(cap, 1),
             "roof_low_cm": round(float(np.percentile(heights, 10)), 1), "footprint_sq_m": round(polygon.area / 1.0e4, 1)}
    return vertices, triangles, stats


def write_mesh(folder, name, vertices, triangles, extra):
    pivot = [float(vertices[:, 0].mean()), float(vertices[:, 1].mean()), float(vertices[:, 2].min())]
    relative = vertices - np.array(pivot)
    with open(os.path.join(folder, name + ".json"), "w", encoding="utf-8") as handle:
        json.dump({"name": name, "pivot": [round(v, 2) for v in pivot], "vertices": np.round(relative, 2).tolist(),
                   "triangles": np.asarray(triangles).astype(int).tolist(), **extra}, handle)
    return pivot


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    data_folder, results_folder, out_folder, manifest_path = argv[1:5]
    os.makedirs(out_folder, exist_ok=True)
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    level_frame = wieland_geo.LevelFrame.load(os.path.join(results_folder, "level_frame.json"))
    with open(os.path.join(data_folder, "fetch_record.json"), encoding="utf-8") as handle:
        record = json.load(handle)["results"]
    dsm = site_analysis.Raster(os.path.join(data_folder, "isgs_dsm_2022.tif"), record["isgs_dsm_2022.tif"]["box"])
    dtm = site_analysis.Raster(os.path.join(data_folder, "isgs_dtm_2022.tif"), record["isgs_dtm_2022.tif"]["box"])
    top = dsm.data.astype(np.float64)
    ground = dtm.data.astype(np.float64)
    valid = np.isfinite(top) & np.isfinite(ground) & (top > -1000) & (ground > -1000) & (top < 1.0e5) & (ground < 1.0e5)
    top_smooth = ndimage.median_filter(np.where(valid, top, np.nanmedian(top[valid])), size=3)
    frame = Frame(level_frame, dsm)
    lot = box(LOT_X[0], LOT_Y[0], LOT_X[1], LOT_Y[1])
    manifest = {"frame": "level coordinates, cm; origin at the lot's south-west corner; north -X, east -Y", "buildings": [], "ground": [], "left_out": []}

    _, footprints = site_analysis.load_polygons(os.path.join(data_folder, "county_footprints_2022.json"))
    for attributes, shape in footprints:
        object_id = attributes.get("OBJECTID")
        parts = [shape] if shape.geom_type == "Polygon" else sorted(getattr(shape, "geoms", []), key=lambda g: -g.area)
        if not parts:
            continue
        ring = list(parts[0].exterior.coords)
        x, y = frame.level_from_map([p[0] for p in ring], [p[1] for p in ring])
        polygon = Polygon(list(zip(x, y)))
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty or polygon.geom_type != "Polygon":
            manifest["left_out"].append({"object_id": object_id, "why": "footprint is not one clean outline"})
            continue
        if polygon.intersection(lot).area > 2.0e5:
            manifest["left_out"].append({"object_id": object_id, "why": "one of the two houses that stood on the lot in 2022"})
            continue
        made = building_mesh(polygon, frame, top_smooth, ground, valid)
        if made is None:
            manifest["left_out"].append({"object_id": object_id, "why": "cut by the edge of the data square, or too small to shape"})
            continue
        vertices, triangles, stats = made
        distance = polygon.distance(lot)
        zone = 1 if distance <= ZONE_1_CM else 2
        name = "SB_%s" % object_id
        pivot = write_mesh(out_folder, name, vertices, triangles, {"kind": "building", "zone": zone})
        entry = {"name": name, "object_id": object_id, "zone": zone, "distance_from_lot_m": round(distance / 100.0, 1), "pivot_cm": [round(v, 1) for v in pivot],
                 "triangles": int(len(triangles)), "county_height_m": None if attributes.get("Height") is None else round(float(attributes["Height"]) * 0.3048006, 2)}
        entry.update(stats)
        manifest["buildings"].append(entry)

    # ---- ground tiles
    rows, cols = ground.shape
    ground_clean = np.where(valid, ground, np.nanmedian(ground[valid]))
    tiles = rows // TILE_FT
    centre_r, centre_c = frame.cells(np.array([-754.38]), np.array([-1557.53]))
    centre_tile = (int(centre_r[0]) // TILE_FT, int(centre_c[0]) // TILE_FT)
    fine = {(centre_tile[0] + a, centre_tile[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)}
    theta = frame.t
    for tr in range(tiles):
        for tc in range(tiles):
            step = 1 if (tr, tc) in fine else 4
            r_index = np.arange(tr * TILE_FT, min((tr + 1) * TILE_FT, rows - 1) + 1, step)
            c_index = np.arange(tc * TILE_FT, min((tc + 1) * TILE_FT, cols - 1) + 1, step)
            rr, cc = np.meshgrid(r_index, c_index, indexing="ij")
            east = dtm.x0 + (cc + 0.5) * dtm.px
            north = dtm.y1 - (rr + 0.5) * dtm.py
            x, y = frame.level_from_map(east, north)
            heights = ground_clean[rr, cc].astype(np.float64)
            if step == 1:
                # where a fine tile meets a coarse one, follow the coarse tile's straight edges so that no crack opens
                for edge, neighbour in (("top", (tr - 1, tc)), ("bottom", (tr + 1, tc)), ("left", (tr, tc - 1)), ("right", (tr, tc + 1))):
                    if neighbour in fine:
                        continue
                    line = heights[0, :] if edge == "top" else heights[-1, :] if edge == "bottom" else heights[:, 0] if edge == "left" else heights[:, -1]
                    nodes = np.arange(0, len(line), 4)
                    if nodes[-1] != len(line) - 1:
                        nodes = np.append(nodes, len(line) - 1)
                    line[:] = np.interp(np.arange(len(line)), nodes, line[nodes])
            z = frame.z_cm(heights)
            vertices = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
            nr, nc = rr.shape
            index = np.arange(nr * nc).reshape(nr, nc)
            a, b, c, d = index[:-1, :-1].ravel(), index[:-1, 1:].ravel(), index[1:, 1:].ravel(), index[1:, :-1].ravel()
            triangles = np.vstack([np.column_stack([a, b, c]), np.column_stack([a, c, d])])
            centres = vertices[triangles].mean(axis=1)
            on_lot = (centres[:, 0] > LOT_X[0]) & (centres[:, 0] < LOT_X[1]) & (centres[:, 1] > LOT_Y[0]) & (centres[:, 1] < LOT_Y[1])
            triangles = triangles[~on_lot]
            if len(triangles) == 0:
                continue
            triangles = wind(vertices, triangles, np.tile([0.0, 0.0, 1.0], (len(triangles), 1)))
            name = "SG_%d_%d" % (tr, tc)
            pivot = write_mesh(out_folder, name, vertices, triangles, {"kind": "ground", "zone": 1 if step == 1 else 2})
            manifest["ground"].append({"name": name, "cell_ft": step, "triangles": int(len(triangles)), "pivot_cm": [round(v, 1) for v in pivot],
                                       "lot_cut_out": bool(on_lot.any())})
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=1)
    b = manifest["buildings"]
    print(json.dumps({"buildings": len(b), "zone_1": sum(1 for e in b if e["zone"] == 1), "zone_2": sum(1 for e in b if e["zone"] == 2),
                      "building_triangles": sum(e["triangles"] for e in b), "left_out": len(manifest["left_out"]),
                      "left_out_why": sorted({e["why"] for e in manifest["left_out"]}),
                      "ground_tiles": len(manifest["ground"]), "ground_triangles": sum(e["triangles"] for e in manifest["ground"]),
                      "fine_tiles": sum(1 for e in manifest["ground"] if e["cell_ft"] == 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
