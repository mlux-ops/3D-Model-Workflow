"""R42 substantive maker-specific two-Duravit-tub control/spout rough corrective shop.
New actual manufacturer installation constraints, conditional owner program
correction paths, plumbing/tiling wet wall and change-order scope; never selects
or orders substitute items. ALL data written only to project workspace.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,json,csv,io,math
B=Path(__file__).resolve().parents[1]
OUT=B/"deliverables/integrated-r42-matte-white-thermostat-diverter-tub-spout-field-rough-wet-wall-GC"
assert not OUT.exists()
R41=B/"deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room/MANIFEST.json"
P41="7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0"
assert hashlib.sha256(R41.read_bytes()).hexdigest()==P41
R33=B/"deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json"
assert hashlib.sha256(R33.read_bytes()).hexdigest()=="a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
ROOMS=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(ROOMS)==13
FOCUS=("PH-BATH2","TX-BATH4")
G={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in FOCUS}
PL={r:json.loads((B/"rooms"/r/"plumbing.json").read_text(encoding="utf-8")) for r in FOCUS}
for r in FOCUS:
 assert len(G[r]["revit_room_numbers"])==2
 SKUs={x["model_or_sku"] for x in PL[r]["fixtures"]}
 assert {"700332000000090","15758701","72411701","01850181"}<=SKUs,(r,SKUs)
DATA={}
def putcsv(name,rows):
 assert rows and len({tuple(x.keys()) for x in rows})==1
 s=io.StringIO(newline="");w=csv.DictWriter(s,list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
 DATA[name]=s.getvalue().encode("utf-8-sig")
def md(name,s):DATA[name]=(s.strip()+"\n").encode("utf-8")
URL={
 "diverter":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-with-diverter-72411701",
 "install":"https://assets.hansgrohe.com/mam/celum/celum_assets/16__hruh1138_pdf.pdf",
 "thermo":"https://images.thdstatic.com/catalog/pdfImages/80/80beae87-199e-580c-8264-e07bb597c987.pdf",
 "plain":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-72410701",
 "pressure":"https://www.hansgrohe-usa.com/articledetail-ecostat-s-pressure-balance-trim-15739001",
 "old_pricebook":"https://assets.hansgrohe.com/celum/web/hansgrohePriceBook2021USf01052Release.pdf"}

# New factory extraction and selected item incompatibility is a verified
# hydraulic hard gate, not a wet-niche tile approval.
FACT=[
 ("selected_thermo","15758701","Hansgrohe Ecostat S thermostatic Matte White trim with volume control and diverter for 2 functions; required rough separate","MANUFACTURER_PRODUCT_PDF","EXACT_SELECT_FIXED",URL["thermo"]),
 ("selected_spout","72411701","Talis S Matte White tub spout with integral diverter; manufacturer explicitly pressure-balance valve ONLY","CURRENT_INDIVIDUAL_MAKER_PAGE","FACTORY_CONFLICT_WITH_THERMO",URL["diverter"]),
 ("spout_specific_install","72411XX1","Manufacturer Talis S diverter spout instruction: pressure-balance trim ONLY, NOT thermostatic mixing valve or PB-with-diverter","ORIGINAL_HANSGROHE_INSTALL_PDF","EXACT_APPLICABLE_FAMILY",URL["install"]),
 ("metal_drop","72411XX1","Manufacturer tub-spout drop 1/2in or 3/4in metal, NO PEX/plastic, 8-18in length, ONE elbow; risk stacking/dripping from showerhead","ORIGINAL_HANSGROHE_INSTALL_PDF","MEASURE_1529_PHYSICAL",URL["install"]),
 ("conditional_plain_spout","72410701","Hansgrohe Talis S Matte White NONDIVERTER tub spout, no integral diverter stated in individual product page; two-outlet thermostat path must be separately factory signed","CURRENT_INDIVIDUAL_MAKER_PAGE","NOT_OWNER_SELECTED_OR_FACTORY_WHOLE_SYSTEM_APPROVAL",URL["plain"]),
 ("conditional_pressure_balance_family","15739_FAMILY","Ecostat S pressure-balance trim family has bypass for diverter tub spout; Chrome 15739001 exact maker listing. Matte White 15739701 historical maker price book only, current individual live item/rough availability not confirmed","CURRENT_MAKER_PRESSURE_BALANCE_OTHER_COLOR_PLUS_2021_PRICEBOOK","NOT_OWNER_SELECTED_OR_FULL_INSTALL_APPROVAL",URL["pressure"]),
 ("rough","01850181","Original selected iBox Universal Plus rough listed with both PH2/TX4; verify real installed version, stops, valve outlet and any compatible cartridge/trim before considering substitution","ORIGINAL_FIXTURES_DECK_AND_MAKER_ACCESSORY","ACTUAL_ROUGH_UNVERIFIED",URL["thermo"])
]
fact=[dict(evidence_id=i,original_or_candidate_SKU=sku,manufacturer_specific_fact=claim,
 maker_authority_class=grade,shop_release_status=gate,official_manufacturer_URL=url,
 individual_maker_original_revision_exact_factory_item_current="UNVERIFIED" if i in ("conditional_pressure_balance_family","rough") else "SOURCE_SPECIFIC_PENDING_SHOP",
 actual_OWNER_change_signed="FALSE",actual_factory_system_compatibility_final="FALSE",
 purchasing_authorized="FALSE") for i,sku,claim,grade,gate,url in FACT]
putcsv("R42_7_ORIGINAL_HANSGROHE_SELECTED_FACTORY_SPOUT_TRIM_DROP_AND_ROUGH_CITATIONS.csv",fact)

# Three truly differentiated correction choices x 4 original physical rooms.
# Preserve Matte White and original Duravit for each; all require owner choice.
routes=[
 ("A_KEEP_THERMOSTAT_SWAP_SPOUT_ONLY","Retain original thermostatic 15758701 Matte White and selected original rough only after factory confirmation, propose Talis S non-diverter 72410701 Matte White; route 2-function diverter in original thermostatic trim","Plain spout individually maker-listed in Matte White, exact plumbing 2-outlet flow/spout/drop/tub/shower valve compatibility NOT confirmed; pressure-balance-only diverter spout must not remain","SP_OUTLET_2FUNCTION"),
 ("B_KEEP_DIVERTER_SPOUT_CHANGE_MIXER","Retain original Talis S 72411701 Matte White diverter spout, owner-conditional pressure-balance Ecostat S trim family; historical 15739701 Matte White possible only if current exact maker item/current install with 01850181 confirmed","Must remove incompatible 15758701 thermostat trim and prove selected PB trim contains diverter bypass; cannot use any PB-with-integral-diverter trim plus spout diverter","PB_BYPASS_OUTLET"),
 ("C_FACTORY_COMPLETE_REPLUMB_STAGED","Hold both selected original trims/spout without compatibility release; design supplier/maker-endorsed complete tub/shower service and spout/trim/rough package with preserved Matte White","Potential significant tile wall/valve/drain/tub-flange demolition and 1:1 re-waterproofing/GC cost; new owner-selected finished parts still unknown","FULL_SYSTEM_SHOP")
]
routes_out=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for code,solution,gate,draw in routes:
   routes_out.append(dict(room=room,physical_copy=copy,option=code,
    current_owner_selected_Duravit="700332000000090",current_owner_finish="Hansgrohe Matte White",
    current_selected_trim="15758701 THERMOSTATIC",current_selected_diverter_spout="72411701 PB-ONLY",
    current_selected_rough="01850181 iBox Universal Plus",
    proposed_correction_not_owner_selected=solution,
    manufacturer_assembly_hard_gate=gate,
    physical_shop_hydraulic_scheme=draw,
    current_factory_supported_assembled_rough_trim_spout="FALSE",
    real_1529_valve_pipe_drain_and_sill_coords="",
    original_Duravit_TUB_NO_tiled_PAN="TRUE",
    waterproof_tub_flange_CORTAR_or_TONES_WET_wall_and_niche_joint="NOT_APPROVED",
    original_RAW_wet_LEVEL_numeric_lab="MISSING",
    independent_shower_PAN_numeric_lab="N_A_TUB",
    current_exact_factory_product_Chicago_offer_and_FULL_installed_GC_bid="",
    original_OLD_quote_paid_material_and_credits="",
    owner_approved="FALSE",plumber_approved="FALSE",architect_approved="FALSE",
    waterproof_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(routes_out)==12
putcsv("R42_12_FOUR_PHYSICAL_TUBS_THREE_DIFFERENT_SELECTED_MATTE_WHITE_CONTROL_CORRECTION_DECISIONS.csv",routes_out)

# Original manufacturer physical drop and selected rough fact transforms
# into a measurable tolerance/section checklist, not invented 1529 drop.
physical=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for stage,required in (
   ("R01_DEMO_FREE_PLUMBER_AS_BUILT","True 1529 valve/rough, installed trim/cartridge, spout wall connection and showerhead service route; photograph and measure without changing fixtures"),
   ("R02_TUB_SPOUT_DROP_FACTORY_HARD_GEOMETRY","Maker 8-18in metal 1/2 or 3/4 line, 1 elbow, NO PEX; actual rough-to-spout measured centerline drop and drop pipe is supported and tested"),
   ("R03_OWNER_SELECTED_CONTROL_HYDRAULIC_DIVERTER","Architect/plumber/maker approve one exact PB-with-spout-diverter OR thermostatic-with-nondiverter branch; never two diverters or thermostat+diverter spout"),
   ("R04_WET_WALL_BACKER_VALVE_ACCESS_TUB_FLANGE","Actual 1529 tiled plane/valve-depth, factory sleeve, tub flange seal, original wall/niche individual wet approval and permitted penetration boots"),
   ("R05_DEMO_AND_MOCKUP_CO_RESPONSIBILITY","Existing new/paid material and returnable credit, tile tearout limits, re-waterproof, grout, trim, paint/glass and installed GC bid before owner CO"),
    ("R06_PHYSICAL_SERVICE_AND_COMMISSION","Prototype fixture wall closure, pressure/flow and controlled outlet switching, no stacking/head drip, signed accessible service and wet-wall finish")
   ):
   physical.append(dict(room=room,physical_copy=copy,trade_hold=stage,exact_factory_or_field_required=required,
    original_SELECTED_thermo_and_spout_incompatible="TRUE",measured_TRUE_1529_SPOUT_DROP_in="",
    manufacturer_allowed_MATERIAL_METAL_NO_PEX_and_one_elbow="TRUE",factory_max_drop_in="18",factory_min_drop_in="8",
    original_Duravit_tub_and_MatteWhite_retained="TRUE",
    original_floors_RAW_numeric_wet_LEVEL_lab="MISSING",original_shower_PAN_test="N_A_TUB",
    owner_choice_signed="FALSE",manufacturer_factory_installed_system_approved="FALSE",
    plumber_signed="FALSE",architect_signed="FALSE",WP_tile_signed="FALSE",
    GC_change_order_signed="FALSE",purchase_authorized="FALSE"))
assert len(physical)==24
putcsv("R42_24_SIX_STAGE_FOUR_TUB_INSTANCE_PLUMBER_WP_TILE_1TO1_FIELD_SHOP_HOLDS.csv",physical)

# Conditional nominal Z interfaces at genuine tiled plane, to be measured.
planes=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for layer in ("EXISTING_STUD_BACKER_UNCERTIFIED","WATERPROOF_MEMBRANE_AND_TUB_FLANGE_LAP","MORTAR_TILE_CALIBER_AND_FACTORY_ESCUTCHEON","ROUGH_VALVE_CARTRIDGE_AND_PB_OR_THERMOSTAT_SERVICE"):
   planes.append(dict(room=room,physical_copy=copy,shop_layer=layer,
    source_previous_finish_wall_before_demolition="UNKNOWN",
    actual_1529_selected_original_tile_or_candidate_finish_thickness_mm="",
    actual_backer_membrane_compressed_mortar_factory_accepted_mm="",
    actual_rough_recess_manufacturer_min_max_from_finished_wall_mm="",
    formula_finished_wall_from_stud="BACKER+MEMBRANE+COMPRESSED_MORTAR+TILE_BODY_AND_RELIEF_FACE",
    maker_rough_sleeve_and_ESCUTCHEON_sealing_gasket_depth_accepted="FALSE",
    original_tub_flange_preserved_and_sealed="FALSE",
    new_owner_rough_spout_change_selected="FALSE",purchase_authorized="FALSE"))
assert len(planes)==16
putcsv("R42_16_TWO_TUB_8_PHYSICAL_RISK_WALL_FINISH_AND_ROUGH_Z_DEPTH_TOLERANCE_SHOP.csv",planes)

# The true 13-room scope remains frozen; R42 is not another 'completed'
# release of selected hardware or factory prices.
release=[]
for x in ROOMS:
 r=x["id"]
 release.append(dict(room=r,formal_board_round=17,original_champion_unchanged=x.get("champion_id") or "null",
  original_status_unchanged=x["status"],original_score_unchanged=str(x.get("champion_score")) if x.get("champion_score") is not None else "null",
  R42_MatteWhite_TUB_high_risk="PB_ONLY_DIVERTER_VS_THERMOSTATIC_HOLD" if r in FOCUS else "PRESERVE_ORIGINAL_PREDECESSOR",
  original_program="DURAVIT_TUB_NO_TILED_SHOWER_PAN" if r in FOCUS else "UNCHANGED",
  original_factory_selected_trim_spout_rough="15758701+72411701+01850181" if r in FOCUS else "SOURCE_UNCHANGED",
  owner_selected_rough_or_finish_CHANGED="FALSE",
  true_1529_site_measurement_and_MAKER_CURRENT_item="",
  exact_original_raw_numeric_wet_LEVEL_lab_if_applies="MISSING_OR_N_A_DRY",
  independent_LINEAR_POINT_PAN_if_applies="N_A_TUB" if r in FOCUS else "PRESERVE_R41_SEPARATE_GATES",
  maker_exact_individual_wet_wall_AND_niche="PRESERVE_SEPARATE",
  current_supplier_lot_installed_quote_and_old_credits="",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  waterproof_approved="FALSE",installer_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(release)==13
putcsv("R42_13_ROOM_TUB_CONFLICT_AND_FULL_ORIGINAL_13ROOM_UNRELEASED_BRIDGE.csv",release)

md("START_HERE_R42_HANSGROHE_TWO_DURAVIT_TUB_FACTORY_DROP_AND_MATTE_WHITE_CORRECTION_BOOK.md",f"""
# R42 real manufacturer-constrained correction of two selected Duravit tub plumbing systems

