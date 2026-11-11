"""R37 one-time substantive additive: three dry powder 1:1 fixture/relief-wall
construction, quantified openings, finish planes, full 13-room GC/PO gates.
Uses original immutable material, prior geometry and signed source citations.
All live Revit/Smartsheet untouched. NO new owner program or purchase.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib,io,csv,json,math
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement"
assert not D.exists(),"One-time signed R37 creator must never overwrite a package"
ANCESTORS={
 "R30_FULL":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
 "R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"),
 "R35_FULL":("deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json","75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"),
 "R36_SOURCE":("state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"),
 "R31_PRELIMINARY":("state/ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json","61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"),
 "R32_PRELIMINARY":("state/ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json","9ad8564e2676f4e72533e6830bea627757e393dc1cdc537b297d443caae962b4"),
}
for k,(path,digest) in ANCESTORS.items():
    assert hashlib.sha256((B/path).read_bytes()).hexdigest()==digest,k
def csvread(path):
    with (B/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
old=csvread("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
W25=csvread("deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
A65=csvread("deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
R31lab=csvread("research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
R31wall=csvread("research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
R31unit=csvread("research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
ROOMS=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
comps=json.loads((B/"research/comps/comps.json").read_text(encoding="utf-8"))["comps"]
assert (len(old),len(W25),len(A65),len(R31lab),len(R31wall),len(R31unit),len(ROOMS),len(comps))==(27,25,65,13,50,26,13,14)
assert sum(Decimal(r["historic_usd_two_copies"] or 0) for r in old)==Decimal("23572.44")
assert sum(r["historic_niche_excluded_no_scope"]=="TRUE" for r in old)==2
rooms={r["id"]:r for r in ROOMS}
FOCUS=("PH-POWDER","TX-POWDER","TX-POWDER2")
G={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in FOCUS}
P={r:json.loads((B/"rooms"/r/"plumbing.json").read_text(encoding="utf-8")) for r in FOCUS}
W={(r["room"],r["wall"]):r for r in W25}
OLD={r["room"]:r for r in old if r["room"] in FOCUS}
assert len(OLD)==3
PARAM={
 "PH-POWDER":{"source":"Earth Lines relief Vera Forma 2x10 Glossy","color":"Earth Lines","size":"2x10","module_a":10.0,"module_b":2.0,"body_mm":8.6,"finish":"Glossy","wood":True,
              "faucet":"Brizo Frank Lloyd Wright T65722LF-GL Luxe Gold WALL+R65700 separate","material_grade":"ELM Vera Forma Earth Lines 2x10 DRY Walls"},
 "TX-POWDER":{"source":"Haze Camel/Wheat 1.6x5 Matte illustrative 70/30","color":"Camel and Wheat DISTINCT","size":"1.6x5","module_a":5.0,"module_b":1.6,"body_mm":8.0,"finish":"Matte","wood":True,
              "faucet":"AXOR One 48140991 PGO WALL TRIM OR hansgrohe Metropol 32526141 BB WALL TRIM (owner program unresolved; NOT a trim/rough pair)","material_grade":"ELM Haze Camel and Wheat DRY Walls only"},
 "TX-POWDER2":{"source":"Vera Forma Indigo Edge 6x6 Glossy relief","color":"Indigo Edge","size":"6x6","module_a":6.0,"module_b":6.0,"body_mm":8.6,"finish":"Glossy","wood":True,
              "faucet":"hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK not wall; basin UNSELECTED","material_grade":"ELM Indigo Edge Vera Forma 6x6 DRY Walls"},
}
FACTORY={
 "BRIZO":"https://www.brizo.com/bath/product/T65722LF-GL",
 "METROPOL":"https://www.hansgrohe-usa.com/articledetail-metropol-wall-mounted-single-handle-faucet-trim-with-lever-handle-1-2-gpm-without-pop-up-drain-32526141",
 "METROPOL_ROUGH":"https://www.hansgrohe-usa.com/articledetail-rough-wall-mounted-single-handle-faucet-13622181",
 "AXOR":"https://www.axor-design.com/us/articledetail-axor-one-wall-mounted-widespread-faucet-220-cross-handles-1-2-gpm-48140991",
 "TECTURIS":"https://www.hansgrohe-usa.com/articledetail-tecturis-e-single-hole-fine-240-1-2-gpm-without-pop-up-drain-73072341",
 "DRAIN_TECTURIS":"https://www.hansgrohe-usa.com/articledetail-drain-for-sinks-push-open-50100341",
 "VERAFORMA":"https://www.elmsurfaces.com/product-collection/vera-forma",
 "HAZE":"https://www.elmsurfaces.com/product-collection/haze",
 "INDIGO":"https://www.elmsurfaces.com/product/indigo-edge-vera-forma",
}
def F(x):return f"{x:.4f}"
def Money(x):return f"{x:.2f}"
PAYLOAD={}
def csvout(name,records):
    assert records and len({tuple(r.keys()) for r in records})==1,(name,len(records))
    s=io.StringIO(newline="")
    w=csv.DictWriter(s,fieldnames=list(records[0]),lineterminator="\n")
    w.writeheader();w.writerows(records)
    PAYLOAD[name]=s.getvalue().encode("utf-8-sig")
def mdout(name,body):PAYLOAD[name]=(body.strip()+"\n").encode("utf-8")
def flags(**kw):return kw
BASE={}
for r in FOCUS:
    g=G[r];w=g["tiled_walls"]
    assert len(w)==1 and w[0]["id"]=="W1" and g["floor_finish"]=="wood, no tile"
    assert (r,"W1") in W and (r,"W3") not in W
    assert len(g["revit_room_numbers"])==2 and len(g["revit_room_element_ids"] or [])==0
    win=float(W[r,"W1"]["source_width_in_UNVERIFIED"])
    hin=float(W[r,"W1"]["source_tiled_height_in_UNVERIFIED"])
    net=win*hin/144
    gross=float(OLD[r]["source_gross_sf_one_copy_waste_15pct_once"])
    assert abs(net*1.15-gross)<0.05,(r,net,gross)
    BASE[r]=dict(width=win,height=hin,face=net,gross=gross,old_two=float(OLD[r]["historic_usd_two_copies"]),
                 rate=float(OLD[r]["historic_usd_two_copies"])/(2*gross))
assert sum(Decimal(OLD[r]["historic_usd_two_copies"]) for r in FOCUS)==Decimal("2159.30")

# Distinct detailed new observation: all original dry-wall old gross amounts
# reconstruct source W1 FULL field *1.15, not a cut/net mirror schedule.
original=[]
for r in FOCUS:
    x=BASE[r]
    original.append(dict(room=r,original_tile_row_ID=OLD[r]["source_row_id"],
      source_wall_W1_width_in_UNVERIFIED=F(x["width"]),source_wall_W1_height_in_UNVERIFIED=F(x["height"]),
      source_full_wall_W1_field_NET_before_splash_mirror_escutcheon_SF=F(x["face"]),
      reconstructed_prior_gross_only_once_1point15_SF=F(x["face"]*1.15),
      original_historic_GROSS_SF_per_copy_includes15pct=F(x["gross"]),
      original_historic_minus_reconstructed_GROSS_SF=F(x["gross"]-x["face"]*1.15),
      original_historic_two_copy_material_only_USD=OLD[r]["historic_usd_two_copies"],
      original_blended_two_copy_rate_USD_per_GROSS_SF_REFERENCE_ONLY=F(x["rate"]),
      original_quote_SOURCE_no_order_pending_owner="TRUE",
      original_reduced_net_openings_mirror_splash_signed_1529="NONE_VERIFIED",
      original_source_W3_face_exists="FALSE",WOOD_FLOOR_untiled="TRUE",
      WET_WALL_NICHE_permissions="N_A_DRY_WALL_WITH_SINK_SPLASH_COMPATIBILITY_STILL_SHOP_HOLD",
      LEVEL_and_PAN_original_numeric_wet_DCOF="N_A_WOOD_FLOOR_NO_SHOWER",
      original15pct_already_in_gross="TRUE",
      new_material_quote_issued="FALSE",owner_approved="FALSE",purchase_authorized="FALSE"))
csvout("R37_3_ACTUAL_POWDER_HISTORIC_W1_FULL_HEIGHT_NET_VS_15PCT_GROSS_AND_PRICE_CONTROL.csv",original)

# Mirror surface vs real wall aperture: mirror fixed over tile MUST NOT cause a
# wall deduction. A genuinely recessed cabinet can remove only the aperture
# and needs separate return faces and return trim. No powder has a real niche.
openings=[]
OPTS=[
 ("SURFACE_MIRROR_24x30_TILE_REMAINS",24.,30.,"SURFACE"),
 ("RECESSED_CABINET_18x24_ONLY_IF_OWNER_SELECTED",18.,24.,"RECESSED"),
 ("RECESSED_CABINET_24x30_ONLY_IF_OWNER_SELECTED",24.,30.,"RECESSED"),
 ("SURFACE_MIRROR_30x36_TILE_REMAINS",30.,36.,"SURFACE")
]
for r in FOCUS:
    x=BASE[r]
    for unit in G[r]["revit_room_numbers"]:
        for label,ow,oh,k in OPTS:
            whole=ow*oh/144.
            deduct=whole if k=="RECESSED" else 0.
            # Not a niche tile requirement: returns are merely an independent
            # conditional shop with no assumed cabinet depth or wet use.
            openings.append(dict(room=r,source_physical_room=unit,hypothetical_option=label,
               original_full_W1_face_SF_unverified=F(x["face"]),
               hypothetical_mirror_or_CABINET_external_face_W_in=F(ow),
               hypothetical_mirror_or_CABINET_external_face_H_in=F(oh),
               mirror_cover_not_a_tile_deduction="TRUE" if k=="SURFACE" else "FALSE",
               hypothetical_wall_aperture_SF=F(whole),
               field_cladding_deduction_SF_ONCE=F(deduct),
               conditional_surrounding_wall_FIELD_NET_SF=F(x["face"]-deduct),
               theoretical_recess_inside_perimeter_LF=F(2*(ow+oh)/12. if k=="RECESSED" else 0.),
               optional_recess_RETURN_depth_in="UNKNOWN_NO_CALIBRATED_CABINET_SELECTED",
               optional_recess_BACK_or_TWO_SIDES_TOP_SILL_SF="N_A_NO_SOURCE_NICHE_NO_AUTOMATIC_TILE",
               actual_load_bearing_substrate_mirror_anchor_and_dry_splash_seal="UNKNOWN",
               actual_1529_wall_support_pipes_vents_wire_mirror_installer_clearance="",
               historic_rate_material_ONLY_field_deduction_proxy_USD_NOT_CREDIT=Money(deduct*x["rate"]*1.15),
               actual_trims_return_paint_labor_price_USD="",
               actual_recess_owner_approval="FALSE",actual_native_1529_verified="FALSE",
               purchase_authorized="FALSE"))
assert len(openings)==24
csvout("R37_24_SIX_POWDER_W1_MIRROR_SURFACE_VS_RECESSED_CABINET_ONE_FIELD_OPENING_AND_TRIMS.csv",openings)

# Localized flat mounting panel for actual wall faucets: do not conflate with
# R27's full-height painted center. Feature field was historically full height.
landings=[]
for r in FOCUS:
    x=BASE[r]
    for unit in G[r]["revit_room_numbers"]:
        for label,wi,hi in (("CONTINUOUS_RELIEF_ALL_FACADE_NO_LOCAL_PANEL",0,0),
                            ("SMALL_LOCAL_PLANAR_MAKER_ESCUTCHEON_BEARING",8,6),
                            ("EXTENDED_LOCAL_PLANAR_SPLASH_BEARING",12,12)):
            is_wall=r!="TX-POWDER2"
            eff=(wi*hi/144.) if is_wall else 0.
            trim=2*(wi+hi)/12 if eff>0 else 0.
            landings.append(dict(room=r,physical_source_copy=unit,landing_scheme=label,
                actual_fixture_mount_type="WALL" if is_wall else "DECK",
                fixture_owner_status=PARAM[r]["faucet"],
                source_fixture_mount_on_tiled_wall=(r!="TX-POWDER2"),
                sample_local_panel_nominal_W_in=F(wi),sample_local_panel_nominal_H_in=F(hi),
                hypothetical_local_relief_TILE_removed_SF_once=F(eff),
                hypothetical_separate_local_PLANAR_FINISHED_bearing_area_SF=F(eff),
                hypothetical_extra_local_perimeter_profile_LF=F(trim),
                source_full_focal_wall_nominal_tile_field_NET_SF=F(x["face"]),
                remaining_TILE_field_NET_SF=F(x["face"]-eff),
                source_old_material_gross_SF_already_15pct_once=F(x["gross"]),
                historic_blended_rate_proxy_tile_only_delta_USD_NO_CREDIT=Money(eff*x["rate"]*1.15),
                actual_selected_faucet_gasket_plate_footprint_and_support="UNKNOWN",
                painted_planar_replacement_is_FINISHED_surface_not_exposed_backer="TRUE",
                true_maker_wall_faucet_rough_supported_thickness="UNKNOWN" if is_wall else "N_A_DECK",
                actual_basin_CENTERLINE_and_faucet_spout_splash_landing="UNKNOWN",
                actual_mirror_edge_counter_recess_electrical_rough="UNKNOWN",
                actual_tile_edge_paint_sealant_and_labor_bid="",
                existing_program_modified_by_this_scenario="FALSE",
                owner_panel_selected="FALSE",architect_PLUMBING_signed="FALSE",purchase_authorized="FALSE"))
assert len(landings)==18
csvout("R37_18_2COPY_POWDER_LOCAL_FLAT_WALL_BEARING_VS_CONTINUOUS_RELIEF_FACET_AND_COST.csv",landings)

# Three different horizontal tile bonds; the 3in project focal criterion
# cannot be physically imposed as a 3in dimension along a 1.6/2in relief tile.
# In such cases mark N/A and require actual calibrated short-axis module.
cuts=[]
for r in FOCUS:
    w=BASE[r]["width"]
    size=PARAM[r]
    for orient,dim in (("LONG_AXIS_HORIZONTAL",size["module_a"]),
                       ("SHORT_AXIS_HORIZONTAL",size["module_b"])):
        for joint in (.125,.1875):
            maxn=max(0,math.floor((w-joint)/(dim+joint)))
            for strategy,n in (("MAX_CENTRAL_FULL_MODULES",maxn),
                               ("ONE_FEWER_CENTRAL_MODULE",max(0,maxn-1))):
                edge=(w-n*dim-(n+1)*joint)/2
                flag="N_A_NARROW_FORMAT_AXIS" if dim<3 else ("PASS_THEORY" if 3<=edge<=dim else "FAIL_THEORY")
                cuts.append(dict(room=r,source_wall="W1_ONLY_NO_W3",bond=strategy,orientation=orient,
                  source_W1_width_in_UNVERIFIED=F(w),source_111in_height_UNVERIFIED=F(BASE[r]["height"]),
                  nominal_tile_face_dimension_in_this_axis=F(dim),illustrative_joint_in=F(joint),
                  integer_full_center_modules=n,
                  hypothetical_balanced_left_and_right_edge_cut_in=F(edge),
                  project_3in_FOCAL_cut_test=flag,
                  short_axis_under3in_inherent_small_format="TRUE" if dim<3 else "FALSE",
                  actual_factory_calibrated_FACE_dimension_in="",
                  actual_joint_bond_slope_flatness_washability_maker_acceptance="",
                  real_faucet_centerline_mirror_EDGE_and_counter_cutout_positions="",
                  actual_1529_wall_width_and_corner_returns="",
                  physical_1to1_cut_grout_edge_acceptance="FALSE",
                  owner_tile_pattern_approved="FALSE",purchase_authorized="FALSE"))
assert len(cuts)==24
csvout("R37_24_NEW_POWDER_TILE_VERTICAL_HORIZONTAL_MODULE_BALANCED_CUTS_JOINTS_3IN_FOCAL.csv",cuts)

# Height programming, an orthogonal facade scope from R27 centered paint.
# Future wall fractions are NOT assumed owner changes; powder floors WOOD.
height=[]
for r in FOCUS:
    span=BASE[r]["width"]
    full=BASE[r]["height"]
    for roomcopy in G[r]["revit_room_numbers"]:
        for target_h in (72,84,111):
            face=span*target_h/144.
            residual=BASE[r]["face"]-face
            height.append(dict(room=r,physical_source_copy=roomcopy,
                hypothetical_tile_wall_HEIGHT_in=F(target_h),
                original_full_source_HEIGHT_in=F(full),
                original_full_W1_field_NET_SF=F(BASE[r]["face"]),
                conditional_TILE_NET_to_this_height_SF=F(face),
                conditional_FINISHED_PAINT_or_panel_upper_wall_SF=F(residual),
                one_full_width_termination_profile_LF=F(span/12 if target_h<111 else 0),
                source_old_gross_SF_15pct_once=F(BASE[r]["gross"]),
                theoretical_NEW_tile_gross_at_historic15pct_equivalent_SF=F(face*1.15),
                theoretical_old_material_rate_removed_reference_USD_NOT_PAID_CREDIT=Money(residual*1.15*BASE[r]["rate"]),
                actual_paint_primer_relief_profile_mirror_sealant_and_labor_quote="",
                actual_factory_color_maker_same_lot_case_and_cut_waste="UNKNOWN",
                actual_OWNER_height_and_mirror_counter_sill_layout_approved="FALSE",
                original_quote_credit_or_paid_stock_verified="FALSE",
                historic_source_original15pct_not_reapplied_twice="TRUE",
                purchase_authorized="FALSE"))
assert len(height)==18
csvout("R37_18_SIX_POWDER_W1_FULL_HEIGHT_VS_APPROVED_FUTURE_SILL_PAINT_TILE_TERM_CONTRACT_SENSITIVITY.csv",height)

# Separate installed-finish-plane terms; not manufacturer buildable details.
# Mortar 2/3/4mm illustrative compressed; backer 12.7/15.875mm theoretical.
# Waterproofing not automatically present on DRY decorative walls.
stacks=[]
for r in FOCUS:
    tile=PARAM[r]["body_mm"]
    for unit in G[r]["revit_room_numbers"]:
        for backer,mortar in ((12.7,2.0),(12.7,3.0),(15.875,4.0)):
            installed=tile+backer+mortar
            stacks.append(dict(room=r,source_physical_copy=unit,
                source_nominal_TILE_BODY_thickness_mm=F(tile),
                hypothetical_dry_wall_BACKER_or_board_thickness_mm=F(backer),
                hypothetical_COMPRESSED_mortar_thickness_mm=F(mortar),
                hypothetical_partial_projection_from_original_stud_FACE_mm=F(installed),
                actual_wall_board_lath_or_existing_finishes_Z="UNKNOWN",
                actual_cementitious_treatment_water_splash_maker_sealant_Z="UNKNOWN",
                actual_tile_relief_HIGH_POINT_relative_to_manufacturer_nominal_body="UNKNOWN",
                actual_planar_escutcheon_support_and_gasket_land_Z="UNKNOWN",
                actual_wall_rough_factory_min_max_to_FINISHED_face="UNKNOWN",
                actual_mirror_bottom_and_vanity_counter_back_splash_Z="UNKNOWN",
                true_source_manufacturer_supported_combined_assembly="FALSE",
                actual_1529_field_tolerance_stack_signed="FALSE",
                actual_wet_WALL_or_PAN_claim="N_A_DRY_ONLY",
                installer_mockup_approved="FALSE",purchase_authorized="FALSE"))
assert len(stacks)==18
csvout("R37_18_SIX_PHYSICAL_POWDER_TILE_RELIEF_BACKER_MORTAR_ESCUTCHEON_PLANAR_FFL_STACKS.csv",stacks)

# Source-cited programs, exact matching component one-program-only rules.
# Do not coerce manufacturer MSRP from old R27 into a Chicago/2026 offer.
products=[
("PH-POWDER","Brizo","T65722LF-GL","WALL one-handle single-hole faucet TRIM Luxe Gold",FACTORY["BRIZO"],"OWNER_SELECTED","Selected factory projected spout 9-11/16in, rough separately needed; true basin splash point unverified","NONE_FLOOR_DRY_FEATURE_WALL"),
("PH-POWDER","Brizo","R65700","separate required wall rough for T65722LF-GL",FACTORY["BRIZO"],"OWNER_SELECTED_ROUGH","Plumber actual wall embed/valve support before substrate/tile relief mockup","N_A_WET_WALL_NUMERIC_LAB"),
("PH-POWDER","Brizo","RP72414GL","original separately specified pop-up drain Luxe Gold",FACTORY["BRIZO"],"OWNER_SELECTED_DRAIN","Verify actual selected basin overflow/trap/finish and compatibility; no assumed site install","N_A"),
("PH-POWDER","ELM Surfaces","Vera Forma Earth Lines 2x10","nominal 8.6mm glossy relief DRY feature wall",FACTORY["VERAFORMA"],"SOURCE_TILE_NOT_PUCHASE_APPROVED","Actual wet splash cleaning and planar faucet gasket bearing unapproved; no blanket wet-wall permission","DRY_ONLY"),
("TX-POWDER","AXOR","48140991","AXOR One 220 wall-mounted CROSS handle Polished Gold Optic TRIM",FACTORY["AXOR"],"OWNER_PROGRAM_UNRESOLVED_TRIM_OPTION","Cannot use Hansgrohe 32526141 as AXOR rough; exact AXOR compatible rough current identity unknown","N_A"),
("TX-POWDER","hansgrohe","32526141","Metropol Brushed Bronze wall-mounted SINGLE lever TRIM, not rough",FACTORY["METROPOL"],"OWNER_PROGRAM_UNRESOLVED_TRIM_OPTION","Not combined with AXOR; 'ALREADY PROCURED' original row does not prove stock","N_A"),
("TX-POWDER","hansgrohe","13622181","maker-listed matching rough ONLY for Metropol 32526141",FACTORY["METROPOL_ROUGH"],"OPTION_NOT_OWNER_SELECTED","Factory rough left/right 1/2in plumbing documented; not AXOR rough","N_A"),
("TX-POWDER","ELM Surfaces","Haze Camel matte","nominal 1.6x5, 8mm DRY only",FACTORY["HAZE"],"HISTORIC_MULTI_SHADE_COMPOSITION","70/30 Camel/Wheat is a single original wall; separate shade SKU/lot and no composite carton","DRY_ONLY"),
("TX-POWDER","ELM Surfaces","Haze Wheat matte","nominal 1.6x5, 8mm DRY only",FACTORY["HAZE"],"HISTORIC_MULTI_SHADE_COMPOSITION","No pooling with Camel unless factory exact same item SKU+color+finish+lot; this is a different color","DRY_ONLY"),
("TX-POWDER2","hansgrohe","73072341","Tecturis E Fine 240 Brushed Black Chrome single-hole DECK faucet",FACTORY["TECTURIS"],"OWNER_SELECTED_DECK","Basin unselected, so no valid owner countertop bore, outlet strike or backset; never wall mount","N_A"),
("TX-POWDER2","hansgrohe","50100341","original matching drain row requires overflow/finish check",FACTORY["DRAIN_TECTURIS"],"SOURCE_DRAIN_NEEDS_BASIN","Existing row notes model/finish ambiguity; owner basin/overflow and maker current exact identity must close","N_A"),
("TX-POWDER2","ELM Surfaces","Vera Forma Indigo Edge 6x6","nominal 8.6mm glossy relief DRY wall",FACTORY["INDIGO"],"HISTORIC_TILE_NOT_SHOP_APPROVED","Prior source carton 30pcs 7.34SF vs nominal 30x6x6=7.5SF; exact current factory yield NULL","DRY_ONLY")
]
manufacturer=[]
for room,brand,sku,description,url,status,gate,wet in products:
    manufacturer.append(dict(room=room,manufacturer=brand,exact_source_SKU_or_maker_collection=sku,
       product_description=description,manufacturer_or_prior_verified_official_URL=url,
       owner_source_status=status,known_factory_assertion_and_shop_HOLD=gate,
       individual_TILE_application=wet,
       current_orderable_factory_SKU_color_finish_caliber_date="UNKNOWN_UNLESS_EXACT_SOURCE_LISTED",
       current_stock_same_SHADE_LOT_chicago_offer_eta="",
       current_case_coverage_verified="FALSE",
       original_wet_RAW_numeric_wet_DCOF="N_A_WOOD_FLOOR_NO_PAN",
       original_WALL_NICHE_wet_permission="N_A_DRY_SOURCE_ONLY",
       owner_alternative_material_or_rough_approved="FALSE",
       GC_installed_shop_approved="FALSE",purchase_authorized="FALSE"))
assert len(manufacturer)==12
csvout("R37_12_INDIVIDUAL_POWDER_FAUCET_ROUGH_DRAIN_TILE_MAKER_IDENTITY_WALL_MOUNT_MISLABEL_GATES.csv",manufacturer)

# Owner-facing decision paths remain distinct by original room and immutable
# programs; they are NOT formal blind challenger packets or weighted boards.
options=[]
for r in FOCUS:
    if r=="PH-POWDER":
        tiers=[
          ("GOOD","RELIEF_FULL_WALL_REAL_BRIZO_WALL_BEARING","Earth Lines full-height source field; manufacturer approved fixture gasket plane must be confirmed or assembly stays HOLD","Minimize design change, but raised relief may prevent watertight flush plate bearing; no installed bid."),
          ("BETTER","LOCAL_PLANAR_FAUCET_SEAL_LANDING","Maintain selected Luxe Gold Brizo trim/rough with localized flat finished planar carrier in relief ONLY after selected escutcheon dimensions and full-size sample","Adds local tile edge/profile/paint sealant and labor; historic material deduction only illustrative."),
          ("BEST","INTEGRATED_MIRROR_COUNTER_WALL_FIXTURE_MOCKUP","Original relief direction with deliberately aligned mirror edge, selected Brizo seal, vanity splash and calibrated tile, lit/day-night 1:1 shop","Quality/cleanability rather than unsupported buyer premium; higher mockup/edge/installer coordination exposure.")]
    elif r=="TX-POWDER":
        tiers=[
          ("GOOD","HISTORIC_HAZE_ONE_WALL_AND_TRIM_HOLD","Keep Camel/Wheat dry W1 as original single wall; two original competing WALL trims remain separate and blocked pending owner program","No conflation of PGO AXOR cross and Brushed Bronze Metropol; no purchase."),
          ("BETTER","OWNER_CHOSEN_AXOR_OR_METROPOL_FLAT_BEARING","Once owner selects exactly one trim, factory exact rough (Metropol only 13622181 supported) and 1:1 three-escutcheon or one-lever bearing, color band modular joints","May reduce tile relief bearing conflicts; genuine rough, sink overflow and labor pricing unknown."),
          ("BEST","CONTROLLED_TWO_COLOR_FOCAL_COMPOSITION_WITH_SELECTED_HARDWARE","Still original Haze Camel/Wheat direction, verified color lot+70/30 real SKU and 1:1 three-handle vs one-lever mirror/backsplash alignment, proper backing and cleanable plane","Conditional visual quality, adds pattern/time and multiple lot constraints; no inferred buyer premium.")]
    else:
        tiers=[
          ("GOOD","ORIGINAL_INDIGO_FULL_WALL_NO_OWNER_BASIN","Preserve Indigo Edge 6x6 wall and selected Tecturis E DECK 73072341; do not add tile escutcheon or bore countertop without selected basin","Historic 7.34SF/case cannot establish current order; basin remains explicit owner HOLD."),
          ("BETTER","INDIGO_MIRROR_COUNTER_SPLASH_COORDINATION","Keep complete dry Indigo wall, source-calibrated 6in grid, mirror field and factory Tecturis E countertop reach template only after actual selected basin","Better symmetry/service; owner sink and drain overflow/countertop installed costs unknown."),
          ("BEST","INDIGO_ACCESSORY_FINISH_PLANE_1to1_MOCKUP","Owner selected actual basin first, then measured deck drilling/overflow/drain finish, full wall/mirror/counter backsplash and trims sample with exact current 6x6 lot","Higher presentation quality but new model and scope must be owner certified, no transfer of wall spout dimensions.")]
    for tier,code,narrative,cost in tiers:
        options.append(dict(room=r,tier=tier,design_branch=code,
           factory_selected_fixture_preserved=PARAM[r]["faucet"],construction_design_improvement=narrative,
           project_material_labor_and_procurement_risk=cost,
           original_wall_tile_SOURCE_direction=PARAM[r]["source"],
           owner_program_selection_made="FALSE",owner_basin_if_TX_POWDER2="UNSELECTED" if r=="TX-POWDER2" else "NOT_TRANSFERRED",
           individual_dry_WALL_only_no_WET_WALL_NICHE_gate="TRUE",
           wood_floor_WET_LEVEL_test="N_A",shower_PAN_test="N_A",
           original_weighted_board_score="NULL",actual_supplier_price_or_installed_bid_USD="",
           owner_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(options)==9
csvout("R37_9_THREE_POWDER_FACTORY_FAUCET_FACADE_GOOD_BETTER_BEST_OWNER_UNSELECTED.csv",options)

# 6 actual field instances x 3 specialized detail gates: rough vs tile face,
# mirror/counter/cabinet and actual wood floor/base/perimeter trim. No 1527
# site geometry can close any witness.
instances=[]
for r in FOCUS:
    for unit in G[r]["revit_room_numbers"]:
        for study in ("D1_PLUMBING_ROUGH_FACET_PENETRATION_ESCUTCHEON",
                      "D2_MIRROR_BASIN_VANITY_SPLASH_CASEWORK_BACKSET",
                      "D3_DRY_TILE_WOOD_FLOOR_MIRROR_EDGE_OUTSIDE_CORNER"):
            instances.append(dict(room=r,physical_source_room=unit,shop_detail=study,
              manufacturer_selected_faucet_or_critical_branch=PARAM[r]["faucet"],
              original_tile_source=PARAM[r]["source"],
              source_W1_width_in_UNVERIFIED=F(BASE[r]["width"]),
              source_W1_height_in_UNVERIFIED=F(BASE[r]["height"]),
              actual_native_1529_project_ID_wall_element_number="",
              true_field_W1_width_height_squareness_mirror_vanity_counter_splash="",
              actual_faucet_reach_to_selected_basin_landing="UNKNOWN",
              actual_wall_faucet_rough_and_gasket_bearing_LANDING="UNKNOWN" if r!="TX-POWDER2" else "N_A_DECK_FAUCET",
              actual_deck_faucet_drilling_template_counter_thickness="UNKNOWN" if r=="TX-POWDER2" else "N_A_WALL_FAUCET",
              real_owner_SELECTED_sink_internal_water_strike_and_overflow="UNSELECTED" if r=="TX-POWDER2" else "NOT_VERIFIED",
              actual_tile_caliber_joint_one_to_one_focal_cut_and_mirror_edge="",
              finished_tiled_dry_WALL_to_vanity_base_and_wood_floor_seal="",
              exposed_opening_edges_MIRROR_recess_vs_surface_distinction="",
              all_relevant_accessibility_clearances_actual="",
              actual_joint_edge_profile_AND_movement_joint_LF="",
              original_exact_rough_spout_and_stop_SERVED_UNDER_1to1="FALSE",
              actual_signed_full_size_physical_mockup="FALSE",
              owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
              tile_installer_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(instances)==18
csvout("R37_18_SIX_UNIT_THREE_SHOP_DETAIL_FACTORY_VANITY_SPLASH_MIRROR_WOOD_BASE_MOCKUP.csv",instances)

# Actual historical 3 dry powder walls are FOUR factory material identity
# buckets (TX Camel/Wheat distinct). Pooling across the physical copies may
# be considered only if actual SKU/color/finish/lot match; never pool room
# groups merely because relief tiles look similar.
lot_groups=[
 ("PH-POWDER","EARTH_LINES_GLOSS_2X10","Earth Lines one original shade",1.0),
 ("TX-POWDER","HAZE_CAMEL_MATTE_1p6X5","Haze Camel separate material",0.7),
 ("TX-POWDER","HAZE_WHEAT_MATTE_1p6X5","Haze Wheat separate material",0.3),
 ("TX-POWDER2","INDIGO_EDGE_GLOSS_6X6","Indigo Edge one shade",1.0)
]
lots=[];cases=[]
for r,bucket,description,frac in lot_groups:
    oldgross=BASE[r]["gross"]*frac
    lots.append(dict(room=r,trade_material_pool_identity=bucket,
        historic_original_SOURCE_tile_group=PARAM[r]["source"],
        original_COLOR_finish_format_distinction=description,
        illustrative_original_TX_Haze_suggested_color_share=F(frac),
        source_total_TWO_copy_gross15pct_once_SF=F(2*oldgross),
        same_SKU_color_size_finish_exact_FACTORY_lot_confirmed="FALSE",
        same_TWO_copy_lot_possible_only_with_factory_evidence="TRUE",
        shareable_WITH_OTHER_POWDER_ROOM_MATERIAL="FALSE",
        licensed_tile_WET_ROOM_application="N_A_DRY_ONLY",
        current_factory_carton_packaging_live_SF="",current_supplier_lot_stock_case_price="",
        exact_four_physical_room_original_location_refs="ONLY_TWO_SAME_ROOM_COPIES",
        actual_1529_site_cutstock_signed="FALSE",
        actual_case_pooling_or_order_authorized="FALSE",
        purchase_authorized="FALSE"))
    for hypothetical in (7.34,8.,12.):
        separately=2*math.ceil(oldgross/hypothetical)
        pooled=math.ceil(2*oldgross/hypothetical)
        cases.append(dict(room=r,distinct_material_pool_bucket=bucket,
          SOURCE_old_gross_per_physical_copy_waste15pct_once=F(oldgross),
          theoretical_historical_gross_across_two_copies_SF=F(2*oldgross),
          fictional_usable_case_capacity_SF_NOT_current_factory=F(hypothetical),
          theoretical_ceiling_TWO_independently_rounded_cases=separately,
          theoretical_ceiling_pooled_ONLY_same_factory_SKU_lot_cases=pooled,
          theoretical_cases_difference_NO_REALIZED_SAVINGS=separately-pooled,
          factory_exact_retail_item_and_usable_package_SF_verified="FALSE",
          actual_same_shade_lot_caliper_stock_for_both_units="FALSE",
          actual_owner_source_material_and_color_allocation_verified="FALSE",
          source_15percent_waste_ALREADY_once="TRUE",
          actual_order_rounding_or_savings_claimed="FALSE",
          purchase_authorized="FALSE"))
assert len(lots)==4 and len(cases)==12
csvout("R37_4_REAL_DRY_POWDER_FACTORY_COLOR_FINISH_MATERIAL_BUCKETS_AND_HARD_NONPOOLING.csv",lots)
csvout("R37_12_THEORETICAL_TWO_UNIT_SAME_SKU_LOT_CASE_CEIL_NOT_ORDERS.csv",cases)

# Deliberate dual quote: floor/material credit is not necessarily actual
# credit when mirror or panel cuts could have been bought already. Labor,
# substrate, mirror and paint/trim are separate adders.
estimate=[]
for r in FOCUS:
    for branch in ("SOURCE_FULL_HEIGHT_TILE_RETENTION",
                   "OWNER_CONDITIONAL_84IN_TILE_PLUS_PAINT",
                   "OWNER_CONDITIONAL_LOCAL_PLANAR_BEARING_WALL_ONLY"):
        full=BASE[r]["face"]
        if branch=="SOURCE_FULL_HEIGHT_TILE_RETENTION":
            reduct=0;extra_trim=0
        elif branch=="OWNER_CONDITIONAL_84IN_TILE_PLUS_PAINT":
            reduct=full-BASE[r]["width"]*84/144
            extra_trim=BASE[r]["width"]/12
        else:
            reduct=0 if r=="TX-POWDER2" else 1.0
            extra_trim=0 if r=="TX-POWDER2" else 4.0
        estimate.append(dict(room=r,owner_UNSELECTED_design_contract_branch=branch,
          original_two_copy_historic_material_ONLY_USD=OLD[r]["historic_usd_two_copies"],
          source_FACADE_full_height_NET_before_openings_SF=F(full),
          theoretical_removed_tile_FIELD_net_per_copy_SF=F(reduct),
          material_only_historic_rate_usd_per_GROSS=F(BASE[r]["rate"]),
          theoretical_original_rate_GROSS_equivalent_credit_two_copies_NOT_REAL=Money(2*reduct*1.15*BASE[r]["rate"]),
          source_old_historic15pct_IN_GROSS_ALREADY="TRUE",
          new_theoretical_2copy_EXPOSED_profile_or_TERMINATION_LF=F(extra_trim*2),
          original_order_paid_received_or_returnable_stock_evidence="",
          actual_supplier_credit_approved_USD="",real_counter_mirror_recess_panel_paint_labor_bid_USD="",
          actual_wall_backer_riser_metals_rough_work_USD="",actual_mirror_and_casework_fixing_price_USD="",
          date_stamp_and_factory_usable_case_color_lot_stock="",
          owner_decision_approved="FALSE",contract_change_order_signed="FALSE",
          actual_payable_savings_or_shortage_established="FALSE",purchase_authorized="FALSE"))
assert len(estimate)==9
csvout("R37_9_POWDER_FULL_HEIGHT_VS_VANITY_H84_VS_LOCAL_FLAT_INSTALLED_GC_CREDIT_CHANGE_ORDER.csv",estimate)

# Source-faithful camera and 1:1 physical mockup briefs only, NOT images or
# actual physical samples. Each unit verifies different fixture placement.
cameras=[]
for room in FOCUS:
    for unit in G[room]["revit_room_numbers"]:
        for view in ("V1_VANITY_FACADE_AND_MIRROR_FULL_W1",
                     "V2_FAUCET_COUNTER_BASIN_TRUE_SIDE_SECTION",
                     "V3_TILE_RELIEF_TRIM_WOOD_THRESHOLD_GRAZING"):
            cameras.append(dict(room=room,source_physical_copy=unit,view_request=view,
                preserve_existing_selected_FACET_and_finish=PARAM[room]["faucet"],
                preserve_existing_tile_design=PARAM[room]["source"],
                no_wall_rough_or_tile_escutcheon_for_DECK_TECTURIS=(
                  "TRUE" if room=="TX-POWDER2" else "N_A_WALL_FAUCET"),
                TX_powder_avoid_visualizing_two_competing_trims_as_one=(
                  "TRUE" if room=="TX-POWDER" else "N_A"),
                TX_powder2_owner_selected_basin="UNSELECTED" if room=="TX-POWDER2" else "NOT_APPLICABLE",
                background_native_1529_geometry_verified="FALSE",
                expected_1to1_references="real tiled board, selected physical fixture, countertop/mirror bearing plane and signed 1529 W1",
                proposed_lighting="neutral morning and warm artificial; no invented competitor tile",
                factory_maker_swatch_verified_color_lot="FALSE",
                created_render_or_photo="FALSE",built_physical_sample_or_mockup="FALSE",
                owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(cameras)==18
csvout("R37_18_SIX_UNIT_THREE_VIEW_SOURCE_FAITHFUL_FACADE_MIRROR_SPLASH_RENDER_AND_SAMPLE_BRIEFS.csv",cameras)

# Preserve 27 historical tile lines as immutable 2026-09 source and normalize
# ordering facts only. EXCLUDED niche rows remain no-scope. Powder items
# had original source_no_order=TRUE, so historic charge not actual purchase.
normalize=[]
for line in old:
    room=line["room"]
    amount=Decimal(line["historic_usd_two_copies"] or "0")
    gross=Decimal(line["source_gross_sf_one_copy_waste_15pct_once"] or "0")
    focus=room in FOCUS
    normalize.append(dict(room=room,
      original_historic_material_row_ID=line["source_row_id"],
      source_surface=line["source_surface"],
      gross_SF_one_copy_waste15pct_ALREADY_ONCE=str(gross),
      original_historic_two_copy_MATERIAL_ONLY_USD=str(amount),
      excluded_primary_niche_NO_ORDER=line["historic_niche_excluded_no_scope"],
      source_was_no_order_or_hold=line["source_no_order"],
      R37_powder_W1_material_scope="DRY_VANITY_WALL_NO_WET_FLOOR" if focus else "OUT_OF_R37_FOCUS_PRESERVE_PREVIOUS_SCOPE",
      R37_applicable_faucet_basin_or_rough_shop_gate=PARAM[room]["faucet"] if focus else "AS_ORIGINAL_ROOM",
      ORIGINAL_15pct_not_reapplied_to_prior_GROSS="TRUE",
      factory_SKU_color_size_finish_lot_same_sha_caliber="",
      source_actual_1529_net_MEASURED_SF_and_openings_once="",
      after_owner_design_REAL_cut_allowance_and_orderable_full_cases="",
      signed_same_FACTORY_product_in_two_copies_only="FALSE",
      public_retail_indication_or_MSRP_separate_current_CHi_supplier_bid="",
      current_chicago_case_stock_delivery_date_freight_tax="",
      current_installed_labor_screed_counter_paint_profile_mirror_bid="",
      available_historic_stock_paid_returnable_credit="",
      owner_approved="FALSE",supplier_approved="FALSE",
      GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(normalize)==27
assert sum(Decimal(x["original_historic_two_copy_MATERIAL_ONLY_USD"]) for x in normalize)==Decimal("23572.44")
csvout("R37_27_ORIGINAL_2026_TILE_MATERIAL_ROWS_TO_REAL_SAME_SKU_LOT_DRY_WALL_POWDER_13ROOM_PO_CROSSWALK.csv",normalize)

def program(room):
    if room in FOCUS:return "DRY_VANITY_TILE_WOOD_FLOOR; "+PARAM[room]["faucet"]
    if room in ("PH-PRIMARY","TX-PRIMARY"):return "SELECTED Brizo BNX 48in LINEAR + separate BR73480, WC floor included once, no niches; FLOOR quote PAN A/B unresolved"
    if room in ("PH-WC","TX-WC"):return "INHERITED parent Primary Cortar AntiSlip LEVEL floor, WC no separate order, TX203A unplaced"
    if room=="PH-BATH4":return "WALKIN Brizo BNX 4in SQUARE POINT + four-plane PAN and separate bath LEVEL; ribbed wall/Clara niche wet HOLD"
    if room in ("PH-BATH2","TX-BATH2","TX-BATH4"):return "DURAVIT TUB and Hansgrohe selected existing finish; NO tiled PAN, PH2/TX4 valve/spout conflict TX2 bathing rough/spout identity unknown"
    if room in ("PH-BATH3","TX-BATH3"):return "OWNER TUB vs WALKIN UNSELECTED; conditional original 4in POINT shower drain only WALKIN; R36 TUB/no PAN vs WALKIN inside/outside original quoted PAN"
    raise RuntimeError(room)
def wet(room):
    if room in FOCUS:return ("N_A_WOOD_DRY_WALL","N_A_WOOD_NO_LEVEL","N_A_PAN")
    if room in ("PH-POWDER","TX-POWDER","TX-POWDER2"):return ("N_A","N_A","N_A")
    if room in ("PH-WC","TX-WC"):return ("N_A","PARENT_WC_ANTISLIP_FINISH_ORIGINAL_NUMERIC_LEVEL_MISSING","N_A")
    if room in ("PH-BATH2","TX-BATH2","TX-BATH4"):return ("INDIVIDUAL_WET_WALL_AND_NICHE_MAKER_PERMISSION", "RAW_ORIGINAL_NUMERIC_LEVEL_MISSING","N_A_TUB")
    if room in ("PH-PRIMARY","TX-PRIMARY"):return ("EXACT_WET_WALL_MAKER_SEPARATE_NO_NICHES", "EXACT_RAW_LEVEL_NUMERIC_MISSING","EXACT_RAW_LINEAR_PAN_NUMERIC_MISSING")
    if room=="PH-BATH4":return ("RIBBED_WALL_CAVIAR_NICHE_INDIVIDUAL_HOLD","EXACT_RAW_LEVEL_NUMERIC_MISSING","EXACT_RAW_FOUR_PLANE_POINT_PAN_NUMERIC_MISSING")
    return ("INDIVIDUAL_WET_WALL_NICHE_MAKER_HOLD","EXACT_RAW_LEVEL_NUMERIC_MISSING","CONDITIONAL_POINT_PAN_NUMERIC_MISSING_IF_WALKIN")

originalR31lab={r["room"]:[] for r in R31lab}
for l in R31lab:originalR31lab[l["room"]].append(l["surface_role"])
all13=[];TRADE=("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")
trade=[]
for room in sorted(rooms):
    r=rooms[room]
    status=r["status"];champ=r.get("champion_id") or "null"
    score=str(r["champion_score"]) if r.get("champion_score") is not None else "null"
    wall_gate,level_gate,pan_gate=wet(room)
    amount=sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old if x["room"]==room)
    all13.append(dict(room=room,source_copies=2,original_board_round=17,
       original_status=status,original_champion=champ,original_score=score,
       original_two_copy_historic_material_only_USD=str(amount),
       selected_room_original_program=program(room),
       individual_WALL_NICHE_application_gate=wall_gate,exact_original_numeric_wet_LEVEL=level_gate,
       independent_linear_or_point_PAN_numeric_wet_gate=pan_gate,
       source_R31_13_labs_roles="|".join(originalR31lab.get(room,[])) or "N_A_DRY_OR_PARENT",
       latest_A_B_or_TUB_BRANCH_original_owner_only="UNSELECTED_BATH3" if room in ("PH-BATH3","TX-BATH3") else
         "A_B_PAN_QUOTE_UNRESOLVED" if room in ("PH-PRIMARY","TX-PRIMARY") else "PRESERVE",
       actual_1529_site_and_all_r31_50_Wall_26_instance_receipts="",
       actual_factory_SKU_color_finish_usable_case_and_true_chicago_installed_bid="",
       selected_OWNER_BASIN_or_FACET_conflict="TX2_POWDER_BASIN_UNSELECTED" if room=="TX-POWDER2" else
         "TX_POWDER_AXOR_VS_METROPOL_TRIM_UNSELECTED" if room=="TX-POWDER" else "SEE_PROGRAM",
       originally_signed_65_trades_unchanged="TRUE",
       owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
       waterproof_approved="FALSE",tile_installer_approved="FALSE",
       supplier_approved="FALSE",GC_approved="FALSE",purchaser_approved="FALSE",
       material_reserved="FALSE",purchase_authorized="FALSE",
       four_critic_SCORE="NULL",standing_nonpro_reviewer_accepted="FALSE"))
    for n,t in enumerate(TRADE,1):
        obligation={
          "OWNER":"Choose exact powder PH relief/flat-bear and TX program or TX2 basin; approve existing selected wet room program unchanged; budget cap and 1to1 sample",
          "ARCHITECT":"True native 1529 W1/W3 only if source proves it, actual powder mirror/vanity/basin and faucet datum, actual wet W/level/pan openings, shop sections",
          "PLUMBER":"Selected Brizo PH R65700 and spout reach; TX competing trim/rough and actual historic item inventory; TX2 DECK Tecturis basin/overflow; all wet bath selected drain/tub rough unchanged",
          "WATERPROOFING":"Powder dry wall N_A shower, approve splash seal/planar rough backing only; wet-bath original tub flange or POINT/LINEAR membrane/drain systems independently",
          "TILE_INSTALLER":"Actual powder dry wall calibrated tile and relief/wall corners/focal cuts/mirror opening, 1to1 matte/gloss/paint/edge, 13 wet lab roles proper N/A wood powders",
          "SUPPLIER":"Exact original 27 row source SKU/color/finish/lot, calibrated shade carton useful SF, case yield current Chicago terms; no Haze color pooling",
          "GC_ESTIMATOR":"Original $23572.44 and waste once, powder wall paint/trim/mirror/counter penetrations and paid inventory credit vs current full installed GC bid",
          "PURCHASER":"Only after seven authentic trade signoffs plus owner/four-seat governance, actual source/lot/current quotation, no early reservations"
        }[t]
        trade.append(dict(room=room,sequence=n,trade=t,submittal_and_situated_release_hold=obligation,
           native_1529_survey_and_signed_shop_detail="",
           original_raw_numeric_WET_LEVEL_AND_PAN_if_applicable="",
           factory_exact_SKU_and_valid_color_lot_case_offer="",
           verified_old_paid_inventory_credit_and_new_approved_installed_GC_bid="",
           formal_board_original_four_critic_scores_no_change="NULL",
           actual_acceptance_signature="",
           owner_approved="FALSE",GC_release="FALSE",purchaser_PO_release="FALSE"))
assert len(all13)==13 and len(trade)==104
assert sum(Decimal(x["original_two_copy_historic_material_only_USD"]) for x in all13)==Decimal("23572.44")
csvout("R37_13_ROOM_WET_DRY_SOURCE_SELECT_OWNER_ARCHITECT_GC_PROCUREMENT_RELEASE.csv",all13)
csvout("R37_104_EIGHT_TRADE_13ROOM_SEQUENTIAL_POWDER_AND_WET_PROGRAM_SPECIFIC_HOLDS.csv",trade)

# Referential overlay into original 26 room and 50 wall witnesses, with
# independent highly specific PH/TX powder details; don't regenerate old
# records, signed original R31 26/50 unchanged.
units=[]
for x in R31unit:
    room=x["room"];source_number=x["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"]
    focus=room in FOCUS
    units.append(dict(room=room,physical_copy_number=x["physical_copy_index"],
       provisional_room_reference=source_number,
       source_program_and_factory_hard_constraint=program(room),
       source_wet_application_and_LEVEL_PAN_R37="|".join(wet(room)),
       source_R31_same_physical_instance_receipt_preserved="TRUE",
       powder_actual_vanity_faucet_R37_deck_or_wall_gate=PARAM[room]["faucet"] if focus else "NOT_R37_POWDER",
       actual_mirror_counter_sink_footprint_recess_and_valve_or_drill="",
       actual_TRUE_1529_wall_floor_DRY_or_WET_geometry="",
       actual_selected_individual_wet_WALL_NICHE_and_original_RAW_floor_wet_labs="",
       physical_one_to_one_full_size_sample_and_source_faithful_camera_receipt="FALSE",
       factory_exact_tile_sku_color_lot_and_bid="",
       owner_signed="FALSE",architect_signed="FALSE",plumber_signed="FALSE",
       waterproof_signed="FALSE",tile_signed="FALSE",supplier_signed="FALSE",
       GC_signed="FALSE",purchaser_signed="FALSE",purchase_authorized="FALSE"))
assert len(units)==26
csvout("R37_26_ORIGINAL_PHYSICAL_ROOM_INSTANCE_DETAILED_DRY_WET_WITNESS_AND_OWNER_PROGRAM_BRIDGE.csv",units)

walls=[]
for x in R31wall:
    room=x["room"];focus=room in FOCUS
    walls.append(dict(room=room,source_physical_copy=x["physical_copy"],
      source_W1_W2_W3_original_wall_reference=x["wall_reference"],
      original_SOURCE_width_in_UNVERIFIED=x["prior_source_wall_width_in_UNVERIFIED"],
      original_SOURCE_height_in_UNVERIFIED=x["prior_source_tiled_height_in_UNVERIFIED"],
      powder_mirror_surface_v_recess_1_OPENING_deduction_logic="SURFACE_MIRROR_ZERO_TILE_DEDUCTION; RECESSED_ONLY_AFTER_SOURCE_CERTIFIED" if focus else "NOT_R37_POWDER",
      powder_direct_deck_vs_WALL_rough_detail=PARAM[room]["faucet"] if focus else "NOT_R37_POWDER",
      actual_NATIVE_1529_W1_face_width_height_and_wall_ID="",
      actual_door_window_mirror_recess_negative_field_ONCE_SF="",
      actual_niche_when_appropriate_separate_BACK_SIDES_TOP_SILL="",
      actual_escutcheon_splash_sink_mirror_bearing_rough_and_wall_STACK="",
      actual_TILE_NET_and_approved_cut_waste="",
      actual_edge_trim_and_movement_joint_LF="",
      individual_WET_wall_or_NICHE_permission_if_applicable="N_A_DRY_ONLY" if focus else "NEED_ITEM_OR_N_A",
      actual_elevation_shop_verified="FALSE",
      owner_approved="FALSE",architect_and_tiler_signed="FALSE",
      purchase_authorized="FALSE"))
assert len(walls)==50
csvout("R37_50_ORIGINAL_TWO_COPY_WALL_SURVEY_OVERLAY_DRY_VANITY_ONE_APERTURE_VS_WET_NICHE_GATE.csv",walls)

mdout("START_HERE_R37_POWDER_THREE_ROOM_FACTORY_FACADE_GC_OWNER_BOOK.md",f"""
# R37 1529 Wieland: integrated powder facade and 13-room procurement control

