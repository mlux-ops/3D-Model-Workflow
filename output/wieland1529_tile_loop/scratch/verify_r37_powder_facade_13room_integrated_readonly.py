"""Strict R37 post-signature independent READ-ONLY source and arithmetic QA."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import csv,hashlib,json,math
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement"
S="985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"
M=D/"MANIFEST.json"
assert hashlib.sha256(M.read_bytes()).hexdigest()==S
m=json.loads(M.read_text(encoding="utf-8"))
assert m["round"]==37 and len(m["files"])==21 and len(list(D.iterdir()))==22
for entry in m["files"]:
    p=D/entry["path"]
    assert p.is_file() and len(p.read_bytes())==entry["bytes"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entry["sha256"]
for label,(path,expected) in {
 "R30_FULL":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
 "R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"),
 "R35_FULL":("deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json","75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"),
 "R36_SOURCE":("state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec")
}.items():
    assert hashlib.sha256((B/path).read_bytes()).hexdigest()==expected==m["predecessor_signed_file_hashes"][label],label
for i in list(range(12,32))+[33,35]:
    ds=[d for d in (B/"deliverables").glob(f"integrated-r{i}*") if (d/"MANIFEST.json").exists() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(ds)==1,(i,ds)
    assert hashlib.sha256((ds[0]/"MANIFEST.json").read_bytes()).hexdigest()==m["predecessor_signed_file_hashes"][f"R{i:03d}_INTEGRATED"]
def rows(prefix):
    matches=[e for e in m["files"] if e["path"].startswith(prefix) and e["path"].endswith(".csv")]
    assert len(matches)==1,(prefix,matches)
    with (D/matches[0]["path"]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def eq(a,b,tol=.00011):
    assert abs(float(a)-float(b))<tol,(a,b)
def FALSE(rs,fields):
    for r in rs:
        for f in fields:assert r[f]=="FALSE",(f,r.get("room"),r[f])
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
walls25=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
a65=list(csv.DictReader((B/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
rooms_current=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
original_ids={x["id"] for x in rooms_current}
assert (len(old),len(walls25),len(a65),len(original_ids))==(27,25,65,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
FOCUS={"PH-POWDER","TX-POWDER","TX-POWDER2"}
assert sum(Decimal(x["historic_usd_two_copies"]) for x in old if x["room"] in FOCUS)==Decimal("2159.30")
original=rows("R37_3_ACTUAL")
assert len(original)==3 and {x["room"] for x in original}==FOCUS
for x in original:
    width=float(x["source_wall_W1_width_in_UNVERIFIED"]);height=float(x["source_wall_W1_height_in_UNVERIFIED"])
    face=width*height/144.
    eq(x["source_full_wall_W1_field_NET_before_splash_mirror_escutcheon_SF"],face)
    eq(x["reconstructed_prior_gross_only_once_1point15_SF"],face*1.15)
    eq(x["original_historic_minus_reconstructed_GROSS_SF"],float(x["original_historic_GROSS_SF_per_copy_includes15pct"])-face*1.15)
    assert x["original_source_W3_face_exists"]=="FALSE"
    assert x["WOOD_FLOOR_untiled"]=="TRUE"
FALSE(original,("new_material_quote_issued","owner_approved","purchase_authorized"))
apertures=rows("R37_24_SIX_POWDER_W1_MIRROR")
assert len(apertures)==24
assert Counter(x["room"] for x in apertures)==Counter({"PH-POWDER":8,"TX-POWDER":8,"TX-POWDER2":8})
for x in apertures:
    sq=float(x["hypothetical_mirror_or_CABINET_external_face_W_in"])*float(x["hypothetical_mirror_or_CABINET_external_face_H_in"])/144.
    deducted=0 if x["mirror_cover_not_a_tile_deduction"]=="TRUE" else sq
    eq(x["hypothetical_wall_aperture_SF"],sq)
    eq(x["field_cladding_deduction_SF_ONCE"],deducted)
    eq(x["conditional_surrounding_wall_FIELD_NET_SF"],
       float(x["original_full_W1_face_SF_unverified"])-deducted)
FALSE(apertures,("actual_recess_owner_approval","actual_native_1529_verified","purchase_authorized"))
landings=rows("R37_18_2COPY")
assert len(landings)==18
for x in landings:
    expected=0 if x["room"]=="TX-POWDER2" else float(x["sample_local_panel_nominal_W_in"])*float(x["sample_local_panel_nominal_H_in"])/144.
    eq(x["hypothetical_local_relief_TILE_removed_SF_once"],expected)
    eq(x["remaining_TILE_field_NET_SF"],float(x["source_full_focal_wall_nominal_tile_field_NET_SF"])-expected)
FALSE(landings,("existing_program_modified_by_this_scenario","owner_panel_selected","architect_PLUMBING_signed","purchase_authorized"))
cuts=rows("R37_24_NEW_POWDER")
assert len(cuts)==24
for x in cuts:
    w=float(x["source_W1_width_in_UNVERIFIED"]);n=int(x["integer_full_center_modules"])
    j=float(x["illustrative_joint_in"]);size=float(x["nominal_tile_face_dimension_in_this_axis"])
    end=(w-size*n-(n+1)*j)/2
    eq(x["hypothetical_balanced_left_and_right_edge_cut_in"],end)
    flag="N_A_NARROW_FORMAT_AXIS" if size<3 else ("PASS_THEORY" if 3<=end<=size else "FAIL_THEORY")
    assert x["project_3in_FOCAL_cut_test"]==flag
FALSE(cuts,("physical_1to1_cut_grout_edge_acceptance","owner_tile_pattern_approved","purchase_authorized"))
heights=rows("R37_18_SIX_POWDER_W1_FULL_HEIGHT")
assert len(heights)==18
for x in heights:
    h=float(x["hypothetical_tile_wall_HEIGHT_in"]);face=float(x["original_full_W1_field_NET_SF"])
    width=float(x["one_full_width_termination_profile_LF"])*12
    calc=face*h/111.
    eq(x["conditional_TILE_NET_to_this_height_SF"],calc)
    eq(x["conditional_FINISHED_PAINT_or_panel_upper_wall_SF"],face-calc)
    if h==111:assert width==0
FALSE(heights,("actual_OWNER_height_and_mirror_counter_sill_layout_approved","original_quote_credit_or_paid_stock_verified","purchase_authorized"))
stacks=rows("R37_18_SIX_PHYSICAL_POWDER")
assert len(stacks)==18
for x in stacks:eq(x["hypothetical_partial_projection_from_original_stud_FACE_mm"],
                   float(x["source_nominal_TILE_BODY_thickness_mm"])+float(x["hypothetical_dry_wall_BACKER_or_board_thickness_mm"])+float(x["hypothetical_COMPRESSED_mortar_thickness_mm"]))
FALSE(stacks,("true_source_manufacturer_supported_combined_assembly","actual_1529_field_tolerance_stack_signed","installer_mockup_approved","purchase_authorized"))
maker=rows("R37_12_INDIVIDUAL")
assert len(maker)==12
assert any(x["exact_source_SKU_or_maker_collection"]=="48140991" and "AXOR" in x["manufacturer"] for x in maker)
assert any(x["exact_source_SKU_or_maker_collection"]=="32526141" and "hansgrohe" in x["manufacturer"] for x in maker)
assert any(x["exact_source_SKU_or_maker_collection"]=="13622181" for x in maker)
assert any(x["exact_source_SKU_or_maker_collection"]=="73072341" and "DECK" in x["product_description"] for x in maker)
FALSE(maker,("current_case_coverage_verified","owner_alternative_material_or_rough_approved","GC_installed_shop_approved","purchase_authorized"))
options=rows("R37_9_THREE_POWDER")
assert len(options)==9 and {x["room"] for x in options}==FOCUS
assert Counter(x["tier"] for x in options)==Counter({"GOOD":3,"BETTER":3,"BEST":3})
assert all(x["original_weighted_board_score"]=="NULL" for x in options)
FALSE(options,("owner_program_selection_made","owner_approved","GC_approved","purchase_authorized"))
instances=rows("R37_18_SIX_UNIT_THREE_SHOP")
assert len(instances)==18 and len({(x["room"],x["physical_source_room"],x["shop_detail"]) for x in instances})==18
FALSE(instances,("original_exact_rough_spout_and_stop_SERVED_UNDER_1to1","actual_signed_full_size_physical_mockup","owner_approved","architect_approved","plumber_approved","tile_installer_approved","GC_approved","purchase_authorized"))
lots=rows("R37_4_REAL")
assert len(lots)==4 and len({x["trade_material_pool_identity"] for x in lots})==4
assert Counter(x["room"] for x in lots)==Counter({"PH-POWDER":1,"TX-POWDER":2,"TX-POWDER2":1})
assert all(x["shareable_WITH_OTHER_POWDER_ROOM_MATERIAL"]=="FALSE" for x in lots)
FALSE(lots,("same_SKU_color_size_finish_exact_FACTORY_lot_confirmed","actual_1529_site_cutstock_signed","actual_case_pooling_or_order_authorized","purchase_authorized"))
cases=rows("R37_12_THEORETICAL")
assert len(cases)==12
assert all(int(x["theoretical_ceiling_TWO_independently_rounded_cases"])>=int(x["theoretical_ceiling_pooled_ONLY_same_factory_SKU_lot_cases"]) for x in cases)
FALSE(cases,("factory_exact_retail_item_and_usable_package_SF_verified","actual_same_shade_lot_caliper_stock_for_both_units","actual_owner_source_material_and_color_allocation_verified","actual_order_rounding_or_savings_claimed","purchase_authorized"))
cost=rows("R37_9_POWDER_FULL_HEIGHT")
assert len(cost)==9
FALSE(cost,("owner_decision_approved","contract_change_order_signed","actual_payable_savings_or_shortage_established","purchase_authorized"))
cameras=rows("R37_18_SIX_UNIT_THREE_VIEW")
assert len(cameras)==18
FALSE(cameras,("background_native_1529_geometry_verified","factory_maker_swatch_verified_color_lot","created_render_or_photo","built_physical_sample_or_mockup","owner_approved","purchase_authorized"))
normalize=rows("R37_27_ORIGINAL")
assert len(normalize)==27
assert sum(Decimal(x["original_historic_two_copy_MATERIAL_ONLY_USD"]) for x in normalize)==Decimal("23572.44")
assert sum(x["excluded_primary_niche_NO_ORDER"]=="TRUE" for x in normalize)==2
FALSE(normalize,("signed_same_FACTORY_product_in_two_copies_only","owner_approved","supplier_approved","GC_approved","purchase_authorized"))
releases=rows("R37_13_ROOM")
assert len(releases)==13 and {x["room"] for x in releases}==original_ids
assert all(int(x["original_board_round"])==17 and x["four_critic_SCORE"]=="NULL" for x in releases)
assert sum(Decimal(x["original_two_copy_historic_material_only_USD"]) for x in releases)==Decimal("23572.44")
FALSE(releases,("owner_approved","architect_approved","plumber_approved","waterproof_approved","tile_installer_approved","supplier_approved","GC_approved","purchaser_approved","material_reserved","purchase_authorized","standing_nonpro_reviewer_accepted"))
trades=rows("R37_104_EIGHT")
assert len(trades)==104 and Counter(x["trade"] for x in trades)==Counter({t:13 for t in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")})
FALSE(trades,("owner_approved","GC_release","purchaser_PO_release"))
units=rows("R37_26_ORIGINAL")
assert len(units)==26 and {x["room"] for x in units}==original_ids
FALSE(units,("physical_one_to_one_full_size_sample_and_source_faithful_camera_receipt","owner_signed","architect_signed","plumber_signed","waterproof_signed","tile_signed","supplier_signed","GC_signed","purchaser_signed","purchase_authorized"))
wallrecords=rows("R37_50_ORIGINAL")
assert len(wallrecords)==50
FALSE(wallrecords,("actual_elevation_shop_verified","owner_approved","architect_and_tiler_signed","purchase_authorized"))
for f in ("owner_faucet_program_TX_POWDER_selected","owner_sink_TX_POWDER2_selected","actual_1529_native_model_or_field_wall_measurements_verified",
          "actual_wall_wet_application_permission_inferred_from_dry","real_current_supplier_chicago_case_stock_eta_installed_quote",
          "source_no_order_historical_quote_reinterpreted_as_actual_order","current_owner_paint_and_local_panel_alternatives_selected",
          "actual_physical_mockups_or_images_created","original_four_critic_reports_complete","independent_nonpro_reviewer_accepted",
          "owner_approved","architect_approved","plumber_approved","waterproofing_approved","tile_installer_approved",
          "supplier_approved","GC_approved","purchaser_approved","material_reserved","purchase_authorized","global_DONE"):
    assert m[f] is False,f
assert m["original_formal_board_round"]==17 and m["weighted_board_scores"] is None
print("PASS R37 STRICT READ ONLY 21/21 SHA+bytes and signed R12-R35/R36 source predecessor")
print("PASS R37 3 source W1 GROSS once, 24 mirror & aperture, 18 local landing, 24 cuts, 18 height, 18 stacks; no false 1529 or W3")
print("PASS R37 12 factory/9 owner design, 4 separated SKU shade groups 12 fictional cases, 9 bid exposures, 27 materials")
print("PASS R37 13/27/25/65 historic source, $23572.44/15pct once, 50 walls/26 physical/104 trade, all release false, formal R017 unchanged")
print("R37_SHA",S)
