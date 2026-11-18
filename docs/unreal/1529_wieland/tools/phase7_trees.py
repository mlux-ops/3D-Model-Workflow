"""Phase 7, step 7.3: the plan of the trees, worked out off line.

Run from the plan folder:  python -B tools/phase7_trees.py

Reads   review/phase2/site_trees.csv            the 34 tall objects of the 2022 laser scan and aerial photograph
        review/phase7/old_level_trees.json      the eleven trees of the earlier production level (read in J1)
        review/phase7/vegetation/model_sizes.json   each model's own height and width, read in the editor
Writes  review/phase7/vegetation/earlier_trees_vs_data.csv   each earlier tree against the nearest tree of the data
        review/phase7/vegetation/trees_plan.json             what the editor places: one tree for each of the 34
        review/phase7/vegetation/megaplant_uses.csv          every use of a Megaplant model (no licence record)

No tree here is from a site visit. Species, trunk size and the exact trunk position are not known: the
position is the top of the crown in the laser scan, the size is the crown's height and width.

Level frame: centimetres, origin at the lot's south-west corner, north = -X, east = -Y.
"""

import csv
import json
import math
import os

OUT = "review/phase7/vegetation"
SHIFT = (15482.32, 5053.7)      # the earlier level's frame to the level frame (as for the 58 parts)
MATCH_DISTANCE_M = 3.0          # an earlier tree matches a tree of the data when it stands this near ...
MATCH_HEIGHT_M = 3.0            # ... and its height differs by no more than this
MOVE_LIMIT_M = 4.0             # a trunk is moved off a roadway or a building by no more than this
NOTE = "surveyed from data, not from a site visit"


