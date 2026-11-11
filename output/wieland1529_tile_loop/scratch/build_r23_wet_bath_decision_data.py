"""Build ADDITIVE R23 numeric / source / shop schedules only, preserving originals."""
from pathlib import Path
import json, csv, hashlib, math
from decimal import Decimal

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc'
O.mkdir(parents=True,exist_ok=True)
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
names=[x['id'] for x in rooms]
assert len(names)==len(set(names))==13
focus=['PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY']

def load_csv(p):
 with (R/p).open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def put_csv(name,rows,fields):
 p=O/name
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)

source=load_csv('deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
walls=load_csv('deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv')
gates=load_csv('deliverables/integrated-r17/R17_13_ROOM_WET_LAB_AND_PROGRAM_MATRIX.csv')
assert len(source)==27 and len(walls)==25 and len(gates)==13
historic=Decimal('0');excluded=0
for s in source:
 if s['historic_usd_one_copy']:
  historic+=Decimal(s['historic_usd_one_copy'])*2
 else:
  assert s['historic_niche_excluded_no_scope']=='TRUE' and s['source_surface']=='accent'
  excluded+=1
assert excluded==2 and historic==Decimal('23572.44'),(excluded,historic)

room_config={
 'PH-PRIMARY':('48-in LINEAR','selected BT0734816-BNX/BR73480, Black Onyx, separate Duravit tub, no niche','RL21 12x24 LEVEL and independently RL21 1.5-in hex LINEAR PAN; source Bone Soft/AntiSlip remains untested','flat ELM Cortar Bone Soft wet WALL individually listed, original Bone Reed wet wall unlisted','N/A, no added Primary niche','R13_PH_RL21_MULTI_FORMAT_LEVEL_LINEAR_POINT_SOURCE_EVIDENCE.md'),
 'PH-BATH2':('DURAVIT TUB / NO PAN','Duravit, Hansgrohe Matte White','Cortar Grey Soft original or HNC6615 independent LEVEL study, exact raw unknown','ELM Tones Sapphire 2x20 Wet Areas PASS','ELM Tones Sandstone wet niche PASS','R13_PH_SOURCE_PRESERVING_INSTALLATION_ALTERNATIVES_20261106.md'),
 'PH-BATH3':('TUB? OR POINT WALK-IN?','owner program unselected; selected Delta DT062412 Chrome 4in shower POINT only if WALK-IN; Hansgrohe Chrome; basin unselected','historical Cortar Bone Soft LEVEL or RL21 12x24 LEVEL conditional; RL21 1.5-in hex POINT PAN if WALK-IN only','ELM Tones Opal wet wall not established; individually listed Sapphire wet wall possible, not approved','Tones Sandstone 2x20 individually wet-listed niche','R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md'),
 'PH-BATH4':('4-in SQUARE POINT WALK-IN','selected Brizo BT062415-BNX Black Onyx 4in SQUARE shower drain, no tub or linear','historical Charcoal Soft/AntiSlip conflicting LEVEL source; HNC6615 or RL21 12x24 LEVEL conditional, HNC6715 or RL21 1.5in hex POINT PAN conditional, tests separate','historical full Bone Ribbed 107.2 SF/copy wet unlisted, flat Bone Soft individually wet-listed conditional','historic Clara Caviar wet absent; Soho Black 2x10 individually wet-listed conditional','R13_PH_SOURCE_PRESERVING_INSTALLATION_ALTERNATIVES_20261106.md'),
 'PH-POWDER':('DRY WOOD','Brizo T65722LF-GL wall/R65700, relief landing unresolved','WOOD no tiled LEVEL/PAN','Earth Lines DRY wall','N/A','R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md'),
 'PH-WC':('SHARED PH PRIMARY LEVEL','no independent tile order','inherited PH Primary LEVEL once','N/A','N/A','R13_PH_RL21_MULTI_FORMAT_LEVEL_LINEAR_POINT_SOURCE_EVIDENCE.md'),
 'TX-PRIMARY':('48-in LINEAR','selected Brizo Black Onyx 48in linear; NO additional niche','Cortar Clay Soft LEVEL source; Emser LEVEL study; separate Prime RL21 linear PAN; each raw lab absent','historic Clay Ribbed wet wall not listed; conditional flat Clay wet-listed','N/A, no added Primary niche','R13_PH_RL21_MULTI_FORMAT_LEVEL_LINEAR_POINT_SOURCE_EVIDENCE.md'),
 'TX-BATH2':('DURAVIT TUB / NO PAN','Duravit tub, Hansgrohe Chrome, basin unselected','Cortar Clay Soft vs independent EL30 LEVEL; exact raw absent','Copper Tones wet wall manufacturer-specific proof pending','Sandstone niche maker wet PASS; verify actual purchased SKU','R15_TX_TUB_PAIR_EL30_KC04_INDIVIDUAL_MAKER_WET_APPLICATION_20261106.md'),
 'TX-BATH3':('TUB? OR POINT WALK-IN?','owner program unselected; Brizo BT062415-BNX Black Onyx square POINT shower drain only if WALK-IN; Roccesco','Cortar Grey Soft LEVEL source or RL21 12x24 conditional; RL21 hex POINT PAN if WALK-IN only','Tones Emerald individually wet-listed WALL PASS','Tones Sandstone individually wet-listed NICHE PASS','R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md'),
 'TX-BATH4':('DURAVIT TUB / NO PAN','Duravit tub, Hansgrohe Matte White','Cortar Bone Soft vs Emser KC04 LEVEL conditional exact raw absent','Cortar Charcoal flat wet WALL individually listed conditional, relief not transferable','Clara Caviar niche wet absent; Soho Ivory wet niche individually listed conditional','R15_TX_TUB_PAIR_EL30_KC04_INDIVIDUAL_MAKER_WET_APPLICATION_20261106.md'),
 'TX-POWDER':('DRY WOOD','AXOR 48140991 vs Hansgrohe 32526141 two different wall TRIMS, latter NOT rough, owner program unselected','WOOD no tiled LEVEL/PAN','Haze Camel/Wheat dry wall 70:30 owner-unsig.','N/A','R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md'),
 'TX-POWDER2':('DRY WOOD','Hansgrohe Tecturis E 73072341 DECK, basin unselected','WOOD no tiled LEVEL/PAN','Indigo Edge/Earth Lines dry wall, not wet','N/A','R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md'),
 'TX-WC':('SHARED TX PRIMARY LEVEL','no independent tile order','inherited TX Primary LEVEL once','N/A','N/A','R13_PH_RL21_MULTI_FORMAT_LEVEL_LINEAR_POINT_SOURCE_EVIDENCE.md'),
}
assert set(room_config)==set(names)

wet=[]
for x in rooms:
 room=x['id']; condition,plumbing,floors,wall,niche,ref=room_config[room]
 orig=next(z for z in gates if z['room']==room)
 labkind='N/A' if 'DRY' in condition else ('PARENT LEVEL ONLY' if 'SHARED' in condition else 'EXACT RAW SKU wet LEVEL required')
 pankind='N/A' if 'DRY' in condition or 'TUB / NO PAN' in condition or 'SHARED' in condition else ('CONDITIONAL only after OWNER WALK-IN' if '?' in condition else 'SEPARATE EXACT RAW PAN required')
 wet.append(dict(room=room,current_status=x['status'],current_champion=x['champion_id'] or '',current_score=x['champion_score'] if x['champion_score'] is not None else '',program=condition,selected_fixture_holds=plumbing,conditional_exact_products=floors,wall_specific_maker_permission=wall,niche_specific_maker_permission=niche,LEVEL_test_applicability=labkind,exact_raw_numeric_LEVEL_DCOF='',LEVEL_test_report_sample_method_date='',PAN_test_applicability=pankind,exact_raw_numeric_LINEAR_or_POINT_PAN_DCOF='',PAN_test_report_sample_method_date='',real_1529_model_approved='FALSE',owner_signed='FALSE',architect_signed='FALSE',GC_signed='FALSE',purchase_release='FALSE',source_link='../../research/products/'+ref))
put_csv('R23_13_ROOM_SKU_WET_WALL_NICHE_LEVEL_PAN_RELEASE_MATRIX.csv',wet,list(wet[0]))

studies=[]
for w in walls:
 room=w['room']; wall=w['wall']; width=Decimal(w['source_width_in_UNVERIFIED']); height=Decimal(w['source_tiled_height_in_UNVERIFIED'])
 assert wall in ['W1','W2','W3']
 nominal=(width*height/Decimal('144')).quantize(Decimal('.0001'))
 studies.append(dict(room=room,wall=wall,source_width_in_UNVERIFIED=str(width),source_tiled_height_in_UNVERIFIED=str(height),preliminary_full_plane_gross_sf_UNVERIFIED=str(nominal),prior_source_centered_cut_study=w['historical_balanced_cut_not_release'],physical_owner_program=room_config[room][0],actual_1529_face_width_in='',actual_1529_tile_height_in='',actual_valve_escutcheon_wet_penetrations='',actual_shower_glass_and_curb='',actual_opening_and_fixture_unfinished_sf='',actual_niche_aperture_displaced_field_sf='',actual_niche_back_sf='',actual_niche_returns_sf='',actual_niche_sill_sf='',new_measured_NET_tile_sf='',net_formula='measured full tile face - measured door/window openings - niche aperture ONCE + niche back/returns/sill ONCE only where those faces are separately tiled; avoid overlap',actual_tile_caliper_grout_joint_in='',centered_cut_inches_formula='(actual_face_width_in - N*calibrated_tile_width_in - (N+1)*approved_joint_in)/2; review minimum focal cuts >=3in where feasible',actual_balanced_side_cuts_in='',edge_termination_LF='',movement_joint_and_change_plane_LF='',movement_and_trim_takeoff='sum independently measured exposed edge/termination lengths after openings; separate change-of-plane/movement joints; no shared edge duplicate',floor_to_shower_pan_transition_and_membrane_detail='',real_1529_room_witness_photo='',architect_approval='FALSE',GC_installer_approval='FALSE',purchase_release='FALSE'))
assert len(studies)==25
put_csv('R23_25_W1_W3_PROVISIONAL_ELEVATIONS_NET_TRIM_MOVEMENT_CUT_SHOP.csv',studies,list(studies[0]))

trace=[]
for s in source:
 row={k:s[k] for k in ['room','source_row_id','source_surface','source_gross_sf_one_copy_waste_15pct_once','historic_usd_one_copy','historic_usd_two_copies','historic_niche_excluded_no_scope']}
 row.update(historic_cost_class='DATED 2026-09-03 TILE MATERIAL ONLY (NOT CURRENT BID)',source_15pct_waste_already_once='TRUE',historic_material_scope='NO ORDER excluded unpriced Primary niche' if s['historic_niche_excluded_no_scope']=='TRUE' else 'SOURCE COMPARATOR ONLY, NOT ORDER',proposed_exact_SKU_and_maker_finish='',maker_raw_numeric_wet_LEVEL_test='',maker_raw_numeric_wet_PAN_test='',separate_measured_level_NET_sf='',separate_measured_pan_NET_sf='',wall_net_after_displaced_niche_and_returns='',one_time_new_waste_after_verified_NET='',actual_supplier_carton_sf_by_exact_SKU='',whole_current_cartons='',current_supplier_dated_Chicago_offer='',public_retail_dated_indication='',manufacturer_MSRP='',freight_tax_setting_and_installed_GC_bid='',owner_room_budget_cap='',owner_signed='FALSE',architect_signed='FALSE',GC_signed='FALSE',procurement_release='FALSE',source_trace='../../deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
 trace.append(row)
assert len(trace)==27
put_csv('R23_27_HISTORICAL_ROWS_TO_NET_CARTON_COST_PROVENANCE_CONTROL.csv',trace,list(trace[0]))

focus_rows=[]
for room in focus:
 geometry=json.loads((R/'rooms'/room/'geometry.json').read_text(encoding='utf-8'))
 for unit in geometry['revit_room_numbers']:
  base=dict(room=room,unit=unit,conditional_program=room_config[room][0],actual_floor_run_in='',actual_fully_measured_LEVEL_net_sf='',actual_shower_PAN_net_sf='',exact_maker_individual_LEVEL_raw_wet_lab='',exact_maker_individual_PAN_raw_wet_lab='',approved_wall_and_niche_maker_use='',actual_wall_and_cut_field_photos='',selected_fixture_actual_rough_photos='',approved_faucet_and_drain_waterproof_assembly_section='',actual_membrane_and_drain_flange_interface='',approved_slope_and_four_plane_fall='',glass_and_curb_or_tub_flange_seal='',penetration_and_movements_approved='',grout_trim_niche_deduction_and_edges='',factory_carton_lot_and_case_yield='',dated_Chicago_material_and_installed_GC_bid='',owner_program_signed='FALSE',architect_shop_signed='FALSE',plumber_wet_rough_signed='FALSE',tile_installer_mockup_signed='FALSE',GC_inspection_signed='FALSE',purchaser_authorized='FALSE',purchase_release='FALSE')
  focus_rows.append(base)
assert len(focus_rows)==8
put_csv('R23_8_WET_UNIT_INSTANCE_OWNER_TRADE_WITNESS_CHECKPOINTS.csv',focus_rows,list(focus_rows[0]))

approval=[]
categories=[('owner_selection','Owner signs program/finish/cost cap without implicit source change'),('maker_lab','Architect verifies individual exact raw LEVEL/PAN lab, wall/niche permission'),('field_geometry','Architect and GC verify native 1529 room W1-W3, openings, floor/pan net'),('waterproofing_shop','Plumber and tile installer sign exact drain/rough/membrane/tub flange and flood witness'),('pricing_and_release','Estimator validates current Chicago offers, case yield, freight and installed GC bid; purchaser separately authorizes')]
for room in names:
 for cat,req in categories:
  approval.append(dict(room=room,workstream=cat,trade_owner=('Owner' if cat=='owner_selection' else 'Architect/GC' if cat=='field_geometry' else 'Architect/Manufacturer' if cat=='maker_lab' else 'Plumber/Tile installer/GC' if cat=='waterproofing_shop' else 'Estimator/Purchaser'),specific_action=req+'; apply '+room_config[room][0]+' program and room identity; no transfer from other room',source_reference='../../state/ROOMS.json and ../../deliverables/integrated-r17/R17_65_TRADE_CLOSURE_EVIDENCE_REQUESTS.csv',field_document_request='',actual_signature='',approved='FALSE',procurement_release='FALSE'))
assert len(approval)==65
put_csv('R23_65_ROOM_TRADE_ACTIONS_REVIEW_BRIDGE_NEW_COPY.csv',approval,list(approval[0]))

subtotal_by_room={x['id']:Decimal(str(x['carried_quote_material_subtotal_usd_per_unit'])) for x in rooms}
assert sum(subtotal_by_room.values())*2==historic
print('PASS R23 generated 13 maker/level/pan records, 25 provisional W elevations, 27 historical rows, 8 wet unit witnesses, 65 new trade actions')
print('HISTORIC',historic,'EXCLUDED',excluded,'FOCUS_2COPY_USD',sum(subtotal_by_room[x] for x in focus)*2)
