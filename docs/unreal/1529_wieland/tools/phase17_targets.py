"""Phase 17: choose the buildings to model in detail, and fetch the 1 ft surface model over each.

Usage:
    python -B -P phase17_targets.py <phase17 data folder> [min cells 3] [min distance m 150]

A target is a Cook County 2022 footprint with at least <min cells> visible 6 ft cells (trees removed, the
leaf-off upper bound) from D1, D1S or D2, beyond <min distance> from the viewpoint (outside the 300 m square,
whose buildings are Zone 1 and 2 work). Writes targets.csv, then fetches the ISGS 1 ft surface model over each
target's outline plus 30 ft into rasters/bldg1ft/<county id>_dsm.npz (skipped when present).
"""

import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase17_fetch_rasters as fr  # noqa: E402


def main(argv):
    base = argv[1]
    min_cells = int(argv[2]) if len(argv) > 2 else 3
    min_dist = float(argv[3]) if len(argv) > 3 else 150.0
    picked = {}
    for view in ("D1", "D1S", "D2"):
        path = os.path.join(base, "viewshed_county", "visible_buildings_%s.csv" % view)
        with open(path, encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if int(row["visible_cells_bare_trees"]) >= min_cells and float(row["distance_m"]) > min_dist:
                    key = row["bldg_id"]
                    if key not in picked or view == "D1":
                        row["views"] = (picked.get(key, {}).get("views", "") + " " + view).strip()
                        picked[key] = row
                    else:
                        picked[key]["views"] += " " + view
    with open(os.path.join(base, "county", "county_footprints_2022_viewbox.json")) as handle:
        county = {str(f["attributes"]["OBJECTID"]): f for f in json.load(handle)["features"]}
    rows = []
    for key, row in picked.items():
        rings = county[key]["geometry"]["rings"]
        es = [p[0] for r in rings for p in r]
        ns = [p[1] for r in rings for p in r]
        row["box"] = "%.1f %.1f %.1f %.1f" % (min(es) - 30, min(ns) - 30, max(es) + 30, max(ns) + 30)
        rows.append(row)
    rows.sort(key=lambda r: float(r["distance_m"]))
    with open(os.path.join(base, "targets.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("targets", len(rows))
    folder = os.path.join(base, "rasters", "bldg1ft")
    os.makedirs(folder, exist_ok=True)
    done = 0
    for row in rows:
        path = os.path.join(folder, "%s_dsm.npz" % row["bldg_id"])
        if os.path.exists(path):
            continue
        box = [float(v) for v in row["box"].split()]
        z, x0, y1, urls = fr.fetch(fr.SERVICES["dsm"], box, 1.0)
        import numpy as np
        np.savez_compressed(path, z=z, x0=x0, y1=y1, cell=1.0, url=urls[0])
        done += 1
        if done % 25 == 0:
            print("fetched", done, time.strftime("%H:%M:%S"), flush=True)
    print("fetched all", done)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