Additive owner/architect/GC engineering. Entire thirteen-room objective OPEN. Formal board R017 unchanged. The focus is PH-POWDER, TX-POWDER and TX-POWDER2, six source physical rooms. Their WOOD floors and dry decorative wall tile mean wet floor numerical DCOF and sloped shower PAN are N/A; dry tile is NOT authorized for a wet wall or niche.

R37 materially advances beyond R22/R27 by separating four different surface conditions in each powder: a surface-mounted mirror whose coverage must NOT be deducted from tile, a hypothetical true recessed mirrored cabinet with ONE actual field aperture and separate edge/return labour, a localized manufacturer-approved flat escutcheon bearing patch rather than an entire full-height painted strip, and partial-height tiled wall with a separate wall finish/termination and installed labour. New quantitative records: 24 mirror/opening cases, 18 local planar wall-patch cases, 24 oriented module/grout/cut cases, 18 vertical wall-height/paint/edge cases, 18 theoretical board/mortar/tile-high-point stacks, 18 six-unit detail witnesses, 12 maker source identities, 9 GOOD/BETTER/BEST options, 4 distinct manufacturer powder material identity groups, 12 fictional case sensitivities, 9 cost/CO exposures and 18 proposed camera/sample briefs. None is certified field geometry, actual mirror, owner approved finish, sample, render or current vendor quote.

