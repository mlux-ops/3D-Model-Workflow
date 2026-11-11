"""R41 complete eight-unit, four-bath architectural wet composition and shop package.
Source geometry is drawing provisional, never certified 1529. All materials conditional.
One-time additive, with immutable predecessor SHA+byte controls; no model or vendor writes.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from collections import Counter
from html import escape as xml_escape
import hashlib, json, csv, io, math

B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room"
assert not D.exists(),"R41 output exists; one-time creator must not be rerun"
PRE={
 "R39_FULL":("deliverables/integrated-r39-ph3-ph4-tx3-wet-wall-drain-assembly-design-and-13room-procurement/MANIFEST.json","34b6f733e97cbb392605f97063f4b5972412d881f00a7728902187b8c6af431e"),
 "R40_FULL":("deliverables/integrated-r40-conditional-soho-ivory-sandstone-same-sku-lot-13room-GC/MANIFEST.json","ce61454e4f31b7021829ee14bc734fab82f6bb4a0025805d43eb22f939dadc39"),
 "R37_FULL":("deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement/MANIFEST.json","985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"),
 "R35_FULL":("deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json","75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"),
 "R36_SOURCE":("state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json","9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"),
 "R30_FULL":("deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json","5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"),
 "R33_FULL":("deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json","a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e")
}
for key,(path,sha) in PRE.items():
 assert hashlib.sha256((B/path).read_bytes()).hexdigest()==sha,key
P40=json.loads((B/PRE["R40_FULL"][0]).read_text(encoding="utf-8"))
P39=json.loads((B/PRE["R39_FULL"][0]).read_text(encoding="utf-8"))
assert P40["owner_approved"] is False and P40["purchase_authorized"] is False
assert P39["global_DONE"] is False
def readcsv(path):
 with (B/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
old=readcsv("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
w25=readcsv("deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
a65=readcsv("deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
l13=readcsv("research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
u26=readcsv("research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
w50=readcsv("research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
rooms=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(old),len(w25),len(a65),len(l13),len(u26),len(w50),len(rooms))==(27,25,65,13,26,50,13)
assert sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert sum(x["historic_niche_excluded_no_scope"]=="TRUE" for x in old)==2
orig={(x["room"],x["source_surface"]):x for x in old}
wall={(x["room"],x["wall"]):x for x in w25}
FOCUS=("PH-BATH3","PH-BATH4","TX-BATH3","TX-BATH4")
G={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in FOCUS}
PL={r:json.loads((B/"rooms"/r/"plumbing.json").read_text(encoding="utf-8")) for r in FOCUS}
assert all(len(G[r]["revit_room_numbers"])==2 and len(G[r]["tiled_walls"])==3 for r in FOCUS)
assert all((r,x) in wall for r in FOCUS for x in ("W1","W2","W3"))
assert all((r,s) in orig for r in FOCUS for s in ("wall","floor","accent"))
for r in FOCUS:
 selected={x["model_or_sku"] for x in PL[r]["fixtures"]}
 if r=="PH-BATH3":assert "DT062412" in selected
 elif r in ("PH-BATH4","TX-BATH3"):assert "BT062415-BNX" in selected
 else:assert {"15758701","72411701","700332000000090"} <= selected

URL={
 "SOHO_BLUE":"https://www.elmsurfaces.com/product/soho-blue",
 "SOHO_IVORY":"https://www.elmsurfaces.com/product/soho-ivory",
 "SOHO_EMERALD":"https://www.elmsurfaces.com/product/soho-emerald",
 "NOHO_EMERALD":"https://www.elmsurfaces.com/product/noho-emerald",
 "NOHO_IVORY":"https://www.elmsurfaces.com/product/noho-ivory",
 "CORTAR_CHARCOAL":"https://www.elmsurfaces.com/product/cortar-charcoal",
 "TONES_OPAL":"https://www.elmsurfaces.com/product/opal-tones",
 "TONES_EMERALD":"https://www.elmsurfaces.com/product/emerald-tones",
 "TONES_SANDSTONE":"https://www.elmsurfaces.com/product/sandstone-tones",
 "CORTAR_BONE_RIBBED":"https://www.elmsurfaces.com/product/cortar-bone-ribbed",
 "CLARA_CAVIAR":"https://traditionsintile.com/project/clara/",
 "SCHLUTER_TUB":"https://www.schluter.com/schluter-us/en_US/showers/shower_with_bathtub",
 "SCHLUTER_KERDI":"https://www.schluter.com/schluter-us/en_US/showers",
 "HANSGROHE_TALIS":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-with-diverter-72411701",
 "HANSGROHE_ECOSTAT":"https://www.hansgrohe-usa.com/articledetail-ecostat-s-thermostatic-trim-with-volume-control-and-diverter-15758001"
}
R={
 "PH-BATH3":dict(copies=G["PH-BATH3"]["revit_room_numbers"],program="OWNER TUB vs WALKIN UNSELECTED",
  selected="Hansgrohe Chrome shower; Delta DT062412 Chrome 4-inch POINT only if owner WALKIN; PH basin UNSELECTED",
  original="Tones Opal 2x20 Glossy wet WALL: exact individual wet permission NOT verified",
  niche="Tones Sandstone 2x20 Glossy archived wet listed; exact niche system/shop unverified",
  hold="OPAL_EXACT_WET_WALL_ABSENT",
  options=[
    dict(id="PH3_A",name="Saturated blue linear",color="ELM Soho Blue 2x10 Glossy",evidence=URL["SOHO_BLUE"],finish="Glossy",
         nominal=9.5,orientation="horizontal",accent="#447b9c",scope="FULL_WET_W1W2W3",value="Horizontal low-height joint rhythm frames existing warm Sandstone niche; Hansgrohe Chrome remains crisp",risk="Color change from original Opal plus smaller joints/more labour, unique Blue lot"),
    dict(id="PH3_B",name="Soft ivory vertical sanctuary",color="ELM Noho Ivory 2x10 Matte",evidence=URL["NOHO_IVORY"],finish="Matte",
         nominal=9.5,orientation="vertical",accent="#dbd1bc",scope="FULL_WET_W1W2W3",value="Matte vertical wet field, reduced glare, strong blue-gray/dry accent only if a true dry wall exists",risk="Major palette change versus Opal and niche Sandstone, dry wall must be verified before preserving Opal")]),
 "PH-BATH4":dict(copies=G["PH-BATH4"]["revit_room_numbers"],program="SELECTED WALKIN; NO TUB",
  selected="Brizo BT062415-BNX Brilliance Black Onyx 4-inch SQUARE POINT, independent four-plane shower PAN and LEVEL",
  original="Cortar Bone Ribbed 24x48 RELIEF wet WALL: exact individual wet permission NOT verified",
  niche="Clara Tierra Madre Caviar 2x8 exact wet NICHE item listing absent",
  hold="RIBBED_WALL_AND_CAVIAR_NICHE_ABSENT",
  options=[
    dict(id="PH4_A",name="Monolithic glossy ivory",color="ELM Soho Ivory 2x10 Glossy",evidence=URL["SOHO_IVORY"],finish="Glossy",
         nominal=9.5,orientation="vertical",accent="#e5d7bb",scope="FULL_WET_W1W2W3_AND_CONDITIONAL_SAME_NICHE",value="Continuous ivory vertical ribs of light contrast selected Black Onyx; same product niche only if item and factory waterproof system approved",risk="Entire original wet Ribbed and Caviar replacement, extra returns/cut and current lots unknown"),
    dict(id="PH4_B",name="Calm matte mineral",color="ELM Noho Ivory 2x10 Matte",evidence=URL["NOHO_IVORY"],finish="Matte",
         nominal=9.5,orientation="horizontal",accent="#c8c4b8",scope="FULL_WET_W1W2W3_AND_CONDITIONAL_SAME_NICHE",value="Matte linear field and restrained niche for Black Onyx; Bone Ribbed only on a physically verified separate DRY feature wall",risk="Noho MATTE not interchangeable with R40 Soho GLOSS lot, premium large new wet wall labour and owner choice")]),
 "TX-BATH3":dict(copies=G["TX-BATH3"]["revit_room_numbers"],program="OWNER TUB vs WALKIN UNSELECTED",
  selected="Brizo BT062415-BNX Black Onyx SQUARE 4-inch POINT only future WALKIN",
  original="Tones Emerald 2x20 Glossy wet WALL archived maker PASS, current exact live SKU/app unconfirmed",
  niche="Tones Sandstone 2x20 Glossy archived wet listed, separate system approval",
  hold="TONES_EMERALD_CURRENT_EXACT_ITEM_REFRESH_MISSING",
  options=[
    dict(id="TX3_A",name="Glazed emerald focus",color="ELM Soho Emerald 2x10 Glossy",evidence=URL["SOHO_EMERALD"],finish="Glossy",
         nominal=9.5,orientation="vertical",accent="#317565",scope="FULL_WET_W1W2W3",value="Full-height vertical emerald focal W1 with cleaner return bonds and the existing warm Sandstone niche",risk="New factory family/lot vs Tones Emerald; glossy glare and niche face sequencing"),
    dict(id="TX3_B",name="Muted emerald horizontal",color="ELM Noho Emerald 2x10 Matte",evidence=URL["NOHO_EMERALD"],finish="Matte",
         nominal=9.5,orientation="horizontal",accent="#497663",scope="FULL_WET_W1W2W3",value="Quiet matte green horizontal stack and Sandstone niche, Brizo Black Onyx contrast",risk="Matte not same SKU as Soho gloss, separate cleaning/sample/quote and bond")]),
 "TX-BATH4":dict(copies=G["TX-BATH4"]["revit_room_numbers"],program="SELECTED DURAVIT TUB; NO TILED SHOWER PAN",
  selected="Duravit 700332000000090 tub; Hansgrohe Matte White 15758701 thermostatic trim, 72411701 Talis S diverter spout, 01850181 iBox rough; incompatible pressure-balance-only spout hold",
  original="Cortar Charcoal FLAT Soft wall; maker individual Charcoal product lists Wet Areas plus Soft/AntiSlip, exact 24x48 Soft SKU/finish coupling still unverified",
  niche="Clara Tierra Madre Caviar 2x8 exact wet NICHE listing absent",
  hold="CAVIAR_NICHE_ABSENT_AND_15758701_VS_72411701_CONTROL_CONFLICT",
  options=[
    dict(id="TX4_A",name="Contrast inset on dark stone",color="ELM Soho Ivory 2x10 Glossy",evidence=URL["SOHO_IVORY"],finish="Glossy",
         nominal=9.5,orientation="horizontal",accent="#ebdfc7",scope="NICHE_ONLY; RETAIN_ORIGINAL_CHARCOAL_FLAT_WET_WALL_CONDITIONALLY",value="Preserve dark Cortar Charcoal surround and selected matte-white fixtures; glossy ivory inset increases niche visibility",risk="Current exact flat Charcoal Soft wet application evidence plus Caviar-to-Soho niche and tub flange/corner still pending"),
    dict(id="TX4_B",name="Light-diffuse matte surround",color="ELM Noho Ivory 2x10 Matte",evidence=URL["NOHO_IVORY"],finish="Matte",
         nominal=9.5,orientation="vertical",accent="#d6d1c6",scope="FULL_TUB_W1W2W3_AND_NICHE_CONDITIONALLY",value="Light matte 3-wall tub enclosure/niche with Matte White Hansgrohe and Duravit tub, quieter than contrast option",risk="Full original Charcoal wall replacement, larger GC labour and need separate owner-approved sample, no blending with Soho Ivory gloss")])
}
assert len(R)==4 and sum(len(r["options"]) for r in R.values())==8
PAY={}
def emitcsv(name,rows):
 assert rows and len({tuple(x.keys()) for x in rows})==1,(name,len(rows))
 s=io.StringIO(newline="");wr=csv.DictWriter(s,list(rows[0]),lineterminator="\n")
 wr.writeheader();wr.writerows(rows)
 PAY[name]=s.getvalue().encode("utf-8-sig")
def emitmd(name,contents):PAY[name]=(contents.strip()+"\n").encode("utf-8")
def emitxml(name,contents):PAY[name]=contents.encode("utf-8")
def fmt(x):return f"{float(x):.4f}"
def money(x):return f"{Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP):.2f}"
assert not any((B/"rooms"/r/"board/round-041").exists() for r in FOCUS)

# Primary design work: eight truly distinct, authored compositions, never
# scored as a new blind board or owner-approved substitution.
design=[]
for room,info in R.items():
 for opt in info["options"]:
  design.append(dict(room=room,neutral_owner_concept_id=opt["id"],concept_name=opt["name"],
   selected_original_tile_and_compliance_hold=info["original"],original_individual_niche_gate=info["niche"],
   proposed_exact_maker_product_display=opt["color"],manufacturer_exact_product_page=opt["evidence"],
   evidence_date="2026-11-06",factory_nominal_size_in="2 x 10",
   product_listed_wet_WALL_on_individual_live_page="TRUE",
   product_exact_manufacturer_ORDER_SKU_color_lot_caliber="UNVERIFIED",
   actual_tub_or_shower_niche_membrane_system_APPROVED="FALSE",
   nominal_body_mm=fmt(opt["nominal"]),factory_finish=opt["finish"],
   visual_direction=opt["orientation"]+"; "+opt["value"],
   scope_wet_W1W2W3_or_niche_only=opt["scope"],
   selected_fixture_and_owner_program=info["selected"]+"; "+info["program"],
   observed_risk_and_material_tradeoff=opt["risk"],
   exact_original_LEVEL_wet_numeric_DCOF="MISSING",
   separate_exact_original_POINT_PAN_numeric_wet_DCOF="N_A_TUB" if room=="TX-BATH4" else "MISSING_IF_WALKIN",
   real_1529_curtain_glass_niche_valve_XY_and_wet_zone_boundary="",
   formal_R017_private_mapping="UNTOUCHED",four_authentic_critic_scores="NULL",
   owner_approved="FALSE",architect_approved="FALSE",manufacturer_WP_approved="FALSE",
   installation_released="FALSE",purchase_authorized="FALSE"))
emitcsv("R41_8_NEUTRAL_ARCHITECTURAL_TILE_COMPOSITIONS_UNSCORED_AND_UNSELECTED.csv",design)

# NEW R41: robust design datum instead of R39's one-width theoretical tile grid.
# This explicitly finds source-based end courses that remain buildable over a
# hypothetical +/-0.25in field-variation envelope; no real field tolerance
# or maker joint/caliber is asserted.
fit=[]
for room,inf in R.items():
 for opt in inf["options"]:
  for w in ("W1","W2","W3"):
   width=float(wall[room,w]["source_width_in_UNVERIFIED"])
   height=float(wall[room,w]["source_tiled_height_in_UNVERIFIED"])
   horiz=2. if opt["orientation"]=="vertical" else 10.
   vertical=10. if opt["orientation"]=="vertical" else 2.
   for joint in (.125,.1875):
    raw=math.floor((width-joint)/(horiz+joint))
    candidates=[]
    for n in range(max(0,raw-3),raw+2):
     edges=[(u-n*horiz-(n+1)*joint)/2 for u in (width-.25,width,width+.25)]
     valid=all(0<=v<=horiz for v in edges)
     cutpass=(horiz<3. or min(edges)>=3.)
     score=min(min(edges),horiz-max(edges))
     candidates.append((valid,cutpass,score,n,edges))
    valid=[c for c in candidates if c[0]]
    chosen=max(valid,key=lambda x:(x[1],x[2])) if valid else max(candidates,key=lambda x:x[2])
    _,focalpass,score,n,edges=chosen
    wlo,wbase,whi=edges
    short="N_A_NATIVE_2IN_AXIS" if horiz<3 else "PASS_ALL_WIDTH_VARIATIONS" if focalpass else "FAIL_FOCAL_REQUIRE_REVISIT_JOINT_OR_DATUM"
    # Use paired height phase shift to distinguish first/final course. Actual
    # actual niche sill/head elevations dictate after 1529 survey.
    nvert=max(0,math.floor((height-joint)/(vertical+joint)))
    upper=(height-nvert*vertical-(nvert+1)*joint)/2
    fit.append(dict(room=room,option_id=opt["id"],source_wall=w,
     source_width_in_UNVERIFIED=fmt(width),source_height_in_UNVERIFIED=fmt(height),
     tile_LONG_in_nominal="10",tile_SHORT_in_nominal="2",
     orientation=opt["orientation"],horizontal_tile_FACE_in=fmt(horiz),
     vertical_tile_FACE_in=fmt(vertical),hypothetical_joint_in=fmt(joint),
     hypothetical_half_in_total_FIELD_width_envelope_in="+/-0.25",
     nominal_full_tiles_selected=n,
     nominal_balanced_left_and_right_cut_in=fmt(wbase),
     robust_min_left_right_cut_if_WIDTH_minus_quarter=fmt(wlo),
     robust_max_left_right_cut_if_WIDTH_plus_quarter=fmt(whi),
     three_in_focal_cut_requirement=short,
     vertical_center_full_courses=nvert,
     top_and_bottom_balanced_course_cut_in=fmt(upper),
     actual_calibrated_factory_face_in="UNKNOWN",actual_maker_approved_joint_in="UNKNOWN",
     actual_true_1529_valve_centerline_XY_niche_axis_and_glass="",
     signed_1to1_layout_approval="FALSE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(fit)==48
emitcsv("R41_48_FIELD_WIDTH_SENSITIVITY_CONTROLLED_W1W2W3_FOCAL_TILE_DATUM_OPTIMIZER.csv",fit)

# New field coordinate dependencies. All x/y measured from finished clear wall
# origins, NEVER made up from neighboring 1527 geometry. Separate tub and point.
deps=[]
for room,inf in R.items():
 for copy in inf["copies"]:
  for w in ("W1","W2","W3"):
   original=wall[room,w]
   deps.append(dict(room=room,physical_copy=copy,wall=w,
    source_width_in_unverified=original["source_width_in_UNVERIFIED"],
    source_tiled_height_in_unverified=original["source_tiled_height_in_UNVERIFIED"],
    requested_true_1529_inside_finish_to_finish_WIDTH_in="",
    requested_true_1529_FINISHED_height_in="",
    requested_true_1529_corner_square_plumb_flatness_and_substrate_variance="",
    requested_door_window_glazing_axis_true_XY_openings_and_return_depths="",
    requested_actual_NICHE_count_centerline_XY_width_height_depth_and_backing="",
    requested_genuine_wet_to_certified_DRY_splash_boundary_XY="",
    requested_selected_VALVE_spout_escutcheon_rough_centerline_XY_to_finished_wall="",
    requested_membrane_backer_tile_fillet_and_movement_corner_height="",
    requested_floor_LEVEL_pan_OR_tub_flange_threshold_rough_elevations="",
    requested_original_GC_issued_witness_drawings_and_photo_label="",
    source_wall_references_original_25_walls="TRUE",
    rough_coord_1527_NOT_1529="TRUE",
    actual_1529_field_verified="FALSE",
    architect_shop_signature="FALSE",plumber_wet_seal_signature="FALSE",
    owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(deps)==24
emitcsv("R41_24_PHYSICAL_WALL_COORDINATE_AND_SECTION_DEPENDENCY_SURVEY_REGISTERS.csv",deps)

# Niche and wall finished plane: factory body identity is explicit but trim
# offset requires substrate/membrane/bedding and measured valve rough.
planes=[]
for room,inf in R.items():
 for opt in inf["options"]:
  for copy in inf["copies"]:
   # These alternate assemblies are engineering pathways, not warranty or
   # approval for the selected Brizo/Delta drain.
   for assembly in ("SHEET_WATERPROOFING_OVER_APPROVED_SUBSTRATE",
                    "FACTORY_WATERPROOF_PANEL_WITH_APPROVED_SEAM_AND_PENETRATION"):
    original_niche=13. if room in ("PH-BATH4","TX-BATH4") else None
    nom_delta=(opt["nominal"]-original_niche) if original_niche is not None else None
    planes.append(dict(room=room,physical_copy=copy,concept_id=opt["id"],wet_assembly_path=assembly,
     candidate_wall_body_nominal_mm=fmt(opt["nominal"]),
     original_CAVIAR_niche_body_nominal_mm=fmt(original_niche) if original_niche is not None else "N_A_ORIGINAL_SANDSTONE",
     niche_to_alt_TILE_BODY_only_delta_mm=fmt(nom_delta) if nom_delta is not None else "NOT_COMPARABLE",
     formula_source_FINISHED_face="STUD+BACKER_old+MEMBRANE_old+COMPRESSED_MORTAR_old+TILE_BODY_old",
     formula_proposed_FINISHED_face="STUD+BACKER_new+MEMBRANE_new+COMPRESSED_MORTAR_new+TILE_BODY_new",
     formula_delta_FINISHED_plane="(BACKER_new-BACKER_old)+(MEMBRANE_new-MEMBRANE_old)+(COMPRESSED_MORTAR_new-COMPRESSED_MORTAR_old)+(TILE_BODY_new-TILE_BODY_old)",
     actual_factory_backer_and_membrane_tested_assembly_approved="FALSE",
     actual_selected_Brizo_Delta_POINT_bonding_approved="FALSE",
     actual_Duravit_tub_flange_hansgrohe_rough_approved="FALSE",
     actual_true_tile_caliber_rough_service_clearance_glass_profile_deep_mm="",
     no_invented_MORTAR_compensation_rule="TRUE",
     need_measured_1to1_corner_profile_sill_and_valve_escutcheon="TRUE",
     architect_watertight_system_signed="FALSE",
     owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(planes)==32
emitcsv("R41_32_OPTION_SPECIFIC_FINISHED_WALL_NICHE_SUBSTRATE_MEMBRANE_VALVE_PLANE_STACKS.csv",planes)

# Four different wet-detail engineering critical joints per actual unit, not a
# claim of prefabricated physically installed components. Two independent
# system paths from published Schluter background remain only candidates.
details=[]
for room,inf in R.items():
 for copy in inf["copies"]:
  for key in ("J01_SILL_TO_NICHE_BACK_AND_JAMB_WITH_RETURN",
              "J02_W1W2W3_EXTERNAL_AND_INTERNAL_MOVEMENT",
              "J03_VALVE_SPOUT_SHOWER_ARM_ESCUTCHEON_WP_BOOT",
              "J04_FLOOR_WALL_PAN_DRAIN_CURB_OR_TUB_FLANGE"):
   kind="TUB_FLANGE_NO_PAN" if room=="TX-BATH4" else "WALKIN_POINT_ONLY" if room=="PH-BATH4" else "OWNER_TUB_OR_WALKIN_POINT_BRANCH_PENDING"
   details.append(dict(room=room,physical_copy=copy,section_id=key,
    program_gate=kind,original_fixed_fixtures=inf["selected"],
    exact_individual_WET_WALL_permitted_source_product="UNVERIFIED_OR_CONDITIONAL_ONLY",
    exact_individual_WET_NICHE_and_SILL_membrane_and_tile_system="UNVERIFIED",
    manufacturer_system_reference=URL["SCHLUTER_TUB"] if room=="TX-BATH4" else URL["SCHLUTER_KERDI"],
    reference_only_NOT_approved_Brizo_Delta_drain_or_owner_substitution="TRUE",
    required_TRUE_1529_field_witness="Actual pretile substrate, opening, drain XY and Z, corner condition, glass and pipe centerline",
    required_SHOP_detail="Sealed backer+membrane overlap, niche back/2jambs/head/sill with positive inwards fall, factory trim leg + movement joints, selected fitting boot",
    bath_LEVEL_source_raw_numerical_wet_DCOF="MISSING",
    separate_point_PAN_raw_numerical_wet_DCOF="N_A_TUB" if room=="TX-BATH4" else "MISSING_OR_OWNER_TUB_N_A",
    actual_waterproofing_rough_compatibility_and_flood_WHEN_REQUIRED="FALSE",
    signed_1to1_built_test_and_photograph="FALSE",
    owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
    waterproof_approved="FALSE",installer_approved="FALSE",purchase_authorized="FALSE"))
assert len(details)==32
emitcsv("R41_32_PHYSICAL_BATH_AND_4_ACTUAL_CRITICAL_WP_NICHE_VALVE_POINT_OR_TUB_SECTIONS.csv",details)

# Each physical room gets construction-signable mutually exclusive branches.
# Bath3 tub v walkin inside v walkin outside original quote, PH4 walkin
# included/excluded (NO TUB), TX4 TUB only. Never price future PAN with old
# bath LEVEL factory rate and do not apply second 15% to original gross.
scope=[]
for room,inf in R.items():
 g=G[room]
 footprint=g["shower_or_tub_footprint"]
 pan_rectangle=Decimal(str(footprint["width"]["value"]))*Decimal(str(footprint["depth"]["value"]))
 gross=Decimal(orig[room,"floor"]["source_gross_sf_one_copy_waste_15pct_once"])
 source_net=g["floor_area"]["value"]
 source_net=str(source_net)
 programs=("OWNER_TUB_NO_TILED_PAN","OWNER_WALKIN_POINT_PAN_INCLUDED_IN_OLD_FLOOR_QUOTE","OWNER_WALKIN_POINT_PAN_EXCLUDED_FROM_OLD_FLOOR_QUOTE") if room in ("PH-BATH3","TX-BATH3") else ("SELECTED_WALKIN_POINT_PAN_INCLUDED_IN_OLD_FLOOR_QUOTE","SELECTED_WALKIN_POINT_PAN_EXCLUDED_FROM_OLD_FLOOR_QUOTE") if room=="PH-BATH4" else ("SELECTED_DURAVIT_TUB_NO_TILED_PAN",)
 for copy in inf["copies"]:
  for branch in programs:
   active="WALKIN" in branch
   excluded="EXCLUDED" in branch
   pan=pan_rectangle if active else None
   extra=pan*Decimal("1.10") if excluded else None
   branch_tasks=(
    "Owner exact tub SKU/flange/waste overflow, signed plumber rough and selected tub waterproof-wall-to-flange, NO tiled shower PAN" if not active else
    "Original old bath-floor QUOTE PAN inclusion evidence and factory item-specific small format PAN substitution/credit not proven" if not excluded else
    "New point PAN small-format floor plus waterproof bed/curb and full GC labor quote ONLY after old source excludes PAN"
   )
   scope.append(dict(room=room,physical_copy=copy,mutually_exclusive_program_and_quote=branch,
    owner_TUB_vs_WALKIN_selected=("WALKIN_FIXED" if room=="PH-BATH4" else "TUB_FIXED" if room=="TX-BATH4" else "FALSE_UNSELECTED"),
    original_floor_row=orig[room,"floor"]["source_row_id"],
    source_floor_one_copy_historical_GROSS_SF_15pct_already_once=str(gross),
    source_prior_bath_floor_NET_SF_PROVISIONAL_or_disputed=source_net+(" / PH4 27SF drawing vs 35SF owner unresolved" if room=="PH-BATH4" else ""),
    originally_quoted_two_copy_floor_material_only_USD=orig[room,"floor"]["historic_usd_two_copies"],
    source_rectangular_tub_or_pan_footprint_NET_SF_NOT_TRUE_POLYGON=fmt(pan_rectangle),
    shower_POINT_PAN_active= "TRUE_ONLY_IF_WALKIN" if active else "N_A_TUB",
    hypothetical_EXTRA_point_PAN_material_net_SF_only_if_EXCLUDED=fmt(pan) if excluded else "N_A_OR_INCL",
    hypothetical_NEW_separate_pan_GROSS_SF_at10pct_NEW_APPROVAL_ONLY=fmt(extra) if extra is not None else "N_A_NOT_PROVEN",
    extra_pan15pct_NOT_reapplied_to_original_floor="TRUE",
    actual_LEVEL_net_plus_separate_POINT_net_proven="FALSE",
    actual_original_quote_PAN_inclusion_source_contract="UNKNOWN",
    original_actual_paid_received_source_floors_and_RETURNABLE_stock="UNKNOWN",
    actual_selected_rough_drain_centerline_slope_and_membrane="",
    independent_exact_raw_NUMERIC_LEVEL_lab="MISSING",
    independent_exact_raw_NUMERIC_POINT_PAN_lab="MISSING" if active else "N_A_TUB",
    exact_new_small_format_point_PAN_SKU_color_finish="UNSELECTED" if active else "N_A",
    full_WALL_niche_and_tub_flange_or_PAN_construction_branch_tasks=branch_tasks,
    actual_1529_survey_and_plumbing_shop_signed="FALSE",
    owner_selection_approved="FALSE",architect_approved="FALSE",
    GC_cost_substitution_credit_approved="FALSE",purchase_authorized="FALSE"))
assert len(scope)==18
emitcsv("R41_18_MUTUALLY_EXCLUSIVE_OWNER_TUB_POINT_PAN_QUOTE_SCOPE_CONSTRUCTION_BRANCHES.csv",scope)

# A contractor can close R41 only by supplying measurements, not by
# approving a theoretical FULL wall historical gross/opening credit.
takeoffs=[]
for room,inf in R.items():
 h=float(wall[room,"W1"]["source_tiled_height_in_UNVERIFIED"])
 widths={w:float(wall[room,w]["source_width_in_UNVERIFIED"]) for w in ("W1","W2","W3")}
 old_gross=Decimal(orig[room,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])
 old_usd=Decimal(orig[room,"wall"]["historic_usd_two_copies"])
 for opt in inf["options"]:
  for copy in inf["copies"]:
   cut_scope="NICHE_ONLY_WALL_RETAINED" if opt["scope"].startswith("NICHE_ONLY") else "FULL_THREE_WALL_WET_FIELD_OWNER_OPTION"
   takeoffs.append(dict(room=room,physical_copy=copy,option_id=opt["id"],
    original_wall_SOURCE_row=orig[room,"wall"]["source_row_id"],
    new_owner_selected_scope=cut_scope,
    source_underdeducted_full_wall_NET_SF_before_actual_openings=fmt(sum(widths.values())*h/144),
    original_source_WALL_GROSS_SF_one_copy_original15pct_ONCE=str(old_gross),
    original_SOURCE_two_copy_wall_material_ONLY_USD=str(old_usd),
    original_quote_blended_tile_ONLY_rate_USD_per_GROSS_SF=fmt(old_usd/(old_gross*2)),
    original_niche_separate_source_row=orig[room,"accent"]["source_row_id"],
    actual_measured_W1_W2_W3_NET_including_door_window_negative_one="NULL",
    actual_count_niche_opening_FIELD_negative_WALL_SF_once="NULL",
    actual_positive_niche_BACK_2SIDES_TOP_SILL_tiled_SF="NULL",
    actual_true_LEVEL_or_point_PAN_slab_scope_separate="NULL",
    quantity_formula_WALL_NET="(SUM_W_actual*H_actual/144)-A_window-A_door-A_existingNICHE_ONCE-A_other_field_openings",
    quantity_formula_NICHE_NET="A_BACK+2*A_JAMB+A_HEAD+A_SILL; Niche original source line distinct from WALL field",
    quantity_formula_NEW_approved_GROSS="NET_MEASURED*(1+w_NEW_separately_approved) not old historical GROSS*1.15",
    original_wall_old_GROSS_may_include_covered_openings="UNRESOLVED_NOT_A_PAID_CREDIT",
    sensitivity_NET_SF_per_ONE_inch_IN_EACH_wall_width=fmt(h/144),
    sensitivity_NET_SF_per_ONE_inch_IN_all_three_wall_height=fmt(sum(widths.values())/144),
    unknown_actual_EXPOSED_EDGE_COUNT_AND_NICHE_PROFILE_LF="NULL",
    wall_to_membrane_tubflange_or_POINT_drain_full_installed_GC_quote_USD="NULL",
    old_issued_original_invoice_stock_returnable_material_credit_USD="NULL",
    current_chicago_alt_SKU_lot_case_price_tax_freight_ETA="NULL",
    change_order_or_price_savings_signed="FALSE",
    owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(takeoffs)==16
emitcsv("R41_16_OPTION_SPECIFIC_CONTRACTOR_NICHE_OPENINGS_FIELD_NET_GC_QUOTE_DERIVATIVES.csv",takeoffs)

# Per original 27 lines historical source already included, never reset old
# gross waste or invent a payable new material margin.
quote=[]
for x in old:
 room=x["room"]
 focus=room in R
 quote.append(dict(room=room,original_source_row=x["source_row_id"],surface=x["source_surface"],
  original_one_copy_GROSS_SF_15pct_once=x["source_gross_sf_one_copy_waste_15pct_once"],
  original_two_copy_historical_material_only_USD=x["historic_usd_two_copies"],
  original_SOURCE_historic_no_order_Primary_niche=x["historic_niche_excluded_no_scope"],
  R41_design_alt_exact_factory_product_if_OWNER_approved="; ".join(o["color"] for o in R[room]["options"]) if focus else "ORIGINAL_R39_R40_SOURCE_UNCHANGED",
  actual_owner_approved_material_change="FALSE",
  old_paid_received_installed_vs_short_shipped_vs_current_stock="NULL",
  old_original_usable_excess_material_returnable_credit="NULL",
  new_measured_1529_NET_and_new_owner_approved_waste="NULL",
  new_maker_current_SKU_color_finish_lot_usable_cartons="NULL",
  new_current_supplier_Chicago_unit_material_freight_tax_ETA="NULL",
  new_full_installed_GC_demo_membrane_valve_tub_or_point_glass_rough_profile_labor="NULL",
  original_waste_ALREADY_once_do_not_double_add="TRUE",
  original_niche_OPENING_and_NICHE_faces_separate_no_double_bill="TRUE",
  supplier_approved="FALSE",owner_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(quote)==27
emitcsv("R41_27_ORIGINAL_TILE_ROW_TO_CURRENT_MEASURED_SCOPE_AND_COMPENSATED_GC_QUOTE.csv",quote)

# Owner-facing distinct value levels, baseline GOOD must not be advertised as
# installable when original wet item approval remains deficient.
levels=[]
for room,inf in R.items():
 for copy in inf["copies"]:
  for tier in ("GOOD","BETTER","BEST"):
   o=inf["options"][0] if tier=="BETTER" else inf["options"][1] if tier=="BEST" else None
   levels.append(dict(room=room,physical_copy=copy,tier=tier,
    source_current_original=inf["original"]+"; "+inf["niche"],
    wet_wall_or_niche_tiling_concept="HISTORIC_VISUAL_REFERENCE_HOLD" if tier=="GOOD" else o["id"]+" "+o["color"]+" "+o["orientation"],
    design_quality_delta="Preserve existing identity without authority to install original unverified wet" if tier=="GOOD" else o["value"],
    construction_difficulty="ORIGINAL WET MAKER GATE FAIL/HOLD" if tier=="GOOD" else o["risk"],
    selected_fixture_program_unchanged=inf["selected"]+"; "+inf["program"],
    wet_WALL_individual_maker_item="ORIGINAL_ITEM_UNVERIFIED" if tier=="GOOD" else "LIVE_ITEM_WET_AREAS_LISTED_WALL_ONLY",
    wet_NICHE_individual_installed_system="UNVERIFIED",
    owner_budget_actual_current_supplier_material_price="NULL",
    GC_actual_rough_membrane_tile_labor_price_and_old_stock_credit="NULL",
    Old_Town_market_value_without_invented_buyer_premium="PH 2.8M / TX 2.7M; 14 comps, nine buildings, OT primary; no buyer premium",
    five_trade_owner_accepted_1to1_mockup="FALSE",
    selected_owner_alternative="FALSE",
    four_original_independent_SPECIALIST_acceptance="FALSE",
    formal_weighted_score="NULL",purchasing_authorized="FALSE"))
assert len(levels)==24
emitcsv("R41_24_SIX_EIGHT_PHYSICAL_GOOD_BETTER_BEST_DESIGN_EXECUTION_SCOPE.csv",levels)

# 8 original physical rooms with two camera and 1:1 sample requests each.
samples=[]
for room,inf in R.items():
 for copy in inf["copies"]:
  for view in ("E01_W1W2W3_TILE_FOCAL_COMPOSITION_AND_EXISTING_GLAZING",
               "E02_NICHE_SILL_VALVE_1TO1_MEMBRANE_CURB_OR_TUB_FLANGE",
               "E03_FINISHED_INGRESS_LEVEL_OR_POINT_PAN_THRESHOLD_AND_FIXTURE"):
   samples.append(dict(room=room,physical_copy=copy,source_truth_only="R17 provisional + R31 incomplete survey, NOT certified 1529",
    view_id=view,original_selected_plumbing=inf["selected"],original_program=inf["program"],
    conditionally_designed_option_A=inf["options"][0]["id"],conditionally_designed_option_B=inf["options"][1]["id"],
    candidate_exact_wet_WALL_color_product=inf["options"][0]["color"]+" OR "+inf["options"][1]["color"],
    source_niche_maker_wet_application=inf["niche"],
    owner_visual_acceptance="Full scale calibrated tile/gloss/grout, 1529 real niche back/sides/sill, approved trim, selected valve and 4-plane POINT or tub flange",
    no_invented_camera_actual_position_or_existing_render="TRUE",
    render_created="FALSE",physical_1to1_mockup_created="FALSE",actual_native_1529_fields_signed="FALSE",
    owner_approved="FALSE",architect_approved="FALSE",installer_approved="FALSE",purchase_authorized="FALSE"))
assert len(samples)==24
emitcsv("R41_24_ACTUAL_EIGHT_PHYSICAL_BATH_OWNER_CAMERA_AND_1TO1_MOCKUP_BRIEFS_UNPRODUCED.csv",samples)

def program(r):
 if r in R:return R[r]["selected"]+"; "+R[r]["program"]
 if r in ("PH-PRIMARY","TX-PRIMARY"):return "Original 48-inch Brizo Brilliance Black Onyx LINEAR drain, separate BR73480 rough; no Primary niches; original floor/WC/PAN quoted inclusion ambiguous"
 if r in ("PH-WC","TX-WC"):return "Parent Primary WC anti-slip floor inherited ONCE, no independent WC purchase; TX203A original location unplaced"
 if r in ("PH-BATH2","TX-BATH2"):return "Selected Duravit tub no tiled PAN, Hansgrohe Matte White PH2 / Chrome TX2; original bathing control/rough compatibility remains hold"
 if r=="PH-POWDER":return "Brizo T65722LF-GL Luxe Gold WALL faucet separate R65700 and RP72414GL; wood floor DRY feature wall"
 if r=="TX-POWDER":return "Competing original AXOR One 48140991 PGO wall CROSS versus Metropol 32526141 Brushed Bronze wall lever TRIM; 13622181 rough Metropol only, owner program undecided; wood floor"
 if r=="TX-POWDER2":return "Tecturis E 73072341 Brushed Black Chrome DECK, original basin UNSELECTED, no countertop drill, wood floor"
 raise AssertionError(r)
def gates(r):
 if r in ("PH-POWDER","TX-POWDER","TX-POWDER2"):return ("N_A_DRY_WALL","N_A_WOOD_FLOOR","N_A_NO_PAN")
 if r in ("PH-WC","TX-WC"):return ("N_A_WALL","PARENT_PRIMARY_LEVEL_MISSING_RAW_TEST","N_A_WC")
 if r in ("PH-BATH2","TX-BATH2","TX-BATH4"):return ("EXACT_WET_WALL_AND_NICHE","MISSING_EXACT_LEVEL_RAW","N_A_TUB")
 if r in ("PH-PRIMARY","TX-PRIMARY"):return ("EXACT_WET_WALL_NO_PRIMARY_NICHES","MISSING_EXACT_LEVEL_RAW","MISSING_INDEPENDENT_LINEAR_PAN_RAW")
 if r=="PH-BATH4":return ("RIBBED_WALL_AND_CAVIAR_NICHE_NOT_AUTHORIZED","MISSING_EXACT_LEVEL_RAW","MISSING_INDEPENDENT_POINT_PAN_RAW")
 return ("EXACT_OPAL_WALL_MISSING" if r=="PH-BATH3" else "EMERALD_PRIOR_WET_PASS_CURRENT_RECHECK","MISSING_EXACT_LEVEL_RAW","MISSING_IF_WALKIN_POINT_PAN_RAW")

TRADE=("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC","PURCHASER")
rel=[];sequenced=[]
for x in rooms:
 r=x["id"]
 cost=sum(Decimal(y["historic_usd_two_copies"] or 0) for y in old if y["room"]==r)
 WG,LG,PG=gates(r)
 rel.append(dict(room=r,original_status_unchanged=x["status"],original_champion_unchanged=x.get("champion_id") or "null",
  original_score_unchanged=str(x.get("champion_score")) if x.get("champion_score") is not None else "null",
  original_material_ONLY_historic_two_copy_USD=money(cost),original_program_and_fixture_source=program(r),
  original_individual_wet_WALL_and_NICHE_maker_requirement=WG,exact_original_raw_numeric_wet_LEVEL_gate=LG,
  exact_original_raw_numeric_wet_POINT_or_LINEAR_PAN_gate=PG,
  original_first_R31_13_lab_roles_50_walls_26_units_linked="TRUE",
  original_sourced_25_wall_65_action_27_material_rows_preserved="TRUE",
  R41_four_bath_field_and_shop={"PH-BATH3":"TUB_VS_WALKIN_OWNER_UNSELECTED","PH-BATH4":"SELECTED_WALKIN_POINT",
                                "TX-BATH3":"TUB_VS_WALKIN_OWNER_UNSELECTED","TX-BATH4":"DURAVIT_TUB_NO_PAN"}.get(r,"UNCHANGED_SOURCE_PREDECESSOR"),
  real_signed_1529_room_geometry="NULL",exact_current_factory_SKU_lot_carton_wet_app="NULL",
  complete_actual_installed_supplier_and_GC_bid_USD="NULL",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  waterproofing_approved="FALSE",tile_installer_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE",
  original_four_authentic_critic_reports="FALSE",independent_nonpro_reviewer_DONE="FALSE"))
 for index,t in enumerate(TRADE,1):
  task={
   "OWNER":"Select actual TUB vs WALKIN only if PH3/TX3; choose alternative TILE/finish/budget and actual basin where unselected; preserve all fixtures",
   "ARCHITECT":"Measure true 1529 W1/W2/W3, real openings/spray zones/actual niche pipe and glass, vertical levels and actual 3in focal cuts, sign shop",
   "PLUMBER":"Selected drain/rough as shower only, tub flange/waste separately, Hansgrohe TX4 thermostat vs pressure-balance-only spout conflict and rough service",
   "WATERPROOFING":"Individual exact wet WALL and NICHE application plus approved connected membrane, niche corners, drain flange and tub flange without leaks",
   "TILE_INSTALLER":"Exact ORIGINAL numeric wet LEVEL and independent LINEAR/POINT PAN tests as applicable; real tile calibrations, grout/joints, trims, 1:1 mockups and water inspection",
   "SUPPLIER":"Current exact orderable SKU-color-finish/lot/usable cartons, Illinois actual stock, supplier quote/freight, original paid/returnable inventory",
   "GC":"Separately reconcile original quoted vs real 1529 measured NET and already-included 15% once, demolition/waterproof/rough/trim labour, paid credit, signed CO",
   "PURCHASER":"Only after owner, architect, plumber, waterproofing, installer, supplier, GC and genuine four specialist/Reviewer governance authorization"
  }[t]
  sequenced.append(dict(room=r,sequence=index,trade=t,original_program=program(r),specific_hold_to_clear=task,
   exact_raw_LEVEL_and_independent_PAN_lab_roles=LG+"; "+PG,
   signed_evidence_and_true_1529_survey="NULL",
   original_2026_purchase_quote_and_real_stock_credit="NULL",
   all_eight_stage_RELEASE_authorized="FALSE",individual_trade_signed="FALSE",purchase_authorized="FALSE"))
assert len(rel)==13 and len(sequenced)==104
assert sum(Decimal(x["original_material_ONLY_historic_two_copy_USD"]) for x in rel)==Decimal("23572.44")
emitcsv("R41_13_ROOM_FULL_ORIGINAL_PLUMBING_PROGRAM_WET_APPLICATION_AND_PURCHASE_RELEASE.csv",rel)
emitcsv("R41_104_SEQUENTIAL_8_TRADE_SHOP_APPROVAL_GATES_ALL_FALSE.csv",sequenced)

physical=[]
for x in u26:
 room=x["room"]
 physical.append(dict(room=room,physical_copy=x["physical_copy_index"],
  original_R31_source_room_number=x["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"],
  source_original_program=program(room),original_lab_WALL_NICHE_LEVEL_PAN="|".join(gates(room)),
  new_R41_8_wet_room_focal_niche_valve_1to1_tolerance_section="REQUIRE_MEASURED_FOCUS_MOCKUP" if room in R else "UNCHANGED_R31_EXISTING_WITNESS",
  current_native_Revit_1527_not_true_1529="TRUE",actual_TRUE_1529_field_wall_and_service_openings="NULL",
  actual_maker_WET_NICHE_and_mortar_membrane_rough_assembly="NULL",
  exact_original_raw_numeric_wet_LEVEL_and_PAN_lab="NULL",
  manufacturer_current_wet_WALL_product_and_factory_lot_approved="FALSE",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  waterproof_approved="FALSE",installer_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(physical)==26
emitcsv("R41_26_ORIGINAL_UNIT_INSTANCE_MEASURED_SHOP_AND_MOCKUP_WITNESS_INTEGRATION.csv",physical)
walls=[]
for x in w50:
 room=x["room"]
 walls.append(dict(room=room,physical_copy=x["physical_copy"],wall=x["wall_reference"],
  original_R31_SOURCE_width_in_UNVERIFIED=x["prior_source_wall_width_in_UNVERIFIED"],
  original_R31_SOURCE_height_in_UNVERIFIED=x["prior_source_tiled_height_in_UNVERIFIED"],
  R41_four_room_new_DESIGN_positioning_and_joint_control="R41_WIDTH_ENVELOPE_AND_NICHE_COORDINATE_DATA" if room in R else "OLD_50_SOURCE_PRESERVED",
  original_R31_wall_records_NOT_overwritten="TRUE",
  actual_1529_measured_glass_valve_niche_and_waterproofing="NULL",
  field_approved_PAN_tubflange_point_or_linear_rough_elevation="NULL",
  original_individual_wet_WALL_NICHE_app_revalidated="FALSE",
  actual_1to1_tile_caliber_grout_movement_and_trim_approved="FALSE",
  owner_approved="FALSE",architect_approved="FALSE",purchaser_release="FALSE"))
assert len(walls)==50
emitcsv("R41_50_EXISTING_PROVISIONAL_WALL_REFS_ARCHITECT_TILE_SHOP_DELTA_AND_HOLD.csv",walls)

# Eight schematic source-based vector elevations. Tile tone/module is an
# architectural concept only; no fabricated niche or valve position.
def svgplate(room,info,option):
 widths=[float(wall[room,w]["source_width_in_UNVERIFIED"]) for w in ("W1","W2","W3")]
 h=float(wall[room,"W1"]["source_tiled_height_in_UNVERIFIED"])
 sc=3.; Y=102.; panel=h*sc
 totalheight=int(Y+panel+110)
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1050 {totalheight}">',
  '<rect width="1050" height="100%" fill="#f9faf7"/>',
  f'<text x="36" y="30" font-family="Arial" font-size="20" font-weight="bold" fill="#172b35">R41 {xml_escape(room)} - {xml_escape(option["name"])}</text>',
  '<text x="36" y="54" font-family="Arial" font-size="13" fill="#af553a">CONCEPT SOURCE ONLY - NOT field-verified 1529, owner-approved, manufacturer full-system-approved or built</text>',
  f'<text x="36" y="76" font-family="Arial" font-size="13" fill="#4f6069">{xml_escape(option["color"])} | 2x10in nominal | {xml_escape(option["orientation"])} concept</text>']
 x=42.
 for w,width in zip(("W1","W2","W3"),widths):
  bw=width*sc
  out.append(f'<rect x="{x:.1f}" y="{Y:.1f}" width="{bw:.1f}" height="{panel:.1f}" fill="{option["accent"]}" stroke="#24373e" stroke-width="1.6"/>')
  d=2. if option["orientation"]=="vertical" else 10.
  v=10. if option["orientation"]=="vertical" else 2.
  for n in range(1,80):
   xi=x+n*(d+.125)*sc
   if xi>=x+bw:break
   out.append(f'<line x1="{xi:.1f}" y1="{Y:.1f}" x2="{xi:.1f}" y2="{Y+panel:.1f}" stroke="#f5f6f1" stroke-width=".6"/>')
  for n in range(1,90):
   yi=Y+n*(v+.125)*sc
   if yi>=Y+panel:break
   out.append(f'<line x1="{x:.1f}" y1="{yi:.1f}" x2="{x+bw:.1f}" y2="{yi:.1f}" stroke="#f5f6f1" stroke-width=".6"/>')
  out.append(f'<text x="{x:.1f}" y="{Y-8:.1f}" font-family="Arial" font-size="13" font-weight="bold">{w} {width:.2f}in source</text>')
  out.append(f'<text x="{x:.1f}" y="{Y+panel+18:.1f}" font-family="Arial" font-size="12">H {h:.2f}in source</text>')
  x+=bw+22
 foot=Y+panel+45
 out.extend([
   f'<text x="36" y="{foot:.1f}" font-family="Arial" font-size="13" font-weight="bold" fill="#24373e">NICHE / PIPE / VALVE / GLASS / CURB: exact locations UNKNOWN; do not measure from diagram</text>',
   f'<text x="36" y="{foot+23:.1f}" font-family="Arial" font-size="12" fill="#4f6069">{xml_escape(info["program"])}; original fixture and independent wet-floor gates unchanged</text>',
   f'<text x="36" y="{foot+43:.1f}" font-family="Arial" font-size="12" fill="#af553a">Actual factory calibrations, joint width, wall wet/dry boundaries and signed site geometry required</text></svg>'
 ])
 return "\n".join(out)
for room,info in R.items():
 for option in info["options"]:
  emitxml(f"R41_{option['id']}_SOURCE_PROVISIONAL_W1W2W3_SCHEMATIC_TILE_CONCEPT.svg",svgplate(room,info,option))

for room,info in R.items():
 width=[float(wall[room,w]["source_width_in_UNVERIFIED"]) for w in ("W1","W2","W3")]
 h=float(wall[room,"W1"]["source_tiled_height_in_UNVERIFIED"])
 a,b=info["options"]
 doc=f"""
