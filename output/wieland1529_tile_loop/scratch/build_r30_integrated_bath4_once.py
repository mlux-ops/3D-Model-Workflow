"""One-time ADDITIVE R30 PH4/TX4 construction + 13-room package creator.

Never rerun after signing. No source document, existing round, model, or vendor writes.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "deliverables" / "integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement"
assert not OUT.exists(), "R30 full package already exists; never regenerate or overwrite signed output"
R17 = BASE / "deliverables" / "integrated-r17"
R29 = BASE / "deliverables" / "integrated-r29-sandstone-niche-shared-cutstock"
ROOMS = json.loads((BASE / "state" / "ROOMS.json").read_text(encoding="utf-8"))["rooms"]
ORIGINAL = list(csv.DictReader((R17 / "R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig", newline="")))
WALLS = list(csv.DictReader((R17 / "R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig", newline="")))
RELEASE = list(csv.DictReader((R29 / "R29_13_ROOM_CONDITIONAL_SOURCE_MAKER_TRADE_AND_PURCHASE_RELEASE.csv").open(encoding="utf-8-sig", newline="")))
assert len(ROOMS) == 13 and len(ORIGINAL) == 27 and len(WALLS) == 25 and len(RELEASE) == 13
money = lambda r: Decimal(r.get("historic_usd_two_copies") or "0")
assert sum(map(money, ORIGINAL)) == Decimal("23572.44")
FOCUS = ("PH-BATH4", "TX-BATH4")
NICHES = [r for r in ORIGINAL if r["room"] in FOCUS and r["source_surface"] == "accent"]
assert len(NICHES) == 2
assert sum(Decimal(r["source_gross_sf_one_copy_waste_15pct_once"]) * 2 for r in NICHES) == Decimal("34.52")
assert sum(map(money, NICHES)) == Decimal("1163.32")
assert sum(not bool(r["historic_usd_two_copies"]) for r in ORIGINAL) == 2
W = {(r["room"], r["wall"]): r for r in WALLS}
assert W["PH-BATH4", "W1"]["source_width_in_UNVERIFIED"] == "60.0"
assert W["PH-BATH4", "W3"]["source_width_in_UNVERIFIED"] == "30.48"
assert W["TX-BATH4", "W3"]["source_width_in_UNVERIFIED"] == "30.48"

URL = {
    "caviar": "https://traditionsintile.com/project/clara/",
    "arto_wall": "https://www.arto.com/site/downloads/Installation/ARTO%20CLARA%20Tierra%20Madre%20Installation%20on%20Walls.pdf",
    "arto_2026": "https://www.arto.com/site/downloads/ARTO-pricelist-web/Price%20List%202026_WEB_03022026.pdf",
    "ivory": "https://www.elmsurfaces.com/product/soho-ivory",
    "black": "https://www.elmsurfaces.com/product/soho-black",
    "bone_ribbed": "https://www.elmsurfaces.com/product/bone-ribbed-cortar",
    "bone": "https://www.elmsurfaces.com/product/cortar-bone",
    "charcoal": "https://www.elmsurfaces.com/product/cortar-charcoal",
    "brizo": "https://www.brizo.com/bath/product/BT062415-BNX",
    "duravit": "https://pro.duravit.us/pro/content/homepage/series/sizes/overview/products~402880943a1b6e1b013a1bd2b8e3005b.us-en.html?ncat=undefined&nser=1110&product=3169419",
    "spout": "https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-with-diverter-72411701",
    "ibox": "https://www.hansgrohe-usa.com/articledetail-ibox-universal-rough-with-service-stops-01850181",
}
FILES: dict[str, bytes] = {}
def write_md(name: str, content: str) -> None:
    FILES[name] = (content.strip() + "\n").encode("utf-8")
def write_csv(name: str, rows: list[dict]) -> None:
    assert rows and len({tuple(row.keys()) for row in rows}) == 1, name
    s = io.StringIO(newline="")
    w = csv.DictWriter(s, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    FILES[name] = s.getvalue().encode("utf-8-sig")
def f4(value: float) -> str:
    return f"{value:.4f}"
def flag(value: bool) -> str:
    return "TRUE" if value else "FALSE"

# Exact maker classes; collection and general installation instructions are not individually approved niches.
maker = [
    ("ARTO / Traditions", "Clara Tierra Madre Caviar 2x8", "Original historic NICHE", "Ceramic distressed, 1/2 inch body approx 13 mm; 2026 catalog physical face 1-3/4 x 8-1/8 inch", "COLLECTION_WALL_WET_SYSTEM_GUIDE_ONLY; CAVIAR_2X8_INDIVIDUAL_NICHE_UNVERIFIED", "UNVERIFIED", "NOT_A_FLOOR_TEST", "NOT_A_PAN_TEST", "2026 ARTO generic factory CLARA-TIERRAMADRE2X8; not confirmed color-specific order code", "100 pieces/box and 9 pieces/SF only at catalog 1/4in joints; precise Caviar lot coverage unverified", "MANUFACTURER_2026_SUGGESTED_RETAIL", "37.15_USD_PER_SF_CATALOG_1_4IN_JOINT", URL["caviar"] + " ; " + URL["arto_wall"] + " ; " + URL["arto_2026"]),
    ("ELM Surfaces", "Soho Ivory 2x10 Glossy", "Conditional NOT owner selected NICHE", "Porcelain collection 2x10; 9.5 mm body nominal", "ITEM_PAGE_WET_AREAS_WALLS_LISTED; NICHE_GEOMETRY_AND_SYSTEM_NOT_APPROVED", "LISTED_WET_WALL_WITH_SHOP_HOLD", "NOT_A_FLOOR_TEST", "NOT_A_PAN_TEST", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", URL["ivory"]),
    ("ELM Surfaces", "Soho Black 2x10 Glossy", "Third independent alternative NOT owner selected NICHE", "Porcelain collection 2x10; 9.5 mm body nominal", "ITEM_PAGE_WET_AREAS_WALLS_LISTED; NICHE_GEOMETRY_AND_SYSTEM_NOT_APPROVED", "LISTED_WET_WALL_WITH_SHOP_HOLD", "NOT_A_FLOOR_TEST", "NOT_A_PAN_TEST", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", URL["black"]),
    ("ELM Surfaces", "Cortar Bone Ribbed 24x48 Relief", "PH4 historical wet WALL", "9 mm body; relief pattern", "ITEM_PAGE_WALLS_BACK_SPLASHES_ONLY; NO_WET_AREAS_LISTED", "NOT_LISTED_FOR_WET_WALL_HOLD", "NOT_A_FLOOR_TEST", "NOT_A_PAN_TEST", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", URL["bone_ribbed"]),
    ("ELM Surfaces", "Cortar Bone flat 24x48 Soft/AntiSlip variant not resolved", "PH4 conditional replacement wet WALL", "Flat Bone page separately lists Wet Areas and Soft/Anti-Slip; exact surface variant required", "FLAT_BONE_ITEM_PAGE_WET_AREAS_LISTED; NOT_TRANSFERABLE_TO_RIBBED", "LISTED_WET_WALL_WITH_EXACT_FINISH_HOLD", "RAW_NUMERIC_UNKNOWN", "RAW_NUMERIC_UNKNOWN_POINT_PAN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", URL["bone"]),
    ("ELM Surfaces", "Cortar Charcoal flat 24x48 Soft", "TX4 historical tub-surround WALL", "Flat Charcoal item page has Wet Areas", "ITEM_PAGE_WET_AREAS_WALLS_LISTED; CONFIRM_24X48_SOFT_AND_TUB_SYSTEM", "LISTED_WET_WALL_WITH_EXACT_FINISH_HOLD", "NOT_A_FLOOR_TEST", "TUB_PAN_N_A", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", URL["charcoal"]),
    ("Brizo", "BT062415-BNX 4in Tile-In Square POINT", "PH4 OWNER SELECTED DRAIN", "Brilliance Black Onyx, PVC/brass, adjustable upper, 2in PVC connection", "POINT_DRAIN_ITEM_CONFIRMED; WATERPROOF_FLANGE_COMPATIBILITY_NOT_PROVEN", "NOT_TILE", "NOT_A_FLOOR_TEST", "POINT_PAN_TILE_RAW_NUMERIC_UNKNOWN", "BT062415-BNX CONFIRMED", "N_A", "MANUFACTURER_LIST", "166_USD_DRAIN_ONLY_NOT_INSTALLED", URL["brizo"]),
    ("Duravit", "700332000000090 Starck built-in tub 59x29.5in", "TX4 OWNER SELECTED TUB", "Acrylic drop-in includes support frame; 59 x 29.5 nominal; tub flange option manufacturer lists 790112", "TUB_LISTED; FLANGE_AND_WALL_SECTION_SPECIFIC_SIGNOFF_REQUIRED", "NOT_TILE", "LEVEL_TILE_RAW_NUMERIC_UNKNOWN", "TUB_PAN_N_A", "700332000000090 CONFIRMED", "N_A", "MANUFACTURER_LIST", "1550_USD_TUB_ONLY_NOT_INSTALLED", URL["duravit"]),
    ("Hansgrohe", "72411701 Talis S tub spout w diverter Matte White", "TX4 OWNER SELECTED TUB SPOUT", "Maker explicitly says for use with pressure balance valve ONLY; source trim 15758701 is thermostatic", "THERMOSTATIC_VS_PRESSURE_BALANCE_SPEC_CONFLICT_REQUIRES_MANUFACTURER_PLUMBING_RESOLUTION", "NOT_TILE", "LEVEL_TILE_RAW_NUMERIC_UNKNOWN", "TUB_PAN_N_A", "72411701 CONFIRMED", "N_A", "MANUFACTURER_LIST", "382_USD_SPOUT_ONLY_NOT_INSTALLED", URL["spout"]),
    ("Hansgrohe", "01850181 iBox universal rough", "TX4 OWNER SCHEDULED ROUGH", "¾-in NPT universal rough; selected 15758701 thermostatic trim compatibility must be confirmed", "EXACT_TRIM_SPOUT_SWITCHING_CONFIGURATION_NEEDS_MAKER_PLUMBER_SIGNOFF", "NOT_TILE", "N_A", "TUB_PAN_N_A", "01850181 CONFIRMED", "N_A", "MANUFACTURER_LIST", "228_USD_ROUGH_ONLY_NOT_INSTALLED", URL["ibox"]),
]
cols = ["manufacturer","exact_named_product","original_or_condition","nominal_factory_evidence","individual_wet_permission_and_limits","wet_wall_or_niche_gate","raw_LEVEL_wet_DCOF","raw_POINT_or_LINEAR_PAN_wet_DCOF","maker_item_code_color_lot_status","factory_case_evidence","price_source_class","price_value_and_scope","official_source_URLs"]
write_csv("R30_10_MANUFACTURER_INDIVIDUAL_WET_APPLICATION_DRAIN_TUB_AND_COST_SOURCES.csv", [dict(zip(cols, x)) for x in maker])

tiers = [
("PH-BATH4","GOOD","Retain historical dark Clara Caviar niche and Bone Ribbed relief surround","Caviar CAVIAR_NICHE_HOLD; Bone Ribbed NO_WET_AREAS_LISTED","Unchanged historical Brizo BT062415-BNX Black Onyx POINT, WALK-IN","Retains handmade high-contrast depth; relief accent reads bespoke","Not installable as presented in wet shower; dark niche irregular edge/13mm change complicate exposed returns","Original historical palette comparison ONLY; obtain individual maker wet wall/niche letters; do not price as releasable","Historical material-only carried, no owner change / no additional PO"),
("PH-BATH4","BETTER","Soho Ivory 2x10 Glossy niche, verified flat Bone wet-wall candidate, flush front with fitted profile","Soho Ivory Wet Areas item PASS for WALL; flat Bone separate Wet Areas item PASS; exact finish/system/owner HOLD","WALK-IN Brizo BT062415-BNX POINT with independent 4-plane PAN; preserve plumbing","Light niche reduces dark void, flatter wall supports clean wipe-down and simpler edge bedding","Contrasts less than Caviar; 9.5mm niche body vs 9mm Ribbed and unknown flat Bone body; shop edge depth and 1:1 cut","Require owner color change + full wet wall selection; full niche four-return HYDRO BAN or manufacturer matched membrane detail","Current exact Soho SKU/lot/Chicago quote/bid UNKNOWN; no savings claim"),
("PH-BATH4","BEST","Soho Black 2x10 Glossy niche, flat Bone individually wet-listed wall candidate, coordinated four-sided thin-profile frame","Soho Black individually lists Wet Areas; flat Bone individually Wet Areas; no construction-system approval yet","WALK-IN Brizo BT062415-BNX POINT, no reversible BT062418 rough transfer","Maintains deliberate near-black niche focal contrast without unlisted Caviar; 2x10 improves module flexibility","Dark joints/shade lot need full board; exposed glossy cut edges must be protected; no installer pricing","1:1 factory 2x10 calibrated trim with four miters vs square-cut profile mockups; select approved membrane and soft joint locations","Premium workmanship/bid UNKNOWN, no invented buyer premium"),
("TX-BATH4","GOOD","Retain historical Caviar 2x8 contrast niche against Cortar Charcoal flat surround","Charcoal flat item Wet Areas listed; original Caviar CAVIAR_NICHE_HOLD","Duravit 700332000000090 TUB/Hansgrohe Matte White, NO tiled PAN","Original warm dark contrast and hand-crafted movement","Caviar individual niche wet proof absent; 13mm irregular exposed edges; spout pressure balance versus trim thermostat HOLD","Historical concept comparison only; field verify actual tub flange, all niches and plumbing; no installed release","Historical material-only carried; original 15% already present"),
("TX-BATH4","BETTER","Soho Ivory 2x10 niche with Charcoal flat wet-listed surround and compact 12-16in carefully framed niche","Soho Ivory Wet Areas PASS at individual item; flat Charcoal PASS; system/owner HOLD","Same Duravit 59in TUB Matte White trim, no shower drain or PAN","Lighter legible toiletry niche, balanced against charcoal and white tub; simpler maintenance","Strong light/dark contrast not all buyers; nominal 9.5mm niche vs surrounding wall unknown thickness; tub rim plane must be measured","Waterproofing to actual tub flange, upward-sloped? NO: niche SILL slopes inward to TUB, actual slope per approved detail; spout behind waterproof return only if plumb verified","Actual Soho net/box/premium/labor UNKNOWN"),
("TX-BATH4","BEST","Soho Black 2x10 niche within Charcoal wet-listed wall, dark monolithic field with deliberate recessed perimeter profile","Soho Black individually Wet Areas listed; Charcoal flat separately listed; not owner-approved","Same Duravit and Matte White Hansgrohe; repair valve/spout incompatibility by signed manufacturer-specific solution, no silent substitution","Minimizes visual material proliferation, stronger dark stone-like monochrome appearance","Black tile/charcoal color mismatch in real lighting can be conspicuous; profiles and grout depth more workmanship-sensitive","Provide 1:1 charcoal+black+white-tub light test, measured flange/rough and miter section; architect owner fixture coordination signoff","Labor and trims additional scope requires bid, no confirmed premium"),
]
tier_cols = ["room","tier","proposed_unselected_design","separate_wet_WALL_and_NICHE_application_gate","nonnegotiable_owner_fixture_program","owner_visual_and_maintenance_tradeoff","hard_construction_or_selection_risk","specific_field_maker_mockup_release_action","price_and_procurement_class"]
write_csv("R30_6_PH4_TX4_OWNER_GOOD_BETTER_BEST_CREDIBLE_ALTERNATIVES.csv", [dict(zip(tier_cols,t)) for t in tiers])

# Factory-dimensioned and alternative orientation modules: 3 niche maker options x 2 walls x 2 axes x 3 joints x 2 rooms = 72;
# plus 24x48 original wall-face cut controls 2x2x3=12, total 84.
MAT = {
 "CAVIAR_2X8": (8.125,1.75,13.0,URL["caviar"],"FACTORY_2026_1_3_4_BY_8_1_8_NOT_NOMINAL_2X8"),
 "SOHO_IVORY_2X10": (10.0,2.0,9.5,URL["ivory"],"MAKER_NOMINAL_2X10_NOT_CALIBER_MEASUREMENT"),
 "SOHO_BLACK_2X10": (10.0,2.0,9.5,URL["black"],"MAKER_NOMINAL_2X10_NOT_CALIBER_MEASUREMENT"),
}
def cuts(w:float, tile:float, j:float, minimum:float):
    candidates=[]
    for n in range(int(w / (tile+j))+1):
        end=(w-n*tile-(n+1)*j)/2
        if 0 < end <= tile+1e-8:
            candidates.append((n,end))
    valid=[x for x in candidates if x[1] >= minimum]
    return (max(valid,key=lambda x:x[0]) if valid else (max(candidates,key=lambda x:x[1]) if candidates else (0,-1)))
modules=[]
for room in FOCUS:
    for wall in ("W1","W3"):
        ww=float(W[room,wall]["source_width_in_UNVERIFIED"])
        hh=float(W[room,wall]["source_tiled_height_in_UNVERIFIED"])
        for product, (long_edge, short_edge, thick, src, quality) in MAT.items():
            for orientation, face in [("LONG_AXIS_ACROSS_WALL",long_edge),("SHORT_AXIS_ACROSS_WALL",short_edge)]:
                focal=face>=3
                target=3.0 if focal else 0.75
                for joint in (.125,.1875,.25):
                    n,end=cuts(ww,face,joint,target)
                    modules.append(dict(room=room,wall=wall,source_width_in_UNVERIFIED=f4(ww),source_height_in_UNVERIFIED=f4(hh),product=product,
                      manufacturer_face_length_on_this_axis_in=f4(face),tile_orientation=orientation,joint_in_ILLUSTRATIVE=f4(joint),joint_maker_APPROVED="UNVERIFIED",
                      full_middle_tiles=n,balanced_end_face_each_in=f4(end),target_visible_end_in=f4(target),
                      focal_min_3in_applies=flag(focal),focal_test="PASS_PROVISIONAL" if end>=target else "FAIL_PROVISIONAL",
                      raw_cut_formula="(SOURCE_W-N*FACTORY_OR_NOMINAL_FACE-(N+1)*JOINT)/2",tile_dimension_quality=quality,
                      tile_body_thickness_mm_NOMINAL=f4(thick),actual_caliber_mortar_trim_verified="FALSE",true_1529_field_verified="FALSE",owner_approved="FALSE",purchase_authorized="FALSE",source_url=src))
        product="PH4_FLAT_BONE_24X48_ORIGINAL_RIBBED_HOLD" if room.startswith("PH") else "TX4_CHARCOAL_FLAT_24X48"
        for joint in (.125,.1875,.25):
            n,end=cuts(ww,24.0,joint,3.0)
            modules.append(dict(room=room,wall=wall,source_width_in_UNVERIFIED=f4(ww),source_height_in_UNVERIFIED=f4(hh),product=product,
              manufacturer_face_length_on_this_axis_in="24.0000",tile_orientation="24IN_AXIS_ACROSS_WALL",joint_in_ILLUSTRATIVE=f4(joint),joint_maker_APPROVED="UNVERIFIED",
              full_middle_tiles=n,balanced_end_face_each_in=f4(end),target_visible_end_in="3.0000",focal_min_3in_applies="TRUE",
              focal_test="PASS_PROVISIONAL" if end>=3 else "FAIL_PROVISIONAL",raw_cut_formula="(SOURCE_W-N*24-(N+1)*JOINT)/2",
              tile_dimension_quality="NOMINAL_24IN_FACE_NOT_ACTUAL_CALIBER",tile_body_thickness_mm_NOMINAL="UNKNOWN_FOR_FLAT_EXACT_FINISH",
              actual_caliber_mortar_trim_verified="FALSE",true_1529_field_verified="FALSE",owner_approved="FALSE",purchase_authorized="FALSE",
              source_url=URL["bone"] if room.startswith("PH") else URL["charcoal"]))
assert len(modules)==84
write_csv("R30_84_W1_W3_FACTORY_VS_NOMINAL_TWO_AXIS_AND_24IN_FIELD_BALANCED_CUT_MODULES.csv",modules)

# Aperture displacement once, back/sides/top/sill independent, two orientations prove cut directions.
apertures=[]
for room in FOCUS:
    w3=float(W[room,"W3"]["source_width_in_UNVERIFIED"])
    for product,(tile_long,tile_short,thick,src,quality) in MAT.items():
        for width in (12,16,20,24):
            for joint in (.125,.1875,.25):
                for orient in ("HORIZONTAL_LONG","VERTICAL_LONG"):
                    h=12.0
                    depth=4.0
                    pier=(w3-width-2*joint)/2
                    field=width*h/144
                    sides=2*h*depth/144
                    top=sill=width*depth/144
                    net=field+sides+top+sill
                    face=tile_long if orient=="HORIZONTAL_LONG" else tile_short
                    desired=3 if face>=3 else .75
                    full,end=cuts(width,face,joint,desired)
                    apertures.append(dict(room=room,unit_instances="TWO_SOURCE_COPIES_NOT_TWO_EXISTING_NICHES",niche_location_and_count="UNKNOWN",
                       source_W3_width_in_UNVERIFIED=f4(w3),niche_candidate_material=product,orientation=orient,niche_opening_width_in_HYPOTHETICAL=width,
                       niche_opening_height_in_HYPOTHETICAL=f4(h),niche_reveal_depth_in_HYPOTHETICAL=f4(depth),proposed_joint_in_UNAPPROVED=f4(joint),
                       W3_side_pier_each_in_PROVISIONAL=f4(pier),min_3in_pier="PASS_PROVISIONAL" if pier>=3 else "FAIL_PROVISIONAL",
                       one_field_wall_opening_deduct_ONCE_SF=f4(field),separate_niche_back_SF=f4(field),
                       two_side_returns_SF=f4(sides),niche_top_SF=f4(top),niche_sill_SF=f4(sill),
                       independent_niche_face_NET_SF_NO_WASTE=f4(net),
                       face_edge_perimeter_trim_theoretical_LF=f4(2*(width+h)/12),
                       back_to_return_internal_corner_theoretical_LF=f4(2*(width+h)/12),
                       actual_movement_joint_locations_and_LF="TBD_BY_FACTORY_MEMBRANE_AND_ARCHITECT",
                       niche_width_module_full_tile_count=full,niche_width_balanced_end_in=f4(end),
                       tile_face_factory_or_nominal_in=f4(face),tile_body_nominal_mm=f4(thick),
                       Caviar_minus_Soho_nominal_body_mm="3.5_NOT_FINISHED_PLANE",
                       field_openings_outside_niche_SF="UNKNOWN_NEVER_DEDUCT_AGAIN",
                       manufacturer_approved_niche_wet_AND_system="FALSE",true_field_width_position_riser_and_valve_clearance="FALSE",
                       owner_approved="FALSE",purchase_authorized="FALSE",source_url=src))
assert len(apertures)==144
write_csv("R30_144_NICHE_APERTURE_BACK_SIDES_TOP_SILL_EDGE_PIER_AND_JOINT_ALTERNATIVES.csv",apertures)

offcuts=[]
for room in FOCUS:
    for product,(tile_long,tile_short,thick,src,quality) in MAT.items():
        for width in (12,16,20,24):
            for j in (.125,.1875,.25):
                n,end=cuts(float(width),tile_long,j,3)
                # Only evaluate simple 4in return reuse after one end cut from one long tile, ignoring glaze orientation.
                remaining=tile_long-end-.125
                offcuts.append(dict(room=room,product=product,opening_width_in_HYPOTHETICAL=width,illustrative_joint_in=f4(j),
                    factory_or_nominal_tile_long_face_in=f4(tile_long),n_full_center_tiles=n,one_end_cut_in=f4(end),
                    assumed_saw_kerf_in_HYPOTHETICAL="0.1250",long_side_offcut_after_one_end_in=f4(max(0,remaining)),
                    one_4in_side_return_strip_geometric_possible=flag(remaining>=4),
                    reuse_actual_glaze_side_miter_waterproof_edge_lot_verified="FALSE",
                    number_orderable_real_usable_pieces="UNKNOWN",current_factory_cut_sheet="UNKNOWN",
                    purchase_authorized="FALSE",source_url=src))
assert len(offcuts)==72
write_csv("R30_72_PH4_TX4_MAKER_FORMAT_END_CUT_TO_RETURN_REUSE_UPPER_BOUNDS.csv",offcuts)

cost_case=[]
def add_case(product, coverage, kind, basis):
    gross=34.52
    each=8.63
    pooled=math.ceil(gross/coverage-1e-10)
    apart=4*math.ceil(each/coverage-1e-10)
    cost_case.append(dict(product=product,nominal_case_SF=f4(coverage),case_evidence_class=kind,
        source_historic_CAVIAR_gross_all_four_rooms_SF="34.5200",
        source_gross_one_each_of_four_copies_SF="8.6300",
        assumed_all_four_use_IDENTICAL_PRODUCT_AND_LOT="HYPOTHETICAL_NOT_OWNER_SELECTED",
        pooled_whole_cartons_if_same_approved_LOT=pooled,
        separately_rounded_four_receivers_whole_cartons=apart,
        theoretical_carton_rounding_difference=apart-pooled,
        may_apply_to_Soho_actual_current_order="FALSE",
        uses_historical_gross_as_alternate_order_QTY="FALSE",
        installed_cost_savings="UNKNOWN",actual_chicago_case_yield_LOT_stock="UNKNOWN",
        source=basis,purchase_authorized="FALSE"))
for prod in MAT:
    for cov in (6.,8.,10.,12.):
        add_case(prod,cov,"THEORETICAL_SENSITIVITY_NO_VENDOR_CASE","R17 historic Caviar; not interchangeable with proposed new net")
add_case("CAVIAR_2X8",100/9,"ARTO_2026_GENERIC_100PCS_BOX_9PCS_SF_AT_1_4IN_JOINT_ONLY",URL["arto_2026"])
assert len(cost_case)==13
write_csv("R30_13_SAME_LOT_HISTORIC_GROSS_VS_CARTON_SENSITIVITIES_NOT_ORDERS.csv",cost_case)

historic=[]
for r in ORIGINAL:
    is_focus=r["room"] in FOCUS
    is_niche=is_focus and r["source_surface"]=="accent"
    one=Decimal(r["source_gross_sf_one_copy_waste_15pct_once"] or "0")
    cost=money(r)
    is_unpriced=r["historic_niche_excluded_no_scope"]=="TRUE"
    historic.append(dict(room=r["room"],source_row_id=r["source_row_id"],original_source_surface=r["source_surface"],
       two_unit_copies_of_each_room="2",original_gross_SF_one_copy_15pct_already_once=str(one),
       original_gross_SF_two_copies=str(one*2),original_two_copy_material_ONLY_USD=str(cost),
       original_unpriced_niche_REFERENCE_NO_SCOPE_NO_ORDER=flag(is_unpriced),
       original_SOURCE_ROW_UNCHANGED="TRUE",historical_source_not_new_purchase="TRUE",
       original_r17_source_trace=r["source_trace"],
       proposed_R30_product_class=("ORIGINAL_CAVIAR_EXACT_WET_NICHE_HOLD_OR_SOHO_IVORY_SOHO_BLACK_OWNER_UNSELECTED" if is_niche else "PRESERVE_ORIGINAL_SELECTED_PRODUCT_NO_R30_CHANGE"),
       original_wet_WALL_versus_NICHE_status=("CAVIAR_INDIVIDUAL_NICHE_UNVERIFIED" if is_niche else "VERIFY_ORIGINAL_INDIVIDUAL_EXACT_SKU_WHEN_APPLICABLE"),
       original_LEVEL_numeric_RAW_wet_lab=("REQUIRED_MISSING" if r["source_surface"]=="floor" else "N_A_FOR_THIS_SOURCE_SURFACE"),
       independent_POINT_OR_LINEAR_PAN_raw_lab=("REQUIRED_SEPARATE_IN_PH4" if r["room"]=="PH-BATH4" and r["source_surface"]=="floor" else "PROGRAM_SPECIFIC_APPLICABILITY_DO_NOT_IMPORT"),
       actual_original_true_1529_measured_NET_SF="UNKNOWN",
       actual_niche_FIELD_aperture_displacement_SF_once="UNKNOWN",
       proposed_niche_back_sides_top_sill_SF_once="UNKNOWN",
       current_exact_same_maker_color_finish_SKU="UNKNOWN",
       current_maker_price_class="MANUFACTURER_2026_SUGGESTED_RETAIL_FAMILY_ONLY" if is_niche else "UNKNOWN",
       current_manufacturer_MSRP_USD_per_SF="37.15_NOT_CURRENT_PO_OR_COLOR_SPECIFIC" if is_niche else "UNKNOWN",
       current_public_retail_offer_USD="UNKNOWN",current_Chicago_supplier_offer_USD="UNKNOWN",
       current_factory_usable_case_SF="UNKNOWN_PER_EXACT_LOT_AND_INSTALL_JOINT",
       current_chicago_allocation_same_lot="UNKNOWN",freight_tax_breakage_eta="UNKNOWN",
       updated_gc_installed_bid_USD="UNKNOWN",
       owner_signed="FALSE",architect_signed="FALSE",plumber_signed="FALSE",waterproof_signed="FALSE",tile_signed="FALSE",
       supplier_signed="FALSE",gc_signed="FALSE",purchase_authorized="FALSE"))
write_csv("R30_27_ORIGINAL_HISTORICAL_ROWS_TO_FACTORY_MSRP_QUOTE_SKU_CASE_AND_GC_NORMALIZATION.csv",historic)

receiver=[]
for room in FOCUS:
    g=json.loads((BASE/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
    for i,unit in enumerate(g["revit_room_numbers"]):
        wall_key=(room,"W3")
        receiver.append(dict(room=room,source_room_copy=unit,unit_copy_index=i+1,
           actual_niche_number_size_position="UNKNOWN",parent_niche_source_accent_row_id=next(x["source_row_id"] for x in NICHES if x["room"]==room),
           original_Caviar_historic_gross_one_copy_SF="8.63",original_material_USD_one_copy="290.83",
           original_spatial_niche_NET_IS_NOT_historical_gross="TRUE",
           hypothetical_16x12x4in_field_aperture_SF="1.3333",hypothetical_independent_back_SF="1.3333",
           hypothetical_two_side_SF="0.6667",hypothetical_top_SF="0.4444",
           hypothetical_sill_SF="0.4444",hypothetical_niche_NET_no_waste_SF="2.8889",
           hypothetical_trim_face_LF="4.6667",hypothetical_back_corner_LF="4.6667",
           W1_source_width_in_UNVERIFIED=W[room,"W1"]["source_width_in_UNVERIFIED"],
           W3_source_width_in_UNVERIFIED=W[room,"W3"]["source_width_in_UNVERIFIED"],
           W3_source_height_in_UNVERIFIED=W[room,"W3"]["source_tiled_height_in_UNVERIFIED"],
           source_program="WALK_IN_SELECTED_BRIZO_BNX_POINT_FOURPLANE_PAN" if room.startswith("PH") else "TUB_SELECTED_DURAVIT_MATTE_WHITE_NO_PAN",
           true_1529_frame_aperture_flange_valve_pipe_verified="FALSE",
           physical_1to1_mockup_delivered="FALSE",all_trade_acceptance="FALSE",
           chicago_same_LOT_allocation="FALSE",purchase_authorized="FALSE"))
assert len(receiver)==4
write_csv("R30_4_ACTUAL_ROOM_COPIES_SOURCE_NICHE_BACK_RETURN_SILL_FIELD_SHOP_WITNESS.csv",receiver)

# Technical comparison of actual source geometry/quote registers, NOT measured payable changes.
geometry_recon=[]
for room in FOCUS:
    w1=float(W[room,"W1"]["source_width_in_UNVERIFIED"])
    w2=float(W[room,"W2"]["source_width_in_UNVERIFIED"])
    w3=float(W[room,"W3"]["source_width_in_UNVERIFIED"])
    h=float(W[room,"W1"]["source_tiled_height_in_UNVERIFIED"])
    wall_net=(w1+w2+w3)*h/144
    source_wall=next(r for r in ORIGINAL if r["room"]==room and r["source_surface"]=="wall")
    source_floor=next(r for r in ORIGINAL if r["room"]==room and r["source_surface"]=="floor")
    geometry_recon.append(dict(room=room,
      W1_source_in_UNVERIFIED=f4(w1),W2_source_in_UNVERIFIED=f4(w2),W3_source_in_UNVERIFIED=f4(w3),
      prior_wall_tiled_height_in_UNVERIFIED=f4(h),W1_W2_W3_full_field_geometric_SF_before_openings=f4(wall_net),
      hypothetical_original_once_15pct_gross_SF_from_full_field=f4(wall_net*1.15),
      original_source_quoted_wall_GROSS_one_copy_SF=source_wall["source_gross_sf_one_copy_waste_15pct_once"],
      original_source_wall_GROSS_two_copies_SF=f4(2*float(source_wall["source_gross_sf_one_copy_waste_15pct_once"])),
      actual_verified_W1W2W3_NET_openings_and_niche_SF="UNKNOWN",
      original_floor_gross_SF_one_copy_15pct_once=source_floor["source_gross_sf_one_copy_waste_15pct_once"],
      source_floor_LEVEL_vs_PAN_split="UNVERIFIED_MIXED_SOURCE_DO_NOT_ALLOCATE",
      owner_floor_SF=35 if room=="PH-BATH4" else "NO_R30_OWNER_OVERRIDE",
      drawing_prior_floor_SF=27 if room=="PH-BATH4" else "38.5_UNVERIFIED",
      original_source_107_2_times_two_214_4_diagnostic=("ORIGINAL_GROSS_TWO_COPIES_214.4_NOT_PAYABLE_SHORTAGE" if room=="PH-BATH4" else "NOT_APPLICABLE"),
      eight_SF_PH_owner_vs_drawing_delta_times_1_15_one_copy=("9.20_HYPOTHETICAL_GROSS_NOT_EXTRA_ORDER" if room=="PH-BATH4" else "N_A"),
      equivalent_two_copy_historic_floor_material_rate_exposure=("124.20_USD_IF_8_SF_TIMES_1_15_TIMES_TWO_TIMES_6_75_HISTORICAL_ONLY" if room=="PH-BATH4" else "N_A"),
      field_signed_net_count_areas="FALSE",vendor_reconciliation_signed="FALSE",PO_change_order_authorized="FALSE"))
write_csv("R30_2_BATH4_W1W2W3_214_4_VENDOR_FLOOR_35_27_AND_WASTE_RECONCILIATION.csv",geometry_recon)

# 13-unit/room full program and trade release: explicitly no invented powder wet PAN, no Primary niche.
hard = {
"PH-PRIMARY":"Brizo BT0734816-BNX + separate BR73480, 48in LINEAR; no Primary niche; separate LEVEL and LINEAR PAN original exact raw wet lab; WC inherited once; RL21 1/4 vs5/16 thickness and grout unresolved",
"PH-BATH2":"Duravit tub/Hansgrohe Matte White, individual wet Sapphire and Sandstone niche; tub flange + source 59.496in fit; LEVEL exact raw lab; PAN N/A",
"PH-BATH3":"Owner TUB/WALK-IN and basin UNSELECTED; Chrome Hansgrohe; Delta DT062412 POINT only if walk-in; Opal WALL unlisted; Sandstone niche; LEVEL raw lab and conditional POINT PAN independent",
"PH-BATH4":"WALK-IN BT062415-BNX square POINT (NOT BT062418); Ribbed Bone lacks individual Wet Areas; Caviar niche lacks individual wet proof; Soho Ivory/Black owner unselected; independent four-plane POINT PAN raw lab and LEVEL raw lab; 35-vs27 and 214.4 quote reconciliation",
"PH-POWDER":"Brizo T65722LF-GL WALL rough R65700, Earth Lines dry relief escutcheon level landing; wood floor, PAN/LEVEL tile tests N/A",
"PH-WC":"Seeded Bone AntiSlip LEVEL inherited Primary area once; TOTO Nexus UniFit assignment/door clearance/actual flange unresolved; no standalone order or PAN",
"TX-PRIMARY":"Brizo Black Onyx 48in LINEAR with separate rough, NO niche; Clay LEVEL vs PAN finish lab and WC once; TX203A unplaced",
"TX-BATH2":"Duravit tub/Hansgrohe Chrome, basin UNSELECTED; Copper/Sandstone individually wet wall/niche; LEVEL raw lab, PAN N/A",
"TX-BATH3":"Owner TUB/WALK-IN UNSELECTED; Brizo Black Onyx POINT BT062415-BNX only conditional walk-in; Emerald maker refresh; Sandstone niche; LEVEL/conditional four-plane POINT PAN labs separate",
"TX-BATH4":"Duravit 700332 59in tub Matte White; NO PAN. Hansgrohe Talis S spout 72411701 PRESSURE BALANCE ONLY versus thermostatic 15758701 & iBox 01850181 hold; tub flange/waste, original Caviar niche vs Soho Ivory/Black not selected; flat Charcoal Wet Areas listed; LEVEL lab missing",
"TX-POWDER":"AXOR 48140991 wall CROSS TRIM versus Hansgrohe 32526141 wall single TRIM; 32526141 NOT ROUGH; Metropol 13622181 rough only conditional Metropol owner choice; dry feature wood floor",
"TX-POWDER2":"Hansgrohe 73072341 DECK Brushed Black Chrome; basin UNSELECTED; Indigo feature retain; wood floor, no PAN",
"TX-WC":"Clay AntiSlip LEVEL inherited TX Primary once, TX203A UNPLACED and Nexus parent toilet assignment unresolved; no new niche, wall, PAN or order",
}
assert set(hard)=={r["id"] for r in ROOMS}
release_rows=[]
trades=["OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER"]
trade_rows=[]
for rm in ROOMS:
    name=rm["id"]
    source=next(x for x in RELEASE if x["room"]==name)
    gpath=BASE/"rooms"/name/"geometry.json"
    g=json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else {}
    wet="TUB_NO_TILED_PAN" if name in ("PH-BATH2","TX-BATH2","TX-BATH4") else (
        "NO_SHOWER_WOOD_FLOOR" if "POWDER" in name else ("WC_INHERITS_PARENT_LEVEL_NO_PAN" if name.endswith("WC") else (
        "OWNER_TUB_OR_WALKIN_UNSELECTED_POINT_ONLY_IF_WALKIN" if "BATH3" in name else (
        "PRIMARY_LINEAR_NO_NICHE_SEPARATE_LEVEL_AND_PAN" if name.endswith("PRIMARY") else "SELECTED_WALKIN_POINT_SEPARATE_LEVEL_AND_FOURPLANE_PAN"))))
    level_lab = ("N_A_WOOD_FLOOR" if "POWDER" in name else
       "INHERITED_PARENT_LEVEL_ORIGINAL_RAW_NUMERIC_MISSING" if name.endswith("WC") else
       "ORIGINAL_EXACT_PRODUCT_LEVEL_RAW_NUMERIC_WET_LAB_MISSING")
    pan_lab = ("INDEPENDENT_LINEAR_PAN_RAW_NUMERIC_MISSING" if name.endswith("PRIMARY") else
       "INDEPENDENT_POINT_FOUR_PLANE_PAN_RAW_NUMERIC_MISSING" if name=="PH-BATH4" else
       "CONDITIONAL_WALKIN_POINT_PAN_RAW_NUMERIC_MISSING_IF_OWNER_SELECTS_WALKIN" if name in ("PH-BATH3","TX-BATH3") else
       "N_A_TUB_OR_NO_SHOWER_PAN")
    rel=dict(room=name,copies="2",status=rm["status"],champion_id=rm.get("champion_id") or "null",
        champion_score=rm.get("champion_score") if rm.get("champion_score") is not None else "null",
        original_historic_material_ONLY_USD_two_copies=str(sum(money(x) for x in ORIGINAL if x["room"]==name)),
        source_fixture_and_program_exact_gate=hard[name],surface_and_pan_applicability=wet,
        original_manufacturer_individual_WALL_NICHE_permission="PROGRAM_SPECIFIC_NOT_TRANSFERABLE",
        original_exact_RAW_numeric_wet_LEVEL_test=level_lab,
        independent_exact_RAW_numeric_wet_SLOPED_PAN_test=pan_lab,
        verified_native_1529_dimensions_and_openings="FALSE",actual_net_quote_takeoff="FALSE",
        owner_selected_material_and_program_signed="FALSE",architect_shop_signed="FALSE",plumber_rough_and_fixture_signed="FALSE",
        waterproof_assembly_and_seal_signed="FALSE",tile_install_actual_caliber_mockup_signed="FALSE",
        current_exact_SKU_lot_case_chicago_allocated="FALSE",actual_gc_installed_bid_signed="FALSE",
        purchase_release="FALSE",material_reservation="FALSE",owner_sign_date="",architect_sign_date="",GC_sign_date="")
    release_rows.append(rel)
    for num,trade in enumerate(trades,1):
        if trade=="OWNER": require="Sign exact color/tier and nonselected programs/fixtures, budget cap; no price assumption. "+hard[name]
        elif trade=="ARCHITECT": require="Dimension true 1529 wall W1/W3, openings, niches, returns, access, calibrated surface and minimum visible cuts; signed elevation/revision."
        elif trade=="PLUMBER": require="Match selected factory drain/rough/valve/spout/waste and actual glass/tub flange/niche clashes; TX4 thermostat-vs-spout safety hold; record fixture-centerline elevations."
        elif trade=="WATERPROOFING": require="Approve exact factory membrane/backer, all niche folded returns and sloped sill, corners, pipe collars, tub flange OR shower POINT/LINEAR pan drain interface by program."
        elif trade=="TILE_INSTALLER": require="Produce unit-by-unit 1:1 calibrated tile thickness/joint/color/trim mockup and original SKU wet WALL/NICHE permission plus distinct LEVEL/PAN raw lab as applicable."
        elif trade=="SUPPLIER": require="Certify exact manufacturer order SKU/color/size/finish, same factory shade/caliber lot, actual pieces/carton usable coverage, Chicago allocated stock, date, freight/breakage/ETA; NO contact performed."
        elif trade=="GC_ESTIMATOR": require="Break out site measured NET and approved additional waste, finish/level/pan separately, niche field aperture once versus back/sides/top/sill, waterproof system, labor, trim, accessories, fees and separate unpriced scope."
        else: require="Cross-check signed owner/architect/plumber/wp/tile/supplier/GC approvals, final same-lot offer and contract; forbid Primary niche, WC extra order, original 15% twice; PURCHASE_FALSE."
        trade_rows.append(dict(room=name,step=num,trade=trade,room_specific_original_hard_gate=hard[name],
           actual_trade_acceptance_evidence_required=require,physical_1529_or_factory_evidence_doc="",signature="",date="",
           independent_original_4seat_critic_clearance="FALSE",owner_approval="FALSE",
           material_or_service_release="FALSE",purchase_authorized="FALSE"))
assert len(release_rows)==13 and len(trade_rows)==104
write_csv("R30_13_ROOM_ORIGINAL_SOURCE_PROGRAM_LEVEL_PAN_WET_AND_EIGHT_TRADE_RELEASE_MATRIX.csv",release_rows)
write_csv("R30_104_EIGHT_TRADE_ORDERED_ROOM_SPECIFIC_FIELD_MAKER_SAMPLE_AND_BID_CHECKPOINTS.csv",trade_rows)

norm=[]
for rm in ROOMS:
    name=rm["id"]
    gross=sum(Decimal(x["source_gross_sf_one_copy_waste_15pct_once"] or "0")*2 for x in ORIGINAL if x["room"]==name)
    v=sum(money(x) for x in ORIGINAL if x["room"]==name)
    norm.append(dict(room=name,original_historic_GROSS_SF_two_copies_15pct_once=str(gross),
       original_material_ONLY_USD_two_copies=str(v),original_contract_material_quote_class="HISTORICAL_2026_09_03_VENDOR_SOURCE_NOT_CURRENT",
       special_R30_evidence=("ARTO_GENERIC_2026_MSRP_CAVIAR_FAMILY_37_15_SF_AT_1_4IN_JOINT_NOT_COLOR_ORDERED" if name in FOCUS else "NO_NEW_PRICE_SOURCE"),
       actual_current_Chicago_material_QUOTE="UNKNOWN",actual_lot_case_coverage_freight="UNKNOWN",
       actual_gc_installed_quote_USD="UNKNOWN",
       actual_1529_field_NET_not_including_twice_niche_opening="UNKNOWN",
       separate_manufacturer_specific_LEVEL_and_PAN="REQUIRED_BY_ROOM_PROGRAM",
       original_shared_WC_floor_only_once="TRUE" if name.endswith("WC") or name.endswith("PRIMARY") else "N_A",
       price_source_classification_options="historical material; public retail indication; manufacturer MSRP; verified Chicago offer; allowance; theoretical; unknown GC installed",
       new_bid_scope="tile + cut/trim + waterproof + system drain/tub flange + labor + tax + shipping + protection + mockup + warranty allowances, separately enumerated",
       owner_approved="FALSE",verified_local_supplier="FALSE",GC_installed_bid_signed="FALSE",purchase_authorized="FALSE"))
assert sum(Decimal(x["original_material_ONLY_USD_two_copies"]) for x in norm)==Decimal("23572.44")
write_csv("R30_13_ROOM_TWO_COPY_HISTORICAL_VS_CURRENT_NORMALIZED_MATERIAL_AND_INSTALLED_SCOPE.csv",norm)

samples=[]
for room in FOCUS:
  g=json.loads((BASE/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
  for nr in g["revit_room_numbers"]:
    for camera,frame,require in [
      ("CAMERA_W1_STRAIGHT_ON","Prior full W1 width 60in, height "+W[room,"W1"]["source_tiled_height_in_UNVERIFIED"]+"in, no certified openings","Show original-versus-flat Bone PH or Charcoal TX, tub/spout or point PAN intact; labels unmeasured"),
      ("CAMERA_W3_ELEVATION","Prior W3 30.48in width; unknown niche size/place","Show 12/16/20/24in alternative focal pier, centerline valve clearance, true texture and grout scale; no invented niche"),
      ("CAMERA_45_DEGREE_CUTAWAY","Walk-in glass/point four-plane PAN PH or selected tub lip/flange TX","Show wall substrate waterproof plane, returns/sill/miter, actual BNX POINT or Duravit 59in tub; do not render fabricated finishes")
    ]:
      samples.append(dict(room=room,source_room_number=nr,camera_brief_not_render=camera,
        unverified_source_frame=frame,view_requirement=require,
        physical_sample_1to1_requirements="Compare factory original Caviar color and 13mm actual caliper vs Soho Ivory/Black 9.5mm; wall flat vs Ribbed; maker-approved grout/edge/profile, wet corner and corner membrane test; actual selected metal matte white/BNX light board",
        acceptance_test="Actual batch caliper, joint by manufacturer, full wet test letter per exact SKU, flush front and back planes, 3in focal pier or explicit owner exception, perimeter and slope, flange/point drain isolated waterproof joint",
        image_generated="FALSE",physical_sample_obtained="FALSE",render_created="FALSE",
        owner_signed="FALSE",architect_signed="FALSE",plumber_signed="FALSE",waterproof_signed="FALSE",tile_installer_signed="FALSE",GC_signed="FALSE",
        purchase_authorized="FALSE"))
assert len(samples)==12
write_csv("R30_12_ACTUAL_ROOM_INSTANCE_SOURCE_FAITHFUL_CAMERAS_AND_1TO1_SHOP_MOCKUP_ACCEPTANCE.csv",samples)

seq = [
 ("DIMENSIONED_1529_PREDRILL","Record actual elevations, rough-face, slab elevation, door/glass, niche locations and chases from correctly identified 1529 only; obtain document/field witness"),
 ("LAB_AND_APPLICATION_PER_SKU","Obtain signed factory individual Wet Areas WALL/NICHE and exact measured numerical raw lab for LEVEL and independent PAN if shower; specify finish, testing method, report, sample date"),
 ("PLUMBING_FORM_AND_ROUGH","PH4 selected BT062415-BNX with 2in PVC and R75000-WS; TX4 15758701 thermostat vs 72411701 pressure-balance-only hold; verified tub waste, flange, access"),
 ("MEMBRANE_SYSTEM_APPROVAL","Select one maker-backed waterproof substrate, folded niche corners, sill positive fall toward wet area, penetration, transition and drain/tub flange; no generic compatibility transfer"),
 ("TILE_CALIBER_AND_1TO1","Mockup factory 1-3/4x8-1/8 Caviar 13mm vs nominal Soho 2x10 9.5mm; actual grout/edge trim and corner geometry; PH Ribbed wet hold"),
 ("QUOTE_AND_RECEIPT","Convert signed NET minus one wall aperture plus separate niche back/sides/top/sill, approved waste once, stock/lot/carton/ETA, installed GC cost; old quote unmodified"),
]
next_technical=[]
for rm in ROOMS:
  for stage, detail in seq[:(6 if rm["id"] in FOCUS else 3)]:
    next_technical.append(dict(room=rm["id"],next_cycle_evidence_gate=stage,
        contractor_factory_or_field_request=detail+" | "+hard[rm["id"]],
        actual_manufacturer_laboratory_report_id="",raw_numerical_wet_DCOF_reading="",
        exact_lot_and_finish="",test_surface_LEVEL_or_POINT_LINEAR_PAN="PROGRAM_SPECIFIC_SEPARATE",
        true_1529_measured_geometry_reference="",responsible_trade="UNASSIGNED_NOT_CONTACTED",
        physical_evidence_in_hand="FALSE",technical_gate_closed="FALSE",release="FALSE"))
assert len(next_technical)==45
write_csv("R30_45_NEXT_CONSEQUENTIAL_PER_SURFACE_WET_LAB_1529_AND_TRADE_EVIDENCE_WORKLIST.csv",next_technical)

price=Decimal("37.15")*Decimal("34.52")
assert price.quantize(Decimal(".01"))==Decimal("1282.42")
write_md("START_HERE_R30.md",f"""
# R30 integrated Bath4 source-to-construction and 13-room quote release — 2026-11-06

