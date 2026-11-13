"""Phase 10: where the neighbours' walls that the plat of survey ties to the lot stand in the level today.

Reads review/phase10/heights/ties/*.json and .f32 (ties_now.py: 5 cm height maps, 8 m windows, of the earlier
detailed buildings after Phase 7's fit) and review/phase10/heights/ties_job.json (the surveyed points, level cm).
A cell counts as building when its top is 2.5 m or more above the datum. Seen from above, a wall's place is the
edge of what stands over it, so eaves and cornices are included; that is stated with the numbers.
Writes review/phase10/survey_ties_now.csv. Run from the plan folder. Nothing in Unreal is touched.
Level frame: north is -X, east is -Y.
"""
import csv
import json

import numpy as np

with open("review/phase10/heights/ties_job.json", encoding="utf-8") as handle:
    jobs = {job["name"]: job for job in json.load(handle)}
# per tie: which walls to find, and the strip (cm from the surveyed point, into the building) in which to look
WALLS = {
    "tie1_1533_sw": [("south", "east"), ("west", "north")],
    "tie2_1525_nw": [("north", "east"), ("west", "south")],
    "tie3_1525_ne": [("north", "west"), ("east", "south")],
    "tie4_rear_30": [("west", None)],
    "tie5_rear_45": [("west", None)],
}
# 1525 has a one-storey rear part, 3.2 m high and 2.4 m deep, east of the corner the survey ties (the corner of the
# main house). At that tie the main house is found with a higher threshold; the rear part is noted.
THRESHOLD_CM = {"tie3_1525_ne": 500.0}
NOTE = {"tie3_1525_ne": "main house wall (top over 5 m); a one-storey rear part 3.2 m high reaches 2.4 m further east",
        "tie1_1533_sw": "the west edge is the coping of the parapet, seen from above",
        "tie2_1525_nw": "the west edge is the roof's edge (eaves), seen from above"}
STEP = {"north": (-1, 0), "south": (1, 0), "east": (0, -1), "west": (0, 1)}
rows = []
for name, walls in WALLS.items():
    job = jobs[name]
    with open("review/phase10/heights/ties/%s.json" % name, encoding="utf-8") as handle:
        header = json.load(handle)
    n, cell, half = header["n"], header["cell_cm"], header["half"]
    z = np.fromfile("review/phase10/heights/ties/%s.f32" % name, dtype=np.float32).reshape(n, n)
    mask = z > THRESHOLD_CM.get(name, 250.0)
    xs = job["x"] - half + (np.arange(n) + 0.5) * cell
    ys = job["y"] - half + (np.arange(n) + 0.5) * cell
    row = {"tie": name, "what": job["what"], "surveyed_x_cm": job["x"], "surveyed_y_cm": job["y"]}
    found = {}
    for wall, inward in walls:
        # strip of cells 1.0 to 2.5 m along the wall from the corner (inward), or 0.5 m either side for a plain wall
        if inward is None:
            along = np.abs((xs if wall in ("east", "west") else ys) - (job["x"] if wall in ("east", "west") else job["y"])) <= 50.0
        else:
            axis_values = xs if inward in ("north", "south") else ys
            origin = job["x"] if inward in ("north", "south") else job["y"]
            sign = STEP[inward][0] + STEP[inward][1]
            offset = (axis_values - origin) * sign
            along = (offset >= 100.0) & (offset <= 250.0)
        places = []
        if wall in ("north", "south"):
            strip = mask[:, along]                      # columns = y inside the strip; rows = x
            for column in strip.T:
                idx = np.nonzero(column)[0]
                if idx.size:
                    edge = xs[idx.min()] - cell / 2 if wall == "north" else xs[idx.max()] + cell / 2
                    places.append(edge)
            surveyed = job["x"]
            outward = -1.0 if wall == "north" else 1.0
        else:
            strip = mask[along, :]
            for line in strip:
                idx = np.nonzero(line)[0]
                if idx.size:
                    edge = ys[idx.min()] - cell / 2 if wall == "east" else ys[idx.max()] + cell / 2
                    places.append(edge)
            surveyed = job["y"]
            outward = -1.0 if wall == "east" else 1.0
        if places:
            place = float(np.median(places))
            found[wall] = place
            # positive: today's wall stands further out from its building than the survey puts it
            row[wall + "_wall_today_cm"] = round(place, 1)
            row[wall + "_wall_further_out_than_surveyed_cm"] = round((place - surveyed) * outward, 1)
    if len(walls) == 2 and len(found) == 2:
        values = [abs(row[w + "_wall_further_out_than_surveyed_cm"]) for w, _ in walls]
        row["corner_distance_cm"] = round(float(np.hypot(values[0], values[1])), 1)
    elif found:
        row["corner_distance_cm"] = abs(row[walls[0][0] + "_wall_further_out_than_surveyed_cm"])
    row["note"] = NOTE.get(name, "")
    rows.append(row)
fields = ["tie", "what", "surveyed_x_cm", "surveyed_y_cm", "corner_distance_cm"]
for wall in ("north", "south", "east", "west"):
    fields += [wall + "_wall_today_cm", wall + "_wall_further_out_than_surveyed_cm"]
fields.append("note")
with open("review/phase10/survey_ties_now.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
for row in rows:
    print({k: v for k, v in row.items() if k != "what"})
