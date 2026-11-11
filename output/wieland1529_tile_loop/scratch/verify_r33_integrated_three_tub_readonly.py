"""Strict independent READ ONLY R33 signed material, maker and arithmetic postcheck."""
from __future__ import annotations
import hashlib,csv,json,math
from decimal import Decimal
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parents[1]
O=P/"deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC"
M=O/"MANIFEST.json"
sha=hashlib.sha256(M.read_bytes()).hexdigest()
assert sha=="a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"
m=json.loads(M.read_text(encoding="utf-8"))
assert len(m["files"])==23 and len(list(O.iterdir()))==24
for f in m["files"]:
    data=(O/f["relative_path"]).read_bytes()
    assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["relative_path"]
def rows(prefix):
    fs=[f["relative_path"] for f in m["files"] if f["relative_path"].startswith(prefix) and f["relative_path"].endswith(".csv")]
    assert len(fs)==1,(prefix,fs)
    with (O/fs[0]).open(encoding="utf-8-sig",newline="") as ff:return list(csv.DictReader(ff))
for i in range(12,30):
    dirs=[x for x in (P/"deliverables").glob(f"integrated-r{i}*")
          if x.name!="integrated-r17-numeric-product-leads" and (x/"MANIFEST.json").exists()]
    assert len(dirs)==1
    ref=f"R{i:03d}_INTEGRATED_MANIFEST_SHA256"
    assert hashlib.sha256((dirs[0]/"MANIFEST.json").read_bytes()).hexdigest()==m["immutable_predecessor_SHA256"][ref]
source={
  "R30":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
  "R31_SOURCE":("state/ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json","61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"),
  "R31_FULL":("deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/MANIFEST.json","b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457"),
  "R32_SOURCE":("state/ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json","9ad8564e2676f4e72533e6830bea627757e393dc1cdc537b297d443caae962b4"),
}
for k,(path,expected) in source.items():
    assert hashlib.sha256((P/path).read_bytes()).hexdigest()==expected==m["immutable_predecessor_SHA256"][k+"_SHA256"]
for n in ("ROUND014_SUBMISSION","ROUND017_SUBMISSION"):
    assert hashlib.sha256((P/"state"/(n+".json")).read_bytes()).hexdigest()==m["immutable_predecessor_SHA256"][n+"_SHA256"]
