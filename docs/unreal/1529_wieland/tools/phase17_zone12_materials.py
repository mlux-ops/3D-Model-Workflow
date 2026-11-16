"""Phase 17, step 17.3: one wall and one roof material description per Zone 1 and 2 building.

Usage:
    python -B -P phase17_zone12_materials.py <phase17 data folder> <out csv>

Order of evidence for the wall: (1) OpenStreetMap building:material / building:colour (osm_join_zone12.csv);
(2) the Cook County Assessor's exterior wall (assessor\\zone12_assessor.csv: Masonry, Frame, Frame + Masonry,
Stucco), which settles the material but not the colour; (3) for buildings the Assessor does not describe
(condominiums, commercial, larger apartment buildings), brick with punched windows, an assumption.
Colours are never in the records: each building takes one colour from a palette for its material, chosen by its
county id so that neighbours differ, and is labelled an assumption for the owner's site photographs to settle.
Roof: Assessor roof covering where given (shingle pitched, else flat membrane or gravel); otherwise flat for
masonry and pitched shingle for frame houses, an assumption.
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase17_materials import lin, params_for  # noqa: E402

BRICK = ["#8a4a3c", "#7a5a45", "#96583f", "#6e4436", "#a0705a", "#b38d6c", "#5e3b30", "#8c6a52", "#a35d48"]
SIDING = ["#d9d4c7", "#8c9399", "#6b7a6e", "#c8b48e", "#4a5a6a", "#e6dcc3", "#7d4038", "#b9b2a2", "#3f4a44"]
STUCCO = ["#d8cbb0", "#cfc6b5", "#e0d6c0"]
ROOFS = {"shingle": "MI_P17_Roof_Shingle", "flat": "MI_P17_Roof_Flat"}


def pick(palette, bid):
    return palette[int(bid) % len(palette)]


def house(params):
    # houses and flats: smaller windows on wider piers than the tower default
    params.update({"FloorHeight": 3.1, "BayWidth": 2.4, "FrameWidth": 1.4, "SpandrelHeight": 1.0})
    return params


def main(argv):
    base, out = argv[1], argv[2]
    targets = list(csv.DictReader(open(os.path.join(base, "targets_zone12.csv"), encoding="utf-8")))
    osm = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(base, "osm_join_zone12.csv"), encoding="utf-8"))}
    ass = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(base, "assessor", "zone12_assessor.csv"), encoding="utf-8"))}
    rows = []
    for t in targets:
        bid = t["bldg_id"]
        o, a = osm.get(bid, {}), ass.get(bid, {})
        name = o.get("name") or ("%s %s" % (o.get("addr:housenumber", ""), o.get("addr:street", ""))).strip()
        mat = (o.get("building:material") or o.get("building:facade:material") or "").lower()
        colour = o.get("building:colour", "")
        wall = a.get("ext_wall", "")
        sources = []
        if mat:
            sources.append("OpenStreetMap building:material=%s" % mat)
        if wall:
            sources.append("Cook County Assessor %s: exterior wall %s (%s), built %s" % (YEAR, wall, a.get("ext_wall_votes", ""), a.get("year_built", "")))
        if mat in ("wood", "timber", "vinyl", "siding") or (not mat and wall == "Frame"):
            material = "painted siding"
            hexs = colour or pick(SIDING, bid)
        elif not mat and wall == "Stucco":
            material = "stucco"
            hexs = colour or pick(STUCCO, bid)
        elif mat in ("glass", "metal", "steel"):
            material = mat
            hexs = colour or "#4a5560"
        else:
            material = "brick" if (mat in ("brick", "") ) else mat
            hexs = colour or pick(BRICK, bid)
            if wall == "Frame + Masonry":
                material = "brick (front) with siding"
        kind = "curtain_wall_glass" if material in ("glass", "metal", "steel") else "punched_windows_masonry"
        p = params_for(kind, hexs, None, None)
        if kind != "curtain_wall_glass":
            p = house(p)
            if material == "painted siding":
                p.update({"FrameRoughness": 0.6, "FrameVariation": 0.06})
            elif material == "stucco":
                p.update({"FrameRoughness": 0.9, "FrameVariation": 0.05})
        roof_src = a.get("roof", "")
        if roof_src:
            roof = "shingle" if "Shingle" in roof_src or "Slate" in roof_src or "Shake" in roof_src else "flat"
        else:
            roof = "shingle" if material == "painted siding" else "flat"
        material_known = bool(mat or wall)
        rows.append({"bldg_id": bid, "zone": t["zone"], "name": name, "distance_m": t["distance_m"],
                     "wall_material": material, "wall_material_source": "; ".join(sources) or "assumption: brick, the commonest wall in Old Town",
                     "wall_colour_hex": hexs, "colour_source": ("OpenStreetMap building:colour" if colour else "assumption: palette for %s, by county id" % material),
                     "roof": roof, "roof_source": ("Assessor roof covering: " + roof_src) if roof_src else "assumption from wall type",
                     "material_assumed": "no" if material_known else "yes", "colour_assumed": "no" if colour else "yes",
                     "instance": "MI_P17_Z_%s" % bid, "roof_instance": ROOFS[roof], "params": json.dumps(p)})
    with open(out, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    z1 = [r for r in rows if r["zone"] == "1"]
    print(json.dumps({"rows": len(rows), "material_known": sum(r["material_assumed"] == "no" for r in rows),
                      "zone1_material_known": sum(r["material_assumed"] == "no" for r in z1), "zone1": len(z1),
                      "colour_known": sum(r["colour_assumed"] == "no" for r in rows),
                      "by_material": {m: sum(r["wall_material"] == m for r in rows) for m in sorted({r["wall_material"] for r in rows})}}))
    return 0


YEAR = "2025"

if __name__ == "__main__":
    sys.exit(main(sys.argv))
