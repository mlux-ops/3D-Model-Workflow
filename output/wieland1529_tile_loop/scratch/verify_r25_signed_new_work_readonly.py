"""READ-ONLY signed R25 and predecessor verification. Does NOT certify actual manufacturer wet lab or independent Reviewer."""
from pathlib import Path
import hashlib,json,csv,re
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc'
M=O/'MANIFEST.json'
def sha(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def csvrows(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
assert sha(M)['sha256']=='0170a18a25c5fdf9c682f8c8379c17944e97b98723db1995cfaf6570350f84fe'
manifest=json.loads(M.read_text(encoding='utf-8'))
assert len(manifest['outputs'])==12
assert all(sha(O/n)==meta for n,meta in manifest['outputs'].items())
assert manifest['original_four_unit_tile_material_only_USD']=='23572.44'
assert manifest['historic_15pct_waste_counted_once'] and manifest['original_historical_material_rows']==27
assert manifest['original_provisional_W_wall_keys']==25 and manifest['inherited_65_trade_acceptance_actions_from_R24']==65
for x in ['owner_approved','architect_issue_released','plumbing_submittals_approved','GC_release','procurement_release','entire_13_room_global_REVIEWER_DONE']:
 assert manifest[x] is False,x
for k,expected in [('R23_corrected_local_FIX1_pending_independent','81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'),('R24_signed_local_pass_not_independently_accepted','7e08b9b787a00abfc9fc18e52458008b07312c44da9c96037b0dce866a55a6d4'),('R017_frozen_source_no_predispatch','01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90')]:
 assert manifest['predecessor_SHA256'][k]==expected
source14=json.loads((R/'state/ROUND014_SUBMISSION.json').read_text(encoding='utf-8'))
source17=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert source17['critic_dispatch']=='NOT_DISPATCHED' and source17['predispatch_reviewer_verdict'] is None
assert len(source17['confidential_prime_only_mappings'])==4
for room,alts in source17['blind_source_candidates'].items():
 for letter,rec in alts.items():
  assert sha(R/rec['path'])=={'sha256':rec['sha256'],'bytes':rec['bytes']}
for room,rec in source17['confidential_prime_only_mappings'].items():
 assert sha(R/rec['path'])=={'sha256':rec['sha256'],'bytes':rec['bytes']}
assert manifest['R014_authentic_critics']==6 and manifest['R014_required_critics']==8
assert manifest['R014_scoring'] is None and manifest['R017_weighted_scoring'] is None
assert manifest['R017_predispatch_Reviewer_verdict'] is None
assert manifest['R23_precise_FIX1_independent_postrepair_verdict'] is None
assert manifest['R25_independent_Reviewer_verdict'] is None
assert manifest['standing_nonPro_Reviewer_worker15']=='FINISHED_NONREVIVABLE'

opts=csvrows('R25_12_UNAPPROVED_FOCUS_GOOD_BETTER_BEST_MANUFACTURER_INSTALL_DECISIONS.csv')
pri=csvrows('R25_13_ROOM_OWNER_GC_PRIORITY_AND_EXACT_EVIDENCE_WITNESS.csv')
walls=csvrows('R25_25_WALL_KEY_TWO_ORIENTATION_JOINT_SLIVER_AND_EDGE_SCENARIOS.csv')
ph=csvrows('R25_PH4_18_SCENARIO_27_VS_35_SF_POINT_PAN_LEVEL_CARTON_SENSITIVITY.csv')
units=csvrows('R25_12_UNIT_REAL_DATUM_DRAIN_ROUGH_AND_MEMBRANE_SECTION_WITNESS.csv')
maker=csvrows('R25_15_HIGH_RISK_INDIVIDUAL_WET_APPLICATION_AND_RAW_LAB_EVIDENCE_BRIDGE.csv')
kits=csvrows('R25_13_ROOM_MAKER_SPECIFIC_REAL_1TO1_KITS_AND_SOURCE_TRUE_CAMERAS.csv')
clos=csvrows('R25_13_ROOM_NEW_EVIDENCE_ACCEPTANCE_AND_FIELD_CLOSURE_BRIDGE.csv')
assert list(map(len,[opts,pri,walls,ph,units,maker,kits,clos]))==[12,13,36,18,12,15,13,13]
ids={r['id'] for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert len(ids)==13 and ids=={r['room'] for r in pri}=={r['room'] for r in kits}=={r['room'] for r in clos}
assert all(r['procurement_release']=='FALSE' and r['actual_1to1_installed']=='FALSE' for r in kits)
assert all(r['procurement_release']=='FALSE' and r['raw_individual_numeric_wet_dcof_for_both']=='MISSING' for r in ph)
assert all(r['proposed_RELEASE_GATE_pass']=='FALSE' for r in maker)
assert all(r['GC_release']=='FALSE' and r['owner_approval']=='FALSE' for r in opts)
assert all(r['owner_branch_approved']=='FALSE' for r in units)
assert all(r['architect_signoff']=='FALSE' for r in walls)
orig=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:orig=list(csv.DictReader(f))
assert len(orig)==27 and sum(Decimal(r['historic_usd_two_copies']) for r in orig if r['historic_usd_two_copies'])==Decimal('23572.44')
assert sum(r['historic_niche_excluded_no_scope']=='TRUE' for r in orig)==2
assert all(r['owner_signed']=='FALSE' and r['purchase_release']=='FALSE' for r in orig)
wallorig=[]
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:wallorig=list(csv.DictReader(f))
assert {(r['room'],r['wall']) for r in wallorig}=={(r['room'],r['wall']) for r in walls}
actions=[]
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig',newline='') as f:actions=list(csv.DictReader(f))
assert len(actions)==65 and all(r['procurement_release']=='FALSE' for r in actions)
assert {r['room'] for r in actions}==ids
print('PASS R25 immutable post-signature 12 SHA/byte outputs; 13 room IDs, 27 dated source rows, 25 original W wall IDs, 65 inherited release classes; 36 alternate cut studies, 18 purely hypothetical PH4 carton cases, 12 real program/unit branches, 15 maker evidence facets, $23,572.44 original with 15% ONCE; zero owner/GC/purchase and zero manufactured Reviewer decisions')
print('R25_SHA',sha(M)['sha256'])
