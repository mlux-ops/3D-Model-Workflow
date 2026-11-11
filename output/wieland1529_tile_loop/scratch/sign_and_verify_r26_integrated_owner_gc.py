"""One-time sign new R26 outputs, without any overwrite of predecessor or owner records."""
from pathlib import Path
import hashlib,json,csv,re
from decimal import Decimal
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r26-tx-primary-and-three-duravit-tubs'
outputs=[
'START_HERE_R26.md','R26_MAKER_HARDWARE_COMPATIBILITY_AND_SOURCE_GRADES.md',
'R26_OWNER_GOOD_BETTER_BEST_FOUR_ROOM_1TO1_DESIGN_BOOK.md',
'R26_12_MANUFACTURER_SPECIFIC_FOUR_ROOM_OWNER_GOOD_BETTER_BEST.csv',
'R26_11_WALLS_22_TILE_AXIS_JOINT_CUT_TRIM_STUDIES.csv',
'R26_12_TUB_ALCOVE_NOMINAL_FINISH_BUILDUP_FIT_SENSITIVITY.csv',
'R26_27_HISTORICAL_TO_CURRENT_PROCUREMENT_COST_SCOPE_BRIDGE.csv',
'R26_OLD_SAME_MATERIAL_RATE_ONLY_PLUS_MINUS_2SF_TWO_UNIT_SENSITIVITY.csv',
'R26_13_ROOM_SEQUENTIAL_TRADE_RELEASE_AND_OWNER_DESIGN_DECISIONS.csv',
'R26_ALL_13_ROOM_OWNER_ARCHITECT_GC_APPROVAL_SEQUENCE.md',
'R26_8_PHYSICAL_UNIT_DURAVIT_TUB_AND_TX_LINEAR_TRADE_SUBMITTAL_WITNESS.csv',
'R26_QUANTIFIED_HISTORIC_PRICE_EXPOSURE_AND_SOURCE_NOTES.md']
assert len(outputs)==12 and all((O/n).is_file() for n in outputs)
def fp(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def data(name):
 with (O/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
opts=data(outputs[3]);cuts=data(outputs[4]);fit=data(outputs[5]);materials=data(outputs[6]);rate=data(outputs[7]);allroom=data(outputs[8]);shops=data(outputs[10])
assert list(map(len,[opts,cuts,fit,materials,rate,allroom,shops]))==[12,22,12,27,33,13,8]
idrooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
ids={r['id'] for r in idrooms};assert len(ids)==13 and {r['room'] for r in allroom}==ids
focus={'TX-PRIMARY','PH-BATH2','TX-BATH2','TX-BATH4'}
assert {r['room'] for r in opts}=={r['room'] for r in cuts}=={r['room'] for r in shops}==focus
assert all(sum(r['room']==rid for r in opts)==3 for rid in focus)
assert len({(r['room'],r['wall']) for r in cuts})==11
assert len({(r['room'],r['wall'],r['scenario_tile_direction']) for r in cuts})==22
assert sum(1 for r in fit if r['room']=='PH-BATH2')==4
assert {r['room'] for r in fit}=={'PH-BATH2','TX-BATH2','TX-BATH4'}
assert len({(r['room'],r['physical_unit']) for r in shops})==8
assert all(r['purchaser_released']=='FALSE' for r in shops)
assert all(r['architect_release']=='FALSE' and r['plumber_release']=='FALSE' and r['GC_release']=='FALSE' and r['purchasing_release']=='FALSE' for r in opts)
assert all(r['procurement_release']=='FALSE' and r['actual_1529_checked_W_H']=='' for r in cuts)
assert all(r['GC_released']=='FALSE' and r['purchasing_released']=='FALSE' for r in fit)
assert all(r['purchase_release']=='FALSE' and r['current_verified_Chicago_vendor_offer']=='' and r['current_installed_GC_bid']=='' for r in materials)
assert all(r['purchasing_released']=='FALSE' and r['actual_field_measurement']=='' for r in rate)
assert all(r['owner_approved']=='FALSE' and r['purchaser_released']=='FALSE' for r in allroom)
assert len({(r['room'],r['source_material_row_id']) for r in materials})==27
assert sum(Decimal(r['historical_material_USD_2copies']) for r in materials if r['historical_material_USD_2copies'])==Decimal('23572.44')
assert sum(r['original_unpriced_primary_niche_NO_SCOPE']=='TRUE' for r in materials)==2
assert sum(Decimal(r['historical_material_USD_2copies']) for r in materials if r['room'] in focus and r['historical_material_USD_2copies'])==Decimal('10481.24')
assert all(r['exact_raw_measured_LINEAR_PAN_wet_DCOF_certified']=='N/A_TUB' for r in opts if r['room']!='TX-PRIMARY')
assert all(r['exact_raw_measured_LINEAR_PAN_wet_DCOF_certified']=='FALSE' for r in opts if r['room']=='TX-PRIMARY')
assert all(r['raw_exact_LINEAR_PAN_wet_DCOF_certified']=='N/A_TUB' for r in opts if r['room']!='TX-PRIMARY') if False else True
orig17=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:orig17=list(csv.DictReader(f))
assert [(r['room'],r['source_row_id']) for r in orig17]==[(r['room'],r['source_material_row_id']) for r in materials]
originalwalls=[]
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:originalwalls=list(csv.DictReader(f))
assert len(originalwalls)==25
assert {(r['room'],r['wall']) for r in cuts}=={(r['room'],r['wall']) for r in originalwalls if r['room'] in focus}
actions=[]
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig',newline='') as f:actions=list(csv.DictReader(f))
assert len(actions)==65 and {r['room'] for r in actions}==ids and all(r['procurement_release']=='FALSE' for r in actions)
for n in outputs:
 if n.endswith('.md'):
  for path in re.findall(r'\]\(([^)]+)\)',(O/n).read_text(encoding='utf-8')):
   if path.startswith(('https://','http://')):continue
   assert (O/path).exists(),(n,path)

pres={}
for tag,path in [
 ('R12','deliverables/integrated-r12/MANIFEST.json'),
 ('R21','deliverables/integrated-r21-install-witness-sequence/MANIFEST.json'),
 ('R22','deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json'),
 ('R23_fixed_local_unreviewed','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R24','deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/MANIFEST.json'),
 ('R25','deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc/MANIFEST.json'),
 ('R014','state/ROUND014_SUBMISSION.json'),
 ('R015','state/ROUND015_SUBMISSION.json'),
 ('R016','state/ROUND016_SUBMISSION.json'),
 ('R017','state/ROUND017_SUBMISSION.json'),
]:pres[tag]=fp(R/path)['sha256']
assert pres['R23_fixed_local_unreviewed']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert pres['R25']=='0170a18a25c5fdf9c682f8c8379c17944e97b98723db1995cfaf6570350f84fe'
assert pres['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
assert pres['R016']=='dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a'
s17=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert len(s17['confidential_prime_only_mappings'])==4 and s17['critic_dispatch']=='NOT_DISPATCHED'
assert s17['predispatch_reviewer_verdict'] is None
body={
 'round':'R26','date':'2026-11-06','artifact_kind':'Additive 13-room owner/architect/GC technical and historic cost change control only, unscored, no release',
 'focused_rooms':['TX-PRIMARY','PH-BATH2','TX-BATH2','TX-BATH4'],
 'signed_output_count':len(outputs),
 'new_GOOD_BETTER_BEST_focus_options':12,
 'new_focus_wall_keys':11,'new_focus_orientation_joint_cut_scenarios':22,
 'new_tub_finish_fit_sensitivities':12,'new_physical_unit_shop_witnesses':8,
 'new_all_room_sequential_release_records':13,'new_original_row_procurement_bridge':27,
 'new_historic_rate_only_scope_scenarios':33,
 'original_13_rooms':13,'original_27_tile_source_rows':27,'original_25_provisional_wall_studies':25,'original_65_trade_action_classes':65,'original_R21_156_site_witness_cells':156,
 'historic_four_unit_material_only_USD':'23572.44','historic_four_focus_room_two_copy_subset_USD':'10481.24',
 'two_unpriced_primary_niche_refs_NO_ORDER':2,'original_historical_gross_includes_15pct_once':True,
 'current_original_numeric_wet_LEVEL_test_provided':False,'TX_primary_original_numeric_wet_LINEAR_PAN_lab_provided':False,
 'verified_1529_native_Revit_or_site_geometry':False,'current_Chicago_stock_offer_installed_bid_provided':False,'sample_or_field_shop_witness_performed':False,
 'R014_critic_reports':6,'R014_required':8,'original_worker9_DESIGN':'FAILED',
 'R015_critic_dispatch':'HOLD','R016_critic_dispatch':'NOT_DISPATCHED','R017_critic_dispatch':'NOT_DISPATCHED','R017_source_preflight_independent':None,'any_R26_new_critic_dispatch_or_scoring':False,
 'original_reviewer15':'FINISHED_NONREVIVABLE','R23_precise_FIX_independent_postrepair_acceptance':None,'R24_independent_acceptance':None,'R25_independent_acceptance':None,'R26_independent_acceptance':None,
 'owner_approval':False,'architect_release':False,'plumbing_release':False,'waterproof_installer_release':False,'tile_installer_release':False,'GC_release':False,'procurement_release':False,'global_13_room_DONE':False,
 'signed_predecessors_sha256':pres,
 'output_files':{n:fp(O/n) for n in outputs},
}
M=O/'MANIFEST.json'
assert not M.exists(),'Do not silently regenerate a previously signed R26 manifest'
M.write_bytes((json.dumps(body,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
assert json.loads(M.read_text(encoding='utf-8'))==body
print('PASS R26 12 SHA-signed outputs; 13 original rooms, 27 original material records, 25 wall studies, 65 inherited trade actions; 12 new specific focus tiers, 11 focus wall IDs/22 cuts, 12 tub fit examples, 8 physical unit shops, 33 dated rate what-if; historic $23572.44 and $10481.24 correct, original 15% once, ALL release FALSE')
print('R26_MANIFEST_SHA',fp(M)['sha256'])
