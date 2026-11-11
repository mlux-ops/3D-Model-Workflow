"""Additive signed R16 source-to-field-and-owner evidence book; never edits earlier packages."""
from pathlib import Path
import csv,hashlib,json,math
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
OUT=R/'deliverables/integrated-r16'
assert not OUT.exists()
rs=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
rooms={r['id']:r for r in rs}
assert len(rooms)==13
def csvread(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
r13=R/'deliverables/integrated-r13'
r15=R/'deliverables/integrated-r15'
source=csvread(r13/'R13_27_SOURCE_TO_CONDITIONAL_PURCHASE_RECONCILIATION.csv')
oldcuts=csvread(r13/'R13_25_WALL_OPTION_A_B_FIELD_CUT_AND_EDGE_LAYOUTS.csv')
actions=csvread(r15/'R15_65_TRADE_ACTIONS_LATEST_SCORES.csv')
last=csvread(r15/'R15_13_ROOM_SCORED_OWNER_RELEASE_REGISTER.csv')
assert len(source)==27 and len(oldcuts)==25 and len(actions)==65 and len(last)==13
assert set(rooms)=={r['room'] for r in last}
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit']))*r['unit_count'] for r in rs)==Decimal('23572.44')

def use(rid):
    if rid.endswith('WC'):return 'INHERITED_PRIMARY_LEVEL'
    if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2'):return 'DRY_VANITY_WALL_WOOD_FLOOR'
    if rid in ('PH-PRIMARY','TX-PRIMARY'):return 'LEVEL_BATH_AND_SHARED_WC_SEPARATE_LINEAR_PAN'
    if rid in ('PH-BATH2','TX-BATH2','TX-BATH4'):return 'TUB_LEVEL_ONLY_NO_TILED_PAN'
    if rid=='PH-BATH4':return 'WALK_IN_SQUARE_POINT_SEPARATE_LEVEL_AND_PAN'
    if rid in ('PH-BATH3','TX-BATH3'):return 'OWNER_UNSELECTED_TUB_OR_WALKIN_SQUARE_POINT_CONDITIONAL'
    raise AssertionError(rid)
def wall_gate(rid):
    if rid=='PH-BATH3':return 'Source Tones Opal individually Wet Areas UNLISTED FAIL; proposed Sapphire and existing Sandstone individually maker wet-listed PASS only for WALL/NICHE; no owner change approved'
    if rid=='TX-BATH3':return 'Tones Emerald and Sandstone individually Wet Areas PASS, not FLOOR; selected Brizo SQUARE POINT if owner later chooses WALK-IN'
    if rid=='PH-BATH2':return 'Tones Sapphire and Sandstone individually Wet Areas PASS; keep TUB/no PAN'
    if rid=='PH-BATH4':return 'Source full Bone Ribbed and Clara Caviar individually wet unlisted FAIL; revised flat Bone and Soho Black individually wet PASS WALL/NICHE only'
    if rid=='TX-BATH4':return 'Original Caviar wet niche unlisted, revised Soho Ivory individually maker wet PASS, selected TUB no PAN'
    if rid in ('PH-PRIMARY','TX-PRIMARY'):return 'Source Reed/Ribbed wet wall unlisted; flat Bone/Clay wet permission nontransferable to dimensional relief, no extra Primary niche'
    if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2'):return 'Scheduled DRY decorative wall, wood floor; shower wet-wall and pan tests not applicable; verify vanity splash/cleaning and maker backsplash suitability'
    if rid.endswith('WC'):return 'No additional wall tile; inherited Primary LEVEL tested floor and no independent tile source'
    return 'Individual selected wet-wall maker letter still required'
def actual_pan(rid):
    if rid in ('PH-PRIMARY','TX-PRIMARY'):return 'LINEAR PAN: selected Brizo 48in BNX+BR73480; separate manufacturer rough/liner/bed, raw numeric wet DCOF'
    if rid=='PH-BATH4':return 'POINT PAN: selected Brizo BT062415-BNX 4in square; four-plane slope, membrane/flood, separate raw wet numerical DCOF'
    if rid in ('PH-BATH3','TX-BATH3'):return 'OWNER CONDITIONAL POINT PAN ONLY IF WALK-IN signed: PH Delta DT062412 Chrome/TX Brizo BT062415-BNX Black Onyx; never assume tub drain'
    if rid in ('PH-BATH2','TX-BATH2','TX-BATH4'):return 'TUB NO TILED PAN; actual selected Duravit tub flange and rough shall be resolved, LEVEL only'
    if rid.endswith('WC'):return 'NO PAN; primary level source already includes this WC, separate purchase prohibited'
    return 'DRY vanity with WOOD FLOOR: no tiled floor/PAN and no shower drain'
def source_alt(r):
    rid=r['room'];surf=r['surface'].lower()
    if rid in ('PH-BATH3','TX-BATH3'):
        if 'floor' in surf:return 'R014 conditional LEVEL: Daltile Prime Dynamic Beige RL21 12x24 Matte. If owner WALK-IN, separate RL21 1.5in Hex POINT PAN; exact suffix, raw numeric lab and real area TBD'
        if 'wall' in surf:return ('R014 PH proposed ELM Tones Sapphire 2x20 Glossy individual wet PASS replacing unlisted source Opal' if rid=='PH-BATH3' else 'R014 TX retain individually wet-listed Emerald 2x20; grout/orientation and field cuts remain provisional')
        return 'Original individually wet-listed Tones Sandstone niche, measure displaced field face and back/returns/sill before assigning net'
    if rid in ('PH-PRIMARY','TX-PRIMARY') and 'floor' in surf:return 'Revised LEVEL 12x24 and distinct POINT? NO - LINEAR 1.5in Hex PAN; Brizo 48in BNX+BR73480, maker raw tests and authorized rough TBD'
    if rid=='PH-BATH4' and 'floor' in surf:return 'LEVEL 12x24 and distinct 1.5in Hex four-plane SQUARE POINT PAN, measured split unknown; 35vs27-SF owner discrepancy'
    if rid in ('PH-BATH2','TX-BATH2','TX-BATH4') and 'floor' in surf:return 'REAL TUB NO TILED PAN; only LEVEL manufacturer exact wet numeric result, case coverage and tub flange section TBD'
    return 'Historic maker/size/finish retained as source only; conditional alternative actual authorizing SKU/finish, quantity and landed bid NULL'
def formula(rid,surf):
    if rid.endswith('WC'):return 'NO NEW ORDER; source gross included in primary ROOM floor'
    if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2'):return 'ceil(verified wall gross SF incl one approved waste factor / manufacturer documented actual carton SF), after full 1:1 mockup'
    if rid in ('PH-BATH3','TX-BATH3') and 'floor' in surf.lower():
        return 'If TUB: ceil(verified LEVEL gross SF / actual LEVEL carton SF), PAN N/A. If WALK-IN: independently ceil(verified LEVEL gross / LEVEL carton), ceil(verified POINT PAN gross / POINT PAN carton); compare original combined floor gross once.'
    if 'floor' in surf.lower():
        return 'ceil(verified net LEVEL gross incl original once waste / actual LEVEL carton SF); if walk-in/linear, separately verify PAN gross and calculate separate SKU cartons after measured net allocation'
    if 'accent' in surf.lower() or 'niche' in surf.lower():
        return 'ceil(verified niche back/returns/sill gross - double-counted source field face (if applicable), include waste exactly once / real maker carton SF)'
    return 'ceil(actual measured wall field gross less displaced niche opening, with one waste factor / actual maker carton coverage SF)'
rows=[]
fields=['room','original_smartsheet_row_id','source_surface','source_quantity_gross_sf_per_copy_15pct_included','arithmetic_source_net_sf_not_measured','old_material_usd_per_copy','two_copy_historic_material_usd',
        'historic_source_only_not_order','specific_program_classification','individual_wet_wall_niche_authorization','separate_level_vs_pan_drain_technical_gate',
        'conditional_good_better_best_source_direction','next_possible_order_formula_not_current_quantity',
        'actual_manufacturer_sku_finish','raw_numeric_level_wet_dcof_certificate','raw_numeric_pan_wet_dcof_certificate','verified_1529_measured_net_sf','pan_measured_net_sf','niche_aperture_back_returns_sill_net_sf','manufacturer_current_carton_coverage_sf','actual_cases_orderable','current_local_vendor_lot_eta_and_installed_bid','source_ref_or_vendor_quote_id','owner_finish_program_approved','gc_purchase_release']
for r in source:
    rid=r['room']; surf=r['surface'];rr=rooms[rid]
    row={k:'' for k in fields}
    row.update({'room':rid,'original_smartsheet_row_id':r['source_row_id'],
      'source_surface':surf,
      'source_quantity_gross_sf_per_copy_15pct_included':r['historic_gross_sf_per_copy_waste_15pct_included'],
      'arithmetic_source_net_sf_not_measured':r['arithmetic_unwasted_sf_NOT_measured'],
      'old_material_usd_per_copy':r['historic_material_usd_per_copy'],
      'two_copy_historic_material_usd':f"{Decimal(r['historic_material_usd_per_copy'])*2:.2f}" if r['historic_material_usd_per_copy'] else '',
      'historic_source_only_not_order':'TRUE',
      'specific_program_classification':use(rid),
      'individual_wet_wall_niche_authorization':wall_gate(rid),
      'separate_level_vs_pan_drain_technical_gate':actual_pan(rid),
      'conditional_good_better_best_source_direction':source_alt(r),
      'next_possible_order_formula_not_current_quantity':formula(rid,surf),
      'source_ref_or_vendor_quote_id':'2026-09-03 original row '+r['source_row_id']+' only, NOT current quote',
      'owner_finish_program_approved':'FALSE','gc_purchase_release':'FALSE'})
    rows.append(row)
assert len(rows)==27
assert sum(Decimal(x['two_copy_historic_material_usd']) for x in rows if x['two_copy_historic_material_usd'])==Decimal('23572.44')
assert sum(not x['two_copy_historic_material_usd'] for x in rows)==2  # historical Primary niche EXCLUDED/unpriced, not $0 paid

cut_fields=['room','wall','drawing_width_in_not_verified','drawing_tiled_height_in_not_verified','prior_nominal_source_face_sf','historical_balanced_tile_study','historical_full_tile_study','current_room_specific_movement_edge_niche_cut_resolver','actual_grout_and_caliber','actual_openings_valve_and_backing','actual_niche_wet_sill_and_4plane_drain_if_applicable','verified_1529_model_id','owner_program_or_finish_signed','architect_gc_shop_approved']
cuts=[]
for r in oldcuts:
    rid=r['room']; x={k:'' for k in cut_fields}
    x.update({'room':rid,'wall':r['wall'],
      'drawing_width_in_not_verified':r['provisional_source_width_in'],
      'drawing_tiled_height_in_not_verified':r['provisional_source_tiled_height_in'],
      'prior_nominal_source_face_sf':r['source_nominal_wall_face_sf_before_openings'],
      'historical_balanced_tile_study':r['centered_equal_cut_grid_study'],
      'historical_full_tile_study':r['single_end_full_tile_grid_study'],
      'current_room_specific_movement_edge_niche_cut_resolver':(
       ('Owner decide TUB/WALK-IN then locate valve, niche and square POINT drain only for walk-in; actual flange/curb and joint first. ' if rid in ('PH-BATH3','TX-BATH3') else '')+
       ('Wall faucet escutcheon needs fully flat support and actual relief end-cut rather than wet shower detail. ' if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2') else '')+
       'Architect/GC field verify W width, tile caliber and joint, centered end cuts >=3in where possible, niche subtract field opening once, returns/sill and external edge LF, movement joints at changes of plane, true valve rough and mirror/backing; field-approved section required.'),
      'verified_1529_model_id':'FALSE','owner_program_or_finish_signed':'FALSE','architect_gc_shop_approved':'FALSE'})
    cuts.append(x)
assert len(cuts)==25

OUT.mkdir(parents=True,exist_ok=False)
def writer(path,fields,rows):
    with (OUT/path).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
writer('R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv',fields,rows)
writer('R16_25_WALL_EDGE_MOVEMENT_AND_CUT_OPEN_HOLDS.csv',cut_fields,cuts)

book=['# R16 — thirteen-room owner/architect/GC design and procurement decision workbook','',
 '**NOT AN APPROVED SCHEDULE, QUOTE OR PROCUREMENT RELEASE.** Source-first additive improvement to signed R10–R15 packages, 2026-11-06. No actual native 1529 session verified: current process title 1527; all W-derived widths and allocations remain PROVISIONAL.',
 '',
 '## Release ladder: source -> branch -> measured work -> signed scope -> quote -> release','',
 '1. **Owner fixture/program choice:** PH3 and TX3 each owner-sign TUB or WALK-IN. PH3 basin, TX2 basin and TX Powder2 basin remain unselected. Preserve selected Primary 48-in Black Onyx LINEAR with separate BR73480 rough and NO niche; PH4 true selected Black Onyx 4-in square WALK-IN; PH2, TX2 and TX4 actual Duravit TUB (NO PAN). Never treat a selected shower drain as a tub waste.',
 '2. **Technical manufacturer evidence:** individual wet-wall/individual niche SKU/finish permissions and exact raw NUMERIC measured wet LEVEL and separately sloped PAN DCOF with lab citation. Flat Bone/Clay approval does not transfer to Reed/Ribbed. PH2 Tones Sapphire wet PASS; Opal PH3 wet unlisted; original PH4 107.2-SF/unit Bone Ribbed/Caviar individually wet unlisted. Glazzio >0.50 or >0.42, Emser >=0.60 and Daltile Target >=0.42 are bounds/targets, not raw individual lab numerical points.',
 '3. **Substrate/drain:** GC/manufacturer stamp Brizo 48in LINEAR solid-or-tile-in grate+BR73480 and selected PH4/TX3 Brizo 4in POINT or PH3 Delta DT062412 POINT with compatible membrane/channel/rough mortar build, shower PAN slopes, movement/curb/glass, flood test; TUB-only flange/overflow wall termination instead of tiled PAN. RL21 current maker 1.5in hex 5/16 vs old brochure 1/4in discrepancy remains assembly HOLD (7–18mm selected Brizo tile-in frame is not proof incompatibility); distinguish 12x24 LEVEL 3/8 from hex PAN and current grout page.',
 '4. **Field evidence:** verify actual 1529 building model session/title/path first; survey all 25 provisional wall elevations W widths and height, door/window, valve axes, niche aperture/back/returns/sill, floor LEVEL and PAN separately, original 15%-included gross, physical trim LF and movement joints. No phantom double WC floor; never count niche field face twice; never buy two complete floor quantities after program changes.',
 '5. **Financial evidence:** original 27 dated ELM source lines total USD 23,572.44 tile material across TWO PH and TWO TX with ORIGINAL waste already INCLUDED once. Separate manufacturer list/MSRP, verified public online retail, current exact Chicago supplier lot/stock/ETA, landed material-only quote, current complete installed GC labor/waterproofing and owner approved room cap; present null until independently evidenced. Current real carton yields/purchasable count = null, formula supplied only after net measured area and exact maker coverage.',
 '6. **Owner/GC final:** mockup sample kit 1:1 finish, grout/joint, wall wet permission, metal escutcheon/drain insert, niche and slip PAN; owner signs program/room cost/finish and GC separately signs shop/waterproof/quantities and purchasing. No sample orders, vendor contacts, owner approvals, invoices, or Revit/Smartsheet writes were performed.',
 '',
 '## Full 13-room GOOD / BETTER / BEST design directions (NOT graded or owner accepted)','',
 '| Room | GOOD: retain historic record safely | BETTER: bounded maker-backed design study | BEST: evidence-first installation / procurement release, not a new design commitment |',
 '|---|---|---|---|']
for rid,r in rooms.items():
    pr=use(rid)
    w=wall_gate(rid)
    dr=actual_pan(rid)
    good=f"Retain dated original row as provenance only; current {r['status']} / R{r['last_round']:03d}, owner unsigned."
    if rid=='PH-BATH3':better='Conditional source Opal wet FAIL -> individual wet Sapphire field + Sandstone niche; distinct RL21 LEVEL and conditional hex POINT PAN, with selected Chrome square drain if WALK-IN'
    elif rid=='TX-BATH3':better='Maintain wet Emerald/Sandstone and Black Onyx Brizo; change HNC prior concept to distinct RL21 LEVEL/conditional 1.5in hex POINT PAN, owner program unselected'
    elif rid in ('PH-PRIMARY','TX-PRIMARY'):better='Individual maker flat field wet listed; LEVEL/LINEAR small-hex split, Brizo 48-in rough and no new niche; cosmetic preference not technical approval'
    elif rid=='PH-BATH4':better='Flat Bone/Soho Black wet-listed alternative, separately tested LEVEL and 1.5in hex four-plane square POINT PAN, retain true WALK-IN'
    elif rid=='PH-BATH2':better='Wet-listed Sapphire and Sandstone unchanged; improve real Duravit tub flange 0.496-in nominal fit resolution and LEVEL raw DCOF'
    elif rid in ('TX-BATH2','TX-BATH4'):better='Retain actual Duravit TUB and selected Hansgrohe Chrome/Matte White, NO PAN; individualized maker wet field/LEVEL and basin decision if TX2'
    elif rid.endswith('WC'):better='Keep shared Primary LEVEL material and no independent carton purchase; coordinate true net/threshold'
    else:better='Retain dry vanity wall accepted/conditional owner-unsigned palette with exact faucet/basin/edge/joint and 1:1 sample; wood floor no tiled shower PAN'
    best='Exact signed owner/GC program+finish and verified model, wet maker letter and required raw measured FLOOR/PAN test, approved drain/tub shop, independent current Chicago installed quote, permitted measured takeoff and carton yield; no purchase until all PASS.'
    book.append(f'| {rid} | {good} | {better} | {best} |')
book.extend(['',
 '## Two major owner-directed Bath3 decisions with geometry and 1:1 render/sample brief','',
 '| Decision | PH Bath3 | TX Bath3 |',
 '|---|---|---|',
 '| SOURCE vs selected plumbing | Drawing 5.00ft x2.33ft tub alcove; selected Delta DT062412 Chrome 4-in SQUARE POINT shower drain and Hansgrohe Chrome; PH basin unselected | Drawing 5.10ft x2.60ft tub alcove; selected Brizo BT062415-BNX Brilliance Black Onyx square POINT and Roccesco; owner program unselected |',
 '| If owner signs TUB | Bathtub, waste/overflow/rough and flange all owner and architect selected LATER. LEVEL floor only, PAN N/A. Never use shower point drain as tub waste | Same, but selected Brizo shower plumbing must be reconciled by signed owner/architect before tub purchase |',
 '| If owner signs WALK-IN | Retain Delta Chrome POINT; actual four-plane slope with maker written pan/rough and small-format RAW wet-test, remeasure LEVEL/PAN | Retain Brizo Black Onyx POINT and waterproofing shop; separately tested small-format PAN and net level, no imagined tub |',
 '| Maker wall contrast | Historical Opal individually wet-unlisted; proposed Sapphire individually wet PASS, Sandstone niche PASS; 2x20 mockup next to Chrome | Emerald and Sandstone individually wet-listed, 2x20 grout/orientation and niche edge against Black Onyx |',
 '| Room source/quote | Original $930.42 per copy including 15%-loaded gross and niche once, not substitute quote | Original $958.88 per copy including 15%-loaded gross and niche once, not substitute quote |',
 '| Render + sample kit | Show dual alternative TUB vs WALK-IN without choosing owner program: two 2x20 wall palettes, 12x24 LEVEL, 1.5in POINT pan only walk-in, actual chrome/glass once measured | Two explicit owner program variants with Emerald 2x20, warm Sandstone niche, Black Onyx, conditional POINT PAN and no invented tub |',
 '',
 '## Market and trade sourcing limits','',
 'Four listing entries 405 W Armitage OT01–OT04 are ONE building design precedent. Existing 14 listings are NINE independent buildings; no authenticated comp bath tile photos, do not infer unseen specific designs. Old Town listings sold/listed within 24 months primary; Lincoln Park/Gold Coast secondary and labeled. Price anchors PH ~$2.8M and TX ~$2.7M, range $2.4–$3.2M. Verified maker public catalog suitability and online retail are NOT an actual Chicago supplier inventory/lot/installed quote.',
 '',
 '## Required attachments/checklist before buyer signoff','',
 '- Level maker-specific exact raw numeric wet DCOF; independent PAN maker-specific exact numeric wet DCOF if shower; individual wall/niche maker listing, physical calibration, available exact SKU/finish.',
 '- 1:1 wet-wall layout with grout/chip/edge, selected plumbing escutcheon and drain study, three-dimensional shower slope or true tub flange, movement joint positions and real measured 1529 W/opening/valve/threshold schedules.',
 '- Actual supplier carton SF and full-case formulas from R16_27 source reconciliation, no added automatic source 15% waste; current Chicago dated landed and full installed bid, lead/stock/lot, owner-signed cap and GC approval.',
 '',
 'Read the source-preserving R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv and R16_25_WALL_EDGE_MOVEMENT_AND_CUT_OPEN_HOLDS.csv together with R15 signed 65 trade actions. Unknown numeric requirements remain blank/null rather than inferred. Source original 2026-09-03 and v4 schedule, 2026-08-26 fixture v3.2 and individual current maker pages are distinct levels of commercial authority.'])
bookfile=OUT/'R16_13_ROOM_DESIGN_CONSTRUCTION_PROCUREMENT_BOOK.md'
bookfile.write_text('\n'.join(book)+'\n',encoding='utf-8')
guide=OUT/'START_HERE_R16.md'
guide.write_text('# R16 decision and procurement hold index\n\nStart with R16_13_ROOM_DESIGN_CONSTRUCTION_PROCUREMENT_BOOK.md for 13-room GOOD/BETTER/BEST and owner Bath3 tub vs point-drain branches. R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv holds every source row and formula, and R16_25_WALL_EDGE_MOVEMENT_AND_CUT_OPEN_HOLDS.csv holds provisional existing wall studies without inventing actual 1529 geometry. R15 signed 65 trade actions still govern trade owners. NO OWNER APPROVAL, REVISED QUOTE OR PURCHASE AUTHORIZATION.\n',encoding='utf-8')
files=[bookfile,OUT/'R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv',
       OUT/'R16_25_WALL_EDGE_MOVEMENT_AND_CUT_OPEN_HOLDS.csv',guide]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'date':'2026-11-06','kind':'additive evidence driven 13-room owner/GC 16',
 'rooms':13,'original_supplier_material_rows':27,'original_wall_studies':25,
 'prior_trade_action_count':65,'original_material_two_PH_two_TX_usd':23572.44,'original_gross_waste_included_once':True,
 'r15_manifest_sha256':sha(r15/'MANIFEST.json'),
 'r014_source_sha256':sha(R/'state/ROUND014_SUBMISSION.json'),
 'R014_score':None,'actual_1529_model_verified':False,'owner_approval':False,'procurement_release':False,
 'outputs':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in files}}
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
assert len(manifest['outputs'])==4
print('PASS additive R16 4 SHA-signed outputs + manifest, 13 room GOOD/BETTER/BEST, 27 original source conditional carton rows, 25 preliminary wall cuts, prior 65 actions retained, 23572.44 material, no owner/GC release')
