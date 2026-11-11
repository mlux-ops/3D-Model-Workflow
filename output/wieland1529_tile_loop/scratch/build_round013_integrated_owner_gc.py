"""New R13 integrated work-product build; preserve signed R10/R11/R12 historical artifacts.
13 room decision packets + 65 cross-trade actions + 25 dimensioned cut alternatives,
27 original quote/purchasing reconciliation and scored R012 evidence, with SHA manifest.
"""
from pathlib import Path
from decimal import Decimal
import csv,json,hashlib,math
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r13'
assert not (O/'MANIFEST.json').exists(),'R13 signed output already exists; do not overwrite'
O.mkdir(parents=True,exist_ok=True)
state=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))
s12=json.loads((R/'state/ROUND012_SCORING.json').read_text(encoding='utf-8'))
s11=json.loads((R/'state/ROUND011_SCORING.json').read_text(encoding='utf-8'))
source=list(csv.DictReader((R/'deliverables/integrated-r10/R10_27_ROW_BID_COMPARISON_AND_NON_ORDERABLE_GAPS.csv').open(encoding='utf-8-sig')))
holds=list(csv.DictReader((R/'deliverables/integrated-r10/R10_65_WORK_ITEM_OWNER_GC_EVIDENCE_CLOSURE.csv').open(encoding='utf-8-sig')))
walls=list(csv.DictReader((R/'deliverables/integrated-r10/R10_SOURCE_WALL_CUT_AND_TRIM_CHECKS.csv').open(encoding='utf-8-sig')))
assert len(state['rooms'])==13 and len(source)==27 and len(holds)==65 and len(walls)==25
assert set(s12['room_results'])=={'TX-PRIMARY','TX-BATH2','TX-BATH4'}
roommap={x['id']:x for x in state['rooms']}
assert len(roommap)==13
specific={
 'PH-PRIMARY':('selected Brizo BT0734816-BNX 48-in Black Onyx LINEAR; required BR73480 separate rough; separate selected Duravit tub; NO PRIMARY NICHE','flat Cortar Bone wet-listed field vs unlisted Reed relief; new LEVEL candidate floor exact raw test and pan separate Prime RL21 only conditional','Obtain one full-scale linear tile insert/frame section from maker and installer: adjustable 7–18mm vs Prime RL21 6.35mm nominal mosaic; drain/membrane/pan/water test; include WC floor in same level takeoff'),
 'PH-BATH2':('Duravit tub + Matte White Hansgrohe; NO tiled shower pan','ELM Tones Sapphire 2x20 Glossy individual Wet Areas PASS; proposed HNC6615 level and source Grey Soft both need exact numerical wet-floor report','Tub-flange-to-shower-wall waterproofing, niche pitch and opening deduction, level floor threshold; preserve approved Sapphire wall rating and no new pan'),
 'PH-BATH3':('selected Delta DT062412 Chrome 4-in SQUARE shower point drain conflicts with drawing tub alcove; basin UNSELECTED','Original Tones Opal wet use UNVERIFIED, Sandstone revised wall maker wet PASS; LEVEL and conditional walk-in 2x2 point PAN exact numeric lab FAIL','Owner chooses tub or walk-in; if tub, obtain an actually selected tub waste/overflow (do NOT reuse Delta shower drain); if walk-in, measure point pan, slope, curb/glass and rough'),
 'PH-BATH4':('actual WALK-IN, selected Brizo BT062415-BNX Black Onyx SQUARE POINT; NOT tub','source Bone Ribbed and Clara Caviar niche wet unlisted; flat Bone/Soho wet alternative conditional; LEVEL and 2x2 point PAN exact lab FAIL','Survey 35 vs 27 SF floor; separate level and pan gross with 15% once; Soft vs Anti-Slip conflict; inspect 107.2 SF/unit x2=214.4 SF Ribbed original source versus supplier GRAND TOTAL (not payable shortage)'),
 'PH-POWDER':('dry Earth Lines v4 source board-preferred 3.69, not owner signed','dry vanity wall; NO floor/shower raw wet DCOF gate; grout/edge and fixture sampling pending','Full W1 elevation with actual mirror, sconce, vanity top and fixture centers; measure two vertical exposed edge lengths before trim sticks'),
 'PH-WC':('PH Primary shared WC FLOOR only; original WC material subtotal $0','same tested Primary LEVEL tile product, no niche/pan, no standalone floor order','Survey WC shared threshold and allocate physical net into Primary floor once; do not duplicate 15 SF from source'),
 'TX-PRIMARY':('selected Brizo BT0734816-BNX 48-in Black Onyx LINEAR; BR73480 separate rough; NO PRIMARY NICHE; shared TX WC LEVEL floor','Round012 revised C flat Clay wet PASS / Emser F08CAPITR1224M LEVEL + Prime RL21 LINEAR mosaic pan; source B Ribbed wet FAIL','Separate measured WC/LEVEL/PAN polygon with one waste, resolve Brizo 7–18mm frame versus Prime 6.35mm mosaic nominal build, liner/membrane/test and true local supplier lot; no 125% cap guess'),
 'TX-BATH2':('selected Duravit 59-in tub + Hansgrohe Chrome; basin OWNER UNSELECTED; NO tiled shower pan','Round012 revised A Copper/Sandstone individually Wet Areas PASS and Emser Trosa 12x24 LEVEL raw lab FAIL; original Clay Soft also FAIL','62.484-in source W1 2x20 full modules + 2x11.242-in balanced theoretical ends before grout; measure tub edge, niche field and true flush floor; test actual Emser carton cost'),
 'TX-BATH3':('drawing tub alcove versus selected Brizo BT062415-BNX Black Onyx SQUARE shower POINT; owner tub vs walk-in UNSELECTED','Emerald/Sandstone individual Wet Areas PASS, HNC6615 LEVEL and HNC6715 POINT PAN conditional raw numeric wet lab FAIL','Owner tub/walk-in program election; 1.60-in 2x20 vertical edge mockup conditional and drain-vs-waste choice; do not select tub or reinterpret Brizo point as tub waste'),
 'TX-BATH4':('actual Duravit 59-in tub + Hansgrohe Matte White; NO tiled pan','Round012 revised B flat Charcoal wet PASS / Soho Ivory individual Wet Areas PASS niche / Emser Trosa LEVEL raw lab FAIL; original Caviar wet listing FAIL','Actual niche face displacement, back/returns/sill, trim and tub flange; original 8.63 SF gross is only an estimate, cannot add same tile face twice'),
 'TX-POWDER':('dry Haze Camel/Wheat exactly 70:30 board-preferred 3.67, not owner-approved','dry vanity only, no wet-pan/slip gate; no unapproved palette ratio change','Full-scale mixed tile 70:30 distribution grid, shade lot, grout/trim, and lighting/vanity mirror datum verification'),
 'TX-POWDER2':('dry Indigo Edge 6x6 board-retained 3.23; basin OWNER UNSELECTED','dry vanity relief only, no floor DCOF gate; retain source quoted 6x6 until signed owner selection','Coordinate sink/faucet, backsplash outlet, mirror and W1 6in true grout module; provisional trim LF null'),
 'TX-WC':('TX Primary shared WC FLOOR only; zero separately quoted material','same tested Primary LEVEL tile, not an added room or new source invoice','Survey 14 SF provisional shared WC floor in Primary 116.1 SF source gross, one waste factor and no double count')
}
assert set(specific)==set(roommap)
def fmt(x):
 if x is None:return 'null'
 return str(x)
