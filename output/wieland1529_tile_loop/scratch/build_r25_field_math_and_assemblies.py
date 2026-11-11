"""New R25 source-linked wet layout/case PH4 scenario and actual branch-specific trade evidence.
No original files touched; hypothetical field and waste assumptions are never purchase quantities.
"""
from pathlib import Path
import csv,json,math
from decimal import Decimal,ROUND_CEILING,ROUND_HALF_UP
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r25-manufacturer-verified-assemblies-and-owner-gc'
def read(name):
 with (R/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def put(name,data):
 assert len(data)>0
 p=O/name;assert not p.exists(),name
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n')
  w.writeheader();w.writerows(data)
def D(x):return Decimal(str(x))
def nd(x,n='0.001'):return str(x.quantize(D(n),rounding=ROUND_HALF_UP))
walls=read('deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv')
oldmat=read('deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
branch=read('deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_12_WET_UNIT_OWNER_BRANCH_AND_DRAIN_ROUGH_DECISION_MATRIX.csv')
assert (len(walls),len(oldmat),len(branch))==(25,27,12)
assert sum(D(x['historic_usd_two_copies']) for x in oldmat if x['historic_usd_two_copies'])==D('23572.44')
assert sum(x['historic_niche_excluded_no_scope']=='TRUE' for x in oldmat)==2

# Pattern dimensions sourced from actual public maker for Rondo and nominal handoff for Tones/Cortar.
# Two distinct orientation/cut solutions per W keyed original wall; all walls retain source provenance.
pattern={
 'PH-BATH3':('Tones Sapphire long-side horizontal 20in NOMINAL',D('20'),D('0.125'),'Tones maker caliber and individual wet WALL confirmation pending','Tones Sapphire long-side VERTICAL 2in NOMINAL',D('2'),D('0.125'),'horizontal vs vertical orientation visual sample; 2in edge refers to separate tile axis, not 20in module'),
 'TX-BATH3':('Tones Emerald long-side horizontal 20in NOMINAL',D('20'),D('0.125'),'Individual Emerald wet WALL prior evidence; maker actual tile caliber unverified','Tones Emerald long-side VERTICAL 2in NOMINAL',D('2'),D('0.125'),'vertical long dimension shifts vertical cut/grid; not a manufacturer approved exact module'),
 'PH-BATH4':('Flat Bone 24x48 long 48in NOMINAL run',D('48'),D('0.125'),'24x48 source format flat WALL; large wall cuts may require turn and edge plan','Flat Bone 24x48 SHORT 24in run',D('24'),D('0.125'),'flat tile source wall maker wet authority separate from Ribbed; 24in gives more field module repeats'),
 'PH-PRIMARY':('Flat Bone 24x48 long 48in NOMINAL run',D('48'),D('0.125'),'Primary ceiling 111in source not an exposed edge; no shower NICHE','Flat Bone 24x48 SHORT 24in run',D('24'),D('0.125'),'joint chosen nominal 1/8 only for illustrative wall cut, not approved grout for Bone')
}

def balanced(W,tile,j):
 # Choose highest integer count of FULL interior tiles with two equal side cuts > 0.
 count=math.floor((W-2*j)/(tile+j))
 while count>0 and (W-count*tile-(count+1)*j)<=0:count-=1
 cut=(W-count*tile-(count+1)*j)/2
 return count,cut
out=[]
for item in walls:
 rid=item['room'];W=D(item['source_width_in_UNVERIFIED']);H=D(item['source_tiled_height_in_UNVERIFIED'])
 base={'room':rid,'wall':item['wall'],'source_wall_W_in_1529_NOT_VERIFIED':nd(W),'source_tile_height_in_1529_NOT_VERIFIED':nd(H),'provisional_face_sf_no_openings':nd(W*H/D(144)),'actual_1529_field_confirmed':'FALSE','actual_rough_escutcheon_niche_glass_openings_deductions_sf':'','actual_approved_joint_and_tile_caliber':'','actual_movement_joint_each_change_of_plane_LF':'','actual_exposed_metal_trim_each_edge_LF':'','niche_displaced_field_plus_sill_returns_back_once':'','new_material_order_quantity_sf':'','architect_signoff':'FALSE','installer_signoff':'FALSE','procurement_release':'FALSE'}
 if rid in pattern:
  a=pattern[rid]
  for opt in range(2):
   label,tile,j,note=a[0+opt*3],a[1+opt*3],a[2+opt*3],a[3+opt*3] if opt==0 else a[5]
   # Initial tuple layout is 7 entries, customized indexing explicitly.
   if opt==0:label,tile,j,note=a[0],a[1],a[2],a[3]
   else:label,tile,j,note=a[4],a[5],a[2],a[6]
   n,cut=balanced(W,tile,j)
   sensitivity3= cut<D('3')
   x=dict(base,scenario=label,module_in_schematic=nd(tile),assumed_joint_in_schematic=nd(j,'0.0001'),nominal_fully_uninterrupted_modules=n,idealized_symmetric_terminal_piece_in=nd(cut),architect_3in_sliver_review_required='YES_NOMINAL_BELOW_3IN' if sensitivity3 else 'NO_NOMINAL_ONLY_REAL_JOINT_REQUIRED',theoretical_top_plus_two_vertical_edges_LF_UPPER_BOUND_NOT_ORDER=nd((W+2*H)/D(12)),manufacturer_and_field_uncertainty=note,actual_cut_formula='(verified W - N*actual calibrated module - (N+1)*approved grout)/2',net_cut_order_formula='(actual physical WALL face minus openings minus niche aperture once plus back/returns/sill once) + one approved NEW waste only')
   out.append(x)
 else:
  out.append(dict(base,scenario='NOT_FOCUS_WALL_OR_SHARED_WC_NA',module_in_schematic='',assumed_joint_in_schematic='',nominal_fully_uninterrupted_modules='',idealized_symmetric_terminal_piece_in='',architect_3in_sliver_review_required='N/A',theoretical_top_plus_two_vertical_edges_LF_UPPER_BOUND_NOT_ORDER='',manufacturer_and_field_uncertainty='Do not invent bath wall in WC; powder DRY W1 only; all R24 source-study wall keys preserved',actual_cut_formula='',net_cut_order_formula='actual site measured net + separately approved once-only NEW waste'))
assert len({(x['room'],x['wall']) for x in out})==25
assert len(out)>=25
put('R25_25_WALL_KEY_TWO_ORIENTATION_JOINT_SLIVER_AND_EDGE_SCENARIOS.csv',out)

# Distinguish 35-vs-27 problem without manufacturing floor measurements. 18 hypotheticals use NEW NET assumptions,
# never original 40.2 SF historical per copy gross (contains original 15% once).
ph4=[]
for owner_or_drawing_total in ['27','35']:
 for pan_fraction in ['0.20','0.35','0.50']:
  for NEW_once_waste in ['0.00','0.05','0.10']:
   level=D(owner_or_drawing_total)*(D('1')-D(pan_fraction))
   pan=D(owner_or_drawing_total)*D(pan_fraction)
   factor=D('1')+D(NEW_once_waste)
   level2=level*D('2')*factor
   pan2=pan*D('2')*factor
   levelcase=D('9.69');pancase=D('4.85')
   lc=int((level2/levelcase).to_integral_value(rounding=ROUND_CEILING))
   pc=int((pan2/pancase).to_integral_value(rounding=ROUND_CEILING))
   ph4.append(dict(room='PH-BATH4',two_physical_copies='2',input_source_area_SF_PER_COPY_NOT_SURVEYED=owner_or_drawing_total,area_input_type='OWNER_35_SF_NOT_VERIFIED' if owner_or_drawing_total=='35' else 'HISTORIC_DRAWING_27_SF_NOT_VERIFIED',hypothetical_POINT_PAN_fraction_of_assumed_total=pan_fraction,hypothetical_NEW_net_LEVEL_SF_one_copy=nd(level),hypothetical_NEW_net_POINT_PAN_SF_one_copy=nd(pan),hypothetical_once_only_NEW_offcut_waste_factor=NEW_once_waste,published_HNC6615_LEVEL_case_SF='9.69',published_HNC6715_POINT_case_SF='4.85',hypothetical_LEVEL_plus_waste_2copy_SF=nd(level2),hypothetical_PAN_plus_waste_2copy_SF=nd(pan2),illustrative_rounded_LEVEL_cases_not_orderable=lc,illustrative_rounded_PAN_cases_not_orderable=pc,illustrative_LEVEL_case_capacity_SF=nd(D(lc)*levelcase),illustrative_PAN_case_capacity_SF=nd(D(pc)*pancase),actual_SF_is_assumption='TRUE',source_historic_40p2_gross_includes_15pct_do_NOT_add_to_new_case='TRUE',current_Chicago_factory_case_lot_confirmed='FALSE',actual_1529_LEVEL_PAN_partition='',raw_individual_numeric_wet_dcof_for_both='MISSING',owner_approval='FALSE',GC_release='FALSE',procurement_release='FALSE'))
assert len(ph4)==18
put('R25_PH4_18_SCENARIO_27_VS_35_SF_POINT_PAN_LEVEL_CARTON_SENSITIVITY.csv',ph4)

# Depth/riser/actual flow/grade and rough field witness plan all 12 program-unit scenarios.
tri=[]
for r in branch:
 rid=r['room'];variant=r['owner_program_branch'];tub=variant=='TUB_CONDITIONAL'
 program='TUB_ONLY_PAN_NA' if tub else 'POINT_FOUR_PLANE' if rid in ['PH-BATH3','TX-BATH3','PH-BATH4'] else 'LINEAR_CHANNEL'
 interface=('OWNER_TUB_MODEL_AND_FACTORY_WASTE_UNSELECTED' if tub else 'Delta DT062412 2in PVC selected shower-only' if rid=='PH-BATH3' else 'Brizo BT062415-BNX 2in PVC tile-in POINT selected' if rid in ['TX-BATH3','PH-BATH4'] else 'Brizo BT0734816-BNX + BR73480 LINEAR separately required')
 tri.append(dict(room=rid,physical_unit=r['physical_unit'],program_branch=variant,assembly_type=program,selected_or_conditional_model=interface,maker_original_document='Delta 113919 Rev B' if rid=='PH-BATH3' else 'Brizo 113920 Rev C / 4in tile-in' if rid in ['TX-BATH3','PH-BATH4'] else 'Brizo BT0734816-BNX / BR73480 maker installation',true_1529_subfloor_datum_in='',actual_selected_drain_rough_FFE_in='' if not tub else 'N/A',actual_perimeter_slope_runs_L1_L2_L3_L4_in='' if not tub else 'N/A',designer_approved_each_plane_slope='' if not tub else 'N/A',design_each_edge_drop_formula='' if tub else 'approved s_i times actual L_i (no unverified numerical pitch)',proposed_pretile_mortar_or_substrate_thickness_in='',selected_exact_membrane_fabricator_section='',slope_four_plane_point_diagonal_or_linear_channel_shop='' if not tub else 'N/A',true_tile_finished_thickness_and_grout_from_lot='',approved_curb_glass_tub_flange_and_threshold_section='',specific_wall_escutcheon_and_niche_penetration_coords='',raw_individual_LEVEL_wet_numeric_lab='',raw_individual_PAN_wet_numeric_lab='' if not tub else 'N/A',owner_branch_approved='FALSE',architect_shop_approved='FALSE',plumber_rough_approved='FALSE',waterproof_installer_and_tile_approved='FALSE',GC_flood_witness_complete='FALSE' if not tub else 'N/A_NO_SHOWER_PAN',procurement_release='FALSE',next_signoff='OWNER program first for Bath3; 1529 architect field shop; specific manufacturer rough/liner approval; separate numeric wet tests and current installed quote'))
assert len(tri)==12
put('R25_12_UNIT_REAL_DATUM_DRAIN_ROUGH_AND_MEMBRANE_SECTION_WITNESS.csv',tri)

# This is strictly a research/closure request bridge, not a replacement to 27 source line financials or R24 65 RFIs.
flags={
'PH-PRIMARY':'Test actual 5/16 hex versus 7–18mm Brizo tile-in, historical 1/4 below minimum, solid grate alternative and separate BR73480, no niche',
'PH-BATH2':'Verify 59 vs 59.496in alcove only with actually measured tub-flange and field wall substrate, no shower pan',
'PH-BATH3':'Owner tub-vs-walkin and PH basin unsigned; exact Delta 2in PVC square point shower-only or separate owner-selected tub waste',
'PH-BATH4':'Cross-tab two areas 27/35 and 18 scenario case count, source vendor 214.4SF not a shortage, old Soft/AntiSlip and unlisted Ribbed/Caviar, real BNX tile-in square',
'PH-POWDER':'Actual Brizo WALL faucet relief-to-painted-flat landing, no shower or wet floor',
'PH-WC':'PH Primary LEVEL area and exact lab inherited once, no independent order',
'TX-PRIMARY':'Selected TX Black Onyx LINEAR no extra niche, no PH rough transfer; TX WC included once',
'TX-BATH2':'Actual Duravit tub Chrome and owner sink unselected, independently listed Copper/Sandstone and LEVEL lab only',
'TX-BATH3':'Owner tub or walkin unresolved, selected Black Onyx BT062415 is TILE-IN square not reversible; Emerald/Sandstone wet source, separate LEVEL/PAN',
'TX-BATH4':'Duravit tub MATTE WHITE, Soho Ivory exact niche versus Caviar wet permission and LEVEL only',
'TX-POWDER':'AXOR 48140991 vs Hansgrohe 32526141 are two incompatible TRIMS, choose one and factory matched rough; 70/30 Haze dry',
'TX-POWDER2':'Owner basin unselected, Tecturis 73072341 DECK, blank countertop drill template, dry Indigo',
'TX-WC':'TX Primary inherited LEVEL once and no independent WC order'
}
statuses=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert len(statuses)==13 and set(flags)=={x['id'] for x in statuses}
f=[]
for rm in statuses:
 rid=rm['id']
 f.append(dict(room=rid,owner_research_priority='P0' if rid in ['PH-PRIMARY','PH-BATH3','PH-BATH4','TX-BATH3'] else 'P1' if rid not in ['PH-POWDER','PH-WC','TX-WC'] else 'P2',specific_field_technical_closeout_intent=flags[rid],trade_responsible='OWNER+ARCHITECT+PLUMBER+TILE_INSTALLER+GC+ESTIMATOR' if rid in ['PH-PRIMARY','PH-BATH3','PH-BATH4','TX-BATH3'] else 'ASSIGNED_ROOM_SPECIFIC_OWNER_AND_TRADE_BY_R24',source_actual_verified_1529='FALSE',individual_wet_WALL_NICHE_current_letter='PENDING_OR_NOT_APPLICABLE',exact_raw_numeric_wet_LEVEL='MISSING_OR_INHERITED_OR_NA',exact_raw_numeric_wet_PAN='MISSING_OR_NA',real_current_supplier_Chicago_stock_case='NULL',actual_installed_current_GC_bid='NULL',owner_signed='FALSE',architect_signed='FALSE',plumber_signed='FALSE',tile_signed='FALSE',GC_signed='FALSE',purchase_released='FALSE'))
put('R25_13_ROOM_NEW_EVIDENCE_ACCEPTANCE_AND_FIELD_CLOSURE_BRIDGE.csv',f)
print('PASS R25 25 wall IDs as 25/alternate focus scenario rows',len(out),'18 PH4 owner-area + pan/waste hypothetical carton sensitivity, 12 physical branch sections, 13 room closure records; original 27 source cost rows unchanged')
