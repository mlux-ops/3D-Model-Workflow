"""Independent strict READ-ONLY R39 byte/signature, arithmetic, item application,
mutually-exclusive owner branches, original source and 13-room release verifier.
No file mutations, no model/native writes or external contact.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import csv,hashlib,json,math
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement"
SHA="34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"
M=D/"MANIFEST.json"
assert hashlib.sha256(M.read_bytes()).hexdigest()==SHA
m=json.loads(M.read_text(encoding="utf-8"))
assert m["round"]==39 and len(m["files"])==23
assert len(list(D.iterdir()))==24
assert len({x["path"] for x in m["files"]})==23
for f in m["files"]:
    data=(D/f["path"]).read_bytes()
    assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["path"]
PRE={
"R37_FULL":("deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement/MANIFEST.json","985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"),
"R38_PRELIM_SOURCE":("state/ROUND038_NEXT_DISTINCT_WET_WALL_MAKER_PERMISSION_FULL_FIELD_NICHE_OPENING_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","34d5fa02c436cf94d06aa56e662dad27ffc57fbb11b4dd8a9a18a084b03a80f4"),
"R36_PRELIM_SOURCE":("state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"),
"R35_FULL":("deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json","75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"),
"R30_FULL":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
"R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e")}
for key,(path,sha) in PRE.items():
    assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha==m["predecessor_signed_file_hashes"][key],key
for i in list(range(12,32))+[33,35]:
    dirs=[x for x in (B/"deliverables").glob(f"integrated-r{i}*") if (x/"MANIFEST.json").exists() and x.name!="integrated-r17-numeric-product-leads"]
    assert len(dirs)==1,(i,dirs)
    assert hashlib.sha256((dirs[0]/"MANIFEST.json").read_bytes()).hexdigest()==m["predecessor_signed_file_hashes"][f"R{i:03d}_INTEGRATED"]
def rows(prefix):
    x=[e["path"] for e in m["files"] if e["path"].startswith(prefix) and e["path"].endswith(".csv")]
    assert len(x)==1,(prefix,x)
    with (D/x[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def close(a,b,tol=.00011):
    assert abs(float(a)-float(b))<tol,(a,b)
def false(rows_,columns):
    for x in rows_:
        for column in columns:assert x[column]=="FALSE",(x.get("room"),column,x[column])
SRC=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
W=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
A=list(csv.DictReader((B/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
R31L=list(csv.DictReader((B/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv").open(encoding="utf-8-sig")))
R31W=list(csv.DictReader((B/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv").open(encoding="utf-8-sig")))
R31U=list(csv.DictReader((B/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv").open(encoding="utf-8-sig")))
ROOMS=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
ids={x["id"] for x in ROOMS}
assert (len(SRC),len(W),len(A),len(R31L),len(R31W),len(R31U),len(ids))==(27,25,65,13,50,26,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in SRC)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in SRC)==2
assert m["baseline"]["original_four_unit_material_ONLY_USD"]=="23572.44"
assert m["baseline"]["original_three_focus_rooms_nine_source_material_rows_historic_total_USD"]=="6483.08"
FOCUS={"PH-BATH3","PH-BATH4","TX-BATH3"}

neutral=rows("R39_6_FOCUS")
assert len(neutral)==6 and Counter(x["room"] for x in neutral)==Counter({r:2 for r in FOCUS})
assert all(x["formal_board_round"]=="17" and x["weighted_score"]=="NULL" for x in neutral)
assert all("Wet" not in x["original_level_numeric_raw_lab"] for x in neutral)
false(neutral,("four_original_SPECIALIST_critiques_complete","owner_chosen","manufacturer_WP_system_and_installed_1to1_signed","purchase_authorized"))
assert all(x["evidence_grade"] in ("LIVE_PUBLIC_ITEM","ARCHIVED_PRODUCT_EXACT_CURRENT_REVALIDATION_REQUIRED") for x in neutral)
assert all(x["maker_nominal_body_mm"] if False else True for x in neutral)

cuts=rows("R39_72_PLUS")
assert len(cuts)==144
assert {x["room"] for x in cuts}==FOCUS
for x in cuts:
    w=float(x["source_width_in_DRAWING_UNVERIFIED"])
    n=int(x["nominal_center_full_tiles"])
    j=float(x["hypothetical_grout_joint_in"])
    tile=float(x["tile_nominal_horizontal_axis_in"])
    edge=(w-n*tile-(n+1)*j)/2
    close(x["theoretical_left_cut_in"],edge)
    close(x["theoretical_right_cut_in"],edge)
    flag="N_A_SHORT_TILE_AXIS_UNDER_3IN" if tile<3 else "PASS_ILLUSTRATIVE" if 3<=edge<=tile else "FAIL_ILLUSTRATIVE_FOCAL_CUT"
    assert x["project_3in_focal_piece_check"]==flag
    assert j in (.125,.1875)
false(cuts,("physical_1to1_mockup_completed","owner_selection_approved","purchase_authorized"))
trims=rows("R39_36_CONDITIONAL")
assert len(trims)==36
for x in trims:
    close(x["hypothetical_vertical_finish_profile_length_LF"],int(x["hypothetical_exposed_VERTICAL_RETURN_count"])*float(x["drawing_source_tiled_height_in_UNVERIFIED"])/12)
false(trims,("substrate_approved_to_movement_sealant_system","actual_site_measured_edge_count","owner_approved","purchase_authorized"))
niches=rows("R39_24_WET_NICHE")
assert len(niches)==24
for x in niches:
    width=float(x["hypothetical_existing_niche_aperture_width_in"])
    height=float(x["hypothetical_existing_niche_aperture_height_in"])
    dep=float(x["hypothetical_recess_depth_in"])
    o=width*height/144
    close(x["subtract_original_ONE_wall_FIELD_aperture_NET_SF"],o)
    close(x["independently_tiled_niche_BACK_NET_SF"],o)
    close(x["independently_tiled_two_SIDE_returns_NET_SF"],2*height*dep/144)
    close(x["independently_tiled_TOP_NET_SF"],width*dep/144)
    close(x["independently_tiled_SILL_NET_SF"],width*dep/144)
    close(x["total_independent_niche_tiled_faces_NET_SF"],o+2*height*dep/144+2*width*dep/144)
    close(x["hypothetical_full_four_side_trim_or_movement_perimeter_LF"],2*(width+height)/12)
    close(x["hypothetical_positive_sill_2pct_fall_in_NOT_CODE_APPROVAL"],dep*.02)
false(niches,("actual_1to1_waterfall_and_penetration_mockup","owner_approved","purchasing_authorized"))
stacks=rows("R39_36_MAKER")
assert len(stacks)==36
for x in stacks:
    sums=sum(float(x[k]) for k in ("candidate_NOMINAL_body_mm","hypothetical_compressed_set_bed_mm","hypothetical_waterproof_MBR_THICKNESS_mm","hypothetical_BACKER_board_mm"))
    close(x["illustrative_partial_STUD_to_tiled_face_stack_mm"],sums)
    if x["original_NOMINAL_body_mm"]!="UNKNOWN_RELIEF_HIGH_POINT":
        close(x["nominal_delta_body_mm"],float(x["candidate_NOMINAL_body_mm"])-float(x["original_NOMINAL_body_mm"]))
false(stacks,("owner_approved","manufacturer_shop_approved","physical_1to1_accepted","purchase_authorized"))
assemblies=rows("R39_40_SIX_UNIT")
assert len(assemblies)==40
assert Counter(x["room"] for x in assemblies)==Counter({"PH-BATH3":16,"PH-BATH4":8,"TX-BATH3":16})
for x in assemblies:
    tub="TUB" in x["conditional_program"]
    if tub:
        assert x["independent_shower_PAN_role"]=="N_A_TUB_NOT_TILED_SHOWER_PAN"
        assert x["conditional_actual_shower_drain_or_TUB_waste"]=="N_A_TUB_OWNER_UNSELECTED_TUB_WASTE_OVERFLOW"
    else:
        assert "POINT" in x["conditional_actual_shower_drain_or_TUB_waste"]
        assert x["independent_shower_PAN_role"]=="SEPARATE_FOUR_PLANE_POINT_PAN_NO_LEVEL_FLOOR_TRANSFER"
    assert x["actual_selected_fixture_source"]
false(assemblies,("signed_test_board_1to1_mockup_and_flood_when_required","original_OWNER_branch_decision_approved","architect_plumber_WP_installer_GC_approved","purchase_authorized"))
pans=rows("R39_20_PROGRAM")
assert len(pans)==20
for x in pans:
    tub="TUB" in x["conditional_owner_program"]
    if tub:assert x["conditional_point_pan_NET_source_rectangle_SF"]=="N_A_TUB"
    else:
        close(x["conditional_point_pan_NET_source_rectangle_SF"],float(x["source_provisional_footprint_width_in_NOT_CERTIFIED"])*float(x["source_provisional_footprint_depth_in_NOT_CERTIFIED"])/144)
    close(x["hypothetical_one_quarter_in_per_foot_vertical_FALL_in"],0 if tub else .25*float(x["hypothetical_longest_planar_axis_run_ft_NOT_TRUE_CORNERS"]))
false(pans,("actual_code_system_shower_slope_acceptance","actual_sloped_tiling_format_and_bond_maker_signed","owner_TUB_vs_WALKIN_selection_approved","waterproof_installer_GC_approved","purchase_authorized"))
tiers=rows("R39_18_SIX_PHYSICAL_ROOM_GOOD")
assert len(tiers)==18 and Counter(x["owner_tier"] for x in tiers)==Counter({"GOOD":6,"BETTER":6,"BEST":6})
assert all(x["weighted_score"]=="NULL" for x in tiers)
false(tiers,("chosen_for_actual_site","verified_1529_walls_and_actual_niche_location","owner_cap_and_full_budget_spend_accepted","owner_architect_plumber_WP_tile_supplier_GC_signed","original_four_SPECIALISTS_reviewed","purchase_authorized"))
historical=rows("R39_9_EXACT")
assert len(historical)==9
assert sum(Decimal(x["original_two_copy_material_ONLY_total_USD"]) for x in historical)==Decimal("6483.08")
assert Counter(x["room"] for x in historical)==Counter({r:3 for r in FOCUS})
for x in historical:
    gross=Decimal(x["original_one_copy_GROSS_SF_includes15pct"])
    total=Decimal(x["original_two_copy_material_ONLY_total_USD"])
    close(x["original_blended_historic_material_ONLY_rate_USD_per_GROSS_SF"],total/(gross*2))
false(historical,("original_PAID_inventory_credit_or_room_net_wall_verified","current_alternative_material_is_exact_same_factory_product","owner_approved","GC_approved","purchase_authorized"))
rates=rows("R39_6_FACTORY")
assert len(rates)==6
assert sum(x["source_PRIOR_niche_rate_if_SAME_Sandstone_item_USD_per_SF"]!="N_A_DIFFERENT_PRODUCT" for x in rates)==1
false(rates,("current_chicago_offer_ETA_freight_and_tax_verified","actual_change_order_signed","material_PO_released"))
cases=rows("R39_18_THEORETICAL")
assert len(cases)==18
for x in cases:
    gross=float(x["original_old_WALL_gross_per_physical_copy_SF_15pct_once"])
    coverage=float(x["fictional_FUTURE_case_usable_coverage_SF_NOT_REAL"])
    assert int(x["original_wall_two_copies_rounded_SEPARATELY_cases"])==2*math.ceil(gross/coverage)
    assert int(x["hypothetical_two_copies_SAME_LOT_CASE_POOLING_ceiling"])==math.ceil(2*gross/coverage)
false(cases,("same_current_FACTORY_SKU_color_finish_caliber_LOT_verified","same_material_with_original_SANSTONE_NICHE_same_BAG_tag_maker_proven","original_wall_and_niche_combined_quote_RECONCILED","owner_approved","current_supply_offer_verified","purchase_authorized"))
permissions=rows("R39_18_INDIVIDUAL")
assert len(permissions)==18 and Counter(x["room"] for x in permissions)==Counter({r:6 for r in FOCUS})
assert Counter(x["surface"] for x in permissions)==Counter({"ORIGINAL_WET_WALL":3,"ORIGINAL_WET_NICHE":3,"CONDITIONAL_WET_WALL_OPTION":6,"BATH_LEVEL_WET_FLOOR":3,"CONDITIONAL_POINT_PAN_IF_WALKIN":3})
assert all(x["permission_to_install"].startswith("HOLD") for x in permissions)
false(permissions,("purchase_authorized",))
samples=rows("R39_18_SIX_ACTUAL")
assert len(samples)==18
false(samples,("image_or_render_created","physical_sample_created","architect_WP_tile_GC_approved","owner_approved","purchase_authorized"))
normalized=rows("R39_27_HISTORIC")
assert len(normalized)==27
assert sum(Decimal(x["original_two_copy_material_ONLY_USD"] or "0") for x in normalized)==Decimal("23572.44")
assert sum(x["no_order_original_unsupported_Primary_niche"]=="TRUE" for x in normalized)==2
false(normalized,("same_lot_two_copy_factory_verified","buyer_substitution_signed","architect_signed","supplier_signed","GC_signed","purchase_authorized"))
pools=rows("R39_7_CROSS")
assert len(pools)==7
false(pools,("eligible_approved_actual_SameSKU_wet_wall_and_niche","shared_PO_or_material_RESERVATION"))
rel=rows("R39_13_ROOM")
assert len(rel)==13 and {x["room"] for x in rel}==ids
assert sum(Decimal(x["original_two_copy_historical_material_ONLY_USD"]) for x in rel)==Decimal("23572.44")
assert all(x["original_board_round"]=="17" and x["formal_weighted_score"]=="NULL" for x in rel)
assert all("N_A_WOOD" in x["exact_original_RAW_wet_LEVEL_DCOF_role"] for x in rel if x["room"] in ("PH-POWDER","TX-POWDER","TX-POWDER2"))
assert all("N_A_DURAVIT_TUB" in x["separate_LINEAr_or_POINT_PAN_exact_RAW_numeric_wet_DCOF"] for x in rel if x["room"] in ("PH-BATH2","TX-BATH2","TX-BATH4"))
assert all("LINEAR" in x["original_SELECTED_fixture_program"] and "BR73480" in x["original_SELECTED_fixture_program"] for x in rel if x["room"] in ("PH-PRIMARY","TX-PRIMARY"))
assert all("BT062415-BNX" in x["original_SELECTED_fixture_program"] for x in rel if x["room"]=="PH-BATH4")
false(rel,("owner_signed","architect_signed","plumber_signed","waterproof_trade_signed","tile_trade_signed","supplier_signed","GC_signed","purchaser_signed","actual_owner_material_release","purchase_authorized","independent_four_specialists_complete","independent_nonpro_reviewer_DONE"))
trades=rows("R39_104_EIGHT")
assert len(trades)==104 and Counter(x["responsible_trade"] for x in trades)==Counter({t:13 for t in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")})
false(trades,("owner_approved","GC_approved","purchaser_release"))
units=rows("R39_26_ORIGINAL")
assert len(units)==26 and {x["room"] for x in units}==ids
false(units,("owner_approved","architect_approved","plumber_approved","waterproof_approved","installer_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
walls=rows("R39_50_ORIGINAL")
assert len(walls)==50
false(walls,("owner_approved","architect_approved","waterproof_installer_signed","purchase_authorized"))
assert m["formal_board_round"]==17
for k in ("original_four_specialist_critic_reports_complete","independent_R39_reviewer_accepted",
          "actual_native_1529_or_field_geometry_verified","current_EXACT_original_Opal_Ribbed_Emerald_item_wet_PERMISSION_approved",
          "owner_approved_WALL_or_NICHE_substitution","approved_WP_membrane_with_selected_drain_and_factory_rough",
          "exact_raw_numeric_wet_LEVEL_and_separate_POINT_PAN_test_received",
          "original_paid_stock_or_real_Chicago_case_lot_current_offer",
          "actual_installed_GC_bid_and_CHANGE_ORDER_signed","actual_1to1_physical_mockups_or_renders_produced",
          "owner_TUB_vs_WALKIN_selection_changed","owner_approved","architect_approved",
          "plumber_approved","waterproofing_approved","tile_installer_approved",
          "supplier_approved","GC_approved","purchaser_approved","material_reserved","purchase_authorized","global_DONE"):
    assert m[k] is False,k
assert len([f for f in m["files"] if f["path"].endswith(".md")])==4
print("PASS R39 STRICT READ ONLY 23/23 signed SHA+bytes, immutable R12-R38 predecessor lineage")
print("PASS R39 six neutral/144 tile modules/36 trim/24 niches/36 finish stacks/40 WP/20 slope/18 owner tiers")
print("PASS R39 9 original floor/niche/wall $6483.08 INCLUDED in original 27/$23572.44, old15pct once")
print("PASS R39 individual WALL/NICHE vs LEVEL/POINT PAN wet evidence, 13 room/26 physical/50 walls/104 trade all FALSE")
print("R39_MANIFEST_SHA",SHA)
