"""Phase 17: one facade material description per skyline building, for the instances of M_W1529_P17_Facade.

Usage:
    python -B -P phase17_materials.py <phase17 data folder> <out csv>

Order of evidence: (1) tower_materials_research.csv (public descriptions: Wikipedia, architects, CTBUH; colours
estimated from Commons photographs where so noted), (2) OpenStreetMap tags from osm_join.csv (building:material,
building:colour), (3) an assumption from the building's height (taller than 60 m: glass and light concrete;
otherwise brick with punched windows), marked "assumption" for the owner. Colours are sRGB hex in the sources and
written as linear values for the engine. The window grid: curtain walls 1.5 m bays with thin frames; punched
windows in masonry about 1.0 by 1.9 m per 1.8 m bay; ribbon windows continuous; precast grids with 0.5 m frames.
"""

import csv
import json
import os
import re
import sys

HEX = re.compile(r"#?([0-9a-fA-F]{6})")
NAMED = {"black": "#1e1e1e", "white": "#e8e6e1", "grey": "#8c8c8c", "gray": "#8c8c8c", "lightgrey": "#c3c3c0",
         "darkgrey": "#4a4a4a", "beige": "#cbb89a", "brown": "#7a5a45", "red": "#8a4a3c", "blue": "#4a6a8a",
         "silver": "#b8bcc0", "tan": "#c2a77f", "cream": "#e6dcc3", "bronze": "#6a5236", "green": "#4f6b5b"}
MATERIAL_HEX = {"glass": "#3c4a55", "brick": "#8a5a44", "concrete": "#a8a49c", "limestone": "#d8cdb5",
                "masonry": "#b9a98f", "granite": "#9a8d82", "marble": "#ddd6cc", "metal": "#8f969c",
                "steel": "#6f767c", "stone": "#c4b8a3", "aluminium": "#9aa0a6", "aluminum": "#9aa0a6"}


def lin(hexs, fallback):
    m = HEX.search(hexs or "")
    if not m:
        key = (hexs or "").strip().lower()
        if key in NAMED:
            m = HEX.search(NAMED[key])
    if not m:
        m = HEX.search(fallback)
    v = m.group(1)
    return tuple(round((int(v[i:i + 2], 16) / 255.0) ** 2.2, 4) for i in (0, 2, 4))


def params_for(kind, wall_hex, glass_hex, frame_hex, floor_h=None, bay=None):
    if kind == "curtain_wall_glass":
        return {"GlassColor": lin(glass_hex, "#3c4a55"), "FrameColor": lin(frame_hex or wall_hex, "#5a6066"),
                "FloorHeight": floor_h or 3.9, "BayWidth": bay or 1.5, "FrameWidth": 0.10, "SpandrelHeight": 0.9,
                "GlassRoughness": 0.06, "FrameRoughness": 0.4, "FrameMetallic": 0.3, "GlassVariation": 0.3, "FrameVariation": 0.08}
    if kind == "ribbon_windows":
        return {"GlassColor": lin(glass_hex, "#2c3238"), "FrameColor": lin(wall_hex, "#b0aca4"),
                "FloorHeight": floor_h or 3.8, "BayWidth": bay or 1.5, "FrameWidth": 0.06, "SpandrelHeight": 1.3,
                "GlassRoughness": 0.08, "FrameRoughness": 0.8, "GlassVariation": 0.35, "FrameVariation": 0.1}
    if kind == "precast_grid":
        return {"GlassColor": lin(glass_hex, "#2a3036"), "FrameColor": lin(wall_hex, "#bdb6aa"),
                "FloorHeight": floor_h or 3.6, "BayWidth": bay or 1.6, "FrameWidth": 0.5, "SpandrelHeight": 1.1,
                "GlassRoughness": 0.08, "FrameRoughness": 0.8, "GlassVariation": 0.35, "FrameVariation": 0.1}
    # punched windows in masonry or concrete
    return {"GlassColor": lin(glass_hex, "#262b30"), "FrameColor": lin(wall_hex, "#8a5a44"),
            "FloorHeight": floor_h or 3.2, "BayWidth": bay or 1.8, "FrameWidth": 0.8, "SpandrelHeight": 1.1,
            "GlassRoughness": 0.1, "FrameRoughness": 0.85, "GlassVariation": 0.4, "FrameVariation": 0.12}


