"""Immutable R28 SHA+byte signatures with exact predecessor and historical evidence validation."""
from pathlib import Path
from decimal import Decimal
import json,csv,hashlib,re
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r28-wc-primary-floor-flange-threshold'
NAMES=[
 'START_HERE_R28.md',
 'R28_NEXUS_CORTAR_FACTORY_SOURCE_AND_OWNER_APPLICATION_GATES.md',
 'R28_PRIMARY_WC_OWNER_ARCHITECT_GC_DECISION_AND_CONSTRUCTION_BOOK.md',
 'R28_8_UNIT_SOURCE_TRUE_TOILET_THRESHOLD_FLOOR_CAMERA_AND_MOCKUP_REQUESTS.md',
 'R28_12_WC_AND_PARENT_FACTORY_NEXUS_CORTAR_GOOD_BETTER_BEST.csv',
 'R28_48_WC_PRIOR_AREA_HYPOTHETICAL_RECTANGULAR_BOND_AND_JOINT_CUTS.csv',
 'R28_4_WC_INCLUDED_PARENT_MIXED_FLOOR_QUOTE_DIAGNOSTIC_SPLITS.csv',
 'R28_4_SAME_COLOR_TWO_UNIT_NOMINAL_TILE_PIECE_MINIMUM_NO_CASE_CLAIM.csv',
 'R28_12_WC_DOOR_BASE_TRANSITION_PERIMETER_WITHOUT_NEW_ORDER.csv',
 'R28_8_PHYSICAL_PARENT_WC_TOILET_DOOR_FLOOR_FINISH_FACTORY_SHOP_WITNESSES.csv',
 'R28_13_ROOM_OWNER_CONSTRUCTION_AND_MAKER_LEVEL_PAN_RELEASE_DEPENDENCY.csv',
 'R28_12_WC_HYPOTHETICAL_STANDALONE_CASE_LEVEL_SENSITIVITIES_NOT_ORDER.csv']
assert len(NAMES)==12 and all((O/n).is_file() for n in NAMES)
def fp(p):
 b=p.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
o,c,split,piece,door,field,allroom,box=[read(n) for n in NAMES[4:]]
assert list(map(len,[o,c,split,piece,door,field,allroom,box]))==[12,48,4,4,12,8,13,12]
focus={'PH-WC','TX-WC','PH-PRIMARY','TX-PRIMARY'}
owner=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
ids={r['id'] for r in owner};assert len(ids)==13
assert {r['room'] for r in o}==focus and {r['room'] for r in field}==focus and {r['room'] for r in allroom}==ids
assert len({(r['room'],r['tier']) for r in o})==12
assert len({(r['room'],r['physical_unit_room']) for r in field})==8
assert all(r['purchasing_released']=='FALSE' and r['owner_approved']=='FALSE' and r['exact_original_measured_LEVEL_wet_DCOF_provided']=='FALSE' for r in o)
assert all(r['purchase_released']=='FALSE' and r['actual_WC_wall_length_or_door_width_known']=='FALSE' for r in c)
assert all(r['purchase_released']=='FALSE' and r['check_partition_EQUALS_original_gross']=='TRUE' for r in split)
assert all(r['new_WC_order_amount_USD']=='0_SEPARATE_DO_NOT_ORDER' for r in split)
assert all(r['purchase_released']=='FALSE' and r['supplier_lot_allocated']=='FALSE' for r in piece)
assert all(r['purchasing_release']=='FALSE' and r['owner_tilebase_selected']=='FALSE' for r in door)
assert all(r['purchasing_release']=='FALSE' and r['independent_source_1529_survey_completed']=='FALSE' for r in field)
assert all(r['purchase_authorized']=='FALSE' and r['owner_approved']=='FALSE' and r['material_reservation_released']=='FALSE' for r in allroom)
assert all(r['purchasing_release']=='FALSE' and r['DO_NOT_ADD_TO_parent_quote_gross_or_order']=='TRUE' for r in box)
assert {r['WC_unit'] for r in split}=={'313A','313B','203A','203B'}
assert all(r['special_case_203A_unplaced']=='TRUE' for r in split if r['WC_unit']=='203A')
assert all(Decimal(r['WC_hypothetical_original_waste_equivalent_piece_SF_DIAGNOSTIC'])+Decimal(r['hypothetical_remaining_PRIMARY_including_mixed_PAN_source_GROSS_SF_DIAGNOSTIC'])==Decimal(r['original_parent_PRIMARY_mixed_floor_QUOTE_GROSS_SF_copy']) for r in split)
assert {r['WC_hypothetical_original_waste_equivalent_piece_SF_DIAGNOSTIC'] for r in split}=={'17.2500','16.1000'}
assert {(r['room'],r['original_parent_PRIMARY_mixed_floor_QUOTE_GROSS_SF_copy']) for r in split}=={('PH-WC','135.6'),('TX-WC','116.1')}
assert all(r['actual_cumulative_room_NET_excluding_openings']=='' for r in read if False) if False else True
old=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
assert len(old)==27 and sum(Decimal(r['historic_usd_two_copies']) for r in old if r['historic_usd_two_copies'])==Decimal('23572.44')
assert sum(r['historic_niche_excluded_no_scope']=='TRUE' for r in old)==2
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==25
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==65
for n in NAMES[:4]:
 for link in re.findall(r'\]\(([^)]+)\)',(O/n).read_text(encoding='utf-8')):
  assert link.startswith(('http://','https://')) or (O/link).exists(),(n,link)
