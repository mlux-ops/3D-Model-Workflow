"""Independent, read-only R44 full signed structural and fabrication solver QA."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib,json,csv,math,xml.etree.ElementTree as ET,importlib.util
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r44-field-jig-wet-architecture-and-13room-procurement"
SHA="1d7115395e90dd5d0c38b2e8929676f011b0ab897ea4cbfc420f118f2f4d6910"
assert hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest()==SHA
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
assert m["round"]==44 and m["formal_board_round"]==17
assert len(m["files"])==23 and len(list(D.iterdir()))==24
for f in m["files"]:
 data=(D/f["path"]).read_bytes()
 assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["path"]
 if f["path"].endswith(".svg"):
  assert ET.fromstring(data).tag.endswith("svg") and b"NOT certified native 1529" in data
assert sum(f["path"].endswith(".svg") for f in m["files"])==4
assert sum(f["path"].endswith(".py") for f in m["files"])==1
pre={
 "R43_FULL":("deliverables/integrated-r43-four-wet-bath-niche-focal-wall-fabrication-and-13room-GC/MANIFEST.json","71921913b2f8efb733a40d1ca87154c8d816af1519e1a59e5f7dc03943a5d6b0"),
 "R44_SOURCE":("state/ROUND044_NEXT_SOURCE_ONLY_CONTINUOUS_W3_FINISHED_PIER_CAPACITY_PREPARED_NOT_REVIEWED.json","b354b6fffe308bc204c68ee7a56559a6ed3c7dab6ae3dcaea8621f1d43e5c0f5"),
 "R42_FULL":("deliverables/integrated-r42-matte-white-thermostat-diverter-tub-spout-field-rough-wet-wall-GC/MANIFEST.json","1659fb4bb1bb57b1a26e8ab17ad36ce40ed49ba41ebd33b6fb45807e21c94712"),
 "R41_FULL":("deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room/MANIFEST.json","7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0")}
for k,(path,sha) in pre.items():
 assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha==m["predecessor_signed_file_hashes"][k]
def rows(prefix):
 paths=[x["path"] for x in m["files"] if x["path"].startswith(prefix) and x["path"].endswith(".csv")]
 assert len(paths)==1,(prefix,paths)
 with (D/paths[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def eq(a,b,eps=.00011):assert abs(float(a)-float(b))<eps,(a,b)
def flags(R,keys):
 for r in R:
  for k in keys:assert r[k]=="FALSE",(r.get("room"),k,r[k])
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
walls=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
acts=list(csv.DictReader((B/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
lab=list(csv.DictReader((B/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv").open(encoding="utf-8-sig")))
w50=list(csv.DictReader((B/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv").open(encoding="utf-8-sig")))
u26=list(csv.DictReader((B/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv").open(encoding="utf-8-sig")))
source_rooms=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(old),len(walls),len(acts),len(lab),len(w50),len(u26),len(source_rooms))==(27,25,65,13,50,26,13)
assert sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
assert sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old if x["room"] in m["focus_rooms"])==Decimal("9124.72")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
source_wall={(x["room"],x["wall"]):x for x in walls}
source_mat={(x["room"],x["source_surface"]):x for x in old}
survey=rows("R44_8_PHYSICAL")
assert len(survey)==8 and Counter(x["room"] for x in survey)==Counter({r:2 for r in m["focus_rooms"]})
for x in survey:
 assert x["actual_W3_FINISHED_width_in"]=="" and x["actual_W3_service_glass_pipe_exclusion_X_intervals"]==""
 eq(x["source_W3_width_in_UNVERIFIED"],source_wall[(x["room"],"W3")]["source_width_in_UNVERIFIED"])
flags(survey,("site_1529_measured","architect_1529_signed","plumber_obstruction_signed","WP_niche_system_signed","tiler_profile_caliber_signed","actual_physical_1TO1_witness","owner_approved","GC_approved","purchase_authorized"))
datum=rows("R44_16_COHERENT")
assert len(datum)==16
for x in datum:
 room=x["room"];w1=float(source_wall[room,"W1"]["source_width_in_UNVERIFIED"])
 w2=float(source_wall[room,"W2"]["source_width_in_UNVERIFIED"])
 w3=float(source_wall[room,"W3"]["source_width_in_UNVERIFIED"])
 p=float(x["nominal_pitch_in"])
 eq(x["W1_center_to_INSIDE_corner_running_phase_in"],w1/2%p)
 eq(x["W2_return_to_W3_running_phase_in"],(w1/2+w2)%p)
 eq(x["W3_end_running_phase_in"],(w1/2+w2+w3)%p)
 flags([x],("tile_cuts_actual_piece_reuse_verified","owner_approved","architect_approved","fabrication_authorized"))
shop=rows("R44_80_EIGHT")
assert len(shop)==80 and Counter(x["room"] for x in shop)==Counter({r:20 for r in m["focus_rooms"]})
assert len({(x["room"],x["physical_copy"],x["step"]) for x in shop})==80
flags(shop,("actual_physical_1to1_completed","owner_approved","architect_approved","plumber_approved","waterproofer_approved","tiler_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
maker=rows("R44_12_ORIGINAL")
assert len(maker)==12 and sum(x["role"]=="HISTORIC_ORIGINAL_WALL" for x in maker)==4
assert all(x["current_manufacturer_URL"].startswith("https://") for x in maker)
flags(maker,("owner_substitution_approved","architect_approved","purchasing_approved"))
scope=rows("R44_32_INSTALLED")
assert len(scope)==32 and Counter(x["room"] for x in scope)==Counter({r:8 for r in m["focus_rooms"]})
for x in scope:
 eq(x["source_three_wall_full_NET_SF_UNVERIFIED"],sum(float(source_wall[(x["room"],w)]["source_width_in_UNVERIFIED"])*float(source_wall[(x["room"],w)]["source_tiled_height_in_UNVERIFIED"])/144 for w in ("W1","W2","W3")))
 eq(x["proposed_new_full_wall_if_REPLACING_all_three_NET_SF"],float(x["source_three_wall_full_NET_SF_UNVERIFIED"])-16*12/144)
 eq(x["separate_new_NICHE_back_jambs_head_sill_NET_SF"],16*12/144+2*4*12/144+2*4*16/144)
 eq(x["proposed_sill_and_profile_if_four_undisguised_EDGES_LF"],(2*16+2*12)/12)
 eq(x["original_historic_WALL_material_per_GROSS_SF_USD"],float(x["original_two_copy_WALL_historic_material_only_USD"])/(2*float(x["original_WALL_GROSS_SF_ONE_COPY_with_15pct_once"])))
 flags([x],("actual_new_same_factory_SKU_color_finish_lot_verified","signed_change_order_owner_and_GC","purchaser_approved","purchase_authorized"))
choice=rows("R44_24_EIGHT")
assert len(choice)==24 and Counter(x["tier"] for x in choice)==Counter({"GOOD_HISTORIC_UNRELEASED":8,"BETTER":8,"BEST":8})
assert all(x["weighted_score"]=="NULL" for x in choice)
flags(choice,("full_1TO1_physical_mockup_and_render_created","owner_approved","architect_approved","four_authentic_blind_specialists_scored","purchase_authorized"))
branches=rows("R44_36_MUTUALLY")
assert len(branches)==36 and Counter(x["room"] for x in branches)==Counter({"PH-BATH3":12,"PH-BATH4":8,"TX-BATH3":12,"TX-BATH4":4})
assert all(x["independent_exact_raw_numerical_POINT_PAN_lab"]=="N_A_TUB" for x in branches if "TUB" in x["source_program_branch"])
assert all(x["original_exact_raw_numerical_LEVEL_lab"]=="MISSING" for x in branches)
flags(branches,("owner_option_selected","GC_change_order_approved","purchase_authorized"))
unit=rows("R44_26_ORIGINAL")
assert len(unit)==26 and {x["room"] for x in unit}=={x["id"] for x in source_rooms}
flags(unit,("true_1529_field_address_and_W1W2W3_verified","owner_approved","architect_approved","plumber_approved","WP_approved","tiler_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
rel=rows("R44_13_ORIGINAL")
assert len(rel)==13 and {x["room"] for x in rel}=={x["id"] for x in source_rooms}
assert all(x["formal_board_round"]=="17" for x in rel)
assert "FIXED_WALKIN" in next(x["owner_program_original_fixed_or_unselected"] for x in rel if x["room"]=="PH-BATH4")
assert "FIXED_DURAVIT" in next(x["owner_program_original_fixed_or_unselected"] for x in rel if x["room"]=="TX-BATH4")
flags(rel,("old_owner_selected_fixture_CHANGED","true_native_1529_site_measurements_received","original_all_four_AUTHENTIC_critic_scores_and_reviewer_CLEARANCE","owner_approved","architect_approved","plumber_approved","WP_approved","tiler_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
mat=rows("R44_27_HISTORICAL")
assert len(mat)==27 and sum(Decimal(x["historic_two_copy_material_only_USD"] or 0) for x in mat)==Decimal("23572.44")
flags(mat,("same_exact_SKU_COLOR_FINISH_CALIBER_LOT_and_OFFCUT_condition_authorized","owner_approved","purchaser_approved","purchase_authorized"))
trade=rows("R44_104_SEQUENTIAL")
assert len(trade)==104 and Counter(x["trade"] for x in trade)==Counter({t:13 for t in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC","PURCHASER")})
flags(trade,("real_trade_signature","owner_approved","GC_approved","purchaser_approved","purchase_authorized"))
for k in ("original_OWNED_selected_program_CHANGED","actual_true_1529_geometry_received","actual_owner_selected_concept_or_niche","full_manufacturer_exact_original_WET_WALL_and_independent_WET_NICHE_approval","exact_original_RAW_numerical_wet_LEVEL_and_independent_POINT_LINEAR_PAN_lab_received","original_selected_tub_flange_POINT_drain_WP_bonding_approved","original_R42_thermostat_spout_incompatibility_resolved","original_PAN_full_wall_included_excluded_contract_interpretation_resolved","physical_1to1_sample_or_render_produced","current_supplier_usable_cases_Chicago_offer_and_installed_GC_bid_received","original_paid_returnable_inventory_verified","original_four_authentic_blind_critiques_complete","original_nonpro_Reviewer_GLOBAL_DONE","owner_approved","architect_approved","plumber_approved","WP_approved","tiler_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized","global_DONE"):
 assert m[k] is False,k
# Import signed executable read-only, run synthetic mathematical tests without
# creating a measured field file or writing new accepted artifacts.
spec=importlib.util.spec_from_file_location("signed_R44_shop_jig",D/"R44_FIELD_FINISHED_PIER_OBSTRUCTION_JIG.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
base=dict(survey[0]); v={
"actual_W3_FINISHED_width_in":"30.48","actual_W3_FINISHED_height_in":"93",
"niche_actual_center_X_in":"15.24","niche_authorized_opening_width_in":"24",
"niche_authorized_opening_height_in":"12","niche_actual_sill_bottom_Z_in":"40",
"niche_depth_actual_pipe_free_in":"4","actual_tile_calibrated_LONG_in":"10",
"actual_tile_calibrated_SHORT_in":"2","approved_grout_joint_in":"0.125",
"actual_LEFT_profile_projection_in":"0","actual_RIGHT_profile_projection_in":"0",
"installer_each_side_execution_tolerance_in":"0","actual_valve_to_FINISHED_wall_depth_in":"2.5",
"actual_backer_membrane_compressed_mortar_tile_THICKNESS_mm":"22",
"actual_W3_service_glass_pipe_exclusion_X_intervals":"NONE"}
base.update(v)
a=mod.check(base)
assert a["status"]=="GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE" and not a["purchase_authorized"]
eq(a["finished_left_pier"],3.24);eq(a["finished_right_pier"],3.24)
base["actual_LEFT_profile_projection_in"]="0.25";base["actual_RIGHT_profile_projection_in"]="0.25"
b=mod.check(base);assert b["status"]=="REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION" and not b["purchase_authorized"]
eq(b["finished_left_pier"],2.99)
base["niche_authorized_opening_width_in"]="16"
c=mod.check(base);assert c["status"]=="GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE"
eq(c["finished_left_pier"],6.99)
base["actual_W3_service_glass_pipe_exclusion_X_intervals"]="10:20"
d=mod.check(base);assert d["status"]=="REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION" and d["blocked_by_real_pipe_glass"]
base["actual_W3_service_glass_pipe_exclusion_X_intervals"]=""
assert mod.check(base)["status"]=="HOLD_MISSING_PHYSICAL_OBSTRUCTION_SURVEY"
base["actual_W3_service_glass_pipe_exclusion_X_intervals"]="NONE"
base["actual_W3_FINISHED_width_in"]=""
assert mod.check(base)["status"]=="HOLD_MISSING_ACTUAL_SURVEY"
print("PASS R44 FULL strict independent READ-ONLY 23/23 SHA+bytes, original R43/R44 preliminary/R42/R41 lineage")
print("PASS signed executable jig six synthetic HOLD/PASS/REJECT/OBSTRUCTION cases, no fabricated field measurement or purchase")
print("PASS 8 empty physical survey, 16 W1W2W3 corner datums, 80 physical inspection stages, 4 SVG shop, 24 owner tiers")
print("PASS 32 quote scope, 36 exclusive TUB/WALKIN PAN, 13 rooms/26 physical/27 original/104 trades, all FALSE")
print("R44_FULL_MANIFEST_SHA",SHA)
