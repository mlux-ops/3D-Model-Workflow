"""R39 substantive 3-bath owner/architect/GC wet design and procurement package.
One-time creation. No native Revit, Smartsheet, email, vendor, board or owner writes.
Original signed R37/R38 and all earlier references strictly immutable.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from collections import Counter
import hashlib,io,csv,json,math
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement"
assert not OUT.exists(),"Signed R39 folder already exists; never rerun one-time creator"
PREDECESSOR={
 "R37_FULL":("deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement/MANIFEST.json","985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"),
 "R38_PRELIM_SOURCE":("state/ROUND038_NEXT_DISTINCT_WET_WALL_MAKER_PERMISSION_FULL_FIELD_NICHE_OPENING_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","34d5fa02c436cf94d06aa56e662dad27ffc57fbb11b4dd8a9a18a084b03a80f4"),
 "R36_PRELIM_SOURCE":("state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"),
 "R35_FULL":("deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json","75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"),
 "R30_FULL":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
 "R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e")
}
for n,(f,sha) in PREDECESSOR.items():
    assert hashlib.sha256((BASE/f).read_bytes()).hexdigest()==sha,n
def csvread(rel):
    with (BASE/rel).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
old=csvread("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
W25=csvread("deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
A65=csvread("deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
LAB=csvread("research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
W50=csvread("research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
U26=csvread("research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
ROOMS=json.loads((BASE/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
comps=json.loads((BASE/"research/comps/comps.json").read_text(encoding="utf-8"))["comps"]
assert (len(old),len(W25),len(A65),len(LAB),len(W50),len(U26),len(ROOMS),len(comps))==(27,25,65,13,50,26,13,14)
assert len({x["id"] for x in ROOMS})==13
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
FOCUS=("PH-BATH3","PH-BATH4","TX-BATH3")
G={r:json.loads((BASE/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in FOCUS}
PL={r:json.loads((BASE/"rooms"/r/"plumbing.json").read_text(encoding="utf-8")) for r in FOCUS}
W={(x["room"],x["wall"]):x for x in W25}
OLD={(x["room"],x["source_surface"]):x for x in old}
PAY={}
def F(x):return f"{float(x):.4f}"
def C(x):return f"{Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP):.2f}"
def addcsv(name,records):
    assert records and len({tuple(x.keys()) for x in records})==1,(name,len(records))
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(records[0]),lineterminator="\n")
    w.writeheader();w.writerows(records)
    PAY[name]=s.getvalue().encode("utf-8-sig")
def addmd(name,txt):PAY[name]=(txt.strip()+"\n").encode("utf-8")
def B(room):return room in ("PH-BATH3","TX-BATH3")
MAKER={
 "SOHO_BLUE":"https://www.elmsurfaces.com/product/soho-blue",
 "SOHO_IVORY":"https://www.elmsurfaces.com/product/soho-ivory",
 "SOHO_EMERALD":"https://www.elmsurfaces.com/product/soho-emerald",
 "NOHO_EMERALD":"https://www.elmsurfaces.com/product/noho-emerald",
 "SANDSTONE":"https://www.elmsurfaces.com/product/sandstone-tones",
 "SAPPHIRE":"https://www.elmsurfaces.com/product/sapphire-tones",
 "EMERALD":"https://www.elmsurfaces.com/product/emerald-tones",
 "OPAL":"https://www.elmsurfaces.com/product/opal-tones",
 "RIBBED":"https://www.elmsurfaces.com/product/cortar-bone-ribbed",
 "CAVIAR":"https://traditionsintile.com/project/clara/",
 "DRAIN_BRIZO":"https://www.brizo.com/bath/product/BT062415-BN",
 "TCNA_SHOWER":"https://tcnatile.com/resource-center/faq/showers/",
 "TCNA_MOVEMENT":"https://tcnatile.com/resource-center/faq/placement/",
 "IMI_MOVEMENT":"https://imiweb.org/detailing-series/06ej171k/"
}
V={
 "PH-BATH3":{
  "old_tile":"ELM Tones Opal 2x20 Glossy", "old_nom_mm":8.5,
  "wall_issue":"INDIVIDUAL_OPAL_WET_WALL_UNVERIFIED_STOP", "niche":"ELM Tones Sandstone 2x20 Glossy maker wet WALL/NICHE archived PASS",
  "fixtures":"Hansgrohe Chrome shower; Delta DT062412 Chrome SQUARE 4in POINT conditional WALKIN; owner basin UNSELECTED",
  "decision":"TUB vs WALKIN UNSELECTED; tub selection/overflow UNSELECTED",
  "options":[
   dict(code="P3-A",name="SOHO_BLUE_WET_WALL_WITH_EXISTING_SANDSTONE_NICHE",maker="ELM Soho Blue 2x10 Glossy",size=(10.,2.),nom_mm=9.5,
      state="LIVE_CURRENT_INDIVIDUAL_WET_WALL_LISTED",url=MAKER["SOHO_BLUE"],
      design="Blue glossy wet enclosure with warm Sandstone niche; Opal used only outside certified wet splash if owner wants it",
      diff="Color/format change from Opal 2x20 to Soho Blue 2x10; new lot/edge plane plus grout modules; historic niche distinct SKU"),
   dict(code="P3-B",name="TONES_SANDSTONE_UNIFIED_WET_FIELD_AND_NICHE",maker="ELM Tones Sandstone 2x20 Glossy",size=(20.,2.),nom_mm=8.5,
      state="ARCHIVED_EXACT_WET_LISTED_CURRENT_LIVE_ITEM_NOT_RETRIEVED",url=MAKER["SANDSTONE"],
      design="One warm family for wet walls and prior Sandstone niche; align horizontal field and return face; Opal cannot remain inside wet",
      diff="Physically different 20in format/finish plane, potential same product Sandstone across original four niche rooms only with factory identical SKU+lot; actual retail source not verified") ]},
 "PH-BATH4":{
  "old_tile":"ELM Cortar Bone Ribbed 24x48 relief", "old_nom_mm":None,
  "wall_issue":"INDIVIDUAL_RIBBED_WET_WALL_UNVERIFIED_STOP", "niche":"Clara Tierra Madre Caviar 2x8 exact individual NICHE wet authorization absent; conditional Soho Ivory only",
  "fixtures":"Brizo BT062415-BNX 4in SQUARE POINT actual WALKIN, separate four-plane PAN and bath LEVEL; Black Onyx",
  "decision":"WALKIN SELECTED; no tub; 35 vs 27 SF bath floor & vendor 214.4 disputed",
  "options":[
   dict(code="P4-A",name="SOHO_IVORY_SINGLE_WET_WALL_AND_WET_NICHE",maker="ELM Soho Ivory 2x10 Glossy",size=(10.,2.),nom_mm=9.5,
      state="LIVE_CURRENT_INDIVIDUAL_WET_WALL_LISTED",url=MAKER["SOHO_IVORY"],
      design="Uniform wet-listed ivory wall and niche with matte Black Onyx shower fixtures; remove Caviar from wet niche if owner authorizes",
      diff="Replace original ribbed relief and Caviar with one smooth current maker wet wall product for niche only if exact application/edge confirmed; cross-surface two original quotes NOT automatically combined"),
   dict(code="P4-B",name="SOHO_IVORY_WET_ENCLOSURE_RIBBED_DRY_ACCENT_ONLY",maker="ELM Soho Ivory 2x10 Glossy",size=(10.,2.),nom_mm=9.5,
      state="LIVE_CURRENT_INDIVIDUAL_WET_WALL_LISTED",url=MAKER["SOHO_IVORY"],
      design="Wet-listed smooth 2x10 enclosure; original Bone Ribbed limited to independently verified OUTSIDE spray/dry vanity backdrop",
      diff="Requires a real source 1529 dry wall, seal/wet boundary and explicit separately purchased ribbed trim/lot; no dry wall is presently certified") ]},
 "TX-BATH3":{
  "old_tile":"ELM Tones Emerald 2x20 Glossy", "old_nom_mm":8.5,
  "wall_issue":"ARCHIVED_WET_LISTED_EMERALD_LIVE_EXACT_ITEM_PAGE_UNAVAILABLE", "niche":"Original Tones Sandstone 2x20 glossy wet NICHE archived listed",
  "fixtures":"Brizo Black Onyx BT062415-BNX 4in SQUARE POINT conditional WALKIN only",
  "decision":"TUB vs WALKIN UNSELECTED; no owner-selected tub/overflow",
  "options":[
   dict(code="T3-A",name="SOHO_EMERALD_GLOSSY_WET_WALL_SANDSTONE_NICHE",maker="ELM Soho Emerald 2x10 Glossy",size=(10.,2.),nom_mm=9.5,
      state="LIVE_CURRENT_INDIVIDUAL_WET_WALL_LISTED",url=MAKER["SOHO_EMERALD"],
      design="Preserve lively green glossy value but change original 2x20 Tones to manufacturer-listed 2x10 Soho Emerald; retained warm Sandstone niche",
      diff="Same color word not same SKU: new maker collection and 9.5 vs Tones 8.5mm nominal body, new module/edge/service."),
   dict(code="T3-B",name="NOHO_EMERALD_MATTE_WET_WALL_SANDSTONE_NICHE",maker="ELM Noho Emerald 2x10 Matte",size=(10.,2.),nom_mm=9.5,
      state="LIVE_CURRENT_INDIVIDUAL_WET_WALL_LISTED",url=MAKER["NOHO_EMERALD"],
      design="More subdued matte green wet wall with warm Sandstone niche/Brizo Black Onyx; retain owner original fixtures",
      diff="Distinct Noho MATTE SKU vs SOHO GLOSSY and Tones GLOSSY, requires separate cleaning/grout sample, not a floor approval or raw pan DCOF.") ]}
}
for room in FOCUS:
    assert len(G[room]["revit_room_numbers"])==2 and len(G[room]["tiled_walls"])==3
    assert all((room,w) in W for w in ("W1","W2","W3"))
    assert all((room,s) in OLD for s in ("wall","floor","accent"))
    assert len(V[room]["options"])==2
    plids={x["model_or_sku"] for x in PL[room]["fixtures"]}
    if room=="PH-BATH3":assert "DT062412" in plids
    else:assert "BT062415-BNX" in plids
assert not any((BASE/n).exists() for n in ["rooms/PH-BATH3/board/round-039","rooms/PH-BATH4/board/round-039","rooms/TX-BATH3/board/round-039"])

# Exactly six distinct unscored owner neutral design challengers. No formal
# hidden private mapping or fictitious four-seat blind critiques.
chall=[]
for room in FOCUS:
 for item in V[room]["options"]:
  chall.append(dict(room=room,unscored_evidence_neutral_option=item["code"],
    proposed_factory_product_exact_display=item["maker"],nominal_long_axis_in=F(item["size"][0]),
    nominal_short_axis_in=F(item["size"][1]),nominal_tile_BODY_thickness_mm=F(item["nom_mm"]),
    manufacturer_individual_page=item["url"],wet_WALL_listing_status=item["state"],
    existing_original_WET_WALL_permission_gate=V[room]["wall_issue"],
    separately_original_WET_NICHE_status=V[room]["niche"],
    evidence_grade="LIVE_PUBLIC_ITEM" if item["state"].startswith("LIVE") else "ARCHIVED_PRODUCT_EXACT_CURRENT_REVALIDATION_REQUIRED",
    conditional_design_quality=item["design"],construction_and_real_procurement_difference=item["diff"],
    actual_selected_fixture_and_owner_program=V[room]["fixtures"]+"; "+V[room]["decision"],
    original_level_numeric_raw_lab="MISSING",original_independent_POINT_pan_numeric_raw_lab="MISSING_IF_WALKIN",
    four_original_SPECIALIST_critiques_complete="FALSE",
    formal_board_round=17,weighted_score="NULL",owner_chosen="FALSE",
    actual_same_SKU_color_finish_lot_current_Chicago_stock="",
    manufacturer_WP_system_and_installed_1to1_signed="FALSE",
    purchase_authorized="FALSE"))
assert len(chall)==6
addcsv("R39_6_FOCUS_ROOM_CONDITIONAL_NEUTRAL_OWNER_ALTERNATIVES_UNSCORED_NOT_FORMAL_R017.csv",chall)

# Source-calibrated two-dimensional tile grid test. For each of W1/W2/W3,
# compare long/short horizontal orientation, two illustrative joint widths
# and two edge balances. This is new candidate-specific work, NOT R38's
# historical full-wall-area or niche-aperture study.
grid=[];trim=[]
for room in FOCUS:
  for option in V[room]["options"]:
    for wall in ("W1","W2","W3"):
      sw=W[room,wall];wid=float(sw["source_width_in_UNVERIFIED"]);height=float(sw["source_tiled_height_in_UNVERIFIED"])
      for orient,d in (("LONG_TILE_AXIS_HORIZONTAL",option["size"][0]),("SHORT_TILE_AXIS_HORIZONTAL",option["size"][1])):
        for joint in (.125,.1875):
          nmax=max(0,math.floor((wid-joint)/(d+joint)))
          for center_n in sorted({nmax,max(0,nmax-1)}):
            edge=(wid-center_n*d-(center_n+1)*joint)/2.
            assert edge>=-0.00001,(room,wall,option["code"],center_n,edge)
            flag="N_A_SHORT_TILE_AXIS_UNDER_3IN" if d<3 else "PASS_ILLUSTRATIVE" if 3<=edge<=d else "FAIL_ILLUSTRATIVE_FOCAL_CUT"
            grid.append(dict(room=room,owner_neutral_conditional_option=option["code"],
              source_wall=wall,source_width_in_DRAWING_UNVERIFIED=F(wid),
              source_height_in_DRAWING_UNVERIFIED=F(height),tile_exact_display=option["maker"],
              tile_nominal_horizontal_axis_in=F(d),maker_nominal_body_mm=F(option["nom_mm"]),
              hypothetical_grout_joint_in=F(joint),orientation=orient,
              nominal_center_full_tiles=center_n,
              theoretical_left_cut_in=F(edge),theoretical_right_cut_in=F(edge),
              project_3in_focal_piece_check=flag,
              actual_tile_caliber_face_mm="UNKNOWN",maker_approved_joint_and_bond="UNKNOWN",
              actual_W1_W2_W3_corner_glazing_valves_niche_centers="UNKNOWN",
              physical_1to1_mockup_completed="FALSE",
              original_raw_numeric_LEVEL_lab="MISSING",
              independent_POINT_PAN_lab="MISSING_IF_WALKIN",
              owner_selection_approved="FALSE",purchase_authorized="FALSE"))
      # Trade/field finish boundaries: one exposed vertical return vs two;
      # no inventing exact counts; ceiling and niche edge not included.
      for nvertical in (1,2):
        trim.append(dict(room=room,owner_neutral_option=option["code"],wall=wall,
          hypothetical_exposed_VERTICAL_RETURN_count=nvertical,
          drawing_source_tiled_height_in_UNVERIFIED=F(height),
          hypothetical_vertical_finish_profile_length_LF=F(nvertical*height/12),
          actual_glazing_window_tub_wall_ceiling_perimeter_slope_service_termination_LF="",
          actual_factory_exact_profile_depth_matches_finished_tile_and_mortar="UNKNOWN",
          source_shower_OR_TUB_movement_joint_perimeter_treatment="UNVERIFIED",
          substrate_approved_to_movement_sealant_system="FALSE",
          actual_site_measured_edge_count="FALSE",
          actual_supplier_current_trim_cost_and_GC_labor="",
          owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(grid)>=70 and len(trim)==36,(len(grid),len(trim))
addcsv("R39_72_PLUS_SIX_NEUTRAL_OPTION_THREE_WALL_BALANCED_TILE_GRID_JOINT_FOCAL_CUTS.csv",grid)
addcsv("R39_36_CONDITIONAL_EXPOSED_WET_WALL_VERTICAL_EDGE_PROFILE_AND_MOVEMENT_LF.csv",trim)

# Niche field deduction and actual isolated returns are shown in NEW physical
# installation choices: not merely R38 "field - 1 aperture"; two independent
# pitched sill and profile/trim assemblies including manufacturer permission.
niches=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for aperture_w in (12.,16.):
   for depth in (3.,4.):
    h=12.
    opening=aperture_w*h/144
    back=opening;sides=2*h*depth/144;top=aperture_w*depth/144;sill=top
    edge=2*(aperture_w+h)/12
    # An indicative minimum positive drainage fall in sill; NOT code spec.
    fall=depth*0.02
    niches.append(dict(room=room,physical_copy=copy,
      hypothetical_existing_niche_aperture_width_in=F(aperture_w),
      hypothetical_existing_niche_aperture_height_in=F(h),
      hypothetical_recess_depth_in=F(depth),
      subtract_original_ONE_wall_FIELD_aperture_NET_SF=F(opening),
      independently_tiled_niche_BACK_NET_SF=F(back),
      independently_tiled_two_SIDE_returns_NET_SF=F(sides),
      independently_tiled_TOP_NET_SF=F(top),
      independently_tiled_SILL_NET_SF=F(sill),
      total_independent_niche_tiled_faces_NET_SF=F(back+sides+top+sill),
      hypothetical_full_four_side_trim_or_movement_perimeter_LF=F(edge),
      hypothetical_positive_sill_2pct_fall_in_NOT_CODE_APPROVAL=F(fall),
      original_wall_vs_accent_NICHE_two_SOURCE_rows_not_combined="TRUE",
      original_WET_WALL_maker_gate=V[room]["wall_issue"],
      original_WET_NICHE_maker_gate=V[room]["niche"],
      niche_corner_WRAPPED_WP_factory_membrane_inside_outside_lap="UNKNOWN",
      actual_1529_niche_count_wall_valve_pipe_sill_glass_location="",
      actual_maker_SILL_pieces_absorption_thickness_caliber_grout="",
      actual_1to1_waterfall_and_penetration_mockup="FALSE",
      actual_original_paid_stock_and_extra_return_labor_credit="",
      owner_approved="FALSE",purchasing_authorized="FALSE"))
assert len(niches)==24
addcsv("R39_24_WET_NICHE_FOUR_PLANE_SECTIONS_RETURN_SILL_POSITIVE_FALL_AND_NO_DOUBLE_NET.csv",niches)

# Physical finish plane tolerances are explicitly partial; waterproof
# system thickness is hypothetical, tile relief/per-product and mortar
# actual compressed build-up remain subject to manufacturer approval.
stacks=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for item in V[room]["options"]:
   for mortar,mem in ((2.,.5),(3.,1.),(4.,1.5)):
    tile=item["nom_mm"]
    # backer12.7mm is an illustrative material only. Real waterproof
    # assembly can use another approved substrate entirely.
    total=tile+mortar+mem+12.7
    original=V[room]["old_nom_mm"]
    delta=(tile-original) if original is not None else None
    stacks.append(dict(room=room,physical_copy=copy,conditional_item=item["code"],
      selected_original_wet_wall_product=V[room]["old_tile"],
      candidate_product=item["maker"],
      original_NOMINAL_body_mm=F(original) if original is not None else "UNKNOWN_RELIEF_HIGH_POINT",
      candidate_NOMINAL_body_mm=F(tile),
      nominal_delta_body_mm=F(delta) if delta is not None else "UNKNOWN",
      hypothetical_compressed_set_bed_mm=F(mortar),
      hypothetical_waterproof_MBR_THICKNESS_mm=F(mem),
      hypothetical_BACKER_board_mm=F(12.7),
      illustrative_partial_STUD_to_tiled_face_stack_mm=F(total),
      actual_maker_approved_membrane_mortar_substrate_AND_flange="UNKNOWN",
      actual_tile_RELIEF_high_face_tolerance_caliber_lippage="UNKNOWN",
      real_wall_rough_escutcheon_gasket_depth_and_valve_SERVICE="UNKNOWN",
      actual_niche_SILL_trim_leg_vs_finished_tile_thickness="UNKNOWN",
      actual_1529_WALL_vs_glass_outside_corner_FINISHED_plane="",
      no_using_mortar_to_correct_unknown_factory_tolerance="TRUE",
      owner_approved="FALSE",manufacturer_shop_approved="FALSE",
      physical_1to1_accepted="FALSE",purchase_authorized="FALSE"))
assert len(stacks)==36
addcsv("R39_36_MAKER_NOMINAL_BODY_MEMBRANE_MORTAR_PARTIAL_FINISH_PLANES_AND_TRANSITIONS.csv",stacks)

# One physical wet-bath maker-specific waterproof assembly per room / branch,
# with true selected fixture and exact signed trade hold.
assemblies=[]
for room in FOCUS:
 programs=("WALKIN_SQUARE_POINT_4_PLANE",) if room=="PH-BATH4" else ("OWNER_TUB_BRANCH_NO_SHOWER_PAN","OWNER_WALKIN_4IN_SQUARE_POINT_4_PLANE")
 for copy in G[room]["revit_room_numbers"]:
  for program in programs:
   for assembly in ("WP01_WALL_BASE_CURB_OR_TUB_FLANGE_TRANSITION",
                    "WP02_NICHE_SILL_RETURNS_WATERPROOF_CONTINUITY",
                    "WP03_VALVE_GLASS_JAMB_EXTERNAL_EDGE_AND_MOVEMENT",
                    "WP04_LEVEL_VS_SLOPED_POINT_PAN_AND_THRESHOLD"):
    pan="N_A_TUB_NOT_TILED_SHOWER_PAN" if "TUB" in program else "SEPARATE_FOUR_PLANE_POINT_PAN_NO_LEVEL_FLOOR_TRANSFER"
    drain=("BT062415-BNX Brizo Black Onyx 4in square POINT"
            if room!="PH-BATH3" else "DT062412 Delta Chrome 4in square POINT") if "TUB" not in program else "N_A_TUB_OWNER_UNSELECTED_TUB_WASTE_OVERFLOW"
    assemblies.append(dict(room=room,physical_copy=copy,conditional_program=program,detail=assembly,
       existing_owner_program=V[room]["decision"],actual_selected_fixture_source=V[room]["fixtures"],
       conditional_actual_shower_drain_or_TUB_waste=drain,independent_shower_PAN_role=pan,
       original_WALL_WET_manufacturer_permission=V[room]["wall_issue"],
       original_NICHE_WET_manufacturer_permission=V[room]["niche"],
       factory_selected_drain_rough_bonding_flange_WP_system="UNCONFIRMED_NOT_GENERIC_COMPLIANCE",
       source_shower_plumb_in_vertical_XY_and_slope_polygon="DRAWING_PROVISIONAL_ONLY",
       actual_tub_flange_clip_backer_tape_waste_head_if_TUB="UNKNOWN" if "TUB" in program else "N_A_WALKIN",
       actual_1529_drain_spot_pan_heights_angle_waterproof_lap="UNKNOWN" if "TUB" not in program else "N_A_TUB",
       actual_factory_approved_membrane_curbs_sealing_escutcheon="UNKNOWN",
       actual_tiled_wall_corner_factory_movement_sealant_backing="UNKNOWN",
       actual_1529_floor_wall_rough_glass_backing_niche_coords="",
       original_raw_wet_LEVEL_DCOF="MISSING",
       original_raw_numeric_POINT_PAN_DCOF=pan if "TUB" in program else "MISSING_DISTINCT_SMALL_FORMAT_SLOPED_PAN",
       signed_test_board_1to1_mockup_and_flood_when_required="FALSE",
       original_OWNER_branch_decision_approved="FALSE",
       architect_plumber_WP_installer_GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(assemblies)==40,len(assemblies)
addcsv("R39_40_SIX_UNIT_TUB_OR_POINT_PAN_WALL_NICHE_GLASS_VALVE_CURB_WP_CONSTRUCTION_HOLD_DETAILS.csv",assemblies)

# Quantitative conditional PAN slope/threshold: 1/4in/ft only an explicitly
# chosen engineering sensitivity, NOT asserted code approval or real slope.
# Actual corner lengths depend on drain XY and any curbless trench; nonuniform
# heights at four wall edges and tile format require certified shop sections.
point=[]
for room in FOCUS:
 p=G[room]["shower_or_tub_footprint"]
 assert p is not None
 wide=float(p["width"]["value"])*12
 deep=float(p["depth"]["value"])*12
 for copy in G[room]["revit_room_numbers"]:
  for program in (("OWNER_TUB_NO_SHOWER_PAN","OWNER_WALKIN_POINT_PAN") if B(room) else ("SELECTED_WALKIN_POINT_PAN",)):
   for pos in ("HYPOTHETICAL_CENTER_DRAIN","HYPOTHETICAL_BACK_1_3_DEPTH_DRAIN"):
    pan_active=("TUB" not in program)
    if pos=="HYPOTHETICAL_CENTER_DRAIN":
     run=max(wide/2.,deep/2.)/12.
    else:
     # farthest horizontal run dominates; conceptual and not every actual plane
     run=max(wide/2.,deep*2./3.)/12.
    fall=.25*run if pan_active else 0
    point.append(dict(room=room,physical_copy=copy,conditional_owner_program=program,
      actual_selected_POINT_for_WALKIN_only=("DT062412 Chrome Delta" if room=="PH-BATH3" else "BT062415-BNX Brizo Black Onyx"),
      source_provisional_footprint_width_in_NOT_CERTIFIED=F(wide),
      source_provisional_footprint_depth_in_NOT_CERTIFIED=F(deep),
      hypothetical_POINT_drain_position=pos,
      hypothetical_longest_planar_axis_run_ft_NOT_TRUE_CORNERS=F(run),
      hypothetical_one_quarter_in_per_foot_vertical_FALL_in=F(fall),
      conditional_point_pan_NET_source_rectangle_SF=F(wide*deep/144) if pan_active else "N_A_TUB",
      separate_shower_PAN_vs_bath_LEVEL= "SEPARATE_FOUR_PLANE_PAN_ONLY_IF_WALKIN" if pan_active else "N_A_TUB",
      original_quote_includes_PAN_branch="UNKNOWN_A_B_NOT_PROVEN",
      actual_1529_drain_flange_XY_elevation_and_vessel_waste="",
      actual_code_system_shower_slope_acceptance="FALSE",
      original_PAN_TILE_SKU_raw_exact_numeric_wet_DCOF="MISSING" if pan_active else "N_A_TUB",
      original_LEVEL_TILE_SKU_raw_exact_numeric_wet_DCOF="MISSING",
      actual_sloped_tiling_format_and_bond_maker_signed="FALSE",
      owner_TUB_vs_WALKIN_selection_approved="FALSE",
      waterproof_installer_GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(point)==20
addcsv("R39_20_PROGRAM_BRANCH_FOUR_PLANE_POINT_PAN_DRAIN_HYPOTHETICAL_SLOPE_THRESHOLD_SYSTEM.csv",point)

# 6 actual units x 3 owner tiers, all architect/GC alternatives conditional.
tiers=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for tier in ("GOOD","BETTER","BEST"):
   if tier=="GOOD":
    desc="Retain original aesthetic as documentation-only comparison; no wet installation until exact original item-specific permission, separate original wet tests and system approved"
    material=V[room]["old_tile"]
    grade="CURRENT_ORIGINAL_APPLICATION_NOT_VERIFIED_SO_BLOCKED"
   elif tier=="BETTER":
    item=V[room]["options"][0]
    material=item["maker"]
    desc=item["design"]+"; actual shared corner/niche section, true selected fixtures, exact same-lot factory item and real installed GC quotation prerequisite"
    grade=item["state"]
   else:
    item=V[room]["options"][1]
    material=item["maker"]
    desc=item["design"]+"; premium is workmanship and 1:1 color/cuts/waterproof/movement validation, NOT an invented increased sale premium"
    grade=item["state"]
   tiers.append(dict(room=room,physical_copy=copy,owner_tier=tier,
      chosen_for_actual_site="FALSE",illustrative_actual_tile_system=material,
      conditional_source_gate=grade,design_and_build_scope=desc,
      original_plumbing_and_program=V[room]["fixtures"]+"; "+V[room]["decision"],
      original_WET_NICHE_identity_separate=V[room]["niche"],
      design_quality_value="Old Town premium cleanable wet wall, controlled contrast and 1to1 mockup, no measured buyer premium",
      real_maker_exact_WALL_NICHE_permission_and_rough_WP_lap="UNKNOWN" if tier=="GOOD" else "CONDITIONAL_ITEM_WET_WALL_ONLY_WRITTEN_INSTALL_SYSTEM_MISSING",
      verified_1529_walls_and_actual_niche_location="FALSE",
      original_raw_numeric_LEVEL_lab="MISSING",
      independent_POINT_PAN_raw_lab="MISSING_IF_WALKIN",
      current_chicago_material_full_bom_and_installed_bid_USD="",
      owner_cap_and_full_budget_spend_accepted="FALSE",
      owner_architect_plumber_WP_tile_supplier_GC_signed="FALSE",
      original_four_SPECIALISTS_reviewed="FALSE",weighted_score="NULL",
      purchase_authorized="FALSE"))
assert len(tiers)==18
addcsv("R39_18_SIX_PHYSICAL_ROOM_GOOD_BETTER_BEST_OWNER_ARCHITECT_GC_BUYER_UNSELECTED.csv",tiers)

# Three source wet-wall and accent rows per focus room. Reconstruct original
# contract once, never claim wall+niche totals are new payable scope.
orig_focus=[];historic_total=Decimal("0")
for room in FOCUS:
 for surface in ("wall","floor","accent"):
  x=OLD[room,surface]
  historic_total+=Decimal(x["historic_usd_two_copies"])
  orig_focus.append(dict(room=room,source_original_row_ID=x["source_row_id"],
    source_surface=surface,original_two_unit_gross_SF=F(float(x["source_gross_sf_one_copy_waste_15pct_once"])*2),
    original_one_copy_GROSS_SF_includes15pct=x["source_gross_sf_one_copy_waste_15pct_once"],
    original_two_copy_material_ONLY_total_USD=x["historic_usd_two_copies"],
    original_blended_historic_material_ONLY_rate_USD_per_GROSS_SF=F(Decimal(x["historic_usd_two_copies"])/(Decimal(x["source_gross_sf_one_copy_waste_15pct_once"])*2)),
    must_NOT_add15percent_to_old_gross="TRUE",
    original_PAID_inventory_credit_or_room_net_wall_verified="FALSE",
    current_alternative_material_is_exact_same_factory_product="FALSE",
    source_program=V[room]["decision"],
    actual_1529_signed_net_and_existing_niche_aperture="",
    current_maker_same_SKU_color_finish_lot_usable_case="",
    current_installed_quote_supplier_offer_or_actual_CO="",
    owner_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(orig_focus)==9
assert historic_total==Decimal("6483.08"),historic_total
addcsv("R39_9_EXACT_THREE_WET_BATH_HISTORIC_WALL_LEVEL_NICHE_SOURCE_ROWS_COST_INCLUSION.csv",orig_focus)

# Distinguish original rates from genuinely applicable alternative reference
# rates. Only PH-BATH3 Sandstone new field may refer to old niche item rate,
# and only with authentic source exact product/lot verification.
rates=[];case=[]
for room in FOCUS:
 for item in V[room]["options"]:
  gross=float(OLD[room,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])
  oldrate=float(Decimal(OLD[room,"wall"]["historic_usd_two_copies"])/(2*Decimal(OLD[room,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])))
  source_historical_same_factory_reference=(item["code"]=="P3-B")
  candidate_reference=float(Decimal(OLD["PH-BATH3","accent"]["historic_usd_two_copies"])/(2*Decimal(OLD["PH-BATH3","accent"]["source_gross_sf_one_copy_waste_15pct_once"]))) if source_historical_same_factory_reference else None
  rates.append(dict(room=room,neutral_unscored_option=item["code"],
    old_SOURCE_WALL_gross_per_copy_15pct_IN_PAST=F(gross),
    old_original_two_copy_WALL_material_ONLY_USD=OLD[room,"wall"]["historic_usd_two_copies"],
    old_original_blended_material_only_rate_USD_gross=F(oldrate),
    candidate_different_or_same_maker_identity=item["maker"],
    source_PRIOR_niche_rate_if_SAME_Sandstone_item_USD_per_SF=F(candidate_reference) if candidate_reference is not None else "N_A_DIFFERENT_PRODUCT",
    hypothetical_candidate_wall_reference_cost_at_historic_niche_rate_two_copies_USD=C(2*gross*candidate_reference) if candidate_reference is not None else "UNKNOWN_NOT_QUOTED",
    current_material_SKU_color_finish_LOT_case_price="UNKNOWN",
    current_rough_membrane_edges_and_GC_installed_labor_quote="UNKNOWN",
    old_paid_material_returnable_invoice_credit="UNKNOWN",
    new_actual_OWNER_changed_wall_NET_and_WASTE_allowed="UNKNOWN",
    original_wall_PLUS_NICHE_has_DISTINCT_quote_lines="TRUE",
    original_15pct_IN_GROSS_DO_NOT_REAPPLY="TRUE",
    current_chicago_offer_ETA_freight_and_tax_verified="FALSE",
    actual_change_order_signed="FALSE",material_PO_released="FALSE"))
  for fictional_box in (6.,8.,12.):
    separately=2*math.ceil(gross/fictional_box)
    pooled=math.ceil(2*gross/fictional_box)
    case.append(dict(room=room,conditional_alternative=item["code"],candidate_same_factory_item=item["maker"],
      original_old_WALL_gross_per_physical_copy_SF_15pct_once=F(gross),
      fictional_FUTURE_case_usable_coverage_SF_NOT_REAL=F(fictional_box),
      original_wall_two_copies_rounded_SEPARATELY_cases=separately,
      hypothetical_two_copies_SAME_LOT_CASE_POOLING_ceiling=pooled,
      hypothetical_difference_case_only_not_savings=separately-pooled,
      same_current_FACTORY_SKU_color_finish_caliber_LOT_verified="FALSE",
      same_material_with_original_SANSTONE_NICHE_same_BAG_tag_maker_proven="FALSE",
      original_wall_and_niche_combined_quote_RECONCILED="FALSE",
      final_actual_MEASURED_NET_case_breakage="UNKNOWN",
      owner_approved="FALSE",current_supply_offer_verified="FALSE",
      purchase_authorized="FALSE"))
assert len(rates)==6 and len(case)==18
addcsv("R39_6_FACTORY_ORIGINAL_VS_CONDITIONAL_WET_WALL_MATERIAL_ONLY_RATE_AND_GC_CHANGEORDER.csv",rates)
addcsv("R39_18_THEORETICAL_TWO_COPY_WET_WALL_TRUE_SKU_LOT_CASE_CEIL_NOT_ORDER.csv",case)

# Original source per-item manufacturer evidence classification: exact old
# color wet permission is not transferred from adjacent collection.
permissions=[]
for room in FOCUS:
 original_cred=("MISSING_EXACT_INDIVIDUAL_WET_LISTING"
                if room in ("PH-BATH3","PH-BATH4") else "ARCHIVED_INDIVIDUAL_WET_LISTING_PRIOR_PASS_CURRENT_LIVE_RECHECK")
 permissions.append(dict(room=room,surface="ORIGINAL_WET_WALL",
   exact_color_finish_product=V[room]["old_tile"],maker_evidence_URL=MAKER["OPAL"] if room=="PH-BATH3" else MAKER["RIBBED"] if room=="PH-BATH4" else MAKER["EMERALD"],
   evidence_classification=original_cred,permission_to_install="HOLD_NO",
   proposed_current_owner_substitution="NONE",actual_maker_install_and_WP_detail="UNKNOWN",
   exact_numeric_original_wet_DCOF="N_A_WALL_ONLY",purchase_authorized="FALSE"))
 permissions.append(dict(room=room,surface="ORIGINAL_WET_NICHE",
   exact_color_finish_product=V[room]["niche"],maker_evidence_URL=MAKER["CAVIAR"] if room=="PH-BATH4" else MAKER["SANDSTONE"],
   evidence_classification="ORIGINAL_CAVIAR_INDIVIDUAL_NICHE_WET_NOT_VERIFIED" if room=="PH-BATH4" else "ARCHIVED_INDIVIDUAL_SANDSTONE_WET_LISTED_REVERIFY_INSTALL_SYSTEM",
   permission_to_install="HOLD_NO",proposed_current_owner_substitution="NONE",
   actual_maker_install_and_WP_detail="UNKNOWN",exact_numeric_original_wet_DCOF="N_A_VERTICAL_NICHE",purchase_authorized="FALSE"))
 for opt in V[room]["options"]:
  permissions.append(dict(room=room,surface="CONDITIONAL_WET_WALL_OPTION",
    exact_color_finish_product=opt["maker"],maker_evidence_URL=opt["url"],
    evidence_classification=opt["state"],permission_to_install="HOLD_PENDING_OWNER_WP_MOCKUP_AND_1529_SHOP",
    proposed_current_owner_substitution=opt["code"],
    actual_maker_install_and_WP_detail="UNKNOWN",
    exact_numeric_original_wet_DCOF="N_A_WALL_ONLY",purchase_authorized="FALSE"))
 permissions.append(dict(room=room,surface="BATH_LEVEL_WET_FLOOR",
   exact_color_finish_product="ORIGINAL_ROOM_SOURCE_FLOOR_DISTINCT_FROM_WALL",
   maker_evidence_URL="",evidence_classification="EXACT_ORIGINAL_ITEM_RAW_NUMERIC_WET_DCOF_MISSING",
   permission_to_install="HOLD_NO",proposed_current_owner_substitution="NONE",
   actual_maker_install_and_WP_detail="ACTUAL_1529_SUBSTRATE_SLOPE_UNKNOWN",
   exact_numeric_original_wet_DCOF="MISSING",purchase_authorized="FALSE"))
 permissions.append(dict(room=room,surface="CONDITIONAL_POINT_PAN_IF_WALKIN",
   exact_color_finish_product="SEPARATE_SMALL_FORMAT_POINT_PAN_MAKER_ITEM_UNSELECTED",
   maker_evidence_URL="",evidence_classification="RAW_NUMERIC_INDEPENDENT_POINT_PAN_MISSING",
   permission_to_install="HOLD_NO",proposed_current_owner_substitution="NONE",
   actual_maker_install_and_WP_detail="N_A_ONLY_IF_OWNER_TUB" if B(room) else "FOUR_PLANE_SELECTED_WALKIN_REQUIRED",
   exact_numeric_original_wet_DCOF="MISSING_IF_WALKIN",purchase_authorized="FALSE"))
assert len(permissions)==18
addcsv("R39_18_INDIVIDUAL_ORIGINAL_VS_OPTION_WET_WALL_NICHE_LEVEL_POINT_PAN_FACTORY_EVIDENCE.csv",permissions)

samples=[]
for room in FOCUS:
 for copy in G[room]["revit_room_numbers"]:
  for view in ("W1_W2_W3_ONE_CONTINUOUS_LEVEL_WET_WALL_SAMPLE",
               "TRUE_FOUR_SURFACE_NICHE_SILL_AND_GROUT_OR_EDGE_CORNER",
               "SELECTED_VALVE_GLASS_CURB_OR_TUB_FLANGE_PAN_THRESHOLD_SECTION"):
   samples.append(dict(room=room,physical_copy=copy,conditional_design_camera_or_1to1=view,
     original_tile_and_selected_plumbing_preserved=V[room]["old_tile"]+"; "+V[room]["fixtures"],
     conditional_owner_program=V[room]["decision"],
     exact_maker_wet_wall_and_niche_permission="NOT_ALL_CLEARED",
     original_real_NATIVE_1529_W1W2W3_glass_valve_niche_geometry="UNVERIFIED",
     required_tile_genuine_color_gloss_grout_trim_sill_fall="ONE_PHYSICAL_REAL_SIZE_AFTER_OWNER_SELECTION",
     sample_factory_backer_membrane_rough_and_actual_finish_face="UNKNOWN",
     light="neutral diffuse + warm artificial; camera not fabricated",
     prior_original_drawings_are_only_PROVISIONAL="TRUE",
     image_or_render_created="FALSE",physical_sample_created="FALSE",
     architect_WP_tile_GC_approved="FALSE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(samples)==18
addcsv("R39_18_SIX_ACTUAL_PHYSICAL_WET_BATH_THREE_CAMERAS_AND_1TO1_TRADES_UNPRODUCED.csv",samples)

# Room-specific old 27 material line exact source-to-current supplier/GC BOM
# with no false pooling of visually similar tiles or reassignment of WC.
normalized=[]
for x in old:
 room=x["room"];focus=room in FOCUS
 normalized.append(dict(room=room,original_material_SOURCE_row_ID=x["source_row_id"],
  original_surface=x["source_surface"],original_GROSS_SF_one_copy_15pct_once=x["source_gross_sf_one_copy_waste_15pct_once"],
  original_two_copy_material_ONLY_USD=x["historic_usd_two_copies"],
  no_order_original_unsupported_Primary_niche=x["historic_niche_excluded_no_scope"],
  relevant_R39_exact_WET_WALL_NICHE_maker_HOLD=V[room]["wall_issue"]+" / "+V[room]["niche"] if focus else "PRESERVE_ORIGINAL_PREDECESSOR",
  current_true_1529_NET_surface_field_niche_back_returns_sill_or_pan="",
  factory_exact_orderable_SKU_color_finish_caliber_WET_app="",
  same_lot_two_copy_factory_verified="FALSE",actual_case_usable_SF="",
  actual_Chicago_stock_price_freight_eta_and_tax="",
  original_PAID_RECEIVED_stock_real_returnable_credit="",
  actual_rough_waterproof_curbs_glass_edges_install_labor_FULL_bid="",
  original_15pct_already_once="TRUE",buyer_substitution_signed="FALSE",
  wall_maker_wet_LISTING_is_NOT_floor_DCOF="TRUE",
  architect_signed="FALSE",supplier_signed="FALSE",GC_signed="FALSE",purchase_authorized="FALSE"))
assert len(normalized)==27
addcsv("R39_27_HISTORIC_SOURCE_TO_CURRENT_SEPARATE_WET_APPLICATION_SKU_LOT_PO_GC_RECEIVING.csv",normalized)

# Material groups: genuine same exact item vs same-name unverified,
# estimate old material included; user can later request quote on rows.
groups=[
 ("EXISTING_ORIGINAL_PH3_TX3_TONES_SANDSTONE_NICHE","PH-BATH3,PH-BATH2,TX-BATH2,TX-BATH3","Tones Sandstone 2x20 Glossy","POTENTIAL_ONLY_IF_SAME_FACTORY_ORDER_CODE_COLOR_FINISH_LOT","Historically 51.64 gross and $358.92 across eight source physical niche copies already included"),
 ("CONDITIONAL_PH3_SANDSTONE_WET_WALL_NICHE","PH-BATH3","Tones Sandstone 2x20 Glossy","POTENTIAL_ONLY_AFTER_OWNER_WALL_SELECTION_AND_REAL_WET_APP","Potential PH3 same original Sandstone niche color, current identical actual carton/lot unresolved"),
 ("CONDITIONAL_PH4_SOHO_IVORY_SAME_WALL_NICHE","PH-BATH4","Soho Ivory 2x10 Glossy","POTENTIAL_ONLY_IF_OWNER_SIGNS_SAME_ITEM_FOR_WALL_AND_NICHE","No mixing with original Clara Caviar 2x8 or Ribbed Bone 24x48"),
 ("CONDITIONAL_TX3_SOHO_EMERALD","TX-BATH3","Soho Emerald 2x10 Glossy","NOT_INTERCHANGEABLE_NOHO_EMERALD_OR_TONES_EMERALD","Color name Emerald does not make formats/finish/surface exactly same"),
 ("CONDITIONAL_TX3_NOHO_EMERALD","TX-BATH3","Noho Emerald 2x10 Matte","NOT_INTERCHANGEABLE_SOHO_EMERALD_GLOSSY","Distinct matte maker product and shade lot"),
 ("CONDITIONAL_PH3_SOHO_BLUE","PH-BATH3","Soho Blue 2x10 Glossy","NOT_INTERCHANGEABLE_SANDSTONE_OR_OTHER_SOHO_COLOR","Color-specific Wet Areas and current factory exact SKU required"),
 ("ORIGINAL_PH4_TX4_CLARA_CAVIAR_HISTORICAL","PH-BATH4,TX-BATH4","Clara Tierra Madre Caviar 2x8","HISTORIC_ONLY_WET_NICHE_UNVERIFIED_NO_NEW_ORDER","34.52 gross and $1163.32 across two-room x2 original niche line INCLUDED"),
]
pool=[]
for identity,rooms_use,sku,rule,explain in groups:
 pool.append(dict(pool_id=identity,scope_rooms=rooms_use,source_or_conditional_item=sku,
   strict_factory_SKU_color_finish_CALIBER_lot_rule=rule,
   historical_quote_and_application_scope=explain,
   current_real_factory_lot_same_packaging_usable_SF="UNKNOWN",
   current_vendor_CHICAGO_stock_installed_offer="UNKNOWN",
   physical_OFFCUT_reuse_and_measured_cut_direction_saw_kerf="UNKNOWN",
   eligible_approved_actual_SameSKU_wet_wall_and_niche="FALSE",
   shared_PO_or_material_RESERVATION="FALSE"))
assert len(pool)==7
addcsv("R39_7_CROSS_ROOM_ORIGINAL_VS_CONDITIONAL_FACTORY_COLOR_FINISH_LOT_AND_OFFCUT_NONPOOLING.csv",pool)

def program(room):
 if room in V:return V[room]["fixtures"]+"; "+V[room]["decision"]
 if room in ("PH-PRIMARY","TX-PRIMARY"):return "Selected Brizo Black Onyx 48in LINEAR BT0734816-BNX + separately required BR73480 rough; no Primary niches; source A/B shower PAN quote unresolved"
 if room in ("PH-WC","TX-WC"):return "Inherit original Primary source tile floor ONCE, no independent order; TX203A unplaced"
 if room=="PH-BATH4":return V[room]["fixtures"]
 if room in ("PH-BATH2","TX-BATH2","TX-BATH4"):return "Original selected Duravit bathtub no tiled PAN; Hansgrohe PH2 Matte White / TX2 Chrome / TX4 Matte White; fixture/valve rough conflicts remain"
 if room=="PH-POWDER":return "Brizo FLW T65722LF-GL Luxe Gold WALL + R65700 rough, RP72414GL; wood floor, R37 relief/gasket shop"
 if room=="TX-POWDER":return "AXOR One 48140991 cross-handle or Metropol 32526141 single-lever competing WALL TRIMS, 13622181 Metropol rough only; wood floor"
 if room=="TX-POWDER2":return "Tecturis E 73072341 Brushed Black Chrome DECK, basin UNSELECTED, no counter bore; wood floor"
 raise KeyError(room)
def wet(room):
 if room in ("PH-POWDER","TX-POWDER","TX-POWDER2"):return ("N_A_DRY_WALL_SINK_SPLASH_ONLY","N_A_WOOD_FLOOR","N_A")
 if room in ("PH-WC","TX-WC"):return ("N_A","PARENT_PRIMARY_WC_ANTISLIP_EXACT_RAW_NUMERIC_MISSING","N_A")
 if room in ("PH-BATH2","TX-BATH2","TX-BATH4"):return ("SEPARATE_EXACT_WET_WALL_NICHE_MAKER","MISSING_EXACT_LEVEL_RAW_NUMERIC","N_A_DURAVIT_TUB")
 if room in ("PH-PRIMARY","TX-PRIMARY"):return ("INDIVIDUAL_WET_WALL_NO_NICHES","MISSING_EXACT_LEVEL_RAW_NUMERIC","MISSING_EXACT_LINEAR_PAN_RAW_NUMERIC")
 if room=="PH-BATH4":return ("RIBBED_WET_WALL_AND_CAVIAR_WET_NICHE_UNVERIFIED","MISSING_EXACT_LEVEL_RAW_NUMERIC","MISSING_EXACT_SQUARE_POINT_FOUR_PLANE_PAN_RAW_NUMERIC")
 return ("PH3_OPAL_WALL_NOT_AUTHORIZED" if room=="PH-BATH3" else "TX3_EMERALD_PRIOR_WET_LISTING_NEEDS_RECONFIRM","MISSING_EXACT_LEVEL_RAW_NUMERIC","MISSING_IF_OWNER_WALKIN_SQUARE_POINT")
status={x["id"]:x for x in ROOMS}
all13=[];trades=[]
TRADES=("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER")
for room in sorted(status):
 s=status[room];wallgate,levelgate,pangate=wet(room)
 amount=sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old if x["room"]==room)
 all13.append(dict(room=room,original_source_physical_copies=2,
  original_board_round=17,current_status_UNCHANGED=s["status"],
  current_champion_UNCHANGED=s.get("champion_id") or "null",
  original_score_UNCHANGED=str(s.get("champion_score")) if s.get("champion_score") is not None else "null",
  original_two_copy_historical_material_ONLY_USD=str(amount),
  original_SELECTED_fixture_program=program(room),
  individual_wet_WALL_NICHE_or_dry_application=wallgate,
  exact_original_RAW_wet_LEVEL_DCOF_role=levelgate,
  separate_LINEAr_or_POINT_PAN_exact_RAW_numeric_wet_DCOF=pangate,
  original_R31_13_LAB_specimen_scope_preserved="TRUE",
  original_R31_50_wall_26_instance_signoff_refs_preserved="TRUE",
  source_27_original_material_and_25_wall_65_trade_rows_preserved="TRUE",
  source_R35_primary_wc_mutually_exclusive_A_B="UNRESOLVED" if room in ("PH-PRIMARY","TX-PRIMARY") else "NOT_R35_FOCUS",
  source_R36_owner_tub_walkin_pan_quote_branch="UNRESOLVED" if B(room) else "NOT_R36_FOCUS",
  source_R37_powder_flat_rough_and_deck="UNRESOLVED" if room in ("PH-POWDER","TX-POWDER","TX-POWDER2") else "NOT_R37_FOCUS",
  R39_wet_original_maker_HOLD=V[room]["wall_issue"] if room in V else "UNCHANGED",
  actual_1529_geometry_OPENINGS_and_correct_native_model="",
  exact_current_factory_SKU_lot_case_chicago_offer_full_GC_INSTALLED_bid="",
  owner_signed="FALSE",architect_signed="FALSE",plumber_signed="FALSE",
  waterproof_trade_signed="FALSE",tile_trade_signed="FALSE",
  supplier_signed="FALSE",GC_signed="FALSE",purchaser_signed="FALSE",
  actual_owner_material_release="FALSE",purchase_authorized="FALSE",
  independent_four_specialists_complete="FALSE",formal_weighted_score="NULL",
  independent_nonpro_reviewer_DONE="FALSE"))
 for step,trade in enumerate(TRADES,1):
  if trade=="OWNER":task="Owner confirm PH3/TX3 TUB/WALKIN program; PH4 walkin unchanged; owner wet wall versus dry zoning palette, optional niche replacement, budget cap and actual 1:1"
  elif trade=="ARCHITECT":task="Certify native TRUE1529 W1W2W3 actual widths, slope/threshold/glass, valve/niche/return/trim coordinates, 3in focal cuts and 1:1 shop"
  elif trade=="PLUMBER":task="Preserve selected Delta Chrome/Brizo BNX square POINT only shower, approve conditional tub waste separately and drain rough WP/valves/escutcheon service"
  elif trade=="WATERPROOFING":task="Independent original WALL/NICHE manufacturer exact permissions, approved selected membrane/curb/tub flange/point drain bonding and niche corner/sill"
  elif trade=="TILE_INSTALLER":task="Original exact LEVEL wet measured numeric vs independent POINT PAN original raw lab; actual small-format 4plane pan, layout, movement, calibrated cuts, flood/1:1"
  elif trade=="SUPPLIER":task="Original paid inventory and same SKU/color/finish/caliber/lot, exact useful cartons, Chicago offer/stock/ETA/freight and no cross-color pooling"
  elif trade=="GC_ESTIMATOR":task="Separate old source 15pct GROSS and 3 wet WALL original material from new bid full installed rewaterproof, corner, glass, trim, demo, paid stock and labor credit"
  else:task="Only after authentic owner and seven trade signatures plus four original independent specialists, numeric wet gate and authorized original Reviewer"
  trades.append(dict(room=room,trade_sequence=step,responsible_trade=trade,source_program=program(room),
   evidence_required_to_RELEASE=task,
   must_classify_dry_WOOD_floor_and_tub_only_PAN_NA=wet(room)[2],
   actual_certified_1529_shop_and_factory_item_wet_application="",
   exact_original_raw_LEVEL_vs_POINT_OR_LINEAR_lab="",
   dated_material_and_installed_GC_bid_credits="",
   actual_trade_signature="",
   original_formal_R017_board_SCORES="NULL",
   owner_approved="FALSE",GC_approved="FALSE",purchaser_release="FALSE"))
assert len(all13)==13 and len(trades)==104
assert sum(Decimal(x["original_two_copy_historical_material_ONLY_USD"]) for x in all13)==Decimal("23572.44")
addcsv("R39_13_ROOM_PROGRAM_INDIVIDUAL_WET_APPLICATION_LEVEL_POINT_LINEAR_PAN_RELEASE_MATRIX.csv",all13)
addcsv("R39_104_EIGHT_TRADE_SOURCE_SITUATED_OWNER_ARCH_PLUMB_WP_TILE_SUPPLIER_GC_PURCHASER_GATES.csv",trades)

# Additive integration of the original physical record IDs and wall witness IDs,
# not copies of their obsolete gates or a replacement for signed R31.
unit=[]
for x in U26:
 room=x["room"];focus=room in FOCUS
 unit.append(dict(room=room,original_physical_COPY_index=x["physical_copy_index"],
  original_R31_source_ROOM_number=x["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"],
  owner_source_selected_program=program(room),
  exact_room_WALL_NICHE_and_LEVEL_POINT_LINEAR_WET_gate="|".join(wet(room)),
  original_R31_26_physical_receipt_immutably_retained="TRUE",
  R39_focus_original_wet_approval_issue=V[room]["wall_issue"] if focus else "UNCHANGED",
  source_WALL_corner_glass_rough_slope_1to1_fullsize_witness="NOT_BUILT" if focus else "PRESERVE_PREVIOUS_REVIEW",
  actual_1529_model_and_wet_WALL_PAN_POLYGONS="",
  actual_niche_wall_count_back_sides_top_sill_penetrations="",
  actual_factory_maker_same_item_SKU_and_approved_WP_system="",
  actual_raw_WET_LEVEL_and_independent_PAN_labs="",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  waterproof_approved="FALSE",installer_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(unit)==26
addcsv("R39_26_ORIGINAL_TWO_COPY_PHYSICAL_INSTANCE_WALL_NICHE_FIXTURE_WP_ACCEPTANCE_INTEGRATION.csv",unit)
walls=[]
for x in W50:
 room=x["room"];focus=room in FOCUS
 walls.append(dict(room=room,physical_copy=x["physical_copy"],
  original_source_wall_reference=x["wall_reference"],
  original_provisional_wall_width_in=x["prior_source_wall_width_in_UNVERIFIED"],
  original_provisional_wall_height_in=x["prior_source_tiled_height_in_UNVERIFIED"],
  original_R31_50_WALL_studies_immutable="TRUE",
  R39_conditional_new_2x10_vs_old_2x20_or_ribbed_module="NEW_72_GRID_AND_WP_SECTIONS" if focus else "NOT_R39_FOCUS",
  original_WALL_NICHE_independent_maker_gate=V[room]["wall_issue"]+"; "+V[room]["niche"] if focus else "PRESERVE_PREVIOUS",
  actual_native_1529_walls_glass_edge_jamb_niche_and_valves="",
  actual_one_aperture_negative_FIELD_and_new_returns_plus_sill_NET="",
  actual_1to1_caliber_joints_focal_width_trim_and_movement="",
  actual_approved_dry_vs_wet_zoning_boundary="",
  exact_numeric_raw_wet_LEVEL_vs_PAN_labs="",
  owner_approved="FALSE",architect_approved="FALSE",
  waterproof_installer_signed="FALSE",purchase_authorized="FALSE"))
assert len(walls)==50
addcsv("R39_50_ORIGINAL_PROVISIONAL_WALL_WITNESS_WET_ACTUAL_MODULE_AND_MEMBRANE_OVERLAY.csv",walls)

for room in FOCUS:
 info=V[room]
 sizes=[float(W[room,w]["source_width_in_UNVERIFIED"]) for w in ("W1","W2","W3")]
 h=float(W[room,"W1"]["source_tiled_height_in_UNVERIFIED"])
 candidates=info["options"]
 doc=f"""
