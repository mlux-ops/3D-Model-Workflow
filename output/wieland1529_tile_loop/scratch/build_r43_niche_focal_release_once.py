"""R43 first-generation deterministic wet-bath fabrication decision package.
All geometry source drawing-provisional, no existing signed artifact mutated.
Distinct from R41 generic 48 balanced-wall studies and R40 carton pooling:
this models COUPLED niche aperture / side-pier + field/rough conflict,
architectural zone segregation and actual owner/GC change-trigger choices.
"""
from pathlib import Path
from decimal import Decimal
import csv,io,json,hashlib,math

B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r43-four-wet-bath-niche-focal-wall-fabrication-and-13room-GC"
assert not D.exists(),"One-time R43 signed output already exists"
PRE={
"R39_FULL":("deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement/MANIFEST.json","34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"),
"R40_FULL":("deliverables/integrated-r40-conditional-soho-ivory-sandstone-same-sku-lot-13room-GC/MANIFEST.json","ce61454e4f31b7021829ee14bc734fab82f6bb4a0025805d43eb22f939dadc39"),
"R41_FULL":("deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room/MANIFEST.json","7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0"),
"R42_FULL":("deliverables/integrated-r42-matte-white-thermostat-diverter-tub-spout-field-rough-wet-wall-GC/MANIFEST.json","1659fb4bb1bb57b1a26e8ab17ad36ce40ed49ba41ebd33b6fb45807e21c94712")
}
for k,(p,h) in PRE.items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h,(k,p)
def readcsv(path):
 with (B/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
old=readcsv("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
wall=readcsv("deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
actions=readcsv("deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
lab=readcsv("research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
w50=readcsv("research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
u26=readcsv("research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
rooms=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(old),len(wall),len(actions),len(lab),len(w50),len(u26),len(rooms))==(27,25,65,13,50,26,13)
assert sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
F=("PH-BATH3","PH-BATH4","TX-BATH3","TX-BATH4")
G={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in F}
P={r:json.loads((B/"rooms"/r/"plumbing.json").read_text(encoding="utf-8")) for r in F}
W={(x["room"],x["wall"]):x for x in wall}
O={(x["room"],x["source_surface"]):x for x in old}
assert all(len(G[r]["revit_room_numbers"])==2 for r in F)
assert all((r,"W3") in W for r in F)
TILE={
 "PH-BATH3":[("A","Soho Blue 2x10 Glossy","https://www.elmsurfaces.com/product/soho-blue","Wet blue WALL; retain source Sandstone NICHE only after actual factory/membrane approval","Focal glazed long wall W1, eliminate unapproved wet Opal completely"),
             ("B","Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","Matte three-wall WET; original Opal only on physically surveyed DRY wall not a fictitious dry segment","Vertical calm field, stronger light reflection control and chrome integration")],
 "PH-BATH4":[("A","Soho Ivory 2x10 Glossy","https://www.elmsurfaces.com/product/soho-ivory","Single same exact tile WET WALL and independently maker-approved NICHE","Black Onyx square drain and glossy ivory full-height focal wall"),
             ("B","Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","Matte entire WET WALL and independently approved niche; original Ribbed dry-only if field-certified DRY","Continuous matte wet envelope, lower glare next to Brizo BNX")],
 "TX-BATH3":[("A","Soho Emerald 2x10 Glossy","https://www.elmsurfaces.com/product/soho-emerald","Glossy Emerald full WET WALL, Sandstone original niche requires separate maker wet niche install","Emerald W1 focal, return W2/W3 quieter bonds, existing Brizo Black Onyx"),
             ("B","Noho Emerald 2x10 Matte","https://www.elmsurfaces.com/product/noho-emerald","Matte emerald full WET WALL independently wet-listed, original Emerald exact page still unresolved","Matte W1 focal and return, quieter premium aesthetic while retaining BNX shower")],
 "TX-BATH4":[("A","Soho Ivory 2x10 Glossy","https://www.elmsurfaces.com/product/soho-ivory","Retain original CORTAR Charcoal flat WALL only after exact Soft/24x48 wet app signed; replace old Caviar niche with glossy ivory","Dark charcoal wall + luminous contrast niche, minimal new demolition scope if authorized"),
             ("B","Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","Full replacement of original charcoal WET tub walls and Caviar niche with individually wet-listed matte porcelain","Light quiet three-wall volume with Hansgrohe Matte White, more waterproof labor")],
}
AUTHOR={
 "PH-BATH3":"TUB OR WALKIN OWNER UNSELECTED; Hansgrohe Chrome; Delta DT062412 Chrome 4in square POINT only if WALKIN; basin UNSELECTED",
 "PH-BATH4":"SELECTED WALKIN; Brizo BT062415-BNX Black Onyx square POINT; separate 4-plane shower PAN vs LEVEL",
 "TX-BATH3":"TUB OR WALKIN OWNER UNSELECTED; Brizo BT062415-BNX Black Onyx square POINT only if WALKIN",
 "TX-BATH4":"SELECTED Duravit tub, Hansgrohe Matte White, NO tiled PAN; 15758701 thermostat/72411701 PB-only spout conflict R42"
}
PAY={}
def csvout(name,rows):
 assert rows and len({tuple(x.keys()) for x in rows})==1,name
 f=io.StringIO(newline="");d=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");d.writeheader();d.writerows(rows)
 PAY[name]=f.getvalue().encode("utf-8-sig")
def md(name,s):PAY[name]=(s.strip()+"\n").encode("utf-8")
def n(v):return f"{v:.4f}"
def yes(v):return "PASS_PROVISIONAL_ONLY" if v else "FAIL_PROVISIONAL_3IN_PIER"

# New actual construction feasibility: centered design choices tested for
# potential 3in structural/tile pier, notch/corner. Actual niche location is
# UNKNOWN; this is a hard conditional decision, not a located niche drawing.
Piers=[];Open=[]
for r in F:
 w=float(W[r,"W3"]["source_width_in_UNVERIFIED"])
 h=float(W[r,"W3"]["source_tiled_height_in_UNVERIFIED"])
 for width in (12,16,20,24):
  for offset in (0,1.0):
   left=(w-width)/2+offset;right=w-width-left
   for joint in (.125,.1875):
    minpier=min(left,right)
    Piers.append(dict(room=r,wall="W3",source_provisional_wall_width_in=n(w),
     source_provisional_tiled_height_in=n(h),niche_opening_width_in_HYPOTHETICAL=width,
     niche_opening_height_in_HYPOTHETICAL=12,
     theoretical_aperture_offset_from_CENTER_in=offset,
     proposed_vertical_joint_in_ILLUSTRATIVE=joint,
     left_pier_before_trim_and_factory_caliber_in=n(left),
     right_pier_before_trim_and_factory_caliber_in=n(right),
     minimum_raw_side_pier_in=n(minpier),focal3inch_RAW_SIDE_PIER_gate=yes(minpier>=3),
     minimum_pier_after_hypothetical_one_quarter_in_field_width_loss=n(minpier-.125),
     robust_3inch_gate_after_width_LOSS=yes(minpier-.125>=3),
     source_wet_wall_actual_pipe_valve_glass_and_niche_centerline_XY="UNKNOWN",
     available_actual_niche_count_and_blocking="UNKNOWN",
     approved_1529_location_and_3inch_finish_pier="FALSE",
     owner_approved="FALSE",shop_fabrication_authorized="FALSE"))
  # Field loss independently shown once, niche surfaces on top of aperture:
  field=width*12/144
  back=field;side=2*4*12/144;head=width*4/144;sill=head
  Open.append(dict(room=r,source_wall="W3",hypothetical_niche_opening_width_in=width,
   hypothetical_height_in=12,hypothetical_depth_in=4,
   original_WALL_field_negative_aperture_SF_once=n(field),
   separately_positive_niche_BACK_SF=n(back),two_SIDES_SF=n(side),
   separate_HEAD_SF=n(head),separate_SILL_SF=n(sill),
   total_positive_niche_tiled_sides_BACK_JAMBS_HEAD_SILL_SF=n(back+side+head+sill),
   net_proposed_wall_plus_niche_SURFACE_change_vs_full_wall_only_SF=n(-field+back+side+head+sill),
   already_original_accent_historic_material_line=O[r,"accent"]["source_row_id"],
   quote_full_WALL_vs_OPENING_deducted="UNKNOWN",actual_original_paid_niche_returnable_material="UNKNOWN",
   real_1529_aperture_and_sill_location="UNKNOWN",actual_displaced_area_credit_approved="FALSE",
   owner_niche_size_approved="FALSE",purchaser_release="FALSE"))
assert len(Piers)==64 and len(Open)==16
csvout("R43_64_HARD_3IN_NICHE_PIER_LOCATION_FIELD_SENSITIVITY_AND_FABRICATION_GATE.csv",Piers)
csvout("R43_16_PHYSICAL_NICHE_OPENING_ONCE_VS_BACK_JAMBS_HEAD_SILL_SF_AND_QUOTE_SCOPE.csv",Open)

# Novel cross-wall compositional zoning: 2 new assembly/program decisions per
# room build on R41 tile selected prior visual candidates, but now actually
# identify W1 vs returns and close the wet/dry 'unknown' escape hatch.
Concept=[]
for r in F:
 for letter,product,url,coverage,visual in TILE[r]:
  Concept.append(dict(room=r,neutral_owner_concept=f"R43_{r}_{letter}",
   actual_prior_R41_source_design="CARRIED_FORWARD_NOT_SCORABLE",
   original_program_and_fixed_plumbing=AUTHOR[r],
   exact_conditional_maker_product=product,current_individual_product_page=url,
   individual_product_Wet_Areas_WALL_listed="YES_PUBLISHED_ITEM_BUT_EXACT_ORDER_SKU_PENDING",
   individual_NICHE_application_and_SYSTEM_approval="MISSING_FACTORY_AND_SYSTEM_APPROVAL",
   dry_WALL_boundary_certified="FALSE",
   W1_wet_hero_wall=visual,
   W2_wet_return_system=coverage+"; continue approved water envelope at corners",
   W3_wet_niche_wall_decision="Choose conditional 12/16/20/24in aperture only where >=3in pier and true fixture clearance; no niche addition to Primary",
   WALL_vs_NICHE_individual_approval_gate="SEPARATE_REQUIRED",
   finish_FOCAL_factory_real_joint_and_caliber="UNKNOWN",
   source_actual_1529_valve_glass_XY="UNKNOWN",
   maker_current_exact_SKU_color_finish_lot_usable_case="UNKNOWN",
   GOOD_BETTER_BEST="GOOD = old historically aesthetic but wet HOLD; BETTER = keep only maker-listed wet wall; BEST = complete system and 1:1 approved finish/pipe and planned focal niche",
   owner_selection="FALSE",original_four_specialist_review="FALSE",formal_weighted_score="NULL",
   architect_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(Concept)==8
csvout("R43_8_PRIOR_R41_SHEME_REAL_W1_W2_W3_WET_COMPOSITION_AND_NICHE_ARCHITECT_RELEASE.csv",Concept)

# Independent executable conditional point-drain geometry, not an actual code
# compliant slope design. Historical source foot-print, not certified drain
# location, and no tub pan. Three distinct centerline hypotheses per bath.
PAN=[]
for r in ("PH-BATH3","PH-BATH4","TX-BATH3"):
 box=G[r]["shower_or_tub_footprint"]
 wi=float(box["width"]["value"])*12;di=float(box["depth"]["value"])*12
 for drag in ("SOURCE_RECT_CENTER","HYPOTHETICAL_DRAIN_6IN_OFFSET_ALONG_LONG_AXIS","HYPOTHETICAL_DRAIN_6IN_OFFSET_ALONG_SHORT_AXIS"):
  x=wi/2+(6 if drag=="HYPOTHETICAL_DRAIN_6IN_OFFSET_ALONG_LONG_AXIS" else 0)
  y=di/2+(6 if drag=="HYPOTHETICAL_DRAIN_6IN_OFFSET_ALONG_SHORT_AXIS" else 0)
  runs=[x,wi-x,y,di-y]
  assert min(runs)>0
  # deliberately a numerical scenario, not a claimed Chicago/code slope.
  FALL=[a*.25/12 for a in runs]
  PAN.append(dict(room=r,source_conditional_pan_width_in_PROVISIONAL=n(wi),
   source_conditional_pan_depth_in_PROVISIONAL=n(di),
   source_reference_fixture="PH3 Delta DT062412 Chrome POINT if WALKIN" if r=="PH-BATH3" else
    "PH4 Brizo BT062415-BNX actual WALKIN POINT" if r=="PH-BATH4" else "TX3 Brizo BT062415-BNX only WALKIN",
   hypothetical_POINT_location=drag,centerline_x_from_SOURCE_alcove_corner_in=n(x),
   centerline_y_from_SOURCE_alcove_corner_in=n(y),
   left_run_in=n(runs[0]),right_run_in=n(runs[1]),front_run_in=n(runs[2]),back_run_in=n(runs[3]),
   independent_test_hypothetical_slope_in_per_foot="0.25_NOT_CODE_OR_ACTUAL",
   left_required_FALL_in_HYPOTHETICAL=n(FALL[0]),right_required_FALL_in_HYPOTHETICAL=n(FALL[1]),
   front_required_FALL_in_HYPOTHETICAL=n(FALL[2]),back_required_FALL_in_HYPOTHETICAL=n(FALL[3]),
   furthest_run_from_POINT_in_HYPOTHETICAL=n(max(runs)),
   highest_implied_relative_surface_elevation_in_HYPOTHETICAL=n(max(FALL)),
   actual_true_1529_perimeter_rough_and_glass="UNKNOWN",
   actual_selected_bonding_flange_z_with_selected_rough="UNKNOWN",
   original_POINT_PAN_raw_exact_numeric_wet_lab="MISSING",
   original_LEVEL_independent_raw_exact_numeric_wet_lab="MISSING",
   owner_TUB_vs_WALKIN_selected="FIXED_WALKIN" if r=="PH-BATH4" else "FALSE",
   actual_code_maker_slope_approved="FALSE",architect_plumber_WP_SIGNED="FALSE",
   construction_release="FALSE",purchase_authorized="FALSE"))
assert len(PAN)==9
csvout("R43_9_SOURCE_RECTANGLE_POINT_DRAIN_FOUR_PLANE_Z_ENVELOPE_WITH_SELECTED_FIXTURE_GATES.csv",PAN)

# A usable contractor scope rather than invented material cost: origin/meaning,
# factory-compatibility, measurable exterior edge LF and scenario-only niche
# surface, existing old material credit and complete installed work.
Scope=[]
for r in F:
 h=float(W[r,"W1"]["source_tiled_height_in_UNVERIFIED"])
 ww=[float(W[r,z]["source_width_in_UNVERIFIED"]) for z in ("W1","W2","W3")]
 original_wall_net=sum(ww)*h/144
 orig_gross=Decimal(O[r,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])
 oldtwo=Decimal(O[r,"wall"]["historic_usd_two_copies"])
 rate=oldtwo/(orig_gross*2)
 for letter,product,url,coverage,visual in TILE[r]:
  for aperture in (12,16):
   depth=4;nh=12
   field_negative=aperture*nh/144
   positive=field_negative + 2*nh*depth/144+2*aperture*depth/144
   edge=(2*nh+2*aperture)/12
   wall=original_wall_net-field_negative
   for copy in G[r]["revit_room_numbers"]:
    Scope.append(dict(room=r,physical_copy=copy,concept=f"R43_{r}_{letter}",
     item=product,original_wall_row=O[r,"wall"]["source_row_id"],
     original_niche_row=O[r,"accent"]["source_row_id"],
     quote_source_W1W2W3_full_wall_NET_SF_PREOPENING=n(original_wall_net),
     source_original_historic_WALL_GROSS_one_copy_INCL15pct_ONCE=str(orig_gross),
     source_historic_WALL_two_copy_material_only_USD=str(oldtwo),
     source_historic_WALL_material_per_GROSS_SF_USD=n(rate),
     illustrative_ONE_opening_wide_in=aperture,
     illustrative_ONE_opening_high_in=nh,
     illustrated_negative_ONE_wall_field_SF=n(field_negative),
     illustrated_positive_niche_BACK_SIDES_TOP_SILL_SF=n(positive),
     illustrative_wall_field_after_ONE_opening_NET_SF=n(wall),
     illustrative_perimeter_profile_if_all_four_edges_exposed_LF=n(edge),
     NOTE_do_not_bill_all_four_edges_if_embedded="Actual sill/support/return and trim terminations determine exposed perimeter; finish and waterproof membrane alone not costed here",
     current_factory_APPROVED_usable_carton_and_SKU_lot="UNKNOWN",
     real_true_1529_niche_2D_3D_and_wall_openings="UNKNOWN",
     new_original_15pct_reuse_not_an_increment="TRUE",
     current_actual_net_PLUS_NEW_separately_owner_approved_waste="UNKNOWN",
     WET_WALL_vs_NICHE_maker_permission_and_WP_assembly="NOT_SIGNED",
     original_purchased_received_returnable_material_credit_USD="UNKNOWN",
     actual_supplier_material_and_spare_LOT_USD="UNKNOWN",
     GC_demolition_new_backer_valve_WP_drain_or_tubflange_trim_install_labor_USD="UNKNOWN",
     owner_budget_upgrade_cap="UNSELECTED",
     real_payable_change_order_approved="FALSE",owner_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(Scope)==32
csvout("R43_32_FOCUS_UNIT_CONDITIONAL_FIELD_NICHE_PROFILE_AND_GC_SCOPE_NOT_A_PRICE.csv",Scope)

# New fabrication go / no-go checklist grouped into physical signed junctions.
# Different from R41 generic four per bath: identifies the exact 3in side
# pier pass on source 24in niche and exact conflict with controls and glass.
Shop=[]
for r in F:
 for copy in G[r]["revit_room_numbers"]:
  for step,hold in (
   ("S01_FOCAL_W1_LAY_OUT","Survey actual 1529 WIDTH/HEIGHT/plane, selected chrome or black/white rough and glass axis, locate original tile focal and field/dry boundary"),
   ("S02_W3_NICHE_PIER_ACTUAL","Derive left/right actual niche side-piers with trim and factory calibrated joint; nominal 24in PH3 W3 fails 3in before glazing; no cut until verified"),
   ("S03_WET_WALL_NICHE_MAKER","Prove selected exact COLOR/FINISH/SIZE wet WALL listing separately from manufacturer-approved niche substrate/membrane/sill/head returns, never borrow from adjacent variant"),
   ("S04_NICHE_AND_TRIM_PHYSICAL","Block actual pipe-free niche depth, sill drain-to-wet, back+2 sides+top+sill, trim depth and movement joint without piercing membrane"),
   ("S05_PROGRAM_DRAIN_TUB_ROUGH","PH4 fixed BNX square POINT four-plane PAN separate LEVEL; PH3/TX3 TUB vs WALKIN owner unselected; TX4 Duravit tub, selected Matte White spout/thermostat R42 hold and no tiled PAN"),
   ("S06_FLOOR_LEVEL_AND_SLOPE","If WALKIN verify actual four plane pan polygon drain X/Y/Z, membrane bonding selected rough, threshold/curb/glass; exact original LEVEL DCOF and independent smallformat POINT PAN original numeric wet DCOF; tub N/A PAN"),
   ("S07_INSTALLED_FINISH_PLANE","Maker tile body alone not full finish; actual backer, mortar compressed range, waterproof lap, wall profile and valve/escutcheon depth, no assumed compensating mortar rule"),
   ("S08_GC_OLD_AND_NEW_PAYABLE","Reconcile original opening not automatically paid credit, 15% old waste once, wet-wall vs niche positive materials, current same exact lot/caliber only, full installed labor and old paid/returnable stock"),
   ("S09_1TO1_SOURCE_WITNESS","Each physical copy must have exact field photographed wall/niche/valve and original wet-lab; physical full 1:1 tile finish/trim/movement/sill/drain or tub flange proof, not existing renders")
  ):
   Shop.append(dict(room=r,physical_copy=copy,shop_hold_step=step,
    contractor_check=hold,original_fixture_and_program=AUTHOR[r],
    original_WALL_NICHE_PERMISSION="HOLD_NEED_INDIVIDUAL_AND_SYSTEM",
    required_TRUE_1529_survey_or_original_RAW_numerical_wet_lab="UNKNOWN",
    actual_original_selected_rough_WP_compatibility="UNKNOWN",
    trade_owner_arch_plumb_WP_tile_supplier_GC_purchase_signatures="FALSE",
    actual_1TO1_per_physical_room_mockup="FALSE",
    owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(Shop)==72
csvout("R43_72_FOCUS_PHYSICAL_BATH_NINE_TRADE_AND_1TO1_CONSTRUCTION_HOLD_POINTS.csv",Shop)

Maker=[]
for r in F:
 selected=[
  ("ORIGINAL_WALL","ORIGINAL_SOURCE_HOLD","Tones Opal 2x20 glossy","https://www.elmsurfaces.com/product-collection/tones") if r=="PH-BATH3" else
  ("ORIGINAL_WALL","ORIGINAL_SOURCE_HOLD","Cortar Bone Ribbed relief","https://www.elmsurfaces.com/product-collection/cortar") if r=="PH-BATH4" else
  ("ORIGINAL_WALL","ARCHIVED_ONLY_NEED_CURRENT_EXACT","Tones Emerald 2x20 glossy","https://www.elmsurfaces.com/product-collection/tones") if r=="TX-BATH3" else
  ("ORIGINAL_WALL","FAMILY_WET_LISTED_EXACT_SOFT_RECHECK","Cortar Charcoal 24x48 flat Soft","https://www.elmsurfaces.com/product-collection/cortar")
 ]
 for classification,status,item,url in selected:
  Maker.append(dict(room=r,role=classification,product_identification=item,manufacturer_page=url,
   individual_exact_selected_COLOR_SIZE_FINISH_wet_WALL_evidence=status,
   independent_exact_item_WET_NICHE_evidence="NOT_PROVEN",
   wall_pan_or_tub_flange_membrane_complete_assembly_APPROVAL="FALSE",
   original_exact_item_raw_wet_DCOF_LEVEL="MISSING",
   separate_POINT_PAN_exact_original_lab="N_A_TUB" if r=="TX-BATH4" else "MISSING_IF_WALKIN",
   manufacturer_current_usable_case_SKU_color_finish_lot="UNKNOWN",
   factory_product_OWNER_SELECTED_alternative="FALSE",purchase_authorized="FALSE"))
 for letter,item,url,coverage,visual in TILE[r]:
  Maker.append(dict(room=r,role="R43_CONDITIONAL_MAKER_LISTED_WALL_"+letter,
   product_identification=item,manufacturer_page=url,
   individual_exact_selected_COLOR_SIZE_FINISH_wet_WALL_evidence="PRODUCT_PAGE_LISTS_WET_AREAS_WALLS_2X10",
   independent_exact_item_WET_NICHE_evidence="PRODUCT_PAGE_WET_WALL_NOT_COMPLETE_NICHE_SYSTEM",
   wall_pan_or_tub_flange_membrane_complete_assembly_APPROVAL="FALSE",
   original_exact_item_raw_wet_DCOF_LEVEL="MISSING",
   separate_POINT_PAN_exact_original_lab="N_A_TUB" if r=="TX-BATH4" else "MISSING_IF_WALKIN",
   manufacturer_current_usable_case_SKU_color_finish_lot="UNKNOWN",
   factory_product_OWNER_SELECTED_alternative="FALSE",purchase_authorized="FALSE"))
assert len(Maker)==12
csvout("R43_12_EXACT_ORIGINAL_VS_CONDITIONAL_INDIVIDUAL_MAKER_WET_WALL_SEPARATE_NICHE_MATRIX.csv",Maker)

# Witness records explicitly integrate existing R31 (13 lab,50 wall,26
# physical), preserving each original source row and its existing program.
WIT=[]
for x in u26:
 r=x["room"]
 WIT.append(dict(room=r,physical_copy_index=x["physical_copy_index"],
  original_R31_source_room_number=x["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"],
  original_program=x["program"],selected_plumbing_and_branch="R43_"+AUTHOR[r] if r in F else
  "ORIGINAL_R41_SELECTED_UNCHANGED",
  R43_niche_focal_pier_and_ACTUAL_XY_GC_witness="R43_72_JUNCTION_SHOP_AND_64_PIER_MATCH_REQUIRED" if r in F else "ORIGINAL_R31_WITNESS_PRESERVED",
  signed_true_1529_W1W2W3_valve_niche_glass_in="UNKNOWN",
  selected_material_current_wet_WALL_vs_NICHE_identity="UNKNOWN",
  original_exact_RAW_LEVEL_lab="N_A_WOOD" if "POWDER" in r else "PARENT_PRIMARY" if r.endswith("-WC") else "MISSING",
  separate_original_exact_RAW_POINT_or_LINEAR_PAN_lab="N_A_TUB" if r in ("PH-BATH2","TX-BATH2","TX-BATH4") else
  "N_A_WOOD_OR_WC" if "POWDER" in r or r.endswith("-WC") else
  "MISSING_IF_OWNER_WALKIN" if r in ("PH-BATH3","TX-BATH3") else "MISSING",
  actual_fullscale_mockup_built="FALSE",signed_wet_assembly="FALSE",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",waterproof_approved="FALSE",
  tiler_approved="FALSE",supplier_approved="FALSE",GC_approved="FALSE",purchaser_approved="FALSE",
  purchase_authorized="FALSE"))
assert len(WIT)==26
csvout("R43_26_PHYSICAL_INSTANCE_NICHE_FOCAL_POINT_OR_TUB_AND_1TO1_WITNESS_BRIDGE.csv",WIT)

roomg=[]
for x in rooms:
 r=x["id"]
 ORIGINAL=("PH_BATH3_OWNER_TUB_VS_WALKIN" if r=="PH-BATH3" else "TX_BATH3_OWNER_TUB_VS_WALKIN" if r=="TX-BATH3" else
  "PH4_ACTUAL_WALKIN_BRIZO_BNX_4IN_POINT_FOUR_PLANE_PAN_SEPARATE_LEVEL" if r=="PH-BATH4" else
  "TX4_ACTUAL_DURAVIT_TUB_HANSGROHE_MATTE_WHITE_NO_PAN_THERMOSTAT_SPOUT_HOLD" if r=="TX-BATH4" else
  "PH_TX_PRIMARY_48IN_BRIZO_BNX_LINEAR_SEPARATE_ROUGH_NO_PRIMARY_NICHE" if r in ("PH-PRIMARY","TX-PRIMARY") else
  "PH_TX_WC_INHERITED_PRIMARY_LEVEL_NO_NEW_WC_ORDER_TX203A_UNPLACED" if r in ("PH-WC","TX-WC") else
  "ORIGINAL_DURAVIT_TUB_NO_PAN_HANSGROHE_FINISH_PRESERVED" if r in ("PH-BATH2","TX-BATH2") else
  "DRY_POWDER_WOOD_FLOOR_KEEP_ORIGINAL_FACET_MOUNTING_UNSELECTED_BASIN")
 roomg.append(dict(room=r,formal_board_round=17,
  original_champion=x.get("champion_id") or "null",original_status=x["status"],
  original_score=str(x.get("champion_score")) if x.get("champion_score") is not None else "null",
  original_nonnegotiable_owner_program=ORIGINAL,
  new_R43_approved_design="NONE_UNSELECTED",
  R43_specific_pier_gate="FALSE_NEEDS_TRUE_1529" if r in F else "N_A_R43_FOCUS",
  wet_WALL_and_independent_NICHE_factory_system="MISSING_OR_N_A_DRY",
  original_LEVEL_exact_raw_numeric_test="MISSING_OR_N_A_WOOD",
  independent_POINT_or_LINEAR_pan_exact_numeric_test="MISSING_OR_N_A_TUB_OR_DRY",
  actual_field_1529_reverified="FALSE",
  current_factory_same_SKU_COLOR_FINISH_LOT_and_box="UNKNOWN",
  original_hist_material_GROSS_15pct_counted_once="TRUE",
  original_paid_quote_current_material_and_full_GC_bids="UNKNOWN",
  formal_4_original_specialist_weighted_champion_review="FALSE",
  original_nonPro_Reviewer_global_DONE="FALSE",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  waterproofing_approved="FALSE",tile_installer_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(roomg)==13
csvout("R43_13_ROOM_FULL_OWNER_SELECTED_PROGRAM_WET_FLOOR_AND_PURCHASING_GATE.csv",roomg)

# Reconciliation of all old original material rows and original historical
# material dollars, but R43 contracts are conditional NEW installed scope.
source=[]
for x in old:
 source.append(dict(room=x["room"],original_row=x["source_row_id"],original_surface=x["source_surface"],
  historical_one_copy_GROSS_SF_already_includes_original15pct=x["source_gross_sf_one_copy_waste_15pct_once"],
  historic_two_copy_material_only_USD=x["historic_usd_two_copies"],
  original_primary_niche_EXCLUDED=x["historic_niche_excluded_no_scope"],
  new_R43_model="NICHE_SIDE_PIER_HARD_GATE_AND_MEMBRANE_NEGATIVE_FIELD_POSITIVE_RETURNS" if x["room"] in F else "HISTORIC_SOURCE_PRESERVED",
  actual_factory_identical_SKU_COLOR_FINISH_CALIBER_lot_verified="FALSE",
  observed_actual_site_NICHE_layout_CUTSTOCK="UNKNOWN",
  actual_current_supplier_2026_chicago_unit_quote_box_freight_eta="UNKNOWN",
  actual_GC_installed_labor_backer_WP_tub_rough_point_trim_scope_bid="UNKNOWN",
  original_purchase_received_and_RETURNABLE_credit_signed="FALSE",
  new_payable_amount_or_realized_savings="UNKNOWN_NOT_APPROVED",
  owner_approved="FALSE",GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(source)==27
csvout("R43_27_ORIGINAL_MATERIAL_ROWS_WITH_GC_INSTALLATION_CHANGE_SCOPE_NO_DUPLICATE.csv",source)

TRADE=("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC","PURCHASER")
seq=[]
for r in (x["id"] for x in rooms):
 for i,role in enumerate(TRADE,1):
  task={
   "OWNER":"Approve true bath3 tub vs walkin only owner; accept exact tile/finish and dry/wet zoning/budget",
   "ARCHITECT":"Sign true 1529 W1W2W3 actual niche X/Y and minimum 3in focal pier after trim/joint, glass, elevation and datum",
   "PLUMBER":"Sign actual valve/service/drain/tub flange and exact rough; retain R42 PH2/TX4 thermostatic vs PB spout hold",
   "WATERPROOFING":"Exact individual wet Wall versus niche maker item and fully approved backer/membrane/drain/tub flange/sill details",
   "TILE_INSTALLER":"Source calibrated module/trim/movement joints/1:1 niche and exact raw wet LEVEL and separate POINT or LINEAR PAN lab if applies",
   "SUPPLIER":"Exact current orderable SKU/color/finish/lot/case usable SF/Chicago stock/pricing freight and owner selection",
   "GC":"Actual 1529 measured negative wall opening and positive niche face separately, original old 15pct once, paid material credit and full new installed CO",
   "PURCHASER":"Only after all original seven trade approvals plus authentic four specialists and independent reviewer global readiness"
  }[role]
  seq.append(dict(room=r,sequence=i,trade=role,actual_new_R43_scope=task,
   original_room_program_unchanged="TRUE",signed_completion="FALSE",
   owner_approved="FALSE",architect_approved="FALSE",GC_approved="FALSE",
   purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(seq)==104
csvout("R43_104_SEQUENTIAL_EIGHT_TRADE_13ROOM_NICHE_FIELD_AND_WET_SHOP_ACCEPTANCE.csv",seq)

def svg(r):
 wi=float(W[r,"W3"]["source_width_in_UNVERIFIED"])
 hh=float(W[r,"W3"]["source_tiled_height_in_UNVERIFIED"])
 a=(wi-16)/2;b=(wi-24)/2
 def panel(x,opening,sign):
  sc=9; w=wi*sc; H=290; left=(wi-opening)/2*sc
  color="#4c815f" if sign else "#b45e48"
  parts=[f'<rect x="{x}" y="113" width="{w:.1f}" height="{H}" fill="#e5e0d8" stroke="#253847" stroke-width="2"/>',
    f'<rect x="{x+left:.1f}" y="201" width="{opening*sc:.1f}" height="108" fill="#fbfaf6" stroke="{color}" stroke-width="3"/>',
    f'<text x="{x}" y="92" font-size="15" font-family="Arial">W3 source {wi:.2f}in / H {hh:.2f}in</text>',
    f'<text x="{x}" y="428" font-size="15" font-family="Arial" fill="{color}">Hypothetical {opening}in aperture: {(wi-opening)/2:.2f}in each side pier</text>',
    f'<text x="{x}" y="452" font-size="13" font-family="Arial">{ "PASS raw 3in" if sign else "FAIL raw 3in" } | No valve/glass, trim or actual 1529 site measured</text>']
  return "\n".join(parts)
 return "\n".join([
 '<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="565" viewBox="0 0 1040 565">',
 '<rect width="100%" height="100%" fill="#faf9f5"/>',
 f'<text x="30" y="33" font-family="Arial" font-size="23" font-weight="bold" fill="#23333d">R43 {r} W3 conditional fabrication feasibility</text>',
 '<text x="30" y="57" font-family="Arial" font-size="14" fill="#a34b3f">CONCEPT DRAWING. Original 1529 W3 width/height NOT site-certified. No actual niche, tile, valve or curb shown.</text>',
 panel(30,16,a>=3),panel(530,24,b>=3),
 f'<text x="30" y="493" font-family="Arial" font-size="13" font-weight="bold">Actual field clearance formula: left=(actual width - actual aperture)/2 + real offset; right=width-aperture-left.</text>',
 '<text x="30" y="520" font-family="Arial" font-size="13">Approve only when BOTH true finished side piers >=3in after trim/grout, pipe and glass. Signed 1:1 is required.</text>',
 '<text x="30" y="544" font-family="Arial" font-size="12">Niche field opening deducted ONCE; back, two jambs, head and sloped sill counted separately; no approved credit.</text></svg>'
 ])
for r in F:PAY[f"R43_{r}_16IN_VS_24IN_W3_NICHE_SOURCE_PIER_SHOP_CONDITIONAL.svg"]=svg(r).encode("utf-8")

for r in F:
 width=float(W[r,"W3"]["source_width_in_UNVERIFIED"]);h=float(W[r,"W3"]["source_tiled_height_in_UNVERIFIED"])
 def sizepass(a,offset=0):return "PASS raw >=3in" if (width-a)/2-abs(offset)>=3 else "FAIL raw >=3in"
 a,b=TILE[r]
 a1=(width-16)/2;a2=(width-24)/2
 details=f"""
# R43 | {r} actual-source wet focal / niche / fixture coordination shop decision

**Authority:** Original owner-selected fixture and shower/tub program: **{AUTHOR[r]}**. This is a conditional architect/GC evaluation; no approved tile substitution, maker waterproof system, original wet-lab certification or 1529 verified dimensions. Physical source instances: {", ".join(G[r]["revit_room_numbers"])}.

## Architectural decision — redesign the junction, not just substitute a product

GOOD reference: retain source material appearance for owner evaluation only. Original WALL individual wet gate: {next(x["individual_exact_selected_COLOR_SIZE_FINISH_wet_WALL_evidence"] for x in Maker if x["room"]==r and x["role"]=="ORIGINAL_WALL")}; original niche installation individually unverified. Source-original wet WALL not certified for installation by a different product listing.

BETTER conditional: **{a[1]}** individually listed Wet Areas WALL {a[2]}, focal composition **{a[4]}**. Wet zone **{a[3]}**. W1 read as deliberate focal vertical or horizontal tile field with selected fixture as axis; W2/W3 returns must maintain water barrier continuously through niche and corners. This proposal is NOT owner selected.

BEST conditional: **{b[1]}**, individual wet Wall listing {b[2]}, visually **{b[4]}**, wet assembly {b[3]}. Difference is a distinct finish and physical replacement/setting strategy, not an unsupported resale premium. Good/better/best is a value/constructability comparison, not the frozen R017 board's weighted result. Both alternatives require exact factory orderable SKU/color/finish/caliber and separately approved niche membrane system, real setting joint and 1:1.

## W3 pier feasibility and concrete site choice

Original drawing-provisional W3 clear source width **{width:.2f}in**, tile height **{h:.2f}in**. A hypothetical *centered* **16in × 12in** opening yields **{a1:.2f}in side piers**, {sizepass(16)}. A centered **24in × 12in** yields **{a2:.2f}in side piers**, {sizepass(24)}. The W3 SVG illustrates both only as hypothetical cut geometry, not actual niche count or position. A 1in offset makes the narrower pier shrink by 1in: 16in case **{a1-1:.2f}in**, {sizepass(16,1)}; 24in case **{a2-1:.2f}in**, {sizepass(24,1)}. After actual field opening/trim and manufacturer calibrated joint/pipe, the minimum 3in focal side pier can change. Require signed true 1529 field W3 clear width and niche actual location relative to valve, glass edge, head/sill and any pipe/structural block. Choose 12/16/20/24 only after physical clearance; no invented existing niche opening.

## Conditional section W3A — field+niche+trim

Actual-stud/approved backing and membrane continuous through internal corners -> niche BACK, two JAMB returns, HEAD, supported inward FALL SILL -> compatible seam, liquid/sheet joint if separately approved manufacturer and tile body with actual compressed mortar -> real joint and return-edge profile depth. Do not drill through waterproof layer at accessories. Original nominal Caviar body ~13mm (PH4/TX4) vs conditional manufacturer Soho/Noho nominal 9.5mm changes *tile body* only; actual finished plane is backer + membrane + COMPRESSED mortar + calibrated tile, NOT automatically a 3.5mm finished plane shift. Confirm actual valve rough-to-finished wall trim engagement and glass positioning before backer closure. Allow independent movement at change of plane; final joint width/profile requires factory/architect approval.

### Quantitative 16 × 12 × 4in niche example (not an existing condition)

- Surrounding wall **one aperture -1.3333 SF**, original surrounding quote/full wall claim uncertain; cannot claim credit automatically.
- Tiled niche BACK **+1.3333 SF**, two SIDES **+0.6667 SF**, TOP **+0.4444 SF**, SILL **+0.4444 SF**. Total individually positive niche **2.8889 SF NET**, assuming four inside returns fully tiled, without new waste.
- Conditional profile if all four sides exposed = **(2×16 + 2×12)/12 = 4.6667 LF**. Real trim LF may be less due to concealed sill/return, factory edge needs and movement. Niche supply is already a different historic source row, not new full-wall add.
- True material order = actual measured **NET × (1 + separately signed NEW waste)** and rounded by verified usable case. Do not reapply original 15% to historic gross, do not treat old Caviar or old Sandstone amount as new credit, and do not pool Soho Gloss with Noho Matte.

## Conditional section W1+W2+W3 and original program/floor

If {r} owner-selected program includes TUB, NO tiled shower PAN: require actual owner-selected tub/flange waste and overflow, signed selected controls/valve/service, membrane seal to tub flange, sill/tub joint and original LEVEL floor raw measured numeric wet test. WALKIN branch only if actually selected: keep original selected Delta Chrome or Brizo Black Onyx four-inch SQUARE POINT as applicable, real four-plane small-format PAN with selected drain/bonding flange system and separately exact original RAW numeric wet PAN DCOF, distinct bath LEVEL raw lab; confirm actual drain centerline X/Y/Z, curb/threshold/glass, water test. PH4 is WALKIN fixed, never conditional tub. TX4 Duravit tub fixed, Hansgrohe Matte White NO PAN, R42 thermostat/spout factory conflict retained.

## Actual 1:1 and contractor release dependencies

1. Survey physical source copy 1529 dimensions all W1/W2/W3, niche actual count/X/Y/depth and backing, valve/escutcheon and niche clearance, glass/wet splash boundary, tub flange or point drain elevations and real threshold.
2. Architect approve exact wet-zone WALL/NICHE material and final 3in focal pier/short tile cuts after calibrated factory size/joint, turns, edges and movement.
3. Plumber/WP provide ONE supported exact selected drain/tub flange, backing, membrane seams, penetration boots and setting mortar arrangement; no permission transfer across similar colors or factory finishes. 
4. Field 1:1 witness actual niche BACK/JAMBS/HEAD/SILL fall, finish plane/trim and installed sample with signed photo; actual source wet floor numeric independent LEVEL/PAN evidence, and documented inspection/water test where required.
5. Supplier and GC distinguish old wall gross/paid stock, opening once, original accent/niche line, exact material replacement + new waterproofing/trim/labor and conditional walkin PAN quoted inclusion; no actual original payable shortfall until signed quantity and scope.

Full sample rendering only AFTER actual native **1529** survey, source-faithful W1/W2/W3 camera and fixtures; R43 schematic SVG is NOT a real photograph, existing physical mockup or render. Market original 14 listings/nine buildings, Old Town $2.4M–$3.2M primary; Lincoln Park/Gold Coast secondary, no fake competitor tile or premium. Every owner/architect/plumber/WP/tile/supplier/GC/purchase release FALSE.
"""
 md(f"R43_{r}_HARD_PIER_FOCAL_WALL_TUB_OR_POINT_NICHE_ARCHITECT_GC_BOOK.md",details)

focuscost=sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old if x["room"] in F)
assert focuscost==Decimal("9124.72")
md("START_HERE_R43_FOUR_BATH_ARCHITECTURAL_FABRICATION_CRITICAL_NICHE_PIER_AND_GC_SCOPE.md",f"""
# R43 — 1529 Wieland integrated four-bath actionable wet-focal and niche fabrication engineering

**Substantial NEW four-focus architecture/shop/GC implementation** following R41 eight schematic material concepts (not repeated) and R42 Hansgrohe exact PB diverter/thermostat conflict (not re-investigated). Rooms PH-BATH3, PH-BATH4, TX-BATH3, TX-BATH4, eight physical source room copies. Formal R017 blind board remains frozen and global 13-room objective OPEN.

## Actual new architectural consequences

Each room now has a **two-sided fabrication answer rather than another undifferentiated wall module drawing**. Source-provisional W3 centered niche aperture is compared at 12/16/20/24in with a signed 3in side-pier go/no-go, offset and field-width loss. The result changes the proposed focal composition materially:

- **PH-BATH3** source W3 **27.96in**: hypothetical centered **24in niche leaves 1.98in each side and FAILS 3in minimum** before grout/trim/field width; centered **16in yields 5.98in each** (source-only PASS). If offset by 1in, the 24in worst side is **0.98in**, unacceptable focal pier. Original Opal wet WALL still unlisted; retain owner chromed plumbing and tub-versus-walkin owner unselected. Advance the existing R41 Soho Blue full WET wall and Noho Ivory full WET wall as distinct architectural looks; original Opal may be retained in **physically demonstrated dry wall** only and not redefined as dry without glass/splash survey.
- **PH-BATH4** source W3 **30.48in**: centered 24in niche has **3.24in** raw piers and nominally passes, but 1in offset reduces one pier to **2.24in**, FAIL. Therefore 16in or 20in niche is more robust pending actual valve/glass and tile return; selected Brizo Black Onyx 4in square POINT WALKIN and separate 4-plane PAN vs LEVEL remain immutable. Original Bone Ribbed/Caviar individual wet WALL/NICHE approval incomplete; owner-conditional Soho Ivory glossy vs Noho Ivory matte full wet enclosure, each independent exact wet niche membrane approval and trim coordination.
- **TX-BATH3** source W3 **31.20in**: centered 24in niche leaves **3.60in** piers, but 1in displacement makes one **2.60in**, fails. Distinct Soho Emerald GLOSS W1 focal versus Noho Emerald MATTE W1 alternative continue, original Emerald current exact color/size/finish item needs renewal. Original Brizo Black Onyx POINT only if owner selects WALKIN; owner TUB versus WALKIN unresolved.
- **TX-BATH4** source W3 **30.48in**: same centered 24in **3.24in** / offset 1in FAIL; contrast small Soho Ivory glossy niche within original Cortar Charcoal (conditional exact original Soft Wet Areas approval) versus full Noho Ivory matte three-wall tub refresh. Selected Duravit tub and Hansgrohe Matte White NO tiled PAN preserved. R42 15758701 thermostat vs PB-only 72411701 spout remains physically held until exact manufacturer approved full rough/trim/spout path.

These are **not located niches** or surveyed dimensions; the four SVGs show source 16in/24in hypothetical geometry and explicitly omit exact 1529 niche position, any valve/glass, trim or actual field tolerance. 64 centered/offset/joint/source-width pier gate records and 16 separate opening negative plus four positive niche surfaces demonstrate exactly what an architect/installer needs to witness before final shop. A 16×12×4in example displaces one wall aperture -1.3333SF, adds niche BACK 1.3333, TWO SIDES .6667, TOP .4444 and SILL .4444, positive 2.8889SF, exposed 4-side hypothetical edge 4.6667LF; original accent line already quoted separately. No wholesale opening-credit or new charge without actual net/invoice scope.

## NEW functional construction and physical inspection

72 **physical eight-unit × nine trade/1:1 source-specific site checklist holds** from original selected fixture through wet WALL versus independently wet NICHE factory assembly, pipe and niche backing, verified valve escutcheon finish plane, glass/corner/movement, selected tub flange or Brizo/Delta POINT 4-plane drain, old paid stock/current labor GC installed comparison. Nine distinct source RECTANGLE-based hypothetical four-plane point-PAN Z fall envelope cases for PH3, PH4 and TX3 (3 geometric drain centerline options each) avoid fictitious actual drain placement. Assumed 0.25in/ft is ONLY an engineering geometry trial, NOT accepted code slope; separate original numeric raw wet LEVEL versus POINT PAN laboratory tests and maker drain-to-membrane compatibility remain missing. If owner selects TUB in PH3/TX3, no tiled PAN, actual original 4in POINT cannot become a tub waste.

Original product evidence remains individual manufacturer-scope: ELM Soho/Noho specific wet-WALL listing, nominal 9.5mm 2x10, **not** installed wet NICHE compatibility. Original Clara Caviar 2x8 nominal ~13mm collection documentation is not exact Caviar wet NICHE authorization. Original Tones Opal wet WALL absent, Cortar Bone Ribbed relief wall unverified, Tones Emerald older exact wet evidence needs live SKU renewal, TX4 Cortar Charcoal Soft current exact source SKU wet item needs verification. Original factory/current exact SKU, grout, calibers, actual membrane, substrate, mortar, trim depth, tub flange, drain rough, 1:1 actual 1529 and sample all held. Original nominal 3.5mm body difference does not directly establish actual finish plane.

## Integrated material and GC construction cost, no fictitious savings

Source original PH3/PH4/TX3/TX4 wall/floor/niche **12 rows $9,124.72 historic material-only included within old four-unit $23,572.44 total**, 15% waste ALREADY ONCE in original source gross. Other old Sandstone $358.92, Cortar Grey $1116.46, Caviar $1163.32, powder $2159.30 historical subsets INCLUDED. New 32 exact room-copy/concept/12-vs-16-aperture conditional original rate vs true installed WALL/niche positive return and edge, factory item, actual paid stock/credit, current supplier and full GC demolition/rough/waterproof/trim/labor quotes—not current orders or realized savings. Existing original wall quote may be full-wall or opening-deducted and original shower PAN may be included or excluded (mutually exclusive old contract interpretations). No duplicate WC, Primary niche, re-added 15%, separate PAN/LEVEL or niche opening/back charges.

Original 13 room IDs/26 physical room copies, 27 material rows including two no-order Primary niche references, 25 W elevation studies, 65 trade action records, R31 13 exact numerical wet lab roles, 50 wall survey and 26 physical witness obligations unchanged. New 13 room source program/wet lab/approval release bridge and 104 eight-trade sequenced hold records ALL FALSE. Original two selected Primary 48in BNX LINEAR drains each separate BR73480 NO additional niches, inherited WC once, three Duravit tubs PH2/TX2/TX4 original Hansgrohe finishes NO shower PAN, powders wood floor wet-lab N/A and faucet/deck mounting/owner unselected basins all retained.

## Owner-facing value and governance

GOOD retained source visual only (blocked original exact wet use), BETTER individually listed wet WALL candidate with optimized focal pier, BEST independent factory-approved WALL+NICHE membrane/rough/trim and 1:1 architect/owner approved sample. This is design direction, not formal board score. Source owner PH $2.8M/TX $2.7M, Old Town primary comparable $2.4M-$3.2M, 14 listings/9 independent buildings; Lincoln Park and Gold Coast secondary. No inferred competitor bathroom tile or dollar premium.

Original four specialist MARKET .30 DESIGN .25 BUILD .25 COST .20, all hard gates, minimum individual 3.0 and advantage +0.25; R014 worker9 DESIGN FAILED missing two authentic reports, original non-Pro Reviewer15 FINISHED/nonrevivable. R017 source/keys original champion and scores unchanged. No vendor/owner contact, physical mockups, sample purchases, supply offers, 1527 substituted measurements, Revit/Smartsheet/Git writes, new commission or approval. All original material release flags FALSE. Entire 13-room objective OPEN.
""")

# Every new signed file SHA and bytes, historical immutable predecessors
# including R41 and R42 already verified before signer is invoked.
lineage=dict(json.loads((B/PRE["R42_FULL"][0]).read_text(encoding="utf-8"))["predecessor_signed_file_hashes"])
lineage.update({k:h for k,(p,h) in PRE.items()})
meta=dict(round=43,date_local="2026-11-06",formal_board_round=17,
 phase="FULL_ARCHITECTURAL_NICHE_FOCAL_3IN_PIER_FIELD_SECTION_GC_13ROOM_UNRELEASED",
 predecessor_signed_file_hashes=lineage,
 focus_rooms=list(F),actual_original_13room_count=13,actual_original_26physical_instances=26,
 original_27_material_rows=27,original_25_W_elevations=25,original_65_trade_actions=65,
 original_R31_13_wet_lab_roles=13,original_R31_50_wall_witnesses=50,original_R31_26_physical_witnesses=26,
 historic_material_ONLY_four_unit_USD="23572.44",historic_original_15pct_waste_in_gross_once=True,
 original_four_focus_old_material_only_included_USD=str(focuscost),
 historical_Sandstone_already_included_USD="358.92",historical_Cortar_Grey_already_included_USD="1116.46",
 historical_Caviar_already_included_USD="1163.32",historical_powder_already_included_USD="2159.30",
 comps_listing_entries=14,comps_independent_buildings=9,old_town_primary_market=True,
 new_hard_niche_pier_sensitivity_and_location_trials=len(Piers),new_individual_aperture_plus_returns_quantities=len(Open),
 new_maker_supported_architecture_zone_decision_trees=len(Concept),
 new_POINT_four_plane_Z_source_hypothetical_slopes=len(PAN),
 new_actual_GC_field_and_edge_option_controls=len(Scope),
 new_physical_1to1_and_nine_trade_shop_sections=len(Shop),
 new_original_and_candidate_individual_maker_wet_matrix=len(Maker),
 new_physical_instance_control=len(WIT),new_all_13room_release_count=len(roomg),
 source_material_to_GC_quote_rows=len(source),eight_trade_sequential_steps=len(seq),
 new_illustrated_source_pier_sections=4,
 original_OWNER_selection_changed=False,certified_NATIVE_1529_geometry=False,
 authentic_factory_current_exact_WET_WALL_and_independent_WET_NICHE_all_approved=False,
 original_exact_numeric_raw_wet_LEVEL_and_independent_POINT_LINEAR_PAN_labs_complete=False,
 selected_original_Drain_tub_flange_membrane_factory_supported_complete=False,
 original_PH3_TX3_TUB_vs_WALKIN_owner_resolved=False,
 current_Chicago_SKU_color_finish_lot_usable_carton_and_GC_full_installed_bid_received=False,
 old_historic_original_invoice_PAID_returnable_material_and_change_order_approved=False,
 actual_1to1_built_mockups_or_renders_produced=False,
 original_four_authentic_BLIND_specialist_reports_complete=False,
 original_standing_nonPro_reviewer_GLOBAL_DONE=False,
 owner_approved=False,architect_approved=False,plumber_approved=False,waterproofing_approved=False,
 installer_approved=False,supplier_approved=False,GC_approved=False,purchaser_approved=False,
 purchase_authorized=False,global_DONE=False,
 files=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in sorted(PAY.items())])
assert len(PAY)==20,len(PAY)
D.mkdir(parents=True,exist_ok=False)
for name,data in sorted(PAY.items()):
 with (D/name).open("xb") as f:f.write(data)
(D/"MANIFEST.json").write_bytes((json.dumps(meta,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R43_PAYLOADS",len(PAY),"R43_MANIFEST_SHA",hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest())