# R41 {room} individual architectural wet-bath shop and construction decision plate

**SOURCE ONLY; no verified 1529 geometry, owner approval, completed mockup or permission to install.** Physical copies: {', '.join(info["copies"])}. Source W1/W2/W3 width {width[0]:.2f}/{width[1]:.2f}/{width[2]:.2f}in and height {h:.2f}in, original 25 source wall records, not a certified plan. Original room material: {info["original"]}; niche independently: {info["niche"]}; existing selected fixtures: {info["selected"]}; branch: {info["program"]}.

## Three visibly and technically differentiated directions

GOOD: retain original owner design identity for comparison only; original wet WALL/NICHE exact manufacturer authorization is incomplete and the historic design is NOT yet installable. BETTER: {a["name"]}, specific maker product {a["color"]} in {a["orientation"]} 2x10 format (individual Wet Areas listing: {a["evidence"]}). Visual: {a["value"]}. Actual risk: {a["risk"]}. BEST: {b["name"]}, specific maker product {b["color"]} in {b["orientation"]} 2x10 format (individual Wet Areas listing: {b["evidence"]}). Visual: {b["value"]}. Actual risk: {b["risk"]}. Each changes true material/color/finish/orientation/coverage—not simply a new price tier. All maker current orderable codes, WET NICHE system support, original owner selection, factory lots/usable cartons and installed GC bid remain unverified.

