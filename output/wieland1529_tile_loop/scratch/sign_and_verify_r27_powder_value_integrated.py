"""Create immutable SHA+byte manifest for genuine R27 additive owner/GC studies.
Source approvals and historical R12-R26 files never overwritten.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,csv,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/integrated-r27-powder-value-and-13room-procurement'
FILES=[
 'START_HERE_R27.md',
 'R27_FACTORY_FAUCET_BOM_AND_DRY_TILE_MANUFACTURER_FACTS.md',
 'R27_THREE_POWDER_AND_13_ROOM_OWNER_ARCHITECT_GC_DECISION_BOOK.md',
 'R27_9_THREE_POWDER_MANUFACTURER_PHYSICAL_GOOD_BETTER_BEST.csv',
 'R27_PH_BRIZO_4_PAINT_RELIEF_WIDTH_TILE_EDGE_COST_SCENARIOS.csv',
 'R27_TX_HAZE_3_SINGLE_WALL_COLOR_ALLOCATION_AND_CUT_STUDIES.csv',
 'R27_TX2_INDIGO_4_HISTORIC_CARTON_THRESHOLD_SENSITIVITIES.csv',
 'R27_27_HISTORICAL_MATERIAL_ROWS_TO_ACTUAL_MULTI_ROOM_RESERVATION.csv',
 'R27_7_SOURCE_SAME_MATERIAL_MULTI_ROOM_GROUPS_AND_EXCLUSIONS.csv',
 'R27_3_ALTERNATE_POWDER_MATERIAL_REFERENCE_RATE_VALUE_SCENARIOS.csv',
 'R27_13_ROOM_SEQ_OWNER_ARCH_PLUMB_WP_TILE_SUPPLIER_RESERVATION_RELEASE.csv',
 'R27_6_PHYSICAL_POWDER_UNIT_1TO1_MOCKUP_FAUCET_FIELD_SHOP_CLOSURES.csv'
]
assert len(FILES)==12 and all((OUT/n).is_file() for n in FILES)
def fp(p):
 b=p.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def data(n):
 with (OUT/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
options,paint,haze,indigo,history,groups,price,release,units=[data(n) for n in FILES[3:]]
assert list(map(len,[options,paint,haze,indigo,history,groups,price,release,units]))==[9,4,3,4,27,7,3,13,6]
focus={'PH-POWDER','TX-POWDER','TX-POWDER2'}
rooms=json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
roomids={r['id'] for r in rooms};assert len(roomids)==13
assert {r['room'] for r in options}=={r['room'] for r in units}==focus
assert {r['room'] for r in release}==roomids
assert len({(r['room'],r['tier']) for r in options})==9
assert len({(r['room'],r['physical_room_number']) for r in units})==6
assert all(r['wood_floor_numeric_wet_LEVEL_NA']=='TRUE' and r['no_tiled_shower_PAN_NA']=='TRUE' and r['procurement_release']=='FALSE' for r in options)
assert all(r['purchaser_released']=='FALSE' and r['ACTUAL_net_tile_SF']=='' and r['physical_mockup_installed']=='FALSE' and r['camera_render_created']=='FALSE' for r in units)
assert all(r['purchasing_release']=='FALSE' and r['supplier_offer_verified']=='FALSE' for r in release)
assert all(r['original_primary_niche_NO_SCOPE_NO_ORDER']=='TRUE' for r in history if r['original_surface']=='accent' and not r['original_historic_USD_TWO_copies'])
assert len([r for r in history if r['original_primary_niche_NO_SCOPE_NO_ORDER']=='TRUE'])==2
assert sum(Decimal(r['original_historic_USD_TWO_copies']) for r in history if r['original_historic_USD_TWO_copies'])==Decimal('23572.44')
assert sum(Decimal(r['original_historic_USD_TWO_copies']) for r in history if r['room'] in focus)==Decimal('2159.30')
assert all(r['purchase_release']=='FALSE' and r['current_verified_SKU_order_code']=='' for r in history)
assert all(r['verified_identical_SKU_or_color_lot']=='FALSE' and r['purchase_released']=='FALSE' for r in groups)
assert all(r['purchase_released']=='FALSE' and r['is_current_Chicago_supplier_offer']=='FALSE' for r in price)
assert {r['hypothetical_owner_NOT_SELECTED_full_height_flat_center_width_in'] for r in paint}=={'0','12','16','20'}
assert all(r['owner_signed']=='FALSE' for r in paint)
assert all(r['AXOR_48140991_trim_or_Metropol_32526141_trim_owner_unselected']=='TRUE' and r['purchase_released']=='FALSE' for r in haze)
assert {r['hypothetical_mathematically_rounded_cases_IF_7p34_same_lot'] for r in indigo}=={'11','12'}
assert all(r['purchase_release']=='FALSE' and r['owner_selected_basin_or_deck_holes']=='FALSE' for r in indigo)
old=csv.DictReader((ROOT/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig'))
old=list(old)
assert [(r['room'],r['source_row_id']) for r in old]==[(r['room'],r['original_source_row_id']) for r in history]
with (ROOT/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig') as f:
 assert len(list(csv.DictReader(f)))==25
with (ROOT/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig') as f:
 originalactions=list(csv.DictReader(f))
assert len(originalactions)==65 and all(r['procurement_release']=='FALSE' for r in originalactions)
for n in FILES:
 if n.endswith('.md'):
  for link in re.findall(r'\]\(([^)]+)\)',(OUT/n).read_text(encoding='utf-8')):
   if link.startswith(('https://','http://')):continue
   assert (OUT/link).exists(),(n,link)

pred={}
for tag,path in [
 ('R12','deliverables/integrated-r12/MANIFEST.json'),
 ('R21','deliverables/integrated-r21-install-witness-sequence/MANIFEST.json'),
 ('R22','deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json'),
 ('R23_FIXED_LOCAL_NOT_ACCEPTED','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R24','deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/MANIFEST.json'),
 ('R25','deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc/MANIFEST.json'),
 ('R26','deliverables/integrated-r26-tx-primary-and-three-duravit-tubs/MANIFEST.json'),
 ('R014','state/ROUND014_SUBMISSION.json'),('R015','state/ROUND015_SUBMISSION.json'),
 ('R016','state/ROUND016_SUBMISSION.json'),('R017','state/ROUND017_SUBMISSION.json')]:
 pred[tag]=fp(ROOT/path)['sha256']
assert pred['R26']=='16c02f7c01da25457b1ae53860b6166a6b82bb956d319432298a8fbc7d24fb74'
assert pred['R23_FIXED_LOCAL_NOT_ACCEPTED']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert pred['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
source17=json.loads((ROOT/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert source17['critic_dispatch']=='NOT_DISPATCHED' and source17['predispatch_reviewer_verdict'] is None
assert len(source17['confidential_prime_only_mappings'])==4
source16=json.loads((ROOT/'state/ROUND016_SUBMISSION.json').read_text(encoding='utf-8'))
assert source16['critic_dispatch']=='NOT_DISPATCHED'
assert (ROOT/'state/ROUND016_PREDISPATCH_REVIEWER_CLEARANCE_FIX2.json').exists()

obj=dict(round='R27',date='2026-11-06',kind='Source-evidenced additive three powder design/build/value engineering and all-13-room reservation, not blind critic scoring or PO',
focus_rooms=['PH-POWDER','TX-POWDER','TX-POWDER2'],signed_output_count=12,
new_focus_room_GOOD_BETTER_BEST_options=9,new_PH_selected_Brizo_flat_center_cut_cost_scenarios=4,
new_TX_Haze_single_wall_color_split_studies=3,new_TX2_historic_case_threshold_studies=4,
new_six_separate_real_powder_unit_fixture_shop_mockup_camera_requests=6,
new_source_matched_material_pool_and_prohibited_groups=7,new_cross_room_source_row_reservation_proofs=27,
new_historic_reference_rate_powder_scenarios=3,new_detailed_all_13_room_release_dependencies=13,
original_room_ids=13,original_tile_material_rows=27,original_provisional_wall_keys=25,original_trade_actions=65,
two_excluded_primary_niche_references_NO_SCOPE_NO_ORDER=2,original_four_unit_material_only_USD='23572.44',
powder_original_two_copy_three_room_subset_USD='2159.30',original_gross_waste_counted_once='15percent',
actual_correct_1529_site_model_verified=False,actual_current_Chicago_lot_case_supplier_offer=False,
original_exact_numeric_measured_wet_LEVEL_and_PAN_test_received=False,
actual_1to1_mockup_or_1529_render_created=False,owner_fixture_elections_made=False,
R014_original_critic_reports=6,R014_required=8,original_DESIGN_worker9='FAILED',
R015_original_four_seat_partial_dispatch='HOLD',R016_original_critic_dispatch='NOT_DISPATCHED',R017_original_critic_dispatch='NOT_DISPATCHED',
R017_independent_predispatch_clearance=None,R27_new_blind_dispatch=False,R27_critic_weighted_scores=None,
independent_nonPro_Reviewer_worker15='FINISHED_NONREVIVABLE',R23_FIXED1_independent_postrepair_accepted=None,
R24_R25_R26_independent_acceptance=None,R27_independent_acceptance=None,
owner_approved=False,architect_released=False,plumber_released=False,waterproof_installer_released=False,
tile_installer_released=False,GC_released=False,supplier_offer_verified=False,purchasing_released=False,
entire_13_room_Reviewer_GLOBAL_DONE=False,
predecessor_manifest_sha256=pred,
outputs={n:fp(OUT/n) for n in FILES})
manifest=OUT/'MANIFEST.json'
assert not manifest.exists(),'Never overwrite previously signed R27'
manifest.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
assert json.loads(manifest.read_text(encoding='utf-8'))==obj
print('PASS R27 signed 12 additive outputs SHA+bytes, 9 focus options /4 PH/3 TX/4 TX2 study/6 physical units, 27 source records 7 pooled & excluded groups 13 room sequence, historic $23572.44, powder $2159.30 15% once, all releases FALSE')
print('R27_MANIFEST_SHA',fp(manifest)['sha256'])
