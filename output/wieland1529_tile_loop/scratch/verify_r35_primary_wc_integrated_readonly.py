"""Strict independent R35 read-only post-signature audit.
No modifications; exact original product, source, two mutually exclusive floor
branches, wet gates, historic money and all release flags tested.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import csv,hashlib,json,math
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC"
M=D/"MANIFEST.json"
SHA="75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"
assert hashlib.sha256(M.read_bytes()).hexdigest()==SHA
m=json.loads(M.read_text(encoding="utf-8"))
assert m["round"]==35 and len(m["files"])==24 and len(list(D.iterdir()))==25
for x in m["files"]:
    raw=(D/x["relative_path"]).read_bytes()
    assert len(raw)==x["bytes"] and hashlib.sha256(raw).hexdigest()==x["sha256"],x["relative_path"]
P={}
for i in list(range(12,32))+[33]:
    choices=[d for d in (B/"deliverables").glob(f"integrated-r{i}*") if
             (d/"MANIFEST.json").exists() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(choices)==1,i
    hash=hashlib.sha256((choices[0]/"MANIFEST.json").read_bytes()).hexdigest()
    assert hash==m["immutable_predecessor_manifest_sha256"][f"R{i:03d}_INTEGRATED"]
    P[f"R{i}"]=hash
for name,path,sha in [
 ("R30","deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
 ("R33_FULL","deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"),
 ("R34_SOURCE","state/ROUND034_DISTINCT_ORIGINAL_PRIMARY_WC_POINT_LINEAR_LEVEL_PAN_SOURCE_PREPARED_NOT_REVIEWED.json","c00f011dfb83ad27360c2caebd7038a60caac4ba59647df51a6dea1c65b4ec22"),
 ("R31_SOURCE","state/ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json","61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"),
 ("R31_FULL","deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/MANIFEST.json","b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457"),
 ("R32_SOURCE","state/ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json","9ad8564e2676f4e72533e6830bea627757e393dc1cdc537b297d443caae962b4"),
]:
    assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha==m["immutable_predecessor_manifest_sha256"][name]
def csvrows(prefix):
    choices=[x["relative_path"] for x in m["files"] if x["relative_path"].startswith(prefix) and x["relative_path"].endswith(".csv")]
    assert len(choices)==1,(prefix,choices)
    with (D/choices[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def num(v):return float(v)
def close(a,b,tol=.00011):assert abs(num(a)-num(b))<tol,(a,b)
def false(rows,fields):
    for x in rows:
        for f in fields:assert x[f]=="FALSE",(f,x.get("room"),x[f])

old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
walls0=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
action0=list(csv.DictReader((B/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
rooms=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(old),len(walls0),len(action0),len(rooms))==(27,25,65,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
ids={x["id"] for x in rooms}
focus={"PH-PRIMARY","PH-WC","TX-PRIMARY","TX-WC"}
assert ids>=focus and len(ids)==13
f_old={x["room"]:x for x in old if x["source_surface"]=="floor"}
wcarea={"PH-PRIMARY":15.,"TX-PRIMARY":14.}
batharea={"PH-PRIMARY":103.,"TX-PRIMARY":87.}
width={"PH-PRIMARY":5.854,"TX-PRIMARY":5.1875}
depth={"PH-PRIMARY":4.646,"TX-PRIMARY":4.7708}
assert {x["room"] for x in walls0 if x["wall"]=="W3" and x["room"] in ("PH-PRIMARY","TX-PRIMARY")}==set()

bal=csvrows("R35_8_TWO_COPY_MUTUALLY")
assert len(bal)==8
assert len({(x["room"],x["physical_parent_source_copy"],x["branch"]) for x in bal})==8
assert {x["branch"] for x in bal}=={"A_PAN_INCLUDED_IN_ORIGINAL_BATH_FLOOR","B_PAN_EXCLUDED_FROM_ORIGINAL_BATH_FLOOR"}
for x in bal:
    p=x["room"];bath=batharea[p];wc=wcarea[p];pan=width[p]*depth[p]
    included=x["branch"].startswith("A_")
    lev=bath-pan if included else bath
    total_level=lev+wc
    total=total_level+pan
    gross=float(f_old[p]["source_gross_sf_one_copy_waste_15pct_once"])
    rate=Decimal(f_old[p]["historic_usd_two_copies"])/(Decimal(str(gross))*2)
    extra=0. if included else pan*1.15
    close(x["hypothetical_bath_LEVEL_excluding_PAN_NET_SF"],lev)
    close(x["hypothetical_inherited_WC_LEVEL_NET_SF"],wc)
    close(x["hypothetical_total_LEVEL_NET_SF"],total_level)
    close(x["hypothetical_distinct_LINEAR_PAN_NET_SF"],pan)
    close(x["hypothetical_unique_total_LEVEL_plus_PAN_NET_SF"],total)
    close(x["historic_original_floor_GROSS_SF_per_copy_waste15pct_once"],gross)
    close(x["reconstructed_original_waste15pct_once_GROSS_SF"],(bath+wc)*1.15)
    close(x["hypothetical_PAN_GROSS_INCREMENT_BRANCH_B_over_A_SF"],extra)
    close(x["historic_mixed_floor_rate_USD_per_GROSS_SF_REFERENCE_ONLY"],float(rate))
    assert abs(num(x["theoretical_incremental_BLEND_RATE_proxy_USD_nonpayable"])-round(float(rate)*extra,2))<.011
    assert x["original15percent_not_reapplied_to_historical_gross"]=="TRUE"
false(bal,("source_geometry_certified","owner_approved","GC_authorized","purchase_authorized"))
assert Counter(x["room"] for x in bal)==Counter({"PH-PRIMARY":4,"TX-PRIMARY":4})

historical=csvrows("R35_8_HISTORIC")
assert len(historical)==8
false(historical,("new_owner_CO_established","procurement_release"))
physical=csvrows("R35_8_PRIMARY_WC_PHYSICAL")
assert len(physical)==8
assert all(x["WC_own_new_order_authorized"]=="FALSE" for x in physical)
false(physical,("architect_signed","tile_installer_signed","owner_approved","purchase_authorized"))
maker=csvrows("R35_11_INDIVIDUAL")
assert len(maker)==11
assert any(x["product_identity"]=="BT0734816-BNX" for x in maker)
assert any(x["product_identity"]=="BR73480" for x in maker)
assert any("RL21" in x["product_identity"] for x in maker)
false(maker,("owner_material_substitution_approved","purchase_authorized"))
frame=csvrows("R35_24_SIX_PRIMARY_BRIZO")
assert len(frame)==24
assert Counter(x["frame_mode_alternative"] for x in frame)==Counter({
 "SOLID_BNX_FINISH_MATCHED_NO_TILE_INSERT":8,
 "TILEIN_OLDER_RL21_BROCHURE_1OVER4IN":8,
 "TILEIN_CURRENT_RL21_MAKER_5OVER16IN":8})
assert all(x["source_selected_Brizo_trim"]=="BT0734816-BNX" and x["source_separate_required_rough"]=="BR73480" for x in frame)
assert all(x["actual_watertight_connection_and_maker_written_approval"]==x["purchase_authorized"]=="FALSE" for x in frame)
slope=csvrows("R35_32_PRIMARY")
assert len(slope)==32
for x in slope:
    close(x["theoretical_perimeter_to_drain_rise_inches_not_shop"],
          num(x["source_shower_depth_FT_UNVERIFIED"])*num(x["assumed_uniform_sloped_pan_FALL_in_per_foot_NOT_CODE"]))
false(slope,("actual_slope_CODE_and_maker_grade_approved","actual_membrane_compatible_Brizo_WPS_written_system","purchase_authorized"))
cut=csvrows("R35_24_PARENT_PRIMARY")
assert len(cut)==24 and {x["source_shower_wall"] for x in cut}=={"W1","W2"}
for x in cut:
    c=int(x["intentional_central_full_tiles"]);span=num(x["source_width_in_UNVERIFIED"])
    joint=num(x["illustrative_joint_in"])
    end=(span-24*c-(c+1)*joint)/2
    close(x["theoretical_symmetric_left_and_right_focal_cut_in"],end)
    assert x["project_min3in_focal_cut_test"]==("PASS_THEORY" if 3<=end<=24 else "FAIL_THEORY")
    assert x["original_NICHES_in_Primary"]=="NONE_NO_NEW"
false(cut,("architect_tiler_1to1_approval","owner_approved","purchase_authorized"))
alts=csvrows("R35_12_FOUR_ROOM")
assert len(alts)==12 and {x["room"] for x in alts}==focus
assert Counter(x["tier"] for x in alts)==Counter({"GOOD":4,"BETTER":4,"BEST":4})
assert all(x["score_weighted_BOARD"]=="NULL" for x in alts)
false(alts,("current_hypothetical_alternative_owner_selection","owner_approved","architect_plumber_waterproof_tile_signed","purchase_authorized"))
case=csvrows("R35_36_BATH")
assert len(case)==36 and all(x["actual_realized_savings"]==x["purchase_authorized"]=="FALSE" for x in case)
assert all(int(x["theoretical_TWO_separate_copy_ceil_cases"])>=int(x["theoretical_same_SKU_two_copy_pool_ceil_cases"]) for x in case)
bom=csvrows("R35_16_TWO_PRIMARY_PHYSICAL")
assert len(bom)==16 and Counter(x["source_item_or_hard_check"] for x in bom)==Counter({
    "BT0734816-BNX":4,"BR73480":4,"BR73480_DUPLICATE_SOURCE_DESCRIPTION":4,"BT0734870_FAMILY":4})
assert all(x["derived_true_rough_count_from_this_source"]=="1_REQUIRED_PER_LINEAR_DRAIN" for x in bom)
false(bom,("owner_approved_optional_wall_edge_trim","supplier_signed","GC_signed","purchase_authorized"))
co=csvrows("R35_16_SELECTED")
assert len(co)==16
false(co,("payable_change_order_established","owner_approved","purchase_authorized"))
labs=csvrows("R35_13_ORIGINAL")
assert len(labs)==13
assert Counter(x["original_surface_role"] for x in labs)==Counter({
    "LEVEL":8,"LINEAR_SLOPED_PAN":2,"POINT_FOUR_PLANE_SLOPED_PAN":1,
    "CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN":2})
assert all(x["original_raw_measured_wet_DCOF_exact_numeric"]=="" for x in labs)
false(labs,("original_report_RECEIVED","installer_signed","owner_approved","purchase_authorized"))
shop=csvrows("R35_12_SELECTED")
assert len(shop)==12
false(shop,("physical_one_to_one_waterproof_drain_grade_floodtest_signed","all_trades_release","purchase_authorized"))
orig=csvrows("R35_27_HISTORICAL")
assert len(orig)==27
assert sum(Decimal(x["historic_material_only_USD_two_copies"]) for x in orig)==Decimal("23572.44")
assert sum(x["excluded_unpriced_Primary_niche_NO_NEW_ORDER"]=="TRUE" for x in orig)==2
false(orig,("same_SKU_COLOR_SIZE_FINISH_LOT_pool_authorized","payable_credit_or_CO_approved","owner_approved","supplier_signed","purchase_authorized"))
unit=csvrows("R35_26_ORIGINAL")
assert len(unit)==26 and {x["room"] for x in unit}==ids
assert len({(x["room"],x["physical_copy_number"]) for x in unit})==26
false(unit,("owner_signoff","architect_signoff","plumber_signoff","waterproof_signoff","tile_installer_signoff","supplier_signoff","GC_signoff","purchaser_signoff","purchase_authorized"))
wall=csvrows("R35_50_PRIOR")
assert len(wall)==50
assert all(x["source_wall_reference"] in ("W1","W2") for x in wall if x["room"] in ("PH-PRIMARY","TX-PRIMARY"))
false(wall,("owner_approved","waterproof_and_tile_signed","purchase_authorized"))
release=csvrows("R35_13_ROOM_BATH")
assert len(release)==13 and {x["room"] for x in release}==ids
assert all(x["original_board_round"]=="017" and x["original_four_critic_panel_score_clearance"]=="NULL" for x in release)
false(release,("owner_approved","architect_approved","plumber_approved","waterproofing_approved",
              "tile_installer_approved","supplier_approved","GC_bid_approved","purchaser_approved","material_reserved",
              "purchase_authorized","independent_nonpro_reviewer_accepted"))
assert sum(Decimal(x["original_HISTORICAL_two_copy_material_only_USD"]) for x in release)==Decimal("23572.44")
trade=csvrows("R35_104_EIGHT")
assert len(trade)==104 and Counter(x["trade"] for x in trade)==Counter({
    "OWNER":13,"ARCHITECT":13,"PLUMBER":13,"WATERPROOFING":13,
    "TILE_INSTALLER":13,"SUPPLIER":13,"GC_ESTIMATOR":13,"PURCHASER":13})
false(trade,("owner_approved","current_GC_contract_release","purchase_authorized"))
briefs=csvrows("R35_16_FOUR_ROOM_EIGHT")
assert len(briefs)==16
false(briefs,("physical_mockup_built","actual_camera_or_image_generated","owner_signed","architect_WP_tile_signed","purchase_authorized"))
noW3=csvrows("R35_4_PRIMARY")
assert len(noW3)==4 and all(x["W3_original_R17_source_elevation_exists"]=="FALSE" and x["W3_wall_width_in"]=="" for x in noW3)
false(noW3,("need_a_third_wall_construction_or_elevation_approval","architect_signed","owner_approved","purchase_authorized"))
for k in ("correct_1529_native_or_measured_polygon_verified",
          "source_DUPLICATE_BR73480_assumed_two_required_roughs",
          "true_rl21_nominal_body_and_grout_version_resolved",
          "exact_raw_numeric_wet_LEVEL_and_LINEAR_PAN_lab_received",
          "factory_brizo_drain_waterproof_membrane_approved",
          "verified_current_sku_color_finish_usable_case_caliber_lot_chicago_bid",
          "source_floor_quote_inclusion_approved","current_installed_GC_bid_or_payable_CO_established",
          "original_four_critic_reports_complete","independent_nonpro_reviewer_accepted",
          "owner_approved","architect_approved","plumber_approved","waterproof_approved",
          "tile_installer_approved","supplier_approved","GC_approved","purchaser_approved",
          "material_reserved","purchase_authorized","global_DONE"):
    assert m[k] is False,k
assert m["weighted_scores"] is None and m["original_formal_board_round"]==17
print("PASS R35 READ ONLY 24 SHA+byte files, R12-R31/R33 signed manifests, six source+blind receipts")
print("PASS R35 A/B mutually exclusive 8 balanced physical Primary/WC quote lines, 13 lab roles, 24 tilein/frame, 24 focal, 32 slopes")
print("PASS R35 historical 27/25/65 and 13 rooms/50 W/26 physical/104 trade; 23572.44 USD with original15pct once")
print("PASS R35 all 8 trade/owner/GC/PO FALSE; exact BNX+BR73480 once, NO W3 or added Primary niches; scored NULL")
print("R35_MANIFEST_SHA",SHA)