## Source dimensional elevations, cuts, movement and edge

Two independent R41 SVG plates show only W1/W2/W3 abstract source-based tile composition; not actual pipe/niche/camera coordinates. Tile-origin MUST be reset at actual field-surveyed 1529 focal fixture/spray axis. Balanced cut formula = (actual finish width - N*factory calibrated tile face - (N+1)*manufacturer-approved joint)/2. R41 nominal two-joint, width +/-0.25in stress sensitivity is hypothetical only, not a factory grout rule or actual building tolerance. Preserve focal cuts >=3in on long-axis tile pieces; inherent 2in short-axis is separately classed N/A and must instead be laid out as a real-caliber module. Show true W1/W2/W3 glazing, corner, valve, tile top termination, and actual 1/1 wall-to-niche and outside edge cut before release. Field-confirm all exposed profile length, trim depth, substrates and movement joints.

## Wet section 01: substrate to manufacturer approved niche and tile

Field-confirm studs, backing and viable substrate. Choose ONE actual tile/drain-compatible factory waterproofing assembly and inspect backer + seams + corner wrapping + valve/head pipe boots before setting. Install real compressed setting bed and calibrated tile; record actual finished-wall plane, allowable lippage and edge depth, separate original nominal tile body from actual overall assembly. For original Caviar nominal approx13mm vs proposed Soho/Noho approx9.5mm, tile BODY delta approx -3.5mm, not a permitted mortar correction. Draw niche back plus both returns, HEAD and inclined SILL with positive drainage to shower, no through-membrane accessory screws, corner movement and physically supported trim. Deduct real opening from surrounding WALL only once; separate historically quoted niche face/returns/sill scope. Exact wet WALL listing does not prove manufacturer-approved niche seam/corner membrane.

