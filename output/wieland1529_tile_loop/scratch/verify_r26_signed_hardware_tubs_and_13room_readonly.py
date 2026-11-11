"""Strict READ-ONLY signed R26 and source baseline check, no reviewer-acceptance claims."""
from pathlib import Path
import hashlib,json,csv
from decimal import Decimal
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r26-tx-primary-and-three-duravit-tubs'
def fingerprint(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def rows(n):
 with (O/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
m=O/'MANIFEST.json'
expected='16c02f7c01da25457b1ae53860b6166a6b82bb956d319432298a8fbc7d24fb74'
assert fingerprint(m)['sha256']==expected
x=json.loads(m.read_text(encoding='utf-8'))
assert len(x['output_files'])==12
for file,old in x['output_files'].items():assert fingerprint(O/file)==old,file
assert x['original_13_rooms']==13 and x['original_27_tile_source_rows']==27 and x['original_25_provisional_wall_studies']==25 and x['original_65_trade_action_classes']==65
assert x['historic_four_unit_material_only_USD']=='23572.44' and x['historic_four_focus_room_two_copy_subset_USD']=='10481.24' and x['original_historical_gross_includes_15pct_once']
for key in ['owner_approval','architect_release','plumbing_release','waterproof_installer_release','tile_installer_release','GC_release','procurement_release','global_13_room_DONE']:
 assert x[key] is False
assert x['R014_critic_reports']==6 and x['R014_required']==8 and x['R017_source_preflight_independent'] is None
assert x['R23_precise_FIX_independent_postrepair_acceptance'] is None and x['R26_independent_acceptance'] is None
assert x['original_reviewer15']=='FINISHED_NONREVIVABLE'
assert x['signed_predecessors_sha256']['R25']=='0170a18a25c5fdf9c682f8c8379c17944e97b98723db1995cfaf6570350f84fe'
assert x['signed_predecessors_sha256']['R23_fixed_local_unreviewed']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert x['signed_predecessors_sha256']['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
for tag,file in [('R25','deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc/MANIFEST.json'),('R017','state/ROUND017_SUBMISSION.json'),('R23_fixed_local_unreviewed','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json')]:
 assert fingerprint(R/file)['sha256']==x['signed_predecessors_sha256'][tag]
foc={'TX-PRIMARY','PH-BATH2','TX-BATH2','TX-BATH4'}
opts=rows('R26_12_MANUFACTURER_SPECIFIC_FOUR_ROOM_OWNER_GOOD_BETTER_BEST.csv')
walls=rows('R26_11_WALLS_22_TILE_AXIS_JOINT_CUT_TRIM_STUDIES.csv')
fit=rows('R26_12_TUB_ALCOVE_NOMINAL_FINISH_BUILDUP_FIT_SENSITIVITY.csv')
hist=rows('R26_27_HISTORICAL_TO_CURRENT_PROCUREMENT_COST_SCOPE_BRIDGE.csv')
pricing=rows('R26_OLD_SAME_MATERIAL_RATE_ONLY_PLUS_MINUS_2SF_TWO_UNIT_SENSITIVITY.csv')
allrooms=rows('R26_13_ROOM_SEQUENTIAL_TRADE_RELEASE_AND_OWNER_DESIGN_DECISIONS.csv')
shops=rows('R26_8_PHYSICAL_UNIT_DURAVIT_TUB_AND_TX_LINEAR_TRADE_SUBMITTAL_WITNESS.csv')
assert [len(v) for v in [opts,walls,fit,hist,pricing,allrooms,shops]]==[12,22,12,27,33,13,8]
allids={r['id'] for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert len(allids)==13 and {r['room'] for r in allrooms}==allids
assert {r['room'] for r in opts}=={r['room'] for r in shops}==foc
assert len({(r['room'],r['wall']) for r in walls})==11 and len({(r['room'],r['wall'],r['scenario_tile_direction']) for r in walls})==22
assert len({(r['room'],r['physical_unit']) for r in shops})==8
assert sum(Decimal(r['historical_material_USD_2copies']) for r in hist if r['historical_material_USD_2copies'])==Decimal('23572.44')
assert sum(Decimal(r['historical_material_USD_2copies']) for r in hist if r['room'] in foc and r['historical_material_USD_2copies'])==Decimal('10481.24')
assert sum(r['original_unpriced_primary_niche_NO_SCOPE']=='TRUE' for r in hist)==2
assert all(r['purchasing_release']=='FALSE' for r in opts)
assert all(r['purchaser_released']=='FALSE' for r in allrooms)
assert all(r['purchase_release']=='FALSE' for r in hist)
assert all(r['purchaser_released']=='FALSE' for r in shops)
assert all(r['purchasing_released']=='FALSE' for r in pricing)
assert all(r['actual_1529_checked_W_H']=='' for r in walls)
assert all(r['architect_site_signed']=='FALSE' for r in fit)
assert all(r['exact_raw_measured_LINEAR_PAN_wet_DCOF_certified']=='N/A_TUB' for r in opts if r['room']!='TX-PRIMARY')
assert all(r['exact_raw_measured_LINEAR_PAN_wet_DCOF_certified']=='FALSE' for r in opts if r['room']=='TX-PRIMARY')
s17=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert len(s17['confidential_prime_only_mappings'])==4 and s17['critic_dispatch']=='NOT_DISPATCHED' and s17['predispatch_reviewer_verdict'] is None
r=(R/'state/ROUND026_INDEPENDENT_NONPRO_REVIEWER_REPORT_PREPARED_NOT_SENT.md').read_text(encoding='utf-8')
assert len(r)<=4000 and [s for s in ['GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT'] if s in r]==['GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT']
status=(R/'state/ROUND026_CURRENT_ACTIVE_BOARD_FIVE_LINE_STATUS.txt').read_text(encoding='utf-8').splitlines()
assert len(status)==5 and status[0]=='STATUS round=017 phase=4-deepen'
assert (R/'state/LEDGER.md').read_text(encoding='utf-8').count('## R26 new TX Primary + three selected Duravit tub owner/GC buildable coordination')==1
print('PASS R26 READ-ONLY 12/12 signed SHA+bytes; 13 rooms/27 original materials/25 source W keys/65 inherited actions; 11 focus W/22 cut studies; 12 tub fit, 8 physical unit shops, 33 dated only old rate sensitivities; $23572.44 full/$10481.24 focus, 15% original once, all release flags FALSE')
print('R26_SHA',expected)