# R39 {room} conditional full-size wet-bath design and contractor shop exhibit

**HOLD: not an owner selection, certified 1529 geometry or waterproof-system approval.** Original 1529 handoff W1 {F(sizes[0])}in, W2 {F(sizes[1])}in, W3 {F(sizes[2])}in, all {F(h)}in tiled high; three-wall undeducted nominal field {F(sum(sizes)*h/144)} SF NET, source original historical WALL {OLD[room,"wall"]["source_gross_sf_one_copy_waste_15pct_once"]} SF GROSS/copy 15% already included once. Original WALL two-copy material-only $ {OLD[room,"wall"]["historic_usd_two_copies"]}, original niche source accent {OLD[room,"accent"]["source_gross_sf_one_copy_waste_15pct_once"]} GROSS/copy separately priced. No actual measured 1529 openings, niche pipe cavities, valve/sills, field deducts or factory lot; neither receipt is a current quote.

**Selected program stays unchanged:** {info["fixtures"]}; {info["decision"]}. Original {info["old_tile"]} wet WALL gate **{info["wall_issue"]}**. Niche gate **{info["niche"]}**. Source original color/finish does not inherit a nearby color's wet listing.

## GOOD / BETTER / BEST design decisions, not formal scored board

GOOD: preserve original visual design as a history/reference plate **only**; wet-wall maker approval absent or item current verification missing, so installation STOP and no PO. BETTER: conditional individual maker-listed [{candidates[0]["maker"]}]({candidates[0]["url"]}), {candidates[0]["size"][0]}x{candidates[0]["size"][1]}in nominal {candidates[0]["nom_mm"]}mm body; {candidates[0]["design"]}. BEST: physically distinct [{candidates[1]["maker"]}]({candidates[1]["url"]}), {candidates[1]["size"][0]}x{candidates[1]["size"][1]}in nominal {candidates[1]["nom_mm"]}mm; {candidates[1]["design"]}. Different color, exact factory SKU/finish/lot, grout module, waterproof detail, mockup and actual owner consent required; no invented buyer premium or current Chicago stock. Original owner selections stay intact until separately signed.

