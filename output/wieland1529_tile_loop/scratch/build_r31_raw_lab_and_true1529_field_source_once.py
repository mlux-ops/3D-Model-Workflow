"""One-time R31 substantive NEXT source-cycle, separate from signed full R30.
Creates source-only quantified evidence commissioning, not a formal R031 board.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from decimal import Decimal
import csv, io, json, hashlib

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"research"/"products"
STATE=BASE/"state"
STAMP="R31_20261106_"
EVIDENCE=OUT/(STAMP+"ORIGINAL_SKU_RAW_WET_TEST_AND_TRUE1529_SITE_DIMENSION_SOURCE.md")
LAB=OUT/(STAMP+"13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
WALL=OUT/(STAMP+"50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
UNIT=OUT/(STAMP+"26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
RECEIPT=STATE/"ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json"
FILES=(EVIDENCE,LAB,WALL,UNIT)
assert all(not p.exists() for p in (*FILES,RECEIPT)),"Do not rerun source-only creator"
R30_MANIFEST=BASE/"deliverables"/"integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement"/"MANIFEST.json"
R30_SHA="5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"
assert hashlib.sha256(R30_MANIFEST.read_bytes()).hexdigest()==R30_SHA
r17=BASE/"deliverables"/"integrated-r17"
rooms=json.loads((STATE/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
orig=list(csv.DictReader((r17/"R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig",newline="")))
walls=list(csv.DictReader((r17/"R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig",newline="")))
assert len(rooms)==13 and len(orig)==27 and len(walls)==25
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in orig)==Decimal("23572.44")
program={
 "PH-PRIMARY":("SELECTED_WALKIN_LINEAR_48IN_BNXL","BT0734816-BNX + BR73480 separate","NO_PRIMARY_NICHE","PARENT_PLUS_WC_LEVEL_INCLUDED_ONCE"),
 "PH-BATH2":("SELECTED_DURAVIT_TUB_NO_TILED_PAN","Hansgrohe Matte White; factory Duravit tub","SANDSTONE_NICHE_WET_LISTED","LEVEL_ONLY"),
 "PH-BATH3":("OWNER_TUB_OR_WALKIN_UNSELECTED","Chrome Hansgrohe; Delta DT062412 POINT only conditional WALKIN","OPAL_WALL_WET_NOT_LISTED_SANDSTONE_NICHE","LEVEL_PLUS_CONDITIONAL_POINT"),
 "PH-BATH4":("SELECTED_WALKIN_POINT","Brizo BT062415-BNX Black Onyx","CAVIAR_NICHE_UNVERIFIED_BONE_RIBBED_WET_WALL_NOT_LISTED","LEVEL_PLUS_FOUR_PLANE_POINT"),
 "PH-POWDER":("WOOD_DRY_POWDER","Brizo FLW wall and separate R65700","NO_SHOWER_NICHE","N_A"),
 "PH-WC":("INHERITED_PARENT_PRIMARY_LEVEL","TOTO Nexus source actual WC attribution unverified","NO_NICHE_NO_PAN","NO_INDEPENDENT_ORDER"),
 "TX-PRIMARY":("SELECTED_WALKIN_LINEAR_48IN_BNXL","Brizo 48in Black Onyx LINEAR + separate rough","NO_PRIMARY_NICHE","PARENT_PLUS_WC_LEVEL_INCLUDED_ONCE"),
 "TX-BATH2":("SELECTED_DURAVIT_TUB_NO_TILED_PAN","Hansgrohe Chrome; basin UNSELECTED","COPPER_WET_WALL_SANDSTONE_NICHE","LEVEL_ONLY"),
 "TX-BATH3":("OWNER_TUB_OR_WALKIN_UNSELECTED","Brizo Black Onyx BT062415-BNX POINT only conditional WALKIN","EMERALD_WET_MAKER_PAGE_REFRESH_SANDSTONE_NICHE","LEVEL_PLUS_CONDITIONAL_POINT"),
 "TX-BATH4":("SELECTED_DURAVIT_TUB_NO_TILED_PAN","Hansgrohe Matte White 72411701 spout pressure balance only vs 15758701 thermostat hold","CAVIAR_NICHE_UNVERIFIED_CHARCOAL_WET_LISTED","LEVEL_ONLY"),
 "TX-POWDER":("WOOD_DRY_POWDER","AXOR 48140991 trim vs Hansgrohe 32526141 trim; program unselected","NO_SHOWER_NICHE","N_A"),
 "TX-POWDER2":("WOOD_DRY_POWDER","Hansgrohe 73072341 DECK; basin UNSELECTED","INDIGO_DRY_FEATURE","N_A"),
 "TX-WC":("INHERITED_PARENT_PRIMARY_LEVEL","TOTO Nexus attributed to parent; TX203A UNPLACED","NO_NICHE_NO_PAN","NO_INDEPENDENT_ORDER"),
}
assert set(program)=={r["id"] for r in rooms}
floorrows={r["room"]:r for r in orig if r["source_surface"]=="floor"}
assert len(floorrows)==8
def csv_bytes(items):
    assert items
    out=io.StringIO(newline="")
    w=csv.DictWriter(out,fieldnames=list(items[0]),lineterminator="\n")
    w.writeheader();w.writerows(items)
    return out.getvalue().encode("utf-8-sig")
lab=[]
for rm in rooms:
    room=rm["id"]
    if room not in floorrows:continue
    source=floorrows[room]
    lab_specs=[("LEVEL","ACTIVE_ORIGINAL_SPECIMEN")]
    if room.endswith("PRIMARY"):
        lab_specs.append(("LINEAR_SLOPED_PAN","SELECTED_48IN_LINEAR_DRAIN_SEPARATE_SPECIMEN"))
    if room=="PH-BATH4":
        lab_specs.append(("POINT_FOUR_PLANE_SLOPED_PAN","SELECTED_4IN_SQUARE_POINT_DRAIN_SEPARATE_SPECIMEN"))
    if room in ("PH-BATH3","TX-BATH3"):
        lab_specs.append(("CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN","OWNER_WALKIN_NOT_SELECTED_NO_PAN_ORDER"))
    for surface,state in lab_specs:
        lab.append(dict(room=room,source_original_floor_row_id=source["source_row_id"],surface_role=surface,
         product_scope="ORIGINAL_EXACT_MAKER_SIZE_COLOR_FINISH_SAMPLE_MUST_BE_SEPARATELY_IDENTIFIED",source_program=program[room][0],
         selected_or_conditionally_active=state,
         physical_2_room_copies="2",
         historic_floor_quoted_GROSS_SF_one_copy_may_mingle_LEVEL_and_PAN=source["source_gross_sf_one_copy_waste_15pct_once"],
         historic_floor_material_ONLY_USD_two_copies=source["historic_usd_two_copies"],
         historic_15pct_waste_IN_GROSS_ALREADY="TRUE",
         level_and_pan_original_quote_area_SPLIT_VERIFIED="FALSE",
         original_exact_orderable_SKU_color_finish_caliber="UNKNOWN",
         exact_raw_wet_numeric_DCOF_reading="",
         original_manufacturer_lab_report_ID="",original_lab_test_standard_and_method="",
         wet_condition_water_medium_and_test_surface="",original_test_sample_size_finish_and_batch="",
         test_date="",manufacturer_individual_WET_surface_application_permission="UNVERIFIED_EXACT_ITEM",
         original_raw_result_receipt="FALSE",
         alternate_material_result_TRANSFER_ALLOWED="FALSE",
         individual_bath_LEVEL_may_substitute_PAN_test="FALSE",
         four_plane_pAN_or_linear_drain_physical_layout_verified="FALSE",
         actual_1529_site_floor_substrate_and_slope_verified="FALSE",
         trade_and_architect_test_approval="FALSE",
         owner_released="FALSE",purchase_authorized="FALSE"))
assert len(lab)==13,Counter(x["surface_role"] for x in lab)
assert Counter(x["surface_role"] for x in lab)==Counter({"LEVEL":8,"LINEAR_SLOPED_PAN":2,"CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN":2,"POINT_FOUR_PLANE_SLOPED_PAN":1})

unit=[]
for rm in rooms:
    room=rm["id"]; gpath=BASE/"rooms"/room/"geometry.json"
    geom=json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else {}
    candidates=geom.get("revit_room_numbers",[]) or rm.get("revit_room_numbers",[])
    assert len(candidates)==2,(room,candidates)
    for copy,source_id in enumerate(candidates,1):
        unit.append(dict(room=room,physical_copy_index=copy,source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED=source_id,
          exact_native_model_document_name="UNKNOWN_1529_NOT_CURRENT_1527",
          true_1529_field_property_validation="FALSE",
          program=program[room][0],selected_fixture_or_rough_nonnegotiable=program[room][1],
          original_wet_WALL_NICHE_gate=program[room][2],
          LEVEL_and_PAN_original_raw_lab_application=program[room][3],
          actual_floor_NET_SF="",separate_LEVEL_NET_SF="",separate_PAN_NET_SF="",
          measured_shower_point_or_linear_drain_centerline_XY_and_elevation="",
          verified_tub_flange_and_valve_spout_waste_geometry="",
          measured_1529_opening_door_and_window_locations="",
          measured_1529_niche_count_width_height_depth_sill_and_pipe_clashes="",
          actual_1529_document_built_revision_and_field_witness_signature="",
          owner_decision_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
          waterproof_trade_approved="FALSE",tile_installer_approved="FALSE",
          purchase_authorized="FALSE"))
assert len(unit)==26

wall_witness=[]
unit_ids={(r["room"],r["physical_copy_index"]):r["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"] for r in unit}
for w in walls:
    room=w["room"]
    for copy in (1,2):
        wall_witness.append(dict(room=room,physical_copy=copy,source_revit_room_number_UNVERIFIED=unit_ids[room,copy],
            wall_reference=w["wall"],
            prior_source_wall_width_in_UNVERIFIED=w["source_width_in_UNVERIFIED"],
            prior_source_tiled_height_in_UNVERIFIED=w["source_tiled_height_in_UNVERIFIED"],
            prior_source_nominal_full_field_SF=w["source_nominal_field_area_sf"],
            actual_TRUE_1529_field_width_in="",
            actual_TRUE_1529_tiled_height_in="",
            actual_TRUE_1529_wall_orientation_and_origin="",
            measured_window_door_other_openings_negative_WALL_NET_SF_once="",
            actual_niche_count_and_centerline_locations="",
            actual_niche_field_aperture_SF_to_deduct_ONCE="",
            separately_tiled_niche_back_SF="",separately_tiled_both_SIDE_SF="",
            separately_tiled_TOP_SF="",separately_tiled_SILL_SF="",
            actual_edge_profile_LF="",actual_movement_joint_locations_and_LF="",
            measured_valve_head_tub_flange_or_drains_and_service_clashes="",
            manufacturer_exact_tile_caliber_and_joint_for_3in_cuts="",
            signed_surfaces_NET_SF_minus_one_opening_plus_separate_niche_faces="",
            measured_original_native_1529_document_identity="",
            field_capture_exists="FALSE",architect_signed="FALSE",tile_and_waterproof_trade_signed="FALSE",
            purchase_authorized="FALSE"))
assert len(wall_witness)==50

note="""# R31 NEW consequential technical source — precise wet lab and actual 1529 witness identifiers

