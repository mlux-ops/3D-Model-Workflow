"""Write mesh_swaps.csv from the rounding record of Phase 6, step 6.2.

Run with:  python -B mesh_swaps.py <rounding_results.json> <mesh_swaps.csv> <date>

The record is written from inside the editor (see phase6_results.md, J4). It holds
    mapping: imported mesh path -> rounded copy path
    info:    imported mesh path -> counts measured when the copy was made
    meta:    imported mesh path -> Revit category, family and type, the number of objects that use it, their units
Rows that are already in the file for another reason (a different `reason` text) are kept.
"""

import csv
import json
import sys

HEAD = ["imported_mesh_name", "revit_family", "revit_type", "replacement_mesh_path", "reason", "decided_by", "date",
        "revit_category", "sharp_edges_before", "sharp_edges_after", "triangles_before", "triangles_after",
        "objects_using_it", "units"]
REASON = "edges rounded 2 mm (step 6.2): copy of the imported mesh with its sharp edges chamfered"


def main(record_path, out_path, date):
    with open(record_path, encoding="utf-8") as handle:
        record = json.load(handle)
    kept = []
    try:
        with open(out_path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("reason") != REASON:
                    kept.append([row.get(name, "") for name in HEAD])
    except FileNotFoundError:
        pass
    rows = []
    for source in sorted(record["mapping"]):
        info = record["info"][source]
        meta = record["meta"].get(source, {})
        rows.append([source.split(".")[-1], meta.get("family") or "", meta.get("type") or "",
                     record["mapping"][source].split(".")[0], REASON, "agent (Phase 6 session)", date,
                     meta.get("category") or "", info["before"], info["after"], info["triangles_before"],
                     info["triangles_after"], meta.get("users", 0), " ".join(meta.get("units", []))])
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEAD)
        writer.writerows(kept)
        writer.writerows(rows)
    before = sum(row[8] for row in rows)
    after = sum(row[9] for row in rows)
    print("rows %d (kept from before: %d); sharp edges in the meshes %d -> %d; copies with none left: %d; objects %d"
          % (len(rows), len(kept), before, after, sum(1 for row in rows if row[9] == 0), sum(row[12] for row in rows)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
