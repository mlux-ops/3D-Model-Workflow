"""One-time R17 evidence-forward 13-room owner/GC package. No source mutation."""
from pathlib import Path
from decimal import Decimal
import json,hashlib,csv,io

R=Path(__file__).resolve().parents[1]
OUT=R/"deliverables/integrated-r17"
assert not OUT.exists(), "R17 signed output already exists"
OUT.mkdir(parents=True)
S=R/"state"; old=R/"deliverables/integrated-r16"; r15=R/"deliverables/integrated-r15"
rooms=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
src=list(csv.DictReader((old/"R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv").open(encoding="utf-8-sig",newline="")))
walls=list(csv.DictReader((old/"R16_25_WALL_EDGE_MOVEMENT_AND_CUT_OPEN_HOLDS.csv").open(encoding="utf-8-sig",newline="")))
acts=list(csv.DictReader((r15/"R15_65_TRADE_ACTIONS_LATEST_SCORES.csv").open(encoding="utf-8-sig",newline="")))
assert len(rooms)==13 and len(src)==27 and len(walls)==25 and len(acts)==65
assert len(set(x["original_smartsheet_row_id"] for x in src))==27
assert len(set((x["room"],x["group"]) for x in acts))==65
room_ids=[r["id"] for r in rooms]
assert {x["room"] for x in src}<=set(room_ids)
assert {x["room"] for x in acts}==set(room_ids)
total=sum((Decimal(x["two_copy_historic_material_usd"] or "0") for x in src),Decimal("0"))
assert total==Decimal("23572.44"), total
excluded=[x for x in src if x["old_material_usd_per_copy"]==""]
assert len(excluded)==2 and {x["room"] for x in excluded}=={"PH-PRIMARY","TX-PRIMARY"}
assert all(x["owner_finish_program_approved"]=="FALSE" and x["gc_purchase_release"]=="FALSE" for x in src)

