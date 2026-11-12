"""Phase 5 acceptance: texel density of 20 sampled surfaces against the plan's table.

    python -B phase5_texel_density.py <material_tests.csv> <material_audit.csv> <largest_surfaces.json>
                                      <texel_density.csv>

Texel density is how many image pixels fall on one metre of a surface. The
sample is fixed by a rule, not picked by hand: of the candidates that carry
an image with a physical size and are placed in the level, the 20 whose
largest placed object is largest (longest side times second side). For each,
the surface sampled is that object.

Required density, from the plan's table: 1,024 pixels per metre for interior
surfaces and for exterior surfaces a station sees from within 3 m; 512 for
other surfaces of Zone 1 (the whole building is in Zone 1). A surface counts
as exterior when the Revit category of its object is a roof, a site or
topography element, or a wall, floor, railing, stair or generic model whose
name carries "Exterior", "Masonry", "Siding", "Parapet", "Coping", "Site",
"Deck", "Fence" or "Paving"; everything else counts as interior. It counts
as within 3 m of a station when the centre of the object's bounding box is
less than 3 m plus half the object's longest side from station S1, S3 or S6
(the stations rendered in this phase), measured in plan. Both rules are
coarse and are written into each row, so that a row can be argued with.

Two readings of "within 25 percent" are given: not more than 25 percent
below the table (a denser image is not a defect), and within 25 percent
either way. The Revit material's own density is given beside the
candidate's, read from the audit's sentence where the audit measured it.
"""

import csv
import json
import math
import re
import sys

STATIONS = {"S1": (-754.4, 1400.0), "S3": (-3254.4, 1400.0), "S6": (-3508.8, 210.0)}
EXTERIOR_WORDS = ("exterior", "masonry", "siding", "parapet", "coping", "site", "deck", "fence", "paving")
EXTERIOR_CATEGORIES = ("roofs", "site", "topography")


def main(tests_csv, audit_csv, surfaces_json, out_csv):
    with open(tests_csv, encoding="utf-8", newline="") as handle:
        tests = list(csv.DictReader(handle))
    with open(audit_csv, encoding="utf-8", newline="") as handle:
        audit = {row["material"]: row for row in csv.DictReader(handle)}
    with open(surfaces_json, encoding="utf-8") as handle:
        surfaces = json.load(handle)
    pool = []
    for row in tests:
        surface = surfaces.get(row["material"])
        if not surface or not row["pixels_per_metre"] or max(surface["largest_m"]) <= 0:
            continue
        pool.append((surface["largest_m"][0] * surface["largest_m"][1], row, surface))
    pool.sort(key=lambda item: (-item[0], item[1]["material"]))
    rows = []
    for _area, row, surface in pool[:20]:
        label = surface["object"]
        low = label.lower()
        exterior = low.startswith(EXTERIOR_CATEGORIES) or any(word in low for word in EXTERIOR_WORDS)
        x, y = surface["at_cm"][0], surface["at_cm"][1]
        name, distance = min(((n, math.hypot(x - sx, y - sy) / 100.0) for n, (sx, sy) in STATIONS.items()),
                             key=lambda item: item[1])
        near = distance < 3.0 + surface["largest_m"][0] / 2.0
        required = 1024 if (not exterior or near) else 512
        density = float(row["pixels_per_metre"])
        found = re.search(r"\(([\d,]+) pixels per metre\)", audit.get(row["material"], {}).get("confidence_reason", ""))
        revit = found.group(1).replace(",", "") if found else ""
        rows.append({
            "material": row["material"],
            "sampled_object": label,
            "object_sides_m": "%.2f x %.2f" % tuple(surface["largest_m"]),
            "counts_as": "exterior" if exterior else "interior",
            "nearest_station": "%s, %.1f m from the object's centre" % (name, distance),
            "within_3_m_of_a_station": "yes" if near else "no",
            "required_pixels_per_metre": required,
            "candidate_pixels_per_metre": int(density),
            "candidate_against_required_percent": round(100.0 * density / required - 100.0),
            "not_more_than_25_percent_below": "yes" if density >= 0.75 * required else "no",
            "within_25_percent_either_way": "yes" if 0.75 * required <= density <= 1.25 * required else "no",
            "revit_material_pixels_per_metre": revit,
            "revit_not_more_than_25_percent_below": ("" if not revit else
                                                     "yes" if float(revit) >= 0.75 * required else "no"),
        })
    with open(out_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    below = sum(1 for r in rows if r["not_more_than_25_percent_below"] == "yes")
    both = sum(1 for r in rows if r["within_25_percent_either_way"] == "yes")
    with_revit = [r for r in rows if r["revit_material_pixels_per_metre"]]
    revit_ok = sum(1 for r in with_revit if r["revit_not_more_than_25_percent_below"] == "yes")
    print("%d sampled; candidate not more than 25%% below the table: %d; within 25%% either way: %d; "
          "Revit material measured in the audit: %d, of which not more than 25%% below: %d" % (
              len(rows), below, both, len(with_revit), revit_ok))


if __name__ == "__main__":
    main(*sys.argv[1:5])
