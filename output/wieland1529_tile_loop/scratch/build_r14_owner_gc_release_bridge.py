"""One-time SHA-signed all-13-room release interface addendum. Not a purchase order."""
from pathlib import Path
import csv,hashlib,json,io

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/integrated-r14'
assert not OUT.exists(), 'Do not regenerate or overwrite a signed snapshot'
rooms=json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert len(rooms)==13
by={r['id']:r for r in rooms}
assert len(by)==13

# Each owner/architect/installer row is independent of original R013 blind candidate identity.
actions={
 'PH-PRIMARY':('Selected Brizo Black Onyx 48-in LINEAR BT0734816-BNX + BR73480; separate Duravit tub, NO niche; PH WC floor within Primary gross',
               'Confirm selected Brizo solid-grate OR tile-in orientation after manufacturer-approved rough/flange/liner section; actual LEVEL vs LINEAR PAN area and two exact measured wet DCOF tests; ceiling mounting and final grout',
               'Owner sample color/grout + architect finish section + GC Brizo manufacturer waterproof/slope and exact LEVEL/PAN lab tests; no new niche'),
 'PH-BATH2':('Selected Duravit 700332000000090 59-in actual TUB with Hansgrohe MATTE WHITE; Tones Sapphire wet wall and Sandstone wet niche individually maker Wet Areas YES; NO PAN',
             'Nominal tub back 59.496-in vs nominal tub 59-in = 0.496-in TOTAL difference before backer/tile/flange and tolerance: verify real rough cavity, framing and actual tub installation envelope; exact LEVEL floor raw wet test',
             'Owner Matte White/Sapphire/Sandstone/floor sample + GC actual tub rough-and-finish dimension sketch, flange/niche waterproof section and floor lab report'),
 'PH-BATH3':('Actual program owner UNRESOLVED: tub alcove on drawing vs selected Delta DT062412 Chrome SQUARE POINT shower drain; basin UNSELECTED',
             'Owner must explicitly choose tub vs walk-in before drain/slope/liner/field-order scope; verify basin separately; Tones Opal individual wet approval missing; LEVEL and any PAN raw DCOF',
             'Owner tub-or-walk-in signature and basin selection; architect updated matching actual 1529 layout; manufacturer wet/level/pan and Delta install approvals'),
 'PH-BATH4':('Actual WALK-IN, Brizo Brilliance Black Onyx BT062415-BNX 4-in SQUARE POINT, NOT tub',
             'Resolve owner 35-SF vs older 27-SF source and 40.2-gross-SF pooled LEVEL+POINT PAN; Cortar Bone Ribbed/Clara Caviar wet listing FAIL; Soft-vs-AntiSlip quoted finish; audit 214.4-SF two-copy Ribbed vendor-total itemization without claiming payable shortage',
             'Owner material/finish/niche sample, manufacturer flat-vs-relief wet approval and exact two raw DCOF certificates, GC square-point four-plane membrane/rough layout, vendor dated itemization clarification'),
 'PH-POWDER':('Earth Lines conditional board direction, NOT owner-signed',
              'Resolve selected product exact finish/size/dry-vs-wet location and level-floor raw DCOF if used as bath floor; verify compact powder cuts/grout, all current quotes',
              'Owner Earth Lines sample/signature; architect dimensions and trim; vendor current lot and manufacturer floor certificate if applicable'),
 'PH-WC':('Shared PH WC inherits PH-PRIMARY LEVEL floor and is NOT independent tile purchase',
           'Verify the actual WC boundary is included within PH Primary single gross floor source; avoid duplicate materials/cartons; check level wet-slip certificate and threshold movement',
           'GC field measured WC-to-Primary area partition and shared floor order reconciliation only; NO separate WC quote or new niche'),
 'TX-PRIMARY':('Selected Brizo Black Onyx 48-in LINEAR drain, separately required BR73480 rough, no Primary niche; shared TX WC original gross included',
               'Obtain exact maker wet permission for Clay Ribbed vs flat variant, separate LEVEL and LINEAR PAN measured raw numerical wet DCOF; Prime RL21 insert/grate nominal thickness/version vs actual manufacturer approved assembly; verify net pan/field',
               'GC Brizo/liner/slope section with sample tile stack; owner finish mockup; source-specific manufacturer wet and FLOOR/PAN lab report; signed Chicago bid'),
 'TX-BATH2':('Selected Duravit TUB and Hansgrohe CHROME; basin OWNER UNSELECTED; NO tiled shower PAN',
             'Resolve basin only with owner, Cortar Clay Soft vs Emser exact LEVEL floor measured raw wet DCOF, tub edge/flange and source gross net/niche if any',
             'Owner basin selection and floor sample; GC tub waterproof/threshold detail; maker floor lab and current exact lot quote'),
 'TX-BATH3':('Owner UNRESOLVED tub-alcove drawing versus selected Brizo Black Onyx BT062415-BNX SQUARE POINT shower drain/controls; no tub SKU selection',
             'Do not assign point drain as tub waste or authorize walk-in; owner must decide program; verify matched controls, raw LEVEL/PAN DCOF when applicable and true 1529 dimensions',
             'Owner explicit tub-or-walk-in program and basin where required; architect updated complete drainage plan and GC compatible rough/liner section'),
 'TX-BATH4':('Selected Duravit TUB with Hansgrohe MATTE WHITE; NO tiled shower PAN',
             'Original Cortar Bone Soft level vs revised Emser Capisco Trosa F08CAPITR1224M LEVEL floor separate maker raw numeric wet DCOF; individual Soho Ivory niche wet PASS vs original Caviar unlisted; tub flange and net niche surfaces',
             'Owner floor/niche/Matte White sample, GC tub waterproofing/edge and niche sill, manufacturer individual wet and exact level slip report'),
 'TX-POWDER':('70:30 Haze Camel/Wheat board direction accepted, NOT signed owner approval',
              'Verify true 70:30 area assignment, actual tile wet/dry applications, wall edge and floor slip test if present; source quote and real lot/cap unresolved',
              'Owner sample and signature, architect side elevations, GC quantified install scope, current exact vendor landed quote'),
 'TX-POWDER2':('Indigo Edge 6x6 conditional design retained; basin OWNER UNSELECTED',
               'Owner must select basin before accurate elevation/spout/niche/clearance; verify wall field/color/grout and wet/level slip where applicable; no invented basin',
               'Owner basin SKU and Indigo Edge sample, architect measured backsplash/trim section, installer quantity/cost and vendor stock evidence'),
 'TX-WC':('Shared TX WC inherits TX-PRIMARY LEVEL floor, no separate tile purchase',
           'Verify measured shared WC boundary within Primary source 15%-gross floor allocation, finish/threshold continuity and individual LEVEL-floor raw wet DCOF; avoid double count',
           'GC field measured WC-to-Primary partition and matching one floor order only; no extra WC vendor line'),
}
assert set(actions)==set(by)