Original preliminary W1 full-height wall SOURCE widths and quantities per copy: PH 50.688in x111in =39.072SF net; x1.15=44.9328 vs old44.9 GROSS SF. TX 35.880in x111in=27.6575SF net; x1.15=31.806125 vs old31.8. TX2 45.672in x111in=35.2055SF net; x1.15=40.486325 vs old40.5. Original combined six-unit powder material only $2,159.30 already within $23,572.44 historic full four-unit quote; original 15 percent waste INCLUDED ONCE. This near match only identifies preliminary original quote method, not a field-finished area or real credit. None of these original three powder W1 sources has a W3 elevation; do NOT invent one.

PH Powder: selected Brizo T65722LF-GL Luxe Gold WALL, separately required R65700 rough and original RP72414GL drain. Nominal published factory spout reach 9-11/16in from manufacturer {FACTORY["BRIZO"]} is not verified sink water strike, and Earth Lines 2x10 glossy relief nominal8.6mm may not furnish a flat gasket bearing. The 1:1 fixture/relief/flat support, mirror/vanity/wood base must be measured and approved before any tile cut.

TX Powder: original AXOR One 48140991 Polished Gold Optic CROSS-handle WALL TRIM versus hansgrohe Metropol 32526141 Brushed Bronze SINGLE-lever WALL TRIM, not trim plus rough. Factory-compatible 13622181 rough is for Metropol only, not AXOR. Owner program still unselected; original showroom procurement words do not prove actual inventory. Haze Camel and Wheat 1.6x5 matte nominal8mm occupy ONE original wall at provisional 70/30 mixture and require two different color lots, never two historic wall orders.

