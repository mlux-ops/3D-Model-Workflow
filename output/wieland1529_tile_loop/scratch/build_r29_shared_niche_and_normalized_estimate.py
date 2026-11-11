"""Additive R29 4-bath / eight-receiver niche-cut and cost normalization.
Original source files and previously signed rounds are always read-only.
"""
from pathlib import Path
import csv,json,math
from decimal import Decimal,ROUND_HALF_UP,ROUND_CEILING

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r29-sandstone-niche-shared-cutstock'
O.mkdir(parents=True,exist_ok=True)
D=lambda x: Decimal(str(x))
def n(x):return str(D(x).quantize(D('0.0001'),rounding=ROUND_HALF_UP))
def ce(x):return int(D(x).to_integral_value(rounding=ROUND_CEILING))
def load(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(name,rows):
 p=O/name
 assert rows and not p.exists(),name
 with p.open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
roomdata={r['id']:r for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert len(roomdata)==13
source=load(R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
walls=load(R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv')
assert len(source)==27 and len(walls)==25
assert sum(D(x['historic_usd_two_copies']) for x in source if x['historic_usd_two_copies'])==D('23572.44')
assert sum(x['historic_niche_excluded_no_scope']=='TRUE' for x in source)==2
focus=['PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3']
names={'PH-BATH2':'Sapphire','PH-BATH3':'Opal','TX-BATH2':'Copper','TX-BATH3':'Emerald'}
fixtures={
 'PH-BATH2':'Duravit 700332000000090 tub; Hansgrohe Matte White trim 15758701 and iBox 01850181; selected separate white tub waste/overflow, no PAN',
 'PH-BATH3':'Hansgrohe Chrome 15758001 + iBox 01850181; Delta DT062412 Chrome 4-inch square POINT shower only if owner WALK-IN; owner basin UNSELECTED',
 'TX-BATH2':'Duravit 700332000000090 tub; Hansgrohe Chrome; own selected Westbrass waste/overflow; basin UNSELECTED; no tiled PAN',
 'TX-BATH3':'Brizo Black Onyx T755110-BNXLHP + R75000-WS; selected BT062415-BNX square POINT only if owner WALK-IN; no owner-selected bathtub'
}
wallsby={(x['room'],x['wall']):x for x in walls}
for rid in focus:
 assert [q['surface'] for q in roomdata[rid]['carried_tile_rows']]==['wall','floor','accent']
 assert (rid,'W1') in wallsby and (rid,'W3') in wallsby
 assert len(roomdata[rid]['revit_room_numbers'])==2
accents={rid:next(x for x in source if x['room']==rid and x['source_surface']=='accent') for rid in focus}
assert all('sandstone' in next(x for x in roomdata[r]['carried_tile_rows'] if x['surface']=='accent')['carried_description'].lower() for r in focus)
assert sum(D(x['source_gross_sf_one_copy_waste_15pct_once']) for x in accents.values())*2==D('51.64')
assert sum(D(x['historic_usd_two_copies']) for x in accents.values())==D('358.92')

# One receiver per actual old/source unit; the niche may not actually exist as drawn.
receivers=[]
for rid in focus:
 for unit in roomdata[rid]['revit_room_numbers']:
  q=accents[rid]
  receivers.append(dict(room=rid,physical_source_unit_room_number=unit,manufacturer_product='ELM Surfaces Tones Sandstone 2x20 Glossy 8.5mm',
    individual_wet_NICHE_listed='TRUE',source_historic_accent_row_id=q['source_row_id'],
    source_historic_per_copy_GROSS_SF_original_15pct_once=q['source_gross_sf_one_copy_waste_15pct_once'],
    source_historic_per_copy_material_USD=q['historic_usd_one_copy'],
    conditional_owner_actual_tub_or_walkin='UNSELECTED' if rid.endswith('BATH3') else 'TUB_SELECTED',
    actual_site_1529_niche_exists='',actual_niche_quantity='',actual_selected_tiled_wall_id='',actual_niche_inside_width_in='',actual_niche_inside_height_in='',actual_reveal_depth_in='',actual_sill_pitch_and_waterproof_method='',actual_same_20in_calibrated_cut_reuse='',actual_same_Sandstone_factory_SKU='',actual_same_lot_verified='FALSE',
    receiver_signed_allocated_cases='',installer_physical_1to1_mockup='FALSE',owner_signed='FALSE',waterproof_signed='FALSE',architect_signed='FALSE',GC_signed='FALSE',supplier_offer_verified='FALSE',purchase_released='FALSE'))
assert len(receivers)==8
save('R29_8_SOURCE_SANDSTONE_NICHE_RECEIVER_AND_FULL_SCALE_WITNESS.csv',receivers)

# A credible synthetic material/cut study, NOT a hypothetical complete shop drawing:
# aperture imagined in each room W3 for calculation only (W3 is not a confirmed niche wall).
systems=[]
for rec in receivers:
 rid=rec['room'];w3=wallsby[rid,'W3']
 wallW=D(w3['source_width_in_UNVERIFIED']);wallH=D(w3['source_tiled_height_in_UNVERIFIED'])
 assert wallH==D(93)
 for width in (12,16,20,24):
  for depth in (3,4):
   for joint in (D('0.125'),D('0.1875')):
    high=D(12)
    niche_back=D(width)*high/D(144)
    sides=D(2)*high*D(depth)/D(144)
    top=D(width)*D(depth)/D(144)
    sill=top
    net=niche_back+sides+top+sill
    field_area=wallW*wallH/D(144)
    only_one_displaced_face=niche_back
    remaining_field=field_area-only_one_displaced_face
    sidePier=(wallW-D(width)-D(2)*joint)/D(2)
    theoretical_nominal_courses=ce((high+joint)/(D(2)+joint))
    raw_leftover_per_full_length_20=D(20)-D(width) if width<=20 else None
    historical_gross=D(rec['source_historic_per_copy_GROSS_SF_original_15pct_once'])
    systems.append(dict(room=rid,receiver=rec['physical_source_unit_room_number'],source_W3_WIDTH_in_UNVERIFIED=n(wallW),
       source_W3_tile_height_in_UNVERIFIED=n(wallH),niche_selected_on_W3='FALSE',
       hypothetical_OPENING_width_in=str(width),hypothetical_OPENING_height_in=str(high),hypothetical_REVEAL_depth_in=str(depth),
       illustrative_joint_in=str(joint),source_field_W3_FULL_FACE_SF_unverified=n(field_area),
       displaced_one_field_OPENING_SF=n(only_one_displaced_face),hypothetical_field_after_one_opening_SF=n(remaining_field),
       Sandstone_BACK_SF_count_once=n(niche_back),Sandstone_TWO_SIDE_RETURNS_SF_count_once=n(sides),
       Sandstone_TOP_RETURN_SF_count_once=n(top),Sandstone_SILL_SF_count_once=n(sill),
       hypothetical_Sandstone_back_returns_sill_NET_SF_no_waste=n(net),
       historical_Sandstone_original_GROSS_SF_per_receiver_15pct_once=str(historical_gross),
       hypothetical_net_exceeds_original_historic_gross='TRUE' if net>historical_gross else 'FALSE',
       wet_opening_4_exposed_edge_nominal_LF=n(D(2)*(D(width)+high)/D(12)),
       illustrative_nominal_three_in_PIER_after_joint_each_in=n(sidePier),
       projected_side_pier_under_3_in='TRUE' if sidePier<D(3) else 'FALSE',
       nominal_2in_courses_for_12in_height_NOT_FACTORY_CALIBRATED=theoretical_nominal_courses,
       hypothetical_nominal_20in_strip_offcut_after_ONE_back_course_in='' if raw_leftover_per_full_length_20 is None else n(raw_leftover_per_full_length_20),
       can_reuse_offcut_in_actual_side_returns='UNVERIFIED_SAW_KERF_WATERPROOF_AND_DIRECTION',
       new_NET_plus_ONE_owner_approved_waste_not_deduced_from_old_GROSS='TRUE',
       verified_correct_1529_wall_location='FALSE',actual_niche_number='',actual_frambacking_waterproof_sill_shop='',
       exact_individual_current_tile_SKU_color_lot='',actual_case_usable_SF='',current_Chicago_offer='',
       owner_signed='FALSE',architect_signed='FALSE',installer_1to1_test='FALSE',purchase_release='FALSE'))
assert len(systems)==128
save('R29_128_W3_ILLUSTRATIVE_NICHE_APERTURE_RETURN_SILL_PIER_CUT_STOCK.csv',systems)

# True source group, shared receiver floors, excluded close visual matches; old material unchanged.
groupdefs=[
 ('Tones Sandstone 2x20 Glossy NICHE',focus,'accent','conditional_identical_color_finish_NO_LOT','Manufacturer Sandstone individual wet wall PASS; all eight actual niche exists/amount and identical exact factory code/lot unverified'),
 ('Cortar Grey 12x24 Soft LEVEL',['PH-BATH2','TX-BATH3'],'floor','conditional_identical_color_finish_NO_RAW_LAB','Same historic name & old rate, no individual original exact numeric measured wet LEVEL report or actual exact factory orderable SKU; NOT shower PAN'),
 ('Cortar Bone 12x24 Soft LEVEL OUTSIDE FOCUS',['PH-BATH3','TX-BATH4'],'floor','FUTURE_ONLY_NO_R29_DOUBLE_ORDER','Similar old manufacturer product identity but TX4 tub and PH3 conditional; not included in R29 Sandstone priority cash change'),
 ('Clara Tierra Madre Caviar 2x8 NICHE NEVER RESERVE',['PH-BATH4','TX-BATH4'],'accent','FORBIDDEN_WET_NICHE','Original individual maker wet NICHE permission absent; similar accent name does not make it Sandstone'),
 ('Primary mixed Soft LEVEL and AntiSlip LINEAR PAN + inherited WC',['PH-PRIMARY','TX-PRIMARY'],'floor','FORBIDDEN_AS_ONE_ACTUAL_SKU','Old source is deliberately mixed finishes/levels/PAN, seeded WCs already included ONCE; R28 controls and no new WC order')
]
groups=[]
for name,rooms,surf,grade,reason in groupdefs:
 qs=[q for q in source if q['room'] in rooms and q['source_surface']==surf]
 gross=sum(D(q['source_gross_sf_one_copy_waste_15pct_once']) for q in qs)*2
 hist=sum(D(q['historic_usd_two_copies'] or '0') for q in qs)
 groups.append(dict(group=name,group_type=grade,source_room_ids=';'.join(rooms),
   original_source_rows=';'.join(q['source_row_id'] for q in qs),original_two_copy_GROSS_SF_15pct_once=n(gross),
   historic_material_only_USD_two_copies=n(hist),same_factory_SKU_and_color_finish_test='UNVERIFIED',
   actual_owner_branch_and_room_release='FALSE',actual_identical_SHADE_LOT='FALSE',usable_actual_box_SF='',
   verified_current_Chicago_material_price='',actual_installed_tile_bid='',actual_receiving_unit_allocation='',
   original_raw_numeric_LEVEL_test='FALSE_IF_FLOOR',original_PAN_cross_use='FORBIDDEN',
   independent_wet_WALL_NICHE_maker_permission='PASS_SANSTONE_ONLY' if name.startswith('Tones Sandstone') else 'EXACT_INDIVIDUAL_EVIDENCE_REQUIRED',
   manufacturer_and_prohibition_reason=reason,original_15pct_already_in_gross_once='TRUE',
   supplier_signed_reservation='FALSE',owner_approved='FALSE',GC_release='FALSE',purchase_authorized='FALSE'))
assert len(groups)==5
assert D(groups[0]['original_two_copy_GROSS_SF_15pct_once'])==D('51.64')
assert D(groups[0]['historic_material_only_USD_two_copies'])==D('358.92')
assert D(groups[1]['original_two_copy_GROSS_SF_15pct_once'])==D('165.4')
assert D(groups[1]['historic_material_only_USD_two_copies'])==D('1116.46')
save('R29_5_ACTUAL_SAME_MATERIAL_GROUPS_AND_HARD_NONPOOLING_RULES.csv',groups)

# Quantify ORIGINAL gross ceiling only with fictional carton capacities.
# Compare gross pooled vs separately rounded each of eight original units; not an installed savings.
cartons=[]
for grp,rooms,surf in [('SANDSTONE_NICHE',focus,'accent'),('GREY_SOFT_LEVEL',['PH-BATH2','TX-BATH3'],'floor')]:
 qs=[q for q in source if q['room'] in rooms and q['source_surface']==surf]
 one_areas=[D(q['source_gross_sf_one_copy_waste_15pct_once']) for q in qs]
 one_sum=sum(one_areas)*2
 assert (grp=='SANDSTONE_NICHE' and one_sum==D('51.64')) or (grp=='GREY_SOFT_LEVEL' and one_sum==D('165.4'))
 for case_sf in (D(5),D(8),D(10),D(16),D(20)):
  one_each=sum(2*ce(q/case_sf) for q in one_areas)
  room_two=sum(ce(2*q/case_sf) for q in one_areas)
  whole=ce(one_sum/case_sf)
  cartons.append(dict(group=grp,source_historic_gross_two_copies_SF_15pct_included=n(one_sum),
    actual_factory_case_coverage_SF='',hypothetical_case_coverage_SF_NOT_VERIFIED=str(case_sf),
    individually_rounded_per_room_instance_cases_THEORETICAL=one_each,
    individually_rounded_per_two_copy_room_type_cases_THEORETICAL=room_two,
    all_eight_or_four_room_instances_if_one_lot_cases_THEORETICAL=whole,
    theoretical_only_cases_difference_per_instance_vs_pooled=one_each-whole,
    theoretical_only_cases_difference_room_pair_vs_pooled=room_two-whole,
    financially_verified_savings_USD='',actual_supplier_whole_cases='',actual_cross_unit_cut_share='',latest_supplier_offer_or_stock='',
    old_original_15pct_added_again='FALSE',old_source_material_quote_changed='FALSE',owner_approved='FALSE',purchase_release='FALSE'))
assert len(cartons)==10
save('R29_10_HISTORIC_GROSS_CEIL_CASE_POOLING_SENSITIVITIES_NOT_ORDERS.csv',cartons)

# A more meaningful physically coherent upper bound on 20in strip offcuts.
strip=[]
for rid in focus:
 for side in (12,16,20,24):
  for niche_count in (1,2):
   # 12 in high niche; two inch tile horizontal nominal courses, no actual calibrated joints.
   courses=6*niche_count
   for depth in (3,4):
    back_needed=2 if side>20 else 1
    leftover_length=(D(20)-D(side)) if side<=20 else D(20)-(D(side)-D(20))
    potential_per_course=int((leftover_length/D(depth)).to_integral_value(rounding='ROUND_FLOOR')) if leftover_length>0 else 0
    returns_per_course=2
    max_useful_back_offcut_returns=min(courses*returns_per_course,courses*potential_per_course)
    strip.append(dict(room=rid,hypothetical_niches_one_or_two_per_room=niche_count,one_niche_inside_width_in=side,one_niche_inside_height_in=12,
      hypothetical_reveal_depth_in=depth,nominal_2in_courses_total=6*niche_count,nominal_20in_back_tiles_per_course=back_needed,
      theoretical_full_20in_BACK_tiles_consumed=courses*back_needed,
      nominal_remnant_after_last_back_tile_each_course_in=n(leftover_length),
      theoretical_SIDE_RETURN_strips_needed=2*courses,
      theoretical_side_return_strip_count_from_BACK_offcut_upper_bound_NO_KERF=max_useful_back_offcut_returns,
      saw_kerf_glaze_cut_edge_and_tile_caliber_considered='FALSE',actual_joint_spacing_and_number_courses_measured='FALSE',
      manufacturer_exact_Sandstone_same_factory_caliber_lot='FALSE',actual_wall_niche_and_reveal_verification='FALSE',
      feasibility_requires_1to1_physical_cut_sheet='TRUE',actual_cutstock_transfer_SF='',actual_money_saved_USD='',owner_approved='FALSE',purchasing_release='FALSE'))
assert len(strip)==64
save('R29_64_THEORETICAL_2X20_NICHE_BACK_TO_RETURN_STRIP_CUTSTOCK_CAPS.csv',strip)

# Additional 27-row trace makes each material scope classification, same-lot options and economic boundary explicit.
rowbridge=[]
for q in source:
 rid=q['room'];sf=q['source_surface'];grp='NO_SHARED_IDENTICAL_SKU_PROVEN'
 for g in groups:
  if q['source_row_id'] in g['original_source_rows'].split(';'):grp=g['group']
 rowbridge.append(dict(room=rid,original_source_row_id=q['source_row_id'],original_surface=sf,
  original_GROSS_SF_one_copy_waste_ALREADY_15pct=q['source_gross_sf_one_copy_waste_15pct_once'],
  original_GROSS_SF_two_copies=n(D(q['source_gross_sf_one_copy_waste_15pct_once'])*2),
  original_material_ONLY_USD_two_copies=q['historic_usd_two_copies'],
  source_selected_or_conditional_product=q['source_trace'][:220],pool_candidate_or_exclusion_group=grp,
  unpriced_primary_niche_REFERENCE_NO_SCOPE_NO_ORDER='TRUE' if q['historic_niche_excluded_no_scope']=='TRUE' else 'FALSE',
  original_collected_allocation_15pct_already_once='TRUE',actual_field_NET_area_SF='',distinct_levels_and_sloped_POINT_LINEAR_pan='',niche_displaced_wall_field_SF_once='',
  niche_back_returns_top_sill_NET_SF_once='',actual_new_owner_approved_waste_only_after_NET='',same_exact_current_maker_color_finish_SKU='',same_factory_shade_caliber_lot='FALSE',
  confirmed_factory_case_usable_SF='',confirmed_Chicago_price_offer_date='',manufacturer_public_MSRP='',public_retail_reference='',actual_installed_GC_bid_USD='',
  owner_signed='FALSE',architect_signed='FALSE',supplier_allocation_signed='FALSE',GC_release='FALSE',purchasing_release='FALSE'))
assert len(rowbridge)==27
save('R29_27_ORIGINAL_MATERIAL_SOURCE_TO_CONDITIONAL_SKU_LOT_RECEIVING.csv',rowbridge)

# Four rooms x three genuinely different source-coherent owner configurations.
alt={
 'PH-BATH2':[
  ('GOOD','Retain individually wet-listed Tones Sapphire 2x20 Glossy tub WALL, independently wet-listed Sandstone NICHE, Grey 12x24 Soft LEVEL, selected Duravit Starck tub and Hansgrohe MATTE WHITE','One historic 3.67SF gross per copy Sandstone niche, no PAN; W1 59.496in/ W3 30.6in historic width; actual 59in tub wall flange still not physically checked','Lowest visual/material change and permitted wet wall; current SKU/lot/level raw lab and installed bid unknown'),
  ('BETTER','Keep selected exact Sapphire/Sandstone products; put an owner-signed single-piece Sandstone sill and calibrated Sandstone 2x20 stack against actual Sapphire W3 joint grid','Actual niche not confirmed; 20in nominal full-piece sill only if verified opening and depth joint fit, real 8.5mm tile caliper and waterproof return; one opening deducted from Sapphire field, backs/returns/sill added once','Controlled niche cut stock and less visible metal edging can improve buyer detailing; custom waterproof and labor not priced'),
  ('BEST','Conditional same ELM Tones wet-listed Sandstone niche with a deliberate Sapphire-to-Sandstone course alignment and finished termination, not another niche; compare maker-compatible optional metal-free corner versus signed trim profile','No new product picked; require physical same-lot sample, wet backing/membrane and tub flange clip, original Grey LEVEL raw lab, full installed edge/setting/bid','High quality alignment without unsupported premium tile substitution; possible extra craftsmanship cost, not approved')
 ],
 'PH-BATH3':[
  ('GOOD','Retain historic Tones Opal 2x20 Glossy as archival ONLY, Sandstone wet-listed NICHE, Cortar Bone Soft LEVEL and Hansgrohe Chrome selected shower; DO NOT INSTALL OPAL WET without individual maker wet authorization','The old Opal wet WALL application is not individually listed; owner TUB/WALK-IN and basin unselected, Delta DT062412 POINT only if WALK-IN. NO maker-approved wall release','Original palette may read calm with Chrome, but unsupported wet use is a HARD FAIL, not a purchase-ready good choice'),
  ('BETTER','Conditional replace wet WALL only with individually wet-listed ELM Tones Sapphire 2x20 Glossy, same maker 8.5mm nominal and retain Sandstone NICHE; no selection/point drain change','Sapphire is a distinct COLOR and order line, not transferred maker approval; source W1 60.0 W3 27.96in, actual 24in illustrative niche centered on W3 leaves <3in side piers. Obtain new owner samples/installed bid','Defensible wet-wall correction, shares possible Sapphire exact SKU with PH2 if same maker lot/color/finish, but no proved cost saving'),
  ('BEST','Conditional wet-approved Sapphire tiled wall with independently permitted Sandstone tone-on-tone niche, calibrated stagger/stack course and minimized exposed trim; keep both Bath3 program branches','If owner TUB: independent selected tub waste/overflow, no tiled PAN. If WALK-IN: conditional original Delta Chrome POINT four-plane small-format PAN with its own exact raw lab, waterproof shop. No PH basin assignment','Resale-value improvement is compliant cohesive wet use and measured niche/slope, not invented upgrade price; owner aesthetic and program unresolved')
 ],
 'TX-BATH2':[
  ('GOOD','Retain individual wet-listed Tones Copper 2x20 Glossy WALL, Sandstone 2x20 wet NICHE, Cortar Clay Soft LEVEL, actual Duravit tub with Hansgrohe CHROME','Historical TX2 Sandstone niche 8.63SF gross per copy, original W1 62.484 W3 31.2in, physical 59in Duravit tub plus wall build-up require signed flange and tub waste','Warm/copper palette and Chrome retained for buyer, no tiled shower PAN; raw exact Clay LEVEL lab and actual cut net unknown'),
  ('BETTER','Same Copper/Sandstone wet-listed products with centered actual niche back/sill and course termination on nominal 2x20 calibrated tile, no second niche','Use a real 1:1 8.5mm Copper/Sandstone sample, pitch sill/waterproof complete corners, no extra wall field quantity for niche back, same Sandstone lot only if source geometry confirmed','Potential cleaner mixed warm accent and lower cut labor through cross-unit 2x20 coordinated shop; no proven carton savings'),
  ('BEST','Conditional Copper Wet Areas WALL with Sandstone wet niche feature balanced at owner-signed tub spout/Chrome valve elevations, calibrated round-corner trim/plane change options','Actual TX2 W1 62.484 vs 59in tub no proven fit; sign flange/end support, membrane and grille edge BEFORE estimating joint/base/trim, preserve Clay LEVEL exact maker raw lab','Improves construction confidence with same approved maker palette, but no added niche, tub swap or premium substitute allowed')
 ],
 'TX-BATH3':[
  ('GOOD','Retain historic separately wet-listed Tones Emerald 2x20 Glossy wall, wet-listed Sandstone NICHE, Cortar Grey Soft LEVEL and selected Brizo Black Onyx shower POINT conditionally','Reconfirm inaccessible individual Emerald maker product page wet approval; original LEVEL exact raw numeric missing and conditional POINT PAN not specified/tested, owner TUB/WALK-IN unselected','Emerald and Black Onyx buyer appearance remains conditionally coherent; not currently procurement-ready'),
  ('BETTER','Keep original Emerald wall color and Sandstone niche, with a true shared Grey 12x24 Soft LEVEL case/finish/caliber study with PH-BATH2 only if exact manufacturer source/lab approved','Niche W3 31.2in historic, source accent4.89SF per copy; coordinate niche actual width/returns and repeat tile courses, no Panther shower pan substitution or gross double count','Potential fewer split cases between same Grey Soft level floors, but no current factory SKU/case/real cut-share so monetary savings zero'),
  ('BEST','Conditional Emerald wet WALL re-certified individual lot and Sandstone niche module edge discipline, coupled with real signed Black Onyx POINT shower or separate owner tub branch','If WALK-IN: Brizo BT062415-BNX 4in square four-plane PAN with separately selected small-format original measured raw wet numeric lab and membrane shop. If TUB: no selected tub, require independently approved tub/waste/overflow; no PH basin gap imported','High-impact buyer/GC value through reliable drain-to-wall assembly and source-coherent niche design; branch must remain unselected')
 ]
}
opts=[]
for rid,items in alt.items():
 assert len(items)==3
 rd=roomdata[rid]
 for tier,proposal,detail,value in items:
  opts.append(dict(room=rid,tier=tier,source_board_status=rd['status'],source_champion_id=rd['champion_id'] or '',
    original_weighted_score='' if rd['champion_score'] is None else str(rd['champion_score']),
    original_room_tile_only_per_copy_USD=str(rd['carried_quote_material_subtotal_usd_per_unit']),
    original_niche_gross_per_copy_with_historic_waste=str(accents[rid]['source_gross_sf_one_copy_waste_15pct_once']),
    exact_selected_plumbing_retained=fixtures[rid],manufacturer_specific_source_design=proposal,
    field_shop_niche_cut_rough_wet_controls=detail,Old_Town_buyer_and_incremental_value=value,
    maker_Sandstone_individual_wet_NICHE='PASS_CURRENT_INDIVIDUAL_PRODUCT_PAGE',
    other_current_individual_WALL_status={'PH-BATH2':'SAPPHIRE_PASS','PH-BATH3':'OPAL_FAIL_SAPPHIRE_CONDITIONAL_PASS','TX-BATH2':'COPPER_PASS','TX-BATH3':'EMERALD_PRIOR_MAKER_PASS_CURRENT_REVALIDATION_REQUIRED'}[rid],
    bath_LEVEL_raw_exact_measured_wet_DCOF='MISSING',conditional_POINT_PAN_raw_exact_measured_wet_DCOF='N_A_TUB_ONLY' if rid.endswith('BATH2') else 'MISSING_IF_WALKIN',
    real_1529_niche_dimensions_and_wall='MISSING',exact_factory_orderable_SKU_and_Chicago_lot='MISSING',
    current_installed_change_bid='',owner_selected='FALSE',architect_released='FALSE',GC_released='FALSE',purchasing_release='FALSE'))
assert len(opts)==12
save('R29_12_FOUR_BATH_SANDSTONE_WET_NICHE_GOOD_BETTER_BEST.csv',opts)
print('PASS R29 built 8 niche receivers, 128 niche wall/returns/sill scenarios, 64 strip cutstock caps, 10 hypothetical carton ceilings, 5 material group rules, 27 source rows and 12 owner tiers')