original=list(csv.DictReader((P/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(original)==27
assert sum(Decimal(x["historic_usd_two_copies"] or 0) for x in original)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in original)==2
old_byid={x["source_row_id"]:x for x in original}
old_W=list(csv.DictReader((P/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
assert len(old_W)==25
old_actions=list(csv.DictReader((P/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
assert len(old_actions)==65
room_src=json.loads((P/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
room_ids={x["id"] for x in room_src}
assert len(room_ids)==13 and len(room_src)==13
def N(x):return float(x)

maker=rows("R33_12_FACTORY")
assert len(maker)==12
assert any(x["exact_model_or_source_code"]=="72411701" and "pressure-balance" in x["hard_factory_or_scope_gate"].lower() for x in maker)
assert any(x["exact_model_or_source_code"]=="27458003" and "not a mixing" in x["hard_factory_or_scope_gate"].lower() for x in maker)
assert all(x["purchase_authorized"]==x["owner_substitution_approved"]=="FALSE" for x in maker)
options=rows("R33_9_THREE_TUB_GOOD")
assert len(options)==9 and Counter(x["room"] for x in options)==Counter({"PH-BATH2":3,"TX-BATH2":3,"TX-BATH4":3})
assert {x["tier"] for x in options}=={"GOOD","BETTER","BEST"}
assert all(x["tiled_shower_PAN"]=="N_A" and x["owner_approved"]==x["purchase_authorized"]=="FALSE" and x["weighted_board_score"]=="NULL" for x in options)
assert all(x["selected_finish"]=="CHROME" for x in options if x["room"]=="TX-BATH2")
assert all(x["selected_finish"]=="MATTE_WHITE" for x in options if x["room"]!="TX-BATH2")
ports=rows("R33_54_PHYSICAL")
assert len(ports)==54
assert Counter(x["endpoint"] for x in ports)==Counter({"TUB_FILL":18,"OVERHEAD_SHOWER":18,"HAND_SHOWER":18})
assert len({(x["room"],x["physical_source_room"],x["tier"],x["endpoint"]) for x in ports})==54
assert all(x["factory_certified_hot_cold_mixer_and_distribution_port"]=="UNASSIGNED" and x["purchase_authorized"]=="FALSE" for x in ports)
assert all("MISSING_SOURCE_SPOUT" in x["actual_selected_endpoint_part_or_missing"] for x in ports if x["room"]=="TX-BATH2" and x["endpoint"]=="TUB_FILL")

walls=rows("R33_3_TUB")
assert len(walls)==3
oldwall={(x["room"],x["wall"]):x for x in old_W}
oldmat={(x["room"],x["source_surface"]):x for x in original}
for x in walls:
    r=x["room"]
    widths=[N(oldwall[r,w]["source_width_in_UNVERIFIED"]) for w in ("W1","W2","W3")]
    height=N(oldwall[r,"W1"]["source_tiled_height_in_UNVERIFIED"])
    assert abs(sum(widths)*height/144-N(x["unverified_full_3wall_FIELD_NET_SF_per_copy_before_openings"]))<.00011
    assert abs(sum(widths)*height/144*1.15-N(x["theoretical_source_full_3wall_NET_times_original_15pct_once_SF_per_copy"]))<.00011
    rate=Decimal(oldmat[r,"wall"]["historic_usd_two_copies"])/Decimal(oldmat[r,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])/2
    assert abs(float(rate)-N(x["historic_wall_rate_per_GROSS_SF_only_USD"]))<.00011
    assert x["owner_approved"]==x["purchase_authorized"]=="FALSE"
layout=rows("R33_36_SOURCE")
assert len(layout)==36
assert len({(x["room"],x["wall"],x["selected_candidate_module"],x["joint_width_in_ILLUSTRATIVE"]) for x in layout})==36
for x in layout:
    w=N(x["source_wall_span_in_UNVERIFIED"])
    T=N(x["long_axis_nominal_tile_in"])
    j=N(x["joint_width_in_ILLUSTRATIVE"])
    n=int(x["central_full_tiles"])
    if x["alignment"]=="BALANCED" and n>0:
        expected=(w-n*T-(n+1)*j)/2
        assert abs(expected-N(x["left_visible_end_piece_in"]))<.00011
        assert abs(expected-N(x["right_visible_end_piece_in"]))<.00011
        assert x["minimum3in_focal_gate"]==("PASS_FOCAL_BALANCED" if 3<=expected<=T else "FAIL_NEGATIVE_OR_UNDER_3IN_FOCAL")
assert any(x["room"]=="TX-BATH2" and x["wall"]=="W1" and x["central_full_tiles"]=="3" and x["minimum3in_focal_gate"].startswith("FAIL") for x in layout)
shops=rows("R33_18_SIX_TUB_REAL")
assert len(shops)==18 and len({(x["room"],x["physical_source_room"],x["wall"]) for x in shops})==18
fit=rows("R33_36_SIX_UNIT")
assert len(fit)==36
for x in fit:
    theoretical=N(x["original_W1_source_in_UNVERIFIED"])+N(x["hypothetical_actual_FIELD_delta_in"])-2*N(x["hypothetical_end_wall_BUILDUP_each_in"])
    assert abs(theoretical-N(x["hypothetical_59in_tub_insert_AFTER_FINISH_clear_in"]))<.00011
    assert abs(theoretical-59-N(x["source_minus_factory_tub_body_in"]))<.00011
plane=rows("R33_36_TUB_MIXER")
assert len(plane)==36
for x in plane:
    p=sum(N(x[k]) for k in ("hypothetical_backer_in","hypothetical_mortar_COMPRESSED_in","hypothetical_tile_BODY_in"))
    assert abs(p-N(x["partial_total_EXCLUDING_MEMBRANE_gasket_and_frustrated_tub_flange_in"]))<.00011
    assert x["onsite_mockup_witness"]==x["purchase_authorized"]=="FALSE"
niches=rows("R33_6_SYNTHETIC")
assert len(niches)==6
for x in niches:
    assert abs(N(x["single_wall_FIELD_aperture_SF_Deduct_once"])-16*12/144)<.00011
    actual=N(x["independent_niche_BACK_SF"])+N(x["both_SIDE_SF"])+N(x["TOP_SF"])+N(x["SILL_SF"])
    assert abs(actual-N(x["sample_niche_NET_tile_surface_SF_before_new_waste"]))<.00011
rate=rows("R33_27_THREE_TUB")
assert len(rate)==27
assert all(x["credit_claim_payable"]==x["purchase_authorized"]=="FALSE" for x in rate)
for x in rate:
    h=N(oldwall[x["room"],"W1"]["source_tiled_height_in_UNVERIFIED"])
    n=(N(x["source_W1_shift_in_PER_PHYSICAL_COPY"])+2*N(x["source_W2_and_W3_each_shift_in_PER_PHYSICAL_COPY"]))*h/144*2
    assert abs(n-N(x["theoretical_two_copy_WALL_NET_DELTA_SF"]))<.00011
cartons=rows("R33_12_THEORETICAL")
assert len(cartons)==12 and all(x["purchase_authorized"]=="FALSE" and x["real_carton_saving_credit"]=="FALSE" for x in cartons)
assert all(int(x["independent_unit_ceiled_cases"])>=int(x["pooled_same_room_exact_SKU_lot_if_verified_cases"]) for x in cartons)
lab=rows("R33_13_ORIGINAL")
assert len(lab)==13 and Counter(x["surface_role"] for x in lab)==Counter({
  "LEVEL":8,"LINEAR_SLOPED_PAN":2,"POINT_FOUR_PLANE_SLOPED_PAN":1,"CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN":2})
assert all(x["original_raw_measured_wet_DCOF_numeric"]=="" and x["purchase_authorized"]=="FALSE" for x in lab)
assert not any(x["room"] in ("PH-BATH2","TX-BATH2","TX-BATH4") and x["surface_role"]!="LEVEL" for x in lab)
wet=rows("R33_9_THREE_TUB_DISTINCT")
assert len(wet)==9 and all(x["selected_tub_no_tiled_PAN"]==x["purchase_authorized"]=="FALSE" or x["selected_tub_no_tiled_PAN"]=="TRUE" and x["purchase_authorized"]=="FALSE" for x in wet)
hold=rows("R33_48_SIX")
assert len(hold)==48 and Counter(x["hold_point"] for x in hold)==Counter({x:6 for x in set(x["hold_point"] for x in hold)})
assert all(x["actual_field_work_complete"]==x["purchase_authorized"]=="FALSE" for x in hold)
units=rows("R33_26_EXISTING")
assert len(units)==26 and len({(x["room"],x["physical_copy_index"]) for x in units})==26
assert all(x["purchase_authorized"]=="FALSE" for x in units)
W50=rows("R33_50_ORIGINAL")
assert len(W50)==50 and len({(x["room"],x["source_copy"],x["wall"]) for x in W50})==50
assert all(x["purchase_authorized"]=="FALSE" for x in W50)
mat=rows("R33_27_ORIGINAL")
assert len(mat)==27 and {x["original_source_row_id"] for x in mat}==set(old_byid)
assert sum(Decimal(x["historic_two_copy_material_ONLY_USD"]) for x in mat)==Decimal("23572.44")
assert sum(x["original_unpriced_Primary_niche_excluded_NO_ORDER"]=="TRUE" for x in mat)==2
assert all(x["owner_signed"]==x["supplier_signed"]==x["purchase_authorized"]=="FALSE" for x in mat)
release=rows("R33_13_ROOM")
assert len(release)==13 and {x["room"] for x in release}==room_ids
assert all(x["purchase_authorized"]==x["purchaser_material_reservation"]=="FALSE" and x["weighted_BOARD_scores"]=="NULL" for x in release)
for room in ("PH-BATH2","TX-BATH2","TX-BATH4"):
    assert release[[x["room"] for x in release].index(room)]["independent_shower_PAN_wet_lab_or_N_A"]=="N_A_TUB_WOOD_OR_INHERITED_WC"
trade=rows("R33_104_EIGHT")
assert len(trade)==104 and Counter(x["trade"] for x in trade)==Counter({a:13 for a in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")})
assert all(x["purchase_authorized"]==x["GC_release"]=="FALSE" for x in trade)
cams=rows("R33_18_PHYSICAL_TUB_SOURCE_CORRECT")
assert len(cams)==18 and all(x["actual_image_created"]==x["actual_mockup_built"]==x["purchase_authorized"]=="FALSE" for x in cams)
for flag in ("exact_1529_native_model_or_site_geometry_verified","original_exact_raw_numeric_wet_LEVEL_and_PAN_labs_received",
             "current_chicago_factory_case_lot_freight_ETA_installed_GC_bid_known","original_four_critic_reports_complete",
             "independent_nonpro_reviewer_accepted","owner_approved","purchase_authorized","global_13room_DONE"):
    assert m[flag] is False,flag
assert m["weighted_board_score"] is None
print("PASS R33 local READ ONLY: 23/23 payload SHA+bytes, R12-R29 18 ancestors and four R30/R31/R32 predecessor hashes exact")
print("PASS R33 13/27/25/65 original, $23572.44 material-only and old 15pct once, 13 raw wet surface roles no fabricated reports")
print("PASS R33 54 hydraulic ports, 36 focal cuts, 36 six-unit clearances, 36 finish planes, 27 cost sensitivities, 18 physical tub walls, 48 holds")
print("PASS R33 26 copies +50 W +13 rooms +104 eight trade +18 unmade mockups, zero owner/GC/PO/releases")
print("R33_FINAL_MANIFEST_SHA",sha)
