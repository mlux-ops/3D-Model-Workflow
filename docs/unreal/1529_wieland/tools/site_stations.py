"""Place the exterior stations of REFERENCE_VIEWS.md from the measured street, in every frame in use.

Usage:
    python site_stations.py <results folder>

Reads level_frame.json from the results folder and writes stations.csv
there. Each station is given as metres north and metres east of the lot's
south-west corner, along the lot's own axes, and from that as latitude and
longitude, as State Plane coordinates, as coordinates in the new level frame
(origin at the south-west lot corner) and as coordinates in the existing
level and the Revit export (the same axes, shifted; see
compare_existing_model.py).

The walking lines come from Phase 2's measurements: the west kerb is 11.7 m
and the west right-of-way line 15.2 m west of the front lot line, so the
west sidewalk's walking line is put at 14.0 m; the east kerb is 3.6 m west
of the front lot line, so the east sidewalk's walking line is put at 2.1 m.
Eye height is 1.60 m above the sidewalk.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wieland_geo  # noqa: E402

FT = wieland_geo.US_SURVEY_FOOT_M
OLD_TO_NEW_X_CM = 15482.32
OLD_TO_NEW_Y_CM = 5053.7
FRONTAGE_M = 49.50 * FT
DEPTH_M = 102.20 * FT
WEST_WALK_M = -14.0
EAST_WALK_M = -2.1
CENTRE_NORTH_M = FRONTAGE_M / 2.0

# name, metres north of the south-west corner, metres east of it, true bearing the camera faces, note
STATIONS = (
    ("S1 Frontal", CENTRE_NORTH_M, WEST_WALK_M, 90.0, "west sidewalk opposite the lot's centre line"),
    ("S2 From the south-west", CENTRE_NORTH_M - 25.0, WEST_WALK_M, 45.0, "west sidewalk 25 m south of S1"),
    ("S3 From the north-west", CENTRE_NORTH_M + 25.0, WEST_WALK_M, 135.0, "west sidewalk 25 m north of S1"),
    ("S4 Long view from the south", CENTRE_NORTH_M - 50.0, WEST_WALK_M, 15.0, "west sidewalk 50 m south of S1"),
    ("S5 Long view from the north", CENTRE_NORTH_M + 60.0, WEST_WALK_M, 165.0, "west sidewalk 60 m north of S1"),
    ("S6 Along the frontage", FRONTAGE_M + 20.0, EAST_WALK_M, 180.0, "east sidewalk 20 m north of the lot's north line"),
    ("S7 From the rear", CENTRE_NORTH_M - 15.0, DEPTH_M + 4.0, 330.0, "there is no alley: this point is inside the rear neighbour's lot and cannot be stood on; kept only to show where the plan had put it"),
    ("S8 Plan", CENTRE_NORTH_M, DEPTH_M / 2.0, None, "straight down over the lot centre"),
    ("S9 Opposite side", CENTRE_NORTH_M, EAST_WALK_M, 270.0, "east sidewalk at the lot's centre line, looking west"),
)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    folder = argv[1]
    frame = wieland_geo.LevelFrame.load(os.path.join(folder, "level_frame.json"))
    lat0, lon0 = wieland_geo.lat_lon_from_state_plane(frame.origin_east_ft, frame.origin_north_ft)
    convergence = wieland_geo.convergence_and_scale(lat0, lon0)[0]
    level_north_true = frame.north_grid_bearing_deg + convergence
    rows = []
    for name, north_m, east_m, bearing, note in STATIONS:
        x_cm, y_cm = frame.level_from_site(north_m / FT, east_m / FT)
        east_ft, north_ft = frame.map_from_level(x_cm, y_cm)
        lat, lon = wieland_geo.lat_lon_from_state_plane(east_ft, north_ft)
        rows.append({
            "station": name,
            "metres_north_of_sw_corner": round(north_m, 2), "metres_east_of_sw_corner": round(east_m, 2),
            "latitude": round(lat, 7), "longitude": round(lon, 7),
            "state_plane_east_ft": round(east_ft, 2), "state_plane_north_ft": round(north_ft, 2),
            "new_level_x_cm": round(x_cm, 1), "new_level_y_cm": round(y_cm, 1),
            "existing_level_x_cm": round(x_cm - OLD_TO_NEW_X_CM, 1), "existing_level_y_cm": round(y_cm - OLD_TO_NEW_Y_CM, 1),
            "faces_true_bearing_deg": bearing,
            # Unreal yaw 0 looks along +X, which is the level's south; yaw grows clockwise seen from above.
            # So yaw = bearing - (bearing of +X) = bearing - (bearing of the level's north + 180), folded into -180 to +180.
            "level_yaw_deg": None if bearing is None else round((bearing - level_north_true) % 360.0 - 180.0, 2),
            "note": note,
        })
    with open(os.path.join(folder, "stations.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("level north (-X) true bearing: %.4f degrees" % level_north_true)
    for row in rows:
        print("%-28s N %7.2f E %7.2f  lat %.7f lon %.7f  new level (%8.1f, %8.1f)  existing level (%9.1f, %8.1f)  yaw %s" % (
            row["station"], row["metres_north_of_sw_corner"], row["metres_east_of_sw_corner"], row["latitude"], row["longitude"],
            row["new_level_x_cm"], row["new_level_y_cm"], row["existing_level_x_cm"], row["existing_level_y_cm"], row["level_yaw_deg"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
