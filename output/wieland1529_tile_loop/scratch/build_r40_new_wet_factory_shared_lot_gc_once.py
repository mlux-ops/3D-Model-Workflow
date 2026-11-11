"""R40 new substantive cross-room conditional identical-factory-SKU lot planning.
True 6 physical Soho Ivory receivers across PH4 WALKIN and TX4 TUB, plus
10 Sandstone receiver surfaces (8 existing 4-room niches + 2 conditional PH3
walls), fully separate install assemblies/old quote credits. Zero approvals.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,json,csv,math,io
B=Path(__file__).resolve().parents[1]
OUT=B/"deliverables/integrated-r40-conditional-soho-ivory-sandstone-same-sku-lot-13room-GC"
assert not OUT.exists()
R39=B/"deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement/MANIFEST.json"
RSHA="34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"
assert hashlib.sha256(R39.read_bytes()).hexdigest()==RSHA
R38=B/"state/ROUND038_NEXT_DISTINCT_WET_WALL_MAKER_PERMISSION_FULL_FIELD_NICHE_OPENING_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json"
assert hashlib.sha256(R38.read_bytes()).hexdigest()=="34d5fa02c436cf94d06aa56e662dad27ffc57fbb11b4dd8a9a18a084b03a80f4"
R30=B/"deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json"
assert hashlib.sha256(R30.read_bytes()).hexdigest()=="5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"
def read(rel):
 with (B/rel).open(encoding="utf-8-sig") as f:return list(csv.DictReader(f))
old=read("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
SOURCE={(x["room"],x["source_surface"]):x for x in old}
TARGET=("PH-BATH4","TX-BATH4","PH-BATH3")
G={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in TARGET}
assert all(len(G[r]["revit_room_numbers"])==2 for r in TARGET)
SAND=("PH-BATH2","PH-BATH3","TX-BATH2","TX-BATH3")
assert sum(Decimal(SOURCE[r,"accent"]["source_gross_sf_one_copy_waste_15pct_once"])*2 for r in SAND)==Decimal("51.64")
assert sum(Decimal(SOURCE[r,"accent"]["historic_usd_two_copies"]) for r in SAND)==Decimal("358.92")
assert sum(Decimal(SOURCE[r,"accent"]["source_gross_sf_one_copy_waste_15pct_once"])*2 for r in ("PH-BATH4","TX-BATH4"))==Decimal("34.52")
assert sum(Decimal(SOURCE[r,"accent"]["historic_usd_two_copies"]) for r in ("PH-BATH4","TX-BATH4"))==Decimal("1163.32")
PAY={}
def F(n):return f"{float(n):.4f}"
def csvout(name,records):
 assert records and len({tuple(x.keys()) for x in records})==1
 s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(records[0]),lineterminator="\n")
 w.writeheader();w.writerows(records);PAY[name]=s.getvalue().encode("utf-8-sig")
def md(name,txt):PAY[name]=(txt.strip()+"\n").encode("utf-8")

# New TRUE transaction source receivers, not old R30 tile format grid.
receivers=[]
for room,surface in (("PH-BATH4","wall"),("PH-BATH4","accent"),("TX-BATH4","accent")):
 for copy in G[room]["revit_room_numbers"]:
  x=SOURCE[room,surface]
  receivers.append(dict(product_group="CONDITIONAL_SOHO_IVORY_2x10_GLOSS_WET_WALL",
   actual_physical_copy=copy,room=room,original_source_surface=surface,
   original_historic_source_row_id=x["source_row_id"],
   conditional_owner_SELECTED_product="NONE_OPTION_ONLY_ELM_SOHO_IVORY_2x10_GLOSS",
   source_old_material_PRODUCT="PH4 Bone Ribbed" if room=="PH-BATH4" and surface=="wall" else "Clara Caviar 2x8 NICHE",
   quoted_old_historic_GROSS_SF_includes15pct_ONCE=x["source_gross_sf_one_copy_waste_15pct_once"],
   quoted_old_historic_two_copy_material_ONLY_USD=x["historic_usd_two_copies"],
   actual_true_1529_wall_niche_surface_net_and_cut_allowance="",
   current_factory_exact_SAME_SKU_color_finish_caliber_shade_lot="",
   current_factory_carton_usable_SF_and_current_Chicago_offer="",
   independent_WET_WALL_vs_NICHE_application="WET_WALL_INDIVIDUAL_LISTED; NICHE_SYSTEM_APPROVAL_UNVERIFIED",
   construction_condition="PH4_ACTUAL_WALKIN_BNXSQUARE_POINT_WP_WALL_AND_NICHE" if room=="PH-BATH4" else "TX4_DURAVIT_TUB_HANSGROHE_MATTE_WHITE_FLANGE_NICHE_NO_TILED_PAN",
   source_dated_quote_old_paid_stock_original_return_credit="",
   source_actual_NEW_gc_scope_membrane_tub_flange_niche_return_profiles_labor="",
   owner_approved="FALSE",supplier_signed="FALSE",GC_signed="FALSE",purchase_authorized="FALSE"))
assert len(receivers)==6
csvout("R40_6_REAL_PH4_TX4_OPTIONAL_IDENTICAL_SOHO_IVORY_WALL_NICHE_PHYSICAL_RECEIVERS.csv",receivers)

sand=[]
for room in SAND:
 geometry=json.loads((B/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
 for copy in geometry["revit_room_numbers"]:
  x=SOURCE[room,"accent"]
  sand.append(dict(material_group="CONDITIONAL_TONES_SANDSTONE_2x20_GLOSS_WET",
   source_physical_copy=copy,room=room,receiver="EXISTING_HISTORICAL_NICHE",
   original_row_ID=x["source_row_id"],
   source_quoted_gross_15pct_ONCE=x["source_gross_sf_one_copy_waste_15pct_once"],
   original_two_copy_historical_material_ONLY_USD=x["historic_usd_two_copies"],
   owner_conditional_new_wall_selection="FALSE",
   original_existing_wet_WALL_NICHE_individual_maker_appl="ARCHIVED_WET_LISTED_RENEW_AT_EXACT_CURRENT_SKU",
   factory_exact_SKU_color_finish_caliber_lot_same_with_all_others="FALSE",
   original_paid_received_or_existing_stock="",
   new_installed_tiling_quote_and_true_1529_geometry="",
   purchase_authorized="FALSE"))
for copy in G["PH-BATH3"]["revit_room_numbers"]:
 x=SOURCE["PH-BATH3","wall"]
 sand.append(dict(material_group="CONDITIONAL_TONES_SANDSTONE_2x20_GLOSS_WET",
   source_physical_copy=copy,room="PH-BATH3",receiver="OWNER_OPTION_NEW_WET_WALL_NOT_SELECTED",
   original_row_ID=x["source_row_id"],
   source_quoted_gross_15pct_ONCE=x["source_gross_sf_one_copy_waste_15pct_once"],
   original_two_copy_historical_material_ONLY_USD=x["historic_usd_two_copies"],
   owner_conditional_new_wall_selection="FALSE",
   original_existing_wet_WALL_NICHE_individual_maker_appl="ORIGINAL_OPAL_WALL_UNVERIFIED_SANDSTONE_WALL_ARCHIVED_WET_LISTED",
   factory_exact_SKU_color_finish_caliber_lot_same_with_all_others="FALSE",
   original_paid_received_or_existing_stock="",
   new_installed_tiling_quote_and_true_1529_geometry="",
   purchase_authorized="FALSE"))
assert len(sand)==10
assert sum(Decimal(x["source_quoted_gross_15pct_ONCE"]) for x in sand)==Decimal("224.04")
csvout("R40_10_REAL_OR_CONDITIONAL_PH3_SANDSTONE_FIELD_PLUS_EIGHT_ORIGINAL_NICHE_RECEIVERS.csv",sand)

# Individual physical receiver versus hypothetical identical factory lot
# ceiling per group. Historical gross only, never new 15% on those rows.
theory=[]
for label,records in (("SOHO_IVORY",receivers),("SANDSTONE",sand)):
 total=sum(float(x["quoted_old_historic_GROSS_SF_includes15pct_ONCE"] if label=="SOHO_IVORY" else x["source_quoted_gross_15pct_ONCE"]) for x in records)
 for cap in (6.,8.,12.):
  indep=sum(math.ceil(float(x["quoted_old_historic_GROSS_SF_includes15pct_ONCE"] if label=="SOHO_IVORY" else x["source_quoted_gross_15pct_ONCE"])/cap) for x in records)
  pooled=math.ceil(total/cap)
  theory.append(dict(conditional_group=label,source_original_receivers=len(records),
   originally_quoted_historical_GROSS_SF_sum_15pct_ONCE=F(total),
   hypothetical_future_case_usable_coverage_SF_NOT_REAL=F(cap),
   hypothetical_individually_rounded_SOURCE_receiver_case_count=indep,
   hypothetical_one_identical_SKU_same_lot_pool_case_count=pooled,
   hypothetical_case_difference_NOT_REAL_SAVING=indep-pooled,
   owner_selects_ONE_exact_product_for_all_relevant_surfaces="FALSE",
   actual_calibrated_same_SHAPE_size_color_finish_lot_verified="FALSE",
   factory_current_usable_case_SF_current_Chicago_offer_verified="FALSE",
   signed_actual_1529_NET_and_trim_or_site_cutstock_verified="FALSE",
   original_material_quote_ALTERATION_signed="FALSE",
   purchase_authorized="FALSE"))
assert len(theory)==6
csvout("R40_6_SAME_ITEM_6_8_12SF_FICTIONAL_POOLING_SENSITIVITIES_NO_ORDER_OR_SAVINGS.csv",theory)

# Original contract scope 4-copy Caviar and 8-copy Sandstone existing.
# Newly proposed wall line is NOT new historical original quote. No double
# counting of original dollars when comparing true substitution.
quot=[]
for label,records,old_basis in (("SOHO_IVORY",receivers,Decimal("2743.44")),("SANDSTONE",sand,Decimal("1557.10"))):
 actual=sum(Decimal(x["quoted_old_historic_two_copy_material_ONLY_USD"] if False else "0") for x in []) # no duplicate 2copy over actual units
 quot.append(dict(group=label,
  historical_original_material_ONLY_subscope_in_full_four_unit_USD=str(old_basis),
  historical_full_original_project_material_ONLY_USD="23572.44",
  original_waste_15pct_ALREADY_ONCE="TRUE",
  alternative_source_new_factory_SKU_lot_current_case_price="UNKNOWN",
  old_material_original_paid_shipped_received_return_eligibility="UNKNOWN",
  current_NEW_item_replacement_material_budget_USD="UNKNOWN",
  source_existing_old_MATERIAL_only_quote_not_current_purchasing="TRUE",
  new_substrate_membrane_sealant_rough_glass_tub_flange_trim_labor_installed_bid_USD="UNKNOWN",
  new_delivery_truck_access_freight_tax_min_order_ETA="UNKNOWN",
  actual_OWNER_selected_alternative_and_credit_offset_signed="FALSE",
  actual_1529_net_actual_same_lot_case_receipt="FALSE",
  actual_change_order_payable_or_real_savings="FALSE",
  supplier_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(quot)==2
csvout("R40_2_CROSSROOM_MATERIAL_VS_FULL_INSTALLED_FACTORY_SAMELOT_BID_ORIGINAL_CREDIT_GATES.csv",quot)

# Every physical receiver needs its own distinct installation method. Even
# when identical tile, PH4 shower and TX4 tub assemblies cannot share shop
# approval. Original PH3 wall and other niches are different projects.
sections=[]
for x in receivers:
 for concern in ("WET_WALL_OR_NICHE_MEMBRANE_SILL_PENETRATION","EDGE_FLOOR_TUBFLANGE_OR_POINT_PAN_TRANSITION","SITE_NET_CASE_LOT_PLUMBING_GLASS_AND_CHANGE_ORDER"):
  sections.append(dict(group="SOHO_IVORY",physical_source_copy=x["actual_physical_copy"],room=x["room"],
   original_surface=x["original_source_surface"],individual_trades_shop_hold=concern,
   original_factory_quoted_surface=x["source_old_material_PRODUCT"],
   conditional_approved_alt_only="ELM_SOHO_IVORY_2x10_GLOSS_OWNER_NOT_SELECTED",
   selected_fixture_preserved=x["construction_condition"],
   individual_WET_WALL_application="MAKER_LISTED_ON_INDIVIDUAL_PRODUCT",
   individual_exact_WET_NICHE_and_MEMBRANE_SYSTEM_approval="UNVERIFIED",
   installed_tile_body_nominal_9point5mm_not_actual_finished_plane="TRUE",
   original_Caviar_13mm_diff_nominal_3point5mm_not_mortar_rule="TRUE",
   actual_native_1529_valve_niche_sill_backer_movement_and_finish="",
   actual_signed_1to1_wall_niche_edge_mockup="FALSE",
   actual_factory_usable_lot_case_and_current_full_GC_bid="",
   owner_approved="FALSE",WP_tiler_plumber_signed="FALSE",purchase_authorized="FALSE"))
assert len(sections)==18
csvout("R40_18_SIX_PHYSICAL_SOHO_IVORY_SHOWER_VS_TUB_DISTINCT_TRADE_WP_NICHE_1TO1_HOLDS.csv",sections)

# Hard prohibition lists maker-looking synonyms but distinct materials.
exclude=[]
for candidate,reason in [
 ("ELM Soho Emerald 2x10 Glossy","Different color from Soho Ivory, cannot pool"),
 ("ELM Noho Emerald 2x10 Matte","Different brand collection, color and finish"),
 ("ELM Soho Blue 2x10 Glossy","Different color, cannot pool"),
 ("Tones Sandstone 2x20 Glossy","Different factory collection, module and color from Soho Ivory"),
 ("Tones Opal 2x20 Glossy","Unverified wet original, different color/format from Soho Ivory"),
 ("Cortar Bone Ribbed 24x48 relief","Wet permission unverified; not an identical tile to Soho Ivory"),
 ("Clara Caviar 2x8","Different brand body 13mm vs Soho nominal9.5mm, unapproved NICHE use"),
 ("Tones Emerald 2x20 Glossy","Not same exact SKU as Soho/Noho Emerald")]:
 exclude.append(dict(disallowed_cross_lot_material=candidate,
  factory_same_SKU_color_finish_CALIBER_lot_compatible="FALSE",
  reason_exact_scope=reason,
  may_pool_against_SOHO_IVORY="FALSE",
  may_borrow_other_item_individual_wet_WALL_NICHE_approval="FALSE",
  may_transfer_different_SOURCE_original_NUMERIC_wet_DCOF="FALSE",
  actual_owner_substitution_signed="FALSE",purchase_authorized="FALSE"))
assert len(exclude)==8
csvout("R40_8_MATERIAL_IDENTITY_HARD_NONPOOLING_SOHO_EMERALD_NOHO_BLUE_CAVIAR_RIBBED.csv",exclude)

# A distinct contractor-ready quote normalization schedule. No current
# pricing or paid stock is invented; maker item compatibility is independent
# of waterproofing and architectural actual wall dimensions.
rfq=[]
for group,room,surface,description in (
("SOHO_IVORY","PH-BATH4","wall","Original Ribbed wet WALL potential replacement"),
("SOHO_IVORY","PH-BATH4","accent","Original Clara Caviar wet NICHE potential replacement"),
("SOHO_IVORY","TX-BATH4","accent","Original Clara Caviar tub NICHE potential replacement"),
("SANDSTONE","PH-BATH3","wall","Original Tones Opal wet WALL potential replacement"),
("SANDSTONE","PH-BATH3","accent","Original existing wet Sandstone niche retained"),
("SANDSTONE","PH-BATH2","accent","Original existing wet Sandstone niche, Duravit tub"),
("SANDSTONE","TX-BATH2","accent","Original existing wet Sandstone niche, Duravit tub"),
("SANDSTONE","TX-BATH3","accent","Original existing wet Sandstone niche, owner tub/walkin undecided"),
):
 x=SOURCE[room,surface]
 rfq.append(dict(group=group,room=room,surface=surface,
  original_vendor_source_row=x["source_row_id"],old_GROSS_one_physical_copy_SF_15pct_once=x["source_gross_sf_one_copy_waste_15pct_once"],
  original_historical_two_copy_MATERIAL_only_USD=x["historic_usd_two_copies"],
  contractor_scope_DESCRIPTION=description,
  current_factory_selected_SKU_color_finish_lot_approved="FALSE",
  approved_same_exact_factory_product_for_wet_WALL_and_NICHE="FALSE",
  factory_current_exact_case_usable_SF_and_selected_shade_caliber="",
  case_qty_at_actual_measured_net_plus_NEW_owner_approved_cut_waste="",
  original_paid_received_inventory_full_unit_price_returnable_credit="",
  supplier_current_chicago_pricing_ETA_min_order_freight_tax="",
  actual_WALL_NICHE_method_membrane_edge_trim_slope_WP="",
  installed_GC_demo_backer_valve_glass_movement_paint_tile_labor="",
  independent_original_LEVEL_PAN_lab_scope="RETAIN_SEPARATE_NOT_INCLUDED_IN_WALL_NICHE_QUOTE",
  owner_signed="FALSE",architect_signed="FALSE",plumber_signed="FALSE",WP_tile_signed="FALSE",
  supplier_signed="FALSE",GC_signed="FALSE",purchaser_signed="FALSE",purchase_authorized="FALSE"))
assert len(rfq)==8
csvout("R40_8_CORRECTED_GROUPED_MATERIAL_LOT_WALL_NICHE_VS_INSTALLED_GC_RFP_LINE_ITEMS.csv",rfq)

# Owner 13-room status remains frozen, R40 only changes newly conditional
# supplier receiving readiness of the three focus room identities. No extra
# niche/Primary/WC/floor line is manufactured.
ROOMS=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(ROOMS)==13
release=[]
for room in ROOMS:
 id=room["id"]
 release.append(dict(room=id,original_formal_round_017_unchanged="TRUE",
  original_status_unchanged=room["status"],
  original_champion_unchanged=room.get("champion_id") or "null",
  original_champion_score_unchanged=str(room.get("champion_score")) if room.get("champion_score") is not None else "null",
  new_R40_conditional_supplier_BOM="SOHO_IVORY_WALL_OR_NICHE" if id in ("PH-BATH4","TX-BATH4") else "SANDSTONE_OPTION_WALL_OR_EXISTING_NICHE" if id in ("PH-BATH3","PH-BATH2","TX-BATH2","TX-BATH3") else "NOT_R40_NEW_SCOPE_PRESERVE_R39_13ROOM_CONTROL",
  source_ROOM_program_nonnegotiable="PH4_WALKIN_BNXSQUARE_POINT_4PLANE_SEPARATE_LEVEL" if id=="PH-BATH4" else "TX4_DURAVIT_TUB_MATTE_WHITE_NO_PAN" if id=="TX-BATH4" else "PH3_TUB_VS_WALKIN_OWNER_UNSELECTED" if id=="PH-BATH3" else "PRESERVE_PRIOR",
  actual_individual_SKU_color_finish_WET_WALL_vs_WET_NICHE_app_approved="FALSE",
  exact_RAW_original_numeric_LEVEL_wet_DCOF_if_applies="MISSING_OR_N_A_IF_DRY",
  separate_exact_RAW_original_numeric_POINT_OR_LINEAR_PAN_if_applies="MISSING_OR_N_A_IF_TUB",
  certified_native_1529_geometry_and_actual_NET_NICHE_WALL_FLOOR="",
  current_compatible_factory_same_exact_SKU_CALIBER_LOT_and_usable_case="",
  actual_Chicago_quote_full_installed_GC_bid_paid_credit="",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  waterproof_trade_approved="FALSE",tile_installer_approved="FALSE",
  supplier_approved="FALSE",GC_approved="FALSE",purchaser_approved="FALSE",
  original_4_SPECIALIST_board_scored="FALSE",current_nonpro_Reviewer_DONE="FALSE",
  purchase_authorized="FALSE"))
assert len(release)==13
csvout("R40_13_ROOM_NEW_SAMELOT_MATERIAL_AND_SEPARATE_WET_PROGRAM_RELEASE_BRIDGE.csv",release)

md("START_HERE_R40_IDENTITY_CONSTRAINED_SAME_SKU_WET_WALL_NICHE_GC_OWNER_BOOK.md",f"""
# R40 — new cross-room 2x10 wet wall/niche lot and installed GC procurement optimization