2026-11-06. Source-only, UNSENT/UNREVIEWED, not an official four-seat blind challenger/score. Prepared immediately after fully signed and audited R30. Original R12-R30 sources, owner programs, historical quantities, and all 13 room champions preserved. Do not use current Revit title 1527 as certified 1529. No contacts, orders, model or Smartsheet changes.

## New measurable escalation beyond R30

**Thirteen actually distinct wet-surface test-source roles** from **eight original quoted floor row IDs**: eight bathroom LEVEL original product wet-lab specimens; two Primary independently drained LINEAR PAN specimens (selected Brizo 48in/rough, no Primary niches); one PH-BATH4 actual WALK-IN independently four-plane square POINT PAN specimen (Brizo BT062415-BNX); two Bath3 **conditional** POINT PAN specimens only if the owner selects WALK-IN, with no new pan order while tub/walk-in remains UNSELECTED. TX-BATH4 Duravit TUB is LEVEL only, PAN N/A. Three dry/wood POWDER areas and two inherited Primary WC areas add no independent original source test rows or no new WC material orders. Actual raw wet numerical lab readings are **all UNKNOWN**; no brochure threshold substitutes for raw numerical data. Separate wet WALL and NICHE permissions are documented by factory item application letters, not by a floor lab result.

**Fifty** individual actual room-copy W1/W2/W3 field sheet targets (25 historical drawing-provisional W studies x two physical copies), preserving prior widths/heights and providing distinct blank actual measurement, actual openings, one niche field deduction, back, both sides, top and sill, corner/trim movement, fixture and pipe interference, dated true 1529 model ID and witness signoffs. **Twenty-six** room-source identity/site coordination records are distinct physical copy targets, not twenty-six purchased bath orders. TX203A is specifically UNPLACED until true field/model verification.

