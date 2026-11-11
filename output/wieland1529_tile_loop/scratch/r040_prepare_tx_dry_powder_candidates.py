"""Prepare R040 two-room neutral candidate sources. NO scoring/selection writes."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json

P=Path(__file__).resolve().parents[1]
decision=json.loads((P/'state/ROUND039_TWO_DRY_POWDER_DECISIONS.json').read_text(encoding='utf-8'))
assert decision['rooms']['TX-POWDER']['selected_id'] is None
assert decision['rooms']['TX-POWDER2']['selected_id']=='v4-TX-POWDER2'
Q=lambda n:n.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
data={
 'TX-POWDER':{
  'sf':Decimal('31.8'),'width':'2.99 ft / approximately 35.88 inches','numbers':'102A/102B',
  'plumbing':'Wall-mounted Hansgrohe 32526141 rough and 48140991 trim; visible faucet finish UNCONFIRMED; dry vanity wall only.',
  'A':{'maker':'Elm Surfaces','name':'Vera Forma Earth Lines Glossy Relief','size':'2x10','sku':'individual color/order code to confirm','url':'https://www.elmsurfaces.com/product/earth-lines-vera-forma','price':'8.20','basis':'2026-09-04 actual 1529 Wieland Elm quotation; glossy relief and exact dry-wall use from previous Elm product listing, current individual URL temporarily unreliable','gate':'Elm wall-series listing supports DRY vanity WALL only; exact current maker variant/lot status should be confirmed; no wet ceiling or floor permission inferred','design':'A defined linear-relief decorative wall, with warm tile presence, controlled grout and trim around wall faucet and mirror.'},
  'B':{'maker':'Floor & Decor','name':'Canvas La Belle Purity High Gloss Ceramic','size':'3x12','sku':'100507722','url':'https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html','price':'5.56','basis':'2026-11-07 public Kirkwood Atlanta GA retailer rate $1.39/piece, 0.25 SF/piece; NOT Chicago current quote','gate':'Retailer exact SKU WALL-only YES; Shower Wall YES but this room selects DRY vanity wall only; NO floor use; 8.5mm pressed edge','design':'A warm light beige high-gloss ceramic feature wall using 3x12 units; test if buyer-facing specificity matches price tier.'}
 },
 'TX-POWDER2':{
  'sf':Decimal('40.5'),'width':'3.806 ft / approximately 45.67 inches','numbers':'009A/009B',
  'plumbing':'Hansgrohe Tecturis E 73072341 DECK-mounted Brushed Black Chrome, basin UNSELECTED; dry vanity wall only.',
  'A':{'maker':'Elm Surfaces','name':'Vera Forma Indigo Edge Glossy Relief','size':'6x6','sku':'exact individual color/order code to confirm','url':'https://www.elmsurfaces.com/product/indigo-edge-vera-forma','price':'8.20','basis':'2026-09-04 actual 1529 Wieland Elm trade quotation; exact room tile maker wall listing previously confirmed','gate':'Ceramic glossy relief in Vera Forma WALL collection, DRY vanity wall only; verify current exact item listing, lot, relief trim','design':'A six-inch dimensional glossy feature field, composed around actual mirror/basin and Brushed Black Chrome deck faucet.'},
  'B':{'maker':'MSI Surfaces','name':'Stella La Perla Glossy Ceramic','size':'2x10','sku':'NSTELAPEA2X10G','url':'https://www.msisurfaces.com/porcelain-stella/la-perla-2x10/','price':None,'basis':'PRICE ON REQUEST; no usable 1529 Wieland or older exact MSI La Perla per-SF quote in inputs/TRADE_QUOTES.md; no Chicago retail price assumed','gate':'Exact MSI maker item Wall Residential YES, Commercial YES; flooring NO; 3/8-inch ceramic, glossy, nominal 2x10, pressed edge; wet-floor DCOF not applicable','design':'Pearly white glossy elongated wall tile, restrained light-reflective field; test visual differentiation and real installed cost against 6x6 relief.'}
 }
}
comps=('Authentic OT01 405 W Armitage #2N DRY powder-style image is relevant as a room-program example; '
       'OT04 #4S dark glossy-green WET shower photo is a separate use, in the SAME 405 W Armitage development, '
       'not product or maker permission. OT05 image content unverified. Lincoln Park/Gold Coast are ADJACENT, '
       'not independent Old Town design votes. TX target $2.7M; Old Town comp band ~$2.4M-$3.2M.')
options=('Three+ materially distinct third-party maker wall families for surrounding neutral comparison '
         '(not purchases): Elm Vera Forma Earth Lines 2x10 ($8.20/SF same-job trade); '
         'F&D La Belle Purity 3x12 ($5.56/SF Kirkwood GA public); '
         'MSI Stella La Perla 2x10 (PRICE ON REQUEST); '
         'Elm Haze Camel/Wheat Matte 1.6x5 ($11.93/SF same-job trade). '
         'Distinct product families, not same-family recolors.')
for rid,room in data.items():
 folder=P/'rooms'/rid/'board/round-040'
 assert not folder.exists(),str(folder)+' already exists; one-time source generator'
 for letter in ('A','B'):
  x=room[letter]
  amt=('PRICE ON REQUEST; not numerically determinable' if x['price'] is None
       else '$'+str(Q(room['sf']*Decimal(x['price'])))+'/copy')
  rate=('PRICE ON REQUEST' if x['price'] is None else '$'+x['price']+'/SF')
  text=f"""# R040 neutral {rid} candidate {letter}

