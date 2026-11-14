"""Phase 17: join OpenStreetMap buildings and building parts to the county footprints of the targets.

Usage:
    python -B -P phase17_osm_join.py <phase17 data folder> <out csv>

Reads osm/osm_*.json (Overpass "out tags geom") and county/county_footprints_2022_viewbox.json. For each target of
targets.csv, every OSM way or relation tagged building or building:part whose outline overlaps the county outline
by at least 30 percent of the smaller of the two is joined; the building's name, address, height, levels, material,
colour, roof colour and shape, architect, start date and wikidata/wikipedia keys are collected (parts listed too).
Data (c) OpenStreetMap contributors, ODbL 1.0.
"""

import csv
import glob
import json
import os
import sys

from shapely.geometry import Polygon
from shapely.strtree import STRtree
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

KEYS = ["name", "alt_name", "addr:housenumber", "addr:street", "height", "building:levels", "building:material",
        "building:colour", "building:facade:material", "facade:material", "roof:colour", "roof:material", "roof:shape",
        "architect", "start_date", "wikidata", "wikipedia", "building", "building:part"]


def ring(geom):
    pts = [g.state_plane_from_lat_lon(p["lat"], p["lon"]) for p in geom]
    if len(pts) < 4:
        return None
    try:
        poly = Polygon(pts).buffer(0)
    except Exception:
        return None
    return poly if poly.area > 1.0 else None


def elements(folder):
    seen = {}
    for path in sorted(glob.glob(os.path.join(folder, "osm", "osm_*.json"))):
        for el in json.load(open(path, encoding="utf-8")).get("elements", []):
            key = (el["type"], el["id"])
            if key in seen:
                continue
            tags = el.get("tags", {})
            if not ("building" in tags or "building:part" in tags):
                continue
            poly = None
            if el["type"] == "way" and "geometry" in el:
                poly = ring(el["geometry"])
            elif el["type"] == "relation":
                outers = [ring(m["geometry"]) for m in el.get("members", []) if m.get("role") == "outer" and "geometry" in m]
                inners = [ring(m["geometry"]) for m in el.get("members", []) if m.get("role") == "inner" and "geometry" in m]
                outers = [p for p in outers if p is not None]
                if outers:
                    poly = unary_union(outers)
                    for h in inners:
                        if h is not None:
                            poly = poly.difference(h)
            if poly is not None and not poly.is_empty:
                seen[key] = {"type": el["type"], "id": el["id"], "tags": tags, "poly": poly}
    return list(seen.values())


def main(argv):
    base, out = argv[1], argv[2]
    els = elements(base)
    tree = STRtree([e["poly"] for e in els])
    county = {str(f["attributes"]["OBJECTID"]): f for f in json.load(open(os.path.join(base, "county", "county_footprints_2022_viewbox.json")))["features"]}
    rows = list(csv.DictReader(open(os.path.join(base, "targets.csv"), encoding="utf-8")))
    outrows = []
    for r in rows:
        f = county.get(r["bldg_id"])
        if f is None:
            continue
        outline = unary_union([Polygon(x).buffer(0) for x in f["geometry"]["rings"]])
        joined = []
        for i in tree.query(outline):
            e = els[int(i)]
            inter = e["poly"].intersection(outline).area
            if inter >= 0.3 * min(e["poly"].area, outline.area):
                joined.append((inter, e))
        joined.sort(key=lambda t: -t[0])
        bldgs = [e for _, e in joined if "building" in e["tags"]]
        parts = [e for _, e in joined if "building:part" in e["tags"]]
        main_el = bldgs[0] if bldgs else (parts[0] if parts else None)
        row = {"bldg_id": r["bldg_id"], "osm": "%s/%s" % (main_el["type"], main_el["id"]) if main_el else "",
               "osm_buildings": len(bldgs), "osm_parts": len(parts)}
        tags = dict(main_el["tags"]) if main_el else {}
        # Fill blanks from the other joined buildings and parts (a part often carries the material).
        for e in bldgs[1:] + parts:
            for k in KEYS:
                if k not in tags and k in e["tags"] and k not in ("name", "building:part", "building"):
                    tags[k] = e["tags"][k]
        for k in KEYS:
            row[k] = tags.get(k, "")
        row["part_names"] = "; ".join(sorted({e["tags"].get("name", "") for e in parts if e["tags"].get("name")}))
        row["part_heights"] = "; ".join(sorted({e["tags"].get("height", "") for e in parts if e["tags"].get("height")}))
        outrows.append(row)
    keys = ["bldg_id", "osm", "osm_buildings", "osm_parts"] + KEYS + ["part_names", "part_heights"]
    with open(out, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=keys)
        w.writeheader()
        w.writerows(outrows)
    named = sum(1 for r in outrows if r["name"])
    mat = sum(1 for r in outrows if r["building:material"] or r["building:facade:material"] or r["facade:material"])
    col = sum(1 for r in outrows if r["building:colour"])
    print("targets", len(rows), "joined", sum(1 for r in outrows if r["osm"]), "named", named, "material", mat, "colour", col)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