columns=['room','room_status','last_board_round','copies','original_material_only_usd_per_copy','original_two_copy_material_usd','selected_plumbing_program_or_board_direction','source_specific_open_releases','required_owner_architect_gc_manufacturer_or_vendor_evidence','verified_native_1529_model','measured_level_area_sf','measured_shower_pan_area_sf','individual_exact_numeric_wet_dcof_floor','individual_exact_numeric_wet_dcof_pan','current_exact_chicago_lot_price_eta','owner_approval','gc_procurement_release']
rows=[]
for rid in [r['id'] for r in rooms]:
 r=by[rid]
 f=actions[rid]
 assert r['unit_count']==2
 rows.append({
  'room':rid,'room_status':r['status'],'last_board_round':r['last_round'],
  'copies':2,'original_material_only_usd_per_copy':f"{r['carried_quote_material_subtotal_usd_per_unit']:.2f}",
  'original_two_copy_material_usd':f"{r['carried_quote_material_subtotal_usd_per_unit']*2:.2f}",
  'selected_plumbing_program_or_board_direction':f[0],
  'source_specific_open_releases':f[1],
  'required_owner_architect_gc_manufacturer_or_vendor_evidence':f[2],
  'verified_native_1529_model':'FALSE',
  'measured_level_area_sf':'','measured_shower_pan_area_sf':'',
  'individual_exact_numeric_wet_dcof_floor':'',
  'individual_exact_numeric_wet_dcof_pan':'',
  'current_exact_chicago_lot_price_eta':'',
  'owner_approval':'FALSE','gc_procurement_release':'FALSE'
 })
assert round(sum(float(x['original_two_copy_material_usd']) for x in rows),2)==23572.44

OUT.mkdir(parents=True,exist_ok=False)
target=OUT/'R14_13_ROOM_EXACT_SOURCE_AND_OWNER_GC_RELEASE_BRIDGE.csv'
with target.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=columns)
 w.writeheader(); w.writerows(rows)

