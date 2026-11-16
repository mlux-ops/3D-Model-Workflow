"""Phase 2 measurements from the fetched map data: the lot, true north, the level frame, heights.

Usage:
    python site_analysis.py <site data folder> <results folder>

Reads the five extracts that fetch_site_data.py wrote and writes, into the
results folder (inside the repository; numbers and tables only, no county
imagery):

    site_analysis.json    every figure, with the method beside it
    level_frame.json      the tie between map coordinates and the Unreal level
    site_neighbours.csv   each building footprint near the lot, with heights
    site_trees.csv        each tall object outside a footprint (tree crowns, mostly)

and, into <site data folder>\\derived (outside the repository, because they
contain the county's aerial photograph):

    overlay_block.png     parcels, footprints, the lot and the kerb line over the aerial photograph
    overlay_lot.png       the same, cut to the lot and its neighbours at full resolution
    heights_above_ground.png   the top surface minus the ground, as a picture

All map coordinates are Illinois State Plane East in US survey feet. Heights
are US survey feet above NAVD 88. The lot is the two county parcels of the
site, 17-04-203-010-0000 and 17-04-203-011-0000.

Needs NumPy, SciPy, Shapely and Pillow.
"""

import csv
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wieland_geo  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
SITE_PINS = ("17042030100000", "17042030110000")
FT = wieland_geo.US_SURVEY_FOOT_M

# From sheet T1.4 (site plan) and sheet T1.1 (plat of survey) of drawing set 25-006.
KERB_FROM_FRONT_LINE_FT = 11.0 + 10.25 / 12.0
CENTRE_LINE_FROM_FRONT_LINE_FT = 25.0
RIGHT_OF_WAY_FT = 50.0
SURVEY = {
    "west_ft": 50.18, "north_ft": 102.01, "east_ft": 50.50, "south_ft": 101.93,
    "north_west_deg": 90 + 11 / 60 + 38 / 3600, "north_east_deg": 89 + 43 / 60 + 3 / 3600,
    "south_east_deg": 90 + 6 / 60 + 6 / 3600, "south_west_deg": 89 + 59 / 60 + 13 / 3600,
}


def signed_area(ring):
    total = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        total += x0 * y1 - x1 * y0
    return total / 2.0


def load_polygons(path):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    out = []
    for feature in data["features"]:
        outer, holes = [], []
        for ring in feature["geometry"].get("rings", []):
            ring = [(float(p[0]), float(p[1])) for p in ring]
            if len(ring) < 4:
                continue
            polygon = Polygon(ring)
            if not polygon.is_valid:
                polygon = polygon.buffer(0)
            (outer if signed_area(ring) < 0 else holes).append(polygon)  # Esri: outer rings run clockwise
        if not outer:
            continue
        shape = unary_union(outer)
        if holes:
            shape = shape.difference(unary_union(holes))
        out.append((feature["attributes"], shape))
    return data.get("spatialReference"), out


def azimuth(p, q):
    """Grid bearing from p to q, degrees clockwise from grid north."""
    return math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])) % 360.0


def fold(angle):
    """Fold a bearing into -45 to +45 degrees, the turn of a rectangular grid from grid north."""
    return (angle + 45.0) % 90.0 - 45.0


def weighted_median(values, weights):
    order = np.argsort(values)
    values, weights = np.asarray(values)[order], np.asarray(weights)[order]
    cumulative = np.cumsum(weights)
    return float(values[np.searchsorted(cumulative, cumulative[-1] / 2.0)])


def long_edges(shape, tolerance, shortest):
    polygons = [shape] if shape.geom_type == "Polygon" else list(getattr(shape, "geoms", []))
    for polygon in polygons:
        coords = list(polygon.simplify(tolerance).exterior.coords)
        for p, q in zip(coords, coords[1:]):
            length = math.hypot(q[0] - p[0], q[1] - p[1])
            if length >= shortest:
                yield fold(azimuth(p, q)), length


