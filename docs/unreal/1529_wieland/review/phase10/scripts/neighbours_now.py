"""Phase 10: the neighbouring buildings as they stand in the level today against the 2022 laser scan and the
Phase 4 footprints (which follow the county's 2022 outlines).

Reads review/phase10/heights/r15fit/*.json and .f32 (heights_now.py: the earlier detailed buildings after
Phase 7's fit, top surface on the 0.5 m grid), review/phase7/heights/combined.npz (which Phase 4 building owns
which cell, and the Phase 4 ground), review/phase4/acceptance_measurements.json (the laser scan's typical roof
level per building) and review/phase4/surroundings_manifest.json.
Writes review/phase10/neighbours_now.csv and review/phase10/neighbours_now.json.
Run from the plan folder:  python -B review/phase10/scripts/neighbours_now.py     Nothing in Unreal is touched.
"""
import csv
import glob
import json
import os

import numpy as np
from scipy import ndimage

NONE = -99999.0
CELL = 50.0
BUILDING_OVER_GROUND_CM = 250.0

old = np.load("review/phase7/heights/combined.npz")
owner, ground, top_p4b = old["owner"], old["ground_p4"], old["top_p4b"]
i0, j0 = int(old["i0"]), int(old["j0"])
ni, nj = owner.shape
top = np.full((ni, nj), NONE, dtype=np.float32)
for header_path in sorted(glob.glob("review/phase10/heights/r15fit/*.json")):
    with open(header_path, encoding="utf-8") as handle:
        header = json.load(handle)
    values = np.fromfile(header_path[:-5] + ".f32", dtype=np.float32).reshape(header["ni"], header["nj"])
    a, b = header["i0"] - i0, header["j0"] - j0
    a0, b0 = max(a, 0), max(b, 0)
    a1, b1 = min(a + header["ni"], ni), min(b + header["nj"], nj)
    if a1 <= a0 or b1 <= b0:
        continue
    view = top[a0:a1, b0:b1]
    np.maximum(view, values[a0 - a:a1 - a, b0 - b:b1 - b], out=view)

has_top = top > NONE / 2
has_ground = ground > NONE / 2
building = has_top & has_ground & (top - ground > BUILDING_OVER_GROUND_CM)
labels, _ = ndimage.label(building)
distance, nearest = ndimage.distance_transform_edt(owner < 0, return_indices=True)
nearest_owner = owner[nearest[0], nearest[1]]

with open("review/phase4/acceptance_measurements.json", encoding="utf-8") as handle:
    accept = {b["name"]: b for b in json.load(handle)["buildings"]}
with open("review/phase4/surroundings_manifest.json", encoding="utf-8") as handle:
    manifest = {b["name"]: b for b in json.load(handle)["buildings"]}
names = sorted(os.path.basename(p)[:-5] for p in glob.glob("review/phase7/heights/p4b/*.json"))
xs = (np.arange(ni) + i0 + 0.5) * CELL
ys = (np.arange(nj) + j0 + 0.5) * CELL

rows = []
for index, name in enumerate(names):
    mine = owner == index
    cells = int(mine.sum())
    if cells == 0:
        continue
    both = mine & building
    share = both.sum() / cells
    info, measured = manifest.get(name, {}), accept.get(name, {})
    row = {"building": name, "zone": info.get("zone", ""), "distance_from_lot_m": info.get("distance_from_lot_m", ""),
           "footprint_sq_m": round(cells * 0.25, 1), "share_covered_by_todays_building": round(float(share), 3)}
    if share >= 0.5:
        roof = float(np.median(top[both]))
        lidar = measured.get("typical_lidar_cm")
        row["roof_typical_today_cm"] = round(roof, 1)
        row["roof_typical_laser_2022_cm"] = lidar if lidar is not None else ""
        if lidar is not None:
            row["roof_difference_today_minus_laser_m"] = round((roof - lidar) / 100.0, 2)
        ii, jj = np.nonzero(mine)
        touching = [int(v) for v in np.unique(labels[both]) if v > 0]
        shape = building & (nearest_owner == index) & (distance <= 6.0) & np.isin(labels, touching)
        ei, ej = np.nonzero(shape)
        # positive: today's building reaches further out than the county outline on that side
        row["north_side_further_out_m"] = round((float(xs[ii].min()) - float(xs[ei].min())) / 100.0, 1)
        row["south_side_further_out_m"] = round((float(xs[ei].max()) - float(xs[ii].max())) / 100.0, 1)
        row["east_side_further_out_m"] = round((float(ys[jj].min()) - float(ys[ej].min())) / 100.0, 1)
        row["west_side_further_out_m"] = round((float(ys[ej].max()) - float(ys[jj].max())) / 100.0, 1)
    rows.append(row)

fields = ["building", "zone", "distance_from_lot_m", "footprint_sq_m", "share_covered_by_todays_building",
          "roof_typical_today_cm", "roof_typical_laser_2022_cm", "roof_difference_today_minus_laser_m",
          "north_side_further_out_m", "south_side_further_out_m", "east_side_further_out_m", "west_side_further_out_m"]
with open("review/phase10/neighbours_now.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in sorted(rows, key=lambda r: (r["distance_from_lot_m"] if r["distance_from_lot_m"] != "" else 1e9)):
        writer.writerow(row)


def summary(group):
    heights = np.array([r["roof_difference_today_minus_laser_m"] for r in group if "roof_difference_today_minus_laser_m" in r])
    sides = np.array([[r[k] for k in fields[8:]] for r in group if "north_side_further_out_m" in r])
    out = {"buildings": len(group), "covered_by_todays_building": int(sum(1 for r in group if "roof_typical_today_cm" in r))}
    if heights.size:
        out["roof"] = {"measured": int(heights.size), "median_m": round(float(np.median(heights)), 2),
                       "median_of_size_m": round(float(np.median(np.abs(heights))), 2),
                       "largest_m": round(float(np.abs(heights).max()), 2),
                       "within_0.3_m": int((np.abs(heights) <= 0.3).sum()),
                       "over_1_m": int((np.abs(heights) > 1.0).sum()), "over_3_m": int((np.abs(heights) > 3.0).sum())}
    if sides.size:
        out["sides"] = {"measured": int(sides.size), "median_m": round(float(np.median(sides)), 2),
                        "within_0.5_m": int((np.abs(sides) <= 0.5).sum()), "within_1.0_m": int((np.abs(sides) <= 1.0).sum()),
                        "largest_m": round(float(np.abs(sides).max()), 1)}
    return out


result = {"grid_cell_m": 0.5, "all": summary(rows), "zone_1": summary([r for r in rows if r["zone"] == 1]),
          "zone_2": summary([r for r in rows if r["zone"] == 2]),
          "worst_roofs": sorted(([r["building"], r["zone"], r["roof_difference_today_minus_laser_m"]] for r in rows
                                 if "roof_difference_today_minus_laser_m" in r), key=lambda t: -abs(t[2]))[:12]}
with open("review/phase10/neighbours_now.json", "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=1)
np.savez_compressed("review/phase10/heights/top_today.npz", top=top, building=building, i0=i0, j0=j0)
print(json.dumps(result, indent=1))