decisions={
"PH-PRIMARY":("BLOCKED","48in BNX LINEAR + BR73480; NO NICHE","WALL flat maker application distinct from relief; shared WC LEVEL test; separate LINEAR PAN raw DCOF","PH 48in selected linear rough, frame 7-18mm and mosaic thickness fit hold","separate fixed tub and shower; no shower niche","Owner signs final flat-field shade, no additional niche, material cap"),
"PH-BATH2":("BLOCKED","Duravit TUB; Hansgrohe MATTE WHITE; NO tiled PAN","Sapphire wet WALL PASS; Sandstone NICHE PASS; LEVEL exact raw DCOF NULL","0.496in nominal alcove fit check; tub flange, valve axes","tub apron/edge and 2x20 Sapphire stacked sample","Owner approves exact tub-wall tile/grout and bid"),
"PH-BATH3":("BLOCKED","Delta DT062412 Chrome POINT shower drain; TUB/WALK-IN unselected; PH BASIN unselected","Opal wet WALL FAIL; Sapphire wet PASS proposed; Sandstone NICHE PASS; LEVEL raw NULL; conditional POINT PAN raw NULL","if tub new tub waste/flange; if walk-in Delta 4-plane clamped-liner section","two distinct TUB and WALK-IN renders without an election","Owner signs TUB or WALK-IN and basin before geometry/shop"),
"PH-BATH4":("BLOCKED","Brizo BT062415-BNX 4in SQUARE POINT WALK-IN; NO TUB","Cortar Bone Ribbed/Clara Caviar wet permissions absent; flat Bone/Soho Black wet alternative; LEVEL/POINT PAN raw NULL","35 vs 27-SF reconciliation; source Soft/AntiSlip; potential 214.4 SF Ribbed vendor-total audit","flat versus ribbed elevation, wet niche and BNX point detail","Owner signs actual 35/27 area and sample/upgrade before quote"),
"PH-POWDER":("ACTIVE","DRY vanity tile/WOOD FLOOR; Luxe Gold wall faucet","DRY vanity WALL; bath wet LEVEL and PAN tests N/A","Flat wall escutcheon landing, sink rough, movement and edge","Earth Lines sample, 1:1 escutcheon/edge","Owner approves conditional Earth Lines visual only"),
"PH-WC":("SEEDED","Inherited PH-PRIMARY LEVEL only; NO independent purchase","Shared Primary exact raw LEVEL wet DCOF required once; shower PAN N/A","WC threshold and movement; net includes Primary gross","Threshold tile sample match Primary","Owner/GC approve single allocation without duplicate cartons"),
"TX-PRIMARY":("BLOCKED","48in BNX LINEAR + BR73480; NO NICHE","Flat Clay maker wet WALL PASS distinct from Ribbed; LEVEL/shared WC and separate LINEAR PAN raw NULL","Selected 48in linear system, grade/rough/membrane and grate frame hold","Clay flat sample; 48in linear and 1:1 mosaic","Owner signs no added niche; cap and material/rough"),
"TX-BATH2":("BLOCKED","Duravit TUB; Hansgrohe CHROME; BASIN owner UNSELECTED; NO PAN","Copper and Sandstone wet WALL/NICHE PASS; historical Clay Soft raw LEVEL NULL; conditional Prime White EL30 Target only","Real tub flange/backer and measured W1 at tub edge; sink unselected","Copper horizontal vs offset mockup, Chrome against warm white floor","Owner selects basin, tub finishes and budget"),
"TX-BATH3":("BLOCKED","Brizo BT062415-BNX Black Onyx POINT; owner TUB/WALK-IN unselected","Emerald and Sandstone wet PASS; LEVEL raw NULL, conditional POINT PAN raw NULL","Owner program versus tub alcove; actual Brizo clamped liner if WALK-IN","Emerald/BNX two alternative program renders","Owner first chooses TUB/WALK-IN; preserve selected shower POINT"),
"TX-BATH4":("BLOCKED","Duravit TUB; Hansgrohe MATTE WHITE; NO PAN","Charcoal flat wet WALL PASS; Clara Caviar NICHE unlisted; Soho Ivory wet listed conditional; Bone Soft/Prime Grey LEVEL raw NULL","Niche back/returns/sill, 2x10 vs 24x48 joint and true tub flange","Charcoal contrast and Ivory luminous niche versus Caviar","Owner signs approved niche/LEVEL palette, no tub PAN"),
"TX-POWDER":("ACTIVE","DRY vanity WALL; WOOD FLOOR","NO wet bath LEVEL or shower PAN","Haze Camel/Wheat 70:30 feature wall, edges, faucet backing","Two 70:30 1:1 swatches and metal silhouette","Owner approves powder palette"),
"TX-POWDER2":("ACTIVE","DRY vanity WALL; WOOD FLOOR; sink owner UNSELECTED; Hansgrohe 73072341 DECK-mounted","NO tiled wet LEVEL or PAN","Deck faucet rough and basin opening not wall-faucet","Indigo Edge 6x6 + deck-mount 1:1 vanity mockup","Owner selects actual basin and deck hole layout"),
"TX-WC":("SEEDED","Inherited TX-PRIMARY LEVEL only; NO separate tile order","Shared Primary exact raw LEVEL wet DCOF once; shower PAN N/A","WC threshold/movement, no duplicate cartons","Primary threshold 1:1 sample","Owner/GC verifies shared order not duplicate")
}
assert set(decisions)==set(room_ids)
def writecsv(name,fields,rows):
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for row in rows:
            assert set(row)==set(fields),(name,set(row)^set(fields))
            w.writerow(row)
def sha(p):
    b=p.read_bytes()
    return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}

