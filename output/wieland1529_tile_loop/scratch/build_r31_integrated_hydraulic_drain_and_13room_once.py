"""Create one-time ADDITIVE R31 integrated owner/architect/GC package.

Input: immutable R30 signed manifest + R31 preliminary SHA receipt and original R17.
The figures below are source-dimension and hypothetical sensitivity models, NOT
measured 1529 values or authorized substitutions. Do not rerun after success.
"""
from __future__ import annotations
import csv, hashlib, io, json, math
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"deliverables"/"integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity"
assert not OUT.exists(), "Integrated R31 already exists: do not overwrite."
HIST_DIR=ROOT/"deliverables"/"integrated-r17"
R30=ROOT/"deliverables"/"integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement"/"MANIFEST.json"
R30_HASH="5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"
R31=ROOT/"state"/"ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json"
R31_HASH="61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"
assert hashlib.sha256(R30.read_bytes()).hexdigest()==R30_HASH
assert hashlib.sha256(R31.read_bytes()).hexdigest()==R31_HASH
receip=json.loads(R31.read_text(encoding="utf-8"))
for x in receip["files"]:
    b=(ROOT/x["relative"]).read_bytes()
    assert len(b)==x["bytes"] and hashlib.sha256(b).hexdigest()==x["sha256"],x
