"""Phase 20: what the reference photographs show, building by building, and the material settings that follow.

Usage: python -B -P phase20_observations.py <worklist csv> <commons_index csv> <out building table csv> <out params json>

OBS holds, for each work-list building whose photographs were looked at (contact sheets of up to three files per
tower, J4), what they show and the settings chosen from it. Colours are judged on lit facade areas of the photographs
and written as sRGB (0-255); they are converted to linear here, the form the material instances take, and clamped to
a plausible albedo (0.02 to 0.80). Floor height is the building's height divided by its storey count where a count
is published (OpenStreetMap building:levels, or the count named in the note). Only instance parameters change; the
facade parent is not touched. A building not in OBS keeps its Phase 17 settings; its confidence follows its Phase 17
source (2 when a public description or the Assessor named the material, 1 when assumed by building type).
"""

import csv
import json
import sys

DATA = "E:/Wieland1529_site_data/phase17"

# county id: (photographs (file title fragments), what they show, settings, confidence, note)
OBS = {
    "889662": ("Skyline de Chicago desde el centro", "black tower: black-tinted glass in black anodised aluminium, as the Phase 17 research said",
               {}, 4, "confirmed; no change"),
    "861246": ("Merchandise Mart Chicago.jpg; Chicago in 2022 Merchandise Mart", "tan limestone-coloured masonry, grid of punched windows, green roof pavilions",
               {"FrameColor": (190, 175, 150), "FloorHeight": 5.0}, 4, "masonry darker and warmer than the Phase 17 value; 18 storeys on 108 m incl. tower"),
    "879467": ("Chicago in 2022 Part of the Accenture", "blue reflective glass in silver aluminium mullions, cascading glass top",
               {"FrameColor": (170, 175, 180), "GlassColor": (60, 90, 120), "GlassMetallic": 0.4, "FloorHeight": 4.17}, 4, "42 storeys"),
    "840907": ("Chicago IMG 1030", "cream precast piers and spandrels, balconies, blue-grey glass",
               {"FrameColor": (215, 200, 165), "GlassColor": (80, 100, 120), "FrameWidth": 0.5, "BayWidth": 1.6, "FloorHeight": 3.86}, 3,
               "17 storeys; one photograph (text search on the name)"),
    "837303": ("North Branch Chicago River 2023; Architecture boat tour", "long cream concrete loft block with red-brown horizontal spandrel bands and punched windows (the former Montgomery Ward catalogue house, 'ECHO' sign)",
               {"FrameColor": (225, 215, 195), "GlassColor": (55, 65, 75), "FrameWidth": 0.6, "BayWidth": 1.8, "FloorHeight": 4.2}, 3,
               "identified from geotagged photographs; the red-brown bands cannot be shown separately by the facade parent"),
    "716911": ("Retrofitted Garbage trucks with sno", "pale grey precast grid with dark punched windows", {"FrameColor": (200, 200, 195), "GlassColor": (45, 55, 65), "FrameWidth": 0.5, "BayWidth": 1.6, "FloorHeight": 3.0}, 2,
               "identified from one geotagged photograph within 150 m; the building is not named in any source"),
    "821651": ("2015 Chicago 43", "light warm-grey stone tower with setbacks and punched windows (not a glass curtain wall)",
               {"FrameColor": (175, 170, 160), "GlassColor": (60, 70, 82), "FrameWidth": 0.6, "BayWidth": 1.8, "SpandrelHeight": 1.2, "FrameRoughness": 0.8, "FloorHeight": 3.54}, 4,
               "60 storeys; the Phase 17 assumption (glass) corrected"),
    "864465": ("Construction on the Salesforce Towe; Chicago River @ Wolf Po", "blue-grey clear glass curtain wall with silver vertical fins",
               {"FrameColor": (175, 180, 185), "GlassColor": (70, 95, 115), "FrameWidth": 0.12, "GlassMetallic": 0.3, "FloorHeight": 4.33}, 4, "61 storeys"),
    "785344": ("SONO Chicago", "dark grey frames and slab bands with blue-grey glass", {"FrameColor": (60, 62, 66), "GlassColor": (80, 100, 120), "FrameWidth": 0.15, "FloorHeight": 2.9}, 4,
               "residential floors about 2.9 m"),
    "869193": ("Grant Park, Chicago, Illinois, Esta", "white tower (white granite cladding), as the Phase 17 research said", {}, 4, "confirmed; no change"),
    "869122": ("Two Prudential Plaza Chicago; Two Prudential Plaza (2638855469)", "light grey granite piers, blue-grey reflective glass, chevron top with spire",
               {"FrameColor": (190, 190, 192), "GlassColor": (90, 110, 135), "FrameWidth": 0.5, "BayWidth": 1.6, "GlassMetallic": 0.3, "FloorHeight": 4.07}, 4,
               "64 storeys; the Phase 17 assumption corrected"),
    "829659": ("Neely Building 2021", "light grey precast frame with large windows and balconies, behind the Neely Building", {"FrameColor": (170, 170, 168), "GlassColor": (75, 90, 105), "FrameWidth": 0.5, "FloorHeight": 3.2}, 2,
               "identified from geotagged photographs within 150 m; the same photographs fall within 150 m of county 822893, so the match is not certain"),
    "863915": ("Chicago River confluence 20190522", "blue-tinted glass with silver vertical mullion bands (under construction in 2019)", {}, 4, "confirmed; no change"),
    "864161": ("Chicago in 2022 The Residences at R", "curved tower of light blue glass with white horizontal balcony bands", {"FrameColor": (210, 212, 215), "FloorHeight": 3.61}, 4, "38 storeys; frame lightened to white"),
    "836153": ("One Chicago 20240629", "light blue glass with silver-white vertical fins and grey frames", {"FrameColor": (200, 203, 207), "GlassColor": (95, 125, 155), "FrameWidth": 0.15, "GlassMetallic": 0.3, "FloorHeight": 3.9}, 4,
               "the Phase 17 assumption corrected; about 76 storeys"),
    "871124": ("155 North Wacker Chicago 2021", "blue-grey reflective flush curtain wall with thin silver mullions", {"FrameColor": (170, 175, 180), "GlassColor": (90, 115, 140), "FrameWidth": 0.1, "GlassMetallic": 0.35, "FloorHeight": 4.3}, 4, "45 storeys"),
    "869294": ("150 N RiversidePlaza 8 26 16", "dark blue-grey highly reflective glass, thin mullions", {"GlassMetallic": 0.4, "FloorHeight": 4.13}, 4, "54 storeys; colours confirmed"),
    "861432": ("Chicago - Alta Towers at K Station", "light cool-grey precast with grey-blue punched glass", {"FrameColor": (205, 207, 208), "GlassColor": (85, 100, 115), "FrameWidth": 0.6, "BayWidth": 1.8, "FloorHeight": 3.4}, 4, "37 storeys"),
    "871090": ("151 North Franklin from Ra", "blue reflective glass curtain wall with thin dark mullions", {"GlassColor": (105, 135, 160), "GlassMetallic": 0.35, "FloorHeight": 4.37}, 4, "36 storeys; glass darker than the Phase 17 value"),
    "863968": ("Chicago River @ Wolf Po", "dark blue-black glass with silver horizontal bands", {"GlassColor": (45, 55, 65), "FloorHeight": 3.04}, 3, "48 storeys"),
}