**OPEN / UNREVIEWED / NOT OWNER OR GC RELEASED.** This is a genuinely new full R30 package, not the previously signed 24-case preliminary worksheet. Existing R12–R29 and R30 source receipt are immutable predecessors.

## Immediate decisions

1. **PH-BATH4** must remain WALK-IN, selected Brizo BT062415-BNX Black Onyx 4-inch square POINT, with an actual four-plane sloped PAN separately specified from LEVEL floor. Maker {URL["brizo"]}. Do not confuse reversible BT062418-BNX / BR62400 with the actual selected drain.
2. **TX-BATH4** remains Duravit 700332000000090 59x29.5in built-in tub, Hansgrohe Matte White, **NO tiled PAN**. Its selected 72411701 tub spout is documented by maker as **pressure-balance valve only**, yet 15758701 is a thermostatic trim. Plumber + Hansgrohe written compatibility/revised schedule resolution is a HARD HOLD, not authority to substitute.
3. PH4 original Cortar Bone Ribbed maker item lists only Walls and Back Splashes, not Wet Areas; separate flat Bone item lists Wet Areas. Original ARTO Clara Caviar 2x8 generic wet wall system doc does not individually approve Caviar niche. ELM Soho Ivory **and** Soho Black 2x10 individually list Wet Areas on official product pages. All substitutes remain conditional owner proposals.
4. **Actual factory difference:** ARTO 2026 CLARA-TIERRAMADRE2X8 1-3/4 x 8-1/8in; nominal 13mm body, nine pieces/SF at catalog **1/4in joint**, 100 pieces/box, **$37.15/SF maker 2026 suggested retail** (not verified Caviar-specific order or local quote). Soho 2x10 nominal 9.5mm; exact caliber and carton unknown. Nominal body delta = 3.5mm, not installed face offset.
5. Derived original source PH4 unverified W1+W2+W3 full-height field = **93.24 SF**; applying old single 15% ≈**107.23 SF** versus historical 107.2 SF/copy and **214.4 SF for TWO copies**, not an established payable shortage. PH4 owner 35 SF versus prior 27 SF gives 8 SF area discrepancy, or 9.2 gross-SF/copy only in a hypothetical once-wasted same-material comparison; actual LEVEL versus four-plane PAN allocation is unknown.