roomrows=[]
for x in rooms:
    rid=x["id"]; status,program,wet,construct,render,sign=decisions[rid]
    assert x["status"].upper()==status,(rid,x["status"],status)
    roomrows.append(dict(
        room=rid,original_room_status=status,latest_original_board_round=x.get("last_round"),
        source_material_usd_per_copy=str(sum(Decimal(z["old_material_usd_per_copy"] or "0") for z in src if z["room"]==rid)),
        owner_program_or_selected_plumbing=program,
        source_specific_WALL_NICHE_LEVEL_PAN_tests=wet,
        architect_GC_shop_and_waterproofing_hold=construct,
        owner_sample_and_render_option=render,
        owner_signoff_task=sign,
        actual_1529_measurement_id="",owner_signature="",architect_signature="",GC_shop_signature="",supplier_quote_id="",verified_exact_lot_and_cases="",authorized_purchase_order="",owner_approved="FALSE",GC_release="FALSE",procurement_release="FALSE"
    ))
assert sum(Decimal(z["source_material_usd_per_copy"])*2 for z in roomrows)==Decimal("23572.44")
writecsv("R17_13_OWNER_GC_RELEASE_GATES.csv",list(roomrows[0]),roomrows)

materialrows=[]
for x in src:
    rid=x["room"];surface=x["source_surface"].lower()
    excluded_row=bool(x["old_material_usd_per_copy"]=="")
    is_powder="POWDER" in rid
    is_primary=rid.endswith("PRIMARY")
    is_tub=rid in ("PH-BATH2","TX-BATH2","TX-BATH4")
    is_bath3=rid in ("PH-BATH3","TX-BATH3")
    relevant=("NONE / dry wall, WOOD floor" if is_powder else
              "N/A / excluded extra Primary niche" if excluded_row else
              "N/A / inherited WC no independent floor line" if rid.endswith("-WC") else
              "LEVEL mandatory, TUB PAN N/A" if is_tub else
              "LEVEL mandatory; conditional POINT PAN only after owner WALK-IN" if is_bath3 else
              "LEVEL mandatory; separate LINEAR PAN only if floor source" if is_primary else
              "LEVEL mandatory; square POINT PAN separately")
    raw_level=("N/A" if excluded_row or surface in ("wall","accent","niche") or is_powder else "")
    raw_pan=("N/A" if excluded_row or is_powder or is_tub or surface in ("wall","accent","niche") else "")
    materialrows.append(dict(
        room=rid,source_row_id=x["original_smartsheet_row_id"],source_surface=x["source_surface"],
        source_gross_sf_one_copy_waste_15pct_once=x["source_quantity_gross_sf_per_copy_15pct_included"],
        historic_usd_one_copy=x["old_material_usd_per_copy"],
        historic_usd_two_copies=x["two_copy_historic_material_usd"],
        source_no_order="TRUE",historic_niche_excluded_no_scope="TRUE" if excluded_row else "FALSE",
        actual_selected_tile_SKU_finish="",source_or_conditional_maker_evidence=x["individual_wet_wall_niche_authorization"],
        individual_wall_niche_wet_doc_url="",LEVEL_vs_PAN_applicability=relevant,
        exact_RAW_measured_LEVEL_wet_DCOF="" if raw_level=="" else raw_level,
        exact_RAW_measured_POINT_or_LINEAR_PAN_wet_DCOF="" if raw_pan=="" else raw_pan,
        wet_lab_method_test_sample_and_date="",verified_1529_measured_wall_openings_and_net_sf="",
        measured_level_net_sf="",measured_pan_net_sf="",niche_opening_displaced_field_back_returns_sill_net_sf="",
        confirmed_once_only_waste_factor="0.15 already within original source gross; reapply only ONCE to new verified net, not to original gross",
        actual_carton_coverage_sf="",number_orderable_full_cases="",shade_lot_and_stock_allocated="",
        dated_local_supplier_material_offer="",manufacturer_MSRP="",public_retail_offer="",
        freight_tax_setting_waterproof_install_cost="",owner_room_cap="",owner_signed="FALSE",GC_signed="FALSE",purchase_release="FALSE",
        conditional_order_formula="NO ORDER (excluded reference)" if excluded_row else "ceil((verified NET surface SF + documented approved cut waste SF) / confirmed exact SKU carton yield), separately by material and pan/level branch; no original SF double purchase",
        source_trace="integrated-r16/R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv; original 2026-09-03 vendor rows"
    ))
