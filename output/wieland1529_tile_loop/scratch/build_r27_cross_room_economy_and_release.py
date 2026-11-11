"""R27 source-accurate historical cross-room aggregation, optional not-approved pooling, and sequential reservations."""
from pathlib import Path
from decimal import Decimal, ROUND_CEILING
import csv, json, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/integrated-r27-powder-value-and-13room-procurement'
def D(x):return Decimal(str(x))
def n(x):return str(D(x).quantize(D('0.0001')))
def load(path):
    with (ROOT/path).open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    assert rows
    p=OUT/name;assert not p.exists(),name
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)

rooms=json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
byid={r['id']:r for r in rooms};assert len(byid)==13
base=load('deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
assert len(base)==27
original= sum(D(r['historic_usd_two_copies']) for r in base if r['historic_usd_two_copies'])
assert original==D('23572.44')
assert sum(r['historic_niche_excluded_no_scope']=='TRUE' for r in base)==2
g=[]
for r in base:
    name=next((z['carried_description'] for z in byid[r['room']]['carried_tile_rows'] if z['smartsheet_row_id']==r['source_row_id']),None)
    assert name,r['source_row_id']
    gross=r['source_gross_sf_one_copy_waste_15pct_once']
    g.append(dict(room=r['room'],original_source_row_id=r['source_row_id'],original_exact_historic_description=name,
      original_surface=r['source_surface'],original_GROSS_SF_copy_15pct_included_once=gross,
      original_gross_TWO_copies_SF=n(D(gross)*2) if gross else '',
      original_historic_USD_TWO_copies=r['historic_usd_two_copies'],original_primary_niche_NO_SCOPE_NO_ORDER=r['historic_niche_excluded_no_scope'],
      candidate_same_SKU_color_finish_caliber_other_room='UNRESOLVED_MUST_COMPARE_EXACT_FACTORY_LABEL',
      cross_room_combining_requires_owner_finish_and_identical_lot='TRUE',
      actual_cumulative_room_NET_excluding_openings='',measured_LEVEL_DISTINCT_from_PAN='',current_verified_SKU_order_code='',same_lot_supplier_allocated_carton_SF='',same_lot_actual_usable_piece_count='',full_case_reservation_quantity='',attic_stock_allocation='',owner_release_signature='FALSE',architect_release_signature='FALSE',supplier_offer_date='',supplier_Chicago_lot_lead='',GC_installed_bid='',purchase_release='FALSE'))
write('R27_27_HISTORICAL_MATERIAL_ROWS_TO_ACTUAL_MULTI_ROOM_RESERVATION.csv',g)

# Real matching historic color/format and original row identities, NOT authorized consolidation.
groups={
'Tones Sandstone 2x20 Glossy historic NICHE across four baths':[
 ('PH-BATH2','accent'),('PH-BATH3','accent'),('TX-BATH2','accent'),('TX-BATH3','accent')],
'Clara Tierra Madre Caviar 2x8 historic NICHE wet UNLISTED - NEVER RESERVE':[
 ('PH-BATH4','accent'),('TX-BATH4','accent')],
'Cortar Bone 12x24 Soft historic LEVEL (exclude Primary mixed floor)':[
 ('PH-BATH3','floor'),('TX-BATH4','floor')],
'Cortar Grey 12x24 Soft historic LEVEL':[
 ('PH-BATH2','floor'),('TX-BATH3','floor')],
'Vera Forma Earth Lines 2x10 Glossy Relief historic PH POWDER ONLY':[
 ('PH-POWDER','vanity_wall')],
'Vera Forma Indigo Edge 6x6 Glossy Relief historic TX POWDER2 ONLY':[
 ('TX-POWDER2','vanity_wall')],
'Haze Camel/Wheat historic TX POWDER blended dual color NOT separate same-SKU':[
 ('TX-POWDER','vanity_wall')]
}
aggreg=[]
for label,req in groups.items():
    selected=[]
    for rid,surface in req:
        selected += [r for r in base if r['room']==rid and r['source_surface']==surface]
    assert len(selected)==len(req),label
    totalgross=sum(D(r['source_gross_sf_one_copy_waste_15pct_once'])*2 for r in selected)
    totalmoney=sum(D(r['historic_usd_two_copies']) for r in selected)
    issue='Pending exact same manufacturer/product/color/format/caliber/finish and lot; independent owner room approvals, field actual net and lot/case evidence'
    if 'Caviar' in label:issue='HARD EXCLUSION: original Caviar maker individual Wet Areas niche approval absent; historical quote only, NO WET NICHE RESERVATION'
    if 'Haze' in label:issue='Camel and Wheat are DIFFERENT color SKUs: blended historical price/gross cannot be pooled as one actual carton'
    aggreg.append(dict(source_group=label,source_room_ids=';'.join(x[0] for x in req),original_source_row_ids=';'.join(r['source_row_id'] for r in selected),
      original_two_copy_GROSS_SF_15pct_included_once=n(totalgross),original_two_copy_historic_material_only_USD=n(totalmoney),
      no_additional_15pct_on_old_gross='TRUE',verified_identical_SKU_or_color_lot='FALSE',current_same_lot_box_SF='',actual_approved_NET_SF='',current_purchasable_whole_cases='',supplier_current_discount_or_actual_staged_savings='',actual_receiver_split_by_room_and_unit='',
      known_blocker=issue,architect_GC_owner_approved='FALSE',supplier_written_allocation='FALSE',purchase_released='FALSE'))
write('R27_7_SOURCE_SAME_MATERIAL_MULTI_ROOM_GROUPS_AND_EXCLUSIONS.csv',aggreg)

# Cross-room conditional unapproved value-engineering: change rate-class to PH original maker reference. Never installed savings.
ph=byid['PH-POWDER'];tx=byid['TX-POWDER'];tx2=byid['TX-POWDER2']
assert D(ph['carried_quote_material_subtotal_usd_per_unit'])==D('368.18')
assert D(tx['carried_quote_material_subtotal_usd_per_unit'])==D('379.37')
assert D(tx2['carried_quote_material_subtotal_usd_per_unit'])==D('332.10')
haze_old_two=D('379.37')*2
earth_tx_reference=D('31.8')*D('8.20')*2
earth_group_reference=(D('44.9')+D('31.8')+D('40.5'))*D(2)*D('8.20')
actual_powder_old=D(2)*(D('368.18')+D('379.37')+D('332.10'))
assert actual_powder_old==D('2159.30')
cases=[]
for label,description,reference in [
 ('RETENTION','Each powder room keeps own historical dry wall, original gross with waste once',actual_powder_old),
 ('HISTORIC_EQUIVALENT_REFERENCE_NOT_QUOTE','PH keeps Earth Lines, TX Haze fully substitutes Earth Lines at PH old $8.20/SF price reference, TX2 keeps Indigo',actual_powder_old-haze_old_two+earth_tx_reference),
 ('ALL_THREE_EARTH_LINES_CROSS_ROOM_REFERENCE_ONLY','All three dry powder source gross totals at PH old Earth Lines historical rate, without yet adjusting paint landing, color cases or installed work',earth_group_reference)
]:
    cases.append(dict(scenario=label,design_assumption=description,original_entire_three_powder_two_copy_historic_tile_only_USD='2159.30',historical_ph_room_same_product_reference_rate_USD_SF='8.20',analytical_reference_material_USD_TWO_copies=n(reference),
      hypothetical_reference_minus_original_two_copy_USD=n(reference-actual_powder_old),
      is_new_TX_supplier_quote='FALSE',is_current_Chicago_supplier_offer='FALSE',is_signed_owner_material_selection='FALSE',is_comparable_installed_cost='FALSE',net_after_PH_painted_center='NOT_ACCOUNTED_FOR',real_case_rounding_by_individual_color='UNKNOWN',additional_wall_paint_trim_labor='UNKNOWN',lot_and_ETA='UNKNOWN',GC_accepted='FALSE',purchase_released='FALSE'))
write('R27_3_ALTERNATE_POWDER_MATERIAL_REFERENCE_RATE_VALUE_SCENARIOS.csv',cases)

# 13 rooms: sequence is not a generic repeated HOLD; first evidence is room-specific and parent/wet applications distinct.
specific={
'PH-PRIMARY':('PH Brizo 48in Black Onyx LINEAR + BR73480; no niche','Two distinct original raw measured wet LEVEL/PAN certificates, actual 1529 liner/BR73480 field and RL21 7-18mm insert acceptance; WC inherited floor once'),
'PH-BATH2':('Duravit 700332 tub, Hansgrohe Matte White, no tiled PAN','Factory-approved 15758701 thermostatic + 72411701 pressure-balance-only spout resolution, tub 59in/59.496in W1 flange/finish clearance and Sapphire wall approval'),
'PH-BATH3':('Owner TUB versus WALKIN unselected; selected Delta DT062412 POINT only if WALKIN; basin unselected','Owner chooses exact program and basin; tub future waste versus selected shower-point/4-plane small PAN maker exact lab, not cross-applied'),
'PH-BATH4':('Confirmed Brizo Black Onyx square POINT walkin with separate PAN and LEVEL','Survey owner35/drawing27 SF plus Soft/AntiSlip, Ribbed/Clara wet proof FAIL and 214.4-SF vendor source audit NOT payable shortage'),
'PH-POWDER':('Selected Brizo T65722LF-GL Luxe Gold WALL/R65700 + Earth Lines relief DRY; WOOD floor','Approve real faucet/basin reach and actual relief-to-PAINT flat center width, exposed two transition lengths, cut >=3in and per unit mockup'),
'PH-WC':('Inherits PH Primary LEVEL, no separate tile or niche','Physical threshold + toilet flange and same parent lot floor allocation, do not create second WC order'),
'TX-PRIMARY':('TX Black Onyx 48in LINEAR/BR73480 and NO niche; TX WC LEVEL inherited','Correct duplicated BR73480 mistaken wall trim in BOM, verify raw exact wet LEVEL/PAN lab and TXWC continuity, manufacturer drain secondary path'),
'TX-BATH2':('Selected Duravit tub with Hansgrohe Chrome, basin unselected, PAN N/A','Survey 62.484 W1 vs 59in nominal tub/filler and exact wet Copper/Sandstone, original LEVEL raw test and owner basin'),
'TX-BATH3':('TUB/WALKIN unselected; Brizo Black Onyx square POINT only for WALKIN','Owner branch, tub waste if elected vs real four-plane POINT PAN if shower; maker original wet LEVEL/PAN lab'),
'TX-BATH4':('Duravit tub Matte White; no PAN, flat Charcoal wet WALL conditional Soho Ivory NICHE','Talis spout/Ecostat compatibility, corrected Westbrass trim, original Caviar wet FAIL, 60in W1 vs 59in tub flange'),
'TX-POWDER':('Unselected AXOR One 48140991 cross handle OR Metropol 32526141 single lever WALL trim, wood floor','Owner elect exactly one trim and finish, Metropol maker-matched 13622181 rough only if that path; actual original source rough inventory/evidence and Haze 70:30 single wall cut'),
'TX-POWDER2':('Selected DECK Hansgrohe 73072341 Brushed Black Chrome; basin UNSELECTED, wood floor','Owner basin/drain overflow then counter drilling/fixture reach, 6x6 Indigo nominal grout/case historic 7.34 versus 30pcs discrepancy; no wall rough'),
'TX-WC':('Inherits TX Primary LEVEL, no separate tile or niche','Single parent TX Primary floor lot/level threshold and water closet flange proof, no extra case ordering')}
assert set(specific)==set(byid)
out=[]
for rid,x in byid.items():
    fixture,critical=specific[rid]
    kind=('DRY_WOOD_NO_WET_LEVEL_OR_PAN' if rid in ['PH-POWDER','TX-POWDER','TX-POWDER2'] else
          'WC_LEVEL_INHERITS_PARENT_ONCE_PAN_NA' if rid in ['PH-WC','TX-WC'] else
          'DURAVIT_TUB_LEVEL_EXACT_RAW_LAB_PAN_NA' if rid in ['PH-BATH2','TX-BATH2','TX-BATH4'] else
          'BATH3_OWNER_TUB_WALKIN_UNSELECTED_LEVEL_AND_CONDITIONAL_PAN' if rid in ['PH-BATH3','TX-BATH3'] else
          'SELECTED_SHOWER_LEVEL_AND_DISTINCT_LINEAR_POINT_PAN_RAW_LAB')
    out.append(dict(room=rid,original_board_status=x['status'],original_champion=x['champion_id'] or '',original_score='' if x['champion_score'] is None else str(x['champion_score']),copies=2,
      original_historical_material_only_USD_copy=str(x['carried_quote_material_subtotal_usd_per_unit']),selected_hardware_program_and_selection_hold=fixture,
      reason_this_room_must_not_pooled_blindly=critical,wet_LEVEL_and_PAN_applicability=kind,
      scope_first_owner_decision='OWNER provide signed selected program/finish and room cap; actual Bath3 branch/basins conditional' if rid in ['PH-BATH3','TX-BATH3','TX-BATH2','TX-POWDER2','TX-POWDER','PH-POWDER'] else 'Retain original source plumbing; owner signs any revised finish/sample only',
      architect_measured_1529_and_calibrated_tile_elevation='Actual PH/TX field W1/W2/W3/threshold/vanity/substrate by correct 1529 identity, not 1527',
      plumber_factory_selected_rough_and_fixture_required=critical,
      waterproof_submittal_required=('N/A DRY WOOD OR WC' if kind.startswith(('DRY_','WC_')) else 'Manufacturer-selected tub flange/liner/rough/threshold/penetrations and specified pre-tile test if applicable'),
      tile_exact_maker_application_and_numeric_lab=('DRY WALL maker-only, numeric wet floor N/A' if kind.startswith('DRY_') else 'Parent LEVEL numeric lab ONCE' if kind.startswith('WC_') else 'Exact individual wet WALL/NICHE and raw numerical LEVEL, separate PAN only for installed shower'),
      supplier_actual_same_SKU_lot_current_case_stock_ETA='UNKNOWN, requires exact maker color/format/finish SKU/lot/qty, verified cases and dated Chicago allocation',
      estimate_actual_installed_material_trim_labor_and_tax='UNKNOWN, room-level trade bid after measured NET and one independent new cut factor',
      sample_and_camera_acceptance='Physical 1:1 complete maker, grout, light and actual 1529 camera/survey; all NOT CREATED',
      owner_signed='FALSE',architect_signed='FALSE',plumber_signed='FALSE',waterproof_signed='FALSE',tile_installer_signed='FALSE',GC_signed='FALSE',supplier_offer_verified='FALSE',purchasing_release='FALSE'))
write('R27_13_ROOM_SEQ_OWNER_ARCH_PLUMB_WP_TILE_SUPPLIER_RESERVATION_RELEASE.csv',out)
print('PASS R27: 27 exact old source row IDs, 7 genuine/caution aggregation classes, 3 not-quoted powder rate comparisons, 13 program-specific trade release chains, full historical $23572.44')