Manufacturer-facing original wet-lab evidence minimum required for every active one of thirteen surface roles: exact orderable SKU/manufacturer/color/finish/size, specimen and batch, original test standard/method, numeric original measured wet DCOF, report ID and date, substrate/use limitation (LEVEL vs four-plane POINT vs LINEAR slope), signed maker applicability, architect/installer review. A selected LEVEL material test cannot be assigned to a sloped PAN; a manufacturer >=0.42 / >0.50 / >=0.60 / Target >=0.42 threshold cannot replace a measured original numeric report. A conditional Bath3 POINT is not a selected pan and is never ordered.

Actual site verification shall independently capture floor construction, selected drain centerline/slope or Duravit tub 59in source fit, substrate plane, waterproof field and transitions. Confirm actual owner program before locating a CONDITIONAL Bath3 pan. PH4 owner 35SF vs prior 27SF and source 214.4SF vendor-total classification remain unresolved until certified field and vendor source partition. No assumption that an original floor quote includes a separately identified numeric LEVEL/PAN split.

## Procurement and governance

Across the original 27 material rows the original 15% gross allowance was already applied ONCE; original historical four-unit $23,572.44 remains unchanged. A correct new signed NET schedule is computed from actual measured site wall field minus actual original openings/one niche aperture plus separately measured niche back/two side/top/sill, with new documented wastage once, distinct level/pan, parent Primary/WC floors only once. Original 13 rooms, 25 historical W, 65 original trade actions unchanged. No verified current same-lot Chicago case/stock/price/freight/ETA/GC bid; no sample actually delivered. Original worker9 missing R014 Design, standing non-Pro Reviewer15 FINISHED; R017 private neutral governance untouched. This source-only research is **not** an independently cleared new board, independent CONTINUE, material/owner approval, or global DONE.

