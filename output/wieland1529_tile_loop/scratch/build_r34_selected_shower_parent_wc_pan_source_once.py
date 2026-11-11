"""One-time R34 substantive new SOURCE engineering, after signed full R33.

Separates already included Primary-WC LEVEL from selected Brizo LINEAR and
Brizo POINT sloped PAN. No geometric truth, raw lab, installed quote or PO.
"""
from __future__ import annotations
import csv,hashlib,io,json
from decimal import Decimal
from pathlib import Path

B=Path(__file__).resolve().parents[1]
R33=B/"deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json"
R33_HASH="a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"
assert hashlib.sha256(R33.read_bytes()).hexdigest()==R33_HASH
OUT=B/"research/products"
S=B/"state"
paths={
 "technical":OUT/"R34_20261106_ACTUAL_SELECTED_BRIZO_PRIMARY_WC_LEVEL_VS_PAN_GEOMETRY_COST_SOURCE.md",
 "areas":OUT/"R34_20261106_18_SELECTED_SHOWER_2COPY_LEVEL_WC_PAN_ALLOCATION_SCENARIOS.csv",
 "lab":OUT/"R34_20261106_12_PHYSICAL_SELECTED_SHOWER_LEVEL_AND_PAN_ORIGINAL_RAW_LAB_RECEIVERS.csv",
 "drain":OUT/"R34_20261106_6_SELECTED_BRIZO_POINT_LINEAR_ROUGH_MEMBRANE_THRESHOLD_DETAIL_RECEIVERS.csv",
 "wc":OUT/"R34_20261106_4_WC_PARENT_LEVEL_NO_DOUBLE_ORDER_WITNESSES.csv"}
