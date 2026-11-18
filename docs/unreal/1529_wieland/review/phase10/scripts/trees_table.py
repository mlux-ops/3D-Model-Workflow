"""Phase 10: the trees as they stand in the level today (review/phase10/trees_now.json, read by trees_now.py)
against the tree data of Phase 7 (review/phase7/vegetation/tree_positions.csv: crown tops of the 2022 laser
scan). Writes review/phase10/trees_check.csv. Run from the plan folder."""
import csv
import json
import math

with open("review/phase10/trees_now.json", encoding="utf-8") as handle:
    today = {item["label"]: item for item in json.load(handle)}
with open("review/phase7/vegetation/tree_positions.csv", encoding="utf-8") as handle:
    data = list(csv.DictReader(handle))

rows = []
for item in data:
    now = today.get(item["tree"])
    row = {"tree": item["tree"], "in_level_today": "yes" if now else "no", "trunk_from_data_point_m": "",
           "data_height_m": item["data_height_m"], "height_today_m": "", "height_difference_m": "",
           "data_crown_width_m": item["data_crown_width_m"], "box_width_today_m": "",
           "data_point_lies_on": item["data_point_lies_on"], "trunk_note": item["trunk_note"],
           "model": item["species_of_model"]}
    if now:
        height = (now["top_z"] - now["z"]) / 100.0
        row["trunk_from_data_point_m"] = round(math.hypot(now["x"] - float(item["data_x_cm"]),
                                                          now["y"] - float(item["data_y_cm"])) / 100.0, 2)
        row["height_today_m"] = round(height, 1)
        row["height_difference_m"] = round(height - float(item["data_height_m"]), 1)
        row["box_width_today_m"] = now["box_width_m"]
    rows.append(row)
with open("review/phase10/trees_check.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
placed = [r for r in rows if r["in_level_today"] == "yes"]
print(len(rows), "trees in the data,", len(placed), "in the level today;",
      sum(1 for r in placed if r["trunk_from_data_point_m"] <= 0.3), "trunks within 0.3 m of the data point;",
      "largest height difference", max(abs(r["height_difference_m"]) for r in placed), "m")