## Signed quantitative package index

* Manufacturer 10-row item/permission/source and six GOOD/BETTER/BEST design options.
* 84 original W1/W3 actual factory-versus-nominal tile and larger 24in field-joint cut cases.
* 144 niche opening/returns/top/sill/edge/corner/Pier section cases, 72 independent offcut upper bounds and 13 case-rounding sensitivities.
* Four physical unit instance 1:1 checks, 12 distinct source-faithful camera briefs and 45 following-cycle evidence checkpoints.
* 27 original material line cost and supplier source normalization, two Bath4 geometric/quote disputes, 13 original room release schedules and 104 eight-trade checks, 13 room two-copy cost normalization.
* Three detailed manuscripts: manufacturer/source, PH4 WALK-IN POINT shop sections, TX4 Duravit tub/spout shop sections, and 13-room original-owner/GC program and priority book.
* MANIFEST.json SHA-256/byte-signs every file listed herein, with signed predecessor references. No original signed source file overwritten.

Original source material-only four-unit sum **$23,572.44**, 27 rows including two unpriced/NO ORDER Primary niche history; historical 15% waste already included ONCE. PH4/TX4 Caviar source group 34.52 SF/$1,163.32 (already included). Current $37.15 maker family 1/4in-joint reference applied hypothetically to historical 34.52 SF gives **$1,282.42**, a **$119.10** non-comparable retail-versus-historic rate exposure, NOT a purchase delta or new cost. ELM Soho current actual material/installed quote UNKNOWN.

