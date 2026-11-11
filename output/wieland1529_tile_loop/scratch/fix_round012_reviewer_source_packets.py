"""Apply exact independent Reviewer R012 pre-dispatch FIX to neutral candidate paragraphs only.
Does not modify private role keys or original source receipts; next script performs audit refreeze.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
fix={
 ('TX-PRIMARY','B'):{
 'maker':'- Exact specified wet wall: [ELM Cortar Clay Soft flat](https://www.elmsurfaces.com/product/cortar-clay) individually lists Wet Areas, whereas specified [Clay Ribbed Relief](https://www.elmsurfaces.com/product/clay-ribbed-cortar) lists Walls/Back Splashes only. Wet-wall relief application **FAIL**, flat portions **PASS**; actual v4 relief split null. Source ceiling fastening and membrane choice must be separately engineered.',
 'floor':'- Original blended Cortar Clay Soft LEVEL plus Anti-Slip LINEAR PAN source has **NO published exact SKU/finish raw wet DCOF** for either surface. Its historical $905.58 blended line is not a tested safety approval; level+pan+shared WC is one source gross pool, not separate duplicate materials.',
 'drain':'- [Brizo selected 48-in BNX LINEAR and BR73480 rough](../../plumbing.json): retained on a separately surveyed sloped pan with correct liner/membrane, body connection, flood test and threshold; no new Prime RL21 mosaic or Emser level-floor item is selected by this option. **NO PRIMARY NICHE**. Pan geometry and maker-approved installation null.',
 'gate':'**Hard-gate status:** Exact Cortar Clay Ribbed relief individual shower wet use **FAIL**, flat Clay only PASS; original Soft/Anti-Slip LEVEL and LINEAR PAN measured wet-DCOF **FAIL**; Brizo 48-in linear rough/liner/slope/finished threshold HOLD; site 1529 identity, quotes, shade lot and signed owner cap HOLD. No invented 125%-of-budget outcome.'},
 ('TX-PRIMARY','C'):{
 'maker':'- Wet field/ceiling uses ONLY individually [maker Wet Areas-listed flat Cortar Clay Soft 24x48](https://www.elmsurfaces.com/product/cortar-clay); unlisted [Clay Ribbed relief](https://www.elmsurfaces.com/product/clay-ribbed-cortar) is EXCLUDED from wet uses, not transferred maker approval. Overhead mortar, retention, waterproof seam and movement review still required.',
 'floor':'- Proposed maker-identified [Emser Capisco Trosa F08CAPITR1224M 12x24 Matte](https://www.emser.com/catalog/shop-products/material/Porcelain/capisco-f08capitr1224m) only on LEVEL main bath and TX WC shared field; maker reported DCOF >=0.60 is LOWER BOUND, exact lab point/certificate null, strict floor gate **FAIL**. Emser actual carton yield, current Chicago rate and lot null. [Exact maker study](../../../../../research/products/emser-capisco-trosa-f08capitr1224m-matte-wet-field.md).',
 'drain':'- Linear Brizo [48-in BNX / BR73480](../../plumbing.json) receives a SEPARATE [Daltile Core Fundamentals Prime RL21](../../../../../research/products/R10_EXACT_SKU_WET_USAGE_AND_CARTON_DECISION_REGISTER.md) MOSAIC conditional linear-pan study, whose manufacturer brochure gives application category/Target NOT individual numeric test. Actual order variant, measured sloped pan, membrane/liner/flood details, pack area, cost and wet lab point null. No Primary niche.',
 'gate':'**Hard-gate status:** Flat Clay exact individual wet-wall PASS; Emser level reported >=0.60 lower bound NOT tested numeric reading, strict **FAIL**; Prime RL21 exact mosaic numeric linear pan DCOF **FAIL**, system/drain/rough/slope/1529 model/owner cap/Chicago lot HOLD. No invented 125%-of-budget outcome.'},
 ('TX-BATH2','C'):{
 'maker':'- Wet tub walls use individual [ELM Tones Copper Glossy 2x20](https://www.elmsurfaces.com/product/copper-tones) maker Wet Areas PASS; original niche uses separately [Tones Sandstone 2x20 Glossy](https://www.elmsurfaces.com/product/sandstone-tones) Wet Areas PASS. The 8.63 SF quoted niche is not independently surveyed, so field face/returns/sill and trim must be measured.',
 'floor':'- Source **Cortar Clay Soft 12x24** is a LEVEL bathroom floor material with no exact raw numeric wet-DCOF lab report; strict bath-floor gate **FAIL**, not an alternate Emser or Prime pan material. Source 43.7 SF gross already contains 15% waste.',
 'drain':'- Actual selected **Duravit 700332000000090 59-in TUB** and **Hansgrohe Chrome shower controls** govern tub flange, overflow and wall waterproofing; **NO tiled shower pan, NO Brizo primary linear drain**. The sink/basin remains OWNER UNSELECTED, niche sill slopes into tub; no new fixtures.',
 'gate':'**Hard-gate status:** Copper and Sandstone individual maker wet walls PASS; original Clay Soft LEVEL exact raw numeric wet DCOF **FAIL**; installed tub flange/niche, owner basin, correct 1529 geometry, current Chicago quote/lot, material cap HOLD. Tiled shower pan = N/A. No invented 125% failure.'},
 ('TX-BATH2','A'):{
 'maker':'- Wet tub wall [Tones Copper 2x20 Glossy](https://www.elmsurfaces.com/product/copper-tones) and existing niche [Sandstone 2x20 Glossy](https://www.elmsurfaces.com/product/sandstone-tones) each individually maker Wet Areas PASS. Candidate uses centered horizontal Copper rhythm to reduce the old uncentered strip; actual grout, niche cutouts and metal trim remain null.',
 'floor':'- Maker-identified [Emser Capisco Trosa F08CAPITR1224M Matte LEVEL tile](https://www.emser.com/catalog/shop-products/material/Porcelain/capisco-f08capitr1224m) reports wet DCOF >=0.60 lower bound and commercial wet-floor suitability but NOT exact raw test/certificate; strict floor gate FAIL. Carton yield and true current quote/Chicago case stock null. [Research](../../../../../research/products/emser-capisco-trosa-f08capitr1224m-matte-wet-field.md). Original Clay Soft price is NOT Emser pricing.',
 'drain':'- Existing **Duravit 59-in TUB / Hansgrohe Chrome**, owner basin unselected; retain shower-over-tub flange-to-wet-wall waterproofing and positive niche sill fall, **NO tiled pan and no Brizo linear drain**. Reconcile level floor-to-tub apron and wood threshold from true field dimensions.',
 'gate':'**Hard-gate status:** Copper and Sandstone individual Wet Areas PASS; Emser level reported >=0.60 not raw exact measured DCOF -> strict **FAIL**; owner basin, tub flange/niche and actual 1529 cuts, new carton yield, current Chicago quote and cap HOLD. Tiled pan N/A, no invented 125% failure.'},
 ('TX-BATH4','A'):{
 'maker':'- Individual [Cortar Charcoal flat 24x48 Soft](https://www.elmsurfaces.com/product/cortar-charcoal) lists Wet Areas for tub surround (PASS); existing niche [Clara Caviar](https://www.elmsurfaces.com/product-collection/clara-collection) is listed in generic wall/floor/outdoor collection but has NO individual documented Wet Areas permission for tub niche (**FAIL**). Do not transfer approvals across makers or another finish.',
 'floor':'- Source **Cortar Bone Soft 12x24** is LEVEL floor material with accepted exact maker-SKU raw numeric wet-DCOF certificate **NULL / FAIL**. Its existing dated ELM rate and 44.3 SF gross include one 15% source waste, not another floor or pan.',
 'drain':'- Actual selected **Duravit Starck 59-in TUB and Hansgrohe MATTE WHITE** determine waterproof tub rim/flange, niche sill and floor threshold. NO tiled shower pan, no Brizo linear point or other shower drain added, no new niche. Caviar original 8.63 SF quoted allowance requires face deduction/back/returns measurement.',
 'gate':'**Hard-gate status:** Flat Charcoal tub wet-wall PASS; original Clara Caviar niche individual Wet Areas **FAIL**; Cortar Bone Soft LEVEL exact raw numeric wet DCOF **FAIL**; tub/niche survey, owner approval and exact quote/Chicago lot/installation HOLD. Shower pan N/A; no invented cost-cap gate.'},
 ('TX-BATH4','B'):{
 'maker':'- Individually maker Wet Areas-listed [Cortar Charcoal flat Soft 24x48](https://www.elmsurfaces.com/product/cortar-charcoal) tub surround plus individually wet-listed [ELM Soho Ivory 2x10 Glossy](https://www.elmsurfaces.com/product/soho-ivory) inside EXISTING original niche; original [Clara Caviar](https://www.elmsurfaces.com/product-collection/clara-collection) has no individual wet permit and is not included. [Ivory evidence](../../../../../research/products/elm-soho-ivory-2x10-glossy-tx-bath4-wet-niche.md).',
 'floor':'- Maker-identified [Emser Capisco Trosa F08CAPITR1224M 12x24 Matte](https://www.emser.com/catalog/shop-products/material/Porcelain/capisco-f08capitr1224m) replaces source Bone Soft only on LEVEL bath floor. Published maker wet DCOF >=0.60 is lower bound, NOT exact raw lab certificate; project strict floor gate **FAIL**. Actual box yield, new supply cost, installation bid and Chicago lot/ETA null.',
 'drain':'- Actual **Duravit Starck 59-in TUB / Hansgrohe Matte White** program, NO new shower pan or drain. Detail positive Ivory niche sill pitch toward tub, wet back/returns, trim/edge, tub flange and actual measured wall subtraction before any substituted material takeoff.',
 'gate':'**Hard-gate status:** Charcoal and Soho Ivory individual wet wall/niche PASS; Emser lower-bound DCOF lacks exact raw lab report, bath LEVEL FLOOR strict **FAIL**; actual 1529 niche/threshold/cut, owner sample, real project carton cost/lot/lead/material cap HOLD. Pan N/A; no 125% conclusion.'}
}
assert len(fix)==6
for (rid,letter),v in fix.items():
 f=R/'rooms'/rid/'board/round-012/candidates'/f'{letter}.md'
 body=f.read_text(encoding='utf-8');lines=body.splitlines()
 assert lines[2].startswith('This specification is a design option for independent evaluation;')
 idx=next(i for i,x in enumerate(lines) if x.startswith('## Manufacturer and material evidence'))
 assert idx+1<len(lines) and lines[idx+1]=='' and lines[idx+2].startswith('- ')
 # Replace exact room-inappropriate shared maker section, preserve downstream source quote and evidence paragraph.
 j=next(i for i in range(idx+1,len(lines)) if lines[i].startswith('## Exact quantity/waste'))
 shared=lines[idx:j]
 assert len(shared)==7,(rid,letter,shared)
 new=['## Manufacturer and material evidence','',v['maker'],v['floor'],v['drain'],shared[-2],'']
 lines=lines[:idx]+new+lines[j:]
 # Replace 1 combined boilerplate hard gate and two cross-room construction paragraphs.
 ix=next(i for i,x in enumerate(lines) if x.startswith('**Hard-gate status:**'))
 lines[ix]=v['gate']
 wix=next(i for i,x in enumerate(lines) if x.startswith('**Waterproof/install planning:**'))
 if rid=='TX-PRIMARY':
  lines[wix]='**Waterproof/install planning:** Dimension Brizo 48-in LINEAR rough, shower pan pitch and the selected manufacturer-approved liner/bonded membrane assembly, independent LEVEL+WC transition, no Primary niche, flat Clay 24x48 overhead securement, substrate flatness, joint movement, selected Black Onyx metal, actual threshold and water testing; every actual product and install section remains unapproved.'
 else:
  lines[wix]='**Waterproof/install planning:** Keep existing Duravit TUB and selected Hansgrohe metal intact; detail tub flange-to-backer waterproof transition, penetrations, niche backs/returns and positive sill fall, movement joints and sealant, field-face subtraction, measured grout/corner/edge, floor-level threshold and tub apron/vanity clearance. There is NO separately tiled shower pan or primary linear drain in this room.'
 six=next(i for i,x in enumerate(lines) if x.startswith('**Sample/render brief,'))
 metal='Brizo Black Onyx LINEAR' if rid=='TX-PRIMARY' else 'Hansgrohe Chrome with Duravit tub' if rid=='TX-BATH2' else 'Hansgrohe Matte White with Duravit tub'
 lines[six]=f'**Sample/render brief, NOT purchased/rendered:** Same-size wet field and floor sample, selected {metal} physical metal reference, calibrated W1–W3 focal elevation with grout/corner/niche cuts, tile-to-movement and waterproofing details. Draw an actual 48-in LINEAR shower membrane/pan section only for Primary, or tub flange/niche section for Bath2/Bath4. Dashed unmeasured openings/fixtures remain TBD; actual finish, current bids and owner signoff null.'
 if rid=='TX-BATH2':
  assert '3 full 20-in modules + 2 x 1.242-in' in '\n'.join(lines)
  lines=[x.replace('3 full 20-in modules + 2 x 1.242-in','2 full 20-in modules + 2 x 11.242-in') for x in lines]
 t='\n'.join(lines)+'\n'
 assert not ('TX-PRIMARY selected 48in Brizo linear' in t and rid!='TX-PRIMARY')
 f.write_text(t,encoding='utf-8')
 print(rid,letter,len(f.read_bytes()))
print('PASS corrected six R012 pre-dispatch candidate-only room-specific maker/gates/cuts; private role keys and receipt not changed yet')