lines=['# R14 — owner/architect/GC release bridge for all 13 bathrooms / WCs','',
       '**Release classification: NOT FOR PURCHASE, NOT OWNER APPROVED.** November 6, 2026. This document adds specific current technical decisions to the signed integrated R13 package without changing or superseding that five-output snapshot. The standing non-Pro Reviewer cleared Round013 PH neutral source for authentic independent critics only; no Round013 weighted scores or new PH tile approvals exist.','',
       '## Release integrity and technical priorities','',
       '- Original 27 source material rows for two Penthouse and two Triplex copies total **$23,572.44 tile-only**, including original **15% waste in every supplied gross quantity once**. Historical amounts are not current installed bids or approved caps. PH/TX WC flooring is carried within its respective Primary source, never separately purchased; do not double-count niche faces/returns, separate level/pan area, trim or samples.',
       '- The only live native Revit title verified is **25-006 1527 N Wieland**, not 1529. Every 1529 drawing-derived width, niche, drain location and shower slope is provisional. In particular PH Bath2 nominal W1 **59.496 in** versus selected Duravit **59 in** leaves **0.496 in total nominal difference** before wall build-up, flange and tolerances; not confirmed to fit.',
       '- Daltile RL21 Dynamic Beige **12x24 Matte** (3/8 in, USA, LEVEL) and **1.5-in hex Matte** (5/16 in, Mexico, shower PAN) are **different products**. Exact individual wet numeric measured DCOF results remain missing for each. Daltile application **Target >=0.42** (versioned linear maker sheet once Target >=0.60) is not a raw measured result. [Daltile individual RL21 manufacturer](https://www.daltile.com/products/stone-look/prime/dynamic-beige). Earlier project brochure reported mosaic nominal 1/4 in but current maker item 5/16 in; do not treat the old **0.65-mm** Brizo frame shortfall as proven fit error or prescribe shimming.',
       '- Selected [Brizo BT0734816-BNX 48-in reversible linear](https://www.brizo.com/bath/product/BT0734816-BNX) includes a manufacturer **solid finished grate** and decorative tile-in insert; mandatory separately ordered [BR73480 rough](https://www.brizo.com/bath/product/BR73480) includes sloped stainless channel, setting risers and its secondary drainage system. Study factory solid grate at PH Primary without changing any owner-selected fixture SKU. No manufacturer approval of the complete tile/mortar/membrane/drain/perimeter, flood test, glass/threshold or slope has been obtained; no assumption of exact tile-in fit. Public Brizo $825/$684 is list only.',
       '- Exact maker wall approval applies only to the **individual finish**. Flat Cortar Bone does not authorize wet Ribbed/Reed; Tones Sapphire/Sandstone have individually Wet Areas yes; Soho niche requires its own individual wet listing; Clara Caviar/Tones Opal lack exact individual maker release. Bathroom **LEVEL floor** and separate LINEAR/POINT **PAN** each require tested numeric wet DCOF and physical shop section.',
       '- Public [Vynara Flooring RL21 12x24](https://vynaraflooring.com/products/daltile-prime-12-x-24-matte?variant=51593507504411) advertised **RL21 1224J1PV $4.01/SF, 17.49 SF/case** and [PoshHaus alternate RL21 catalog](https://poshhaus.com/collections/daltile-prime) advertised variant **Z1PV $3.93/SF, 15.04 SF/case**, another J1PV $4.14/SF; PoshHaus labeled New England delivery only/unavailable. Different online pages, SKUs/case coverage and dates are **illustrative retailer data, not current Chicago accepted stock or SHB landed/installed bids**. Actual order cases/cost remain NULL.',
       '', '## Room-specific owner/GC closeout cards', '']
for idx,r in enumerate(rows,1):
 lines.extend([f'### {idx}. {r["room"]} — {r["room_status"]}',
  f'**Retained authority:** {r["selected_plumbing_program_or_board_direction"]}',
  f'**Nondelegable technical hold:** {r["source_specific_open_releases"]}',
  f'**Required evidence and signoff:** {r["required_owner_architect_gc_manufacturer_or_vendor_evidence"]}',
  f'**Dated material basis:** ${r["original_material_only_usd_per_copy"]} per copy ×2 = ${r["original_two_copy_material_usd"]}; source gross carries one 15% waste factor; actual current cost, order cartons and approved room cap NULL. Owner/GC purchase release FALSE.',''])
