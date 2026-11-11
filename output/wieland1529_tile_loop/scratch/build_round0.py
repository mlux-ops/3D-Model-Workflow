"""Build source-backed, provisional Round 0 packets for 1529 Wieland.

Reads only this loop's copied source files; makes no model or API calls.
Refuses to overwrite existing room packets. Room dimensions remain provisional
until the actual 1529 model document and element ids are verified.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scratch" / "sources"
TILE_HANDOFF = "HANDOFF_1529_Wieland_Tile.md, v4 selection / v7 takeoff, Google Drive 12gJwYBe70RT8xjwjp9jpzBwvPad1iiMS"
TILE_SHEET = "FINISH DATABASE - 1527 Wieland (rows for job 25-006 1529 Wieland), Smartsheet 8569278453206916, read 2026-11-06"
PLUMBING_SHEET = "Smartsheet 8569278453206916, plumbing rows, read 2026-11-06"
DECK = "1529_Wieland_Fixtures_v3_2.pdf, Google Drive 1XBZwGrspwZFDZ7jicgCe41FVjNBxPhLS"

def data(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))

TROWS = {str(row["row_id"]): row for row in data("smartsheet_tile_rows_20261106.json")["rows"]}
PROWS = {
    "Penthouse": data("smartsheet_plumbing_ph_20261106.json")["rows"],
    "Triplex": data("smartsheet_plumbing_tx_20261106.json")["rows"],
}

# The codes below come from v4 schedule. For future versions, update the
# underlying schedule first, then review any changes explicitly.
PRODUCTS = {
    "FT1": "Cortar Bone 24x48 Anti-Slip",
    "FT2": "Cortar Clay 24x48 Anti-Slip",
    "FT3": "Cortar Grey 12x24 Soft",
    "FT4": "Cortar Bone 12x24 Soft",
    "FT5": "Cortar Clay 12x24 Soft",
    "FT6": "Cortar Charcoal 12x24 Anti-Slip",
    "WT1": "Cortar Bone 24x48 Soft",
    "WT2": "Cortar Bone Reed dimensional",
    "WT3": "Cortar Clay 24x48 Soft",
    "WT4": "Cortar Clay Ribbed dimensional",
    "WT5": "Tones Sapphire 2x20 Glossy stacked",
    "WT6": "Tones Opal 2x20 Glossy stacked",
    "WT7": "Tones Copper 2x20 Glossy stacked",
    "WT8": "Tones Emerald 2x20 Glossy stacked",
    "WT9": "Cortar Bone Ribbed 24x48 dimensional",
    "WT10": "Cortar Charcoal 24x48 Soft",
    "WT11": "Vera Forma Earth Lines 2x10 relief",
    "WT12": "Haze Camel + Wheat 1.6x5 matte stacked mix",
    "WT13": "Vera Forma Indigo Edge 6x6 relief",
    "AT1": "Clara Tierra Madre Caviar 2x8 zellige",
    "AT2": "Tones Sandstone 2x20 Glossy",
}
ROOMS = [
    # id, unit, room name, A/B room numbers, area, area basis,
    # wet-zone type, dimensions (W,D) feet, previously derived tiled wall LF,
    # tile codes by surface, Smartsheet leaf row ids
    ("PH-PRIMARY","Penthouse","Primary Bathroom",["304A","304B"],103,"prior Revit area",
     "corner shower",(5.854,4.646),10.50,
     {"wall":["WT1","WT2"],"floor":["FT1"],"ceiling":["WT1"],"accent":[]},
     {"wall":"4302621473570692","floor":"2715002737917828","accent":"6554421287255940"}),
    ("PH-BATH2","Penthouse","Bath 2",["305A","305B"],35,"prior Revit area",
     "tub alcove",(4.958,2.55),10.06,
     {"wall":["WT5"],"floor":["FT3"],"ceiling":[],"accent":["AT2"]},
     {"wall":"8806221100941188","floor":"221234311266180","accent":"7218602365288324"}),
    ("PH-BATH3","Penthouse","Bath 3",["307A","307B"],35,"prior Revit area",
     "tub alcove",(5.0,2.33),9.67,
     {"wall":["WT6"],"floor":["FT4"],"ceiling":[],"accent":["AT2"]},
     {"wall":"4724833938636676","floor":"2473034124951428","accent":"1589102831075204"}),
    ("PH-BATH4","Penthouse","Bath 4",["311A","311B"],35,"owner 35 SF; prior Revit 27 SF conflict",
     "walk-in shower",(5.0,2.54),10.08,
     {"wall":["WT9"],"floor":["FT6"],"ceiling":[],"accent":["AT1"]},
     {"wall":"6976633752321924","floor":"1347134218108804","accent":"6092702458445700"}),
    ("PH-POWDER","Penthouse","Powder Room",["405A","405B"],28,"prior Revit area",
     "powder vanity wall",None,4.224,
     {"wall":["WT11"],"floor":[],"ceiling":[],"accent":[]},
     {"vanity_wall":"6851772612214660"}),
    ("PH-WC","Penthouse","Primary WC",["313A","313B"],15,"prior Revit area",
     "WC floor only",None,None,
     {"wall":[],"floor":["FT1"],"ceiling":[],"accent":[]},{}),
    ("TX-PRIMARY","Triplex","Primary Bathroom",["202A","202B"],87,"prior Revit area",
     "corner shower",(5.1875,4.7708),9.96,
     {"wall":["WT3","WT4"],"floor":["FT2"],"ceiling":["WT3"],"accent":[]},
     {"wall":"8102533659164548","floor":"784184264687492","accent":"3840902644760452"}),
    ("TX-BATH2","Triplex","Bath 2",["205A","205B"],38,"prior Revit area",
     "tub alcove",(5.207,2.60),10.41,
     {"wall":["WT7"],"floor":["FT5"],"ceiling":[],"accent":["AT2"]},
     {"wall":"3035984078372740","floor":"7539583705743236","accent":"8344502272130948"}),
    ("TX-BATH3","Triplex","Bath 3",["207A","207B"],37,"prior Revit area",
     "tub alcove",(5.10,2.60),10.30,
     {"wall":["WT8"],"floor":["FT3"],"ceiling":[],"accent":["AT2"]},
     {"wall":"6413683798900612","floor":"4161883985215364","accent":"1026152877653892"}),
    ("TX-BATH4","Triplex","Bath 4",["007A","007B"],38.5,"prior Revit area",
     "tub alcove",(5.0,2.54),10.08,
     {"wall":["WT10","WT9"],"floor":["FT4"],"ceiling":[],"accent":["AT1"]},
     {"wall":"502709287976836","floor":"5006308915347332","accent":"5529752505024388"}),
    ("TX-POWDER","Triplex","Powder Room",["102A","102B"],22.5,"prior Revit area",
     "powder vanity wall",None,2.990,
     {"wall":["WT12"],"floor":[],"ceiling":[],"accent":[]},
     {"vanity_wall":"4966802551603076"}),
    ("TX-POWDER2","Triplex","Powder 2",["009A","009B"],27,"prior Revit area",
     "powder vanity wall",None,3.806,
     {"wall":["WT13"],"floor":[],"ceiling":[],"accent":[]},
     {"vanity_wall":"7258108729032580"}),
    ("TX-WC","Triplex","Primary WC",["203A","203B"],14,"203B prior Revit area; 203A unplaced",
     "WC floor only",None,None,
     {"wall":[],"floor":["FT2"],"ceiling":[],"accent":[]},{}),
]
DECK_PAGE = {
    "PH-PRIMARY":1, "PH-BATH2":2, "PH-BATH3":3, "PH-BATH4":4,"PH-POWDER":5,
    "TX-PRIMARY":7, "TX-BATH2":8, "TX-BATH3":9, "TX-BATH4":10,
    "TX-POWDER":11,"TX-POWDER2":12
}
SINKS_UNSELECTED = {"PH-BATH3","TX-BATH2","TX-POWDER2"}
PRIMARY_NO_ACCENT = {"PH-PRIMARY","TX-PRIMARY"}
WET_GAPS = {
    "PH-PRIMARY": ["Cortar Bone Reed WT2 wet-wall listing absent; no feature-area split.",
                   "Primary shower 24x48 floor slope, drain location and wet DCOF must be validated."],
    "TX-PRIMARY": ["Cortar Clay Ribbed WT4 wet-wall listing absent; no feature-area split.",
                   "Primary shower 24x48 floor slope, drain location and wet DCOF must be validated."],
    "PH-BATH3": ["Tones Opal WT6 tub-wall wet-area listing unverified.", "Sink unselected."],
    "PH-BATH4": ["Cortar Bone Ribbed WT9 wet-wall listing absent; quoted order quantity unconfirmed.",
                  "Clara Caviar AT1 niche wet-area listing absent.", "35/27 SF room-area discrepancy.",
                  "FT6 Anti-Slip v4 contradicts live sheet Soft description."],
    "TX-BATH2": ["Sink unselected."],
    "TX-BATH4": ["Clara Caviar AT1 niche wet-area listing absent.",
                  "Cortar Bone Ribbed WT9 accent area not quantified within Charcoal field.",
                  "Drawing takeoff is tub alcove, not shower."],
    "TX-POWDER2": ["Sink unselected."],
}
FINISH_RE = re.compile(
    r"Brilliance Black Onyx|Brushed Black Chrome|Brushed Gold Optic|Matte White|Luxe Gold|"
    r"Polished Chrome|Satin Nickel|Chrome|Cotton|Matte Black|Gloss White", re.I)
BRANDS = ["Victoria + Albert", "Hansgrohe", "Westbrass", "Duravit", "Brizo",
          "AXOR","GROHE","TOTO","Delta"]

def field(value, unit, provenance, note=None):
    return {"value":value,"unit":unit,
            "classification":provenance,
            "live_revit_verified":False,
            "source":TILE_HANDOFF,
            "note":note}

def room_walls(kind, dims, length):
    if kind in ("WC floor only",):
        return []
    if kind == "powder vanity wall":
        return [("vanity feature wall",length)]
    if kind == "corner shower":
        return [("shower wall A; orientation unverified",dims[0]),
                ("shower wall B; orientation unverified",dims[1])]
    return [("tub back wall; assumed",dims[0]),("tub return wall left; assumed",dims[1]),
            ("tub return wall right; assumed",dims[1])]

def geometry(r):
    room_id, unit, name, numbers, area, area_basis, kind, dims, run, tiles, ids = r
    tiled_height = 7.75 if kind=="tub alcove" else 9.25
    walls = []
    for i,(description,length) in enumerate(room_walls(kind,dims,run),1):
        walls.append({
            "id":"W"+str(i),
            "revit_element_id":None,
            "description":description,
            "length":field(length,"ft","drawing-derived / assumed"),
            "height":field(9.25,"ft","drawing-derived","Ceiling 9'-3 \" from seven prior elevation sheets"),
            "tiled_height":field(tiled_height,"ft","assumed tub deck or drawing-derived ceiling"),
            "openings":None, "niches":None,"window_sills":None,
            "openings_measurement_status":"unknown",
            "niches_measurement_status":"unknown",
            "window_sills_measurement_status":"unknown",
            "wall_finish_revit_type":None,
        })
    footprint = None
    if dims:
        footprint = {
            "kind":kind,
            "width":field(dims[0],"ft","drawing-derived / assumed"),
            "depth":field(dims[1],"ft","drawing-derived / assumed"),
            "revit_fixture_element_ids":[],
            "orientation":None,
        }
    return {
        "room_id":room_id,
        "unit_type":unit,
        "copies":2,
        "revit_room_numbers":numbers,
        "revit_room_element_ids":None,
        "model_identity_verified":False,
        "floor_area":field(area,"SF","owner override" if "owner" in area_basis else "prior Revit-derived / unverified",area_basis),
        "ceiling_height":field(9.25,"ft","drawing-derived"),
        "tiled_walls":walls,
        "wet_zone_tiled_wall_run":field(run,"linear ft","drawing-derived / assumed") if run is not None else None,
        "shower_or_tub_footprint":footprint,
        "shower_floor_drain_type":None,
        "shower_floor_drain_location":None,
        "floor_finish": "wood, no tile" if "POWDER" in room_id else "scheduled tile",
        "ceiling_tiling": "shower ceiling only" if kind=="corner shower" else "none",
        "finish_schedule_revit_ids":[],
        "source_caveat":"Dimensions copied from a prior handoff that reports Revit measurements; the currently open model and its element ids have not been verified.",
        "geometry_gaps":[
           "Current Revit model identity and element IDs not verified.",
           "Door/window/opening widths, heights, jambs and sill elevations missing.",
           "Actual niche sizes and locations missing.",
           "Shower drain position and slope design not measured.",
           "Existing wall finish layers and floor types not queried.",
           "Wall orientation and fixture coordinate locations not measured."
        ],
    }

def plumbing(r):
    room_id,unit,name,_,_,_,kind,_,_,_,_ = r
    if room_id.endswith("-WC"):
        # WC is a separate room but the general 'Primary Bathroom' rows combine
        # its toilet with bathroom fixtures; no fixtures are duplicated.
        return {
            "room_id":room_id,"source":PLUMBING_SHEET,"deck_page":None,
            "fixtures":[],"unselected_fixtures":[],
            "notes":["WC is floor-only. Primary Bathroom plumbing group includes the toilet; separate room attribution requires Revit room location data."],
        }
    fixtures = []
    missing_sinks = []
    for row in PROWS[unit]:
        if row.get("Room Type") != name: continue
        rawname=(row.get("Primary Column") or "").strip()
        sku=(row.get("SKU") or "").strip()
        if rawname.casefold() in ("sink","bathroom 2","bathroom 3","bathroom 4",
                                  "primary bathroom","powder room","powder 2"):
            if rawname.casefold()=="sink": missing_sinks.append({"fixture":"sink/basin","selection":None,"source_row_id":row["row_id"]})
            continue
        if not sku: continue
        maker=next((b for b in BRANDS if re.search(r"\b"+re.escape(b)+r"\b",rawname,re.I)),None)
        found=FINISH_RE.search(rawname)
        finish=found.group(0) if found else None
        notes=(row.get("PM Notes") or "").strip()
        descoped=bool(re.search(r"\bDESCOPED\b",notes,re.I))
        fixtures.append({
            "description":re.sub(r"\s+"," ",rawname),
            "manufacturer":maker,
            "model_or_sku":sku,
            "finish":finish,
            "finish_status":"specified in row" if finish else "not explicit in row; verify with fixture deck or manufacturer",
            "qty_per_unit":float(row["Qty"]) if row.get("Qty") not in (None,"") else None,
            "source":PLUMBING_SHEET,
            "source_row_id":row["row_id"],
            "deck_reference":{"source":DECK,"page":DECK_PAGE.get(room_id)},
            "status":"historical / descoped" if descoped else "sheet-listed; purchase/installation status unverified",
            "notes":notes[:320] if notes else None
        })
    # Three unselected basins are explicit user constraints, even when the sheet
    # does not have a separate 'Sink' placeholder.
    if room_id in SINKS_UNSELECTED and not missing_sinks:
        missing_sinks.append({"fixture":"sink/basin","selection":None,
                              "source_row_id":None,"reason":"owner brief explicitly unselected"})
    special = []
    if room_id=="PH-POWDER":
        special.append("Current Smartsheet Brizo Luxe Gold faucet differs from AXOR Brushed Gold Optic proposed alternative on deck page 5; do not promote the deck proposal without approval.")
    if room_id in ("PH-PRIMARY","TX-PRIMARY","PH-BATH4"):
        special.append("Fixture deck contains both current selections and proposed AXOR brand-transfer alternatives. Only Smartsheet rows are carried.")
    if room_id in ("PH-BATH3","TX-BATH3") and kind=="tub alcove":
        special.append("Plumbing row includes a tile-in square shower drain although tile takeoff calls this a tub alcove; verify the actual fixture and wet-floor scope.")
    if missing_sinks: special.append("Sink/basin unselected; tile remains provisional. Do not select a basin on behalf of owner.")
    return {"room_id":room_id,"unit_type":unit,"source":PLUMBING_SHEET,
            "deck_source":DECK,"deck_page":DECK_PAGE.get(room_id),
            "fixtures":fixtures,"unselected_fixtures":missing_sinks,
            "notes":special}

def quote_rows(r):
    ids=r[-1]; result=[]; base=0.0
    for surface, row_id in ids.items():
        row=TROWS.get(row_id)
        if not row: raise ValueError("Missing tile row "+row_id)
        qty=float(row["Qty"]) if row.get("Qty") not in (None,"") else None
        rate=float(row["Acutal Unit Cost"]) if row.get("Acutal Unit Cost") not in (None,"") else None
        historical = surface=="accent" and r[0] in PRIMARY_NO_ACCENT
        subtotal=round(qty*rate,2) if qty is not None and rate is not None and not historical else None
        if subtotal is not None:base+=subtotal
        result.append({
            "surface":surface, "smartsheet_row_id":row_id,
            "carried_description":row.get("Primary Column"),
            "qty_sf_per_unit":qty,"quoted_rate_usd_per_sf":rate,
            "extended_quote_cost_usd_per_unit":subtotal,
            "sheet_cost_of_good_sold":float(row["Cost of Good Sold"]) if row.get("Cost of Good Sold") not in (None,"") else None,
            "source":TILE_SHEET,
            "v4_scope_status":"historical, excluded: no primary niche scope" if historical else "quoted row; reconcile to v4",
            "note":"Quoted quantities may differ from physically confirmed installed area; takeoff includes 15% waste, accents require niche layout confirmation."
        })
    return result,round(base,2)

def room_gaps(r):
    room_id,unit,name,_,_,_,kind,_,_,tiles,_=r
    gaps=list(WET_GAPS.get(room_id,[]))
    if kind=="tub alcove": gaps.append("Tub alcove wet-wall lengths and deck height are drawing-derived, not live Revit measurements.")
    if kind=="powder vanity wall": gaps.append("Vanity wall length is drawing-derived and not validated against Revit openings.")
    if kind=="WC floor only":gaps.append("WC area is included in primary floor quoted quantity; do not duplicate material cost.")
    if kind=="corner shower":gaps.append("Primary niches/accent are outside the schedule; do not add any niche product or quantity.")
    if tiles["floor"]: gaps.append("Floor tile wet DCOF >=0.42 has not been independently confirmed from a current manufacturer document.")
    if tiles["accent"]: gaps.append("Accent/niche area and location require confirmed measured layout; cannot add to wall field quantity.")
    return gaps

def champion(r, quoted):
    room_id,unit,name,_,_,_,kind,_,_,tiles,_=r
    lines=[f"# {room_id}: tile schedule v4 seed", "",
           "**Status:** seeded — provisional; no board score or owner approval.", "",
           f"**Source:** {TILE_HANDOFF}", "",
           f"**Basis:** {kind}. Each room represents the two {unit} units (A/B); takeoffs are per unit.", "",
           "| Surface | v4 code | Specified tile |", "|---|---|---|"]
    for surf,codes in tiles.items():
        for code in codes:
            lines.append(f"| {surf} | {code} | Elm Surfaces {PRODUCTS[code]} |")
    if not tiles["floor"]:lines.append("| floor | — | No tile: wood floor outside scope |")
    if not tiles["wall"]:lines.append("| wall | — | No wall tile |")
    lines+=["",
            "Selection is copied from v4. Smartsheet quoted row rates and quantities are stored in state/ROOMS.json and kept separately from unverified Revit dimensions.",
            "",
            "## Gaps and release holds"]
    lines += ["- "+x for x in room_gaps(r)]
    if room_id=="PH-PRIMARY":
        lines += ["- Live Smartsheet quotes blended 24x48 Soft floor plus 12x24 Anti-Slip pan, but v4 specifies Anti-Slip over the entire floor. Do not silently replace v4."]
    if room_id=="TX-PRIMARY":
        lines += ["- Live Smartsheet quotes blended 24x48 Soft floor plus 12x24 Anti-Slip pan, but v4 specifies Anti-Slip over the entire floor. Do not silently replace v4."]
    if room_id=="TX-BATH4":
        lines += ["- Live quote carries a Charcoal field, but its description does not split the v4 Bone Ribbed accent. Accent must displace field SF, not add wall area."]
    lines += ["",
              "## Evaluation",
              "- Weighted board score: not yet scored.",
              "- Tile DCOF and wet-area gating: pending current product evidence.",
              "- Manufacturer availability and project stock: verify.",
              "- Geometry cut/sliver and drain slope gates: pending model validation.",
              "- Cost gate: quoted baseline is available, but owner has not stated the bath tile upgrade allowance.",
              "- No purchase or substitution authorized.",
              ""]
    return "\n".join(lines)

def write_once(path,obj_or_text):
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("Out-of-run output path")
    if path.exists():
        raise FileExistsError("Existing packet must be preserved: "+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(obj_or_text,str):
        path.write_text(obj_or_text,encoding="utf-8")
    else:
        path.write_text(json.dumps(obj_or_text,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    assert len(ROOMS)==13
    assert all(r.get("Job Numbers")=="25-006 1529 Wieland" for r in TROWS.values() if r.get("Room Type"))
    state = {
      "_note":"Provisional 1529 tile loop Round 0 inventory. Actual Revit project identity and every dimension must be checked before design/layout acceptance.",
      "as_of":"2026-11-06",
      "price_band":{"PH":{"sale_price_usd":2800000,"unit_count":2},
                    "TX":{"sale_price_usd":2700000,"unit_count":2},
                    "comps_target_min_usd":2400000,"comps_target_max_usd":3200000},
      "tile_budget_upgrade_stance":None,
      "tile_budget_upgrade_stance_reason":"state/OWNER_FEEDBACK.md says FILL IN",
      "revit_project_check":{
        "status":"blocked_unverified","model_project_name":None,
        "model_project_number":None,"model_project_address":None,
        "model_document_title":None,"model_document_path":None,
        "document_session_id":None,
        "observed_revit_process":"Revit 2025 running; document identity unknown",
        "blocker":"No Revit named read tools available. H: native Revit integration is outside CoS approved roots.",
        "fallback_geometry_source":TILE_HANDOFF
      },
      "source_reconciliation":[
        {"issue":"Sheet title 1527 vs 1529","observed":"Smartsheet title FINISH DATABASE - 1527 Wieland; tile and plumbing rows job number 25-006 1529 Wieland","status":"identity caution"},
        {"issue":"Primary floor finish mismatch","observed":"v4 whole-floor Anti-Slip; Smartsheet row blended Soft floor and Anti-Slip pan","status":"unresolved"},
        {"issue":"PH Bath 4 floor finish mismatch","observed":"v4 Cortar Charcoal Anti-Slip; Smartsheet quote Cortar Charcoal Soft","status":"unresolved"},
        {"issue":"Niche quantities","observed":"v4 says niche layouts unconfirmed; Smartsheet has priced accent quantity estimates","status":"provisional"},
      ],
      "source_documents":{"tile_schedule":TILE_HANDOFF,"tile_quote":TILE_SHEET,"plumbing":PLUMBING_SHEET,"fixtures_deck":DECK},
      "rooms":[]
    }
    dest = ROOT/"rooms"
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError("Existing room inventory found; refusing overwrite")
    for room in ROOMS:
        room_id,unit,name,numbers,area,area_basis,kind,dims,run,tiles,ids=room
        quoted,base = quote_rows(room)
        g=geometry(room)
        p=plumbing(room)
        if room_id.endswith("-PRIMARY"):
            assert not tiles["accent"]
        if room_id.endswith("-POWDER") or room_id.endswith("-POWDER2"):
            assert not tiles["floor"]
        if room_id=="TX-BATH4":assert kind=="tub alcove"
        folder=dest/room_id
        write_once(folder/"geometry.json",g)
        write_once(folder/"plumbing.json",p)
        write_once(folder/"champion.md",champion(room,quoted))
        write_once(folder/"history.md",f"# {room_id} history\n\n- 2026-11-06 Round 000: seeded from governing tile schedule v4. Live geometry unavailable; no scored board round yet.\n")
        state["rooms"].append({
            "id":room_id,"unit_type":unit,"room_name":name,
            "unit_count":2,"revit_room_numbers":numbers,
            "status":"seeded","owner_status":None,
            "champion_id":"v4-"+room_id,"champion_score":None,
            "last_round":0,
            "floor_area_sf_prior":area,
            "floor_area_status":area_basis+"; live Revit unverified",
            "tiled_wall_run_lf_prior":run,
            "carried_tile_rows":quoted,
            "carried_quote_material_subtotal_usd_per_unit":base,
            "carried_budget_material_only_usd_per_unit":None,
            "carried_budget_missing_reason":"Sheet has a tile-section budget, but no per-room allocated budget; provisional quote subtotal shown separately.",
            "open_gaps":room_gaps(room),
            "no_sink_selection":room_id in SINKS_UNSELECTED
        })
    write_once(ROOT/"state"/"ROOMS_R000_PROPOSED.json",state)
    print(json.dumps({"rooms":len(ROOMS),"room_ids":[r[0] for r in ROOMS],
       "per_unit_tile_quote_subtotals_usd":{"PH":round(sum(x["carried_quote_material_subtotal_usd_per_unit"] for x in state["rooms"] if x["unit_type"]=="Penthouse"),2),
                                              "TX":round(sum(x["carried_quote_material_subtotal_usd_per_unit"] for x in state["rooms"] if x["unit_type"]=="Triplex"),2)},
       "state_candidate":"state/ROOMS_R000_PROPOSED.json",
       "live_revit_verified":False},indent=2))

if __name__=="__main__":
    main()
