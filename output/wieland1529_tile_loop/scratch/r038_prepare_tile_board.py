"""One-time R038 neutral candidate preparation; never rerun after reviewer dispatch."""
from pathlib import Path
from decimal import Decimal
import json

ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'state'/'ROOMS.json').read_text(encoding='utf-8'))
rs={r['id']:r for r in state['rooms']}
assert len(rs)==13 and sum(x['unit_count'] for x in rs.values())==26
assert sum(len(x['carried_tile_rows']) for x in rs.values())==27
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*x['unit_count'] for x in rs.values())==Decimal('23572.44')
assert all(x['owner_status']!='approved' for x in rs.values())
assert rs['PH-BATH2']['champion_id']=='round-031-A'
assert rs['TX-BATH3']['champion_id']=='round-031-B'

R={
 'PH-BATH2':{
  'program':'Two physical 305A/305B, owner-selected Duravit 59-inch TUB and Hansgrohe Matte White, no tiled shower PAN/drain or wet overhead; retain tub waste/flange; selected basin program unchanged.',
  'areas':('89.7','3.67','40.2'),
  'geometry':'Drawing W1 4.958 ft and two assumed 2.55 ft returns, 7.75 ft tiled height, original ~35 SF bath; 59.496-inch assumed tub alcove versus nominal 59-inch tub is NOT as-built clearance.',
  'scheme':{
   'A':[
    ('Wet TUB WALL','Elm Surfaces Tones Sapphire Glossy 2x20','https://www.elmsurfaces.com/product/sapphire-tones','6.95','Maker Walls + Wet Areas YES; 8.5 mm, exact color'),
    ('Niche VERTICAL wet faces','Elm Surfaces Tones Sandstone Glossy 2x20','https://www.elmsurfaces.com/product/sandstone-tones','6.95','Maker Walls + Wet Areas YES; 8.5 mm; horizontal sill assembly unapproved'),
    ('Bathroom LEVEL','Floor & Decor Luxe Sand Matte 24x24 SKU101317949','https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html','3.49','Bathroom Floor YES; Shower Floor YES; published wet DCOF >=0.42; 8 mm rectified')],
   'B':[
    ('Wet TUB WALL','Floor & Decor Pienza Terra Matte Porcelain 24x48 SKU110850387','https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html','2.99','Shower Walls YES; Shower Floors YES; 23.59x47.30 actual, 9 mm rectified'),
    ('Niche VERTICAL wet faces','Elm Surfaces Tones Sandstone Glossy 2x20','https://www.elmsurfaces.com/product/sandstone-tones','6.95','Maker Walls + Wet Areas YES; 8.5 mm; horizontal sill assembly unapproved'),
    ('Bathroom LEVEL','Floor & Decor De Rossi Ivory Matte Porcelain 24x24 SKU100996800','https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html','6.99','Bathroom Floor YES; Shower Floor YES; published wet DCOF >=0.42; 23.50x23.50 actual, 10.5 mm rectified')]
  },
  'mapping':{'incumbent_neutral_letter':'A','new_material_challenger_neutral_letter':'B','previous_genuinely_product_board_qualified_provisional_incumbent':'round-031-A'}
 },
 'TX-BATH3':{
  'program':'Two physical 207A/207B, owner TUB versus WALK-IN UNSELECTED, Brizo Brilliance Black Onyx BNX BT062415-BNX four-inch square POINT drain ONLY if WALK-IN, never a tub waste. No tiled wet ceiling.',
  'areas':('91.8','4.89','42.5'),
  'geometry':'Drawing W1 5.1 ft and two assumed 2.6 ft returns, 7.75 ft tiled height, ~37 SF bathroom floor; source original 42.5 SF LEVEL. Optional separate WALK-IN POINT PAN additional SF/cost NULL (not zero), excluded from LEVEL.',
  'scheme':{
   'A':[
    ('Wet WALL','Floor & Decor La Belle Antique Blue High Gloss Ceramic 3x12 SKU100507706','https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html','5.56','Shower Walls YES; Shower Floors NO; 8.5 mm pressed'),
    ('Niche VERTICAL wet faces','Floor & Decor La Belle Purity High Gloss Ceramic 3x12 SKU100507722','https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html','5.56','Shower Walls YES; Shower Floors NO; horizontal sill assembly unapproved'),
    ('Bathroom LEVEL','Floor & Decor Luxe Sand Matte Porcelain 24x24 SKU101317949','https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html','3.49','Bathroom Floor YES; Shower Floors YES; wet DCOF >=0.42; 8 mm rectified')],
   'B':[
    ('Wet WALL','Elm Surfaces Cortar Charcoal FLAT Soft 24x48','https://www.elmsurfaces.com/product/cortar-charcoal','8.14','Manufacturer Walls + Wet Areas YES; 24x48 Soft flat, 9 mm; NOT ribbed relief'),
    ('Niche VERTICAL wet faces','Floor & Decor La Belle Purity High Gloss Ceramic 3x12 SKU100507722','https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html','5.56','Shower Walls YES; Shower Floors NO; horizontal sill assembly unapproved'),
    ('Bathroom LEVEL','Floor & Decor De Rossi Ivory Matte Porcelain 24x24 SKU100996800','https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html','6.99','Bathroom Floor YES; Shower Floor YES; published wet DCOF >=0.42; 10.5 mm rectified')]
  },
  'mapping':{'incumbent_neutral_letter':'A','new_material_challenger_neutral_letter':'B','previous_genuinely_product_board_qualified_provisional_incumbent':'round-031-B'}
 }
}