class Raster:
    def __init__(self, path, box):
        picture = Image.open(path)
        self.tags = {}
        try:
            for key in (33550, 33922, 34735, 34737):
                if key in picture.tag_v2:
                    value = picture.tag_v2[key]
                    self.tags[str(key)] = value if isinstance(value, str) else [float(v) for v in value][:24]
        except Exception as exc:
            self.tags["error"] = repr(exc)
        self.data = np.asarray(picture)
        self.x0, self.y0, self.x1, self.y1 = box
        self.rows, self.cols = self.data.shape[:2]
        self.px = (self.x1 - self.x0) / self.cols
        self.py = (self.y1 - self.y0) / self.rows

    def pixel(self, east, north):
        return (east - self.x0) / self.px, (self.y1 - north) / self.py

    def sample(self, east, north, radius_ft=1.5):
        """Median of the cells within radius_ft of a point."""
        col, row = self.pixel(east, north)
        r = max(1, int(round(radius_ft / self.px)))
        c0, c1 = int(col) - r, int(col) + r + 1
        r0, r1 = int(row) - r, int(row) + r + 1
        if c0 < 0 or r0 < 0 or c1 > self.cols or r1 > self.rows:
            return None
        window = self.data[r0:r1, c0:c1].astype(np.float64)
        window = window[np.isfinite(window) & (window > -1000.0) & (window < 100000.0)]
        return float(np.median(window)) if window.size else None

    def mask(self, shape):
        picture = Image.new("L", (self.cols, self.rows), 0)
        draw = ImageDraw.Draw(picture)
        polygons = [shape] if shape.geom_type == "Polygon" else list(getattr(shape, "geoms", []))
        for polygon in polygons:
            draw.polygon([self.pixel(x, y) for x, y in polygon.exterior.coords], fill=1)
            for hole in polygon.interiors:
                draw.polygon([self.pixel(x, y) for x, y in hole.coords], fill=0)
        return np.asarray(picture, dtype=bool)


