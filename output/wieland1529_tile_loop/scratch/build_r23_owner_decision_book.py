"""Author additive R23 owner-tier cards from governed sources, not new selections."""
from pathlib import Path
from decimal import Decimal
import json, csv

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc'
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']

tiers={
'PH-PRIMARY':(
 'Source-faithful Bone Soft/Anti-Slip and original BNX 48-in LINEAR; original full wet relief and floor lab gates FAIL, no niche.',
 'Conditional individually maker-wet-listed flat Bone shower wall + individually checked RL21 12x24 LEVEL / RL21 1.5in hex LINEAR PAN, solid BNX grate layout study; no substitute drain.',
 'Same technically conditional program with two true-scale full bathroom material boards, finished 48-in Brizo/BR73480 pan and floor/ceiling mockup, verified individual raw wet labs and factory approved sections; owner selects only after cost and documents.'),
'PH-BATH2':(
 'Preserve maker-Wet Areas Sapphire tub walls, Sandstone wet niche, Duravit tub/Hansgrohe Matte White, source level floor still raw-test FAIL; no tiled PAN.',
 'Refine 2x20 vertical or controlled horizontal bond with actually measured tub flange, 59-vs-59.496in clearance, level flooring exact raw evidence and niches deducted once.',
 'True 1:1 sapphire/Matte White/grout/niche/tub edge build and verified 1529 trim/apron, shop-ready tub alcove and complete installed supplier bid, without adding a shower PAN.'),
'PH-BATH3':(
 'Keep original Opal source as historical **wet WALL FAIL**; preserve Sandstone wet NICHE, Hansgrohe Chrome and Delta point shower drain, no decision tub/walk-in.',
 'Conditional maker-Wet Areas Sapphire WALL and Sandstone niche, independently selected LEVEL floor raw test; explicit signed owner TUB branch with new tub/waste and NO PAN or WALK-IN branch with Delta four-plane POINT PAN exact wet raw test.',
 'Choice-conditioned actual 1:1 full-size Chrome/wet tile/niche/glass/tub-flange OR point-drain pan mockup with factory membrane and slope, signed owner basin/program and actual installed cost; no owner branch inferred.'),
'PH-BATH4':(
 'Keep 2026-09-03 Bone Ribbed/Clara Caviar as original quoted reference, wet WALL/NICHE FAIL pending maker proof; selected WALK-IN BNX square POINT preserved.',
 'Conditional flat maker-wet Bone wall + individually wet-listed Soho Black niche, independently approved separate raw wet LEVEL and Glazzio HNC6715 2x2 POINT PAN or RL21 hex POINT study; 35 vs 27 SF hold.',
 '1:1 four-plane point shower, BNX square drain and black/white finish sample with full factory membrane, 107.2 SF/copy original wall-vendor-total audit, 35/27 field survey, current installed bid and owner final signature.'),
'PH-POWDER':(
 'Keep Earth Lines dry relief wall and selected Luxe Gold Brizo T65722LF-GL/R65700; WOOD floor, wet tests N/A.',
 'Evaluate two flank relief fields framing a dry painted planar faucet landing with width and trim wall plane owner-unselected.',
 'Full-scale approved Brizo trim + real mirror/paint/relief/wood section and owner-signed cost/edge/caliper sample; R22 six-copy shop holds remain.'),
'PH-WC':(
 'Shared original PH-PRIMARY LEVEL floor/quote only, no additional niche or WC tile order.',
 'Study continuity joint, toilet flange transition and accurate shared-parent measured LEVEL boundary without duplicate area.',
 '1:1 shared threshold/trim/wood or stone junction and parent wet lab signoff; no additional separate order or shower PAN.'),
'TX-PRIMARY':(
 'Source Cortar Clay Soft LEVEL and AntiSlip LINEAR pan, source relief wet-wall approval absent; selected 48-in BNX LINEAR NO NICHE.',
 'Individually maker-listed flat Clay wall + independently verified Emser LEVEL and Prime RL21 1.5-in hex LINEAR PAN studies, all exact raw test pending, original Black Onyx trim untouched.',
 'Manufacturer-signed Brizo linear rough/membrane/solids versus tile insert, grout/caliper/cut/mockup and current two-copy installed bid before owner decision.'),
'TX-BATH2':(
 'Original Copper/Sandstone wet tub walls, historical Clay Soft LEVEL untested, Duravit tub/Chrome Hansgrohe, basin UNSELECTED; PAN N/A.',
 'Conditional maker application specific wall/niche reconciliation + individually verified alternate EL30 LEVEL only, no shower drain conversion and no inferred basin.',
 'Signed 1:1 Copper/Sandstone/Chrome/tub opening and verified floor lab + measured 1529 elevations, actual supplier case/bid and owner basin signature.'),
'TX-BATH3':(
 'Preserve Emerald maker-Wet Areas WALL and Sandstone NICHE, historical Grey Soft LEVEL raw FAIL and selected Brizo BNX 4-in square POINT only conditionally.',
 'Owner TUB: select actual tub/waste and retain LEVEL only, no PAN; owner WALK-IN: retain selected BNX square POINT with separate tested RL21 hex 4-plane PAN study, original Emerald wall stays.',
 'True Black Onyx/Emerald/Sandstone sample and manufacturer shop; 207A/207B actual drain center, membrane/weeps, separate LEVEL/PAN exact raw lab and full installed price before owner program choice.'),
'TX-BATH4':(
 'Duravit tub/Matte White Hansgrohe, original Bone Soft LEVEL and historic Clara Caviar wet niche unlisted; no PAN.',
 'Conditional maker-wet flat Charcoal wet wall and individually wet-listed Soho Ivory niche; Emser KC04 LEVEL with separate exact raw lab, tub waste and opening.',
 'Physical flat Charcoal/Soho Ivory/Matte White grout/edge/tub-flange mockup and signed true 1529 level floor cartons/GC bid, without adding PAN or importing TX2 basin hold.'),
'TX-POWDER':(
 'Haze Camel/Wheat 70:30 dry wall source, WOOD floor, unresolved AXOR 48140991 vs Hansgrohe 32526141 two incompatible TRIMS, neither matching rough authorized.',
 'Provisional one-wall Camel/Wheat balanced band and 1:1 source-listed metals for owner election; DO NOT pair trims as faucet+rough.',
 'Owner signs a single manufacturer faucet trim/finish, plumber verifies corresponding factory rough, GC approves 102A/B actual landing, then measured 70:30 color cases and current bid.'),
'TX-POWDER2':(
 'Indigo Edge 6x6 dry wall source, WOOD floor, Tecturis E 73072341 Brushed Black Chrome DECK faucet, basin UNSELECTED.',
 'Centered dry Indigo versus Earth Lines independent design compositions, mirror/countertop mockup only; do NOT assume a wall faucet.',
 'Signed basin and finish-specific drain, actual deck faucet hole reach/overflow and countertop drill template, full-size Indigo/grout/wood photo study and current quote.'),
'TX-WC':(
 'Shared TX-PRIMARY LEVEL floor quoted once, no WC shower PAN or independent tile order.',
 'Coordinate threshold/flange and owner LEVEL floor with Primary, without extra quote.',
 'True 1:1 shared floor transition and exact parent wet LEVEL lab approval and copy-specific installer signoff, NO double-counted cases.'),
}
assert set(tiers)=={x['id'] for x in rooms}

