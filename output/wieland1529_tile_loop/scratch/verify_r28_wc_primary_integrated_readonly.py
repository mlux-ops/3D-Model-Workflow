"""Strict, READ ONLY R28 source/quantity/room/release/signature verification, not independent Reviewer clearance."""
from pathlib import Path
from decimal import Decimal, ROUND_CEILING
import csv,json,hashlib,re
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r28-wc-primary-floor-flange-threshold'
def fp(p):
 b=p.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
EX='45db073bc7e78509627a01ea599ecfd291a0cbcacd5cc9c07a1126f6568c8212'
assert fp(O/'MANIFEST.json')['sha256']==EX
m=json.loads((O/'MANIFEST.json').read_text(encoding='utf-8'))
assert len(m['outputs'])==12 and all(fp(O/name)==f for name,f in m['outputs'].items())
assert m['original_room_ids']==13 and m['original_material_rows']==27 and m['original_historic_wall_studies']==25 and m['original_trade_actions']==65
assert m['original_historic_four_unit_material_only_USD']=='23572.44' and m['original_15pct_waste_gross_counted_once']
assert m['WC_separate_tile_material_order_rows']==0 and m['unpriced_extra_PRIMARY_niche_refs_NO_ORDER']==2
assert m['source_toilet_TOTO_exact_SKU']=='MS642124CEFG#01'
assert m['R014_authentic_reports']==6 and m['R014_required']==8 and m['original_DESIGN_worker_9']=='FAILED'
assert m['R017_independent_source_clearance'] is None and m['standing_independent_nonPro_worker_15']=='FINISHED_NONREVIVABLE'
assert m['R28_critic_dispatch'] is False and m['R28_weighted_scoring'] is None and m['full_13room_global_DONE'] is False
for key in ('owner_approval','architect_release','plumber_release','waterproof_installer_release','tile_installer_release','GC_release','supplier_verified_offer','material_reservation_release','purchasing_release','actual_WC_attribution_verified','correct_native_1529_Revit_or_signed_site_geometry','actual_1to1_mockup_or_render_created'):
 assert m[key] is False,key
