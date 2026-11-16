"""Phase 17: the viewshed table and map copies for phase17_results.md, from the outputs of phase17_viewshed.py.

Usage:
    python -B -P phase17_viewshed_table.py <phase17 data folder> <review out folder>

Per viewpoint, with and without trees: county 2022 buildings with 3 or more visible 6 ft cells, by zone (by
distance from the lot centre: Zone 1 under 40 m, Zone 2 to 300 m (the 300 m square), Zone 3 to 1 km, Zone 4
beyond), the farthest visible building, and the visible lake surface (ground model at or under 582 ft NAVD 88 east
of Lake Shore Drive, in hectares). Map copies are scaled to 1,600 px wide.
"""

import csv
import math
import os
import sys

import numpy as np
from PIL import Image

FT = 0.3048006096
SITE = (1174227.19, 1910645.18)


def main(argv):
    base, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    vs = os.path.join(base, "viewshed_county")
    ids = np.load(os.path.join(vs, "building_ids.npz"))["ids"]
    dtm = np.load(os.path.join(base, "rasters", "view6ft_dtm.npz"))
    z, x0, y1, cell = dtm["z"], float(dtm["x0"]), float(dtm["y1"]), float(dtm["cell"])
    h, w = ids.shape
    ex = x0 + (np.arange(w) + 0.5) * cell
    ny = y1 - (np.arange(h) + 0.5) * cell
    lake = (np.nan_to_num(z[:h, :w], nan=0.0) <= 582.0) & (np.nan_to_num(z[:h, :w], nan=0.0) > 0) & (ex[None, :] > 1176500)
    lake |= np.isnan(z[:h, :w]) & (ex[None, :] > 1176500)  # the state leaves tiles wholly over the lake empty
    rows = []
    for name in ["D1", "D1S", "D2", "D5", "S1", "S2", "S3", "S4", "S5", "S6", "S9"]:
        path = os.path.join(vs, "vis_%s.npz" % name)
        if not os.path.exists(path):
            continue
        d = np.load(path)
        for label, key in (("with trees", "vis"), ("trees removed", "vis_bare")):
            v = d[key][:h, :w] > 0
            b = ids[v]
            b = b[b > 0]
            u, cnt = np.unique(b, return_counts=True)
            keep = u[cnt >= 3]
            zones = {1: 0, 2: 0, 3: 0, 4: 0}
            far = 0.0
            if len(keep):
                rr, cc = np.nonzero(v & np.isin(ids, keep))
                dist = np.hypot(ex[cc] - SITE[0], ny[rr] - SITE[1]) * FT
                per = {}
                for bid, dd in zip(ids[rr, cc], dist):
                    per[bid] = min(per.get(bid, 1e9), dd)
                for dd in per.values():
                    zones[1 if dd < 40 else 2 if dd < 300 else 3 if dd < 1000 else 4] += 1
                far = max(per.values())
            lake_ha = float((v & lake).sum()) * (cell * FT) ** 2 / 1e4
            rows.append({"view": name, "trees": label, "buildings": int(len(keep)), "zone1": zones[1], "zone2": zones[2],
                         "zone3": zones[3], "zone4": zones[4], "farthest_m": round(far), "lake_ha": round(lake_ha, 1)})
        src = os.path.join(vs, "viewshed_%s.png" % name)
        if os.path.exists(src):
            im = Image.open(src)
            im.thumbnail((1600, 1600))
            im.save(os.path.join(out, "viewshed_%s.png" % name), optimize=True)
    with open(os.path.join(out, "viewshed_table.csv"), "w", newline="", encoding="utf-8") as handle:
        wr = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    for r in rows:
        print("| %s | %s | %d | %d | %d | %d | %d | %d | %.1f |" % (r["view"], r["trees"], r["buildings"], r["zone1"], r["zone2"],
                                                            r["zone3"], r["zone4"], r["farthest_m"], r["lake_ha"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
