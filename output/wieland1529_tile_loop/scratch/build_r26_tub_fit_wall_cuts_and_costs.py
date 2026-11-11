"""Additive R26 four-room dimensional sensitivities and auditable historical price deltas.
All source lengths are NOT 1529-verified; study assumptions are NOT fabrication clearances.
"""
from pathlib import Path
import csv,math,json
from decimal import Decimal,ROUND_CEILING,ROUND_HALF_UP
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r26-tx-primary-and-three-duravit-tubs'
def D(x):return Decimal(str(x))
def fmt(x,n='0.001'):return str(D(x).quantize(D(n),rounding=ROUND_HALF_UP))
def read(path):
 with (R/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(name,records):
 assert records
 p=O/name;assert not p.exists(),name
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
foc={'TX-PRIMARY','PH-BATH2','TX-BATH2','TX-BATH4'}
walls=[r for r in read('deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv') if r['room'] in foc]
assert len(walls)==11
# TX Primary 24/48 flat clay field, the 3 TUB rooms 2x20 Tones or 24x48 flat Charcoal.
schemas={
 'TX-PRIMARY':[('Flat Cortar Clay 24x48 Soft long-side 48 inch horizontal',D('48'),D('0.125')),('Flat Cortar Clay short-side 24 inch horizontal',D('24'),D('0.125'))],
 'PH-BATH2':[('Tones Sapphire long side 20 inch horizontal',D('20'),D('0.125')),('Tones Sapphire short side 2 inch horizontal for vertical brick concept',D('2'),D('0.125'))],
 'TX-BATH2':[('Tones Copper long side 20 inch horizontal',D('20'),D('0.125')),('Tones Copper short side 2 inch horizontal for vertical brick concept',D('2'),D('0.125'))],
 'TX-BATH4':[('Flat Cortar Charcoal 24x48 long side 48 inch horizontal',D('48'),D('0.125')),('Flat Cortar Charcoal short side 24 inch horizontal',D('24'),D('0.125'))],
}
layouts=[]
for r in walls:
 width=D(r['source_width_in_UNVERIFIED']);height=D(r['source_tiled_height_in_UNVERIFIED'])
 for label,module,j in schemas[r['room']]:
  # Number of full-width interior tiles constrained by two equal terminal pieces and N+1 joints.
  n=max(0,math.floor((width-j)/(module+j)))
  while n>0 and width-n*module-(n+1)*j <=0:n-=1
  cut=(width-n*module-(n+1)*j)/2
  layouts.append(dict(room=r['room'],wall=r['wall'],source_W_in_UNVERIFIED=fmt(width),source_H_in_UNVERIFIED=fmt(height),scenario_tile_direction=label,nominal_module_in=fmt(module),illustrative_grout_joint_in=fmt(j),full_centered_modules=n,nominal_symmetric_end_cut_in=fmt(cut),needs_actual_cut_or_sliver_redesign='YES_NOMINAL_LESS_THAN_3' if cut<D(3) else 'FIELD_CALIBER_REQUIRED',source_FULL_FACE_SF_pre_openings=fmt(width*height/D(144)),theoretical_top_plus_two_vertical_trim_LF_MAX_NOT_ORDER=fmt((width+2*height)/D(12)),actual_opening_dimensions='',actual_niche_field_aperture_displacement_SF='',actual_niche_back_returns_sill_added_SF='',actual_jamb_glass_tub_flange_exposed_trim_LF='',actual_change_of_plane_movement_LF='',actual_1529_checked_W_H='',actual_tile_caliber_and_approved_grout='',actual_pan_slope_and_field_rough='N/A_TUB' if r['room']!='TX-PRIMARY' else 'NEEDS_LINEAR_SHOP',raw_exact_LEVEL_wet_DCOF='',raw_exact_LINEAR_PAN_wet_DCOF='N/A_TUB' if r['room']!='TX-PRIMARY' else '',owner_approval='FALSE',tile_installer_acceptance='FALSE',procurement_release='FALSE',source='deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv'))
assert len(layouts)==22 and len({(r['room'],r['wall']) for r in layouts})==11
save('R26_11_WALLS_22_TILE_AXIS_JOINT_CUT_TRIM_STUDIES.csv',layouts)

fit=[]
# Nominal source W1 width NOT a post-backboard/finish clear span.
# Demonstrate actual required field width = tub nominal + both side build-ups + clearance, and tolerances.
for room,w in [('PH-BATH2','59.496'),('TX-BATH2','62.484'),('TX-BATH4','60.000')]:
 for each_side in ['0.25','0.50','0.75','1.00']:
  real=D(w);tub=D(59);side=D(each_side)
  theoretical_clear=real-2*side
  residual=theoretical_clear-tub
  fit.append(dict(room=room,source_W1_before_finish_in_UNVERIFIED=w,selected_Duravit_700332_nominal_tub_length_in='59',illustrative_both_walls_extra_build_up_in_each=each_side,theoretical_remaining_clear_after_two_fictitious_symmetric_buildups_in=fmt(theoretical_clear),theoretical_clear_minus_nominal_tub_in=fmt(residual),is_nominal_fit_sensitivity_only='TRUE',manufacturer_and_owner_final_tolerance_in='',actual_1529_rough_opening_and_wall_plumb_in='',tub_actual_factory_max_measure_in='',actual_pre_or_post_finish_W1_definition='',exact_approved_tub_three_side_flange_product_and_width='',actual_supported_tub_frame_and_floor_slope='',actual_end_fill_or_tiling_return_detail='',actual_foot_end_overflow_drain_clearance='',architect_site_signed='FALSE',plumber_site_signed='FALSE',GC_released='FALSE',purchasing_released='FALSE'))
assert len(fit)==12
save('R26_12_TUB_ALCOVE_NOMINAL_FINISH_BUILDUP_FIT_SENSITIVITY.csv',fit)

hist=read('deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
assert len(hist)==27
assert sum(D(x['historic_usd_two_copies']) for x in hist if x['historic_usd_two_copies'])==D('23572.44')
mat=[]
for r in hist:
 rid=r['room']
 row=dict(room=rid,source_material_row_id=r['source_row_id'],source_surface=r['source_surface'],source_GROSS_with_original_15pct_per_copy=r['source_gross_sf_one_copy_waste_15pct_once'],historical_material_USD_per_copy=r['historic_usd_one_copy'],historical_material_USD_2copies=r['historic_usd_two_copies'],original_unpriced_primary_niche_NO_SCOPE=r['historic_niche_excluded_no_scope'],current_original_quote_historic_only='TRUE',source_quoted_2026_09_03='TRUE',reused_same_historical_material_price_as_new_quote='FALSE',actual_1529_NET_sf='',actual_current_selected_program_branch='',real_original_gross_deducted_openings_once='',new_level_and_separate_pan_net_no_overlap='',new_same_lot_carton_yield_sf='',real_orderable_cases='',manufacturer_MSRP_reference='',public_retail_indication='',current_verified_Chicago_vendor_offer='',current_supplier_case_lot_ETA='',current_installed_GC_bid='',approved_owner_upgrade_cap='',verified_change_order_delta='',owner_signature='FALSE',GC_signature='FALSE',purchase_release='FALSE')
 mat.append(row)
assert len(mat)==27
save('R26_27_HISTORICAL_TO_CURRENT_PROCUREMENT_COST_SCOPE_BRIDGE.csv',mat)

# Historic same-SKU changed-scope illustration only. Original quote is NOT a newly offered price.
q=[]
for r in hist:
 if r['room'] not in foc or r['historic_niche_excluded_no_scope']=='TRUE' or not r['historic_usd_one_copy']:continue
 gross=D(r['source_gross_sf_one_copy_waste_15pct_once'])
 rate=D(r['historic_usd_one_copy'])/gross
 for quantity_change in ['-2.0','0.0','2.0']:
  delta=D(quantity_change)
  q.append(dict(room=r['room'],source_material_row_id=r['source_row_id'],source_surface=r['source_surface'],original_gross_SF_per_copy_including_15pct=fmt(gross),historical_extended_USD_per_copy=r['historic_usd_one_copy'],arithmetic_derived_historical_USD_per_SF_NOT_OFFER=fmt(rate,'0.0001'),hypothetical_net_quantity_adjustment_SF_per_copy_NO_ADDITIONAL_WASTE=quantity_change,historical_same_price_linear_change_USD_two_copies=fmt(delta*rate*2,'0.01'),qualification='ILLUSTRATIVE_HISTORICAL_RATE_ONLY; NOT alternative SKU price, current offer, actual net, or payable shortage',verified_case_covered_Chicago_offer='',actual_field_measurement='',owner_upgrade_cap='',GC_installed_cost='',architect_signed='FALSE',GC_signed='FALSE',purchasing_released='FALSE'))
assert len(q)>0
save('R26_OLD_SAME_MATERIAL_RATE_ONLY_PLUS_MINUS_2SF_TWO_UNIT_SENSITIVITY.csv',q)
print('PASS R26 11 focus source wall keys/22 orientation+joint cases, 12 hypothetical three-tub finish-fit studies, 27 original material-to-current procurement rows,',len(q),'same-original-rate-only historic quote arithmetic scenarios')