def main():
    os.makedirs(OUT, exist_ok=True)
    with open("review/phase2/site_trees.csv", encoding="utf-8", newline="") as handle:
        data = list(csv.DictReader(handle))
    with open("review/phase7/old_level_trees.json", encoding="utf-8") as handle:
        earlier = json.load(handle)

    # The models: one for each of the eleven earlier trees, with its own height and width at scale 1.
    models = []
    for tree in earlier:
        place = tree["instances"][0]["transform"]
        models.append({
            "component": tree["component"], "asset": tree["asset"], "species_of_model": tree["asset"].split("/")[3].replace("Tree_", "").replace("_", " "),
            "x": place[0] + SHIFT[0], "y": place[1] + SHIFT[1],
            "height_m": 2.0 * tree["bounds_extent"][2] / 100.0, "width_m": 2.0 * max(tree["bounds_extent"][0], tree["bounds_extent"][1]) / 100.0,
            "materials": tree["materials"]})

    # The models' own height and width as the editor reads them from the mesh assets (written by the editor step);
    # the earlier level's readback gave the placed, turned tree's box, which is wider.
    if os.path.exists(OUT + "/model_sizes.json"):
        with open(OUT + "/model_sizes.json", encoding="utf-8") as handle:
            sizes = json.load(handle)
        for model in models:
            model["height_m"], model["width_m"] = sizes[model["asset"]]["height_m"], sizes[model["asset"]]["width_m"]

    for number, row in enumerate(data, 1):
        row["number"] = number
        row["x"], row["y"] = float(row["level_x_cm"]), float(row["level_y_cm"])
        row["h"], row["w"] = float(row["top_height_m"]), float(row["crown_width_m"])

    # Each earlier tree against the nearest tree of the data.
    compare, brought = [], {}
    for model in models:
        nearest = min(data, key=lambda r: math.hypot(r["x"] - model["x"], r["y"] - model["y"]))
        distance = math.hypot(nearest["x"] - model["x"], nearest["y"] - model["y"]) / 100.0
        height_difference = model["height_m"] - nearest["h"]
        match = distance <= MATCH_DISTANCE_M and abs(height_difference) <= MATCH_HEIGHT_M
        if match and (nearest["number"] not in brought or distance < brought[nearest["number"]][1]):
            brought[nearest["number"]] = (model, distance)
        compare.append({
            "earlier_tree": model["component"], "model": model["asset"].split("/")[-1], "species_of_model": model["species_of_model"],
            "earlier_x_cm": round(model["x"], 1), "earlier_y_cm": round(model["y"], 1),
            "earlier_height_m": round(model["height_m"], 1), "earlier_crown_width_m": round(model["width_m"], 1),
            "nearest_data_tree": "T%02d" % nearest["number"], "data_x_cm": nearest["x"], "data_y_cm": nearest["y"],
            "data_height_m": nearest["h"], "data_crown_width_m": nearest["w"],
            "distance_m": round(distance, 2), "height_difference_m": round(height_difference, 1),
            "matches": "yes" if match else "no",
            "rule": "matches when within %.1f m and %.1f m of height" % (MATCH_DISTANCE_M, MATCH_HEIGHT_M)})
    for row in compare:
        number = int(row["nearest_data_tree"][1:])
        row["brought_across"] = "yes, as T%02d at the data position" % number if (
            row["matches"] == "yes" and brought[number][0]["component"] == row["earlier_tree"]) else "no"
    with open(OUT + "/earlier_trees_vs_data.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(compare[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(compare)

    # One tree for each tree of the data. Where an earlier tree matches, its model is kept; otherwise the model
    # that needs the least change of shape (its height stretched by sz, its width by sxy) is taken.
    plan, uses = [], []
    for row in data:
        if row["number"] in brought:
            model, distance = brought[row["number"]]
            source = "brought across from the earlier level (%s, %.2f m from the data position)" % (model["component"], distance)
        else:
            def cost(m):
                sz, sxy = row["h"] / m["height_m"], row["w"] / m["width_m"]
                return abs(math.log(sz / sxy)) + 0.5 * abs(math.log(sz))
            model = min(models, key=cost)
            source = "new stand-in: the model whose shape is nearest to the measured crown"
        sz, sxy = row["h"] / model["height_m"], row["w"] / model["width_m"]
        yaw = (row["number"] * 137.5) % 360.0
        entry = {"name": "VT_T%02d" % row["number"], "x": row["x"], "y": row["y"], "height_m": row["h"], "crown_width_m": row["w"],
                 "asset": model["asset"], "materials": model["materials"], "scale_xy": round(sxy, 4), "scale_z": round(sz, 4), "yaw": round(yaw, 1),
                 "in_wieland_right_of_way": row["in_wieland_right_of_way"] == "True", "distance_from_lot_ft": float(row["distance_from_lot_ft"]),
                 "species_of_model": model["species_of_model"], "source": source, "note": NOTE}
        plan.append(entry)
        uses.append({"object": entry["name"], "level": "/Game/Wieland1529/Vegetation/L_Vegetation", "megaplant_model": model["asset"],
                     "species_of_model": model["species_of_model"], "real_species": "not known (no site visit)",
                     "use": "placement and measurement test; stand-in tagged W1529.Placeholder", "licence": "NO RECORD in asset_licences.csv",
                     "for_the_owner": "confirm the licence of the Megaplant library or name another source (vegetation_proposal.csv)"})
    # Where the trunk can stand. The data gives the top of the crown, not the trunk. Where that point lies on a
    # roadway or under a building of the model, the trunk is moved to the nearest free ground (sidewalk, paving,
    # lawn or soil) and half a metre further in, if that is no more than MOVE_LIMIT_M away; the move is recorded.
    import numpy as np
    from scipy import ndimage
    cover = np.load("review/phase7/ground/cover.npz")
    x0, y0, step = float(cover["x0"]), float(cover["y0"]), float(cover["step"])
    classes = cover["classes"]
    words = {1: "roadway or car park", 2: "public sidewalk", 3: "private paving", 4: "lawn", 5: "soil", 6: "under a building"}
    free = ~((classes == 1) | (classes == 6))
    inner = ndimage.binary_erosion(free, iterations=int(round(50.0 / step)))
    distance, nearest = ndimage.distance_transform_edt(~inner, return_indices=True)
    for entry in plan:
        i = min(max(int((entry["x"] - x0) / step), 0), classes.shape[0] - 1)
        j = min(max(int((entry["y"] - y0) / step), 0), classes.shape[1] - 1)
        entry["data_point_lies_on"] = words.get(int(classes[i, j]), "not classed")
        entry["trunk_x"], entry["trunk_y"], entry["trunk_shift_m"] = entry["x"], entry["y"], 0.0
        entry["trunk_note"] = "trunk at the data point"
        if not free[i, j]:
            shift = float(distance[i, j]) * step / 100.0
            if shift <= MOVE_LIMIT_M:
                ni, nj = int(nearest[0][i, j]), int(nearest[1][i, j])
                entry["trunk_x"], entry["trunk_y"] = round(x0 + (ni + 0.5) * step, 1), round(y0 + (nj + 0.5) * step, 1)
                entry["trunk_shift_m"] = round(math.hypot(entry["trunk_x"] - entry["x"], entry["trunk_y"] - entry["y"]) / 100.0, 2)
                entry["trunk_note"] = "trunk moved off the %s to the nearest free ground (%s)" % (
                    entry["data_point_lies_on"], words.get(int(classes[ni, nj]), "not classed"))
            else:
                entry["trunk_note"] = ("LEFT at the data point on the %s: free ground is %.1f m away, more than %.1f m; "
                                       "this tall object may not be a tree" % (entry["data_point_lies_on"], shift, MOVE_LIMIT_M))
    with open(OUT + "/trees_plan.json", "w", encoding="utf-8") as handle:
        json.dump({"note": NOTE, "trees": plan}, handle, indent=1)
    with open(OUT + "/megaplant_uses.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(uses[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(uses)
    stretch = [abs(math.log(t["scale_z"] / t["scale_xy"])) for t in plan]
    print(json.dumps({"earlier_trees": len(models), "match": sum(1 for r in compare if r["matches"] == "yes"),
                      "brought_across": len(brought), "trees_planned": len(plan),
                      "models_used": sorted({t["asset"].split("/")[-1] for t in plan}),
                      "largest_change_of_shape": round(math.exp(max(stretch)), 2),
                      "scale_z": [min(t["scale_z"] for t in plan), max(t["scale_z"] for t in plan)],
                      "trunks_at_data_point": sum(1 for t in plan if t["trunk_shift_m"] == 0.0 and not t["trunk_note"].startswith("LEFT")),
                      "trunks_moved": sum(1 for t in plan if t["trunk_shift_m"] > 0.0),
                      "largest_move_m": max(t["trunk_shift_m"] for t in plan),
                      "left_on_roadway_or_building": [t["name"] for t in plan if t["trunk_note"].startswith("LEFT")]}))


if __name__ == "__main__":
    main()