lines=['# 1529 Wieland — R13 integrated 13-room OWNER + GC decision and shop coordination',
       '', '**Release classification:** This is an OWNER/GC study package, not an accepted manufacturer/shop submittal, approved sample, site-measured takeoff, signed material order or construction instruction. Previous R10 nine, R11 one and R12 six signed packages remain preserved as audit source; v4 original and scored board outcomes govern.','',
       '**Bidding basis:** Historical 2026-09-03 Smartsheet material-only four-unit line arithmetic $23,572.44 across PH/TX; 27 original line items with 15% waste embedded ONCE. Alternative current prices/installed costs/room material caps/local inventory/ETA = null. No source waste double-count, shared WC, duplicate niche face, trim, sample or shower-pan addition.','',
       '## Four-seat completed score decisions — no champion release','',
       '| Focus | Historic | Revised | Improvement | Revised min critic | Formal outcome |',
       '|---|---:|---:|---:|---:|---|']
for rid in ('TX-PRIMARY','TX-BATH2','TX-BATH4'):
 r=s12['room_results'][rid];a=r['candidates'][r['historical_letter']];b=r['candidates'][r['revised_letter']]
 lines.append('| %s | %.2f | %.2f | %+.2f | %.1f | **BLOCKED** — raw wet lab and min/threshold failures |'%(rid,a['weighted_score'],b['weighted_score'],r['challenger_margin'],b['minimum_critic_score']))