## W1/W2/W3 elevation and trim shop

At each true measured W1/W2/W3 finished face width W, actual calibrated tile face d and maker/installer-approved grout joint j, balanced end cut = (W - N*d - (N+1)*j)/2. R39 compares 1/8in and 3/16in hypothetical joints and two horizontal modules on all three source walls, both long- and short-axis. On long-axis 10/20in tiles, check minimum 3in focal cuts or change N; a 2in short-axis small-format tile is inherently narrower than 3in and is N/A for that large-format focal criterion, not automatically a false wet compliance PASS. Must field locate real valve, niche, jamb, mirror, glazing return and tile high points, and keep bond and movement alignment through W1/W2/W3. Illustrative exposed vertical trim 1 or 2 returns at {F(h/12)} LF each (other ends, ceiling/base and niches separately and NOT presumed exposed).

## Section A: wall and original niche wet membrane

Stud/blocking -> approved backer -> manufacturer-selected tested waterproof membrane, fully sealed lap/inside-outside corners -> maker-approved actual compressed mortar -> calibrated tile high face -> grout plus full movement sealant at dissimilar planes/edges. Partial R39 Z-stack assumes only for calculation 12.7mm board, 0.5/1/1.5mm membrane and 2/3/4mm compressed mortar with nominal tile body. Actual existing backer, factory ribbed high point, rough recess, waterproofing installation and trim/gasket clearance are unverified; no rule permitting a 1mm body difference to be corrected by thicker mortar without factory approval. Niche field aperture is negative ONE wall field only; niche BACK, TWO SIDES, TOP, SILL separately quantified and shop-approved with positive drainage into shower, actual slope, lip, supported edge, piping clearance and full membrane corners. Illustrative 3/4in reveal depths and 12/16in aperture are not site openings or new additional niche orders. Original WALL and NICHE wet application letters remain distinct, with no automatic permission for Caviar or relief Ribbed.

