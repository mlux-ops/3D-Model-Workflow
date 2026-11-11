"""Author unbiased A/B exact-product current-board packets for PH-BATH4/PH-BATH3/TX-BATH3.

Run once. Never overwrite source A/B after four independent critics begin.
Historical candidate scores/incumbent status are deliberately NOT exposed.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
import json

ROOT=Path(__file__).resolve().parents[1]
Q=lambda x: Decimal(x).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)

P={
 "perimeter":{"name":"Floor & Decor Perimeter Gray Matte Porcelain","size":"24x48 nominal; calibrated dimensions held","sku":"101239218","thick":"9 mm rectified","price":"3.99","carton":"15.50 SF / 2 tiles; $61.84 per carton","url":"https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html","use":"Shower Walls YES; Bathroom Floor YES; separate Shower Floor YES; published wet DCOF >=0.42","joints":"vendor suggested 1/16, 1/8, 3/16 in"},
 "luxe24":{"name":"Floor & Decor Luxe Sand Matte Porcelain","size":"24x24 nominal; 23.70x23.70 actual","sku":"101317949","thick":"8 mm rectified","price":"3.49","carton":"15.52 SF / 4 tiles; $54.08 per carton","url":"https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html","use":"Bathroom Floor YES; separate Shower Floor YES; wet DCOF >=0.42","joints":"vendor suggested 1/16, 1/8, 3/16 in"},
 "luxe48":{"name":"Floor & Decor Luxe Sand Matte Porcelain","size":"24x48 nominal","sku":"101317865","thick":"approximately 8 mm rectified","price":"3.99","carton":"15.50 SF / 2 tiles; $61.84 per carton","url":"https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317865.html","use":"Exact SKU Shower Walls YES; bath floor and Shower Floor YES; wet DCOF >=0.42, but here used only on wet WALL","joints":"confirm exact vendor joint recommendation against current size-specific spec"},
 "riviera":{"name":"Floor & Decor Riviera Oat Matte Porcelain","size":"24x48 nominal; 23.58x47.28 actual","sku":"101487775","thick":"8 mm rectified","price":"3.99","carton":"16.00 SF / 2 tiles; $63.84 per carton","url":"https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html","use":"Bathroom Floor YES; independently Shower Floor YES; published wet DCOF >=0.42","joints":"vendor suggested 1/16, 1/8, 3/16 in"},
 "purity":{"name":"Floor & Decor La Belle Purity High Gloss Ceramic","size":"3x12","sku":"100507722","thick":"8.5 mm pressed","price":"5.56","carton":"priced $1.39/piece at 0.25 SF/piece; case rounding unresolved","url":"https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html","use":"Shower Walls YES; Shower Floors NO; wet niche vertical faces only pending sill/waterproof assembly","joints":"maker joint recommendation must be rechecked for this exact pressed SKU"},
 "antique":{"name":"Floor & Decor La Belle Antique Blue High Gloss Ceramic","size":"3x12","sku":"100507706","thick":"8.5 mm pressed","price":"5.56","carton":"priced $1.39/piece at 0.25 SF/piece; case rounding unresolved","url":"https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html","use":"Shower Walls YES; Shower Floors NO","joints":"maker joint recommendation must be rechecked for this exact pressed SKU"},
 "sapphire":{"name":"Elm Surfaces Tones Sapphire Glossy","size":"2x20","sku":"exact color/variant; public standalone order SKU not established","thick":"8.5 mm maker/quote","price":"6.95","carton":"6.50 SF / 24 tiles; 2026-09-04 same-job quote","url":"https://www.elmsurfaces.com/product/sapphire-tones","use":"Specific maker page Walls + Wet Areas YES; not floor or ceiling","joints":"proposed aligned low-contrast 1/8 in; verify maker joint and lippage"},
 "sandstone":{"name":"Elm Surfaces Tones Sandstone Glossy","size":"2x20","sku":"exact color/variant; public standalone order SKU not established","thick":"8.5 mm maker/quote","price":"6.95","carton":"6.50 SF / 24 tiles; 2026-09-04 same-job quote","url":"https://www.elmsurfaces.com/product/sandstone-tones","use":"Specific maker page Walls + Wet Areas YES; niche wet-wall faces only; assembly unqualified","joints":"proposed aligned low-contrast 1/8 in; verify maker joint and lippage"},
 "copper":{"name":"Elm Surfaces Tones Copper Glossy","size":"2x20","sku":"exact color/variant; public standalone order SKU not established","thick":"8.5 mm maker/quote","price":"6.95","carton":"6.50 SF / 24 tiles; 2026-09-04 same-job quote","url":"https://www.elmsurfaces.com/product/copper-tones","use":"Specific maker page Walls + Wet Areas YES; not ceiling or floor","joints":"proposed aligned low-contrast 1/8 in; verify maker joint and lippage"},
 "emerald":{"name":"Elm Surfaces Tones Emerald Glossy","size":"2x20","sku":"exact color/variant; public standalone order SKU not established","thick":"8.5 mm maker/quote","price":"6.95","carton":"6.50 SF / 24 tiles; 2026-09-04 same-job quote","url":"https://www.elmsurfaces.com/product/emerald-tones","use":"Individual maker Walls + Wet Areas (must revalidate exact page during four-seat maker check); not floor/ceiling","joints":"proposed aligned low-contrast 1/8 in; verify maker joint and lippage"}
}

R={
 "PH-BATH4":{
  "ids":"311A / 311B","program":"Owner WALK-IN selected, Brizo Roccesco Brilliance Black Onyx (BNX), 4-in square POINT BT062415-BNX. NO tub and NO tiled ceiling.",
  "areas":{"wall":"107.2","niche":"8.63","level":"40.2"},
  "branches":"Only shower branch: LEVEL and actual four-plane installer-cut POINT PAN use the same exact floor SKU, but original 40.2 gross SF combines the existing floor+pan and cannot be double counted. Actual pan net/boundary/centerline must be measured before an order.",
  "a":{"wall":"perimeter","niche":"purity","level":"luxe24","grout":"Wall vertical straight stack medium gray 1/8 in; niche pale-beige vertical 3x12 proposed 1/16 in; level/pan 1/8 in warm neutral.","idea":"Graphite matte field, luminous pale niche and warm-ivory monolithic shower floor. Matches BNX visually but graphite/ivory contrast may read more generic than a material-specific warm composition."},
  "b":{"wall":"luxe48","niche":"sandstone","level":"riviera","grout":"Wall warm-ivory 24x48 vertical straight stack 1/8 in suggested pending SKU maker joint; niche 2x20 glazed Sandstone proposed 1/8 in; Riviera Oat floor/pan neutral 1/8 in.","idea":"Warmer and calmer hospitality-style alternative with light-reflective Sandstone recess and Oat ground; avoids cool gray field but requires two-source F&D/Elm lots and robust warm-on-warm grout contrast."},
  "special":"Owner 35 SF vs prior 27 SF floor conflict; W1 5 ft, W2/W3 2.54 ft and 9.25 ft height are drawings, not certified native. Niche original 8.63 gross SF is ALL five faces together; subtract measured wall opening once, not add 8.63 per face. Four-plane Brizo POINT-pan cut >=3in edge, grate/rough/tile-in depth, positive sill fall, waterproof return, 9mm/8.5mm profiles or 8mm/8.5mm needs coordination."
 },
 "PH-BATH3":{
  "ids":"307A / 307B","program":"Owner TUB versus WALK-IN NOT selected; basin NOT selected; Hansgrohe Chrome selected. Delta Chrome DT062412 square POINT applies to WALK-IN only, NEVER tub waste. No tiled ceiling.",
  "areas":{"wall":"86.2","niche":"8.63","level":"40.2"},
  "branches":"TUB branch: LEVEL only, no tiled PAN; tub model/flange/waste not assumed. WALK-IN branch: separate real-measured added POINT PAN quantity/cost is NULL, use exact chosen FLOOR SKU only if individual Shower Floor YES+DCOF>=0.42. Original LEVEL 40.2 gross never silently covers unmeasured new WALK-IN PAN.",
  "a":{"wall":"sapphire","niche":"sandstone","level":"luxe24","grout":"Sapphire horizontal straight stack and subtly contrasting Sandstone niche; grout proposed 1/8 in maker confirmation; Luxe Sand floor 1/8 in.","idea":"Saturated cool-blue jewel accent on Chrome hardware; warm Sandstone niche and ivory floor balance intensity."},
  "b":{"wall":"copper","niche":"sandstone","level":"riviera","grout":"Copper glazed 2x20 vertical aligned field, pale Sandstone niche; 1/8 in proposed; Riviera Oat large-format 24x48 floor/pan 1/8 in maker option.","idea":"Warm copper/ochre wall with pale Oat ground emphasizes tactile Old Town-inspired glaze without claiming the comparable uses this material; Chrome becomes a crisp counterpoint. More warm-toned than Sapphire and a longer floor tile; tile shade/color must be physically reviewed."},
  "special":"Floor 35 SF and W1 5 ft/W2/W3 2.33 ft/tile height 7.75 ft are drawings; niches measured aperture absent. Basin and TUB/WALK-IN remain owner choices; cannot put Delta POINT tile-in drain in TUB. Four-plane installer-cut POINT PAN only if WALK-IN, separate source-independent measured SF and cuts >=3in. No added waste to historical gross."
 },
 "TX-BATH3":{
  "ids":"207A / 207B","program":"Owner TUB versus WALK-IN not confirmed; Brizo Roccesco Brilliance Black Onyx selected; 4-in square BNX POINT BT062415-BNX WALK-IN only; TUB branch NO shower PAN.",
  "areas":{"wall":"91.8","niche":"4.89","level":"42.5"},
  "branches":"TUB: retaining surround/niche and tile LEVEL, no shower PAN or invented tub waste. WALK-IN: separately measured conditional installer-cut BNX POINT PAN added beyond historic LEVEL gross, area/dollars NULL; exact LEVEL SKU must independently be Shower Floor YES+DCOF>=0.42.",
  "a":{"wall":"antique","niche":"purity","level":"luxe24","grout":"Antique Blue 3x12 horizontal straight stack, warm ivory niche, low-contrast grout confirmed at maker sizing; Luxe Sand aligned 24x24.","idea":"Blue-glaze modern accent with bright contrasting niche, warm matte ivory grounding and BNX dark metal graphic contrast. Expansive joint rhythm vs long 2x20."},
  "b":{"wall":"emerald","niche":"sandstone","level":"riviera","grout":"Emerald Tones 2x20 gloss horizontal aligned wet wall, Sandstone 2x20 vertical niche, muted grout 1/8 in proposed pending maker, warm Riviera Oat large-format LEVEL/conditional PAN.","idea":"Deep glazed green direct visual design response to OT04 #4S observed wet-shower wall at the same 405 W Armitage development (NOT an identical SKU/format), beside black BNX; warm muted niche/floor support rather than copying tile identity."},
  "special":"Drawing room identifiers 207A/B; assumed bath floor 37 SF and unverified wet wall dimensions. Niche existing gross 4.89 SF is all faces combined; measured opening/returns/sill/trim and waterproofing unknown. Existing Smartsheet POINT note refers to walk-in, v4 describes tub; owner TUB/WALK-IN unresolved despite source clash. No imaginary walk-in pan SF, slope or added wastage."
 }
}
SOURCES={
 "oldtown":"OT01 #2N 405 W Armitage attributable DRY powder photo has wallpaper/wainscot/graphic floor; OT04 #4S same building WET shower photo has glossy deep green horizontal courses but NO verified tile maker/size/finish, grout or date; OT02/03 are same development without separately verified baths; OT05 bathroom photograph unverified. Lincoln Park/Gold Coast are secondary, not Old Town. See research/comps/R030_AUTHENTIC_OLD_TOWN_PHOTOGRAPHIC_EVIDENCE_20261107.md. Compare PH ~$2.8M and TX ~$2.7M within ~$2.4M-$3.2M range.",
 "cost":"All gross source areas are legacy quote carry-forward with original 15% waste ONCE. Elm rates from 1529 same-job 2026-09-04 quote (inputs/TRADE_QUOTES.md); F&D rates public Kirkwood Atlanta GA observed 2026-11-07, NOT Chicago matching lot/availability/quote, ETA or landed supply. Owner room budget FILL IN; 125%-of-historic arithmetic does NOT establish signed owner cap. No tax/freight/setting/trim/labor quoted.",
}
def link(k):
 x=P[k]
 return f"[{x['name']} {x['size']} {x['sku']}]({x['url']})"
assert len(R)==3
for id,meta in R.items():
 path=ROOT/'rooms'/id/'board'/'round-034'/'candidates'
 path.mkdir(parents=True,exist_ok=True)
 for letter in ('a','b'):
  cand=meta[letter]
  assert (path/(letter.upper()+'.md')).exists()==False,(id,letter,'DO NOT OVERWRITE BLIND SOURCE')
  wall,niche,level=(P[cand[k]] for k in ('wall','niche','level'))
  amounts={k:Decimal(meta['areas'][k])*Decimal(x['price']) for k,x in [('wall',wall),('niche',niche),('level',level)]}
  cost=sum(amounts.values())
  s=[f"# R034 neutral candidate {letter.upper()} — {id}",
   "",
   "**Strict blind, independently developed tile option.** Status, previous round, prior score, winning role, other critics, private mapping and accepted-incumbent identities are intentionally absent. Product and geometry evidence below is equally scoped for A and B. Critic may read ONLY this room's R034 candidate folder, OWN geometry/plumbing, four governance docs in required order, permitted product maker pages and neutral photographic comparable research without historical scoring.",
   "",
   f"**Physical project copies:** {meta['ids']}. **Plumbing/program:** {meta['program']}",
   "",
   "| Actual surface | Exact product / maker / SKU / size / price | Separate product-level suitability / construction boundary |",
   "|---|---|---|",
   f"| WET WALL field | {link(cand['wall'])}; {wall['thick']}; **${wall['price']}/SF**; {wall['carton']} | {wall['use']}. Wall/grout/opening geometry, bonding and waterproofing must still be field-coordinated. |",
   f"| Existing or conditional wet NICHE back/returns/top/sill | {link(cand['niche'])}; {niche['thick']}; **${niche['price']}/SF**; {niche['carton']} | {niche['use']}. Permission for wet-wall tile does NOT certify horizontal sill finish, positive fall, substrate or waterproof continuity. All niche faces share the original SINGLE gross niche pool. |",
   f"| Bathroom dry/wet LEVEL | {link(cand['level'])}; {level['thick']}; **${level['price']}/SF**; {level['carton']} | Exact SKU {level['use']}. Actual tile cut, substrate and transitions unverified. |",
   f"| Shower POINT PAN only if applicable | {link(cand['level'])} | **Maker Shower Floor YES and published DCOF >=0.42** independent of Bathroom Floor. Point-drain four-plane slope design, cut dimensions and waterproof assembly UNKNOWN. WALK-IN branch only where not owner-selected. |",
   "| Tiled CEILING | **N/A — none scheduled in this room** | Do not add an overhead shower ceiling. |",
   "",
   "**Program branches / quantity integrity:** "+meta['branches'],
   "",
   "**Architectural scheme:** "+cand['idea']+" **Grout and layout concept:** "+cand['grout']+" Maker joint, light, glass, valve placements and actual material boards remain unapproved. Distinguish installed mockup from retail web image.",
   "",
   f"**Legacy gross quantity cost control per physical copy:** WALL **{meta['areas']['wall']} SF x ${wall['price']}/SF = ${Q(amounts['wall'])}**; NICHE all faces **{meta['areas']['niche']} SF x ${niche['price']}/SF = ${Q(amounts['niche'])}**; LEVEL/(where source shared PAN) **{meta['areas']['level']} SF x ${level['price']}/SF = ${Q(amounts['level'])}**. Total **${Q(cost)}/copy material RATE ONLY**. These are gross legacy source figures, **not** net surface verification, carton purchase quantities, signed budget or current supplier total. Two physical copies, no added 15%. Conditional separately measured WALK-IN PAN where relevant remains **unknown/NOT priced**.",
   "",
   "**Manufacturer variant and store context:** "
    +f"WALL: {wall['size']}, {wall['thick']}; {wall['joints']}; exact maker item {wall['url']}. "
    +f"NICHE: {niche['size']}, {niche['thick']}; {niche['joints']}; maker {niche['url']}. "
    +f"LEVEL/PAN: {level['size']}, {level['thick']}; {level['joints']}; maker {level['url']}. "
    +"Any absent color-specific maker numeric SKU is explicitly UNKNOWN; never infer generic collection use for a different finish. Do not assert raw-lab result where maker only publishes >=0.42.",
   "",
   "**Three genuinely distinct families considered BY surface, qualified only to each independent use:** Wet WALL **F&D Perimeter Gray** (Adessi) / **F&D Luxe Sand 24x48** (Vetta Elements) / **Elm Cortar Bone FLAT** (Elm Cortar) each individual Shower Walls or Wet Areas listing; Wall alternates also Elm Tones Sapphire/Copper/Emerald colorways which count as ONE Tones family. Niche wet WALL **F&D La Belle Purity** / **Elm Tones Sandstone** / **Elm Soho Ivory** manufacturer wet-wall listing; La Belle Blue/Purity colorways count one family. LEVEL and any wet POINT PAN **F&D Luxe Sand 101317949 / F&D Riviera Oat 101487775 / F&D Perimeter Gray 101239218**, distinct three families with exact maker published wet DCOF >=0.42, Bathroom Floor YES and separately Shower Floor YES. [MSI Murcia Dune](https://www.msisurfaces.com/porcelain-murcia/dune/) maker floor DCOF >0.42, PRICE ON REQUEST, Shower Floor UNKNOWN, so exclude from qualified PAN count. [Porcelanosa Bottega Caliza](https://store.porcelanosa.com/us/search/bottega) price variants exist but exact wet DCOF/POINT PAN permission UNKNOWN; not qualified. No Daltile, Emser, Platform or Glazzio new selection. F&D Concept Gray/Chastain/Tower discontinued-store concerns: not candidates.",
   "",
   "**Actual design/installation holds:** "+meta['special'],
   "",
   "**Commercial restrictions:** "+SOURCES['cost'],
   "",
   "**Authenticated Old Town visual evidence:** "+SOURCES['oldtown'],
   "",
   "**No owner decision or procurement authorization.** A/B judges must independently score MARKET 4 criteria, DESIGN/BUILD/COST 5 each, 1-5 with sourced reasons, arithmetic one-decimal mean, gate_flags, top_fix, confidence. No historical scores, prior roles, ROOMS/LEDGER/private mapping/previous critics/contaminated aggregator access."
  ]
  (path/(letter.upper()+'.md')).write_text('\n'.join(s)+'\n',encoding='utf-8')
  print(id,letter.upper(),Q(cost),len('\n'.join(s)),'characters')
print('R034 3 rooms / 6 complete neutral room-specific products + no earlier outcome hints')