for rid,details in R.items():
    b=ROOT/'rooms'/rid/'board'/'round-038'
    assert not b.exists(),f'Existing R038 output must not be overwritten: {b}'
    (b/'candidates').mkdir(parents=True)
    (b/'_key.json').write_text(json.dumps({'round':38,'room':rid,**details['mapping']},indent=2)+'\n',encoding='utf-8')
    for letter,scheme in details['scheme'].items():
        rows=[]
        full=Decimal('0')
        for area,(surf,name,url,rate,gate) in zip(details['areas'],scheme):
            ext=Decimal(area)*Decimal(rate)
            full+=ext
            quote=('2026-09-04 actual 1529 trade quote' if name.startswith('Elm') else '2026-11-07 selected OUT-OF-STATE public retail, NOT Chicago')
            rows.append(f'| {surf} | [{name}]({url}) | {gate}; ${rate}/SF ({quote}) | {area} original gross SF x ${rate}/SF = ${ext.quantize(Decimal(".01"))} |')
        text=f'''# R038 neutral candidate {letter} - {rid}

**STRICT-BLIND SOURCE:** A/B identity says NOTHING about prior selection role; do not read previous rounds, mappings, state/ROOMS, LEDGER, champion/history, other critics, role-annotated research/products notes, or other room histories.

**Actual plumbing and immutable room program:** {details['program']}
**Drawing-only geometry:** {details['geometry']}

| Actual surface | Exact maker/variant/size/official URL | Product-level maker application, size and price provenance | One original gross SF pool / gross-rate extension |
|---|---|---|---|
'''+ '\n'.join(rows)+f'''

**Material-only gross area-rate illustration:** ${full.quantize(Decimal(".01"))}/physical copy, two physical copies at full-precision x2 ${(full*2).quantize(Decimal(".01"))}. Historical 15% waste ALREADY included ONCE. This is NOT carton rounded or current Chicago matched-lot freight/tax/installed price. Original 27 historical rows and $23,572.44 baseline unchanged; room budget FILL IN, zero owner approvals.

**Technical distinctions:** A maker's exact wet WALL approval is separate from horizontal niche-sill waterproofing. Bathroom LEVEL exact manufacturer wet DCOF >=0.42 and Bathroom Floor YES, not shower ceiling approval. Product wet suitability never establishes full installed flange, point drain, waterproof assembly, cuts/slivers, current matched lots, stock or lead time. {('No tiled PAN exists for selected Duravit tub.' if rid=='PH-BATH2' else 'If WALK-IN eventually selected, additional independently surveyed POINT PAN SF and cost are NULL, never double counted as bathroom LEVEL. Exact chosen LEVEL product says Shower Floors YES but installed point-pan scheme remains held.')}

**Stylistic review question:** How does this actual product composition read against verified OT01 *dry powder-only* image and OT04 glossy green *wet shower* image in the SAME 405 W Armitage development? Maker/SKU/grout of comparable unknown; OT05 bath image unverified; Lincoln Park and Gold Coast are adjacent market only. Compare selected plumbing contrast, format, grout and unit-wide distinctiveness without inventing imagery.

**At least three genuinely distinct family options for potential future comparison, NOT additional selections:** Wet wall: [Elm Cortar Charcoal flat](https://www.elmsurfaces.com/product/cortar-charcoal), [F&D Pienza Terra](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html), [F&D La Belle Antique Blue](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html). Wet vertical niche: [Elm Tones Sandstone](https://www.elmsurfaces.com/product/sandstone-tones), [F&D La Belle Purity](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html), [Elm Soho Ivory](https://www.elmsurfaces.com/product/soho-ivory) price on request. Bathroom LEVEL: [F&D Luxe Sand 24x24](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html), [F&D De Rossi 24x24](https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html), [F&D Pienza Terra 24x48](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html), [MSI Livingstyle Cream 24x24](https://www.msisurfaces.com/porcelain-livingstyle/cream/) price on request. Qualify exact chosen makers separately; NO tiled ceiling approval implied.

**Four independent specialist scoring required:** MARKET 4 criteria 0.30, DESIGN 5 criteria 0.25, BUILD 5 criteria 0.25, COST 5 criteria 0.20; each 1-5 integer evidence reasons, HALF_UP 1-decimal means, top_fix, gate_flags and confidence. No scoring or owner acceptance exists merely because this source was prepared.

**No Git, fabrication, procurement, samples, vendor contact/email, orders, Revit/Smartsheet writes, deployment or owner approval.**
'''
        (b/'candidates'/f'{letter}.md').write_text(text,encoding='utf-8')
        print(rid,letter,'gross_area_rate',full.quantize(Decimal('.01')), 'bytes',len(text.encode('utf-8')))
print('PASS: R038 two rooms/four neutral sources; two private mappings; NO specialist scores, decisions, or owner changes')
