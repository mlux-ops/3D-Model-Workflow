"""One-time R29 additive output signatures + exact original SHA chain. Never rerun after signing."""
from pathlib import Path
from decimal import Decimal
import csv,json,re,hashlib
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r29-sandstone-niche-shared-cutstock'
names=sorted(p.name for p in O.iterdir() if p.is_file() and p.suffix in ('.md','.csv'))
assert len(names)==15 and all(not name.endswith('MANIFEST.json') for name in names)
def fp(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def rd(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
lookup={
 'R29_8_SOURCE_SANDSTONE_NICHE_RECEIVER_AND_FULL_SCALE_WITNESS.csv':8,
 'R29_128_W3_ILLUSTRATIVE_NICHE_APERTURE_RETURN_SILL_PIER_CUT_STOCK.csv':128,
 'R29_24_PROVISIONAL_FOUR_ROOM_W1_W3_2X20_WALL_EDGE_MODULE_AND_TRIM.csv':24,
 'R29_64_THEORETICAL_2X20_NICHE_BACK_TO_RETURN_STRIP_CUTSTOCK_CAPS.csv':64,
 'R29_5_ACTUAL_SAME_MATERIAL_GROUPS_AND_HARD_NONPOOLING_RULES.csv':5,
 'R29_10_HISTORIC_GROSS_CEIL_CASE_POOLING_SENSITIVITIES_NOT_ORDERS.csv':10,
 'R29_27_ORIGINAL_MATERIAL_SOURCE_TO_CONDITIONAL_SKU_LOT_RECEIVING.csv':27,
 'R29_12_FOUR_BATH_SANDSTONE_WET_NICHE_GOOD_BETTER_BEST.csv':12,
 'R29_13_ROOM_CONDITIONAL_SOURCE_MAKER_TRADE_AND_PURCHASE_RELEASE.csv':13,
 'R29_104_13ROOM_EIGHT_TRADE_SEQUENTIAL_SHOP_AND_OWNER_GATES.csv':104,
 'R29_13_ROOM_TWO_COPY_HISTORIC_COST_VS_ACTUAL_2026_BID_NORMALIZATION.csv':13,
 'R29_8_PHYSICAL_ROOM_W1W3_NICHE_SILL_TRIM_SAMPLE_AND_CAMERAS.csv':8
}
assert len(lookup)==12 and all(len(rd(n))==num for n,num in lookup.items())
assert sum(Decimal(r['source_historic_material_ONLY_USD_two_copies']) for r in rd('R29_13_ROOM_TWO_COPY_HISTORIC_COST_VS_ACTUAL_2026_BID_NORMALIZATION.csv'))==Decimal('23572.44')
assert sum(Decimal(r['original_material_ONLY_USD_two_copies'] or '0') for r in rd('R29_27_ORIGINAL_MATERIAL_SOURCE_TO_CONDITIONAL_SKU_LOT_RECEIVING.csv'))==Decimal('23572.44')
assert len({r['room'] for r in rd('R29_13_ROOM_CONDITIONAL_SOURCE_MAKER_TRADE_AND_PURCHASE_RELEASE.csv')})==13
assert len({(r['room'],r['receiver']) for r in rd('R29_128_W3_ILLUSTRATIVE_NICHE_APERTURE_RETURN_SILL_PIER_CUT_STOCK.csv')})==8
for n in names:
 if n.endswith('.md'):
  for link in re.findall(r'\]\(([^)]+)\)',(O/n).read_text(encoding='utf-8')):
   assert link.startswith(('http://','https://')) or (O/link).exists(),(n,link)
for n in lookup:
 for r in rd(n):
  for k,v in r.items():
   if k.lower() in ('owner_signed','owner_approved','owner_selected','purchase_release','purchase_released','purchase_authorized','purchasing_release','gc_release','gc_signed','supplier_offer_verified','material_reservation_release','purchaser_order_authorized'):
    assert v in ('FALSE','','NOT_APPLICABLE'),(n,k,v)

pred={}
for key,file in (
 ('R12','deliverables/integrated-r12/MANIFEST.json'),
 ('R23_LOCAL_FIXED_UNREVIEWED','deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json'),
 ('R24','deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/MANIFEST.json'),
 ('R25','deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc/MANIFEST.json'),
 ('R26','deliverables/integrated-r26-tx-primary-and-three-duravit-tubs/MANIFEST.json'),
 ('R27','deliverables/integrated-r27-powder-value-and-13room-procurement/MANIFEST.json'),
 ('R28','deliverables/integrated-r28-wc-primary-floor-flange-threshold/MANIFEST.json'),
 ('R014','state/ROUND014_SUBMISSION.json'),('R015','state/ROUND015_SUBMISSION.json'),
 ('R016','state/ROUND016_SUBMISSION.json'),('R017','state/ROUND017_SUBMISSION.json')
 ):
 pred[key]=fp(R/file)['sha256']
assert pred['R28']=='45db073bc7e78509627a01ea599ecfd291a0cbcacd5cc9c07a1126f6568c8212'
assert pred['R017']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
src17=json.loads((R/'state/ROUND017_SUBMISSION.json').read_text(encoding='utf-8'))
assert src17['critic_dispatch']=='NOT_DISPATCHED' and src17['predispatch_reviewer_verdict'] is None and len(src17['confidential_prime_only_mappings'])==4
assert len(json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms'])==13
orig=[]
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig') as f:orig=list(csv.DictReader(f))
assert len(orig)==27 and sum(Decimal(q['historic_usd_two_copies'] or '0') for q in orig)==Decimal('23572.44')
assert sum(q['historic_niche_excluded_no_scope']=='TRUE' for q in orig)==2
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig') as f:assert len(list(csv.DictReader(f)))==25
with (R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv').open(encoding='utf-8-sig') as f:assert len(list(csv.DictReader(f)))==65
manifest=dict(
 round='R29',date='2026-11-06',kind='ADDITIVE four wet-bath Tones Sandstone same-source 2x20 niche receiver and eight-unit cutstock/13-room procurement normalization; no scored/owner-approved changes',
 focus_rooms=['PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3'],
 signed_output_count=len(names),new_eight_individual_niche_receivers=8,new_W3_illustrative_niche_back_side_top_sill_cases=128,
 new_W1_W2_W3_provisional_wall_module_trim_cases=24,new_nominal_2x20_back_return_cutstock_upper_bound_cases=64,
 new_theoretical_case_rounding_pool_sensitivities=10,new_conditional_same_material_and_forbidden_groups=5,
 new_original_27_line_current_lot_receiving_bridge=27,new_four_focus_room_owner_design_tiers=12,
 new_actual_unit_specific_1to1_sample_camera_requests=8,new_source_true_camera_briefs_unproduced=24,
 new_all_13_room_trade_and_wet_raw_lab_release_register=13,new_owner_arch_plumb_wp_tile_supplier_GC_purchaser_steps=104,
 new_all_13_room_historical_vs_current_offer_and_installed_bid_normalization=13,
 original_historic_room_ids=13,original_historic_tile_rows=27,original_W_source_studies=25,original_trade_actions=65,
 two_unpriced_Primary_niche_reference_rows_NO_SCOPE_NO_ORDER=2,original_four_unit_tile_only_USD='23572.44',original_15pct_waste_applied_once_in_gross=True,
 original_eight_Sandstone_niche_receiver_gross_SF='51.64',original_eight_Sandstone_niche_material_only_USD='358.92',
 original_Grey_Soft_2copy_PH2_TX3_gross_SF='165.4',original_Grey_Soft_2copy_PH2_TX3_material_only_USD='1116.46',
 actual_individual_current_factory_Sandstone_SKU_color_caliber_current_lot_verified=False,
 actual_correct_1529_niche_dimensions_and_constructed_count_verified=False,actual_1to1_samples_or_renderings_created=False,
 exact_individual_original_maker_RAW_numeric_wet_LEVEL_PAN_labs_received=False,current_Chicago_supplier_offer_case_stock_installed_bid_verified=False,
 maker_individual_wet_WALL_PH3_original_Opal='FAIL',maker_individual_wet_NICHE_Sandstone='PASS',maker_individual_wet_WALL_TX3_Emerald='HISTORICAL_PASS_FRESH_RENEWAL_NEEDED',
 owner_Bath3_program_selected=False,PH_Bath3_basin_selected=False,original_DESIGN_worker_9='FAILED',
 R014_authentic_original_critics=6,R014_required_critics=8,R015_three_seat_partial_dispatch='HOLD',
 R016_original_critic_dispatch='NOT_DISPATCHED',R017_original_critic_dispatch='NOT_DISPATCHED',R017_independent_preflight=None,
 R29_new_blind_source_frozen=False,R29_critic_dispatch=False,R29_weighted_score=None,
 independent_nonPro_Reviewer_worker_15='FINISHED_NONREVIVABLE',R23_POST_FIX1_independent_clearance=None,R24_to_R29_independent_acceptance=None,
 owner_approval=False,architect_release=False,plumber_release=False,waterproof_installer_release=False,tile_installer_release=False,
 supplier_material_reservation=False,GC_release=False,purchasing_release=False,entire_13_room_global_DONE=False,
 predecessor_manifest_SHA256=pred,outputs={n:fp(O/n) for n in names}
)
m=O/'MANIFEST.json';assert not m.exists(),'Do not overwrite signed R29'
m.write_bytes((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print('PASS R29 '+str(len(names))+' signed outputs and complete original 13/27/25/65, 8 receivers, 128 openings, 24 wall modules, 64 cutstock, 104 stage gates; all release FALSE')
print('R29_MANIFEST_SHA',fp(m)['sha256'])
