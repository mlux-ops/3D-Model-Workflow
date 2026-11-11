"""Prepare genuinely new, equally detailed neutral R036 sources; NO scores or dispatch.

Prerequisite to independent blind review: original R035 Reviewer67 final verdict.
No historical score, previous critic, champion, private map, or state paths in critic files.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

ROOT=Path(__file__).resolve().parents[1]
Q=lambda x:x.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
P={
 'pienza':{
  'name':'Floor & Decor Pienza Terra Matte Travertine-look Porcelain',
  'sku':'110850387','size':'24x48 nominal / 23.59x47.30 actual',
  'finish':'matte rectified, 9 mm','rate':'2.99','box':'15.50 SF/2 pieces, $46.32/box',
  'url':'https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html',
  'source':'2026-11-07 West Des Moines, Iowa public retailer price',
  'wall':'Shower Walls YES (exact SKU)','level':'Bathroom Floor YES, wet DCOF >=0.42',
  'pan':'Shower Floors YES INDEPENDENTLY; installer four-plane slope/cut and assembly UNVERIFIED'},
 'derossi':{
  'name':'Floor & Decor De Rossi Ivory Matte Terrazzo-look Porcelain',
  'sku':'100996800','size':'24x24 nominal / 23.50x23.50 actual',
  'finish':'matte rectified, 10.5 mm','rate':'6.99','box':'11.64 SF/3 pieces, $81.27/box',
  'url':'https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html',
  'source':'2026-11-07 Camelback Phoenix, Arizona public retailer price',
  'wall':'Shower Walls YES (exact SKU)','level':'Bathroom Floor YES, wet DCOF >=0.42',
  'pan':'Shower Floors YES INDEPENDENTLY; installer four-plane slope/cut and assembly UNVERIFIED'},
 'luxe':{
  'name':'Floor & Decor Luxe Sand Matte Porcelain',
  'sku':'101317949','size':'24x24 nominal / 23.70x23.70 actual',
  'finish':'matte rectified, 8 mm','rate':'3.49','box':'15.52 SF/4 pieces, $54.08/box',
  'url':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html',
  'source':'2026-11-07 Kirkwood Atlanta, Georgia public retailer price',
  'wall':'Shower Walls YES (exact SKU)','level':'Bathroom Floor YES, wet DCOF >=0.42',
  'pan':'Shower Floors YES INDEPENDENTLY; installer four-plane slope/cut and assembly UNVERIFIED'},
 'riviera':{
  'name':'Floor & Decor Riviera Oat Matte Porcelain',
  'sku':'101487775','size':'24x48 nominal / 23.58x47.28 actual',
  'finish':'matte rectified, 8 mm','rate':'3.99','box':'16.00 SF/2 pieces, $63.84/box',
  'url':'https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html',
  'source':'2026-11-07 Kirkwood Atlanta, Georgia public retailer price',
  'wall':'Shower Walls YES (exact SKU)','level':'Bathroom Floor YES, wet DCOF >=0.42',
  'pan':'Shower Floors YES INDEPENDENTLY; installer four-plane slope/cut and assembly UNVERIFIED'},
 'perimeter':{
  'name':'Floor & Decor Perimeter Gray Matte Porcelain',
  'sku':'101239218','size':'24x48 nominal / exact calibrated dimensions unknown',
  'finish':'matte rectified, 9 mm','rate':'3.99','box':'15.50 SF/2 pieces, $61.84/box',
  'url':'https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html',
  'source':'2026-11-07 Kirkwood Atlanta, Georgia public retailer price',
  'wall':'Shower Walls YES (exact SKU)','level':'Bathroom Floor YES, wet DCOF >=0.42',
  'pan':'Shower Floors YES INDEPENDENTLY; installer four-plane slope/cut and assembly UNVERIFIED'},
 'sapphire':{
  'name':'Elm Surfaces Tones Sapphire Glossy Ceramic',
  'sku':'public standalone order code UNKNOWN','size':'2x20',
  'finish':'glossy 8.5 mm','rate':'6.95','box':'6.50 SF/24 pieces',
  'url':'https://www.elmsurfaces.com/product/sapphire-tones',
  'source':'2026-09-04 actual 1529 Wieland same-job Elm quote',
  'wall':'Maker Walls + Wet Areas YES for this color/finish','level':'NOT floor qualified; do not use as LEVEL',
  'pan':'NOT shower PAN; wet vertical wall only'},
 'emerald':{
  'name':'Elm Surfaces Tones Emerald Glossy Ceramic',
  'sku':'public standalone order code UNKNOWN','size':'2x20',
  'finish':'glossy 8.5 mm','rate':'6.95','box':'6.50 SF/24 pieces',
  'url':'https://www.elmsurfaces.com/product/emerald-tones',
  'source':'2026-09-04 actual 1529 Wieland same-job Elm quote',
  'wall':'Maker Walls + Wet Areas YES for this color/finish','level':'NOT floor qualified',
  'pan':'NOT floor or PAN'},
 'antique':{
  'name':'Floor & Decor La Belle Antique Blue High Gloss Ceramic',
  'sku':'100507706','size':'3x12','finish':'glossy pressed 8.5 mm',
  'rate':'5.56','box':'0.25 SF/piece $1.39 each, 48-piece manufacturer carton',
  'url':'https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html',
  'source':'2026-11-07 Kirkwood Atlanta, Georgia public retailer price',
  'wall':'Shower Walls YES (exact SKU); Shower Floors NO',
  'level':'NOT for bath LEVEL','pan':'NOT shower PAN'},
 'sandstone':{
  'name':'Elm Surfaces Tones Sandstone Glossy Ceramic',
  'sku':'public standalone order code UNKNOWN','size':'2x20',
  'finish':'glossy 8.5 mm','rate':'6.95','box':'6.50 SF/24 pieces',
  'url':'https://www.elmsurfaces.com/product/sandstone-tones',
  'source':'2026-09-04 actual 1529 Wieland same-job Elm quote',
  'wall':'Maker Walls + Wet Areas YES for exact color/finish, vertical niche faces ONLY',
  'level':'Horizontal niche sill NOT a qualified assembly','pan':'NOT shower PAN'},
 'purity':{
  'name':'Floor & Decor La Belle Purity High Gloss Ceramic',
  'sku':'100507722','size':'3x12','finish':'glossy pressed 8.5 mm',
  'rate':'5.56','box':'0.25 SF/piece $1.39 each, 48-piece manufacturer carton',
  'url':'https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html',
  'source':'2026-11-07 Kirkwood Atlanta, Georgia public retailer price',
  'wall':'Shower Walls YES (exact SKU) vertical niche only; Shower Floors NO',
  'level':'Horizontal niche sill NOT a qualified assembly','pan':'NOT shower PAN'}
}
R={
 'PH-BATH4':{
   'instances':'311A/311B','program':'Owner selected WALK-IN; Brizo Brilliance Black Onyx BT062415-BNX four-inch square POINT shower drain, no tub or tiled ceiling',
   'geometry':'W1 ~5.0 ft, two returns ~2.54 ft, 9.25-ft height all drawing-derived; owner says bath floor 35 SF versus previously assumed 27 SF unresolved',
   'qty':('107.2','8.63','40.2'),
   'pool':'40.2 SF gross is preexisting combined bathroom LEVEL + four-plane POINT PAN. NEVER multiply or separately add PAN quantity',
   'cases':{'A':('perimeter','purity','luxe'),'B':('pienza','sandstone','pienza')},
   'design':{'A':'Graphite large-format wall, glossy pale niche and calm warm-ivory floor; strong BNX contrast but possibly a gray/white spec-home appearance. Proposed 24x48 stack, 1/8-in grout subject to exact maker, 3x12 niche with proper joint and profile.',
             'B':'Travertine-tone warm continuous 24x48 wall and LEVEL/POINT PAN, glazed narrow Sandstone niche as subtle gloss relief, BNX black accents. Same product may span large floor and pan ONLY after field four-plane slope/cut proof; no fixed joint or drain geometry asserted.'},
   'holds':'Correct 35 vs 27 SF owner floor area, tub-N/A walk-in glass, cut pieces >=3 in, actual BNX point grate/rough depth, four-plane slope and waterproof system, niche sill fall, two-room lot and Chicago price all unresolved.'},
 'PH-BATH3':{
   'instances':'307A/307B','program':'Owner TUB or WALK-IN UNSELECTED; Hansgrohe Chrome unchanged; basin OWNER UNSELECTED; Delta Chrome DT062412 POINT only for WALK-IN (NEVER tub waste), no tiled ceiling',
   'geometry':'W1 ~5.0 ft, returns ~2.33 ft, tiled height ~7.75 ft, floor ~35 SF, all drawing/hand-off derived, not measured live',
   'qty':('86.2','8.63','40.2'),
   'pool':'40.2 SF original bathroom LEVEL gross only; separate WALK-IN POINT PAN net area and price are NULL (not zero, not included), tub branch PAN N/A',
   'cases':{'A':('pienza','sandstone','derossi'),'B':('sapphire','sandstone','luxe')},
   'design':{'A':'Quiet limestone-like large-format 24x48 wet wall and an intentionally playful ivory terrazzo 24x24 LEVEL. Chrome trim echoes subtle speckle; glazed Sandstone niche gives warmth. De Rossi cost is above standard warm neutral and heavier 10.5mm; intentional pattern requires physical sample.',
             'B':'Rich blue glossy 2x20 wet wall, warm vertical Sandstone niche and simple beige 24x24 LEVEL; Chrome crisp contrast. Strong buyer-photo signature but more saturated than a quiet spa scheme. Setout requires niche corners and full height checked.'},
   'holds':'Owner basin AND TUB/WALK-IN decisions; any walk-in Delta point drain and full independent pan SF/dollars NULL, tub waste not to be replaced, actual cut layout/waterproof niche/Chicago lot held.'},
 'TX-BATH3':{
   'instances':'207A/207B','program':'Owner TUB or WALK-IN UNSELECTED; Brizo Brilliance Black Onyx BNX BT062415-BNX four-inch square POINT only if WALK-IN, never tub waste; no tiled ceiling',
   'geometry':'W1 ~5.1 ft, two returns ~2.60 ft, tiled height ~7.75 ft, floor ~37 SF, all drawing assumptions',
   'qty':('91.8','4.89','42.5'),
   'pool':'42.5 SF original bathroom LEVEL only; optional separately measured WALK-IN POINT PAN square footage and price NULL; owner TUB branch no PAN',
   'cases':{'A':('antique','purity','luxe'),'B':('emerald','purity','pienza')},
   'design':{'A':'Deep antique-blue gloss 3x12 horizontal wet wall, La Belle Purity niche contrast and matte ivory LEVEL; BNX hardware strong contrast. Accessible blue but potentially generic or graphic with bright niche; pressed ceramic grout alignment needs care.',
             'B':'Elm Tones Emerald green glossy 2x20 with a slender Purity niche and Pienza Terra warm travertine-look 24x48 floor; intentional contemporary greens closely relate to OT04 photo language without asserting matching SKU. BNX strong graphic accent; warm large format calms saturation.'},
   'holds':'TUB/WALK-IN owner choice not made; optional BNX POINT PAN independent area and cost NULL; opening/3in-cuts, niche waterproof/sill, actual curb/threshold, Chicago matched lot and owner budget held.'}
}

INTRO=('**BLIND A/B source. No prior product role, historical score or prior outcome is disclosed.** '
       'Two distinct candidate letters must be scored separately with four authentic independent '
       'MARKET (4 criteria/.30), DESIGN (5/.25), BUILD (5/.25), COST (5/.20) judges. '
       'No previous critiques, champion/history, ROOMS/LEDGER, other-room candidates, private keys '
       'or outcome-contaminated sources should be available to specialists.')
COMPS=('**Actual comparable limit:** OT01 405 W Armitage #2N photo shows a DRY powder '
       'wallcovering/wainscot scene, while OT04 #4S photo shows a WET glossy dark-green shower '
       'wall. They are separate rooms inside ONE 405 W Armitage development, not independent '
       'market votes; actual maker/SKU/grout unverified. OT05 bathroom image NOT verified, '
       'other Old Town photograph attribution limited; Lincoln Park and Gold Coast are adjacent '
       'and secondary. PH $2.8M and TX $2.7M within approximate $2.4M-$3.2M sold comp band.')
FAMILIES=('**Three genuinely different allowed product families per actual tiled surface:** '
          'Wet vertical WALL [Pienza Terra Montalcino NatureMatch 110850387](' + P['pienza']['url'] + '), '
          '[Elm Cortar Bone FLAT 24x48](https://www.elmsurfaces.com/product/cortar-bone), '
          '[La Belle Antique Blue 100507706](' + P['antique']['url'] + ') all individually permit wet wall; '
          'Elm Tones Emerald/Sapphire is a FOURTH different family but its colorways are NOT counted separately. '
          'NICHE vertical faces [Elm Tones Sandstone](' + P['sandstone']['url'] + '), '
          '[F&D La Belle Purity](' + P['purity']['url'] + '), '
          '[Elm Soho Ivory](https://www.elmsurfaces.com/product/soho-ivory), specific wet-wall use only, '
          'complete sill/penetration waterproof system NOT rated by these tile listings. '
          'Bathroom LEVEL and possible POINT PAN [Pienza Terra 110850387](' + P['pienza']['url'] + '), '
          '[De Rossi Ivory 100996800](' + P['derossi']['url'] + '), '
          '[Luxe Sand 101317949](' + P['luxe']['url'] + '), '
          'each independently maker-retailer Bathroom Floor YES, Shower Floor YES and DCOF >=0.42; '
          'Riviera Oat another independent qualified family. Unproven MSI/Porcelanosa floor SKUs are '
          'comparison-only, NEVER represented as qualified PAN. Platform/Emser/Daltile excluded.')

for room,config in R.items():
 for letter,(wall,niche,level) in config['cases'].items():
  target=ROOT/'rooms'/room/'board'/'round-036'/'candidates'/(letter+'.md')
  assert not target.exists(),('do not overwrite',target)
  target.parent.mkdir(parents=True,exist_ok=True)
  w,n,l=[P[key] for key in (wall,niche,level)]
  gross=[Decimal(s) for s in config['qty']]
  money=[gross[i]*Decimal(p['rate']) for i,p in enumerate((w,n,l))]
  total=sum(money)
  rows=[]
  for surf,p,qty,rate in (('Wet WALL',w,config['qty'][0],money[0]),('One existing NICHE all-face pool',n,config['qty'][1],money[1]),('Bathroom LEVEL',l,config['qty'][2],money[2])):
   use=p['wall'] if surf!='Bathroom LEVEL' else p['level']
   rows.append(f'| {surf} | [{p["name"]} {p["sku"]}]({p["url"]}) | {p["size"]}; {p["finish"]}; {p["box"]} | **{use}**; {qty} historic gross SF x ${p["rate"]}/SF = **${Q(rate)}** |')
  branch=('PH-BATH4 WALK-IN selected: '+l['pan']+'; SAME original gross shared LEVEL/PAN source, no new duplicate SF.' if room=='PH-BATH4' else
          'Owner TUB/WALK-IN not yet selected: TUB -> tiled PAN N/A, WALK-IN -> '+l['pan']+
          '; separate PAN area and material cost NULL until measured.')
  text=(
   f'# R036 neutral candidate {letter} - {room}\n\n{INTRO}\n\n'
   f'**Actual two instances:** {config["instances"]}. **Immutable plumbing and owner program:** {config["program"]}. '
   f'**Geometry provenance:** {config["geometry"]}; all measured cuts/openings/niche faces, curb and substrate remain UNKNOWN.\n\n'
   '| Surface | Exact allowed-vendor product / URL | Size, finish and real carton coverage | Individual maker application and historical-area cost |\n'
   '|---|---|---|---|\n'+'\n'.join(rows)+'\n\n'
   f'**Floor/pan gate, not a guessed family-wide rating:** {branch} The floor manufacturer independently publishes wet DCOF >=0.42 '
   'for this exact listed SKU; all relevant shower-floor permission must be independently confirmed and no product page supplies a four-plane cut plan, rough drain setout or complete waterproof assembly. '
   'Vertical wet-wall manufacturer listing NEVER proves horizontal niche sill pitch/waterproofing or overhead wet-shower-ceiling permission. '
   'No ceiling tile scheduled in any of these three rooms.\n\n'
   f'**Architectural composition and proposed layout (not approved):** {config["design"][letter]} '
   'Use suitable LFT thinset/flatness and full coverage over the compatible waterproof substrate, '
   'verify factory grout-joint ranges at exact SKU, no premixed shower mastic, and confirm joint '
   'at tub/valve/niche/grate/glass or curb only once fixtures and opening geometry are field verified.\n\n'
   f'**Original gross quantities:** WALL {config["qty"][0]} SF, total combined NICHE {config["qty"][1]} SF, LEVEL/source pool {config["qty"][2]} SF per copy. '
   f'{config["pool"]}. The source gross already contains historical 15% waste ONCE, '
   'so NO extra 15%, no per-niche-face multiplication and no fictional independent pan purchase. '
   f'**Gross material RATE total ${Q(total)}/copy**, two instances ${Q(total*2)}; full-precision total ${total}, '
   f'component extended amounts {" + ".join(str(x) for x in money)}. Purchase/order BOX counts, tax, waterproofing, '
   'profiles, trim, shipping, labor and real installation price are not included. '
   'Niche cartons can pool across physical copies only with an actual matching-lot order.\n\n'
   f'**Price-source authority:** WALL {w["source"]}; NICHE {n["source"]}; LEVEL {l["source"]}. '
   'All store-specific Floor & Decor posted prices observed 2026-11-07 are out-of-state public retail '
   'and DO NOT prove current Chicago matched lot, stock, ETA or delivery route. Elm Tones rate $6.95/SF '
   'is 2026-09-04 job 1529 quote, not installed or landed. '
   'Owner allocated room tile budget FILL IN; 125% threshold not computable; no owner product signoff.\n\n'
   f'**Technical and buyer-facing open gates:** {config["holds"]} '
   'Expected visible edge cuts >=3 in must be proven by installer with actual calibrated tile size '
   'and physical points/returns; large-format POINT pan is NOT automatically unbuildable or buildable. '
   'Candidate appearance and BNX/Chrome fitting contrast require real project light/material mockup.\n\n'
   +FAMILIES+'\n\n'+COMPS+'\n\n'
   '**Review instructions:** MARKET 4 independent 1-5 criteria, DESIGN/BUILD/COST 5 each, '
   'specific reasons with verifiable exact source and own-room geometry, one-decimal half-up '
   'arithmetic specialist mean, top_fix, gate_flags, confidence for EACH letter. '
   'Do not infer previous product roles from A/B. No owner approval, vendor contact, '
   'Revit/Smartsheet write, orders or fabricated Chicago supplier quotes.\n')
  target.write_text(text,encoding='utf-8')
  print(room,letter,'candidate',target.stat().st_size,'bytes','rate',Q(total),flush=True)
print('PASS six R036 neutral complete alternatives, no scores, critics or owner selection')
