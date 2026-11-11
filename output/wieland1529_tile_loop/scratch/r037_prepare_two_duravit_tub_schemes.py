"""One-time R037 neutral source preparation; no scoring, no reviewer or owner claims.

Creates two truly distinct tile alternatives per selected Duravit TUB room.
Do not repeat once files exist. Source readings are limited to user-governed
existing R035 selections, currently selected manufacturer pages and geometry.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json
ROOT = Path(__file__).resolve().parents[1]
ROOMS=('TX-BATH2','TX-BATH4')
Q=lambda n:n.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
U={
 'sapphire':'https://www.elmsurfaces.com/product/sapphire-tones',
 'sandstone':'https://www.elmsurfaces.com/product/sandstone-tones',
 'purity':'https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html',
 'blue':'https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html',
 'pienza':'https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html',
 'derossi':'https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html',
 'luxe24':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html',
 'luxe48':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317865.html',
 'msiliving':'https://www.msisurfaces.com/porcelain-livingstyle/cream/',
 'msidims':'https://cdn.msisurfaces.com/files/flyers/dimensions-porcelain-flyer.pdf',
}
PRODUCTS={
 'sapphire':('Elm Surfaces Tones Sapphire Glossy Ceramic, exact color/finish 2x20, order code UNKNOWN',
            '8.5 mm / 6.50 SF per 24 pcs carton','maker Walls + Wet Areas YES; vertical tub surround only',Decimal('6.95'),'2026-09-04 actual 1529 trade quote'),
 'sandstone':('Elm Surfaces Tones Sandstone Glossy Ceramic, exact color/finish 2x20, order code UNKNOWN',
              '8.5 mm / 6.50 SF per 24 pcs carton','maker Walls + Wet Areas YES for vertical niche; sill assembly separate',Decimal('6.95'),'2026-09-04 actual 1529 trade quote'),
 'purity':('Floor & Decor La Belle Purity High Gloss Ceramic SKU100507722, 3x12',
           '8.5 mm pressed; 0.25 SF/piece; 48-piece carton','Shower Walls YES, Shower Floors NO; vertical niche only',Decimal('5.56'),'2026-11-07 Kirkwood Atlanta public retail'),
 'blue':('Floor & Decor La Belle Antique Blue High Gloss Ceramic SKU100507706, 3x12',
         '8.5 mm pressed; 0.25 SF/piece; 48-piece carton','Shower Walls YES, Shower Floors NO; wet tub WALL only',Decimal('5.56'),'2026-11-07 Kirkwood Atlanta public retail'),
 'pienza':('Floor & Decor Pienza Terra Matte Porcelain SKU110850387, 24x48 nominal',
           '23.59x47.30 actual, 9 mm rectified, 2 pcs / 15.50 SF carton','Shower Walls YES; Bathroom Floor YES; Shower Floor YES; wet DCOF >=0.42',Decimal('2.99'),'2026-11-07 West Des Moines Iowa public retail'),
 'derossi':('Floor & Decor De Rossi Ivory Matte Porcelain SKU100996800, 24x24 nominal',
            '23.50x23.50 actual, 10.5 mm rectified, 3 pcs / 11.64 SF carton','Bathroom Floor YES; Shower Floor YES; wet DCOF >=0.42',Decimal('6.99'),'2026-11-07 Camelback Phoenix AZ public retail (store-dependent)'),
 'luxe24':('Floor & Decor Luxe Sand Matte Porcelain SKU101317949, 24x24 nominal',
           '23.70x23.70 actual, 8 mm rectified, 4 pcs / 15.52 SF carton','Bathroom Floor YES; Shower Floor YES; wet DCOF >=0.42',Decimal('3.49'),'2026-11-07 Kirkwood Atlanta public retail'),
 'luxe48':('Floor & Decor Luxe Sand Matte Porcelain SKU101317865, 24x48 nominal',
           'approximately 8 mm rectified, 2 pcs / 15.50 SF carton','Shower Walls YES, distinct size/SKU from 24x24 LEVEL',Decimal('3.99'),'2026-11-07 Kirkwood Atlanta public retail'),
}
spec={
 'TX-BATH2':dict(instances='205A/205B',plumbing='Owner-selected Duravit 59-in BATHTUB with Hansgrohe Chrome; basin UNSELECTED; NO tiled PAN, POINT drain or wet ceiling. Actual tub waste/overflow preserved.',
    areas=('92.8','8.63','43.7'),proposals={'A':('pienza','sandstone','derossi'),'B':('sapphire','purity','luxe24')},
    design={'A':'Warm stone-look 24x48 tub wall and ivory terrazzo-look 24x24 bath LEVEL, bounded Sandstone gloss niche, Chrome contrasts; visually materially different from a saturated Sapphire wall.',
            'B':'Glossy saturated Sapphire 2x20 tub wall, pale glossy La Belle niche, quiet matte ivory 24x24 floor. Richer color but smaller wall format; project-wide contrast must be compared with other TX baths.'},
    extra='Drawing W1 approximately 62.484 in conflicts a 59.496-in assumed opening and nominal 59-in tub. Actual finished tub installation width, flange, niches and penetrations unresolved.'),
 'TX-BATH4':dict(instances='007A/007B',plumbing='Owner-selected Duravit 59-in BATHTUB with Hansgrohe Matte White; NO tiled PAN, POINT drain or wet ceiling. Actual tub waste/overflow preserved.',
    areas=('89.8','8.63','44.3'),proposals={'A':('luxe48','sandstone','luxe24'),'B':('blue','purity','pienza')},
    design={'A':'Quiet tonal Luxe Sand 24x48 wet surround and matching-brand 24x24 ivory bath LEVEL (distinct exact SKUs), warm Sandstone 2x20 gloss niche. Matte White fittings blend with pale warm field.',
            'B':'Expressive La Belle Antique Blue 3x12 high gloss wet tub surround and Purity niche with warm matte Pienza 24x48 LEVEL; white tub trim graphic. Blue could duplicate TX-BATH3 emphasis, so unit-level differentiation must be judged.'},
    extra='~60-inch nominal tub alcove wall vs actual Duravit 59-inch envelope not physical fit evidence; actual flange, finished openings and bath LEVEL edges unresolved.'),
}
state=json.loads((ROOT/'state'/'ROOMS.json').read_text(encoding='utf-8'))
assert (len(state['rooms']),sum(r['unit_count'] for r in state['rooms']),
        sum(len(r['carried_tile_rows']) for r in state['rooms']))==(13,26,27)
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit']))*r['unit_count']
           for r in state['rooms'])==Decimal('23572.44')
for rid in ROOMS:
    s=spec[rid]
    room=next(r for r in state['rooms'] if r['id']==rid)
    assert room['status']=='provisional champion' and room['owner_status'] is None
    assert room['champion_id']==('round-031-B' if rid=='TX-BATH2' else 'round-035-B')
    assert s['instances'] and all((ROOT/'rooms'/rid/n).is_file() for n in ('geometry.json','plumbing.json'))
    rdir=ROOT/'rooms'/rid/'board'/'round-037'
    out=rdir/'candidates'
    for letter in ('A','B'):
        assert not (out/(letter+'.md')).exists(),(rid,letter,'prior candidate exists')
    assert not (rdir/'_key.json').exists(),(rid,'sealed mapping exists')
for rid in ROOMS:
    s=spec[rid]; out=ROOT/'rooms'/rid/'board'/'round-037'/'candidates'
    out.mkdir(parents=True,exist_ok=True)
    for letter,items in s['proposals'].items():
        data=[f'# R037 neutral candidate {letter} - {rid}','',
              '**STRICT BLIND NEUTRAL A/B SOURCE:** historical product roles and scores are withheld. Specialists must not open earlier rounds, _key.json, room champion/history, state/ROOMS.json, LEDGER, other critic reports or outcome-contaminated research/products notes. A/B role is unknown to specialists.','',
              f'**Two actual physical instances:** {s["instances"]}. **Selected immutable room program:** {s["plumbing"]} Geometry and actual finished openings in own geometry.json/plumbing.json are drawing-source not field measured.','',
              '| Actual surface | Exact eligible vendor/product/official manufacturer URL | Size, carton, wet-use permission and applicable price | Gross source SF and material RATE extension |',
              '|---|---|---|---|']
        total=Decimal('0')
        for label,key,area in zip(('WET TUB WALL','One combined NICHE all-face pool (vertical tile only)','Bathroom LEVEL only'),items,s['areas']):
            desc,pack,permit,rate,price_source=PRODUCTS[key]
            ext=Decimal(area)*rate
            total+=ext
            data.append(f'| {label} | [{desc}]({U[key]}) | {pack}; **{permit}**; **${rate}/SF** ({price_source}) | **{area} SF x ${rate}/SF = ${Q(ext)}** |')
        data+=['',
           f'**Material-only original gross area-rate total:** **${Q(total)}/physical copy**; **${Q(total*2)}/two copies**. Original room gross SF already includes **historical 15% waste ONCE**. This is not a carton-rounded, landed, installed or Chicago matched-lot quote. No secondary 15%, no doubled NICHE, no invented tiled PAN or floor drain. Three true source pools wall/niche/LEVEL only.',
           '',
           '**Architectural new composition / evaluation:** '+s['design'][letter],
           '',
           '**Technical hard gates:** individual named maker wet-area permission for actual tub WALL; exact LEVEL published wet DCOF >=0.42 and Bathroom Floor YES, no discontinued product or high-severity selected-plumbing finish clash. Niche published vertical Shower Walls YES/Wet Areas DOES NOT establish horizontal sill pitch, waterproof penetration, liner/edge detail or factory system. No tub floor PAN, POINT shower drain, or tiled ceiling in actual room program. Manufacturer use is not installed assembly clearance.',
           '',
           '**Source price hierarchy:** Elm Tones 2x20 exact 1529 Wieland quote dated 2026-09-04, $6.95/SF; F&D amounts are selected non-Chicago store public prices observed 2026-11-07. MSI/Porcelanosa current missing prices must be PRICE ON REQUEST, not arbitrary historical order allocation. The ELM Cortar-specific 10–12-week lead and 300-SF minimum are NOT evidenced as Tones terms. Chicago matched lots, inventory, ETA, freight/tax, installed pricing and owner room tile budget **FILL IN**; owner approval **NONE**.',
           '',
           '**Own-room geometry and fixture holds:** '+s['extra']+' Native measured openings/field cut map, ≥3-in exposed edges, grout spec, wet-tub flange, waterproofed horizontal niche sill, manufacturer setting coverage/flatness and transitions are not completed. No unproven infeasibility asserted.',
           '',
           '**Comparable photo discipline:** OT01 405 W Armitage #2N = authenticated DRY powder patterned walls/wainscot, NOT wet tub tile evidence; OT04 405 W Armitage #4S = authenticated glossy deep-green WET shower wall in different unit SAME DEVELOPMENT, no maker/SKU/DCOF evidenced; not two independent developments. OT05 bathroom image UNKNOWN; adjacent Gold Coast/Lincoln Park secondary. Market PH target $2.8M, TX target $2.7M, band ~$2.4M–$3.2M.',
           '',
           '**Genuine third-family options per surface for open maker comparison only, not selected here:** WET TUB WALL [Elm Tones Sapphire]('+U['sapphire']+') / [F&D Pienza Terra 24x48]('+U['pienza']+') / [F&D La Belle Antique Blue 3x12]('+U['blue']+') / [F&D Luxe Sand 24x48]('+U['luxe48']+'); NICHE [Elm Tones Sandstone]('+U['sandstone']+') / [La Belle Purity]('+U['purity']+') / [Elm Soho Ivory](https://www.elmsurfaces.com/product/soho-ivory) (exact wet vertical permission only, PRICE ON REQUEST); bath LEVEL [F&D Luxe Sand 24x24]('+U['luxe24']+') / [F&D De Rossi Ivory 24x24]('+U['derossi']+') / [Pienza Terra 24x48]('+U['pienza']+') / [MSI Livingstyle Cream 24x24 NLIVSTYCRE2424]('+U['msiliving']+') / [MSI Dimensions Glacier 24x48 NDIMGLA2448-N]('+U['msidims']+'); MSI floor source DCOF>0.42 but independent Shower Floor YES not established; no PAN in actual TUB room. Avoid treating distinct colors within Tones as different families.',
           '',
           '**Review:** four independent real blind specialists MARKET .30 (4 evidenced 1–5 criteria), DESIGN .25 (5), BUILD .25 (5), COST .20 (5) per A/B; 1-decimal HALF_UP means, all individual seat means >=3.0; top_fix, gate_flags, confidence. No critic may see this round private _key.json, previous scores/role/history or other seats. Manufacturer hard gates override weighted score. The +0.250 displacement rule applies only to a product-gate-qualified previously selected scheme; no failing scheme is protected.',
           '',
           '**No procurement, samples, vendor outreach, owner signoff, Revit/Smartsheet write, Git or installation/fabrication.**']
        (out/(letter+'.md')).write_text('\n'.join(data)+'\n',encoding='utf-8')
    incumbent='B' if rid=='TX-BATH2' else 'A'
    role={'round':37,'room':rid,'private_only':True,
          'previous_board_qualified_incumbent':next(r for r in state['rooms'] if r['id']==rid)['champion_id'],
          'incumbent_letter':incumbent,'new_challenger_letter':'A' if incumbent=='B' else 'B',
          'blind_reviewers_may_read_this':False,
          'scoring_note':'Use same-round original mean and true manufacturer gate; +0.250 only qualifies defended incumbent',
          'owner_approved':False}
    (ROOT/'rooms'/rid/'board'/'round-037'/'_key.json').write_text(json.dumps(role,indent=2)+'\n',encoding='utf-8')
    print(rid, [(letter,'/'.join(s['proposals'][letter])) for letter in ('A','B')])
print('PASS: four substantive neutral R037 candidates, two prime-only keys, two selected Duravit tub rooms; no scoring or selection changes.')