TX Powder2: selected Hansgrohe Tecturis E 73072341 Brushed Black Chrome single-hole DECK faucet, no wall valve, no tile escutcheon. BASIN UNSELECTED, so there is no authorized countertop drilling or water strike. Separate drain 50100341 requires real manufacturer model/finish and basin overflow compatibility. Indigo Edge 6x6 glossy relief nominal8.6mm retains original owner direction. Historical 30pcs/7.34SF box source differs from nominal 7.5SF exposed face of thirty nominal 6x6 tiles; both are only source observations, neither verified current Chicago carton yield.

Source-grade complete 13-room protection: 27 original tile source lines (two excluded no-order Primary niche reference rows), 25 original provisional wall studies, 65 historic trade actions, R31 13 original numerical wet specimen roles, 50 wall witnesses and 26 room physical instances reconciled. New thirteen release rows and 104 eight-trade sequence holds all FALSE. Parent WC floor included once, no added Primary shower niche, PH/TX Primary original BNX LINEAR+BR73480 rough, PH Bath4 actual BNX POINT walkin PAN distinct from LEVEL, Duravit three tubs NO tiled PAN, Bath3 owner TUB/WALKIN and source R36 changed scope UNSELECTED. Historic Sandstone $358.92, Grey Soft $1116.46 and Caviar $1163.32 ALREADY INCLUDED. No owner/current supplier/GC/PO approval; all scoring remains NULL.

