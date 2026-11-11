"""R35 one-time additive integrated Primary/WC manufacturer, installation and quote engineering.
All source geometry is drawing-provisional, not verified 1529.
No prior source rewrite, no Git/Revit/Smartsheet/vendor/owner action.
"""
from __future__ import annotations
import csv,hashlib,io,json,math
from decimal import Decimal
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]
OUT=P/"deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC"
assert not OUT.exists(),"R35 already exists - one-time creator prohibited"
S={
 "R30":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
 "R31_SOURCE":("state/ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json","61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"),
 "R31_FULL":("deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/MANIFEST.json","b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457"),
 "R32_SOURCE":("state/ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json","9ad8564e2676f4e72533e6830bea627757e393dc1cdc537b297d443caae962b4"),
 "R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"),
 "R34_SOURCE":("state/ROUND034_DISTINCT_ORIGINAL_PRIMARY_WC_POINT_LINEAR_LEVEL_PAN_SOURCE_PREPARED_NOT_REVIEWED.json","c00f011dfb83ad27360c2caebd7038a60caac4ba59647df51a6dea1c65b4ec22")
}
for name,(path,h) in S.items():assert hashlib.sha256((P/path).read_bytes()).hexdigest()==h,name
def readcsv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def F(x):return f"{x:.4f}"
def M(x):return f"{x:.2f}"
def truth(x):return "TRUE" if x else "FALSE"
old=readcsv(P/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
w25=readcsv(P/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
old65=readcsv(P/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
raw13=readcsv(P/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
walls50=readcsv(P/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
rooms26=readcsv(P/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
r34=readcsv(P/"research/products/R34_20261106_18_SELECTED_SHOWER_2COPY_LEVEL_WC_PAN_ALLOCATION_SCENARIOS.csv")
rc=json.loads((P/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
ids={r["id"] for r in rc};byroom={r["id"]:r for r in rc}
assert (len(old),len(w25),len(old65),len(raw13),len(walls50),len(rooms26),len(r34),len(ids))==(27,25,65,13,50,26,18,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
FOCUS=("PH-PRIMARY","PH-WC","TX-PRIMARY","TX-WC")
parents=("PH-PRIMARY","TX-PRIMARY")
W={(r["room"],r["wall"]):r for r in w25}
HIST={(r["room"],r["source_surface"]):r for r in old}
assert all((r,"W3") not in W for r in parents)
geos={r:json.loads((P/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in FOCUS}
source={
 "PH-PRIMARY":{"wc":"PH-WC","wcarea":15,"area":103,"gross":135.6,"panwidth":5.854,"pandepth":4.646,"LEVEL":"Cortar Bone Soft 24x48 source conditional","WC":"Cortar Bone AntiSlip 24x48 seeded","PAN":"Original AntiSlip PAN format vs conditional RL21 hex requires exact wet factory source"},
 "TX-PRIMARY":{"wc":"TX-WC","wcarea":14,"area":87,"gross":116.1,"panwidth":5.1875,"pandepth":4.7708,"LEVEL":"Cortar Clay Soft 24x48 source conditional","WC":"Cortar Clay AntiSlip 24x48 seeded","PAN":"Original AntiSlip PAN format vs conditional RL21 hex requires exact wet factory source"}}
for room,d in source.items():
    g=geos[room]
    assert g["floor_area"]["value"]==d["area"] and geos[d["wc"]]["floor_area"]["value"]==d["wcarea"]
    assert abs(g["shower_or_tub_footprint"]["width"]["value"]-d["panwidth"])<1e-9
    assert len(g["revit_room_numbers"])==2 and len(geos[d["wc"]]["revit_room_numbers"])==2
    assert abs(float(HIST[(room,"floor")]["source_gross_sf_one_copy_waste_15pct_once"])-d["gross"])<1e-9
    codes=[str(f["model_or_sku"]) for f in json.loads((P/"rooms"/room/"plumbing.json").read_text(encoding="utf-8"))["fixtures"]]
    assert codes.count("BT0734816-BNX")==1 and codes.count("BR73480")==2
assert all(len(geos[r]["tiled_walls"])==0 for r in ("PH-WC","TX-WC"))
assert len(json.loads((P/"research/comps/comps.json").read_text(encoding="utf-8"))["comps"])==14
FILES={}
def csvout(name,records):
    assert records and len(set(tuple(r.keys()) for r in records))==1,(name,len(records))
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(records[0]),lineterminator="\n")
    w.writeheader();w.writerows(records);FILES[name]=s.getvalue().encode("utf-8-sig")
def mdout(name,body):FILES[name]=(body.rstrip()+"\n").encode("utf-8")
URLS={
 "BRIZO_TRIM":"https://www.brizo.com/bath/product/BT0734816-BNX",
 "BRIZO_ROUGH":"https://www.brizo.com/bath/product/BR73480",
 "BRIZO_WALLEDGE":"https://www.brizo.com/bath/product/BT0734870-PC",
 "DALTILE_RL21":"https://www.daltile.com/products/stone-look/prime/dynamic-beige",
 "DALTILE_BROCHURE":"https://digitalassets.daltile.com/content/dam/Daltile/website/resources/products/product-brochures/core-fundamentals-prime/DAL_CoreFundamentals_Brochure_Prime.pdf",
 "DALTILE_ACUTEST":"https://www.daltile.com/why-daltile/industry-standards/dcof-slip-resistance-testing-reading-test-results",
 "TOTO_NEXUS":"https://www.totousa.com/nexus-one-piece-toilet-128-gpf-elongated-bowl",
 "ELM_CORTAR":"https://www.elmsurfaces.com/product-collection/cortar"
}

# 8 independently BALANCED branch-specific physical floor accounting rows.
account=[]
for room,d in source.items():
    for copy in geos[room]["revit_room_numbers"]:
        pan=d["panwidth"]*d["pandepth"]
        for branch in ("A_PAN_INCLUDED_IN_ORIGINAL_BATH_FLOOR","B_PAN_EXCLUDED_FROM_ORIGINAL_BATH_FLOOR"):
            included=branch.startswith("A")
            lev=d["area"]-pan if included else d["area"]
            wc=d["wcarea"]
            signed=lev+wc
            total=signed+pan
            reconstructed_base=d["area"]+wc
            gross_original=d["gross"]
            grossA=(d["area"]+wc)*1.15
            gross_model=total*1.15
            gross_extra=0 if included else pan*1.15
            historic=Decimal(HIST[(room,"floor")]["historic_usd_two_copies"])
            historic_rate=historic/(Decimal(str(d["gross"]))*2)
            # Intentional historic blended material-only sensitivity -- NOT
            # an actual possible PAN price, and not an accepted credit.
            account.append(dict(room=room,physical_parent_source_copy=copy,linked_WC_room=d["wc"],
              branch=branch,mutually_exclusive_with="B" if included else "A",
              source_bath_area_SF_unverified=F(d["area"]),source_inherited_WC_area_SF_unverified=F(wc),
              source_selected_LINEAR_RECTANGLE_pan_area_SF_unverified=F(pan),
              hypothetical_bath_LEVEL_excluding_PAN_NET_SF=F(lev),
              hypothetical_inherited_WC_LEVEL_NET_SF=F(wc),
              hypothetical_total_LEVEL_NET_SF=F(signed),
              hypothetical_distinct_LINEAR_PAN_NET_SF=F(pan),
              hypothetical_unique_total_LEVEL_plus_PAN_NET_SF=F(total),
              source_reconstructed_original_bath_plus_wc_NET_SF=F(reconstructed_base),
              historic_original_floor_GROSS_SF_per_copy_waste15pct_once=F(gross_original),
              reconstructed_original_waste15pct_once_GROSS_SF=F(grossA),
              source_reconstruction_minus_historic_quote_GROSS_SF=F(grossA-gross_original),
              hypothetical_prospective_LEVEL_GROSS_at_1point15_SF=F(signed*1.15),
              hypothetical_prospective_PAN_GROSS_at_1point15_SF=F(pan*1.15),
              hypothetical_unique_total_GROSS_at_1point15_SF=F(gross_model),
              hypothetical_PAN_GROSS_INCREMENT_BRANCH_B_over_A_SF=F(gross_extra),
              historical_two_copy_floor_material_only_USD=str(historic),
              historic_mixed_floor_rate_USD_per_GROSS_SF_REFERENCE_ONLY=F(float(historic_rate)),
              theoretical_incremental_BLEND_RATE_proxy_USD_nonpayable=M(float(historic_rate)*gross_extra),
              known_quoted_old_level_vs_pan_material_breakdown="UNKNOWN_MIXED_ORIGINAL_ROW",
              verified_ordered_shipped_installed_paid_mixed_floor="UNKNOWN",
              actual_1529_drain_pan_wc_polygon="UNKNOWN",
              actual_raw_LEVEL_and_distinct_PAN_lab="MISSING",
              new_supplier_pan_vs_level_rate_and_case_usable_SF="UNKNOWN",
              actual_case_rounding_or_offcut_reuse="UNKNOWN",
              installed_GC_quote_credit_backer_membrane_threshold="UNKNOWN",
              original15percent_not_reapplied_to_historical_gross="TRUE",
              no_WC_separate_purchase="TRUE",no_payable_shortage_established="TRUE",
              source_geometry_certified="FALSE",owner_approved="FALSE",
              GC_authorized="FALSE",purchase_authorized="FALSE"))
assert len(account)==8
csvout("R35_8_TWO_COPY_MUTUALLY_EXCLUSIVE_PRIMARY_WC_LEVEL_LINEAR_PAN_FULL_BALANCE.csv",account)

# Cost is documented as contractual open ledger, not invented bid.
forbidden=[
 ("SOURCE_FLOOR_ALREADY_HISTORICAL","Original dated 2026 historic floor gross including WC once","Original $/GROSS material-only included 15pct once; no extra order"),
 ("PAN_INCLUDED_A","If original bath contains LINEAR PAN, subtract PAN from bath before computing LEVEL plus WC","Historical gross only once; separate new PAN SKU with owner approval requires proper original credit/reclassification"),
 ("PAN_EXCLUDED_B","If original bath excludes PAN, original quote may describe LEVEL+WC only","Additional separately measurable PAN scope must have written original quotation exclusions, actual maker SKU, installer bid, owner CO before payable"),
 ("WC_INCLUDED_ONCE","WC has zero separate historic material rows, matched parent source","Retained AntiSlip vs parent Soft is finish-specific new SKU not automatically identical to original mixed source"),
 ("PARENT_WC_FINISH_CONFLICT","Primary Soft LEVEL vs selected WC AntiSlip","Cannot pool cases as same SKU, require actual current factory selected floor legend and calibrated transition"),
 ("PAN_MAKER_LAB_HOLD","LINEAR shower PAN cannot borrow LEVEL original numerical wet test","Exact independent raw measured original lab and maker linear application required"),
 ("LOT_AND_CASE","Public 12x24 RL21 15.04/17.49SF cartons from distinct seller listings are not validated supplier cases","No available-current Chicago lot, origin or 1.5 hex usable case yield, no order or savings"),
 ("THRESHOLD_LABOR","Separate drain rough/pitch, curb or curbless membrane, perimeter movement, trims, grout and waterproof mockup","Unknown installed GC bid and written CO credit, do not collapse into original material-only rate"),
]
csvout("R35_8_HISTORIC_CONTRACT_SCOPE_LINE_CREDITS_MATERIAL_ONLY_VS_INSTALLED_BID_DO_NOT_DOUBLE_CHARGE.csv",[
 dict(scope_code=code,classification=classification,contract_control=description,
      source_historic_tile_cost_included_once="TRUE",new_owner_CO_established="FALSE",
      current_chicago_vendor_date_case_lot_offer="",current_installed_subtrade_signed_bid="",
      original_quoted_inclusion_exclusion_signed_vendor_line="",
      procurement_release="FALSE")
 for code,classification,description in forbidden])

# Eight physical parent/WC controls. No WC standalone floor material PO.
unitpairs=[]
for p,d in source.items():
    for pcopy,wcopy in zip(geos[p]["revit_room_numbers"],geos[d["wc"]]["revit_room_numbers"]):
        for typ in ("PRIMARY_LEVEL_AND_LINEAR_PAN","INHERITED_WC_LEVEL"):
            unitpairs.append(dict(primary_room=p,source_primary_copy=pcopy,
                linked_WC_room=d["wc"],source_wc_copy=wcopy,
                physical_zone=typ,original_floor_material_row=HIST[(p,"floor")]["source_row_id"],
                selected_fixture="BT0734816-BNX_BR73480_ONCE_EACH" if typ.startswith("PRIMARY") else
                   "WC_TILE_INHERITS_PARENT_ORDER_NO_WC_PLUMBING_ASSIGNMENT",
                source_wc_AREA_SF_unverified=F(d["wcarea"]),
                source_WC_to_Primary_portal_width_or_threshold="NOT_MEASURED",
                source_wc_true_spatial_identity="TX203A_UNPLACED" if wcopy=="203A" else "UNVERIFIED_SOURCE_REFERENCE",
                actual_WC_Nexus_toilet_Unifit_vs_door_attribute="NOT_VERIFIED_OR_ASSIGNED_WC",
                parent_level_finish_soft_identity=d["LEVEL"],WC_selected_finish_antiSlip=d["WC"],
                original_source_parent_level_pan_scope="QUOTED_MIXED_PENDING_A_VS_B",
                original_WC_separate_historical_row_exists="FALSE",
                WC_own_new_order_authorized="FALSE",
                raw_wet_LEVEL_for_exact_WC_finish_and_Parent="MISSING_DIFFERENT_FINISH_TESTS_NOT_TRANSFERABLE",
                actual_level_tile_thickness_and_soft_antiSlip_transition="",
                actual_finished_surface_WC_threshold_profile_length="",
                actual_room_boundaries_verified_native_1529="FALSE",
                actual_ANSI_wet_lab_and_drains_compliant_signoff="FALSE",
                architect_signed="FALSE",tile_installer_signed="FALSE",
                owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(unitpairs)==8
csvout("R35_8_PRIMARY_WC_PHYSICAL_SOURCE_ROOM_LINKED_THRESHOLD_TOILET_NO_DOUBLE_ORDER_GATE.csv",unitpairs)

# Maker declarations are application evidence, NEVER original measured wet lab
# or actual factory approval for a combined waterproof membrane.
manufacturer=[
("Brizo","BT0734816-BNX","Brilliance Black Onyx 48in reversible LINEAR drain","OWNER_SELECTED_PH_TX","current maker exact selected finish",URLS["BRIZO_TRIM"],"Dual solid or tile-in frame, specified tile thickness 7-18mm; rough separately required", "UNIT_MAKER_LIST_$825_INDICATION_NOT_OUR_VENDOR"),
("Brizo","BR73480","48in linear rough channel","OWNER_SELECTED_SEPARATE_ROUGH","current maker exact part",URLS["BRIZO_ROUGH"],"Water Protection System secondary drainage, height risers, hair catcher; do not transfer third-party membrane", "UNIT_MAKER_LIST_$684_INDICATION_NOT_OUR_VENDOR"),
("Brizo","BT0734870 family","48in optional finish-matched wall-edge extension","UNSELECTED_OPTION","maker current Chrome sibling demonstrates product type, BNX exact finish NOT certified",URLS["BRIZO_WALLEDGE"],"Original BR73480 labelled Wall Edge Trim is a duplicate rough reference, not wall-edge trim; do NOT auto-order", "UNKNOWN_BNX_SKU_LOT_MSDS"),
("Daltile","RL21 Dynamic Beige hex mosaic","1.5in hex Matte Mexico nominal 5/16in (7.9375mm)","UNSELECTED_PAN_ALT","official individual maker current color page",URLS["DALTILE_RL21"],"Conditional mosaic shower/linear application; maker Target is not raw numeric individual wet laboratory; 1/8 vs 3/16 grout source disputed", "CURRENT_SKU_OR_CASE_UNKNOWN"),
("Daltile","RL21 Dynamic Beige older mosaic brochure","1.5in hex Matte brochure nominal 1/4in (6.35mm)","UNSELECTED_VERSIONED_PAN_ALT","older maker brochure identity version does NOT resolve current mosaic SKU",URLS["DALTILE_BROCHURE"],"Brochure older Target >=0.60 vs later >=0.42 not raw numeric results; 6.35mm chip below 7mm frame nominal, not installed proof", "NOT_CURRENT_MATERIAL_PRICE"),
("Daltile","RL21 Dynamic Beige 12x24 Matte","12x24 nominal 3/8in U.S. manufacture","UNSELECTED_LEVEL_ALT","maker individual color page",URLS["DALTILE_RL21"],"Separate LEVEL product, distinct SKU/lot, Target >=0.42 not an original measured raw test; not interchangeable with Mexican hex", "PUBLIC_RETAIL_INDICATIONS_NOT_CHICAGO"),
("ELM Cortar","Bone Soft 24x48","Original PH Primary LEVEL historical source","HISTORIC_SOURCE_NOT_NEW_SELECTION","original project handoff + maker collection, exact item letter missing",URLS["ELM_CORTAR"],"Individual exact color/finish and original raw numeric wet LEVEL DCOF missing","HISTORIC_BLENDED_FLOOR_ONLY"),
("ELM Cortar","Bone AntiSlip 24x48","PH WC original seeded finish","ORIGINAL_WC_SELECTED_NO_EXTRA_ORDER","original v4 owner WC only maker individual evidence needed",URLS["ELM_CORTAR"],"Soft wet tests do not authorize AntiSlip, no automatic case pooling against Soft","PARENT_QUOTE_INCLUDED_ONCE"),
("ELM Cortar","Clay Soft 24x48","Original TX Primary LEVEL historical source","HISTORIC_SOURCE_NOT_NEW_SELECTION","original project handoff + maker collection",URLS["ELM_CORTAR"],"Independent exact original raw wet LEVEL lab and tile caliber missing","HISTORIC_BLENDED_FLOOR_ONLY"),
("ELM Cortar","Clay AntiSlip 24x48","TX WC original seeded finish","ORIGINAL_WC_SELECTED_NO_EXTRA_ORDER","original v4 owner WC only maker individual evidence needed",URLS["ELM_CORTAR"],"Source TX203A physically unplaced; no independent WC purchase or raw lab transfer","PARENT_QUOTE_INCLUDED_ONCE"),
("TOTO","MS642124CEFG#01","Nexus original PH/TX Parent source toilet","SOURCE_PARENT_TOILET_NOT_IN_WC_LIST","TOTO factory selected toilet, location yet to confirm",URLS["TOTO_NEXUS"],"Actual toilet location, genuine UniFit dimensions/door and flooring threshold must be field-confirmed; no second toilet","PUBLIC_MAKER_LIST_NOT_QUOTE")
]
csvout("R35_11_INDIVIDUAL_FACTORY_LINEAR_DRAIN_RL21_CORTAR_WC_FINISH_AND_MAKER_GATES.csv",[
 dict(manufacturer=m,product_identity=part,source_description=descr,owner_status=status,
      individual_product_evidence_grade=grade,manufacturer_or_original_source_url=url,
      factory_interface_and_application_gate=gate,price_classification=price,
      exact_current_orderable_SKU_color_size_finish_factory_lot="UNKNOWN",
      original_RAW_wet_numeric_DCOF_report_id_date="MISSING_OR_N_A_FOR_NON_TILE",
      full_1529_selected_membrane_AND_rough_compatibility_letter="",
      actual_calibrated_body_and_installed_thickness="",
      owner_material_substitution_approved="FALSE",purchase_authorized="FALSE")
 for m,part,descr,status,grade,url,gate,price in manufacturer])

# Tile-in chip versions vs 7..18mm maker frame; two grout widths represent
# documented conflicting snapshots only. Each is a separate construction
# branch, not a finalized installation adjustment or manufacturer finding.
frames=[]
for room in parents:
    for copy in geos[room]["revit_room_numbers"]:
        for kind,chip in (("SOLID_BNX_FINISH_MATCHED_NO_TILE_INSERT",None),
                          ("TILEIN_OLDER_RL21_BROCHURE_1OVER4IN",6.35),
                          ("TILEIN_CURRENT_RL21_MAKER_5OVER16IN",7.9375)):
            for grout in (.125,.1875):
                below=None if chip is None else chip-7
                frames.append(dict(room=room,physical_primary_source_copy=copy,
                    source_selected_Brizo_trim="BT0734816-BNX",
                    source_separate_required_rough="BR73480",
                    selected_MAKER_frame_tile_adjustment_mm_min="7",
                    selected_MAKER_frame_tile_adjustment_mm_max="18",
                    frame_mode_alternative=kind,
                    source_chip_mosaic_nominal_BODY_mm=F(chip) if chip is not None else "N_A_SOLID_GRATE",
                    original_chip_mm_minus_min_frame_mm=F(below) if below is not None else "N_A_SOLID_GRATE",
                    frame_nominal_chip_gate=("N_A_SOLID_GRATE_BYPASSES_TILE_INSERT" if chip is None else
                        "BELOW_NOMINAL_7MM_CHIP_HOLD_NO_THINSET_TRICK" if chip<7 else
                        "WITHIN_NOMINAL_CHIP_LIMIT_BUT_ASSEMBLY_UNKNOWN"),
                    RL21_competing_maker_grout_snapshot_in=F(grout),
                    maker_exact_SKU_and_format_joint_approval="UNRESOLVED_1OVER8_VS_3OVER16",
                    calibrated_tile_carrier_and_insert_bed_mortar_thickness_mm="UNKNOWN",
                    actual_waterproof_MEMBRANE_tiling_substrate_plane_mm="UNKNOWN",
                    drain_channel_riser_height_and_grate_top_actual_Z="UNKNOWN",
                    actual_watertight_connection_and_maker_written_approval="FALSE",
                    drain_wall_edge_optional_extension_required="UNKNOWN_NOT_AUTO_BR73480",
                    factory_grate_removal_cleaning_access_mockup="FALSE",
                    owner_option_selected="FALSE",purchase_authorized="FALSE"))
assert len(frames)==24
csvout("R35_24_SIX_PRIMARY_BRIZO_SOLID_VS_2_VERSION_RL21_TILEIN_FRAME_JOINT_1to1_SECTIONS.csv",frames)

# Manufacturer threshold/slope is only an illustrative gradeline. A certified
# threshold must be derived from code, structural conditions, manufacturer
# instruction, physical doorway and true shower polygon.
slopes=[]
for room in parents:
    d=source[room]
    depth=d["pandepth"]
    for copy in geos[room]["revit_room_numbers"]:
        for branch in ("A_PAN_INCLUDED_IN_ORIGINAL_BATH_FLOOR","B_PAN_EXCLUDED_FROM_ORIGINAL_BATH_FLOOR"):
            for placement in ("WALL_ALIGNED_LINEAR_WITH_OPTIONAL_SEPARATE_TRIM",
                              "FREE_STANDING_LINEAR_WITH_END_GAP_UNVERIFIED"):
                for rate in (.125,.25):
                    rise=depth*rate
                    slopes.append(dict(room=room,physical_primary_source_copy=copy,
                        mutually_exclusive_quote_branch=branch,
                        drain_selected_trim="BT0734816-BNX",
                        drain_selected_separate_rough="BR73480",
                        hypothetical_linear_drain_placement=placement,
                        source_shower_depth_FT_UNVERIFIED=F(depth),
                        assumed_uniform_sloped_pan_FALL_in_per_foot_NOT_CODE=F(rate),
                        theoretical_perimeter_to_drain_rise_inches_not_shop=F(rise),
                        actual_drain_body_top_elevation_Z="",actual_linear_rough_outlet_Z="",
                        actual_membrane_lower_flange_or_watertight_system_top_Z="",
                        actual_shower_perimeter_edge_Z="",actual_tub_bath_LEVEL_finished_Z="",
                        actual_door_threshold_and_finished_access_clearance_Z="",
                        actual_wc_finished_level_plus_antiSlip_transition_Z="",
                        measured_1529_slab_recess_structural_floor_thickness="UNKNOWN",
                        actual_slope_CODE_and_maker_grade_approved="FALSE",
                        actual_membrane_compatible_Brizo_WPS_written_system="FALSE",
                        factory_drain_cleanability_1to1_witness="FALSE",
                        GC_installed_labor_and_screed_bid="UNKNOWN",
                        owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(slopes)==32
csvout("R35_32_PRIMARY_SOURCE_PAN_GRADE_THRESHOLD_WC_DATUM_MEMBRANE_DRAIN_SYSTEM_SECTIONS.csv",slopes)

# Original W1 and W2 only; NEVER claim the absent W3 as known measured wall.
cuts=[]
for room in parents:
    for wall in ("W1","W2"):
        span=float(W[room,wall]["source_width_in_UNVERIFIED"])
        height=float(W[room,wall]["source_tiled_height_in_UNVERIFIED"])
        for central in (1,2):
            for joint in (.125,.1875,.25):
                long=24.
                end=(span-central*long-(central+1)*joint)/2
                cuts.append(dict(room=room,source_shower_wall=wall,
                    source_1529_verified_wall_model_ID="",
                    source_width_in_UNVERIFIED=F(span),
                    source_height_in_UNVERIFIED=F(height),
                    nominal_Bone_or_Clay_wall_LONG_axis_tile_in=F(long),
                    intentional_central_full_tiles=central,illustrative_joint_in=F(joint),
                    theoretical_symmetric_left_and_right_focal_cut_in=F(end),
                    project_min3in_focal_cut_test=("PASS_THEORY" if end>=3 and end<=long else "FAIL_THEORY"),
                    actual_24in_tile_caliber_and_brick_offset="UNKNOWN",
                    actual_shower_escutcheon_and_glass_cut_interference="UNKNOWN",
                    original_NICHES_in_Primary="NONE_NO_NEW",
                    actual_door_window_other_aperture_FIELD_deduction_SF="",
                    source_full_field_SF_before_any_opening=F(span*height/144),
                    actual_SIGNED_net_wall_SF="",
                    actual_waterproof_wet_WALL_item_permission="UNKNOWN",
                    actual_exposed_EDGE_profile_LF="",actual_MOVEMENT_joint_LF="",
                    true_1529_source_W3_status="NO_PRIMARY_W3_IN_25_W_STUDIES",
                    architect_tiler_1to1_approval="FALSE",owner_approved="FALSE",
                    purchase_authorized="FALSE"))
assert len(cuts)==24
csvout("R35_24_PARENT_PRIMARY_W1W2_24IN_TILE_FOCAL_SYMMETRY_3IN_TESTS_NO_INVENTED_W3.csv",cuts)

# Revised actual floor color/comparable decision options distinct by wet
# construction and operations, no fake owner selection and NO new tile pan.
tiers=[]
for room in FOCUS:
    if room in parents:
        wc=source[room]["wc"]
        choices=[
          ("GOOD","SOURCE_CONTINUITY_WITH_DRAIN_OPTION_HOLD",
            "Preserve old Bone/Clay Soft LEVEL and WC AntiSlip selected, no separate WC order; original selected BNX linear/rough. Source PAN finish application/raw wet DCOF unresolved; show solid grate owner-neutral. NO installation release.",
            "Lowest theoretical redesign quantity but literal old mixed floor quote and raw PAN lab remain unknown; retain open GC scope ledger."),
          ("BETTER","SOLID_BNX_GRATE_DRAIN_SECTION_CALIBRATED",
            "Use factory selected reversible drain SOLID Black Onyx configuration, separate original BR73480, independently wet-authorized small-format LINEAR PAN tile (unselected), verified 3-wall membrane/wall/floor transition.",
            "Avoids RL21 decorative insert chip min conflict, but requires true 1529 rough/threshold and full waterproof field assembly; no cost established."),
          ("BEST","RL21_COLOR_COHESION_WITH_TWO_DIFFERENT_SKUS",
            "Owner-only conditional RL21 Dynamic Beige 12x24 level/1.5 hex mosaic LINEAR pan, exact 7-18mm grate tile-in OR owner-granted solid BNX configuration, no assumed same-lot/case, WC AntiSlip separately reconciled.",
            "Could improve palette continuity and modularity; Mexico mosaic vs U.S. level different factories/cases, RL21 grout 1/8 vs3/16 and 1/4 vs5/16 conflicting, numeric DCOF and budget unknown."),
        ]
    else:
        p="PH-PRIMARY" if room=="PH-WC" else "TX-PRIMARY"
        choices=[
          ("GOOD","SOURCE_ANTISLIP_FLOOR_INHERITED_ONCE",
            "Keep original Bone/Clay AntiSlip WC selected as a physical seeded finish, no new WC material row; don't transfer parent Soft wet tests.",
            "No second order; real original mixed parent quote cannot prove exact WC SKU/finish purchased."),
          ("BETTER","INDIVIDUAL_ANTISLIP_LEVEL_TEST_AND_THRESHOLD_SHOP",
            "Retain WC AntiSlip, obtain its own exact raw LEVEL wet test and dry/wet threshold, full toilet door/UniFit geometry and calibrated parent Soft-versus-AntiSlip finish transition.",
            "Small physical movement/trim/door mockup may avoid rework, real case yield and labor unknown."),
          ("BEST","FULL_PARENT_WC_ONE_CONTROLLED_SHOP_RELEASE",
            "Owner-only coordinated verified WC AntiSlip vs parent selected LEVEL finish with matched actual 1529 door/tile alignment and same manufacturer where genuinely same factory SKU/lot; maintain no new WC order until reconciliation.",
            "Possible aesthetic alignment improvement and labor normalization; no assumed same SKU, no factory test transfer or unsupported buyer premium."),
        ]
    for tier,name,detail,cost in choices:
        tiers.append(dict(room=room,tier=tier,design_name=name,
            owner_facing_construction_aesthetic=detail,material_and_installed_scope_exposure=cost,
            original_SELECTED_48in_BNX_rough_preserved=truth(room in parents),
            original_wet_ANTISLIP_WC_and_no_standalone_buy=truth(room not in parents),
            hypothetical_PAN_quote_branch_unresolved="BOTH_A_INCLUDED_AND_B_EXCLUDED_REMAIN_OPEN",
            independent_raw_numeric_LEVEL_and_LINEARPAN_if_applicable="MISSING",
            separate_individual_maker_WALL_NICHE_wet_application="REQUIRED_IF_ACTUAL_SELECTED_WET_SURFACE",
            current_hypothetical_alternative_owner_selection="FALSE",score_weighted_BOARD="NULL",
            actual_installed_vendor_quote_USD="",owner_approved="FALSE",
            architect_plumber_waterproof_tile_signed="FALSE",purchase_authorized="FALSE"))
assert len(tiers)==12
csvout("R35_12_FOUR_ROOM_PARENT_WC_GOOD_BETTER_BEST_FUNCTION_COST_AND_WET_GATE_OPTIONS.csv",tiers)

# Real physically distinct quote zones (bath LEVEL, WC AntiSlip LEVEL,
# sloped PAN), with fictional case coverage ONLY; unlike finishes forbidden.
cases=[]
for room,d in source.items():
    for branch in ("A_PAN_INCLUDED_IN_ORIGINAL_BATH_FLOOR","B_PAN_EXCLUDED_FROM_ORIGINAL_BATH_FLOOR"):
        pan=d["panwidth"]*d["pandepth"]
        bathlevel=d["area"]-pan if branch.startswith("A") else d["area"]
        for zone,net,material in (("BATH_LEVEL_SOFT",bathlevel,d["LEVEL"]),
                                  ("WC_LEVEL_ANTISLIP",d["wcarea"],d["WC"]),
                                  ("LINEAR_SLOPED_PAN_UNSELECTED_TILE",pan,d["PAN"])):
            for fictional in (8,12,16):
                gross=net*1.15
                separate=2*math.ceil(gross/fictional)
                pooled=math.ceil(2*gross/fictional)
                cases.append(dict(parent_room=room,quote_branch=branch,surface=zone,
                    original_FINISH_distinct_from_other_zones=material,
                    source_net_per_physical_copy_SF_unverified=F(net),
                    hypothetical_1point15_new_GROSS_SF_per_copy=F(gross),
                    fictional_case_usable_SF_not_factory=F(fictional),
                    theoretical_TWO_separate_copy_ceil_cases=separate,
                    theoretical_same_SKU_two_copy_pool_ceil_cases=pooled,
                    theoretical_only_case_ceiling_difference=separate-pooled,
                    actual_factory_usable_case_SF="",
                    actual_SKU_size_finish_color_shade_caliber_same_lot="UNKNOWN",
                    source_combined_original_quote_NOT_purchasable_as_three_distinct_SKUs="TRUE",
                    actual_approved_original_quote_A_or_B="FALSE",
                    actual_original_15pct_waste_reapplied_to_prior_gross="FALSE",
                    actual_realized_savings="FALSE",purchase_authorized="FALSE"))
assert len(cases)==36
csvout("R35_36_BATH_SOFT_WC_ANTISLIP_LINEAR_PAN_SEPARATE_SAME_SKU_FICTIONAL_CASE_ROUNDING.csv",cases)

# Linked product/BOM controls: two actual shower copies per parent, one rough
# per selected drain, optional wall-edge trim independent of rough.
rough=[]
for room in parents:
    for copy in geos[room]["revit_room_numbers"]:
        for item,program in (("BT0734816-BNX","OWNER_SELECTED_BNX_48IN_LINEAR_FINISHED_GRATE_OR_INSERT"),
                             ("BR73480","ONE_REQUIRED_ROUGH_FOR_SELECTED_DRAIN"),
                             ("BR73480_DUPLICATE_SOURCE_DESCRIPTION","MISLABELLED_WALL_EDGE_TRIM_IS_NOT_A_SECOND_ROUGH"),
                             ("BT0734870_FAMILY","OPTIONAL_WALL_EDGE_TRIM_SEPARATE_BNX_SKU_UNVERIFIED")):
            rough.append(dict(room=room,source_primary_physical_copy=copy,
                source_item_or_hard_check=item,authorized_item_identity=program,
                selected_or_extra=("SELECTED_ALREADY" if item in ("BT0734816-BNX","BR73480") else "NOT_SELECTED_OR_DUPLICATE"),
                exact_owner_selected_BNX_drain_remains="BT0734816-BNX",
                exact_required_rough_once_per_selected_drain="BR73480",
                current_original_schedule_BR73480_count_in_room="2",
                derived_true_rough_count_from_this_source="1_REQUIRED_PER_LINEAR_DRAIN",
                different_item_wall_edge_trim_current_BNX_factory_SKU="UNKNOWN_NOT_BR73480",
                owner_approved_optional_wall_edge_trim="FALSE",
                same_factory_component_actual_current_stock="UNKNOWN",
                actual_brizo_maker_shop_revision_and_membrane_WPS_fit="",
                manufacturer_approved_mounting_at_wall_or_offset="FALSE",
                current_quote_price_and_material_receipts="",
                supplier_signed="FALSE",GC_signed="FALSE",purchase_authorized="FALSE"))
assert len(rough)==16
csvout("R35_16_TWO_PRIMARY_PHYSICAL_BRIZO_FINISHED_ROUGH_DUPLICATE_WALLEDGE_BOM_IDENTITY.csv",rough)

# Conditional cost exposure is an audit/control ledger, not a material order,
# a change order, nor a duplicate historic credit.
installed=[]
for room in parents:
    d=source[room];pan=d["panwidth"]*d["pandepth"]
    rate=float(Decimal(HIST[(room,"floor")]["historic_usd_two_copies"])/(Decimal(str(d["gross"]))*2))
    for copy in geos[room]["revit_room_numbers"]:
        for branch in ("A_PAN_INCLUDED_IN_ORIGINAL_BATH_FLOOR","B_PAN_EXCLUDED_FROM_ORIGINAL_BATH_FLOOR"):
            for grate in ("SELECTED_BNX_SOLID_GRATE","SELECTED_BNX_TILE_IN_OPTION"):
                delta=0 if branch.startswith("A") else pan*1.15
                installed.append(dict(room=room,source_physical_copy=copy,
                    mutually_exclusive_quote_ownership=branch,
                    drain_grate_OWNER_NOT_YET_SET_OPTION=grate,
                    historical_floor_two_copy_USD=HIST[(room,"floor")]["historic_usd_two_copies"],
                    source_original_waste15pct_already_included="TRUE",
                    hypothetical_distinct_EXTRA_pan_GROSS_SF_branchB_only=F(delta),
                    historic_mixed_quoted_rate_material_only_NOT_pan_specific=F(rate),
                    theoretical_inclusion_exclusion_mixed_rate_reference_USD_NOT_PAYABLE=M(rate*delta),
                    actual_exact_pan_tile_SKU_and_original_numeric_wet_lab="",
                    actual_current_exact_sku_pan_rate_level_rate_wc_rate="",
                    original_2026_quote_INCLUDED_or_EXCLUDED_pan_document="",
                    original_approved_invoice_order_shipped_material_remaining="",
                    actual_site_verified_1529_level_wc_and_pan_signed_NET="",
                    current_factory_case_shade_caliber_lot_rounding="",
                    actual_separate_pan_waterproof_slope_screed_membrane_labor_bid_USD="",
                    actual_valve_drain_BR73480_and_optional_wall_edge_trim_scope="",
                    true_deleted_original_purchased_parts_credit_USD="",
                    actual_wet_shower_tile_level_wc_threshold_and_movement_joint_scope="",
                    installed_GC_signed_material_labor_total_USD="",
                    payable_change_order_established="FALSE",owner_approved="FALSE",
                    purchase_authorized="FALSE"))
assert len(installed)==16
csvout("R35_16_SELECTED_DRAIN_BRANCH_INSTALLED_BID_CREDIT_MIXED_RATE_EXPOSURE_NOT_PAYABLE.csv",installed)

# Exact original lab roles remain canonical, transformed to acceptance evidence.
labs=[]
for r in raw13:
    room=r["room"];role=r["surface_role"]
    labs.append(dict(room=room,original_surface_role=role,
        original_floor_quote_source_id=r["source_original_floor_row_id"],
        current_owner_selected_or_conditional_pan="PRIMARY_48IN_BNX_LINEAR" if room in parents else
          "WALKIN_4IN_BNX_POINT" if room=="PH-BATH4" else
          "ONLY_OWNER_CONDITIONAL_POINT_PAN" if room in ("PH-BATH3","TX-BATH3") else "N_A_TUB_OR_LEVEL",
        exact_original_maker_SKU_color_size_finish="",
        original_raw_measured_wet_DCOF_exact_numeric="",
        original_test_standard_method_batch_ID_date="",
        maker_wet_use_individual_APPLICATION_LEVEL_vs_LINEAR_PAN_vs_POINT="UNKNOWN",
        manufacturer_TARGET_or_bound_not_original_raw_test="TRUE",
        WC_ALIQUOT_raw_lab_may_NOT_transfer_SOFT_to_ANTISLIP="TRUE" if room in parents else "NOT_APPLICABLE",
        specific_substrate_slope_and_pan_drain_system="UNKNOWN",
        original_13_ROLE_not_13_NEW_tile_orders="TRUE",
        original_report_RECEIVED="FALSE",installer_signed="FALSE",
        owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(labs)==13
csvout("R35_13_ORIGINAL_WET_NUMERIC_LAB_APPLICATION_AND_PARENT_WC_SAME_SKU_SEPARATION.csv",labs)

# Parent two physical copies x three factory-certification construction
# witness layers. No additional Primary wet shower niches.
sections=[]
for room in parents:
    for copy in geos[room]["revit_room_numbers"]:
        for section in ("S1_ROUGH_AND_WPS_WALL_FLOOR_CHANNEL_DATUM",
                        "S2_GRATE_TILE_INSERT_FRAME_GRADIENT_THRESHOLD",
                        "S3_WALL_WC_FLOOR_FINISH_SERVICE_TOILET_ACCESS"):
            sections.append(dict(room=room,physical_copy=copy,section=section,
                certified_native_1529_document_ID_and_revision="",
                actual_wet_shower_corner_wall_W1_W2_width_height_and_position="",
                drain_exact_selected_trim="BT0734816-BNX",
                one_separate_required_rough="BR73480",
                selected_drained_CHANNEL_orientation_vs_wall="",
                actual_subfloor_Z_and_structural_recess_thickness="",
                actual_concrete_or_wood_or_LEWIS_substrate_by_factory_and_site="",
                manufacturer_mandated_SLOPE_direction_and_thickness="UNKNOWN_NEED_OFFICIAL_CERTIFIED_SYSTEM",
                membrane_BRIZO_WPS_bonding_and_clamp_detail_signed="FALSE",
                actual_LINEAR_channel_frame_TILEIN_vs_SOLID_assy_Z="",
                actual_TILED_pan_chip_thickness_grout_joint_mortar_frame_and_access="",
                actual_perimeter_high_Z_and_glass_door_threshold_Z="",
                actual_bath_LEVEL_soft_tile_finish_and_wc_antiSlip_step_Z="",
                real_TOILET_Nexus_Unifit_12_or14in_rough_and_washer_door="UNSELECTED_WC_LOCATION",
                original_PAN_vs_LEVEL_quote_inclusion_A_or_B="UNKNOWN",
                original_exact_raw_NUMERIC_level_wc_pan_lab="MISSING",
                existing_niches_in_Primary="NONE_NO_NEW",
                actual_wall_other_openings_and_escutcheon_seal="",
                actual_total_exposed_EDGE_and_movement_joint_LF="",
                physical_one_to_one_waterproof_drain_grade_floodtest_signed="FALSE",
                all_trades_release="FALSE",purchase_authorized="FALSE"))
assert len(sections)==12
csvout("R35_12_SELECTED_LINEAR_CHANNEL_ROUGH_MEMBRANE_FINISH_WC_SERVICE_1to1_SECTIONS.csv",sections)

# Every one of the 27 original historic material lines is used as a quoted
# SOURCE ID only; two excluded Primary niche references NEVER become orders.
normalize=[]
for x in old:
    room=x["room"];gross=Decimal(x["source_gross_sf_one_copy_waste_15pct_once"] or "0")
    money=Decimal(x["historic_usd_two_copies"] or "0")
    excluded=x["historic_niche_excluded_no_scope"]=="TRUE"
    normalize.append(dict(room=room,original_unique_source_material_ID=x["source_row_id"],
        historic_surface=x["source_surface"],
        historical_GROSS_SF_one_copy_includes15pct_once=str(gross),
        historical_GROSS_SF_both_physical_copies=str(gross*2),
        historic_material_only_USD_two_copies=str(money),
        historical_blended_material_only_rate_USD_per_GROSS_SF=F(float(money/(2*gross))) if gross else "N_A",
        excluded_unpriced_Primary_niche_NO_NEW_ORDER=truth(excluded),
        original_floor_WC_PAN_quote_branch_unresolved=truth(room in parents and x["source_surface"]=="floor"),
        original_R34_A_v_B_mutually_exclusive_reconciliation="REQUIRED_IF_PRIMARY_FLOOR" if room in parents and x["source_surface"]=="floor" else "NOT_R35_FOCUS",
        actual_supplier_maker_SKU_color_size_finish_lot="",
        exact_original_wet_WALL_NICHE_APPLICATION_permission="",
        exact_original_numeric_wet_LEVEL_and_independent_PAN_report_ID="",
        certified_1529_survey_signed_NET_level_wc_pan_or_wall="",
        original_quote_PAN_EXCLUSION_or_INCLUSION_evidence="",
        original_paid_order_shipped_received_inventory_document="",
        current_factory_usable_SF_case="",
        after_signed_net_actual_orderable_case_count="",
        same_SKU_COLOR_SIZE_FINISH_LOT_pool_authorized="FALSE",
        dated_Chicago_supplier_price_stock_ETA_freight_tax="",
        public_retail_or_manufacturer_MSRP_not_current_project_quote="",
        actual_subtrade_labor_waterproof_rough_trim_grout_co_USD="",
        original15percent_gross_not_applied_twice="TRUE",
        payable_credit_or_CO_approved="FALSE",
        owner_approved="FALSE",supplier_signed="FALSE",purchase_authorized="FALSE"))
assert len(normalize)==27
assert sum(Decimal(x["historic_material_only_USD_two_copies"]) for x in normalize)==Decimal("23572.44")
csvout("R35_27_HISTORICAL_QUOTE_TO_SOURCE_PAN_LEVEL_WC_MAKER_LOT_INSTALLED_BID.csv",normalize)

# Every original physical instance receives a new concrete conditional
# contract release role, not a second fixture or a second source geometry.
other={
 "PH-BATH2":"Duravit 700332 selected TUB Hansgrohe Matte White; 15758701 thermostat vs 72411701 PB-only diverter spout 3-endpoint source HOLD; LEVEL lab PAN N_A",
 "TX-BATH2":"Duravit 700332 selected TUB Hansgrohe Chrome 04925000 and 04790000; mixer/rough/tub-fill absent source schedule, NOT physically verified absent; LEVEL lab PAN N_A; basin unselected",
 "TX-BATH4":"Duravit 700332 selected TUB Hansgrohe Matte White PB-only 72411701 vs 15758701 thermostat conflict; no shower PAN",
 "PH-BATH3":"Owner TUB/WALKIN UNSELECTED; Delta Chrome square POINT drain only conditional WALKIN; PH sink unselected; Tones Opal wall wet not authorized",
 "TX-BATH3":"Owner TUB/WALKIN UNSELECTED; Brizo Black Onyx POINT only conditional WALKIN; Emerald live item permission renew",
 "PH-BATH4":"Owner WALKIN Brizo Black Onyx 4in POINT separate four-plane PAN and bath LEVEL; Cortar Ribbed wet wall/Clara Caviar niche HOLD; 35/27SF and 214.4 disputed",
 "PH-POWDER":"Wood floor dry feature, selected Brizo Frank Lloyd Wright WALL T65722LF-GL with R65700 rough; no wet floor PAN",
 "TX-POWDER":"Wood floor dry feature, AXOR One 48140991 WALL trim vs Hansgrohe Metropol 32526141 WALL trim, not trim+rough; owner program unresolved",
 "TX-POWDER2":"Wood floor and dry Indigo wall, Hansgrohe Tecturis E 73072341 DECK; basin unselected, no wet tile PAN",
}
assert set(other)==ids-set(FOCUS)
physical=[]
for r in rooms26:
    room=r["room"];num=r["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"]
    if room in parents:scope=(
       "Brizo 48in Black Onyx LINEAR + BR73480 once, solid vs tilein 7-18mm, raw LEVEL vs PAN labs, WC inherited Soft vs AntiSlip, R34 mutually exclusive A/B quote"
    )
    elif room in ("PH-WC","TX-WC"):scope=(
       "Source WC physical placement/door/toilet UniFit and exact AntiSlip finish field; parent Primary floor ROW included ONCE, do not place separate PO or assume Soft lab"
    )
    else:scope=other[room]
    physical.append(dict(room=room,physical_copy_number=r["physical_copy_index"],
        provisional_source_room_number=num,
        certified_actual_1529_room_id="",
        original_owner_program_and_R35_specific_shop_top_fix=scope,
        original_2unit_selected_rough_or_floor_source_row="BR73480_SELECTED_ONCE_PER_PRIMARY_DRAIN" if room in parents else
           "INHERITED_PARENT_QUOTE_FLOOR_NO_SEPARATE_WC_ORDER" if room.endswith("WC") else "SEE_ORIGINAL_ROOM_PLUMBING_JSON",
        physical_signed_shower_PAN_polygon_vs_LEVEL_wc_spatial_boundary="",
        original_QUOTE_A_v_B_vendor_scope_letter="",
        source_actual_exposed_edge_movement_threshold_LF="",
        maker_individual_WALL_NICHE_wet_letter_or_not_applicable="",
        original_numeric_wet_LEVEL_and_independent_PAN_lab="",
        maker_exact_SLOPED_pan_application_and_membrane_drain="",
        true_site_case_lot_caliber_factory_item_ticket="",
        actual_installed_GC_scope_rough_backer_waterproof_grout_trim_bid="",
        owner_signoff="FALSE",architect_signoff="FALSE",plumber_signoff="FALSE",
        waterproof_signoff="FALSE",tile_installer_signoff="FALSE",
        supplier_signoff="FALSE",GC_signoff="FALSE",purchaser_signoff="FALSE",
        purchase_authorized="FALSE"))
assert len(physical)==26
csvout("R35_26_ORIGINAL_PHYSICAL_INSTANCE_PRIMARY_WC_AND_ALL_13_PROGRAM_RELEASE_DEPENDENCIES.csv",physical)

# Original R31 source 50 two-copy wall rows remain untouched; explicit Primary
# no-new-W3/no-niche and dated true wall positions. WCs had no W1/W2/W3 source.
walls=[]
for r in walls50:
    room=r["room"];wallid=r["wall_reference"]
    if room in parents:
        shop="LINEAR_WET_WALL_W1_W2_CUT_3IN_MIN_AND_GLASS_VALVE_SEAL; NO_W3_SOURCE_NO_PRIMARY_NICHE"
        assert wallid in ("W1","W2")
    elif room=="PH-BATH4":shop="Owner WALKIN POINT 4plane PAN and LEVEL; Ribbed wet wall/Caviar niche maker individual permission HOLD"
    elif room in ("PH-BATH2","TX-BATH2","TX-BATH4"):shop="Actual Duravit tub 3wall flange and signed mixer/spout/rough selected; no tiled PAN"
    elif room in ("PH-BATH3","TX-BATH3"):shop="Owner TUB/WALKIN unselected, POINT only conditional"
    else:shop="Dry vanity wall/powder selected faucet positioning, no fabricated wet PAN"
    walls.append(dict(room=room,source_physical_copy=r["physical_copy"],
        source_wall_reference=wallid,
        source_prior_width_in_UNVERIFIED=r["prior_source_wall_width_in_UNVERIFIED"],
        source_prior_height_in_UNVERIFIED=r["prior_source_tiled_height_in_UNVERIFIED"],
        exact_R35_field_shop_top_fix=shop,
        native_actual_1529_project_and_element_ID="",
        actual_measured_width_height_and_surface_origin="",
        actual_door_window_other_openings_SF="",
        actual_ONE_existing_niche_aperture_negative_FIELD_SF="",
        actual_existing_niche_BACK_TWO_SIDES_TOP_SILL_SF="",
        no_extra_Primary_NICHE_invented="TRUE" if room in parents else "NOT_APPLICABLE",
        actual_escutcheon_wall_penetration_glass_cutout="",
        calibrated_joint_and_end_focal_under3in_gate="",
        actual_profile_exposed_edge_LF_and_movement_LF="",
        signed_1529_NET_WET_wall_tile_SF="",
        actual_maker_individual_wet_WALL_NICHE_permission="",
        owner_approved="FALSE",waterproof_and_tile_signed="FALSE",
        purchase_authorized="FALSE"))
assert len(walls)==50
csvout("R35_50_PRIOR_TWO_COPY_WALLS_TRUE1529_W1W2_PRIMARY_NO_W3_SHOP_AND_OPENING_GATES.csv",walls)

# Full 13 room release with exact original champion/status and selected program.
lab_for={}
for row in labs:lab_for.setdefault(row["room"],[]).append(row["original_surface_role"])
release=[]
trades=[]
TRADE=("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")
for room in sorted(ids):
    original=byroom[room]
    room_cost=sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old if x["room"]==room)
    if room in parents:
        program="SELECTED Brizo 48in BNX LINEAR BT0734816-BNX + BR73480 separate; PAN A/B quote unresolved, linked WC inherits, no niches"
        pan="LINEAR_RAW_ORIGINAL_NUMERIC_WET_LAB_REQUIRED_SEPARATE_FROM_LEVEL"
        lev="LEVEL_SOFT_PARENT_WC_ANTISLIP_DIFFERENT_FINISH_IND_CERTS"
    elif room.endswith("WC"):
        program="Cortar Bone/Clay AntiSlip LEVEL inherits parent Primary original mixed floor quote ONCE; no separate WC PO"
        pan="N_A_WC";lev="PARENT_AND_ANTISLIP_WC_LEVEL_RAW_PER_EXACT_FINISH"
    else:
        program=other[room]
        pan=("N_A_TUB_OR_WOOD_POWDER" if room in ("PH-BATH2","TX-BATH2","TX-BATH4","PH-POWDER","TX-POWDER","TX-POWDER2") else
            "POINT_PAN_RAW_NUMERIC_REQUIRED_IF_ACTUAL_OR_OWNER_CONDITIONAL")
        lev="N_A_WOOD_POWDER" if "POWDER" in room else "EXACT_ORIGINAL_LEVEL_WET_NUMERIC_TEST_UNKNOWN"
    release.append(dict(room=room,original_board_round="017",
        original_status=original["status"],
        original_champion=original.get("champion_id") or "null",
        original_weighted_champion_score=str(original["champion_score"]) if original["champion_score"] is not None else "null",
        two_source_physical_copies=2,
        original_HISTORICAL_two_copy_material_only_USD=str(room_cost),
        actual_owner_program_and_R35_specific_top_fix=program,
        exact_raw_wet_LEVEL_application=lev,distinct_SLOPED_PAN_raw_wet_application_or_N_A=pan,
        individual_WALL_wet_maker_letter="REQUIRED_IF_WET_WALL_PRESENT",
        separate_individual_NICHE_wet_maker_letter="REQUIRED_IF_ACTUAL_WET_NICHE_PRESENT",
        original_13_global_numeric_lab_roles= "|".join(lab_for.get(room,[])) or "N_A_OR_PARENT_INHERITED",
        source_1529_field_geometry_and_original_quote_scope_verification="",
        exact_material_sku_color_finish_factory_usable_case_lot="",
        installed_supplier_bid_labor_rough_membrane_edge_grout_tax_ETA="",
        owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
        waterproofing_approved="FALSE",tile_installer_approved="FALSE",
        supplier_approved="FALSE",GC_bid_approved="FALSE",purchaser_approved="FALSE",
        material_reserved="FALSE",purchase_authorized="FALSE",
        original_four_critic_panel_score_clearance="NULL",
        independent_nonpro_reviewer_accepted="FALSE"))
    for i,t in enumerate(TRADE,1):
        descriptions={
          "OWNER":"Unchanged fixture and material program, Primary A/B PAN contract branch and WC finish approval, budget cap and mockup",
          "ARCHITECT":"Certified true 1529 W1/W2 and no Primary W3 invented; actual shower polygon/door/WC area and floor/linear threshold Z; owner-signed A/B takeoff",
          "PLUMBER":"Factory selected exact BR73480 once per 48in BNX linear, channel/optional wall trim accurate SKU; full water service access and all other room fixture roughs",
          "WATERPROOFING":"Brizo WPS integrated rough, approved membrane/flange, shower-to-LEVEL threshold, floodproof and compatible backer; tub flange in tub rooms",
          "TILE_INSTALLER":"Original exact raw numeric wet LEVEL and independent PAN tests, different Soft/AntiSlip and RL21 1/4 vs5/16/1/8 vs3/16, 3in focal cuts, calibrated 1to1",
          "SUPPLIER":"27 original source material line proof, verified manufacturer exact SKU/finish/caliber/lot/usable SF case, inventory and dated Chicago price ETA freight",
          "GC_ESTIMATOR":"Historic $23572.44 15pct once, mutually exclusive A/B contract pan interpretation, real signed LEVEL/ WC/ PAN NET and installed labor/rough/membrane/trim/credit CO",
          "PURCHASER":"Only after prior owner+seven trade signatures, true exact lab, same factory case/lot, independently cleared original four-seat governance if applicable"
        }
        trades.append(dict(room=room,sequence=i,trade=t,
            independent_trade_acceptance_obligation=descriptions[t],
            actual_source_1529_document_and_fact_certification="",
            real_chemical_maker_wet_paper_or_numeric_lab="",
            exact_fact_checked_pricing_factory_lot_and_purchasable_case="",
            original_board_required_MARKET_0point30_DESIGN_0point25_BUILD_0point25_COST_0point20="PRESERVED_NO_NEW_SCORE",
            trade_real_signature="",owner_approved="FALSE",
            current_GC_contract_release="FALSE",purchase_authorized="FALSE"))
assert len(release)==13 and len(trades)==104
csvout("R35_13_ROOM_BATH_PROGRAM_OWNER_WET_NUMERIC_WALL_NICHE_FINAL_RELEASE_MATRIX.csv",release)
csvout("R35_104_EIGHT_TRADE_13ROOM_SEQUENTIAL_PAN_QUOTE_DRAIN_R35_RFI_HOLD_POINTS.csv",trades)

# Requested physical sample/render briefs only; don't emit images,
# fabricated lenses, 1529 room geometry, or actual owner choices.
briefs=[]
for x in unitpairs:
    for view in ("R35_TRUE1529_TOPDOWN_PRIMARY_LEVEL_WC_PAN_POLYGON_AND_QUOTE_BRANCH",
                 "R35_1TO1_DRAIN_GRATE_TILEIN_WC_THRESHOLD_SECTION_W1_W2"):
        briefs.append(dict(parent_room=x["primary_room"],primary_source_copy=x["source_primary_copy"],
            linked_WC_room=x["linked_WC_room"],wc_source_copy=x["source_wc_copy"],
            physical_zone=x["physical_zone"],requested_future_view=view,
            preserve_selected_exact_BNX_48in_and_rough="TRUE",
            preserve_wc_original_antislip_no_independent_order="TRUE",
            do_not_render_primary_niches="TRUE",
            do_not_show_W3_as_original_Primary_wall="TRUE",
            actual_owner_tub_and_powder_other_13_room_constraints="PRESERVE_ALL",
            original_quoted_A_vs_B_pan_boundary="UNRESOLVED_DO_NOT_DRAW_AS_FACT",
            real_site_measured_curb_pan_wc_floor_heights_and_drain_axis="UNKNOWN",
            required_full_scale_sample="actual RL21 nominal chip/setting/frame, Soft/AntiSlip level, WPS liner, 1/8 vs 3/16 grout, threshold and cleaning service",
            physical_mockup_built="FALSE",actual_camera_or_image_generated="FALSE",
            owner_signed="FALSE",architect_WP_tile_signed="FALSE",purchase_authorized="FALSE"))
assert len(briefs)==16
csvout("R35_16_FOUR_ROOM_EIGHT_PHYSICAL_ZONE_SOURCE_FAITHFUL_CAMERA_AND_1to1_BRIEFS.csv",briefs)

# A specific architectural hold: source Primary W1/W2 studies exist, W3 does
# NOT. This prevents accidental geometry transfer from unrelated Bath4 W3.
missing_w3=[]
for room in parents:
    for copy in geos[room]["revit_room_numbers"]:
        missing_w3.append(dict(room=room,physical_primary_source_copy=copy,
          W1_W2_existing_source_verified_as_provisional="TRUE",
          W3_original_R17_source_elevation_exists="FALSE",
          room_original_tiled_wall_elements_count=2,
          proposed_actual_1529_third_return_or_glass_transition="FIELD_DETERMINE_NOT_INVENT",
          W3_wall_width_in="",W3_wall_tiled_height_in="",
          actual_1529_verified_project_element_ID="",wall_surface_penetrations_wet_return="",
          zero_additional_Primary_niches="TRUE",actual_profile_or_movement_LF="",
          need_a_third_wall_construction_or_elevation_approval="FALSE",
          architect_signed="FALSE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(missing_w3)==4
csvout("R35_4_PRIMARY_PHYSICAL_NO_SOURCE_W3_NEVER_INVENT_ELEVATION_GATES.csv",missing_w3)

mdout("START_HERE_R35_FOUR_ROOM_PRIMARY_WC_13ROOM_IMPLEMENTATION.md",f"""
# R35 complete 1529 Primary + inherited WC integrated construction and procurement engineering

**This is additive, not an owner's approved material revision, signed 1529 field survey, installation release or a new blind board. Entire 13-room objective OPEN; all releases FALSE.** Formal board stays 017. Four-room focus **PH-PRIMARY, PH-WC, TX-PRIMARY, TX-WC**, covering **eight physical room-zone instances** as four parent-to-WC unit pairs (PH 304A/313A, 304B/313B, TX 202A/203A unplaced, TX 202B/203B), labels only drawing-provisional.

## The consequential new implementation — source and signed lineage

R34 source math nearly reconstructs quoted blended parent floor gross at original **15% waste once**, not whether a selected 48in LINEAR shower PAN is inside it. R35 now develops **eight fully balanced A/B UNIT-copy scenarios**: A quote includes shower PAN, B excludes PAN. Each has independent bath LEVEL, inherited WC LEVEL, separately identified sloped LINEAR PAN and mutually exclusive total NET/GROSS, plus historical-rate reference delta and exact required original quote/invoice/lot/GC evidence. This is a greater contractor and procurement scope than recreating R34's 18 conditional rows. R35 independently splits **three distinct physical tile finish groups** (Soft LEVEL, AntiSlip WC, independent PAN) instead of using a single blended quote as purchase SKU. No standalone WC material order; no fabricated pan shortage, payable CO or case yield.

Factory-specific full selected PH/TX Brizo **BT0734816-BNX** Black Onyx reversible LINEAR + **BR73480** separately required rough retained. Brizo official {URLS["BRIZO_TRIM"]} confirms solid BNX or tile-in; 7–18mm frame nominal and must order rough separately. Exact BR73480 {URLS["BRIZO_ROUGH"]} has WPS secondary-drainage rough, built-in sloping channel, adjusting risers, drain hair catcher; manufacturer compatibility with actual site backer/membrane and tile/grade/rough must be signed, not inferred. Actual source room plumbing records twice mention BR73480 (one labelled wall-edge trim), **but this is NOT authorization for two BR73480 rough orders**. Maker optional wall-edge family is a different trim product ({URLS["BRIZO_WALLEDGE"]} Chrome sibling only), actual BNX exact wall-edge SKU/finish and owner need unknown.

Original **Daltile Prime RL21 Dynamic Beige** is conditional manufacturer alternative, NOT selected pan nor new tile change. Its maker {URLS["DALTILE_RL21"]} lists 1.5in hex matte 5/16in nominal thickness, 12x24 matte 3/8in, two distinct factories/formats; earlier signed research references older Prime mosaic brochure nominal 1/4in and a Target 0.60 vs 2026 Target 0.42. One maker snapshot grout 1/8 vs another 3/16. Neither brochures, Targets nor current item-family listing establishes the project's **exact original measured numeric wet DCOF** for independently selected LEVEL, AntiSlip WC and LINEAR PAN. The 5/16in nominal chip is 7.9375mm (+0.9375 nominal mm vs frame min7); older 1/4in chip6.35mm (-0.65mm). This is not an installed thickness pass/fail; actual carrier, mortar, waterproofing, frame seat, dry/level datum and drain connection remain UNKNOWN. **Solid grate** is a distinct genuinely available selected fixture configuration avoiding only decorative tile-in chip/frame fit, not any other floor/pan gates.

Source-provisional W1/W2 in original R17: PH Primary70.248in/55.752in and TX Primary62.25in/57.25in, height111in. **There is no original Primary W3 among the 25**; do not invent one from another room or from 1527. New 24 source W1/W2 focal cut and 4 missing W3 gate studies, 32 slope/threshold alternatives, 24 solid/tile-in RL21 thickness/grout variants, 12 three-section construction templates and 16 one-to-one mockup/camera briefs provide contractor shop dependencies, not approved construction or generated images.

Original source 13 rooms x two copies, **27** historical material rows including two excluded no-order Primary niches, **25** original W elevations and **65** original trade actions preserved. **$23,572.44 four-unit material only** with gross waste15% ONCE, already includes Sandstone 51.64SF/$358.92, Cortar Grey165.40SF/$1116.46 and Caviar34.52SF/$1163.32. Old pan blended cost **not** factory-specific. Current Chicago case/lot, price, freight, ETA, actual net, installed GC bid and owner cap all UNKNOWN. All 26 original physical rooms, 50 wall targets, 13 lab application roles, 27 originals, 13 room release and 104 trade gates have R35 actionable cross-links and FALSE signoffs without overwriting old work.

Market: PH ~$2.8M, TX ~$2.7M, Old Town priority ~$2.4M–$3.2M, original **14 listing entries / nine actual buildings**, OT01–OT04 at 405 W Armitage count ONE precedent; adjacent Lincoln Park and Gold Coast are secondary. No asserted owner premium, competitor hidden tile identity, invented sample, reservation or price saving.

Read the companion accounting, factory section, three-tier design and 13-room GC books plus signed CSVs. Signed local read-only verification is **not independent non-Pro Reviewer acceptance or GLOBAL DONE**. Original DESIGN worker9 R014 reports missing, Reviewer15 finished/nonrevivable; original four-seat weighted scoring NULL, formal R017 unchanged.
""")

mdout("R35_CONTRACT_A_V_B_PAN_QUOTE_MATERIAL_ALLOCATION_AND_GC_PAYMENT_BOOK.md",f"""
# Contract-grade two-branch quantity balance and authorization control

## Source arithmetic, owner-source versus factory versus hypothesis

PH-PRIMARY original drawing bath 103 SF plus linked PH-WC 15 SF source, prior shower rectangle 5.854x4.646ft = **27.197684 SF**, historical mixed floor **135.6 GROSS SF per copy** already includes original 15%. TX-PRIMARY bath87+TX-WC14, rectangle5.1875x4.7708ft = **24.748525 SF**, historical **116.1 GROSS SF per copy**. These are unverified old handoff dimensions, NOT native certified 1529 polygons; original 2026 source quote floor row is not an exact orderable current pan tile SKU. Difference in reconstructed (bath+WC)*1.15 vs old original quote is PH +0.1000 SF and TX+0.0500 SF/copy and may simply reflect historic rounding. **Do not infer PAN inclusion** or vendor fault from that numerical match.

## Branch A — PAN included in original quoted bath floor

For each physical copy, LEVEL bath = bath drawing source - shower rectangle, inherited WC LEVEL = original WC, independent PAN net = shower rectangle; combined = bath + WC. PH LEVEL bath **75.802316 SF** + WC15 = **90.802316 LEVEL**, PAN27.197684. TX LEVEL bath **62.251475 SF** + WC14 = **76.251475 LEVEL**, PAN24.748525. Nominal level/PAN order groups are DISTINCT even though original quote is a blended gross rate; every actual selected exact SKU/finish must be classified. If old line already covered PAN, supplier must prove original pan product and ordered receipt/credit, not charge a second pan as new material on top of old parent gross. Original 15% gross already applied once.

## Branch B — PAN excluded from original quoted bath floor

For each physical copy original LEVEL bath plus inherited WC stays PH **118.0000 SF**, TX **101.0000 SF** NET, AND PAN is independently PH27.197684/TX24.748525 NET. The additional illustrative PAN with 15% *newly justified future* gross would be PH **31.277337 SF** and TX **28.460804 SF per copy**, or for two physical copies of each PH **62.554674 gross SF** / TX **56.921608 gross SF**, if a distinct new PAN order is actually proven. Do not add these to the historical 135.6/116.1 gross absent original dated quotation/exclusion document and certified site polygons. New PAN material may have a completely DIFFERENT maker, size, raw wet numeric test, case yield, installing/waterproof labor and waste than historic blended Soft/AntiSlip floor.

## Exact contract-document decision tree

HOLD: original quote line 2715002737917828 PH and 784184264687492 TX includes mixed material without verified LEVEL/PAN boundaries. Obtain contemporaneous original dated vendor quote's line semantics, original finish schedule floor legend, model/field PAN boundaries, material order confirmation, shipped/delivered and paid records. Confirm if original source quote listed shower pan tile separately in another source row (not currently evidenced), and original exclusion/credit basis. Then owner/architect/plumber/installer/GC sign one TRUE branch, mark the other FALSE; do not alter frozen old quote.

If documented A and actual PAN included, reconcile delivered actual suitable wet-test pan tile and current installed membrane/rough before ordering any replacement. If documented B, actual new independent PAN qty is signed physical NET plus independently owner-approved NEW cutting/waste once; then obtain separate dated supplier SKU/usable carton, current landed price, lot, approved installation and actual GC labor change order, less genuine original paid/source credits. If original scope remains ambiguous, both branches remain **UNRESOLVED** with order qty NULL.

Historical mixed material-only rates: PH **$2120.78/(2 x135.6 gross SF) = $7.81999/SF**, TX **$1811.16/(2 x116.1 gross SF) = $7.79914/SF**. Applying them to hypothetical extra PAN gross B yields only a *reference comparison*, NOT PAN-specific supplier price, factory material SKU, payable shortage, actual installed CO or realized savings. Distinguish true quoted/ordered/received/paid, remaining inventory, current verified factory lot case, actual measured pan net, 1:1 workmanship labor and owner change-order signing. Do not add original 15% a second time or double-buy the PH-WC/TX-WC floors.

R35 has 8 independently balanced physical-copy A/B formulas, 36 future three-SKU and fictional-case ceiling sensitivity controls, 16 selected grate/branch GC labor-credit scope records and 8 historic charge/no-double count holds; all RELEASE FALSE. WC AntiSlip and Primary Soft DIFFERENT finishes; they cannot be treated as one purchasable case or one raw measured wet test even if original mixed gross is shared. Correct current factory item/case and actual PH/TX WC area and tile calibration needed.
""")

mdout("R35_BRIZO_RL21_FACTORY_WATERPROOF_DRAIN_1TO1_SHOP_AND_W1W2_SECTIONS.md",f"""
# Brizo Black Onyx 48-inch LINEAR wet-room construction assembly and acceptance details

**Selected and immutable for both Primaries:** Brizo BT0734816-BNX reversible 48-inch LINEAR trim, separate required **BR73480** rough. Owner selected no extra Primary shower niche. Original source plumbing arrays label BR73480 twice, once as rough and once as wall-edge trim; the factory wall-edge trim is an independently numbered optional family, not another BR73480. The duplicate code must trigger a source BOM RFI, not two purchase lines or a fabricated Black Onyx edge-profile SKU.

## Manufacturer and finish variant control

Factory {URLS["BRIZO_TRIM"]} lists solid Black Onyx or tile-in grate and nominal **7–18mm** chip-frame window; factory {URLS["BRIZO_ROUGH"]} identifies separately purchased rough, risers, drainage and cleanable channel. These facts do NOT prove a proposed waterproof membrane, slope, threshold or tile manufacturer's carrier/glue/grout compatibility.

Conditional Daltile Prime RL21 Dynamic Beige 1.5-inch hex mosaic {URLS["DALTILE_RL21"]} is an **unselected candidate**. An older maker brochure {URLS["DALTILE_BROCHURE"]} said 1/4 inch, **6.35 mm chip** (below 7-mm nominal insert min by 0.65mm). Newer individual maker page says 5/16 inch **7.9375 mm** (above 7-mm min by ~0.94mm). This is VERSIONED manufacturer source inconsistency, not a calibrated cross section. Both numbers exclude uncertain sheet carrier and compressed bedding; **no arbitrary mortar shim to make a lower nominal chip pass**. The same color RL21 12x24 LEVEL material nominal3/8 and different manufacturing origin is **not** the same item/SKU/lot as the hex PAN. Archived RL21 joint snapshots 1/8 vs3/16 and old maker target >=0.60 versus later >=0.42 are unresolved; none provides actual original SKU-specific numeric measured wet DCOF. No qualified pan substitution or new owner selection.

### S-1 Structure/drain membrane rough datum

Site survey must certify true **1529 native model/address** (the accessible current Revit document is 1527 and cannot certify 1529), structural floor/subfloor and actual available recess at each 304A/B and 202A/B source copy. Measure complete shower pan polygon, selected 48-inch rough actual outlet and body height, channel distance from wall, adjacent bath/door/wc floor Z datum and planned curb/curbless transition. Independent factory/installer system signoff must show exactly how selected Brizo BR73480 water protection system bonds or clamps the specified manufacturer-approved substrate membrane including corners, backer and wall-flashing—no third-party flange compatibility by assumption. Provide required slope and high-point/perimeter elevations from verified design jurisdiction and maker technical manual, not from hypothetical 1/8 or1/4 inch per foot examples.

### S-2 Reversible frame to selected floor tile/threshold

Solid grate GOOD/BETTER: preserve selected reversible factory BNX face and access/removal; it avoids decorative tile insert thickness limit only, not shower-pan wet lab, perimeter waterproofing, height or user selection. Tile-in BEST: physical mockup with exact pan tile SKU, maker-approved nominal chip, actual sheet carrier, mortar after compression, Brizo insert bed/gasket, riser, finished surround height; physically test removability/cleanability, edge seals, grate face flushness, compatible grout and drainage. Stage actual verified LEVEL tile finish plane and independent PAN mosaic finish plane at interface; draw movement/transition joint and edge or profile line separately from material SF, not as automatically ordered trim.

### S-3 Primary wet W1/W2, glass, service and WC threshold

R17 source only PH Primary W1 70.248in/W2 55.752in, TX Primary W1 62.25in/W2 57.25in, tiled height 111in. **No original Primary W3 study**, no additional Primary niches. R35 has 24 independent nominal 24in tile long-axis central-full/joint cut cases with >=3in focal test, but calibrated tile geometry, glass stops, trim, trim edge LF, actual escutcheon and openings are unknown; do not claim 1529 wall orientation, missing W3 or new niches. All actual seam/movement locations, wall/window/door aperture deductions and source original field rate must be witnessed.

WCs **PH-WC** original 15 SF and **TX-WC** 14 SF inherited ONCE in parents. They have no independently quoted material row, no separately fabricated tiled shower PAN. WC originally seeded **Cortar Bone/Clay AntiSlip**, whereas parent prior SOURCE LEVEL **Cortar Bone/Clay Soft**, separate finish identity/lab; 24x48 nominal sizes alone do not grant pooled lot or matching test. The source parent TOTO Nexus toilet has actual location/UniFit, water closet entry, door, finished wall rough-in and floor transition uncertain; **TX203A specifically UNPLACED**. 1:1 threshold should include finish faces, profile, stool/door swing, actual toilet base clearance and cleaning access; do not order an additional WC toilet or claim exact placement.

### Factory 1:1 release test

Each selected physical drain x2 bathroom copies: real Brizo rough and selected reversible frame, signed manufacturer-compatible waterproof pan to wall, actual calibrated tile/body/grout and mechanical rough, verified slope/door glass and water/flood test, maintenance removal/cleaning. Independently **original raw numeric wet DCOF for exact selected LEVEL Soft tile, exact WC AntiSlip finish and independent LINEAR PAN tile**, plus item color/finish/size/test method/report date/batch. Manufacturer brochure Targets and other finishes are INVALID substitutes. All source and physical shop signatures FALSE; all procurement FALSE.
""")

mdout("R35_FOUR_ROOM_GOOD_BETTER_BEST_AND_13ROOM_GC_PROCUREMENT_RELEASE_BOOK.md",f"""
# R35 owner presentation, conditional material/installed scope and full 13-room approval workflow

Four focus rooms: **PH-PRIMARY / PH-WC and TX-PRIMARY / TX-WC**, four original Primary/WC physical-copy pairs, eight room-zone identities. Every GOOD/BETTER/BEST option in the 12-row design register is a conditional architectural material/assembly alternate, NOT a selected new pan tile or a blind-board-scored challenger.

## Differentiated owner design value

**Primary GOOD:** retain the original Bone or Clay Soft LEVEL source and AntiSlip WC selection, Brizo 48-in Black Onyx selected LINEAR and rough, original mixed floor quote unresolved. Lowest proposed redesign but no shower-PAN original raw wet result and owner release cannot pass.

**Primary BETTER:** selected reversible Brizo SOLID Black Onyx metal grate, separate original BR73480, qualified individually wet-tested small-format sloped LINEAR pan (specific tile unselected), calibrated membrane/threshold and W1/W2 balanced focal cuts. No tile insert chip/frame issue, but pan wet approval and GC bid/rough/slope unresolved.

**Primary BEST:** conditional Daltile RL21 Dynamic Beige 12x24 LEVEL plus separate 1.5-in hex PAN with factory tile-in or solid BNX gate; material alignment may improve design, but two independent production SKUs/origins/lots, conflicting mosaic thickness/grout, missing exact measured numeric wet DCOF and current landed costs keep option unselected. WC AntiSlip must independently fit. Never represent this as accepted cost savings or proven buyer premium.

**WC GOOD:** keep seeded AntiSlip original WC with no additional tile purchase. **WC BETTER:** verify independent anti-slip factory lab, door/toilet rough and calibrated floor-to-Primary Soft threshold. **WC BEST:** one coordinated approved Primary/WC original room-level release including physical source IDs, installer mockup and same-lot procurement *only where factory item/finish are truly identical*; Soft/AntiSlip are not automatically poolable.

## Selected owner program locks outside the four focus rooms

PH/TX Bath2 and TX Bath4 remain actual selected Duravit tubs **NO tiled shower PAN**, respectively Hansgrohe Matte White/Chrome/Matte White; PH2/TX4 pressure-balance-only diverter spout vs selected thermostat conflict and TX2 absent scheduled bathing mixer/rough/spout identity remain blocked. PH-BATH4 remains WALK-IN with selected Brizo square POINT, distinct four-plane shower PAN and LEVEL. PH/TX BATH3 owner TUB vs WALK-IN undecided, square POINT drains only for conditional walk-in, PH3 basin unselected; TX2 basin and TX POWDER2 basin unselected. Primary showers never gain niches, powder wood floors are dry, PH Powder Brizo wall faucet requires separate rough, TX Powder AXOR One and Metropol are different wall trim programs, TX Powder2 Tecturis E is DECK. Parent WC floors count once, and TX203A remains unplaced. No false transfer of flat tile wet permission to Ribbed/Opal, or maker numeric LEVEL lab to PAN.

## 13-room source/quote conservation

13 distinct rooms x two copies, 27 historical material rows with **two excluded/unpriced Primary niche references**, 25 original provisional elevations, 65 historical trade actions preserved. Historical material-only **$23,572.44** four-unit total with old 15% waste ONCE. Original subgroup Sandstone **51.64 SF/$358.92**, Grey Soft **165.40 SF/$1116.46**, Caviar **34.52 SF/$1163.32** ALREADY INCLUDED. No original WC separate floor line, no duplicate PAN/LEVEL area, no added 15%, no redundant BR73480 as wall-edge trim, no double niche aperture and returns, no unmeasured profile/movement charge. Current price classifications separate historical rate, public manufacturer MSRP, online retail indication, proposed owner allowance, hypothetical quantity sensitivity, UNKNOWN current Chicago supplier offer and UNKNOWN full installed GC bid. The online 12x24 RL21 box sizes are not authenticated current factory Chicago usable cartons and DO NOT transfer to hex mosaic. Only genuine same SKU/color/finish/lot is poolable.

Market context PH ~$2.8M, TX ~$2.7M, 14 listings represent NINE real buildings including 405 W Armitage OT01–04 as one precedent, Old Town primary $2.4M-$3.2M, Lincoln Park/Gold Coast secondary. Do not infer competitor tile from unauthorized photos or fabricate buyer premium.

## Sequential eight-trade signature gate

1. **Owner** chooses actual floor A versus B *only after vendor original quote written inclusion evidence*, approves exact existing finishes/optional grate/tile alternative and budget cap.
2. **Architect** certifies true 1529 native project and measured four-physical bath/WC pair geometry, actual shower/level/wc floor polygons, verified W1/W2 and nonexistent Primary W3/NO niches, glass/door threshold and trim finish datum.
3. **Plumber** verifies selected 48-in BT0734816-BNX + ONE required BR73480 per actual shower, original duplicated rough label versus separately numbered optional wall trim, drain outlet elevations and accessible service; carries other room selected plumbing untouched.
4. **Waterproofing** submits maker-compatible true Brizo water-protection rough channel, approved membrane/bonding and wet-wall corners; actual site slope/threshold and physical water test.
5. **Tile installer** selects only owner-approved exact color/size/finish SKU; independent original exact numerical wet LEVEL and LINEAR PAN laboratory report; WC AntiSlip independent proof, chip/grout tolerance 1/8 vs3/16, 3-in focal cuts and 1:1 full assembly.
6. **Supplier** establishes verified factory lot/color/caliber, exact orderable SKU and usable case/real Chicago allocation, actual carton ceil, delivered stock and freight/ETA.
7. **GC estimator** prepares actual post-survey NET LEVEL/WC/PAN takeoff, original quote/invoice/order/paid reconciliation, installed labor/backer/slope/membrane/edge/grout/rough, legitimate deletion credits and priced written CO if any. A/B branches never both bill.
8. **Purchaser** no stock reservation/PO without all seven authentic signoffs, applicable original four-specialist governance and independent Reviewer clearance where required.

Original MARKET .30 worker13, DESIGN .25 worker9 FAILED two R014 reports, BUILD .25 worker10, COST .20 worker12. Original R014 6 of8 critiques, R015 three-seat dispatch HOLD, R017 frozen source no independent clearance. Challenger scoring needs all four authentic original seats, all hard gates, each specialist >=3.0 and +0.25 weighted advantage in a later authorized turn. Original non-Pro Reviewer15 last finished/nonrevivable, no fabricated R35 independent CONTINUE/FIX/DONE or global closure. All owner/trade/PO fields FALSE.
""")

# Manifest exact immutable ancestor hashes and original signed material tables.
ancestors={}
for i in list(range(12,32))+[33]:
    dirs=[d for d in (P/"deliverables").glob(f"integrated-r{i}*") if (d/"MANIFEST.json").exists() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(dirs)==1,(i,[str(d) for d in dirs])
    ancestors[f"R{i:03d}_INTEGRATED"]=hashlib.sha256((dirs[0]/"MANIFEST.json").read_bytes()).hexdigest()
for name,(path,_sha) in S.items():ancestors[name]=hashlib.sha256((P/path).read_bytes()).hexdigest()
for formal in ("ROUND014_SUBMISSION","ROUND017_SUBMISSION"):
    ancestors[formal]=hashlib.sha256((P/"state"/(formal+".json")).read_bytes()).hexdigest()
manifest=dict(
 round=35,project="1529 Wieland 13 bathroom design/tile/GC program",
 date_local="2026-11-06",
 phase="SUBSTANTIVE_ADDITIVE_PRIMARY_WC_LINEAR_GRATE_NET_PAN_GC_RELEASE_NOT_BLIND_BOARD",
 focus_rooms=list(FOCUS),immutable_predecessor_manifest_sha256=ancestors,
 original_scope={"distinct_rooms":13,"physical_two_copy_instances":26,
  "original_material_source_rows":27,"excluded_unpriced_primary_niche_refs":2,
  "old_wall_elevations":25,"old_trade_actions":65,"historic_four_unit_material_only_USD":"23572.44",
  "waste_15pct_in_original_gross_once":True,
  "historic_sandstone_included_USD":"358.92","historic_grey_soft_included_USD":"1116.46",
  "historic_caviar_included_USD":"1163.32",
  "comp_listing_entries":14,"independent_comp_buildings":9},
 new_engineering={
  "two_branch_balanced_primary_copy_models":len(account),
  "old_contract_cost_bucket_distinct_holdpoints":len(forbidden),
  "parent_WC_unit_source_physical_zones":len(unitpairs),
  "maker_identity_source_version_items":len(manufacturer),
  "solid_vs_two_thickness_RL21_frame_joint_physical_cases":len(frames),
  "linear_drain_rough_membrane_threshold_slope_models":len(slopes),
  "actual_only_W1W2_balanced_3in_focal_cut_cases":len(cuts),
  "four_room_good_better_best_options":len(tiers),
  "fictional_distinct_SOFT_ANTISLIP_PAN_case_math":len(cases),
  "duplicate_BR73480_source_item_4_physical_checks":len(rough),
  "two_branch_four_drain_installed_CO_ledger":len(installed),
  "original_independent_exact_lab_roles":len(labs),
  "three_source_sections_per_four_selected_drain":len(sections),
  "27_history_to_current_quote_crosswalk":len(normalize),
  "26_physical_instance_release":len(physical),
  "50_original_W_wall_additive_specific_gates":len(walls),
  "13_room_final_release":len(release),
  "eight_trade_13room_sequential_actions":len(trades),
  "16_future_camera_sample_briefs":len(briefs),
  "four_primary_no_W3_source_guards":len(missing_w3)
 },
 distinct_PRIMARY_LEVEL_wc_floor_PAN_original_scope_A_or_B="UNRESOLVED_MUTUALLY_EXCLUSIVE",
 correct_1529_native_or_measured_polygon_verified=False,
 selected_BNXL_48in_rough_preserved=True,
 selected_primary_extra_niches_added=False,
 source_DUPLICATE_BR73480_assumed_two_required_roughs=False,
 true_rl21_nominal_body_and_grout_version_resolved=False,
 exact_raw_numeric_wet_LEVEL_and_LINEAR_PAN_lab_received=False,
 factory_brizo_drain_waterproof_membrane_approved=False,
 verified_current_sku_color_finish_usable_case_caliber_lot_chicago_bid=False,
 source_floor_quote_inclusion_approved=False,
 current_installed_GC_bid_or_payable_CO_established=False,
 original_four_critic_reports_complete=False,
 independent_nonpro_reviewer_accepted=False,
 original_formal_board_round=17,
 weighted_scores=None,
 owner_approved=False,architect_approved=False,plumber_approved=False,
 waterproof_approved=False,tile_installer_approved=False,
 supplier_approved=False,GC_approved=False,purchaser_approved=False,
 material_reserved=False,purchase_authorized=False,global_DONE=False,
 files=[{"relative_path":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()} for name,data in sorted(FILES.items())]
)
assert len(FILES)>=20,len(FILES)
OUT.mkdir(parents=True,exist_ok=False)
for name,data in sorted(FILES.items()):
    with (OUT/name).open("xb") as f:f.write(data)
(OUT/"MANIFEST.json").write_bytes((json.dumps(manifest,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R35_SIGNED_PAYLOADS",len(FILES))
print("R35_MANIFEST_SHA256",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
print("R35_COUNTS",json.dumps(manifest["new_engineering"],sort_keys=True))
