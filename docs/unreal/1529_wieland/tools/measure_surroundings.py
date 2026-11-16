"""Phase 4: measure the surroundings, as placed in the level, against the map data and the survey.

Usage:
    python measure_surroundings.py <site data folder> <phase 2 results folder> <folder of mesh files>
                                   <manifest .json> <level read-back .json> <out .json>

Runs outside the editor. It reads the mesh files that were built, the read-back of where the editor
placed each object, and the 2022 data, and writes the numbers for Phase 4's acceptance list:

  placement   each object's extent in the level against the extent of its file (did the editor put it where the file says)
  plan        Zone 1 buildings: every corner of the county's 2022 footprint against the outline of the object's foot;
              and the three ties of the plat of survey against the same outlines
  kerbs       the kerb's step in the ground objects, on sections across the street, against the same step in the
              2022 ground surface and against the site plan's offset
  heights     every building: the roof of the object against the unsmoothed 2022 top surface inside the footprint

Needs NumPy, SciPy and Shapely.
"""

import json
import os
import sys

import numpy as np
from scipy.interpolate import LinearNDInterpolator
from shapely.geometry import LineString, Point, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_surroundings  # noqa: E402
import site_analysis  # noqa: E402
import wieland_geo  # noqa: E402

FT_CM = wieland_geo.CM_PER_US_SURVEY_FOOT
LIMIT_CM = 30.0
# plat of survey, August 2025: feet north and east of the lot's south-west corner
SURVEY_TIES = [
    {"what": "number 1533 (north neighbour), south-west corner", "object_id": 780226, "north_ft": 49.50, "east_ft": 12.06},
    {"what": "number 1525 (south neighbour), north-west corner", "object_id": 781632, "north_ft": -0.68, "east_ft": 6.51},
    {"what": "number 1525 (south neighbour), north-east corner", "object_id": 781632, "north_ft": -0.37, "east_ft": 55.1},
    {"what": "four-storey building at the rear, west wall (0.22 ft east of the rear line)", "object_id": 781010, "north_ft": 30.0, "east_ft": 102.42},
    {"what": "four-storey building at the rear, west wall (0.34 ft east of the rear line)", "object_id": 781010, "north_ft": 45.0, "east_ft": 102.54},
]
EAST_KERB_CM = 11.854 * FT_CM   # site plan, sheet T1.4: 11 ft 10 1/4 in west of the front lot line
WEST_KERB_CM = 38.5 * FT_CM     # 2022 ground surface, Phase 2


def load_mesh(folder, name):
    with open(os.path.join(folder, name + ".json"), encoding="utf-8") as handle:
        data = json.load(handle)
    return data, np.asarray(data["vertices"], dtype=np.float64) + np.asarray(data["pivot"], dtype=np.float64)


def steepest_step(y, z, low, high, window_cm=30.48):
    """Where, between low and high, the height changes most over one cell: the middle of the kerb's face."""
    step = y[1] - y[0]
    span = max(1, int(round(window_cm / step)))
    rise = np.abs(z[span:] - z[:-span])
    middle = (y[span:] + y[:-span]) / 2.0
    inside = (middle >= low) & (middle <= high) & np.isfinite(rise)
    if not inside.any():
        return None, None
    best = np.argmax(np.where(inside, rise, -1.0))
    return float(middle[best]), float(rise[best])