def survey_shape():
    """The four corners the survey measured, in a frame whose north is the west lot line. South-west corner at 0, 0."""
    corners = [(0.0, 0.0), (0.0, SURVEY["west_ft"])]
    bearing = 180.0 - SURVEY["north_west_deg"]
    corners.append((corners[-1][0] + SURVEY["north_ft"] * math.sin(math.radians(bearing)),
                    corners[-1][1] + SURVEY["north_ft"] * math.cos(math.radians(bearing))))
    bearing = bearing + 180.0 - SURVEY["north_east_deg"]
    corners.append((corners[-1][0] + SURVEY["east_ft"] * math.sin(math.radians(bearing)),
                    corners[-1][1] + SURVEY["east_ft"] * math.cos(math.radians(bearing))))
    bearing = bearing + 180.0 - SURVEY["south_east_deg"]
    closing = (corners[-1][0] + SURVEY["south_ft"] * math.sin(math.radians(bearing)),
               corners[-1][1] + SURVEY["south_ft"] * math.cos(math.radians(bearing)))
    return {"south_west": corners[0], "north_west": corners[1], "north_east": corners[2], "south_east": corners[3],
            "misclosure_ft": math.hypot(closing[0], closing[1])}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    data_folder, out_folder = argv[1], argv[2]
    derived = os.path.join(data_folder, "derived")
    os.makedirs(out_folder, exist_ok=True)
    os.makedirs(derived, exist_ok=True)
    with open(os.path.join(data_folder, "fetch_record.json"), encoding="utf-8") as handle:
        record = json.load(handle)["results"]
    result = {"inputs": {}, "method_notes": []}

    # ---- parcels and the lot
    parcel_reference, parcels = load_polygons(os.path.join(data_folder, "county_parcels_2025.json"))
    footprint_reference, footprints = load_polygons(os.path.join(data_folder, "county_footprints_2022.json"))
    result["inputs"]["parcels"] = {"count": len(parcels), "coordinate_system": parcel_reference}
    result["inputs"]["footprints"] = {"count": len(footprints), "coordinate_system": footprint_reference}
    site = [(a, s) for a, s in parcels if str(a.get("Name")) in SITE_PINS]
    if len(site) != 2:
        raise RuntimeError("expected the two site parcels, found %d" % len(site))
    lot = unary_union([s for _, s in site])
    ring = list(lot.simplify(0.15).exterior.coords)[:-1]
    corner = {
        "south_west": min(ring, key=lambda p: p[0] + p[1]),
        "north_east": max(ring, key=lambda p: p[0] + p[1]),
        "north_west": max(ring, key=lambda p: p[1] - p[0]),
        "south_east": max(ring, key=lambda p: p[0] - p[1]),
    }
    sw, nw, ne, se = corner["south_west"], corner["north_west"], corner["north_east"], corner["south_east"]
    side = lambda p, q: {"length_ft": round(math.hypot(q[0] - p[0], q[1] - p[1]), 3), "grid_bearing_deg": round(azimuth(p, q), 4)}
    centre = lot.centroid
    lat, lon = wieland_geo.lat_lon_from_state_plane(centre.x, centre.y)
    convergence, scale = wieland_geo.convergence_and_scale(lat, lon)
    result["lot"] = {
        "pins": SITE_PINS,
        "vertices_after_simplifying": len(ring),
        "area_sq_ft": round(lot.area, 2),
        "corners_east_north_ft": {k: [round(v[0], 3), round(v[1], 3)] for k, v in corner.items()},
        "corners_lat_lon": {k: [round(c, 8) for c in wieland_geo.lat_lon_from_state_plane(*v)] for k, v in corner.items()},
        "west_line_south_to_north": side(sw, nw),
        "east_line_south_to_north": side(se, ne),
        "north_line_west_to_east": side(nw, ne),
        "south_line_west_to_east": side(sw, se),
        "centre_east_north_ft": [round(centre.x, 3), round(centre.y, 3)],
        "centre_lat_lon": [round(lat, 8), round(lon, 8)],
        "each_parcel": [{"pin": str(a.get("Name")), "area_sq_ft": round(s.area, 2)} for a, s in site],
    }
    result["survey"] = {"corners_in_its_own_frame_ft": {k: [round(c, 4) for c in v] if isinstance(v, tuple) else round(v, 4) for k, v in survey_shape().items()},
                        "note": "The survey gives lengths and angles and no bearing; its frame's north is its west lot line."}

    # ---- true north, two ways
    west_bearing = fold(azimuth(sw, nw))
    east_bearing = fold(azimuth(se, ne))
    cross_bearing = fold(azimuth(sw, se))
    fabric, fabric_weight = [], []
    for attributes, shape in parcels:
        if 1200.0 <= shape.area <= 40000.0:
            for angle, length in long_edges(shape, 0.3, 40.0):
                if abs(angle - west_bearing) < 6.0:
                    fabric.append(angle)
                    fabric_weight.append(length)
    walls, wall_weight = [], []
    for attributes, shape in footprints:
        for angle, length in long_edges(shape, 0.75, 25.0):
            if abs(angle - west_bearing) < 6.0:
                walls.append(angle)
                wall_weight.append(length)
    fabric_median = weighted_median(fabric, fabric_weight)
    wall_median = weighted_median(walls, wall_weight)
    spread = lambda values, weights, middle: float(np.sqrt(np.average((np.asarray(values) - middle) ** 2, weights=weights)))
    result["true_north"] = {
        "grid_convergence_deg": round(convergence, 4),
        "point_scale": round(scale, 8),
        "lot_west_line_grid_deg": round(west_bearing, 4),
        "lot_east_line_grid_deg": round(east_bearing, 4),
        "lot_north_and_south_lines_folded_grid_deg": [round(fold(azimuth(nw, ne)), 4), round(cross_bearing, 4)],
        "method_1_parcel_lines_of_the_block": {"grid_deg": round(fabric_median, 4), "edges": len(fabric), "total_length_ft": round(sum(fabric_weight), 0),
                                              "spread_deg": round(spread(fabric, fabric_weight, fabric_median), 3)},
        "method_2_building_walls_2022": {"grid_deg": round(wall_median, 4), "edges": len(walls), "total_length_ft": round(sum(wall_weight), 0),
                                        "spread_deg": round(spread(walls, wall_weight, wall_median), 3)},
        "site_north_true_bearing_deg": {
            "lot_west_line": round(west_bearing + convergence, 4),
            "method_1_parcel_lines": round(fabric_median + convergence, 4),
            "method_2_building_walls": round(wall_median + convergence, 4),
        },
        "difference_between_methods_deg": round(abs(fabric_median - wall_median), 4),
        "how_to_read": "A bearing here is the turn of the street grid from north, negative to the west. True bearing = grid bearing + convergence.",
    }

    # ---- the level frame: origin at the south-west lot corner, the level's north (-X) along the west lot line
    dsm = Raster(os.path.join(data_folder, "isgs_dsm_2022.tif"), record["isgs_dsm_2022.tif"]["box"])
    dtm = Raster(os.path.join(data_folder, "isgs_dtm_2022.tif"), record["isgs_dtm_2022.tif"]["box"])
    result["inputs"]["dsm"] = {"cells": [dsm.cols, dsm.rows], "cell_ft": [round(dsm.px, 6), round(dsm.py, 6)], "dtype": str(dsm.data.dtype), "geotiff_tags": dsm.tags}
    result["inputs"]["dtm"] = {"cells": [dtm.cols, dtm.rows], "cell_ft": [round(dtm.px, 6), round(dtm.py, 6)], "dtype": str(dtm.data.dtype), "geotiff_tags": dtm.tags}
    origin_height = dtm.sample(sw[0], sw[1])
    frame = wieland_geo.LevelFrame(sw[0], sw[1], origin_height, north_grid_bearing_deg=azimuth(sw, nw) if azimuth(sw, nw) < 180 else azimuth(sw, nw) - 360.0)
    frame.save(os.path.join(out_folder, "level_frame.json"))
    checks = []
    for name in ("south_west", "north_west", "north_east", "south_east"):
        east, north = corner[name]
        x, y = frame.level_from_map(east, north)
        back = frame.map_from_level(x, y)
        checks.append({"corner": name, "level_x_cm": round(x, 2), "level_y_cm": round(y, 2),
                       "there_and_back_error_m": round(math.hypot(back[0] - east, back[1] - north) * FT, 9)})
    result["level_frame"] = {
        "file": "level_frame.json",
        "origin": "south-west lot corner of the county parcels, at level 0, 0, 0",
        "origin_east_north_ft": [round(sw[0], 3), round(sw[1], 3)],
        "origin_lat_lon": [round(c, 8) for c in wieland_geo.lat_lon_from_state_plane(sw[0], sw[1])],
        "origin_ground_height_ft_navd88": round(origin_height, 2) if origin_height is not None else None,
        "level_north_is": "-X, along the west lot line from south to north; east is -Y, toward the rear of the lot (the axes of the existing Unreal level and of the Datasmith import)",
        "level_north_grid_bearing_deg": round(frame.north_grid_bearing_deg, 4),
        "level_north_true_bearing_deg": round(frame.north_grid_bearing_deg + convergence, 4),
        "corner_checks": checks,
    }

    # ---- ground heights along a line across the street and the lot, through the middle of the frontage
    def along(north_ft, east_ft):
        """A map point given as feet north along the west line and feet east of it, from the south-west corner."""
        return frame.map_from_level(*frame.level_from_site(north_ft, east_ft))
    frontage = math.hypot(nw[0] - sw[0], nw[1] - sw[1])
    depth = math.hypot(se[0] - sw[0], se[1] - sw[1])
    stations = (
        ("west right-of-way line", -RIGHT_OF_WAY_FT), ("west kerb (site plan offset mirrored)", -(RIGHT_OF_WAY_FT - KERB_FROM_FRONT_LINE_FT)),
        ("street centre line", -CENTRE_LINE_FROM_FRONT_LINE_FT), ("east kerb (site plan: 11 ft 10 1/4 in from the lot line)", -KERB_FROM_FRONT_LINE_FT),
        ("sidewalk, 4 ft west of the lot line", -4.0), ("front lot line", 0.0), ("10 ft inside the lot", 10.0),
        ("lot centre", depth / 2.0), ("rear lot line", depth), ("10 ft east of the rear line", depth + 10.0),
    )
    profile = []
    for label, east_ft in stations:
        east, north = along(frontage / 2.0, east_ft)
        ground, top = dtm.sample(east, north), dsm.sample(east, north)
        profile.append({"where": label, "feet_east_of_front_line": round(east_ft, 2),
                        "ground_ft": None if ground is None else round(ground, 2),
                        "ground_m_above_origin": None if ground is None or origin_height is None else round((ground - origin_height) * FT, 3),
                        "top_surface_ft": None if top is None else round(top, 2)})
    result["ground_profile_through_mid_frontage"] = profile
    result["ground_at_lot_corners_ft"] = {k: (None if dtm.sample(*v) is None else round(dtm.sample(*v), 2)) for k, v in corner.items()}
    section = []
    for step in range(-58, 7):
        east, north = along(frontage / 2.0, float(step))
        value = dtm.sample(east, north, radius_ft=0.5)
        section.append([step, None if value is None else round(value, 2)])
    result["ground_cross_section_ft_east_of_front_line"] = section

    # ---- the county's parcel lines against three figures of the survey
    fabric_all = unary_union([s for _, s in parcels]).buffer(0)

    def first_change(start_north_ft, start_east_ft, step_north_ft, step_east_ft, limit_ft, want_inside, least_run_ft=0.0):
        """Walk from a point of the lot frame and return the distance at which the parcel fabric starts (or stops) covering the ground."""
        distance, run_start = 0.0, None
        while distance <= limit_ft:
            east, north = along(start_north_ft + step_north_ft * distance, start_east_ft + step_east_ft * distance)
            inside = fabric_all.contains(Point(east, north))
            if inside == want_inside:
                if run_start is None:
                    run_start = distance
                if distance - run_start >= least_run_ft:
                    return run_start
            else:
                run_start = None
            distance += 0.05
        return None
    to_north_avenue = first_change(frontage, 6.0, 1.0, 0.0, 470.0, want_inside=False, least_run_ft=30.0)
    street_width = first_change(frontage / 2.0, -0.5, 0.0, -1.0, 120.0, want_inside=True)
    behind = first_change(frontage / 2.0, depth + 0.5, 0.0, 1.0, 400.0, want_inside=False, least_run_ft=30.0)
    result["county_parcels_against_the_survey"] = {
        "north_west_corner_to_the_south_line_of_north_avenue_ft": {"county_parcels": None if to_north_avenue is None else round(to_north_avenue, 2), "survey": 266.87},
        "right_of_way_width_at_the_lot_ft": {"county_parcels": None if street_width is None else round(street_width + 0.5, 2), "survey": RIGHT_OF_WAY_FT},
        "lot_depth_ft": {"county_parcels": [result["lot"]["north_line_west_to_east"]["length_ft"], result["lot"]["south_line_west_to_east"]["length_ft"]],
                         "record": 102.20, "survey_measured": [SURVEY["north_ft"], SURVEY["south_ft"]]},
        "lot_frontage_ft": {"county_parcels": result["lot"]["west_line_south_to_north"]["length_ft"], "record": 49.50, "survey_measured": SURVEY["west_ft"]},
        "from_the_rear_line_east_to_the_next_street_ft": None if behind is None else round(behind, 2),
        "how": "walked in steps of 0.05 ft along and across the lot's own axes over the union of all 258 parcels",
    }

    # ---- buildings: heights from the surfaces, beside the county's own figures
    top = dsm.data.astype(np.float64)
    ground = dtm.data.astype(np.float64)
    bad = ~np.isfinite(top) | ~np.isfinite(ground) | (top < -1000) | (ground < -1000) | (top > 100000) | (ground > 100000)
    above = np.where(bad, 0.0, top - ground)
    building_mask = np.zeros(above.shape, dtype=bool)
    rows = []
    lot_box = lot.buffer(260.0)
    for attributes, shape in footprints:
        if not shape.intersects(lot_box):
            continue
        mask = dsm.mask(shape)
        building_mask |= mask
        inner = dsm.mask(shape.buffer(-3.0)) if shape.buffer(-3.0).area > 60 else mask
        cells = above[inner & ~bad]
        if cells.size < 30:
            continue
        ground_here = float(np.median(ground[mask & ~bad]))
        p20, p50, p95 = (float(np.percentile(cells, q)) for q in (20, 50, 95))
        x_cm, y_cm = frame.level_from_map(shape.centroid.x, shape.centroid.y)
        gap = shape.distance(lot)
        site_north, site_east = frame.site_from_level(x_cm, y_cm)
        d_north = site_north - frontage / 2.0
        d_east = site_east - depth / 2.0
        side_of_lot = ("north" if d_north > 0 else "south") if abs(d_north) > abs(d_east) * frontage / depth else ("east" if d_east > 0 else "west")
        rows.append({
            "object_id": attributes.get("OBJECTID"),
            "side_of_lot": side_of_lot,
            "gap_to_lot_ft": round(gap, 2),
            "overlap_with_lot_sq_ft": round(shape.intersection(lot).area, 1),
            "centre_east_ft": round(shape.centroid.x, 2), "centre_north_ft": round(shape.centroid.y, 2),
            "level_x_cm": round(x_cm, 0), "level_y_cm": round(y_cm, 0),
            "footprint_sq_ft": round(shape.area, 0),
            "ground_ft": round(ground_here, 2),
            "height_typical_m": round(p50 * FT, 2), "height_high_m": round(p95 * FT, 2), "height_low_m": round(p20 * FT, 2),
            "roof": "flat or nearly flat" if (p95 - p20) < 4.0 else "pitched or stepped",
            "county_height_m": None if attributes.get("Height") is None else round(float(attributes["Height"]) * FT, 2),
            "county_ground_ft": attributes.get("Ground_Z"), "county_highest_ft": attributes.get("Max_Point"),
        })
    rows.sort(key=lambda r: r["gap_to_lot_ft"])
    with open(os.path.join(out_folder, "site_neighbours.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    result["buildings"] = {"within_ft_of_lot": 260, "count": len(rows), "file": "site_neighbours.csv",
                           "nearest_twelve": rows[:12],
                           "on_the_lot_in_2022": [r for r in rows if r["overlap_with_lot_sq_ft"] > 50.0]}

    # ---- the lot that governs: the record rectangle of the site plan, on the county's front line
    record_frontage, record_depth = 49.50, 102.20
    governing = {}
    for name, (north_ft, east_ft) in (("south_west", (0.0, 0.0)), ("north_west", (record_frontage, 0.0)),
                                      ("north_east", (record_frontage, record_depth)), ("south_east", (0.0, record_depth))):
        east, north = along(north_ft, east_ft)
        x_cm, y_cm = frame.level_from_map(east, north)
        back = frame.map_from_level(x_cm, y_cm)
        lat_c, lon_c = wieland_geo.lat_lon_from_state_plane(east, north)
        county = corner[name]
        governing[name] = {
            "level_x_cm": round(x_cm, 2), "level_y_cm": round(y_cm, 2),
            "east_ft": round(east, 3), "north_ft": round(north, 3),
            "latitude": round(lat_c, 8), "longitude": round(lon_c, 8),
            "there_and_back_error_m": round(math.hypot(back[0] - east, back[1] - north) * FT, 9),
            "from_the_county_parcel_corner_m": round(math.hypot(county[0] - east, county[1] - north) * FT, 3),
            "ground_ft_2022": None if dtm.sample(east, north) is None else round(dtm.sample(east, north), 2),
        }
    result["governing_lot"] = {
        "what": "The record lot of the site plan (sheet T1.4), 49.50 ft by 102.20 ft, with its south-west corner at the county parcel's south-west corner and its front line on the county parcel's front line.",
        "why": "The owner settled that the Revit model's property lines govern, and the site plan draws them at these dimensions. The county's front line agrees with the kerbs in the 2022 ground surface and its parcel is 1.1 to 1.2 ft deeper than the record; the rear neighbour's wall sits where the record depth puts it.",
        "corners": governing,
    }

    # ---- the neighbours' corners nearest the lot, in the lot's own frame, to set beside the survey's ties
    def lot_frame(east, north):
        north_ft, east_ft = frame.site_from_level(*frame.level_from_map(east, north))
        return round(north_ft, 2), round(east_ft, 2)
    near = {}
    for attributes, shape in footprints:
        if shape.distance(lot) > 1.5 or shape.intersection(lot).area > 200.0:
            continue
        polygons = [shape] if shape.geom_type == "Polygon" else list(getattr(shape, "geoms", []))
        points = []
        for polygon in polygons:
            for east, north in list(polygon.simplify(0.5).exterior.coords)[:-1]:
                if Point(east, north).distance(lot) <= 14.0:
                    points.append(lot_frame(east, north))
        near[str(attributes.get("OBJECTID"))] = points
    result["neighbour_corners_near_the_lot_ft_north_and_east_of_the_south_west_corner"] = {
        "corners": near,
        "survey_ties": {
            "number 1533, north": "its south-west corner is on the north line, 12.06 ft east of the front line: north %.2f, east 12.06" % frontage,
            "number 1525, south": "its north-west corner is 0.68 ft south of the south line and 6.51 ft east of the front line (north -0.68, east 6.51); its north-east corner 0.37 ft south (north -0.37, east about 55.1)",
            "the four-storey building at the rear": "its corners are 0.22 and 0.34 ft east of the rear line; with the record depth of 102.20 ft that is east 102.42 to 102.54",
        },
        "note": "The county's footprints are roof outlines taken from 2022 imagery and laser scan, so a pitched roof's eaves reach past its walls.",
    }

    # ---- tall things outside buildings: tree crowns, mostly
    grown = ndimage.binary_dilation(building_mask, iterations=3)
    tall = (above > 15.0) & ~grown & ~bad
    labels, count = ndimage.label(tall)
    trees = []
    if count:
        index = np.arange(1, count + 1)
        areas = ndimage.sum(tall, labels, index)
        heights = ndimage.maximum(above, labels, index)
        centres = ndimage.center_of_mass(tall, labels, index)
        for area, height, (row, col) in zip(areas, heights, centres):
            if area < 60 or area > 8000:
                continue
            east = dsm.x0 + (col + 0.5) * dsm.px
            north = dsm.y1 - (row + 0.5) * dsm.py
            distance = Point(east, north).distance(lot)
            if distance > 330.0:
                continue
            x_cm, y_cm = frame.level_from_map(east, north)
            trees.append({"east_ft": round(east, 1), "north_ft": round(north, 1), "level_x_cm": round(x_cm, 0), "level_y_cm": round(y_cm, 0),
                          "distance_from_lot_ft": round(distance, 1), "top_height_m": round(float(height) * FT, 1),
                          "crown_area_sq_m": round(float(area) * FT * FT, 1), "crown_width_m": round(2.0 * math.sqrt(float(area) / math.pi) * FT, 1),
                          "in_wieland_right_of_way": bool(-RIGHT_OF_WAY_FT <= frame.site_from_level(x_cm, y_cm)[1] <= 0.0)})
    trees.sort(key=lambda t: t["distance_from_lot_ft"])
    with open(os.path.join(out_folder, "site_trees.csv"), "w", newline="", encoding="utf-8") as handle:
        fields = list(trees[0].keys()) if trees else ["east_ft"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(trees)
    result["tall_objects_outside_buildings"] = {
        "rule": "top surface more than 15 ft above ground, outside every footprint grown by 3 ft, 60 to 8,000 sq ft, within 330 ft of the lot",
        "count": len(trees), "file": "site_trees.csv",
        "in_wieland_right_of_way_within_150_ft": [t for t in trees if t["in_wieland_right_of_way"] and t["distance_from_lot_ft"] <= 150.0],
        "caution": "The scan was flown leaf-off in spring 2022, so crowns read smaller than in summer; poles, signs and parts of roofs that overhang a footprint are in this list too.",
    }

    # ---- pictures (outside the repository)
    ortho = Raster(os.path.join(data_folder, "county_ortho_2025.tif"), record["county_ortho_2025.tif"]["box"])
    result["inputs"]["ortho"] = {"pixels": [ortho.cols, ortho.rows], "pixel_ft": [round(ortho.px, 6), round(ortho.py, 6)], "bands": int(ortho.data.shape[2]) if ortho.data.ndim == 3 else 1,
                                 "dtype": str(ortho.data.dtype), "geotiff_tags": ortho.tags}
    base = Image.fromarray(np.ascontiguousarray(ortho.data[:, :, :3])).convert("RGB")
    draw = ImageDraw.Draw(base)

    def outline(shape, colour, width):
        polygons = [shape] if shape.geom_type == "Polygon" else list(getattr(shape, "geoms", []))
        for polygon in polygons:
            points = [ortho.pixel(x, y) for x, y in polygon.exterior.coords]
            draw.line(points, fill=colour, width=width)
    for _, shape in parcels:
        outline(shape, (255, 230, 0), 1)
    for _, shape in footprints:
        outline(shape, (0, 255, 255), 2)
    outline(lot, (255, 0, 0), 3)
    for offset, colour in ((-KERB_FROM_FRONT_LINE_FT, (255, 0, 255)), (-CENTRE_LINE_FROM_FRONT_LINE_FT, (255, 255, 255)),
                           (-(RIGHT_OF_WAY_FT - KERB_FROM_FRONT_LINE_FT), (255, 0, 255)), (-RIGHT_OF_WAY_FT, (255, 140, 0))):
        draw.line([ortho.pixel(*along(-150.0, offset)), ortho.pixel(*along(frontage + 150.0, offset))], fill=colour, width=1)
    base.save(os.path.join(derived, "overlay_block.png"))
    pad = 120.0
    c0, r0 = ortho.pixel(lot.bounds[0] - pad - RIGHT_OF_WAY_FT, lot.bounds[3] + pad)
    c1, r1 = ortho.pixel(lot.bounds[2] + pad, lot.bounds[1] - pad)
    base.crop((int(c0), int(r0), int(c1), int(r1))).save(os.path.join(derived, "overlay_lot.png"))
    shade = np.clip(above / 70.0, 0.0, 1.0)
    Image.fromarray((shade * 255).astype(np.uint8)).resize((dsm.cols * 2, dsm.rows * 2), Image.NEAREST).save(os.path.join(derived, "heights_above_ground.png"))
    result["pictures_outside_the_repository"] = [os.path.join(derived, n) for n in ("overlay_block.png", "overlay_lot.png", "heights_above_ground.png")]
    result["overlay_legend"] = "yellow parcels, cyan footprints (2022), red the lot, magenta the kerbs by the site plan's offset, white the street centre line, orange the west right-of-way line"

    with open(os.path.join(out_folder, "site_analysis.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1)

    north = result["true_north"]
    print("lot: %d vertices, %.1f sq ft" % (len(ring), lot.area))
    for key in ("west_line_south_to_north", "east_line_south_to_north", "north_line_west_to_east", "south_line_west_to_east"):
        print("  %-26s %8.3f ft   grid bearing %9.4f" % (key, result["lot"][key]["length_ft"], result["lot"][key]["grid_bearing_deg"]))
    print("corners (east, north):", {k: v for k, v in result["lot"]["corners_east_north_ft"].items()})
    print("survey shape misclosure %.4f ft" % survey_shape()["misclosure_ft"])
    print("convergence %.4f; west line %.4f; east line %.4f (grid, folded)" % (convergence, west_bearing, east_bearing))
    print("method 1 parcel lines: %.4f grid (%d edges, spread %.3f); method 2 walls: %.4f grid (%d edges, spread %.3f); difference %.4f" % (
        fabric_median, len(fabric), north["method_1_parcel_lines_of_the_block"]["spread_deg"], wall_median, len(walls),
        north["method_2_building_walls_2022"]["spread_deg"], north["difference_between_methods_deg"]))
    print("site north, true bearing:", north["site_north_true_bearing_deg"])
    print("level frame:", {k: result["level_frame"][k] for k in ("origin_east_north_ft", "origin_ground_height_ft_navd88", "level_north_grid_bearing_deg", "level_north_true_bearing_deg")})
    print("corner checks:", checks)
    print("ground profile:")
    for row in profile:
        print("  %-58s ground %s ft  (%s m)  top %s" % (row["where"], row["ground_ft"], row["ground_m_above_origin"], row["top_surface_ft"]))
    print("buildings within 260 ft: %d; tall objects outside buildings: %d" % (len(rows), len(trees)))
    for row in rows[:10]:
        print("  id %-7s %-5s gap %6.2f ft overlap %7.1f  typical %5.1f m high %5.1f m  %-20s county %s m" % (
            row["object_id"], row["side_of_lot"], row["gap_to_lot_ft"], row["overlap_with_lot_sq_ft"], row["height_typical_m"], row["height_high_m"], row["roof"], row["county_height_m"]))
    print("county parcels against the survey:", json.dumps(result["county_parcels_against_the_survey"]))
    print("neighbour corners near the lot (north ft, east ft):", json.dumps(near))
    print("governing lot corners:", json.dumps(governing))
    print("ground cross-section (ft east of the front line: ground ft):", " ".join("%d:%s" % (s, v) for s, v in section))
    print("tall objects in the Wieland right-of-way within 150 ft:", json.dumps(result["tall_objects_outside_buildings"]["in_wieland_right_of_way_within_150_ft"]))
    print("raster tags:", json.dumps({k: (v if isinstance(v, str) else v[:6]) for k, v in dsm.tags.items()})[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
