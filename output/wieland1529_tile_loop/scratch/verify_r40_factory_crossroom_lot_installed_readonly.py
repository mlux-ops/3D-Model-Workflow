"""Strict independent read-only R40 conditional maker same-lot procurement QA."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib,json,csv,math
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r40-conditional-soho-ivory-sandstone-same-sku-lot-13room-GC"
SHA="ce61454e4f31b7021829ee14bc734fab82f6bb4a0025805d43eb22f939dadc39"
P=D/"MANIFEST.json"
assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
m=json.loads(P.read_text(encoding="utf-8"))
assert m["round"]==40 and len(m["files"])==9 and len(list(D.iterdir()))==10
for f in m["files"]:
 data=(D/f["path"]).read_bytes()
 assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["path"]
R39=B/"deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement/MANIFEST.json"
assert hashlib.sha256(R39.read_bytes()).hexdigest()==m["predecessor_signed_file_hashes"]["R39_FULL"]=="34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"
R30=B/"deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json"
assert hashlib.sha256(R30.read_bytes()).hexdigest()==m["predecessor_signed_file_hashes"]["R30_FULL"]
src=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(src)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in src)==Decimal("23572.44")
def rows(prefix):
 x=[f["path"] for f in m["files"] if f["path"].startswith(prefix) and f["path"].endswith(".csv")]
 assert len(x)==1,(prefix,x)
 with (D/x[0]).open(encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def neg(r,cols):
 for x in r:
  for k in cols:assert x[k]=="FALSE",(x.get("room"),k,x[k])
soho=rows("R40_6_REAL")
sand=rows("R40_10_REAL")
case=rows("R40_6_SAME")
quot=rows("R40_2_CROSS")
sections=rows("R40_18_SIX")
exclude=rows("R40_8_MATERIAL")
rfq=rows("R40_8_CORRECTED")
release=rows("R40_13_ROOM")
assert (len(soho),len(sand),len(case),len(quot),len(sections),len(exclude),len(rfq),len(release))==(6,10,6,2,18,8,8,13)
assert Counter((x["room"],x["original_source_surface"]) for x in soho)==Counter({("PH-BATH4","wall"):2,("PH-BATH4","accent"):2,("TX-BATH4","accent"):2})
assert sum(Decimal(x["quoted_old_historic_GROSS_SF_includes15pct_ONCE"]) for x in soho)==Decimal("248.92")
assert sum(Decimal(x["source_quoted_gross_15pct_ONCE"]) for x in sand)==Decimal("224.04")
assert Counter(x["receiver"] for x in sand)==Counter({"EXISTING_HISTORICAL_NICHE":8,"OWNER_OPTION_NEW_WET_WALL_NOT_SELECTED":2})
assert all(x["room"] in ("PH-BATH4","TX-BATH4") for x in soho)
assert all(x["room"] in ("PH-BATH2","PH-BATH3","TX-BATH2","TX-BATH3") for x in sand)
neg(soho,("owner_approved","supplier_signed","GC_signed","purchase_authorized"))
neg(sand,("owner_conditional_new_wall_selection","factory_exact_SKU_color_finish_caliber_lot_same_with_all_others","purchase_authorized"))
for x in case:
 group=x["conditional_group"]
 values=[float(y["quoted_old_historic_GROSS_SF_includes15pct_ONCE"]) for y in soho] if group=="SOHO_IVORY" else [float(y["source_quoted_gross_15pct_ONCE"]) for y in sand]
 qty=float(x["hypothetical_future_case_usable_coverage_SF_NOT_REAL"])
 assert int(x["source_original_receivers"])==len(values)
 assert abs(float(x["originally_quoted_historical_GROSS_SF_sum_15pct_ONCE"])-sum(values))<.00011
 assert int(x["hypothetical_individually_rounded_SOURCE_receiver_case_count"])==sum(math.ceil(v/qty) for v in values)
 assert int(x["hypothetical_one_identical_SKU_same_lot_pool_case_count"])==math.ceil(sum(values)/qty)
 assert int(x["hypothetical_case_difference_NOT_REAL_SAVING"])==sum(math.ceil(v/qty) for v in values)-math.ceil(sum(values)/qty)
neg(case,("owner_selects_ONE_exact_product_for_all_relevant_surfaces","actual_calibrated_same_SHAPE_size_color_finish_lot_verified","factory_current_usable_case_SF_current_Chicago_offer_verified","signed_actual_1529_NET_and_trim_or_site_cutstock_verified","original_material_quote_ALTERATION_signed","purchase_authorized"))
assert {x["historical_original_material_ONLY_subscope_in_full_four_unit_USD"] for x in quot}=={"2743.44","1557.10"}
neg(quot,("actual_OWNER_selected_alternative_and_credit_offset_signed","actual_1529_net_actual_same_lot_case_receipt","actual_change_order_payable_or_real_savings","supplier_approved","GC_approved","purchase_authorized"))
assert Counter(x["room"] for x in sections)==Counter({"PH-BATH4":12,"TX-BATH4":6})
assert all("TX4_DURAVIT_TUB" in x["selected_fixture_preserved"] for x in sections if x["room"]=="TX-BATH4")
assert all("PH4_ACTUAL_WALKIN" in x["selected_fixture_preserved"] for x in sections if x["room"]=="PH-BATH4")
neg(sections,("actual_signed_1to1_wall_niche_edge_mockup","owner_approved","WP_tiler_plumber_signed","purchase_authorized"))
assert all("FALSE"==x["may_pool_against_SOHO_IVORY"] for x in exclude)
neg(exclude,("factory_same_SKU_color_finish_CALIBER_lot_compatible","may_pool_against_SOHO_IVORY","may_borrow_other_item_individual_wet_WALL_NICHE_approval","may_transfer_different_SOURCE_original_NUMERIC_wet_DCOF","actual_owner_substitution_signed","purchase_authorized"))
assert len({(x["room"],x["surface"]) for x in rfq})==8
neg(rfq,("current_factory_selected_SKU_color_finish_lot_approved","approved_same_exact_factory_product_for_wet_WALL_and_NICHE","owner_signed","architect_signed","plumber_signed","WP_tile_signed","supplier_signed","GC_signed","purchaser_signed","purchase_authorized"))
ids={x["id"] for x in json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
assert {x["room"] for x in release}==ids
assert all(x["original_formal_round_017_unchanged"]=="TRUE" for x in release)
neg(release,("actual_individual_SKU_color_finish_WET_WALL_vs_WET_NICHE_app_approved","owner_approved","architect_approved","plumber_approved","waterproof_trade_approved","tile_installer_approved","supplier_approved","GC_approved","purchaser_approved","original_4_SPECIALIST_board_scored","current_nonpro_Reviewer_DONE","purchase_authorized"))
for k in ("original_4_specialist_complete","nonpro_reviewer_DONE","actual_true_1529_native_site_survey","original_exact_raw_wet_LEVEL_PAN_labs_received","owner_conditional_materials_selected","manufacturer_exact_WET_NICHE_WP_system_approved","original_paid_inventory_and_credit_verified","current_factory_exact_SHADE_LOT_current_case_Chicago_quote","current_installed_GC_change_order_signed","supplier_materials_reserved","owner_approved","GC_approved","purchase_authorized","global_DONE"):
 assert m[k] is False,k
assert m["six_SOHO_IVORY_original_receivers_gross_SF_historical_once"]=="248.92" and m["ten_SANDSTONE_existing_niche_plus_unselected_new_wall_gross_SF_historical_once"]=="224.04"
print("PASS R40 STRICT READ ONLY 9/9 SHA+bytes immutable R39 full and predecessor signatures")
print("PASS R40 6 Soho PH4/TX4 248.92 gross and 10 Sandstone old niches+new PH3 wall 224.04 gross")
print("PASS R40 6 fictional case ceilings, 18 separate shower vs tub factory shop, 8 RFQ, 13 room all FALSE")
print("PASS historic 27/$23572.44 old15pct once, source identities, no current supplier lot/savings/owner choice")
print("R40_MANIFEST_SHA",SHA)