## Scope control

No certified 1529 native model: currently reachable document is 1527. No actual maker original raw numeric LEVEL or independent POINT PAN test; no Caviar-specific niche release, exact membrane compatibility, measured actual corners/openings, selected Soho, physical mockup, owner cap, 2026 Chicago exact case/lot, supplier commitment, freight, installed GC bid or owner/architect/GC signature. No owner contact or purchase. R014 two original DESIGN criticisms absent; R017 source-frozen and NOT scored; original independent reviewer worker15 FINISHED/nonrevivable, R30 UNSENT/UNREVIEWED. 13-room GLOBAL OBJECTIVE OPEN.
""")

write_md("R30_INDIVIDUAL_MAKER_WET_WALL_NICHE_RAW_LEVEL_AND_PAN_SOURCE_RECONCILIATION.md",f"""
# R30 source-grading — original SKU, wet WALL/NICHE and independent LEVEL/PAN

## Verified maker evidence and classification

* ARTO Clara Caviar 2x8: {URL["caviar"]} identifies Clara handmade blonde-body 1/2in / 13mm nominal ceramic, Caviar color. Official ARTO wall-install spec {URL["arto_wall"]} applies to general Clara on walls and describes LATICRETE HYDRO BAN and compatible setting/grout/sealant as a **system example**, not an individual Caviar 2x8 niche-specific written authorization. 2026 ARTO factory price book {URL["arto_2026"]} item **CLARA-TIERRAMADRE2X8**, real listed face **1-3/4 x 8-1/8in**, nine pcs/SF at book 1/4in joint, **100 pcs per generic box**, **$37.15/SF manufacturer suggested retail updated 2026-03-02**. Factory catalog family code is not confirmed orderable Caviar shade-lot suffix; do not call 100/9 actual 1/8in or 3/16in usable carton SF. Caviar individual wet niche remains UNVERIFIED (no evidence of explicit prohibition).
* ELM Soho Ivory 2x10 Glossy {URL["ivory"]} **individual Wet Areas and Walls** listed, nominal 9.5mm; color Ivory. ELM Soho Black 2x10 Glossy {URL["black"]} same independent Wet Areas and Walls listing but a DIFFERENT COLOR/LOT, never pool with Ivory. Wet AREA item listing supports niche wall-face use as conditional design evidence, not all approved waterproofing, decorative termination or owner choice. Exact item SKU/caliber/usable carton/bid not retrieved.
* ELM Cortar Bone Ribbed 24x48 Relief {URL["bone_ribbed"]} **Walls + Back Splashes only**; no individual Wet Areas listing; PH4 original wet-wall candidate NOT releasable. ELM Cortar flat Bone {URL["bone"]} individually lists Wet Areas, Soft/AntiSlip variants; factory check actual 24x48 finish. The flat listing never transfers to Ribbed.
* ELM Cortar flat Charcoal {URL["charcoal"]} lists Wet Areas and 24x48 with Soft/AntiSlip; TX4 tub-surround flat exact finish to be confirmed against shade/size, system and rough.
* Brizo actual selected {URL["brizo"]} **BT062415-BNX** point drain, item notes adjustable upper, PVC/brass and 2in PVC connection, manufacturer **$166 list**; no permission to replace it with the distinct BT062418 reversible series or assume BR62400 rough is relevant. Membrane flashing/drain interfaces require selected exact factory shop detail.
* Duravit {URL["duravit"]}: 700332000000090 **59 x 29-1/2in**, 59 nominal, sanitary acrylic, built-in drop-in, support frame included; factory lists accessory tile flange 790112 as suitable, NOT installed or selected; **$1,550 maker list**, outside historical tile cost.
* Hansgrohe {URL["spout"]}: 72411701 Matte White **tub spout with diverter** maker states **for pressure balance valve only**, **$382 maker list**; current room source also 15758701 thermostatic trim and 01850181 rough {URL["ibox"]}. **Resolve exact control-type compatibility with maker and plumber before roughing, not through an unapproved automatic swap**.

