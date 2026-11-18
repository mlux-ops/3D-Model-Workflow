"""Phase 2, step 2.6: how far the existing site model's buildings sit from the 2022 map data.

Usage:
    python compare_existing_model.py <site data folder> <results folder>

Reads, from the results folder, level_frame.json and the height grid that
wieland_site_probe.height_grid() traced in the existing level
(existing_model_heights_2m.f32 and .json), and, from the site data folder,
the state's two height surfaces and the county's 2022 footprints.

The existing level and the Revit export share one frame: north is -X, east
is -Y, the lot's centre line is at X = -16236.7 and its front line at
Y = -5053.7 (phase1_results.md, "Positions used"). The new level frame of
Phase 2 has the same axes with its origin at the lot's south-west corner,
so the two differ by a shift only:

    new x = old x + 15482.32      new y = old y + 5053.7

The script places every traced point on the map through that shift and the
level frame, and looks for the turn and the shift of the model that make
its buildings (surface more than 3 m above the model's grade) cover the 2022
buildings best. It then compares heights building by building.

Writes existing_model_vs_map.json and existing_model_vs_map.csv into the
results folder. Needs NumPy, Shapely and Pillow.
"""

import array
import csv
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_analysis  # noqa: E402
import wieland_geo  # noqa: E402

OLD_TO_NEW_X_CM = 15482.32
OLD_TO_NEW_Y_CM = 5053.7
FT = wieland_geo.US_SURVEY_FOOT_M
RECORD_FRONTAGE_FT, RECORD_DEPTH_FT = 49.50, 102.20


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    data_folder, out_folder = argv[1], argv[2]
    frame = wieland_geo.LevelFrame.load(os.path.join(out_folder, "level_frame.json"))
    with open(os.path.join(out_folder, "existing_model_heights_2m.json"), encoding="utf-8") as handle:
        header = json.load(handle)
    values = array.array("f")
    with open(os.path.join(out_folder, "existing_model_heights_2m.f32"), "rb") as handle:
        values.fromfile(handle, header["nx"] * header["ny"])
    model_cm = np.array(values, dtype=np.float64).reshape(header["nx"], header["ny"])
    hit = model_cm > -90000.0
    ix, iy = np.meshgrid(np.arange(header["nx"]), np.arange(header["ny"]), indexing="ij")
    new_x = header["x_min_cm"] + ix * header["step_cm"] + OLD_TO_NEW_X_CM
    new_y = header["y_min_cm"] + iy * header["step_cm"] + OLD_TO_NEW_Y_CM
    north_m = -new_x / 100.0   # metres north of the lot's south-west corner
    east_m = -new_y / 100.0    # metres east of it

    with open(os.path.join(data_folder, "fetch_record.json"), encoding="utf-8") as handle:
        record = json.load(handle)["results"]
    dsm = site_analysis.Raster(os.path.join(data_folder, "isgs_dsm_2022.tif"), record["isgs_dsm_2022.tif"]["box"])
    dtm = site_analysis.Raster(os.path.join(data_folder, "isgs_dtm_2022.tif"), record["isgs_dtm_2022.tif"]["box"])
    top, ground = dsm.data.astype(np.float64), dtm.data.astype(np.float64)
    bad = ~np.isfinite(top) | ~np.isfinite(ground) | (top < -1000) | (ground < -1000)
    above_m = np.where(bad, 0.0, top - ground) * FT
    _, footprints = site_analysis.load_polygons(os.path.join(data_folder, "county_footprints_2022.json"))
    picture = Image.new("I", (dsm.cols, dsm.rows), 0)
    draw = ImageDraw.Draw(picture)
    shapes = {}
    for number, (attributes, shape) in enumerate(footprints, start=1):
        shapes[number] = (attributes, shape)
        polygons = [shape] if shape.geom_type == "Polygon" else list(getattr(shape, "geoms", []))
        for polygon in polygons:
            draw.polygon([dsm.pixel(x, y) for x, y in polygon.exterior.coords], fill=number)
    building_id = np.asarray(picture, dtype=np.int32)

    theta = math.radians(frame.north_grid_bearing_deg)

    def to_pixels(north, east):
        d_east = north * math.sin(theta) / FT + east * math.cos(theta) / FT
        d_north = north * math.cos(theta) / FT - east * math.sin(theta) / FT
        col = (frame.origin_east_ft + d_east - dsm.x0) / dsm.px
        row = (dsm.y1 - (frame.origin_north_ft + d_north)) / dsm.py
        return np.floor(row).astype(np.int64), np.floor(col).astype(np.int64)

    def sample(north, east):
        row, col = to_pixels(north, east)
        inside = (row >= 0) & (row < dsm.rows) & (col >= 0) & (col < dsm.cols)
        r, c = np.clip(row, 0, dsm.rows - 1), np.clip(col, 0, dsm.cols - 1)
        return inside, above_m[r, c], building_id[r, c]

    lot_north, lot_east = RECORD_FRONTAGE_FT * FT, RECORD_DEPTH_FT * FT
    on_lot = (north_m > -1.5) & (north_m < lot_north + 1.5) & (east_m > -1.5) & (east_m < lot_east + 1.5)
    model_m = np.where(hit, model_cm / 100.0, np.nan)
    model_building = hit & (model_m > 3.0)
    centre_n, centre_e = lot_north / 2.0, lot_east / 2.0

    def score(turn_deg, shift_north, shift_east):
        t = math.radians(turn_deg)
        dn, de = north_m - centre_n, east_m - centre_e
        # a clockwise turn (seen from above) of the model about the lot centre, then a shift
        n2 = centre_n + dn * math.cos(t) - de * math.sin(t) + shift_north
        e2 = centre_e + dn * math.sin(t) + de * math.cos(t) + shift_east
        inside, real_height, real_id = sample(n2, e2)
        use = hit & inside & ~on_lot
        real_building = (real_id > 0) & (real_height > 3.0)
        both = np.count_nonzero(model_building & real_building & use)
        either = np.count_nonzero((model_building | real_building) & use)
        return (both / either if either else 0.0), int(np.count_nonzero(use))

    identity, compared = score(0.0, 0.0, 0.0)
    best = (identity, 0.0, 0.0, 0.0)
    for turn in np.arange(-3.0, 3.01, 0.5):
        for sn in np.arange(-10.0, 10.01, 1.0):
            for se in np.arange(-10.0, 10.01, 1.0):
                value = score(float(turn), float(sn), float(se))[0]
                if value > best[0]:
                    best = (value, float(turn), float(sn), float(se))
    coarse = best
    for turn in np.arange(coarse[1] - 0.5, coarse[1] + 0.501, 0.1):
        for sn in np.arange(coarse[2] - 1.5, coarse[2] + 1.501, 0.25):
            for se in np.arange(coarse[3] - 1.5, coarse[3] + 1.501, 0.25):
                value = score(float(turn), float(sn), float(se))[0]
                if value > best[0]:
                    best = (value, float(turn), float(sn), float(se))

    # ---- heights building by building, with the model as it stands (no turn, no shift)
    inside, real_height, real_id = sample(north_m, east_m)
    rows = []
    for number, (attributes, shape) in shapes.items():
        cells = (real_id == number) & inside & hit & ~on_lot
        count = int(np.count_nonzero(cells))
        if count < 6:
            continue
        model_here = model_m[cells]
        covered = float(np.count_nonzero(model_here > 3.0)) / count
        lidar_here = above_m[building_id == number]
        lidar_typical = float(np.median(lidar_here)) if lidar_here.size else None
        model_typical = float(np.median(model_here[model_here > 3.0])) if covered > 0 else None
        x_cm, y_cm = frame.level_from_map(shape.centroid.x, shape.centroid.y)
        site_north, site_east = frame.site_from_level(x_cm, y_cm)
        rows.append({
            "object_id": attributes.get("OBJECTID"),
            "metres_north_of_sw_corner": round(site_north * FT, 1), "metres_east_of_sw_corner": round(site_east * FT, 1),
            "grid_points": count, "share_covered_by_a_model_building": round(covered, 2),
            "model_height_m": None if model_typical is None else round(model_typical, 1),
            "scan_height_m": None if lidar_typical is None else round(lidar_typical, 1),
            "model_minus_scan_m": None if model_typical is None or lidar_typical is None else round(model_typical - lidar_typical, 1),
            "county_height_m": None if attributes.get("Height") is None else round(float(attributes["Height"]) * FT, 1),
        })
    rows.sort(key=lambda r: math.hypot(r["metres_north_of_sw_corner"] - centre_n, r["metres_east_of_sw_corner"] - centre_e))
    with open(os.path.join(out_folder, "existing_model_vs_map.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with_height = [r for r in rows if r["model_minus_scan_m"] is not None and r["share_covered_by_a_model_building"] >= 0.5]
    differences = np.array([r["model_minus_scan_m"] for r in with_height]) if with_height else np.array([0.0])
    missing = [r for r in rows if r["share_covered_by_a_model_building"] < 0.2 and (r["scan_height_m"] or 0) > 3.0]

    # the model's extent, and model buildings where the 2022 data have none
    extra = hit & inside & ~on_lot & model_building & ~((real_id > 0) & (real_height > 3.0))
    hits_north = north_m[hit]
    hits_east = east_m[hit]
    result = {
        "frames": "existing level and Revit export: north -X, east -Y; new x = old x + %.2f, new y = old y + %.2f (cm)" % (OLD_TO_NEW_X_CM, OLD_TO_NEW_Y_CM),
        "grid": {"step_m": header["step_cm"] / 100.0, "points": int(hit.size), "points_with_a_surface": int(np.count_nonzero(hit)),
                 "model_covers_metres_north_of_sw_corner": [round(float(hits_north.min()), 0), round(float(hits_north.max()), 0)],
                 "model_covers_metres_east_of_sw_corner": [round(float(hits_east.min()), 0), round(float(hits_east.max()), 0)]},
        "overlap_of_building_areas": {
            "how": "share of grid points that are building in both, out of those that are building in either (model: surface over 3 m; 2022: inside a footprint and over 3 m); the lot itself left out",
            "points_compared": compared,
            "as_the_model_stands": round(identity, 3),
            "best": round(best[0], 3),
            "best_turn_deg_clockwise": round(best[1], 2),
            "best_shift_m_north": round(best[2], 2), "best_shift_m_east": round(best[3], 2),
            "searched": "turn -3 to +3 degrees in 0.5 then 0.1; shift -10 to +10 m in 1 then 0.25; about the lot centre",
        },
        "heights": {
            "buildings_compared": len(with_height),
            "median_model_minus_scan_m": round(float(np.median(differences)), 2),
            "median_size_of_difference_m": round(float(np.median(np.abs(differences))), 2),
            "within_1_m": int(np.count_nonzero(np.abs(differences) <= 1.0)),
            "within_3_m": int(np.count_nonzero(np.abs(differences) <= 3.0)),
            "largest_differences": sorted(with_height, key=lambda r: -abs(r["model_minus_scan_m"]))[:6],
            "nearest_ten": rows[:10],
        },
        "footprints_of_2022_with_no_model_building": {"count": len(missing), "nearest_six": missing[:6]},
        "model_building_points_with_no_2022_building": int(np.count_nonzero(extra)),
        "file": "existing_model_vs_map.csv",
    }
    with open(os.path.join(out_folder, "existing_model_vs_map.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1)
    print(json.dumps(result["grid"]))
    print(json.dumps(result["overlap_of_building_areas"]))
    print("heights:", json.dumps({k: v for k, v in result["heights"].items() if k not in ("largest_differences", "nearest_ten")}))
    for row in rows[:10]:
        print("  id %-7s N %6.1f E %6.1f  covered %.2f  model %s  scan %s  county %s" % (
            row["object_id"], row["metres_north_of_sw_corner"], row["metres_east_of_sw_corner"], row["share_covered_by_a_model_building"],
            row["model_height_m"], row["scan_height_m"], row["county_height_m"]))
    print("2022 footprints with no model building: %d; model building points with no 2022 building: %d" % (len(missing), int(np.count_nonzero(extra))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