**SUBSTANTIAL DISTINCT NEXT CYCLE after signed R41 SHA {P41}, not R33 generic compatibility register.** Four physical original bathtubs PH-BATH2 and TX-BATH4 copies A/B. Both actually selected owner Duravit 700332000000090, Hansgrohe Matte White 15758701 two-function THERMOSTATIC trim, 72411701 Talis S integrated diverter tub spout, selected 01850181 iBox. All retained as owner source but product assembly is demonstrably NOT SUPPORTED as scheduled, not installation ready and requires owner/plumber/architect/factory decision. No tub tiled PAN in either room; both original LEVEL tile exact measured numeric wet DCOF still required.

## Genuine factory installation evidence, beyond earlier generic compatibility notes

Hansgrohe 72411701 product individual page {URL["diverter"]}: integral diverter spout for PRESSURE BALANCE valve ONLY, Matte White. Official exact family installation instruction {URL["install"]}: diverter tub spouts 72411 family NEVER with thermostatic mixing trims NOR pressure-balance trim with diverter. Metal tub spout drop only 1/2 or3/4in, 8-18in vertical, exactly ONE elbow and NO PEX/plastic to avoid stacking / leaking at shower head. Original selected thermo 15758701 two-function diverter uses thermostatic cartridge {URL["thermo"]}, separate iBox rough. Two independently manufacturer-supported component modes cannot be combined automatically.

