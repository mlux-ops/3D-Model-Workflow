from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1]
rooms={x['id']:x for x in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
focus={
'PH-BATH3':{
 'letters':{'B':'SOURCE','A':'NEW'},
 'fixture':'Hansgrohe Chrome shower controls, Delta DT062412 4-in square tile-in shower drain; sink/basin owner-unselected, no bathtub line in carried plumbing',
 'program':'Prior drawing/export describes TUB ALCOVE but carried selected plumbing specifies a SQUARE shower drain. Owner tub versus walk-in program is unresolved; this packet does not decide.',
 'source_wall':'Tones Opal 2x20 Glossy wet field',
 'new_wall':'ELM Tones Sandstone 2x20 Glossy individually maker Wet Areas-listed wet field and niche; separate Opal source wet listing is absent',
 'source_floor':'ELM Cortar Bone 12x24 Soft level floor, exact raw numeric wet DCOF null',
 'new_floor':'Glazzio Harmonic Rondo HNC6615 nominal 12x24 DCOF Matte LEVEL floor (maker wet DCOF >0.50 lower-bound), with HNC6715 2x2 hex shower-pan mosaic ONLY IF owner chooses walk-in, raw lab numeric points null',
 'niche':'ELM Tones Sandstone 2x20 Glossy wet niche; original niche net field displacement / actual back and sill dimensions null',
 'wet':'Tones Opal individual Wet Areas absent on wet tub/shower surfaces: FAIL. Sandstone Wet Areas PASS as distinct maker product, not floor.',
 'special':'**PH Bath3 owner sink is explicitly UNSELECTED** (plumbing source row 2580485884149636); no basin, faucet location or mirror placement may be invented. Delta DT062412 Chrome square point shower drain cannot be silently substituted as a bathtub drain.',
 'owner':'Owner must first confirm tub versus walk-in program AND separately select sink; neither tile candidate supplies the answer.'
},
'TX-BATH3':{
 'letters':{'C':'SOURCE','B':'NEW'},
 'fixture':'Brizo BT062415-BNX 4-in square tile-in point shower drain, Brilliance Black Onyx Roccesco shower controls and carried lavatory faucet; NO tub selected in plumbing rows',
 'program':'Prior drawing/export describes TUB ALCOVE while the carried selected plumbing contains a SQUARE shower drain and shower fixtures. Owner tub versus walk-in program remains unresolved.',
 'source_wall':'ELM Tones Emerald 2x20 Glossy individually maker Wet Areas-listed wet field',
 'new_wall':'ELM Tones Emerald 2x20 Glossy individually maker Wet Areas-listed wet field, with Sandstone niche; no unrequested replacement color',
 'source_floor':'ELM Cortar Grey 12x24 Soft LEVEL floor, exact raw numeric wet DCOF null',
 'new_floor':'Glazzio Harmonic Rondo HNC6615 nominal 12x24 DCOF Matte LEVEL floor (maker wet DCOF >0.50 lower-bound) with HNC6715 2x2 hex shower pan ONLY IF walk-in is owner authorized; raw measured numeric DCOF null',
 'niche':'ELM Tones Sandstone 2x20 Glossy individually maker Wet Areas-listed existing niche; actual opening/returns and field overlap null',
 'wet':'ELM Tones Emerald 2x20 Glossy exact individual maker Wet Areas PASS per prior documented product audit; no DCOF floor certification is inherited. Sandstone niche wet PASS.',
 'special':'Existing Brizo Black Onyx point-drain shower set is not a selected BATHTUB assembly. If owner chooses tub, correct bathtub SKU, waste/overflow and fixture changes require separate explicit owner/architect approval before ANY tile takeoff or vendor release.',
 'owner':'Owner must select tub versus shower. Do not infer walk-in approval solely from point-drain source or tub approval solely from older drawing.'
}}
assert set(focus)=={'PH-BATH3','TX-BATH3'}
for rid,cfg in focus.items():
 r=rooms[rid]
 assert r['status']=='blocked' and r['champion_id'] is None and r['owner_status'] is None
 g=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 d=R/'rooms'/rid/'board/round-011/candidates';d.mkdir(parents=True,exist_ok=True)
 for letter,kind in cfg['letters'].items():
  p=d/(letter+'.md')
  assert not p.exists(),p
  isnew=(kind=='NEW')
  wall=cfg['new_wall'] if isnew else cfg['source_wall']
  floor=cfg['new_floor'] if isnew else cfg['source_floor']
  lines=['# '+rid+' — Candidate '+letter+' — complete tile design option','',intro,'',
  '## Complete bounded material and selected fixture program',
  '',
  '**Geometry and program fact:** '+cfg['program']+' **Selected plumbing:** '+cfg['fixture']+'. Geometry from prior handoff **NOT certified by verified 1529 Revit**; currently connected native model is titled 1527. The material and floor/pan concept is conditional, not an owner decision, budget approval or contractor release.',
  '',
  'This option uses '+wall+'; floor study is '+floor+'. Existing niche plane: '+cfg['niche']+'. Current substitute prices/lot/lead, raw SKU wet-slip lab point, actual floor/pan survey, signed owner selection and installed labor are NULL. All 15% source waste is already in original ELM gross quantities.',
  '',
  '| Original source surface and Smartsheet ID | Proposed maker/format/use and individual evidence | Original gross SF per unit, 15% INCLUDED | Original dated ELM unit material USD versus new alternate USD | Hard gate and final installation scope |',
  '|---|---|---|---|---|']
  for z in r['carried_tile_rows']:
   surf=z['surface'];q=z['qty_sf_per_unit'];money=z['extended_quote_cost_usd_per_unit']
   material=wall if surf=='wall' else floor if surf=='floor' else cfg['niche']
   wetgate=(cfg['wet'] if surf in ('wall','accent') else 'LEVEL bath floor exact numeric manufacturer wet DCOF raw test currently null FAIL. A distinct small-format point shower PAN would be needed only if owner chooses WALK-IN; actual size/centering/4-plane slope/test and materials null.')
   lines.append('| '+surf+' / '+z['smartsheet_row_id']+' | '+material+'; reference source product: '+z['carried_description'].replace('|','/')+' | '+format(q,'.2f')+' SF gross / '+format(q/1.15,'.2f')+' SF implied pre-waste arithmetic ONLY | ELM 2026-09-03 old '+('null' if money is None else format(money,'.2f'))+' USD/unit, original source rate '+str(z['quoted_rate_usd_per_sf'])+' USD/SF; new/current price NULL | '+wetgate+' |')
  lines.append('| Membrane, grout, outside edges, transitions, carton and labor | Manufacturer approved actual substrate and drain assembly, actual grout/color, trim, glass/door threshold and NICHE returns are NULL | Real exposed edge LF, waterproof area, level/pan allocation and cartons NULL | Historical setting/trim/installed price NULL; live quote NULL | Correct model, exact tile calibration and signed owner branch required |')
  lines+=['','## Drawing-derived dimensional elevation / cut-control studies','',
  '| W tag | Source width and tiled height | Possible 2x20 wall course study (before actual grout) | Project-source geometry and build requirements |','|---|---|---|---|']
  for w in g['tiled_walls']:
   width=w['length']['value']*12;height=w['tiled_height']['value']*12
   n=max(0,math.floor((width-6)/20));edge=(width-20*n)/2
   lines.append('| '+w['id']+' | '+format(width,'.2f')+' × '+format(height,'.2f')+' in | '+str(n)+' nominal 20-in width runs + 2 × '+format(edge,'.2f')+'-in theoretical balanced edges before grout/actual tile caliber; rotate only after mock-up | Orientation, tub/shower program, drain plane, sill/niche, owner sink, valve centers, doors, movement and real trim LF unmeasured |')
  lines+=['',
  '## Owner program A/B — both unselected; no independent fixture decision',
  '',
  '**TUB interpretation (if owner approves):** source 2x20 wet-wall field/tub returns to actual owner-selected new bathtub and waste/overflow (both NULL); existing listed SQUARE shower drain conflicts and cannot become a tub waste without corrected signed plumbing schedule. All historic gross FLOOR would be remeasured as LEVEL only; shower pan quantity N/A if no separate walk-in. Tub backer/flange waterproof detail, shower controls, niche sill fall, glass/curb and cabinet/threshold survey required. DO NOT buy a HNC6715 pan or invent any bathtub model.',
  '',
  '**WALK-IN interpretation (if owner approves):** selected SQUARE point drain remains the concept, but prior tub alcove geometry cannot be used as a verified shower footprint. Four-plane shower pan slope, waterproof membrane/drain throat, curb/glass, drain-center and finished tile depth require licensed trade coordination. Source total gross floor is ONE pool: measured LEVEL gross plus measured PAN gross must reconcile with original quantity, after correctly classified waste. HNC6715 nominal 2x2 hex, individual Glazzio Shower Floor YES and wet >0.50 **BOUND** is a conditional point-pan idea ONLY; exact raw measured wet DCOF, mesh setting compatibility, actual pan SF and box count null. HNC6615 12x24 stays on LEVEL only.',
  '',
  'Manufacturer >0.50 published lower bound is NOT an exact raw measured numeric SKU lab test; Daltile Portfolio Target >=0.42 is not a test reading. Historic Soft floor lacks a released raw exact test. **Neither branch nor candidate passes current exact wet-DCOF release gate.**',
  '',
  '## Product-specific documentation and commercial accountability',
  '',
  '- '+cfg['wet'],
  '- '+cfg['special'],
  '- Existing original project nominal ELM material sum **USD '+format(r['carried_quote_material_subtotal_usd_per_unit'],'.2f')+'/unit**, two copies, one embedded 15% waste, original original rows and supplier terms dated 2026-09-03. No current pricing for these substitutes; do not copy other color/size or old quote into new order.',
  '- Individual maker evidence [Tones Sandstone](https://www.elmsurfaces.com/product/sandstone-tones), [Tones Emerald](https://www.elmsurfaces.com/product/emerald-tones), [Tones collection](https://www.elmsurfaces.com/product-collection/tones) (no verified individual Opal Wet Areas listing); [Glazzio HNC6615](https://glazziosurfaces.com/products/harmonic-rondo-12x24-matte-porcelain-tile), [Glazzio HNC6715](https://glazziosurfaces.com/products/harmonic-rondo-2x2-matte-hex-mosaic). Exact 2x20 wall/level/pan order SKU, relevant maker finish-specific wet authorization, lot and local ETA must be independently checked.',
  '- Local evidence: [market comparables](../../../../../research/comps/COMPS.md), [Sandstone maker and quote](../../../../../research/products/elm-tones-sandstone-2x20.md), [Emerald maker and quote](../../../../../research/products/elm-tones-emerald-2x20.md), [floor alternate source](../../../../../research/products/R10_EXACT_SKU_WET_USAGE_AND_CARTON_DECISION_REGISTER.md), [owner price and scope authority](../../../../../state/OWNER_FEEDBACK.md). Existing maker/comps links do not imply site approval.',
  '- Market reference set: 14 listings/nine unique building groups, 405 W Armitage OT01–OT04 ONE independent precedent; Old Town priority, Lincoln Park and Gold Coast secondary, PH $2.8M, TX $2.7M, about $2.4M–$3.2M. No authenticated photos establishing a comparable bathroom tile palette. The source-selected Chrome or Black Onyx fixtures remain as recorded, not reassigned.',
  '- '+cfg['owner']+' Exact owner material cap, signed alternate, current Chicago stock/lot freight, lead, total installed price, current sample approval, real edge LF and orderable carton quantity all null.',
  '',
  '**Sample/render brief (NOT purchased/rendered):** separately draw labelled OWNER-UNSELECTED Tub and Walk-In orthographic W1–W3 elevations and waterproof transitions, with one same-size wall sample, floor/mosaic sheet and grout/trim references, selected metal, and every uncertain tub/sink/door/drain point dashed. This is a conditional concept, not an approved design or order.']
  p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
  assert p.read_text(encoding='utf-8').splitlines()[2]==intro
  print(rid,letter,p.stat().st_size)
print('PASS 4 R011 Bath3 source-supported neutral draft concepts; not frozen and not dispatched')
