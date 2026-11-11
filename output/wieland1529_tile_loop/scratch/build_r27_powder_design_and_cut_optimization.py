"""R27 genuinely new conditional powder-room design and tile-mathematics studies.
Only creates additive outputs in new R27 folder. No original owner sources altered.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
import csv, json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/integrated-r27-powder-value-and-13room-procurement'
OUT.mkdir(parents=True,exist_ok=True)
def D(v):return Decimal(str(v))
def n(v):return str(D(v).quantize(D('0.0001'),rounding=ROUND_HALF_UP))
def write(name,data):
    path=OUT/name
    assert not path.exists(),name
    with path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n')
        wr.writeheader(); wr.writerows(data)
def cut(span,module,grout):
    """Nominal centered orientation: zero or more full modules plus two cut ends and n+1 joints."""
    span,module,grout=map(D,(span,module,grout))
    possible=[]
    for full in range(0,30):
        edge=(span-full*module-(full+1)*grout)/2
        if D('0') < edge <= module:
            possible.append((full,edge))
    candidates=[(a,b) for a,b in possible if b>=D('3')]
    if candidates:
        return max(candidates,key=lambda x:(x[0],x[1]))+('NO_NOMINAL_UNDER_3',)
    if possible:
        return max(possible,key=lambda x:(x[1],x[0]))+('CUT_UNDER_3_REDESIGN',)
    return (-1,D(0),'NO_NOMINAL_SOLUTION')

rooms={x['id']:x for x in json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
focus=['PH-POWDER','TX-POWDER','TX-POWDER2']
info={
'PH-POWDER':dict(w=D('50.688'),h=D('111'),gross=D('44.9'),cost=D('368.18'),rate=D('8.20'),selected='Brizo T65722LF-GL Luxe Gold WALL plus R65700 factory rough; RP72414GL drain',finish='ELM Vera Forma Earth Lines 2x10 Glossy Relief, DRY WALL',units='405A/405B'),
'TX-POWDER':dict(w=D('35.880'),h=D('111'),gross=D('31.8'),cost=D('379.37'),rate=D('11.93'),selected='AXOR One 48140991 WALL trim Polished Gold Optic OR hansgrohe Metropol 32526141 WALL trim Brushed Bronze; owner trim unselected, never combine',finish='ELM Haze Camel/Wheat 1.6x5 Matte, one DRY WALL, source 70:30',units='102A/102B'),
'TX-POWDER2':dict(w=D('45.672'),h=D('111'),gross=D('40.5'),cost=D('332.10'),rate=D('8.20'),selected='Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK; basin UNSELECTED',finish='ELM Vera Forma Indigo Edge 6x6 Glossy Relief DRY WALL',units='009A/009B')
}
assert all(rooms[r]['status']=='active' for r in focus)
for rid,x in info.items():assert D(rooms[rid]['carried_quote_material_subtotal_usd_per_unit'])==x['cost']

tiers={
'PH-POWDER':[
('GOOD','One complete dry Earth Lines 2x10 relief wall, selected Brizo WALL trim; keep a relief-free factory-bearing tile insert only if the actual escutcheon fully seals and rough plane matches','Earth Lines direct original room quote, 44.9 SF historic gross with 15% once; no new maker or paint line','Uninterrupted costly tile is an owner-visible textured statement but hidden escutcheon sealing risk; do NOT claim original relief can seal until real 1:1','Factory R65700 installed-depth and Brizo trim footprint; exact 9-11/16in spout reach to selected actual basin; no PH paint owner authorization'),
('BETTER','Three-field composed Earth Lines relief flanks with owner-selected full-height DRY PAINTED FLAT 12-to-16in center at Brizo trim; two actual material-to-paint transitions, centered calibrated 10in horizontal tile modules','Remove measured flat center from NEW net tile takeoff once, add painted face and actual two exposed profile LF; historic gross is comparator, not new order','Flat gasket-plane reduces reliance on relief tile, calmer symmetrical tile near selected Luxe Gold, but extra paint/edge work not free','Mock 12/16/20in center widths; 20in is nominal tile-edge cut under 3in with one full 10in module; manufacturer metal reach/body and mirror center gate'),
('BEST','Keep only owner-approved calibrated Earth Lines relief as vertical accent flanks over fully finished painted central wash-zone, allow mirror-cabinet service space and removable faucet/valve trim; exact shop joint plan across tile/pained/wood/counter','No new tile SKU, but separate takeoff of central painted area, two tile edge assemblies, countertop splash and finish return; include owner selected paint trim brand/color if later chosen','More deliberate Old Town presentation at reduced relief coverage, but 9.25-ft metal edge lines and paint labor can exceed tile-only theoretical savings','Require independent 405A/B 1:1 samples with true Brizo rough and actual chosen counter/basin reach, wood floor junction, 2 lighting settings')
],
'TX-POWDER':[
('GOOD','One Haze Camel/Wheat 70:30 Matte 1.6x5 dry wall; balanced intentional bands, not random alternating fragments; keep two different faucet trims UNSELECTED','One historical 31.8 SF gross/copy already 15%; 70/30 color area shares a single wall, not a full 31.8SF order per color','Calm matte dry-wall composition may be the lowest tile change risk but cannot be physically finished before selecting exact AXOR versus Hansgrohe WALL trim','Preserve AXOR 48140991 CROSS versus Metropol 32526141 SINGLE lever as distinct trims; new individual verified 13622181 rough matches only Metropol'),
('BETTER','Source-led Haze 70/30 bands with a true narrow finished FLAT non-relief plumbing bearing panel only if selected faucet trim footprint and metal hand-clearance demand it; keep both materials in one allocation','Quantify revised net Camel/Wheat after measured flat aperture and independent color-specific carton rounding; no new double-faced wall','Eases wall faucet service and gasket bearing while preserving warm organic muted buyer appeal; creates two painted/tile transitions and labor risk','Owner selects one manufacturer trim/finish and exact rough FIRST, architect certifies rough-plane/handle setbacks and mirror; plumber verifies 13622181 only with Metropol if that program chosen'),
('BEST','Dry Earth Lines Vera Forma 2x10 glossy relief on entire wall EXCEPT source-necessary finished flat faucet island; alternative to Haze not mixed into Haze wall, executed around owner-chosen selected-later trim','Historic PH same-product $8.20/SF may be used for REFERENCE exposure on TX original 31.8 gross (not current TX supplier quote), new island/edge/setting unknown','More sculptural relief could read premium against either warm metal but adds backsplash cleaning and faucet gasket risks; may not beat Haze after labor','Two current physical fixture assemblies remain mutually exclusive; owner authenticates exact AXOR factory rough or Metropol 13622181 and matching finish, then 1:1 relief/metal/labor mockup')
],
'TX-POWDER2':[
('GOOD','Owner-active Indigo Edge 6x6 glossy relief dry W1 centered bond; keep selected Tecturis E DECK faucet and unselected basin/uncut counter','Historic 40.5 SF gross/copy and 30pc/7.34SF-case quote only, no current Chicago lot or current case coverage verified','High-character blue glossy relief may read playful but at vanity mirror catches glare; center six nominal modules with balanced edges before final grout','Require no wall-faucet rough and no countertop drilling; center 6 tile modules and two end cuts; owner selects basin separately'),
('BETTER','One continuous Indigo dry wall with mirror framed to the tile joint axis, restrained matched grout and grounded counter edge; keep the full-height tile to avoid new finish transitions','No change to historic material SKU; shop optimization/calibrated 6in joint and exact case-yield check, old source 81SF/7.34 might straddle 12-case threshold across two units','Most defensible value engineering: eliminate unneeded flat insert/trim while improving visual grid and mirror alignment; actual installer labor not priced','Physical 3x3 Indigo sample at day/night grazing light, actual owner-selected basin before any DECK bore and drain/overflow; actual 009A/B wall and mirror measurements'),
('BEST','Single-source Earth Lines 2x10 glossy relief alternate for TX2 dry W1, with intentional lighter textural field and coordinated Black Chrome DECK faucet; basin still unselected, no wall trim landing required','Conditional reference $8.20/SF from PH Earth Lines only and not a firm TX2 purchase price; 2x10 wall re-cut may add edge/corner labor; case yield unknown','Potential material/color consistency with PH powder if owner wants cross-unit identity, but PH/TX are separate buyers so pooled order/visual uniformity not assumed','1:1 Earth Lines versus Indigo sample, deck reach and mirror/wood junction; case-level current supplier prices and owner palette signatures before choosing')
]}

out=[]
for rid in focus:
 x=info[rid];r=rooms[rid]
 for name,wall,quantity,value,physical in tiers[rid]:
  out.append(dict(room=rid,tier=name,source_champion_preserved=r['champion_id'],source_score_preserved=str(r['champion_score']),program_and_fixture=x['selected'],original_historic_material_USD_copy=str(x['cost']),original_15pct_GROSS_SF_copy=str(x['gross']),individually_maker_DRy_wall_tile=x['finish'],new_distinct_material_and_install_design=wall,source_versus_new_quantity_and_cost=quantity,Old_Town_buyer_value_and_constructability=value,manufacturer_reach_rough_or_deck_1to1_verification=physical,wood_floor_numeric_wet_LEVEL_NA='TRUE',no_tiled_shower_PAN_NA='TRUE',manufacturer_wet_wall_authorization_NA_DRy='TRUE',owner_approval='FALSE',architect_approval='FALSE',plumber_approval='FALSE',GC_approval='FALSE',procurement_release='FALSE'))
assert len(out)==9
write('R27_9_THREE_POWDER_MANUFACTURER_PHYSICAL_GOOD_BETTER_BEST.csv',out)

# PH physical paint center new-net theoretical study, not additional old gross waste.
ph=[]
W=info['PH-POWDER']['w'];H=info['PH-POWDER']['h'];gross=info['PH-POWDER']['gross']
for center in [D(0),D(12),D(16),D(20)]:
    paint=center*H/D(144)
    tile_net=(W-center)*H/D(144)
    theoretical_future_gross=tile_net*D('1.15')
    flank=(W-center)/2 if center else W
    full,edge,flag=cut(flank,10,D('0.125'))
    ph.append(dict(room='PH-POWDER',two_units='405A/405B',selected_Brizo='T65722LF-GL Luxe Gold + R65700 WALL',SOURCE_W1_width_in_NOT_MEASURED=n(W),SOURCE_height_in_NOT_MEASURED=n(H),hypothetical_owner_NOT_SELECTED_full_height_flat_center_width_in=str(center),hypothetical_one_copy_dry_paint_FACE_SF=n(paint),hypothetical_one_copy_relief_tile_FACE_NET_SF=n(tile_net),theoretical_NEW_GROSS_at_ONE_independent_15pct_allowance_SF=n(theoretical_future_gross),historical_15pct_gross_SOURCE_SF_copy=str(gross),source_gross_minus_theoretical_new_gross_SF_copy_NOT_Purchasing=n(gross-theoretical_future_gross),reference_historic_EarthLines_rate_USD_SF='8.20',reference_same_material_only_tile_exposure_delta_TWO_COPIES_USD=n((theoretical_future_gross-gross)*D('8.20')),nominal_each_relief_flank_width_in=n(flank),tile_module_horiz_in='10',illustrative_grout_joint_in='0.125',nominal_full_centered_tiles_each_flank=full,nominal_symmetric_end_cut_each_flank_in=n(edge),cut_gate=flag if center else 'FULL_WALL_LAYOUT_NO_PAINT',hypothetical_new_exposed_transition_vertical_LF_two_edges='18.50' if center else '0',actual_escutcheon_bearing_width_and_reach_in='',actual_owner_selected_paint_and_height='',real_1529_W1_or_Brizo_rough_plane='',live_exact_lot_case_yield='',supplier_offer='',installed_paint_edge_labor='',owner_signed='FALSE',GC_released='FALSE',purchase_released='FALSE'))
write('R27_PH_BRIZO_4_PAINT_RELIEF_WIDTH_TILE_EDGE_COST_SCENARIOS.csv',ph)

# TX Haze split across one wall; conservative exact area arithmetic, no double full-wall.
tx=[]
W=info['TX-POWDER']['w'];H=info['TX-POWDER']['h'];G=info['TX-POWDER']['gross']
for camel in [D('0.70'),D('0.60'),D('0.80')]:
    wheat=D(1)-camel
    span_c=W*camel;span_w=W*wheat
    nc,ec,fc=cut(span_c,D(5),D('0.125'))
    nw,ew,fw=cut(span_w,D(5),D('0.125'))
    tx.append(dict(room='TX-POWDER',two_units='102A/102B',SOURCE_W1_width_in_UNVERIFIED=n(W),nominal_height_in_UNVERIFIED=n(H),conditional_area_share_Camel=n(camel),conditional_area_share_Wheat=n(wheat),Camel_band_width_in=n(span_c),Wheat_band_width_in=n(span_w),one_wall_historic_GROSS_15pct_SF_copy=str(G),illustrative_original_Camel_SHARE_GROSS_SF_copy=n(G*camel),illustrative_original_Wheat_SHARE_GROSS_SF_copy=n(G*wheat),sum_one_wall_gross_SF_copy=str(G),tile_long_axis_nominal_in='5',joint_illustrative_in='0.125',Camel_centered_full_modules=nc,Camel_end_cut_each_in=n(ec),Camel_cut_risk=fc,Wheat_centered_full_modules=nw,Wheat_end_cut_each_in=n(ew),Wheat_cut_risk=fw,AXOR_48140991_trim_or_Metropol_32526141_trim_owner_unselected='TRUE',manufacturer_13622181_matches_only_Metropol='TRUE',current_color_specific_case_size='',current_color_specific_rate='',actual_1529_wall_and_recess='',selected_rough_and_escutcheon='',owner_signed='FALSE',purchase_released='FALSE'))
write('R27_TX_HAZE_3_SINGLE_WALL_COLOR_ALLOCATION_AND_CUT_STUDIES.csv',tx)

# Indigo carton boundary and full 6-in field corrected joint arithmetic.
ind=[]
W=info['TX-POWDER2']['w'];H=info['TX-POWDER2']['h'];gross=info['TX-POWDER2']['gross']
full,edge,gate=cut(W,D(6),D('0.125'))
vertical_full,vertical_edge,vertical_gate=cut(H,D(6),D('0.125'))
for new_gross_two in [D('81'),D('80.74'),D('80'),D('78')]:
    box=D('7.34')
    c=int((new_gross_two/box).to_integral_value(rounding=ROUND_CEILING))
    ind.append(dict(room='TX-POWDER2',two_units='009A/009B',SOURCE_W1_width_in_UNVERIFIED=n(W),SOURCE_height_in_UNVERIFIED=n(H),tile_nominal='ELM Vera Forma Indigo Edge 6x6 8.6mm dry WALL only',selected_Tecturis_73072341_DECK_basin_unselected='TRUE',nominal_horizontal_full_6in_modules=full,nominal_horiz_symmetric_end_cut_in=n(edge),nominal_vertical_full_6in_modules=vertical_full,nominal_vertical_top_bottom_cut_in=n(vertical_edge),illustrative_joint_in='0.125',historic_2copies_original_GROSS_SF_including_15pct_ONCE='81',hypothetical_two_copy_new_GROSS_SF_not_measured=n(new_gross_two),historic_source_case_yield_7p34_SF_dated_ONLY=str(box),hypothetical_mathematically_rounded_cases_IF_7p34_same_lot=c,theoretical_case_SF=c*float(box),historical_box_30pcs_yield_vs_nominal_6x6_discrepancy='30 nominal 6in tiles = 7.5 SF; source quote 7.34 SF; DO NOT override source',actual_2026_lot_or_carton_verified='FALSE',physically_shared_two_unit_order_approved='FALSE',owner_selected_basin_or_deck_holes='FALSE',supplier_offer='',GC_release='FALSE',purchase_release='FALSE'))
write('R27_TX2_INDIGO_4_HISTORIC_CARTON_THRESHOLD_SENSITIVITIES.csv',ind)

print('PASS R27: 9 distinct powder tier directions, 4 Brizo flat-center quantity/cut/paint sensitivities, 3 Haze single-wall color-bond studies, 4 Indigo case thresholds, no selections')
