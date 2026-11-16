"""Phase 17, step 17.3: prepare the Zone 1 and Zone 2 buildings (the 144 of Phase 4) for phase17_towers.py.

Usage:
    python -B -P phase17_zone12.py <phase17 data folder> <Phase 4 mesh folder>

Fetches the ISGS 1 ft surface model once over the 300 m square grown by 60 ft (rasters/site1ft_dsm.npz, skipped
when present), slices it per building (outline plus 30 ft) into rasters/bldg1ft/<county id>_dsm.npz, and writes
targets_zone12.csv (the columns phase17_towers.py reads) and zones_zone12.json (county id -> Phase 4 zone).
The point cloud for these buildings is the "SITE300" box of tile 17259100, cut per building by the builder.
"""

import csv
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase17_fetch_rasters as fr  # noqa: E402

FT = 0.3048006096
SITE = (1174227.19, 1910645.18)
HALF = 492.125 + 60.0


def main(argv):
    base, p4 = argv[1], argv[2]
    zones = {}
    for f in glob.glob(os.path.join(p4, "SB_*.json")):
        d = json.load(open(f, encoding="utf-8"))
        zones[os.path.basename(f)[3:-5]] = int(d.get("zone", 2))
    county = {str(f["attributes"]["OBJECTID"]): f for f in json.load(open(os.path.join(base, "county", "county_footprints_2022_viewbox.json")))["features"]}
    site_path = os.path.join(base, "rasters", "site1ft_dsm.npz")
    if not os.path.exists(site_path):
        box = [SITE[0] - HALF, SITE[1] - HALF, SITE[0] + HALF, SITE[1] + HALF]
        z, x0, y1, urls = fr.fetch(fr.SERVICES["dsm"], box, 1.0)
        np.savez_compressed(site_path, z=z, x0=x0, y1=y1, cell=1.0, url=urls[0])
    d = np.load(site_path)
    Z, X0, Y1 = d["z"], float(d["x0"]), float(d["y1"])
    H, W = Z.shape
    rows = []
    folder = os.path.join(base, "rasters", "bldg1ft")
    os.makedirs(folder, exist_ok=True)
    missing = []
    for bid, zone in sorted(zones.items()):
        f = county.get(bid)
        if f is None:
            missing.append(bid)
            continue
        es = [p[0] for r in f["geometry"]["rings"] for p in r]
        ns = [p[1] for r in f["geometry"]["rings"] for p in r]
        b = [min(es) - 30, min(ns) - 30, max(es) + 30, max(ns) + 30]
        c0, c1 = int(math.floor(b[0] - X0)), int(math.ceil(b[2] - X0))
        r0, r1 = int(math.floor(Y1 - b[3])), int(math.ceil(Y1 - b[1]))
        c0, r0 = max(c0, 0), max(r0, 0)
        c1, r1 = min(c1, W), min(r1, H)
        np.savez_compressed(os.path.join(folder, "%s_dsm.npz" % bid), z=Z[r0:r1, c0:c1], x0=X0 + c0, y1=Y1 - r0, cell=1.0, url=str(d["url"]))
        ce, cn = (min(es) + max(es)) / 2.0, (min(ns) + max(ns)) / 2.0
        rows.append({"bldg_id": bid, "name": "", "ground_z_ft": f["attributes"].get("Ground_Z", ""),
                     "county_max_point_ft": f["attributes"].get("Max_Point", ""), "centroid_east_ft": round(ce, 1),
                     "centroid_north_ft": round(cn, 1), "distance_m": round(math.hypot(ce - SITE[0], cn - SITE[1]) * FT, 1),
                     "zone": zone, "box": "%.1f %.1f %.1f %.1f" % tuple(b)})
    with open(os.path.join(base, "targets_zone12.csv"), "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    json.dump({r["bldg_id"]: r["zone"] for r in rows}, open(os.path.join(base, "zones_zone12.json"), "w"))
    print("buildings", len(rows), "zone 1", sum(1 for r in rows if r["zone"] == 1), "missing", missing)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