## Hard original raw lab matrix (do not substitute brochure thresholds)

PH4 LEVEL is independent from its **four-plane square POINT PAN**. Both selected original tile material's exact manufacturer-color-finish-format raw measured numerical wet DCOF report, test method, specimen and date are presently absent. For shower PAN include four-way slope and point drain floor geometry; large LEVEL tile wet permission or DCOF never certifies PAN. TX4 selected Duravit tub has LEVEL floor raw numeric wet lab need, but tiled PAN **N/A**; no spurious shower PAN order. Manufacturer labels >=0.42 / >0.50 / >=0.60 / Target >=0.42 are not the demanded individual original raw readings.

The PH4 original Ribbed wet-wall absence is an application listing gate, not a floor friction report. The Caviar wet niche absent individual listing is an application permission hold, not a fabricated product rejection. Soho wet Wall listing is neither grout-joint authorization nor membrane warranty; four corners/backs/returns/penetrations and actual bath type must be accepted separately.

## Catalog/purchasing controls

Historical PH4 niche row 6092702458445700 and TX4 row 5529752505024388 each **8.63 gross SF/copy**, **$290.83 per copy**; across two copies each **34.52 SF / $1,163.32**. They are NOT proven physical niche net and the original 15% cannot be applied again. 100pcs catalog Clara box at 1/4 joint is a **manufacturer format lead**, not an exact Caviar lot allocation or joint-approved case coverage for 1/8/3/16 designs. No orderability or Chicago quote for Soho colors; its theoretical case sensitivities are deliberately not real cases. GC installed labor, selected trim, sealant, shade batch, freight, breakage and ETA all UNKNOWN.
""")

write_md("R30_PH4_ACTUAL_WALKIN_4PLANE_BRIZO_BNX_POINT_W1W3_AND_WATERPROOF_SECTIONS.md",f"""
# PH-BATH4 311A/311B — WALK-IN construction alternate sections; design/shop PRELIMINARY

