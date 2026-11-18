"""Phase 20: the work list, the buildings to refine from images, in the order of how much of the views each fills.

Usage: python -B -P phase20_worklist.py <out csv> [skyline count 40] [zone 2 count 25]

Skyline: the Phase 17 targets beyond 1 km and 60 m or taller to the top (towers_record.jsonl of
meshes_towers_clean), ranked by visible cells from D1 plus D1S (viewshed_county/visible_buildings_<view>.csv,
"trees removed"); the first <skyline count>.
Zone 1: all 23 county buildings within 40 m of the lot centre, ranked by visible cells summed over the stations and
decks (S1 to S6, S9, D1, D1S, D2, D5).
Zone 2: the Zone 2 buildings ranked the same way; the first <zone 2 count> with any visible cell.
Each row carries the building's current material instance, its Phase 17 material source and whether it rests on an
assumption, so the table can show what Phase 20 changed.
"""

import csv
import json
import os
import sys

DATA = "E:/Wieland1529_site_data/phase17"
VIEWS = ["S1", "S2", "S3", "S4", "S5", "S6", "S9", "D1", "D1S", "D2", "D5"]


def visible(view):
    path = os.path.join(DATA, "viewshed_county", "visible_buildings_%s.csv" % view)
    return {r["bldg_id"]: int(r["visible_cells_bare_trees"] or 0) for r in csv.DictReader(open(path, encoding="utf-8"))}


def main(argv):
    out = argv[1]
    n_sky = int(argv[2]) if len(argv) > 2 else 40
    n_z2 = int(argv[3]) if len(argv) > 3 else 25
    vis = {v: visible(v) for v in VIEWS}
    recs = {}
    for line in open(os.path.join(DATA, "meshes_towers_clean", "towers_record.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        recs[r["id"]] = r
    tmat = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "tower_materials.csv"), encoding="utf-8"))}
    zmat = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "zone12_materials_v2.csv"), encoding="utf-8"))}
    zones = json.load(open(os.path.join(DATA, "zones_zone12.json"), encoding="utf-8"))
    rows = []
    sky = [i for i, r in recs.items() if r["distance_m"] >= 1000 and r["top_incl_masts_m"] >= 60]
    sky.sort(key=lambda i: -(vis["D1"].get(i, 0) + vis["D1S"].get(i, 0)))
    for k, i in enumerate(sky[:n_sky]):
        m = tmat.get(i, {})
        rows.append({"rank": k + 1, "group": "skyline", "county_id": i, "name": m.get("name", ""),
                     "distance_m": recs[i]["distance_m"], "top_m": recs[i]["top_incl_masts_m"],
                     "visible_cells": vis["D1"].get(i, 0) + vis["D1S"].get(i, 0), "instance": "MI_P17_T_" + i,
                     "p17_source": m.get("source", ""), "p17_assumption": m.get("assumption", ""), "p17_kind": m.get("kind", "")})
    for zone, limit in ((1, None), (2, n_z2)):
        ids = [i for i, z in zones.items() if int(z) == zone]
        score = {i: sum(vis[v].get(i, 0) for v in VIEWS) for i in ids}
        ids.sort(key=lambda i: -score[i])
        if limit is not None:
            ids = [i for i in ids if score[i] > 0][:limit]
        for k, i in enumerate(ids):
            m = zmat.get(i, {})
            rows.append({"rank": k + 1, "group": "zone%d" % zone, "county_id": i, "name": m.get("name", ""),
                         "distance_m": m.get("distance_m", ""), "top_m": "", "visible_cells": score[i],
                         "instance": m.get("instance", "MI_P17_Z_" + i), "p17_source": m.get("wall_material_source", ""),
                         "p17_assumption": "material " + m.get("material_assumed", "") + ", colour " + m.get("colour_assumed", ""),
                         "p17_kind": m.get("wall_material", "")})
    with open(out, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({"skyline": sum(r["group"] == "skyline" for r in rows), "zone1": sum(r["group"] == "zone1" for r in rows),
                      "zone2": sum(r["group"] == "zone2" for r in rows)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
