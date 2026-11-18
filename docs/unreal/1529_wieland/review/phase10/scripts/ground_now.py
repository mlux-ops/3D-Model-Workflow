"""Phase 10: the ground, roadway and kerb as they stand in the level today (level L_SiteWorks, made in Phase 7)
against the ground surface of the 2022 laser scan.

Reads review/phase10/heights/siteworks/*.json and .f32 (heights_now.py, 0.5 m grid, level cm),
review/phase10/heights/top_today.npz and review/phase7/heights/combined.npz (to leave out cells under a
building), review/phase2/level_frame.json and the laser scan's ground raster in the site data folder.
Writes review/phase10/ground_now.json.
Usage (from the plan folder):  python -B review/phase10/scripts/ground_now.py E:/Wieland1529_site_data
Nothing in Unreal is touched.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, "tools")
import build_surroundings  # noqa: E402
import site_analysis  # noqa: E402
import wieland_geo  # noqa: E402

NONE = -99999.0
CELL = 50.0
data_folder = sys.argv[1]
level_frame = wieland_geo.LevelFrame.load("review/phase2/level_frame.json")
with open(os.path.join(data_folder, "fetch_record.json"), encoding="utf-8") as handle:
    record = json.load(handle)["results"]
dtm = site_analysis.Raster(os.path.join(data_folder, "isgs_dtm_2022.tif"), record["isgs_dtm_2022.tif"]["box"])
frame = build_surroundings.Frame(level_frame, dtm)
laser = dtm.data.astype(np.float64)

old = np.load("review/phase7/heights/combined.npz")
today = np.load("review/phase10/heights/top_today.npz")
i0, j0 = int(old["i0"]), int(old["j0"])
ni, nj = old["owner"].shape
under_building = (old["owner"] >= 0) | today["building"]

ground = np.full((ni, nj), NONE, dtype=np.float32)
road = np.zeros((ni, nj), dtype=bool)
for header_path in sorted(glob.glob("review/phase10/heights/siteworks/*.json")):
    with open(header_path, encoding="utf-8") as handle:
        header = json.load(handle)
    values = np.fromfile(header_path[:-5] + ".f32", dtype=np.float32).reshape(header["ni"], header["nj"])
    a, b = header["i0"] - i0, header["j0"] - j0
    a0, b0, a1, b1 = max(a, 0), max(b, 0), min(a + header["ni"], ni), min(b + header["nj"], nj)
    if a1 <= a0 or b1 <= b0:
        continue
    view = ground[a0:a1, b0:b1]
    part = values[a0 - a:a1 - a, b0 - b:b1 - b]
    if os.path.basename(header_path).startswith("SW_road"):
        road[a0:a1, b0:b1] |= part >= view
    else:
        road[a0:a1, b0:b1] &= ~(part > view)
    np.maximum(view, part, out=view)

xs = (np.arange(ni) + i0 + 0.5) * CELL
ys = (np.arange(nj) + j0 + 0.5) * CELL
gx, gy = np.meshgrid(xs, ys, indexing="ij")
rows, cols = frame.cells(gx, gy)
inside = (rows >= 0) & (rows < dtm.rows) & (cols >= 0) & (cols < dtm.cols)
laser_cm = np.full((ni, nj), np.nan)
laser_cm[inside] = frame.z_cm(laser[rows[inside], cols[inside]])
ok = inside & (ground > NONE / 2) & np.isfinite(laser_cm) & (np.abs(laser_cm) < 5000.0) & ~under_building
difference = ground - laser_cm


def stats(mask):
    values = difference[mask]
    if values.size == 0:
        return {"cells": 0}
    size = np.abs(values)
    return {"cells": int(values.size), "area_sq_m": round(values.size * 0.25, 0),
            "median_cm": round(float(np.median(values)), 1), "median_of_size_cm": round(float(np.median(size)), 1),
            "root_mean_square_cm": round(float(np.sqrt(np.mean(values ** 2))), 1),
            "p95_of_size_cm": round(float(np.percentile(size, 95)), 1), "largest_cm": round(float(size.max()), 1),
            "share_within_10_cm": round(float((size <= 10.0).mean()), 3), "share_within_20_cm": round(float((size <= 20.0).mean()), 3)}


# the lot: x from 0 (south line) to -1508.8 (north line), y from 0 (front line) to about -3115 (rear line)
near_lot = ok & (gx > -1508.8 - 3000.0) & (gx < 3000.0) & (gy < 2500.0) & (gy > -3115.0 - 1500.0)
frontage = ok & (gx > -1508.8 - 500.0) & (gx < 500.0) & (gy > 0.0) & (gy < 1500.0)
on_lot = (gx > -1508.8) & (gx < 0.0) & (gy < 0.0) & (gy > -3115.0)
result = {"what": "level ground today minus 2022 laser ground, cm; cells under a building left out",
          "everything_measured": stats(ok),
          "within_30_m_of_the_lot": stats(near_lot & ~on_lot),
          "street_and_pavements_in_front_of_the_lot": stats(frontage),
          "roadway_pieces": stats(ok & road),
          "everything_but_roadway": stats(ok & ~road),
          "roadway_in_front_of_the_lot": stats(frontage & road),
          "pavements_in_front_of_the_lot": stats(frontage & ~road)}
with open("review/phase10/ground_now.json", "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=1)
print(json.dumps(result, indent=1))