lines+=['','R011 PH Bath3 and TX Bath3 both also independently BLOCKED; no owner approval or procurement release. Flat Clay/Charcoal, Copper/Sandstone and Soho Ivory wall wet listings do not automatically clear a bath LEVEL floor or POINT/LINEAR PAN.','',
        '## Room-by-room source-specific decision, contractor detail and sign-off sheet','']
for room in state['rooms']:
 rid=room['id'];fixture,material,coord=specific[rid]
 lines+=['','### '+rid+' — '+room['status'].upper()+' (owner approval: '+str(room['owner_status'])+')',
         '', '**GOOD (historical / previously held):** Preserve actual v4/Smartsheet named rows, selected plumbing and any previously board-approved colors; no unqualified acceptance for BLOCKED rooms.',
         '**BETTER (conditional constructible design study):** '+material+'.',
         '**BEST (release only after evidence and signature):** '+coord+'.',
         '**Selected fixtures/program unchanged:** '+fixture+'.',
         '**Original exact material-only basis:** $%.2f per room copy × %d copies = $%.2f historic. No alternate maker order value or installed budget established.'%
         (room['carried_quote_material_subtotal_usd_per_unit'],room['unit_count'],room['carried_quote_material_subtotal_usd_per_unit']*room['unit_count']),
         '**Sample kit / render intent (none ordered/generated):** Side-by-side actual tile and grout/edge physical mock-up under selected fixture finish and room lighting; frontal W1–W3 field elevation with actual geometry gaps dashed; 45° oblique showing specified tub or shower only; scaled drain/liner/threshold/niche cutaway after owner program and raw tests. Distinguish full-size physical sample and photo-real marketing render from contract/shop documents.',
         '**Owner signature & GC release:** Tile scheme [ ] / grout [ ] / niche [ ] / program [ ] / raw LEVEL [ ] / pan if any [ ] / measured elevations [ ] / current installed budget [ ] / shade/lot/lead [ ] / owner signed [ ] / GC approved [ ] / materials ordered [ ] — **ALL PENDING**.']
lines+=['','## Original scope and substitution interfaces','',
        'All W1–W3 dimensions are derived from the prior 1529 drawing/export, NOT a confirmed 1529 live Revit process/document/session/title/path. The last observed native file is 1527. True plumbing rough offsets, niche/field displacement, substrate thickness, actual tile caliber, grout and exposed trim lengths must be surveyed before any purchase. Point showers require manufacturer-approved multi-plane pan grading and actual matched square drain; selected 48-in LINEAR primaries require separate verified sloped-pan/rough and tile-in insert.',
        "Brizo BT0734816-BNX/BR73480 exact manufacturer's reversible 48-in linear frame accepts tile 7–18mm. Proposed Daltile Prime RL21 family mosaic is nominal 1/4in=6.35mm, **0.65mm nominal tile/frame difference**; do not call incompatible or create an unapproved shim. Require actual carrier/adhesive/waterproof buildup/grate section and signed installer/manufacturer assembly. $825/$684 Brizo public list is not an SHB quote.",'',
        'PH4 discrepancy: 35 SF owner versus 27 SF older, Soft versus Anti-Slip, original full Bone Ribbed wet wall and Caviar wet niche unlisted; **107.2 SF/unit × two units = 214.4 SF** historical itemization potentially missing from old supplier GRAND TOTAL, not verified receivable/payable shortage. Never increase historic $23,572.44 nominal source subtotal speculatively.',
        'No owner-only tub/sink decisions silently filled. PH3 Delta DT062412 and TX3 Brizo BT062415-BNX point-drain vs tub-alcove conflicts remain owner-only. No extra primary niches or excluded discussion topics. PH2 and TX2/TX4 actual tubs have NO tiled shower pan. ELM Sapphire 2x20 Glossy maker Wet Areas PASS for wet wall, separate floor raw exact test still FAIL.','']
