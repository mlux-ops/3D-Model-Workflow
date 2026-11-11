"""Author six new R012 neutral unscored TX options; never overwrite existing source."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
cfg={
'TX-PRIMARY':{
 'B':('ELM Cortar Clay 24x48 Soft+Ribbed relief wet field/ceiling from v4 source','ELM Cortar Clay Soft/AntiSlip blended original floor+linear pan','not specified under v4 primary NO NICHE','source'),
 'C':('ELM Cortar Clay 24x48 Soft FLAT wet-listed wall/ceiling only','Emser Capisco Trosa F08CAPITR1224M 12x24 Matte LEVEL+TX WC and separate Daltile Prime RL21 proposed linear mosaic PAN','not specified under v4 primary NO NICHE','conditional'),
 'cuts':[('W1',62.25,24),('W2',57.2496,24)]},
'TX-BATH2':{
 'C':('ELM Tones Copper 2x20 Glossy stacked tub wet surround','ELM Cortar Clay 12x24 Soft LEVEL floor','ELM Tones Sandstone 2x20 Glossy existing niche','source'),
 'A':('ELM Tones Copper 2x20 Glossy centered HORIZONTAL stacked tub surround','Emser Capisco Trosa F08CAPITR1224M 12x24 Matte LEVEL floor, NO tiled pan','ELM Tones Sandstone 2x20 Glossy existing niche only','conditional'),
 'cuts':[('W1',62.484,20),('W2',31.2,20),('W3',31.2,20)]},
'TX-BATH4':{
 'A':('ELM Cortar Charcoal 24x48 Soft tub wet wall; no new relief area','ELM Cortar Bone 12x24 Soft LEVEL floor','ELM Clara Tierra Madre Caviar 2x8 quoted tub niche (wet use unlisted)','source'),
 'B':('ELM Cortar Charcoal 24x48 FLAT Soft wet-listed tub wet wall','Emser Capisco Trosa F08CAPITR1224M 12x24 Matte LEVEL floor, NO tiled pan','ELM Soho Ivory 2x10 Glossy individually wet-listed existing niche','conditional'),
 'cuts':[('W1',60,24),('W2',30.48,24),('W3',30.48,24)]}}
for rid,variants in cfg.items():
 room=next(z for z in rooms if z['id']==rid)
 assert room['status']=='blocked' and room['champion_id'] is None and room['owner_status'] is None
 folder=R/'rooms'/rid/'board/round-012/candidates'
 assert not folder.parent.exists(),'R012 candidate folder already exists; never regenerate'
 folder.mkdir(parents=True)
 geo=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 plumbing=json.loads((R/'rooms'/rid/'plumbing.json').read_text(encoding='utf-8'))
 for letter,candidate in variants.items():
  if letter=='cuts':continue
  wall,floor,accent,kind=candidate
  is_new=kind=='conditional'
  note='Correct model identity, actual installed offsets, manufacturer wet use, raw numeric wet floor/pan certificate, current quote and signed owner selections remain mandatory; no candidate passes procurement release.'
  if rid=='TX-PRIMARY':
   fixture='Brizo Brilliance Black Onyx 48-in LINEAR shower drain BT0734816-BNX with BR73480 rough and separately selected Victoria + Albert tub; NO PRIMARY NICHE and TX-WC floor shared; descoped body sprays stay excluded.'
   area='Original 116.1 SF blended level+linear PAN+WC gross is ONE pool already waste-loaded. Proposed 87.64 LEVEL (including shared WC) + 28.46 linear PAN SF is historic illustration only, NOT verified split and NOT an extra pan; individual current quantities null.'
  elif rid=='TX-BATH2':
   fixture='Actual Duravit Starck 59-in tub 700332000000090 and Hansgrohe CHROME 04925000/04790000, basin OWNER-UNSELECTED; NO tiled shower pan.'
   area='Original 43.7 SF gross bath LEVEL floor includes 15% waste and has NO separate tiled shower-pan quantity. Original niche 8.63 SF is separate quoted allowance, NOT measured additive field face.'
  else:
   fixture='Actual Duravit Starck 59-in tub 700332000000090 and Hansgrohe Matte White 15758701/26866701; NO tiled pan, retain tub program.'
   area='Original 44.3 SF gross level floor with one 15% waste factor; quoted Caviar niche 8.63 SF is provisional, NOT independent measured additional wall face.'
  lines=['# '+rid+' — Candidate '+letter+' — complete tile design option','',intro,'',
         '## Source-bounded finishes, geometry and selected plumbing','',
         '**Selected fixtures/program:** '+fixture+' Project drawings copied from 1529 handoff have NOT been certified by actual live 1529 Revit; current title is 1527. Owner selection and release flags remain false/null.','',
         '**Complete conditional surface scheme:** Wet-zone field = '+wall+'; LEVEL floor/pan interpretation = '+floor+'; niche = '+accent+'. For any proposed floor tile, raw exact measured wet DCOF test evidence, shade-lot and installation release are NULL. Do not add any unselected sink, change tub to shower or introduce a primary niche.','',
         '| Source material surface + exact Smartsheet row | Candidate maker/size/use with individual primary evidence | Original gross SF per copy (15% INCLUDED) | 2026-09-03 historic ELM cost per copy versus current alternate | Exact hard gate / installation and commercial treatment |',
         '|---|---|---|---|---|']
  for row in room['carried_tile_rows']:
   surf=row['surface'];q=row['qty_sf_per_unit'];old=row['extended_quote_cost_usd_per_unit'];sku=row['smartsheet_row_id']
   if surf=='wall':
    product=wall
    if rid=='TX-PRIMARY':gate='Flat Clay maker individual Wet Areas PASS, historic Ribbed individual wet use absent FAIL; exact overhead fastening/membrane specification and true relief split null.'
    elif rid=='TX-BATH2':gate='Copper individual maker Wet Areas PASS; tub flange/membrane, niche opening, calibrated 2x20 cut and grout/edge selection held.'
    else:gate='Charcoal flat Soft individual Wet Areas PASS; no transfer of Bone Ribbed/Clara wet approval; actual niche face deduction needed.'
   elif surf=='floor':
    product=floor
    gate='Raw exact wet ANSI measured DCOF NULL / FAIL for source Soft/AntiSlip or proposed Emser bound >=0.60; 12x24 cannot be presumed suitable for unmeasured pan, conditional liner/slopes unverified.'
   else:
    product=accent
    gate='NO PRIMARY NICHE: old unpriced historic row EXCLUDED, zero order' if rid=='TX-PRIMARY' else ('Clara Caviar wet FAIL vs individually wet-listed Soho Ivory PASS; back/returns/sill and field face netting null' if rid=='TX-BATH4' else 'Sandstone individual Wet Areas PASS, historical 8.63 SF is NOT measured niche; do not add duplicate face')
   rate=row['quoted_rate_usd_per_sf']
   lines.append('| %s / %s | %s | %.2f SF / arithmetic pre-waste %.2f SF only | Old %s USD/unit at %s USD/SF; proposed SKU/project rate NULL | %s |'%(surf,sku,product,q,q/1.15,'NULL' if old is None else f'{old:.2f}','NULL' if rate is None else f'{rate:.2f}',gate))
  lines+=['','## Dimension-controlled cut grid (prior source / not certified as-built)','',
          '| Wall | Provisional drawing width | Candidate nominal module / theoretical balanced end cuts before grout | Source/constructability control |',
          '|---|---:|---|---|']
  for wallid,width,mod in variants['cuts']:
   count=int(width/mod);edge=(width-count*mod)/2
   lines.append('| %s | %.3f in | %d full %g-in modules + 2 x %.3f-in nominal edges (0 offset) | Recenter or rotate under mockup to prevent focal slivers; actual tile caliber, grout, openings, valves, movement and trim LF NULL |'%(wallid,width,count,mod,edge))
  lines+=['','**Geometry classification:** All above W values are drawing-derived/assumed, NOT native live Revit 1529. Ceiling/tub datum, tile actual caliber, deck height, niche openings, shower drain center, rough and glass/door cuts must be physically surveyed and manufacturer-calibrated before GCs issue shop drawings. The 3-in small-strip example for 24x48 large-format focal cuts is not transferable verbatim to each 2x20 module; every small-format cut still requires a deliberate mock-up.','',
          '## Manufacturer and material evidence','',
          '- Individually maker-authorized wet walls: [Cortar Clay flat](https://www.elmsurfaces.com/product/cortar-clay), [Tones Copper](https://www.elmsurfaces.com/product/copper-tones), [Cortar Charcoal flat](https://www.elmsurfaces.com/product/cortar-charcoal), [Tones Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) and [Soho Ivory](https://www.elmsurfaces.com/product/soho-ivory). Each actual color/finish must match its own applicable surface. [Clay Ribbed](https://www.elmsurfaces.com/product/clay-ribbed-cortar) and [Clara collection](https://www.elmsurfaces.com/product-collection/clara-collection) have NO separately established wet-wall listing for relief/Caviar.',
          '- Alternative Emser [Capisco Trosa F08CAPITR1224M exact SKU](https://www.emser.com/catalog/shop-products/material/Porcelain/capisco-f08capitr1224m): 12x24 Matte Taupe, maker reports DCOF >=0.60, commercial wet floor YES, 9-mm thick and rectified; it is a LOWER BOUND, NOT a raw individual laboratory measured certificate. Maker actual pack yield, current SKU stock, installed cost/lead and tested numeric point null. [Research file](../../../../../research/products/emser-capisco-trosa-f08capitr1224m-matte-wet-field.md). Source historic floor rate is NOT Emser pricing.',
          '- Conditional alternative for TX-PRIMARY selected 48in Brizo linear: Daltile Prime RL21 only in family brochure linear-compatible MOSAIC application, with exact item/size and raw wet numeric test still null. [Maker source comparison](../../../../../research/products/R10_EXACT_SKU_WET_USAGE_AND_CARTON_DECISION_REGISTER.md). Preserve Brizo Black Onyx linear trim, selected rough, no extra niche, separate floor/WC and pan allocations.',
          '- [Public newer evidence](../../../../../research/products/R12_PUBLIC_MAKER_DRAIN_AND_SUPPLY_EVIDENCE_20261106.md) distinguishes maker versions, raw wet tests, supplier offers and unverified Chicago lots; no vendor has been contacted. [Old Town comps](../../../../../research/comps/COMPS.md): 14 entries/9 independent buildings, OT01-OT04 at 405 W Armitage one building, LP/GC secondary; no authenticated tile photos. PH $2.8M, TX $2.7M.',
          '','## Exact quantity/waste, technical and owner decision barriers','',
          '**Historic quote:** USD %.2f/unit (two copies), 2026-09-03 ELM source itemized, includes one 15%% gross waste factor. Proposed price/installed delta, exact tile carton/order code where unavailable, room cap, tax, freight, Chicago shade lot and ETA = NULL. Do NOT apply second waste to source gross, double-count shared WC, niche face/back/returns, trim or a new whole-area pan. %s'%(room['carried_quote_material_subtotal_usd_per_unit'],area),'',
          '**Hard-gate status:** '+('Original wet relief listing FAIL; proposed flat wet wall PASS, ' if rid=='TX-PRIMARY' else 'Individually approved candidate wet wall PASS, ' if rid=='TX-BATH2' else 'Original Clara wet listing FAIL; Soho Ivory candidate individually wet niche PASS, ' if is_new else 'Maker wet use checked per exact surface; ')+
          'wet-floor raw numeric test report FAIL/HOLD, applicable linear PAN numeric and membrane/liner/rough connection FAIL/HOLD for Primary, owner/geometry/true cost availability HOLD. No unverified 125%-of-room-cap decision.','',
          '**Waterproof/install planning:** Sketch membrane and bonded-assembly compatibility (or fully engineered liner assembly) at selected fixtures; preserve actual tub flange/waste and no shower pan for Bath2/Bath4, and separately selected 48in Brizo linear rough with verified fall for Primary; full waterproof niche backs and positive sill pitch; choose movement sealant at changes of plane, actual finished threshold elevation, color-matched outside edge, observed flatness, mortar and ceiling retention. No tile area, manufacturer certification or membrane component is guessed.','',
          '**Sample/render brief, NOT ordered/rendered:** Pair exact wall sample with source metal (Primary BNX; Bath2 Chrome; Bath4 Matte White), neutral floor, grout and outside edge; dimension an elevation with provisional W centers and unselected positions dashed, show two physical floor/joint tests under actual lighting, lineal drain or tub-flange cutaway as appropriate. Owner signoff on product, program, finish, floor/pan certificate, GC section and actual cost all NULL.']
  f=folder/f'{letter}.md'
  assert not f.exists()
  f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
  print(rid,letter,len(f.read_bytes()),'bytes')
print('PASS 6 new R012 neutral source-accurate DRAFT packets, not keyed/frozen/dispatched or scored')
