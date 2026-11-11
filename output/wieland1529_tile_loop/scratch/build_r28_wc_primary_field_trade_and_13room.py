"""New cross-room WC shop sequencing and all-13-room evidence release without modifying historical data."""
from pathlib import Path
import json,csv
from decimal import Decimal
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r28-wc-primary-floor-flange-threshold'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
 p=O/name;assert rows and not p.exists(),name
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
rs=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
ids={x['id'] for x in rs}
assert len(ids)==13
orig=read(R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
assert len(orig)==27 and sum(Decimal(x['historic_usd_two_copies']) for x in orig if x['historic_usd_two_copies'])==Decimal('23572.44')
root27=read(R/'deliverables/integrated-r27-powder-value-and-13room-procurement/R27_13_ROOM_SEQ_OWNER_ARCH_PLUMB_WP_TILE_SUPPLIER_RESERVATION_RELEASE.csv')
assert len(root27)==13

focus={
'PH-WC':dict(parent='PH-PRIMARY',copies=['313A','313B'],parent_copies=['304A','304B'],floor='Bone FT1 Cortar 24x48 Anti-Slip v4 LEVEL; no separate tile row',area='15',critical='No WC geometry/door/toilet assigned: original Primary plumbing TOTO Nexus MS642124CEFG#01 Cotton 12-in nominal UniFit; location in WC not verified',first='True flange-to-finished-wall, door swing/clear, sample actual Bone Anti-Slip and owner sign separate WC Soft/Anti-Slip transition'),
'TX-WC':dict(parent='TX-PRIMARY',copies=['203A','203B'],parent_copies=['202A','202B'],floor='Clay FT2 Cortar 24x48 Anti-Slip v4 LEVEL; no separate tile row',area='14',critical='TX 203A unplaced source geometry, 203B prior 14SF unverified, original Nexus TOTO in TX Primary group only',first='Reconcile 203A/203B as-built 1529 and toilet placement, true flange and door, Clay maker exact LEVEL tile and parent Soft finish change'),
'PH-PRIMARY':dict(parent='PH-PRIMARY',copies=['304A','304B'],parent_copies=['313A','313B'],floor='Bone Soft 24x48 source LEVEL plus 12x24 Anti-Slip conditional LINEAR PAN, quoted blended original',area='103',critical='Owner original v4 may require Anti-Slip whole LEVEL, quoted Soft conflicts with WC Anti-Slip; Brizo 48-in LINEAR BT0734816-BNX + BR73480 separate rough remains, no niche',first='Separate measured LEVEL bath/ WC 15SF/ LINEAR pan NET, exact raw maker numeric LEVEL/PAN and optional approved floor-to-WC joint / toilet flange'),
'TX-PRIMARY':dict(parent='TX-PRIMARY',copies=['202A','202B'],parent_copies=['203A','203B'],floor='Clay Soft 24x48 source LEVEL plus 12x24 Anti-Slip conditional LINEAR PAN, quoted blended original',area='87',critical='WC Clay Anti-Slip v4 vs quoted Primary Soft; historical double BR73480 SKU mislabeled wall trim, selected one factory rough + Black Onyx 48-in LINEAR no niche',first='One-rough manufacturer BOM, exact same-SKU LEVEL vs separately measured PAN test, 203A location, WC doorway shift and TOTO install template')
}
rows=[]
for room,z in focus.items():
 for i,u in enumerate(z['copies']):
  rows.append(dict(room=room,physical_unit_room=u,associated_cross_room=z['parent_copies'][i],original_specific_material_and_program=z['floor'],old_source_prior_area_SF=z['area'],first_risk=z['critical'],requested_evidence=z['first'],
    step_1_OWNER='Original finish and WC/Primary threshold/optional base sign; no owner selection presumed',
    step_2_ARCHITECT='Actual certified correct 1529 floor polygon, parent-WC door leaf, W1/W3 wet Primary only, all openings and actual floor finish datum; WC no tiled wall W1/W3',
    step_3_PLUMBER='Original Nexus MS642124CEFG#01 location, 12 versus optional 14 UniFit, 0GU186-A floor template, waste flange/water stop; selected Brizo LINEAR+BR73480 only in primary shower',
    step_4_WATERPROOF='WC: N/A separate shower pan/niche/wet-wall or flood; confirm splash/counter edge only. PARENT: Brizo LINEAR pan membrane and separate slope datum, separate wet walls and selected tub',
    step_5_TILE='Original Bone/Clay 24x48 Anti-Slip WC manufacturer exact SKU/caliper/lab; demonstrate 24x48 vs conditional 12x24 physical cuts >=3in, grout, door/soft transition, no unsupported toilet anchors',
    step_6_SUPPLIER='Written exact individual color-format-finish-SKU/lot/box usable coverage, raw exact wet LEVEL and separate LINEAR PAN lab, Chicago lot/ETA, full delivered price and GC installed thresholds',
    independent_source_1529_survey_completed='FALSE',current_tile_24x48_AntiSlip_individual_maker_SKU_verified='FALSE',TOTO_0GU186A_template_physically_checked='FALSE',TOTO_UniFit_12or14_selected_by_site='FALSE',raw_exact_numeric_LEVEL_wet_DCOF_provided='FALSE',raw_exact_numeric_LINEAR_PAN_wet_DCOF_provided='FALSE_IF_PRIMARY',actual_wc_entrance_threshold_profile_verified='FALSE',actual_net_measured='',
    final_owner_signature='FALSE',architect_signature='FALSE',plumber_signature='FALSE',waterproof_signature='FALSE',installer_signature='FALSE',GC_signature='FALSE',supplier_actual_offer_signature='FALSE',purchasing_release='FALSE'))
assert len(rows)==8
write('R28_8_PHYSICAL_PARENT_WC_TOILET_DOOR_FLOOR_FINISH_FACTORY_SHOP_WITNESSES.csv',rows)

scope={
'PH-PRIMARY':('NEXUS SOURCE ONLY IN PRIMARY, PH WC location NOT certified','PH original mixed Soft LEVEL/Anti-Slip PAN plus seeded WC Bone Anti-Slip','Original maker exact Bone Soft or v4 Anti-Slip level wet lab, and separate Brizo LINEAR PAN maker lab; R25 wet-wall relief not inheritable','No extra primary niche; preserve BT0734816-BNX/BR73480 Black Onyx and separate Duravit tub','Sign bath/WC same lot if owner changes entire LEVEL, distinct nonoverlapping PAN and WC source once'),
'PH-BATH2':('Duravit TUB Matte White Hansgrohe','Individually wet-listed Sapphire wall, Sandstone niche; LEVEL old Grey Soft raw exact lab missing','Maker-specific Sapphire WALL/NICHE and bath LEVEL original measured wet numeric lab, PAN N/A TUB','Selected 15758701 thermostat vs Talis 72411701 pressure-balance-only spout factory clash','Accept factory valve/tub flange/59in nominal vs59.496in provisional alcove, signed 1529 field clearance'),
'PH-BATH3':('Owner TUB/WALK-IN UNSELECTED; PH basin UNSELECTED','Opal original wall wet permission unverified; Sandstone niche PASS historical','Original Opal wet wall fail, LEVEL raw missing, conditional POINT PAN original raw missing if WALK-IN','Selected Delta DT062412 Chrome POINT shower only; future tub separate waste','Owner sign bath program and basin; TUB waste/overflow if chosen or small-format four-plane POINT PAN if walk-in'),
'PH-BATH4':('CONFIRMED WALK-IN Brizo BNX square POINT','Ribbed Bone relief original wet wall unlisted, Clara Caviar niche unlisted','Separate actual LEVEL and four-plane POINT PAN raw lab plus correct independently wet-authorized wall/niche','BT062415-BNX 4in Black Onyx square POINT, never tub or LINEAR','Resolve 35 versus27SF and Soft/Anti-Slip/214.4SF vendor history no payable shortage; manufacturer wet approvals'),
'PH-POWDER':('Brizo Luxe Gold T65722LF-GL WALL with R65700','Earth Lines 2x10 glossy relief DRY wall and WOOD floor','Wet WALL/NICHE, bath LEVEL/PAN N/A DRY','Planar painted center optional unapproved, actual gasket/9-11/16in reach; original selected Brizo retained','R27 0/12/16/20 center scenario owner choice and actual 1:1 rough/paint/edge/wood sample, no mockups done'),
'PH-WC':('Original Primary Nexus MS642124CEFG#01 attribution unverified','v4 Bone 24x48 Anti-Slip WC LEVEL only and NO separate WC tile row','Individual exact original numeric WC LEVEL maker lab required; shower PAN/WALL/NICHE N/A','TOTO 12in UniFit TSU10W.12 optional14 TSU10W.14 and 0GU186-A, no second fixture purchase','Door/FFL/Bone Soft vs Anti-Slip threshold joint, true WC 15SF polygon, child of parent material allocation'),
'TX-PRIMARY':('TX Nexus source in Primary group, TX WC location NOT certified','Clay Soft 24x48 quoted LEVEL /12x24 Anti-Slip original PAN and v4 Clay Anti-Slip WC','Exact Clay size x finish measured bath LEVEL lab and separate sloped LINEAR PAN lab','Brizo BT0734816-BNX plus only one separately required BR73480; correct source duplicate wall edge label without writing Smartsheet','Measured Primary+WC lot-level reserve once, 203A unplaced and CW threshold/UniFit clearances'),
'TX-BATH2':('Duravit tub Chrome Hansgrohe; owner basin UNSELECTED','Copper wall / Sandstone niche historical wet permissions, old Clay Soft LEVEL','Exact individual wet WALL/NICHE permissions and raw numeric LEVEL lab, tiled PAN N/A','Selected tub wall/flange and waste/Chrome rough, no shower PAN','Owner basin later, field 62.484in nominal alcove vs59in tub end support and dry floor transition'),
'TX-BATH3':('Owner TUB/WALK-IN UNSELECTED','Emerald wet wall / Sandstone niche individual historical wet permissions, Grey Soft LEVEL source','LEVEL raw numerical maker lab missing, POINT PAN separate only if WALK-IN','Brizo BT062415-BNX Black Onyx square POINT for walk-in only; tub waste unselected','Signed owner branch, field 1529 and wet-membrane, no copied PH basin problem'),
'TX-BATH4':('Duravit tub Matte White Hansgrohe','Flat Charcoal wet wall; original Caviar niche unlisted, conditional Soho Ivory wet-listed','LEVEL raw exact maker numeric lab; PAN N/A TUB; original Caviar niche wet FAIL','Talis 72411701 spout pressure-balance-only vs selected 15758701 thermostat and flange','60in source W1 vs 59in tub must physically fit, waterproof all three wall interfaces and source drain'),
'TX-POWDER':('AXOR One 48140991 CROSS or Hansgrohe Metropol 32526141 SINGLE WALL trims unselected','Haze Camel/Wheat 70/30 matte one DRY wall + wood','Wet WALL/NICHE/LEVEL/PAN N/A DRY','Manufacturer 13622181 compatible only with Metropol trim if owner chooses, NOT AXOR rough','Owner choose trim, signed true actual site rough/escutcheon and matching dry face, no random mixing'),
'TX-POWDER2':('Tecturis E 73072341 Brushed Black Chrome DECK, basin UNSELECTED','Indigo Edge 6x6 DRY relief one vanity wall and wood','Wet WALL/NICHE/LEVEL/PAN N/A DRY','No wall rough, no counter drilling; original 30pcs/7.34SF historic case contradiction','Owner basin/drain overflow and manufacturer 1:1 deck dimension/trim; R27 cartons not current case stock'),
'TX-WC':('TX Primary Nexus one-piece source, WC attribution unverified','v4 Clay 24x48 Anti-Slip LEVEL with no separate purchased tile','Exact individual Clay LEVEL manufacturer wet raw lab required, PAN/WALL/NICHE N/A','TOTO UniFit factory template/ flange, field TX 203A originally unplaced','Do not duplicate 14SF WC source, resolve 203A/203B geometry and parent Clay Soft-to-AntiSlip doorway')
}
assert set(scope)==ids
out=[]
for room in rs:
 rid=room['id'];fx,base,lab,plumb,first=scope[rid]
 out.append(dict(room=rid,source_board_status=room['status'],source_champion=room['champion_id'] or '',source_board_score='' if room['champion_score'] is None else str(room['champion_score']),
  source_two_copies=2,historic_material_only_USD_copy=str(room['carried_quote_material_subtotal_usd_per_unit']),
  selected_fixture_and_program=fx,currently_scheduled_tile_wall_floor_niche_scheme=base,
  individual_maker_WALL_NICHE_and_separate_LEVEL_PAN_RAW_numeric_application=lab,plumber_and_rough_compatibility=plumb,
  specific_owner_architect_GC_first_evidence_priority=first,
  physical_sample_mockup_and_source_true_camera='Request actual manufacturer physical piece/finish and original correct 1529 field view, not produced; no false competitor photo',
  source_level_wall_shop='Original 25 provisional W1-W3 if actual tiled walls, NO WC W1/W3 tiled elevations; exact measured 1529 source or null',
  supplier_case_and_Chicago_offer='Actual exact SKU/color/size/finish/lot/stock/usable box SF/current local quote NULL, all maker targets not numeric lab',
  all_new_selected_owner_alternatives='FALSE',owner_approved='FALSE',architect_release='FALSE',plumber_release='FALSE',waterproof_installer_release='FALSE',tile_installer_release='FALSE',GC_release='FALSE',supplier_offer_verified='FALSE',material_reservation_released='FALSE',purchase_authorized='FALSE'))
write('R28_13_ROOM_OWNER_CONSTRUCTION_AND_MAKER_LEVEL_PAN_RELEASE_DEPENDENCY.csv',out)

case=[]
for rid,area,color in [('PH-WC',15,'Bone'),('TX-WC',14,'Clay')]:
 for allowance in ['0','0.10','0.15']:
  for usable_carton in ['8','16']:
   new_net=Decimal(str(area))
   theoretical_need=new_net*(1+Decimal(allowance))
   import math
   orders=math.ceil(theoretical_need/Decimal(usable_carton))
   case.append(dict(room=rid,original_provisional_floor_area_SF=str(area),original_parent_gross_includes_WC_once='TRUE',
    scenario_independent_new_NET_SOURCE_UNVERIFIED=str(area),hypothetical_NEW_once_only_cut_factor=allowance,fictional_carton_usable_SF_sensitivity_only=usable_carton,
    theoretical_new_need_SF=str(theoretical_need.quantize(Decimal('.0001'))),theoretical_ceiling_case_count_if_this_single_wc_alone=orders,
    DO_NOT_ADD_TO_parent_quote_gross_or_order='TRUE',same_lot_pool_parent_ROOM_requires_approved_actual_TOTAL_NET='TRUE',
    manufacturer_exact_carton_for_Color24x48AntiSlip_verified='FALSE',actual_approved_NEW_waste_factor='',source_current_Chicago_case_coverage='',actually_computed_shared_primary_wc_order_cases='',
    current_dated_supplier_full_price='',owner_signed='FALSE',supplier_lot_reserved='FALSE',purchasing_release='FALSE'))
assert len(case)==12
write('R28_12_WC_HYPOTHETICAL_STANDALONE_CASE_LEVEL_SENSITIVITIES_NOT_ORDER.csv',case)
print('PASS R28 8 distinct parent-WC factory / field fixture witness rows, 13 room-specific original wet gate releases, 12 hypothetical WC-alone carton sensitivities NO ADDITIONAL ORDER')