def num(v):
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def main(argv):
    base, out = argv[1], argv[2]
    targets = list(csv.DictReader(open(os.path.join(base, "targets.csv"), encoding="utf-8")))
    osm = {r["bldg_id"]: r for r in csv.DictReader(open(os.path.join(base, "osm_join.csv"), encoding="utf-8"))}
    research = {}
    rpath = os.path.join(base, "tower_materials_research.csv")
    if os.path.exists(rpath):
        research = {r["county_id"].strip(): r for r in csv.DictReader(open(rpath, encoding="utf-8"))}
    recs = {}
    rec_path = os.path.join(base, "meshes_towers", "towers_record.jsonl")
    if os.path.exists(rec_path):
        for line in open(rec_path, encoding="utf-8"):
            r = json.loads(line)
            recs[r["id"]] = r
    rows = []
    for t in targets:
        bid = t["bldg_id"]
        o = osm.get(bid, {})
        name = o.get("name") or o.get("part_names") or ("%s %s" % (o.get("addr:housenumber", ""), o.get("addr:street", ""))).strip()
        top = recs.get(bid, {}).get("top_incl_masts_m") or float(t["roof_height_m_dsm6ft"] or 0)
        r = research.get(bid)
        if r and r.get("facade_type"):
            kind = r["facade_type"].strip()
            p = params_for(kind, r.get("primary_colour_hex"), r.get("glass_colour_hex"), r.get("frame_colour_hex"),
                           num(r.get("floor_to_floor_m")), num(r.get("bay_width_m")))
            if kind.startswith("punched") or kind == "mixed":
                p["FrameColor"] = lin(r.get("primary_colour_hex"), "#8a5a44")
            src = "research (%s): %s" % (r.get("confidence", ""), r.get("source_urls", "")[:200])
            desc = "%s; %s; glass %s" % (kind, r.get("primary_material", ""), r.get("glass_tint", ""))
            assumption = (r.get("confidence", "").strip().lower() == "low")
        else:
            mat = (o.get("building:material") or o.get("building:facade:material") or o.get("facade:material") or "").lower()
            colour = o.get("building:colour", "")
            if mat:
                kind = "curtain_wall_glass" if mat in ("glass", "metal", "steel", "aluminium", "aluminum") else "punched_windows_masonry"
                wall_hex = colour or MATERIAL_HEX.get(mat, "#a8a49c")
                p = params_for(kind, wall_hex, colour if kind == "curtain_wall_glass" else None, None)
                src = "OpenStreetMap %s: building:material=%s%s" % (o.get("osm", ""), mat, (", building:colour=" + colour) if colour else "")
                desc = "%s; %s" % (kind, mat)
                assumption = not colour
            elif top >= 60.0:
                kind = "curtain_wall_glass"
                p = params_for(kind, "#a8a49c", colour or "#4a5560", "#a8a49c")
                src = "assumption: tower over 60 m, glass and light concrete" + ((", building:colour=" + colour) if colour else "")
                desc = "%s (assumed)" % kind
                assumption = True
            else:
                kind = "punched_windows_masonry"
                p = params_for(kind, colour or "#8a5a44", None, None)
                src = "assumption: building under 60 m, brick with punched windows" + ((", building:colour=" + colour) if colour else "")
                desc = "%s (assumed)" % kind
                assumption = True
        rows.append({"bldg_id": bid, "name": name, "distance_m": t["distance_m"], "top_m": top, "kind": kind,
                     "description": desc, "assumption": "yes" if assumption else "no", "source": src,
                     "params": json.dumps(p)})
    with open(out, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("rows", len(rows), "research", sum(1 for r in rows if r["source"].startswith("research")),
          "osm", sum(1 for r in rows if r["source"].startswith("OpenStreetMap")),
          "assumed", sum(1 for r in rows if r["assumption"] == "yes"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
