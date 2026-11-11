"""R28 additive WC/Primary floor engineering: synthetic geometry never certified as site data."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
import json,csv

R=Path(__file__).resolve().parents[1]
OUT=R/'deliverables/integrated-r28-wc-primary-floor-flange-threshold'
OUT.mkdir(parents=True,exist_ok=True)
def D(v):return Decimal(str(v))
def n(v):return str(D(v).quantize(D('0.0001'),rounding=ROUND_HALF_UP))
def write(name,rows):
    p=OUT/name
    assert rows and not p.exists(),name
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)
def ce(v):return int(D(v).to_integral_value(rounding=ROUND_CEILING))
ROOMS={q['id']:q for q in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
wc={
 'PH-WC':dict(parent='PH-PRIMARY',color='Bone',code='FT1',area=D('15'),copies=['313A','313B'],parents=['304A','304B'],primary_floor_gross=D('135.6'),rate=D('7.82'),original_floor_USD_copy=D('1060.39'),rectangles=[(30,72),(36,60),(40,54)]),
 'TX-WC':dict(parent='TX-PRIMARY',color='Clay',code='FT2',area=D('14'),copies=['203A','203B'],parents=['202A','202B'],primary_floor_gross=D('116.1'),rate=D('7.80'),original_floor_USD_copy=D('905.58'),rectangles=[(28,72),(36,56),(42,48)])
}
for wid,i in wc.items():
    assert ROOMS[wid]['status']=='seeded' and not ROOMS[wid]['carried_tile_rows']
    parent_floor=next(x for x in ROOMS[i['parent']]['carried_tile_rows'] if x['surface']=='floor')
    assert D(parent_floor['qty_sf_per_unit'])==i['primary_floor_gross']
    assert D(parent_floor['quoted_rate_usd_per_sf'])==i['rate']
    assert D(parent_floor['extended_quote_cost_usd_per_unit'])==i['original_floor_USD_copy']
    assert all(D(a*b)==i['area']*144 for a,b in i['rectangles'])

def centered(span,module,j):
    span,module,j=map(D,(span,module,j))
    valid=[]
    for full in range(20):
        edge=(span-full*module-(full+1)*j)/2
        if D('0')<edge<=module:valid.append((full,edge))
    assert valid,(span,module,j)
    aggressive=max(valid,key=lambda x:x[0])
    safe=[v for v in valid if v[1]>=D('3')]
    preferred=max(safe,key=lambda x:x[0]) if safe else max(valid,key=lambda x:x[1])
    return aggressive,preferred,('CUT_UNDER_3' if aggressive[1]<3 else 'NO_NOMINAL_UNDER_3'),('REVIEW_NO_SAFE_END' if preferred[1]<3 else 'NOMINAL_SAFE_END')

cuts=[]
for rid,i in wc.items():
    for w,l in i['rectangles']:
        for fmt,nom in [('24x48',(D(24),D(48))),('12x24_CONDITIONAL_INDIVIDUAL_MAKER_SKU_UNVERIFIED',(D(12),D(24)))]:
            for orientation,(mwidth,mlength) in [('A_long_axis_depth',nom),('B_long_axis_across',(nom[1],nom[0]))]:
                for jt in [D('0.125'),D('0.1875')]:
                    (agw,safew,gw,sw)=centered(w,mwidth,jt)
                    (agl,safel,gl,sl)=centered(l,mlength,jt)
                    cuts.append(dict(room=rid,parent=i['parent'],v4_finish_color=i['color']+' 24x48 Anti-Slip LEVEL',wc_prior_source_area_SF=str(i['area']),
                      hypothetical_rectangle_width_in=str(w),hypothetical_rectangle_depth_in=str(l),
                      rectangle_area_equals_prior_SF='TRUE',actual_WC_wall_length_or_door_width_known='FALSE',
                      hypothetical_tile_format=fmt,nominal_axis_orientation=orientation,
                      nominal_width_module_in=str(mwidth),nominal_depth_module_in=str(mlength),
                      illustrative_grout_joint_in=str(jt),
                      aggressive_width_full_tiles=agw[0],aggressive_width_edge_each_in=n(agw[1]),aggressive_width_gate=gw,
                      safer_width_full_tiles=safew[0],safer_width_edge_each_in=n(safew[1]),safer_width_gate=sw,
                      aggressive_depth_full_tiles=agl[0],aggressive_depth_edge_each_in=n(agl[1]),aggressive_depth_gate=gl,
                      safer_depth_full_tiles=safel[0],safer_depth_edge_each_in=n(safel[1]),safer_depth_gate=sl,
                      actual_Nexus_UniFit_template_anchor_clearance='',actual_door_to_Primary_grout_line='',true_1529_WC_polygon_and_underlayment='',actual_calibrated_tile_and_grout='',original_raw_exact_wet_LEVEL_lab='',
                      owner_approval='FALSE',architect_shop_accept='FALSE',tile_installer_accept='FALSE',purchase_released='FALSE'))
assert len(cuts)==48
write('R28_48_WC_PRIOR_AREA_HYPOTHETICAL_RECTANGULAR_BOND_AND_JOINT_CUTS.csv',cuts)

costs=[]
for rid,i in wc.items():
    wc_prior=i['area']
    wc_hyp_gross=wc_prior*D('1.15')
    rem=i['primary_floor_gross']-wc_hyp_gross
    assert rem>0
    for u,par in zip(i['copies'],i['parents']):
        costs.append(dict(room=rid,WC_unit=u,PARENT_PRIMARY_unit=par,WC_prior_source_area_SF=str(wc_prior),source_floor_color=i['color'],
          WC_v4_floor_finish='24x48 Anti-Slip',PARENT_source_floor='24x48 Soft LEVEL +12x24 Anti-Slip PAN, SHB BLENDED ORIGINAL',
          original_parent_PRIMARY_mixed_floor_QUOTE_GROSS_SF_copy=str(i['primary_floor_gross']),original_parent_PRIMARY_mixed_floor_rate_USD_per_GROSS_SF=str(i['rate']),
          original_parent_PRIMARY_mixed_floor_USD_copy=str(i['original_floor_USD_copy']),
          WC_hypothetical_original_waste_equivalent_piece_SF_DIAGNOSTIC=n(wc_hyp_gross),
          hypothetical_remaining_PRIMARY_including_mixed_PAN_source_GROSS_SF_DIAGNOSTIC=n(rem),
          check_partition_EQUALS_original_gross='TRUE',
          provisional_WC_diagnostic_at_historic_BLENDED_source_rate_USD=n(wc_hyp_gross*i['rate']),
          true_color_finish_SPECIFIC_WC_price_USD='',new_WC_order_amount_USD='0_SEPARATE_DO_NOT_ORDER',
          actual_1529_WC_floor_NET_SF='',actual_PRIMARY_LEVEL_excluding_WC_NET_SF='',actual_shower_LINEAR_PAN_NET_SF='',new_approved_cut_allowance='',confirmed_factory_tile_SKU_case_sf='',same_lot_shared_parent_WC_purchase_cases='',current_Chicago_supplier_price='',installed_labor_threshold_base_USD='',
          special_case_203A_unplaced='TRUE' if u=='203A' else 'FALSE',
          owner_approved='FALSE',GC_approved='FALSE',reservation_released='FALSE',purchase_released='FALSE'))
assert len(costs)==4
write('R28_4_WC_INCLUDED_PARENT_MIXED_FLOOR_QUOTE_DIAGNOSTIC_SPLITS.csv',costs)

pieces=[]
for rid,i in wc.items():
    for fmt,piecearea in [('24x48_ANtISLIP_v4_exact_SKU_NOT_IDENTIFIED',D(8)),('12x24_ANtISLIP_OPTION_only_if_individually_approved',D(2))]:
        one=ce(i['area']/piecearea)
        two=ce(2*i['area']/piecearea)
        pieces.append(dict(room=rid,color=i['color'],v4_selected_format='24x48 Anti-Slip',
          hypothetical_nominal_format=fmt,nominal_piece_area_SF=str(piecearea),
          prior_wc_area_one_copy_SF=str(i['area']),prior_wc_area_both_copies_SF=str(2*i['area']),
          theoretical_area_only_MIN_pieces_one_copy=one,theoretical_two_copies_MIN_pieces_if_same_lot_nocut=two,
          individual_piece_ceil_if_no_cross_unit_cut_reuse=one*2,
          theoretical_lower_bound_difference_if_pooled_across_two_copies=two-one*2,
          source_primary_floor_gross_ALREADY_INCLUDES_WC='TRUE',actual_exact_color_format_finish_SKU='',actual_usable_calibrated_piece_size='',actual_cardboard_cut_schedule='',actual_cut_reuse_possible='',actual_factory_box_coverage='',current_orderable_cases='',owner_signed='FALSE',GC_signed='FALSE',supplier_lot_allocated='FALSE',purchase_released='FALSE'))
assert len(pieces)==4
write('R28_4_SAME_COLOR_TWO_UNIT_NOMINAL_TILE_PIECE_MINIMUM_NO_CASE_CLAIM.csv',pieces)

threshold=[]
for rid,i in wc.items():
    W,L=i['rectangles'][1]  # illustrated 36in width, no assertion of installed 36in door
    P=2*(D(W)+D(L))/D(12)
    for door in [D('24'),D('30'),D('36')]:
        for joint in ['SAME_EXACT_APPROVED_LEVEL_24x48_AntISlip_NO_COLOR_CHANGE','SCHEDULED_WC_AntISlip_to_parent_QUOTED_Soft_CONDITIONAL_PROFILE']:
            threshold.append(dict(room=rid,hypothetical_nonfield_rectangle_width_in=str(W),hypothetical_nonfield_rectangle_depth_in=str(L),
              original_WC_prior_area_SF=str(i['area']),hypothetical_opening_in_NOT_MEASURED=str(door),
              nominal_face_perimeter_before_door_LF=n(P),nominal_optional_base_less_this_one_door_LF=n(P-door/D(12)),
              optional_tile_base_NEW_scope_UNSELECTED='TRUE',tile_base_height_and_edge_thickness='',factory_preformed_matching_base_available='UNVERIFIED',
              nominated_tile_substrate_change=joint,
              change_in_TRUE_completed_finished_floor_elevation_in='',door_leaf_undercut_and_sweep_actual='',threshold_strip_production_length_and_profile='',actual_movement_joint_length_and_color='',actual_signed_local_code_clearance='',actual_TOto_footprint_under_anchor_condition='',
              owner_tilebase_selected='FALSE',architect_accept='FALSE',plumber_accept='FALSE',installer_mockup_performed='FALSE',purchasing_release='FALSE'))
assert len(threshold)==12
write('R28_12_WC_DOOR_BASE_TRANSITION_PERIMETER_WITHOUT_NEW_ORDER.csv',threshold)

tiers={
'PH-WC':[
('GOOD','Retain v4 ELM Cortar BONE 24x48 Anti-Slip WC LEVEL and original TOTO Nexus Cotton; keep no WC WALL tile or separate Niche/PAN','Separate true finish/FFL profile to parent original Soft if the source descriptions remain different; one inherited PH Primary source floor line includes WC 15 SF','Lower design disruption, source factory WC tile SKU, raw exact individual LEVEL wet lab, factory toilet UniFit/anchoring and one door section still absent'),
('BETTER','Same v4 Bone 24x48 Anti-Slip and same TOTO Nexus, but jointly center/rotate WC bond around skirt and doorway with 1/8 or3/16 mock joint; distinguish full-tile vs safe two-end cuts','No new tile SKU or priced material change; constrain 1:1 layout to verified flange center and toilet footprint, core drills in well-supported tile, actual movement/door line','More intentional grout and serviceability than arbitrary rectangular center, supports buyer quality but needs true 1529 WC polygon and parent tile bond'),
('BEST','Conditional individually maker-verified Bone 12x24 Anti-Slip WC LEVEL layout only with owner finish change, exact current 12x24 x Anti-Slip product and raw maker wet DCOF; full toilet template/accessible door mockup','More joints and possible cut reuse around skirt; must have new cost, raw lab, actual added transitions/base and 125% budget check if cap specified; 12x24 shower PAN historic row is NOT automatic WC LEVEL product','Potential improved cuts and service/maintenance; may lose visual large-format luxury and incur labor/edge cost, not a preferred purchase without lab/quote')
],
'TX-WC':[
('GOOD','Keep v4 ELM Cortar CLAY 24x48 Anti-Slip WC LEVEL, TOTO Nexus Cotton as listed in TX Primary, NO WC WALL/NICHE/PAN','Ensure TX203A UNPLACED original geometry cannot anchor cuts, and 203B old 14SF is no actual survey; finish transition to Clay Soft parent quote requires original individual lab and owner','Safe lowest-change aesthetic is subtle Clay stone and manufacturer-maintained one-piece WC, not a proven installed clear width'),
('BETTER','Retain identical v4 Clay 24x48 Anti-Slip with a shifted bond axis that preserves doorway threshold and avoids narrow cuts under the skirt anchors','No duplicate case purchase; area-equivalent 28x72 or 36x56 synthetic rectangles prove how cut-risk shifts, not geometry; independent 202A/B parent/WC line approval','Cleaner strong-floor continuity and reduced small cuts are conceivable, actual case yield and install cost unknown'),
('BEST','Conditional maker-identified Clay 12x24 Anti-Slip exact orderable SKU with raw individual lab; 1:1 special anchorage/joint and owner-signed primary/WC transition','Smaller format could absorb irregular TX203A/203B WC geometry after survey but more joints/grout and potential new profile, maker catalog size+finish listing not specific SKU','Only consider if a real survey shows 24x48 unavoidable small slivers or poor flange integrity; no silent v4 substitution')
],
'PH-PRIMARY':[
('GOOD','Preserve PH 48in Brizo BT0734816-BNX Black Onyx LINEAR + separate BR73480, no niche, and the original quoted BONE Soft 24x48 bath LEVEL / 12x24 Anti-Slip PAN SOURCE, while PH-WC remains v4 24x48 Anti-Slip','Retain exact quote as historical evidence, expose wet LEVEL vs PAN and door finish mismatch; architect must reconcile original full-room Anti-Slip v4 with quoted Soft BEFORE both same-lot reservation and actual raw lab','Low design rework, but split texture at WC may be less seamless and exact source item permission/raw lab missing'),
('BETTER','Owner-conditional full PH Primary NON-PAN LEVEL and PH-WC in one exact Bone 24x48 Anti-Slip selected by tile schedule v4, one continuous verified-lot field from WC door','Separately maintain Brizo LINEAR sloped small-format PAN and wet-wall evidence; build one parent plus WC actual NET (WC included), factory same SKU/lab/water-resistant threshold owner sign','Reduces dissimilar Soft/AntiSlip change at WC if accepted and may improve visual continuity, but cannot assume equal quote rates or slip/labor'),
('BEST','Architect/owner-signed PH WC threshold/joint and factory Nexus 12 or optional 14 UniFit with correct floor FFL, base/door clearance and source-true simulated 1:1, then choose ONLY a maker tested exact Bone LEVEL tile','Use selected 48in LINEAR+BR73480 and independently certified PAN, do not add niche; premium workmanship and original material lot traceability, no new maker tile/fixture imagined','Buyer-visible clean continuity/maintenance earns priority over unsupported premium tile cost; actual owner fixture/finish change not selected')
],
'TX-PRIMARY':[
('GOOD','Preserve TX 48in Brizo BT0734816-BNX Black Onyx LINEAR with BR73480, no niche, original quoted CLAY Soft 24x48 LEVEL +12x24 Anti-Slip PAN and separate seeded TX-WC Clay 24x48 Anti-Slip','As-built TX 202A/B parent and TX203A/B WC allocation requires one parent floor quote not second WC order; 203A area unplaced and current 1527 Revit mismatch','No premium uplift, but parent-to-WC finish division and duplicate BR73480 source labels remain unresolved'),
('BETTER','Owner-conditional TX PRIMARY NON-PAN LEVEL + TX-WC same exact calibrated Clay 24x48 Anti-Slip per v4, one color lot with written shared LEVEL allocation','Preserve selected independent Brizo 48in LINEAR shower pan test, correct original duplicate BR73480 wall-trim entry into one-rough factory BOM without editing source and owner signatures','Simplified parent/WC doorway finish and two-copy cut reuse possible but no credited savings until true exact SKU/lab/case and installed quote'),
('BEST','Coordinate whole TX floor/door threshold FFL, clay caliper, toilet UniFit 12/14 option, parent WC joint movement and owner material finish choice under final numbered 202/203 1529 site drawings','Do not replace BNX fixture or add niches; advanced source-grade physical mockup checks WC service, shower drain/threshold separately and small-format PAN factory wet evidence','Premium value is reliable install and toe/door service clearance with resale-friendly same color; no current lot, upgraded chrome lever or owner tile alternative assumed')
]}
opts=[]
for rid,rows in tiers.items():
    r=ROOMS[rid]
    for tier,design,detail,value in rows:
        wid=rid if rid.endswith('-WC') else rid.replace('PRIMARY','WC')
        i=wc[wid]
        opts.append(dict(room=rid,tier=tier,original_board_status=r['status'],original_champion_id=r['champion_id'] or '',
          original_weighted_board_score='' if r['champion_score'] is None else str(r['champion_score']),
          current_selected_Nexus='TOTO MS642124CEFG#01 Cotton one per PRIMARY source unit; actual WC/Primary location UNVERIFIED',
          exact_selected_primary_shower='Brizo BT0734816-BNX 48in LINEAR + separate BR73480, NO NICHE',
          original_WC_floor_v4=wid+' '+i['color']+' 24x48 Anti-Slip LEVEL FT'+('1' if rid.startswith('PH') else '2'),
          quotation_parent_floor_conflict='Soft 24x48 bath LEVEL +12x24 Anti-Slip PAN blended old quote versus v4 WC Anti-Slip 24x48',
          new_GOOD_BETTER_BEST_manufacturer_specific_design=design,
          new_cross_room_rough_floor_tile_finish_edge_strategy=detail,
          buyer_value_and_unresolved_cut_install_cost=value,
          fixture_12in_Unifit_standard_14in_OPTION_not_selected='TSU10W.12 standard / TSU10W.14 optional, TOTO 0GU186-A template',
          WC_source_floor_area_SF_copy=str(i['area']),WC_separate_material_order='FALSE',
          exact_original_measured_LEVEL_wet_DCOF_provided='FALSE',exact_original_measured_LINEAR_PAN_wet_DCOF_provided='FALSE_IF_PARENT_ONLY',
          new_manufacturer_specific_color_size_finish_approval='FALSE',actual_1529_geometry_verified='FALSE',
          owner_approved='FALSE',architect_signed='FALSE',plumber_signed='FALSE',tile_installer_signed='FALSE',GC_signed='FALSE',purchasing_released='FALSE'))
assert len(opts)==12
write('R28_12_WC_AND_PARENT_FACTORY_NEXUS_CORTAR_GOOD_BETTER_BEST.csv',opts)
print('PASS R28 48 geometry-equivalent layout scenarios, 4 included-no-extra floor quote partitions, 4 color format lower bound piece diagnostics, 12 door/base profiles, 12 maker-specific GOOD/BETTER/BEST')
