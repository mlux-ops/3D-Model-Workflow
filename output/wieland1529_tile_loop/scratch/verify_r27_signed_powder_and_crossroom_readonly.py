"""Strict READ-ONLY R27 signature, arithmetic, owner/gate, R014/R016/R017 chain verification."""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING
import hashlib,json,csv,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/integrated-r27-powder-value-and-13room-procurement'
def fp(path):
    b=path.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
EXPECTED='5523674db6ef75811b25260405806ef8993329a70e41aec042f5ec63d852f59b'
manifest=OUT/'MANIFEST.json'
assert fp(manifest)['sha256']==EXPECTED
m=json.loads(manifest.read_text(encoding='utf-8'))
assert len(m['outputs'])==12 and all(fp(OUT/n)==v for n,v in m['outputs'].items())
assert m['original_room_ids']==13 and m['original_tile_material_rows']==27 and m['original_provisional_wall_keys']==25 and m['original_trade_actions']==65
assert m['original_four_unit_material_only_USD']=='23572.44' and m['powder_original_two_copy_three_room_subset_USD']=='2159.30'
assert m['original_gross_waste_counted_once']=='15percent' and m['two_excluded_primary_niche_references_NO_SCOPE_NO_ORDER']==2
for key in ['owner_approved','architect_released','plumber_released','waterproof_installer_released','tile_installer_released','GC_released','supplier_offer_verified','purchasing_released','entire_13_room_Reviewer_GLOBAL_DONE']:
 assert m[key] is False,key
assert m['R014_original_critic_reports']==6 and m['R014_required']==8 and m['original_DESIGN_worker9']=='FAILED'
assert m['independent_nonPro_Reviewer_worker15']=='FINISHED_NONREVIVABLE' and m['R27_independent_acceptance'] is None
assert m['R017_independent_predispatch_clearance'] is None and not m['R27_new_blind_dispatch']
assert m['R016_original_critic_dispatch']=='NOT_DISPATCHED' and m['R017_original_critic_dispatch']=='NOT_DISPATCHED'
for tag,p in [('R26','deliverables/integrated-r26-tx-primary-and-three-duravit-tubs/MANIFEST.json'),
 ('R23_FIXED_LOCAL_NOT_ACCEPTED','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R017','state/ROUND017_SUBMISSION.json'),
 ('R016','state/ROUND016_SUBMISSION.json')]:
 assert fp(ROOT/p)['sha256']==m['predecessor_manifest_sha256'][tag]