**Path A: retain original owner THERMOSTAT and change spout only**. Hansgrohe individual current Talis S 72410701 Matte White tub spout WITHOUT integral diverter {URL["plain"]} credible candidate retaining original finish. Two-function diverter already in 15758701; factory must explicitly confirm correct two outlets, routing, no blocked drop, actual 01850181 rough and required standard spout connection, hydraulic commission. 72410701 is NOT owner-approved, not an asserted completed whole-system approval.

**Path B: retain original owner diverter spout 72411701, change mixer**. Maker currently lists Ecostat S PRESSURE BALANCE trim family bypass for diverter spout {URL["pressure"]}. Historical maker book documents MATTE WHITE 15739701 candidate {URL["old_pricebook"]}, but current live individual Matte White availability, real existing rough compatibility, cartridge/flow and installer confirmation unverified; cannot silently choose it. PB with built-in diverter also prohibited with an integral diverter spout.

**Path C: full factory-approved alternative control plus rough/spout reroute**, no nominated new SKU, requires owner, architect, licensed plumber and factory signed control/function diagram and complete GC tile/window/glass or tub-flange recovery cost. May have greater cost but avoids speculative rough rewiring.

## Measurable 1529 plumbing shop and installed-scope hold

Four physical tub-instance checklists x six trade stages (24 records), including signed existing 01850181 rough/trim/cartridge identity and current photo, tub-to-valve horizontal and height coordinates, exact spout drop measured against maker 8in MIN and 18in MAX, actual METAL 1/2 or 3/4 pipe and ONE elbow, no PEX, actual finished wall, service access and flange. Sixteen separate floor-to-tile and wall Z finished-wall/rough interface schedules, avoiding fake mortar shim allowances. Actual full-size 1:1 pressure/temperature/diversion/stacking and sealed tub-flange/membrane wall sample needed per unit, never claimed performed.