lines.extend(['## Contractual release hierarchy', '',
 '1. Owner signs **room program and basin/tub/drain decisions** where still unresolved; owner separately signs physical 1:1 sample and legitimate budget cap. No unsanctioned fixture choice.',
 '2. Architect/GC verify the **correct 1529 model**, surveyed dimensions, tub/wet-room program, field wall W1–W3, niche openings/returns, threshold and level versus sloped pan footprint; approve all cut/edge/movement sheets.',
 '3. Manufacturer confirms **exact wet-use listing per SKU/finish and true raw measured wet DCOF numbers per LEVEL and PAN product**. Tile supplier gives exact ordering codes, case yield/lot, installed or current landed Chicago quotes and ETA, not generic marketing or an online price.',
 '4. Licensed GC installer produces **manufacturer-compatible actual Brizo linear or point drain-to-membrane assembly**, rough, pan pitch, grate/solid configuration, positive niche/tub sill slope, testing and flood/signed inspections; eliminate all real clashes.',
 '5. Only after evidence gates and owner final selections are signed may a separated **purchase release** be created. No current files are purchase orders or owner-approved contracts.', '',
 '## Sources and provenance', '',
 '- Original Smartsheet 2026-09-03 and handoff schedules; signed `deliverables/integrated-r13/MANIFEST.json` five-file package; `state/ROOMS.json` at time of R14 export, including current R013 pending blind board and intact prior R010 scored outcomes.',
 '- Distinct specialist debate: `state/ROUND013_SUBMISSION.json`, independent `state/ROUND013_PREDISPATCH_REVIEWER_FIX1.json`, and `state/ROUND013_CRITIC_DISPATCH.json`, whose source/critic scores remain NULL until a later genuinely distinct prime turn.',
 '- Manufacturer/source notes: `research/products/R13_PH_RL21_MULTI_FORMAT_LEVEL_LINEAR_POINT_SOURCE_EVIDENCE.md`, `R13_PH_SOURCE_PRESERVING_INSTALLATION_ALTERNATIVES_20261106.md`, `R13_RL21_PUBLIC_RETAIL_SKU_PRICE_EXPOSURE_20261106.md`. Genuine approvals and procurement remain pending.', ''])
book=OUT/'R14_OWNER_13_ROOM_EXACT_RELEASE_DECISIONS.md'
book.write_text('\n'.join(lines),encoding='utf-8')
start=OUT/'START_HERE_R14.md'
start.write_text('# R14 immediate owner / GC closeout\n\nBegin with `R14_OWNER_13_ROOM_EXACT_RELEASE_DECISIONS.md`, then use the 13-row CSV for trade assignment and signature collection. The R13 full 65-action/25-wall/27-source package is the prior signed construction/source baseline; R14 is an additive accuracy and actual interface update. All authorizations remain false.\n\nCurrent high-consequence corrections: exact RL21 hex 5/16 versus older 1/4 brochure, different floor/pan manufacturer test documents; Brizo BNX included solid grate but no approved waterproof assembly; PH Bath2 0.496-in nominal total tub tolerance; PH4 square point PAN and 35/27 area conflict. No owner selection or current Chicago installed quote has been inferred.\n',encoding='utf-8')

outputs={}
for p in (book,target,start):
 b=p.read_bytes()
 outputs[p.name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
prior=ROOT/'deliverables/integrated-r13/MANIFEST.json'
dispatch=ROOT/'state/ROUND013_CRITIC_DISPATCH.json'
manifest={
 'created':'2026-11-06','release_status':'NOT FOR PURCHASE',
 'room_count':len(rows),'historic_four_unit_material_only_usd':23572.44,
 'original_gross_already_includes_15pct':True,
 'owner_approval':False,'procurement_release':False,
 'r13_manifest_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),
 'r013_source_submission_sha256':hashlib.sha256((ROOT/'state/ROUND013_SUBMISSION.json').read_bytes()).hexdigest(),
 'r013_critic_dispatch_sha256':hashlib.sha256(dispatch.read_bytes()).hexdigest(),
 'r013_critics_weighted_score':None,
 'outputs':outputs,
}
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
assert len(outputs)==3
print('PASS R14 new signed 3 outputs, 13 owner/GC room release rows, original 23572.44 material only; zero owner/procurement release')
