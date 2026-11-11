"""Immutable R25 signing and exact semantic source QA; original manufacturer review is separate."""
from pathlib import Path
import hashlib,json,csv,re
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc'
M=O/'MANIFEST.json'
names=[
'START_HERE_R25.md',
'R25_PUBLIC_MAKER_VERSIONED_EVIDENCE_AND_RESTRICTIONS.md',
'R25_FOUR_ROOM_THREE_TIER_CONSTRUCTION_DESIGN_EXHIBIT.md',
'R25_THIRTEEN_ROOM_PRIORITY_DECISION_AND_TRADE_EXHIBIT.md',
'R25_12_UNAPPROVED_FOCUS_GOOD_BETTER_BEST_MANUFACTURER_INSTALL_DECISIONS.csv',
'R25_13_ROOM_OWNER_GC_PRIORITY_AND_EXACT_EVIDENCE_WITNESS.csv',
'R25_25_WALL_KEY_TWO_ORIENTATION_JOINT_SLIVER_AND_EDGE_SCENARIOS.csv',
'R25_PH4_18_SCENARIO_27_VS_35_SF_POINT_PAN_LEVEL_CARTON_SENSITIVITY.csv',
'R25_12_UNIT_REAL_DATUM_DRAIN_ROUGH_AND_MEMBRANE_SECTION_WITNESS.csv',
'R25_13_ROOM_NEW_EVIDENCE_ACCEPTANCE_AND_FIELD_CLOSURE_BRIDGE.csv',
'R25_15_HIGH_RISK_INDIVIDUAL_WET_APPLICATION_AND_RAW_LAB_EVIDENCE_BRIDGE.csv',
'R25_13_ROOM_MAKER_SPECIFIC_REAL_1TO1_KITS_AND_SOURCE_TRUE_CAMERAS.csv',
]
assert len(names)==12 and all((O/n).is_file() for n in names)
def fp(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def records(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
opts=records(names[4]);pri=records(names[5]);wall=records(names[6]);ph4=records(names[7]);units=records(names[8]);clos=records(names[9]);maker=records(names[10]);samples=records(names[11])
assert list(map(len,[opts,pri,wall,ph4,units,clos,maker,samples]))==[12,13,36,18,12,13,15,13]
ids={r['id'] for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert len(ids)==13 and {r['room'] for r in pri}=={r['room'] for r in clos}=={r['room'] for r in samples}==ids
focus={'PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY'}
assert {r['room'] for r in opts}=={r['room'] for r in units}==focus
assert all(sum(r['room']==rid for r in opts)==3 for rid in focus)
assert len({(r['room'],r['wall']) for r in wall})==25
assert len({(r['room'],r['wall'],r['scenario']) for r in wall})==36
assert len({(r['room'],r['physical_unit'],r['program_branch']) for r in units})==12
assert len({(r['room'],r['physical_surface'],r['exact_maker_tile_and_finish']) for r in maker})==15
assert all(r['selected_now']=='FALSE' and r['raw_LEVEL_numeric_lab_verified']=='FALSE' and r['raw_PAN_numeric_lab_verified']=='FALSE' for r in opts)
assert all(r['owner_approved']=='FALSE' and r['purchasing_release']=='FALSE' for r in pri)
assert all(r['procurement_release']=='FALSE' and r['owner_branch_approved']=='FALSE' for r in units)
assert all(r['purchase_released']=='FALSE' and r['owner_signed']=='FALSE' for r in clos)
assert all(r['proposed_RELEASE_GATE_pass']=='FALSE' and r['purchasing_release']=='FALSE' for r in maker)
assert all(r['actual_physical_samples_ordered']=='FALSE' and r['actual_render_created']=='FALSE' and r['GC_accepted']=='FALSE' for r in samples)
assert all(r['procurement_release']=='FALSE' and r['actual_SF_is_assumption']=='TRUE' and r['raw_individual_numeric_wet_dcof_for_both']=='MISSING' for r in ph4)
assert all(r['architect_signoff']=='FALSE' and r['procurement_release']=='FALSE' for r in wall)

# Exact R24 and historic sources: R25 references without reauthoring old 27 source finance or 65 release tasks.
pre={
'R12_signed':fp(R/'deliverables/integrated-r12/MANIFEST.json')['sha256'],
'R21_signed':fp(R/'deliverables/integrated-r21-install-witness-sequence/MANIFEST.json')['sha256'],
'R22_signed':fp(R/'deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json')['sha256'],
'R23_corrected_local_FIX1_pending_independent':fp(R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json')['sha256'],
'R24_signed_local_pass_not_independently_accepted':fp(R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/MANIFEST.json')['sha256'],
'R014_original_source':fp(R/'state/ROUND014_SUBMISSION.json')['sha256'],
'R015_original_source':fp(R/'state/ROUND015_SUBMISSION.json')['sha256'],
'R016_frozen_source':fp(R/'state/ROUND016_SUBMISSION.json')['sha256'],
'R017_frozen_source_no_predispatch':fp(R/'state/ROUND017_SUBMISSION.json')['sha256'],
}
assert pre['R23_corrected_local_FIX1_pending_independent']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert pre['R24_signed_local_pass_not_independently_accepted']=='7e08b9b787a00abfc9fc18e52458008b07312c44da9c96037b0dce866a55a6d4'
assert pre['R017_frozen_source_no_predispatch']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
assert pre['R016_frozen_source']=='dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a'

orig27=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:orig27=list(csv.DictReader(f))
assert len(orig27)==27
assert sum(Decimal(r['historic_usd_two_copies']) for r in orig27 if r['historic_usd_two_copies'])==Decimal('23572.44')
assert sum(r['historic_niche_excluded_no_scope']=='TRUE' for r in orig27)==2
oldw=[]
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:oldw=list(csv.DictReader(f))
assert {(r['room'],r['wall']) for r in oldw}=={(r['room'],r['wall']) for r in wall}
oldactions=[]
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig',newline='') as f:oldactions=list(csv.DictReader(f))
assert len(oldactions)==65 and {(r['room'],r['trade_class']) for r in oldactions}=={(rid,cls) for rid in ids for cls in ['OWNER_PROGRAM','ARCHITECT_1529_DIMENSIONS','PLUMBING_WATERPROOF_SUBMITTAL','TILE_MAKER_LAB_AND_1TO1','ESTIMATOR_SUPPLIER_RELEASE']}
assert all(x['procurement_release']=='FALSE' for x in oldactions)

for r in units:
 if r['program_branch']=='TUB_CONDITIONAL':
  assert r['raw_individual_PAN_wet_numeric_lab']=='N/A' and r['actual_selected_drain_rough_FFE_in']=='N/A'
  assert r['GC_flood_witness_complete']=='N/A_NO_SHOWER_PAN'
 else:
  assert r['raw_individual_PAN_wet_numeric_lab']==''
assert len([r for r in units if r['program_branch']=='TUB_CONDITIONAL'])==4
assert sum(r['program_branch']=='WALKIN_POINT_CONDITIONAL' for r in units)==4
assert sum(r['program_branch']=='WALKIN_POINT_SELECTED' for r in units)==2
assert sum(r['program_branch']=='SELECTED_48IN_LINEAR_AND_SEPARATE_TUB' for r in units)==2
assert len(set((r['input_source_area_SF_PER_COPY_NOT_SURVEYED'],r['hypothetical_POINT_PAN_fraction_of_assumed_total'],r['hypothetical_once_only_NEW_offcut_waste_factor']) for r in ph4))==18
example=[r for r in ph4 if r['hypothetical_POINT_PAN_fraction_of_assumed_total']=='0.35' and r['hypothetical_once_only_NEW_offcut_waste_factor']=='0.05']
assert {(r['input_source_area_SF_PER_COPY_NOT_SURVEYED'],r['illustrative_rounded_LEVEL_cases_not_orderable'],r['illustrative_rounded_PAN_cases_not_orderable']) for r in example}=={('27','4','5'),('35','5','6')}
assert all(r['actual_physical_samples_ordered']=='FALSE' and r['actual_1to1_installed']=='FALSE' for r in samples)
for n in names:
 if n.endswith('.md'):
  txt=(O/n).read_text(encoding='utf-8')
  for link in re.findall(r'\]\(([^)]+)\)',txt):
   if link.startswith('http://') or link.startswith('https://'):continue
   assert (O/n).parent.joinpath(link).exists(),(n,link)

meta={
 'round':'R25','as_of':'2026-11-06','purpose':'ADDITIVE research-backed physically differentiated 13-room owner and GC design, not approved selections or four-seat critic results',
 'source_room_ids':13,'original_historical_material_rows':27,'unpriced_primary_niches_NO_SCOPE_NO_ORDER':2,'original_provisional_W_wall_keys':25,'inherited_65_trade_acceptance_actions_from_R24':65,'original_R21_156_field_witness_cells_preserved':156,
 'new_output_files':len(names),'new_focus_three_tier_options':12,'new_25_wall_ids_36_layout_scenarios':36,'new_PH4_hypothetical_case_scenarios':18,'new_physical_wet_unit_program_branches':12,'new_maker_individual_wet_facets':15,'new_13_room_owner_priority_and_physical_kits':13,
 'original_four_unit_tile_material_only_USD':'23572.44','historic_15pct_waste_counted_once':True,
 'original_SELECTED_drain_and_fixture_preserved':True,'PH_TX_BATH3_owner_program_unselected':True,
 'native_1529_model_verified':False,'exact_individual_RAW_numeric_wet_LEVEL_PAN_tests_provided':False,
 'current_Chicago_verified_supplier_offer_and_installed_bid':False,'actual_1to1_field_mockup_or_render_created':False,
 'R014_authentic_critics':6,'R014_required_critics':8,'original_DESIGN_worker9':'FAILED','R014_scoring':None,
 'R015_critic_dispatch':'HOLD','R016_critic_dispatch':'NOT_DISPATCHED','R017_critic_dispatch':'NOT_DISPATCHED','R017_predispatch_Reviewer_verdict':None,'R017_weighted_scoring':None,
 'standing_nonPro_Reviewer_worker15':'FINISHED_NONREVIVABLE','R23_precise_FIX1_independent_postrepair_verdict':None,'R24_independent_Reviewer_verdict':None,'R25_independent_Reviewer_verdict':None,
 'owner_approved':False,'architect_issue_released':False,'plumbing_submittals_approved':False,'GC_release':False,'procurement_release':False,'entire_13_room_global_REVIEWER_DONE':False,
 'predecessor_SHA256':pre,'outputs':{n:fp(O/n) for n in names},
}
assert not M.exists(),'Never re-sign an existing R25 without intentional reviewer change control'
M.write_bytes((json.dumps(meta,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
assert json.loads(M.read_text(encoding='utf-8'))==meta
print('PASS R25 SIGNED 12 outputs, 13 rooms, 25 original walls/36 pattern cases, 27 original source rows, 65 inherited trade actions, 18 PH4 case sensitivities, 12 wet-unit branches, 15 maker grades, all release flags FALSE; $23572.44 exact original 15% once')
print('R25_MANIFEST_SHA',fp(M)['sha256'])
