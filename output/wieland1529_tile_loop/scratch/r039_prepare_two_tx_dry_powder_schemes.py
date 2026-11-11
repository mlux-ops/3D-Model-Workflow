"""One-time R039 role-neutral dry-wall board source, after independent R038 CONTINUE only for scoring."""
from pathlib import Path
from decimal import Decimal
import json
P=Path(__file__).resolve().parents[1]
d=json.loads((P/'state/ROOMS.json').read_text(encoding='utf8'))
R={x['id']:x for x in d['rooms']}
assert len(R)==13 and sum(x['unit_count'] for x in R.values())==26
assert sum(len(x['carried_tile_rows']) for x in R.values())==27
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*x['unit_count'] for x in R.values())==Decimal('23572.44')
assert all(x['owner_status']!='approved' for x in R.values())
SCHEMES={
 'TX-POWDER':{
  'id':'round-003-B','geometry':'102A/102B W1 2.99 ft from drawing, room 22.5 SF prior area; field wall openings/mirror not live-verified.',
  'plumbing':'DRY powder vanity wall with wall-mounted Hansgrohe faucet rough, visible finish UNCONFIRMED; wood flooring retained. No tile LEVEL, PAN, NICHE or wet ceiling.',
  'area':'31.8',
  'A':('Elm Surfaces Haze Camel + Wheat 70/30 Matte 1.6x5','https://www.elmsurfaces.com/product/haze-camel','11.93','2026-09-04 actual same-job trade quotation, individual colors combined on one line, 70/30 not ordered','Dry WALL only; paired mix; no shower-floor or wet overhead permission inferred'),
  'B':('Floor & Decor Pienza Terra Matte Porcelain 24x48 SKU110850387','https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html','2.99','2026-11-07 published OUT-OF-STATE public retail, NOT Chicago exact current lot','Maker Floor/Wall YES and Shower Walls YES; DRY wall use only, 9 mm rectified, actual 23.59x47.30'),
 },
 'TX-POWDER2':{
  'id':'v4-TX-POWDER2','geometry':'009A/009B W1 3.806 ft from drawing, room 27 SF prior area; mirror/faucet clearances not live-verified.',
  'plumbing':'DRY powder vanity wall, Hansgrohe Tecturis E deck-mounted faucet SKU73072341 Brushed Black Chrome, basin UNSELECTED. WOOD flooring retained. No tiled LEVEL/PAN/NICHE/CEILING.',
  'area':'40.5',
  'A':('Elm Surfaces Vera Forma Indigo Edge Glossy Relief 6x6','https://www.elmsurfaces.com/product/indigo-edge-vera-forma','8.20','2026-09-04 actual same-job Elm trade quotation','Dry WALL only, 8.6 mm quoted; relief profile, mirror and basin interfaces unverified'),
  'B':('Elm Surfaces Tones Sandstone Glossy Ceramic 2x20','https://www.elmsurfaces.com/product/sandstone-tones','6.95','2026-09-04 actual same-job Elm trade quote, color/variant exact, individual order code UNKNOWN','Maker Walls + Wet Areas YES, but DRY powder vanity wall is the ONLY selected use, no floor or ceiling; 8.5 mm'),
 }
}
for rid,z in SCHEMES.items():
    x=R[rid]
    assert x['champion_id']==z['id'] and x['status']=='provisional champion'
    b=P/'rooms'/rid/'board/round-039'
    assert not b.exists(),rid
    (b/'candidates').mkdir(parents=True)
    (b/'_key.json').write_text(json.dumps({'round':39,'room':rid,'incumbent_letter':'A','challenger_letter':'B','qualified_incumbent_id':z['id'],'prime_only':True},indent=2)+'\n',encoding='utf8')
    for letter in 'AB':
        name,url,rate,origin,allowed=z[letter]
        amt=Decimal(z['area'])*Decimal(rate)
        (b/'candidates'/(letter+'.md')).write_text(f'''# R039 neutral {rid} candidate {letter}

**Strict blind neutral letter:** no previous score, accepted role or historical identity disclosed. Actual unit type Triplex; two physical room copies.

**Immutable owner plumbing/program:** {z['plumbing']}
**Drawing-derived geometry:** {z['geometry']}

| Actual tiled surface | Exact maker/item/official URL | Use/size, price source and gate evidence | Original gross material-only source rate |
|---|---|---|---|
| ONE DRY vanity WALL only | [{name}]({url}) | {allowed}; **$ {rate}/SF**; {origin} | {z['area']} gross SF/copy x $ {rate}/SF = $ {amt.quantize(Decimal(".01"))}/copy |
| WOOD FLOOR retained | EXISTING WOOD | No floor tile, no wet DCOF test and no duplicate material purchase | N/A |
| Shower PAN / NICHE / wet CEILING | None selected | This is a powder WC, not a shower; manufacturer wet wall permission is irrelevant to an unbuilt shower | N/A |

**Original material-only comparison:** $ {amt.quantize(Decimal(".01"))} per physical room, two copies $ {(amt*2).quantize(Decimal(".01"))} at gross original area-rate; 15% waste already included ONCE in source gross area. No extra 15%, no separate powder-floor tile, no hypothetical niche or PAN. **Room budget FILL IN**; no Chicago matched lot, tax, freight, carton-rounded final order or installation cost verified. The historical 13-room/26-copy/27-row $23,572.44 original baseline must not change.

**Design question:** Actual authentic OT01 405 W Armitage #2N is a DRY powder-style image with contrasted wall and floor treatments; it is NOT a shower precedent. Actual OT04 405 W Armitage #4S is a glossy green WET shower from the SAME development and is NOT powder tile SKU proof. OT05 interior bath image unverified. Adjacent Gold Coast/Lincoln Park are labeled adjacent-market, not Old Town. Evaluate against target Triplex ~ $2.7M, Old Town ~$2.4–$3.2M, correct fixture finish and another TX powder room without inferring exact comparable tile maker.

**At least three materially distinct wall families available to inspect separately, not additional proposed purchases:** [{name}]({url}); [Floor & Decor La Belle Purity high gloss 3x12](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html), price $5.56/SF public OUT-OF-STATE; [MSI Stella La Perla 2x10](https://www.msisurfaces.com/porcelain-stella/la-perla-2x10/), PRICE ON REQUEST; [Elm Vera Forma Earth Lines 2x10](https://www.elmsurfaces.com/product/earth-lines-vera-forma), $8.20/SF actual 2026-09-04 same-job quote. Same-family color variants do not count as independent families.

**Hard gates/holds:** Individual maker DRY wall permission (not wet tile ceiling), manufacturer availability/discontinuation, actual mirror/faucet/basin, real wall opening/edge cuts, owner do-not-use list currently blank, current lot and budget. No floor or PAN slip test applies. Selection and full installed assembly remain PROVISIONAL; no owner approved colors, samples or orders.

**Blind board:** Original four separate MARKET(4 criteria .30), DESIGN(5 .25), BUILD(5 .25), COST(5 .20), all 1–5 integer reasoned ratings, HALF_UP one-decimal means, top_fix/gate_flags/confidence. Do not read roles, private mapping, older scores/critics or state/ROOMS/LEDGER. No Git, purchase, email, vendor contact, Revit/Smartsheet write, deployment or fabrication.
''',encoding='utf8')
        print(rid,letter,name,amt.quantize(Decimal('.01')))
print('PASS R039 neutral two TX dry powder candidates each; existing wood floors, actual plumbing, 0 owner approvals; NO scoring or outcome.')
