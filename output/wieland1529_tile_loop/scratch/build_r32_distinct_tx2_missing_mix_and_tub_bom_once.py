"""R32 substantive next-cycle SOURCE ONLY, additive to signed integrated R31.

TX2 original Chrome tub schedule has no scheduled bathing mixing valve/trim/rough
or tub-filling spout; compare with PH2/TX4 selected Matte White valve-spout issue.
This does not authorize selection or order, or a new formal blind round.
"""
from __future__ import annotations
import csv,hashlib,io,json
from decimal import Decimal
from pathlib import Path

B=Path(__file__).resolve().parents[1]
OUT=B/"research/products"
S=B/"state"
FULL=B/"deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/MANIFEST.json"
H="b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457"
assert hashlib.sha256(FULL.read_bytes()).hexdigest()==H
PREFIX="R32_20261106_"
README=OUT/(PREFIX+"THREE_DURAVIT_TUB_SOURCE_PLUMBING_VALVE_AND_FINISH_IDENTITY_AUDIT.md")
BOM=OUT/(PREFIX+"THREE_TUB_SIX_UNIT_ACTUAL_SELECTED_VS_MISSING_MIXING_ROUGH_SPOUT_BOM.csv")
DETAIL=OUT/(PREFIX+"NINE_ORIGINAL_TUB_WALL_SOURCE_TO_INSTALL_BOM_DEPENDENCY_SECTIONS.csv")
OPTIONS=OUT/(PREFIX+"NINE_SOURCE_ONLY_TUB_MAKER_COMPATIBILITY_BRANCHES.csv")
RECEIPT=S/"ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json"
assert all(not x.exists() for x in (README,BOM,DETAIL,OPTIONS,RECEIPT))