## Wet section 02: owner TUB versus POINT WALKIN and fixture rough

{info["selected"]}. {info["program"]}. PH3 and TX3 owner TUB versus WALKIN remains UNSELECTED. TUB branch requires owner-selected actual tub/flange/tub waste and overflow, water-sealed flange-to-backer and service clearance; tiled shower PAN N/A, original shower 4-inch square POINT drain is not a tub waste. WALKIN branch requires original selected point drain only as applicable, separate true four-plane SMALL FORMAT sloped shower PAN with independently tested exact RAW numeric wet DCOF, distinct original LEVEL lab, selected rough/bonding flange/membrane maker compatibility, independently resolved curb/threshold/glass attachment, slope at true drain XY and Z. PH4 fixed WALKIN BNX square POINT and independent four-plane PAN, never tub. TX4 selected Duravit tub/Hansgrohe Matte White and NO PAN; original 15758701 thermostat trim versus 72411701 diverter-spout pressure-balance-only compatibility conflict held until exact maker/architect/plumber signed program. No new fixture substitution authorized.

## Sequential measurable acceptance

Owner approves actual program and exact conditional finish; architect surveys TRUE native 1529 wall/niche/valve/opening/threshold coordinates (the available 1527 model is NOT 1529 evidence); plumber proves rough/tub flange/drain XY/Z, selected escutcheon seal and access; waterproof trade submits actual coherent manufacturer tested membrane/backer/corner/tub-flange-or-drain combination; tile installer confirms factory tile color/size/caliber and installed grout, 3in focal, movement, actual slab/pan/threshold slope and 1:1 fullsize mockup with real sill runoff and penetrations, plus exact separate ORIGINAL item-specific measured numeric LEVEL vs POINT PAN DCOF where applicable. Supplier confirms actual Chicago lot/shade/case/usable SF/cost/ETA without assumed pooling. GC reconciles original quoted gross 15percent waste ONCE, original paid/returned stock and separately new demo/finish/trim/WP/rough/installation labor, change order only after verified owner approval. Purchaser final signoff only after all other original authentic independent gates. No real samples/renders, signatures, PO, manufacturer approval or current supplier quote exist.