def main(argv):
    if len(argv) < 7:
        print(__doc__)
        return 2
    data_folder, results_folder, mesh_folder, manifest_path, readback_path, out_path = argv[1:7]
    level_frame = wieland_geo.LevelFrame.load(os.path.join(results_folder, "level_frame.json"))
    with open(os.path.join(data_folder, "fetch_record.json"), encoding="utf-8") as handle:
        record = json.load(handle)["results"]
    dsm = site_analysis.Raster(os.path.join(data_folder, "isgs_dsm_2022.tif"), record["isgs_dsm_2022.tif"]["box"])
    dtm = site_analysis.Raster(os.path.join(data_folder, "isgs_dtm_2022.tif"), record["isgs_dtm_2022.tif"]["box"])
    top = dsm.data.astype(np.float64)
    ground = dtm.data.astype(np.float64)
    valid = np.isfinite(top) & np.isfinite(ground) & (top > -1000) & (ground > -1000) & (top < 1.0e5) & (ground < 1.0e5)
    frame = build_surroundings.Frame(level_frame, dsm)
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    with open(readback_path, encoding="utf-8") as handle:
        readback = {row["name"]: row for row in json.load(handle)}
    _, footprints = site_analysis.load_polygons(os.path.join(data_folder, "county_footprints_2022.json"))
    county = {}
    for attributes, shape in footprints:
        parts = [shape] if shape.geom_type == "Polygon" else sorted(getattr(shape, "geoms", []), key=lambda g: -g.area)
        if parts:
            ring = list(parts[0].exterior.coords)
            x, y = frame.level_from_map([p[0] for p in ring], [p[1] for p in ring])
            county[attributes.get("OBJECTID")] = np.column_stack([x, y])

    out = {"limit_cm": LIMIT_CM, "frame": manifest["frame"]}

    # ---- placement: the level against the files
    worst_place, missing = 0.0, []
    for entry in manifest["buildings"] + manifest["ground"]:
        row = readback.get(entry["name"])
        if row is None:
            missing.append(entry["name"])
            continue
        data, vertices = load_mesh(mesh_folder, entry["name"])
        vertices = vertices[np.unique(np.asarray(data["triangles"]))]   # the editor's extent counts only corners that a triangle uses
        difference = max(np.abs(vertices.min(axis=0) - np.array(row["bounds_min"])).max(), np.abs(vertices.max(axis=0) - np.array(row["bounds_max"])).max())
        worst_place = max(worst_place, float(difference))
    out["placement"] = {"objects_in_files": len(manifest["buildings"]) + len(manifest["ground"]), "objects_in_level": len(readback),
                        "missing_from_level": missing, "largest_difference_of_extent_cm": round(worst_place, 3)}

    # ---- plan and heights, per building
    outlines = {}
    buildings = []
    for entry in manifest["buildings"]:
        _, vertices = load_mesh(mesh_folder, entry["name"])
        foot = entry["foot_edges"]
        roof_vertices = vertices[:len(vertices) - foot]
        outline = Polygon(roof_vertices[:foot, :2])
        outlines[entry["object_id"]] = outline
        row = {"name": entry["name"], "zone": entry["zone"], "distance_from_lot_m": entry["distance_from_lot_m"]}
        corners = county.get(entry["object_id"])
        if corners is not None:
            distances = [outline.exterior.distance(Point(c[0], c[1])) for c in corners]
            row["county_corners"] = len(corners) - 1
            row["corner_worst_cm"] = round(float(max(distances)), 1)
        # heights: the unsmoothed top surface at points 1 m inside the outline, against the object's roof there
        inner = outline.buffer(-100.0)
        if inner.is_empty:
            inner = outline.buffer(-45.0)
        minx, miny, maxx, maxy = outline.bounds
        gx, gy = np.meshgrid(np.arange(minx, maxx, 50.0), np.arange(miny, maxy, 50.0))
        gx, gy = gx.ravel(), gy.ravel()
        keep = np.array([inner.contains(Point(a, b)) for a, b in zip(gx, gy)]) if not inner.is_empty else np.zeros(len(gx), dtype=bool)
        if keep.sum() >= 6:
            sx, sy = gx[keep], gy[keep]
            r, c = frame.cells(sx, sy)
            ok = (r >= 0) & (r < top.shape[0]) & (c >= 0) & (c < top.shape[1])
            ok[ok] &= valid[r[ok], c[ok]]
            sx, sy, r, c = sx[ok], sy[ok], r[ok], c[ok]
            lidar = frame.z_cm(top[r, c])
            mesh = LinearNDInterpolator(roof_vertices[:, :2], roof_vertices[:, 2])(sx, sy)
            good = np.isfinite(mesh)
            lidar, mesh = lidar[good], mesh[good]
            if len(lidar) >= 6:
                difference = mesh - lidar
                row.update({
                    "points": int(len(lidar)),
                    "share_of_points_within_limit": round(float((np.abs(difference) <= LIMIT_CM).mean()), 3),
                    "typical_object_cm": round(float(np.median(mesh)), 1), "typical_lidar_cm": round(float(np.median(lidar)), 1),
                    "high_object_cm": round(float(np.percentile(mesh, 97)), 1), "high_lidar_cm": round(float(np.percentile(lidar, 97)), 1),
                    "low_object_cm": round(float(np.percentile(mesh, 10)), 1), "low_lidar_cm": round(float(np.percentile(lidar, 10)), 1),
                })
                for key in ("typical", "high", "low"):
                    row[key + "_difference_cm"] = round(row[key + "_object_cm"] - row[key + "_lidar_cm"], 1)
        buildings.append(row)
    out["buildings"] = buildings

    def height_summary(rows):
        measured = [r for r in rows if "typical_difference_cm" in r]
        summary = {"buildings": len(rows), "measured": len(measured)}
        for key, label in (("typical", "roof_typical"), ("high", "ridge_or_parapet"), ("low", "eave_or_low_roof")):
            values = np.array([abs(r[key + "_difference_cm"]) for r in measured])
            summary[label] = {"largest_cm": round(float(values.max()), 1), "median_cm": round(float(np.median(values)), 1),
                              "over_limit": int((values > LIMIT_CM).sum()),
                              "over_limit_names": [r["name"] for r in measured if abs(r[key + "_difference_cm"]) > LIMIT_CM][:40]}
        shares = np.array([r["share_of_points_within_limit"] for r in measured])
        points = np.array([r["points"] for r in measured])
        summary["share_of_all_roof_points_within_limit"] = round(float((shares * points).sum() / points.sum()), 3)
        return summary

    zone_1 = [r for r in buildings if r["zone"] == 1]
    zone_2 = [r for r in buildings if r["zone"] == 2]
    out["heights"] = {"zone_1": height_summary(zone_1), "zone_2": height_summary(zone_2)}
    corner_values = [r["corner_worst_cm"] for r in zone_1 if "corner_worst_cm" in r]
    out["plan"] = {"zone_1_buildings": len(zone_1), "county_corners_checked": int(sum(r.get("county_corners", 0) for r in zone_1)),
                   "largest_corner_distance_cm": max(corner_values), "buildings_over_limit": [r["name"] for r in zone_1 if r.get("corner_worst_cm", 0.0) > LIMIT_CM]}

    ties = []
    for tie in SURVEY_TIES:
        x, y = -tie["north_ft"] * FT_CM, -tie["east_ft"] * FT_CM
        outline = outlines.get(tie["object_id"])
        row = dict(tie)
        row["level_x_cm"], row["level_y_cm"] = round(x, 1), round(y, 1)
        if outline is None:
            row["distance_to_outline_cm"] = None
        elif "wall" in tie["what"]:
            # a wall line, not a corner: how far east or west of the surveyed line the outline's wall stands at that place
            cut = outline.exterior.intersection(LineString([(x, y + 400.0), (x, y - 400.0)]))
            points = [cut] if cut.geom_type == "Point" else list(getattr(cut, "geoms", []))
            row["distance_to_outline_cm"] = round(min(abs(p.y - y) for p in points if p.geom_type == "Point"), 1) if points else None
        else:
            corners = np.asarray(outline.exterior.coords)
            row["distance_to_outline_cm"] = round(float(outline.exterior.distance(Point(x, y))), 1)
            row["distance_to_nearest_corner_cm"] = round(float(np.hypot(corners[:, 0] - x, corners[:, 1] - y).min()), 1)
        ties.append(row)
    out["survey_ties"] = ties

    # ---- kerbs: sections across the street, in the ground objects and in the 2022 ground surface
    fine = [e["name"] for e in manifest["ground"] if e["cell_ft"] == 1]
    ground_vertices = np.vstack([load_mesh(mesh_folder, name)[1] for name in fine])
    surface = LinearNDInterpolator(ground_vertices[:, :2], ground_vertices[:, 2])
    y_line = np.arange(0.0, 1500.0, 2.54)
    sections = []
    for x in np.arange(3500.0, -5001.0, -500.0):
        z_object = surface(np.full(len(y_line), x), y_line)
        r, c = frame.cells(np.full(len(y_line), x), y_line)
        z_lidar = frame.z_cm(ground[r, c])
        row = {"level_x_cm": float(x), "metres_north_of_sw_corner": round(-x / 100.0, 1)}
        for label, expected in (("east_kerb", EAST_KERB_CM), ("west_kerb", WEST_KERB_CM)):
            at_object, rise_object = steepest_step(y_line, z_object, expected - 120.0, expected + 120.0)
            at_lidar, rise_lidar = steepest_step(y_line, z_lidar, expected - 120.0, expected + 120.0)
            row[label] = {"object_cm_west_of_front_line": None if at_object is None else round(at_object, 1), "object_step_cm": None if rise_object is None else round(rise_object, 1),
                          "lidar_cm_west_of_front_line": None if at_lidar is None else round(at_lidar, 1), "lidar_step_cm": None if rise_lidar is None else round(rise_lidar, 1),
                          "expected_cm_west_of_front_line": round(expected, 1)}
            if at_object is not None and at_lidar is not None:
                row[label]["object_against_lidar_cm"] = round(at_object - at_lidar, 1)
                row[label]["object_against_expected_cm"] = round(at_object - expected, 1)
        sections.append(row)
    out["kerb_sections"] = sections

    def kerb_summary(label):
        rows = [s[label] for s in sections if "object_against_lidar_cm" in s[label] and s[label]["lidar_step_cm"] >= 5.0]
        return {"sections_with_a_step_of_5_cm_or_more": len(rows), "sections": len(sections),
                "largest_against_lidar_cm": max(abs(r["object_against_lidar_cm"]) for r in rows) if rows else None,
                "largest_against_expected_cm": max(abs(r["object_against_expected_cm"]) for r in rows) if rows else None,
                "over_limit_against_expected": sum(1 for r in rows if abs(r["object_against_expected_cm"]) > LIMIT_CM)}

    out["kerbs"] = {"east": kerb_summary("east_kerb"), "west": kerb_summary("west_kerb")}

    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=1)
    print(json.dumps({k: out[k] for k in ("placement", "plan", "survey_ties", "kerbs", "heights")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