**Actual owner program preserved:** WALK-IN shower; selected Brizo Black Onyx **BT062415-BNX 4-inch tile-in square POINT drain**, selected Brizo R75000-WS valve rough + T755110-BNXLHP trim-less-handles with separately scheduled HL75110-BNX handle. Manufacturer actual drain {URL["brizo"]} has 2-inch PVC connection, adjustable height; do NOT use unrelated reversible BT062418 / BR62400 assembly. Document 4-plane sloped PAN, separate bath LEVEL floor, and two independent exact original raw wet numeric DCOF tests by actual material and finish. No Primary LINEAR substitution.

## Provisional source elevation A — W1 field

R17 W1 = **60.00in x 111.00in**, full-face reference = 46.250 SF before ANY actual opening, framing or niche. Base source finish Cortar Bone Ribbed relief 24x48 maker item **Walls/Back Splashes only**, not Wet Areas: **wet WALL HARD HOLD**. Flat Bone separately Wet Areas-listed 24x48 is a proposed substitute NOT owner selected. At 60in W1 with **2 full nominal 24in middle modules** the two balanced ends are **5.8125in** each at 1/8in joint [calculated (60 - 48 - 3x0.125)/2], 5.71875in at 3/16, and 5.625in at 1/4. Actual 24in caliber/crown and waterproof stack TBD. Niche is NOT assigned automatically to W1. Valve/head/hand shower/glass locations and mounting depths require measured linework before niche.