(O/'R13_OWNER_13_ROOM_DECISION_AND_COORDINATED_CONSTRUCTION_BOOK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
# Extend original 65 actionable closures, preserving all source rows and resolving responsibility by gate.
updated=[]
for row in holds:
 rid=row['room'];g=row['gate_group'];room=roommap[rid]
 if g=='manufacturer_spec':
  extra='Obtain exact individual tile SKU/finish wet-area letter and numbered raw wet ANSI laboratory reading for every true wet LEVEL or PAN. Dry powder vanity uses N/A.'
  owner='tile supplier/manufacturer written technical submittal + architect/GC'
 elif g=='dimensions_and_edge':
  extra='GC verify corrected 1529 document/title/path/session then field-measure W1-W3, openings, actual tile caliber/grout, niche face/back/returns, penetrations, trim exposed LF and movement joints; original datum provisional.'
  owner='architect + GC superintendent + tile installer'
 elif g=='floor_pan_and_drain':
  extra='Establish owner room program first; tub rooms pan N/A; Brizo LINEAR primaries require BR73480 and complete 7-18mm frame/6.35mm nominal RL21 carrier build; square POINT pan needs exact 2x2 test + slope/membrane/curb/threshold/flood. Shared WCs included in primaries.'
  owner='licensed plumbing installer + architect + tile/waterproof installer'
 elif g=='owner_approval':
  extra='Owner signs room program, actual fixture selections (PH3/TX3 tub-v-walkin, PH3/TX2/TX Powder2 basins) and sample/visible finish; no design-agent selection.'
  owner='owner + architect'
 else:
  extra='Verify actual lot/carton yield, exact current Chicago merchant dated landed offer, sample lead, installer labor/tax/freight, two-copy net/gross and owner cap; never mistake dated itemized Smartsheet rates or list price as purchase cost.'
  owner='procurement/GC + distributor (no contact by this agent)'
 if rid in s12['room_results']:
  z=s12['room_results'][rid];sc='Round012 scored BLOCKED %.2f/%.2f'%(z['candidates'][z['historical_letter']]['weighted_score'],z['candidates'][z['revised_letter']]['weighted_score'])
 elif rid in s11['room_results']:sc='Round011 scored BLOCKED'
 else:sc='Current '+room['status']+'; owner not signed'
 updated.append({'room':rid,'group':g,'original_r10_evidence':row['current_evidence_state'],'source_quote_usd_per_copy_2026_09_03':row['source_quote_usd_per_copy'],
                 'latest_board_and_source':sc,'responsible_trade':owner,'measurable_next_closure':extra,'manufacturer_raw_lab_certificate_ref':None,
                 'verified_1529_session_title_path':None,'installed_quote_id':None,'owner_rejected_or_approved':None,'exact_gc_approval':False,'owner_approval':False,'purchase_release':False})
assert len(updated)==65 and all(x['purchase_release'] is False for x in updated)
def writecsv(name,records):
 f=O/name
 with f.open('w',encoding='utf-8-sig',newline='') as h:
  writer=csv.DictWriter(h,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
writecsv('R13_65_TRADE_OWNED_EVIDENCE_AND_RELEASE_ACTIONS.csv',updated)
# 25 derived shop-cut alternatives with field controls and actual geometry explicitly unknown.
layout=[]
for x in walls:
 width=float(x['source_width_in']);height=float(x['source_tiled_height_in'])
 module=float(x['nominal_module_in']) if x['nominal_module_in'] else None
 if module:
  # No assumptions about actual caliber or grout. Grid A: symmetric end cuts; B: full tile on end / return.
  count=int(width//module)
  symmetric=round((width-count*module)/2,3)
  fullfirst=round(width-count*module,3)
  # When minimum end cut <3in for larger format, suggest swapping a full module into balanced adjacent cuts.
  if symmetric<3 and count>=1:count-=1;symmetric=round((width-count*module)/2,3)
  sym_label=f'{count} full {module:g}in modules + 2x{symmetric:g}in nominal balanced ends'
  full_label=f'{int(width//module)} full {module:g}in modules + one nominal {fullfirst:g}in end'
 else:sym_label='material-dependent; set actual shade/caliber/module before layout';full_label='not measured'
 risk='MOCKUP: focal <3in strip if true caliber/joint produces one' if module and module>=24 else 'REVIEW small-format cut proportions, opening and grout rhythm'
 layout.append({'room':x['room'],'wall':x['wall'],'provisional_source_width_in':width,'provisional_source_tiled_height_in':height,
                'source_nominal_wall_face_sf_before_openings':x['source_face_sf_no_waste'],'provisional_tile_module_in':module,
                'centered_equal_cut_grid_study':sym_label,'single_end_full_tile_grid_study':full_label,'design_risk':risk,
                'true_tile_caliber_in':None,'true_joint_width_in':None,'verified_wall_openings_niche':None,
                'actual_valve_rough_coordinates':None,'actual_trim_exposed_edge_lf':None,
                'movement_joint_selection':None,'measured_1529_model':False,'gc_layout_approved':False})
writecsv('R13_25_WALL_OPTION_A_B_FIELD_CUT_AND_EDGE_LAYOUTS.csv',layout)
# Exact current orderable unit is NULL until area, pack and raw approval all pass; not the historical material quote.
units=[]
for room in state['rooms']:
 rid=room['id']
 gross=sum((x['qty_sf_per_unit'] or 0) for x in room['carried_tile_rows'] if x['surface'] not in ('accent',))
 items=[(x['surface'],x['smartsheet_row_id'],x['qty_sf_per_unit'],x['extended_quote_cost_usd_per_unit']) for x in room['carried_tile_rows']]
 for surface,rowid,gross_sf,old_cost in items:
  units.append({'room':rid,'copies':room['unit_count'],'source_row_id':rowid,'surface':surface,
                'historic_gross_sf_per_copy_waste_15pct_included':gross_sf,
                'arithmetic_unwasted_sf_NOT_measured':round(gross_sf/1.15,4) if gross_sf is not None else None,
                'historic_material_usd_per_copy':old_cost,'historical_only_not_current_bid':True,
                'alternate_raw_sku_finish':None,'verified_net_level_sf':None,'verified_net_pan_sf':None,
                'niche_displaced_field_face_sf':None,'actual_niche_back_and_returns_sf':None,
                'verified_current_box_coverage_sf':None,'orderable_cases':None,'trim_lf':None,'installed_total':None,
                'current_local_supplier_price_lot_eta':None,'owner_release':False})
assert len(units)==27
writecsv('R13_27_SOURCE_TO_CONDITIONAL_PURCHASE_RECONCILIATION.csv',units)
index=['# Round013 owner / GC handoff — five coordinated signed outputs','',
       'This is the **new integrated R13** owner coordination baseline; previous R10, R11 and R12 frozen signed files are independent historical snapshots. Consult the six-file R12 MANIFEST for the 27 exact maker test matrix and per-room owner-to-release status.','',
       '**Immediate decision sequence:** owner choose PH3/TX3 tub-vs-walkin and PH3/TX2/TX Powder2 basins; architect/GC prove correct 1529 document geometry; maker provide exact per-finish wet and raw FLOOR/PAN test; GC demonstrate approved drain/liner/frame/threshold; procurement reconcile current exact lot + installed quote with owner cap; owner signs. No authorizations supplied.','',
       'R013 includes: room-level GOOD/BETTER/BEST and owner signatures; 65 trade-assigned evidence closures; 25 real nominal A/B wall grid concepts with dimension unknowns explicitly null; 27 separate original quoted line and conditional purchase reconciliation. See each file below.']
(O/'START_HERE_R13_OWNER_GC.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
names=sorted(f for f in O.glob('*') if f.is_file() and f.name!='MANIFEST.json')
manifest={'as_of':'2026-11-06','round':'013 owner/GC integrated package following scored R012','rooms':13,'source_rows':27,'trade_closure_rows':65,
          'wall_layout_studies':25,'historic_four_unit_material_usd':float(round(sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit']))*Decimal(str(r['unit_count'])) for r in state['rooms']),2)),
          'historic_waste_embedded_once':True,'owner_approved':False,'procurement_release':False,
          'scored_R012_sha256':hashlib.sha256((R/'state/ROUND012_SCORING.json').read_bytes()).hexdigest(),
          'R12_prior_manifest_sha256':hashlib.sha256((R/'deliverables/integrated-r12/MANIFEST.json').read_bytes()).hexdigest(),'outputs':{}}
assert manifest['historic_four_unit_material_usd']==23572.44
for f in names:
 b=f.read_bytes();manifest['outputs'][f.name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
(O/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R13',len(names),'signed outputs, 13 rooms, 65 trade actions, 25 wall A/B layouts, 27 historic rows,',manifest['historic_four_unit_material_usd'],'four unit material; no release')