assert m['predecessor_manifest_sha256']['R26']=='16c02f7c01da25457b1ae53860b6166a6b82bb956d319432298a8fbc7d24fb74'
assert m['predecessor_manifest_sha256']['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
assert m['predecessor_manifest_sha256']['R23_FIXED_LOCAL_NOT_ACCEPTED']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
rs=json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert len(rs)==13
ids={r['id'] for r in rs}
orig=[]
with (ROOT/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:orig=list(csv.DictReader(f))
assert len(orig)==27
origsum=sum(Decimal(r['historic_usd_two_copies']) for r in orig if r['historic_usd_two_copies'])
assert origsum==Decimal('23572.44')
opts=read('R27_9_THREE_POWDER_MANUFACTURER_PHYSICAL_GOOD_BETTER_BEST.csv')
assert len(opts)==9 and {r['room'] for r in opts}=={'PH-POWDER','TX-POWDER','TX-POWDER2'}
assert all(r['no_tiled_shower_PAN_NA']=='TRUE' and r['wood_floor_numeric_wet_LEVEL_NA']=='TRUE' for r in opts)
assert all(r['owner_approval']=='FALSE' and r['procurement_release']=='FALSE' for r in opts)
cut=read('R27_PH_BRIZO_4_PAINT_RELIEF_WIDTH_TILE_EDGE_COST_SCENARIOS.csv')
assert len(cut)==4
c16=next(r for r in cut if r['hypothetical_owner_NOT_SELECTED_full_height_flat_center_width_in']=='16')
assert abs(Decimal(c16['nominal_symmetric_end_cut_each_flank_in'])-Decimal('3.547'))<Decimal('0.001')
assert Decimal(c16['hypothetical_new_exposed_transition_vertical_LF_two_edges'])==Decimal('18.5')
assert all(r['owner_signed']=='FALSE' and r['purchase_released']=='FALSE' for r in cut)
tx=read('R27_TX_HAZE_3_SINGLE_WALL_COLOR_ALLOCATION_AND_CUT_STUDIES.csv')
assert len(tx)==3
for r in tx:
 assert Decimal(r['conditional_area_share_Camel'])+Decimal(r['conditional_area_share_Wheat'])==Decimal('1')
 assert abs(Decimal(r['illustrative_original_Camel_SHARE_GROSS_SF_copy'])+Decimal(r['illustrative_original_Wheat_SHARE_GROSS_SF_copy'])-Decimal('31.8'))<Decimal('0.0001')
 assert r['manufacturer_13622181_matches_only_Metropol']=='TRUE'
 assert r['AXOR_48140991_trim_or_Metropol_32526141_trim_owner_unselected']=='TRUE'
 assert r['purchase_released']=='FALSE'
ind=read('R27_TX2_INDIGO_4_HISTORIC_CARTON_THRESHOLD_SENSITIVITIES.csv')
assert len(ind)==4
assert all(Decimal(r['nominal_horiz_symmetric_end_cut_in'])==Decimal('4.3985') for r in ind)
assert all(Decimal(r['nominal_vertical_top_bottom_cut_in'])==Decimal('3.3750') for r in ind)
for r in ind:
 gross=Decimal(r['hypothetical_two_copy_new_GROSS_SF_not_measured'])
 calc=(gross/Decimal('7.34')).to_integral_value(rounding=ROUND_CEILING)
 assert int(r['hypothetical_mathematically_rounded_cases_IF_7p34_same_lot'])==calc
 assert r['actual_2026_lot_or_carton_verified']=='FALSE' and r['purchase_release']=='FALSE'
assert {(r['hypothetical_two_copy_new_GROSS_SF_not_measured'],r['hypothetical_mathematically_rounded_cases_IF_7p34_same_lot']) for r in ind} >= {('81.0000','12'),('80.7400','11')}
history=read('R27_27_HISTORICAL_MATERIAL_ROWS_TO_ACTUAL_MULTI_ROOM_RESERVATION.csv')
assert len(history)==27
assert [(r['room'],r['original_source_row_id']) for r in history]==[(r['room'],r['source_row_id']) for r in orig]
assert sum(Decimal(r['original_historic_USD_TWO_copies']) for r in history if r['original_historic_USD_TWO_copies'])==Decimal('23572.44')
assert sum(r['original_primary_niche_NO_SCOPE_NO_ORDER']=='TRUE' for r in history)==2
assert all(r['purchase_release']=='FALSE' and r['current_verified_SKU_order_code']=='' for r in history)
groups=read('R27_7_SOURCE_SAME_MATERIAL_MULTI_ROOM_GROUPS_AND_EXCLUSIONS.csv')
assert len(groups)==7
sand=next(r for r in groups if r['source_group'].startswith('Tones Sandstone'))
assert Decimal(sand['original_two_copy_GROSS_SF_15pct_included_once'])==Decimal('51.6400')
caviar=next(r for r in groups if r['source_group'].startswith('Clara Tierra'))
assert 'NEVER RESERVE' in caviar['source_group'] and r['purchase_released']=='FALSE' if False else 'NEVER RESERVE' in caviar['source_group']
assert all(r['purchase_released']=='FALSE' and r['supplier_written_allocation']=='FALSE' for r in groups)
pricing=read('R27_3_ALTERNATE_POWDER_MATERIAL_REFERENCE_RATE_VALUE_SCENARIOS.csv')
assert len(pricing)==3
ref=next(r for r in pricing if r['scenario']=='HISTORIC_EQUIVALENT_REFERENCE_NOT_QUOTE')
assert Decimal(ref['hypothetical_reference_minus_original_two_copy_USD'])==Decimal('-237.2200')
assert all(r['is_new_TX_supplier_quote']=='FALSE' and r['purchase_released']=='FALSE' for r in pricing)
release=read('R27_13_ROOM_SEQ_OWNER_ARCH_PLUMB_WP_TILE_SUPPLIER_RESERVATION_RELEASE.csv')
assert len(release)==13 and {r['room'] for r in release}==ids
assert all(r['supplier_offer_verified']=='FALSE' and r['purchasing_release']=='FALSE' for r in release)
units=read('R27_6_PHYSICAL_POWDER_UNIT_1TO1_MOCKUP_FAUCET_FIELD_SHOP_CLOSURES.csv')
assert len(units)==6 and {(r['room'],r['physical_room_number']) for r in units}=={('PH-POWDER','405A'),('PH-POWDER','405B'),('TX-POWDER','102A'),('TX-POWDER','102B'),('TX-POWDER2','009A'),('TX-POWDER2','009B')}
assert all(r['purchaser_released']=='FALSE' and r['ACTUAL_net_tile_SF']=='' and r['physical_mockup_installed']=='FALSE' and r['camera_render_created']=='FALSE' for r in units)
with (ROOT/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==25
with (ROOT/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==65
for name in ['R27_FACTORY_FAUCET_BOM_AND_DRY_TILE_MANUFACTURER_FACTS.md','START_HERE_R27.md','R27_THREE_POWDER_AND_13_ROOM_OWNER_ARCHITECT_GC_DECISION_BOOK.md']:
 for link in re.findall(r'\]\(([^)]+)\)',(OUT/name).read_text(encoding='utf-8')):
  assert link.startswith(('https://','http://')) or (OUT/link).exists(),(name,link)
report=(ROOT/'state/ROUND027_INDEPENDENT_NONPRO_REVIEWER_REPORT_PREPARED_NOT_SENT.md').read_text(encoding='utf-8')
assert len(report)<=4000
assert [line for line in report.splitlines() if line in ('GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT')]==['GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT']
status=(ROOT/'state/ROUND027_CURRENT_ACTIVE_BOARD_FIVE_LINE_STATUS.txt').read_text(encoding='utf-8').splitlines()
assert len(status)==5 and status[0]=='STATUS round=017 phase=4-deepen'
assert (ROOT/'state/LEDGER.md').read_text(encoding='utf-8').count('## R27 maker-specific three powder 1:1 value engineering, true case sensitivity and 13-room controlled procurement')==1
s17=json.loads((ROOT/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert s17['predispatch_reviewer_verdict'] is None and s17['critic_dispatch']=='NOT_DISPATCHED' and len(s17['confidential_prime_only_mappings'])==4
print('PASS R27 READ-ONLY signed 12 output SHA+bytes, 13/27/25/65 original source counts, $23572.44 and powder $2159.30 original waste ONCE, PH/ TX/ TX2 mathematical scenarios, six actual rooms, 13 sequential releases, no Reviewer/critic/owner/GC/PO invented')
print('R27_SHA',EXPECTED)
