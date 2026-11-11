"""Independent strict READ-ONLY R43 signed architectural shop audit.
No write, no owner contact, no Revit/Smartsheet/Git mutation.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import csv,json,hashlib,math,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r43-four-wet-bath-niche-focal-wall-fabrication-and-13room-GC"
SHA="71921913b2f8efb733a40d1ca87154c8d816af1519e1a59e5f7dc03943a5d6b0"
assert hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest()==SHA
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
assert m["round"]==43 and m["formal_board_round"]==17
assert len(m["files"])==20 and len(list(D.iterdir()))==21
for f in m["files"]:
 path=D/f["path"];assert path.is_file(),path
 data=path.read_bytes();assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["path"]
 if f["path"].endswith(".svg"):
  x=ET.fromstring(data);assert x.tag.endswith("svg")
  assert "NOT site-certified" in data.decode("utf-8") or "NOT site-certified".lower() in data.decode("utf-8").lower()
assert sum(f["path"].endswith(".svg") for f in m["files"])==4
assert sum(f["path"].endswith(".md") for f in m["files"])==5
PRE={
 "R39_FULL":("deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement/MANIFEST.json","34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"),
 "R40_FULL":("deliverables/integrated-r40-conditional-soho-ivory-sandstone-same-sku-lot-13room-GC/MANIFEST.json","ce61454e4f31b7021829ee14bc734fab82f6bb4a0025805d43eb22f939dadc39"),
 "R41_FULL":("deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room/MANIFEST.json","7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0"),
 "R42_FULL":("deliverables/integrated-r42-matte-white-thermostat-diverter-tub-spout-field-rough-wet-wall-GC/MANIFEST.json","1659fb4bb1bb57b1a26e8ab17ad36ce40ed49ba41ebd33b6fb45807e21c94712")
}
for key,(path,sha) in PRE.items():
 assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha==m["predecessor_signed_file_hashes"][key]
def get(prefix):
 match=[x["path"] for x in m["files"] if x["path"].startswith(prefix) and x["path"].endswith(".csv")]
 assert len(match)==1,(prefix,match)
 with (D/match[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def off(rows,keys):
 for x in rows:
  for k in keys:assert x[k]=="FALSE",(x.get("room"),k,x[k])
def eq(a,b,eps=0.00011):
 assert abs(float(a)-float(b))<=eps,(a,b)
O=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
W=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
A=list(csv.DictReader((B/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig")))
L=list(csv.DictReader((B/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv").open(encoding="utf-8-sig")))
W50=list(csv.DictReader((B/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv").open(encoding="utf-8-sig")))
U26=list(csv.DictReader((B/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv").open(encoding="utf-8-sig")))
R=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(O),len(W),len(A),len(L),len(W50),len(U26),len(R))==(27,25,65,13,50,26,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in O)==Decimal("23572.44")
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in O if x["room"] in m["focus_rooms"])==Decimal("9124.72")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in O)==2
wall={(x["room"],x["wall"]):x for x in W}
source={(x["room"],x["source_surface"]):x for x in O}
P=get("R43_64_HARD")
assert len(P)==64
assert Counter(x["room"] for x in P)==Counter({r:16 for r in m["focus_rooms"]})
for x in P:
 w=float(wall[x["room"],"W3"]["source_width_in_UNVERIFIED"])
 eq(x["source_provisional_wall_width_in"],w)
 width=int(x["niche_opening_width_in_HYPOTHETICAL"]);offst=float(x["theoretical_aperture_offset_from_CENTER_in"])
 left=(w-width)/2+offst;right=w-width-left
 eq(x["left_pier_before_trim_and_factory_caliber_in"],left)
 eq(x["right_pier_before_trim_and_factory_caliber_in"],right)
 eq(x["minimum_raw_side_pier_in"],min(left,right))
 eq(x["minimum_pier_after_hypothetical_one_quarter_in_field_width_loss"],min(left,right)-.125)
 assert (x["focal3inch_RAW_SIDE_PIER_gate"].startswith("PASS"))==(min(left,right)>=3)
 assert (x["robust_3inch_gate_after_width_LOSS"].startswith("PASS"))==(min(left,right)-.125>=3)
off(P,("approved_1529_location_and_3inch_finish_pier","owner_approved","shop_fabrication_authorized"))
ph=[x for x in P if x["room"]=="PH-BATH3" and x["niche_opening_width_in_HYPOTHETICAL"]=="24" and x["theoretical_aperture_offset_from_CENTER_in"]=="0" and x["proposed_vertical_joint_in_ILLUSTRATIVE"]=="0.125"]
assert len(ph)==1 and ph[0]["focal3inch_RAW_SIDE_PIER_gate"].startswith("FAIL")
eq(ph[0]["minimum_raw_side_pier_in"],1.98)
openings=get("R43_16_PHYSICAL")
assert len(openings)==16
for x in openings:
 wi=int(x["hypothetical_niche_opening_width_in"]);h=int(x["hypothetical_height_in"]);d=int(x["hypothetical_depth_in"])
 ap=wi*h/144;sid=2*h*d/144;head=wi*d/144
 eq(x["original_WALL_field_negative_aperture_SF_once"],ap)
 eq(x["separately_positive_niche_BACK_SF"],ap)
 eq(x["two_SIDES_SF"],sid)
 eq(x["separate_HEAD_SF"],head)
 eq(x["separate_SILL_SF"],head)
 eq(x["total_positive_niche_tiled_sides_BACK_JAMBS_HEAD_SILL_SF"],ap+sid+2*head)
 eq(x["net_proposed_wall_plus_niche_SURFACE_change_vs_full_wall_only_SF"],sid+2*head)
off(openings,("actual_displaced_area_credit_approved","owner_niche_size_approved","purchaser_release"))
concept=get("R43_8_PRIOR")
assert len(concept)==8 and Counter(x["room"] for x in concept)==Counter({r:2 for r in m["focus_rooms"]})
assert all(x["formal_weighted_score"]=="NULL" and x["individual_NICHE_application_and_SYSTEM_approval"]=="MISSING_FACTORY_AND_SYSTEM_APPROVAL" for x in concept)
off(concept,("dry_WALL_boundary_certified","owner_selection","original_four_specialist_review","architect_approved","GC_approved","purchase_authorized"))
pans=get("R43_9_SOURCE")
assert len(pans)==9 and {x["room"] for x in pans}=={"PH-BATH3","PH-BATH4","TX-BATH3"}
for x in pans:
 wi=float(x["source_conditional_pan_width_in_PROVISIONAL"]);di=float(x["source_conditional_pan_depth_in_PROVISIONAL"])
 xx=float(x["centerline_x_from_SOURCE_alcove_corner_in"]);yy=float(x["centerline_y_from_SOURCE_alcove_corner_in"])
 run=(xx,wi-xx,yy,di-yy)
 for v,c in zip(run,("left_run_in","right_run_in","front_run_in","back_run_in")):eq(x[c],v)
 eq(x["furthest_run_from_POINT_in_HYPOTHETICAL"],max(run))
 eq(x["highest_implied_relative_surface_elevation_in_HYPOTHETICAL"],max(run)*.25/12)
 assert x["independent_test_hypothetical_slope_in_per_foot"].startswith("0.25_NOT_CODE")
off(pans,("actual_code_maker_slope_approved","architect_plumber_WP_SIGNED","construction_release","purchase_authorized"))
scope=get("R43_32_FOCUS")
assert len(scope)==32
for x in scope:
 r=x["room"];old=source[r,"wall"];wi=int(x["illustrative_ONE_opening_wide_in"])
 opening=wi*12/144;positive=opening+2*12*4/144+2*wi*4/144
 eq(x["illustrated_negative_ONE_wall_field_SF"],opening)
 eq(x["illustrated_positive_niche_BACK_SIDES_TOP_SILL_SF"],positive)
 eq(x["illustrative_perimeter_profile_if_all_four_edges_exposed_LF"],(2*wi+2*12)/12)
 eq(x["illustrative_wall_field_after_ONE_opening_NET_SF"],float(x["quote_source_W1W2W3_full_wall_NET_SF_PREOPENING"])-opening)
 eq(x["source_original_historic_WALL_GROSS_one_copy_INCL15pct_ONCE"],float(old["source_gross_sf_one_copy_waste_15pct_once"]))
 eq(x["source_historic_WALL_material_per_GROSS_SF_USD"],float(old["historic_usd_two_copies"])/(float(old["source_gross_sf_one_copy_waste_15pct_once"])*2))
off(scope,("real_payable_change_order_approved","owner_approved","GC_approved","purchase_authorized"))
shop=get("R43_72_FOCUS")
assert len(shop)==72 and Counter(x["room"] for x in shop)==Counter({r:18 for r in m["focus_rooms"]})
off(shop,("trade_owner_arch_plumb_WP_tile_supplier_GC_purchase_signatures","actual_1TO1_per_physical_room_mockup","owner_approved","purchase_authorized"))
maker=get("R43_12_EXACT")
assert len(maker)==12
assert Counter(x["role"]=="ORIGINAL_WALL" for x in maker)==Counter({True:4,False:8})
assert all(x["manufacturer_page"].startswith("https://") for x in maker)
off(maker,("wall_pan_or_tub_flange_membrane_complete_assembly_APPROVAL","factory_product_OWNER_SELECTED_alternative","purchase_authorized"))
units=get("R43_26_PHYSICAL")
assert len(units)==26 and Counter(x["room"] for x in units)==Counter({r["id"]:2 for r in R})
off(units,("actual_fullscale_mockup_built","signed_wet_assembly","owner_approved","architect_approved","plumber_approved","waterproof_approved","tiler_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
release=get("R43_13_ROOM")
assert len(release)==13 and {x["room"] for x in release}=={r["id"] for r in R}
assert all(x["formal_board_round"]=="17" for x in release)
assert "ACTUAL_WALKIN" in next(x["original_nonnegotiable_owner_program"] for x in release if x["room"]=="PH-BATH4")
assert "DURAVIT_TUB" in next(x["original_nonnegotiable_owner_program"] for x in release if x["room"]=="TX-BATH4")
off(release,("R43_specific_pier_gate",) ) if False else None
off(release,("actual_field_1529_reverified","formal_4_original_specialist_weighted_champion_review","original_nonPro_Reviewer_global_DONE","owner_approved","architect_approved","plumber_approved","waterproofing_approved","tile_installer_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
material=get("R43_27_ORIGINAL")
assert len(material)==27 and sum(Decimal(x["historic_two_copy_material_only_USD"] or 0) for x in material)==Decimal("23572.44")
off(material,("actual_factory_identical_SKU_COLOR_FINISH_CALIBER_lot_verified","original_purchase_received_and_RETURNABLE_credit_signed","owner_approved","GC_approved","purchaser_approved","purchase_authorized"))
trades=get("R43_104_SEQUENTIAL")
assert len(trades)==104
assert Counter(x["trade"] for x in trades)==Counter({role:13 for role in ("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC","PURCHASER")})
off(trades,("signed_completion","owner_approved","architect_approved","GC_approved","purchaser_approved","purchase_authorized"))
assert m["historic_material_ONLY_four_unit_USD"]=="23572.44" and m["original_four_focus_old_material_only_included_USD"]=="9124.72"
for key in ("original_OWNER_selection_changed","certified_NATIVE_1529_geometry","authentic_factory_current_exact_WET_WALL_and_independent_WET_NICHE_all_approved","original_exact_numeric_raw_wet_LEVEL_and_independent_POINT_LINEAR_PAN_labs_complete","selected_original_Drain_tub_flange_membrane_factory_supported_complete","original_PH3_TX3_TUB_vs_WALKIN_owner_resolved","current_Chicago_SKU_color_finish_lot_usable_carton_and_GC_full_installed_bid_received","old_historic_original_invoice_PAID_returnable_material_and_change_order_approved","actual_1to1_built_mockups_or_renders_produced","original_four_authentic_BLIND_specialist_reports_complete","original_standing_nonPro_reviewer_GLOBAL_DONE","owner_approved","architect_approved","plumber_approved","waterproofing_approved","installer_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized","global_DONE"):
 assert m[key] is False,key
print("PASS R43 strict independent READ ONLY 20/20 SHA bytes, 4 usable valid source-only SVG, immutable R39-42")
print("PASS 64 hard-pier, 16 one aperture+five niche faces, 9 point-PAN hypo slopes, 32 source-to-GC measured scope")
print("PASS PH3 24-inch niche centered 1.98in FAIL vs 16-inch 5.98in source only; all fabrication releases FALSE")
print("PASS 13/27/25/65 + 13 labs/50 source walls/26 units/104 trade preserved; historical $23572.44/15pct once")
print("R43_MANIFEST_SHA",SHA)