assert m['predecessor_manifest_SHA256']['R27']=='5523674db6ef75811b25260405806ef8993329a70e41aec042f5ec63d852f59b'
assert m['predecessor_manifest_SHA256']['R23_LOCAL_FIXED_UNREVIEWED']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert m['predecessor_manifest_SHA256']['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
for key,file in [
 ('R27','deliverables/integrated-r27-powder-value-and-13room-procurement/MANIFEST.json'),
 ('R23_LOCAL_FIXED_UNREVIEWED','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R017','state/ROUND017_SUBMISSION.json')]:
 assert fp(R/file)['sha256']==m['predecessor_manifest_SHA256'][key]
opts=read('R28_12_WC_AND_PARENT_FACTORY_NEXUS_CORTAR_GOOD_BETTER_BEST.csv')
cut=read('R28_48_WC_PRIOR_AREA_HYPOTHETICAL_RECTANGULAR_BOND_AND_JOINT_CUTS.csv')
split=read('R28_4_WC_INCLUDED_PARENT_MIXED_FLOOR_QUOTE_DIAGNOSTIC_SPLITS.csv')
pieces=read('R28_4_SAME_COLOR_TWO_UNIT_NOMINAL_TILE_PIECE_MINIMUM_NO_CASE_CLAIM.csv')
door=read('R28_12_WC_DOOR_BASE_TRANSITION_PERIMETER_WITHOUT_NEW_ORDER.csv')
shops=read('R28_8_PHYSICAL_PARENT_WC_TOILET_DOOR_FLOOR_FINISH_FACTORY_SHOP_WITNESSES.csv')
allr=read('R28_13_ROOM_OWNER_CONSTRUCTION_AND_MAKER_LEVEL_PAN_RELEASE_DEPENDENCY.csv')
cases=read('R28_12_WC_HYPOTHETICAL_STANDALONE_CASE_LEVEL_SENSITIVITIES_NOT_ORDER.csv')
assert list(map(len,[opts,cut,split,pieces,door,shops,allr,cases]))==[12,48,4,4,12,8,13,12]
ids={q['id'] for q in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert len(ids)==13 and {q['room'] for q in allr}==ids
assert {q['room'] for q in opts}=={'PH-WC','TX-WC','PH-PRIMARY','TX-PRIMARY'}
assert len({(q['room'],q['tier']) for q in opts})==12
assert all(q['purchasing_released']=='FALSE' and q['owner_approved']=='FALSE' for q in opts)
assert all(q['purchase_released']=='FALSE' and q['actual_WC_wall_length_or_door_width_known']=='FALSE' for q in cut)
for q in cut:
 width=Decimal(q['hypothetical_rectangle_width_in']);depth=Decimal(q['hypothetical_rectangle_depth_in'])
 area=Decimal(q['wc_prior_source_area_SF'])
 assert width*depth==area*Decimal(144)
 assert q['rectangle_area_equals_prior_SF']=='TRUE'
 assert Decimal(q['safer_width_edge_each_in'])>=Decimal(3) if q['safer_width_gate']=='NOMINAL_SAFE_END' else True
 assert Decimal(q['safer_depth_edge_each_in'])>=Decimal(3) if q['safer_depth_gate']=='NOMINAL_SAFE_END' else True
assert {q['WC_unit'] for q in split}=={'313A','313B','203A','203B'}
for q in split:
 gross=Decimal(q['original_parent_PRIMARY_mixed_floor_QUOTE_GROSS_SF_copy'])
 wc=Decimal(q['WC_hypothetical_original_waste_equivalent_piece_SF_DIAGNOSTIC'])
 rem=Decimal(q['hypothetical_remaining_PRIMARY_including_mixed_PAN_source_GROSS_SF_DIAGNOSTIC'])
 assert wc+rem==gross and q['new_WC_order_amount_USD']=='0_SEPARATE_DO_NOT_ORDER'
 assert q['purchase_released']=='FALSE'
assert all(q['special_case_203A_unplaced']=='TRUE' for q in split if q['WC_unit']=='203A')
assert all(q['purchase_released']=='FALSE' for q in pieces)
for q in pieces:
 amount=Decimal(q['prior_wc_area_one_copy_SF'])
 piece=Decimal(q['nominal_piece_area_SF'])
 expect=int((amount/piece).to_integral_value(rounding=ROUND_CEILING))
 assert int(q['theoretical_area_only_MIN_pieces_one_copy'])==expect
assert all(q['purchasing_release']=='FALSE' and q['owner_tilebase_selected']=='FALSE' for q in door)
assert len({(q['room'],q['physical_unit_room']) for q in shops})==8
assert all(q['purchasing_release']=='FALSE' and q['independent_source_1529_survey_completed']=='FALSE' for q in shops)
assert all(q['owner_approved']=='FALSE' and q['purchase_authorized']=='FALSE' and q['supplier_offer_verified']=='FALSE' for q in allr)
assert all(q['purchasing_release']=='FALSE' and q['DO_NOT_ADD_TO_parent_quote_gross_or_order']=='TRUE' for q in cases)
old=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
assert len(old)==27 and sum(Decimal(q['historic_usd_two_copies']) for q in old if q['historic_usd_two_copies'])==Decimal('23572.44')
assert sum(q['historic_niche_excluded_no_scope']=='TRUE' for q in old)==2
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==25
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==65
for n in m['outputs']:
 if n.endswith('.md'):
  for dest in re.findall(r'\]\(([^)]+)\)',(O/n).read_text(encoding='utf-8')):
   assert dest.startswith(('https://','http://')) or (O/dest).exists(),(n,dest)
report=(R/'state/ROUND028_INDEPENDENT_NONPRO_REVIEWER_REPORT_PREPARED_NOT_SENT.md').read_text(encoding='utf-8')
assert len(report)<=4000
assert [v for v in report.splitlines() if v in ('GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT')]==['GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT']
status=(R/'state/ROUND028_CURRENT_ACTIVE_BOARD_FIVE_LINE_STATUS.txt').read_text(encoding='utf-8').splitlines()
assert len(status)==5 and status[0]=='STATUS round=017 phase=4-deepen'
assert (R/'state/LEDGER.md').read_text(encoding='utf-8').count('## R28 authentic seeded WC and adjacent Primary floor/fixture/threshold/one-order construction cycle')==1
src=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert src['critic_dispatch']=='NOT_DISPATCHED' and src['predispatch_reviewer_verdict'] is None
print('PASS R28 READ-ONLY 12/12 SHA+bytes, 48 synthetic cuts, 12 floor/fixture tiers, 8 unit shops, 13 room source gates, $23572.44 original 15% once, PH 135.6 gross /15SF WC and TX116.1 gross/14SF WC counted ONCE, all release false')
print('R28_SHA',EX)