NEXT: obtain properly certified native 1529 identity or stamped field survey from existing authorized project documents; reconcile exact 13 product-surface lab-report requests and per physical copy geometry with actual selected manufacturer products and individual wet application, then engineer an integrated R31 shop/quote release only when new source results exist. All approval / purchasing flags FALSE.
"""
payload={EVIDENCE:note.encode("utf-8"),LAB:csv_bytes(lab),WALL:csv_bytes(wall_witness),UNIT:csv_bytes(unit)}
for p,b in payload.items():
    with p.open("xb") as f:f.write(b)
receipt={
  "round":31,"phase":"NEW_DISTINCT_SOURCE_ONLY_NOT_FORMAL_BLIND_BOARD",
  "date_local":"2026-11-06","predecessor_R30_FINAL_MANIFEST_SHA256":R30_SHA,
  "files":[{"relative":str(p.relative_to(BASE)).replace("\\","/"),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()} for p,b in payload.items()],
  "counts":{"exact_original_RAW_wet_lab_roles":len(lab),"original_LEVEL_slots":8,
    "selected_LINEAR_PAN_slots":2,"selected_POINT_PAN_slots":1,"conditional_POINT_PAN_slots":2,
    "two_copy_original_W_wall_witness_targets":len(wall_witness),
    "two_copy_room_instance_targets":len(unit)},
  "current_original_13_rooms":13,"historical_27_material_rows":27,"historical_25_W_studies":25,
  "historical_65_trade_actions_PRESERVED":True,"historical_USD_material_only":"23572.44",
  "original15pct_in_gross_once":True,"unselected_bath3_programs_preserved":True,
  "all_original_raw_numeric_lab_readings_known":False,"actual_1529_native_model_certified":False,
  "actual_current_Chicago_quote_and_lot":False,"original_four_seat_board_clearance":False,
  "independent_reviewer_accepted":False,"owner_signatures":False,"purchase_authorized":False,
  "global_13_room_objective_DONE":False}
RECEIPT.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8",newline="\n")
print("R31_NEW_SOURCE_RECEIPT_SHA256",hashlib.sha256(RECEIPT.read_bytes()).hexdigest())
print("R31_ROLES",Counter(x["surface_role"] for x in lab))
print("R31_OUTPUTS",len(FILES),"LAB",len(lab),"WALL",len(wall_witness),"UNIT",len(unit))