Keep original wet WALL and NICHE manufacturer permissions separate, Caviar/Tones source and maker wet verification still pending, original tile back/returns/mortar, physical tub flange, movement, actual bath LEVEL original raw numeric wet DCOF required. Tub-only shower PAN N/A. No false reuse of LEVEL test for shower PAN elsewhere in project.

## Bid and trade scope

Licensed plumber+architect approve EXACT selected real trim/spout/rough construction, hydraulic flow, selected matte white compatibility and all fixture penetrations before tile installation; waterproof trade signs substrate+membrane+tub flange+escutcheon method; installer verifies 1:1 selected tile and movement, original numeric wet LEVEL lab, actual wall finish plane and physical grout/trim. GC records separately old ordered/paid material availability, no automatic return credit, demo/patch, wall tile, backer/membrane, tub spout metal drop and labor, inspection rework, current supplier package and full installed bid; owner must sign change order, purchasing after all. User prohibits supplier contact, sample orders, calls, forms or purchases—no outreach performed.

Full original 13 room programs and authentic formal R017 board/champions unchanged, 27 old historical rows, 25 old elevations, 65 trades, 26 physical witnesses, 50 W, 13 exact lab roles, total original material-only 23572.44 and prior 15percent waste once. Original PH2/TX4 historic wall/floor/niche materials ALREADY included, no R42 new quotation assumed. All 13 releases FALSE, no current Chicago stock/quote, true 1529 field or owner approval. Original Reviewer15 FINISHED and original DESIGN worker9 FAILED; no independent Reviewer DONE, global OPEN.
""")
lineage=dict(json.loads(R41.read_text(encoding="utf-8"))["predecessor_signed_file_hashes"])
lineage["R41_FULL"]=P41
meta=dict(round=42,date_local="2026-11-06",
 phase="SUBSTANTIVE_PH2_TX4_FACTORY_THERMOSTAT_DIVERTER_MATTE_WHITE_TUB_ROUGH_13ROOM_GC_OPEN",
 predecessor_signed_file_hashes=lineage,
 focus_rooms=list(FOCUS),physical_tub_copies=4,
 original_selected_Duravit_and_MatteWhite_finish_preserved=True,
 selected_72411701_pressure_balance_ONLY_cannot_use_selected_15758701_thermostat=True,
 original_two_ROOM_physical_4_tub_owners_selected_spout_no_change=True,
 original_27_material_rows=27,original_13room_count=13,original_USD_material_only="23572.44",
 original_15pct_waste_in_historical_gross_once=True,
 factory_source_records=len(fact),three_tub_control_compatibility_branches_per_unit=len(routes_out),
 six_actual_trade_stages_per_physical_unit=len(physical),four_per_unit_tiled_face_rough_Z_interfaces=len(planes),
 original_13room_release_matrix=len(release),
 actual_1529_spout_DROP_measurement_verified=False,
 exact_original_selected_current_trim_and_rough_AS_BUILT_verified=False,
 correct_FACTORY_complete_thermo_or_PB_spout_assembly_signed=False,
 owner_selects_changed_fixture_or_rough=False,source_fixture_silently_substituted=False,
 current_raw_numeric_LEVEL_wet_lab_received=False,
 physical_one_to_one_mockup_and_commission_completed=False,
 actual_paid_credit_current_Chicago_supplier_or_installed_GC_bid=False,
 original_four_specialists_complete=False,original_Reviewer15_DONE=False,
 owner_approved=False,architect_approved=False,plumber_approved=False,
 waterproof_approved=False,tile_approved=False,supplier_approved=False,GC_approved=False,
 purchaser_approved=False,purchase_authorized=False,global_DONE=False,
 files=[dict(path=n,bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for n,v in sorted(DATA.items())])
assert len(DATA)==6
OUT.mkdir(parents=True,exist_ok=False)
for n,data in sorted(DATA.items()):
 with (OUT/n).open("xb") as f:f.write(data)
(OUT/"MANIFEST.json").write_bytes((json.dumps(meta,indent=2)+"\n").encode("utf-8"))
print("R42_PAYLOADS",len(DATA),"R42_MANIFEST_SHA",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