## Old Town market and owner viewing

Present the two SVG compositions side by side as unmeasured SCHEMATIC diagrams, then request verified 1529 1:1 wall+niche, selected fixture and threshold physical sample/camera briefs before rendering. Old Town PH approximately $2.8M/TX approximately $2.7M, comparable band $2.4M-$3.2M, 14 listing entries representing nine buildings; Lincoln Park/Gold Coast secondary. Prioritize visual restraint, cleaning/maintenance, trusted wet approvals and durable finishes; no inferred competitor tile or buyer premium.
"""
 emitmd(f"R41_{room}_DESIGN_FOCAL_ELEVATIONS_WET_NICHE_WP_FIXTURE_TOLERANCE_AND_OWNER_CHOICES.md",doc)

focus_subtotal=sum(Decimal(orig[r,s]["historic_usd_two_copies"]) for r in FOCUS for s in ("wall","floor","accent"))
assert focus_subtotal==Decimal("9124.72"),focus_subtotal
emitmd("START_HERE_R41_13ROOM_INTEGRATED_ARCHITECT_WET_SHOP_AND_OWNER_BOOK.md",f"""
# R41 Four wet bathrooms: architectural redesign and construction-release decisions

**FULL ADDITIVE, UNSCORED, NO RELEASE.** R39/R40 authenticated original artifacts preserved. R40's six Soho and ten Sandstone surfaces were conditional historical receiving, NOT actual factory same-lot allocations, measured installed offcuts or savings. Eight distinct R41 owner concepts are source-dimensioned W1/W2/W3 schematic vector SVGs (not verified 1529 model geometry or actual photographs), with deliberately omitted unverified niche/pipe/valve/glass X,Y. Eight owner GOOD reference / BETTER / BEST programs and eight physical instances PH3 307A/B, PH4 311A/B, TX3 207A/B, TX4 007A/B.

