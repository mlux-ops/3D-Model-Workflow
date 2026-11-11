"""Strict independent local READ ONLY verifier for R31 21 signed outputs, historical chain.
Never creates/modifies any source, manifest, ledger or report.
"""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from decimal import Decimal
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"deliverables"/"integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity"
P=OUT/"MANIFEST.json"
manifest=json.loads(P.read_text(encoding="utf-8"))
digest=hashlib.sha256(P.read_bytes()).hexdigest()
assert digest=="b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457",digest
assert len(manifest["source_files"])==21 and len(list(OUT.iterdir()))==22
for f in manifest["source_files"]:
    b=(OUT/f["relative_path"]).read_bytes()
    assert len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"],f["relative_path"]

def csv_rows(prefix):
    filenames=[x["relative_path"] for x in manifest["source_files"] if x["relative_path"].startswith(prefix) and x["relative_path"].endswith(".csv")]
    assert len(filenames)==1,(prefix,filenames)
    with (OUT/filenames[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

original=csv_rows("R31_27_HISTORIC")
assert len(original)==27 and len({r["source_row_id"] for r in original})==27
assert sum(Decimal(r["historic_material_ONLY_USD_two_copies"]) for r in original)==Decimal("23572.44")
assert sum(r["original_unpriced_Primary_niche_reference_NO_ORDER"]=="TRUE" for r in original)==2
assert all(r["purchase_authorized"]=="FALSE" and r["historic_15PCT_NOT_REAPPLIED"]=="TRUE" for r in original)
with (BASE/"deliverables"/"integrated-r17"/"R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig") as f:
    old=list(csv.DictReader(f))
assert len(old)==27
for new in original:
    oldrow=next(x for x in old if x["source_row_id"]==new["source_row_id"])
    assert new["original_surface"]==oldrow["source_surface"] and new["room"]==oldrow["room"]
    assert Decimal(new["historic_material_ONLY_USD_two_copies"])==Decimal(oldrow["historic_usd_two_copies"] or "0")
    assert Decimal(new["source_gross_SF_one_copy_15PCT_included"])==Decimal(oldrow["source_gross_sf_one_copy_waste_15pct_once"])
with (BASE/"deliverables"/"integrated-r17"/"R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig") as f:
    walls=list(csv.DictReader(f))
assert len(walls)==25
with (BASE/"deliverables"/"integrated-r24-room-branch-shop-quantity-and-owner-decisions"/"R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig") as f:
    actions=list(csv.DictReader(f))
assert len(actions)==65
rooms=json.loads((BASE/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(rooms)==13
official={x["id"] for x in rooms}
assert len(official)==13
assert official=={"PH-PRIMARY","PH-BATH2","PH-BATH3","PH-BATH4","PH-POWDER","PH-WC","TX-PRIMARY","TX-BATH2","TX-BATH3","TX-BATH4","TX-POWDER","TX-POWDER2","TX-WC"}

for i in range(12,30):
    matches=[d for d in (BASE/"deliverables").glob(f"integrated-r{i}*") if (d/"MANIFEST.json").exists() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(matches)==1
    key=f"R{i:03d}_INTEGRATED_MANIFEST_SHA256"
    assert hashlib.sha256((matches[0]/"MANIFEST.json").read_bytes()).hexdigest()==manifest["immutable_predecessor_SHA256"][key]
r30=BASE/"deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json"
r31=BASE/"state/ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json"
assert hashlib.sha256(r30.read_bytes()).hexdigest()==manifest["immutable_predecessor_SHA256"]["R030_FINAL_INTEGRATED_MANIFEST_SHA256"]=="5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"
assert hashlib.sha256(r31.read_bytes()).hexdigest()==manifest["immutable_predecessor_SHA256"]["R031_PRELIMINARY_SOURCE_SHA256"]=="61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"
for k,path in [("R014_SUBMISSION","ROUND014_SUBMISSION.json"),("R015_SUBMISSION","ROUND015_SUBMISSION.json"),
               ("R016_SUBMISSION","ROUND016_SUBMISSION.json"),("R017_SUBMISSION","ROUND017_SUBMISSION.json")]:
    p=BASE/"state"/path
    assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest["immutable_predecessor_SHA256"][f"{k}_CURRENT_RECEIPT_SHA256"]

tub=csv_rows("R31_6_TWO_TUB")
assert len(tub)==6 and {x["room"] for x in tub}=={"PH-BATH2","TX-BATH4"}
assert all(x["no_tiled_shower_pan"]=="TRUE" and x["purchase_authorized"]==x["owner_approved"]=="FALSE" for x in tub)
assert {x["tier"] for x in tub}=={"GOOD","BETTER","BEST"}
assert any("15739701" in x["proposed_FACTORY_NOT_OWNER_APPROVED"] for x in tub)
assert any("72410701" in (x["proposed_FACTORY_NOT_OWNER_APPROVED"]+" "+x["original_owner_selected_program"]) for x in tub)
assert all("THREE" in x["three_independent_wet_outlet_roles"] or x["three_independent_wet_outlet_roles"].count(";")==2 for x in tub)
maker=csv_rows("R31_16_OFFICIAL")
assert len(maker)==16 and all(x["maker_URL"].startswith("https://") for x in maker)
assert any(x["exact_item_or_family"]=="72411701" and "pressure balance valve ONLY" in x["current_factory_claim_or_limitation"] for x in maker)
assert any(x["exact_item_or_family"]=="15758701" and "TWO outlets" in x["current_factory_claim_or_limitation"] for x in maker)
assert any(x["exact_item_or_family"]=="15739701" and "availability" in x["gate"].lower() for x in maker)
assert any(x["exact_item_or_family"]=="BR73480" and "MUST ORDER DRAIN TRIM" in x["current_factory_claim_or_limitation"] for x in maker)

tubfit=csv_rows("R31_18_TWO_TUB_ROUGH")
assert len(tubfit)==18
for r in tubfit:
    source=float(r["ORIGINAL_SOURCE_W1_SPAN_in_UNVERIFIED"])
    calc=source+float(r["fictional_field_delta_in"])-2*float(r["hypothetical_both_end_wall_finish_assembly_each_in"])
    assert abs(calc-float(r["hypothetical_after_two_end_FINISH_CLEAR_in"]))<.00011
    assert abs(calc-59-float(r["hypothetical_FINISH_clear_minus_TUB_in"]))<.00011
assert {r["room"] for r in tubfit}=={"PH-BATH2","TX-BATH4"}
stack=csv_rows("R31_48_VALVE")
assert len(stack)==48
for r in stack:
    total=sum(float(r[x]) for x in ("hypothetical_backer_in","hypothetical_compressed_mortar_in","hypothetical_calibrated_actual_TILE_BODY_in"))
    assert abs(float(r["subtotal_excluding_MEMBRANE_in"])-total)<.00011
    assert r["preliminary_depth_pass"]=="NOT_ASSESSABLE" and r["purchase_authorized"]=="FALSE"

slopes=csv_rows("R31_24_POINT")
assert len(slopes)==24
assert set(x["room"] for x in slopes)=={"PH-BATH4","TX-PRIMARY"}
for r in slopes:
    width=float(r["source_footprint_W_in_UNVERIFIED"])
    depth=float(r["source_footprint_D_in_UNVERIFIED"])
    rise=float(r["hypothetical_slope_rate_in_per_FT"])*float(r["conceptual_critical_run_in"])/12
    assert abs(width*depth/144-float(r["source_rectangle_AREA_SF_NOT_MEASURED"]))<.00011
    assert abs(rise-float(r["approximate_wet_surface_rise_in_NOT_APPROVED"]))<.00011
    assert r["raw_LEVEL_may_be_used_for_PAN"]=="FALSE"
    assert r["manufacturer_system_signed"]=="FALSE" and r["purchase_authorized"]=="FALSE"

split=csv_rows("R31_4_SELECTED_POINT")
assert len(split)==4
assert Counter(x["room"] for x in split)==Counter({"PH-BATH4":2,"TX-PRIMARY":2})
for r in split:
    level=float(r["hypothetical_LEVEL_net_SF"])
    pan=float(r["hypothetical_distinct_PAN_net_SF"])
    assert abs(level+pan-float(r["hypothetical_total_level_plus_pan_NET_SF"]))<.00011
    assert abs((level+pan)*1.15-float(r["hypothetical_15pct_once_IF_APPROVED_net_not_applied_to_old_gross_SF"]))<.00011
    assert r["actual_owner_floor_include_pan_clarified"]=="FALSE"

wallcases=csv_rows("R31_32_NEW_W1")
assert len(wallcases)==32
for r in wallcases:
    w=float(r["ORIGINAL_SOURCE_width_in_UNVERIFIED"])
    h=float(r["ORIGINAL_SOURCE_height_in_UNVERIFIED"])
    d=float(r["HYPOTHETICAL_measured_field_delta_in"])
    assert abs(w+d-float(r["trial_WIDTH_in_NOT_ACTUAL"]))<.00011
    assert abs((w+d)*h/144-float(r["raw_FIELD_GROSS_before_openings_SF"]))<.00011
    assert r["actual_1529_document"]=="NONE"
assert len({(r["room"],r["wall"]) for r in wallcases})==8
assert {r["wall"] for r in wallcases if r["room"]=="TX-PRIMARY"}=={"W1","W2"}

lab=csv_rows("R31_13_ORIGINAL_FLOOR")
assert len(lab)==13 and Counter(x["surface_role"] for x in lab)==Counter({
  "LEVEL":8,"LINEAR_SLOPED_PAN":2,"POINT_FOUR_PLANE_SLOPED_PAN":1,"CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN":2})
source=BASE/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv"
with source.open(encoding="utf-8-sig") as f:pr=list(csv.DictReader(f))
assert {(r["room"],r["surface_role"],r["original_floor_row_id"]) for r in lab}=={(r["room"],r["surface_role"],r["source_original_floor_row_id"]) for r in pr}
assert all(x["original_manufacturer_raw_measured_wet_numeric_DCOF"]=="" for x in lab)
assert all(x["generic_0_42_0_50_0_60_Target_threshold_acceptable"]=="FALSE" and x["purchase_authorized"]=="FALSE" for x in lab)
assert not any(x["room"]=="TX-BATH4" and "PAN" in x["surface_role"] for x in lab)
assert any(x["room"]=="PH-BATH4" and x["surface_role"]=="POINT_FOUR_PLANE_SLOPED_PAN" for x in lab)

walls=csv_rows("R31_50_TWO_COPY")
assert len(walls)==50 and {(x["room"],x["copy"],x["wall"]) for x in walls}=={(r["room"],r["physical_copy"],r["wall_reference"]) for r in csv.DictReader((BASE/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv").open(encoding="utf-8-sig"))}
assert all(r["site_and_trade_accepted"]==r["purchase_authorized"]=="FALSE" for r in walls)
assert all("MEASURED_W*H/144" in r["certified_NET_WALL_SF_formula"] for r in walls)
units=csv_rows("R31_26_ACTUAL")
assert len(units)==26 and len({(x["room"],x["copy_index"]) for x in units})==26
assert all(x["purchaser_signed"]==x["purchase_authorized"]=="FALSE" for x in units)
assert any(x["room"]=="TX-WC" and x["source_revit_room_number"]=="203A" and x["actual_1529_room_identification_status"]=="UNPLACED" for x in units)

choices=csv_rows("R31_12_FOUR")
assert len(choices)==12
assert Counter(x["room"] for x in choices)==Counter({"PH-BATH2":3,"TX-BATH4":3,"PH-BATH4":3,"TX-PRIMARY":3})
assert all(x["release"]==x["owner_approved"]=="FALSE" and x["weighted_board_score"]=="NULL" for x in choices)
assert all("BT062415" in x["fixtures_locked"] for x in choices if x["room"]=="PH-BATH4")
assert all("BR73480" in x["fixtures_locked"] for x in choices if x["room"]=="TX-PRIMARY")
assert all("DURAVIT_700332" in x["fixtures_locked"] for x in choices if x["room"] in ("TX-BATH4","PH-BATH2"))
assert all(x["no_tiled_PAN"]=="TRUE" for x in choices if x["room"] in ("TX-BATH4","PH-BATH2"))

groups=csv_rows("R31_9_ACTUAL")
assert len(groups)==9 and all(x["purchase_authorized"]=="FALSE" for x in groups)
camera=csv_rows("R31_16_ACTUAL")
assert len(camera)==16 and all(x["real_render_generated"]==x["actual_1to1_mockup_built"]==x["purchase_authorized"]=="FALSE" for x in camera)
release=csv_rows("R31_13_ROOM_SOURCE")
assert len(release)==13 and {x["room"] for x in release}==official
assert all(x["purchase_authorized"]==x["purchaser_material_reservation"]=="FALSE" for x in release)
assert next(r for r in release if r["room"]=="TX-BATH4")["room_SLOPED_PAN_raw_numeric_lab"]=="N_A_TUB_WOOD_OR_INHERITED_WC"
assert next(r for r in release if r["room"]=="PH-BATH4")["room_SLOPED_PAN_raw_numeric_lab"]=="MISSING_INDEPENDENT_SELECTED_FOUR_PLANE_POINT"
assert next(r for r in release if r["room"]=="TX-PRIMARY")["room_SLOPED_PAN_raw_numeric_lab"]=="MISSING_INDEPENDENT_LINEAR"
assert next(r for r in release if r["room"]=="PH-POWDER")["room_wet_LEVEL_raw_numeric_lab"]=="N_A_WOOD"
assert next(r for r in release if r["room"]=="TX-POWDER2")["room_wet_LEVEL_raw_numeric_lab"]=="N_A_WOOD"
assert "UNSELECTED" in next(r for r in release if r["room"]=="TX-BATH3")["actual_source_program_and_top_FIX"]
trades=csv_rows("R31_104_ROOM")
assert len(trades)==104 and Counter(r["trade"] for r in trades)==Counter({x:13 for x in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")})
assert all(x["purchase_authorized"]==x["original_4critics_complete"]=="FALSE" for x in trades)
cost=csv_rows("R31_13_ROOM_HISTORIC")
assert len(cost)==13 and sum(Decimal(x["original_two_copy_material_only_QUOTED_USD"]) for x in cost)==Decimal("23572.44")
assert all(x["purchase_authorized"]=="FALSE" for x in cost)

for key in ("actual_native_1529_verified","all_numeric_original_raw_lab_reports_known","owner_approved","purchase_authorized",
            "original_four_specialists_complete","independent_nonpro_reviewer_accepted","global_13room_DONE"):
    assert manifest[key] is False,key
assert manifest["weighted_board_score"] is None
assert manifest["new_schedules"]["wall_field_survey_rows"]==50 and manifest["new_schedules"]["room_copy_witness_rows"]==26
print("PASS R31 INTEGRATED 21/21 SHA AND BYTE outputs, 18 R12-R29 signed predecessors, R30+source R31 exact")
print("PASS 13 rooms/27 historical rows (2 no order)/25 wall/65 trade, $23,572.44 with prior 15 percent once")
print("PASS tub6/fit18/rough48/point-linear slope24/split4/W32 and 13 distinct original wet specimen roles; real lab blanks")
print("PASS 50 wall +26 physical instance +12 owner tiers +16 unmade mockups +13 release/104 trades, ALL FALSE")
print("R31_FULL_MANIFEST_SHA256",digest)