def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
rooms=json.loads((ROOT/"state"/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
historical=read_csv(HIST_DIR/"R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
wallsource=read_csv(HIST_DIR/"R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
labsource=read_csv(ROOT/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
fieldsource=read_csv(ROOT/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
unitsource=read_csv(ROOT/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
assert (len(rooms),len(historical),len(wallsource),len(labsource),len(fieldsource),len(unitsource))==(13,27,25,13,50,26)
dollars=lambda x:Decimal(x["historic_usd_two_copies"] or "0")
assert sum(dollars(x) for x in historical)==Decimal("23572.44")
assert sum(not x["historic_usd_two_copies"] for x in historical)==2
focus=("TX-BATH4","PH-BATH2","PH-BATH4","TX-PRIMARY")
ROOM={r["id"]:r for r in rooms}
W={(r["room"],r["wall"]):r for r in wallsource}
SOURCE_FLOOR={x["room"]:x for x in historical if x["source_surface"]=="floor"}
assert len(SOURCE_FLOOR)==8
actual_unselected={"PH-BATH3","TX-BATH3"}

URL={
"spout_div":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-with-diverter-72411701",
"spout_plain":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-72410701",
"valve_source":"https://assets.hansgrohe.com/celum/web/hansgrohePriceBook2021USf01052Release.pdf",
"valve_pressure":"https://www.hansgrohe-usa.com/articledetail-ecostat-s-pressure-balance-trim-15739001",
"rough":"https://www.hansgrohe-usa.com/articledetail-ibox-universal-rough-with-service-stops-01850181",
"tub":"https://pro.duravit.us/pro/content/homepage/series/sizes/overview/products~402880943a1b6e1b013a1bd2b8e3005b.us-en.html?ncat=undefined&nser=1110&product=3169419",
"flange":"https://pro.duravit.us/pro/content/homepage/series/categories/overview/products~402880943a1b6e1b013a1bd2494e0047.us-en.html?ncat=accessories&nser=8002&product=105401",
"point":"https://www.brizo.com/bath/product/BT062415-BNX",
"linear":"https://www.brizo.com/bath/product/BT0734816-BNX",
"linearrough":"https://www.brizo.com/bath/product/BR73480",
"membrane":"https://www.schluter.com/schluter-us/en_US/Shower-System/Drains/Shower-Drains/Schluter-KERDI-DRAIN/p/KDIF4GRKTSCD17",
"bone":"https://www.elmsurfaces.com/product/cortar-bone",
"ribbed":"https://www.elmsurfaces.com/product/bone-ribbed-cortar",
"charcoal":"https://www.elmsurfaces.com/product/cortar-charcoal",
"caviar":"https://traditionsintile.com/project/clara/",
"soho":"https://www.elmsurfaces.com/product/soho-ivory",
}
FILES={}
def csvout(name,records):
    assert records,name
    fields=list(records[0])
    assert all(list(x)==fields for x in records),name
    s=io.StringIO(newline="")
    w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n")
    w.writeheader();w.writerows(records)
    FILES[name]=s.getvalue().encode("utf-8-sig")
def mdout(name,txt):
    FILES[name]=(txt.strip()+"\n").encode("utf-8")
def n4(x):return f"{x:.4f}"
def tf(x):return "TRUE" if x else "FALSE"

maker=[
("Hansgrohe","72411701","Talis S Matte White diverter TUB spout","ORIGINAL_SELECTED_PH2_TX4","For use with pressure balance valve ONLY; 1/2in female/3/4in male adapter","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_382_NOT_VENDOR_BID","NO_AUTOMATIC_THERMOSTATIC_COMPATIBILITY",URL["spout_div"]),
("Hansgrohe","15758701","Ecostat S Matte White thermostatic trim, volume and two-outlet diverter","ORIGINAL_SELECTED_PH2_TX4","2021 official maker book calls thermostat with diverter for TWO outlets; compatible listed iBox 01850181","HISTORIC_OFFICIAL_2021_PLUS_2026_RETAILER_ITEM","CURRENT_INSTALLED_PRICE_UNKNOWN","NOT_EQUAL_PRESSURE_BALANCE_SP0UT_BYPASS",URL["valve_source"]),
("Hansgrohe","01850181","iBox Universal 3/4in rough with stops","ORIGINAL_SELECTED_PH2_TX4","Factory universal rough; rough selection DOES NOT make different trims interchangeable without factory approved installation","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_228_NOT_VENDOR_BID","RETAIN_ONLY_IF_MAKER_APPROVES_MATCHED_TRIM",URL["rough"]),
("Hansgrohe","72410701","Talis S Matte White NON-DIVERTER TUB spout","UNSELECTED_CONDITIONAL_PATH_B","Factory current item called Tub Spout (no diverter), 1/2in female/3/4in male adapters; 3-outlet schedule requires independent 2-way/diverter plumbing design","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_321_NOT_VENDOR_BID","NO_AUTOMATIC_15758701_3_OUTLET_APPROVAL",URL["spout_plain"]),
("Hansgrohe","15739701","Ecostat S Matte White PRESSURE BALANCE trim","UNSELECTED_CONDITIONAL_PATH_C","2021 official maker Ecostat pressure balance has INTEGRATED BYPASS for diverter TUB spout, ONE shower outlet; seller reports unavailable/discontinued; confirm live factory status and complete three-fixture distribution","HISTORIC_MAKER_2021_FACTORY_NOT_CURRENT_AVAILABILITY","HISTORIC_2021_LIST_USD_274_NOT_2026_PRICE","CURRENT_US_MARKET_AVAILABILITY_HOLD",URL["valve_source"]),
("Hansgrohe","15739001","Ecostat S Chrome pressure balance finish sibling","NOT_AN_APPROVED_MATTE_WHITE_SUBSTITUTE","Factory current item lists diverter-tub-spout bypass and ONE outlet, but CHROME only; cannot transfer finish/order identity to 15739701","CURRENT_OFFICIAL_SIBLING_ONLY","CURRENT_USD_301_MSRP_CHROME_ONLY","NO_COLOR_OR_FINISH_TRANSFER",URL["valve_pressure"]),
("Duravit","700332000000090","Starck 59x29.5in White built-in acrylic TUB with support frame","ORIGINAL_SELECTED_PH2_TX4","Actual item 59x29.5in; 790112 manufacturer suitable flange accessory NOT installed/ordered by default; user exact waste/overflow not replaced","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_1550_NOT_BID","W1_SOURCE_59_496IN_PH2_60IN_TX4_NOT_FINISHED_CLEAR",URL["tub"]),
("Duravit","790112000000000","16in universal tile flange accessory","UNSELECTED_CONDITIONAL_TUB_SUPPORT","Listed suitable for 700332 at maker item; 16in segment NOT assumed continuous 59in/3-wall flange; full waterproof assembly and how many pieces factory-specified","CURRENT_OFFICIAL_ACCESSORY","MANUFACTURER_LIST_USD_360_UNKNOWN_INSTALL","NO_FULL_PERIMETER_COVERAGE_INFERENCE",URL["flange"]),
("Brizo","BT062415-BNX","4in Black Onyx tile-in square POINT drain","OWNER_SELECTED_PH4","PVC and brass adjustable upper, removable grate, 2in PVC connection; no certified Schluter KERDI interface from other-brand instructions","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_166_NOT_INSTALLED","POINT_FOURPLANE_PAN_SEPARATE_LAB",URL["point"]),
("Brizo","BT0734816-BNX","48in Black Onyx dual-mode LINEAR grate","OWNER_SELECTED_TX_PRIMARY_AND_PH_PRIMARY","Solid grate or tile-in frame, 7-18mm tile adjust range, 48in nominal; BR73480 rough MUST ORDER separately","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_825_NOT_INSTALLED","NO_NICHES_NO_WC_DOUBLE_ORDER",URL["linear"]),
("Brizo","BR73480","48in LINEAR rough body, stainless channel with patented water protection","OWNER_SELECTED_REQUIRED_TX_PRIMARY_AND_PH_PRIMARY","Built-in sloping channel, water protection system, hair catcher; MUST ORDER DRAIN TRIM SEPARATELY; TX-source erroneous duplicate labelled wall-edge trim is not evidence of second rough","CURRENT_OFFICIAL_ITEM","MANUFACTURER_LIST_USD_684_NOT_INSTALLED","FIRM_PAIRING_ONLY_ONE_ROUGH_PER_DRAIN_PENDING_BOM",URL["linearrough"]),
("Schluter","KERDI-DRAIN","Distinct proprietary bonded flange point drain","FOREIGN_SYSTEM_REFERENCE_ONLY","KERDI bonding flange interfaces with Schluter/KERDI membrane; does NOT mean Brizo BT062415 compatible with same flange","CURRENT_OFFICIAL_SYSTEM_EXAMPLE","NO_PRICE_TRANSFER","NEVER_ASSUMED_BRIZO_COMPATIBLE",URL["membrane"]),
("ELM Surfaces","Cortar Bone Ribbed","PH4 ORIGINAL wet WALL","ORIGINAL_PH4_SOURCE","Original Ribbed item Wet Areas NOT individually listed; flat Cortar Bone Wet Areas item cannot transfer to Ribbed","HISTORIC_WALL_HOLD","UNKNOWN","WALL_APPLICATION_HOLD",URL["ribbed"]),
("ELM Surfaces","Cortar Charcoal flat","TX4 ORIGINAL wet WALL","ORIGINAL_TX4_SOURCE","Flat product Wet Areas separately item-listed; actual color/24x48 finish and entire tub backer system still required","CURRENT_WET_WALL_ITEM_LISTED","UNKNOWN","EXACT_ORDERABLE_FINISH_MOCKUP_HOLD",URL["charcoal"]),
("ARTO / Traditions","Clara Caviar 2x8","PH4_TX4 ORIGINAL wet NICHE","ORIGINAL_PH4_TX4_SOURCE","Generic wall wet-system instructions do not authorize individually original Caviar exact wet NICHE","COLLECTION_ONLY_NO_INDIVIDUAL_WET_NICHE","HISTORIC_PRICE_ONLY","NICHE_APPLICATION_HOLD",URL["caviar"]),
("ELM Surfaces","Soho Ivory 2x10 Glossy","PH4_TX4 CONDITIONAL niche","UNSELECTED_OWNER_OPTION","Individual Wet Areas WALL listing but not an approved waterproof system or owner selection","CURRENT_WET_WALL_ITEM_LISTED","UNKNOWN","CURRENT_SKU_LOT_PRICE_UNKNOWN",URL["soho"]),
]
M_FIELDS=("maker","exact_item_or_family","product_identity","selection_class","current_factory_claim_or_limitation","evidence_class","price_classification","gate","maker_URL")
csvout("R31_16_OFFICIAL_MAKER_SPOUT_VALVE_TUB_POINT_LINEAR_AND_WET_SOURCE_MATRIX.csv",[dict(zip(M_FIELDS,x)) for x in maker])

# Two genuine source-duplicate identical Hansgrohe programs. Three paths each,
# none can be released without all three outlet roles being electrically/mechanically assigned.
decision=[]
for room in ("TX-BATH4","PH-BATH2"):
    for tier,path,source,proposed,hard,scope,visual in [
        ("GOOD","A_SOURCE_RETENTION_HARD_HOLD","15758701 thermostat 2 outlet + 72411701 pressure-balance-only diverter spout + iBox 01850181",
         "NO substitution; show clash and await factory sanctioned combined 3-output design",
         "Spout factory pressure-balance ONLY conflicts thermostat, three fixtures: tub spout + overhead + hand shower, unassigned ports",
         "No cost approved; identify existing stock exposure vs unsized rough rework",
         "Original Matte White 2-control face and diverter-spout look retained, but NOT installable with current evidence"),
        ("BETTER","B_RETAIN_THERMOSTAT_WITH_UNSELECTED_NON_DIVERTER_SPOUT","Keep 15758701 thermostat/01850181 selected rough; conditional maker 72410701 Matte White non-diverter spout",
         "Maker-approved routing of one thermostat outlet to tub and other to approved shower distribution/diverter for overhead AND hand shower",
         "Third fixture requires approved additional switching; 2-outlet trim itself cannot be claimed to operate 3 independent outlets; written exact flow/routing and owner signed spout change",
         "Conditionally replace spout + new approved hand shower distribution branch + finish tile/penetration repairs; no installed bid",
         "Clean spout without extra pull-up diverter; retains original two-control thermostat; new finish/sample/geometry witness"),
        ("BEST","C_RETAIN_SELECTED_SPOUT_WITH_UNSELECTED_PRESSURE_BALANCE_TRIM","Keep original 72411701 Matte White diverter spout and source 01850181 rough pending factory",
         "Conditional historic 15739701 Matte White Ecostat S pressure balance with factory integrated spout bypass, 1 outlet to shower, PLUS separately engineered overhead/hand-shower selection",
         "15739701 2021 factory evidence; current retailer lists unavailable/discontinued, not a qualified purchasable substitute; pump capacity, valve/cartidge/multioutlet and manufacturer clearance missing",
         "Potential thermostat trim/cartridge substitution, controls, 2nd shower selector, future service risk; no current price/order or owner change",
         "Preserves original pull-up diverter spout, changes trim control look and thermoregulation program; owner consent mandatory"),
    ]:
        decision.append(dict(room=room,tier=tier,conditional_path=path,original_owner_selected_program=source,
           manufacturer_evidence_reference=URL["spout_div"]+" ; "+URL["valve_source"]+" ; "+URL["rough"],
           proposed_FACTORY_NOT_OWNER_APPROVED=proposed,three_independent_wet_outlet_roles="TUB_SPOUT;OVERHEAD_SHOWER;HAND_SHOWER",
           precise_hard_gate=hard,construction_rework_scope_if_owner_approves=scope,design_buyer_tradeoff=visual,
           specified_Duravit_and_Matte_White_unmodified="TRUE",actual_selected_tub_spout_changed="FALSE",
           no_tiled_shower_pan="TRUE",factory_routing_document="",plumber_signature="",owner_change_order="",current_factory_availability="UNKNOWN",
           GC_installed_bid="UNKNOWN",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(decision)==6
csvout("R31_6_TWO_TUB_HANSGROHE_THREE_OUTLET_MAKER_CONFLICT_OWNER_DECISION_TREE.csv",decision)

# Actual tub physically 59in, back wall source PH2 59.496 and TX4 60in.
# Possible "finished clear" corridor vs setting tub before backer. Both paths unknown.
tub_fit=[]
for room in ("TX-BATH4","PH-BATH2"):
    w=float(W[room,"W1"]["source_width_in_UNVERIFIED"])
    for shift in (-.25,0.,.25):
        for finished_stack_end in (.25,.5,.75):
            source_plus_shift=w+shift
            hypothetical_finish_clear=source_plus_shift-2*finished_stack_end
            excess=hypothetical_finish_clear-59
            tub_fit.append(dict(room=room,nominal_manufacturer_tub_length_in="59.0000",
              ORIGINAL_SOURCE_W1_SPAN_in_UNVERIFIED=n4(w),fictional_field_delta_in=n4(shift),
              hypothetical_both_end_wall_finish_assembly_each_in=n4(finished_stack_end),
              hypothetical_after_two_end_FINISH_CLEAR_in=n4(hypothetical_finish_clear),
              hypothetical_FINISH_clear_minus_TUB_in=n4(excess),
              finished_clear_if_tub_IS_INSERTED_AFTER_FINISH=("INSUFFICIENT_HYPOTHETICAL" if excess<0 else "NONNEGATIVE_NOT_A_REAL_FIT"),
              actual_tub_may_install_before_finish="YES_CONSTRUCTION_SEQUENCE_MUST_BE_SIGNED",
              actual_framing_rough_site_width_in="",flange_installed_type_and_gaps="",tub_anchors_and_support_verified="FALSE",
              actual_access_and_maintenance_clearance="UNKNOWN",source_tub_URL=URL["tub"],field_verified="FALSE",
              release="FALSE",purchase_authorized="FALSE"))
assert len(tub_fit)==18
csvout("R31_18_TWO_TUB_ROUGH_VS_FINISH_CLEARANCE_TOLERANCE_SENSITIVITIES.csv",tub_fit)

# Distinct valve rough/escutcheon and tile field face BUILDUP cases, not Caviar niche body comparison.
stack=[]
for room in focus:
    available_walls=[w for w in ("W1","W3","W2") if (room,w) in W]
    wall="W3" if "W3" in available_walls else "W2"
    for board in (.375,.5):
        for mortar in (.125,.1875,.25):
            for face in (.3125,.375):
                stack.append(dict(room=room,interface_wall=wall,source_W_width_in_UNVERIFIED=W[room,wall]["source_width_in_UNVERIFIED"],
                    hypothetical_backer_in=n4(board),hypothetical_compressed_mortar_in=n4(mortar),
                    hypothetical_calibrated_actual_TILE_BODY_in=n4(face),
                    waterproof_membrane_and_seal_total_thickness_in="UNKNOWN_NOT_ZERO",
                    subtotal_excluding_MEMBRANE_in=n4(board+mortar+face),
                    actual_valve_rough_face_from_finished_wall_in="UNKNOWN",
                    actual_escutcheon_cover_and_seal_compression_in="UNKNOWN",
                    actual_profile_trim_leg_and_tile_caliber_in="UNKNOWN",
                    required_factory_depth_tolerance_window="UNKNOWN_PER_EXACT_15758701_15739701_BRIZO_SELECTED",
                    preliminary_depth_pass="NOT_ASSESSABLE",applies_to="SPOUT_VALVE_AND_TUB_LIP" if "BATH2" in room or room=="TX-BATH4" else "DRAIN_PAN_TRANSITION_AND_VALVE",
                    tile_body_vs_INSTALLED_FACE_NOT_EQUIVALENT="TRUE",
                    physical_1to1_and_factory_depth_required="TRUE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(stack)==48
csvout("R31_48_VALVE_TUB_AND_DRAIN_FINISH_PLANE_PARTIAL_BUILDUP_CASES.csv",stack)

# Distinct geometry: point 4-way slope vs linear trough along TX Primary,
# not an approved 1529 architectural drain point or compliant floor slope design.
slope=[]
for room in ("PH-BATH4","TX-PRIMARY"):
    g=json.loads((ROOT/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
    fp=g["shower_or_tub_footprint"]
    wd=float(fp["width"]["value"])*12
    dp=float(fp["depth"]["value"])*12
    for mode in ("POINT_CENTER" if room=="PH-BATH4" else "LINEAR_AT_END",
                 "POINT_OFFCENTER_HYPOTHETICAL" if room=="PH-BATH4" else "LINEAR_AT_WALL"):
        for rate in (.25,.3125,.375):
            for transition in ("CURBED_WITH_SIGNED_OUTER_LEVEL","CURBLESS_WITH_VERIFIED_RECESS"):
                # Point slope proxy: farthest axis run; linear slope proxy: depth run.
                run=(max(wd/2,dp/2) if mode=="POINT_CENTER" else max(.6*wd,.6*dp) if room=="PH-BATH4" else dp)
                rise=rate*run/12
                slope.append(dict(room=room,selected_drain=("BT062415-BNX_4IN_SQUARE_POINT" if room=="PH-BATH4" else "BT0734816-BNX_PLUS_SEPARATE_BR73480_48IN_LINEAR"),
                    conceptual_layout=mode,threshold_condition=transition,source_footprint_W_in_UNVERIFIED=n4(wd),
                    source_footprint_D_in_UNVERIFIED=n4(dp),
                    source_rectangle_AREA_SF_NOT_MEASURED=n4(wd*dp/144),
                    hypothetical_slope_rate_in_per_FT=n4(rate),conceptual_critical_run_in=n4(run),
                    approximate_wet_surface_rise_in_NOT_APPROVED=n4(rise),
                    actual_drain_centerline_and_high_boundary_elevations="UNKNOWN",
                    drain_bond_flange_AND_selected_membrane_approved="FALSE",
                    free_slope_min_or_code_checked="FALSE",actual_fractured_planar_triangle_geometry="UNVERIFIED",
                    actual_threshold_water_retention_and_accessibility_detail="UNVERIFIED",
                    original_raw_wet_PAN_TILE_DCOF_report="MISSING",original_LEVEL_TILE_DCOF_report="MISSING",
                    raw_LEVEL_may_be_used_for_PAN="FALSE",manufacturer_system_signed="FALSE",
                    owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(slope)==24
csvout("R31_24_POINT_FOURPLANE_VS_48IN_LINEAR_SLOPE_THRESHOLD_DATUM_CASES.csv",slope)

separation=[]
for room in ("PH-BATH4","TX-PRIMARY"):
    source_gross=Decimal(SOURCE_FLOOR[room]["source_gross_sf_one_copy_waste_15pct_once"])
    geom=json.loads((ROOT/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
    source_floor=float(geom["floor_area"]["value"])
    f=geom["shower_or_tub_footprint"]
    footprint=float(f["width"]["value"])*float(f["depth"]["value"])
    for branch in ("SOURCE_FLOOR_INCLUDES_PAN_AREA","SOURCE_FLOOR_EXCLUDES_PAN_AREA"):
        level=max(source_floor-footprint,0) if branch=="SOURCE_FLOOR_INCLUDES_PAN_AREA" else source_floor
        total=level+footprint
        separation.append(dict(room=room,branch=branch,
            source_ROOM_floor_area_SF_UNVERIFIED=n4(source_floor),
            original_source_historic_floor_GROSS_SF_once=str(source_gross),
            drawing_or_assumed_PAN_rectangle_SF=n4(footprint),
            hypothetical_LEVEL_net_SF=n4(level),
            hypothetical_distinct_PAN_net_SF=n4(footprint),
            hypothetical_total_level_plus_pan_NET_SF=n4(total),
            hypothetical_15pct_once_IF_APPROVED_net_not_applied_to_old_gross_SF=n4(total*1.15),
            source_historic_GROSS_minus_hypothetical_NEW_gross_SF=n4(float(source_gross)-total*1.15),
            numbers_from_actual_1529_field="FALSE",actual_owner_floor_include_pan_clarified="FALSE",
            pan_PRODUCT_not_identical_to_LEVEL_product="REQUIRES_SEPARATE_ORIGINAL_SKU_AND_RAW_WET_TEST",
            never_buy_LEVEL_from_room_plus_full_pan_twice="TRUE",
            owner_approved="FALSE",actual_order_SF="",purchase_authorized="FALSE"))
assert len(separation)==4
csvout("R31_4_SELECTED_POINT_AND_LINEAR_LEVEL_VS_PAN_INCLUDED_OR_EXCLUDED_ALTERNATE_TAKEOFFS.csv",separation)

# Original source W1/W3 (TX Primary W2: do NOT invent W3), no R30 niche-format repetition.
widthcases=[]
for room in focus:
    for wall in ("W1","W3" if (room,"W3") in W else "W2"):
        row=W[room,wall];w=float(row["source_width_in_UNVERIFIED"]);h=float(row["source_tiled_height_in_UNVERIFIED"])
        for delta in (-.5,-.25,0,.5):
            trial=w+delta
            widthcases.append(dict(room=room,wall=wall,
                actual_if_no_W3="W2_IS_LAST_TX_PRIMARY_WALL_NO_W3" if room=="TX-PRIMARY" and wall=="W2" else "SOURCE_WALL",
                ORIGINAL_SOURCE_width_in_UNVERIFIED=n4(w),ORIGINAL_SOURCE_height_in_UNVERIFIED=n4(h),
                HYPOTHETICAL_measured_field_delta_in=n4(delta),
                trial_WIDTH_in_NOT_ACTUAL=n4(trial),raw_FIELD_GROSS_before_openings_SF=n4(trial*h/144),
                original_SOURCE_nominal_FIELD_GROSS_SF=n4(w*h/144),
                change_from_SOURCE_field_area_NET_before_openings_SF=n4(delta*h/144),
                actual_doors_windows_recess_aperture_deduction_SF="UNKNOWN",
                one_niche_aperture_once_SF="UNKNOWN",
                separate_back_side_top_sill_net_SF="UNKNOWN",
                installed_valve_or_glass_or_tub_clash="UNKNOWN",
                source_tile_caliber_actual_edge_joint_and_3in_pier="UNVERIFIED",
                signed_measured_NET_after_all_openings_SF="",
                signed_APPROVED_WASTE_and_case_NEEDED="UNKNOWN_NO_DOUBLE_15PCT",
                actual_1529_document="NONE",buyer_owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(widthcases)==32
csvout("R31_32_NEW_W1_W3_OR_TXPRIMARY_W2_FIELD_UNCERTAINTY_AND_OPENING_DEPENDENCY_CASES.csv",widthcases)

# Integrate exactly existing preliminary R31 raw roles, with independent original source,
# readout requirements and no invented manufacturer test.
products={
"PH-PRIMARY":("Cortar Bone Soft/AntiSlip mixed","WET_LEVEL/LINEAR_PAN_SPLIT_UNVERIFIED"),
"PH-BATH2":("Cortar Grey Soft","LEVEL_ONLY_TUB_NO_PAN"),
"PH-BATH3":("Cortar Bone Soft","POINT_IF_OWNER_WALKIN_ONLY"),
"PH-BATH4":("Cortar Bone Soft/AntiSlip discrepancy","SEPARATE_4PLANE_POINT_PAN_NO_TRANSFER"),
"TX-PRIMARY":("Cortar Clay Soft/AntiSlip mixed","WET_LEVEL/LINEAR_PAN_SPLIT_UNVERIFIED"),
"TX-BATH2":("Cortar Clay Soft","LEVEL_ONLY_TUB_NO_PAN"),
"TX-BATH3":("Cortar Grey Soft","POINT_IF_OWNER_WALKIN_ONLY"),
"TX-BATH4":("Cortar Bone Soft","LEVEL_ONLY_TUB_NO_PAN")
}
labrows=[]
for src in labsource:
    room=src["room"];mat,flag=products[room]
    role=src["surface_role"]
    labrows.append(dict(room=room,surface_role=role,original_floor_row_id=src["source_original_floor_row_id"],
        actual_selected_or_historical_material_family_NOT_EXACT_SKU=mat,product_finish_gate=flag,
        source_2026_09_03_original_GROSS_15pct_once_SF=src["historic_floor_quoted_GROSS_SF_one_copy_may_mingle_LEVEL_and_PAN"],
        separate_lab_specimen_distinct_from_LEVEL= tf(role!="LEVEL"),
        specimen_size_color_finish_batch_and_original_SKU="",
        factory_individual_pan_or_level_application_signature="",
        original_manufacturer_raw_measured_wet_numeric_DCOF="",
        original_method_and_test_specimen_report="",
        original_report_date="",original_test_standard_verified="FALSE",
        generic_0_42_0_50_0_60_Target_threshold_acceptable="FALSE",
        actual_1529_surface_slope_grade_or_horizontal="",
        program_condition=("NOT_SELECTABLE_UNTIL_OWNER_WALKIN" if "CONDITIONAL" in role else "ORIGINAL_ACTIVE_REQUIREMENT"),
        signed_orig_report_ID="",actual_raw_gate="FAIL_MISSING_ORIGINAL_RAW_NUMERIC",
        supplier_actual_sku_price_case="",owner_approved="FALSE",GC_approved="FALSE",purchase_authorized="FALSE"))
assert len(labrows)==13
csvout("R31_13_ORIGINAL_FLOOR_TEST_ROLES_MAPPED_TO_ACTUAL_SOURCE_MATERIAL_AND_DISTINCT_LEVEL_PAN.csv",labrows)

# Give 50 original W witnesses new construction-specific measurement, quantity and trim takeoff
# formulas, not duplicate blank source rows.
walltasks=[]
for r in fieldsource:
    room=r["room"];wall=r["wall_reference"]
    if room in ("TX-BATH4","PH-BATH2"):
        detail=("W1 tub 59in flange/tub-waste/valve and 72411701 vs 15758701" if wall=="W1" else "Return waterproof tub rim/niche and escutcheon")
    elif room=="PH-BATH4":
        detail="Selected WALKIN POINT pan, independent pan membrane and penetration" if wall=="W1" else "Wet shower wall valve/BT062415 four-plane transition/actual niche"
    elif room.endswith("PRIMARY"):
        detail="Selected 48in LINEAR BR73480+BT0734816, no Primary niche, WC parent floor once"
    elif room.endswith("BATH3"):
        detail="Owner tub-vs-walkin UNSELECTED; no conditional POINT pan ordered before decision"
    elif room.endswith("BATH2"):
        detail="Actual Duravit TUB; no tiled pan; flange & source wet wall/niche separate"
    else:detail="Dry wall/no shower or inherited WC floor: no wet niche/PAN"
    walltasks.append(dict(room=room,copy=r["physical_copy"],wall=wall,source_room_number=r["source_revit_room_number_UNVERIFIED"],
        drawing_source_W_in_UNVERIFIED=r["prior_source_wall_width_in_UNVERIFIED"],
        drawing_source_H_in_UNVERIFIED=r["prior_source_tiled_height_in_UNVERIFIED"],
        source_FULL_wall_face_SF_UNVERIFIED=r["prior_source_nominal_full_field_SF"],
        particular_shop_dependency=detail,
        true_1529_revision_and_location_receipt="",witness_name_and_date="",field_measure_WIDTH_in="",
        field_measure_HEIGHT_tiled_in="",field_measured_doors_windows_other_openings_SF="",
        field_niche_COUNT="",
        field_niche_aperture_counted_WALL_displacement_ONCE_SF="",
        field_niche_separate_BACK_SF="",field_niche_separate_TWO_SIDES_SF="",
        field_niche_separate_TOP_SF="",field_niche_separate_SILL_SF="",
        field_movement_joint_actual_LF="",field_exposed_trim_actual_LF="",
        field_valve_tub_spout_escutcheon_and_pipe_CLEAR_in="",
        field_membrane_turns_and_waterproofing_SYSTEM="",
        physical_caliber_and_nominal_vs_finished_planes="",
        certified_NET_WALL_SF_formula="MEASURED_W*H/144-OTHER_APERTURES-ONE_NICHE_APERTURE+N_BACK+TWO_SIDES+TOP+SILL",
        actual_signed_WALL_NET_SF="",actual_waste_newly_approved_after_verified_NET="",
        original_historic_15pct_gross_not_rewasted="TRUE",site_and_trade_accepted="FALSE",
        purchase_authorized="FALSE"))
assert len(walltasks)==50
csvout("R31_50_TWO_COPY_FIELD_SURVEY_ACTUAL_WALL_NET_OPENINGS_TRIM_AND_ASSEMBLY_QUANTITY_INSTRUCTIONS.csv",walltasks)

unitrecords=[]
for src in unitsource:
    room=src["room"]
    name=src["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"]
    if room in ("PH-BATH2","TX-BATH4"): program="DURAVIT_TUB_NO_PAN_DIVERTER_THERMOSTAT_CONFLICT"
    elif room=="PH-BATH4":program="WALKIN_BRIZO_POINT_LEVEL_AND_4PLANE_PAN"
    elif room.endswith("PRIMARY"):program="BRIZO_LINEAR_48IN_SEPARATE_ROUGH_NO_PRIMARY_NICHE"
    elif room in actual_unselected:program="OWNER_TUB_OR_WALKIN_UNSELECTED_POINT_ONLY_IF_WALKIN"
    elif room.endswith("WC"):program="PARENT_WC_LEVEL_INHERITED_ONCE_NO_STANDALONE_ORDER"
    elif "POWDER" in room:program="DRY_FEATURE_WOOD_FLOOR_NOT_TILED_LEVEL_OR_PAN"
    else:program="DURAVIT_TUB_NO_PAN"
    distinct="UNPLACED" if name=="203A" else "SOURCE_ROOM_NUMBER_UNVERIFIED"
    unitrecords.append(dict(room=room,copy_index=src["physical_copy_index"],source_revit_room_number=name,
        actual_1529_room_identification_status=distinct,
        specific_physical_wet_program=program,source_SELECTED_Fixture_and_rough=src["selected_fixture_or_rough_nonnegotiable"],
        witness_site_REV_and_date="",room_finish_wall_face_verified="",drain_or_tub_rough_elevation_verified="",
        tub_flange_or_point_linear_waterproof_seal="",valve_supply_pressure_and_outlet_map="",
        signed_wall_OPENINGS_and_niche_counts="",measured_LEVEL_NET_SF="",
        measured_POINT_OR_LINEAR_PAN_NET_SF="",independent_original_RAW_numeric_wet_DCOF_report_IDS="",
        wet_WALL_and_separate_NICHE_maker_approval_IDS="",
        sourced_SKU_COLOR_FINISH_SHADE_LOT="",factory_CARTON_usable_SF="",
        stock_allocation_current_Chicago="",written_factory_lead_and_freight="",
        GC_installed_bid_includes_backer_membrane_labor_trim_mockup="",
        owner_selection_and_budget_cap_signed="FALSE",
        architect_1529_shop_signed="FALSE",plumber_signed="FALSE",
        waterproofing_signed="FALSE",tile_installer_signed="FALSE",
        supplier_signed="FALSE",GC_signed="FALSE",purchaser_signed="FALSE",purchase_authorized="FALSE"))
assert len(unitrecords)==26
csvout("R31_26_ACTUAL_TWO_COPY_ROOM_OUTLET_SLOPE_FLOOR_TILE_LOT_AND_8TRADE_FIELD_WITNESSES.csv",unitrecords)

# Source-faithful owner choices: different systems and construction consequences,
# NOT blind neutral letters / scores / admitted current candidates.
choices=[]
for room in focus:
    if room in ("TX-BATH4","PH-BATH2"):
        subset=[r for r in decision if r["room"]==room]
        for s in subset:
            choices.append(dict(room=room,tier=s["tier"],
                proposed_design_configuration=s["proposed_FACTORY_NOT_OWNER_APPROVED"],
                fixtures_locked="DURAVIT_700332_TUB_HANSGROHE_MATTE_WHITE_72411701_15758701_01850181_BASELINE",
                baseline_selection_status="UNCHANGED_ALL_ALTERNATIVES_UNSELECTED",
                wet_WALL_NICHE="TX4_FLAT_CHARCOAL_LISTED_CAVIAR_NICHE_UNVERIFIED" if room=="TX-BATH4" else "PH2_SAPPHIRE_AND_SANDSTONE_MAKER_WET_LISTED",
                floor_TEST="LEVEL_RAW_ORIGINAL_NUMERIC_MISSING_PAN_N_A",
                owner_acceptance_tradeoff=s["design_buyer_tradeoff"],
                exact_technical_outlet_blocker=s["precise_hard_gate"],
                measured_1529_tub_flange_59in_source_constraint="REQUIRED",
                conditional_cost_source="UNPRICED_MAKER_OPTION_AND_GC_ROUGH_REWORK_UNKNOWN",
                no_tiled_PAN="TRUE",mockup="MAKER_SCHEMATIC_AND_FULL_MATTE_WHITE_RIM_WALL_OUTLET_1TO1",
                release="FALSE",weighted_board_score="NULL",owner_approved="FALSE"))
    elif room=="PH-BATH4":
        for tier,scheme,fix,why in [
            ("GOOD","Original tile/walkin POINT source arrangement only as HOLD baseline",
             "Original Ribbed wet WALL/unlisted and POINT/LEVEL raw labs missing; no approval",
             "No current design change, but critical wet install evidence absent"),
            ("BETTER","Separate calibrated 4-plane POINT PAN small-format candidate with selected BNX grate and standalone LEVEL finished-floor witness",
             "Manufacturer wet WALL/PAN letters, actual membrane-to-BT062415 flange and independent original raw lab plus calibrated 1:1 slope/joint mockup",
             "Improves constructability and crossing-floor control; conditional additional tray/waterproof labor"),
            ("BEST","Field-verified recessed curbless/curbed transition two-datum build with same selected Brizo POINT + maintenance access",
             "Signed subfloor depression/door waterproof termination, exact factory drain/membrane tie-in and two lab reports",
             "Less visible threshold if practical; waterproof/structure/accessibility risk and expensive bid"),
        ]:
            choices.append(dict(room=room,tier=tier,proposed_design_configuration=scheme,
                fixtures_locked="BRIZO_BT062415-BNX_4IN_SQUARE_POINT_SELECTED_WALKIN",
                baseline_selection_status="UNCHANGED_ALL_ALTERNATIVES_UNSELECTED",
                wet_WALL_NICHE="ORIGINAL_BONE_RIBBED_WET_WALL_NOT_LISTED_ORIGINAL_CAVIAR_INDIVIDUAL_NICHE_UNVERIFIED",
                floor_TEST="SEPARATE_LEVEL_AND_FOURPLANE_POINT_PAN_RAW_NUMERIC_LABS_MISSING",
                owner_acceptance_tradeoff=why,exact_technical_outlet_blocker=fix,
                measured_1529_tub_flange_59in_source_constraint="N_A_POINT",
                conditional_cost_source="UNKNOWN_CURRENT_PAN_TILE_BACKER_MEMBRANE_DRAIN_GC_BID",
                no_tiled_PAN="FALSE",mockup="1TO1_BRIZO_POINT_FOUR_PLANE_TRANSITION_WITH_DRAIN_ACCESS",
                release="FALSE",weighted_board_score="NULL",owner_approved="FALSE"))
    else:
        for tier,scheme,fix,why in [
            ("GOOD","Selected 48in Brizo BNX LINEAR solid grate with separate BR73480 rough, source shower footprint hold",
             "Match actual 7-18mm tile-in only if relevant; verify selected grate seat and maker membrane", "Keep classic dark finished grate with low shade variation"),
            ("BETTER","Same selected Brizo dual-mode 48in linear with calibrated tile-in grate mode as owner option",
             "7-18mm tile thickness calibrated; tile inset service/edge/rough slope verified, separate raw LINEAR PAN report",
             "Quieter continuous floor, higher cleaning and service/matching effort"),
            ("BEST","Same Brizo selected LINEAR installed at verified wall line with full field threshold and one-direction slope shop",
             "Confirm orientation/BR73480 placement, shower glass and drain end cap/tiled edge/access and single membrane strategy",
             "Potential reduced four-way field cuts but wall-edge/corner/footprint risk and added shop labor"),
        ]:
            choices.append(dict(room=room,tier=tier,proposed_design_configuration=scheme,
                fixtures_locked="BRIZO_BT0734816-BNX_48IN_LINEAR_AND_BR73480_SEPARATE_ROUGH_SELECTED_NO_NICHE",
                baseline_selection_status="UNCHANGED_ALL_ALTERNATIVES_UNSELECTED",
                wet_WALL_NICHE="ORIGINAL_CLAY_LEVEL_PAN_INDEPENDENT_FINISH_PERMISSIONS_NEED_MAKER",
                floor_TEST="SEPARATE_LEVEL_AND_48IN_LINEAR_PAN_RAW_NUMERIC_LABS_MISSING",
                owner_acceptance_tradeoff=why,exact_technical_outlet_blocker=fix,
                measured_1529_tub_flange_59in_source_constraint="N_A_LINEAR",
                conditional_cost_source="NO_NEW_MATERIAL_SAVING_CURRENT_WATERPROOF_AND_INSTALL_BID_UNKNOWN",
                no_tiled_PAN="FALSE",mockup="1TO1_BRIZO_48IN_ROUGH_GRATE_WALL_EDGE_THRESHOLD_ACCESS",
                release="FALSE",weighted_board_score="NULL",owner_approved="FALSE"))
assert len(choices)==12
csvout("R31_12_FOUR_FOCUS_GOOD_BETTER_BEST_SHOP_AND_OWNER_SYSTEM_DECISIONS.csv",choices)

# Contractor-readable original amounts; 15% exists already and cannot be "new order".
quote=[]
for x in historical:
    room=x["room"]; surf=x["source_surface"]
    unpriced=x["historic_niche_excluded_no_scope"]=="TRUE"
    gross=Decimal(x["source_gross_sf_one_copy_waste_15pct_once"] or "0")
    total=dollars(x)
    quote.append(dict(room=room,source_row_id=x["source_row_id"],original_surface=surf,
        source_gross_SF_one_copy_15PCT_included=str(gross),
        source_gross_SF_two_copies_15PCT_included=str(gross*2),
        historic_material_ONLY_USD_two_copies=str(total),
        original_unpriced_Primary_niche_reference_NO_ORDER=tf(unpriced),
        original_27_row_lineage_unchanged="TRUE",
        tile_original_exact_orderable_SKU_and_finish="UNKNOWN",
        if_same_SKU_factory_shade_color_finish_lot="UNKNOWN_NOT_POOLABLE_YET",
        separately_CERTIFIED_LEVEL_net_SF="",
        separately_CERTIFIED_POINT_or_LINEAR_PAN_net_SF="",
        one_actual_WALL_aperture_deduction_SF="",
        independent_niche_BACK_TWO_SIDES_TOP_SILL_net_SF="",
        newly_approved_waste_after_SIGNED_NET_only="",
        historic_15PCT_NOT_REAPPLIED="TRUE",
        case_factory_usable_SF_per_current_selected_SKU="",
        required_whole_cases_formula="CEIL((SIGNED_NET+ONLY_NEW_SIGNED_CUT_WASTE)/EXACT_USABLE_CASE_SF)",
        actual_current_Chicago_quote_USD="",
        manufacturer_MSRP_reference_class="UNKNOWN_UNLESS_NEW_MAKER_ITEM_MATCHES",
        public_retail_indication="",
        current_stock_ETA_freight_breakage_tax="",
        GC_full_installed_bid_and_old_scope_credit="",
        extra_tub_valve_or_drain_rough_SCOPE_SEPARATE_from_tile_original="TRUE" if room in focus else "PROGRAM_APPLICABILITY",
        same_lot_pool_approval="FALSE",
        owner_price_cap="",owner_signature="FALSE",supplier_signature="FALSE",
        GC_change_order_approved="FALSE",purchase_authorized="FALSE"))
assert len(quote)==27 and sum(Decimal(x["historic_material_ONLY_USD_two_copies"]) for x in quote)==Decimal("23572.44")
csvout("R31_27_HISTORIC_ORIGINAL_ROW_LEVEL_PAN_SKU_LOT_CARTON_SCOPE_CHANGEORDER_QUOTE_BRIDGE.csv",quote)

groups=[
("R31_TUB_MATTE_WHITE_SAME_ITEM","PH-BATH2;TX-BATH4","selected Hansgrohe 72411701/15758701/01850181 and Duravit 700332 are exact same maker/finish IDs; QUANTITIES can group on fixture BOM only","Not tile SKU pooling; compatible corrected routing + actual separate room copy order quantities still unverified"),
("R31_TUB_WASTE_BRAND_HOLD","PH-BATH2;TX-BATH4","Historical TD9028-PCW source Westbrass vs Wetstyle quoted identity discrepancy","Never order as same factory without OEM/waste/trim certification"),
("R31_BRIZO_LINEAR_OTHER_PRIMARY","TX-PRIMARY;PH-PRIMARY","Same selected BT0734816-BNX and separately BR73480 rough per Primary","No duplicate second BR73480 for TX Primary mislabelled wall trim; material PAN tests per exact tile and room, no floor WC double"),
("R31_BRIZO_POINT_SELECTED","PH-BATH4","Only actual PH4 square point product BT062415-BNX currently selected; other Bath3 point is CONDITIONAL","Do not order point for owner undecided Bath3 or interchange with linear"),
("R31_CAVIAR_HISTORIC","PH-BATH4;TX-BATH4","Historical exact named Caviar niche 34.52 GROSS SF/$1163.32 included once","Wet NICHE individual factory unverified; no new order/pooling without actual shade/caliber/surface"),
("R29_SANDSTONE_HISTORIC_INCLUDED","PH-BATH2;PH-BATH3;TX-BATH2;TX-BATH3","Sandstone 51.64 gross SF/$358.92 already included","Historical same named, lot/finish/case/cut behavior not yet jointly documented"),
("R29_CORTAR_GREY_SOFT_INCLUDED","PH-BATH2;TX-BATH3","Grey Soft 165.4 gross SF/$1116.46 included, LEVEL ONLY","Never infer it serves conditional shower pan, exact lab missing"),
("LEVEL_PARENT_WC_SHARES","PH-PRIMARY;PH-WC;TX-PRIMARY;TX-WC","WC 15SF PH/14SF TX source floor included once in corresponding parent mixed floor","Zero new WC floor purchase or original second15% gross; finish differences Soft vs AntiSlip remain unresolved"),
("PROHIBITED_COLOR_FAMILY_POOL","PH-BATH4;TX-BATH4","ELM Soho Ivory vs Soho Black vs original Caviar are not identical item/color/finish/lot","No sharing or current price assumption"),
]
csvout("R31_9_ACTUAL_FACTORY_IDENTITY_SAME_SKU_POOLS_VS_EXCLUSIONS.csv",
    [dict(group=g,source_rooms=rooms_,what_can_share_if_factory_verified=can,strict_non_pooling_or_hard_gate=notp,
      original_historical_cost_already_in_23572="TRUE",factory_exact_sku_shade_caliber_lot_verification="FALSE",
      combined_cartons_estimated_order="NULL",purchase_authorized="FALSE") for g,rooms_,can,notp in groups])

# Eight distinct physical sample/camera briefs -> two views per room-copy and 3 witness
# inspections at each: no render/image produced, no factory material selected.
views=[]
for room in focus:
    physical=[x for x in unitrecords if x["room"]==room]
    assert len(physical)==2
    for x in physical:
        for name in ("ELEVATION_W1_VALVE_DRAIN_OR_TUB_SP0UT","CUTAWAY_WET_THRESHOLD_AND_W1_RETURN"):
            brief={
            "TX-BATH4":"59in Duravit source tub in prior W1 60in; Talis S 72411701 pull-up vs Ecostat two-control; Matte White tub/Charcoal; no tiled shower PAN",
            "PH-BATH2":"59in Duravit source tub in prior W1 59.496in; Hansgrohe Matte White three fixtures; Sapphire/Sandstone; no tiled PAN",
            "PH-BATH4":"Owner WALK-IN Brizo BT062415-BNX BNX POINT, four-plane pan distinct level, Bone Ribbed unlisted wet, no implied new Caviar wet niche",
            "TX-PRIMARY":"Brizo BT0734816-BNX 48in LINEAR and separate BR73480, no Primary niche, Clay level and pan independent, WC floor parent once"
            }[room]
            views.append(dict(room=room,source_physical_room=x["source_revit_room_number"],view_or_1to1_mockup=name,
              exact_source_truth_to_preserve=brief,
              elevation_and_section_evidence="Actual true1529 valve/drain/tub centerline, membrane, grout, finished face, movement, edge support, trap and service",
              acceptance_test="Physical calibrated tile and frame, installer sealed membrane/penetration, accurate offset/slope, no below3in conspicuous cut if applicable, factory full 3-outlet diagram where tub",
              actual_camera_viewpoint_or_lens="UNCERTIFIED_NO_MODEL_POSE",
              real_render_generated="FALSE",actual_1to1_mockup_built="FALSE",actual_1529_geometry_signed="FALSE",
              owner_sample_color_signed="FALSE",plumber_rough_signed="FALSE",waterproof_signed="FALSE",installer_signed="FALSE",
              current_bid_and_supplier_LOT="UNKNOWN",purchase_authorized="FALSE"))
assert len(views)==16
csvout("R31_16_ACTUAL_FOCUS_UNIT_SOURCE_CAMERA_AND_1TO1_PLUMBING_WATERPROOF_TILE_SHOP_BRIEFS.csv",views)

# 13 original rooms unchanged; all 104 eight-trade gated per program, never false
programs={
"PH-PRIMARY":"Selected 48in Brizo BNX LINEAR+separate BR73480, NO niches; shared PH WC floor once; distinct LEVEL/PAN raw numeric missing",
"PH-BATH2":"Duravit TUB Hansgrohe Matte White; SAME three-outlet thermostat/diverter-spout conflict as TX4; Sapphire/Sandstone wet listed; LEVEL raw test, PAN N/A",
"PH-BATH3":"TUB/WALKIN owner UNSELECTED, basin UNSELECTED, Chrome Hansgrohe, Delta DT062412 POINT only conditional WALKIN; Opal wet WALL not listed, Sandstone niche listed",
"PH-BATH4":"Actual WALKIN Brizo Black Onyx BT062415-BNX square POINT, independent four-plane PAN vs LEVEL, original Ribbed Wet WALL not listed/Caviar niche individual missing, floor owner35 vs prior27",
"PH-POWDER":"Dry wall/wood FLOOR, Brizo T65722LF-GL Luxe Gold wall and separate R65700; no tiled PAN/LEVEL test",
"PH-WC":"Seeded Bone AntiSlip floor inherited PH Primary once, source 15 SF physical copy; TOTO Nexus WC attribute needs field verification, no PAN",
"TX-PRIMARY":"Brizo BNX BT0734816-BNX LINEAR with separate BR73480; source duplicate BR73480 called wall edge needs factory BOM; no niche, Clay LEVEL/PAN independent, TX WC inherited once",
"TX-BATH2":"Duravit TUB Hansgrohe Chrome, Copper/Sandstone wet listed, basin UNSELECTED; LEVEL test, NO tiled PAN",
"TX-BATH3":"TUB/WALKIN owner UNSELECTED; Brizo Black Onyx BT062415-BNX POINT conditional WALKIN only, Emerald wet wall maker renewal needed, Sandstone niche listed",
"TX-BATH4":"Duravit 700332 59in tub, Hansgrohe 15758701 Matte White thermostat two-outlet vs 72411701 diverter-spout PRESSURE-BALANCE ONLY; 01850181 rough; Caviar niche wet missing, Charcoal flat listed, LEVEL only, NO PAN",
"TX-POWDER":"Dry wood floor; AXOR One 48140991 WALL cross trim vs Hansgrohe Metropol 32526141 WALL single trim conflicting owner selection; 32526141 NOT rough, 13622181 option only if Metropol",
"TX-POWDER2":"Dry wood floor; Hansgrohe Tecturis E 73072341 DECK Brushed Black Chrome; basin UNSELECTED, Indigo direction retained",
"TX-WC":"Seeded Clay AntiSlip floor inherited TX Primary once, TX203A source UNPLACED, no separate order/niche/PAN"
}
assert set(programs)==set(ROOM)
release=[]
trade=[]
TRADES=["OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER"]
for r in rooms:
    room=r["id"]
    cost=sum(dollars(x) for x in historical if x["room"]==room)
    wood="POWDER" in room
    wc=room.endswith("WC")
    tub=room in ("PH-BATH2","TX-BATH2","TX-BATH4")
    linear=room.endswith("PRIMARY")
    point=room=="PH-BATH4"
    cond=room in actual_unselected
    level_lab="N_A_WOOD" if wood else "INHERITED_PARENT" if wc else "MISSING_ORIGINAL_RAW_NUMERIC"
    pan_lab="MISSING_INDEPENDENT_LINEAR" if linear else "MISSING_INDEPENDENT_SELECTED_FOUR_PLANE_POINT" if point else "IF_OWNER_WALKIN_MISSING_POINT" if cond else "N_A_TUB_WOOD_OR_INHERITED_WC"
    release.append(dict(room=room,copies="2",formal_round="017",original_status=r["status"],
      champion_id=r.get("champion_id") or "null",champion_score=str(r.get("champion_score")) if r.get("champion_score") is not None else "null",
      historical_material_only_TWO_COPIES_USD=str(cost),actual_source_program_and_top_FIX=programs[room],
      room_wet_LEVEL_raw_numeric_lab=level_lab,
      room_SLOPED_PAN_raw_numeric_lab=pan_lab,
      maker_WALL_individual_permission="ROOM_EXACT_SKU_FINISH_NOT_TRANSFERABLE",
      maker_NICHE_individual_permission="ROOM_SCOPE_N_A_OR_INDIVIDUAL_NICHE_PERMISSION_REQUIRED",
      original_R31_actual_1529_room_copies="2_SOURCE_ONLY_NOT_SURVEYED",
      source_W1_W3_and_finished_assembly_field_certified="FALSE",
      exact_room_approved_program="FALSE" if cond else "PROGRAM_PRESERVED_REQUIRES_SHOP_SIGNATURE",
      owner_material_and_budget_approved="FALSE",architect_1529_signed="FALSE",
      plumber_correct_selected_rough_and_outlets_signed="FALSE",
      waterproof_drain_OR_tub_flange_signed="FALSE",
      installer_calibrated_tile_1to1_mockup_signed="FALSE",
      actual_2026_chicago_source_sku_lot_case_and_freight_signed="FALSE",
      GC_actual_installed_quote_and_change_order_signed="FALSE",
      purchaser_material_reservation="FALSE",purchase_authorized="FALSE"))
    for seq,who in enumerate(TRADES,1):
        if who=="OWNER":req="Preserve original fixtures/choice; where unselected get signed TUB-vs-WALKIN or faucet/basin & budget. Choose no unapproved R31 alternative."
        elif who=="ARCHITECT":req="Certified true 1529 wall, door, niche, penetrations, tub flange vs shower pan, rough/finish depth dimension diagrams and owner permits."
        elif who=="PLUMBER":req="Sign every original drain/rough/spout/valve, hydraulic outlet roles, drain connection, tub waste/overflow access; solve PH2/TX4 thermostatic versus pressure-balance-only spout with exact three outlet factory map."
        elif who=="WATERPROOFING":req="Match exact manufacturer membrane/flange/backer/corners/penetration seal, curbed or curbless threshold, tub tiling overlap or actual Brizo POINT/LINEAR compatibility; no Schluter/Brizo assumption."
        elif who=="TILE_INSTALLER":req="Distinct original measured raw wet LEVEL/PAN labs as program, separately wet WALL and NICHE item permissions, shop cuts, profile and one-to-one calibrated tile/substrate mockup."
        elif who=="SUPPLIER":req="Exact full SKU/color/size/finish/case usable SF/lot/caliber, current Chicago allocation/source and dated freight/ETA offer; no outreach done."
        elif who=="GC_ESTIMATOR":req="Original 15%-in-gross once, parent WC once; measured NET openings minus only one niche aperture plus independent returns; include full flange/rough/trim/waterproof labor and source-vs-new change-order credit."
        else:req="Release only after owner/architect/plumber/waterproof/tile/supplier/GC authentic signatures and original four-seat board protocol; no interim PO."
        trade.append(dict(room=room,sequence=seq,trade=who,source_specific_original_program=programs[room],
            exact_R31_trade_completion_evidence=req,source_lab_role_count=sum(x["room"]==room for x in labrows),
            physical_copy_count=2,real_1529_Field_DOC="",signature="",signed_date="",
            original_4critics_complete="FALSE",original_independent_nonpro_reviewer_accepted="FALSE",
            owner_approved="FALSE",GC_release="FALSE",purchase_authorized="FALSE"))
assert len(release)==13 and len(trade)==104
csvout("R31_13_ROOM_SOURCE_WALL_NICHE_LEVEL_PAN_PROGRAM_AND_RELEASE_MATRIX.csv",release)
csvout("R31_104_ROOM_SPECIFIC_SEQUENTIAL_8TRADE_PLUMBING_WET_AND_QUOTE_SIGNOFFS.csv",trade)

costs=[]
for room in programs:
    two=sum(dollars(x) for x in historical if x["room"]==room)
    source_gross=sum(Decimal(x["source_gross_sf_one_copy_waste_15pct_once"] or "0")*2 for x in historical if x["room"]==room)
    costs.append(dict(room=room,original_two_copy_historical_source_GROSS_SF_15PCT_ONCE=str(source_gross),
      original_two_copy_material_only_QUOTED_USD=str(two),
      original_2026_09_03_quote_baseline_class="HISTORICAL_MATERIAL_NOT_CURRENT_SUPPLIER",
      R31_Hansgrohe_pressure_balance_vs_thermostat_alternative_class="2021_MAKER_OLD_MSRP_ONLY_UNSELECTED" if room in ("PH-BATH2","TX-BATH4") else "N_A",
      current_maker_suggested_list_not_material_actual="NO_FINISHED_GC_SCOPE",
      actual_2026_current_exact_LOT_case_Chicago_offer="",
      actual_delivery_freight_ETA_tax_allowances="",
      current_workmanship_labor_bid_backer_membrane_grout_movement="",
      change_order_deleted_original_fixture_credit="",
      change_order_added_factory_matched_controls_and_three_outlet_distribution="",
      source_stock_owner_supplied_material_receipts="",
      original_waste_15percent_once_protected="TRUE",
      no_duplicated_primary_WC_or_PAN_LEVEL="TRUE",
      no_comp_sourced_buyer_premium="TRUE",
      owner_cap_and_sign="FALSE",supplier_signed="FALSE",GC_installed_bid_signed="FALSE",purchase_authorized="FALSE"))
assert sum(Decimal(x["original_two_copy_material_only_QUOTED_USD"]) for x in costs)==Decimal("23572.44")
csvout("R31_13_ROOM_HISTORIC_TILE_ONLY_VS_CURRENT_INSTALLED_SCOPE_AND_CHANGEORDER_NORMALIZATION.csv",costs)

mdout("START_HERE_R31_INTEGRATED.md",f"""
# R31 integrated construction/procurement — TX4 + PH2 + PH4 + TX Primary

**Active entire 1529 project OPEN. NOT owner/architect/GC approved; NO purchase.** This is NOT the immutable earlier 13-lab/50-wall/26-room R31 source-only set and does NOT reissue any R30 niche layout packet. Original formal Board round 017 remains unchanged.

## Actual consequential new manufacturer compatibility result

Manufacturer Hansgrohe {URL["spout_div"]} explicitly says the **original 72411701 Matte White pull-up diverter tub spout** is for **pressure-balance valve ONLY**. The original **15758701 Matte White Ecostat S** is **thermostatic with 2-outlet volume/diverter** (Hansgrohe historic catalogue {URL["valve_source"]}); original **01850181** is a universal rough {URL["rough"]}. The two actual tub rooms **TX-BATH4 and PH-BATH2 share all three original item IDs** and the **Duravit 700332000000090 59x29.5in TUB**, so this is not a TX4-only site exception. Both schedules carry **THREE physical outlets**: tub spout, overhead shower, hand shower. Three outputs CANNOT simply be assumed controlled by a two-outlet trim; complete factory-approved switching/port diagram and flow/temperature safety verification required.

* GOOD (retain originals): source historically preserved but **HARD HOLD** — must not install unsupported thermostat/diverter spout pairing.
* BETTER (unselected): retain original 15758701 thermostatic trim and exact iBox, compare manufacturer current **72410701 Matte White Talis S non-diverter spout** {URL["spout_plain"]}; still needs new manufacturer-approved method assigning tub, overhead AND hand shower. No automatic retrofit or outlet-count pass.
* BEST (unselected): retain selected 72411701 spout and investigate historical factory Matte White **15739701 pressure-balance** trim with integrated diverter-spout bypass, both evidenced in 2021 Hansgrohe maker book; **current availability disputed (retailer says discontinued/unavailable)**, and factory complete independent shower-head/hand-shower selection and exact iBox compatibility are unresolved. May fail current availability hard gate. This is NOT an approved substitute. Current maker Chrome 15739001 is NOT permission to change owner Matte White.

For both tub rooms the 59in actual manufacturer tub nominal vs source W1 spans **59.496in PH2** and **60in TX4** are drawing-provisional; the 18 new finished-clear hypothetical cases show even sub-0.25in end assembly effects can turn nominal gaps negative. Actual tub may be fitted ahead of backer; do not equate a hypothetical finished-clear deficit with a demonstrated tub clash. Duravit maker lists optional 790112 flange as suitable, but its 16in accessory is not proven continuous across three sides {URL["flange"]}; support, rim waterproof return, spout/trap, real edge are signed shop requirements. Tub floors LEVEL original raw numeric wet lab required, PAN N/A.

**PH4 selected WALK-IN Black Onyx Brizo BT062415-BNX POINT** {URL["point"]}: four-plane PAN separate LEVEL; its PVC/brass adjustable upper/2in PVC is NOT proven compatible with Schluter proprietary KERDI point bonding flange; independent maker-approved membrane/drain attachment plus calibrated small-PAN tile raw measured wet lab required. **TX Primary** selected Black Onyx Brizo BT0734816-BNX 48in LINEAR plus separate BR73480 {URL["linear"]}; reversible solid-vs-tile-in frame 7–18mm body range, BR73480 factory water-protection channel {URL["linearrough"]}; none authorizes common bath LEVEL lab as sloped LINEAR PAN. No added Primary niche or duplicate BR73480.

## New quantitative evidence, not a fake survey

* 18 physical tub rough/finish-clear tolerance scenarios; 48 rough-depth/bond thickness **partial stack** cases (all membrane/actual valve depth UNKNOWN); 24 sloped four-plane POINT vs one-direction LINEAR threshold/surface elevation scenarios and 4 mutually exclusive bath LEVEL/PAN room-area interpretations.
* 32 source-W1/W3 (TX Primary real W2, not invented W3) opening/field-width tolerance cases. Original R31 50 W and 26 room-copy blanks turned into field instruction/quantity controls, **not duplicate raw source rows**. 13 original separate wet lab source roles mapped to original eight quoted floor row IDs and exact family/finish uncertainty. 12 genuine four-room owner GOOD/BETTER/BEST alternatives, 16 unit-specific physical 1:1/camera briefs, 13 original-room cost/release rows plus 104 ordered trade gates and 27 intact historical material rows, nine proper pooled/excluded item identity groups.
* **$23,572.44** four-unit historic material-only includes 15% gross waste ONCE, 27 rows including 2 unpriced NO ORDER Primary niche references. Sandstone 51.64SF/$358.92; Cortar Grey Soft 165.40SF/$1,116.46; Caviar 34.52SF/$1,163.32 are **already inside**, never new charges or savings. 25 historical source W studies and 65 trade action rows remain untouched. Current Chicago manufacturer shade/lot/case, freight, ETA, installed labor, bid and owner budget cap UNKNOWN.

## Governance

Original DESIGN worker9 R014 two authentic reports absent, original Reviewer15 FINISHED/nonrevivable; R017 8 frozen neutral sources/4 private mappings without independent preflight. This R31 work is **owner/architect/GC source-only construction options**, NOT duplicate frozen blind candidates; weighted scores NULL, owner approvals FALSE. The 5-section report is PREPARED NOT SENT. 14 comps = 9 distinct buildings (OT01–OT04 405 W Armitage one building), Old Town first; PH ~$2.8M/TX ~$2.7M, $2.4–3.2M range; no competitor material or buyer premium guessed. No Revit/Smartsheet writes, contact, samples, PO, Git changes, external software installs or global DONE.
""")

mdout("R31_HANSGROHE_THREE_OUTLET_FACTORY_COMPATIBILITY_AND_TUB_WALL_SHOP_BOOK.md",f"""
# Two duplicated tub rooms — real hydraulic conflict, physical-section and shop resolution

## Manufacturer evidence, historical versus current

Original PH-BATH2 and TX-BATH4 Smartsheet selections exactly: **700332000000090** Duravit 59x29.5in built-in tub, **15758701** Ecostat S thermostatic trim with two-outlet volume/diverter, **01850181** iBox Universal rough, **72411701** Talis S Matte White tub spout with diverter; overhead shower **04388700**, hand shower **26866701**. Hansgrohe current maker {URL["spout_div"]} labels selected tub spout pressure-balance-only. Original thermostatic two-outlet trim classified in **2021 Hansgrohe official catalogue** {URL["valve_source"]}, NOT manufacturer authorization to use incompatible pressure-balance diverter spout. Factory current iBox maker {URL["rough"]} supplies one rough body, not proof every trim/spout combination is approved. PH-BATH2 and TX-BATH4 both have **three physical endpoints**, not two.

**Maker conditional non-diverter branch:** Hansgrohe current official {URL["spout_plain"]} **72410701** Matte White without pull-up diverter, U.S. factory list $321 (retail/actual installed unknown). Retaining selected 15758701 may permit a tub branch plus a shower branch only after Hansgrohe supplies an official port diagram; additional handshower/overhead selector or manifold is **unselected**, must be drawn and bid. Do not claim this alone is compatible or approved.

**Maker conditional pressure-balance branch:** historical official manufacturer catalogue {URL["valve_source"]} lists **15739701** Ecostat S Matte White pressure-balance trim with integrated bypass for diverter tub spouts, 1 shower outlet and iBox 01850181 rough. That is materially distinct from selected 15758701 2 outlet thermostat, changes temperature-control program and needs physical behind-wall cartridge/trim assembly proof, not just a face swap. Retailer reports 15739701 unavailable/discontinued; it does **NOT PASS availability**, current independent maker SKU approval, finished assembly, plumbing balancing or owner consent. Current maker Chrome sibling {URL["valve_pressure"]} demonstrates principle, not availability or permission to substitute Matte White.

## Controlling hydraulic diagram — 3 endpoint roles, 2 source valve outlets

SOURCE: HOT / COLD -> manufacturer 01850181 -> selected 15758701 thermostat + two-OUTLET selector -> (A: UNKNOWN, B: UNKNOWN). Endpoints T = tub fill via 72411701, S = overhead 04388700, H = hand shower 26866701. **DO NOT connect 3 endpoints to 2 source ports by inference.** Wrong bypass/backpressure from diverter spout is a factory/gc liability; manufacturer determines compatible upstream diverter and backflow/thermostatic/pressure behavior.

CONDITIONAL B: HOT/COLD -> iBox + thermostatic 15758701 -> port T to **non-diverter** 72410701; second port to written maker approved selector dividing S and H. Third endpoint still UNASSIGNED until factory port diagram. All pipe penetrations, volume/flow, water pressure, service stops, shutoff/anti-scald protection and measured trim projection need plumber signoff and sealed plan.

CONDITIONAL C: HOT/COLD -> iBox with factory-qualified **15739701 pressure-balance cartridge/trim** -> tub pull-up diverter 72411701 with explicit bypass; shower distribution to S and H by another manufacturer approved selector. Current product availability and owner thermostat-to-pressure-balance change **unapproved**.

## W1 preliminary elevation and two-phase rough-vs-finished wall construction

* PH2 W1 prior source **59.496 x93in**; TX4 W1 **60x93in**. Factory tub outer nominal **59in**. Subtracting the two finished wall end assemblies from these source spans is merely a hypothetical "install-after-finish" corridor; the actual tub may be set against framed supports and waterproofed around before wall finishes. The 18 alternate scenarios vary source boundary -0.25/0/+0.25in and each end layer 0.25/0.5/0.75in, explicitly identifying negative finished corridor while no actual 1529 framing/side reveal exists.
* Set Duravit tub only under its actual approved support frame, waste/overflow access and physical flange requirements. Confirm **790112** optional suitable accessory's exact segments and use. **Do not assume 16in item is a one-piece 59in/three-side waterproof solution**; manufacturer/deck detail and installer mockup determine continuous membrane/sill return, backer-to-flange and soft movement joint at tub rim. 1:1 specimen required.
* Substrate/bond stack is not tile BODY thickness: actual rough face depth measured from framing, chosen backer, membrane (UNKNOWN), compressed mortar, calibrated tile, trim gasket compression and finished spout projection. 48 alternate R31 stacks intentionally EXCLUDE unverified membrane thickness, are never rough-in depth approvals. Record wall-return corners, sealed escutcheon penetrations and tub head/valve access.
* W3 source PH2 **30.6x93in**, TX4 **30.48x93in** prior, actual surrounds/pipe openings unknown. Only subtract one original front NICHE/door/window aperture, then add independently BACK/two SIDE/TOP/SILL actual measured surfaces; do not repeat R30 Caviar/Soho form-factor grids. PH2 Sapphire wet WALL and Sandstone niche item-listed from previous maker research, TX4 Charcoal flat WALL listed but Caviar individual niche missing. Floor LEVEL exact individual original maker numeric wet DCOF required, PAN N/A.

## Contractor shop and change-order entitlement

Do not issue rough-in/drywall closures/PO on existing unproven pairing. Plumber submits **3-endpoint hot/cold routing diagram** with factory letters for precise selected/trial components, service access, actual head/hand shower simultaneous-use logic, pressure/flow and backflow/crossflow control. Architect signs true-1529 measured valve centerline, tub side supports, wall-to-rim waterproof sections, finish face and trim clearance. Owner signs unchanged or conditional alternative in Matte White plus any fixture control difference. GC obtains separated deleted original material credit, added component/valve/selector/labor/wall repair bids at dated Chicago terms, no fictitious fixed priced difference. Supplier verifies actual compatible SKU in current same factory supply/availability (15739701 historic may be discontinued). No contact/purchase presently authorized.
""")

mdout("R31_BRIZO_FOUR_PLANE_POINT_VS_48IN_LINEAR_WATERPROOF_SLOPE_AND_SOURCE_LAB_SECTIONS.md",f"""
# Four-plane POINT and 48-inch LINEAR require independent factory systems

## PH-BATH4: selected Black Onyx BT062415-BNX 4in square POINT

Actual WALK-IN and four-plane PAN **must be kept**, independent original bath LEVEL. Manufacturer {URL["point"]} says point drain construction PVC/brass, removable grate, adjustable upper and 2in PVC connection. These statements do NOT specify a selected membrane product or authorize a *foreign* Schluter KERDI-DRAIN flange: Schluter {URL["membrane"]} describes its proprietary membrane/point bonding flange, not Brizo compatibility. Architect/plumber/waterproof contractor must select certified connection scheme to actual Brizo and provide factory tested waterproof corner/pipe penetration, sloped point four-plane mortar/floor-tile format. Original maker raw measured wet **LEVEL** and **POINT PAN** values/report numbers are missing independently. Original Cortar Ribbed wet WALL not individually listed and original Caviar exact NICHE still unverified; PH4 original owner 35 vs drawing 27 SF remains unreconciled.

## TX-PRIMARY: selected 48in Black Onyx LINEAR BT0734816-BNX + BR73480

Current Brizo {URL["linear"]} factory identifies grate reversible solid or tile-in and adjusted tile body **7–18mm**, separate rough REQUIRED. Rough current official {URL["linearrough"]} adds an integrated sloping channel, secondary water-protection system and hair catcher, no status to act as generic wall edge trim. TX source has one BR73480 labelled rough and another identical BR73480 labelled *wall edge trim*; require one verified vendor BOM, never automatically purchase two separate roughs. TX Primary WC floor remains included within parent's historic original mixed floor gross, no extra WC line. Do not add shower niches. Exact LINEAR pan tile, distinct LEVEL tile and original RAW measured numerical wet DCOF each missing, and no factory membrane/rough elevations signed.

## Source-footprint hydraulic datum section

PH4 prior shower rectangle **60x30.48in ~12.7000 SF**; TX Primary footprint prior **62.25x57.2496in ~24.752 SF**, *not certified actual 1529 shower polygons*. 24 new conditional slope/rise scenarios assign two drain placements, three hypothetical gradients **0.25, 0.3125, 0.375 in/ft**, two **CURBED/CURBLESS** threshold conditions, yielding approximate critical-rise values; none establishes Chicago-approved minima or floor-plane edges. Architect signs actual drain centerline and high-water termination, subfloor depressed/threshold, waterproof bond flange, owner finish, wall glass door and movement joints before full-size flatness/ponding physical witness. Floor versus PAN four alternate included/excluded original room-floor interpretations expressly prevent mixing source gross and physical pan area twice.

Illustrative **PH4** if prior 35 SF room area INCLUDES hypothetical 12.7 SF source footprint: LEVEL 22.3 SF, PAN 12.7 SF, total net35.0 before site recess; if room area EXCLUDES that pan: LEVEL35.0+PAN12.7 =47.7 SF. Both are contradictory candidate interpretations, NOT owner-approved takeoffs. Historic source floor40.2 gross/copy includes original 15% once, so neither new branch automatically becomes an order.

## Original lab and wet application witness

An individual maker's generic Wet Areas page or ASTM target >=0.42 is not numeric original wet DCOF. Require exact factory maker/SKU/color/finish/size raw measured wet reading, method, date and sample/batch separately for each flat LEVEL and sloped POINT/LINEAR PAN use; tile installer validates actual slope joints and exposure. The original R31 13 source roles remain immutable; new R31 13 role-to-material requirement table makes each request contract-checkable without inventing results. Current true-1529 site model unknown (open model is 1527). No substitute foreign membrane implied, no installed mockups, raw lab reports, purchased drains or building approvals claimed.
""")

mdout("R31_13_ROOM_ARCHITECT_GC_COST_SEQUENCE_OWNER_AND_OLD_TOWN_BUYER_BOOK.md",f"""
# R31 complete architect/GC/owner procurement and original four-seat governance book

Focus technical programs: TX-BATH4+PH-BATH2 **duplicated Hansgrohe 72411701/15758701 pressure-balance vs thermostat conflict**, PH-BATH4 **actual Brizo 4in POINT FOUR-PLANE PAN** and TX-PRIMARY **selected Brizo BNX 48in LINEAR with separate BR73480**. The formal board remains **R017**; do not transfer choice/status from conceptual package to ROOMS.json.

## Scope preserved for 13 distinct source rooms (two copies each)

"""+"\n".join(f"* **{x['id']}** ({x['status']}): {programs[x['id']]}" for x in rooms)+f"""

Every room's original source tile historical material cost is in the new 27-row source-to-current bridge. The total **$23,572.44**, four-unit tile-material-only and original 15% once, is unchanged; the two excluded, unpriced additional Primary niche references remain explicitly **NO SCOPE / NO ORDER**. Pre-existing niche Sandstone 51.64SF/$358.92, Cortar Grey Soft 165.40SF/$1,116.46, Caviar 34.52SF/$1,163.32 are included, not additive charge. Existing parent PH/TX Primary WC floors included once, original shared WC no new floor order, original individual LEVEL vs sloped PAN outputs separate. 25 historical wall elevation studies and 65 original trade RFI/action rows untouched, source R31 50 wall records/26 unit copy records untouched; their NEW R31 executable field/lot/shop instructions are additions.

New supplier normalization splits historical material-only rate from public retail, maker MSRP, verified current Chicago supplier offer, allowances, theoretical alternates and actual UNKNOWN complete installed GC bid. Historical Hansgrohe 2021 pressure balance 15739701 MSRP is NOT a current product quotation. No current Chicago availability, exact tile color/lot/case, freight, ETA, breakage, tax or full GC field bid asserted. Same-named Sandstone, Grey, Caviar and exact selected fixtures form conditional pooling candidates **only after same factory SKU/color/finish/caliber/shade-lot evidence**, never based on visual similarity alone. Floor raw wet lab transfer between LEVEL and PAN prohibited. No second 15% historic waste, niche wall aperture subtract once, add each actual back/side/top/sill once, actual trim/movement lengths separate installation labor; case totals use ceil only after actual carton usable SF.

## Contractor and procurement release sequence

1. Owner: signed actual existing program and any alternate fixture trim/spout/tile substitution; both Bath3 TUB-vs-WALKIN still unselected, PH3/TX2/TX Powder2 basins unselected, TX Powder two incompatible trim programs unselected. No owner cap/approval inferred.
2. Architect: certified authentic 1529 room identity, measured 26 physical instances and 50 W wall surfaces, tested 3in focal cuts, glass, valve/spout/drain/tub geometry and water control.
3. Plumber: original Brizo POINT/LINEAR and rough identities, both tub three outlet factory approved hydraulic diagrams (overhead/tub/hand), Duravit flange/access/overflow, proof of finish/temperature compatibility.
4. Waterproofer: factory-backed bonded membrane/backer/pipe collar/drain seal/tub flange returns and thresholds per actual product, not cross-brand assumed connections.
5. Tile installer: individual wet WALL vs NICHE item listing, original measured RAW numeric LEVEL and independent PAN wet lab, color/caliber, grout, profile, movement and full-size slope/frame mockup.
6. Supplier: exact factory color/finish/SKU/current same shade-caliber lot, exact useful SF/case, written shipping/tax/freight/ETA, real Chicago allocation; no vendor contacted.
7. GC: fully installed trade bid separated from original tile cost and any actual change-order credit; sample/field/rough/trim/drain accessories and labor covered, no hypothetical dollar savings booked.
8. Purchaser: only after all signatures plus original four-seat critic acceptance and legitimate independent Reviewer may an authorized party release material; all R31 flags FALSE.

## Old Town buyer value

User PH target ~$2.8M, TX ~$2.7M; comp band $2.4M–$3.2M. Research's 14 listing records represent **nine buildings**, with OT01–OT04 at 405 W Armitage ONE design precedent. Old Town first, Lincoln Park/Gold Coast secondary. Better buyer value from mechanically reliable 3-outlet tub/shower, low-stress cleanable floor/niche, maintainable adjustable point/linear drain and coordinated Matte White/BNX finish; no invented competitor tile identity or material-caused sale premium. Premium labor/thermostatic-to-pressure-balance switch may be buyer-negative; evaluate owner comfort and lifecycle service instead of unsupported price upside.

## Blind governance and review

Original MARKET worker13 weight .30, DESIGN worker9 .25 (R014 two missing failed), BUILD worker10 .25, COST worker12 .20. R014 six of eight, R015 partial critic dispatch HOLD; R017 frozen neutral packets/four keys independent preflight absent. Existing non-Pro Reviewer worker15 finished/nonrevivable after PRECISE FIX R23; no new judge/revival, duplicate R017 candidates, partial three-seat review or weighted score. Original gates require **four** authentic original independent critiques, every hard gate PASS, minimum critic seat score >=3.0 and weighted challenger margin >=+.25. This is **not a source submission turn**, no scoring or champion changes. R31 five-section independent report UNSENT/UNREVIEWED. Global entire 13-room objective OPEN; zero Revit/Smartsheet/model/Git writes outside these additive workspace files, no external messages, forms, samples or purchases.
""")

# Actual 18 signed R12-R29 manifests verified from disk, plus both R30 and R31 source hashes.
predecessor={}
for i in range(12,30):
    matches=[d for d in (ROOT/"deliverables").glob(f"integrated-r{i}*")
             if (d/"MANIFEST.json").exists() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(matches)==1,(i,matches)
    predecessor[f"R{i:03d}_INTEGRATED_MANIFEST_SHA256"]=hashlib.sha256((matches[0]/"MANIFEST.json").read_bytes()).hexdigest()
predecessor["R030_FINAL_INTEGRATED_MANIFEST_SHA256"]=R30_HASH
predecessor["R031_PRELIMINARY_SOURCE_SHA256"]=R31_HASH
for n,filename in [
    ("R014_SUBMISSION","ROUND014_SUBMISSION.json"),
    ("R015_SUBMISSION","ROUND015_SUBMISSION.json"),
    ("R016_SUBMISSION","ROUND016_SUBMISSION.json"),
    ("R017_SUBMISSION","ROUND017_SUBMISSION.json")]:
    p=ROOT/"state"/filename
    assert p.is_file()
    predecessor[f"{n}_CURRENT_RECEIPT_SHA256"]=hashlib.sha256(p.read_bytes()).hexdigest()
assert len(FILES)>=18,len(FILES)
manifest=dict(round=31,date_local="2026-11-06",
  project="1529 Wieland 13 distinct bathrooms two copies each",
  phase="FULL_INTEGRATED_SOURCE_CONSTRUCTION_PROCUREMENT_NO_BLIND_SCORING",
  focus_rooms=list(focus),immutable_predecessor_SHA256=predecessor,
  original_invariants=dict(room_count=13,physical_instances=26,material_lines=27,
       unpriced_primary_niche_no_order_rows=2,original_wall_elevation_sources=25,
       original_trade_action_rows=65,material_only_USD="23572.44",
       original_historical_waste_included_once="15_percent",
       sandstone_niche_original_subtotal_USD="358.92",
       grey_soft_historic_subtotal_USD="1116.46",
       Caviar_niche_original_subtotal_USD="1163.32",
       old_town_listings=14,unique_buildings=9),
  new_schedules=dict(maker_rows=len(maker),tub_outlet_decision_rows=len(decision),
       tub_fit_rows=len(tub_fit),finish_buildup_rows=len(stack),slope_threshold_rows=len(slope),
       level_pan_split_rows=len(separation),W1_W3_tolerance_rows=len(widthcases),
       exact_original_raw_wet_specimen_roles=len(labrows),wall_field_survey_rows=len(walltasks),
       room_copy_witness_rows=len(unitrecords),owner_GOOD_BETTER_BEST_rows=len(choices),
       historic_supplier_normalization_rows=len(quote),same_lot_pool_exclusion_rows=len(groups),
       one_to_one_camera_rows=len(views),full_room_release_rows=len(release),
       staged_eight_trade_gates=len(trade),two_copy_installed_scope_rows=len(costs)),
  actual_native_1529_verified=False,all_numeric_original_raw_lab_reports_known=False,
  PH4_selected_POINT_unchanged=True,TXPrimary_selected_48in_LINEAR_rough_unchanged=True,
  both_TUB_Matte_White_unchanged=True,both_Bath3_owner_tub_vs_walkin_unselected=True,
  tile_budget_cap_approved=False,current_Chicago_supplier_offer_verified=False,
  real_physical_sample_delivered=False,owner_approved=False,architect_approved=False,
  plumber_approved=False,waterproofing_approved=False,tile_installer_approved=False,
  supplier_approved=False,GC_approved=False,purchaser_approved=False,
  purchase_authorized=False,original_four_specialists_complete=False,
  independent_nonpro_reviewer_accepted=False,weighted_board_score=None,global_13room_DONE=False,
  source_files=[dict(relative_path=k,bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in sorted(FILES.items())])
OUT.mkdir(parents=True,exist_ok=False)
for name,content in sorted(FILES.items()):
    with (OUT/name).open("xb") as f:f.write(content)
(OUT/"MANIFEST.json").write_bytes((json.dumps(manifest,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R31_FULL_INTEGRATED",OUT)
print("FILE_COUNT",len(FILES),"MANIFEST_SHA",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
print("SCHEDULES",json.dumps(manifest["new_schedules"],sort_keys=True))