PH-BATH3 original Tones Opal wet WALL manufacturer individual approval missing. Conditional Soho Blue 2x10 Glossy HORIZONTAL blue/warm niche concept or distinctly Noho Ivory 2x10 MATTE VERTICAL low-glare light concept; Sandstone historical niche has separate wet installation gate. Hansgrohe Chrome shower, Delta Chrome DT062412 4in square POINT only owner WALKIN, TUB/WALKIN and PH basin owner UNSELECTED.

PH-BATH4 original Cortar Bone Ribbed wet WALL and Clara Caviar wet NICHE manufacturer exact authority missing. Conditional Soho Ivory Glossy 2x10 VERTICAL continuous ivory wet wall and niche or distinct Noho Ivory MATTE 2x10 HORIZONTAL, latter different factory finish/lot. Owner fixed WALKIN, Brizo BT062415-BNX Black Onyx square POINT, separate four-plane PAN and LEVEL; 35vs27SF bath floor and 214.4 vendor wall total unresolved nonpayable.

TX-BATH3 original Tones Emerald archived wet WALL pass, exact current item renewal missing. Conditional Soho Emerald Glossy 2x10 VERTICAL or Noho Emerald Matte 2x10 HORIZONTAL, different maker products/color finish lots, both with existing Sandstone niche independently approved in assembly. Original BNX Brizo square POINT only if owner WALKIN; TUB versus WALKIN UNSELECTED.