## Section B: actual tub versus selected/conditional four-plane POINT wet floor

For source PH-BATH3 and TX-BATH3, owner TUB or WALKIN is still UNSELECTED. If future owner TUB: obtain actual selected tub/manufacturer flange, tub waste/overflow, actual 1529 rough clearance, board membrane-to-flange termination and seal; **no tiled shower PAN** and shower 4in POINT drain is not a bathtub waste. If future WALKIN, selected conditional Delta Chrome/Brizo Black Onyx 4in SQUARE POINT as source, independent four-plane small-format sloped PAN and true bath LEVEL, compatible selected drain rough, approved membrane bonding, curb/threshold/glass anchorage and body thickness. PH-BATH4 is WALKIN only with fixed Brizo BT062415-BNX 4in square POINT, separate four-plane PAN and LEVEL; not a tub. R39 .25in/ft slope and center/back-third hypothetical drain XY are numeric sensitivity ONLY, not code approval or actual field elevation. Require distinct exact original measured numeric wet DCOF for bath LEVEL and applicable POINT PAN, not brochure targets and not wall tile tests.

## Signed contractor acceptance sequence

OWNER actual program if Bath3 and selected wall/niche finish; ARCHITECT verified native 1529 W1/W2/W3 openings and shop dimensions; PLUMBER actual selected rough/drain/valve or tub flange waste; WATERPROOF subcontractor exact maker-approved connected substrate/membrane/curb/niche corners and penetration system; TILE installer factory-calibrated grout/cuts, independent original raw LEVEL/PAN laboratory item results, movement/sill and full-size 1:1 wet/mockup; SUPPLIER real color/lot/usable carton/Chicago offer and original paid/received inventory; GC revised complete installed labor/membrane/trim/change order net of proved credits; PURCHASER only after all prior authentic signatures and original independent governance. One 1:1 mockup for each actual physical unit includes real fixture, wet wall, niche sides/top/sill, threshold/slope and cleanable grout/movement; no actual samples or images exist. All release flags FALSE.
"""
 addmd(f"R39_{room}_SOURCE_DIMENSIONED_WET_WALL_NICHE_VALVE_CURB_SHOP_AND_OWNER_OPTIONS.md",doc)

addmd("START_HERE_R39_INTEGRATED_THREE_WET_BATH_AND_13ROOM_GC_OWNER_BOOK.md",f"""
# R39 — three wet bathrooms: actionable design and procurement architecture

