"""R019 tile-only next-cohort frozen SOURCE writer; deliberately no reviewer/scoring.

One-time, additive only. Refuses to overwrite any file; does not touch R018.
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS = {r['id']: r for r in json.loads((ROOT / 'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
N = '2026-11-06'
PRODUCTS = {
    'SAPPHIRE': ('ELM Tones Sapphire 2x20 Glossy', 'https://www.elmsurfaces.com/product/sapphire-tones',
                 'research/products/elm-tones-sapphire-2x20-wet-approved.md', 'legacy individually documented wet WALL listing; recheck live exact SKU'),
    'SANDSTONE': ('ELM Tones Sandstone 2x20 Glossy', 'https://www.elmsurfaces.com/product/sandstone-tones',
                  'research/products/elm-tones-sandstone-2x20.md', 'legacy individually documented wet NICHE wall listing; no floor permission transferred'),
    'BONE_FLAT': ('ELM Cortar Bone 24x48 Soft FLAT', 'https://www.elmsurfaces.com/product/cortar-bone',
                  'research/products/elm-cortar-bone-flat-24x48.md', 'individual flat Bone wet WALL listing; no Ribbed/Reed permission inferred'),
    'SOHO_BLACK': ('ELM Soho Black 2x10 Glossy', 'https://www.elmsurfaces.com/product/soho-black',
                   'research/products/elm-soho-black-2x10.md', 'individual wet NICHE wall listing; NOT a shower floor'),
    'SOHO_IVORY': ('ELM Soho Ivory 2x10 Glossy', 'https://www.elmsurfaces.com/product/soho-ivory',
                   'research/products/elm-soho-ivory-2x10-glossy-tx-bath4-wet-niche.md', 'individual wet NICHE listing; NOT a shower floor'),
    'NOHO_IVORY': ('ELM Noho Ivory 2x10 Matte', 'https://www.elmsurfaces.com/product/noho-ivory',
                   'research/products/R019_ELM_NOHO_IVORY_2X10_MATTE_WET_WALL_EVIDENCE.md', 'exact Noho Ivory individual Wet Areas WALL listing, distinct from Soho Ivory'),
    'SOHO_EMERALD': ('ELM Soho Emerald 2x10 Glossy', 'https://www.elmsurfaces.com/product/soho-emerald',
                     'research/products/R019_ELM_SOHO_EMERALD_2X10_GLOSSY_WET_WALL_EVIDENCE.md', 'exact Soho Emerald individual wet WALL listing; original Tones Emerald approval not assumed'),
    'TROSA': ('Emser Capisco Trosa 12x24 Matte, F08CAPITR1224M', 'https://www.emser.com/product/capisco-f08capitr1224m',
               'research/products/R018_CAPISCO_BODEN_TROSA_INDIVIDUAL_LEVEL_FLOOR_BOARD_EVIDENCE.md', 'LEVEL bath only; exact SKU maker DCOF >=0.60 + Commercial Floor Wet YES'),
    'BODEN': ('Emser Capisco Boden 12x24 Matte, F08CAPIBO1224M', 'https://www.emser.com/product/capisco-f08capibo1224m',
               'research/products/R018_CAPISCO_BODEN_TROSA_INDIVIDUAL_LEVEL_FLOOR_BOARD_EVIDENCE.md', 'LEVEL bath only; exact SKU maker DCOF >=0.60 + Commercial Floor Wet YES'),
    'SOURCE_WHITE': ('Emser Source Pure White 2x2 Matte, W71SOURPWH1212MO2',
                     'https://www.emser.com/product/source-w71sourpwh1212mo2',
                     'research/products/R019_EMSER_SOURCE_PURE_WHITE_W71_2X2_POINT_PAN_EVIDENCE.md',
                     'separate four-plane POINT PAN mosaic; exact SKU maker DCOF >0.60, Residential Shower Floor YES'),
    'TECH_IVORY': ('Emser Technique Ivory 2x2 Matte, F16TECHIV1212MO',
                   'https://www.emser.com/product/technique-f16techiv1212mo',
                   'research/products/R019_EMSER_TECHNIQUE_IVORY_F16_2X2_POINT_PAN_EVIDENCE.md',
                   'separate four-plane POINT PAN mosaic; exact SKU maker DCOF >0.60, Residential Shower Floor YES'),
}
NEW_RESEARCH = {
    'research/products/R019_ELM_NOHO_IVORY_2X10_MATTE_WET_WALL_EVIDENCE.md': """# Noho Ivory 2x10 Matte exact wet WALL item — R019 2026-11-06