lines=['# R23 — thirteen-room owner GOOD / BETTER / BEST conditional design and trade decisions',
 '', '**Date 2026-11-06; proposal-only / NO approved palette, no owner approval or GC/procurement release.** These are scope-quality DESIGN/STUDY directions, **not a rank, current price, or weighted board winner**. All source good/better/best entries are mutually unselected; source-historical failed wet gate is not normalized to PASS by inclusion.',
 '', 'Owner PH resale ~$2.8M; TX ~$2.7M; comp band ~$2.4M–$3.2M, Old Town first. Fourteen listing entries represent only **nine buildings**; OT01–OT04 at 405 W Armitage are ONE building, not four independent baths. Lincoln Park and Gold Coast adjacent/secondary. No authenticated competitor bathroom tile images, no attributed undocumented material photos. Source: [comp register](../../research/comps/COMPS.md).',
 '', '**Numeric meaning:** historical room quote = dated original 2026-09-03 **MATERIAL-ONLY** amount per copy with original 15% waste included exactly once; none is a fresh proposed supplier bid, installed price, allowance or authorized case order. Exact manufacturer SKU/color/finish, individual wet use, fully measured net and case yield remain release conditions in companion CSV. Owner tier approval absent.',
 '']

for x in rooms:
 rid=x['id'];good,better,best=tiers[rid]
 lines.extend([
  f'## {rid} — {x["status"]} | current board {x["champion_id"] or "null"} / {x["champion_score"] if x["champion_score"] is not None else "null"}',
  '', f'**Source historic material-only:** ${Decimal(str(x["carried_quote_material_subtotal_usd_per_unit"])):,.2f} / copy, two copies; no new owner selection.',
  '', f'**GOOD — source-faithful base:** {good}',
  '', f'**BETTER — physically differentiated, conditional:** {better}',
  '', f'**BEST — complete coordinated owner+shop review:** {best}',
  '', '**Approval boundary:** selected fixtures remain only those in `rooms/'+rid+'/plumbing.json`; verified 1529 dimensions, factory individual wet WALL/NICHE listings, raw exact numerical wet LEVEL/PAN lab where applicable, current Chicago lot/cases/offer, complete installed GC bid and owner/architect/plumber/tile/GC/purchaser signatures remain unresolved. Owner tier: `null`; final order: `false`.',
  '', f'**Owner/GC prompt:** review actual finish/fixture and branch physically with 1:1 `{rid}` mockup, source-faithful rendered brief and field shop; never copy another room\'s tub, basin, wet list or drain.',
  ''
 ])

