"""Advance three genuinely differentiated, NO-PAN Duravit TUB-room A/B options.

Preparation only; no critic dispatch or selection promotion until R034 independent
Reviewer verdict. All historical states/previous critiques remain untouched.
"""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import ast,json

ROOT=Path(__file__).resolve().parents[1]
t=(ROOT/'scratch'/'r034_prepare_three_wet_bath_board.py').read_text(encoding='utf-8')
start=t.index('P={')
end=t.index('\nR={',start)
P=ast.literal_eval(t[start+2:end])
assert all(k in P for k in ('sapphire','sandstone','copper','luxe24','luxe48','riviera','perimeter','purity','antique'))
q=lambda x:x.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
R={
 'PH-BATH2':{
  'copies':'305A/305B',
  'plumbing':'Selected Duravit bathtub and Hansgrohe Matte White tub/shower fittings; NO tiled PAN, NO 4-in POINT shower drain reassignment, no tiled ceiling. Basin as selected in source plumbing; do not alter.',
  'gross':('89.7','3.67','40.2'),
  'A':{'w':'sapphire','n':'sandstone','l':'luxe24','idea':'Saturated Sapphire glossy 2x20 field with restrained Sandstone wet niche and warm 24x24 matte ivory floor; refresh premium colored-wall identity without implying OT04 matching SKU.'},
  'B':{'w':'antique','n':'purity','l':'riviera','idea':'More economical glossy Antique Blue 3x12 glazed wet wall and bright neutral La Belle niche over larger 24x48 Oat stone-like floor; more grout joints and cool/warm material tension require a deliberate client mockup.'},
  'holds':'Historic owner handoff tub alcove and individual flange/overflow rough details require native geometry. The niche 3.67 gross SF applies to complete niche faces together, never each face. Tile sill slope/waterproof profiles remain UNKNOWN.'
 },
 'TX-BATH2':{
  'copies':'205A/205B',
  'plumbing':'Selected Duravit TUB, Hansgrohe Chrome hardware; basin UNSELECTED, not inferred. NO tiled PAN, no POINT/LINEAR shower drain reallocation; ceiling not tiled.',
  'gross':('92.8','8.63','43.7'),
  'A':{'w':'copper','n':'sandstone','l':'riviera','idea':'Warm Copper glazed 2x20 vertical wet surround, lighter Sandstone recess, Oat matte 24x48 level; Chrome fixture contrast is deliberate but grout/edge cuts and warm-on-warm niche may need stronger differentiation.'},
  'B':{'w':'sapphire','n':'purity','l':'luxe24','idea':'Blue Sapphire 2x20 wet tub field with pale La Belle 3x12 niche and 24x24 matte Luxe Sand; color contrast evokes independent premium wall finish while preserving Chrome, owner-unselected basin and tub.'},
  'holds':'Source geometry and real Duravit 59-in tub versus 59.496-in approximate opening require actual native wall/finish-width verification. Niche historic 8.63 gross SF is complete niche faces collectively, not per face.'
 },
 'TX-BATH4':{
  'copies':'007A/007B',
  'plumbing':'Selected Duravit TUB, Hansgrohe Matte White. NO tiled shower PAN, no shower floor drain, no tiled ceiling; maintain actual tub flange and waste independent of tile.',
  'gross':('89.8','8.63','44.3'),
  'A':{'w':'perimeter','n':'purity','l':'riviera','idea':'Large-format graphite gray wet surround, neutral glossy Purity recess, warm Riviera Oat matte floor; reserve geometric language but niche/glass contrast must be controlled.'},
  'B':{'w':'luxe48','n':'sandstone','l':'luxe24','idea':'Warm muted ivory 24x48 wet wall, rich Sandstone wet niche and matching Luxe Sand 24x24 bath floor; brighter modern warm-organic expression with crisp Matte White tub controls, but the very pale contrast requires design review.'},
  'holds':'Historic TX-BATH4 owner tub + Hansgrohe Matte White preserved. Actual wall openings, tub spout/valve/trim routing and tile flange clearance unverified; maker 24x48 gross box piece-size gap and niche return edges held. Niche 8.63 gross SF is all faces collectively.'
 }
}
def mk_ref(key):
 x=P[key]
 return f"[{x['name']} — {x['size']}, {x['sku']}]({x['url']})"