Official manufacturer https://www.elmsurfaces.com/product/noho-ivory — **Noho Ivory**, **2 x 10 in**, **Matte**, **9.5 mm**. Individual product lists **Walls, Wet Areas** (also Floors, but no numeric wet DCOF published on this item). Proposed *wet WALL* only; no LEVEL/PAN inference. Ivory warm-neutral, offset or vertical stacked layout conditional on owner design and actual wall receipt geometry. Current maker US page exists; Chicago exact SKU, stock/lot, carton yield, resale price and lead time UNKNOWN. Do not substitute Soho Ivory glossy identity or infer another Noho color permission. No procurement or owner approval.
""",
    'research/products/R019_ELM_SOHO_EMERALD_2X10_GLOSSY_WET_WALL_EVIDENCE.md': """# Soho Emerald 2x10 Glossy exact wet WALL item — R019 2026-11-06

Official manufacturer https://www.elmsurfaces.com/product/soho-emerald — **Soho Emerald**, **2 x 10 in**, **Glossy**, **9.5 mm**. Individual product lists **Walls, Wet Areas**. Supports a wet shower/TUB surround **wall**, not a floor; does not imply original Tones Emerald's exact finish approval. 2x10 vertical stacked field option contrasts with Brizo Black Onyx. Chicago ELM distributor company present but available exact dye lot, factory SKU/order code, carton yield, project price and ETA UNKNOWN. Owner has not selected the change; no purchase.
""",
    'research/products/R019_EMSER_SOURCE_PURE_WHITE_W71_2X2_POINT_PAN_EVIDENCE.md': """# Emser Source Pure White exact 2x2 shower POINT pan — R019 2026-11-06

Official https://www.emser.com/product/source-w71sourpwh1212mo2 — **W71SOURPWH1212MO2**, unglazed porcelain 2x2/12x12 mesh-backed mosaic, **Pure White**, **Matte**, **6 mm**, recommended grout 1/8 inch (maker color 642 Ash), individual **DCOF >0.60**, **Commercial Floor Wet YES**, **Shower Floor Residential YES**. Published maker test-result lower bound (NOT invented actual raw point) satisfies board's product-published >=0.42 on a shower pan, subject to point-drain/slope and manufacturer-approved waterproof assembly. Explicitly DIFFERENT from another similarly named Source SKU W16SOURPUWH1212MO2M (reported 5.5 mm): do not interchange without new verification.

Retailer nonlocal public example https://www.gbtilecollections.com/emser-source-pure-white-matte-porcelain-mosaic.html reported $11.77 per 0.95-SF sheet as of research; **not** Chicago warehouse current project quote, installed cost, or verified available shade lot. Manufacturer US catalog active, Chicago exact stock/ETA, current usable case yield and actual four-plane pan SF UNKNOWN; tub branch PAN N/A. No orders.
""",
    'research/products/R019_EMSER_TECHNIQUE_IVORY_F16_2X2_POINT_PAN_EVIDENCE.md': """# Emser Technique Ivory exact 2x2 shower POINT pan — R019 2026-11-06

Official https://www.emser.com/product/technique-f16techiv1212mo — **F16TECHIV1212MO**, porcelain 2x2/12x12 mesh-backed mosaic, **Ivory**, **Matte**, **9.5 mm**, suggested grout 1/8 inch (maker color 543 Driftwood), individual **DCOF >0.60**, **Commercial Floor Wet YES**, **Shower Floor Residential YES**. Published maker minimum bound rather than an exact raw measured point. Separate shower four-plane POINT PAN mosaic, not the LEVEL 12x24 Capisco. Actual Brizo/Delta 4-in square drain rough/waterproof compatibility and slope still need confirmation.