lines.extend(['## Owner decision checklist (not an electronic authorization)', '',
 '| Decision authority | Exact signed evidence demanded | Status |', '|---|---|---|',
 '| Owner | PH/TX Bath3 separately TUB or WALK-IN, PH3/TX2/TX Powder2 basin, TX Powder actual trim vs rough, selected paints/tiling, each room upgrade cap and final GOOD/BETTER/BEST choice | **UNSIGNED** |',
 '| Architect | Exact 1529 Revit/site ID, dimensioned W1–W3 with openings/niche wall deductions, threshold/tub/point/linear sections, approved maker individual wet permissions | **UNSIGNED** |',
 '| Plumber/waterproofing installer | Approved exact factory trims/rough, tube versus shower drain branches, membrane/preslope/clamp or channel sections, signed inspections/flood | **UNSIGNED** |',
 '| Tile installer/GC | Exact raw wet LEVEL/PAN reports and calibrated 1:1 tile/grout/mockups, complete physical net/trim/cases/paint labor, field witness and punch inspection | **UNSIGNED** |',
 '| Estimator and purchaser | Exact-current Chicago stock/lot/ETA, per SKU case, tax/freight/installed supplier price, approved cap, final separately dated PO authority | **NO PO** |',
 '', '**No procurement, purchase, order, material sample ordering, vendor contact, email, permit model edit or release performed.**'])