## Provisional elevation B — W3 focal niche wall

R17 W3 = **30.48in x 111.00in**, full face = 23.495 SF. The same 24in nominal 1-full-tile + two side cuts equals **3.115in with 1/8 joint**, **3.0525in with 3/16**, but **2.990in with 1/4**: the latter violates project **3in minimum focal pier/cut** before 1529 measurement. Thus JOINT choice and actual calibrated wall width are coupled decisions. For hypothetical niche opening 24in + two outside 1/8 joints, side wall piers = (30.48-24-0.25)/2 = **3.115in**; 3/16 leaves **3.0525in**; 1/4 yields **2.990in FAIL**. Proposed 12/16/20/24in niche apertures are NOT evidence of existing framed niches. Each niche location requires field valve/no-pipe/backer witness.

## Section C — four-plane PAN / POINT drain / waterproof membrane

1. At correct 1529 field: identify shower entry, glass fixed/pivot dimensions, low point and BT062415-BNX physical actual drain center, 2in PVC/trap and installed height. Confirm grate removability/access and tile-face seat.
2. Architect/GC/waterproofer choose a **single compatible shower system** with tested membrane-to-drain attachment, approved seams and overlap, continuous four-plane slope toward point; corners and changes in plane are detailed to its manufacturer, not inferred from a generic HYDRO BAN Caviar wall PDF.
3. Waterproof and installer shop sections identify subfloor/depression and surface heights: substrate -> maker backer -> selected membrane -> actual mortar bed -> calibrated PAN tile -> joints/grate. Distinct adjoining bath LEVEL build-up and walking transition. Avoid blending source gross into both LEVEL and PAN; slope/drain measured first.
4. PAN tile remains UNSELECTED for original raw measured numeric wet result: obtain exact product-color-size-finish original laboratory wet test AND sloped POINT PAN manufacturer application; if absent hard gate FAIL, no tile order.

## Section D — niche Caviar vs Soho and face finish

GOOD historical unlisted Caviar and Bone Ribbed **noninstallable wet until individual approvals**. BETTER Soho Ivory Wet Areas plus wet-listed flat Bone candidate (owner unselected): quieter warm niche with improved cleanability. BEST Soho Black Wet Areas plus flat Bone: preserve original dark focal read, use deliberate physical miter/profile system, separate maker waterproof corners. For each: subtract **one front WALL aperture once**; independently count BACK, both side reveals, TOP and sloped-to-shower SILL, never add aperture area again. Hypothetical 16x12x4in: wall hole 1.3333 SF; niche back1.3333 + sides0.6667 + top0.4444 + sill0.4444 = 2.8889 NET; exposed front profile 4.6667 LF and inner back-to-return corner 4.6667 LF, not yet actual installation lengths or movement-joint schedule.

ARTO 2026 factory **1-3/4x8-1/8in** vs nominal Soho **2x10in** permits visibly different grout/end-cut grids. Caviar nominal 13mm vs Soho 9.5mm is **3.5mm BODY only**: no assumed 3.5mm thinset correction, installed plane must account for substrate/membrane mortar compressed thickness, actual tile caliber, grout/support, glazes and trim tongue depth. Installer builds a 1:1 full recessed niche with two side returns, top and sill slope, inside/outside corners, miter vs profile, 1/8/3/16/1/4 joint **only after maker permits**. Waterproof manufacturer signs penetrations and movement strategy.

## Source gross and floor/quote forensic

W1 60 + W2 30.48 + W3 30.48 = 120.96in=10.08LF; 111in=9.25ft; 93.24 SF before openings. At original 15% once =107.226 SF versus historical 107.2 source gross per copy, ×2 =214.4 historical two-copy reference. This is an **explanation of source math, NOT an installed quantity or owed shortfall**; resolve original quote reading against original vendor line and dated actual takeoff, returns and any existing niche (unknown). Source floor 40.2 gross/copy approximates owner 35x1.15=40.25 while prior drawing 27x1.15=31.05; delta8 actual SF or 9.20 gross at same old convention per copy, but cannot assign to bath LEVEL vs PAN. Historic floor original $271.35/40.2=$6.75/SF, hypothetical 2x9.2x$6.75=$124.20 material-rate exposure only, not a supplier claim.

**Mandatory 1:1 and signatures:** correct 1529 source ID, roughs, niche absence/presence and dimensions, wet-approved exact original/proposed SKU, original numeric lab separate LEVEL/PAN, actual membrane/point flange, physical tile-caliber mockup, 3in cut/piers, supplier same-lot quote and 8 trade signatures. All false.
""")

write_md("R30_TX4_DURAVIT_TUB_FLANGE_THERMOSTATIC_SPOUT_SHOP_W1W3_AND_OWNER_TIERS.md",f"""
# TX-BATH4 007A/007B — actual TUB section and niche controls; shop PRELIMINARY

Selected **Duravit Starck 700332000000090 built-in 59 x 29-1/2in acrylic TUB WITH SUPPORT FRAME** {URL["duravit"]}; Hansgrohe Matte White selected, **NO tiled shower PAN**, no POINT/LINEAR shower drain. Historical original Charcoal flat wall independently item-listed for Wet Areas {URL["charcoal"]}; original Caviar 2x8 niche item-specific wet proof missing. Alternative Soho Ivory and Black individual Wet Areas wall listings both verified, owner UNSELECTED.

## W1, W3 provenance and source dimensional risk

R17 unverified W1 **60in wide x93in high** (38.75 SF full face), W3 **30.48in x93in** (19.685 SF); W2 same. Original source geometry calls W1 assumed tub backwall, NOT a measured physical alcove. If actual W1 is true clear rough alcove, 60in nominal vs Duravit **59in** gives just **1in total nominal difference** before end returns, flange, finish, substrate and out-of-square tolerances; evenly splitting would be hypothetical 0.5in each side and is **NOT a tub-fit verification**. Confirm factory support and installation fasteners; manufacturer lists flange **790112** only as optional/suitable, not specified/installed. Tub lip/backer/membrane continuity to water collection side, upturned returns, caulk/access clearance and tub waste/overflow must be drawn against the exact selected model.

W3 same 30.48in focal wall: centered nominal 24in Charcoal tile at 1/8 joint leaves 3.115in cuts, at 3/16 leaves 3.0525, at 1/4 leaves 2.990in **below 3in focal threshold**. For a hypothetical W3 24in-wide niche, identical 3.115/3.0525/2.990in side piers at these outside joints. This is a mathematical source sensitivity, NOT a permit/site layout. The physical niche must not land behind current spout/head/handshower, pipes, anchors, tub flange or service opening. Measure positions and resolve collisions before framing.

## Section A — tub flange and waterproofing: no pan

1. Installer plumber and waterproofer first verify Duravit 700332 actual flange choice and manufacturer-approved installation sequence, support frame and drainage/access. Backer terminates where its manufacturer requires; waterproof membrane returns continuously over approved tub flange surface and niche backs/sides/top/sill. No generic field-caulk-only substitute for waterproofing.
2. Wet wall niche sill inclines toward tub wetted side (positive fall), with factory compliant niche inside corners and movement joints at wall-to-tub and adjacent planes. Field verify slope value/continuous bond and local tile/trim support; do not invent a universal slope tolerance.
3. Plan service trap/waste overflow access and spout minimum projection. White tub, Matte White trim, Charcoal wall and any selected Caviar/Soho shade must have a real 1:1 lit mockup showing caulk, miter/profiles, grout staining, factory caliper and soffit/return joints.
4. LEVEL bath floor only requires its exact selected Bone Soft original **numeric RAW measured wet DCOF** with lot/test specimen and manufacturer format; it does NOT confer a shower PAN need. No shower PAN tiling or Brizo shower point rough in this tub room.

## Section B — newly confirmed factory plumbing incompatibility checkpoint

Manufacturer official {URL["spout"]} lists **72411701 Talis S Matte White tub spout with diverter: FOR USE WITH PRESSURE BALANCE VALVE ONLY**. Existing room source has Hansgrohe **15758701 Ecostat S thermostatic trim with volume/diverter**, with scheduled **01850181 iBox rough**. Those are different control categories. It is **unresolved / cannot release tub-spout rough** until official maker/plumber full tub-fill and shower-switching schematic shows exact compatible spout plus trim and switching arrangement. Do not automatically swap approved Matte White trim, fabricate rough or claim system safety is already accepted. Existing source Westbrass TD9028-PCW brand attribution to WETSTYLE-vs-Westbrass prior quote separately needs confirmed factory manufacturer and compatibility; no new order.

## Owner tiers and physical color/edge effect

GOOD Caviar / flat Charcoal: retains handmade warm dark historical tile; Caviar wet niche individually unlisted and handmade 13mm irregular returns, **historical only**. BETTER individual wet-listed Soho Ivory / flat Charcoal: legible lighter niche and cleaner 2x10 cuts; requires owner material and installed-plane approval. BEST independent wet-listed Soho Black / flat Charcoal: visually quiet dark monolithic recess, high workmanship on gloss/soft dark boundary, require 1:1 high/low light board to avoid black/charcoal near-match problem. Both substitutions are unselected, not approved installed designs.