**New complete, additive R39 owner/architect/GC package.** R37 predecessor SHA {PREDECESSOR["R37_FULL"][1]}; R38 predecessor SHA {PREDECESSOR["R38_PRELIM_SOURCE"][1]} is a **preliminary source-only signed five-file receipt**, not an integrated signed R38 owner book. Prior R35, R36, R30, R33 and original R12-R31 signed work untouched. Actual current native Revit document 1527 cannot certify 1529 wall or floor dimensions. No owner selection, model alteration, current supplier quote, independent Reviewer release, sample or PO.

PH-BATH3: original Tones Opal individual WET wall permission unverified, original Sandstone niche archived wet listed. Two distinct owner-conditional alternatives [{V["PH-BATH3"]["options"][0]["maker"]}]({MAKER["SOHO_BLUE"]}) 2x10 glossy wet listed (different blue material), or archived maker-wet-listed Tones Sandstone 2x20 (warm unified wall/niche, exact current maker item renewal needed). Preserve original Hansgrohe Chrome and conditional Delta DT062412 Chrome square POINT only future WALKIN, owner TUB/WALKIN and basin unselected.

PH-BATH4: WALKIN fixed Brizo Black Onyx BT062415-BNX 4in square POINT, independent four-plane PAN and LEVEL. Original Cortar Bone Ribbed wet WALL exact individual permission absent, original Caviar 2x8 wet NICHE exact approval absent. Two materially different owner-conditional wet wall options: current individually wet-listed [Soho Ivory 2x10 glossy]({MAKER["SOHO_IVORY"]}) as unified wet wall/niche if independently certified, or same actual wet Soho enclosure with Bone Ribbed DRY-only feature outside verified spray boundary—this second is NOT established feasible until a real DRY wall exists, and not owner-approved. Preserve 35vs27 SF and 214.4 old vendor-total disputed not payable.