rooms=("PH-BATH2","TX-BATH2","TX-BATH4")
source={r:json.loads((B/"rooms"/r/"plumbing.json").read_text(encoding="utf-8"))["fixtures"] for r in rooms}
def code(r):return {str(x["model_or_sku"]) for x in source[r]}
assert all("700332000000090" in code(r) for r in rooms)
assert all("15758701" in code(r) and "72411701" in code(r) and "01850181" in code(r) for r in ("PH-BATH2","TX-BATH4"))
assert {"04790000","04925000","27458003"}.issubset(code("TX-BATH2"))
assert not any(x in code("TX-BATH2") for x in ("15758701","72411701","01850181","72410701","15739701"))
original={x["id"]:x for x in json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
assert len(original)==13
SRCW=list(csv.DictReader((B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig")))
W={(r["room"],r["wall"]):r for r in SRCW}
orig_rows=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(orig_rows)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in orig_rows)==Decimal("23572.44")
def csvb(rows):
    s=io.StringIO(newline="")
    w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator="\n")
    w.writeheader();w.writerows(rows)
    return s.getvalue().encode("utf-8-sig")
def status(room):
    if room=="TX-BATH2":return "SOURCE_CHROME_HANSGROHE_SHOWER_HEAD_AND_HANDSHOWER_ONLY_NO_IDENTIFIABLE_BATHING_MIXING_VALVE_ROUGH_TUB_SPOUT_IN_LIST"
    return "SELECTED_MATTE_WHITE_15758701_THERMOSTAT_TWO_OUTLETS_PLUS_72411701_PRESSURE_BALANCE_ONLY_DIVERTER_SPOUT_CONFLICT"

items=[]
for room in rooms:
    g=json.loads((B/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
    for room_number in g["revit_room_numbers"]:
        b=source[room]
        val=[x["model_or_sku"] for x in b if x["model_or_sku"] in ("15758701","01850181")]
        sp=[x["model_or_sku"] for x in b if x["model_or_sku"]=="72411701"]
        items.append(dict(room=room,source_physical_room=room_number,unit_copy_status="SOURCE_ROOM_NUMBER_UNVERIFIED",
          selected_bathing_program="DURAVIT_59IN_TUB_NO_TILED_PAN",original_tub="700332000000090",
          originally_schedule_bathing_valve_trim="15758701" if "15758701" in val else "",
          originally_schedule_bathing_valve_rough="01850181" if "01850181" in val else "",
          originally_schedule_tub_filling_spout="72411701" if sp else "",
          original_hansgrohe_chrome_overhead="04925000" if room=="TX-BATH2" else "04388700_MATTE_WHITE",
          original_hand_shower="04790000_CHROME" if room=="TX-BATH2" else "26866701_MATTE_WHITE",
          scheduled_hose_outlet="27458003_CHROME" if room=="TX-BATH2" else "26843701_MATTE_WHITE",
          source_program_problem=status(room),
          manufacturer_authorized_3_ENDPOINT_mixing_and_route="MISSING",
          selected_missing_item_means_installed_absent="NOT_PROVEN",
          fixture_deck_v3_2_reconciliation="REQUIRED_NO_CURRENT_SELECTED_PART_ASSIGNED",
          maker_current_factory_compatible_full_BOM="UNVERIFIED",
          original_1529_tub_rough_site_measurement="",measured_factory_flange_spout_wall_seals="",
          wood_floor_or_pan_branch="TILE_LEVEL_ORIGINAL_WET_RAW_LAB_MISSING_PAN_N_A",
          user_fixture_selection_signed="FALSE",architect_signed="FALSE",plumber_signed="FALSE",
          supplier_actual_current_Sku_same_factory_finish_lot="UNKNOWN",
          complete_installed_GC_bid="UNKNOWN",purchase_authorized="FALSE"))
assert len(items)==6

detail=[]
for room in rooms:
    for wall in ("W1","W2","W3"):
        w=W[room,wall]
        width=float(w["source_width_in_UNVERIFIED"])
        height=float(w["source_tiled_height_in_UNVERIFIED"])
        residual=width-59
        detail.append(dict(room=room,wall=wall,source_width_UNVERIFIED_in=f"{width:.4f}",
          source_height_UNVERIFIED_in=f"{height:.4f}",
          nominal_Duravit_tub_outer_length_in="59.0000",
          source_if_W1_width_minus_nominal_tub_in=f"{residual:.4f}" if wall=="W1" else "N_A_NOT_BACK_WALL",
          source_wall_full_face_SF_before_openings=f"{width*height/144:.4f}",
          actual_1529_native_document_identity="",
          correct_rough_plumbing_trim_or_spout_inwall_program=status(room),
          factory_tub_support_frame_and_waste_access_required="TRUE",
          independent_wall_niche_wet_item_permission="EXACT_FACTORY_MAKER_SOURCE_REQUIRED",
          actual_tub_installs_before_finish_elevation_sequence="FIELD_DETERMINE",
          actual_wall_backer_membrane_compressed_mortar_caliber_stack_in="",
          actual_membrane_over_flange_and_corner_treatment="",
          actual_spout_valve_handshower_penetrations_and_piping="",
          actual_separate_other_openings_and_single_niche_FIELD_cut_SF="",
          actual_niche_back_TWO_SIDES_TOP_SILL_SF="",
          actual_waterproof_tub_rim_movement_joint_LF="",
          actual_signed_wall_NET_SF="",
          original_material_quote_15pct_once="TRUE",tub_floor_LEVEL_RAW_numeric_wet_lab="MISSING",
          tub_PAN="N_A",owner_signed="FALSE",purchase_authorized="FALSE"))
assert len(detail)==9

branches=[]
for room in rooms:
    if room=="TX-BATH2":
        paths=[
          ("GOOD","RETAIN_ORIGINAL_CHROME_SOURCE_AS_INCOMPLETE","No identifiably scheduled bathing mixing-valve trim/rough nor tub spout; source may have omitted them; do not infer field omission or borrow Matte White","Obtain original v3.2 deck and construction submittal/Smartsheet history; verify true source item IDs, actual rough, tub-fill, diverter design, owner program"),
          ("BETTER","CHROME_FACTORY_COMPLETE_THREE_ENDPOINT_DESIGN","Keep original 04925000 Chrome overhead and 04790000 Chrome hand shower, 27458003 check-valve outlet and 700332 tub; maker/plumber submits COMPLETE compatible 3-endpoint TUB+HEAD+HAND plumbing scheme","No fabricated mix/diverter SKU; factory written rough/trim/spout/control diagrams, flow, hot/cold safety, actual shop and Chrome sample"),
          ("BEST","CHROME_SERVICE_AND_TUB_FLANGE_COORDINATED_REDLINE","Retain selected tub/Chrome shower programs; redesign only owner-approved future missing controls with selected accessible service and wall-to-tub full waterproof assembly","Vendor signed 3-outlet compatible SKU BOM, measured rough depth and 59in tub flange full scale, architectural approval and actual GC bid before order"),
        ]
    else:
        paths=[
          ("GOOD","ORIGINAL_MATTE_WHITE_CONFLICT_HOLD","Do not install 72411701 diverter spout on thermostatic 15758701 without factory signed routing; three endpoints with only 2 trim outlets","Written full manufacturer three-endpoint routing and anti-scald/volume compatibility required"),
          ("BETTER","UNSELECTED_72410701_NON_DIVERTER_BRANCH","Retain selected thermostat as intent, possible non-diverter 72410701 spout after owner approves, with independent shower hand/head selector not yet selected","Factory signed spout/rough/thermostat plus independent H/S switching, service and flow compliance"),
          ("BEST","UNSELECTED_15739701_PRESSURE_BALANCE_BRANCH","Retain 72411701 diverter spout if owner changes to Matte White pressure-balance 15739701; historic catalog only and current stock disputed","Manufacturer current SKU/supply, temperature-control consent, hand/head independent selector and exact rough/cartridge compatibility before any bid"),
        ]
    for tier,name,issue,fix in paths:
        branches.append(dict(room=room,tier=tier,branch_name=name,
          three_outlet_endpoints="TUB_FILL+CHROME_OVERHEAD+CHROME_HAND" if room=="TX-BATH2" else "TUB_FILL+MATTE_WHITE_OVERHEAD+MATTE_WHITE_HAND",
          actual_source_problem=issue,conditional_owner_and_factory_decision_tree=fix,
          original_selection_preserved="TRUE",tub_no_tiled_pan="TRUE",
          owner_authorized_change="FALSE",maker_current_system_approved="FALSE",
          original_raw_LEVEL_DCOF_missing="TRUE",actual_CHICAGO_bid_stock_ETA="UNKNOWN",purchase_authorized="FALSE"))
assert len(branches)==9

note="""# R32 next consequential manufacturer/bath hydraulic source: TX-BATH2 newly identified omitted bathing control

2026-11-06. This is a genuinely new SOURCE-ONLY next cycle, not R30 niche-format repetition or an R31 rebundle. Entire 13-room objective remains OPEN. No owner selections changed; no vendor/owner outreach, purchase, Revit, Smartsheet, model or Git mutation. Original R31 full integrated manifest is immutable predecessor.

## Source-specific NEW three-tub program discovery

**TX-BATH2** is a confirmed **Duravit 700332000000090 59 x29-1/2in TUB**, owner selected **Hansgrohe Chrome** showers, never owner-selected Matte White. Its actual 11 fixture records show:

- Chrome overhead 04925000 Hansgrohe Croma Select E 180 2-jet; current factory item confirms 7in head and 2.5GPM maximum: https://pro.hansgrohe-usa.com/articledetail-croma-select-e-showerhead-180-2-jet-2-5-gpm-04925000
- Chrome hand shower set 04790000 Croma Select E wallbar with 3 spray types and original **1.75GPM** manufacturer item listing (source schedule description omitted the maximum): https://pro.hansgrohe-usa.com/articledetail-croma-select-e-wallbar-set-110-3-jet-24-1-75-gpm-04790000
- Chrome FixFit 27458003 wall outlet, manufacturer says **integrated backflow prevention**. It is a handshower outlet with check valve **NOT A MIXING VALVE, DIVERTER OR ROUGH**: https://www.hansgrohe-usa.com/articledetail-fixfit-wall-outlet-round-with-check-valves-27458003
- Duravit 700332 original tub and TD954-20LT waste with TD9028-LS-PCW white trim, but the CURRENT 11-item room schedule has **NO identifiable bathing mixing-valve trim, mixing rough-in valve, or separate tub-fill spout**. That means the schedule is incomplete as a supplier order BOM, **NOT evidence the physical project has no mixing valve**. Reconcile original v3.2 deck, submittal and Smartsheet historical rather than invent or transplant PH2/TX4's Matte White 15758701/72411701.
- Actual source W1 **62.484in x93in** drawing-provisional, nominal 59in Duravit gives **3.484in mathematical source width difference** before framing, finish/backer/flange and whether walls were measured clear vs face. Not an established 3.484in install gap or field fit. PH2 W1 source59.496in and TX4 60in are different, not transferable.

Original **PH-BATH2 and TX-BATH4** separately share the selected **Matte White** 15758701 thermostatic/01850181/72411701 diverter spout factory conflict described in full signed R31. This R32 expands into a comparative actual-six-tub-instance three-color/rough BOM reconciliation: TX2 Chrome is a **MISSING SCHEDULE CONTROL** gate, not necessarily the same pressure-balance versus thermostat incompatibility. Both source programs remain NO tiled shower PAN. All three require LEVEL original exact numerical wet DCOF, separate WALL/NICHE wet maker evidence, tub-flange and actual certified 1529 opening/alcove geometry.

## Distinct technical and procurement improvements

- **Six** physical tub-copy source BOM rows across three tubs x2 copies: exact recorded selected versus blank mixing rough/spout, actual 3-endpoint source map; all no new selected parts. Supplier contract cannot price the blank items until owner/architect/plumber recover the original approved control source.
- **Nine** source W1/W2/W3 tub-flange and penetrations quantity dependency rows, with factory 59in length vs each unverified W1 span, actual 1529 wall/finish/flange data blank; preserve one original niche WALL aperture deduction and separately tiled BACK/TWO SIDES/TOP/SILL plus original 15% already included.
- **Nine** GOOD/BETTER/BEST *technical branch* options: three TX2 Chrome paths address the newly missing mix/spout controls with no invented SKU; six PH2/TX4 Matte White alternatives retain original selected baseline until owner/maker verifies the two-outlet spout conflict. No board neutral blind candidates, no independent critic scores.

## Required field/shop and purchasing decision

Find one authentic approved v3.2/Smartsheet control/rough/spout record for TX2, then obtain current manufacturer exact Chrome-compatible full three-outlet tub/overhead/hand shower routing, factory rough and listed accessory identity, anti-scald/flow/check valves and service. Cross-verify all six physical room copies' true 1529 wall spans, tub flanges, waterproof returns, tile finished planes, trap/waste, actual openings/niche and one-to-one mockup. Case/lot current Chicago and installed GC bid remain unknown. Historic $23,572.44 and 27/25/65 original evidence preserved; no change order ascertained. All owner/architect/plumber/waterproof/tile/supplier/GC/purchaser signatures and material release FALSE. Current original DESIGN worker9 failed and authorized Reviewer15 nonrevivable; no independent clearance or global DONE.
"""

payloads={README:note.encode("utf-8"),BOM:csvb(items),DETAIL:csvb(detail),OPTIONS:csvb(branches)}
for p,b in payloads.items():
    with p.open("xb") as f:f.write(b)
rec=dict(round=32,phase="DISTINCT_NEXT_SOURCE_ONLY_NO_FORMAL_BLIND_BOARD",date_local="2026-11-06",
    predecessor_R31_FULL_SHA256=H,
    signed_outputs=[dict(path=p.relative_to(B).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for p,data in payloads.items()],
    measurements=dict(three_source_tub_room_programs=3,actual_source_physical_room_copies=6,source_wet_wall_section_targets=9,conditional_branch_count=9,
                      TX2_original_bath_mix_trim_rough_and_spout_scheduled=0,
                      selected_Chrome_TX2_source_remaining_unchanged=True),
    original_historic_material_only_USD="23572.44",original_15pct_waste_in_source_once=True,
    true_1529_native_site_verified=False,all_source_bathing_control_BOM_complete=False,
    new_owner_selected_fixture=False,original_raw_numeric_wet_lab_received=False,
    formal_original_four_seat_critics_clear=False,independent_nonpro_reviewer_accepted=False,
    supplier_contacted=False,material_reserved=False,purchase_authorized=False,global_DONE=False)
RECEIPT.write_bytes((json.dumps(rec,indent=2)+"\n").encode("utf-8"))
print("R32_SOURCE_ONLY_RECEIPT",hashlib.sha256(RECEIPT.read_bytes()).hexdigest())
print("R32_NEW_RECORDS",len(items),len(detail),len(branches),"SOURCE_FILES",len(payloads))