TX-BATH4 selected Duravit 700332000000090 tub and Hansgrohe Matte White; NO tiled PAN. Original Cortar Charcoal flat family listed Wet Areas, exact original Soft 24x48 variant/current identity must be checked, original Caviar wet NICHE not approved. LOW-SCOPE retain independently confirmed Charcoal wet wall, propose Soho Ivory Glossy 2x10 HORIZONTAL niche only; HIGH-SCOPE full tub wall and niche change to Noho Ivory MATTE VERTICAL; preserve actual tub/spout and 15758701 thermostat versus 72411701 pressure-balance-only diverter conflict, requiring maker-supported repair/rough and plumber/architect hold.

New technical scope includes 48 width-envelope focus cut checks +/-0.25in hypothetical against actual W1/W2/W3 1/8 or 3/16in illustrative grout; 24 physical wall true 1529 coordinate survey requests, 32 exact nominal tile vs partial backer/membrane/mortar/rough installed wall finished plane comparison formulas, 32 corner/niche/valve/POINT or tub-flange WP details; 18 mutually exclusive owner TUB vs WALKIN/PAN quote included or excluded construction branches; 16 true wall negative opening vs niche positive back/side/head/sill and GC quote derivative schedules. No false true 1529 survey, current maker approval, certified membrane/flange, numeric wet floor test, physical sample or executed camera. Contractor acceptance requires real field, calibrated tile, actual finish and physical 1:1 plus all trade signatures.

