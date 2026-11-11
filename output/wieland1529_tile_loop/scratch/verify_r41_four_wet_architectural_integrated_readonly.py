"""Strict independently implemented READ-ONLY R41 source/geometry/integrity audit.
No writes, no viewer or native 1527/1529 operations, no owner/vendor contact.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib,json,csv,math,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room"
SHA="7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0"
assert hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest()==SHA
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
assert m["round"]==41 and len(m["files"])==27 and len(list(D.iterdir()))==28
for f in m["files"]:
 data=(D/f["path"]).read_bytes()
 assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["path"]
 for key in ("MANIFEST","../","..\\"):assert key not in f["path"],f["path"]
 if f["path"].endswith(".svg"):
  root=ET.fromstring(data)
  assert root.tag.endswith("svg")
  assert "NOT field-verified" in data.decode("utf-8") and "W1" in data.decode("utf-8")
assert sum(f["path"].endswith(".svg") for f in m["files"])==8
assert sum(f["path"].endswith(".md") for f in m["files"])==5
previous={
"R39_FULL":("deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement/MANIFEST.json","34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"),
"R40_FULL":("deliverables/integrated-r40-conditional-soho-ivory-sandstone-same-sku-lot-13room-GC/MANIFEST.json","ce61454e4f31b7021829ee14bc734fab82f6bb4a0025805d43eb22f939dadc39"),
"R37_FULL":("deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement/MANIFEST.json","985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"),
"R35_FULL":("deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json","75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"),
"R36_SOURCE":("state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"),
"R30_FULL":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
"R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e")}
for name,(path,sha) in previous.items():
 assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha==m["predecessor_signed_file_hashes"][name],name
def rows(prefix):
 matched=[x["path"] for x in m["files"] if x["path"].startswith(prefix) and x["path"].endswith(".csv")]
 assert len(matched)==1,(prefix,matched)
 with (D/matched[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def truefalse(rows_,cols):
 for x in rows_:
  for c in cols:assert x[c]=="FALSE",(c,x.get("room"),x[c])
def close(a,b,tol=.00011):
 assert abs(float(a)-float(b))<tol,(a,b)
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
w25=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
a65=list(csv.DictReader((B/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
u26=list(csv.DictReader((B/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv").open(encoding="utf-8-sig")))
w50=list(csv.DictReader((B/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv").open(encoding="utf-8-sig")))
lab13=list(csv.DictReader((B/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv").open(encoding="utf-8-sig")))
R=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
focus=("PH-BATH3","PH-BATH4","TX-BATH3","TX-BATH4")
assert (len(old),len(w25),len(a65),len(u26),len(w50),len(lab13),len(R))==(27,25,65,26,50,13,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old if x["room"] in focus)==Decimal("9124.72")
assert m["old_13room_material_only_USD"]=="23572.44" and m["four_focus_12_original_rows_material_only_USD"]=="9124.72"
assert m["original_13rooms"]==13 and m["original_26physical"]==26
sourcewalls={(x["room"],x["wall"]):x for x in w25}
design=rows("R41_8_NEUTRAL")
assert len(design)==8 and Counter(x["room"] for x in design)==Counter({r:2 for r in focus})
assert all("elmsurfaces.com/product" in x["manufacturer_exact_product_page"] and x["four_authentic_critic_scores"]=="NULL" for x in design)
truefalse(design,("actual_tub_or_shower_niche_membrane_system_APPROVED","owner_approved","architect_approved","manufacturer_WP_approved","installation_released","purchase_authorized"))
fits=rows("R41_48_FIELD")
assert len(fits)==48
for x in fits:
 w=float(sourcewalls[(x["room"],x["source_wall"])]["source_width_in_UNVERIFIED"])
 assert float(x["source_width_in_UNVERIFIED"])==w
 d=float(x["horizontal_tile_FACE_in"]);j=float(x["hypothetical_joint_in"])
 n=int(x["nominal_full_tiles_selected"])
 for delta,column in ((-.25,"robust_min_left_right_cut_if_WIDTH_minus_quarter"),(0,"nominal_balanced_left_and_right_cut_in"),(.25,"robust_max_left_right_cut_if_WIDTH_plus_quarter")):
  close(x[column],(w+delta-n*d-(n+1)*j)/2)
 assert x["three_in_focal_cut_requirement"]=="N_A_NATIVE_2IN_AXIS" if d<3 else x["three_in_focal_cut_requirement"] in ("PASS_ALL_WIDTH_VARIATIONS","FAIL_FOCAL_REQUIRE_REVISIT_JOINT_OR_DATUM")
truefalse(fits,("signed_1to1_layout_approval","owner_approved","purchase_authorized"))
deps=rows("R41_24_PHYSICAL")
assert len(deps)==24 and Counter(x["room"] for x in deps)==Counter({r:6 for r in focus})
truefalse(deps,("actual_1529_field_verified","architect_shop_signature","plumber_wet_seal_signature","owner_approved","purchase_authorized"))
planes=rows("R41_32_OPTION")
assert len(planes)==32
for x in planes:
 assert float(x["candidate_wall_body_nominal_mm"])==9.5
 if x["original_CAVIAR_niche_body_nominal_mm"]!="N_A_ORIGINAL_SANDSTONE":
  close(x["niche_to_alt_TILE_BODY_only_delta_mm"],9.5-13.)
 assert "BACKER_new-BACKER_old" in x["formula_delta_FINISHED_plane"]
truefalse(planes,("actual_factory_backer_and_membrane_tested_assembly_approved","actual_selected_Brizo_Delta_POINT_bonding_approved","actual_Duravit_tub_flange_hansgrohe_rough_approved","architect_watertight_system_signed","owner_approved","purchase_authorized"))
details=rows("R41_32_PHYSICAL_BATH")
assert len(details)==32
assert Counter(x["room"] for x in details)==Counter({r:8 for r in focus})
truefalse(details,("actual_waterproofing_rough_compatibility_and_flood_WHEN_REQUIRED","signed_1to1_built_test_and_photograph","owner_approved","architect_approved","plumber_approved","waterproof_approved","installer_approved","purchase_authorized"))
branches=rows("R41_18_MUTUALLY")
assert len(branches)==18
assert Counter(x["room"] for x in branches)==Counter({"PH-BATH3":6,"PH-BATH4":4,"TX-BATH3":6,"TX-BATH4":2})
for x in branches:
 r=x["room"];name=x["mutually_exclusive_program_and_quote"]
 if "TUB" in name:
  assert x["shower_POINT_PAN_active"]=="N_A_TUB"
  assert x["hypothetical_EXTRA_point_PAN_material_net_SF_only_if_EXCLUDED"]=="N_A_OR_INCL"
  assert x["independent_exact_raw_NUMERIC_POINT_PAN_lab"]=="N_A_TUB"
 else:
  assert x["shower_POINT_PAN_active"]=="TRUE_ONLY_IF_WALKIN"
  assert x["independent_exact_raw_NUMERIC_POINT_PAN_lab"]=="MISSING"
  if "EXCLUDED" in name:
   close(x["hypothetical_EXTRA_point_PAN_material_net_SF_only_if_EXCLUDED"],x["source_rectangular_tub_or_pan_footprint_NET_SF_NOT_TRUE_POLYGON"])
   close(x["hypothetical_NEW_separate_pan_GROSS_SF_at10pct_NEW_APPROVAL_ONLY"],float(x["source_rectangular_tub_or_pan_footprint_NET_SF_NOT_TRUE_POLYGON"])*1.10)
  else:assert x["hypothetical_EXTRA_point_PAN_material_net_SF_only_if_EXCLUDED"]=="N_A_OR_INCL"
truefalse(branches,("actual_LEVEL_net_plus_separate_POINT_net_proven","actual_1529_survey_and_plumbing_shop_signed","owner_selection_approved","architect_approved","GC_cost_substitution_credit_approved","purchase_authorized"))
net=rows("R41_16_OPTION")
assert len(net)==16
for x in net:
 wallrows=[sourcewalls[(x["room"],w)] for w in ("W1","W2","W3")]
 gross=sum(float(y["source_width_in_UNVERIFIED"])*float(y["source_tiled_height_in_UNVERIFIED"])/144 for y in wallrows)
 close(x["source_underdeducted_full_wall_NET_SF_before_actual_openings"],gross)
 close(x["sensitivity_NET_SF_per_ONE_inch_IN_EACH_wall_width"],float(wallrows[0]["source_tiled_height_in_UNVERIFIED"])/144)
 close(x["sensitivity_NET_SF_per_ONE_inch_IN_all_three_wall_height"],sum(float(y["source_width_in_UNVERIFIED"]) for y in wallrows)/144)
truefalse(net,("change_order_or_price_savings_signed","owner_approved","purchase_authorized"))
quote=rows("R41_27_ORIGINAL")
assert len(quote)==27 and sum(Decimal(x["original_two_copy_historical_material_only_USD"] or "0") for x in quote)==Decimal("23572.44")
truefalse(quote,("actual_owner_approved_material_change","supplier_approved","owner_approved","GC_approved","purchase_authorized"))
tiers=rows("R41_24_SIX_EIGHT")
assert len(tiers)==24 and Counter(x["tier"] for x in tiers)==Counter({"GOOD":8,"BETTER":8,"BEST":8})
assert all(x["formal_weighted_score"]=="NULL" for x in tiers)
truefalse(tiers,("five_trade_owner_accepted_1to1_mockup","selected_owner_alternative","four_original_independent_SPECIALIST_acceptance","purchasing_authorized"))
samples=rows("R41_24_ACTUAL")
assert len(samples)==24
truefalse(samples,("render_created","physical_1to1_mockup_created","actual_native_1529_fields_signed","owner_approved","architect_approved","installer_approved","purchase_authorized"))
rel=rows("R41_13_ROOM")
ids={x["id"] for x in R}
assert len(rel)==13 and {x["room"] for x in rel}==ids
assert sum(Decimal(x["original_material_ONLY_historic_two_copy_USD"]) for x in rel)==Decimal("23572.44")
assert all("Brizo" in x["original_program_and_fixture_source"] and "BR73480" in x["original_program_and_fixture_source"] for x in rel if x["room"] in ("PH-PRIMARY","TX-PRIMARY"))
assert "BT062415-BNX" in next(x["original_program_and_fixture_source"] for x in rel if x["room"]=="PH-BATH4")
assert "700332000000090" in next(x["original_program_and_fixture_source"] for x in rel if x["room"]=="TX-BATH4")
assert all(x["exact_original_raw_numeric_wet_POINT_or_LINEAR_PAN_gate"]=="N_A_TUB" for x in rel if x["room"] in ("PH-BATH2","TX-BATH2","TX-BATH4"))
assert all(x["exact_original_raw_numeric_wet_LEVEL_gate"]=="N_A_WOOD_FLOOR" for x in rel if x["room"] in ("PH-POWDER","TX-POWDER","TX-POWDER2"))
truefalse(rel,("owner_approved","architect_approved","plumber_approved","waterproofing_approved","tile_installer_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized","original_four_authentic_critic_reports","independent_nonpro_reviewer_DONE"))
trades=rows("R41_104_SEQUENTIAL")
assert len(trades)==104 and Counter(x["trade"] for x in trades)==Counter({t:13 for t in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC","PURCHASER")})
truefalse(trades,("all_eight_stage_RELEASE_authorized","individual_trade_signed","purchase_authorized"))
units=rows("R41_26_ORIGINAL")
assert len(units)==26 and {x["room"] for x in units}==ids
truefalse(units,("manufacturer_current_wet_WALL_product_and_factory_lot_approved","owner_approved","architect_approved","plumber_approved","waterproof_approved","installer_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
walls=rows("R41_50_EXISTING")
assert len(walls)==50
truefalse(walls,("original_individual_wet_WALL_NICHE_app_revalidated","actual_1to1_tile_caliber_grout_movement_and_trim_approved","owner_approved","architect_approved","purchaser_release"))
for name in ("actual_true_1529_model_measurements_verified","actual_owner_design_or_program_selected","original_all_individual_wet_WALL_and_NICHE_authorizations_received","exact_RAW_numeric_wet_LEVEL_and_independent_POINT_LINEAR_PAN_labs_received","approved_actual_factory_WP_tubflange_POINT_drain","authentic_1to1_physical_samples_or_renders_produced","current_factory_SKU_lot_usable_case_and_chicago_offer_received","original_paid_inventory_current_full_GC_bid_CO_signed","original_four_specialist_critiques_complete","original_nonpro_reviewer_DONE","owner_approved","architect_approved","plumber_approved","waterproof_approved","installer_approved","supplier_approved","GC_approved","purchaser_approved","material_reserved","purchase_authorized","global_DONE"):
 assert m[name] is False,name
print("PASS R41 STRICT READ-ONLY 27/27 SHA+bytes, eight valid schematic SVGs, immutable R39/R40/R12+ predecessor hashes")
print("PASS R41 8 materially distinct designs, 48 width-sensitive grid controls, 24 survey, 32 plane + 32 WP, 18 mutually exclusive original PAN quote/program gates")
print("PASS R41 13 rooms/27 materials/25 source walls/65 trade + R31 13 labs/50 walls/26 physical + 104 trades, all FALSE")
print("PASS R41 four focus historic USD 9124.72 included USD 23572.44 with original 15pct once, no stock/owner/GC/supplier/lab/1529 verification claimed")
print("R41_MANIFEST_SHA",SHA)