# Photographs looked at that settled nothing (shown for the record in the table).
INCONCLUSIVE = {
    "886111": "aerial and street photographs within 150 m do not show the tower's facade clearly",
    "710227": "geotagged street photographs at Clark and Fullerton; which tower is in them cannot be told",
    "861253": "river photographs: the tower is too small or hidden",
    "863806": "railway photographs; the tower is not in them",
    "878101": "the photographs show the neighbouring Accenture Tower more than this one",
    "884598": "photographs of a neighbouring building (10 S Canal) and the Citigroup arch",
    "822893": "photographs of the Neely Building; the tower behind may be this one or Parc Chestnut",
    "850491": "a ballroom and distant views",
    "835665": "photographs of Water Tower Place and the John Hancock Center",
    "847101": "a brick loft and a white tower; which is Gallery 400 cannot be told",
    "734344": "street photographs at the 1929 massacre site; the tower is not in them",
    "862529": "river photographs; this tower cannot be picked out",
    "808684": "photographs of nearby low buildings and a station",
    "697781": "church interior photographs",
    "878315": "supermarket interior and a parade",
    "827738": "street photographs near State Street; the tower cannot be picked out",
    "821801": "park and Lynch House photographs",
    "881912": "subway sign, hotel interior, a march",
    "869202": "unrelated photographs (power lines, trains)",
}