assert len(materialrows)==27
writecsv("R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv",list(materialrows[0]),materialrows)

actionrows=[]
for a in acts:
    group=a["group"];rid=a["room"]
    extra={"manufacturer_spec":"Obtain individual product wall/niche wet listing and raw numbered manufacturer SKU/format LEVEL and separate PAN laboratory certificate if applicable.",
           "dimensions_and_edge":"Field confirm native 1529, actual W1-W3 heights/openings, niche net and trim LF; annotate movement joints and actual fixture rough.",
           "floor_pan_and_drain":"Match existing selected drain/rough and waterproof/waste/flood; do not invent shower PAN in tub or powder room.",
           "owner_approval":"Owner signs room-specific palette, basin where unselected, TUB/WALK-IN Bath3 program, approved upgrade cap.",
           "vendor_quote_and_stock":"After authorization, dated exact SKU dye lot cases stock freight tax and full installed waterproofing GC bid, no vendor outreach now."}[group]
    actionrows.append(dict(
        room=rid,trade_action=group,responsible_trade=a["responsible_trade"],prior_R15_source_action=a["measurable_next_closure"],
        R17_independently_closable_deliverable=extra,exact_required_evidence_id="",technical_review_by="",actual_1529_geometry_proven="FALSE",
        selected_owner_plumbing_preserved=decisions[rid][1],
        source_2026_09_03_material_per_copy_usd=a["source_quote_usd_per_copy_2026_09_03"],
        current_trade_bid_id="",owner_signed="FALSE",GC_acceptance="FALSE",purchase_release="FALSE"
    ))
writecsv("R17_65_TRADE_CLOSURE_EVIDENCE_REQUESTS.csv",list(actionrows[0]),actionrows)

wallrows=[]
for w in walls:
    rid=w["room"]; g=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
    ww=next((z for z in g["tiled_walls"] if z["id"]==w["wall"]),None)
    assert ww is not None
    wallrows.append(dict(
        room=rid,wall=w["wall"],source_width_in_UNVERIFIED=w["drawing_width_in_not_verified"],
        source_tiled_height_in_UNVERIFIED=w["drawing_tiled_height_in_not_verified"],
        source_nominal_field_area_sf=w["prior_nominal_source_face_sf"],
        historical_balanced_cut_not_release=w["historical_balanced_tile_study"],
        proposed_per_actual_tile_caliber_formula="balanced_end_cut_in = (verified_face_width_in - N*calibrated_tile_width_in - (N+1)*selected_joint_in) / 2; select N avoiding visible focal slivers; check >3in where feasible",
        actual_tile_nominal_and_caliber_in="",selected_joint_width_in="",actual_face_width_in="",actual_tiled_height_in="",actual_architectural_openings_sf="",
        actual_niche_aperture_sf_displace_field_once="",niche_back_sf="",niche_returns_sf="",niche_sill_sf="",
        actual_finished_edge_LF="",movement_joints_locations_and_LF="",waterproofing_detail_ref="",valve_and_shower_glass_layout="",actual_net_tile_surface_sf="",
        estimator_formula="verified face area - doors/windows/one niche opening + separately measured back/returns/sill (each counted once); approved waste once after NET; verify edges and movement",
        true_1529_document_receipt="",owner_approved="FALSE",architect_gc_approved="FALSE"
    ))
writecsv("R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv",list(wallrows[0]),wallrows)

