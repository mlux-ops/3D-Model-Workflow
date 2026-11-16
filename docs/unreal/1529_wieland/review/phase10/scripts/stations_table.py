"""Phase 10, steps 10.1 and 10.2 without photographs: the station cameras as the pictures use them
(review/phase10/stations_now.json, read from the editor) against the surveyed station list
(review/phase2/stations.csv). Writes review/phase10/stations_check.csv. Run from the plan folder."""
import csv
import json

EYE_CM = 160.0
with open("review/phase10/stations_now.json", encoding="utf-8") as handle:
    now = json.load(handle)
rows = []
with open("review/phase2/stations.csv", encoding="utf-8") as handle:
    for line in csv.DictReader(handle):
        name = line["station"].split()[0]
        if name not in now:
            continue
        cam = now[name]
        ground = cam["under"][0]
        dx = cam["loc"][0] - float(line["new_level_x_cm"])
        dy = cam["loc"][1] - float(line["new_level_y_cm"])
        rows.append({
            "station": name,
            "camera_x_cm": cam["loc"][0], "camera_y_cm": cam["loc"][1], "camera_z_cm": cam["loc"][2],
            "listed_x_cm": line["new_level_x_cm"], "listed_y_cm": line["new_level_y_cm"],
            "position_difference_cm": round((dx * dx + dy * dy) ** 0.5, 2),
            "surface_under_camera": ground["object"], "surface_z_cm": ground["z"],
            "eye_height_cm": round(cam["loc"][2] - ground["z"], 1),
            "eye_height_difference_cm": round(cam["loc"][2] - ground["z"] - EYE_CM, 1),
            "camera_heading_deg": cam["rot"][1], "listed_heading_deg": line["level_yaw_deg"],
            "heading_difference_deg": round(cam["rot"][1] - float(line["level_yaw_deg"]), 3),
            "camera_upward_tilt_deg": cam["rot"][0], "camera_roll_deg": cam["rot"][2],
            "lens_deg_across": cam["fov_h"],
        })
with open("review/phase10/stations_check.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
for row in rows:
    print(row["station"], row["position_difference_cm"], row["eye_height_cm"], row["heading_difference_deg"], row["camera_upward_tilt_deg"])