TX-BATH3: original Tones Emerald 2x20 archived individual wet WALL listing prior PASS but current exact item not retrieved. Individually wet-listed [Soho Emerald 2x10 Glossy]({MAKER["SOHO_EMERALD"]}) and [Noho Emerald 2x10 Matte]({MAKER["NOHO_EMERALD"]}) are distinct factory products, finishes and shade lots, not Tones original or automatically interchangeable. Preserve Black Onyx Brizo conditional BT062415-BNX square POINT only if WALKIN, owner TUB/WALKIN unselected, original Sandstone NICHE separately listed.

Three manufacturer-cited room-specific shop documents advance R38 history source math to original W1/W2/W3 material-dependent tile-grid module cuts, grout, true niche back/sides/top/sill, positive sill fall, substrate/membrane/rough/wet boundary, tub flange versus point-pan threshold and installation acceptance. Six new neutral owner alternative records, independent R39 good/better/best 18 physical options, R39 grid and shop witnesses are NOT frozen private R017 source challengers or scored critiques; do not dispatch incomplete three original specialists or create owner approval.

New quantification: original three-room WALL/FLOOR/NICHE nine material source rows sum {C(historic_total)} material-only for six physical baths, already within original 13-room 23572.44 four-unit tile material budget and original old 15% waste once. Original WALL only PH3 1198.18, PH4 1580.12, TX3 1276.02 across two copies; separately historical already-priced niche. Distinct material old rate versus hypothetical new candidate current price UNKNOWN, old paid material inventory/return credit UNKNOWN. Do not treat modelled niche field opening reduction or new carton-pooling as accepted credit. Different color/finish/format cannot pool; only confirmed same SKU/color/finish/caliber/lot and real usable carton with verified 1529 net may pool. PH3 Sandstone possible overlap existing old Sandstone niche group only if owner approves and real maker lot matches; PH4 Soho Ivory wall+niche conditional; original Caviar and Bone Ribbed never interchangeable; TX3 Soho Gloss and Noho Matte distinct.