labrows=[]
for x in rooms:
    rid=x["id"]
    if "POWDER" in rid:
        surf="DRY_WALL_ONLY"; level="N/A_WOOD_FLOOR"; pan="N/A"
    elif rid.endswith("-WC"):
        surf="SHARED_INHERITED_PRIMARY_LEVEL";level="REQUIRED_IN_PARENT_PRIMARY_ONCE";pan="N/A"
    elif rid in ("PH-BATH2","TX-BATH2","TX-BATH4"):
        surf="WET_TUB_WALL_PLUS_NICHE";level="REQUIRED_RAW_EXACT_NUMERIC";pan="N/A_TUB"
    elif rid in ("PH-BATH3","TX-BATH3"):
        surf="WET_WALL_PLUS_NICHE";level="REQUIRED_RAW_EXACT_NUMERIC";pan="CONDITIONAL_IF_OWNER_WALKIN_RAW_EXACT_NUMERIC"
    elif rid in ("PH-PRIMARY","TX-PRIMARY"):
        surf="WET_SHOWER_WALL_NO_ADDED_NICHE";level="REQUIRED_RAW_EXACT_NUMERIC_INC_WC";pan="REQUIRED_SEPARATE_LINEAR_RAW_EXACT_NUMERIC"
    else:
        surf="WET_WALKIN_WALL_PLUS_NICHE";level="REQUIRED_RAW_EXACT_NUMERIC";pan="REQUIRED_SEPARATE_POINT_RAW_EXACT_NUMERIC"
    labrows.append(dict(room=rid,wet_wall_or_other_applicability=surf,required_LEVEL_lab_gate=level,required_PAN_lab_gate=pan,
                        exact_wall_SKU_color_finish_wet_permission_doc="",exact_niche_SKU_color_finish_wet_permission_doc="",
                        exact_LEVEL_SKU_size_finish="",actual_raw_numeric_LEVEL_wet_DCOF="",LEVEL_lab_method_date_sample_ref="",
                        exact_PAN_SKU_size_finish="",actual_raw_numeric_PAN_wet_DCOF="",PAN_lab_method_date_sample_ref="",
                        no_inherited_test_or_target_as_raw="TRUE",owner_approval="FALSE",GC_release="FALSE"))
writecsv("R17_13_ROOM_WET_LAB_AND_PROGRAM_MATRIX.csv",list(labrows[0]),labrows)

