"""Add authoritative R035 text without deleting historic champion and board evidence."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
STATE=json.loads((ROOT/'state'/'ROOMS.json').read_text(encoding='utf-8'))
FLOOR='https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html'
WALL24='https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317865.html'
SAND='https://www.elmsurfaces.com/product/sandstone-tones'
SAPP='https://www.elmsurfaces.com/product/sapphire-tones'
BLUE='https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html'
PURITY='https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html'
RIV='https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html'
PER='https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html'
COP='https://www.elmsurfaces.com/product/copper-tones'
MEMO='../../state/ROUND035_THREE_DURAVIT_TUB_BOARD_DECISIONS_20261107.md'

rows={
 'PH-BATH2':{
  'id':'round-031-A','score':'3.670','historical':'3.880','incletter':'A','challenger':'B',
  'status':'DEFENDED / unchanged selected materials',
  'summary':'WET TUB WALL Elm Tones Sapphire Glossy 2x20 at $6.95/SF same-job, NICHE Elm Tones Sandstone Glossy 2x20 at $6.95/SF same-job, bath LEVEL F&D Luxe Sand 24x24 SKU101317949 at $3.49/SF GA retail.',
  'comparison':'A 3.670 / $789.23 per-copy sum of cent-rounded source rows vs B 3.600 / $679.54, no positive challenger gain.',
  'alternates':f'B wet WALL [F&D La Belle Antique Blue 3x12 SKU100507706]({BLUE}), NICHE [La Belle Purity 3x12 SKU100507722]({PURITY}), LEVEL [Riviera Oat 24x48 SKU101487775]({RIV}).',
  'picks':f'A WALL [Sapphire 2x20]({SAPP}) wet Walls/Wet Areas YES, NICHE [Sandstone 2x20]({SAND}) wet vertical YES, LEVEL [Luxe Sand 101317949]({FLOOR}) Bathroom Floor YES and wet DCOF >=0.42.',
  'holds':'Duravit 59-in TUB and Hansgrohe Matte White unchanged; assumed W1 59.496 in vs nominal tub 59 in not physical fit proof; tub flange, niche horizontal sill waterproofing, >=3-in visible cuts, substrate, Chicago lots/ETA/landed and owner budget FILL IN held. NO tiled PAN or point drain.',
 },
 'TX-BATH2':{
  'id':'round-031-B','score':'3.590','historical':'3.850','incletter':'B','challenger':'A',
  'status':'DEFENDED / unchanged selected materials',
  'summary':'WET TUB WALL Elm Tones Sapphire Glossy 2x20 at $6.95/SF same-job, NICHE F&D La Belle Purity Glossy 3x12 SKU100507722 at $5.56/SF GA retail, bath LEVEL F&D Luxe Sand 24x24 SKU101317949 at $3.49/SF GA retail.',
  'comparison':'B 3.590 / $845.46 per-copy aggregate unrounded-to-cents ($845.45 source per-line cent sum) vs A 3.470 / $879.30, challenger below incumbent.',
  'alternates':f'A wet WALL [Elm Tones Copper 2x20]({COP}), NICHE [Sandstone 2x20]({SAND}), LEVEL [Riviera Oat 24x48 101487775]({RIV}).',
  'picks':f'B WALL [Sapphire 2x20]({SAPP}) wet Walls/Wet Areas YES, NICHE [La Belle Purity 100507722]({PURITY}) Shower Walls YES / Shower Floor NO (vertical only), LEVEL [Luxe Sand 101317949]({FLOOR}) Bathroom Floor YES and wet DCOF >=0.42.',
  'holds':'Duravit selected TUB / Hansgrohe Chrome unchanged; basin OWNER UNSELECTED. Own drawing W1 62.484 in conflicts candidate ~59.496-in assumed opening and 59-in tub; use neither as measured tub-fit proof. Tub flange, horizontal niche sill waterproofing, substrate and edge cuts, Chicago lot/landed, owner budget FILL IN remain open. NO tiled PAN or point drain.',
 },
 'TX-BATH4':{
  'id':'round-035-B','score':'3.630','historical':'3.650','incletter':'A','challenger':'B',
  'status':'CHANGED / genuine +0.280 replacement of prior R031-B',
  'summary':'NEW WET TUB WALL Floor & Decor Luxe Sand Matte 24x48 SKU101317865 at $3.99/SF GA retail; NEW NICHE Elm Tones Sandstone Glossy 2x20 at $6.95/SF same-job; NEW bath LEVEL Floor & Decor Luxe Sand Matte 24x24 SKU101317949 at $3.49/SF GA retail.',
  'comparison':'R035 A prior Perimeter/Purity/Riviera 3.350 / $583.04 versus new B 3.630 / $572.89 gross-rate per copy; +0.280 > +0.250 threshold. Two physical copies 007A/B: $1,145.7750 aggregate before cartons; dedicated pack ~$623.63/copy, shared two-room pool ~$1,202.09 only hypothetical.',
  'alternates':f'Former incumbent A wet WALL [Perimeter Gray 24x48 SKU101239218]({PER}), NICHE [La Belle Purity 3x12 SKU100507722]({PURITY}), LEVEL [Riviera Oat 24x48 SKU101487775]({RIV}).',
  'picks':f'B WALL [Luxe Sand 24x48 SKU101317865]({WALL24}) Shower Walls YES (exact SKU); NICHE [Elm Sandstone 2x20]({SAND}) Walls/Wet Areas YES for vertical faces; LEVEL [Luxe Sand 24x24 SKU101317949]({FLOOR}) separate exact SKU, Bathroom Floor YES, wet DCOF >=0.42.',
  'holds':'Selected 59-in Duravit TUB / Hansgrohe Matte White unchanged; 60-in nominal drawing back wall not fit proof. Tub flange/Westbrass tub waste, sill positive fall and waterproof transition, 24x48 wall cuts and 24x24 floor layout, 3-in pieces, substrate, two-size matching appearance/lot, actual Chicago F&D/Elm supply, landed/installed cost, signed FILL IN owner budget and owner tile approval held. NO tiled PAN, square point drain or tiled ceiling.',
 },
}

for rid,r in rows.items():
  state=next(x for x in STATE['rooms'] if x['id']==rid)
  assert state['champion_id']==r['id'] and f"{state['champion_score']:.3f}"==r['score']
  assert state['owner_status'] is None and state['last_round']==35
  base=ROOT/'rooms'/rid
  for name in ('champion.md','history.md','vendor_comparison.md'):
    p=base/name
    assert p.is_file() and 'R035 CURRENT' not in p.read_text(encoding='utf-8-sig'),(rid,name,'already integrated')

for rid,r in rows.items():
  base=ROOT/'rooms'/rid
  doc=(base/'champion.md')
  previous=doc.read_text(encoding='utf-8-sig')
  block=(f'# {rid} — R035 CURRENT PROVISIONAL TILE CHAMPION (2026-11-07)\n\n'
         f'**{r["status"]}.** Current independently rescored selection **{r["id"]}**, **{r["score"]}/5**; historic R031 original board score **{r["historical"]}/5** remains retained below. Four original strict-blind MARKET/DESIGN/BUILD/COST critiques; all specialist means >=3.0. Original score and role mapping were not presented to critics. No owner consent or installed/purchase authorization.\n\n'
         f'**Exact selected tile by surface:** {r["summary"]}\n\n'
         f'**Product use qualification:** {r["picks"]} Product-level manufacturer use is not an entire tub flange/niche sill waterproof assembly approval.\n\n'
         f'**Same-round comparison and +0.25 rule:** {r["comparison"]} {r["alternates"]}\n\n'
         f'**UNCHANGED plumbing, source and owner holds:** {r["holds"]} Quantities historical gross with 15% waste already ONCE. F&D Nov 7 GA public prices are not Chicago matching-lot quotes; Elm Tones $6.95/SF is 2026-09-04 same-job quotation. No fabrication/tile installation release. See [{"R035 formal four-seat decision"}]({MEMO}).\n\n---\n\n')
  doc.write_text(block+previous,encoding='utf-8')

  hist=base/'history.md'
  old=hist.read_text(encoding='utf-8-sig').rstrip()
  entry=(f'\n\n## R035 CURRENT strict-blind four-seat tile decision — 2026-11-07\n\n'
         f'- **{r["status"]}; selected {r["id"]} = {r["score"]}/5**, old R031 historic score {r["historical"]} preserved. {r["comparison"]}\n'
         f'- Current surface tiles: {r["summary"]}\n'
         f'- Verified use: {r["picks"]} Actual Duravit bathtub; no tiled PAN, point shower drain or tiled ceiling.\n'
         f'- Holds: {r["holds"]} No owner tile or basin assumption, and no original quantity/waste/quote edits.\n'
         f'- Independent 114-criterion 24-mean 6-weighted R035 decision memo: [{"source"}]({MEMO}); 12 authentic critic files remain unchanged.\n')
  hist.write_text(old+'\n'+entry,encoding='utf-8')

  vc=base/'vendor_comparison.md'
  old=vc.read_text(encoding='utf-8-sig').rstrip()
  entry=(f'\n\n## R035 CURRENT board-qualified four-vendor comparison — 2026-11-07\n\n'
         f'**Selected {r["id"]} at {r["score"]}/5; {r["status"]}.** This section supersedes earlier preliminary/blocked or prior R031 "current" headings; older tables are historical, NOT a reintroduction of Platform/Emser/Daltile as eligible vendors. Allowed: Elm, MSI, Porcelanosa, Floor & Decor.\n\n'
         f'| Actual TUB surface | R035 selected scheme / technical permission | Independent alternative |\n'
         f'|---|---|---|\n'
         f'| WET WALL / vertical NICHE / bath LEVEL | {r["picks"]} | {r["alternates"]} |\n\n'
         f'**Current same-round comparison:** {r["comparison"]} **Pricing:** Elm Tones 2026-09-04 1529 job trade $6.95/SF; F&D exact 2026-11-07 public Atlanta Kirkwood retail, NOT Chicago stock/landed. Distinct large-format products have individual maker exact wet WALL or LEVEL permissions. At least three genuinely different allowed-vendor product families per applicable surface in original neutral R035 candidate descriptions, not repeated same-family colors. Shower PAN, POINT shower drain and tiled ceiling N/A because a Duravit tub is selected.\n\n'
         f'**Non-waived downstream limitations:** {r["holds"]} Niche one historic gross pool for all faces, 15% waste once, no invented additional allowance or quoted installed total. Old Town OT01 dry powder and OT04 wet glossy green wall are two distinct bathrooms within ONE 405 W Armitage development; OT05 bath photo unknown. [Formal R035 board]({MEMO}).\n')
  vc.write_text(old+'\n'+entry,encoding='utf-8')
  print('R035',rid,'UPDATED champion, additive history and vendor comparison',flush=True)
print('PASS 9 room files, old sections retained, owner and plumbing unchanged')