rec=S/"ROUND034_DISTINCT_ORIGINAL_PRIMARY_WC_POINT_LINEAR_LEVEL_PAN_SOURCE_PREPARED_NOT_REVIEWED.json"
assert not rec.exists() and all(not x.exists() for x in paths.values()),"R34 source exists, do not overwrite"
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
room_src={x["id"]:x for x in json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
assert len(room_src)==13 and len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
rooms=("PH-PRIMARY","TX-PRIMARY","PH-BATH4")
wc={"PH-PRIMARY":("PH-WC",15),"TX-PRIMARY":("TX-WC",14),"PH-BATH4":(None,0)}
selected={
 "PH-PRIMARY":("BT0734816-BNX","BR73480","48in LINEAR Black Onyx"),
 "TX-PRIMARY":("BT0734816-BNX","BR73480","48in LINEAR Black Onyx"),
 "PH-BATH4":("BT062415-BNX","POINT_ROUGH_REQUIRE_MAKER_SPEC","4in SQUARE POINT Black Onyx")}
floor={x["room"]:x for x in old if x["source_surface"]=="floor"}
assert len(floor)==8
def csvb(rows):
    assert rows
    assert len({tuple(r.keys()) for r in rows})==1
    s=io.StringIO(newline="")
    w=csv.DictWriter(s,list(rows[0]),lineterminator="\n")
    w.writeheader();w.writerows(rows)
    return s.getvalue().encode("utf-8-sig")
def n4(x):return f"{x:.4f}"
sourcegeoms={}
for name in rooms:
    g=json.loads((B/"rooms"/name/"geometry.json").read_text(encoding="utf-8"))
    width=float(g["shower_or_tub_footprint"]["width"]["value"])
    depth=float(g["shower_or_tub_footprint"]["depth"]["value"])
    sourcegeoms[name]=dict(room_source_floor_SF=float(g["floor_area"]["value"]),source_shower_rect_SF=width*depth,
                           shower_width_in=width*12,shower_depth_in=depth*12,
                           numbers=g["revit_room_numbers"])
    assert len(g["revit_room_numbers"])==2
rows=[]
for name in rooms:
    gg=sourcegeoms[name];old_w=float(floor[name]["source_gross_sf_one_copy_waste_15pct_once"])
    wcname,wcn=wc[name]
    implied=(gg["room_source_floor_SF"]+wcn)*1.15
    for physical in gg["numbers"]:
        for branch in ("A_ORIGINAL_PARENT_ROOM_AREA_INCLUDES_SHOWER_PAN",
                       "B_ORIGINAL_PARENT_ROOM_AREA_EXCLUDES_SHOWER_PAN",
                       "C_SHOWER_PAN_BOUNDARY_UNCONFIRMED_NO_ORDER"):
            if branch.startswith("A"):
                lev=gg["room_source_floor_SF"]-gg["source_shower_rect_SF"]+wcn
                pan=gg["source_shower_rect_SF"]
            elif branch.startswith("B"):
                lev=gg["room_source_floor_SF"]+wcn
                pan=gg["source_shower_rect_SF"]
            else:
                lev=None;pan=None
            total=lev+pan if lev is not None else None
            rows.append(dict(room=name,source_physical_room=physical,branch=branch,
              original_parent_room_floor_area_SF_UNVERIFIED=n4(gg["room_source_floor_SF"]),
              original_WC_area_SOURCE_inherited_once_SF=n4(wcn),
              source_parent_WC_room_ID=wcname or "N_A_NO_INHERITED_WC",
              original_source_selected_shower_footprint_rect_SF_UNVERIFIED=n4(gg["source_shower_rect_SF"]),
              original_historic_floor_GROSS_SF_one_copy_15pct_included=n4(old_w),
              original_room_plus_WC_area_times_prior_1point15=n4(implied),
              historical_quoted_minus_source_rebuilt_gross_SF=n4(old_w-implied),
              hypothetical_distinct_LEVEL_NET_including_WC_once_SF=n4(lev) if lev is not None else "",
              hypothetical_distinct_SLOPED_PAN_NET_SF=n4(pan) if pan is not None else "",
              hypothetical_combined_LEVEL_plus_PAN_NET_SF=n4(total) if total is not None else "",
              hypothesis_1point15_new_NET_total_not_old_quote=n4(total*1.15) if total is not None else "",
              original_historical_tile_material_two_copy_USD=floor[name]["historic_usd_two_copies"],
              selected_true_drain=selected[name][0],
              selected_separate_rough=selected[name][1],
              actual_native_1529_floor_polygon_including_wc_or_pan="UNKNOWN",
              one_WC_tile_order_standalone="FALSE",
              independent_exact_LEVEL_raw_numeric_test_report="MISSING",
              independent_exact_PAN_raw_numeric_test_report="MISSING",
              proposed_purchasable_shower_PAN_material_exact_SKU_color_finish="UNKNOWN",
              actual_owner_approved_LEVEL_and_PAN_boundary="FALSE",
              new_quote_15pct_may_not_reapply_to_old_gross="TRUE",
              owner_signed="FALSE",purchase_authorized="FALSE"))
assert len(rows)==18
labs=[]
for name in rooms:
    gg=sourcegeoms[name]
    for physical in gg["numbers"]:
        for role in ("BATH_LEVEL_INHERITED_WC_ONCE" if wc[name][0] else "BATH_LEVEL",
                     "FOUR_PLANE_POINT_PAN" if name=="PH-BATH4" else "LINEAR_SLOPED_PAN"):
            labs.append(dict(room=name,physical_source_room=physical,role=role,
                exact_selected_drain=selected[name][0],selected_rough=selected[name][1],
                exact_original_laboratory_product_color_size_finish_and_SKU="",
                raw_original_measured_numeric_wet_DCOF="",
                manufacturer_original_lab_method_ID_batch_date="",
                specimen_surface_grade_LEVEL_or_SLOPED_PAN=role,
                other_surface_lab_interchangeable="FALSE",
                generic_target_bound_not_raw_numeric="TRUE",
                laboratory_result_received="FALSE",
                true_1529_measured_field_material_bearing_surface="",
                factory_wet_APPLICATION_for_selected_pan_or_level="UNKNOWN",
                signed_wet_surface_system_and_source_report="",
                actual_factory_same_color_finish_lot_case_US="UNKNOWN",
                owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(labs)==12
for row in labs:
    row["general_manufacturer_DCOF_threshold_not_accepted_as_raw_lab"]="TRUE"
drains=[]
for name in rooms:
    gg=sourcegeoms[name]
    for physical in gg["numbers"]:
        drains.append(dict(room=name,source_physical_room=physical,
          selected_drain=selected[name][0],required_separately_approved_rough=selected[name][1],
          original_drain_type=selected[name][2],
          source_shower_width_in_UNVERIFIED=n4(gg["shower_width_in"]),
          source_shower_depth_in_UNVERIFIED=n4(gg["shower_depth_in"]),
          source_footprint_square_SF_not_actual_1529=n4(gg["source_shower_rect_SF"]),
          actual_true_1529_shower_polygon_and_slab_thickness="",
          drain_centerline_or_linear_end_to_wall_distance="",
          measured_drain_top_and_membrane_bond_elevations="",
          actual_shower_perimeter_high_water_datum_and_threshold="",
          measured_min_slope_max_slope_and_4plane_lines="",
          approved_factory_point_or_linear_bonding_and_collar_system="FALSE",
          selected_grate_vs_tile_in_body_face_thickness_and_service_clearance="UNKNOWN",
          actual_slope_and_grout_geometry_with_chosen_small_pan_tile="",
          original_raw_wet_LEVEL_and_distinct_PAN_lab_received="FALSE",
          physical_1to1_drain_and_threshold_mockup_accepted="FALSE",
          confirmed_source_1529_CBC_and_maker_wet_assembly="FALSE",
          actual_same_factory_SKU_color_finish_pan_level_lot_case="UNKNOWN",
          supplier_chicago_lot_price_stock="UNKNOWN",GC_installed_labor_membrane_quote="UNKNOWN",
          owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(drains)==6
wcs=[]
for name in ("PH-PRIMARY","TX-PRIMARY"):
    wcname,area=wc[name]
    pnums=sourcegeoms[name]["numbers"]
    for i,physical in enumerate(pnums,1):
        wcs.append(dict(parent_room=name,parent_physical_room=physical,
          inherited_WC_room=wcname,parent_and_wc_original_floor_paid_once="TRUE",
          old_source_wc_area_SF_per_copy=n4(area),
          original_floor_row_id=floor[name]["source_row_id"],
          WC_selected_tile_format_original="Cortar Bone AntiSlip" if wcname=="PH-WC" else "Cortar Clay AntiSlip",
          actual_level_finish_match_vs_parent_SOFT_and_tile_caliber="NOT_VERIFIED",
          no_separate_WC_source_floor_bill="TRUE",independent_WC_pan="N_A",
          actual_wc_field_1529_id_verified="FALSE" if wcname=="TX-WC" else "FALSE",
          actual_wc_to_primary_transition_floor_recess_thickness="UNKNOWN",
          actual_wc_floor_level_wet_lab_as_parent_specimen_applicable="UNKNOWN_NEEDS_EXACT_SOFT_VS_ANTISLIP",
          owner_material_approved="FALSE",supplier_additional_WC_purchase="FALSE",
          purchase_authorized="FALSE"))
assert len(wcs)==4
md="""# R34 substantive NEXT selected Brizo shower-floor construction and source gross reconciliation

2026-11-06. DISTINCT source-only technical engineering following completed R33, not repeated R31 two-room slope simulations. Focus PH-PRIMARY, TX-PRIMARY and PH-BATH4: both Primaries retain owner selected **Brizo Black Onyx 48in LINEAR BT0734816-BNX** and separately required **BR73480** rough, NO additional Primary niches, and PH4 retains WALK-IN Black Onyx **BT062415-BNX square POINT** with its independent four-plane PAN. These are six physical shower copies. No owner selection or physical installation changed.

## Quantitative NEW finding: source Primary WC floor partition almost exactly explains historical mixed floor gross

PH Primary prior drawing **103 SF** bath plus historical **15 SF PH-WC**, both only source provisional; 118x1.15 = **135.7000 SF** while original floor quote carries **135.6 SF gross/copy**, difference -0.1000 SF. TX Primary **87 SF bath +14 SF TX-WC** -> 101x1.15 = **116.1500 SF** vs original **116.1 SF**, difference -0.0500 SF. PH4 owner floor **35 SF** -> 35x1.15 = **40.2500 SF** vs historical **40.2 SF**, difference -0.0500 SF. This is a valuable audit of likely source quote convention, NOT certified original physical net or current cut quantities. The WC portion is already included within its Primary floor source, **NEVER duplicate a separate order**. Original source floor gross includes 15% once.

## Three potentially incompatible interpretations of shower PAN inclusion

For each of six selected shower copies, new 18-row mutually exclusive branches distinguish (A) source bath floor area includes sloped shower PAN, (B) source bath floor area excludes sloped PAN, (C) boundary unconfirmed and order blocked. Under A, LEVEL=source bath - independent drawing-provisional shower rectangle + inherited WC area; PAN=source shower rectangle; under B, LEVEL=source bath + WC area while PAN is additionally included, leading to a larger hypothetical total. Neither establishes a room polygon, so no purchase or real shortage/credit follows.

The drawing-provisional selected shower rectangles are PH Primary 5.854x4.646ft (not certified true polygon), TX Primary 5.1875x4.7708ft, PH4 5x2.54ft. Rectangular shower footprint is only a sensitivity proxy; measured curb, linear recess, point four-plane facets, drain bodies and glass may alter the actual pan. Source floor material Soft vs AntiSlip or chosen new small-format pan cannot borrow wet test or exact measured raw numerical DCOF from the corresponding bath LEVEL source. Manufacturer floor DCOF >0.50, >=0.42 or Target >=0.42 remains insufficient.

## Six-instance selected drain assembly RFI and four WC material transition gates

R34 six explicit physical shower rough/membrane/threshold/shop witness records require original exact Brizo trim and rough, measured native 1529 centerline or wall-edge placement, actual slab/recess, independent high-water/drain top and waterproof membrane bonding heights, signed manufacturer connection and collar, adjustable grate thickness, maintenance access and real one-to-one bath LEVEL versus sloped PAN tile transition; selected LINEAR and POINT systems cannot substitute a foreign drain flange by inference. Primary LINEAR rough required exactly once per selected actual drain; do not duplicate TX source BR73480 mislabelled wall-edge trim. PH4 POINT four-plane shower floor needs separate selected manufacturer-approved small-format tile and original raw wet lab. Four WC source-copy rows require factory exact AntiSlip parent tile transition and no double order; TX203A original placement remains unverified.

## Physical and procurement next requirements

Before material order: authentic native 1529 model or independent site survey with room and shower polygon, wall/door/curb/wc boundary and structural slab elevations; factory individual tile SKU/color/size/finish, exact raw measured numerical wet LEVEL and PAN DCOF + report/date/method, independent maker approved wet WALL/NICHE where relevant, Brizo rough and membrane written interface, waterproof shop signed details, all trade witnesses and 1:1 slopes. Existing 27 original tile material rows and four-unit material-only **$23,572.44** with waste **15% once**, two excluded Primary niche refs, and inherited WC floors unchanged. Current Chicago case/lot, freight/ETA, installed GC waterproof labor unknown; no vendor contact, construction, sample, model edit, purchase, four-seat board score or independent non-Pro Reviewer clearance. Formal board R017, global 13-room objective OPEN.
"""
payload={paths["technical"]:md.encode("utf-8"),paths["areas"]:csvb(rows),
         paths["lab"]:csvb(labs),paths["drain"]:csvb(drains),paths["wc"]:csvb(wcs)}
for path,raw in payload.items():
    with path.open("xb") as f:f.write(raw)
receipt=dict(round=34,date_local="2026-11-06",
  phase="NEXT_CONSEQUENTIAL_SELECTED_SHOWER_WC_LEVEL_PAN_SOURCE_ONLY_NOT_BLIND_BOARD",
  predecessor_R33_full_SHA256=R33_HASH,
  files=[dict(path=p.relative_to(B).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
         for p,data in payload.items()],
  counts=dict(source_shower_programs=3,physical_selected_showers=6,
    mutually_exclusive_LEVEL_PAN_WC_area_scenarios=len(rows),independent_LEVEL_AND_PAN_physical_lab_roles=len(labs),
    selected_BRIZO_and_membrane_shop_receivers=len(drains),WC_parent_inherited_no_duplicate_orders=len(wcs)),
  true_1529_native_geometry_certified=False,exact_original_raw_wet_lab_received=False,
  confirmed_level_pan_order_quantities=False,WC_second_purchase=False,
  selected_hydraulic_drain_and_original_program_changed=False,
  current_chicago_supplier_quote=False,original_four_seat_board_complete=False,
  independent_nonpro_reviewer_accepted=False,owner_approved=False,purchase_authorized=False,
  global_DONE=False)
rec.write_bytes((json.dumps(receipt,indent=2)+"\n").encode("utf-8"))
print("R34_TECHNICAL_SOURCE_RECEIPT_SHA256",hashlib.sha256(rec.read_bytes()).hexdigest())
print("R34_FILES",len(payload),"AREA",len(rows),"LAB",len(labs),"DRAIN",len(drains),"WC",len(wcs))