Market PH 2.8M/TX 2.7M, Old Town primary 2.4M-3.2M, 14 listings from nine buildings, OT01-OT04 405 W Armitage ONE building, Lincoln Park/Gold Coast secondary. No fabricated material identity, price saving or buyer premium. Read the manufacturer sections, floor/case/cost tables and future 1:1 camera briefs. Verified 1529 model absent (current accessible 1527 cannot establish 1529 geometry); original DESIGN worker9 failed and sole non-Pro Reviewer15 finished. No independent signoff or global DONE.
""")

mdout("R37_FACTORY_FAUCET_SINK_MIRROR_COUNTER_ESCUTCHEON_1TO1_CONSTRUCTION_SECTIONS.md",f"""
# R37 actual powder maker-specific dry-feature-wall and faucet / counter sections

## SH-PH: Brizo Frank Lloyd Wright wall and glazed relief

Exact selected Brizo Frank Lloyd Wright T65722LF-GL ({FACTORY["BRIZO"]}) is a Luxe Gold wall-mounted single-handle trim with separate R65700 required wall rough and RP72414GL drain in source. Manufacturer published 9-11/16in spout projection, but installed basin geometry, wall datum and water strike are UNKNOWN. Existing ELM Vera Forma Earth Lines 2x10 nominal8.6mm glossy relief ({FACTORY["VERAFORMA"]}) is a dry WALL source, not a certified flat continuous escutcheon gasket plane. Draw structural backing -> actual R65700 rough embedding -> actual substrate and splash seal -> calibrated compressed setting mortar -> ceramic BODY and RELIEF HIGH POINT -> truly planar approved faucet land -> escutcheon/lever sweep -> mirror/vanity/back splash. A localized hypothetical 8x6in or 12x12in finished FLAT patch may be an option only with maker gasket bearing and owner selection; do not treat an exposed board as finished paint. Perimeter patch trim, cleaning seal, wood base and actual labor are separately priced and surveyed, not automatically paid historical tile credits.