**Substantive next engineering after full signed R39** SHA {RSHA}; protects original owner selections, formal board017 and 13-room OPEN. No new owner selection, physical samples, 1529 measurements, vendor outreach, case ordering or contract change.

## Actual new cross-room opportunity, not old R30 2x8/2x10 format study

Individual [ELM Soho Ivory 2x10 Glossy](https://www.elmsurfaces.com/product/soho-ivory) manufacturer product is individually listed for Wet Areas WALL; nominal body9.5mm. R39 PH-BATH4 original Cortar Bone Ribbed wet WALL permission and original Caviar 2x8 wet NICHE individual authorization are deficient. The same **conditional exact Soho Ivory PRODUCT** may be an owner-reviewed candidate for PH-BATH4 full WET WALL and its niche, and separately TX-BATH4 existing Caviar niche in actual owner-selected **Duravit tub with Hansgrohe Matte White**—TX4 is NOT a tiled shower PAN. However each wet NICHE and the PH4 POINT shower WALL require independent manufacturer-approved membrane/system/corner/sill applications; individual Wet Areas wall listing does NOT automatically certify waterproof installation or owner substitution. Keep PH4 WALKIN Brizo BNX 4in square POINT with separate 4plane PAN and bath LEVEL, and the disputed 35/27 bath floor and 214.4 vendor wall total nonpayable.

Six separate physical receiver surfaces, not six distinct room IDs: PH4 original Ribbed WALL two copies 107.2SF gross each, PH4 original Caviar NICHE two copies 8.63SF each, TX4 original Caviar NICHE two copies 8.63SF each. Total original historical **248.92SF old GROSS** loaded once with 15% waste, across six source surfaces/PH4 311A/B + TX4 007A/B. This is **NOT** new Soho calibrated factory case coverage or owner-approved gross. Previously existing Caviar PH4+TX4 historical group 34.52SF/$1163.32 already included. Original PH4 Ribbed wet-wall material-only two copies $1580.12 also already included; resulting historical original material-only subset **$2743.44**, NOT a quote for Soho Ivory and not automatically returnable or payable.

**Different assembly cannot share waterproof approval even if factory SAME SKU:** PH4 WALL shower requires actual Brizo POINT-drain selected rough, four-plane PAN-to-WALL membrane, niche corners, curb/glass hinge, real 1529 coordinates and independent original exact raw LEVEL/POINT PAN wet DCOF. TX4 NICHE in actual Duravit bathtub requires actual tub flange-to-membrane termination, actual Hansgrohe Matte White selected pressure-balance/thermostatic spout-control compatibility resolution, splash/sill seals and no tiled shower PAN. Both need independent actual original tile and niche floor/lab permissions, physical 1:1 in each original physical unit and signed substrate/mortar/calibrated high point/edge profile. Original Caviar body ~13mm versus nominal Soho9.5mm is only nominal **3.5mm** difference, not automatically true installed plane or an approved mortar buildup.

## Newly conditional PH3 Sandstone wall expanded original niche receiving

Original four-room PH2/PH3/TX2/TX3 **eight physical Sandstone 2x20 GLOSS NICHE** receivers total **51.64SF original gross and $358.92 material-only historically already included**. New R39 PH3 owner option makes two original PH3 WET WALL Opal rows (86.2SF old gross each, 172.4SF across two) conditional for **same source Tones Sandstone 2x20 Glossy** WET WALL, only if owner approves and exact factory SKU/color/finish/caliber and lot and wall/niche application actually match. Joint source hypothetical total **224.04SF old gross**, spread over ten distinct receiver surfaces (8 existing niche +2 conditionally new wall), not current actual net, ordered cases or extra historical charge. Old original PH3 Opal wall two-copy material-only $1198.18 plus old original all-room Sandstone niche $358.92 = **$1557.10 already historic**, NOT automatically same price for new wall or realized saving. Sandstone original exact item Wet Areas listing prior verified, current maker identity/lot/site requires renewal; PH3 TUB versus WALKIN, Hansgrohe Chrome, optional Delta Chrome 4in square POINT shower only WALKIN, and basin unselected remain untouched.

## Quantitative new purchase-engineering and exclusions

The six genuine Soho and ten original/conditional Sandstone material RECEIVERS have separate historical row identifiers, surface role, program and original stock-credit flags. Six fictional 6/8/12SF usable carton sensitivity rows calculate independently ceiling-rounded source per-room/face cases versus one pooled factory identical SKU/lot case. Such pooling is **not** allowable today because no owner selected the alternative, no full exact current SKU/shade/caliber/lots/actual usable box or real 1529 NET confirmed. This does not repeat R30 228 tile-bond detail sheets, R29 old niche-only pooling, or R39 144 W-grid cases; R40's newly relevant **PH4 wall+PH4 niche+TX4 niche and PH3 new Sandstone wall+old eight niches** are different scope, and it separately bids the WET wall versus TUB NICHE installed systems. The four-unit historical material total remains **$23572.44** and original waste 15% already included once, no duplicate paid credit, wall+niche overlapping opening, WC, Primary niche or PAN.

Eight current factory procurement/GC RFQ line items specify exact 2026 item SKUs, maker Wet WALL/NICHE permission, real calibrated tile and usable cartons, PH4 shower membrane/point drain or TX4 Duravit tub flange, actual sealant/trim/grout, paid current original returnable stock and full installed trade labor, tax/freight/ETA; all remain blank. Eight hard nonpooling rows forbid Soho/Noho Emerald, Soho Blue, original Bone Ribbed, original Caviar, Tones Opal/Emerald, Tones Sandstone from cross-borrowing Soho Ivory permission/lot or source wet DCOF. The project's 13 original room matrix remains unchanged; all purchase authorizations FALSE.

Next necessary onsite and factory proof: TRUE 1529 W1W3/niche/aperture and valve/tub/glass wall/threshold survey (accessible 1527 model not certifiable), actual owner selection and distinct ORIGINAL individual WET wall/niche maker letter, approved chosen waterproof system, separate raw original numeric LEVEL vs POINT/LINEAR PAN test, actual Chicago current factory same lot/case, and dated full installed GC quote with old original quote paid credit evidence. No contacted vendor or signed GC change order. Original worker9 missing R014 DESIGN critiques and Reviewer15 FINISHED; no score/independent GLOBAL DONE.
""")

parent=json.loads(R39.read_text(encoding="utf-8"))
lineage=dict(parent["predecessor_signed_file_hashes"])
lineage["R39_FULL"]=RSHA
lineage["R38_SOURCE"]=hashlib.sha256(R38.read_bytes()).hexdigest()
lineage["R30_FULL"]=hashlib.sha256(R30.read_bytes()).hexdigest()
meta=dict(round=40,date_local="2026-11-06",
 phase="NEW_POST_R39_CROSSROOM_EXACT_PRODUCT_WET_WALL_NICHE_LOT_AND_GC_INSTALLED_SCOPE_INTEGRATED_UNRELEASED",
 predecessor_signed_file_hashes=lineage,
 focus=["PH-BATH4","TX-BATH4","PH-BATH3"],
 original_distinct_room_count=13,original_historic_material_rows=27,
 original_historic_material_only_USD="23572.44",original_waste_15pct_ALREADY_in_old_gross_once=True,
 original_PHO_PHO_SANDSTONE_4ROOM_niche_USD="358.92",
 original_PH4_TX4_CAVIAR_niche_USD="1163.32",
 original_PH4_wall_original_material_USD="1580.12",
 six_SOHO_IVORY_original_receivers_gross_SF_historical_once="248.92",
 ten_SANDSTONE_existing_niche_plus_unselected_new_wall_gross_SF_historical_once="224.04",
 source_13room_original_owner_programs_unchanged=True,
 original_4_specialist_complete=False,nonpro_reviewer_DONE=False,
 actual_true_1529_native_site_survey=False,original_exact_raw_wet_LEVEL_PAN_labs_received=False,
 owner_conditional_materials_selected=False,manufacturer_exact_WET_NICHE_WP_system_approved=False,
 original_paid_inventory_and_credit_verified=False,current_factory_exact_SHADE_LOT_current_case_Chicago_quote=False,
 current_installed_GC_change_order_signed=False,
 supplier_materials_reserved=False,owner_approved=False,GC_approved=False,
 purchase_authorized=False,global_DONE=False,
 files=[dict(path=k,bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in sorted(PAY.items())])
assert len(PAY)>=9
OUT.mkdir(parents=True,exist_ok=False)
for name,data in sorted(PAY.items()):
 with (OUT/name).open("xb") as f:f.write(data)
(OUT/"MANIFEST.json").write_bytes((json.dumps(meta,indent=2)+"\n").encode("utf-8"))
print("R40_PAYLOADS",len(PAY),"R40_MANIFEST_SHA",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
