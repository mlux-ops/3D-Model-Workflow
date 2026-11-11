"""READ-ONLY R24 post-signature integrity and original R014/R017/R23 no-release gates."""
from pathlib import Path
import hashlib,csv,json,re
from decimal import Decimal

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions'
M=O/'MANIFEST.json'
sha=lambda p:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':len(p.read_bytes())}
assert sha(M)['sha256']=='7e08b9b787a00abfc9fc18e52458008b07312c44da9c96037b0dce866a55a6d4'
meta=json.loads(M.read_text(encoding='utf-8'))
assert len(meta['outputs'])==8
for filename,original in meta['outputs'].items():
 assert sha(O/filename)==original,(filename,'modified after signed manifest')
assert meta['historic_four_unit_material_only_usd']=='23572.44' and meta['gross_original_waste_15pct_once']
assert meta['R014_authentic_original_critic_reports']==6 and meta['R014_required']==8
assert meta['original_design_worker9']=='FAILED' and meta['R017_critic_dispatch']=='NOT_DISPATCHED'
assert not meta['R23_local_FIX1_verified_independent_postfix_clearance'] and meta['R24_independent_reviewer_verdict'] is None
assert not any(meta[x] for x in ['owner_approved','architect_issued','plumber_shop_signed','GC_release','procurement_release','global_13_room_DONE'])
for prefix,path,expected in [
 ('R012','deliverables/integrated-r12/MANIFEST.json',meta['signed_previous_chain_sha256']['R012']),
 ('R022','deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json','32e5ceb807e33e642680dec47aa378d21d5ba9f7b05462214277cb89e7d76df1'),
 ('R023','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json','81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'),
 ('R017','state/ROUND017_SUBMISSION.json','01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'),
]:
 assert sha(R/path)['sha256']==expected,(prefix,'predecessor changed')

def table(file):
 with (O/file).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
branch=table('R24_12_WET_UNIT_OWNER_BRANCH_AND_DRAIN_ROUGH_DECISION_MATRIX.csv')
walls=table('R24_25_W1_W3_ALTERNATE_CENTERING_CUT_EDGE_NET_SENSITIVITY.csv')
material=table('R24_27_MATERIAL_BRANCH_NET_CARTON_AND_COST_DELTA_RECONCILIATION.csv')
owner=table('R24_13_ROOM_GOOD_BETTER_BEST_DELTA_AND_SIGNATURE_DECISIONS.csv')
actions=table('R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv')
assert [len(branch),len(walls),len(material),len(owner),len(actions)]==[12,25,27,13,65]
ids={x['id'] for x in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert len(ids)==13 and {x['room'] for x in owner}==ids and {x['room'] for x in actions}==ids
assert len({(x['room'],x['physical_unit'],x['owner_program_branch']) for x in branch})==12
assert len({(x['room'],x['wall']) for x in walls})==25
assert len({(x['room'],x['material_source_row_id']) for x in material})==27
assert len({(x['room'],x['trade_class']) for x in actions})==65
assert sum(Decimal(x['source_historic_usd_two_physical_units']) for x in material if x['source_historic_usd_two_physical_units'])==Decimal('23572.44')
assert sum(Decimal(x['historical_material_usd_two_copies']) for x in owner)==Decimal('23572.44')
assert sum(x['historical_niche_excluded_NO_ORDER']=='TRUE' for x in material)==2
assert all(x['purchaser_released']=='FALSE' and x['live_Chicago_verified_offer_USD']=='' and x['calculated_cartons']=='' for x in material)
assert all(x['procurement_release']=='FALSE' and x['owner_release']=='FALSE' and x['GC_release']=='FALSE' for x in actions)
assert all(x['owner_signature']=='FALSE' and x['purchasing_release']=='FALSE' for x in branch)
assert all(x['owner_signature']=='FALSE' and x['GC_signature']=='FALSE' and x['purchasing_release']=='FALSE' for x in owner)

for rid in ['PH-BATH3','TX-BATH3']:
 assert len([x for x in branch if x['room']==rid])==4
 assert {x['owner_program_branch'] for x in branch if x['room']==rid}=={'TUB_CONDITIONAL','WALKIN_POINT_CONDITIONAL'}
 assert all(x['owner_program_selected']=='FALSE' for x in branch if x['room']==rid)
 assert all('N/A_TUB_NO_TILED_SHOWER_PAN' in x['PAN_raw_numeric_wet_test_gate'] and x['selected_existing_shower_drain_applies']=='FALSE_NO_TUB_WASTE' for x in branch if x['room']==rid and x['owner_program_branch']=='TUB_CONDITIONAL')
 assert all(x['PAN_raw_numeric_wet_test_gate'].startswith('SEPARATE_POINT_PAN') for x in branch if x['room']==rid and x['owner_program_branch']=='WALKIN_POINT_CONDITIONAL')
assert all(x['room']=='PH-BATH4' and 'POINT' in x['shower_drain_original_SKU_finish'] for x in branch if x['owner_program_branch']=='WALKIN_POINT_SELECTED')
assert all('48in' in x['shower_drain_original_SKU_finish'] and 'BR73480' in x['shower_drain_original_SKU_finish'] for x in branch if x['room']=='PH-PRIMARY')
assert all(x['branch_scope']=='NO_SCOPE_NO_ORDER' or x['historical_niche_excluded_NO_ORDER']=='FALSE' for x in material)

sourcewall=[]
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:sourcewall=list(csv.DictReader(f))
assert [(x['room'],x['wall']) for x in sourcewall]==[(x['room'],x['wall']) for x in walls]
source27=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:source27=list(csv.DictReader(f))
assert [(x['room'],x['source_row_id']) for x in source27]==[(x['room'],x['material_source_row_id']) for x in material]

for filename in meta['outputs']:
 if filename.endswith('.md'):
  txt=(O/filename).read_text(encoding='utf-8')
  for link in re.findall(r'\]\(([^)]+)\)',txt):
   if link.startswith(('http://','https://')):continue
   assert (O/link).exists(),(filename,link)
print('PASS R24 post-sign READ ONLY 8/8 SHA+bytes, exact 13 rooms/65 trade gates/25 source walls/27 dated material IDs/12 exclusive branch-unit records, $23572.44 with 15% once, zero releases')
print('R24_MANIFEST_SHA',sha(M)['sha256'])