## SH-TX: two different wall trim programs, not rough/trim interchangeable

AXOR One 48140991 is a Polished Gold Optic CROSS-handle WALL mounted TRIM ({FACTORY["AXOR"]}); hansgrohe Metropol 32526141 is a Brushed Bronze SINGLE-lever WALL mounted TRIM ({FACTORY["METROPOL"]}). They are mutually exclusive original programs awaiting owner choice, not AXOR trim plus Metropol rough. Hansgrohe 13622181 ({FACTORY["METROPOL_ROUGH"]}) is maker listed compatible ONLY with Metropol 32526141. Original row label claiming 32526141 is a rough is wrong, and historical showroom wording does not establish an order or physical inventory. AXOR exact compatible rough identity and current body/plate bearing/handle spacing remain unknown. Hold rough procurement and Haze Camel/Wheat 1.6x5 nominal8mm dry wall tile faucet penetration cuts until full chosen trim/rough maker shop, three escutcheon vs one-lever clearance, mirror position and actual basin overflow are signed. The tile short 1.6in orientation cannot satisfy an arbitrary 3in small tile focal-piece criterion; a manufacturer-calibrated actual module, grout and visual acceptance sample controls instead. No maker wet tile permission transfers.

## SH-TX2: DECK faucet, no wall escutcheon