16x12x4in hypothetical one original WALL aperture1.3333 SF, independent niche back1.3333, two returns0.6667, TOP0.4444 and sloped SILL0.4444; 2.8889 net niche faces before any new documented waste. Factory Caviar 1-3/4x8-1/8 vs Soho nominal 2x10, body difference 3.5mm **NOT finish plane**. Actual flange/rim, membrane, mortar, joint and field matching measured. Existing historic $290.83 one accent source/copy is not the measured niche net or new Soho quote. Four-room combined 34.52SF / $1,163.32 historical already in $23,572.44.

**Hard release sequence:** verify true 1529 geometry, tub rough and flange/waste manufacturer detail; get exact wet WALL and NICHE applications, original raw LEVEL numeric lab; Hansgrohe spout/thermostat conflict resolution; niche/system/trim 1:1 physical witnesses; shade/color/lot and supplier current Chicago installed bid; all trade and owner approvals. All currently FALSE.
""")

write_md("R30_ALL_13ROOM_OWNER_ARCHITECT_GC_SCOPE_MARKET_AND_NORM_ESTIMATE_BOOK.md",f"""
# R30 13-room architect/GC/owner integration — NOT a released construction set

This owner-facing source control is **conditional technical analysis**, not signed construction documents, actual Revit geometry, stored samples or a purchase order. The active original formal board remains R017; original R014 DESIGN worker9 remains failed with two absent reports and sole existing non-Pro Reviewer15 is finished/nonrevivable. Earlier R23 independent PRECISE FIX is only locally verified afterward, no independent follow-up. No new neutral R30 blind packet or weighted critic score. All thirteen original champion statuses remain as in state/ROOMS.json.

## 13 actual room programs and designer/GC source focus

"""+"\n".join(f"- **{r['id']}** ({r['status']}): {hard[r['id']]}" for r in ROOMS)+f"""

Each historically has **two physical copies**, not thirteen total physical bathrooms. Original **27 historic material rows** include two unpriced/no-scope Primary niche references. Only original quoted material (four-unit historic total **$23,572.44**) is used for base dollars, gross areas include original 15% once. **25** prior W elevations and **65** original trade actions are retained as independent untouched inputs. This R30 adds **104** staged trade checks; not replacing or treating them as completed.

## Material and cost classification with procurement-ready bid structure

The original Caviar combined PH4+TX4 accent historical **34.52 SF gross / $1,163.32 material-only**, included in total. Factory ARTO 2026 generic CLARA 2x8 lists 100pcs/box at **9pcs/SF** based on **1/4 joint** and $37.15/SF *manufacturer suggested retail*; it is **not** a verified Caviar color/lot/box allocation for 1/8 or 3/16 grout. Applying this MSRP to old 34.52 historical gross gives $1,282.42 or +$119.10 versus historical *material-only* Caviar subtotal, an explicitly **non-comparable factory MSRP versus historic vendor rate sensitivity**. Zero contractual cost increase, estimated GC bid or actual Chicago savings is claimed. Soho Ivory and Soho Black materials/usable cases are unknown.

For each exact factory tile SKU group **and only within same manufacturer, same color, size, finish, factory shade/caliber and lot**, estimator will compute (certified original field NET - one real niche aperture and other openings + actual back/two sides/top/sill + approved newly documented waste)/actual manufacturer usable case coverage. Previously quoted source gross is NOT re-wasted; WCs and Primary inherited shared floors are NEVER duplicated; full four-plane POINT PAN and LEVEL floor are separated; TUB rooms never receive a point PAN; wood-floor powders have NO tiled shower PAN. Original Sandstone 51.64SF/$358.92 and Grey Soft 165.40SF/$1,116.46 are earlier historical subsets included already, not newly added costs. Selected Primary drainage 48in LINEAR/rough pairs and no niche unchanged.

New GC normalized bid schedule must separately price verified current material, calibration/grout, physical inside/outside trim/soft joints, backer, membrane, substrate fix, tub flange or manufacturer drain interface, slope, niche frame/back and four returns, labor, cut/seal/waste, waterproof penetration testing, factory freight/tax, mockup, attic/shop access and allowances. Record **historical quoted material rate**, **public retail indication**, **manufacturer MSRP**, **current verified Chicago supplier offer**, **allowance**, **theoretical alternative**, **unknown installed GC bid** in distinct columns; absence remains NULL/UNKNOWN. Do not send requests/outreach or reserve stock under this instruction.

## Buyer value

PH target approximately **$2.8M**, TX approximately **$2.7M**, comp comparison **$2.4M–$3.2M**. Existing comp research's 14 listing entries represent **nine buildings**; OT01–OT04 at 405 W Armitage count **one** building. Old Town priority; Lincoln Park and Gold Coast secondary. There is no authenticated photographic verification of competitor exact tile/grout/niche construction and no credible invented buyer dollar uplift. Practical options are higher-quality wet-compliant simplified surfaces and robust tub/shower trims, not over-finishing hidden niche returns.

## Prerequisite decision sequence

1. Owner signs actual selected program, unchanged plumbing and proposed physical material/finish branch and price cap (present FILL IN). Owner has not selected Caviar retained-vs-Soho Ivory-vs-Soho Black and has not approved PH4 flat Bone substitution.
2. Architect locates correct **1529** native/field record; signed existing openings, W1/W3, true niche count/location and valves. Current reachable Revit document **1527** is not 1529.
3. Plumbing verifies Brizo BT062415-BNX actual POINT drain and slope/pipe flange, TX4 correct Hansgrohe pressure-balance vs thermostatic spout/trim, Duravit support/flange and overflow/access.
4. Manufacturer/waterproof trade authorizes exact original COLOR/SKU/FINISH wet WALL and separately NICHE plus matched membrane and drain/tub flange details, including corners, movement joints and cleaning expectations.
5. Original raw numeric wet lab for each LEVEL product plus distinct four-plane POINT or LINEAR PAN product (where program needs one), with test method/date/specimen; no category threshold substitution.
6. Tile installer builds exact size/caliper/color 1:1 edge/back/returns/sill, grout joint and trim mockup with no <3in feature pier unless owner/architect documented exception.
7. Supplier records actual current Chicago factory SKU/case/same lot/quantity/availability/ETA, independent GC full installed bid; original source 15% once protected.
8. Only after separate owner, architect, plumbing, waterproof, installer, supplier, GC, purchasing signatures may a later authorized party place orders. **Every release remains FALSE** in this R30.
""")

# Predecessor signed SHA values are immutable references; never synthesize missing R26.
predecessors = {
 "R014_original_source":"946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed",
 "R015_original_source":"cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8",
 "R016_original_source":"dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a",
 "R017_original_frozen_source":"01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90",
 "R023_local_fix1_not_independent_review":"81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025",
 "R024":"7e08b9b787a00abfc9fc18e52458008b07312c44da9c96037b0dce866a55a6d4",
 "R025":"0170a18a25c5fdf9c682f8c8379c17944e97b98723db1995cfaf6570350f84fe",
 "R027":"5523674db6ef75811b25260405806ef8993329a70e41aec042f5ec63d852f59b",
 "R028":"45db073bc7e78509627a01ea599ecfd291a0cbcacd5cc9c07a1126f6568c8212",
 "R029":"d3cf560c43c970e172cb2ebec187ebbc1b25472a2de86398a807cfca8300ef70",
 "R030_preliminary_source_only":"b0afd03cd5f471234fceebbcc361ea769d9c0f1ccfaa77569bb40191ae3be604"
}
assert len(FILES)>=16
assert not OUT.exists()
OUT.mkdir(parents=True, exist_ok=False)
manifest={"round":30,"project":"1529 N Wieland 13-room owner/architect/GC tile loop",
  "phase":"INTEGRATED_TECHNICAL_SOURCE_NOT_BLIND_SCORING_UNSENT_REVIEW",
  "created_date_local":"2026-11-06","immutable_predecessor_SHA256":predecessors,
  "lineage_notes":"R12-R22/R26 signed predecessor set retained on disk; no invented hash where current receipt not read.",
  "actual_source_controls":{"rooms":13,"historical_material_rows":27,"unpriced_primary_niche_no_scope_rows":2,
    "prior_original_W_elevation_rows":25,"original_trade_action_rows":65,
    "two_copies_per_room":2,"original_historic_material_only_usd":"23572.44","original_waste_included_once_percent":15,
    "historical_Caviar_group_gross_SF":"34.52","historical_Caviar_group_usd":"1163.32"},
  "new_counts":{"manufacturer_source_rows":len(maker),"owner_options":len(tiers),"W1_W3_module_rows":len(modules),
    "niche_section_rows":len(apertures),"cutstock_rows":len(offcuts),"case_sensitivity_rows":len(cost_case),
    "source_original_rows":len(historic),"bath4_unit_receivers":len(receiver),"bath4_geometry_reconciliation_rows":len(geometry_recon),
    "complete_room_releases":len(release_rows),"eight_trade_gates":len(trade_rows),
    "two_copy_room_quote_normalization":len(norm),"camera_and_mockup_briefs":len(samples),
    "consequential_next_technical_evidence_rows":len(next_technical)},
  "factory_source_presentation":"Original specific Wet Areas listings separately; no manufacturer raw numeric LEVEL/POINT PAN fabricated; 2026 manufacturer suggested retail not a current offer.",
  "geometry_certified_1529":False,"owner_material_approval":False,"all_four_original_critics_complete_R014":False,
  "independent_nonpro_reviewer_accepted":False,"all_wet_raw_lab_gate_pass":False,"material_reserved":False,
  "construction_release":False,"purchase_authorized":False,"global_13_room_DONE":False,
  "files":[{"relative_path":n,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()} for n,b in sorted(FILES.items())]}
for name, data in sorted(FILES.items()):
    target=OUT/name
    assert not target.exists()
    with target.open("xb") as f:
        f.write(data)
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
print("R30_FULL_CREATED",OUT)
print("SIGNED_FILES",len(FILES),"AND_MANIFEST",len(FILES)+1)
print("R30_MANIFEST_SHA256",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
print("COUNTS",json.dumps(manifest["new_counts"],sort_keys=True))