book=[
"# R17 — evidence-to-shop and owner/GC coordinated thirteen-room technical decision package",
"",
"**2026-11-06. NOT AN OWNER APPROVAL, A LAB CERTIFICATE, A CURRENT SUPPLIER BID, AN INSTALLED ALLOWANCE OR A PROCUREMENT RELEASE.** R17 is additive to signed R12–R16; no predecessor file is edited, copied into a replacement or rescored. R014 remains UNSCORED until 8 authentic critiques pass independent clearance. Current Revit title is 1527, not authenticated 1529.",
"",
"## A. New controls beyond R16",
"",
"R17 links **27 original source-line IDs to conditional full-case quantity evidence**, **65 responsible trade actions to separately auditable closure proofs**, **25 provisional W1–W3 elevations to measurable field cuts and niche/edge deductions**, **13 individual owner/GC acceptance checkpoints**, and **13 room-specific wet FLOOR/PAN applicability gates**. None is a false positive acceptance; every release field remains FALSE. Six detailed CSV schedules below are not substitutes for measured/shop-approved specifications.",
"",
"### Owner and GC sequence",
"",
"1. Owner first decides two Bath3 TUB or WALK-IN programs; no assistant election. Preserve PH3 unselected sink, TX2 basin and TX Powder2 basin as UNSELECTED. Preserve actual selected PH4 WALK-IN 4-in Brizo POINT; PH/TX Primary 48-in Brizo Black Onyx LINEAR + BR73480 and no extra niches; PH2/TX2/TX4 actual Duravit TUB with no tiled PAN.",
"2. Architect/GC verify correct 1529 building and survey rough-to-finish widths, W1–W3, pan point/linear drain center, threshold, niche opening/back/returns/sill, valve axes, dry and wet boundaries, exposed trim LF, movement locations and tile caliber; label all R17 inherited drawing dimensions PROVISIONAL.",
"3. Manufacturer must provide each exact color/format/finish WALL and NICHE Wet Areas authorization, plus a numbered exact RAW MEASURED wet DCOF result for each applicable LEVEL tile and separately for each LINEAR/POINT PAN mosaic. The supplier may not substitute brochure DCOF Target, Glazzio >0.50 or Emser >=0.60 bounding statements for an actual reading.",
"4. Plumbing/waterproofing/GC produce exact maker-approved drain/rough, membrane, slope, curb/glass and test section for WALK-IN; actual tub, waste/overflow, tub flange, penetrations and waterproof termination in TUB branches. The Delta DT062412 and Brizo BT062415-BNX 4-in SQUARE POINT shower drains are never tub wastes.",
"5. Tile estimator independently computes manufacturer-calibrated module and balanced cut around actual openings, subtracts niche displaced field once, adds back/returns/sill once and applies ONE approved waste factor to newly measured NET quantities. Historic gross **already includes original 15% once**; do not multiply original gross again or order full LEVEL and full PAN duplicates. The two unpriced Primary niche references are NO SCOPE/NO ORDER.",
"6. Obtain 1:1 maker samples and installation assembly mockups after authorization; compare selected metal escutcheon/drain finish, grout/color in project light and source-sized edge; issue room photo/render brief with explicit uncertainties (no verified competitor tile photos). Separately owner signs the visual program/cap and architect+GC sign shop/quantities/complete installed price; finally project purchaser may release. Current release FALSE.",
"",
"## B. Exact maker/application decision points (not proof of raw lab)",
"",
"| Manufacturer/material | Role | Evidence status | Separate remaining gate |",
"|---|---|---|---|",
"| ELM Tones Sapphire 2×20 Glossy | PH Bath2 listed wet tub wall and PH Bath3 conditional wet WALL | [Individual maker Wet Areas](https://www.elmsurfaces.com/product/sapphire-tones) | Does NOT authorize historic Opal and is not wet FLOOR DCOF |",
"| ELM Tones Copper 2×20 Glossy + Sandstone niche | TX Bath2 selected tub WALL + NICHE | [Copper](https://www.elmsurfaces.com/product/copper-tones), [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) individual wet applications; verify exact source pages before release | Exact waterproof, size/caliber, selected Chrome and net |",
"| ELM Tones Emerald 2×20 Glossy + Sandstone | TX Bath3 potential tub/walk-in wet WALL + NICHE | [Emerald](https://www.elmsurfaces.com/product/emerald-tones), [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) Wet Areas | Owner program and LEVEL / conditional POINT PAN lab |",
"| ELM Cortar Bone/Clay/Charcoal FLAT | Corresponding approved WET WALL-only conditional designs | Individual flat-maker wet listing; dimensional Ribbed/Reed not inherited | Finish/variant trace and installer 24×48 flatness and actual selected tile |",
"| ELM Soho Ivory Glossy 2×10 | TX Bath4 CONDITIONAL individually wet niche; no owner acceptance | [Individual Ivory Wet Areas](https://www.elmsurfaces.com/product/soho-ivory) | Historical Clara Caviar lacks individual wet permission and is not approved by this different tile |",
"| Daltile Prime RL21 Dynamic Beige | Conditional level 12×24 and distinct separate small hex shower PAN in other rooms | [Official maker catalog](https://www.daltile.com/products/stone-look/prime/dynamic-beige) lists **Target ≥0.42** | Not the exact raw SKU lab; 3/16-vs-1/8 grout source version and 1/4-vs-5/16 hex nominal remain HOLD |",
"| Daltile Prime White Elect EL30, 12×24 Matte | New conditional TX Bath2 LEVEL-only study; **no tiled PAN** | [White Elect official page](https://www.daltile.com/products/stone-look/prime/white-elect), white EL30 U.S. 12×24 matte 3/8 nominal | Manufacturer Target wet DCOF NOT raw measured individual reading, quote/case/yield and installed price NULL |",
"| Daltile Prime Grey Koncrete KC04, 12×24 Matte | New conditional TX Bath4 LEVEL-only study; **no tiled PAN** | [Grey Koncrete official page](https://www.daltile.com/products/stone-look/prime/grey-koncrete), KC04 U.S. 12×24 matte 3/8 nominal | Maker 1/8-in grout recommendation, Target NOT raw wet result; compare to individual exact joint/lot; no vendor bid |",
"",
"## C. Thirteen room GOOD / BETTER / BEST and render/sampling decisions",
"",
"| Room | GOOD: legally preserve source | BETTER: visual and technical alternative to sample | BEST: documented release threshold (not design commitment) |",
"|---|---|---|---|"
]
for row in roomrows:
    rid=row["room"]
    book.append("| "+rid+" | Preserve dated material rows $"+row["source_material_usd_per_copy"]+"/copy and selected plumbing, no owner approval | "+row["owner_sample_and_render_option"]+" | "+row["architect_GC_shop_and_waterproofing_hold"]+"; "+row["source_specific_WALL_NICHE_LEVEL_PAN_tests"]+"; "+row["owner_signoff_task"]+"; actual measured/lot/installed quote and signatures required |")