Full 13 original room IDs x2, 27 original materials (two excluded unpriced Primary niche references), 25 original provisional walls, 65 trade actions, R31 original 13 exact numeric lab roles/50 wall/26 physical unit witnesses preserved and new 13 room release /104 trade gates. Both Primary selected Brizo 48in BNX LINEAR with separate BR73480 rough/no niches, WC inherited floor once and unresolved R35 original quote A/B; three original Duravit tubs PH2/TX2/TX4 NO tiled PAN and selected Hansgrohe finishes, control-spout issues pending; PH4 WALKIN BNX POINT; PH3/TX3 R36 TUB/WALKIN conditional with separate POINT shower PAN; three powder WOOD floors, selected faucet mounting and TX Powder2 basin UNSELECTED, all wet lab N/A only there and tub-only PAN N/A. Individual exact manufacturer wet WALL and NICHE permissions and exact original numerical measured wet LEVEL vs independent LINEAR/POINT PAN tests remain mandatory, no brochure target substitutions.

Existing Sandstone 358.92, Grey Soft 1116.46, Caviar 1163.32, and powder 2159.30 material-only subgroups already counted (not additive dollars). Market PH 2.8M/TX 2.7M, 14 comps/nine buildings, Old Town primary 2.4–3.2M and Lincoln Park/Gold Coast secondary, no speculative buyer premiums. Revit and Smartsheet strictly read-only. No vendors contacted, emails, purchases, physical mockups, images, contractor bid or signed change orders.