Selected Tecturis E 73072341 ({FACTORY["TECTURIS"]}) Brushed Black Chrome is single-hole DECK faucet. The owner-selected basin is NULL; do not determine actual spout landing, drilling center, countertop thickness/rear clearance, overflow, drain trim or water geometry without owner-selected basin and current individual factory cut sheets. Original drain 50100341 ({FACTORY["DRAIN_TECTURIS"]}) needs exact finish and overflow compatibility proof. Existing ELM Indigo Edge Vera Forma 6x6 glossy nominal8.6mm ({FACTORY["INDIGO"]}) is a dry feature W1 only. Mirror can remain surface-mounted over full tile with ZERO aperture deduction. Only a truly recessed cabinet with signed manufacturer/service/shelf/back support generates ONE measured opening deduction; separate jamb/top/sill/edge finish scope is independent, not a pre-existing shower niche.

## Quantitative architectural release rules, each two physical instances

Source W1 only PH50.688 x111in, TX35.880 x111in, TX2 45.672 x111in. Source height 111in is a drawing-derived PROVISIONAL full wall. R37 separately models full/84/72in tiled HEIGHT with independent upper paint area, one new horizontal termination LF when partial, and actual mirror/vanity/wood base; no automatic extra old 15 percent waste. For surface-mounted mirror, always original W1 tile field intact. For an unselected REAL cabinet cut aperture, deduct only ONE nominal wall rectangle; separately measure actual back/sides/top/sill if a true framed return needs tile and its full edge profiles, do not automatically add them to dry niche line. The 24 cuts use hypothetical long/short axis tile face and joints, not factory calibrated shop. A tile nominal body plus a hypothetical backer 12.7/15.875mm and compressed mortar2/3/4mm is merely a partial stack: actual rough wall, waterproof/splash seal, relief high point, metal gasket/service and paint base unknown. NO verified 1529 field coordinates. Six physical copy mockups need real manufacturer finish physical tile, actual selected trim, measured vanity mirror and true counter, day/night light, photo and signatures; none exists yet.

Waterproofing: powder walls DRY but sink splash/washability and sealant still require maker and GC documentation; no shower/wet WALL, NICHE, LEVEL wet floor or PAN DCOF test is applicable on the WOOD floor. Genuine 1529 room/counter/valve/door widths must be field checked. A full mockup and signed shop approval precede fixture opening drilling, procurement and installation.
""")

mdout("R37_THREE_POWDER_CROSS_ROOM_REAL_COLOR_LOT_COST_CONTRACT_AND_OWNER_ARCH_GC_BOOK.md",f"""
# R37 independent supplier, GC and owner cost engineering — true dry powder source scope

Three original dry powder material-only source rows (two physical copies each): PH Earth Lines 44.9 SF GROSS/copy $736.36 BOTH copies, TX Powder Haze Camel+Wheat 31.8 SF/copy $758.74 BOTH, TX Powder2 Indigo 40.5 SF/copy $664.20 BOTH, **$2,159.30 ALREADY WITHIN $23,572.44** old tile material-only four-unit total. The original gross contains 15% waste ONCE, and source_no_order TRUE indicates historical amount is not proof tile was ordered or paid. Original W1 geometric field comparisons are provisional and do NOT certify purchased, installed or independently current contract amounts.

