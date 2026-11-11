"""One-time additive R33 integrated three-tub design/GC/procurement engineering.

All R30-R32 signed outputs and original R12-R29 remain immutable.
This script computes from source schedules only, never asserts a true 1529 field
survey, original numeric lab reading, vendor bid, owner selection or release.
"""
from __future__ import annotations
import csv, hashlib, io, json, math
from decimal import Decimal
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"deliverables"/"integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC"
assert not OUT.exists(),"R33 integrated package already exists; never overwrite."
H={
 "R30":"5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a",
 "R31_SOURCE":"61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419",
 "R31_FULL":"b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457",
 "R32_SOURCE":"9ad8564e2676f4e72533e6830bea627757e393dc1cdc537b297d443caae962b4",
}
PRE={
 "R30":ROOT/"deliverables/integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement/MANIFEST.json",
 "R31_SOURCE":ROOT/"state/ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json",
 "R31_FULL":ROOT/"deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/MANIFEST.json",
 "R32_SOURCE":ROOT/"state/ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json",
}
assert all(hashlib.sha256(v.read_bytes()).hexdigest()==H[k] for k,v in PRE.items())
def readcsv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
HIST=ROOT/"deliverables/integrated-r17"
old=readcsv(HIST/"R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
w25=readcsv(HIST/"R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
prior65=readcsv(ROOT/"deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
source13=readcsv(ROOT/"research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
source50=readcsv(ROOT/"research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
source26=readcsv(ROOT/"research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
source6=readcsv(ROOT/"research/products/R32_20261106_THREE_TUB_SIX_UNIT_ACTUAL_SELECTED_VS_MISSING_MIXING_ROUGH_SPOUT_BOM.csv")
source9=readcsv(ROOT/"research/products/R32_20261106_NINE_ORIGINAL_TUB_WALL_SOURCE_TO_INSTALL_BOM_DEPENDENCY_SECTIONS.csv")
ROOMS=json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(ROOMS),len(old),len(w25),len(prior65),len(source13),len(source50),len(source26),len(source6),len(source9))==(13,27,25,65,13,50,26,6,9)
assert sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
rid={r["id"]:r for r in ROOMS}
focus=("PH-BATH2","TX-BATH2","TX-BATH4")
def fixture(room):return json.loads((ROOT/"rooms"/room/"plumbing.json").read_text(encoding="utf-8"))["fixtures"]
def sku(room):return {str(x["model_or_sku"]) for x in fixture(room)}
for r in focus:assert "700332000000090" in sku(r)
assert all({"15758701","01850181","72411701"}.issubset(sku(r)) for r in ("PH-BATH2","TX-BATH4"))
assert {"04790000","04925000","27458003"}.issubset(sku("TX-BATH2"))
assert not any(x in sku("TX-BATH2") for x in ("15758701","01850181","72411701","72410701","15739701"))
wall={(x["room"],x["wall"]):x for x in w25}
by_material={(x["room"],x["source_surface"]):x for x in old}
assert len(wall)==25
assert all(len(json.loads((ROOT/"rooms"/r/"geometry.json").read_text(encoding="utf-8"))["revit_room_numbers"])==2 for r in focus)
u6={(x["room"],x["source_physical_room"]):x for x in source6}
assert len(u6)==6
assert all(x["purchase_authorized"]=="FALSE" for x in source6)
def dec(x):return Decimal(str(x))
def f4(x):return f"{x:.4f}"
def tf(q):return "TRUE" if q else "FALSE"
FILES={}
def csvout(name,rows):
    assert rows and len({tuple(x.keys()) for x in rows})==1,(name,len(rows))
    s=io.StringIO(newline="")
    w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    FILES[name]=s.getvalue().encode("utf-8-sig")
def mdout(name,s):FILES[name]=(s.rstrip()+"\n").encode("utf-8")
URL={
 "spout":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-with-diverter-72411701",
 "nondiv":"https://www.hansgrohe-usa.com/articledetail-talis-s-tub-spout-72410701",
 "price2021":"https://assets.hansgrohe.com/celum/web/hansgrohePriceBook2021USf01052Release.pdf",
 "rough":"https://www.hansgrohe-usa.com/articledetail-ibox-universal-rough-with-service-stops-01850181",
 "chromehead":"https://pro.hansgrohe-usa.com/articledetail-croma-select-e-showerhead-180-2-jet-2-5-gpm-04925000",
 "chromehand":"https://pro.hansgrohe-usa.com/articledetail-croma-select-e-wallbar-set-110-3-jet-24-1-75-gpm-04790000",
 "chromeout":"https://www.hansgrohe-usa.com/articledetail-fixfit-wall-outlet-round-with-check-valves-27458003",
 "duravit":"https://pro.duravit.us/pro/content/homepage/series/sizes/overview/products~402880943a1b6e1b013a1bd2b8e3005b.us-en.html?ncat=undefined&nser=1110&product=3169419",
 "flange":"https://pro.duravit.us/pro/content/homepage/series/categories/overview/products~402880943a1b6e1b013a1bd2494e0047.us-en.html?ncat=accessories&nser=8002&product=105401",
 "soho":"https://www.elmsurfaces.com/product/soho-ivory",
 "clara":"https://traditionsintile.com/project/clara/",
 "charcoal":"https://www.elmsurfaces.com/product/cortar-charcoal",
 "maker_tone":"https://www.elmsurfaces.com/product-collection/tones",
 "kbdiscontinued":"https://www.kbauthority.com/hansgrohe-15758701-ecostat-s-5-7-8-inch-thermostatic-trim-with-volume-control-and-diverter-matte-white.html",
 "home_depot":"https://www.homedepot.com/p/332328623",
}
program={
 "PH-BATH2":"TUB_700332_HANSGROHE_MATTE_WHITE_THERMOSTAT_DIVERTER_CONFLICT_NO_PAN",
 "TX-BATH2":"TUB_700332_HANSGROHE_CHROME_MIXING_ROUGH_TUB_FILL_UNIDENTIFIED_NO_PAN",
 "TX-BATH4":"TUB_700332_HANSGROHE_MATTE_WHITE_THERMOSTAT_DIVERTER_CONFLICT_NO_PAN",
}
materials={
 "PH-BATH2":("ELM Tones Sapphire 2x20 Glossy","ELM Tones Sandstone niche","Cortar Grey Soft LEVEL","2x20 horizontal long axis source nominal, actual factory caliber unverified","MAKER_INDIVIDUAL_WET_WALL_AND_NICHE_REPORTED_PASS"),
 "TX-BATH2":("ELM Tones Copper 2x20 Glossy","ELM Tones Sandstone niche","Cortar Clay Soft LEVEL","2x20 horizontal long axis source nominal, actual factory caliber unverified","MAKER_COPPER_SANDSTONE_WET_WALL_NICHE_REPORTED_PASS_SOURCE_REFRESH"),
 "TX-BATH4":("ELM Cortar Charcoal FLAT 24x48","Clara Caviar 2x8 niche","Cortar Bone Soft LEVEL","24x48 historic flat source, actual caliber unverified","CHARCOAL_FLAT_MAKER_WET_WALL_REPORTED_PASS_CAVIAR_INDIVIDUAL_WET_NICHE_HOLD"),
}

# Actually selected and conditional factory identity evidence. Current list MSRP is
# a comparison class only; never a purchasing line or equivalence proof.
factory=[
 ("Duravit","700332000000090","White sanitary acrylic built-in TUB with original support frame, 59 x 29.5in",
  "ALL_THREE_SELECTED","MODEL_CURRENT_OFFICIAL","$1550 maker U.S. list, not project quote","59in outer cannot establish actual 1529 finished-wall clearance",URL["duravit"]),
 ("Duravit","790112000000000","Tile flange 16in maker accessory listed suitable for selected tub",
  "UNSELECTED_ACCESSORY","CURRENT_OFFICIAL_ACCESSORY","$360 maker list, not unit or complete surround","16in accessory NOT proven continuous 59in/3-wall system; manufacturer attachment/coverage unknown",URL["flange"]),
 ("Hansgrohe","72411701","Matte White Talis S tub spout with pull-up diverter",
  "PH2_TX4_SELECTED","CURRENT_OFFICIAL_ITEM","$382 maker list indication; four copies theoretical","For pressure-balance valve ONLY, source thermostat 15758701 compatibility HOLD",URL["spout"]),
 ("Hansgrohe","15758701","Matte White Ecostat S thermostat with volume and TWO-outlet diverter",
  "PH2_TX4_SELECTED","2021_MAKER_FACTORY_PLUS_RETAIL_CURRENT_RESTRICTIONS","$693 maker 2021 MSRP NOT current supplier","Three endpoints need maker routing; 2026 retailers show conflicting availability",URL["price2021"]),
 ("Hansgrohe","01850181","iBox Universal Plus rough with service stops",
  "PH2_TX4_SELECTED","2021_MAKER_REQUIRED_ROUGH","2021 $169 list not 2026 quote","Rough mounting orientation alone does NOT approve every trim/spout operating system",URL["price2021"]),
 ("Hansgrohe","72410701","Matte White Talis S tub spout without pull-up diverter",
  "UNSELECTED_ALT_MW","CURRENT_OFFICIAL_ITEM","$321 U.S. maker list, $61 less MSRP per piece than 72411701, not credit","2-outlet thermostat still needs written shower-head/handshower selection with 3 endpoints",URL["nondiv"]),
 ("Hansgrohe","15739701","Matte White Ecostat S PRESSURE BALANCE with integrated diverter-spout bypass, ONE shower outlet",
  "UNSELECTED_ALT_MW","2021_MAKER_ONLY_CURRENT_FACTORY_STOCK_UNKNOWN","$274 maker 2021 list, not comparable 2026 value","May be discontinued; neither current availability nor hand/head switching nor owner control accepted",URL["price2021"]),
 ("Hansgrohe","04925000","Chrome Croma Select E overhead 7in, maximum 2.5GPM",
  "TX2_SELECTED","CURRENT_OFFICIAL_ITEM","UNKNOWN current Chicago quote","Shower head is not a shower mixing-valve trim/rough or tub spout",URL["chromehead"]),
 ("Hansgrohe","04790000","Chrome Croma Select E wallbar+hand shower+slider+hose, maximum 1.75GPM",
  "TX2_SELECTED","CURRENT_OFFICIAL_ITEM","UNKNOWN current Chicago quote","Fixture kit not a bath mixing-valve rough or tub-fill spout; don't presume missing field installation",URL["chromehand"]),
 ("Hansgrohe","27458003","Chrome FixFit outlet with check valves/backflow prevention",
  "TX2_SELECTED","CURRENT_OFFICIAL_ITEM","$113 maker list not installed quote","Wall outlet is not a mixing valve/diverter or rough, port assignments missing",URL["chromeout"]),
 ("Westbrass","TD954-20LT","Tub waste/overflow PVC rough less trim",
  "ALL_THREE_SELECTED","ORIGINAL_SCHEDULE_ONLY_NO_LIVE_MAKER_WASTE_SHEET","UNKNOWN installed","Compatibility with Duravit overflow and actual trap access requires exact product/system approval",""),
 ("Westbrass","TD9028-LS-PCW / TD9028-PCW","Source PH2/TX4 corrected white tiptoe trim vs TX2 old LS-PCW row",
  "SOURCE_IDENTITY_DISCREPANCY_NOT_SELECTED_CHANGE","ORIGINAL_ROOM_SCHEDULE_CORRECTION","UNKNOWN","Correct dated source, maker identity and drain/overflow thread before combining current order",""),
]
csvout("R33_12_FACTORY_ACTUAL_VS_UNSELECTED_COMPONENTS_AND_APPLICATION_EVIDENCE.csv",[
 dict(maker=m,exact_model_or_source_code=i,identity=d,selection_scope=selected,evidence_grade=grade,
      price_classification=price,hard_factory_or_scope_gate=gate,manufacturer_evidence_url=url,
      current_chicago_warehouse_offer="",factory_system_approval_document="",owner_substitution_approved="FALSE",
      purchase_authorized="FALSE") for m,i,d,selected,grade,price,gate,url in factory
])

# Decision hierarchy: not merely new product swap, demands complete operating system,
# independent outlet routing/flow/backflow and full physical rework bid.
tiers=[]
for r in focus:
    if r=="TX-BATH2":
        choices=[
         ("GOOD","SOURCE_RECONCILIATION_NO_CHANGE","Recover TX2 ORIGINAL selected Chrome bathing mixer trim, cartridge, rough, tub-fill spout and any diverter from actual v3.2/dated Smartsheet and source submittal; DO NOT invent SKUs.","0 allowed fixture substitutions; no pricing before owner-approved historical identity.","BLOCKED_BOM","Preserves original Chrome fixtures/design but incomplete constructor instructions."),
         ("BETTER","CONDITIONAL_FACTORY_CHROME_THREE_OUTLET_SHOP","Maintain Chrome 04925000 overhead, 04790000 hand shower kit, 27458003 check-valve outlet, selected Duravit; after source identification route TUB+HEAD+HAND with signed compatible mixer, tub-fill and selector in Chrome.","Extra documented control, penetrations and independent distribution may be needed; no known source labor/price.","UNSELECTED_OWNER_ONLY","Could improve service/control clarity, pending exact original SKU and finish."),
         ("BEST","CONDITIONAL_ACCESSIBLE_CHROME_THREE_ENDPOINT_SYSTEM","Retain chosen Chrome endpoints and tub, but request owner/architect/plumber approved, serviceable factory-proven control/selector in measured W1 wall and aligned splash-proof access; source missing controls remain unselected.","Potential new valve-depth/service panel/piping/waterproof wall repair; do not budget savings.","UNSELECTED_OWNER_ONLY","Clean coordinated trim/long-term service at potentially higher cost."),
        ]
    else:
        choices=[
         ("GOOD","OWNER_ORIGINAL_COMPONENTS_HARD_HOLD","Keep 15758701 two-outlet thermostat, 01850181 rough and 72411701 pressure-balance-only diverter spout as selected but NO installation release until maker specifically authorizes exact 3-function routing.","No fixture change; contractor must isolate and price possible correction risk.","BLOCKED_COMPATIBILITY","Existing selected Matte White appearance is retained as non-installable reference pending factory proof."),
         ("BETTER","CONDITIONAL_NON_DIVERTER_72410701","Preserve selected 15758701 thermostatic operation and 01850181 rough subject to manufacturer clearance, propose unselected 72410701 Matte White non-diverter tub spout; design separate maker-approved selector for HEAD and HAND shower.","Replace spout + possibly add shower selector/rough, penetration, finish repair and retest; $61 per unit maker MSRP difference is NON-COMPARABLE.","UNSELECTED_OWNER_ONLY","Continuous Matte White aesthetic without pull-up lever, with potentially added shower selector."),
         ("BEST","CONDITIONAL_PRESSURE_BALANCE_15739701","Preserve selected 72411701 tub pull-up diverter spout; owner-only option historic 15739701 Matte White pressure-balance with integrated bypass, separate maker-approved HEAD/HAND selector, exact compatible cartridge/rough.","Changes thermostatic to pressure-balance control program, historic 2021 item may be unavailable, rework and safety validation unknown; not a current purchasable option.","UNSELECTED_OWNER_ONLY","Keeps pull-up spout but changes control feel and could impair market/service appeal."),
        ]
    for tier,scenario,design,estimate,approval,val in choices:
        tiers.append(dict(room=r,tier=tier,proposal=scenario,owner_facing_design=design,
          actual_three_endpoints="TUB_FILL;OVERHEAD_SHOWER;HAND_SHOWER",
          selected_tub="700332000000090",selected_finish="CHROME" if r=="TX-BATH2" else "MATTE_WHITE",
          selected_components_immutable="TRUE",actual_full_factory_operating_system_qualified="FALSE",
          qty_and_changeorder_exposure=estimate,owner_path_status=approval,design_lifecycle_consequence=val,
          LEVEL_raw_measured_wet_DCOF="MISSING_ORIGINAL_EXACT_NUMERIC",tiled_shower_PAN="N_A",
          source_exact_1529_valve_spout_clearance="",factory_signed_triplex_outlet_diagram="",
          full_installed_GC_bid="",owner_approved="FALSE",architect_signed="FALSE",
          plumber_signed="FALSE",purchase_authorized="FALSE",weighted_board_score="NULL"))
assert len(tiers)==9
csvout("R33_9_THREE_TUB_GOOD_BETTER_BEST_REAL_CONTROL_AND_SERVICE_PATHS.csv",tiers)

# Enumerate actually selected three endpoints and known/unknown feed paths without
# inventing manufacturer-approved outlet pipes from merely two selector ports.
paths=[]
for x in source6:
    room=x["room"]; no_controls=room=="TX-BATH2"
    for tier in ("GOOD","BETTER","BEST"):
        for endpoint in ("TUB_FILL","OVERHEAD_SHOWER","HAND_SHOWER"):
            if no_controls:
                source_item={"TUB_FILL":"MISSING_SOURCE_SPOUT","OVERHEAD_SHOWER":"04925000_CHROME","HAND_SHOWER":"04790000_CHROME_WITH_27458003_CHECK_VALVE"}[endpoint]
                mix="SOURCE_MISSING_NOT_PHYSICALLY_PROVEN_ABSENT"
            else:
                source_item={"TUB_FILL":"72411701_MATTE_WHITE_DIVERTER_PRESSURE_BALANCE_ONLY","OVERHEAD_SHOWER":"04388700_MATTE_WHITE","HAND_SHOWER":"26866701_MATTE_WHITE_26843701_WALL_OUTLET"}[endpoint]
                mix="15758701_THERMOSTATIC_TWO_OUTLET_ON_01850181_ROUGH"
            branch=next(z for z in tiers if z["room"]==room and z["tier"]==tier)
            paths.append(dict(room=room,physical_source_room=x["source_physical_room"],tier=tier,
               endpoint=endpoint,actual_selected_endpoint_part_or_missing=source_item,
               source_mixer_and_rough=mix,owner_alternative_NOT_SELECTED=branch["proposal"],
               factory_certified_hot_cold_mixer_and_distribution_port="UNASSIGNED",
               documented_required_flow_pressure_valve_and_backflow_check="UNKNOWN_FACTORY_REPORT",
               approved_cartridge_and_diverter_current_orderable_SKU="",
               selected_duravit_support_and_waste_access="UNVERIFIED_FIELD",
               hot_cold_crossflow_and_thermal_shock_design_verified="FALSE",
               finish_face_trim_clearance_field_mm="",mounted_control_service_clearance_in="",
               factory_schematic_revision="",licensed_plumber_actual_routing_signature="",
               owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(paths)==54
csvout("R33_54_PHYSICAL_OUTLET_LEVEL_HYDRAULIC_PORT_RFI_MATRIX.csv",paths)

# Reconcile three complete source W1/W2/W3 full faces against the original
# already-wasted historic wall gross. This arithmetic is new and NOT a field takeoff.
roomsheet=[]
for r in focus:
    ws=[wall[r,k] for k in ("W1","W2","W3")]
    w=[float(x["source_width_in_UNVERIFIED"]) for x in ws]
    ht=float(ws[0]["source_tiled_height_in_UNVERIFIED"])
    assert all(float(x["source_tiled_height_in_UNVERIFIED"])==ht for x in ws)
    face=sum(w)*ht/144
    old_wall=by_material[r,"wall"]
    old_gross=float(old_wall["source_gross_sf_one_copy_waste_15pct_once"])
    rate=Decimal(old_wall["historic_usd_two_copies"])/Decimal(str(old_gross*2))
    roomsheet.append(dict(room=r,physical_copies=2,source_W1_in_UNVERIFIED=f4(w[0]),
      source_W2_in_UNVERIFIED=f4(w[1]),source_W3_in_UNVERIFIED=f4(w[2]),
      source_height_each_in_UNVERIFIED=f4(ht),
      unverified_full_3wall_FIELD_NET_SF_per_copy_before_openings=f4(face),
      theoretical_source_full_3wall_NET_times_original_15pct_once_SF_per_copy=f4(face*1.15),
      historic_original_wall_GROSS_SF_per_copy_15pct_already_included=f4(old_gross),
      historical_quote_GROSS_minus_source_geometric_1point15_SF_per_copy=f4(old_gross-face*1.15),
      historic_wall_rate_per_GROSS_SF_only_USD=f"{rate:.4f}",
      historic_two_copy_wall_material_only_USD=old_wall["historic_usd_two_copies"],
      maker_wall_identity_and_source_nominal_format=materials[r][0],
      maker_niche_identity_historical=materials[r][1],
      LEVEL_source_identity=materials[r][2],
      manufacturer_tub_outer_nominal_in="59.0000",
      source_W1_minus_tub_outer_nominal_in=f4(w[0]-59),
      source_3side_tub_rim_joint_PROXY_LF=f4(sum(w)/12),
      potential_2exposed_vertical_tile_edges_PROXY_LF=f4(2*ht/12),
      source_TUB_RIM_LF_for_six_units_group_not_measured="SOURCE_ONLY_NOT_PERIMETER_PAYMENT",
      measured_truE_1529_W_openings_flange_and_spout="",
      source_wall_face_not_net_installed="TRUE",
      original15pct_not_added_twice="TRUE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(roomsheet)==3
csvout("R33_3_TUB_W1W2W3_WALL_GROSS_TO_HISTORIC_15PCT_QUOTE_RECONCILIATION.csv",roomsheet)

# Tub wall tile-layout specific orientation/cut alternatives, not R30 niche study.
# Minimum 3-inch test applies to pieces cut from a long tile dimension; a nominal
# two-inch-long intentional short-axis module is exempt and not modeled here.
module=[]
for r in focus:
    for wallid in ("W1","W3"):
        sw=float(wall[r,wallid]["source_width_in_UNVERIFIED"])
        maker=materials[r][0]
        if r=="TX-BATH4":
            systems=[("24IN_LONG_AXIS_CENTERED",24,2 if wallid=="W1" else 1,"BALANCED"),
                     ("48IN_LONG_AXIS_ALTERNATE",48,1 if wallid=="W1" else 0,"BALANCED_OR_SINGLE_FULL_CUT")]
        elif wallid=="W1":
            systems=[("20IN_TWO_FULL_MIDDLE",20,2,"BALANCED"),("20IN_THREE_FULL_MIDDLE_RISK",20,3,"BALANCED")]
        else:
            systems=[("20IN_ONE_FULL_CENTER",20,1,"BALANCED"),("20IN_ONE_END_FULL_UNBALANCED",20,1,"ONE_SIDED")]
        for mode,T,N,align in systems:
            for joint in (.125,.1875,.25):
                if align=="ONE_SIDED":
                    end=sw-T-joint
                    left=0.0;right=end
                    good=0<=end<=T
                    pieces=2;cut=min(T,end) if good else 0
                    length_from_full_tile=2*T-sw+joint
                    flag="PASS_FOCAL_NOT_BALANCED" if good and cut>=3 else "FAIL_FOCAL_CUT_OR_MODULE"
                elif N==0:
                    good=sw<=T
                    left=right=0.
                    pieces=1;cut=sw;length_from_full_tile=T-sw
                    flag="ONE_PIECE_FIELD_CUT_NO_SIDE_PIER" if good and cut>=3 else "FAIL_SINGLE_PIECE_WIDTH"
                else:
                    end=(sw-N*T-(N+1)*joint)/2
                    left=right=end;good=0<end<=T
                    pieces=N+2;cut=end
                    length_from_full_tile=2*(T-end)
                    flag="PASS_FOCAL_BALANCED" if good and end>=3 else "FAIL_NEGATIVE_OR_UNDER_3IN_FOCAL"
                module.append(dict(room=r,wall=wallid,material_SOURCE_not_approved_current_SKU=maker,
                    long_axis_nominal_tile_in=f4(T),selected_candidate_module=mode,
                    central_full_tiles=N,joint_width_in_ILLUSTRATIVE=f4(joint),
                    source_wall_span_in_UNVERIFIED=f4(sw),alignment=align,
                    left_visible_end_piece_in=f4(left),right_visible_end_piece_in=f4(right),
                    focal_smallest_end_piece_in=f4(cut),minimum3in_focal_gate=flag,
                    theoretical_long_axis_pieces_per_row=pieces,
                    total_trim_cut_offcuts_per_TWO_endpieces_in_NOT_ACTUAL=f4(max(0,length_from_full_tile)),
                    actual_tile_body_factory_caliber_and_grout_approval="UNVERIFIED",
                    onsite_actual_glass_valve_niche_PENETRATION_cut_clashes="UNKNOWN",
                    height_module_and_rows_unverified="TRUE",
                    balanced_design_preference="REQUEST_1TO1_FOCAL_WALL" if good else "REJECT_CONCEPT",
                    physical_1529_factory_shop_verified="FALSE",owner_approved="FALSE",
                    purchase_authorized="FALSE"))
assert len(module)==36
csvout("R33_36_SOURCE_W1W3_TONES_2X20_VS_CHARCOAL_24X48_FOCAL_TILE_MODULES.csv",module)

# Six physical tubs, actual wall survey controls and installation datums.
wall18=[]
for x in source6:
    r=x["room"]
    for w in ("W1","W2","W3"):
        oldw=wall[r,w]
        sw=float(oldw["source_width_in_UNVERIFIED"]);height=float(oldw["source_tiled_height_in_UNVERIFIED"])
        wall18.append(dict(room=r,physical_source_room=x["source_physical_room"],wall=w,
            original_revision_of_true_1529_model="UNKNOWN_1527_IS_NOT_1529",
            drawing_source_wall_width_in_UNVERIFIED=f4(sw),
            drawing_source_tiled_height_in_UNVERIFIED=f4(height),
            unverified_full_rect_FACE_SF_before_any_opening=f4(sw*height/144),
            source_tub_length_in="59.0000",source_W1_minus_59in_in=f4(sw-59) if w=="W1" else "NOT_TUB_LENGTH_WALL",
            valve_and_3outlet_routing_gate=program[r],
            maker_selected_wet_WALL=materials[r][0],
            maker_selected_wet_NICHE=materials[r][1],
            certified_1529_wall_orientation_and_reference_edge="",
            actual_measured_W_in="",actual_measured_tile_height_in="",
            actual_door_window_OTHER_aperture_SF="",actual_niche_COUNT="",
            actual_niche_front_aperture_negative_FIELD_SF_once="",
            actual_independent_niche_BACK_SF="",actual_TWO_SIDE_returns_SF="",
            actual_niche_TOP_SF="",actual_niche_SILL_SF="",
            actual_signed_NET_WALL_SF="",
            actual_2side_tub_flange_membrane_corner_and_sill_elevation="",
            actual_spout_mixer_rough_cartridge_centerlines_and_clearances="",
            actual_escutcheon_outlet_arm_cleanable_penetrations="",
            source_tub_RIM_termination_joint_LF_if_applicable=f4(sw/12),
            actual_signed_tub_to_wall_movement_joint_LF="",
            actual_signed_exposed_vertical_edge_PROFILE_LF="",
            extra_wall_NICHE_not_invented="TRUE",
            maker_item_wet_WALL_vs_NICHE_separate="TRUE",
            field_witness_initials="",install_submittal_signed="FALSE",
            owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(wall18)==18
csvout("R33_18_SIX_TUB_REAL_PHYSICAL_WALL_SURVEY_NICHE_RIM_EDGE_AND_FIXTURE_SHOP_INSTRUCTIONS.csv",wall18)

# 36 true physical-copy *hypothetical* rough opening/installed finish cases,
# mathematically possible corridor is NOT an approved tub-before-tiling setting method.
fit=[]
for x in source6:
    r=x["room"];sw=float(wall[r,"W1"]["source_width_in_UNVERIFIED"])
    for drift in (-.25,0,.25):
        for each_end in (.25,.5):
            clear=sw+drift-2*each_end
            fit.append(dict(room=r,physical_source_room=x["source_physical_room"],
               selected_tub="700332000000090_59IN_LENGTH",
               original_W1_source_in_UNVERIFIED=f4(sw),
               hypothetical_actual_FIELD_delta_in=f4(drift),
               hypothetical_end_wall_BUILDUP_each_in=f4(each_end),
               hypothetical_59in_tub_insert_AFTER_FINISH_clear_in=f4(clear),
               source_minus_factory_tub_body_in=f4(clear-59),
               hypothetical_after_FINISH_clear_gate=("NEGATIVE_NOT_FIT_IN_THIS_HYPOTHESIS" if clear<59 else "NONNEGATIVE_BUT_NOT_CERTIFIED"),
               tub_may_install_BEFORE_wall_finishes="REQUIRES_DURAVIT_FIELD_SEQUENCE",
               true_1529_rough_wall_width="",true_1529_tub_support_frame_location="",
               actual_required_factory_setback_and_anchors="",factory_approved_flange_solution="",
               actual_measured_valve_iBox_rough_depth_and_spout_projection="",
               one_to_one_physical_rough_finish_mockup_pass="FALSE",
               purchase_authorized="FALSE"))
assert len(fit)==36
csvout("R33_36_SIX_UNIT_TUB_W1_ROUGH_FINISH_CORRIDOR_TOLERANCE_CASES.csv",fit)

# Two alternate wall construction stack materials per selected tub program;
# membrane and seal are not assumed zero and this can NEVER qualify a rough.
planes=[]
for r in focus:
    for backer in (.375,.5,.625):
        for thinset in (.125,.1875):
            for tile in (.3125,.375):
                partial=backer+thinset+tile
                planes.append(dict(room=r,
                    selected_source_tub_and_physical_finish=program[r],
                    hypothetical_backer_in=f4(backer),hypothetical_mortar_COMPRESSED_in=f4(thinset),
                    hypothetical_tile_BODY_in=f4(tile),
                    partial_total_EXCLUDING_MEMBRANE_gasket_and_frustrated_tub_flange_in=f4(partial),
                    actual_waterproof_MEMBRANE_thickness_in="UNKNOWN_NOT_ZERO",
                    actual_factory_tile_caliber_and_max_mortar_lift="UNKNOWN",
                    actual_selected_rough_iBox_depth_window_or_unknown_TX2="UNKNOWN",
                    actual_escutcheon_cover_overlap_and_fitting_seal_in="UNKNOWN",
                    actual_waste_overflow_and_spout_projection_or_missing_TX2="UNKNOWN",
                    proper_alcove_tile_face_to_tub_sill_interference="UNKNOWN",
                    clearance_decision="BLOCKED_PENDING_PHYSICAL_CALIBRATED_SECTION",
                    onsite_mockup_witness="FALSE",manufacturer_signed="FALSE",
                    owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(planes)==36
csvout("R33_36_TUB_MIXER_SPOUT_BACKER_MEMBRANE_MORTAR_TILE_PLANE_STACK_HOLDS.csv",planes)

# A single synthetic niche serves a *deduction method example*, not a new niche
# schedule, and carries no actual order/waste assumption. This is deliberate to
# avoid duplicating R30's 144 niche layout cases.
niches=[]
for x in source6:
    aperture=16*12/144
    back=aperture
    sides=2*12*4/144
    top=sill=16*4/144
    niches.append(dict(room=x["room"],physical_source_room=x["source_physical_room"],
       illustrative_1niche_not_actual_width_in="16",height_in="12",depth_in="4",
       single_wall_FIELD_aperture_SF_Deduct_once=f4(aperture),
       independent_niche_BACK_SF=f4(back),both_SIDE_SF=f4(sides),
       TOP_SF=f4(top),SILL_SF=f4(sill),
       sample_niche_NET_tile_surface_SF_before_new_waste=f4(back+sides+top+sill),
       entire_wall_NET_formula="SIGNED_W*H/144-OTHER_OPENINGS-ONCE_NICHE_FRONT+BACK+TWO_SIDES+TOP+SILL",
       actual_niche_count_location_plumbing_conflict="UNKNOWN_NO_ORDER",
       actual_shower_or_tub_WET_NICHE_individual_SKU_certified="FALSE",
       exposed_trim_LF="ACTUAL_FIELD_AND_PROFILE_MUST_BE_SEPARATELY_MEASURED",
       sill_slope_and_1to1_membrane_mockup="NOT_DONE",purchase_authorized="FALSE"))
assert len(niches)==6
csvout("R33_6_SYNTHETIC_SINGLE_NICHE_WALL_DEDUCTION_VS_FIVE_SEPARATE_RETURNS.csv",niches)

# Source-only mathematical change-order sensitivities: historical quoted wall
# per-GROSS rate multiplied by *net* dimension displacement, intentionally with
# NO second waste and NO new price. No fractional carton/genuine savings claimed.
ratecases=[]
for sh in roomsheet:
    r=sh["room"];h=float(sh["source_height_each_in_UNVERIFIED"])
    rate=float(sh["historic_wall_rate_per_GROSS_SF_only_USD"])
    for delta_w1 in (-1,0,1):
        for delta_side in (-.5,0,.5):
            delta_net=(delta_w1+2*delta_side)*h/144*2
            ratecases.append(dict(room=r,source_W1_shift_in_PER_PHYSICAL_COPY=f4(delta_w1),
               source_W2_and_W3_each_shift_in_PER_PHYSICAL_COPY=f4(delta_side),
               source_both_copies_signed_only_HYPOTHETICAL="TRUE",
               theoretical_two_copy_WALL_NET_DELTA_SF=f4(delta_net),
               historical_rate_USD_per_already_wasted_GROSS_SF=f4(rate),
               theoretical_material_ONLY_reference_DELTA_USD_NO_NEW_WASTE=f"{delta_net*rate:.2f}",
               actual_field_wall_offsets_signed="FALSE",actual_supplier_credit_or_installed_changeorder="",
               original_15pct_NOT_applied_again="TRUE",
               other_apertures_niche_tile_TRIM_separate="NOT_INCLUDED_IN_THIS_EXAMPLE",
               actual_current_labor_backer_membrane_quote="UNKNOWN",
               credit_claim_payable="FALSE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(ratecases)==27
csvout("R33_27_THREE_TUB_TWO_COPY_SOURCE_WALL_SPAN_HISTORIC_RATE_CHANGEORDER_SENSITIVITIES.csv",ratecases)

# Two-copy source wall carton tests are *within same-room SKU* only. The only
# potentially shared niche in the focus is *historically named* Tones Sandstone
# PH2 and TX2 -- requires exact SKU/color/finish/lot if used across rooms.
cartons=[]
for sh in roomsheet:
    r=sh["room"]
    gross=float(sh["historic_original_wall_GROSS_SF_per_copy_15pct_already_included"])
    for fictional_case in (8,12,16):
        cases_individual=2*math.ceil(gross/fictional_case)
        cases_pooled=math.ceil(gross*2/fictional_case)
        cartons.append(dict(material_group=r+"_SOURCE_WALL_NOT_CROSS_ROOM_POOLABLE",
           historical_gross_SF_total_two_physical_copies=f4(gross*2),
           hypothetical_case_usable_SF_NOT_FACTORY=f4(fictional_case),
           independent_unit_ceiled_cases=cases_individual,
           pooled_same_room_exact_SKU_lot_if_verified_cases=cases_pooled,
           theoretical_ceiling_difference_cases=cases_individual-cases_pooled,
           real_product_carton_usable_SF="",real_current_factory_same_shade_caliber_lot="UNKNOWN",
           historical_waste_already_in_original_gross="TRUE",
           real_carton_saving_credit="FALSE",purchase_authorized="FALSE"))
# Sandstone two names only; original 8-copy prior R29 amount not charged.
sand=[(r,float(by_material[r,"accent"]["source_gross_sf_one_copy_waste_15pct_once"])) for r in ("PH-BATH2","TX-BATH2")]
assert abs(sum(x*2 for _,x in sand)-24.6)<1e-9
for fictional_case in (5,8,12):
    independent=sum(2*math.ceil(v/fictional_case) for _,v in sand)
    pooled=math.ceil(24.6/fictional_case)
    cartons.append(dict(material_group="SANDSTONE_PH2_TX2_HISTORICALLY_NAMED_NOT_VERIFIED_SHARED_FACTORY_LOT",
       historical_gross_SF_total_two_physical_copies="24.6000",
       hypothetical_case_usable_SF_NOT_FACTORY=f4(fictional_case),
       independent_unit_ceiled_cases=independent,
       pooled_same_room_exact_SKU_lot_if_verified_cases=pooled,
       theoretical_ceiling_difference_cases=independent-pooled,
       real_product_carton_usable_SF="",real_current_factory_same_shade_caliber_lot="UNKNOWN",
       historical_waste_already_in_original_gross="TRUE",real_carton_saving_credit="FALSE",
       purchase_authorized="FALSE"))
assert len(cartons)==12
csvout("R33_12_THEORETICAL_THREE_TUB_LOT_CARTON_AND_SANDSTONE_SAME_SKU_CONDITIONAL_ROUNDING.csv",cartons)

# Every original wet lab role is independently contractually defined; three tub
# focus floor roles are LEVEL ONLY and have NO sloped shower PAN.
wet=[]
source_fin={
  "PH-PRIMARY":"Bone Soft vs AntiSlip LEVEL / separate LINEAR shower PAN",
  "PH-BATH2":"Cortar Grey Soft LEVEL; separately Sapphire/Sandstone wet WALL/NICHE",
  "PH-BATH3":"Bone Soft LEVEL; CONDITIONAL POINT pan if owner chooses WALKIN",
  "PH-BATH4":"Bone Soft vs AntiSlip LEVEL; independent 4-plane POINT pan",
  "TX-PRIMARY":"Clay Soft vs AntiSlip LEVEL / separate LINEAR shower PAN",
  "TX-BATH2":"Clay Soft LEVEL; Copper/Sandstone wet WALL/NICHE",
  "TX-BATH3":"Grey Soft LEVEL; CONDITIONAL POINT pan if owner chooses WALKIN",
  "TX-BATH4":"Bone Soft LEVEL; Charcoal flat WALL/Caviar NICHE individual wet permission hold",
}
for row in source13:
    r=row["room"];p=row["surface_role"]
    wet.append(dict(room=r,surface_role=p,original_quoted_floor_row_id=row["source_original_floor_row_id"],
        source_finish_or_branch=source_fin[r],
        original_SOURCE_full_GROSS_SF_one_copy_15pct_once=row["historic_floor_quoted_GROSS_SF_one_copy_may_mingle_LEVEL_and_PAN"],
        original_exact_selected_color_size_finish_SKU_and_caliber="UNKNOWN_REQUIRES_SIGNED_SOURCE_ITEM",
        original_raw_measured_wet_DCOF_numeric="",
        original_factory_report_ID_test_date_batch_method="",
        maker_wet_application_signed_for_LEVEL_or_specific_SLOPED_PAN="FALSE",
        pan_tile_may_use_bath_LEVEL_lab="FALSE",
        manufacturer_general_threshold_not_raw_numeric="TRUE",
        local_physical_1529_tile_slope_report="",
        tub_PAN_N_A=tf(r in focus),
        pending_owner_WALKIN_activates_conditional_POINT=tf("CONDITIONAL" in p),
        source_raw_report_exists="FALSE",architect_signoff="FALSE",installer_signoff="FALSE",
        owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(wet)==13 and Counter(x["surface_role"] for x in wet)==Counter({
    "LEVEL":8,"LINEAR_SLOPED_PAN":2,"POINT_FOUR_PLANE_SLOPED_PAN":1,
    "CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN":2})
csvout("R33_13_ORIGINAL_ITEM_LEVEL_LINEAR_POINT_RAW_NUMERIC_WET_TEST_CONTRACT_APPLICATION.csv",wet)

# Separate wet wall and niche manufacturer listing classification for each
# actual three-tub selected material. Do not transfer PASS by family.
application=[]
for r in focus:
    for surf in ("WALL","NICHE","LEVEL"):
        tile={"WALL":materials[r][0],"NICHE":materials[r][1],"LEVEL":materials[r][2]}[surf]
        if surf=="LEVEL":
            state="ORIGINAL_EXACT_SKU_RAW_NUMERIC_WET_DCOF_MISSING"
            evidence="UNKNOWN_ORIGINAL_INDIVIDUAL_NUMERIC_LAB"
        elif r=="TX-BATH4" and surf=="NICHE":
            state="INDIVIDUAL_CAVIAR_WET_NICHE_AUTHORIZATION_MISSING_HOLD"
            evidence="COLLECTION_INSTALL_DOES_NOT_AUTHORIZE_EXACT_CAVIAR_INDIVIDUAL_NICHE"
        else:
            state="INDIVIDUAL_MAKER_WET_AREAS_REPORTED_PASS_BUT_REQUIRE_EXACT_CURRENT_COLOR_FINISH_MOUNT"
            evidence="EXISTING_R26_R29_MAKER_PASS_CORROBORATION_REQUIRED_WITH_CURRENT_SHEET"
        application.append(dict(room=r,selected_original_surface=surf,original_material_description=tile,
          factual_individual_factory_application_evidence_class=evidence,
          state_and_fatal_gate=state,
          true_SKU_size_color_finish_orderable_2026="",
          manufacturer_permitted_waterproof_membrane_and_setting="",
          original_raw_numeric_wet_DCOF_if_LEVEL="MISSING" if surf=="LEVEL" else "N_A_WALL_NICHE_ITEM_PERMISSION_INSTEAD",
          selected_tub_no_tiled_PAN="TRUE",
          factory_site_suitable_and_caliber_verified="FALSE",
          owner_substitution_to_Soho_Ivory_or_Black="FALSE",
          installer_1to1_accepted="FALSE",owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(application)==9
csvout("R33_9_THREE_TUB_DISTINCT_WALL_NICHE_LEVEL_WET_APPLICATION_HARD_GATES.csv",application)

# Contractor preflight inspection sequence for 6 original tub instances,
# not a claim that physical work or samples occurred.
phases=[
("01_SOURCE_RFI","Owner/architect reconcile exact controls (TX2 Chrome missing trim/rough/spout; PH2/TX4 Matte White conflict), v3.2/dated Smartsheet and 3 endpoints; keep originals."),
("02_SURVEY_ROUGH","Signed actual native 1529 room identity and tub W1-W3/alignment, outlet and valve centerline, existing pipe/door/window/niche, fixture and access clearance."),
("03_FACTORY_SHOP","Factory full 3-outlet flow/anti-scald/backflow and compatible rough/trim/spout/diverter/certified waste/overflow; no cross-finish transfers."),
("04_TUB_SUPPORT_AND_FLANGE","Duravit 700332 support frame, approved anchor/continuous surround flange, actual 59in nominal fit, drain end/overflow and future service access."),
("05_WATERPROOF_PENETRATIONS","Exact backer/membrane/corner/upturn, tub rim change-of-plane joint, seal around mixer/escutcheons/spout/head and wet NICHE; witnessed test method."),
("06_TILE_FIELD_MOCKUP","1:1 calibrated source wall W1/W3 focal cuts, true backer/mortar/membrane/tile plane, joints, factory wet WALL/NICHE separate, original numeric wet LEVEL report; tub PAN N_A."),
("07_SUPPLIER_AND_BID","Current exact SKU/finish/lot/case/lead/freight + scope-rated GC bid, historical material-only credit separated from added valve/spout/waterproof/trim labor; no fabricated quote."),
("08_RELEASE_GATE","Original eight-trade signatures and owner program; genuine authorized independent four-critic board preflight/Reviewer if applicable; no material reservation before release."),
]
inspect=[]
for x in source6:
    r=x["room"];inst=x["source_physical_room"]
    for idx,(phase,req) in enumerate(phases,1):
        inspect.append(dict(room=r,physical_source_room=inst,sequence=idx,hold_point=phase,
           specific_signed_acceptance_evidence=req,program=program[r],
           selected_Duravit_59in_tub="700332000000090",
           certified_true_1529_field_reference="",factory_source_revision="",
           actual_condition_record="",trade_responsible=("OWNER_ARCHITECT" if idx==1 else
                  "ARCHITECT_PLUMBER" if idx==2 else "PLUMBER_MANUFACTURER" if idx==3 else
                  "PLUMBER_GC" if idx==4 else "WATERPROOFER_TILE" if idx==5 else
                  "TILE_INSTALLER_ARCHITECT" if idx==6 else "SUPPLIER_GC" if idx==7 else "OWNER_PURCHASER"),
           acceptance_signatures="",actual_field_work_complete="FALSE",
           selected_PAN="N_A_TUB",owner_release="FALSE",purchase_authorized="FALSE"))
assert len(inspect)==48
csvout("R33_48_SIX_PHYSICAL_DURAVIT_TUB_EIGHT_CONSTRUCTION_HOLD_POINTS.csv",inspect)

# All 26 original physical instances get an ACTIONABLE existing program
# release requirement; do not rewrite or resnapshot original source26.
other={
 "PH-PRIMARY":"Brizo BNX 48in LINEAR BT0734816-BNX + BR73480 separate; no Primary niche; PH WC floor included once",
 "PH-BATH3":"Owner TUB vs WALKIN UNSELECTED; Chrome Hansgrohe and Delta DT062412 POINT only conditional WALKIN; PH basin unselected",
 "PH-BATH4":"Owner WALKIN Black Onyx BT062415-BNX POINT four-plane PAN distinct LEVEL; original Ribbed WALL wet/Caviar NICHE holds",
 "PH-POWDER":"Dry wood floor, Brizo FLW T65722LF-GL WALL faucet with separate R65700; no wet tile lab",
 "PH-WC":"Cortar Bone AntiSlip LEVEL inherited PH PRIMARY; no standalone tile purchase or PAN",
 "TX-PRIMARY":"Brizo BNX 48in LINEAR BT0734816-BNX + BR73480 separate; no Primary niche; TX WC floor included once",
 "TX-BATH3":"TUB vs WALKIN UNSELECTED; Brizo BNX 4in POINT only conditional WALKIN; Emerald wall maker renewal",
 "TX-POWDER":"AXOR One 48140991 and Hansgrohe Metropol 32526141 are TWO WALL trim programs, not trim + rough; owner selection unresolved",
 "TX-POWDER2":"Hansgrohe Tecturis E 73072341 DECK mounted; basin UNSELECTED and Indigo dry-wall direction preserved",
 "TX-WC":"Clay AntiSlip LEVEL inherited TX Primary; TX203A source UNPLACED, no separate tile purchase/PAN",
}
assert set(other)==set(rid)-set(focus)
instances=[]
for x in source26:
    r=x["room"];number=x["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"]
    requirement=(program[r]+"; 3-ENDPOINT FACTORY CONTROL, TUB FLANGE, LEVEL ONLY" if r in focus else other[r])
    instances.append(dict(room=r,physical_copy_index=x["physical_copy_index"],
      original_source_revit_room_number_UNVERIFIED=number,
      original_1529_native_id_and_revision="UNKNOWN_1527_MODEL_UNRELATED",
      owner_selected_program_and_new_shop_top_fix=requirement,
      project_1529_document_verified="FALSE",
      measured_room_and_tub_or_shower_footprint_NET_SF="",
      measured_3W_wall_apertures_NICHE_BACK_TWO_SIDES_TOP_SILL_SF="",
      physically_measured_valve_spout_rough_depth_and_approved_outlet_map="",
      verified_all_tub_flange_or_selected_shower_POINT_LINEAR_drain="",
      original_exact_SKU_finish_WALL_NICHE_wet_application_letters="",
      original_raw_measured_LEVEL_DCOF_and_distinct_PAN_when_applicable="",
      exact_same_FACTORY_SHADE_caliber_lot_case_supplier_allocation="",
      dated_factory_chicago_stock_and_freight_bid="",
      installed_GC_labor_waterproof_trim_and_changeorder_scope="",
      owner_selection_and_upgrades_signed="FALSE",architect_signed="FALSE",
      plumber_signed="FALSE",waterproofing_signed="FALSE",tile_installer_signed="FALSE",
      supplier_signed="FALSE",GC_signed="FALSE",purchaser_signed="FALSE",purchase_authorized="FALSE"))
assert len(instances)==26
csvout("R33_26_EXISTING_PHYSICAL_ROOM_INSTANCE_ACTIONABLE_OWNER_FACTORY_WET_AND_QUOTE_TRADES.csv",instances)

# Same 50 original W physical witnesses now carry a new program and particular
# wet/fixture/quantification instruction while actual field values stay blank.
allwalls=[]
for x in source50:
    r=x["room"];wallid=x["wall_reference"]
    if r in focus:
        seq=("W1 true 59in tub support/flange/mixing and spout rough plus original selected three-outlet control" if wallid=="W1" else
             "W2/W3 true wet return and side glass, original one NICHE opening, separate sides/top/sill and sealed penetration")
    elif r=="PH-BATH4":seq="Actual WALKIN BNX POINT selected; four-plane PAN isolated from LEVEL; individual Ribbed wet-wall authorization absent"
    elif r.endswith("PRIMARY"):seq="Selected 48in BNX LINEAR with separate BR73480, no Primary NICHE; parent WC floor once"
    elif r in ("PH-BATH3","TX-BATH3"):seq="Owner TUB/WALKIN UNSELECTED, POINT drain conditional to WALKIN only"
    elif r.endswith("WC"):seq="Inherited Primary LEVEL WC area, NO distinct wet niche or PAN or standalone order"
    else:seq="Powder wood floor and/or dry feature, keep original wall faucet mounting and NO pan"
    allwalls.append(dict(room=r,source_copy=x["physical_copy"],wall=wallid,
       original_source_wall_width_in_UNVERIFIED=x["prior_source_wall_width_in_UNVERIFIED"],
       original_source_wall_height_in_UNVERIFIED=x["prior_source_tiled_height_in_UNVERIFIED"],
       R33_exact_construction_trace_to_inspect=seq,
       original_1529_native_revision="",measured_true_1529_WIDTH_HEIGHT_and_wall_origin="",
       measured_other_doors_windows_opening_field_deduction_SF="",
       one_original_NICHE_field_aperture_NEGATIVE_once_SF="",
       separate_tiled_NICHE_BACK_SIDES_TOP_SILL_NET_SF="",
       actual_trim_exposed_edge_LF="",actual_change_plane_movement_joint_LF="",
       signed_original_factory_waterproof_membrane_backer_finish_plane="",
       valve_head_spout_or_drain_pipe_coordination="",
       actual_calibrated_cut_module_and_under3in_focal_gate="",
       true_signed_wall_NET_SF="",
       source_quoted_material15pct_once_not_doubled="TRUE",
       architect_signed="FALSE",tile_watertight_mockup_signed="FALSE",
       owner_approved="FALSE",purchase_authorized="FALSE"))
assert len(allwalls)==50
csvout("R33_50_ORIGINAL_TWO_COPY_W_ELEVATION_FIELD_SURVEY_PROGRAM_CUT_WATERPROOF_TRADE_GATE.csv",allwalls)

# Supplier source lines are immutable; this is NEW quote/scope normalization
# with correct historical rate classification and source rows for every room.
normalize=[]
for x in old:
    r=x["room"];surf=x["source_surface"]
    gross=Decimal(x["source_gross_sf_one_copy_waste_15pct_once"] or "0")
    cost=Decimal(x["historic_usd_two_copies"] or "0")
    noorder=x["historic_niche_excluded_no_scope"]=="TRUE"
    normalize.append(dict(room=r,original_source_row_id=x["source_row_id"],surface=surf,
      historic_GROSS_SF_per_physical_room_one_waste15pct_included=str(gross),
      original_GROSS_SF_two_room_copies=str(gross*2),
      historic_two_copy_material_ONLY_USD=str(cost),
      historic_2026_09_quote_rate_USD_per_GROSS_SF=f"{cost/(gross*2):.4f}" if gross else "N_A_NO_ORDER",
      original_unpriced_Primary_niche_excluded_NO_ORDER=tf(noorder),
      original_source_row_and_gross_unmodified="TRUE",
      R33_TUB_SELECTED_OR_CONDITIONAL_NEW_PARTS_CLASS=("TUB_GC_ACTUAL_QUOTE_SEPARATE_FROM_TILE_HISTORIC" if r in focus else "NO_CHANGE_TO_ORIGINAL_PLUMBING"),
      actual_maker_exact_SKU_color_size_finish="",
      individual_wet_WALL_NICHE_approval_or_RAW_wet_LEVEL_PAN_lab_ID="",
      signed_1529_actual_WALL_NET_plus_apertures_returns_or_separate_LEVEL_PAN_NET="",
      new_material_cut_waste_factor_SIGNED_AFTER_REAL_NET_ONLY="",
      actual_case_USABLE_SF_and_lot_match_verified="",
      rounded_cases_AFTER_actual_factory_usable_SF_formula="CEIL(SIGNED_REQUIRED_GROSS_SF/EXACT_FACTORY_USABLE_SF_CASE)",
      current_Chicago_supplier_material_price_USD="",
      maker_MSRP_not_project_quote_class="UNKNOWN",
      public_retail_indication_class="UNKNOWN",
      allowance_separate_from_original="UNKNOWN",
      GC_installed_watertight_tile_labor_grout_trim_penetration_bid="",
      original_fixture_removed_credit_and_new_exact_3outlet_rough_CHANGEORDER="",
      actual_signed_ETA_freight_tax_breakage_inspection="",
      same_SKU_COLOR_FINISH_LOT_pool_authorized="FALSE",
      original_historic_15pct_already_once="TRUE",
      owner_signed="FALSE",supplier_signed="FALSE",GC_changeorder_approved="FALSE",
      purchase_authorized="FALSE"))
assert len(normalize)==27 and sum(Decimal(x["historic_two_copy_material_ONLY_USD"]) for x in normalize)==Decimal("23572.44")
assert sum(x["original_unpriced_Primary_niche_excluded_NO_ORDER"]=="TRUE" for x in normalize)==2
csvout("R33_27_ORIGINAL_DATED_MATERIAL_GROSS_PRICE_TO_REAL_SKU_LOT_3OUTLET_GC_QUOTE_SCOPE.csv",normalize)

prior_release=readcsv(ROOT/"deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/R31_13_ROOM_SOURCE_WALL_NICHE_LEVEL_PAN_PROGRAM_AND_RELEASE_MATRIX.csv")
assert len(prior_release)==13 and {x["room"] for x in prior_release}==set(rid)
releases=[]
TRADES=["OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER"]
trades=[]
for x in prior_release:
    r=x["room"];rm=rid[r]
    cost=sum(Decimal(row["historic_usd_two_copies"] or 0) for row in old if row["room"]==r)
    releases.append(dict(room=r,original_board_round="017",original_ROOM_status=rm["status"],
        original_champion=rm.get("champion_id") or "null",original_score=str(rm["champion_score"]) if rm.get("champion_score") is not None else "null",
        original_historic_TWOCOPY_material_only_USD=str(cost),
        independent_physical_unit_instances=2,
        signed_current_OWNER_program_NOT_TO_REPLACE=x["actual_source_program_and_top_FIX"],
        R33_focus_new_factory_control_branch=(program[r] if r in focus else "NOT_FOCUS_ORIGINAL_SOURCE_PRESERVED"),
        original_item_wet_LEVEL_lab=x["room_wet_LEVEL_raw_numeric_lab"],
        independent_shower_PAN_wet_lab_or_N_A=x["room_SLOPED_PAN_raw_numeric_lab"],
        individual_wet_WALL_permission_required="TRUE_IF_WET",
        independent_wet_NICHE_permission_required="TRUE_IF_NICHE",
        correct_1529_measured_W1W3_fixture_spout_drains_or_rough="",original_exact_raw_lab_report="",
        original_2026_material_lot_usable_case_Chicago_offer="",actual_freight_ETA_tax="",
        actual_installed_GC_bid_and_original_credit="",owner_actual_signed_program="FALSE",
        architect_1529_shop_signed="FALSE",plumber_full_3outlet_and_drain_rough_signed="FALSE",
        waterproofing_tub_flange_or_shower_pan_signed="FALSE",
        tile_installer_original_lab_1to1_signed="FALSE",
        supplier_same_lot_current_bid_signed="FALSE",GC_installed_changeorder_signed="FALSE",
        purchaser_material_reservation="FALSE",purchase_authorized="FALSE",
        weighted_BOARD_scores="NULL",independent_nonpro_acceptance="FALSE"))
    for step,trade in enumerate(TRADES,1):
        proof=(
         "Owner true program/finish and budget/alternate control signoff" if trade=="OWNER" else
         "True native 1529 two-copy W1-W3, wall openings/niche, tub support/valve datum, tile module/trim signed section" if trade=="ARCHITECT" else
         "Exact selected rough/head/hand/tub spout hydraulic THREE outlet route, factory cartridge and waste; PH2/TX4 pressure-balance-only conflict, TX2 missing schedule identities" if trade=="PLUMBER" and r in focus else
         "Factory each selected POINT/LINEAR/rough or owner Tub-conditional branch and tested plumbing program" if trade=="PLUMBER" else
         "Actual manufacturer-compatible membrane, tub tile flange/2 corners/spout collars and movement joint, drain if shower" if trade=="WATERPROOFING" else
         "Individual wet WALL/NICHE factory listing and original EXACT numerical wet LEVEL/PAN test, 3in focal cuts and full-size water/slope mockup" if trade=="TILE_INSTALLER" else
         "Exact maker SKU/finish/caliber/lot/case usable coverage, dated Chicago allocation and separate factory lead/freight, no cosmetic-only pooling" if trade=="SUPPLIER" else
         "Old quote material $23572.44 already waste15pct once, wall opening counted once and returns separate, full rough/backer/trim/three outlet labor bid and credit" if trade=="GC_ESTIMATOR" else
         "No PO/reservation until all seven prior signatures and independent original four-seat governance when legitimate" )
        trades.append(dict(room=r,trade_order=step,trade=trade,actual_unique_R33_acceptance_document=proof,
          physical_two_unit_witness_count=2,
          original_BOARD_specialists_4_3_0_and_margin_0_25_and_hard_gates="NOT_COMPLETED",
          exact_historical_27_row_and_level_pan_13roles_cross_reference="REQUIRES_SIGNED_CORRESPONDENCE",
          true_1529_source_id="",factory_test_lot_approval_certificate="",
          trade_signature="",source_evidence_date="",owner_approved="FALSE",
          actual_physical_inspection_complete="FALSE",GC_release="FALSE",
          purchase_authorized="FALSE"))
assert len(releases)==13 and len(trades)==104
csvout("R33_13_ROOM_ALL_PROGRAMS_WET_LEVEL_PAN_OWNER_ARCHITECT_GC_PURCHASE_RELEASE.csv",releases)
csvout("R33_104_EIGHT_TRADE_SEQUENTIAL_TWO_COPY_ORIGINAL_13ROOM_HOLDPOINTS.csv",trades)

# Six actual tub copies get distinct, source-faithful three camera and physical
# sample briefs. No image rendered or manufacturer samples procured.
views=[]
for x in source6:
    r=x["room"];num=x["source_physical_room"]
    for camera in ("W1_FULL_FRONT_THREE_OUTLET_PLUMBING_ELEVATION",
                   "W3_TUB_FLANGE_NICHE_RETURN_WATERPROOF_CUTAWAY",
                   "LOW_OBLIQUE_FINISH_PLANE_PROFILE_RIM_AND_ESCUTCHEON"):
        views.append(dict(room=r,source_room_number=num,
            requested_future_camera=camera,
            true_source_fixture_truth=program[r],
            wall_selected_tone=materials[r][0],wet_niche_source_only=materials[r][1],
            show_no_tiled_shower_PAN="TRUE",
            preserve_tub_700332_59in_source_and_selected_MW_or_CHROME="TRUE",
            do_not_draw_unselected_TX2_mixer_spout_as_selected="TRUE",
            do_not_assume_72411701_15758701_compatibility="TRUE",
            actual_1529_wall_millwork_door_window_and_light="UNVERIFIED",
            mandatory_1to1_mockup_witness="Factory calibrated backer, waterproof membrane, rim slope seal, 3 valve/penetration alignment, 3in cuts, manufacturer FULL 3outlet routing, maintenance accessibility",
            physical_sample_and_live_render_NOT_PRODUCED="TRUE",
            future_verified_lens_pose_and_elevations="",maker_sample_lot_caliber="",
            actual_image_created="FALSE",actual_mockup_built="FALSE",owner_signature="FALSE",
            architect_plumber_tile_waterproof_signature="FALSE",purchase_authorized="FALSE"))
assert len(views)==18
csvout("R33_18_PHYSICAL_TUB_SOURCE_CORRECT_THREE_VIEW_AND_MOCKUP_ACCEPTANCE_BRIEFS.csv",views)

mdout("START_HERE_R33_INTEGRATED_OWNER_ARCHITECT_GC.md",f"""
# R33 integrated three-Duravit-tub hydraulic, wet-wall, quantity and purchasing implementation

**FULL 1529 13-room objective OPEN. Formal Board R017 unchanged; no owner, architect, plumber, waterproofing, tile installer, supplier, GC, purchaser or independent Reviewer approval. No samples ordered/rendered, no actual 1529 measurements, no purchase.**

Focus **PH-BATH2 (305A/305B), TX-BATH2 (205A/205B), TX-BATH4 (007A/007B)**. All six room numbers are source labels, NOT certified 1529 model identities.

## Actual advance beyond immutable R30, R31, R32

1. **PH2 and TX4 real selected conflict:** both owner-selected Duravit 700332000000090 59x29.5in tub, Matte White Hansgrohe 15758701 thermostat two-outlet/volume-diverter, separate iBox 01850181 rough, and 72411701 pressure-balance-only pull-up diverter tub spout, plus overhead and hand shower. Maker {URL["spout"]} explicitly restricts the spout. Historic factory {URL["price2021"]} documents 15758701 two-outlet thermostat and conditional 15739701 pressure-balance with bypass for ONE shower outlet. Three physical endpoints are not automatically serviceable by either; full maker 3-endpoint schematic and true 1529 rough coordination needed.
2. **TX2 distinct source omission:** remains owner-selected Hansgrohe CHROME 04925000 overhead, 04790000 handshower and 27458003 check-valve wall outlet. Current eleven-fixture source list contains NO identifiable bathing mixer/rough or tub-fill spout. This is not proof installed physical piping is absent. v3.2 fixture deck, dated Smartsheet record and signed submittal not locally available; this is a precise RFI, not authorization to invent components.
3. **Construction arithmetic:** three source W1/W2/W3 dimensions reconciled to historical gross and original 15% already included; new 36 physical tub-clearance sensitivities, 36 partial rough/finish stacks, 36 long-axis tile focal cut layouts, six-unit 18 wall physical survey/penetration schedules, three room rim/edge proxies and 27 historic-rate material sensitivities. Single hypothetical niche example per copy demonstrates one field aperture versus five tiled return faces; not actual niche count or orders. All are drawing-provisional scenarios, no certified 1529 geometry.
4. **Manufacturer and GC deliverables:** 12 factory identity/evidence rows, nine differentiated GOOD/BETTER/BEST systems, 54 per-physical-branch hydraulic outlet port RFI rows, 48 physical-copy sequential construction holds, 12 fictional carton rounding cases and 18 source-faithful future camera/1:1 briefs (none produced). Nine distinct WALL/NICHE/LEVEL applications and 13 original raw LEVEL/PAN specimens. All original 26 physical instances and 50 W wall target records transformed to trade-controlled release instructions, without modifying source records. New 27 original cost/lot/case bridge, 13 room release and 104 eight-trade gates.

## Three wall quote-to-drawing provisional face reconciliations

"""+"\n".join(
 f"* **{x['room']}** source W1/W2/W3 {x['source_W1_in_UNVERIFIED']} + {x['source_W2_in_UNVERIFIED']} + {x['source_W3_in_UNVERIFIED']}in x {x['source_height_each_in_UNVERIFIED']}in; source full 3-wall field **{x['unverified_full_3wall_FIELD_NET_SF_per_copy_before_openings']} SF**/copy before openings; x original 1.15 method **{x['theoretical_source_full_3wall_NET_times_original_15pct_once_SF_per_copy']} SF** vs original historical quoted **{x['historic_original_wall_GROSS_SF_per_copy_15pct_already_included']} SF**/copy. Historical material-only quote rate USD {x['historic_wall_rate_per_GROSS_SF_only_USD']}/gross SF, not a current bid."
 for x in roomsheet
)+f"""

Small differences support the historical calculation's derivation, NOT actual measured net, a payable shortage or savings; manufacturer caliber, actual wall openings/niches/penetrations and real model still missing. Source already includes waste 15% ONCE; new 27 cost sensitivities multiply hypothetical **NET movement** by historical rate WITHOUT adding another waste factor. Any real new waste allowance must be separately signed after actual NET and exact case factors.

Original **27** material rows incl two no-order unpriced Primary niche references; four-unit historical tile material-only **$23,572.44**, original 15% once. Sandstone **51.64 SF/$358.92**, Grey Soft **165.4 SF/$1,116.46**, Caviar **34.52 SF/$1,163.32** already included, not new charges. Previous **25** original W studies, **65** original trade actions untouched. Current Chicago exact SKU/case/lot/lead/freight/installed GC bid UNKNOWN, owner cap unspecified.

**Market:** PH target approx **$2.8M**, TX **$2.7M**, comps $2.4M-$3.2M Old Town priority. Four OT01-OT04 listings at 405 W Armitage are ONE building; 14 listings = nine independent buildings. Lincoln Park and Gold Coast adjacent/secondary. Buyer appeal anchored in functional water delivery, safe and cleanable grout/movement joints, durable wet surround and accessible servicing; no fabricated comparable tile identity or selling premium.

Formal four-seat board governance blocked: worker9 DESIGN R014 two absent reports, Reviewer15 finished/nonrevivable, R017 frozen neutral candidate source no independent clearance. These are owner/GC technical OPTIONS, NOT new blind candidates or board scores; all releases FALSE and independent review UNSENT.
""")

mdout("R33_THREE_TUB_WATERPROOF_ROUGH_AND_MAKER_DECISION_SHOP_BOOK.md",f"""
# R33 six-physical-bath detailed construction shop and real hydraulic decision tree

**Owner fixtures remain unchanged.** PH-BATH2 and TX-BATH4 contain source Matte White Hansgrohe 15758701 two-outlet thermostatic control, 01850181 rough and diverter 72411701; Hansgrohe officially says the **72411701 spout is pressure-balance only** ({URL["spout"]}), so source assembly is a HARD INSTALLATION HOLD. Each includes a tub spout, overhead and hand shower, THREE physical endpoints. Never assume that a 2-outlet trim independently operates all three. The factory must certify exact TUB/HEAD/HAND outlet ports, mixer cartridge and diverter, flow/pressure/backflow, anti-scald temperature, controls, shutoff/service and finish mounting. Current universal iBox rough alone does not authorize this operating system.

**GOOD:** preserve original Matte White selected controls and diverter spout as source only, no installation until maker signs full three-endpoint routing. **BETTER:** conditional unselected Matte White 72410701 NON-diverter tub spout ({URL["nondiv"]}) with original thermostatic control only if maker certifies a separate overhead/hand selector and rough/operation; nominal public manufacturer list 321 vs original 382 USD per piece creates a 61 USD per-piece or 244 USD/four-copy maker MSRP comparison, NOT a vendor credit, bid or savings. **BEST:** unselected historic Matte White 15739701 pressure-balance bypass control with selected 72411701 spout, identified only in 2021 maker evidence ({URL["price2021"]}); factory live availability uncertain, one shower outlet still requires HEAD/HAND selection, and changing thermostatic operation is owner-only. Neither option is factory-approved installation or purchase.

**TX-BATH2 is independently different.** Selected Chrome Hansgrohe overhead 04925000 ({URL["chromehead"]}), handshower set 04790000 ({URL["chromehand"]}), and 27458003 FixFit with check valves ({URL["chromeout"]}), plus Duravit tub. Its eleven-source-fixture schedule does NOT identify original bathing mixing trim, mixer rough, or tub-fill spout. This proves a source BOM identity gap, NOT missing installed piping; do not transfer Matte White controls or invent Chrome parts. GOOD: obtain authentic v3.2/dated Smartsheet and signed source; BETTER: factory-approved complete Chrome TUB/HEAD/HAND schematic after original IDs recovered; BEST: conditional serviceable alternative only by owner/architect/plumber signed substitution and GC bid.

## Construction sequence and datum

1. Site witness: true 1529 model/address and each source room number; actual rough W1/W2/W3 width, squareness, door/window and niche and drain locations. Reachable Revit **1527** is NOT certified 1529. Establish wall datum at framing, backer or finished face explicitly.
2. Factory hydraulic shop: lock original or owner-consented mixer, rough, cartridge, spout, HEAD/HAND selector, hot/cold/backflow/anti-scald and service; draw and approve all three actual outlets and penetration/rough centers. TX2 source blank controls remain NULL.
3. Tub and framing: actual selected Duravit 700332000000090 nominal **59 x29.5in tub with support frame** ({URL["duravit"]}); manufacturer optional **790112** 16in flange accessory ({URL["flange"]}) is NOT a certified continuous 59in back + two side tub waterproof system. Require exact flange segment/connectors/three-wall corner approval, support/anchor and waste/overflow service.
4. Finish and moisture: approved wet backer, compatible actual membrane continuous over flange/around corners, shower supply/spout/valve penetrations with manufacturer collars; a compressible/compatible movement joint at tub rim and changes of plane, no rigid mortar bridge. Actual finish plane = measured backer + actual membrane + compressed mortar + calibrated tile BODY + actual trim/gasket compression. **36 partial** R33 stack cases deliberately omit membrane/gasket and therefore CANNOT approve a rough/spout nipple length.
5. Field tile approval: physical full-scale wall/focal 3in cut test, actual joint/finish and wet WALL permission separate from individual NICHE, 1:1 tub rim/water test and full 3-endpoint controls operation; no sourced sample/mockup performed yet.

R33 **36 nominal long-axis W1/W3 examples** reveal TX2 source W1 **62.484in** with three centered full 20in tiles and 1/8in joints has **0.992in** focal side pieces FAIL. Two full center 20in yields **11.0545in** side pieces, conditional PASS. PH2 W1 **59.496in**, same two center gives **9.5605in** sides. TX4 W3 source **30.48in** one central 24in, 1/8in joints has **3.115in** end pieces; at 1/4in joint **2.990in FAIL**. Alternative single 48in horizontal cut has hypothetical 17.52in offcut before saw kerf, not an established reusable tile or material saving. Real factory caliber, grout allowance, focal openings, selected pattern and 1529 measurements must override all scenarios.

One synthetic 16 x12 x4in niche per physical room is a quantity-method illustration, **not an asserted niche count**: WALL field aperture **1.3333SF deducted ONCE**, niche BACK1.3333, TWO SIDES0.6667, TOP0.4444, SILL0.4444, niche surfaces2.8889SF before new cut waste. Actual physical location and piping clearance, edge LF, water-shedding sill, movement seal and company-approved wall/niche products require separate signed takeoff. Historical waste15pct already included in original gross and not re-applied.

Original tub-only **LEVEL** floor exact individual raw measured wet DCOF still missing for all three, **PAN N/A**. Existing project original 13 wet test roles include independent applicable Primary LINEAR, PH4 actual POINT and conditional Bath3 POINT PANs; their tile test findings cannot transfer to another format/finish/slope or sibling. PH2 Sapphire wet WALL/Sandstone NICHE individual reported PASS, TX2 Copper/Sandstone reported PASS, TX4 flat Charcoal wet WALL reported PASS but Caviar individual wet NICHE remains HOLD. Any conditional Soho alternative remains owner-unselected. Factory selected item wet application, matching waterproof substrate and sample mockup required.

All original 27 material lines and historical 15percent once remain intact. Cost change order must itemize original deleted owner-selected parts as verified **credits**, new controls/rough/diverter, penetration/valve/flange/waterproof/trim/tile labor and full 1:1 acceptance; no invented installed Chicago bid, stock, freight, ETA, case coverage or owner approval. **Six baths x eight holdpoints =48 signed future contractor inspections**, not physical work completed. All release flags FALSE.
""")

mdout("R33_13ROOM_GC_OLDTOWN_SOURCE_AND_SEQUENTIAL_RELEASE_BOOK.md",f"""
# R33 full 13-room historical source, buyer value, supplier and trade controls

13 room IDs, two physical room copies each, original statuses, selections and champions preserved. New 26 per-instance and 50 per-wall detailed shop matrices are additive extensions of immutable R31 source records, not redrawn or field-measured 1529 geometry. R33 focus is six physical Duravit tub rooms across PH-BATH2, TX-BATH2, TX-BATH4, with selected Hansgrohe Matte White in PH2/TX4 and Chrome TX2, NO tiled shower PAN.

**Do not change:** PH and TX PRIMARY selected Brizo Black Onyx 48in LINEAR with separate BR73480 rough, NO extra Primary niche; parent WC tile floor counted once. PH-BATH4 selected WALK-IN Black Onyx square POINT with separate four-plane PAN and bath LEVEL. PH/TX BATH3 owner TUB or WALK-IN UNSELECTED, point drains only for conditional WALK-IN and not tub waste; PH3 basin, TX2 basin, TX Powder2 basin unselected. PH Powder WALL faucet separate rough; TX Powder AXOR One and Metropol are incompatible separate WALL trim programs not trim+rough, TX Powder2 Tecturis E is DECK mounted, wood powder floors PAN/LEVEL wet tile test N/A. TX203A WC room UNPLACED.

## Original historical cost and physically useful quantity sequencing

Historic **27 material source rows**, two unpriced excluded Primary niches, **25** W elevations and **65** original trade actions are unchanged. **Four-unit material-only USD 23,572.44** includes original **15% waste once**; Sandstone niches **51.64SF / USD358.92**, Grey Soft LEVEL **165.40SF / USD1116.46** and original Caviar niches **34.52SF / USD1163.32** are INCLUDED, not new purchases or savings. Original SOURCE W1+W2+W3 three tub room provisional full faces have been computed separately and compared with original historic gross. These comparisons are not measured signed NET or accepted shortages. True NET = actual wall field minus all measured door/window + one original niche aperture ONCE, plus separately measured niche BACK/TWO SIDES/TOP/SILL only if actually present, after measuring penetration/trim, with a new separately owner-approved waste allowance only on actual new quote; original gross never receives a second 15%.

Material rate sensitivities in R33 apply source historical quoted gross-rate to *hypothetical* change in measured NET geometry without second waste: they do NOT price installed work, create credits or claim current material prices. Twelve carton rounding examples use fictional case yields, with no current order; PH2/TX2 historically same-named Sandstone cannot share a lot unless exact factory SKU/size/color/finish/caliber/lot and usable case coverage proven. Same fixture maker/model across six tubs is BOM comparison only, not six new purchases. Pricing must separate historical quoted material, current maker MSRP, retail indication, current dated Chicago supplier offer, allowances, theoretical owner alternatives, actual full installed GC bid, legitimate deleted parts credit, current stock/lot/freight/ETA and owner-approved cap. Source-only Hansgrohe 72411701 vs 72410701 61USD/unit maker-list delta, 244USD/four Mat White copies, NOT a signed supplier savings.

## Buyer position and eight-trade order

PH approx USD2.8M, TX approx USD2.7M; authentic comparison band USD2.4M to USD3.2M. 14 comps are NINE buildings, OT01-OT04 405 W Armitage one building; Old Town primary and Lincoln Park/Gold Coast adjacent/secondary. No fabricated buyer premium, competitor bath tile SKU or private sale outcome.

OWNER: selected programs/budget, alternate control/finish choice, mockup. ARCHITECT: true native 1529 physical W1/W2/W3, actual opening/niche/rough/trim and tub 59in fit. PLUMBER: source or consented three-endpoint manufacturer-approved valve/rough/spout/cartridge/head/hand and waste/overflow, service, backflow. WATERPROOFER: exact maker tub flange/three-wall membrane corners/seals and shower point/linear system where applicable. TILE INSTALLER: exact item wet WALL and NICHE approval, original raw numeric wet LEVEL and independent applicable PAN lab, caliber/grout/focal cuts, 1:1. SUPPLIER: current exact same-SKU/finish/lot/case and Chicago quote stock/lead/freight. GC: old material 15pct once, every actual wall NET/edge/movement, and full installed rough/wet wall labor bid with true deletion credit. PURCHASER: eight signed trades and genuine original four-seat independent governance; R33 all FALSE.

Formal blind BOARD round017 unchanged. MARKET worker13 .30, DESIGN worker9 .25 FAILED two R014 critiques, BUILD worker10 .25, COST worker12 .20. R014 six of eight, R015 3-seat dispatch HOLD, R017 frozen source eight candidates/four confidential mappings no independent preflight; require FOUR original reports, hard gates, each overall >=3.0 and challenger advantage >=+0.25 from weighted MARKET/DESIGN/BUILD/COST before changing champion in a distinct authorized scoring turn. Sole non-Pro Reviewer15 FINISHED/nonrevivable after R23 PRECISE FIX, R33 prepared five-section report UNSENT/UNREVIEWED. No independent CONTINUE or global DONE, no vendor communications, samples, orders, model/Smartsheet/Git writes.
""")

# Actual integrated predecessor SHA, all signed source files and no owner release.
ancestors={}
for i in range(12,30):
    matches=[d for d in (ROOT/"deliverables").glob(f"integrated-r{i}*")
             if (d/"MANIFEST.json").is_file() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(matches)==1,(i,matches)
    ancestors[f"R{i:03d}_INTEGRATED_MANIFEST_SHA256"]=hashlib.sha256((matches[0]/"MANIFEST.json").read_bytes()).hexdigest()
for k,path in PRE.items():
    ancestors[k+"_SHA256"]=hashlib.sha256(path.read_bytes()).hexdigest()
for n in ("ROUND014_SUBMISSION","ROUND017_SUBMISSION"):
    ancestors[n+"_SHA256"]=hashlib.sha256((ROOT/"state"/(n+".json")).read_bytes()).hexdigest()
comps=json.loads((ROOT/"research/comps/comps.json").read_text(encoding="utf-8"))
assert len(comps["comps"])==14
assert len(FILES)>=21,len(FILES)
manifest={
 "round":33,"date_local":"2026-11-06",
 "phase":"INTEGRATED_THREE_DURAVIT_TUB_ARCHITECT_GC_PURCHASING_ENGINEERING_NO_FORMAL_BOARD_SCORE",
 "project":"1529 Wieland 13 separate bathrooms x two physical copies",
 "focus_rooms":list(focus),
 "immutable_predecessor_SHA256":ancestors,
 "source_invariants":{"distinct_room_ids":13,"two_copy_room_instances":26,
    "historical_material_rows":27,"unpriced_and_excluded_Primary_niche_rows":2,
    "historic_W_studies":25,"original_trade_action_rows":65,
    "original_four_unit_material_ONLY_USD":"23572.44","original_15pct_waste_once":True,
    "Sandstone_USD_included":"358.92","Grey_USD_included":"1116.46",
    "Caviar_USD_included":"1163.32","old_town_comparable_listings":14,
    "actual_unique_comparable_buildings":9},
 "new_eng_studies":{"maker_item_identifications":len(factory),
     "owner_three_tub_GOOD_BETTER_BEST":len(tiers),
     "six_tub_three_outlet_per_branch_RFI":len(paths),
     "three_tub_source_W1W2W3_quote_gross":len(roomsheet),
     "long_axis_focal_3in_cut_module":len(module),
     "six_unit_W1W2W3_shop_field":len(wall18),
     "six_unit_tub_rough_finish_fit":len(fit),
     "three_wall_partial_mortar_membrane_finish_stacks":len(planes),
     "six_synthetic_niche_net_method":len(niches),
     "historic_rate_changeorder_scenarios":len(ratecases),
     "fictional_carton_rounding_scenarios":len(cartons),
     "original_independent_numeric_wet_lab_roles":len(wet),
     "focus_WALL_NICHE_LEVEL_individual_wet_gates":len(application),
     "six_unit_eight_step_shop_holdpoints":len(inspect),
     "all_two_copy_room_witnesses":len(instances),
     "all_two_copy_W_wall_source_witnesses":len(allwalls),
     "original_material_quote_bid_bridge":len(normalize),
     "all_13_room_release":len(releases),
     "eight_trade_13room_signoffs":len(trades),
     "six_unit_camera_and_mockup_futures":len(views)},
 "original_fixture_selections_preserved":True,
 "three_focus_Duravit_tub_no_PAN":True,"TX2_chrome_mixer_source_original_SKU_recovered":False,
 "PH2_TX4_exact_factory_3outlet_thermostatic_spout_approved":False,
 "exact_1529_native_model_or_site_geometry_verified":False,
 "original_exact_raw_numeric_wet_LEVEL_and_PAN_labs_received":False,
 "current_chicago_factory_case_lot_freight_ETA_installed_GC_bid_known":False,
 "sample_render_or_one_to_one_mockup_performed":False,
 "weighted_board_score":None,
 "original_four_critic_reports_complete":False,"independent_nonpro_reviewer_accepted":False,
 "owner_approved":False,"architect_approved":False,"plumber_approved":False,
 "waterproofing_approved":False,"tile_installer_approved":False,
 "supplier_approved":False,"GC_approved":False,"purchaser_approved":False,
 "material_reserved":False,"purchase_authorized":False,"global_13room_DONE":False,
 "files":[{"relative_path":name,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
          for name,b in sorted(FILES.items())]
}
OUT.mkdir(parents=True,exist_ok=False)
for name,b in sorted(FILES.items()):
    with (OUT/name).open("xb") as f:f.write(b)
(OUT/"MANIFEST.json").write_bytes((json.dumps(manifest,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R33_SIGNED",OUT,"SOURCE_FILES",len(FILES))
print("R33_MANIFEST_SHA256",hashlib.sha256((OUT/"MANIFEST.json").read_bytes()).hexdigest())
print("COUNTS",json.dumps(manifest["new_eng_studies"],sort_keys=True))