book += [
"",
"## D. Release math and purchase authority",
"",
"Historic 2026-09-03 four-unit material-only basis: **$23,572.44** (two PH + two TX); all 27 historical rows preserved, including two source Primary niche references historically excluded/unpriced, not $0 order authorizations. 15% original waste already embedded in quoted source gross SF once. The full-case release formula is conditional: measured net surface including niche displacements and returns, plus a separately justified approved waste quantity, divided by actual confirmed cartons per exact SKU/color/finish, rounded up by material; **never** infer a carton or installed price from old ELM rates.",
"",
"No live Chicago local lot, verified current trade sell price, delivered freight/tax, labor, waterproof installation, owner allowance or supplier reservation exists. Public Daltile [Chicago design showroom](https://locations.daltile.com/il/chicago/233/) and [Elk Grove service center](https://locations.daltile.com/il/elk-grove-village/124/) are possible channels only, not project stock confirmations. ELM [public Chicago contact](https://www.elmsurfaces.com/contact) likewise not a quoted trade offer. Separate manufacturer MSRP and public retailer screenshots from actual dated owner-authorized GC bids.",
"",
"## E. Specific hard holds, not fabricated failures",
"",
"- Original PH Bath4 area **35 vs 27 SF**, source **Soft/Anti-Slip**, original **107.2 SF/copy Ribbed** and **Clara Caviar** individual wet FAIL remain separate disputes. Potential 214.4 SF two-copy vendor aggregate difference is a reconciliation question only, NEVER payable shortage/credit.",
"- Selected Primary 48-in Brizo Black Onyx LINEAR tile-in frame **7–18 mm** and RL21 current mosaic **5/16 in**, earlier **1/4 in** and 1/8 vs 3/16 grout maker version disagreements are assembly HOLD, not proven fit/incompatibility.",
"- PH Bath2 selected Duravit 59-in tub against drawing 59.496-in nominal width offers only 0.496-in theoretical difference BEFORE rough/backer/flange/tile; no certification of fit or clash.",
"- PH Bath3 and TX Bath3 source tub alcove drawings versus selected SQUARE shower POINT drains are owner branch decisions, not a reversible drain-to-tub adaptation. See independently cleared R014 Bath3 point-drain addendum.",
"- PH/TX WC rooms inherit Primary LEVEL floor tile and same LEVEL test; no distinct purchasable original WC floor rows; dry powder walls on wood floors require no imaginary wet shower pan or bath LEVEL tile lab.",
"",
"## F. Comparables and cost context",
"",
"Market file holds 14 listing entries representing **nine buildings**; OT01–OT04 at 405 W Armitage count as **ONE** precedent, Old Town recent <=24 months preferred; Lincoln Park/Gold Coast must be labelled secondary. PH sale target $2.8M, TX $2.7M, target comp band $2.4M–$3.2M. There are no authenticated competitor tile photos; no claimed finishes in unseen images. Current budget caps, upgrade % and comparative installed bids remain NULL.",
"",
"## G. Outputs, required order of review",
"",
"1. R17_13_OWNER_GC_RELEASE_GATES.csv: all 13 actual room statuses and separately signable approvals.",
"2. R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv: frozen source IDs and quantities, tested applications and exact carton evidence fields.",
"3. R17_65_TRADE_CLOSURE_EVIDENCE_REQUESTS.csv: 65 existing original trade actions enriched with measurable next documentation and authority.",
"4. R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv: every original drawing W1–W3 mapped to actual measured cut, movement, trim and opening/niche deduction inputs.",
"5. R17_13_ROOM_WET_LAB_AND_PROGRAM_MATRIX.csv: WALL/NICHE, bath LEVEL and separate LINEAR/POINT PAN gates with N/A where physically inapplicable.",
"",
"No supplier outreach, sample orders, model writes, site certification, owner approval, material release, labor purchase or change to the frozen R014 or signed R16 evidence occurred."
]
(OUT/"R17_13_ROOM_DESIGN_AND_RELEASE_FIELD_BOOK.md").write_text("\n".join(book)+"\n",encoding="utf-8")
(OUT/"START_HERE_R17.md").write_text("# R17 — coordinated owner, GC and estimator release review\n\nStart with R17_13_ROOM_DESIGN_AND_RELEASE_FIELD_BOOK.md and review five SHA-signed CSVs by source row, trade action, W elevation, room release and manufacturer raw wet-test applicability. Additive ONLY to signed R12–R16; zero accepted R014 weighting, owner approvals or purchases. Current native document says 1527, not certified 1529.\n",encoding="utf-8")
outputs=sorted([p for p in OUT.iterdir() if p.is_file()])
assert len(outputs)==7,len(outputs)
man={
"as_of":"2026-11-06","round":14,"phase":"additive_R17_all_13_rooms_open",
"kind":"new 13-room evidence-to-GC shop + manufacturer wet lab + conditional carton + five class trade closure and 25 wall plan",
"room_count":len(rooms),"source_material_rows":len(src),"source_trade_actions":len(acts),"source_wall_elevations":len(walls),
"original_historic_material_usd_four_unit":str(total),"source_waste_15pct_included_once":True,
"source_R16_manifest_sha256":sha(old/"MANIFEST.json")["sha256"],
"source_R15_manifest_sha256":sha(r15/"MANIFEST.json")["sha256"],
"source_R014_submission_sha256":sha(S/"ROUND014_SUBMISSION.json")["sha256"],
"source_R014_dispatch_sha256":sha(S/"ROUND014_CRITIC_DISPATCH.json")["sha256"],
"original_R014_critic_collection_complete":False,"R014_weighted_scoring":None,
"all_13_room_owner_release":False,"actual_1529_model_verified":False,
"source_originals_untouched":True,"owner_approval":False,"procurement_release":False,
"outputs":{p.name:sha(p) for p in outputs}
}
(OUT/"MANIFEST.json").write_text(json.dumps(man,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert sum(Decimal(x["source_material_usd_per_copy"])*2 for x in roomrows)==Decimal("23572.44")
assert all(row["owner_approved"]=="FALSE" for row in roomrows)
assert all(row["purchase_release"]=="FALSE" for row in materialrows)
assert len({(w["room"],w["wall"]) for w in wallrows})==25
print("PASS additive R17 seven outputs signed + MANIFEST, 13 owner room gates, 27 source material, 65 trades, 25 walls and 13 wet lab rows; historic $23572.44 15pct once; R014 unscored; release false")
print("R17_MANIFEST_SHA",sha(OUT/"MANIFEST.json")["sha256"])