**Strict blind:** These are neutral A/B source letters, not identities or roles. Two real room copies, {room['numbers']}.
**Actual fixed program:** DRY vanity WALL only; existing WOOD floor retained; no tile LEVEL, PAN, NICHE, shower or overhead. {room['plumbing']}
**Prior drawing-derived (not field-certified) W1 width:** {room['width']}; room ~9.25 ft high; actual mirror, basin and edge openings must be verified.

| Actual tiled surface | Exact permitted maker product and official URL | Maker application, size, sourced price | Original gross area-rate |
|---|---|---|---|
| ONE DRY vanity WALL W1 | [{x['maker']} {x['name']} {x['size']} ({x['sku']})]({x['url']}) | {x['gate']}; rate {rate}. Evidence: {x['basis']} | {room['sf']} source gross SF/copy x {rate} = {amt} |
| Retained WOOD floor | EXISTING WOOD | No new floor tile or wet DCOF requirement | No independent floor purchase |
| Shower PAN / NICHE / wet CEILING | None | DRY powder, no new tiled wet scope | No purchase |

**Material-only quantity/price basis:** Two physical room instances; original {room['sf']} gross SF/copy includes historical 15% waste ONCE. {amt} is purely original area-rate screen, not boxed or installed price, Chicago lot, freight or owner budget. When price is PRICE ON REQUEST, do not convert to zero or invent a total. No second waste multiplier. No basin, shower pan or tiled wood-floor replacement.

**Design hypothesis (NOT scored):** {x['design']} Evaluate alongside a distinct related TX dry powder room, actual wood flooring, faucet finish and mirror. No owner design approval or physical sample exists.

**Market provenance:** {comps}

**Three-plus family research set:** {options} No other item is selected or bought by this source pack. The four permitted vendor pool is Elm, MSI, Porcelanosa, Floor & Decor; Platform/Daltile/Emser are not new candidate vendors.

**Technical/owner gates:** Exact maker DRY-WALL use, availability, non-discontinued product, actual wall cuts/trim, selected fixture compatibility, visual design, current lot, price/installation risk, and unknown owner budget FILL IN. No wet DCOF or Shower Floor permission is needed on a dry vanity wall above retained WOOD. Owner approvals zero; manufacturer application is not full installed-release proof.

**Blind board instruction:** Four independent specialists MARKET(4 criteria .30), DESIGN(5 criteria .25), BUILD(5 criteria .25), COST(5 criteria .20); integer 1–5 ratings each tied to specific maker/comp/quote/geometry evidence, HALF_UP one-decimal means, candidate-specific top_fix/gate_flags/confidence. No weights/previous score or historical role mapping to reviewers. No external writes, procurement, account, vendor contact or Git.
"""
  target=folder/'candidates'/(letter+'.md')
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text(text,encoding='utf-8')
 key={'round':40,'room':rid,'prime_only':True}
 if rid=='TX-POWDER':
  key.update({'prior_qualified_incumbent':None,'candidate_roles':{'A':'new materially distinct family','B':'new materially distinct family'},'protective_margin_applies':False})
 else:
  key.update({'incumbent_letter':'A','challenger_letter':'B','qualified_incumbent_id':'v4-TX-POWDER2'})
 (folder/'_key.json').write_text(json.dumps(key,indent=2)+'\n',encoding='utf-8')
 print(rid,'A',room['A']['name'],'B',room['B']['name'],'source-only; zero critic files')
print('PASS prepared R040 four A/B neutral source files and two sealed keys, NO scores, no material purchases, no champion/owner revisions.')