def lin(c):
    c = c / 255.0
    v = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return round(min(max(v, 0.02), 0.80), 4)


def main(argv):
    worklist, index, out_table, out_params = argv[1:5]
    wl = list(csv.DictReader(open(worklist, encoding="utf-8")))
    idx = list(csv.DictReader(open(index, encoding="utf-8")))
    tm = {r["bldg_id"]: r for r in csv.DictReader(open(DATA + "/tower_materials.csv", encoding="utf-8"))}
    zm = {r["bldg_id"]: r for r in csv.DictReader(open(DATA + "/zone12_materials_v2.csv", encoding="utf-8"))}
    rows, params = [], {}
    for r in wl:
        bid = r["county_id"]
        if r["group"] == "skyline":
            p17 = json.loads(tm[bid]["params"])
            assumed = tm[bid]["assumption"] == "yes"
            base_conf = 1 if assumed else 2
            mi = "MI_P17_T_" + bid
        else:
            p17 = json.loads(zm[bid]["params"]) if zm.get(bid, {}).get("params") else {}
            assumed = zm.get(bid, {}).get("material_assumed") == "yes"
            base_conf = 1 if assumed else 2
            mi = zm.get(bid, {}).get("instance") or ("MI_P17_Z_" + bid)
        mine = [x for x in idx if bid in x["buildings"].split()]
        if bid in OBS:
            frags, shows, sets, conf, note = OBS[bid]
            used = [x for x in mine if any(f.strip() and f.strip() in x["title"] for f in frags.split(";"))]
            new = dict(p17)
            for k, v in sets.items():
                new[k] = [lin(c) for c in v] if isinstance(v, tuple) else v
            if sets:
                params[mi] = {k: new[k] for k in sets}
            change = "; ".join("%s %s -> %s" % (k, p17.get(k, "default"), new[k]) for k in sets) or "none (confirmed)"
            still_assumed = "no"
        else:
            used, shows, change, conf = [], INCONCLUSIVE.get(bid, "no photograph of this building found" if r["group"] == "skyline"
                                                            else "no photograph of its facade on Wikimedia Commons; KartaView has none within 540 m"), "none", base_conf
            note = "Phase 17 setting kept"
            still_assumed = "yes" if assumed else "colour" if r["group"] != "skyline" else "no"
        rows.append({"group": r["group"], "rank": r["rank"], "county_id": bid, "name": r["name"], "instance": mi,
                     "photographs": " | ".join("%s (%s, %s, %s)" % (x["title"].replace("File:", ""), x["licence"], x["author"][:40] or "author not given", x["page_url"]) for x in used),
                     "what_they_show": shows, "settings_changed": change, "details_added": "none", "confidence": conf,
                     "still_assumed": still_assumed, "note": note})
    with open(out_table, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    json.dump(params, open(out_params, "w", encoding="utf-8"), indent=1)
    conf = [r["confidence"] for r in rows]
    print(json.dumps({"buildings": len(rows), "instances_changed": len(params),
                      "confidence": {c: conf.count(c) for c in sorted(set(conf))},
                      "photographs_used": sum(1 for r in rows if r["photographs"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