Four rooms' 12 historical material source rows USD {money(focus_subtotal)} material-only already INSIDE historic 13-room USD 23572.44 four-unit total with 15pct old waste ONCE. Original Sandstone USD358.92, Grey Soft USD1116.46, Caviar USD1163.32, powders USD2159.30 all included (not additive). Missing exact source actual original paid/returned stock and current supplier SKU/lot usable cartons Chicago installed GC full bid; theoretical openings or existing old PAN inclusion A/B cannot prove payable shortages or credits.

Original 13 room IDs, 27 historical material rows incl two excluded no-order Primary niches, 25 original W, 65 original trade actions, R31 13 wet lab roles, 50 wall witnesses, 26 actual physical room witnesses and new 104 eight-trade release gates, all FALSE. Preserve both original 48in BNX Brizo LINEAR Primary with separate BR73480 and no niches, WC floor inherited once; other two Duravit tub rooms PH2/TX2 NO tiled PAN with selected Hansgrohe finishes, all original powder WALL-vs-DECK faucet mounting and TX Powder2 basin UNSELECTED. Independent exact measured original raw numeric wet LEVEL vs LINEAR/POINT PAN tests required; manufacturer brochure thresholds not accepted. Tub-only PAN and wood dry powder floors N/A. Old Town primary PH2.8M/TX2.7M, 14 listing entries/nine buildings, $2.4M-$3.2M, LP/Gold Coast adjacent only, no buyer premium.

Formal board R017 frozen. Four original specialists MARKET .30, DESIGN .25, BUILD .25, COST .20, applicable hard gates, all individual >=3.0 and weighted +.25 before champions change. Original DESIGN worker9 missing R014 reports, sole original Reviewer15 FINISHED, no new seats, scoring or independent DONE. All owner/architect/plumber/WP/tile/supplier/GC/purchaser releases FALSE; Revit 1527 NOT evidence 1529, no emails/vendor contacts/samples/orders/physical renders/Git/model writes. Entire 13-room objective OPEN.
""")

lineage=dict(P40["predecessor_signed_file_hashes"])
lineage.update({key:sha for key,(_,sha) in PRE.items()})
meta=dict(round=41,date_local="2026-11-06",
 phase="NEW_FOUR_WET_BATH_ARCHITECTURAL_COMPOSITION_COORDINATE_SHOP_GC_13ROOM_INTEGRATED_UNRELEASED",
 predecessor_signed_file_hashes=lineage,focus_rooms=list(FOCUS),formal_board_round=17,
 original_13rooms=13,original_26physical=26,original_27material=27,original_25walls=25,
 original_65trades=65,original_R31_13labs=13,original_R31_50walls=50,original_R31_26instances=26,
 old_13room_material_only_USD="23572.44",old_original_gross_15pct_waste_already_ONCE=True,
 four_focus_12_original_rows_material_only_USD=money(focus_subtotal),
 Sandstone_included="358.92",Cortar_Grey_included="1116.46",Caviar_included="1163.32",Powders_included="2159.30",
 original_comps=14,distinct_buildings=9,
 eight_NEUTRAL_design_options=len(design),eight_schematic_vector_concepts=8,
 W1W2W3_joint_robust_cut_checks=len(fit),four_bath_true_site_wall_survey_inputs=len(deps),
 finished_wall_tile_rough_Z_stacks=len(planes),physical_critical_wet_sections=len(details),
 mutually_exclusive_owner_TUB_point_PAN_quote_branches=len(scope),
 source_WALL_opening_installation_COST_formula_controls=len(takeoffs),
 original_27line_GC_quote_matrix=len(quote),physical_owner_tiers=len(levels),
 unproduced_camera_mockup_requests=len(samples),all_13room_release=len(rel),
 sequential_eight_trade_holds=len(sequenced),source_26_instance_witness=len(physical),source_50_wall_witness=len(walls),
 actual_true_1529_model_measurements_verified=False,actual_owner_design_or_program_selected=False,
 original_all_individual_wet_WALL_and_NICHE_authorizations_received=False,
 exact_RAW_numeric_wet_LEVEL_and_independent_POINT_LINEAR_PAN_labs_received=False,
 approved_actual_factory_WP_tubflange_POINT_drain=False,
 authentic_1to1_physical_samples_or_renders_produced=False,
 current_factory_SKU_lot_usable_case_and_chicago_offer_received=False,
 original_paid_inventory_current_full_GC_bid_CO_signed=False,
 original_four_specialist_critiques_complete=False,original_nonpro_reviewer_DONE=False,
 owner_approved=False,architect_approved=False,plumber_approved=False,waterproof_approved=False,
 installer_approved=False,supplier_approved=False,GC_approved=False,purchaser_approved=False,
 material_reserved=False,purchase_authorized=False,global_DONE=False,
 files=[dict(path=k,bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in sorted(PAY.items())])
assert len(PAY)>=25,len(PAY)
D.mkdir(parents=True,exist_ok=False)
for name,data in sorted(PAY.items()):
 with (D/name).open("xb") as f:f.write(data)
(D/"MANIFEST.json").write_bytes((json.dumps(meta,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R41_PAYLOADS",len(PAY),"R41_MANIFEST_SHA",hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest())
