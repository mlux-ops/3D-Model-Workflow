"""Independent read-only local R29 post-sign exact output/source/arithmetic/gates audit.
Local verification is NOT a non-Pro independent Reviewer CONTINUE or owner release.
"""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING
import csv,json,hashlib,re
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r29-sandstone-niche-shared-cutstock'
def d(x):return Decimal(str(x))
def fp(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def rd(name):
 with (O/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
M=O/'MANIFEST.json'
SHA='d3cf560c43c970e172cb2ebec187ebbc1b25472a2de86398a807cfca8300ef70'
assert fp(M)['sha256']==SHA
m=json.loads(M.read_text(encoding='utf-8'))
assert len(m['outputs'])==15 and all(fp(O/n)==v for n,v in m['outputs'].items())
assert m['original_historic_room_ids']==13 and m['original_historic_tile_rows']==27 and m['original_W_source_studies']==25 and m['original_trade_actions']==65
assert m['two_unpriced_Primary_niche_reference_rows_NO_SCOPE_NO_ORDER']==2
assert m['original_four_unit_tile_only_USD']=='23572.44' and m['original_15pct_waste_applied_once_in_gross']
assert m['original_eight_Sandstone_niche_receiver_gross_SF']=='51.64' and m['original_eight_Sandstone_niche_material_only_USD']=='358.92'
assert m['original_Grey_Soft_2copy_PH2_TX3_gross_SF']=='165.4' and m['original_Grey_Soft_2copy_PH2_TX3_material_only_USD']=='1116.46'
for key in ('owner_approval','architect_release','plumber_release','waterproof_installer_release','tile_installer_release','supplier_material_reservation','GC_release','purchasing_release','entire_13_room_global_DONE','R29_new_blind_source_frozen','R29_critic_dispatch','actual_correct_1529_niche_dimensions_and_constructed_count_verified','actual_1to1_samples_or_renderings_created'):
 assert m[key] is False,key
assert m['R29_weighted_score'] is None and m['original_DESIGN_worker_9']=='FAILED' and m['independent_nonPro_Reviewer_worker_15']=='FINISHED_NONREVIVABLE'
assert m['R014_authentic_original_critics']==6 and m['R014_required_critics']==8 and m['R017_independent_preflight'] is None
assert m['maker_individual_wet_WALL_PH3_original_Opal']=='FAIL'
assert m['maker_individual_wet_NICHE_Sandstone']=='PASS'
assert m['predecessor_manifest_SHA256']['R28']=='45db073bc7e78509627a01ea599ecfd291a0cbcacd5cc9c07a1126f6568c8212'
assert m['predecessor_manifest_SHA256']['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
for key,path in (
 ('R28','deliverables/integrated-r28-wc-primary-floor-flange-threshold/MANIFEST.json'),
 ('R23_LOCAL_FIXED_UNREVIEWED','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R017','state/ROUND017_SUBMISSION.json'),
 ('R014','state/ROUND014_SUBMISSION.json')
):
 assert fp(R/path)['sha256']==m['predecessor_manifest_SHA256'][key]

counts={
'R29_8_SOURCE_SANDSTONE_NICHE_RECEIVER_AND_FULL_SCALE_WITNESS.csv':8,
'R29_128_W3_ILLUSTRATIVE_NICHE_APERTURE_RETURN_SILL_PIER_CUT_STOCK.csv':128,
'R29_24_PROVISIONAL_FOUR_ROOM_W1_W3_2X20_WALL_EDGE_MODULE_AND_TRIM.csv':24,
'R29_64_THEORETICAL_2X20_NICHE_BACK_TO_RETURN_STRIP_CUTSTOCK_CAPS.csv':64,
'R29_10_HISTORIC_GROSS_CEIL_CASE_POOLING_SENSITIVITIES_NOT_ORDERS.csv':10,
'R29_5_ACTUAL_SAME_MATERIAL_GROUPS_AND_HARD_NONPOOLING_RULES.csv':5,
'R29_27_ORIGINAL_MATERIAL_SOURCE_TO_CONDITIONAL_SKU_LOT_RECEIVING.csv':27,
'R29_12_FOUR_BATH_SANDSTONE_WET_NICHE_GOOD_BETTER_BEST.csv':12,
'R29_13_ROOM_CONDITIONAL_SOURCE_MAKER_TRADE_AND_PURCHASE_RELEASE.csv':13,
'R29_104_13ROOM_EIGHT_TRADE_SEQUENTIAL_SHOP_AND_OWNER_GATES.csv':104,
'R29_13_ROOM_TWO_COPY_HISTORIC_COST_VS_ACTUAL_2026_BID_NORMALIZATION.csv':13,
'R29_8_PHYSICAL_ROOM_W1W3_NICHE_SILL_TRIM_SAMPLE_AND_CAMERAS.csv':8}
assert all(len(rd(n))==q for n,q in counts.items())
focus={'PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3'}
receiver=rd('R29_8_SOURCE_SANDSTONE_NICHE_RECEIVER_AND_FULL_SCALE_WITNESS.csv')
assert len({(q['room'],q['physical_source_unit_room_number']) for q in receiver})==8
assert {q['room'] for q in receiver}==focus
assert sum(d(q['source_historic_per_copy_GROSS_SF_original_15pct_once']) for q in receiver)==d('51.64')
assert sum(d(q['source_historic_per_copy_material_USD']) for q in receiver)==d('358.92')
assert all(q['actual_same_lot_verified']=='FALSE' and q['purchase_released']=='FALSE' and q['installer_physical_1to1_mockup']=='FALSE' for q in receiver)

scenarios=rd('R29_128_W3_ILLUSTRATIVE_NICHE_APERTURE_RETURN_SILL_PIER_CUT_STOCK.csv')
for q in scenarios:
 w,h,depth,j=map(d,(q['hypothetical_OPENING_width_in'],q['hypothetical_OPENING_height_in'],q['hypothetical_REVEAL_depth_in'],q['illustrative_joint_in']))
 aperture=w*h/d(144); sides=2*h*depth/d(144);tops=w*depth/d(144); net=aperture+sides+2*tops
 assert abs(d(q['displaced_one_field_OPENING_SF'])-aperture)<=d('0.00005')
 assert abs(d(q['hypothetical_Sandstone_back_returns_sill_NET_SF_no_waste'])-net)<=d('0.00005')
 assert abs(d(q['source_field_W3_FULL_FACE_SF_unverified'])-d(q['source_W3_WIDTH_in_UNVERIFIED'])*d(q['source_W3_tile_height_in_UNVERIFIED'])/144)<=d('0.00005')
 assert q['niche_selected_on_W3']=='FALSE' and q['owner_signed']=='FALSE' and q['purchase_release']=='FALSE'
assert len({(q['room'],q['receiver']) for q in scenarios})==8
example=next(q for q in scenarios if q['room']=='PH-BATH3' and q['hypothetical_OPENING_width_in']=='24' and q['illustrative_joint_in']=='0.125')
assert example['projected_side_pier_under_3_in']=='TRUE'
assert d(example['illustrative_nominal_three_in_PIER_after_joint_each_in'])==d('1.8550')

wall=rd('R29_24_PROVISIONAL_FOUR_ROOM_W1_W3_2X20_WALL_EDGE_MODULE_AND_TRIM.csv')
assert len({(q['room'],q['source_wall'],q['assumed_grout_joint_in']) for q in wall})==24
assert all(q['actual_field_exposed_edges_LF']=='' and q['purchase_released']=='FALSE' for q in wall)
strips=rd('R29_64_THEORETICAL_2X20_NICHE_BACK_TO_RETURN_STRIP_CUTSTOCK_CAPS.csv')
assert all(q['saw_kerf_glaze_cut_edge_and_tile_caliber_considered']=='FALSE' and q['purchasing_release']=='FALSE' for q in strips)
groups=rd('R29_5_ACTUAL_SAME_MATERIAL_GROUPS_AND_HARD_NONPOOLING_RULES.csv')
assert d(groups[0]['original_two_copy_GROSS_SF_15pct_once'])==d('51.64') and d(groups[0]['historic_material_only_USD_two_copies'])==d('358.92')
assert d(groups[1]['original_two_copy_GROSS_SF_15pct_once'])==d('165.4') and d(groups[1]['historic_material_only_USD_two_copies'])==d('1116.46')
assert all(q['supplier_signed_reservation']=='FALSE' and q['purchase_authorized']=='FALSE' for q in groups)
cases=rd('R29_10_HISTORIC_GROSS_CEIL_CASE_POOLING_SENSITIVITIES_NOT_ORDERS.csv')
for q in cases:
 gross=d(q['source_historic_gross_two_copies_SF_15pct_included'])
 box=d(q['hypothetical_case_coverage_SF_NOT_VERIFIED'])
 assert int(q['all_eight_or_four_room_instances_if_one_lot_cases_THEORETICAL'])==int((gross/box).to_integral_value(rounding=ROUND_CEILING))
 assert q['actual_factory_case_coverage_SF']=='' and q['purchase_release']=='FALSE'
assert next(q for q in cases if q['group']=='SANDSTONE_NICHE' and q['hypothetical_case_coverage_SF_NOT_VERIFIED']=='8')['all_eight_or_four_room_instances_if_one_lot_cases_THEORETICAL']=='7'

rows=rd('R29_27_ORIGINAL_MATERIAL_SOURCE_TO_CONDITIONAL_SKU_LOT_RECEIVING.csv')
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig') as f:old=list(csv.DictReader(f))
assert [(q['room'],q['original_source_row_id']) for q in rows]==[(q['room'],q['source_row_id']) for q in old]
assert sum(d(q['original_material_ONLY_USD_two_copies'] or '0') for q in rows)==d('23572.44')
assert sum(q['unpriced_primary_niche_REFERENCE_NO_SCOPE_NO_ORDER']=='TRUE' for q in rows)==2
assert all(q['purchasing_release']=='FALSE' and q['same_factory_shade_caliber_lot']=='FALSE' for q in rows)
tiers=rd('R29_12_FOUR_BATH_SANDSTONE_WET_NICHE_GOOD_BETTER_BEST.csv')
assert len({(q['room'],q['tier']) for q in tiers})==12
assert all(q['owner_selected']=='FALSE' and q['purchasing_release']=='FALSE' for q in tiers)
assert all(q['other_current_individual_WALL_status'].startswith('OPAL_FAIL') for q in tiers if q['room']=='PH-BATH3')
main=rd('R29_13_ROOM_CONDITIONAL_SOURCE_MAKER_TRADE_AND_PURCHASE_RELEASE.csv')
all_ids={q['id'] for q in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert {q['room'] for q in main}==all_ids
assert all(q['purchaser_order_authorized']=='FALSE' and q['supplier_chicago_offer_and_same_shade_lot_signed']=='FALSE' and q['GC_installed_bid_signed']=='FALSE' for q in main)
trade=rd('R29_104_13ROOM_EIGHT_TRADE_SEQUENTIAL_SHOP_AND_OWNER_GATES.csv')
assert len({(q['room'],q['sequence']) for q in trade})==104 and all(q['release_authorized']=='FALSE' for q in trade)
cost=rd('R29_13_ROOM_TWO_COPY_HISTORIC_COST_VS_ACTUAL_2026_BID_NORMALIZATION.csv')
assert sum(d(q['source_historic_material_ONLY_USD_two_copies']) for q in cost)==d('23572.44')
assert all(q['new_owner_approved_setting_waterproof_trim_grout_labor_bid_USD']=='' and q['purchaser_authorized']=='FALSE' for q in cost)
shops=rd('R29_8_PHYSICAL_ROOM_W1W3_NICHE_SILL_TRIM_SAMPLE_AND_CAMERAS.csv')
assert len({(q['room'],q['source_room_number']) for q in shops})==8 and all(q['camera_views_produced']=='FALSE' and q['purchasing_release']=='FALSE' for q in shops)

with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig') as f:assert len(list(csv.DictReader(f)))==25
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig') as f:assert len(list(csv.DictReader(f)))==65
for name in m['outputs']:
 if name.endswith('.md'):
  for link in re.findall(r'\]\(([^)]+)\)',(O/name).read_text(encoding='utf-8')):
   assert link.startswith(('https://','http://')) or (O/link).exists(),(name,link)
report=(R/'state/ROUND029_INDEPENDENT_NONPRO_REVIEWER_REPORT_PREPARED_NOT_SENT.md').read_text(encoding='utf-8')
assert len(report)<=4000
assert [q for q in report.splitlines() if q in ('GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT')]==['GOAL','WHAT I DID','EVIDENCE','OPEN ISSUES','WHAT I PLAN NEXT']
status=(R/'state/ROUND029_CURRENT_ACTIVE_BOARD_FIVE_LINE_STATUS.txt').read_text(encoding='utf-8').splitlines()
assert len(status)==5 and status[0]=='STATUS round=017 phase=4-deepen'
assert (R/'state/LEDGER.md').read_text(encoding='utf-8').count('## R29 four-bath shared Sandstone wet niche cut-stock and all-13-room supplier quote-normalization cycle')==1
s17=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert s17['critic_dispatch']=='NOT_DISPATCHED' and s17['predispatch_reviewer_verdict'] is None
print('PASS R29 READ-ONLY 15 SHA+bytes, 128 niche deductions/returns, 24 W1-W3 module, 64 cutstock, 10 hypothetical cases, 8 actual receivers, 27 original rows, 13 room/104 trade gates, historic $23572.44 once, zero releases')
print('R29_SHA',SHA)