Manufacturer US catalog active. The exact item on Lowes.com may appear **no longer sold by Lowe's**; this does not establish manufacturer discontinuation, but specific channel availability deserves verification. Chicago local lot/usable carton, lead time and actual project material price UNKNOWN. No orders or owner approval.
""",
}

COHORT = {
    'PH-BATH3': {
        'A': dict(wall='SAPPHIRE', niche='SANDSTONE', level='BODEN', point='TECH_IVORY', wall_layout='centered HORIZONTAL stack 2x20 with muted grout', feature='Cool Sapphire field and chromed Hansgrohe remain legible; warm Ivory small-format PAN provides a deliberately restrained contrast'),
        'C': dict(wall='NOHO_IVORY', niche='SANDSTONE', level='TROSA', point='SOURCE_WHITE', wall_layout='VERTICAL stack 2x10 with tonal warm-white grout', feature='Warm matte Ivory walls counter the source Opal uncertainty; mineral Taupe floor frames Chrome and Sandstone as the warm accent'),
    },
    'PH-BATH4': {
        'B': dict(wall='BONE_FLAT', niche='SOHO_BLACK', level='TROSA', point='TECH_IVORY', wall_layout='24x48 FLAT full wet wall, vertically aligned joints (no Ribbed)', feature='Bold glossy black niche echoes selected Brizo Black Onyx against quiet limestone-look Bone; Taupe level floor anchors the contrast'),
        'C': dict(wall='BONE_FLAT', niche='SOHO_IVORY', level='BODEN', point='SOURCE_WHITE', wall_layout='24x48 FLAT full wet wall, centered low-joint layout (no Ribbed)', feature='Tonal Ivory niche and pale floor brighten the walk-in; restrained White POINT pan keeps the all-neutral field cohesive against Black Onyx fixtures'),
    },
    'TX-BATH3': {
        'A': dict(wall='SOHO_EMERALD', niche='SANDSTONE', level='TROSA', point='TECH_IVORY', wall_layout='VERTICAL stack glossy green 2x10 with tonal green grout', feature='Green saturated wet wall recalls the source Emerald direction but uses an actually wet-listed individual SKU; taupe floor and BNX metal ground the color'),
        'B': dict(wall='NOHO_IVORY', niche='SOHO_BLACK', level='BODEN', point='SOURCE_WHITE', wall_layout='HORIZONTAL stack matte warm-white 2x10 with a controlled half-module return (0 offset preferred)', feature='A low-contrast warm neutral wall with a small black glossy niche makes Brizo Black Onyx deliberate; off-white level floor preserves light'),
    },
}
PROGRAM = {
    'PH-BATH3': 'Owner TUB vs WALK-IN UNSELECTED. Hansgrohe CHROME wet fixtures; Delta DT062412 CHROME 4-in square POINT is a *shower* drain ONLY if WALK-IN is chosen; NEVER tub waste. Basin OWNER-UNSELECTED. Neither tub nor walk-in branch is decided.',
    'PH-BATH4': 'Owner-selected WALK-IN only; Brizo BT062415-BNX Black Onyx 4-in square POINT shower drain fixed, four-plane sloped PAN required. No tub. Distinct bath LEVEL and shower POINT PAN.',
    'TX-BATH3': 'Owner TUB vs WALK-IN UNSELECTED. Brizo Black Onyx wet fixtures; Brizo BT062415-BNX 4-in square POINT is a *shower* drain ONLY if WALK-IN. No tub waste substitution. Do not apply PH-BATH3 basin-unselected note to TX-BATH3.',
}
GATE = {
    'PH-BATH3': 'Original ELM Tones Opal 2x20 Glossy specific Wet Areas WALL approval not established. Original Cortar Bone Soft LEVEL wet DCOF unknown; no source conditional POINT PAN item. Replace with individually wet-listed WALL and published-DCOF LEVEL; conditionally add separately suitable 2x2 POINT PAN only when WALK-IN is selected.',
    'PH-BATH4': 'Original Cortar Bone Ribbed full wet WALL individual Wet Areas permission not established; original Clara Caviar 2x8 NICHE individual Wet Areas not established; original Cortar Charcoal Soft LEVEL wet DCOF unknown and source did not isolate four-plane POINT PAN. Flat Bone+Soho+Emser supply distinct exact wet-permitted alternatives.',
    'TX-BATH3': 'Original Tones Emerald exact current individual wet WALL identity unresolved; original Cortar Grey Soft LEVEL wet DCOF unknown; no selected separate POINT PAN tile. Replace with individually wet-listed Soho Emerald/Noho Ivory, documented Capisco LEVEL and separate Emser 2x2 POINT PAN conditional on WALK-IN.',
}

def refs(k):
    name, url, path, detail = PRODUCTS[k]
    assert (ROOT / path).exists() or path in NEW_RESEARCH, path
    return f'[{name}]({url}) ([evidence](../../../../../{path}))', detail

def candidate(room, letter, cfg):
    source = ROOMS[room]
    row = {x['surface']: x for x in source['carried_tile_rows']}
    assert set(row) == {'wall', 'floor', 'accent'}
    assert source['status'] == 'blocked' and source['champion_id'] is None and source['owner_status'] is None
    geom = json.loads((ROOT / 'rooms' / room / 'geometry.json').read_text(encoding='utf-8'))
    wall, wd = refs(cfg['wall'])
    niche, nd = refs(cfg['niche'])
    level, ld = refs(cfg['level'])
    pan, pd = refs(cfg['point'])
    wallname = PRODUCTS[cfg['wall']][0]
    niche_name = PRODUCTS[cfg['niche']][0]
    floorname = PRODUCTS[cfg['level']][0]
    panname = PRODUCTS[cfg['point']][0]
    fmt = lambda n: f'{n:.2f}'
    lines = [f'# {room} — Candidate {letter} — neutral complete tile scheme',
             '',
             'This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.',
             '',
             '## Exact selected room program and distinct material design',
             PROGRAM[room],
             f'**Wet WALL:** {wallname}; {cfg["wall_layout"]}. **Existing NICHE** (if physically confirmed in source): {niche_name}; align to wet-wall grid, make actual sill positive fall, final grout/edge TBD. **Bath LEVEL:** {floorname}, 0-offset layup, nominal 1/8-inch recommended grout; ***never a four-plane POINT PAN.*** **Shower POINT PAN:** {panname}, 2x2 mosaic in separate four-plane sloping footprint only if owner-program includes WALK-IN. Tub branch: **tiled PAN N/A**; never replace a tub waste with shower drain.',
             f'**Design position:** {cfg["feature"]}. Two copies share this one distinct room-type scheme; no owner-selected fixtures/basins/program changes.',
             '',
             '## Actual source schedule and manufacturer-specific hard gates',
             '| Surface / original Smartsheet row | Proposed manufacturer-specific selection / use | Original gross SF per copy (original 15% waste ONCE) | Historical direct tile $/copy, original source $/SF | Evidence; board PASS condition vs unresolved holds |',
             '|---|---|---:|---:|---|']
    for surf, use, desc in [
        ('wall', wall, wd),
        ('accent', niche, nd),
        ('floor', level, ld)]:
        rr = row[surf]
        note = f'{desc}; new project item price, exact factory/color lot, existing face-net/returns and current Chicago availability UNCONFIRMED.'
        if surf == 'floor':
            note += ' Existing gross may cover LEVEL and/or shower source scope; independently split LEVEL vs new separate POINT PAN; no guessed PAN SF.'
        lines.append(f'| {surf.upper()} `{rr["smartsheet_row_id"]}` | {use} | {fmt(rr["qty_sf_per_unit"])} SF | ${fmt(rr["extended_quote_cost_usd_per_unit"])} / ${fmt(rr["quoted_rate_usd_per_sf"])}/SF | {note} |')
    lines += [
        '| **Separate conditional POINT PAN** — no new Smartsheet row | ' + pan + ' | **UNKNOWN** pending owner TUB/WALK-IN + actual pan/level boundary' +
        ('; WALK-IN FIXED, but actual four-plane pan SF still UNKNOWN' if room == 'PH-BATH4' else '; TUB branch N/A') +
        ' | **NOT INCLUDED as a newly priced line** | ' + pd + '; manufacturer-published wet DCOF >0.60 meets board product-published >=0.42 for residential shower pan; physical slope/drain assembly unverified. |',
        '',
        '## Hard-gate resolution and truthful remaining unknowns',
        '**Exact previously failed material problem:** ' + GATE[room],
        f'**Wet WALL:** {wd}. **Existing NICHE:** {nd}. A wet WALL approval does not substitute for a wet NICHE listing and vice versa. For PH-BATH4 selected WALK-IN, 24x48 flat WALL is never laid on the four-plane PAN.',
        f'**LEVEL:** {ld}; **separate POINT PAN:** {pd}. Both official item pages publish wet DCOF above board 0.42, but these are manufacturer bounds, NOT raw exact site laboratory readings. Reconcile any separate legacy heightened certificate requirements with the current board, without inventing numbers.',
        'Availability gate: product appears on its current US manufacturer catalog and Emser lists an Illinois location at https://www.emser.com/EnhanceDesignShowrooms ; ELM is Chicago-based at https://www.elmsurfaces.com . These facts do NOT prove local in-stock project quantity, dye lot, current supplier price, order-carton coverage, or dispatch ETA. Such fields remain **null**. Do not claim current Chicago stock.',
        'Budget: current maker-substitute and installation pricing unavailable. The historical ${:.2f}/copy is already material-only with the original 15% included, not a current alternate price or owner-approved room cap. No 125% gate claim can be computed from null current price and null allocated budget.'.format(source['carried_quote_material_subtotal_usd_per_unit']),
        '',
        '## Source geometry, finish coordination and alternatives',
        'Native 1527 and 1529 names are the **same building, owner-confirmed 2026-11-07**; old room wall dimensions are drawing-derived and **NOT** native element/receipt verified. Source-only W1–W3 nominal widths and tiled heights (feet): ' +
        '; '.join(f'{w["id"]} {w["length"]["value"]:.3f} x {w["tiled_height"]["value"]:.3f}' for w in geom['tiled_walls']) +
        '. Actual openings/niche/valve/door/shower pan line/threshold, grout calibration, profile/corner and any field under-3-in sliver still require source receipt and survey.',
        'POINT pan install: nominal 2x2 mosaic is a four-plane drain-friendly *candidate* only, not proof of Delta/Brizo drain grate/rough/waterproof compatibility. If the owner selects TUB in Bath3, the pan and shower POINT drain become N/A without changing the actual owner-selected fixtures or inventing tub waste.',
        'Evidence against comp set: [OT01–OT04 405 W Armitage one development; OT05 1849 N Mohawk](../../../../../research/comps/COMPS.md) are Old Town / boundary comparables, not four independent designs. No independently verified comp bathroom image here supports an exact competing tile dimension, grout, stone or fixture finish. No ungrounded buyer premium assumed; LP/GC remain secondary.',
        'Owner sample direction, not ordered: 1:1 field/niche/floor/pan (only if WALK-IN) against actual selected Chrome/Black Onyx; use separate tone-confirmation for glossy vs matte, grout width, edge and niche. No drawing/field/shop/flood/supplier/GC/owner approval, email, order, or construction authorized.',
        ''
    ]
    return '\n'.join(lines)

files = {}
for room, cand in COHORT.items():
    assert not (ROOT / 'rooms' / room / 'board' / 'round-019').exists(), 'Never overwrite existing formal board'
for k in NEW_RESEARCH:
    assert not (ROOT / k).exists(), 'New research exists unexpectedly'
receipt = ROOT / 'state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json'
assert not receipt.exists()
for p, content in NEW_RESEARCH.items():
    out = ROOT / p
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding='utf-8', newline='\n')
    b = out.read_bytes()
    files[p] = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
for room, opts in COHORT.items():
    for letter, cfg in opts.items():
        p = f'rooms/{room}/board/round-019/candidates/{letter}.md'
        out = ROOT / p
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(candidate(room, letter, cfg), encoding='utf-8', newline='\n')
        b = out.read_bytes()
        files[p] = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
index = 'research/products/R019_TILE_ONLY_PUBLISHED_DCOF_2X2_POINT_WALL_AND_CHICAGO_SOURCE_INDEX.md'
assert not (ROOT/index).exists()
entry = '''# R019 blocked wet-bath tile-selection evidence — 2026-11-06

Distinct next-source focus PH-BATH3, PH-BATH4 and TX-BATH3. R018 stays source-frozen/UNSCORED and must receive formal independent pre-dispatch clearance and four authentic original specialist critiques BEFORE dispatching/scoring R019. Not an owner selection or installed shop/PO.

**Actual blocker substitutions:** PH-BATH3 source Tones Opal individual wet-wall unlisted -> sourced individual Sapphire (archived manufacturer item) or current Noho Ivory wet WALL. PH-BATH4 original Bone Ribbed wet WALL + Caviar NICHE unlisted -> flat Bone wet WALL + separately wet-listed Soho Black or Ivory NICHE. TX-BATH3 original Tones Emerald exact current product wet approval uncertain -> individually wet-listed Soho Emerald green or Noho Ivory matte WALL, separately wet-listed Sandstone or Soho Black NICHE. All bath LEVEL original Cortar Soft floors lack product-published wet DCOF -> exact Emser Capisco Trosa/Boden 12x24 Matte item-published >=0.60 for LEVEL only.

**Genuinely new POINT PAN options:** exact Emser Technique Ivory F16TECHIV1212MO 2x2 Matte 9.5mm and Source Pure White W71SOURPWH1212MO2 2x2 Matte 6mm each individually list **Shower Floor Residential YES** and **wet DCOF >0.60**, not generic family targets. 2x2 allows proposed four-plane transitions at 4in square POINT only with actual drain/mesh/backer approval. For PH3/TX3 owner unselected TUB branch, PAN N/A; WALK-IN conditional and square drain never substitutes tub waste. PH4 WALK-IN fixed.

**Board gate interpretation:** board/BOARD.md explicitly requires a published product-specific wet DCOF >=0.42, not an invented exact laboratory point. Maker DCOF >=0.60 or >0.60 is a genuine published bound; meets that narrow board criterion but does not document exact raw reading or site waterproofing/drain assembly. Product-specific current U.S. maker page = evidence of U.S. distribution; Chicago actual orderable same lot/on-hand cartons/lead = UNKNOWN. ELM public site states Chicago address; Emser official list has Bensenville IL showroom. No vendor contact.

**Historical cost:** original material-only totals PH3 $930.42, PH4 $1,352.24, TX3 $958.88 per room copy, each original 15% gross waste already ONCE. Wall/floor/niche line SF and price are exact source carried *old items* not alternative quotes. New PAN SF, substitute price, installation cost and owner per-room budget are UNKNOWN. Original entire four-unit source remains $23,572.44.

**Market evidence:** OT01-04 one 405 W Armitage development, OT05 1849 N Mohawk different Old Town Triangle property; listing text supports program only unless bath photo is visually attributable. Adjacent LP/GC explicitly secondary. No visual claims made without an inspected exact bath photo.

**Formal state:** original DESIGN worker-9 failed/not listening; original Reviewer worker-15 finished/nonrevivable. No private history role mapping or signed predecessor mutation. R019 candidate source prepared in advance of independent R018 clearance, **NOT_DISPATCHED, score NULL, championship unchanged**.
'''
o=ROOT/index
o.write_text(entry,encoding='utf-8',newline='\n')
b=o.read_bytes()
files[index]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
receipt_data={'round':19,'as_of':N,'cohort':list(COHORT),'phase':'NEXT_TILE_COHORT_SOURCE_ONLY_AWAIT_R018_AUTHORIZATION','files':files,
              'prior_R018_source_receipt':'state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json',
              'R018_status':'SOURCE_FROZEN_PREDISPATCH_NOT_CLEARED',
              'neutral_role_mapping':'NONE: all six proposed are challenger options for rooms with no incumbent champion',
              'independent_source_preflight':None,'critic_dispatch':'NOT_DISPATCHED','four_original_critic_reports':False,
              'weighted_board_scoring':None,'champions_changed':False,'owner_approval':False,'procurement_release':False,
              'historic_total_usd_four_units':'23572.44','original_15_percent_gross_applied_once':True,
              'source_and_predecessor_immutable':True}
receipt.write_text(json.dumps(receipt_data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('R019 NEW SOURCE:',len(files),'signed files, 6 neutral candidate schemes, separate maker evidence, receipt',receipt.name)
for k,v in files.items():print(k,v['bytes'],v['sha256'])
