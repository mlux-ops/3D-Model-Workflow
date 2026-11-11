"""Sign additive R24 with source semantic checks; never re-create or overwrite signed outputs."""
from pathlib import Path
import hashlib,csv,json,re
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions'

outputs=['START_HERE_R24.md','R24_FOUR_WET_ROOM_1TO1_ASSEMBLY_SECTION_SHOP_AND_OWNER_PROGRAM.md','R24_12_WET_UNIT_OWNER_BRANCH_AND_DRAIN_ROUGH_DECISION_MATRIX.csv','R24_25_W1_W3_ALTERNATE_CENTERING_CUT_EDGE_NET_SENSITIVITY.csv','R24_27_MATERIAL_BRANCH_NET_CARTON_AND_COST_DELTA_RECONCILIATION.csv','R24_13_ROOM_GOOD_BETTER_BEST_DELTA_AND_SIGNATURE_DECISIONS.csv','R24_13_ROOM_OWNER_DESIGN_TIER_BOOK.md','R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv']
def fingerprint(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def h(p):return fingerprint(R/p)['sha256']
def load(file):
 with (O/file).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
assert len(outputs)==8
for name in outputs:
 assert (O/name).is_file(),name

predecessors={
 'R012':h('deliverables/integrated-r12/MANIFEST.json'),
 'R021':h('deliverables/integrated-r21-install-witness-sequence/MANIFEST.json'),
 'R022':h('deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json'),
 'R023_FIXED_LOCALLY_NOT_INDEPENDENTLY_CLEARED':h('deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 'R023_original_reviewer_FIXED_from':json.loads((R/'state/ROUND023_REVIEWER_PROGRAM_SPECIFIC_SAME_PACKAGE_FIX1.json').read_text(encoding='utf-8'))['old_manifest']['sha256'],
 'R014_original_source':h('state/ROUND014_SUBMISSION.json'),
 'R015_original_source':h('state/ROUND015_SUBMISSION.json'),
 'R016_original_source':h('state/ROUND016_SUBMISSION.json'),
 'R017_frozen_source_awaiting_review':h('state/ROUND017_SUBMISSION.json'),
}
assert predecessors['R023_FIXED_LOCALLY_NOT_INDEPENDENTLY_CLEARED']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert predecessors['R017_frozen_source_awaiting_review']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
assert predecessors['R022']=='32e5ceb807e33e642680dec47aa378d21d5ba9f7b05462214277cb89e7d76df1'
assert predecessors['R021']=='a212a902fcf61433cbcf165c05b07681abffcb3f70ae9f8deeb8e0756989ad66'
assert predecessors['R016_original_source']=='dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a'

rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
ids={r['id'] for r in rooms}
assert len(ids)==13
branch=load(outputs[2]);w=load(outputs[3]);cost=load(outputs[4]);decision=load(outputs[5]);trade=load(outputs[7])
assert [len(a) for a in [branch,w,cost,decision,trade]]==[12,25,27,13,65]
assert set(x['room'] for x in decision)==ids
assert len({(x['room'],x['trade_class']) for x in trade})==65
assert len({(x['room'],x['wall']) for x in w})==25
assert len({(x['room'],x['material_source_row_id']) for x in cost})==27
assert len({(x['room'],x['physical_unit'],x['owner_program_branch']) for x in branch})==12
assert {x['room'] for x in branch}=={'PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY'}
assert sum(1 for x in cost if x['historical_niche_excluded_NO_ORDER']=='TRUE')==2
assert sum(Decimal(x['source_historic_usd_two_physical_units']) for x in cost if x['source_historic_usd_two_physical_units'])==Decimal('23572.44')
assert sum(Decimal(x['historical_material_usd_two_copies']) for x in decision)==Decimal('23572.44')
assert all(x['one_time_waste_already_in_historic_gross']=='TRUE' for x in decision)
assert all(x['owner_signature']=='FALSE' and x['GC_signature']=='FALSE' and x['purchasing_release']=='FALSE' for x in decision)
assert all(x['owner_release']=='FALSE' and x['architect_release']=='FALSE' and x['GC_release']=='FALSE' and x['procurement_release']=='FALSE' and x['acceptance']=='FALSE' for x in trade)
assert all(x['purchaser_released']=='FALSE' and not x['correct_actual_1529_NET_sf'] and not x['live_Chicago_verified_offer_USD'] and not x['calculated_cartons'] for x in cost)
assert all(x['owner_signature']=='FALSE' and x['purchasing_release']=='FALSE' for x in branch)
assert all(x['owner_approved']=='FALSE' and x['purchase_release']=='FALSE' for x in w)

pan_tub=[x for x in branch if x['owner_program_branch']=='TUB_CONDITIONAL']
assert len(pan_tub)==4 and all(x['PAN_raw_numeric_wet_test_gate']=='N/A_TUB_NO_TILED_SHOWER_PAN' and x['selected_existing_shower_drain_applies']=='FALSE_NO_TUB_WASTE' for x in pan_tub)
point=[x for x in branch if 'POINT' in x['owner_program_branch']]
assert len(point)==6 and all('POINT' in x['PAN_raw_numeric_wet_test_gate'] and x['owner_signature']=='FALSE' for x in point)
linear=[x for x in branch if x['room']=='PH-PRIMARY']
assert len(linear)==2 and all('BR73480' in x['shower_drain_original_SKU_finish'] and 'LINEAR' in x['PAN_raw_numeric_wet_test_gate'] for x in linear)
assert all(x['owner_program_selected']=='FALSE' for x in branch if x['room'] in ['PH-BATH3','TX-BATH3'])

for room in ['PH-WC','TX-WC']:
 x=next(d for d in decision if d['room']==room)
 assert x['historical_material_usd_copy']=='0.0' and ('one purchase allocation' in x['BEST_unapproved_scope'] or 'no independent WC PAN' in x['BEST_unapproved_scope'])
for room in ['PH-BATH2','TX-BATH2','TX-BATH4']:
 x=next(d for d in decision if d['room']==room)
 assert 'TUB' in x['exact_selected_program_and_fixture'] and 'PAN' in x['exact_selected_program_and_fixture']
for room in ['PH-POWDER','TX-POWDER','TX-POWDER2']:
 x=next(d for d in decision if d['room']==room)
 assert 'DRY' in x['exact_selected_program_and_fixture'] and 'WOOD' in x['individual_maker_wet_and_lab_gate'].upper()

historic25=[]
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:historic25=list(csv.DictReader(f))
assert [(x['room'],x['wall']) for x in historic25]==[(x['room'],x['wall']) for x in w]
source27=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:source27=list(csv.DictReader(f))
assert [(x['room'],x['source_row_id']) for x in source27]==[(x['room'],x['material_source_row_id']) for x in cost]

for name in outputs:
 if name.endswith('.md'):
  txt=(O/name).read_text(encoding='utf-8')
  for link in re.findall(r'\]\(([^)]+)\)',txt):
   if link.startswith(('https://','http://')):continue
   assert (O/link).exists(),(name,link)

record={
 'version':'R24','as_of':'2026-11-06','type':'ADDITIVE owner/architect/GC construction quantity and branch design package, no previous signed replacement',
 'original_13_room_count':13,'historical_27_material_lines':27,'two_original_primary_niche_reference_rows_NO_SCOPE_NO_ORDER':2,
 'original_25_provisional_wall_studies':25,'original_65_trade_actions':65,'R21_original_field_witness_cells':156,
 'new_R24_branch_unit_scenarios':12,'new_R24_65_trade_specific_acceptance_RFI_cells':65,
 'historic_four_unit_material_only_usd':'23572.44','gross_original_waste_15pct_once':True,
 'source_1529_native_model_certified':False,'actual_manufacturer_raw_numerical_wet_LEVEL_PAN_available':False,
 'actual_Chicago_supplier_and_installed_bid':None,'sample_or_field_mockup_performed':False,
 'owner_Bath3_tub_or_walkin_selected':False,'original_design_worker9':'FAILED','R014_authentic_original_critic_reports':6,'R014_required':8,
 'R014_weighted_scoring':None,'R015_critic_dispatch':'HOLD','R016_critic_dispatch':'NOT_DISPATCHED','R017_critic_dispatch':'NOT_DISPATCHED','R017_reviewer_predispatch_clearance':None,'R017_weighted_score':None,
 'R23_local_FIX1_verified_independent_postfix_clearance':False,
 'reviewer_worker15_finished_nonrevivable':True,'R24_independent_reviewer_verdict':None,
 'owner_approved':False,'architect_issued':False,'plumber_shop_signed':False,'GC_release':False,'procurement_release':False,'global_13_room_DONE':False,
 'signed_previous_chain_sha256':predecessors,
 'outputs':{name:fingerprint(O/name) for name in outputs}
}
M=O/'MANIFEST.json';assert not M.exists(),'R24 manifest already exists; do not re-sign silently'
M.write_bytes((json.dumps(record,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
assert json.loads(M.read_text(encoding='utf-8'))==record
print('PASS R24 eight SHA-signed outputs; 13 owner decision rooms, 65 specific trade RFIs, 25 unchanged original wall keys, 27 source material IDs, 12 mutually exclusive wet unit/branch records, 2 excluded Primary niches, historical $23572.44 exact with 15% once, all releases FALSE')
print('R24_MANIFEST_SHA',fingerprint(M)['sha256'])
print('R12_MANIFEST_SHA',predecessors['R012'])
