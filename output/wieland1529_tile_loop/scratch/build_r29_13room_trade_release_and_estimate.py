"""Substantive R29 cross-room receiving, exact trade release and cost normalization."""
from pathlib import Path
import csv,json
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r29-sandstone-niche-shared-cutstock'
def rd(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wr(n,rows):
 p=O/n;assert rows and not p.exists(),p
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
orig=rd(R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
by={r['id']:r for r in rooms}
assert len(orig)==27 and len(by)==13
eligible={'PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3'}
focus_areas={
 'PH-BATH2':('Tones Sapphire wet WALL; Sandstone individual wet NICHE; Cortar Grey Soft LEVEL','Duravit 59in TUB/Hansgrohe Matte White; PAN N/A','PH2 tub alcove source 59.496in versus nominal 59in; spout/valve flange and full waterproof section'),
 'PH-BATH3':('Tones Opal wet WALL FAIL; conditional Sapphire individual wet WALL PASS; Sandstone wet NICHE; Bone Soft LEVEL','Owner TUB versus WALK-IN UNSELECTED; Hansgrohe Chrome/Delta DT062412 square POINT shower only if WALK-IN; basin unselected','New selected tub waste/overflow only if owner TUB, independent 4-plane POINT PAN if WALK-IN; no Opal wet installation'),
 'TX-BATH2':('Tones Copper individual wet WALL; Sandstone wet NICHE; Cortar Clay Soft LEVEL','Duravit 59in TUB/Hansgrohe Chrome; PAN N/A; basin unselected','TX2 original 62.484in W1 vs nominal tub 59in: field-check end support, tub flange and actual waterproof returns'),
 'TX-BATH3':('Historic individual Emerald wet WALL (fresh page unverified); Sandstone individual wet NICHE; Grey Soft LEVEL','Owner TUB versus WALK-IN UNSELECTED; Brizo Black Onyx BT062415-BNX square POINT shower only if WALK-IN','Reconfirm Emerald individual wet listing and 4-plane small POINT PAN if owner WALK-IN; no PH basin confusion')
}
others={
 'PH-PRIMARY':('Cortar Bone Soft LEVEL/AntiSlip mixed original quote; Reed relief must not inherit flat wet use; NO extra NICHE','Brizo BT0734816-BNX 48in LINEAR Black Onyx + separate BR73480; Duravit tub; WC included once','R28 owner Bone WC AntiSlip vs parent Soft, verify selected LEVEL raw lab, separate LINEAR PAN raw lab and RL21 thickness 1/4 vs 5/16; no WC double count'),
 'PH-BATH4':('Cortar Bone Ribbed original wet WALL unlisted; Clara Caviar NICHE unlisted; alternate flat Bone/Soho only if approved','Confirmed WALK-IN Brizo BT062415-BNX Black Onyx 4in square POINT; separate LEVEL and four-plane PAN','Resolve 35 vs 27 SF, Soft/AntiSlip, vendor 214.4SF historical total with no payable shortage, individual maker wet WALL/NICHE and raw LEVEL/PAN lab'),
 'PH-POWDER':('Vera Forma Earth Lines 2x10 glossy RELIEF dry vanity WALL; WOOD floor, wet WALL/NICHE/LEVEL/PAN N/A','Brizo T65722LF-GL Luxe Gold WALL + separate R65700','R27 owner planar paint/relief escutcheon landing, selected rough and 1:1 0/12/16/20in owner decision; no tile wet lab on wood'),
 'PH-WC':('Cortar Bone 24x48 AntiSlip v4 LEVEL, no tiled WALL/NICHE/PAN; within parent historic mixed floor once','Original TOTO Nexus MS642124CEFG#01 Cotton listed in PH Primary, WC physical attribution unverified','R28 15SF/copy inherited, as-built flange, UniFit 12 vs optional14, factory 0GU186-A template, parent Soft vs WC AntiSlip door'),
 'TX-PRIMARY':('Cortar Clay Soft LEVEL/AntiSlip PAN original mixed quote; Ribbed relief does not inherit flat approval; NO extra NICHE','Brizo BT0734816-BNX 48in LINEAR Black Onyx + separate BR73480; WC included once','R28 Clay WC AntiSlip vs parent Soft, verified exact LEVEL and LINEAR PAN labs, 203A unplaced, no WC double count'),
 'TX-BATH4':('Cortar Charcoal flat wet WALL; Clara Caviar NICHE wet unlisted, conditional Soho Ivory wet-listed; Bone Soft LEVEL','Actual Duravit 59in tub/Hansgrohe Matte White, NO tiled PAN','Check tub spout selected pressure-balance-only against 15758701 thermostatic and 60in source W1 vs 59in tub; Caviar never wet NICHE reserved'),
 'TX-POWDER':('Vera Forma Haze Camel/Wheat 70:30 DRY WALL, WOOD floor, wet WALL/NICHE/LEVEL/PAN N/A','AXOR One 48140991 WALL CROSS trim vs Metropol 32526141 single trim unresolved, 13622181 factory rough only if Metropol chosen','R27 owner selection between incompatible programs and actual wall bearing/rough; do not call 32526141 a rough'),
 'TX-POWDER2':('Vera Forma Indigo 6x6 DRY WALL; WOOD floor, wet WALL/NICHE/LEVEL/PAN N/A','Hansgrohe Tecturis E 73072341 DECK Brushed Black Chrome; basin unselected','R27 factory deck/basin/drilling hold and 30pcs/7.34SF old carton discrepancy, no wet-floor lab'),
 'TX-WC':('Cortar Clay 24x48 AntiSlip v4 LEVEL; no tiled WALL/NICHE/PAN; parent floor once','Original Nexus MS642124CEFG#01 Cotton in TX Primary source, WC installed location unverified','R28 TX203A unplaced, 14SF/copy parent floor inherited, UniFit factory template and Clay Soft-to-AntiSlip door')
}
assert set(focus_areas)|set(others)==set(by)
stage=[
 ('OWNER','Owner chooses only available program, tub/walk-in and basin where unselected, wall color, niche number and owner upgrade cap; all unselected remain NULL'),
 ('ARCHITECT','Identify verified 1529 model/site room, W1/W3 wall/fixture/door face, floor and niche dimensions, deducted openings, owner-selected finish schedule and shop tolerances'),
 ('PLUMBER','Lock original fixture trim/rough compatibility, valve/handshower/point/linear drain or selected tub waste, confirm valve center, penetrations and niche clash'),
 ('WATERPROOF','One complete manufacturer-compatible membrane/substrate and original selected drain/tub flange, full niche corners/sill slope/flood where applicable; dry rooms N/A'),
 ('TILE','Individual factory exact SKU/finish/color/caliper and wet WALL versus NICHE list, raw exact numerical LEVEL and separately POINT/LINEAR PAN lab, module cuts/edge trims/grout/movement, 1:1 sample'),
 ('SUPPLIER','Dated Chicago written SKU-by-color lot/case usable yield, stock/ETA freight/tax/returns/attic stock, split allocated eight niche receivers and separately 27 original material rows'),
 ('GC','Full install unit price and physical 1529 net takeoff approval, compare historical quote and actual installed bid, labor/waterproof/membrane/cases/waste, release only after prior signatures'),
 ('PURCHASER','Confirm signed owner/architect/plumber/waterproof/tile/GC and actual supplier allocation; issue zero transactions until all independent approvals')
]
releases=[]
for row in rooms:
 rid=row['id'];mat,fix,gate=focus_areas.get(rid,others.get(rid))
 nid=next((q for q in orig if q['room']==rid and q['source_surface']=='accent'),None)
 releases.append(dict(room=rid,source_status=row['status'],source_champion=row['champion_id'] or '',source_score='' if row['champion_score'] is None else str(row['champion_score']),
  original_tile_material_per_copy_USD=str(row['carried_quote_material_subtotal_usd_per_unit']),
  source_selected_manufacturer_WALL_LEVEL_NICHE_and_application=mat,fixture_selected_finish_rough_and_owner_program=fix,
  most_consequential_1529_trade_field_shop_or_owner_decision=gate,
  R29_Sandstone_same_lot_receiving_candidate='TRUE' if rid in eligible else 'FALSE',
  current_exact_Sandstone_wet_NICHE_individual_maker='PASS' if rid in eligible else 'NOT_APPLICABLE_OR_DIFFERENT_MATERIAL',
  WALL_wet_manufacturer_permission='Opal FAIL' if rid=='PH-BATH3' else ('Emerald historical PASS, current refresh needed' if rid=='TX-BATH3' else ('N/A dry or inherited' if 'POWDER' in rid or rid.endswith('WC') else 'Individual maker evidence must be verified')),
  independent_level_RAW_measured_numeric_original_maker_test='N/A wood floor' if 'POWDER' in rid else 'REQUIRED_IF_EXACT_CHOSEN_LEVEL_TILE',
  independent_pan_RAW_measured_numeric_original_maker_test='N/A no tiled shower PAN' if ('POWDER' in rid or rid.endswith('WC') or rid in ('PH-BATH2','TX-BATH2','TX-BATH4')) else 'REQUIRED_IF_SELECTED_POINT_OR_LINEAR_SHOWER_PAN',
  verified_native_1529_geometry='',actual_approved_NET_faces_SF='',actual_deducted_one_niche_field_OPENING_SF='',separate_niche_back_return_sill_NET_SF='',
  owner_wet_program_and_finish_signed='FALSE',architect_1529_shop_signed='FALSE',plumber_rough_niche_clash_signed='FALSE',waterproof_tub_or_shower_niche_section_signed='FALSE',tile_installer_maker_lab_cut_mockup_signed='FALSE',supplier_chicago_offer_and_same_shade_lot_signed='FALSE',GC_installed_bid_signed='FALSE',material_reservation_release='FALSE',purchaser_order_authorized='FALSE'))
assert len(releases)==13
wr('R29_13_ROOM_CONDITIONAL_SOURCE_MAKER_TRADE_AND_PURCHASE_RELEASE.csv',releases)

actions=[]
for r in releases:
 for index,(name,task) in enumerate(stage,1):
  if r['room'] in eligible:
   extra='R29: source Sandstone niche, exact full back/two side/top/sill shop, original displaced WALL once, per-unit actual receiver assignment, lot and cost; owner conditional Bath3 program'
  elif r['room'] in ('PH-PRIMARY','TX-PRIMARY','PH-WC','TX-WC'):
   extra='R28 unchanged: inherited WC parent LEVEL once; no added WC order or shower niches; original Brizo 48in LINEAR plus rough only in Primary wet PAN'
  elif 'POWDER' in r['room']:
   extra='R27 unchanged: DRY vanity wall and WOOD floor; N/A wet niche/pan lab; actual original faucet/basin compatibility'
  else:
   extra='Original program: specific maker wet WALL/NICHE and original numeric LEVEL/PAN where applicable; no unselected owner or fixture change'
  actions.append(dict(room=r['room'],sequence=index,trade=name,trade_specific_source_evidence_required=task+'; '+extra,
    evidence_doc_revision='',physical_1529_field_or_factory_sample_verified='FALSE',
    completion_date='',same_SKU_color_finish_factory_lot_verified='FALSE',owner_direct_approval='FALSE',
    release_authorized='FALSE',purchase_authorized='FALSE'))
assert len(actions)==104
wr('R29_104_13ROOM_EIGHT_TRADE_SEQUENTIAL_SHOP_AND_OWNER_GATES.csv',actions)

# Quote normalization makes no unproved price changes.
summary=[]
for row in rooms:
 rid=row['id'];src=[q for q in orig if q['room']==rid]
 v=sum(Decimal(q['historic_usd_two_copies'] or '0') for q in src)
 assert v==Decimal(str(row['carried_quote_material_subtotal_usd_per_unit']))*2
 summary.append(dict(room=rid,unit_copies=2,source_historic_material_ONLY_USD_two_copies=str(v),
 original_quote_15pct_once='TRUE',source_quoted_SF_original_GROSS_two_copies=str(sum(Decimal(q['source_gross_sf_one_copy_waste_15pct_once']) for q in src)*2),
 niche_reference_NO_ORDER_count=sum(q['historic_niche_excluded_no_scope']=='TRUE' for q in src),
 source_room_wc_tile_material_double_count='FALSE',
 actual_correct_1529_NET_qty_SF='',actual_identical_orderable_factory_SKU_color_finish='',actual_lot_shade_caliber='',supplier_actual_carton_usable_SF='',supplier_actual_current_Chicago_allocation_cases='',supplier_2026_unit_price_USD='',supplier_freight_tax_discount_USD='',
 only_original_MSRP_if_applicable='',only_public_retail_indication='',new_owner_approved_setting_waterproof_trim_grout_labor_bid_USD='',supplier_total_verified_offer_USD='',scope_normalized_difference_vs_historic_USD='',
 original_quote_not_current_offer='TRUE',provisional_8unit_Sandstone_offset_cost_verified='FALSE',all_actual_claimed_savings_USD='',owner_approved='FALSE',GC_release='FALSE',purchaser_authorized='FALSE'))
assert sum(Decimal(x['source_historic_material_ONLY_USD_two_copies']) for x in summary)==Decimal('23572.44')
wr('R29_13_ROOM_TWO_COPY_HISTORIC_COST_VS_ACTUAL_2026_BID_NORMALIZATION.csv',summary)

# Each focus room: 3 design options paired with source gross, actual rough and shop.
units=[]
focus=['PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3']
for rid in focus:
 for unit in by[rid]['revit_room_numbers']:
  units.append(dict(room=rid,source_room_number=unit,
   original_niche_historic_SF_with_15pct_per_copy=next(q for q in orig if q['room']==rid and q['source_surface']=='accent')['source_gross_sf_one_copy_waste_15pct_once'],
   original_selected_fixture=focus_areas[rid][1],original_W1_provisional_width_in=str(next(q for q in rd(R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv') if q['room']==rid and q['wall']=='W1')['source_width_in_UNVERIFIED']),
   real_niche_location_number_width_height_depth='',real_window_valve_openings_and_wall_face='',actual_NICHE_back_side_top_sill_SF='',actual_displaced_one_field_face_SF='',actual_waterproof_niche_sill_preformed_or_maker_shop='',actual_2x20_color_calibrated_joint_and_cut_stock='',actual_shower_drain_or_tub_waste_signed='',
   request_1to1_panel='Actual full-height W1/W3 wet-wall field at point of niche; original wall color and Sandstone 2x20 8.5mm nominal with exact factory caliber/joint and four corners, sill pitch and waterproof membrane continuity',
   request_camera_1='Correct verified 1529 3D entry-to-tub/shower context, selected original fixture metal, no invented photo geometry',
   request_camera_2='Orthographic dimensioned actual W1/W3 wet-wall elevation including only real niche location, windows/valve/one deducted aperture, cuts and edge/movement line',
   request_camera_3='One-to-one niche four return water-control section and selected tub flange/conditional point drain, not a generated render',
   original_maker_NICHE_wet_list='PASS_SANDSTONE_CURRENT_INDIVIDUAL',original_maker_WALL_wet_status=focus_areas[rid][0],
   physical_panel_produced='FALSE',camera_views_produced='FALSE',manufacturer_factory_lot_verified='FALSE',individual_wet_LEVEL_or_PAN_lab_received='FALSE',owner_signed='FALSE',architect_signed='FALSE',GC_signed='FALSE',purchasing_release='FALSE'))
assert len(units)==8
wr('R29_8_PHYSICAL_ROOM_W1W3_NICHE_SILL_TRIM_SAMPLE_AND_CAMERAS.csv',units)
print('PASS R29 13 room release, 104 per-trade sequence, 13 historic-to-current quote normalization and 8 physically distinct niche shop/camera witness requests')
