"""Phase 5: the table of switchable alternatives.

    python -B phase5_alternatives.py <material_candidates.csv> <material_audit.csv> <slot_uses.json> <level name>
                                     <material_alternatives.csv>

A switchable alternative is a material swap the scene can turn on and off.
Each row names the Revit material (the active default), the candidate that
can stand in for it, and how many mesh slots of the level show the Revit
material and would be switched. The table is what
wieland_candidates.alternatives_on() reads; the state column records that
every swap is off in the saved project. slot_uses.json is what
wieland_candidates.count_uses() returned with the level open.
"""

import csv
import json
import sys


def main(candidates_csv, audit_csv, uses_json, level, out_csv):
    with open(candidates_csv, encoding="utf-8", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    with open(audit_csv, encoding="utf-8", newline="") as handle:
        audit = {row["material"]: row for row in csv.DictReader(handle)}
    with open(uses_json, encoding="utf-8") as handle:
        uses = json.load(handle)
    rows = []
    for row in candidates:
        slots = int(uses.get(row["material"], 0))
        rows.append({
            "material": row["material"],
            "family": row["family"],
            "confidence": row["confidence"],
            "revit_asset": row["revit_asset"],
            "candidate_asset": row["candidate_asset"],
            "level": level,
            "mesh_slots_in_the_level": slots,
            "state_in_the_saved_project": "off (the Revit material is shown)",
            "how_to_switch": "wieland_candidates.alternatives_on(<this file>) / alternatives_off()",
            "owner_decision": audit.get(row["material"], {}).get("decision", ""),
            "note": "" if slots else "The level shows this material on no mesh slot; the swap has nothing to switch there.",
        })
    with open(out_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    placed = sum(1 for r in rows if r["mesh_slots_in_the_level"])
    print("%d swaps written; %d switch at least one slot of %s (%d slots in all); %d switch none" % (
        len(rows), placed, level, sum(r["mesh_slots_in_the_level"] for r in rows), len(rows) - placed))


if __name__ == "__main__":
    main(*sys.argv[1:6])