The original one-wall Haze source contains two distinct colors. Its 70/30 mixture is a previous hypothetical design proportion, **NOT** two 31.8-SF wall orders. Four actual distinct factory color/finish/size groups: PH Earth Lines glossy 2x10, TX Haze Camel matte 1.6x5, TX Haze Wheat matte 1.6x5, TX2 Indigo Edge glossy 6x6. No two of these can pool material across rooms; same two copies within one material bucket require exact maker full SKU/color/finish/caliber/lot and usable factory case coverage before cross-unit remainder pooling. R37 twelve fictional 7.34 / 8 / 12 SF carton ceiling tests demonstrate why initial individual rounding can exceed same-SKU shared rounding but none is a real manufacturer box size, allocated Chicago stock or realized saving. TX2 historic 30pcs/7.34 SF/case conflicts with nominal thirty6x6=7.5SF nominal face; retain the original quote label and require current factory pack verification rather than silently updating.

R37 explicitly tests three independent alteration types not co-mingled in historic source: superficial mirror (no tile deduction) versus real recessed cabinet (one wall aperture deduction, independent return/casing), new local faucet gasket flat support (one finished patch replaces original relief field, independent edge and splash seal), or reduced wall tile height with newly finished painted upper wall and one termination line. A theoretical material-only rate applied to removed tile GROSS-equivalent is NOT a payable credit: old tile could already be purchased, actual factory SKU/case and real returnability unknown; mirror, carpenter/cabinet, paint, tile trim, plumber, setting and other actual installed labor are separate bid categories. R37 nine contractor cost/credit records provide no fabricated difference or change order authorization.

Maker public MSRP historically recorded: Brizo PH trim and R65700 separately $1080 +$191, TX AXOR 48140991 trim $1695 (AXOR rough unknown), TX Metropol 32526141 trim $844 + matching 13622181 rough $475, TX2 Tecturis E deck $835; all are original PUBLIC MANUFACTURER INDICATIONS as-of prior R27 research, not current Chicago supplier pricing or purchased materials. Do not assert the unequal AXOR-trim-only $1695 vs Metropol-complete-$1319 MSRP difference as a like-for-like actual saving, and do not treat 32526141 as rough. All pending material variation costs need current exact factory and installer signed quote including plumber rough/return, countertop and drain/overflow, true room-specific 1:1 mockup, paint and tile edge labor, case/lot/freight/tax and any actual paid original invoice credit.

Eight sequential trade release: owner chooses only actual powder feature wall/tier and TX faucet or TX2 basin, architect certifies true 1529 W1 and mirror/vanity/counter shop, plumber verifies original Brizo or one actual TX trim/rough and owner TX2 deck/basin drain, waterproof trade confirms dry-wall splash seal (other wet baths independently), tile trade signs calibrated mirror/edge/relief and 1:1 sample, supplier provides exact color/shade/lot/case current offer, GC signs measured net and complete installed bid/actual historical returnability, purchaser acts ONLY after all signatures and applicable original independent governance. No 1527 geometry transfers.

Full 13 original ID release/witness integration includes two Primary selected BNX 48in LINEAR with separate BR73480 and no new niches, inherited Primary/WC flooring once, actual PH4 BNX square POINT shower four-plane PAN and LEVEL, PH2/TX2/TX4 three Duravit tubs and NO tiled PAN, PH3/TX3 owner TUB/WALKIN unselected with R36 distinct contract scopes, powder faucets/finishes and TX Powder2 sink not selected. Wet individual WALL/NICHE approvals separately and exact original measured numerical wet LEVEL and LINEAR/POINT PAN test roles unresolved where applicable; dry powder wood floors N/A. Original 13 rooms/27 material rows incl two unpriced Primary niches/25 old W studies/65 trade rows and old $23,572.44 once. Included Sandstone $358.92, Cortar Grey $1116.46, Caviar $1163.32 not new money. Original 14 listing entries are nine separate properties, Old Town first for $2.4M-$3.2M PH/TX buyers; Lincoln Park/Gold Coast secondary, no hidden-photo competitor tile assumption or arbitrary resale premium.

Formal round017 unchanged. Original worker9 failed without two authentic R014 design critiques, Reviewer15 finished/nonrevivable, no formal R37 blind panel or challenger score. All owner, architect, plumber, waterproofing, tile installer, supplier, GC and purchaser approval/purchase flags FALSE. Entire 13-room objective OPEN.
""")

# Predecessor immutable signed manifests; R32 and R36 signed source receipts
# are NOT misrepresented as full integrated manifests.
LINEAGE={}
for i in list(range(12,32))+[33,35]:
    dirs=[d for d in (B/"deliverables").glob(f"integrated-r{i}*") if (d/"MANIFEST.json").exists() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(dirs)==1,(i,dirs)
    LINEAGE[f"R{i:03d}_INTEGRATED"]=hashlib.sha256((dirs[0]/"MANIFEST.json").read_bytes()).hexdigest()
for key,(path,digest) in ANCESTORS.items():LINEAGE[key]=digest
for formal in ("ROUND014_SUBMISSION","ROUND017_SUBMISSION"):
    LINEAGE[formal]=hashlib.sha256((B/"state"/(formal+".json")).read_bytes()).hexdigest()

M=dict(round=37,date_local="2026-11-06",
 project="1529 Wieland 13-room bathroom owner/architect/GC design and procurement loop",
 phase="SUBSTANTIVE_NEW_THREE_POWDER_FACTORY_FACADE_13_ROOM_RELEASE_NOT_FORMAL_BLIND_BOARD",
 focus=list(FOCUS),predecessor_signed_file_hashes=LINEAGE,
 original_scope=dict(original_distinct_room_IDs=13,original_two_physical_copy_instances=26,
  original_material_rows=27,original_unpriced_excluded_Primary_niche_refs=2,
  original_W1_W2_W3_provisional_elevations=25,original_trade_actions=65,
  historic_tile_only_four_unit_USD="23572.44",historical_old_waste_15pct_ALREADY_once=True,
  historic_sandstone_material_included_USD="358.92",historic_grey_material_included_USD="1116.46",
  historic_caviar_material_included_USD="1163.32",
  three_powder_source_material_included_usd="2159.30",
  comp_entries=14,distinct_comp_buildings=9),
 new_quantified_scope=dict(
  original_three_dry_powder_gross_W1_reconstructions=len(original),
  mirror_surface_vs_cabinet_aperture_unit_cases=len(openings),
  local_planar_faucet_escutcheon_relief_removal_cases=len(landings),
  long_short_tile_module_and_joint_cut_cases=len(cuts),
  partial_height_W1_paint_and_termination_unit_cases=len(height),
  approximate_board_mortar_nominal_tile_finished_plane_units=len(stacks),
  manufacturer_identity_wet_dry_faucet_program_rows=len(manufacturer),
  owner_GOOD_BETTER_BEST_room_options=len(options),
  six_unit_three_specialized_shop_detail_hold_rows=len(instances),
  four_distinct_maker_material_bucket_nonpooling_rows=len(lots),
  fictional_case_ceiling_sensitivities=len(cases),
  theoretical_historic_material_only_vs_installed_gc_credit_exposures=len(estimate),
  proposed_sample_camera_briefs_not_produced=len(cameras),
  original_quote_item_normalization_rows=len(normalize),
  original_26_physical_instance_shop_extension=len(units),
  original_50_wall_study_extension=len(walls),
  all_13_room_release_matrix=len(all13),
  eight_trade_13_room_sequential_holds=len(trade)),
 owner_faucet_program_TX_POWDER_selected=False,
 owner_sink_TX_POWDER2_selected=False,
 preserved_original_SELECTED_DECK_TECTURIS=True,
 selected_original_Brizo_PH_wall_faucet_rough_and_drain_preserved=True,
 actual_1529_native_model_or_field_wall_measurements_verified=False,
 actual_wall_wet_application_permission_inferred_from_dry=False,
 real_current_supplier_chicago_case_stock_eta_installed_quote=False,
 source_no_order_historical_quote_reinterpreted_as_actual_order=False,
 current_owner_paint_and_local_panel_alternatives_selected=False,
 actual_physical_mockups_or_images_created=False,
 original_four_critic_reports_complete=False,
 independent_nonpro_reviewer_accepted=False,
 original_formal_board_round=17,weighted_board_scores=None,
 owner_approved=False,architect_approved=False,plumber_approved=False,
 waterproofing_approved=False,tile_installer_approved=False,supplier_approved=False,
 GC_approved=False,purchaser_approved=False,material_reserved=False,
 purchase_authorized=False,global_DONE=False,
 files=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in sorted(PAYLOAD.items())])
assert len(PAYLOAD)>=20,len(PAYLOAD)
D.mkdir(parents=True,exist_ok=False)
for name,data in sorted(PAYLOAD.items()):
    with (D/name).open("xb") as f:f.write(data)
(D/"MANIFEST.json").write_bytes((json.dumps(M,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R37_PAYLOADS",len(PAYLOAD))
print("R37_MANIFEST_SHA",hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest())
print("R37_COUNTS",json.dumps(M["new_quantified_scope"],sort_keys=True))
