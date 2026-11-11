"""R24 additive 1529 provisional source-driven elevations, mutually exclusive branch takeoffs and trade checkpoints.
Original Revit/Smartsheet, frozen candidates, old packages NEVER written.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv,json,math
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions'
O.mkdir(parents=True,exist_ok=True)
def readcsv(path):
 with (R/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def csvout(filename,rows):
 assert rows
 p=O/filename
 assert not p.exists(),f'R24 output exists: {filename}'
 with p.open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n',extrasaction='raise');writer.writeheader();writer.writerows(rows)
def dec(x):return Decimal(str(x))
def fmt(x,prec='0.001'):return str(x.quantize(Decimal(prec),rounding=ROUND_HALF_UP))

rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
ids=[r['id'] for r in rooms]
assert len(set(ids))==len(ids)==13
source=readcsv('deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/R23_27_HISTORICAL_ROWS_TO_NET_CARTON_COST_PROVENANCE_CONTROL.csv')
walls=readcsv('deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv')
gates=readcsv('deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/R23_13_ROOM_SKU_WET_WALL_NICHE_LEVEL_PAN_RELEASE_MATRIX.csv')
assert len(source)==27 and len(walls)==25 and len(gates)==13
amount=sum((dec(x['historic_usd_two_copies']) for x in source if x['historic_usd_two_copies']),Decimal('0'))
assert amount==Decimal('23572.44')
assert sum(1 for r in source if r['historic_niche_excluded_no_scope']=='TRUE')==2

focus={
 'PH-BATH3':{'program':'TUB_UNSELECTED_OR_WALKIN_UNSELECTED','shower_drain':'Delta DT062412 4in square Chrome POINT','tub_waste':'UNSELECTED new tub manufacturer waste and overflow; Delta square shower drain NOT tub waste','wall':'ELM Tones Sapphire 2x20 Glossy, individual wet WALL listing; historical Opal NOT individually listed','niche':'ELM Tones Sandstone 2x20 Glossy wet NICHE listing','level':'RL21 12x24 Matte LEVEL conditional; raw exact numerical wet test absent','pan':'RL21 1.5in hex Matte 4-plane POINT PAN only if WALK-IN; raw exact numerical wet absent','point':True,'linear':False,'tile_long':20,'tile_short':2,'selected_rough':'Hansgrohe 01850181 iBox for selected chrome shower; separately confirm Delta point drain factory rough and membrane','physical_source':'Original tub alcove 5.00 x 2.33 ft drawing only; width for actual tub finish clearance unmeasured'},
 'TX-BATH3':{'program':'TUB_UNSELECTED_OR_WALKIN_UNSELECTED','shower_drain':'Brizo BT062415-BNX Black Onyx 4in square POINT','tub_waste':'UNSELECTED new tub manufacturer waste and overflow; Brizo square shower drain NOT tub waste','wall':'ELM Tones Emerald 2x20 Glossy individual wet WALL listed','niche':'ELM Tones Sandstone 2x20 Glossy individual wet NICHE listed','level':'Original Cortar Grey Soft LEVEL raw test absent or conditional Prime RL21 12x24 separately tested','pan':'Conditional Prime RL21 1.5in hex small format 4-plane POINT PAN only if WALK-IN, raw exact numerical wet absent','point':True,'linear':False,'tile_long':20,'tile_short':2,'selected_rough':'Brizo R75000-WS selected shower valve rough, separately selected square drain factory interface','physical_source':'Original tub alcove 5.10 x 2.60 ft drawing only; no owner tub selected'},
 'PH-BATH4':{'program':'WALKIN_CONFIRMED_POINT','shower_drain':'Brizo BT062415-BNX Black Onyx 4in square POINT','tub_waste':'N/A no tub in PH Bath4','wall':'Individually maker wet-listed flat Cortar Bone Soft conditional; source full Bone Ribbed NOT maker individually wet-listed','niche':'Individually wet-listed ELM Soho Black 2x10 conditional; historical Clara Caviar not individually wet listed','level':'Glazzio HNC6615 12x24 Matte LEVEL study, maker bound not raw numeric wet result','pan':'Glazzio HNC6715 2x2 matte hex 4-plane POINT PAN conditional, maker >0.50 bound NOT raw numeric wet result','point':True,'linear':False,'tile_long':24,'tile_short':12,'selected_rough':'Brizo selected 4in square shower drain factory clamping liner/preslope detail to coordinate, R75000-WS valve rough','physical_source':'OWNER 35 SF vs prior DRAWING 27 SF remain distinct; 107.2 SF/copy full Ribbed source x2 = 214.4 vendor total audit; Soft/AntiSlip conflict'},
 'PH-PRIMARY':{'program':'LINEAR_SHOWER_WITH_SEPARATE_SELECTED_DURAVIT_TUB','shower_drain':'Brizo BT0734816-BNX 48in Black Onyx LINEAR + separate BR73480 rough','tub_waste':'Selected separate Duravit 700337000000090 tub and own tub waste/overflow separate from shower linear','wall':'Individually maker wet-listed flat Cortar Bone Soft wet WALL conditional; source Reed/Ribbed relief wet approval absent','niche':'NO PRIMARY NICHE. Two unpriced historic niche refs are NO SCOPE / NO ORDER','level':'Prime RL21 12x24 Matte LEVEL (includes PH WC once), maker Target not raw wet test','pan':'Prime RL21 1.5in hex Matte LINEAR PAN, maker Target not raw numeric wet lab; inspect BNX solid vs tile-in 7-18mm, 1/4 versus 5/16 mosaic','point':False,'linear':True,'tile_long':24,'tile_short':12,'selected_rough':'BR73480 factory internally sloped channel/tiling aid, check selected 48in trim riser, waterproof junction and selected tub rough independently','physical_source':'Two original source shower walls W1 70.248 in/W2 55.752 in 111in height; source wall gross 143 SF includes ceiling, floor 135.6 SF includes WC and shower pan ONCE'},
}

branch_rows=[]
for rid,cfg in focus.items():
 g=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 variants=['TUB_CONDITIONAL','WALKIN_POINT_CONDITIONAL'] if rid.endswith('BATH3') else ['WALKIN_POINT_SELECTED'] if rid=='PH-BATH4' else ['SELECTED_48IN_LINEAR_AND_SEPARATE_TUB']
 for physical in g['revit_room_numbers']:
  for variant in variants:
   tub=variant.startswith('TUB_')
   pan='N/A_TUB_NO_TILED_SHOWER_PAN' if tub else 'SEPARATE_POINT_PAN_RAW_EXACT_WET_DCOF_REQUIRED' if cfg['point'] else 'SEPARATE_LINEAR_PAN_RAW_EXACT_WET_DCOF_REQUIRED'
   branch_rows.append(dict(room=rid,physical_unit=physical,owner_program_branch=variant,owner_program_selected='FALSE' if rid.endswith('BATH3') else 'TRUE_FIXED_EXISTING_SOURCE_ONLY',selected_existing_shower_drain_applies='FALSE_NO_TUB_WASTE' if tub else 'TRUE_CONDITIONAL_SHOWER_ONLY' if rid.endswith('BATH3') else 'TRUE_EXISTING',shower_drain_original_SKU_finish=cfg['shower_drain'],tub_model_waste_and_flange=cfg['tub_waste'],selected_shower_rough_and_interface=cfg['selected_rough'],individual_wall_wet_maker=cfg['wall'],individual_niche_wet_maker=cfg['niche'],separate_LEVEL_product=cfg['level'],separate_PAN_product=cfg['pan'] if not tub else 'N/A',PAN_raw_numeric_wet_test_gate=pan,LEVEL_raw_numeric_wet_test_gate='MISSING_EXACT_MEASURED_NUMERIC_SKU_RESULT',actual_1529_room_confirmed='FALSE',real_1529_drain_center_and_rough_elevation_in='',actual_owner_approved_tub_and_waste='',survey_floor_LEVEL_NET_sf='',survey_shower_PAN_NET_sf='' if not tub else 'N/A',verified_maker_compatible_membrane='',true_slope_and_drain_edge_shop='',tub_flange_glass_threshold_shops='',owner_signature='FALSE',architect_signature='FALSE',plumber_signature='FALSE',tile_installer_signature='FALSE',GC_signature='FALSE',purchasing_release='FALSE',source='../../rooms/'+rid+'/geometry.json; ../../rooms/'+rid+'/plumbing.json; manufacturer refs in R24 four wet room details'))
assert len(branch_rows)==12
csvout('R24_12_WET_UNIT_OWNER_BRANCH_AND_DRAIN_ROUGH_DECISION_MATRIX.csv',branch_rows)

quant=[]
for w in walls:
 rid=w['room'];cfg=focus.get(rid)
 W=dec(w['source_width_in_UNVERIFIED']);H=dec(w['source_tiled_height_in_UNVERIFIED'])
 face=(W*H/dec(144))
 if cfg:
  module=dec(cfg['tile_long']);
  # Nominal centered repeat with 2 side pieces; ignore calibrated grout/finish in these examples.
  n=max(0,int(W//module)-1)
  cut=(W-module*dec(n))/2
  # Alternative over-full layout can expose sliver and must not be presented as releasable.
  na=int(W//module)
  c2=(W-module*dec(na))/2
  nominal_perimeter=(W+H*2)/dec(12)
 else:
  n='';cut='';na='';c2='';nominal_perimeter=''
 quant.append(dict(room=rid,wall=w['wall'],source_width_in_NOT_VERIFIED=fmt(W),source_height_in_NOT_VERIFIED=fmt(H),source_gross_full_face_sf_NOT_VERIFIED=fmt(face),nominal_field_module_in=cfg['tile_long'] if cfg else '',two_balanced_end_cut_full_tile_count=n,idealized_two_balanced_end_cuts_in=fmt(cut) if cfg else '',idealized_max_full_tile_count=na,idealized_high_full_tile_count_end_cuts_in=fmt(c2) if cfg else '',nominal_wall_three_exposed_sides_LF_UPPER_BOUND_NOT_ORDER=fmt(nominal_perimeter) if cfg else '',nominal_all_edges_assumes_top_and_two_verticals='ILLUSTRATION_ONLY_NOT_ACTUAL_EXPOSED_TRIM',actual_width_in='',actual_height_in='',actual_tile_caliber_and_approved_grout_in='',actual_tile_pitch_and_origin='',actual_openings_sf='',niche_aperture_displaced_field_sf_once='',niche_back_tiled_sf='',niche_return_tiled_sf='',niche_sill_tiled_sf='',actual_net_WALL_tile_sf='',actual_exposed_edge_trim_LF='',movement_joint_change_of_plane_LF='',waterproofing_terminations_and_critical_penetrations='',calculated_actual_cut_with_grout_formula='(measured_wall_width - N*measured_caliber_tile_width - (N+1)*approved_joint_width)/2',actual_NET_formula='actual_W*H/144 - actual architectural openings - actual niche field aperture ONCE + actual niche back/returns/sill not otherwise included',verify_units_and_1529_true_field='FALSE',owner_approved='FALSE',GC_tile_shop_approved='FALSE',purchase_release='FALSE',source='../integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv'))
assert len(quant)==25
csvout('R24_25_W1_W3_ALTERNATE_CENTERING_CUT_EDGE_NET_SENSITIVITY.csv',quant)

cases=[]
for row in source:
 origin=dec(row['source_gross_sf_one_copy_waste_15pct_once']) if row['source_gross_sf_one_copy_waste_15pct_once'] else None
 # Reversal is an arithmetic benchmark only, NOT certified actual net scope.
 indicative=fmt(origin/dec('1.15')) if origin is not None else ''
 case=dict(room=row['room'],material_source_row_id=row['source_row_id'],source_surface=row['source_surface'],source_historic_gross_sf_with_one_15pct=fmt(origin) if origin is not None else '',arithmetic_gross_divided_by_1p15_sf_NOT_FIELD_NET=indicative,source_historic_usd_two_physical_units=row['historic_usd_two_copies'],historical_niche_excluded_NO_ORDER=row['historic_niche_excluded_no_scope'],branch_scope='NO_SCOPE_NO_ORDER' if row['historic_niche_excluded_no_scope']=='TRUE' else 'EXACT_SELECTED_BRANCH_REQUIRED' if row['room'] in ['PH-BATH3','TX-BATH3'] else 'SOURCE_COMPARATOR_ONLY',correct_actual_1529_NET_sf='',separate_actual_LEVEL_NET_sf='',separate_actual_PAN_NET_sf='',measured_displaced_niche_aperture_sf_once='',niche_back_returns_sill_added_once='',cut_waste_selected_for_NEW_NET_only='',supplier_exact_SKU_format_finish='',supplier_actual_same_lot_carton_yield_sf='',calculated_cartons='',case_formula='ceil( (approved verified net SF + approved documented once-only offcut/waste SF) / same-lot actual factory carton SF )',rounded_order_sf='',unverified_public_retail_reference_USD='',manufacturer_MSRP_reference_USD='',live_Chicago_verified_offer_USD='',verified_stock_ETA_and_case_allocation='',current_freight_tax_and_installed_GC_bid_USD='',owner_approved_upgrade_cap_USD='',price_delta_vs_historic_USD='',owner_signed='FALSE',GC_signed='FALSE',purchaser_released='FALSE')
 case['2026_09_03_historic_source_cost_type']='MATERIAL_ONLY_NOT_CURRENT_SUPPLIER_QUOTE'
 cases.append(case)
assert len(cases)==27
csvout('R24_27_MATERIAL_BRANCH_NET_CARTON_AND_COST_DELTA_RECONCILIATION.csv',cases)

for rid in ids:
 assert sum(dec(s['historic_usd_two_copies']) for s in source if s['room']==rid and s['historic_usd_two_copies'])==dec(next(x for x in rooms if x['id']==rid)['carried_quote_material_subtotal_usd_per_unit'])*2

print('PASS R24 new 12 unit branch combinations, 25 provisional alternate centering and edge studies, 27 material branch net/carton/cost deltas; 13 rooms, $23572.44 and original 15% once')