for room,meta in R.items():
 base=ROOT/'rooms'/room/'board'/'round-035'
 target=base/'candidates'
 assert not base.exists(),(room,'round035 source already exists; do not overwrite')
 target.mkdir(parents=True,exist_ok=False)
 for letter in ('A','B'):
  k=meta[letter]
  wall,niche,level=(P[k[z]] for z in ('w','n','l'))
  gw,gn,gl=map(Decimal,meta['gross'])
  eW=q(gw*Decimal(wall['price']))
  eN=q(gn*Decimal(niche['price']))
  eL=q(gl*Decimal(level['price']))
  total=q(eW+eN+eL)
  s=f"""# R035 neutral candidate {letter} — {room}

**Strict blind neutral A/B alternative; status and historical score intentionally withheld.** Two real physical room copies: **{meta['copies']}**. All flooring quantities are historical drawing/quote gross provisional, not live Revit-certified. Actual unchanged owner plumbing: **{meta['plumbing']}**

| Actual tiled surface | Exact allowed-vendor manufacturer product/finish/rate | Independent exact use and geometry evidence |
|---|---|---|
| WET TUB WALL W1/W2/W3 | {mk_ref(k['w'])}, {wall['thick']}, **${wall['price']}/SF**, {wall['carton']}; maker/source date 2026-11-07; Elm Tones rate if applicable same-job 2026-09-04 | **{wall['use']}**. Actual tile thickness, tub flange, valve and pipe penetrations, grout/out-of-plumb returns held; no shower-ceiling approval or relief inferred. |
| Existing/conditional NICHE BACK, TWO RETURNS, HEAD and SILL collectively | {mk_ref(k['n'])}, {niche['thick']}, **${niche['price']}/SF**, {niche['carton']} | **{niche['use']}**; one historic gross niche pool shared by all faces; maker wet vertical WALL use does NOT authorize an untested horizontal positive-fall sill/waterproof and edge system. |
| Bathroom LEVEL only | {mk_ref(k['l'])}, {level['thick']}, **${level['price']}/SF**, {level['carton']} | **{level['use']}**; published wet **DCOF >=0.42** and Bathroom Floor YES independently required for exact SKU. Actual floor width, threshold and cut geometry unknown. |
| Tiled PAN / Shower drain / tiled CEILING | **N/A**; selected Duravit bathtub, independent tub flange/waste and shower/tub controls retained | No tiled shower PAN, point drain or LINEAR drain, no tiled ceiling; never price a pan as 0 SF if not in the selected program. |

**Architectural proposal:** {k['idea']} Proposed straight stack where the body is long; no offset over maker recommendation without source. WALL grout approximate 1/8 in and NICHE maker-specific 1/16–1/8 in must be separately confirmed for exact pressed/rectified edges and color; bath LEVEL 1/8 in where individually maker-listed. Owner has not signed grout, sample or final layout. A photo of a tile cannot show exact delivered shade/lot or reveal.

**Exact manufacturer context:** wet WALL is {wall['size']} {wall['thick']}, {wall['use']}; [official item]({wall['url']}). Niche is {niche['size']} {niche['thick']}, wet vertical use {niche['use']}; [official item]({niche['url']}). LEVEL is {level['size']} {level['thick']}; maker [original exact item]({level['url']}) publishes product-specific Bathroom Floor YES and wet DCOF >=0.42. If an individual Elm color order SKU is unlisted, state that identity is color/format and the factory order code is still UNKNOWN; generic collection color variants cannot qualify every finish.

**Original gross material-rate pricing, per copy only:** WET WALL **{gw} SF × ${wall['price']} = ${eW}**; complete NICHE **{gn} SF × ${niche['price']} = ${eN}**; LEVEL **{gl} SF × ${level['price']} = ${eL}**, summed **${total}/copy**. Original quote gross had the original **15% waste ONCE**. Two copies; no new 15%, no niche 5-times, no pan SF, no imported carton rounding as actual order. These prices omit trim, membranes, waterproofing, freight/tax, labor, floor substrate, field cut losses and owner's upgrades. Elm Tones ${6.95}/SF when used from exact 2026-09-04 same-job quote in inputs/TRADE_QUOTES.md; Floor & Decor store public rates **Kirkwood Atlanta GA, 2026-11-07**, not Chicago matched lot, delivery ETA or landed procurement. Budget per room **FILL IN**, not historical cost × 125% signoff.

**Separate genuinely distinct qualified families compared for EACH surface (not merely colorways):** wet WALL [Elm Tones](https://www.elmsurfaces.com/product/sapphire-tones) / [F&D La Belle](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html) / [F&D Luxe Sand 24x48](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317865.html), each individually maker Wet Areas or Shower Walls YES. Niche [Elm Tones Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) / [F&D La Belle Purity](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) / [Elm Soho Ivory](https://www.elmsurfaces.com/product/soho-ivory) wet wall-listed; full niche assembly not automatically approved. LEVEL [F&D Luxe Sand 101317949](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) / [F&D Riviera Oat 101487775](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) / [F&D Perimeter Gray 101239218](https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html), all exact maker >=0.42 wet DCOF and Bathroom Floor YES. MSI Murcia Dune [maker](https://www.msisurfaces.com/porcelain-murcia/dune/) LEVEL wet DCOF>0.42 PRICE ON REQUEST, verify exact order code; Porcelanosa Bottega [US source](https://store.porcelanosa.com/us/search/bottega) lacks verified exact 0.42 and is NOT qualified. Do not count same Tones or La Belle colors as different families. Older Daltile, Emser, Platform and Glazzio are historically ineligible.

**Source-specific architectural and field holds:** {meta['holds']} Native Revit drawing-derived measurements, niche actual aperture credit, tub clearance/flange, no visible edge sliver below approx 3in, current Chicago lots/ETA/landed price, signed owner budget, physical samples and owner selection all UNVERIFIED. Do not fabricate doors, openings or install details.

**Old Town photographic comparisons within ~$2.4M–$3.2M:** OT01 #2N 405 W Armitage genuine DRY powder photo shows patterned wallpaper/wainscot and striped contrasted floor, no verified wet WALL tile. OT04 #4S same 405 W Armitage development separately shows glossy dark green horizontal WET shower wall, tile brand, size, grout unknown; **not** independent development nor proof chosen products. OT05 bath photograph unverified; Gold Coast / Lincoln Park comps adjacent not Old Town. See allowed neutral research/comps/COMPS.md without past score material.

**No final owner approval, installed assembly release, trade order, product sample, Revit/Smartsheet write or vendor outreach.** Each specialist must score its own independently evidenced A/B 4 or 5 rubric criteria on 1–5, arithmetic one-decimal mean and source-based top_fix, gate_flags, confidence. Do not consult prior-round critics, historical scores, other seats, champion/history, ROOMS, LEDGER, private mappings or contaminated outcome aggregators.
"""
  (target/(letter+'.md')).write_text(s,encoding='utf-8')
  print(room,letter,'$',total,'bytes',len(s.encode('utf-8')),flush=True)
 print('PREPARED (not dispatched):',room)