Eight trade sequence owner -> TRUE 1529 architect -> selected plumbing/rough -> waterproof manufacturer support -> installer/independent wet labs -> supplier lot/current source -> GC full installed bid and paid credit -> purchaser only after authentic signoffs. Formal board R017 original four specialists MARKET .30, DESIGN .25, BUILD .25, COST .20, hard gates, each >=3.0 and candidate +0.25 only after independent authentic critiques; original DESIGN9 FAILED missing R014 two reports, non-Pro Reviewer15 FINISHED/nonrevivable. All approvals and procurement FALSE. Entire 13-room program OPEN.
""")

# Preserve exactly original authenticated predecessor receipts; a signed
# source-only R32/R34/R36/R38 MUST NOT be mislabeled integrated completion.
R37=json.loads((BASE/PREDECESSOR["R37_FULL"][0]).read_text(encoding="utf-8"))
LINEAGE=dict(R37["predecessor_signed_file_hashes"])
LINEAGE.update({name:sha for name,(path,sha) in PREDECESSOR.items()})
for formal in ("ROUND014_SUBMISSION","ROUND017_SUBMISSION"):
 p=BASE/"state"/(formal+".json")
 LINEAGE[formal]=hashlib.sha256(p.read_bytes()).hexdigest()
sum_original=Decimal("23572.44")
assert sum_original==sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)
meta=dict(round=39,date_local="2026-11-06",
 project="1529 Wieland 13-room bathroom original plumbing and tile design/GC procurement loop",
 phase="COMPLETE_NEW_ADDITIVE_PH3_PH4_TX3_WET_WALL_WP_TILE_13ROOM_OWNER_ARCH_GC_UNRELEASED",
 focus=list(FOCUS),predecessor_signed_file_hashes=LINEAGE,
 baseline=dict(distinct_original_rooms=13,original_two_copy_physical_units=26,
  original_material_source_rows=27,original_excluded_unpriced_Primary_niche_refs=2,
  original_W1W2W3_studies=25,original_historic_trades=65,
  original_four_unit_material_ONLY_USD="23572.44",
  original_historic_waste15percent_IN_GROSS_ONCE=True,
  Sandstone_existing_historical_material_USD="358.92",
  Grey_Soft_existing_historical_material_USD="1116.46",
  Caviar_existing_historical_material_USD="1163.32",
  powder_existing_historical_material_USD="2159.30",
  original_three_focus_rooms_nine_source_material_rows_historic_total_USD=str(historic_total),
  original_R31_lab_source_records=13,original_R31_wall_witnesses=50,
  original_R31_physical_instances=26,market_entries=14,distinct_market_buildings=9),
 new_substantive_work=dict(
   neutral_owner_unscored_manufacturer_conditionals=len(chall),
   recalibrated_candidate_tile_grid_cut_joint_walls=len(grid),
   candidate_wall_conditional_vertical_finish_edge_lengths=len(trim),
   physical_niche_positive_sill_and_four_surface_sections=len(niches),
   partial_factory_tile_body_membrane_mortar_wall_Z_stack=len(stacks),
   conditional_program_drain_tub_flange_membrane_glass_WP_holds=len(assemblies),
   original_point_drain_4plane_slope_threshold_scenarios=len(point),
   six_actual_unit_three_tier_owner_GBB=len(tiers),
   original_three_room_wall_level_niche_source_records=len(orig_focus),
   alternative_historic_vs_current_gc_cost_rows=len(rates),
   hypothetical_original_two_copy_same_factory_case_ceiling=len(case),
   individual_WALL_NICHE_LEVEL_POINT_PAN_item_evidence=len(permissions),
   six_unit_source_faithful_1to1_camera_requests_not_produced=len(samples),
   original_all_27_line_supplier_GC_normalization=len(normalized),
   crossroom_same_factory_sku_color_finish_lot_rules=len(pool),
   original_13_room_individual_wet_and_release_records=len(all13),
   original_26_physical_unit_shop_witnesses=len(unit),
   original_50_wall_shop_witnesses=len(walls),
   full_13_room_8_trade_sequential_holds=len(trades)),
 formal_board_round=17,old_champion_scores_unchanged=True,
 original_R014_DESIGN_missing_reports_not_fabricated=True,
 original_four_specialist_critic_reports_complete=False,
 original_independent_reviewer_worker15_fully_finished=True,
 independent_R39_reviewer_accepted=False,
 actual_native_1529_or_field_geometry_verified=False,
 current_EXACT_original_Opal_Ribbed_Emerald_item_wet_PERMISSION_approved=False,
 owner_approved_WALL_or_NICHE_substitution=False,
 approved_WP_membrane_with_selected_drain_and_factory_rough=False,
 exact_raw_numeric_wet_LEVEL_and_separate_POINT_PAN_test_received=False,
 original_paid_stock_or_real_Chicago_case_lot_current_offer=False,
 actual_installed_GC_bid_and_CHANGE_ORDER_signed=False,
 actual_1to1_physical_mockups_or_renders_produced=False,
 owner_TUB_vs_WALKIN_selection_changed=False,
 PH4_walkin_selected_preserved=True,
 actual_selected_Delta_or_Brizo_square_POINT_only_if_shower=True,
 original_PRIMARY_Brizo_48in_LINEAR_with_separate_rough_preserved=True,
 owner_approved=False,architect_approved=False,plumber_approved=False,
 waterproofing_approved=False,tile_installer_approved=False,
 supplier_approved=False,GC_approved=False,purchaser_approved=False,
 material_reserved=False,purchase_authorized=False,global_DONE=False,
 files=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in sorted(PAY.items())])
assert len(PAY)>=18,len(PAY)
OUT.mkdir(parents=True,exist_ok=False)
for name,data in sorted(PAY.items()):
 with (OUT/name).open("xb") as f:f.write(data)
(OUT/"MANIFEST.json").write_bytes((json.dumps(meta,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R39_PAYLOADS",len(PAY))
print("R39_MANIFEST_SHA",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
print("R39_NEW_COUNTS",json.dumps(meta["new_substantive_work"],sort_keys=True))