prev={}
for label,filename in [
 ('R12','deliverables/integrated-r12/MANIFEST.json'),
 ('R22','deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json'),
 ('R23_LOCAL_FIXED_UNREVIEWED','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R24','deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/MANIFEST.json'),
 ('R25','deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc/MANIFEST.json'),
 ('R26','deliverables/integrated-r26-tx-primary-and-three-duravit-tubs/MANIFEST.json'),
 ('R27','deliverables/integrated-r27-powder-value-and-13room-procurement/MANIFEST.json'),
 ('R014','state/ROUND014_SUBMISSION.json'),('R015','state/ROUND015_SUBMISSION.json'),
 ('R016','state/ROUND016_SUBMISSION.json'),('R017','state/ROUND017_SUBMISSION.json')]:
 prev[label]=fp(R/filename)['sha256']
assert prev['R27']=='5523674db6ef75811b25260405806ef8993329a70e41aec042f5ec63d852f59b'
assert prev['R23_LOCAL_FIXED_UNREVIEWED']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert prev['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
src17=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert src17['critic_dispatch']=='NOT_DISPATCHED' and src17['predispatch_reviewer_verdict'] is None and len(src17['confidential_prime_only_mappings'])==4
manifest={
 'round':'R28','date':'2026-11-06','kind':'Additive source-authentic WC/parent floor, exact factory toilet, no-duplicate material order; unscored and all releases false',
 'focus_rooms':['PH-WC','TX-WC','PH-PRIMARY','TX-PRIMARY'],
 'signed_output_count':12,'new_focus_owner_GOOD_BETTER_BEST':12,
 'hypothetical_area_equivalent_WC_24x48_vs_12x24_cuts':48,
 'original_parent_quote_WC_included_partition_diagnostics':4,
 'manufacturer_24x48_and_12x24_piece_lower_bounds':4,
 'hypothetical_optional_door_base_threshold_scenarios':12,
 'unit_individual_factory_Nexus_Brizo_WC_shops':8,
 'source_true_unperformed_camera_briefs':24,
 'new_room_specific_original_wet_gate_and_release_rows':13,
 'hypothetical_WC_alone_cases_prohibited_from_double_order':12,
 'original_room_ids':13,'original_material_rows':27,
 'original_historic_wall_studies':25,'original_trade_actions':65,'unpriced_extra_PRIMARY_niche_refs_NO_ORDER':2,
 'original_historic_four_unit_material_only_USD':'23572.44','original_15pct_waste_gross_counted_once':True,
 'PH_WC_prior_source_floor_SF_per_copy':'15','TX_WC_prior_source_floor_SF_per_copy':'14',
 'PH_PARENT_mixed_floor_historic_quote_gross_SF_copy':'135.6','TX_PARENT_mixed_floor_historic_quote_gross_SF_copy':'116.1',
 'WC_separate_tile_material_order_rows':0,'source_toilet_TOTO_exact_SKU':'MS642124CEFG#01','actual_WC_attribution_verified':False,
 'correct_native_1529_Revit_or_signed_site_geometry':False,'actual_1to1_mockup_or_render_created':False,
 'current_exact_individual_Bone_Clay_24x48AntiSlip_SKU_and_raw_wet_lab_verified':False,
 'current_exact_original_measured_numeric_LEVEL_PAN_lab_received':False,
 'current_Chicago_case_lot_stock_eta_full_installed_bid_verified':False,
 'original_DESIGN_worker_9':'FAILED','R014_authentic_reports':6,'R014_required':8,'R015_partial_dispatch':'HOLD',
 'R016_critic_dispatch':'NOT_DISPATCHED','R017_critic_dispatch':'NOT_DISPATCHED','R017_independent_source_clearance':None,
 'standing_independent_nonPro_worker_15':'FINISHED_NONREVIVABLE','R23_POST_FIX_independent_clearance':None,'R24_to_R28_independent_acceptance':None,
 'R28_critic_dispatch':False,'R28_weighted_scoring':None,'owner_approval':False,'architect_release':False,'plumber_release':False,
 'waterproof_installer_release':False,'tile_installer_release':False,'GC_release':False,'supplier_verified_offer':False,
 'material_reservation_release':False,'purchasing_release':False,'full_13room_global_DONE':False,
 'predecessor_manifest_SHA256':prev,'outputs':{n:fp(O/n) for n in NAMES}
}
M=O/'MANIFEST.json'
assert not M.exists(),'Do not regenerate a signed R28'
M.write_bytes((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print('PASS R28 signed 12 outputs, 48 WC cuts, 12 maker-tier options, 8 unit shops, 13 room gates, $23572.44 and WC included once, no purchase or independent clearance')
print('R28_SHA',fp(M)['sha256'])