(O/'R23_ALL_13_ROOM_GOOD_BETTER_BEST_OWNER_DECISION_BOOK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

kit=['# R23 — physical 1:1 samples, render/camera truth, mockup and Chicago price-origin register',
 '', '**REQUEST ONLY**: no samples bought, physical mockups executed, verified 1529 renders generated, actual site photographs taken, Chicago prices or verified delivery leads obtained. Two physical copies per room must each be site-controlled. Signed R18 thirty-nine camera instructions remain immutable and are expanded below without claiming any image exists.',
 '', '## Physical sample and reference protocol',
 '', '| Scope | Source-specific kit and site witness | Image/camera shots AFTER authentic 1529 dimensions | Contractor acceptance |',
 '|---|---|---|---|']
for x in rooms:
 rid=x['id']; a,b,c=tiers[rid]
 if 'POWDER' in rid:
  kitnote='Dry wall tile actual factory color/finish, mirror/wood/base/metal swatch and grout. PH Brizo dry flat landing; TX 2 conflicting wall TRIMS; TX2 DECK/counter/drill only.'
 elif rid.endswith('-WC'):
  kitnote='Parent Primary LEVEL test and same purchased tile, threshold/flange/wood or hall transition; NO additional WC purchase.'
 else:
  kitnote='Real maker-wet WALL/NICHE piece and separate source-specific LEVEL and applicable POINT/LINEAR PAN samples, actual exact drain/grate/rough, grout, edge/trim, waterproof backer and floor assembly. Tub rooms NO PAN.'
 kit.append(f'| {rid} | {kitnote} | Frontal W1 with true fixture positions; W3 oblique with niche/corner and actual cut pattern; full-scale drain/tub-flange or dry faucet detail under daylight/night as applicable | owner/architect/plumber/GC sample/photo/field acceptance: **FALSE** |')
kit.extend(['', '### Fixed four priority project render briefs (not generated images)',
 '', '1. **PH-BATH3 307A/B:** show current tub-ALCOVE source geometry as *unverified* with mutually exclusive labeled **TUB TBD** and **WALK-IN TBD** drawing overlays, Hansgrohe Chrome and selected Delta 4-in shower POINT only in walk-in; render Sapphire wet-approved alternative versus historical Opal unapproved as distinctly labeled visual decisions, Sandstone niche. The basin stays UNSELECTED, no unowned tub shown as selected.',
 '2. **TX-BATH3 207A/B:** same two mutually exclusive owner program illustrations, Emerald wet wall/Sandstone niche and selected BNX 4-in POINT only if walk-in, Brizo Roccesco form. Do not transfer PH basin hold. Point PAN small-format, no false 48-in linear.',
 '3. **PH-BATH4 311A/B:** walk-in only, BNX square 4-in POINT and real four-plane small-format pan schematic; one labeled historical Bone Ribbed/Caviar wet-unapproved reference versus flat Bone/Soho conditional wet-authorized design. Overlay owner 35 vs drawing 27 floor discrepancy as an unresolved annotation, never fake resolved dimension.',
 '4. **PH-PRIMARY 304A/B:** keep selected BNX 48-in LINEAR and separate Duravit tub, NO niche, flat Bone wet-approved alternative to original Reed unlisted. Show factory solid BNX grate versus tile-in insert as *same selected drain configuration studies*, with 7–18mm original tile-in frame, 1/4-vs-5/16 mosaic and physical finish cross-section undetermined.',
 '', '### True source/photography release rule',
 '', 'Use only correct verified native 1529 W1/W3/floor/niche/fixture coordinates with architect check before labeling a render accurate. Existing native 1527 file cannot certify 1529. Show any provisional view as **schematic**. Three image instructions per room are not generated buyer images; do not claim competitive bath photographs identify tile manufacturer or SKU. Source-witnessed 1:1 cuts, relief height and grout choice take priority over AI image appearance.',
 '', '## Pricing evidence and carton discipline',
 '', '| Evidence type | Current classification | Buyer/GC use |', '|---|---|---|',
 '| 2026-09-03 original ELM Smartsheet source, 27 rows | **HISTORICAL MATERIAL ONLY**, $23,572.44 for two PH plus two TX, includes original 15% waste once | comparator, not accepted purchase quantity or installed budget |',
 '| Manufacturer Brizo public MSRP for original BNX drain/rough | **PUBLIC MANUFACTURER LIST PRICE / MSRP**, dated source reference, no current confirmed supplier discount/installed price | do not add to original tile-only or use as Chicago PO |',
 '| Public online TileBar/Daltile retail and package page | **PUBLIC RETAIL INDICATION**, often inconsistent case yields; product/order version and date matter | no proof current Chicago stock, freight, lot, installed cost |',
 '| Factory exact tile availability, wet-wall listing and raw lab | **MANUFACTURER technical evidence** only when exact color/finish/format/test identified; bounds and Target are NOT raw lab | clearance gate distinct from retail marketing and current stock |',
 '| Dated current Chicago warehouse allocated stock/ETA, same-SKU factory carton, freight and taxes | **VERIFIED LOCAL SUPPLIER OFFER**: `null` / not obtained | REQUIRED for order once vendor contacts authorized separately |',
 '| Workmanlike wet setting, drains, waterproof, trims, float/pitch, grout, mockup, tax and overhead | **COMPLETE INSTALLED GC BID**: `null` | required per owner-approved scope before release |',
 '| Owner per-room material cap / upgrade allowance | **ALLOWANCE / CAP**: `null`, owner feedback FILL IN | no fabricated 125% budget failure threshold when cap absent |',
 '', '**Carton math:** source gross *already* has 15% once. For a NEW, separately approved measured surface, calculate each color/formats net independently; `new need = independently measured NET x (1+single documented cut allowance)`; `orderable cases = ceil(new need / supplier verified carton SF for same factory SKU/lot)`. Separate level vs point/linear pan, niche opening displaced face vs returns/sill once, two WCs inherited from Primary and two unpriced Primary extra niches NO SCOPE. Source retail 8 pieces/17.49 SF-carton contradiction for Daltile EL301224J1PV must remain HOLD, not magically made nine pieces. Need confirmed current pack and local bid.',
 '', '## Actual market evidence boundary',
 '', '14 listing records = nine buildings; OT01–OT04 at 405 W Armitage counted as one; Old Town first, then secondary adjacent Lincoln Park and Gold Coast. $2.8M Penthouse, $2.7M Triplex, $2.4M–$3.2M comp band. No verified competitor bath tile images. No unsupported photos/stock, fabricated manufacturer colors or unsupported good/better/best pricing.',
 '', '**Signatures:** OWNER `false`; ARCHITECT `false`; PLUMBER `false`; INSTALLER `false`; GC `false`; PROCUREMENT `false`.'])
(O/'R23_13_ROOM_1TO1_SAMPLE_RENDER_SHOP_AND_PRICE_ORIGINS.md').write_text('\n'.join(kit)+'\n',encoding='utf-8')

print('PASS R23 13 room GOOD/BETTER/BEST actual room-specific material, owner and GC mockup/render/price provenance book')
